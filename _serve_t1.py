"""_serve_t1.py — T1 种子 v1/hr 双版对比页（Tailscale 100.84.28.40:8861）。

Range 206（视频 seek）。用法: python _serve_t1.py
"""
import http.server
import re
import socketserver
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V1 = ROOT / "runs" / "envpsy-t1-61"
HR = ROOT / "runs" / "envpsy-t1-61-hr"
T2 = ROOT / "runs" / "envpsy-t2-94"
FILES = {
    "/v1.mp4": V1 / "out" / "final_envpsy-t1-61.mp4",
    "/hr.mp4": HR / "out" / "final_envpsy-t1-61-hr.mp4",
    "/t2.mp4": T2 / "out" / "final_envpsy-t2-94.mp4",
    "/t3.mp4": ROOT / "runs" / "envpsy-t3-intro" / "out" / "final_envpsy-t3-intro.mp4",
    "/t4.mp4": ROOT / "runs" / "envpsy-t4-91" / "out" / "final_envpsy-t4-91.mp4",
    "/glm.mp4": ROOT / "runs" / "envpsy-glm-t1-31" / "out" / "final_envpsy-glm-t1-31.mp4",
    "/hr-yunjian.mp4": ROOT / "runs" / "envpsy-t1-61-hr-yj" / "out" / "final_envpsy-t1-61-hr-yj.mp4",
    "/v1-storyboard.md": V1 / "storyboard.md",
    "/hr-storyboard.md": HR / "storyboard.md",
    "/t2-storyboard.md": T2 / "storyboard.md",
    "/t2-topic-brief.md": T2 / "topic-9-4.md",
    "/t3-storyboard.md": ROOT / "runs" / "envpsy-t3-intro" / "storyboard.md",
    "/t4-storyboard.md": ROOT / "runs" / "envpsy-t4-91" / "storyboard.md",
    "/glm-storyboard.md": ROOT / "runs" / "envpsy-glm-t1-31" / "storyboard.md",
    "/topic-brief.md": V1 / "topic-6-1.md",
    "/v1-produce.log": V1 / "produce.log",
    "/hr-produce.log": HR / "produce.log",
    "/t2-produce.log": T2 / "produce.log",
}
for _f in sorted((ROOT / "audio" / "tts-ab").glob("*.mp3")):
    FILES[f"/tts-{_f.name}"] = _f
MIME = {".mp4": "video/mp4", ".mp3": "audio/mpeg", ".md": "text/plain; charset=utf-8", ".log": "text/plain; charset=utf-8"}
PORT = 8861

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>T1 种子对比 · 个人空间与人际距离</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:15px;color:#8fb;margin-top:28px}a{color:#7fd}video{width:100%;border-radius:8px;background:#000}
.meta{color:#9ab;font-size:13px;line-height:1.7}table{border-collapse:collapse;font-size:13px}
td,th{border:1px solid #2a3540;padding:4px 10px;text-align:left}th{color:#8fb}</style></head><body>
<h1>《看不见的气泡》T1 种子 · 两版对比</h1>
<table>
<tr><th></th><th>v1 默认推理</th><th>hr 高推理</th></tr>
<tr><td>时长</td><td>396.7s</td><td>348.6s（更贴近 5min 目标）</td></tr>
<tr><td>storyboard</td><td>3,357 tok</td><td>5,321 tok</td></tr>
<tr><td>codegen</td><td>9,713 tok / 20,749 字符</td><td>11,670 tok / 23,956 字符</td></tr>
<tr><td>账单合计（已记账）</td><td>13,070 tok</td><td>16,991 tok（+30%）</td></tr>
<tr><td>repair 轮</td><td>0</td><td>0</td></tr>
<tr><td>QA</td><td>PASS</td><td>PASS</td></tr>
</table>
<h2>hr 版（高推理）——先看这版</h2>
<video controls preload="metadata" src="/hr.mp4"></video>
<p class="meta">学术严谨性升级：区间归属规则显式化（[0,0.45) 左闭右开）、中点划分声明"仅为本片数值划分"、D1/D2 数学约束 0&lt;D2&lt;D1≤3.00m、相关≠因果表述、Math-check 16 条全可验证。</p>
<h2>v1 版（默认推理）</h2>
<video controls preload="metadata" src="/v1.mp4"></video>
<p class="meta">对照基准。质量合格（你已验收），但亚档中点未声明划分依据、图表较抽象。</p>
<h2>材料</h2>
<p class="meta"><a href="/hr-storyboard.md">hr storyboard</a> · <a href="/v1-storyboard.md">v1 storyboard</a> · <a href="/topic-brief.md">topic brief</a> · <a href="/hr-produce.log">hr log</a> · <a href="/v1-produce.log">v1 log</a></p>
<h2>🔊 配音对比——T1 种子 · 云健（纪录片男声）版</h2>
<video controls preload="metadata" src="/hr-yunjian.mp4"></video>
<p class="meta">347.5s · 42 句 · 与上方 hr 版同分镜同画面，仅旁白换为 zh-CN-YunjianNeural（云健）· QA PASS<br>
供同事对比：<b>晓晓（hr 版）vs 云健（本版）</b>——结合 <a href="/tts.html">音色 A/B 页</a> 一起打分。男声候选：云健（纪录片）/ 云扬（新闻播报）。</p>
<h2>T2 种子（案例解析）——成都与乐山茶馆</h2>
<video controls preload="metadata" src="/t2.mp4"></video>
<p class="meta">262.5s · 40 句 · sol effort=high · 零 repair · QA PASS · 账单 16,715 tok（storyboard 3,380 + codegen 13,335）<br>
案例场景感：纪实插画风街景（卸铺板/桌椅上街/赶路与落座）；密度对比 1.0 vs 1.125 家/千人 + 12.5% 相对差完整呈现；六启示编号导航。<b>打磨项已修</b>：1997·冯/胡调查来源标注、页码去重、标签对比度。</p>
<p class="meta"><a href="/t2-storyboard.md">T2 storyboard</a> · <a href="/t2-topic-brief.md">T2 topic brief</a> · <a href="/t2-produce.log">T2 log</a></p>
<h2>T3 种子（学科史）——环境心理学从哪里来（绪论 · 3分钟级）</h2>
<video controls preload="metadata" src="/t3.mp4"></video>
<p class="meta">216.7s · 24 句 · sol effort=high · QA PASS · 账单 13,033 tok（storyboard 3,831 + codegen 9,202）+ 2 轮 visual-repair<br>
卫城祭祀开场 → 1886 沃尔芬 → 1968 EDRA（27→900人构成核算）→ 四刊年份 → 中国引入（1993/1996/2010）。五人卡（含林奇）+ 期刊卡 + 事件卡。</p>
<p class="meta"><a href="/t3-storyboard.md">T3 storyboard</a></p>
<h2>T4 种子（方法演示）——观察者的工具箱（9.1 · 5分钟）</h2>
<video controls preload="metadata" src="/t4.mp4"></video>
<p class="meta">303.2s · 41 句 · sol effort=high · 零 repair · QA PASS · 账单 16,880 tok（storyboard 4,369 + codegen 12,511）<br>
"师傅带徒弟"口吻 + 工具卡隐喻（五W → 单一因素 → 行为观察四式 → 痕迹推测三径）；含相关≠因果与研究伦理提醒句。</p>
<p class="meta"><a href="/t4-storyboard.md">T4 storyboard</a></p>
<h2>扩散验证：GLM 复刻 T1——认知地图五要素（3.1）</h2>
<video controls preload="metadata" src="/glm.mp4"></video>
<p class="meta">277.8s · 40 句 · model=glm（不占 sol 额度）· QA PASS · 自动 repair 1 轮 · storyboard 29,183 tok + codegen 65,321 tok<br>
设计语言规范蒸馏进 brief 后 GLM 全项复刻成功：深蓝底/青绿强调/扁平图解/旁白面板/页码骨架 5/5 一致；分镜 Math-check 20+ 条；基钦 1994 五功能页完整。<b>结论：种子→扩散路线成立，可放量。</b></p>
<p class="meta"><a href="/glm-storyboard.md">GLM storyboard</a> · <a href="/tts.html">🔊 TTS 音色 A/B 试听页</a> · <a href="http://199.68.217.229:8862/?p=course/chapter-06/lesson-t1-personal-space">🎮 互动课件 Runtime 测试页</a><br>
公网访问：视频 gallery <a href="http://199.68.217.229:8861/">http://199.68.217.229:8861/</a> · 互动课件 <a href="http://199.68.217.229:8862/">http://199.68.217.229:8862/</a>（备用 Tailscale 通道 :8443/:10000）</p>
</body></html>"""

TTS_PAGE = """<!doctype html><meta charset="utf-8"><title>TTS 音色 A/B</title>
<style>body{font-family:system-ui,"Microsoft YaHei";max-width:760px;margin:32px auto;background:#10161F;color:#dfe7ee;padding:0 16px}
h2{color:#4FD1C5}p{color:#9fb3c1;line-height:1.7}audio{width:100%;margin:6px 0 18px}
.card{border:1px solid #2a3644;border-radius:12px;padding:12px 16px;margin-bottom:14px;background:#161e28}
.card b{color:#F5C04A}</style>
<title>TTS A/B</title><h1>🔊 TTS 音色 A/B（同一段旁白）</h1>
<p>试听文案（T1 开头）："{{TEXT}}"<br>问题：现状 A（晓晓）AI 感偏强。请同事对每个变体打分（自然度 1-5）。</p>
{{CARDS}}
<p style="margin-top:28px;color:#7a8b98">若本页音色仍不够自然 → 升级路径：①SSML 停顿/重音工程（零成本）②Azure 付费层 style 风格（cheerful/calm）③MiniMax/豆包情感 TTS（按字符计费）④IndexTTS-2.5 云方案克隆讲师音色（需素材，按用户既有裁决只走云）。</p>
</body></html>"""

def _tts_page():
    cards = "".join(
        f'<div class="card"><b>{n}</b> — {desc}<br><audio controls preload="none" src="/tts-{n}.mp3"></audio></div>'
        for n, _v, _r, desc in [
            ("A-xiaoxiao-current", "", "", "现状：晓晓，标准女声"),
            ("B-yunxi", "", "", "云希：男声，自然对话感最强"),
            ("C-yunjian", "", "", "云健：男声，沉稳纪录片感"),
            ("D-yunyang", "", "", "云扬：男声，新闻播报感"),
            ("E-xiaoyi", "", "", "晓伊：女声，年轻柔和"),
            ("F-xiaoxiao-slow", "", "", "晓晓降速 5%：检验语速的影响"),
        ]
    )
    text = "我们每个人都有一个看不见的气泡，它跟着我们走，随我们坐。陌生人靠得太近，我们会不由自主地后退。一九六六年，人类第一次给这个现象起了名字：个人空间。"
    return (TTS_PAGE
            .replace("{{TEXT}}", text)
            .replace("{{CARDS}}", cards))


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_file(self, f: Path):
        size = f.stat().st_size
        ctype = MIME.get(f.suffix, "application/octet-stream")
        rng = self.headers.get("Range")
        if rng and (m := re.match(r"bytes=(\d*)-(\d*)", rng)):
            start = int(m.group(1) or 0)
            end = min(int(m.group(2)) if m.group(2) else size - 1, size - 1)
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            length = end - start + 1
        else:
            self.send_response(200)
            length = size
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        with f.open("rb") as fh:
            fh.seek(start if rng else 0)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(1 << 20, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/tts.html":
            body = _tts_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        f = FILES.get(self.path)
        if f and f.exists():
            self._send_file(f)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def do_HEAD(self):
        f = FILES.get(self.path)
        if f and f.exists():
            self.send_response(200)
            self.send_header("Content-Type", MIME.get(f.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(f.stat().st_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)


socketserver.TCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"serving T1 compare page at http://100.84.28.40:{PORT}/ (0.0.0.0:{PORT})", flush=True)
    httpd.serve_forever()
