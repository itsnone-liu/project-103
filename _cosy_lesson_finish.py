# -*- coding: utf-8 -*-
"""_cosy_lesson_finish.py — T1 CosyVoice 版收尾：STARTS 替换 → 渲染 → QA → mux → Lesson Package。
前置: audio/timing_envpsy-t1-cosy.json + audio/narration_envpsy-t1-cosy.wav 已生成。
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0, str(ROOT))

SRC_RUN = "envpsy-t1-61-hr"
RUN = "envpsy-t1-cosy"
WD = ROOT / "runs" / RUN
VOICE_LABEL = "CosyVoice·龙书(沉稳青年男)"

tm_new = json.loads((ROOT / "audio" / f"timing_{RUN}.json").read_text(encoding="utf-8"))
tm_old = json.loads((ROOT / "audio" / f"timing_{SRC_RUN}.json").read_text(encoding="utf-8"))
assert len(tm_new["starts"]) == len(tm_old["starts"]) == 42, "句数不一致"

# ---------- 1. 准备 run 目录 ----------
if not (WD / "code" / "index.html").exists():
    shutil.copytree(ROOT / "runs" / SRC_RUN / "code", WD / "code")
    shutil.copy(ROOT / "runs" / SRC_RUN / "storyboard.md", WD / "storyboard.md")
    shutil.copy(ROOT / "runs" / SRC_RUN / "decision.json", WD / "decision.json")
    (WD / "out").mkdir(parents=True, exist_ok=True)

# ---------- 2. STARTS 替换（narr = 42 起点 + total） ----------
html_path = WD / "code" / "index.html"
html = html_path.read_text(encoding="utf-8")
narr = tm_new["narr"]
new_block = "const STARTS = [\n  " + ",\n  ".join(
    ",".join(f"{v:.3f}" for v in narr[i:i + 8]) for i in range(0, len(narr), 8)
) + "\n];"
html2, n = re.subn(r"const STARTS = \[[\s\S]*?\];", new_block, html, count=1)
assert n == 1, "STARTS 替换失败"
html_path.write_text(html2, encoding="utf-8")
print(f"STARTS replaced: total {tm_new['total']}s (原 {tm_old['total']}s)")

# ---------- 3. 渲染 ----------
from pipeline.adapters import web2d  # noqa: E402
res = web2d.render(WD, tm_new)
if not res["ok"]:
    print("render FAIL:", res["errors"][:3]); sys.exit(1)
print("render ok:", res["meta"])

# ---------- 4. QA ----------
from pipeline import qa  # noqa: E402
report = qa.check(res["video"], tm_new, WD)
print("qa:", "PASS" if report["pass"] else "FAIL", json.dumps(report.get("checks", {}), ensure_ascii=False)[:200])

# ---------- 5. mux ----------
final = WD / "out" / f"final_{RUN}.mp4"
import audio  # noqa: E402
audio.cmd_mux(res["video"], str(ROOT / "audio" / f"timing_{RUN}.json"), str(final))

# ---------- 6. Lesson Package（cue/timeline 按句索引重映射） ----------
old_starts, new_starts = tm_old["starts"], tm_new["starts"]

def remap(t_old, targets=old_starts):
    """旧时刻 → 该时刻后第一句的句索引，保持相对开口的偏移。"""
    for k, s in enumerate(targets):
        if s >= t_old:
            off = t_old - s
            return round(new_starts[k] + off, 1), k
    return round(tm_new["total"] - (tm_old["total"] - t_old), 1), len(targets) - 1

import _make_lesson as ml  # noqa: E402

interactions = json.loads(json.dumps(ml.t1_interactions if hasattr(ml, "t1_interactions") else {}))
# _make_lesson 的字典在 __main__ 里，直接重建：
interactions = {
    "version": "1.0",
    "lesson_id": "lesson-t1-personal-space-cosy",
    "cues": [
        {"id": "num-d1d2", "time": remap(72.9)[0], "type": "short_numeric", "pause": True,
         "question": "一次止步距离实验里，被试的 D1＝0.45 米、D2＝1.20 米。按“D1÷D2 越小越敏感”的指标，这位被试的敏感度是多少？（保留两到三位小数）",
         "answer": 0.375, "tolerance": 0.01, "unit": "",
         "feedback": {
             "correct": "对：0.45 ÷ 1.20 = 0.375。D2 只比 D1 大不到三倍，说明这位被试对距离入侵相当敏感。",
             "incorrect": "公式是 D1 ÷ D2（小的除以大的），0.45 ÷ 1.20 = 0.375。注意方向别除反了。"}},
        {"id": "choice-zones", "time": remap(195.4)[0], "type": "single_choice", "pause": True,
         "question": "在营业厅和工作人员谈业务，双方通常站得比较自在的距离属于哪一段？",
         "options": ["密切距离（0–0.45 米）", "个人距离（0.45–1.2 米）", "社会距离（1.2–3.6 米）", "公共距离（3.6–7.6 米）"],
         "correct": 2,
         "feedback": {
             "correct": "对——谈业务这类“不那么私人的事”属于社会距离（1.2–3.6 米），正常音量即可交谈。",
             "incorrect": "回想一下：个人距离（0.45–1.2 米）是亲属密友谈心的距离；跟营业员谈业务通常站在社会距离（1.2–3.6 米）更自在，对方贴太近反而惹人烦。"}},
        {"id": "tf-dh", "time": remap(316.0)[0], "type": "true_false", "pause": True,
         "question": "判断：按芦原义信的 D/H 指标，建筑间距与高度之比等于 1 时，建筑之间偏“远离”。",
         "correct": False,
         "feedback": {
             "correct": "对——比值小于 1 才偏“接近”，等于 1 是临界，大于 1 才偏“远离”。",
             "incorrect": "记反了：D/H 小于 1 偏接近，大于 1 偏远离，等于 1 是临界值（视频里说“二”是远离一侧的临界）。"}},
    ],
}
summary = json.loads((ROOT / "lesson-runtime" / "course" / "chapter-06" /
                      "lesson-t1-personal-space" / "summary.json").read_text(encoding="utf-8"))
summary["lesson_id"] = "lesson-t1-personal-space-cosy"
timeline = []
for seg in [
    {"s": 0, "type": "intro", "topic": "从鸟儿与西湖引入"},
    {"s": 19.3, "type": "concept", "topic": "个人空间与止步距离法"},
    {"s": 93.8, "type": "concept", "topic": "霍尔四段人际距离"},
    {"s": 195.5, "type": "concept", "topic": "气泡的来源证据"},
    {"s": 266.1, "type": "application", "topic": "个体差异与设计应用 D/H"},
    {"s": 341.7, "type": "summary", "topic": None},
]:
    t, _ = remap(seg["s"])
    timeline.append({"start": round(t if seg["s"] > 0 else 0, 1), "end": None,
                     "type": seg["type"], "topic": seg["topic"] or "小结"})
for i in range(len(timeline) - 1):
    timeline[i]["end"] = timeline[i + 1]["start"]
timeline[-1]["end"] = round(tm_new["total"], 1)

pkg = ml.make(
    src_run=RUN, lesson_id="lesson-t1-personal-space-cosy",
    chapter_id="chapter-06", course_id="envpsy-course-001",
    title=f"看不见的气泡——个人空间与人际距离（6.1·{VOICE_LABEL}）",
    knowledge_points=["个人空间", "Proxemics 空间接近学", "止步距离法 D1/D2", "霍尔四段距离",
                      "气泡来源的证据与边界", "D/H 比值与设计应用"],
    timeline=timeline, interactions=interactions, summary=summary,
)

# ---------- 7. course.json 追加 ----------
course_path = ROOT / "lesson-runtime" / "course" / "course.json"
course = json.loads(course_path.read_text(encoding="utf-8"))
lessons = course["chapters"][0]["lessons"]
if not any(l["lesson_id"] == "lesson-t1-personal-space-cosy" for l in lessons):
    lessons.append({
        "lesson_id": "lesson-t1-personal-space-cosy",
        "title": f"看不见的气泡——个人空间与人际距离（6.1·{VOICE_LABEL}）",
        "duration": round(tm_new["total"], 1),
        "package": "course/chapter-06/lesson-t1-personal-space-cosy",
    })
course_path.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
print("course.json ok — 完成")
