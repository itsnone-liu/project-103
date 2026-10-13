# -*- coding: utf-8 -*-
"""_batch5.py — 第五批：章绪论十篇（2026-10-13 用户批准方案）。

chapter-01..10 各一篇 75-105s 元层面导览（run = envpsy-ci1..ci10）。
规格差异（与正文批相比）：
  - 时长门禁下限 70s（正文批为 300s）；上限无硬门（用户裁决"只能多不能少"）。
  - 冻结门禁不变：≥20s 静止段命中即不打包留人工处置。
  - lesson_id = lesson-N-0-chapter-intro，字典序天然排每章最前。
course.json：合并式重建，标题更新为 48 件全集。
断点续跑：包目录存在即跳过；produce stage 哨兵可重入。
单课重跑：python -X utf8 _batch5.py envpsy-ciN
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0, str(ROOT))

import _first10 as F  # noqa: E402
import _freeze_check as FC  # noqa: E402

COURSE_DIR = F.COURSE_DIR
VL = F.VOICE_LABEL

MIN_TOTAL = 70.0  # 章绪论时长下限（秒）


def gate_freeze(final_mp4: Path):
    runs, _ = FC.freeze_windows(str(final_mp4))
    if runs:
        return False, f"冻结段: {runs}"
    return True, "无≥20s冻结"


def gate_duration(run: str):
    tm_p = ROOT / "audio" / f"timing_{run}.json"
    if not tm_p.exists():
        return False, "timing json 缺失"
    total = json.loads(tm_p.read_text(encoding="utf-8"))["total"]
    if total < MIN_TOTAL:
        return False, f"时长过短 {total:.0f}s < {MIN_TOTAL:.0f}s"
    return True, f"{total:.0f}s"


# (kind, run, chapter, lesson_id, title, kps, next_lesson, tl)
LESSONS = [
    dict(kind="new", run="envpsy-ci1",
         chapter="chapter-01", lesson_id="lesson-1-0-chapter-intro",
         title=f"第一章 章绪论——知觉：环境设计的入口（章绪论·{VL}）",
         kps=["钩子：同一个词四种人的四种答案", "章地图：流水线→视觉→听觉→嗅触动觉",
              "三关键词：感觉阈限/格式塔/多感官",
              "金句：设计不是摆弄形式，而是编排感觉"],
         next_lesson="下一节（1.1）：基于感觉和认知的知觉理论",
         tl=[("intro", "四种答案", 18), ("concept", "章地图四节点", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci2",
         chapter="chapter-02", lesson_id="lesson-2-0-chapter-intro",
         title=f"第二章 章绪论——环境知觉：谁在点亮世界（章绪论·{VL}）",
         kps=["钩子：喂给大脑还是大脑点亮世界", "章地图：提供→倒U→情绪坐标",
              "三关键词：提供/复杂性倒U/唤醒",
              "金句：人不是照相机，是求生的解释器"],
         next_lesson="下一节（2.1）：生态知觉理论",
         tl=[("intro", "百年之争", 18), ("concept", "章地图三节点", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci3",
         chapter="chapter-03", lesson_id="lesson-3-0-chapter-intro",
         title=f"第三章 章绪论——环境认知：脑中的城市地图（章绪论·{VL}）",
         kps=["钩子：黄桷湾立交 5 层 20 匝道（外部事实，2017）", "章地图：城市意象→成图研究→寻址命名",
              "三关键词：认知地图/五要素/易识别性",
              "金句：城市不仅立在土地上，也活在人脑中"],
         next_lesson="下一节（3.1）：早期的城市意象研究",
         tl=[("intro", "立交迷宫", 20), ("concept", "章地图三节点", 38),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci4",
         chapter="chapter-04", lesson_id="lesson-4-0-chapter-intro",
         title=f"第四章 章绪论——场景与场所：行为的舞台（章绪论·{VL}）",
         kps=["钩子：白天咖啡馆晚上酒吧", "章地图：行为场景→场所感→场所依恋",
              "三关键词：行为场景/场所感/场所依恋",
              "金句：场所不是容器，是行为与意义的舞台"],
         next_lesson="下一节（4.1）：行为场景",
         tl=[("intro", "一间屋子两种人生", 18), ("concept", "章地图三节点", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci5",
         chapter="chapter-05", lesson_id="lesson-5-0-chapter-intro",
         title=f"第五章 章绪论——环境应激：失衡的科学（章绪论·{VL}）",
         kps=["钩子：1936 塞利手术台的一刀", "章地图：过程→灾变→背景→个人",
              "三关键词：应激源/适应水平/应对资源",
              "金句：应激不是事件本身，是失衡的信号"],
         next_lesson="下一节（5.1）：应激过程研究",
         tl=[("intro", "塞利的发现", 18), ("concept", "章地图四节点", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci6",
         chapter="chapter-06", lesson_id="lesson-6-0-chapter-intro",
         title=f"第六章 章绪论——空间行为：距离的语法（章绪论·{VL}）",
         kps=["钩子：电梯里的半步", "章地图：个人空间→私密性→领域性→拥挤感",
              "三关键词：人际距离/私密性/领域",
              "金句：距离不是冷漠，是社交的语法"],
         next_lesson="下一节（6.1）：个人空间和人际距离",
         tl=[("intro", "电梯半步", 18), ("concept", "章地图四节点", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci7",
         chapter="chapter-07", lesson_id="lesson-7-0-chapter-intro",
         title=f"第七章 章绪论——感恩自然：天性的回响（章绪论·{VL}）",
         kps=["钩子：全人类统一的自然口味", "章地图：进化→情感→康复→行动",
              "三关键词：进化遗存/注意力恢复/亲环境行为",
              "金句：亲近自然不是情趣，是天性"],
         next_lesson="下一节（7.1）：在自然的孕育中进化",
         tl=[("intro", "统一口味之谜", 18), ("concept", "章地图四节点", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci8",
         chapter="chapter-08", lesson_id="lesson-8-0-chapter-intro",
         title=f"第八章 章绪论——景观偏爱：好恶的测量学（章绪论·{VL}）",
         kps=["钩子：壁纸选择与景观房溢价", "章地图：方法版图→四属性→评价意象",
              "三关键词：四属性/偏爱矩阵/评价意象",
              "金句：偏爱可以被测量，也可以被设计"],
         next_lesson="下一节（8.1）：研究方法和理论类别",
         tl=[("intro", "市价定价", 18), ("concept", "章地图三节点", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci9",
         chapter="chapter-09", lesson_id="lesson-9-0-chapter-intro",
         title=f"第九章 章绪论——外部公共空间：街道的生命（章绪论·{VL}）",
         kps=["钩子：古希腊广场到今日街角", "章地图：方法→内容→习性→实例",
              "三关键词：第三场所/行为习性/生气感",
              "金句：街道的生命在于活动，不在装饰"],
         next_lesson="下一节（9.1）：研究目的和方法",
         tl=[("intro", "三画面两千年", 20), ("concept", "章地图四节点", 38),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
    dict(kind="new", run="envpsy-ci10",
         chapter="chapter-10", lesson_id="lesson-10-0-chapter-intro",
         title=f"第十章 章绪论——建筑与行为：概率的学问（章绪论·{VL}）",
         kps=["钩子：1972 爆炸炸掉获奖住宅区", "章地图：三种建筑观→体验→认知+全书结语",
              "三关键词：或然论/建筑体验/易识别性",
              "金句：建筑给的不是答案，是概率与机会"],
         next_lesson="下一节（10.1）：建筑学中的一般应用",
         tl=[("intro", "一声爆炸", 18), ("concept", "章地图三节点+结语", 40),
             ("application", "关键词与衔接", 20), ("summary", "金句收束", 12)]),
]

CHAPTER_ORDER = ["chapter-00", "chapter-01", "chapter-02", "chapter-03",
                 "chapter-04", "chapter-05", "chapter-06", "chapter-07",
                 "chapter-08", "chapter-09", "chapter-10"]


def rebuild_course():
    course_p = COURSE_DIR / "course.json"
    course = json.loads(course_p.read_text(encoding="utf-8"))
    old = {c["chapter_id"]: c for c in course["chapters"]}
    new_title = {}
    for l in LESSONS:
        new_title.setdefault(l["chapter"], "")
    chapters = []
    for ch in CHAPTER_ORDER:
        rows = [dict(r) for r in old.get(ch, {}).get("lessons", [])]
        have = {r["lesson_id"] for r in rows}
        for l in [x for x in LESSONS if x["chapter"] == ch]:
            pkg = COURSE_DIR / ch / l["lesson_id"]
            if l["lesson_id"] in have or not pkg.exists():
                continue
            tm_p = ROOT / "audio" / f"timing_{l['run']}.json"
            dur = None
            if tm_p.exists():
                dur = round(json.loads(tm_p.read_text(encoding="utf-8"))["total"], 1)
            rows.append({"lesson_id": l["lesson_id"], "title": l["title"],
                         "duration": dur, "package": f"course/{ch}/{l['lesson_id']}"})
        if rows:
            rows.sort(key=lambda r: r["lesson_id"])
            title = old[ch]["title"] if ch in old else ""
            chapters.append({"chapter_id": ch, "title": title, "lessons": rows})
    course["chapters"] = chapters
    course["title"] = "环境心理学·系列课件（第一至五批：38 讲正文+10 章绪论·全书完整版）"
    course_p.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(c["lessons"]) for c in chapters)
    print(f"[course.json] {len(chapters)} chapters / {n} lessons", flush=True)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    prof_override = sys.argv[2] if len(sys.argv) > 2 else None
    results = []
    for lesson in LESSONS:
        if only and lesson["run"] != only:
            continue
        run = lesson["run"]
        pkg = COURSE_DIR / lesson["chapter"] / lesson["lesson_id"]
        if (pkg / "video.mp4").exists():
            print(f"[skip] {run} 已打包", flush=True)
            results.append((run, "skip"))
            continue
        t0 = time.time()
        ok, info = F.produce_new(run, profile=prof_override or
                                 "profiles/envpsy-intro.profile.yaml")
        if not ok:
            print(f"[FAIL] {run}: {info}", flush=True)
            results.append((run, "FAIL"))
            continue
        print(f"[done] {run} 生产 {time.time() - t0:.0f}s — {info[-120:]}", flush=True)
        dok, dmsg = gate_duration(run)
        if not dok:
            print(f"[GATE-DUR-FAIL] {run}: {dmsg}", flush=True)
            results.append((run, "FAIL-DUR"))
            continue
        final = ROOT / "runs" / run / "out" / f"final_{run}.mp4"
        fok, fmsg = gate_freeze(final)
        if not fok:
            print(f"[GATE-FREEZE-FAIL] {run}: {fmsg}（不打包，留人工处置）", flush=True)
            results.append((run, "FAIL-FREEZE"))
            continue
        print(f"[gate] {run} dur={dmsg} freeze=ok", flush=True)
        F.package(lesson)
        rebuild_course()
        results.append((run, "ok"))
    print("==== 第五批（章绪论）结果 ====", flush=True)
    for r, s in results:
        print(f"  {r}: {s}", flush=True)
    rebuild_course()


if __name__ == "__main__":
    main()
