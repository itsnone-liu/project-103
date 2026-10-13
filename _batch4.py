# -*- coding: utf-8 -*-
"""_batch4.py — 第四批六段视频批产驱动（2026-10-13 用户指令"完成批4"）。

9.2、9.3、9.4、10.1、10.2、10.3（全部新片，sol 高推理）——全书收官批。
沿袭批 3 双门禁：
  1. 时长下限：timing total < 300s 视为异常（批 3 实绩 325-416s）。
  2. 冻结门禁：produce 成功后扫成片 ≥20s 静止段，命中即不打包、
     标记 FAIL-FREEZE 留人工处置（捕获器 KP-011 帧号语义桥接兜底）。
- 生产：复用 _first10.produce_new（_run_produce.py 内部含健壮 STARTS 重写，
  兼容 Object.freeze 形态——批 2/3 已验证）。
- course.json：合并式重建，chapter-10 建筑环境与行为为新章。
断点续跑：包目录存在即跳过；produce stage 哨兵可重入。
单课重跑：python -X utf8 _batch4.py envpsy-XX
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0, str(ROOT))

import _first10 as F  # noqa: E402  复用 sh/produce_new/package
import _freeze_check as FC  # noqa: E402

COURSE_DIR = F.COURSE_DIR
VL = F.VOICE_LABEL


def gate_freeze(final_mp4: Path):
    """返回 (ok, msg)。≥20s 静止段命中 → 不打包。"""
    runs, _ = FC.freeze_windows(str(final_mp4))
    if runs:
        return False, f"冻结段: {runs}"
    return True, "无≥20s冻结"


def gate_duration(run: str):
    """返回 (ok, msg)。timing total < 300s 异常。"""
    tm_p = ROOT / "audio" / f"timing_{run}.json"
    if not tm_p.exists():
        return False, "timing json 缺失"
    total = json.loads(tm_p.read_text(encoding="utf-8"))["total"]
    if total < 300:
        return False, f"时长过短 {total:.0f}s"
    return True, f"{total:.0f}s"


# (kind, run, chapter, chapter_title, lesson_id, title, kps, next_lesson, tl)
LESSONS = [
    dict(kind="new", run="envpsy-92",
         chapter="chapter-09", chapter_title="第九章 外部公共空间活动研究",
         lesson_id="lesson-9-2-research-overview",
         title=f"研究内容概述——外部空间里的众生相（9.2·{VL}）",
         kps=["第三场所与《美国大城市的死与生》", "阻力和一致性步行模式",
              "城市规模与步速：都柏林 1.56 m/s", "圣何塞双广场的文化表征与话语权",
              "西特广场形状与 40 m²/人 生气感", "怀特七元素：坐处为首",
              "安全新解：踩点、灌木与智能照明"],
         next_lesson="下一节（9.3）：外部空间中的行为习性——抄近路、人看人与出神",
         tl=[("intro", "死与生开场", 20), ("concept", "第三场所", 40),
             ("concept", "步行法则", 45), ("application", "圣何塞双广场", 50),
             ("concept", "广场形状与生气感", 50), ("application", "怀特七元素", 50),
             ("application", "安全新解", 40), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-93",
         chapter="chapter-09", chapter_title="第九章 外部公共空间活动研究",
         lesson_id="lesson-9-3-behavior-habits",
         title=f"外部空间中的行为习性——抄近路、人看人与出神（9.3·{VL}）",
         kps=["动作性三习性：抄近路/逆时针/依靠性", "迪士尼草种：世界最佳园路设计",
              "依靠性与前景—庇护、形胜智慧", "看人也为人所看：张岱西湖七月半",
              "围观五级参与与广义学习", "凝思出神 being lost in thought",
              "靠右通行史与归巢兜圈"],
         next_lesson="下一节（9.4）：调查实例——深圳书城、成都茶馆与乐山个案",
         tl=[("intro", "三问开场", 20), ("concept", "动作三习性", 55),
             ("application", "迪士尼与依靠性设计", 45), ("concept", "人看人与围观", 50),
             ("concept", "安静与出神", 40), ("concept", "认知性习性", 40),
             ("application", "差异与设计启示", 45), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-94",
         chapter="chapter-09", chapter_title="第九章 外部公共空间活动研究",
         lesson_id="lesson-9-4-survey-cases",
         title=f"调查实例——深圳书城、成都茶馆与乐山个案（9.4·{VL}）",
         kps=["深圳漫游观察：木圈座与文化摊贩", "摊位成败：漂亮姐姐 vs 怪大叔",
              "成都吃讲茶：茶馆五大功能", "三位一体：喝茶麻将麻辣烫",
              "乐山数据：茶馆数与人口成正比", "分间布局/借景/生态联系三启示",
              "方法阶梯：漫游→专题→系统调查"],
         next_lesson="下一章（10.1）：建筑学中的一般应用——从决定论到或然论",
         tl=[("intro", "三城三法开场", 20), ("application", "深圳书城乐园", 60),
             ("application", "成都吃讲茶", 55), ("application", "乐山系统调查", 55),
             ("concept", "方法比较", 40), ("concept", "结语与展望", 35),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-101",
         chapter="chapter-10", chapter_title="第十章 建筑环境与行为",
         lesson_id="lesson-10-1-general-applications",
         title=f"建筑学中的一般应用——从决定论到或然论（10.1·{VL}）",
         kps=["建筑决定论三盲点", "普鲁蒂-艾戈：形式追随失败",
              "扬西解释：非正规空间与污名", "可能论/或然论/过滤器对比",
              "四合院改用与圆桌课室", "温莎四柱：坚固的暗示",
              "中国馆四红与长城肌理"],
         next_lesson="下一节（10.2）：建筑体验研究——偏爱从哪里来",
         tl=[("intro", "决定人之问", 20), ("concept", "决定论与艾戈悲剧", 60),
             ("concept", "三论对比", 55), ("application", "四合院与圆桌", 40),
             ("concept", "功能泛化", 55), ("application", "视错觉正用", 40),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-102",
         chapter="chapter-10", chapter_title="第十章 建筑环境与行为",
         lesson_id="lesson-10-2-experience-research",
         title=f"建筑体验研究——偏爱从哪里来（10.2·{VL}）",
         kps=["中国馆：四种红与长城形肌理", "SD 法与多项分类任务",
              "纳萨纵贯：落选者被评为更好", "绿化/历史/色彩三因素",
              "蓝领白领与最帅谷仓", "玻璃幕墙联结体最讨喜",
              "宽敞感手法清单与减拥挤三对策"],
         next_lesson="下一节（10.3）：建筑认知研究——意象、寻址与隐喻",
         tl=[("intro", "偏爱之问", 20), ("application", "中国馆视错觉", 40),
             ("concept", "研究方法", 40), ("application", "纳萨纵贯", 35),
             ("concept", "三因素", 50), ("concept", "群体差异", 40),
             ("concept", "协调宽敞围合", 60), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-103",
         chapter="chapter-10", chapter_title="第十章 建筑环境与行为",
         lesson_id="lesson-10-3-cognition-research",
         title=f"建筑认知研究——意象、寻址与隐喻（10.3·{VL}）",
         kps=["意象三来源：使用/可见性/形式", "绰号建筑学与轮廓关键性",
              "认知距离：信息贮存与努力假设", "O'Neill 5×3：+13%/-50%/-62%",
              "标志悖论：医院走廊与火灾 8%", "隐喻：一塔湖图与天平地不平",
              "金色便便等反例与全书结语"],
         next_lesson="本课完结——感谢观看环境心理学系列课件",
         tl=[("intro", "三问开场", 15), ("concept", "意象三来源", 45),
             ("application", "绰号建筑学", 30), ("concept", "认知距离", 40),
             ("concept", "易识别与标志", 50), ("concept", "拓扑与定向建议", 40),
             ("concept", "隐喻与象征", 40), ("application", "收官与结语", 50),
             ("summary", "小结", 15)]),
]

CHAPTER_ORDER = ["chapter-00", "chapter-01", "chapter-02", "chapter-03",
                 "chapter-04", "chapter-05", "chapter-06", "chapter-07",
                 "chapter-08", "chapter-09", "chapter-10"]


def rebuild_course():
    """合并式：现有 course.json 章课保留，本批新课按 lesson_id 并入。"""
    course_p = COURSE_DIR / "course.json"
    course = json.loads(course_p.read_text(encoding="utf-8"))
    old = {c["chapter_id"]: c for c in course["chapters"]}
    new_title = {}
    for l in LESSONS:
        new_title.setdefault(l["chapter"], l["chapter_title"])
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
            title = old[ch]["title"] if ch in old else new_title[ch]
            chapters.append({"chapter_id": ch, "title": title, "lessons": rows})
    course["chapters"] = chapters
    course["title"] = "环境心理学·系列课件（第一至四批共三十六课试产）"
    course_p.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(c["lessons"]) for c in chapters)
    print(f"[course.json] {len(chapters)} chapters / {n} lessons", flush=True)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
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
        ok, info = F.produce_new(run)
        if not ok:
            print(f"[FAIL] {run}: {info}", flush=True)
            results.append((run, "FAIL"))
            continue
        print(f"[done] {run} 生产 {time.time() - t0:.0f}s — {info[-120:]}", flush=True)
        # 门禁 1：时长下限
        dok, dmsg = gate_duration(run)
        if not dok:
            print(f"[GATE-DUR-FAIL] {run}: {dmsg}", flush=True)
            results.append((run, "FAIL-DUR"))
            continue
        # 门禁 2：冻结扫描（兜底 KP-011 桥接）
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
    print("==== 第四批结果 ====", flush=True)
    for r, s in results:
        print(f"  {r}: {s}", flush=True)
    rebuild_course()


if __name__ == "__main__":
    main()
