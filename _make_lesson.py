"""_make_lesson.py — 从 run 的 timing/scene/storyboard 生成 Lesson Package（讨论稿 §29/§30 合同）。

产出: lesson-runtime/course/<chapter>/<lesson_id>/
      video.mp4(复制) lesson.json transcript.vtt script.md interactions.json summary.json
用法: python _make_lesson.py <src-run> <lesson_id> <chapter_id> --cues auto|none
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
RUNTIME = ROOT / "lesson-runtime"


def fmt_vtt(t: float) -> str:
    ms = int(round(t * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def build_vtt(starts, ends, texts) -> str:
    lines = ["WEBVTT", ""]
    for i, (a, b, txt) in enumerate(zip(starts, ends, texts)):
        end = min(b, starts[i + 1] if i + 1 < len(starts) else b)
        lines += [f"{i + 1}", f"{fmt_vtt(a)} --> {fmt_vtt(end)}", txt.replace("\n", " "), ""]
    return "\n".join(lines)


def make(src_run: str, lesson_id: str, chapter_id: str, course_id: str, title: str,
         knowledge_points: list, timeline: list, interactions: dict, summary: dict):
    src = ROOT / "runs" / src_run
    tm = json.loads((ROOT / "audio" / f"timing_{src_run}.json").read_text(encoding="utf-8"))
    sc = json.loads((ROOT / "audio" / f"scene_{src_run}.json").read_text(encoding="utf-8"))
    texts = [s["text"] for s in sc["sentences"]]
    starts, ends, total = tm["starts"], tm["ends"], round(tm["total"], 1)

    pkg = RUNTIME / "course" / chapter_id / lesson_id
    pkg.mkdir(parents=True, exist_ok=True)
    shutil.copy(src / "out" / f"final_{src_run}.mp4", pkg / "video.mp4")
    shutil.copy(src / "storyboard.md", pkg / "script.md")
    (pkg / "transcript.vtt").write_text(build_vtt(starts, ends, texts), encoding="utf-8")

    manifest = {
        "schema": "lesson-manifest-v0.1",
        "course_id": course_id, "chapter_id": chapter_id, "lesson_id": lesson_id,
        "title": title, "duration": total,
        "video": "video.mp4", "transcript": "transcript.vtt", "script": "script.md",
        "knowledge_points": knowledge_points, "timeline": timeline,
    }
    (pkg / "lesson.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (pkg / "interactions.json").write_text(json.dumps(interactions, ensure_ascii=False, indent=2), encoding="utf-8")
    (pkg / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"package ok -> {pkg} ({total}s, {len(texts)} 句, {len(interactions.get('cues', []))} cues)")
    return pkg


if __name__ == "__main__":
    # T1《看不见的气泡——个人空间与人际距离》：测试载体（3 种 IR 类型全验证）
    t1_interactions = {
        "version": "1.0",
        "lesson_id": "lesson-t1-personal-space",
        "cues": [
            {
                "id": "num-d1d2", "time": 72.9, "type": "short_numeric", "pause": True,
                "question": "一次止步距离实验里，被试的 D1＝0.45 米、D2＝1.20 米。按“D1÷D2 越小越敏感”的指标，这位被试的敏感度是多少？（保留两到三位小数）",
                "answer": 0.375, "tolerance": 0.01, "unit": "",
                "feedback": {
                    "correct": "对：0.45 ÷ 1.20 = 0.375。D2 只比 D1 大不到三倍，说明这位被试对距离入侵相当敏感。",
                    "incorrect": "公式是 D1 ÷ D2（小的除以大的），0.45 ÷ 1.20 = 0.375。注意方向别除反了。",
                },
            },
            {
                "id": "choice-zones", "time": 195.4, "type": "single_choice", "pause": True,
                "question": "在营业厅和工作人员谈业务，双方通常站得比较自在的距离属于哪一段？",
                "options": ["密切距离（0–0.45 米）", "个人距离（0.45–1.2 米）", "社会距离（1.2–3.6 米）", "公共距离（3.6–7.6 米）"],
                "correct": 2,
                "feedback": {
                    "correct": "对——谈业务这类“不那么私人的事”属于社会距离（1.2–3.6 米），正常音量即可交谈。",
                    "incorrect": "回想一下：个人距离（0.45–1.2 米）是亲属密友谈心的距离；跟营业员谈业务通常站在社会距离（1.2–3.6 米）更自在，对方贴太近反而惹人烦。",
                },
            },
            {
                "id": "tf-dh", "time": 316.0, "type": "true_false", "pause": True,
                "question": "判断：按芦原义信的 D/H 指标，建筑间距与高度之比等于 1 时，建筑之间偏“远离”。",
                "correct": False,
                "feedback": {
                    "correct": "对——比值小于 1 才偏“接近”，等于 1 是临界，大于 1 才偏“远离”。",
                    "incorrect": "记反了：D/H 小于 1 偏接近，大于 1 偏远离，等于 1 是临界值（视频里说“二”是远离一侧的临界）。",
                },
            },
        ],
    }
    t1_summary = {
        "schema": "summary-v0.1", "lesson_id": "lesson-t1-personal-space",
        "knowledge_points": [
            "个人空间＝身体周围看不见的“气泡”：腰以上近圆柱、腰以下收尖，随人移动、随关系与场合胀缩",
            "霍尔 1963 年命名 Proxemics（空间接近学）",
            "止步距离法 stop-distance：D1＝开始不舒服，D2＝相当不舒服；D1÷D2 越小越敏感",
            "霍尔四段人际距离：密切 0–0.45m（触觉，中点界 0.225）｜个人 0.45–1.2m（一臂长，界 0.825）｜社会 1.2–3.6m（正常音量，中点 2.4）｜公共 3.6–7.6m（中点 5.6）",
            "气泡的证据与边界：阅览室实验约七成离座；病原体假说（Fincher & Thornhill 2012）只是推测，史实不能证因果；2014 fMRI 见顶内沟—前运动皮层耦合，是相关不是定位",
            "设计应用：D/H＜1 接近、＞1 远离、＝2 远离侧临界、＞4 影响弱；观赏距离 ≥ 对象高度 4 倍；L 形座椅/边缘座位更吸引停留",
        ],
        "common_mistakes": [
            "四段距离的“近/远两档”是按区间中点划分的近似，不是霍尔的原始全部数值",
            "D/H＝1 是接近与远离的分界，不是“远离”",
            "疾病史实只能说明风险真实存在，不能证明气泡起源于防病（相关 ≠ 因果）",
        ],
        "next_lesson": "下一节（3.1）：认知地图——人在陌生城市里如何记忆道路与方位（已有同题种子片）",
    }
    t1_timeline = [
        {"start": 0, "end": 19.3, "type": "intro", "topic": "从鸟儿与西湖引入"},
        {"start": 19.3, "end": 93.8, "type": "concept", "topic": "个人空间与止步距离法"},
        {"start": 93.8, "end": 195.5, "type": "concept", "topic": "霍尔四段人际距离"},
        {"start": 195.5, "end": 266.1, "type": "concept", "topic": "气泡的来源证据"},
        {"start": 266.1, "end": 341.7, "type": "application", "topic": "个体差异与设计应用 D/H"},
        {"start": 341.7, "end": 348.6, "type": "summary"},
    ]
    pkg = make(
        src_run="envpsy-t1-61-hr", lesson_id="lesson-t1-personal-space",
        chapter_id="chapter-06", course_id="envpsy-course-001",
        title="看不见的气泡——个人空间与人际距离（6.1）",
        knowledge_points=["个人空间", "Proxemics 空间接近学", "止步距离法 D1/D2", "霍尔四段距离", "气泡来源的证据与边界", "D/H 比值与设计应用"],
        timeline=t1_timeline, interactions=t1_interactions, summary=t1_summary,
    )
    # 课程清单
    course = {
        "schema": "course-manifest-v0.1", "course_id": "envpsy-course-001",
        "title": "环境心理学·互动课件（单课测试）", "version": "0.1",
        "chapters": [{
            "chapter_id": "chapter-06", "title": "第六章 空间行为",
            "lessons": [{
                "lesson_id": "lesson-t1-personal-space",
                "title": "看不见的气泡——个人空间与人际距离（6.1）",
                "duration": 348.6, "package": "course/chapter-06/lesson-t1-personal-space",
            }],
        }],
    }
    (RUNTIME / "course" / "course.json").write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
    print("course.json ok")
