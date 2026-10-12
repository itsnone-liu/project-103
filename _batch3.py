# -*- coding: utf-8 -*-
"""_batch3.py — 第三批十段视频批产驱动（2026-10-12 用户指令）。

6.3、6.4、7.1、7.2、7.3、7.4、8.1、8.2、8.3、9.1（全部新片，sol 高推理）。
本批新增防线（吸取 4.3/5.1 教训）：
  1. 冻结门禁：produce 成功后立即扫成片 ≥20s 静止段，命中即不打包、标记
     FAIL-FREEZE 留人工处置（捕获器已带 KP-011 帧号语义桥接，此处兜底）。
  2. 时长下限：timing total < 300s 视为异常（前两批实绩 353-439s）。
- 生产：复用 _first10.produce_new（_run_produce.py 内部含健壮 STARTS 重写，
  兼容 Object.freeze 形态——批 2 已验证）。
- course.json：合并式重建，chapter-07/08/09 为新章。
断点续跑：包目录存在即跳过；produce stage 哨兵可重入。
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
    dict(kind="new", run="envpsy-63",
         chapter="chapter-06", chapter_title="第六章 空间行为",
         lesson_id="lesson-6-3-territoriality",
         title=f"领域性——占有与防卫的空间策略（6.3·{VL}）",
         kps=["阿尔托曼定义：占用+人格化+防卫", "战俘营与日本灾民避难的领域本能",
              "主要/次要/公共三类型", "领域三功能：认知社会/控制感/安全防卫",
              "纽曼能防卫空间四原则", "306户被盗调查：领域标志与自然监视",
              "城中村牌坊：我的领域我做主"],
         next_lesson="下一节（6.4）：密度与拥挤感——老鼠乌托邦的崩溃与人类的两难",
         tl=[("intro", "战俘营的狐狸洞", 20), ("concept", "定义与证据", 50),
             ("concept", "三类型", 55), ("concept", "三功能", 50),
             ("application", "能防卫空间", 60), ("application", "被盗调查与城中村", 40),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-64",
         chapter="chapter-06", chapter_title="第六章 空间行为",
         lesson_id="lesson-6-4-density-crowding",
         title=f"密度与拥挤感——老鼠乌托邦的崩溃与人类的两难（6.4·{VL}）",
         kps=["卡尔霍恩老鼠行为堕落实验", "社会密度 vs 空间密度",
              "短期实验：情绪/攻击/绩效三发现", "监狱、宿舍与助人行为研究",
              "密度—强度理论与工体国骂", "拥挤感三解释：信息超载/行为约束/人员过剩",
              "阿尔托曼模式：控制感是关键"],
         next_lesson="下一章（7.1）：在自然的孕育中进化——从大裂谷走出的我们",
         tl=[("intro", "老鼠乌托邦", 20), ("concept", "两类密度", 55),
             ("application", "短期实验三发现", 55), ("application", "监狱宿舍与助人", 55),
             ("concept", "密度强度与影响因素", 50), ("concept", "三种理论解释", 50),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-71",
         chapter="chapter-07", chapter_title="第七章 感恩自然",
         lesson_id="lesson-7-1-evolution-in-nature",
         title=f"在自然的孕育中进化——从大裂谷走出的我们（7.1·{VL}）",
         kps=["自然四分类：纯/开化/准/半自然", "灾变推动进化：多巴火山与基因瓶颈",
              "大裂谷的环境提供：领域与庇护所", "探索行为：广泛与特殊（神农看/尝百草）",
              "投掷、追逐与旧石器：有益性法则", "狮首人身雕像：概念形成与认知飞跃",
              "生态理性：有限理性与直觉遗存"],
         next_lesson="下一节（7.2）：人类基本情感反应的来源——敬畏、恐惧与愉悦",
         tl=[("intro", "感恩自然开场", 20), ("concept", "四分类", 45),
             ("concept", "灾变与进化", 55), ("concept", "大裂谷提供", 45),
             ("concept", "探索行为", 45), ("application", "投掷与旧石器", 40),
             ("concept", "认知与生态理性", 50), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-72",
         chapter="chapter-07", chapter_title="第七章 感恩自然",
         lesson_id="lesson-7-2-emotional-origins",
         title=f"人类基本情感反应的来源——敬畏、恐惧与愉悦（7.2·{VL}）",
         kps=["敬畏=惊讶+恐惧：山神水神与转湖三瓢", "黑夜恐惧与第一夜效应（大脑值夜班）",
              "人脸错视：FFA 0.165秒与猛兽的脸", "满月恐惧：狮子袭击的月亮周期",
              "蛇类检测理论：优势眼与婴儿ERP", "前景—庇护所假设",
              "疏林草原偏爱：五生物群落实验"],
         next_lesson="下一节（7.3）：自然环境在当代的作用——从敬畏符号到康复环境",
         tl=[("intro", "敬畏开场", 20), ("concept", "敬畏之心", 35),
             ("concept", "黑夜与第一夜", 55), ("concept", "人脸错视与满月", 55),
             ("concept", "蛇虫恐惧", 45), ("concept", "前景庇护所", 40),
             ("concept", "疏林草原偏爱", 45), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-73",
         chapter="chapter-07", chapter_title="第七章 感恩自然",
         lesson_id="lesson-7-3-nature-today",
         title=f"自然环境在当代的作用——从敬畏符号到康复环境（7.3·{VL}）",
         kps=["畏惧的蜕变：符号化与紫禁城层次", "愉悦的印记：上树避难与鲜花果实",
              "乌尔里希病房研究：窗景与康复", "应激缓解理论 SRT",
              "注意力恢复理论 ART 四属性", "北京公园水体比率与耕读传家",
              "感知流畅与分形自相似"],
         next_lesson="下一节（7.4）：亲环境行为——从破窗到养成",
         tl=[("intro", "开场钩子", 20), ("concept", "畏惧蜕变", 45),
             ("concept", "愉悦印记", 35), ("application", "病房研究", 45),
             ("concept", "ART四属性", 55), ("application", "湖泊调查与耕读", 50),
             ("concept", "感知流畅与分形", 40), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-74",
         chapter="chapter-07", chapter_title="第七章 感恩自然",
         lesson_id="lesson-7-4-proenvironment",
         title=f"亲环境行为——从价值信念到破窗治理（7.4·{VL}）",
         kps=["定义与正名：与环保激进主义之别", "VBN：价值—信念—规范三维度",
              "表里不一：环境远视与知行不一", "同情移情与好恶美丑（颜值保护）",
              "社会规范：禁令性 vs 约定习惯", "破窗假设与格罗宁根涂鸦实验",
              "改变习惯：警告桩为何失效"],
         next_lesson="下一章（8.1）：景观偏爱研究——方法与理论的版图",
         tl=[("intro", "开场钩子", 20), ("concept", "定义正名", 40),
             ("concept", "VBN理论", 50), ("concept", "表里不一", 45),
             ("concept", "好恶与物种保护", 45), ("application", "破窗与杂乱蔓延", 55),
             ("application", "改变习惯", 40), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-81",
         chapter="chapter-08", chapter_title="第八章 景观偏爱研究",
         lesson_id="lesson-8-1-methods-theories",
         title=f"研究方法和理论类别——从风景画到评价成图（8.1·{VL}）",
         kps=["landscape 词源：从风景画到心田", "评价五模式：生态/形式美/心理生理/心理/现象学",
              "专家三原理：框景/会聚/对比", "德尔菲法与物质—知觉法",
              "受众三法：改进SD/SBE/评价成图", "襄樊评价地图：火车站为何最不受待见",
              "理论三类别：进化/文化/折中"],
         next_lesson="下一节（8.2）：影响即时景观偏爱的因素——四种属性与神秘性",
         tl=[("intro", "词源开场", 20), ("concept", "五模式", 45),
             ("concept", "专家三原理", 55), ("concept", "受众三法", 55),
             ("application", "评价成图实例", 45), ("concept", "理论类别", 35),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-82",
         chapter="chapter-08", chapter_title="第八章 景观偏爱研究",
         lesson_id="lesson-8-2-instant-preference",
         title=f"影响即时景观偏爱的因素——四种属性与神秘性（8.2·{VL}）",
         kps=["四属性：连贯/易识别/复杂/神秘", "卡普兰偏爱矩阵：理解×探索",
              "神秘性：曲率与危险的两难", "能见度与进出通道",
              "转角效应：虚拟环境与桃花源", "九属性构想",
              "进化偏爱：对称、抽象与可畏异化"],
         next_lesson="下一节（8.3）：基于意象的场所外观评价——好恶的地图",
         tl=[("intro", "开场钩子", 20), ("concept", "四属性", 55),
             ("concept", "偏爱矩阵", 50), ("concept", "神秘性研究", 50),
             ("application", "转角与桃花源", 50), ("concept", "九属性", 30),
             ("concept", "进化偏爱", 35), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-83",
         chapter="chapter-08", chapter_title="第八章 景观偏爱研究",
         lesson_id="lesson-8-3-appraisal-images",
         title=f"基于意象的场所外观评价——好恶的地图（8.3·{VL}）",
         kps=["评价意象：愉悦激动放松紧张", "本能/认知/审美三类反应",
              "图式理论：一致—不一致—偏爱曲线", "纳萨正面属性七项",
              "泰姬陵与身份象征", "负面属性：气氛恐惧与陷阱景观",
              "文化差异：障景先抑后扬与泄愤屋"],
         next_lesson="下一章（9.1）：外部公共空间活动研究——目的与方法",
         tl=[("intro", "开场钩子", 20), ("concept", "三类反应", 55),
             ("concept", "图式理论", 50), ("concept", "正面属性", 55),
             ("application", "泰姬陵", 30), ("concept", "负面属性", 50),
             ("application", "文化差异", 40), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-91",
         chapter="chapter-09", chapter_title="第九章 外部公共空间活动研究",
         lesson_id="lesson-9-1-purpose-methods",
         title=f"研究目的和方法——观察城市的五种姿势（9.1·{VL}）",
         kps=["研究目的：行为规律与异用现象", "五W法及其简化",
              "单一因素研究：行道树实验", "行为观察四种：介入/旁观/隐蔽/漫游",
              "行为痕迹推测：牛粪指路", "参与性成图与网络地图",
              "从里坊宵禁到中央公园"],
         next_lesson="下一节（9.2）：研究内容概述——外部空间里的众生相",
         tl=[("intro", "开场钩子", 20), ("concept", "目的与异用", 45),
             ("concept", "五W法", 45), ("concept", "单一因素", 35),
             ("application", "观察四法", 60), ("application", "痕迹推测", 45),
             ("concept", "参与性成图", 35), ("summary", "小结", 15)]),
]

CHAPTER_ORDER = ["chapter-00", "chapter-01", "chapter-02", "chapter-03",
                 "chapter-04", "chapter-05", "chapter-06", "chapter-07",
                 "chapter-08", "chapter-09"]


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
    course["title"] = "环境心理学·系列课件（第一至三批共三十课试产）"
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
    print("==== 第三批结果 ====", flush=True)
    for r, s in results:
        print(f"  {r}: {s}", flush=True)
    rebuild_course()


if __name__ == "__main__":
    main()
