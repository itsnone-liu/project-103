# -*- coding: utf-8 -*-
"""_batch6.py — 第六批：设计案例片（2026-10-13 用户批准"论文框架+生动活泼"与图纸组合方案）。

案例片 = 设计论文六段文体 × 工程图纸视觉母语 × 纪录片叙事（无真人镜头）。
规格：每片目标 ~600s（10 分钟），时长门禁下限 570s；冻结门禁 ≥20s 不打包。
新章 chapter-11（案例研究）。单课重跑：python -X utf8 _batch6.py envpsy-caseN [profileOverride]
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

MIN_TOTAL = 570.0  # 案例片时长下限（秒）——用户裁决"只能多不能少"

# (kind, run, chapter, lesson_id, title, kps, next_lesson, tl)
LESSONS = [
    dict(kind="new", run="envpsy-case1",
         chapter="chapter-11", lesson_id="lesson-11-1-case-times-square",
         title=f"案例研究A——抢街：时代广场的人本改造（设计案例·{VL}）",
         kps=["问题：4500万人年访客的广场却无人驻留", "理论框架：怀特/盖尔观察法·感觉超载与倒U·密度≠拥挤",
              "诊断：2008四病灶（零驻留/超载/高密度高拥挤/几何死结）",
              "策略：72小时油漆+折叠椅试点；椅子=控制感·涂装=领域提示·禁车=负荷削减",
              "检验：NYC DOT数据（车内伤↓63%/行人伤↓35%/走车道↓80%/步行↑11%/支持率74%）",
              "永久化：Snøhetta公共空间翻倍·黑花岗岩光影·集会台阶",
              "结论：证据先行·轻量可逆试验·人本非零和"],
         next_lesson="下一案例（B）：北京杨梅竹斜街微更新——同一套透镜的东方语境",
         tl=[("intro", "世界十字路口的悖论", 55), ("concept", "三个理论透镜", 85),
             ("diagnosis", "2008四病灶", 90), ("strategy", "油漆与折叠椅", 105),
             ("evidence", "数据与永久化", 130), ("conclusion", "三条结论", 85),
             ("outro", "作业与预告", 50)]),
]

CHAPTER_ORDER = ["chapter-00", "chapter-01", "chapter-02", "chapter-03",
                 "chapter-04", "chapter-05", "chapter-06", "chapter-07",
                 "chapter-08", "chapter-09", "chapter-10", "chapter-11"]

NEW_CHAPTER_TITLES = {"chapter-11": "第十一章 案例研究——理论的设计应用"}


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


def rebuild_course():
    course_p = COURSE_DIR / "course.json"
    course = json.loads(course_p.read_text(encoding="utf-8"))
    old = {c["chapter_id"]: c for c in course["chapters"]}
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
            title = old.get(ch, {}).get("title") or NEW_CHAPTER_TITLES.get(ch, "")
            chapters.append({"chapter_id": ch, "title": title, "lessons": rows})
    course["chapters"] = chapters
    course["title"] = "环境心理学·系列课件（第一至六批：38 讲正文+10 章绪论+案例研究·完整版）"
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
                                 "profiles/envpsy-case.profile.yaml")
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
    print("==== 第六批（设计案例）结果 ====", flush=True)
    for r, s in results:
        print(f"  {r}: {s}", flush=True)
    rebuild_course()


if __name__ == "__main__":
    main()
