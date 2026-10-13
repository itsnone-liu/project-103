# -*- coding: utf-8 -*-
"""_first10.py — 前十段视频批产驱动（2026-10-11 用户指令）。

按章节顺序：绪论(换声)、1.1、1.2①、1.2②、1.3、1.4、2.1、2.2+2.3、2.4、3.1①(换声)。
- 新片：sol 模型走 pipeline.produce 全链（scene voice 默认 cosy 龙小淳）。
- 换声：复制旧 run → audio.py tts(重试循环) → STARTS 重写 → web2d.render → qa → mux。
- 打包：只做视频 + 数据接口（lesson.json / interactions.json 空 cues / transcript.vtt / summary.json），
  并重写 course.json（chapter-00..03 + 保留 chapter-06）。
断点续跑：包目录存在即跳过；produce 自带 stage 哨兵可重入。
"""
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0, str(ROOT))

COURSE_DIR = ROOT / "lesson-runtime" / "course"
VOICE = "cosy:cosyvoice-v2/longxiaochun_v2"
VOICE_LABEL = "龙小淳(知性积极女)"

# (kind, src_run, run, chapter, chapter_title, lesson_id, title, kps, next_lesson, timeline_secs)
# timeline_secs: [(type, topic, 目标秒)] 按句数比例落位
LESSONS = [
    dict(kind="revoice", src="envpsy-t3-intro", run="envpsy-intro-cosy",
         chapter="chapter-00", chapter_title="绪论",
         lesson_id="lesson-intro",
         title=f"环境心理学是什么——环境·行为研究的开场白（绪论·{VOICE_LABEL}）",
         kps=["环境心理学的定义与研究对象", "环境—行为研究的特点：源于实际生活、跨学科",
              "新研究动向：景观评价与偏爱、自然环境的积极影响"],
         next_lesson="下一节（1.1）：感觉、知觉与认知——环境信息的加工流水线",
         tl=[("intro", "学科开场", 20), ("concept", "环境心理学定义与特点", 90),
             ("concept", "研究动向与领域", 70), ("summary", "小结", 20)]),
    dict(kind="new", src=None, run="envpsy-11",
         chapter="chapter-01", chapter_title="第一章 知觉研究及其设计应用",
         lesson_id="lesson-1-1-perception-chain",
         title=f"感觉、知觉与认知——环境信息的加工流水线（1.1·{VOICE_LABEL}）",
         kps=["感觉/知觉/认知三级流水线", "绝对阈限：下阈限与上阈限", "感觉剥夺实验与托蒂案例",
              "图式、同化与顺化（皮亚杰）", "耶文斯黑豆实验与注意广度 7 临界",
              "知觉定势、习惯化适应、韦伯-费希纳定律"],
         next_lesson="下一节（1.2①）：看世界的三种方式——视知觉功能与格式塔组织",
         tl=[("intro", "鸟鸣开场", 25), ("concept", "感觉：采集与阈限", 55),
             ("concept", "知觉与认知：组织与图式", 70), ("concept", "鸟鸣流水线模型", 45),
             ("application", "流水线的三个 bug", 75), ("summary", "小结", 15)]),
    dict(kind="new", src=None, run="envpsy-12a",
         chapter="chapter-01", chapter_title="第一章 知觉研究及其设计应用",
         lesson_id="lesson-1-2a-vision-gestalt",
         title=f"看世界的三种方式——视知觉功能与格式塔组织（1.2①·{VOICE_LABEL}）",
         kps=["中央凹（2°圆锥·视平线下 10°）与视敏度", "黄斑（12°-15°）与阅读",
              "周围视觉：运动夸大与隧道/林荫道设计", "点划式扫描与注视点（西湖 vs 东湖）",
              "格式塔：图底之分与鲁宾两可图", "群化四则：邻近/相似/连续/封闭", "简化原则与良好完形"],
         next_lesson="下一节（1.2②）：眼见未必为实——视错觉与设计",
         tl=[("intro", "霍尔论中央凹", 20), ("concept", "三种视觉功能", 80),
             ("concept", "扫描规律", 60), ("concept", "格式塔组织规律", 100), ("summary", "小结", 15)]),
    dict(kind="new", src=None, run="envpsy-12b",
         chapter="chapter-01", chapter_title="第一章 知觉研究及其设计应用",
         lesson_id="lesson-1-2b-illusion",
         title=f"眼见未必为实——视错觉与设计（1.2②·{VOICE_LABEL}）",
         kps=["似动三兄弟：自动/闪动/诱动", "深圳 1999 与成都 2008 群体事件",
              "平面构成错觉（吐鲁番宾馆/咖啡墙）", "坡度错觉：缓坡看成平路（Hajnal 2016）",
              "漂浮错觉与精神病院走廊", "怪相错觉（Caputo 2010）与特罗勒效应",
              "黑体字错觉：下划线 1/8-1/6 字高"],
         next_lesson="下一节（1.3）：听建筑——听知觉、声景与环境设计",
         tl=[("intro", "深圳狂奔事件", 20), ("concept", "似动错觉", 70),
             ("concept", "平面构成与街头立体画", 40), ("application", "坡度错觉", 55),
             ("application", "漂浮与怪相错觉", 60), ("application", "黑体字错觉与策略二分", 35), ("summary", "小结", 15)]),
    dict(kind="new", src=None, run="envpsy-13",
         chapter="chapter-01", chapter_title="第一章 知觉研究及其设计应用",
         lesson_id="lesson-1-3-soundscape",
         title=f"听建筑——听知觉、声景与环境设计（1.3·{VOICE_LABEL}）",
         kps=["听觉：在场感的充分条件（聖字）", "经典声学应用：回音壁/德和园/维特鲁威共鸣缸",
              "园林听景家族与八景传统", "声源三分：固体/液体/空气（Gaver）",
              "声音事件：上海弄堂清晨", "声景（soundscape）：谢弗到日本百佳与佐贺匹配研究",
              "声景评价四因：因人/因地/因时/因文化"],
         next_lesson="下一节（1.4）：鼻尖、手底、脚下——嗅觉触觉动觉与环境设计",
         tl=[("intro", "聖字开场", 20), ("concept", "经典应用", 65),
             ("concept", "听觉造景", 50), ("concept", "生态听觉研究", 60),
             ("application", "声景研究与四因", 60), ("summary", "小结", 15)]),
    dict(kind="new", src=None, run="envpsy-14",
         chapter="chapter-01", chapter_title="第一章 知觉研究及其设计应用",
         lesson_id="lesson-1-4-other-senses",
         title=f"鼻尖、手底、脚下——嗅觉触觉动觉与环境设计（1.4·{VOICE_LABEL}）",
         kps=["嗅觉难表述（3M 广告）", "园林香景与听香境界、禅机案例",
              "气味偏爱实验：情感反应主导（Schloss 2015）", "触觉：铺地即路标",
              "动觉：汀步与步移景异", "热觉与味觉：景不靓美食凑"],
         next_lesson="下一节（2.1）：环境的提供——生态知觉理论",
         tl=[("intro", "3M 三排比", 20), ("concept", "嗅觉：难说却难忘", 80),
             ("concept", "触觉：质感是路标", 45), ("application", "动觉：身体的镜头语言", 55),
             ("application", "温度气流与味觉", 35), ("summary", "小结", 15)]),
    dict(kind="new", src=None, run="envpsy-21",
         chapter="chapter-02", chapter_title="第二章 环境知觉",
         lesson_id="lesson-2-1-affordance",
         title=f"环境的提供——生态知觉理论（2.1·{VOICE_LABEL}）",
         kps=["吉布森与直接知觉理论", "视觉悬崖：90% 婴儿拒绝爬过（Gibson & Walk）",
              "光阵列与质感梯度", "提供（affordance）：环境的功用可能性",
              "寓知觉于行动：TTC 与 Tau 理论", "提供三分类：虚假/隐藏/可察觉（Gaver）",
              "儿童生态知觉与设计：猫耳洞/卡他/沙坑", "潜在功能：鸟栖现象与盆栽垃圾盆"],
         next_lesson="下一节（2.2+2.3）：复杂性与适应——环境偏爱的倒 U 曲线",
         tl=[("intro", "海龟与小鱼", 20), ("concept", "视觉悬崖", 50),
             ("concept", "光阵列与提供", 60), ("concept", "寓知觉于行动", 45),
             ("concept", "提供的三种伪装", 35), ("application", "儿童与环境设计", 55), ("summary", "小结", 15)]),
    dict(kind="new", src=None, run="envpsy-22",
         chapter="chapter-02", chapter_title="第二章 环境知觉",
         lesson_id="lesson-2-2-complexity",
         title=f"复杂性与适应——环境偏爱的倒 U 曲线（2.2+2.3·{VOICE_LABEL}）",
         kps=["对照刺激特性四件套（Berlyne）", "兴趣单调增 vs 喜好倒 U（Wohlwill）",
              "自然环境例外：越复杂越偏爱", "芦苞祖庙：兴趣 ≠ 喜好",
              "复杂组织三态：无组织/有组织/协同", "适应水平理论（Wohlwill 1974）",
              "信息超载与信息阙如：南京路/光谷 vs 群岛化", "顺应与适应：同伴街/詹宁斯/雅莉玛"],
         next_lesson="下一节（2.4）：情绪的坐标——环境刺激与情绪反应",
         tl=[("intro", "两座繁华两种反应", 20), ("concept", "环境知觉特点", 35),
             ("concept", "倒 U 曲线", 75), ("concept", "时代漂移：圣家寺与凤凰中心", 35),
             ("application", "适应水平：过度/不足/调节", 75), ("summary", "小结", 15)]),
    dict(kind="new", src=None, run="envpsy-24",
         chapter="chapter-02", chapter_title="第二章 环境知觉",
         lesson_id="lesson-2-4-emotion",
         title=f"情绪的坐标——环境刺激与情绪反应（2.4·{VOICE_LABEL}）",
         kps=["唤醒：网状结构与生理指标", "SD 法与形容词维度",
              "情绪三因子：快乐/控制/唤醒（Russell & Mehrabian）", "多巴胺与脑啡肽：欲望与奖赏",
              "控制感：心理对抗/习得性无助/疗养院实验", "布克钟表匠与金字塔推论",
              "环状模型与四维度", "新天地：一平方公里的情绪地图", "耶克斯-多德森倒 U 与设计匹配"],
         next_lesson="下一节（3.1①）：城市意象五要素——凯文·林奇的城市地图",
         tl=[("intro", "新天地表情变化", 20), ("concept", "维度来源：SD 法", 45),
             ("concept", "情绪三因子", 95), ("concept", "环状模型到四维度", 55),
             ("application", "新天地情绪地图", 40), ("application", "耶克斯-多德森与设计", 35), ("summary", "小结", 15)]),
    dict(kind="revoice", src="envpsy-glm-t1-31", run="envpsy-31-cosy",
         chapter="chapter-03", chapter_title="第三章 环境认知",
         lesson_id="lesson-3-1-city-image",
         title=f"城市意象五要素——在陌生城市里认路（3.1①·{VOICE_LABEL}）",
         kps=["认知地图与城市意象", "五要素：道路/边界/区域/节点/标志",
              "波士顿/泽西城/洛杉矶调查", "意象性与可读性", "北京意象调查与应用"],
         next_lesson="下一章（第六章）：空间行为——个人空间与人际距离（已有种子片）",
         tl=[("intro", "认路开场", 25), ("concept", "五要素定义", 90),
             ("concept", "三城调查与意象性", 80), ("application", "北京意象与设计应用", 60), ("summary", "小结", 23)]),
]

CHAPTER_ORDER = ["chapter-00", "chapter-01", "chapter-02", "chapter-03", "chapter-06"]


def sh(cmd, timeout=None):
    """跑子进程，返回 (rc, tail_output)。PYTHONUTF8=1：子进程 stdout 走 UTF-8，
    防止重定向管道下 GBK 控制台编码撞上 U+FFFD 直接 UnicodeEncodeError。"""
    import os
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout, env=env)
    tail = ((r.stdout or "") + (r.stderr or ""))[-400:]
    return r.returncode, tail


def produce_new(run, profile="profiles/envpsy.profile.yaml"):
    topic = next((ROOT / "runs" / run).glob("topic-*.md"))
    cmd = [sys.executable, "_run_produce.py", f"runs/{run}",
           "--topic", str(topic), "--model", "sol", "--effort", "high",
           "--profile", profile]
    for attempt in range(3):
        rc, tail = sh(cmd, timeout=7200)
        if rc == 0:
            return True, tail
        print(f"[produce] attempt {attempt + 1} fail rc={rc}: {tail}", flush=True)
        time.sleep(30)
    return False, tail


def revoice_run(src, run):
    """换声：setup → tts 重试 → narration/audit → STARTS 重写 → render → qa → mux。"""
    dst = ROOT / "runs" / run
    if not (dst / "code" / "index.html").exists():
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / "runs" / src / "code", dst / "code")
        for f in ("storyboard.md", "decision.json"):
            if (ROOT / "runs" / src / f).exists():
                shutil.copy(ROOT / "runs" / src / f, dst / f)
        (dst / "out").mkdir(parents=True, exist_ok=True)
    # scene 换声
    scene_p = ROOT / "audio" / f"scene_{run}.json"
    if not scene_p.exists():
        sc = json.loads((ROOT / "audio" / f"scene_{src}.json").read_text(encoding="utf-8"))
        sc["title"], sc["voice"] = run, VOICE
        scene_p.write_text(json.dumps(sc, ensure_ascii=False, indent=2), encoding="utf-8")
    # tts：外层重试（cosy SSL 抽风）
    for attempt in range(12):
        rc, tail = sh([sys.executable, "audio.py", "tts", str(scene_p)], timeout=3600)
        timing = ROOT / "audio" / f"timing_{run}.json"
        if rc == 0 and timing.exists():
            break
        print(f"[tts] attempt {attempt + 1} rc={rc}: {tail}", flush=True)
        time.sleep(25)
    else:
        return False, "tts exhausted"
    # narration + audit
    for cmdx in (["narration", str(timing)],):
        rc, tail = sh([sys.executable, "audio.py"] + cmdx, timeout=600)
        if rc != 0:
            return False, f"narration fail: {tail}"
    nar = ROOT / "audio" / f"narration_{run}.wav"
    rc, tail = sh([sys.executable, "audio.py", "audit", str(nar), str(timing)], timeout=300)
    if rc != 0:
        return False, f"audit fail: {tail}"
    print(f"[revoice] tts+narration ok: {tail[-120:]}", flush=True)
    return finish_render(run)


def finish_render(run):
    """STARTS 重写 → render → qa → mux。新片 produce 已渲染，仅换声需要。"""
    import audio  # noqa
    from pipeline import qa  # noqa
    from pipeline.adapters import web2d  # noqa

    wd = ROOT / "runs" / run
    timing_p = ROOT / "audio" / f"timing_{run}.json"
    tm = json.loads(timing_p.read_text(encoding="utf-8"))
    html_p = wd / "code" / "index.html"
    html = html_p.read_text(encoding="utf-8")
    narr = tm["narr"]
    new_block = "const STARTS = [\n  " + ",\n  ".join(
        ",".join(f"{v:.3f}" for v in narr[i:i + 8]) for i in range(0, len(narr), 8)
    ) + "\n];"
    html2, n = re.subn(r"const STARTS\s*=\s*\[[\s\S]*?\];", new_block, html, count=1)
    if n == 0:
        # 2026-10-12：sol 新片可能写成 const STARTS = Object.freeze([...]);
        # 括号归属不同，单独处理（重配音路径才会走到这里；produce 内部重写更健壮）。
        frozen = "const STARTS = Object.freeze(" + new_block[len("const STARTS = "):-1] + ");"
        html2, n = re.subn(
            r"const STARTS\s*=\s*Object\.freeze\(\s*\[[\s\S]*?\]\s*\)\s*;",
            frozen, html, count=1)
    if n == 0:
        # GLM 复刻版代码：const NS=[...仅起点...] + DUR=xxx
        ns_block = "const NS=[" + ",".join(f"{v:.3f}" for v in tm["starts"]) + "];"
        html2, n1 = re.subn(r"const NS\s*=\s*\[[\s\S]*?\];", ns_block, html, count=1)
        html2, n2 = re.subn(r"DUR\s*=\s*[\d.]+", f"DUR={tm['total']:.3f}", html2, count=1)
        assert n1 == 1 and n2 == 1, f"NS/DUR 替换失败 n1={n1} n2={n2}"
        n = n1
    else:
        html2, n2 = re.subn(r"DUR\s*=\s*[\d.]+", f"DUR={tm['total']:.3f}", html2, count=1)
    assert n == 1, "STARTS 替换失败"
    html_p.write_text(html2, encoding="utf-8")

    res = web2d.render(wd, tm)
    if not res["ok"]:
        return False, f"render fail: {res.get('errors', [])[:2]}"
    report = qa.check(res["video"], tm, wd)
    if not report["pass"]:
        print(f"[qa] WARN not pass: {json.dumps(report.get('checks', {}), ensure_ascii=False)[:200]}", flush=True)
    final = wd / "out" / f"final_{run}.mp4"
    audio.cmd_mux(res["video"], str(timing_p), str(final))
    # 2026-10-12 磁盘治理：mux 落地后清中间产物（frames ~1-2GB/课、narration wav
    # ~70MB/课）。保留 final/无声 video.mp4/code/scene+timing json——足够重渲染
    # 与重配音；真要重 mux 可从 final 提轨或重 TTS。失败不清（重试还依赖它们）。
    try:
        shutil.rmtree(wd / "out" / "frames", ignore_errors=True)
        (ROOT / "audio" / f"narration_{run}.wav").unlink(missing_ok=True)
    except Exception as e:  # noqa: BLE001
        print(f"[cleanup] WARN {e}", flush=True)
    return True, f"final {final.name} {tm['total']:.1f}s"


def fmt_vtt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def package(lesson):
    run = lesson["run"]
    timing = json.loads((ROOT / "audio" / f"timing_{run}.json").read_text(encoding="utf-8"))
    scene = json.loads((ROOT / "audio" / f"scene_{run}.json").read_text(encoding="utf-8"))
    final = ROOT / "runs" / run / "out" / f"final_{run}.mp4"
    assert final.exists(), f"missing {final}"

    pkg = COURSE_DIR / lesson["chapter"] / lesson["lesson_id"]
    pkg.mkdir(parents=True, exist_ok=True)
    shutil.copy(final, pkg / "video.mp4")
    # script.md（storyboard 副本）
    sb = ROOT / "runs" / run / "storyboard.md"
    if sb.exists():
        shutil.copy(sb, pkg / "script.md")

    # transcript.vtt
    texts = [s["text"] if isinstance(s, dict) else s for s in scene["sentences"]]
    lines = ["WEBVTT\n"]
    for i, (a, b) in enumerate(zip(timing["starts"], timing["ends"])):
        lines += [str(i + 1), f"{fmt_vtt(a)} --> {fmt_vtt(b)}", texts[i], ""]
    (pkg / "transcript.vtt").write_text("\n".join(lines), encoding="utf-8")

    # timeline：按 tl 目标秒比例切句
    n = len(texts)
    total_w = sum(x[2] for x in lesson["tl"])
    cum, boundaries = 0.0, [0]
    for _, _, secs in lesson["tl"][:-1]:
        cum += secs
        boundaries.append(min(n - 1, round(cum / total_w * n)))
    boundaries.append(n)
    timeline = []
    for (typ, topic, _), a, b in zip(lesson["tl"], boundaries[:-1], boundaries[1:]):
        timeline.append({
            "start": round(timing["starts"][a], 1) if a < n else 0,
            "end": round(timing["ends"][b - 1] if b > a else timing["starts"][a], 1),
            "type": typ, "topic": topic,
        })
    for i in range(len(timeline) - 1):
        timeline[i]["end"] = timeline[i + 1]["start"]
    timeline[-1]["end"] = round(timing["total"], 1)

    # lesson.json
    (pkg / "lesson.json").write_text(json.dumps({
        "schema": "lesson-manifest-v0.1",
        "course_id": "envpsy-course-001",
        "chapter_id": lesson["chapter"],
        "lesson_id": lesson["lesson_id"],
        "title": lesson["title"],
        "duration": round(timing["total"], 1),
        "video": "video.mp4",
        "transcript": "transcript.vtt",
        "script": "script.md",
        "knowledge_points": lesson["kps"],
        "timeline": timeline,
        "tts": {"engine": "cosyvoice-v2", "voice": "longxiaochun_v2"},
        "produced_by": "sol",
        "interactions": "interactions.json",
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # interactions.json —— 数据接口：本批留空，后续填 cues 即可
    (pkg / "interactions.json").write_text(json.dumps({
        "schema": "interactions-v0.1",
        "lesson_id": lesson["lesson_id"],
        "cues": [],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # summary.json
    (pkg / "summary.json").write_text(json.dumps({
        "schema": "summary-v0.1",
        "lesson_id": lesson["lesson_id"],
        "knowledge_points": lesson["kps"],
        "common_mistakes": [],
        "next_lesson": lesson["next_lesson"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return pkg


def rebuild_course():
    course_p = COURSE_DIR / "course.json"
    course = json.loads(course_p.read_text(encoding="utf-8"))
    old = {c["chapter_id"]: c for c in course["chapters"]}
    chapters = []
    for ch in CHAPTER_ORDER:
        if ch in ("chapter-00", "chapter-01", "chapter-02", "chapter-03"):
            lessons = [l for l in LESSONS if l["chapter"] == ch]
            entries = []
            for l in lessons:
                pkg = COURSE_DIR / ch / l["lesson_id"]
                tm_p = ROOT / "audio" / f"timing_{l['run']}.json"
                dur = round(json.loads(tm_p.read_text(encoding="utf-8"))["total"], 1) if tm_p.exists() else None
                if pkg.exists():
                    entries.append({"lesson_id": l["lesson_id"], "title": l["title"],
                                    "duration": dur, "package": f"course/{ch}/{l['lesson_id']}"})
            if entries:
                chapters.append({"chapter_id": ch, "title": lessons[0]["chapter_title"], "lessons": entries})
        elif ch in old:
            chapters.append(old[ch])
    course["chapters"] = chapters
    course["title"] = "环境心理学·系列课件（前置十章试产）"
    course_p.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[course.json] {len(chapters)} chapters", flush=True)


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
        if lesson["kind"] == "new":
            ok, info = produce_new(run)
        else:
            ok, info = revoice_run(lesson["src"], run)
        if not ok:
            print(f"[FAIL] {run}: {info}", flush=True)
            results.append((run, f"FAIL"))
            continue
        print(f"[done] {run} 生产 {time.time() - t0:.0f}s — {info[-120:]}", flush=True)
        package(lesson)
        rebuild_course()
        results.append((run, "ok"))
    print("==== 批产结果 ====")
    for r, s in results:
        print(f"  {r}: {s}")
    rebuild_course()


if __name__ == "__main__":
    main()
