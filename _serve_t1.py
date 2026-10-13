"""_serve_t1.py — T1 种子 v1/hr 双版对比页（Tailscale 100.84.28.40:8861）。

Range 206（视频 seek）。用法: python _serve_t1.py
"""
import http.server
import re
import socketserver
import time
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
FILES["/cosy.mp4"] = ROOT / "runs" / "envpsy-t1-cosy" / "out" / "final_envpsy-t1-cosy.mp4"
_cosy_label = {  # 试听页标签
    "cosyvoice-v2_longshu_v2": "G-龙书·沉稳青年男(v2)",
    "cosyvoice-v2_longxiaochun_v2": "H-龙小淳·知性积极女(v2)",
    "cosyvoice-v2_longxiaocheng_v2": "I-龙小诚·磁性低音男(v2)",
    "cosyvoice-v2_longtian_v2": "J-龙天·磁性理智男(v2)",
    "cosyvoice-v2_longze_v2": "K-龙泽·温暖元气男(v2)",
    "cosyvoice-v2_longbaizhi": "L-龙白芷·睿气旁白女(v2)",
    "cosyvoice-v2_longwan_v2": "M-龙婉·积极知性女(v2)",
    "cosyvoice-v3-plus_longanyang": "N-龙安洋·阳光大男孩(v3-plus)",
}
for _f in sorted((ROOT / "cache" / "cosy_voices").glob("*.mp3")):
    _key = _f.stem
    if _key in _cosy_label:
        FILES[f"/cosy-{_key}.mp3"] = _f
MIME = {".mp4": "video/mp4", ".mp3": "audio/mpeg", ".md": "text/plain; charset=utf-8", ".log": "text/plain; charset=utf-8"}

# ---- 前十段（first10）批产 ----
F10 = [
    ("f10-00", "envpsy-intro-cosy", "绪论 · 环境心理学是什么", "换声重制"),
    ("f10-01", "envpsy-11", "1.1 感觉、知觉与认知——加工流水线", "sol 新制"),
    ("f10-02", "envpsy-12a", "1.2① 看世界的三种方式——视知觉功能与格式塔", "sol 新制"),
    ("f10-03", "envpsy-12b", "1.2② 眼见未必为实——视错觉与设计", "sol 新制"),
    ("f10-04", "envpsy-13", "1.3 听建筑——听知觉、声景与环境设计", "sol 新制"),
    ("f10-05", "envpsy-14", "1.4 鼻尖、手底、脚下——嗅触动觉与环境设计", "sol 新制"),
    ("f10-06", "envpsy-21", "2.1 环境的提供——生态知觉理论", "sol 新制"),
    ("f10-07", "envpsy-22", "2.2+2.3 复杂性与适应——环境偏爱的倒U曲线", "sol 新制"),
    ("f10-08", "envpsy-24", "2.4 情绪的坐标——环境刺激与情绪反应", "sol 新制"),
    ("f10-09", "envpsy-31-cosy", "3.1① 城市意象五要素——凯文·林奇", "换声重制"),
    ("f10-10", "envpsy-32", "3.2 城市意象的后续研究——从五要素到日常生活", "sol 新制"),
    ("f10-11", "envpsy-33", "3.3 空间定向与场所命名——大脑里的GPS与街名的学问", "sol 新制"),
    ("f10-12", "envpsy-41", "4.1 行为场景——巴克与人生大舞台", "sol 新制"),
    ("f10-13", "envpsy-42", "4.2 场所感——空间如何变成『我的地方』", "sol 新制"),
    ("f10-14", "envpsy-43", "4.3 场所依恋——为什么我们会爱上一个地方", "sol 新制"),
    ("f10-15", "envpsy-51", "5.1 应激过程——从警报到成长的三级火箭", "sol 新制"),
    ("f10-16", "envpsy-52", "5.2 灾变事件——信息、认知缺失与漫长的后效", "sol 新制"),
    ("f10-17", "envpsy-53", "5.3 城市背景应激源——噪声、雾霾与靴子落地", "sol 新制"),
    ("f10-18", "envpsy-54", "5.4 个人应激源——量表、敏感噪声与刮黑板的科学", "sol 新制"),
    ("f10-19", "envpsy-62", "6.2 私密性——选择与控制的艺术", "sol 新制"),
    ("f10-20", "envpsy-63", "6.3 领域性——占有与防卫的空间策略", "sol 新制·批3"),
    ("f10-21", "envpsy-64", "6.4 密度与拥挤感——老鼠乌托邦的崩溃与人类的两难", "sol 新制·批3"),
    ("f10-22", "envpsy-71", "7.1 在自然的孕育中进化——从大裂谷走出的我们", "sol 新制·批3"),
    ("f10-23", "envpsy-72", "7.2 人类基本情感反应的来源——敬畏、恐惧与愉悦", "sol 新制·批3"),
    ("f10-24", "envpsy-73", "7.3 自然环境在当代的作用——从敬畏符号到康复环境", "sol 新制·批3"),
    ("f10-25", "envpsy-74", "7.4 亲环境行为——从价值信念到破窗治理", "sol 新制·批3"),
    ("f10-26", "envpsy-81", "8.1 研究方法和理论类别——从风景画到评价成图", "sol 新制·批3"),
    ("f10-27", "envpsy-82", "8.2 影响即时景观偏爱的因素——四种属性与神秘性", "sol 新制·批3"),
    ("f10-28", "envpsy-83", "8.3 基于意象的场所外观评价——好恶的地图", "sol 新制·批3"),
    ("f10-29", "envpsy-91", "9.1 研究目的和方法——观察城市的五种姿势", "sol 新制·批3"),
    ("f10-30", "envpsy-92", "9.2 研究内容概述——外部空间里的众生相", "sol 新制·批4"),
    ("f10-31", "envpsy-93", "9.3 外部空间中的行为习性——抄近路、人看人与出神", "sol 新制·批4"),
    ("f10-32", "envpsy-94", "9.4 调查实例——深圳书城、成都茶馆与乐山个案", "sol 新制·批4"),
    ("f10-33", "envpsy-101", "10.1 建筑学中的一般应用——从决定论到或然论", "sol 新制·批4"),
    ("f10-34", "envpsy-102", "10.2 建筑体验研究——偏爱从哪里来", "sol 新制·批4"),
    ("f10-35", "envpsy-103", "10.3 建筑认知研究——意象、寻址与隐喻（全课收官）", "sol 新制·批4"),
]
for _k, _r, _t, _tag in F10:
    FILES[f"/{_k}.mp4"] = ROOT / "runs" / _r / "out" / f"final_{_r}.mp4"

INTROS = [
    ("f10i-1", "envpsy-ci1", "第一章 知觉：环境设计的入口", "章绪论"),
    ("f10i-2", "envpsy-ci2", "第二章 环境知觉：谁在点亮世界", "章绪论"),
    ("f10i-3", "envpsy-ci3", "第三章 环境认知：脑中的城市地图", "章绪论"),
    ("f10i-4", "envpsy-ci4", "第四章 场景与场所：行为的舞台", "章绪论"),
    ("f10i-5", "envpsy-ci5", "第五章 环境应激：失衡的科学", "章绪论"),
    ("f10i-6", "envpsy-ci6", "第六章 空间行为：距离的语法", "章绪论"),
    ("f10i-7", "envpsy-ci7", "第七章 感恩自然：天性的回响", "章绪论"),
    ("f10i-8", "envpsy-ci8", "第八章 景观偏爱：好恶的测量学", "章绪论"),
    ("f10i-9", "envpsy-ci9", "第九章 外部公共空间：街道的生命", "章绪论"),
    ("f10i-10", "envpsy-ci10", "第十章 建筑与行为：概率的学问", "章绪论"),
]
for _k, _r, _t, _tag in INTROS:
    FILES[f"/{_k}.mp4"] = ROOT / "runs" / _r / "out" / f"final_{_r}.mp4"

INTROS_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>章绪论十篇 · 每章 1-2 分钟</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
.item{margin:22px 0}.item b{font-size:15px}.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:1px 6px;margin:0 6px}
video{width:100%;border-radius:8px;background:#000;margin-top:8px}s{color:#667}</style></head><body>
<h1>《环境心理学》章绪论十篇 · 每章 1-2 分钟导览</h1>
<p class="meta">元层面导览：只讲"为什么学、学什么、怎么串"，不与正文重复。配音 CosyVoice v2 · 龙小淳；sol(gpt-6.1-sol 高推理) 制作；时长门禁 ≥70s + 冻结扫描。
<br><a href="/first10.html">▶ 三十八讲正文正片</a></p>
{{ITEMS}}
</body></html>"""


def _intros_page():
    import json as _json
    rows = []
    for _k, _r, _t, _tag in INTROS:
        f = FILES[f"/{_k}.mp4"]
        if not f.exists():
            rows.append(f'<div class="item"><s><b>{_t}</b></s> <span class="tag">生产中…</span></div>')
            continue
        tm_p = ROOT / "audio" / f"timing_{_r}.json"
        dur = ""
        if tm_p.exists():
            _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
            dur = f'<span class="meta">{_d:.0f}s</span>'
        rows.append(f'<div class="item"><b>{_t}</b><span class="tag">{_tag}</span>{dur}'
                    f'<video controls preload="metadata" src="/{_k}.mp4"></video></div>')
    return INTROS_PAGE.replace("{{ITEMS}}", "".join(rows))

F10_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>前三十六段 · 章节正片</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
.item{margin:26px 0}.item b{font-size:15px}.tag{color:#8fb;font-size:12px;border:1px solid #2a4;border-radius:4px;padding:1px 6px;margin:0 6px}
video{width:100%;border-radius:8px;background:#000;margin-top:8px}s{color:#667}</style></head><body>
<h1>《环境心理学》前三十六段正片 · 章节序</h1>
<p class="meta">配音 CosyVoice v2 · 龙小淳(知性积极女)；新制 34 段＝sol(gpt-6.1-sol 高推理) storyboard→codegen→渲染；绪论/3.1① 为旧片换声重制；6.3→9.1 为第三批、9.2→10.3 为第四批收官批（含时长下限+冻结扫描双门禁）。
<br>互动课件版（带字幕/数据接口）在 <a href="http://100.84.28.40:8862/?p=course/course.json">Runtime 8862</a>。</p>
{{ITEMS}}
</body></html>"""


def _f10_page():
    import json as _json
    rows = []
    for _k, _r, _t, _tag in F10:
        f = FILES[f"/{_k}.mp4"]
        if not f.exists():
            rows.append(f'<div class="item"><s><b>{_t}</b></s> <span class="tag">生产中…</span></div>')
            continue
        tm_p = ROOT / "audio" / f"timing_{_r}.json"
        dur = ""
        if tm_p.exists():
            _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
            dur = f'<span class="meta">{_d / 60:.1f} min</span>'
        rows.append(f'<div class="item"><b>{_t}</b><span class="tag">{_tag}</span>{dur}'
                    f'<video controls preload="metadata" src="/{_k}.mp4"></video></div>')
    return F10_PAGE.replace("{{ITEMS}}", "".join(rows))
PORT = 8861

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>T1 种子对比 · 个人空间与人际距离</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:15px;color:#8fb;margin-top:28px}a{color:#7fd}video{width:100%;border-radius:8px;background:#000}
.meta{color:#9ab;font-size:13px;line-height:1.7}table{border-collapse:collapse;font-size:13px}
td,th{border:1px solid #2a3540;padding:4px 10px;text-align:left}th{color:#8fb}</style></head><body>
<h1>《看不见的气泡》T1 种子 · 两版对比</h1>
<p class="meta"><a href="/intros.html">▶ 章绪论十篇（每章 1-2 分钟导览，龙小淳配音）</a><br>
<a href="/first10.html">▶ 前三十六段正片批产（绪论→10.3 全书收官，龙小淳配音，sol 新制 34 段+换声 2 段）</a></p>
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
<h2>配音对比——T1 种子 · CosyVoice 龙书版（百炼 cosyvoice-v2）</h2>
<video controls preload="metadata" src="/cosy.mp4"></video>
<p class="meta">311.7s · 42 句 · 同分镜同画面，旁白换为百炼 CosyVoice cosyvoice-v2 / longshu_v2（龙书·沉稳青年男）· AUDIT PASS<br>
互动课件版（带问答/互动题）：<a href="http://199.68.217.229:8862/?p=course/chapter-06/lesson-t1-personal-space-cosy">Runtime 打开 CosyVoice 版</a> ·
<a href="http://199.68.217.229:8862/?p=course/chapter-06/lesson-t1-personal-space">原晓晓版对照</a> ·
更多音色见 <a href="/tts.html">A/B 页 G–N 组</a>（龙书/小淳/小诚/龙天/龙泽/白芷/龙婉/安洋）。成本：整课 1,623 字 ≈ ¥0.33。</p>
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
    edge_cards = "".join(
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
    cosy_cards = "".join(
        f'<div class="card"><b>{label}</b> — {desc}<br><audio controls preload="none" src="/cosy-{k}.mp3"></audio></div>'
        for label, k, desc in [
            ("G-longshu", "cosyvoice-v2_longshu_v2", "龙书·沉稳青年男(v2)——T1 CosyVoice 成片所用音色"),
            ("H-longxiaochun", "cosyvoice-v2_longxiaochun_v2", "龙小淳·知性积极女(v2)"),
            ("I-longxiaocheng", "cosyvoice-v2_longxiaocheng_v2", "龙小诚·磁性低音男(v2)"),
            ("J-longtian", "cosyvoice-v2_longtian_v2", "龙天·磁性理智男(v2)"),
            ("K-longze", "cosyvoice-v2_longze_v2", "龙泽·温暖元气男(v2)"),
            ("L-longbaizhi", "cosyvoice-v2_longbaizhi", "龙白芷·睿气旁白女(v2)"),
            ("M-longwan", "cosyvoice-v2_longwan_v2", "龙婉·积极知性女(v2)"),
            ("N-longanyang", "cosyvoice-v3-plus_longanyang", "龙安洋·阳光大男孩(v3-plus·支持Instruct情感指令)"),
        ] if (ROOT / "cache" / "cosy_voices" / f"{k}.mp3").exists()
    )
    cards = edge_cards + cosy_cards
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
        # 2026-10-12：成片会被同名替换（4.3/5.1 重制），必须带校验器且禁缓存，
        # 否则浏览器/中间代理拿着旧 mp4 不知道更新（用户实测踩坑）。
        mt = f.stat().st_mtime
        etag = f'W/"{int(mt)}-{size}"'
        lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mt))
        self.send_header("Last-Modified", lm)
        self.send_header("ETag", etag)
        self.send_header("Cache-Control", "no-cache")
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
        if self.path == "/first10.html":
            body = _f10_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/intros.html":
            body = _intros_page().encode("utf-8")
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
            size = f.stat().st_size
            mt = f.stat().st_mtime
            self.send_response(200)
            self.send_header("Content-Type", MIME.get(f.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Last-Modified",
                             time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mt)))
            self.send_header("ETag", f'W/"{int(mt)}-{size}"')
            self.send_header("Cache-Control", "no-cache")
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
