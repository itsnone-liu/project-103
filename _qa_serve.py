"""_qa_serve.py — Phase AI1 课后问答后端（无状态 demo）· 端口 8863。

POST /api/ask   {package, question, markers[], answers[]}
  → 拼 §20 上下文（course/lesson 元数据 + summary + 互动题 + transcript±20s 窗口）
  → 阿里云百炼 DashScope（OpenAI 兼容口）deepseek-v4.1-flash
  → {answer, review_links[], model, usage, elapsed_ms}

GET /api/health → {ok, model}

无状态约定（为将来集成原有学习平台留路）：学生数据（markers/answers）全部由前端
随请求带上，后端只按 package 名读磁盘上的静态 Lesson Package，不存任何会话。
"""
import json
import os
import re
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LESSON_ROOT = ROOT / "lesson-runtime"
PORT = 8863
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = os.environ.get("QA_MODEL", "deepseek-v4.1-flash")
WINDOW = 20.0  # transcript ±20s（§20）

SYSTEM_PROMPT = """你是这门课的课后助教，负责解答学生看完教学视频后的疑问。规则：
1. 只依据给定的【讲稿节选】【本节摘要】【互动题】作答，不要引入课程之外的未经确认的数据；讲稿未覆盖的问题，直说"本节讲稿没有展开"，并按【本节结构】建议回看哪一段。
2. 回答结构：先用一两句直接回答，再给一句"为什么/依据"；引用讲解内容时标注时间点，格式 @MM:SS。
3. 全文 ≤300 字，中文，语气自然，不用客套开场白。
4. 学生答题记录里有错题时，如果与本次提问相关，顺手点一句易错点。"""


def _parse_vtt(text):
    """[(start, end, text)]，时间戳转秒。"""
    cues = []
    block = []
    for line in text.splitlines() + [""]:
        if line.strip():
            block.append(line)
            continue
        if len(block) >= 2:
            m = re.search(r"(\d+):(\d+):(\d+)[.,](\d+)\s*-->\s*(\d+):(\d+):(\d+)[.,](\d+)", block[0] + " " + block[1] if "-->" not in block[0] else block[0])
            if m:
                g = [int(x) for x in m.groups()]
                s = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
                e = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
                body = [b for b in block[1:] if "-->" not in b]
                cues.append((s, e, " ".join(body).strip()))
        block = []
    return cues


def _fmt(t):
    return f"{int(t // 60):02d}:{int(t % 60):02d}"


def _window(cues, t):
    """覆盖 [t-20, t+20] 的字幕条。"""
    return [(s, e, x) for s, e, x in cues if e >= t - WINDOW and s <= t + WINDOW]


def build_context(pkg):
    """读静态 Lesson Package，返回 (course, lesson, summary, cues, transcript cues)。"""
    p = LESSON_ROOT / pkg
    if not p.exists():
        return None
    def j(name):
        f = p / name
        return json.loads(f.read_text("utf-8")) if f.exists() else None
    course = json.loads((LESSON_ROOT / "course" / "course.json").read_text("utf-8"))
    lesson = j("lesson.json")
    summary = j("summary.json")
    inter = j("interactions.json") or {"cues": []}
    vtt = p / lesson.get("transcript", "transcript.vtt")
    tr = _parse_vtt(vtt.read_text("utf-8")) if vtt.exists() else []
    return course, lesson, summary, inter["cues"], tr


def assemble_user_message(pkg, question, markers, answers, course, lesson, summary, cues, tr):
    parts = [f"【课程】{course['title']}", f"【本节】{lesson['title']}（{lesson['lesson_id']}）"]
    if lesson.get("knowledge_points"):
        parts.append("【本节知识点】" + "；".join(lesson["knowledge_points"]))
    if summary:
        parts.append("【本节摘要·知识点】\n- " + "\n- ".join(summary.get("knowledge_points", [])))
        if summary.get("common_mistakes"):
            parts.append("【本节摘要·易错点】\n- " + "\n- ".join(summary["common_mistakes"]))
    if cues:
        lines = []
        for c in cues:
            ans = c.get("correct", c.get("answer", "?"))
            lines.append(f"- @{_fmt(c['time'])} {c['question'][:60]}…（正确答案：{ans}）")
        parts.append("【课堂互动题】\n" + "\n".join(lines))
    if answers:
        rn = {"correct": "✓", "wrong": "✗", "skipped": "跳过"}
        lines = [f"- @{_fmt(a['time'])} {a['id']}（{a['type']}）答 {a['picked']} → {rn.get(a['result'], a['result'])}" for a in answers]
        parts.append("【学生答题记录】\n" + "\n".join(lines))
    if markers:
        parts.append("【学生看视频时标记的疑问】\n" + "\n".join(f"- @{_fmt(m['timestamp'])} {m['question']}" for m in markers))
        wins, seen = [], set()
        for m in markers:
            for s, e, x in _window(tr, m["timestamp"]):
                if s not in seen:
                    seen.add(s)
                    wins.append((s, e, x))
        wins.sort()
        if wins:
            lines = [f"[{_fmt(s)}–{_fmt(e)}] {x}" for s, e, x in wins]
            parts.append("【讲稿节选（疑问点前后 ±20 秒）】\n" + "\n".join(lines))
    if lesson.get("timeline"):
        parts.append("【本节结构】\n" + "\n".join(f"- @{_fmt(s['start'])} {s.get('topic') or s['type']}" for s in lesson["timeline"]))
    parts.append(f"【学生本次提问】\n{question}")
    return "\n\n".join(parts)


def call_llm(user_msg):
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        raise RuntimeError("DASHSCOPE_API_KEY 未设置")
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_msg}],
        "temperature": 0.3, "max_tokens": 2000,
    }).encode("utf-8")
    req = urllib.request.Request(DASHSCOPE_URL, data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        out = json.loads(r.read().decode("utf-8"))
    msg = out["choices"][0]["message"]
    return msg.get("content") or "(模型未返回内容)", out.get("usage", {}), int((time.time() - t0) * 1000)


class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] in ("/api/health", "/api/"):
            return self._json(200, {"ok": True, "model": MODEL, "package_root": str(LESSON_ROOT)})
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.split("?")[0] != "/api/ask":
            return self._json(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception as e:
            return self._json(400, {"error": f"bad json: {e}"})
        pkg = (req.get("package") or "").strip("/")
        question = (req.get("question") or "").strip()
        if not question:
            return self._json(400, {"error": "question 为空"})
        ctx = build_context(pkg)
        if ctx is None:
            return self._json(404, {"error": f"package 不存在: {pkg}"})
        markers = req.get("markers") or []
        answers = req.get("answers") or []
        user_msg = assemble_user_message(pkg, question, markers, answers, *ctx)
        try:
            answer, usage, ms = call_llm(user_msg)
        except urllib.error.HTTPError as e:
            return self._json(502, {"error": f"dashscope {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}"})
        except Exception as e:
            return self._json(502, {"error": f"llm 调用失败: {e}"})
        links = [{"timestamp": m["timestamp"], "label": f"@{_fmt(m['timestamp'])} 我的疑问：{m['question'][:24]}"} for m in markers]
        self._json(200, {"answer": answer, "review_links": links, "model": MODEL, "usage": usage, "elapsed_ms": ms})

    def log_message(self, fmt, *a):
        print(f"{self.address_string()} {fmt % a}", flush=True)


if __name__ == "__main__":
    print(f"QA backend at http://127.0.0.1:{PORT}/api/ask (model={MODEL})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
