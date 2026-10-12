# -*- coding: utf-8 -*-
"""_next10.py — 第二批十段视频批产驱动（2026-10-12 用户指令）。

按章节顺序：3.2、3.3、4.1、4.2、4.3、5.1、5.2、5.3、5.4、6.2（全部新片，sol 高推理）。
- 生产：复用 _first10 的 produce_new（sol --effort high + cosy 龙小淳）。
- 打包：只做视频 + 数据接口（同第一批格式）。
- course.json：合并式重建——保留现有章课（00-03 已有 + 06 种子），追加本批新课，
  按 lesson_id 排序；chapter-04/05 为新章。
断点续跑：包目录存在即跳过；produce 自带 stage 哨兵可重入。
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0, str(ROOT))

import _first10 as F  # noqa: E402  复用 sh/produce_new/package

COURSE_DIR = F.COURSE_DIR
VL = F.VOICE_LABEL

# (kind, run, chapter, chapter_title, lesson_id, title, kps, next_lesson, tl)
LESSONS = [
    dict(kind="new", run="envpsy-32",
         chapter="chapter-03", chapter_title="第三章 环境认知",
         lesson_id="lesson-3-2-image-followup",
         title=f"城市意象的后续研究——从五要素到日常生活（3.2·{VL}）",
         kps=["拉普波特三因素与米尔格拉姆再认公式", "场所—路径—领域三要素（诺伯-舒兹）",
              "海淀镇、台北、汉正街三个中国案例", "无意识记与寻址提示元素",
              "中等尺度环境认知：问卷 vs GIS", "空间句法：连通性、集成性与可理解性",
              "认知距离：400m 分界与乡村两倍效应"],
         next_lesson="下一节（3.3）：空间定向与场所命名——大脑里的 GPS 与街名的学问",
         tl=[("intro", "开场钩子", 20), ("concept", "三因素与再认公式", 60),
             ("concept", "场所路径领域", 35), ("application", "三个中国案例", 80),
             ("concept", "中等尺度认知", 40), ("concept", "空间句法与认知距离", 50),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-33",
         chapter="chapter-03", chapter_title="第三章 环境认知",
         lesson_id="lesson-3-3-wayfinding-naming",
         title=f"空间定向与场所命名——大脑里的 GPS 与街名的学问（3.3·{VL}）",
         kps=["位置细胞、边界细胞与网格细胞", "定向策略三主因子（德国 4000 人调查）",
              "定向系统的文化差异：网格/放射/八卦城", "环境改变与定向混乱（环路高架）",
              "场所命名四注意：好记/谐音/歧义/洋地名", "地名是城市记忆与文化图式"],
         next_lesson="下一章（4.1）：行为场景——巴克与人生大舞台",
         tl=[("intro", "开场钩子", 20), ("concept", "大脑里的三类细胞", 55),
             ("concept", "定向策略三因子", 40), ("application", "定向的文化差异", 60),
             ("application", "场所命名四注意", 85), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-41",
         chapter="chapter-04", chapter_title="第四章 场景和场所研究",
         lesson_id="lesson-4-1-behavior-settings",
         title=f"行为场景——巴克与人生大舞台（4.1·{VL}）",
         kps=["勒温 B=f(P,E) 与巴克中西部现场站", "行为场景定义与同步形态",
              "场景四属性：整体/依赖/固定/边界", "三组成：物质环境/参与人员/程式",
              "后续探讨：背景因素、意义建构与广场舞进化", "应用：场景复兴（兰亭蒲团）与管理",
              "评价：生态心理学基石与长期沉寂"],
         next_lesson="下一节（4.2）：场所感——空间如何变成『我的地方』",
         tl=[("intro", "开场钩子", 20), ("concept", "巴克与现场站", 45),
             ("concept", "从儿童观察到定义", 60), ("concept", "四属性与三组成", 55),
             ("application", "场景会进化", 55), ("application", "复兴与管理", 45),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-42",
         chapter="chapter-04", chapter_title="第四章 场景和场所研究",
         lesson_id="lesson-4-2-sense-of-place",
         title=f"场所感——空间如何变成『我的地方』（4.2·{VL}）",
         kps=["场所感三维度：依赖/认同/依恋", "同一性与差异性（康平路/下只角）",
              "钱俊希广州研究：城市与社区尺度", "古斯塔夫森模型：自我/环境/他人",
              "曼左纽约研究与意义之网", "多场所分析：罗马 vs 莱切"],
         next_lesson="下一节（4.3）：场所依恋——为什么我们会爱上一个地方",
         tl=[("intro", "开场钩子", 20), ("concept", "三个维度", 70),
             ("concept", "影响因素与尺度", 40), ("concept", "场所的意义两模型", 60),
             ("application", "多场所分析", 45), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-43",
         chapter="chapter-04", chapter_title="第四章 场景和场所研究",
         lesson_id="lesson-4-3-place-attachment",
         title=f"场所依恋——为什么我们会爱上一个地方（4.3·{VL}）",
         kps=["3P 模型：人—过程—场所", "依恋的阴影面与图式机制",
              "尺度 U 形关系与华沙修正", "三功能：安全/连续性/自我实现",
              "哈洛恒河猴实验", "吉庆街的拆与归：四铁与场景载体"],
         next_lesson="下一章（5.1）：应激过程——从警报到成长的三级火箭",
         tl=[("intro", "情感与情绪之分", 20), ("concept", "3P 模型", 65),
             ("concept", "尺度 U 形", 35), ("concept", "三种功能", 55),
             ("application", "吉庆街的拆与归", 60), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-51",
         chapter="chapter-05", chapter_title="第五章 环境应激",
         lesson_id="lesson-5-1-stress-process",
         title=f"应激过程——从警报到成长的三级火箭（5.1·{VL}）",
         kps=["塞利 GAS：警戒/抵抗/衰竭", "应激源三分类",
              "认知图式与控制感（桑枣中学/福岛）", "行为反应：0.018 秒母亲与迁怒",
              "应对策略：情绪应对 vs 问题应对", "习得性无助及其边界",
              "创伤后成长 PTG 与瑞典森林大火研究"],
         next_lesson="下一节（5.2）：灾变事件——信息、认知缺失与漫长的后效",
         tl=[("intro", "开场钩子", 20), ("concept", "三级警报 GAS", 55),
             ("concept", "认知与控制感", 55), ("concept", "行为反应与应对", 45),
             ("concept", "习得性无助", 30), ("application", "创伤后成长", 60),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-52",
         chapter="chapter-05", chapter_title="第五章 环境应激",
         lesson_id="lesson-5-2-catastrophe",
         title=f"灾变事件——信息、认知缺失与漫长的后效（5.2·{VL}）",
         kps=["三类灾变与五个共同点", "小道消息为何跑赢官方发布",
              "松潘 1976 成功预报", "认知缺失现象（汶川实录）",
              "反应多样性：麻木到恍惚", "后效差异：福岛野猪与切尔诺贝利静寂",
              "认知偏差：可利用性法则与天灾人祸之别"],
         next_lesson="下一节（5.3）：城市背景应激源——噪声、雾霾与靴子落地",
         tl=[("intro", "开场钩子", 20), ("concept", "分类与共性", 35),
             ("application", "灾变信息的认知", 70), ("application", "认知缺失与反应谱", 55),
             ("concept", "后效的差异性", 65), ("concept", "认知偏差三条", 40),
             ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-53",
         chapter="chapter-05", chapter_title="第五章 环境应激",
         lesson_id="lesson-5-3-background-stressors",
         title=f"城市背景应激源——噪声、雾霾与靴子落地（5.3·{VL}）",
         kps=["背景应激源定义与三类现象学", "热岛效应与农民工应激",
              "雾霾认知觉醒（2011）与 PM2.5", "噪声评价三尺子：响度/预见性/控制感",
              "耳聋发病率曲线 80/90/100dB", "珠三角调查：噪声 77% 与夜晚靴子声",
              "治理：立法、不许时间与惩罚"],
         next_lesson="下一节（5.4）：个人应激源——量表、敏感噪声与刮黑板的科学",
         tl=[("intro", "开场钩子", 20), ("concept", "三类与热岛", 40),
             ("application", "雾霾与 PM2.5", 55), ("concept", "噪声三把尺子", 65),
             ("application", "一线调查：靴子落地", 55), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-54",
         chapter="chapter-05", chapter_title="第五章 环境应激",
         lesson_id="lesson-5-4-personal-stressors",
         title=f"个人应激源——量表、敏感噪声与刮黑板的科学（5.4·{VL}）",
         kps=["Holmes-Rahe 生活事件量表（38 项）", "中国特色应激源清单",
              "敏感噪声：无法适应的耳朵边", "低频噪声：500Hz 以下穿透楼板",
              "特异噪声四敏感与进化解释", "杏仁核与刮黑板声音科学",
              "缓解之道的批判：没有万灵药"],
         next_lesson="下一章（6.2）：私密性——选择与控制的艺术",
         tl=[("intro", "稻草开场", 20), ("concept", "生活事件量表", 50),
             ("application", "敏感噪声", 55), ("concept", "特异噪声四敏感", 70),
             ("application", "缓解之道批判", 45), ("summary", "小结", 15)]),
    dict(kind="new", run="envpsy-62",
         chapter="chapter-06", chapter_title="第六章 空间行为",
         lesson_id="lesson-6-2-privacy",
         title=f"私密性——选择与控制的艺术（6.2·{VL}）",
         kps=["奥尔特曼定义：选择性控制", "ATM/AVM/TVM 人际距离实验",
              "六种类型与五种心理作用", "缺乏私密性的代价（淘大花园）",
              "设计应用：视听控制/层次梯度/焦虑阈", "赖特切内住宅挡墙",
              "三文化焦虑阈对比"],
         next_lesson="下一节（6.3）：领域性——占有与防卫的空间策略（待制作）",
         tl=[("intro", "开场钩子", 20), ("concept", "定义与证据", 40),
             ("concept", "六类型五作用", 65), ("application", "缺乏的代价", 35),
             ("application", "设计应用三式", 70), ("application", "注意事项", 30),
             ("summary", "小结", 15)]),
]

CHAPTER_ORDER = ["chapter-00", "chapter-01", "chapter-02", "chapter-03",
                 "chapter-04", "chapter-05", "chapter-06"]


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
    course["title"] = "环境心理学·系列课件（第一、二批共二十课试产）"
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
        F.package(lesson)
        rebuild_course()
        results.append((run, "ok"))
    print("==== 第二批结果 ====", flush=True)
    for r, s in results:
        print(f"  {r}: {s}", flush=True)
    rebuild_course()


if __name__ == "__main__":
    main()
