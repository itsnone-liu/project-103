"""_serve_t1.py — T1 种子 v1/hr 双版对比页（Tailscale 100.84.28.40:8861）。

Range 206（视频 seek）。用法: python _serve_t1.py
"""
import http.server
import re
import socketserver
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _vtag(_run):
    """视频缓存击穿版本号：按成片文件 mtime，文件更新→src 变化→浏览器必然重取。"""
    p = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
    return int(p.stat().st_mtime) if p.exists() else "fin"
V1 = ROOT / "runs" / "envpsy-t1-61"
HR = ROOT / "runs" / "envpsy-t1-61-hr"
T2 = ROOT / "runs" / "envpsy-t2-94"
FILES = {
    "/style-sample.mp4": ROOT / "runs" / "lightcolor-1-01" / "style_sample" / "style_sample_lightcolor.mp4",
    "/v1.mp4": V1 / "out" / "final_envpsy-t1-61.mp4",
    "/hr.mp4": HR / "out" / "final_envpsy-t1-61-hr.mp4",
    "/t2.mp4": T2 / "out" / "final_envpsy-t2-94.mp4",
    "/t3.mp4": ROOT / "runs" / "envpsy-t3-intro" / "out" / "final_envpsy-t3-intro.mp4",
    "/t4.mp4": ROOT / "runs" / "envpsy-t4-91" / "out" / "final_envpsy-t4-91.mp4",
    "/case-spike.mp4": ROOT / "runs" / "urban-doc-style-spike" / "C_times_square" / "out" / "video.mp4",
    "/case-spike-sheet.jpg": ROOT / "runs" / "urban-doc-style-spike" / "C_times_square" / "out" / "storyboard_24.jpg",
    "/case-spike-c2.mp4": ROOT / "runs" / "urban-doc-style-spike" / "C2_times_square" / "out" / "video.mp4",
    "/case-spike-c2-sheet.jpg": ROOT / "runs" / "urban-doc-style-spike" / "C2_times_square" / "out" / "storyboard_24.jpg",
    "/sugelan-report.pptx": Path(r"D:\AI-Teaching-Assistant\output\sugelan\苏格兰学院高质量发展与育人案例分享_20页.pptx"),
    "/sugelan-report-contrast.pptx": Path(r"D:\AI-Teaching-Assistant\output\sugelan\苏格兰学院高质量发展与育人案例分享_20页.pptx"),
    "/sugelan-report-modern.pptx": Path(r"D:\AI-Teaching-Assistant\output\sugelan\苏格兰学院高质量发展与育人案例分享_20页_第二模板版.pptx"),
    "/urban-spike-a.mp4": ROOT / "runs" / "urban-doc-style-spike" / "A_legacy" / "out" / "video.mp4",
    "/urban-spike-b.mp4": ROOT / "runs" / "urban-doc-style-spike" / "B_explicit" / "out" / "video.mp4",
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
MIME = {".mp4": "video/mp4", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".md": "text/plain; charset=utf-8", ".log": "text/plain; charset=utf-8", ".jpg": "image/jpeg", ".html": "text/html; charset=utf-8", ".png": "image/png", ".js": "text/javascript; charset=utf-8"}
# ===== QWEN3 TTS AUDITION BEGIN =====
_q3dir = ROOT / "cache" / "qwen3tts_test"
FILES["/qwen3tts.mp3"] = _q3dir / "qwen3tts_flash_cherry.mp3"
FILES["/qwen3tts.html"] = _q3dir / "qwen3tts.html"
# ===== QWEN3 TTS AUDITION END =====

# ===== XDSDS GALLERY BEGIN =====
_xds = ROOT / "现代设计史"
FILES["/xdsds/kaogang.md"] = _xds / "现代设计史自学考试大纲_提取版.md"
FILES["/xdsds/yangjuan.md"] = _xds / "样卷_v1.md"
FILES["/xdsds/yangjuan_ans.md"] = _xds / "样卷_答案_v1.md"
FILES["/xdsds/tiku.md"] = _xds / "题库_v1.md"
FILES["/xdsds/zhangce.md"] = _xds / "章节测验_v1.md"
FILES["/xdsds/suitang.md"] = _xds / "随堂测验题_v1.md"
# ===== XDSDS GALLERY END =====
# ===== DSB GALLERY BEGIN =====
_dsb = ROOT / "设计基础"
FILES["/dsbv.html"] = _dsb / "_gallery_dsb.html"
FILES["/dsbv/dsb-2-03.mp4"] = ROOT / "runs" / "dsb-2-03" / "out" / "final_dsb-2-03.mp4"
FILES["/dsbv/dsb-2-03-sheet.jpg"] = ROOT / "runs" / "dsb-2-03" / "out" / "qa_sheet.jpg"
FILES["/dsbv/dsb-2-03-poster.jpg"] = ROOT / "runs" / "dsb-2-03" / "out" / "poster.jpg"
FILES["/dsbv/frame-008.jpg"] = ROOT / "runs" / "dsb-2-03" / "out" / "frame_008.jpg"
FILES["/dsbv/frame-145.jpg"] = ROOT / "runs" / "dsb-2-03" / "out" / "frame_145.jpg"
FILES["/dsbv/frame-225.jpg"] = ROOT / "runs" / "dsb-2-03" / "out" / "frame_225.jpg"
FILES["/dsbv/frame-250.jpg"] = ROOT / "runs" / "dsb-2-03" / "out" / "frame_250b.jpg"
FILES["/dsbv/seed.md"] = _dsb / "视频课件_种子视频_v1.md"
FILES["/dsbv/storyboard.md"] = ROOT / "runs" / "dsb-2-03" / "storyboard.md"
FILES["/dsbv/plan.md"] = _dsb / "视频课件_分段方案-v1.md"
FILES["/dsbv/ref.md"] = _dsb / "视频课件_参考库-v1.md"
FILES["/dsbv/topic.md"] = ROOT / "runs" / "dsb-2-03" / "topic-dsb-2-03.md"
# ===== DSB SEED2 GALLERY BEGIN =====
FILES["/dsb5v.html"] = _dsb / "_gallery_dsb5.html"
FILES["/dsb5v/dsb-5-05.mp4"] = ROOT / "runs" / "dsb-5-05" / "out" / "final_dsb-5-05.mp4"
FILES["/dsb5v/dsb-5-05-sheet.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "qa_sheet.jpg"
FILES["/dsb5v/dsb-5-05-poster.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "poster.jpg"
FILES["/dsb5v/frame-010.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "frame_010.jpg"
FILES["/dsb5v/frame-120.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "frame_120.jpg"
FILES["/dsb5v/frame-174.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "frame_174.jpg"
FILES["/dsb5v/frame-192.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "frame_192.jpg"
FILES["/dsb5v/frame-232.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "frame_232.jpg"
FILES["/dsb5v/frame-278.jpg"] = ROOT / "runs" / "dsb-5-05" / "out" / "frame_278.jpg"
FILES["/dsb5v/seed.md"] = _dsb / "视频课件_种子视频_v1.md"
FILES["/dsb5v/storyboard.md"] = ROOT / "runs" / "dsb-5-05" / "storyboard.md"
FILES["/dsb5v/plan.md"] = _dsb / "视频课件_分段方案-v1.md"
FILES["/dsb5v/ref.md"] = _dsb / "视频课件_参考库-v1.md"
FILES["/dsb5v/topic.md"] = ROOT / "runs" / "dsb-5-05" / "topic-dsb-5-05.md"
# ===== DSB SEED2 GALLERY END =====
# ===== DSB BATCH GALLERY BEGIN（2026-11-27 批产 B1—B5；页面由 _dsb_gallery.py 再生成）=====
FILES["/dsbb.html"] = _dsb / "_gallery_dsb_batches.html"
# ===== DSB BATCH GALLERY END =====
# ===== DSB GALLERY END =====

# ===== BSD COURSE FILES BEGIN =====
_bsd = ROOT / "商业空间设计"
FILES["/bsd/suitang.md"] = _bsd / "随堂测验题_v1.md"
FILES["/bsd/kaogang.md"] = _bsd / "考试大纲_v0.1.md"
FILES["/bsd/yangjuan.md"] = _bsd / "样卷_v1.md"
FILES["/bsd/yangjuan_ans.md"] = _bsd / "样卷_答案_v1.md"
FILES["/bsd/tiku.md"] = _bsd / "题库_v1.md"
FILES["/bsd/zhangce.md"] = _bsd / "章节测验_v1.md"

# ===== ENVPSY COURSE FILES BEGIN =====
_env = ROOT / "环境心理学"
FILES["/envpsy/suitang.md"] = _env / "随堂测验题_v1.md"
FILES["/envpsy/kaogang.md"] = _env / "考试大纲_v0.1.md"
FILES["/envpsy/yangjuan.md"] = _env / "样卷_v1.md"
FILES["/envpsy/yangjuan_ans.md"] = _env / "样卷_答案_v1.md"
FILES["/envpsy/tiku.md"] = _env / "题库_v1.md"
FILES["/envpsy/zhangce.md"] = _env / "章节测验_v1.md"
FILES["/envpsy/zhangce_app.md"] = _env / "章节测验_应用版_v1.md"
# ===== ENVPSY COURSE FILES END =====
# ===== BSD COURSE FILES END =====

# ===== IJC COURSE FILES BEGIN =====
_ijc = ROOT / "室内构造与材料学"
FILES["/ijc/suitang.md"] = _ijc / "随堂测验题_v1.md"
# ===== IJC COURSE FILES END =====


APP_PRON_TESTS = [
    ("User suggestion - A屁屁, both pi4", ROOT / "cache" / "app_pron_test" / "app_user_A_pipi_fulltone.wav"),
    ("User suggestion - plain A屁屁", ROOT / "cache" / "app_pron_test" / "app_user_A_pipi.wav"),
    ("A - CMU EY P IY P IY", ROOT / "cache" / "app_pron_test" / "ssml_cmu_unstressed.wav"),
    ("B - CMU EY1 P IY1 P IY1", ROOT / "cache" / "app_pron_test" / "ssml_cmu_stress.wav"),
    ("C - characters", ROOT / "cache" / "app_pron_test" / "ssml_characters.wav"),
]
for _label, _path in APP_PRON_TESTS:
    FILES[f"/app-pron-{_path.stem}.wav"] = _path
APP_PRON_PAGE = """<!doctype html><meta charset=utf-8><title>App 字母发音短句试听</title>
<style>body{font:16px system-ui,'Microsoft YaHei';max-width:760px;margin:40px auto;padding:0 18px;background:#10151c;color:#e9eef4}audio{width:100%;margin:10px 0 24px}p{line-height:1.7;color:#b9c5d2}</style>
<h1>App 字母发音短句试听</h1>
<p>第一个是你刚提的“ A屁屁 ”，其余是之前的字母名测试。请听候选；正式视频尚未采用任何一个。</p>
<h3>你的候选 · 两个「屁」都用四声</h3><audio controls preload=metadata src="/app-pron-app_user_A_pipi_fulltone.wav"></audio>
<h3>原始 A屁屁</h3><audio controls preload=metadata src="/app-pron-app_user_A_pipi.wav"></audio>
<h3>A · CMU 字母名</h3><audio controls preload=metadata src="/app-pron-ssml_cmu_unstressed.wav"></audio>
<h3>B · CMU 带重音字母名</h3><audio controls preload=metadata src="/app-pron-ssml_cmu_stress.wav"></audio>
<h3>C · SSML 按字符读</h3><audio controls preload=metadata src="/app-pron-ssml_characters.wav"></audio>
<p>测试文本：用 App 也一样，我们熟悉的是别人做出的结果，设计却要追问，这个结果怎么造出来。</p>"""

# ---- 103 教材线上实践（ISD-L04K 厨房实验 / ISD-L04 全户型实验） ----
LAB = ROOT / "室内空间设计" / "线上实践" / "labs" / "ISD-L04K"
FILES["/isd-l04k.html"] = LAB / "kitchen_lab.html"
FILES["/isd-l04k-qa.png"] = LAB / "qa_initial.png"
LAB4 = ROOT / "室内空间设计" / "线上实践" / "labs" / "ISD-L04"
FILES["/isd-l04.html"] = LAB4 / "unit_lab.html"
FILES["/isd-l04-qa.png"] = LAB4 / "qa_initial.png"
LAB3 = ROOT / "室内空间设计" / "线上实践" / "labs" / "ISD-L03"
FILES["/isd-l03.html"] = LAB3 / "bubble_lab.html"
FILES["/isd-l03-qa.png"] = LAB3 / "qa_initial.png"
LAB6 = ROOT / "室内空间设计" / "线上实践" / "labs" / "ISD-L06"
FILES["/isd-l06-preview.html"] = LAB6 / "render_preview.html"
ISD_V = ROOT / "runs" / "isd-3-02" / "out"
FILES["/isd-3-02.mp4"] = ISD_V / "final_isd-3-02.mp4"
FILES["/isd-3-02-sheet.jpg"] = ISD_V / "qa_sheet.jpg"
ISD_V2 = ROOT / "runs" / "isd-4-02" / "out"
FILES["/isd-4-02.mp4"] = ISD_V2 / "final_isd-4-02.mp4"
FILES["/isd-4-02-sheet.jpg"] = ISD_V2 / "qa_sheet.jpg"
for _asset in ("three.min.js", "OrbitControls.js", "RoomEnvironment.js"):
    FILES[f"/isd-l06-vendor/{_asset}"] = LAB6 / "vendor" / _asset

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

CASES = [
    ("case-1", "envpsy-case1", "案例A 抢街：时代广场的人本改造", "设计案例·12min"),
]
for _k, _r, _t, _tag in CASES:
    FILES[f"/{_k}.mp4"] = ROOT / "runs" / _r / "out" / f"final_{_r}.mp4"

# ---- 案例 v2 验收（2026-10-14：口语化旁白 + 中段一句一世界） ----
V2 = ROOT / "runs" / "envpsy-case1-v2"
FILES["/case-1-v2-stream.mp4"] = V2 / "out" / "final_stream_1080p.mp4"
FILES["/case-1-v2.mp4"] = V2 / "out" / "final_envpsy-case1-v2.mp4"
FILES["/case-1-v2-sheet.jpg"] = V2 / "out" / "contact_sheet_48.jpg"
FILES["/case-1-v2-cue-index.md"] = V2 / "out" / "cue_index.md"
FILES["/case-1-v2-preview-mid.mp4"] = V2 / "out" / "preview_mid_cue17-24.mp4"
FILES["/case-1-v2-preview-evidence.mp4"] = V2 / "out" / "preview_evidence_cue33-35.mp4"
FILES["/case-1-full-v1.mp4"] = ROOT / "runs" / "envpsy-case1-full" / "out" / "final_envpsy-case1-full.mp4"

# ---- 案例 B《隔间》（2026-10-15：E组透视设计图语法） ----
C2 = ROOT / "runs" / "envpsy-case2-cubicle"
FILES["/case-2-stream.mp4"] = C2 / "out" / "final_stream_1080p.mp4"
FILES["/case-2.mp4"] = C2 / "out" / "final_envpsy-case2-cubicle.mp4"
FILES["/case-2-sheet.jpg"] = C2 / "out" / "contact_sheet_39.jpg"
FILES["/case-2-cue-index.md"] = C2 / "out" / "cue_index.md"
FILES["/case-2-preview-explode.mp4"] = C2 / "out" / "preview_explode_cue13-18.mp4"
FILES["/case-2-preview-strip.mp4"] = C2 / "out" / "preview_strip_grid_cue23-26.mp4"
FILES["/case-2-preview-evidence.mp4"] = C2 / "out" / "preview_evidence_cue27-32.mp4"

CASE2_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>案例B《隔间》· 验收页</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:15px;color:#8fb;margin-top:30px}a{color:#7fd}video,img{width:100%;border-radius:8px;background:#000;margin:8px 0 6px}
.meta{color:#9ab;font-size:13px;line-height:1.7}.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:1px 6px;margin:0 6px}</style></head><body>
<h1>案例B《隔间：Action Office 的理想与异化》· 验收页 <span class="tag">定稿</span><span class="tag">透视设计图语法</span></h1>
<p class="meta">07:07 · 39 句 · 旁白 2219 字 · TTS 全自然语速 · 对齐审计 PASS · 10249 帧零错误<br>
主打你点的三件事：①设计图展示（透视旋转/爆炸分解/制图标注）②不做卡片布局（一句一世界）③按内容针对性变化的动画（六幕各持语法）</p>
<h2>▶ 正片（流播版 1080p，已验证含音轨）</h2>
<video controls preload="metadata" src="/case-2-stream.mp4?v=case2-v1"></video>
<p class="meta">原画质版（crf17）：<a href="/case-2.mp4?v=case2-v1">final_envpsy-case2-cubicle.mp4</a>（132MB）</p>
<h2>E组语法实拍段（spike 验证后进正片）</h2>
<p class="meta">▸ 爆炸分解+制图标注（cue13-18，53s）：AO II 部件悬浮标注 → 站桌升起带尺寸线 → 半高屏视线剧场（坐挡/站越）<br>
▸ 自由度剥离+网格复制（cue23-26，34s）：站桌锁平/搁架脱落/倾角拉直/褪灰，一格到一座楼<br>
▸ 证据钟摆（cue27-32，74s）：约70% 指数条 + 四荡钟摆机</p>
<video controls preload="none" src="/case-2-preview-explode.mp4"></video>
<video controls preload="none" src="/case-2-preview-strip.mp4"></video>
<video controls preload="none" src="/case-2-preview-evidence.mp4"></video>
<h2>快审材料</h2>
<p class="meta">▸ 39 句联系表 · <a href="/case-2-cue-index.md">逐句时间戳索引</a>（报 cue 号定点补渲）</p>
<img src="/case-2-sheet.jpg" loading="lazy">
<p class="meta">数字口径：1964/1968/4年间隔、1962 税务规程（Rev. Proc. 62-21）、约70% 面对面降幅（Bernstein &amp; Turban 2018，两家《财富》500 强）、《呆伯特》1989；Propst 晚年批评用安全转述；无来源数字一律不出现。</p>
</body></html>"""

CASE_V2_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>案例A v2 · 验收页</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:15px;color:#8fb;margin-top:30px}a{color:#7fd}video,img{width:100%;border-radius:8px;background:#000;margin:8px 0 6px}
.meta{color:#9ab;font-size:13px;line-height:1.7}.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:1px 6px;margin:0 6px}
.fix{border-left:3px solid #2a4;padding-left:12px}</style></head><body>
<h1>案例A《抢街：时代广场的人本改造》v2 · 验收页 <span class="tag">定稿</span><span class="tag">口语化旁白</span><span class="tag">中段一句一世界</span></h1>
<p class="meta">11:01 · 48 句 · 旁白 3564 字（v1 3060）· TTS 全自然语速 · 对齐审计 PASS · 15871 帧零错误<br>
按你 2026-10-14 反馈三处修复 ↓（v1 对照片在页底）</p>
<h2>▶ 正片（流播版 1080p·2.0Mbps，适合中继带宽）</h2>
<video controls preload="metadata" src="/case-1-v2-stream.mp4?v=v2b-final"></video>
<p class="meta">原画质版（4.5Mbps，下载观看更佳）：<a href="/case-1-v2.mp4?v=v2b-final">final_envpsy-case1-v2.mp4</a>（343MB）· 已修复开场瑕疵：改后画面百老汇对角车道不再有车穿过右侧休息区</p>
<h2>修复① 中段不再"一张底图画圈"（原 1:24–6:25）</h2>
<p class="meta fix">第 7–31 句每句一个专属视觉世界：决策墙三卡 / 道具特写 / 挡风玻璃 POV / 路牌翻面 / 三沙漏+怀表 / 四色诉求牌落桌 / 三镜片工具箱 / 一天多时段剧场 / 过载减层主观剧 / 追光椅 / 同格双填 / 三扇门杠杆 / 待检命题卡 / 双机位同法对照……全段零圈线箭头、零字母角标，来源一律自然写法（"来源：NYC DOT 2010 评估"）。</p>
<h2>修复② 旁白口语化（无 B/T 等书面标记）</h2>
<p class="meta fix">48 句全部重写："先看…换算一下：改造前算一百，改造后是三十七""第一…第二…"式连接；〔B〕〔T〕标记从语音与画面根除（text/sources 字段级分离）。时长 10:01→11:01。</p>
<h2>修复③ 表达方式扩容</h2>
<p class="meta fix">城市化纪录片采样分析建库（大同/城市梦/Whyte 1980/Urbanized/人的尺度 五卡）；三种新语法先经短样片实证再进正片。</p>
<h2>快审材料</h2>
<p class="meta">▸ 96 秒中段样段（cue17-24，直接听新语气）<br>▸ 42 秒数字证据段（cue33-35）<br>▸ 48 句联系表（一眼扫全部世界）<br>▸ <a href="/case-1-v2-cue-index.md">逐句时间戳索引</a>（按秒定位任意一句）</p>
<video controls preload="none" src="/case-1-v2-preview-mid.mp4"></video>
<video controls preload="none" src="/case-1-v2-preview-evidence.mp4"></video>
<img src="/case-1-v2-sheet.jpg" loading="lazy">
<h2>v1 对照（你已验收的版本，10:01）</h2>
<video controls preload="none" src="/case-1-full-v1.mp4"></video>
<p class="meta">验收口径：通过 → 归档为动画纪录片式模板 v2 代表作；点状修改 → 报 cue 号（见逐句索引），定点补渲不重跑全片。已知注记：cue21/22 的"经过/停留计数器"并入多时段剧场（语义成立；要计数器可定点补）。</p>
</body></html>"""

SPIKE_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Sol 城市视觉短样</title><style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}video,img{width:100%;margin:8px 0 22px}.meta{color:#9ab;line-height:1.7}h1,h2{color:#bce}</style></head><body><h1>Sol代码视频能力短样·旧/新上下文对照</h1><p class="meta">A/B同题用于验证视觉指令影响；C/C2为时代广场短样。均为原型，不是完整课程片。</p><h2>A · 城市化主题旧上下文</h2><video controls preload="metadata" src="/urban-spike-a.mp4"></video><h2>B · 城市化主题完整视觉指令</h2><video controls preload="metadata" src="/urban-spike-b.mp4"></video><h2>C · 时代广场首轮</h2><video controls preload="metadata" src="/case-spike.mp4"></video><img src="/case-spike-sheet.jpg"><h2>C2 · 多样混合构图迭代</h2><video controls preload="metadata" src="/case-spike-c2.mp4"></video><img src="/case-spike-c2-sheet.jpg"><p><a href="/spike-evaluation.md">制作与评估记录</a></p></body></html>"""

CASES_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>设计案例研究 · 论文框架教学片</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
.item{margin:22px 0}.item b{font-size:15px}.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:1px 6px;margin:0 6px}
video{width:100%;border-radius:8px;background:#000;margin-top:8px}s{color:#667}</style></head><body>
<h1>《环境心理学》设计案例研究 · 论文框架教学片</h1>
<p class="meta">设计论文六段文体（问题→理论框架→诊断→设计策略→实证检验→结论）× 工程图纸视觉母语 × 纪录片叙事；全程代码确定性渲染，数字全部带来源。配音 CosyVoice v2 · 龙小淳；sol(gpt-6.1-sol 高推理) 制作；时长门禁 ≥570s + 冻结扫描。
<br><a href="/intros.html">▶ 章绪论十篇</a> · <a href="/first10.html">▶ 三十八讲正文正片</a> · <a href="/case-v2.html" style="color:#fc8">▶ 案例A v2 验收页（定稿）</a> · <a href="/case-2.html" style="color:#fc8">▶ 案例B《隔间》验收页（定稿）</a> · <a href="/isd-l03.html" style="color:#8f8">🎮 需求档案与气泡图任务书实验（ISD-L03·成果①）</a> · <a href="/isd-l06-preview.html" style="color:#8ff">🧊 U90双档3D渲染预演（L06渲染层）</a> · <a href="/isd-l04.html" style="color:#8f8">🎮 U90全户型功能组织实验（ISD-L04·成果②）</a> · <a href="/isd-l04k.html" style="color:#8f8">🎮 厨房折返计数实验（ISD-L04K）</a> · <a href="/labs.html" style="color:#8f8">📋 线上实践实验目录（12章规划）</a></p>
{{ITEMS}}
</body></html>"""


def _cases_page():
    import json as _json
    rows = []
    for _k, _r, _t, _tag in CASES:
        f = FILES[f"/{_k}.mp4"]
        if not f.exists():
            rows.append(f'<div class="item"><s><b>{_t}</b></s> <span class="tag">生产中…</span></div>')
            continue
        tm_p = ROOT / "audio" / f"timing_{_r}.json"
        dur = ""
        if tm_p.exists():
            _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
            dur = f'<span class="meta">{_d/60:.1f}min</span>'
        rows.append(f'<div class="item"><b>{_t}</b><span class="tag">{_tag}</span>{dur}'
                    f'<video controls preload="metadata" src="/{_k}.mp4?v=b6"></video></div>')
    return CASES_PAGE.replace("{{ITEMS}}", "".join(rows))

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


# ---- 教材线上实践实验目录（labs.html） ----
LABS = [
    ("L01", "观察与问题标注：居住摩擦证据图", "第1–2章", "规划中"),
    ("L02", "人体尺度与动作包络叠加", "第3章", "规划中"),
    ("L03", "居住需求档案与气泡图任务书", "第2章", "online"),
    ("L04", "U90全户型功能组织与动线冲突", "第4章", "online"),
    ("L04K", "厨房工作三角与折返计数", "第7章", "online"),
    ("L05", "动线与通达：起终点与障碍路径", "第4章", "规划中"),
    ("L06P", "U90 双档3D渲染预演（L06渲染层）", "第5–6章", "preview"),
    ("L06", "空间围合与视线分析", "第5–6章", "规划中"),
    ("L07", "采光与照明四场景切换", "第8章", "规划中"),
    ("L08", "材料色彩七属性对比", "第9章", "规划中"),
    ("L09", "家具收纳与多情境切换", "第10章", "规划中"),
    ("L10", "技术疑点三层分类与待核单", "第11章", "规划中"),
    ("L11", "A/B 表达与同伴评议", "第12章", "规划中"),
    ("L12", "综合项目作品包（承接各实验）", "第12章", "规划中"),
]
LABS_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>线上实践实验目录</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #2a3542;padding:8px 10px;font-size:14px;text-align:left}
th{color:#8fb}.tag{color:#8fb;font-size:12px;border:1px solid #2a4;border-radius:4px;padding:1px 6px}
.tag.todo{color:#788;border-color:#445}.item{margin:22px 0}</style></head><body>
<h1>《室内空间设计》线上实践 · 实验目录</h1>
<p class="meta">配套读本 v0.4（12章）· 一章一实验 · 全部为单文件网页（无后端、无依赖、平台无关）。
规则约束：教学常用值/教学假设与国家标准严格区分；三层反馈分列（观察/规则建议/教师判断），不合成 AI 总分；导出 isd-design-v1 数据契约。
生产管线：lab.yaml 合同 → sol(gpt-6.1-sol 高推理) 生成 → 程序化 QA 门禁（6断言+确定性+视觉审）。
<br><a href="/">◀ 返回总入口</a></p>
<table><tr><th>编号</th><th>实验</th><th>教材锚点</th><th>状态</th></tr>{{ROWS}}</table>
{{FEATURED}}
</body></html>"""


LAB_FEATURED = {
    "L03": "访谈要点→功能气泡装进冻结房间槽→五档邻接边+证据标签→面积/时段/三角张力/区带/覆盖/对表六类白盒检查→双情境任务书导出（成果①，可作L04前置）",
    "L04": "固定约束下重组功能（书房三模式/储物四模式/门位槽位/家具拖拽）→ 邻接矩阵7条+四动线交叉+早高峰四口离散事件模拟+时段冲突 → A/B对比与失效条件（成果②）",
    "L04K": "拖拽工作站→模拟四菜一汤→折返计数（基线6次→优化2次，对应教材图7-1）",
}


# ---- 《室内空间设计》视频课件 51 段 · 章节化画廊（isdv.html） ----
# 段名权威源：室内空间设计\视频课件_分段方案-v1.md（54 为笔误，实 51 段）
ISD_CHAPTERS = [
    ("课程绪论", [("isd-0-00", "课程绪论：住宅是翻译题，U90 走五阶段", "S5")]),
    ("第1章 概论", [("isd-1-01", "1.1 先翻译再设计", "S1"), ("isd-1-02", "1.3 住宅类型", "S1"),
                     ("isd-1-03", "1.4 好房子五个词", "S1"), ("isd-1-04", "1.5+1.6 读优秀案例·U90五阶段地图", "S5")]),
    ("第2章 行为与需求", [("isd-2-01", "2.1 频率/归属/节律三分类", "S1"), ("isd-2-02", "2.2 生命周期与两代同住", "S5"),
                         ("isd-2-03", "2.3 三件工具：画像/日志/矩阵", "S2"), ("isd-2-04", "2.4+2.5 三类人→空间清单", "S2")]),
    ("第3章 人体尺度", [("isd-3-01", "3.1 站着多大→活着多大", "S3"), ("isd-3-02", "3.2 通行不是一条线", "S3"),
                       ("isd-3-03", "3.3 家具+人+动作", "S3"), ("isd-3-04", "3.4+3.5 方便说清方便谁·教学值到项目值", "S1")]),
    ("第4章 功能分区与动线", [("isd-4-01", "4.1 先摆关系再画墙", "S5"), ("isd-4-02", "4.2 邻接矩阵摊开假设", "S2"),
                             ("isd-4-03", "4.3 画出这个家的动线", "S2"), ("isd-4-04", "4.4 固定约束里做设计", "S5"),
                             ("isd-4-05", "4.5 比较方案不打分", "S2")]),
    ("第5章 客餐厅", [("isd-5-01", "5.1 客厅是干什么用的", "S1"), ("isd-5-02", "5.2 家具组群怎么摆人就怎么坐", "S3"),
                     ("isd-5-03", "5.3 餐桌多面手", "S5"), ("isd-5-04", "5.4+5.5 进门第一分钟·同处一室各做各事", "S5")]),
    ("第6章 卧室书房私密", [("isd-6-01", "6.1 私密是分层的", "S1"), ("isd-6-02", "6.2 卧室从一张床开始", "S3"),
                           ("isd-6-03", "6.3+6.4 儿童房·老人房适老化", "S5"), ("isd-6-04", "6.5 书房工位声学双模式", "S5"),
                           ("isd-6-05", "6.6+例题 一间房多重身份", "S5")]),
    ("第7章 厨卫家务", [("isd-7-01", "7.1 看见看不见的家务", "S1"), ("isd-7-02", "7.2 厨房工作站尺度与中餐现实", "S3"),
                       ("isd-7-03", "7.3 卫生间分离度谱系与安全底线", "S2"), ("isd-7-04", "7.4+7.5 家务区阳台·大挪位的代价", "S5")]),
    ("第8章 采光照明", [("isd-8-01", "8.1 光是给行为服务的", "S4"), ("isd-8-02", "8.2 自然采光：朝向只是第一层", "S4"),
                       ("isd-8-03", "8.3 人工照明三层光", "S4"), ("isd-8-04", "8.4 情境表到照明图纸", "S2")]),
    ("第9章 材料色彩", [("isd-9-01", "9.1+9.2 读材料多属性·界面各有脾气", "S4"), ("isd-9-02", "9.3 色彩来自关系", "S4"),
                       ("isd-9-03", "9.4 材料矩阵与预算取舍", "S2")]),
    ("第10章 家具收纳", [("isd-10-01", "10.1 家具是空间构件", "S1"), ("isd-10-02", "10.2 收纳跟着行为走", "S2"),
                         ("isd-10-03", "10.3+10.4 可变家具真实成本·小户型四种资源", "S5"),
                         ("isd-10-04", "10.5 家具清单到实施顺序", "S2")]),
    ("第11章 技术与表达", [("isd-11-01", "11.1 方案背后的工程系统", "S6"), ("isd-11-02", "11.2+11.3 技术提醒·图纸语言", "S6"),
                           ("isd-11-03", "11.4 版本与可追溯论证", "S6")]),
    ("第12章 综合设计", [("isd-12-01", "12.1 分散成果整合为一个命题", "S5"), ("isd-12-02", "12.2 五轮整合与回退", "S2"),
                         ("isd-12-03", "12.3+12.4 完整作品包·评价与答辩", "S6")]),
    ("案例专题", [("isd-13-01", "CA-1 U90五阶段总复盘：从需求到方案包", "S5"),
                 ("isd-13-02", "CA-2 情境B：夜起与照护（两代同住的压力测试）", "S5"),
                 ("isd-13-03", "CA-3 30㎡/60㎡ 小户型：同一方法论的压缩版", "S5")]),
]

ISD_PAGE_TPL = """<!doctype html><html><head><meta charset="utf-8"><title>室内空间设计 · 视频课件 51 段</title>
<style>
body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:16px;color:#bce;margin:28px 0 6px;border-bottom:1px solid #2a3542;padding-bottom:4px}
.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
.item{margin:14px 0}.item b{font-size:14px}
.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:0 5px;margin:0 4px}
.dur{color:#89a;font-size:12px;margin-left:6px}
video{width:100%;border-radius:8px;background:#000;margin-top:6px}
s{color:#667}.ok{color:#7d8}</style></head><body>
<h1>《室内空间设计》视频课件 · {{N}} 段全量</h1>
<p class="meta">读本 v0.4 十二章 × 章节化分段教学片（51 段，绪论 1 ＋ 正文 44 ＋ 案例专题 3 ＋ ...）。
配音 CosyVoice v2 · 龙小淳；sol(gpt-6.1-sol 高推理) 代码确定性渲染；门禁：时长 ≥270s ＋ 冻结扫描全绿。
{{STATS}}<br><a href="/">◀ 返回总入口</a> · <a href="/labs.html" style="color:#8f8">🎮 线上实践实验目录</a></p>
{{BODY}}
</body></html>"""


def _isd_page():
    import json as _json
    parts, have, total, dsum = [], 0, 0, 0.0
    for _chname, _segs in ISD_CHAPTERS:
        rows = [f"<h2>{_chname}</h2>"]
        for _run, _title, _typ in _segs:
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            if not f.exists():
                rows.append(f'<div class="item"><s><b>{_title}</b></s><span class="tag">缺片</span></div>')
                continue
            have += 1
            total += 1
            dur = ""
            tm_p = ROOT / "audio" / f"timing_{_run}.json"
            if tm_p.exists():
                _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
                dsum += _d
                dur = f'<span class="dur">{_d/60:.1f} min · {int(_d)}s</span>'
            rows.append(
                f'<div class="item"><b>{_title}</b><span class="tag">{_typ}</span>'
                f'<span class="tag ok">门禁通过</span>{dur}'
                f'<video controls preload="metadata" src="/isdv/{_run}.mp4?v={_vtag(_run)}"></video></div>')
        parts.append("".join(rows))
    stats = f"当前成片 <b>{have}</b> 段 · 总时长 <b>{dsum/3600:.1f} 小时</b>（{dsum/60:.0f} 分钟）。"
    return ISD_PAGE_TPL.replace("{{N}}", str(have)).replace("{{STATS}}", stats).replace("{{BODY}}", "".join(parts))


# ---- 《室内色彩与图案设计》视频课件 49 段 · 章节化画廊（colorv.html，2026-10-22 上线） ----
# 段名权威源：室内色彩与图案设计\视频课件_分段方案-v1.md（v1 定稿）
COLOR_CHAPTERS = [
    ("课程绪论", [("color-0-00", "课程绪论：从白盒子到家——空间定稿，色彩登场", "C5")]),
    ("第1章 概论", [("color-1-01", "1.1+1.2 格局定了为什么还要谈色彩", "C1"),
                    ("color-1-02", "1.3 算给你看·三种气质动了什么", "C3"),
                    ("color-1-03", "1.4–1.6 能帮忙不包办·选择有来由·这门课怎么学", "C1")]),
    ("第2章 三个把手", [("color-2-01", "2.1+2.9 先别急着说暖·给颜色做诊断单", "C1"),
                       ("color-2-02", "2.2+2.3 明度分量最重·同一面墙只改明度", "C2"),
                       ("color-2-03", "2.4+2.5 纯度与太花·色相环邻近对比", "C2"),
                       ("color-2-04", "2.6–2.8 暖冷不是一个旋钮·三把手进日常", "C2")]),
    ("第3章 体系与表示法", [("color-3-01", "3.1+3.2 只说米色不行·孟塞尔记号怎么读", "C2"),
                          ("color-3-02", "3.3 色立体为什么不是一条直线", "C2"),
                          ("color-3-03", "3.4+3.5 NCS 看法·劳尔潘通色卡", "C2"),
                          ("color-3-04", "3.6+3.7 屏幕颜色上墙·颜色沟通单", "C1/C6")]),
    ("第4章 感知", [("color-4-01", "4.1+4.2 颜色住在哪里·旁边换了颜色", "C3"),
                   ("color-4-02", "4.3+4.4 眼睛自己调光·小色卡上墙显得深", "C3"),
                   ("color-4-03", "4.5 店里好回家变", "C3"),
                   ("color-4-04", "4.6 判断变可复核记录", "C1/C6")]),
    ("第5章 心理与联想", [("color-5-01", "5.1+5.2 联想谱是地图不是判决书", "C1"),
                        ("color-5-02", "5.3–5.5 有据与流传·三分框算给你看", "C2"),
                        ("color-5-03", "5.6+5.7 语境压过颜色·设计师能谈什么", "C1")]),
    ("第6章 光与色", [("color-6-01", "6.1+6.2 三抓手·朝向剧本", "C3"),
                    ("color-6-02", "6.3+6.4 分层照明·灯一换颜色像换了", "C3"),
                    ("color-6-03", "6.5 算给你看·两种光剧本同一块灰蓝布", "C3"),
                    ("color-6-04", "6.6 按光剧本选色", "C3")]),
    ("第7章 材质", [("color-7-01", "7.1+7.2 同色号变脸·光泽分级", "C3"),
                   ("color-7-02", "7.3+7.4 透光·木纹石纹不是缺点", "C3"),
                   ("color-7-03", "7.5+7.6 组合节奏·材质板", "C2"),
                   ("color-7-04", "7.7–7.10 现场复核·冲突检查·可追溯", "C6")]),
    ("第8章 角色框架", [("color-8-01", "8.1+8.2 为什么要分角色·比例不是规定", "C1"),
                      ("color-8-02", "8.3+8.4 三角色与三属性·方案主线", "C2"),
                      ("color-8-03", "8.5+8.6 从房间条件开始·沈家客厅三版推演", "C5"),
                      ("color-8-04", "8.7 现场复核先看整间房", "C6")]),
    ("第9章 图案是什么", [("color-9-01", "9.1+9.2 不只花朵·纹样排队成节奏", "C4"),
                       ("color-9-02", "9.3+9.4 密度对比方向·单元大小不能脱房间", "C4"),
                       ("color-9-03", "9.5+9.6 太花了是哪种病·四只抱枕诊断", "C4"),
                       ("color-9-04", "9.7+9.8 三步拆解·放回房间做检查", "C4/C1")]),
    ("第10章 谱系", [("color-10-01", "10.1+10.2 认亲·条纹格纹家世", "C4"),
                    ("color-10-02", "10.3 自然纹几支", "C4"),
                    ("color-10-03", "10.4 传统进当代怎么翻译", "C4/C5"),
                    ("color-10-04", "10.5–10.7 混搭不各说各话·三块布样认亲·四步讲清", "C5")]),
    ("第11章 组织", [("color-11-01", "11.1+11.2 单元多大·近看远看不是一回事", "C4"),
                    ("color-11-02", "11.3+11.4 铺满为什么累·边界收口", "C4"),
                    ("color-11-03", "11.5+11.6 跟着生活走·小书房三次推演", "C5"),
                    ("color-11-04", "11.7 选图案四问", "C1")]),
    ("第12章 综合", [("color-12-01", "12.1–12.3 不能只靠效果图·盘条件·翻译感觉", "C6"),
                    ("color-12-02", "12.4+12.5 角色图案各就各位·小样要够大", "C6/C3"),
                    ("color-12-03", "12.6+12.7 现场复核不是找借口·定可执行版本", "C6"),
                    ("color-12-04", "12.8–12.10 交底遗留·沈家七步终局·答辩有据", "C5")]),
    ("案例专题", [("color-13-01", "CA-1 白盒子到入住：沈家色彩层总复盘", "C5"),
                 ("color-13-02", "CA-2 一次失败的试色：错误如何变成记录", "C5")]),
]

COLOR_PAGE_TPL = """<!doctype html><html><head><meta charset="utf-8"><title>室内色彩与图案设计 · 视频课件 49 段</title>
<style>
body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:16px;color:#bce;margin:28px 0 6px;border-bottom:1px solid #2a3542;padding-bottom:4px}
.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
.item{margin:14px 0}.item b{font-size:14px}
.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:0 5px;margin:0 4px}
.tag.seed{color:#f9a;border:1px solid #c56;border-radius:4px;padding:0 5px;margin:0 4px}
.dur{color:#89a;font-size:12px;margin-left:6px}
video{width:100%;border-radius:8px;background:#000;margin-top:6px}
s{color:#667}.ok{color:#7d8}</style></head><body>
<h1>《室内色彩与图案设计》视频课件 · 49 段全量</h1>
<p class="meta">读本 v0.2 十二章 × 章节化分段教学片（49 段，绪论 1 ＋ 正文 46 ＋ 案例专题 2）。
C1–C6 镜头语言（同机位状态切换为主力，图案段平铺生长）；配音 CosyVoice v2 · 龙小淳；sol(gpt-6.1-sol 高推理) 代码确定性渲染；
门禁：时长 ≥270s ＋ 冻结扫描全绿；沈家案例数据全引自《沈家色彩冻结包》。
{{STATS}}<br><a href="/">◀ 返回总入口</a> · <a href="/isdv.html">《室内空间设计》51 段画廊（前序课程）</a></p>
{{BODY}}
</body></html>"""


def _color_page():
    import json as _json
    parts, have, total, dsum = [], 0, 0, 0.0
    for _chname, _segs in COLOR_CHAPTERS:
        rows = [f"<h2>{_chname}</h2>"]
        for _run, _title, _typ in _segs:
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            if not f.exists():
                rows.append(f'<div class="item"><s><b>{_title}</b></s><span class="tag">待批产</span></div>')
                total += 1
                continue
            have += 1
            total += 1
            dur = ""
            tm_p = ROOT / "audio" / f"timing_{_run}.json"
            if tm_p.exists():
                _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
                dsum += _d
                dur = f'<span class="dur">{_d/60:.1f} min · {int(_d)}s</span>'
            rows.append(
                f'<div class="item"><b>{_title}</b><span class="tag">{_typ}</span>'
                f'<span class="tag seed">种子片</span><span class="tag ok">门禁通过</span>{dur}'
                f'<video controls preload="metadata" src="/colorv/{_run}.mp4?v={_vtag(_run)}"></video></div>')
        parts.append("".join(rows))
    stats = f"当前成片 <b>{have}</b> / {total} 段 · 总时长 <b>{dsum/60:.0f} 分钟</b>。种子片已验收路线（C3 同机位状态切换 / C4 平铺生长），批产按章推进。"
    return COLOR_PAGE_TPL.replace("{{STATS}}", stats).replace("{{BODY}}", "".join(parts))


# ---- 《光与色彩》视频课件 · 章节化画廊（lightcolorv.html，2026-11-05 上线） ----
# 段名权威源：光与色彩/读本_v0.1.md 章节目录（12 章 57 节，规划一节一支 300–340s）
# 生产模型：GLM-5.3 首选 / MIMO-v2.6-pro fallback
LC_CHAPTERS = [
    ("第1章 概论：白天看好的院子，晚上去哪了", [("lightcolor-1-01", "1.1 同一座宅子，为什么像两个地方"),
                      ("lightcolor-1-02", "1.2 光改写了什么：颜色、明暗，还有氛围"),
                      ("lightcolor-1-03", "1.3 这门课管什么、不管什么"),
                      ("lightcolor-1-04", "1.4 从买灯到设计光"),
                      ("lightcolor-1-05", "1.5 这本书怎么用")]),
    ("第2章 光从哪来：光源、光谱与色温", [("lightcolor-2-01", "2.1 暖光冷光，说的是温度吗——色温，一把用温度画的尺子"),
                      ("lightcolor-2-02", "2.2 光的颜色从哪来：光谱是光的配方单"),
                      ("lightcolor-2-03", "2.3 十七个灯位排进一把尺：南院色温普查"),
                      ("lightcolor-2-04", "2.4 色温没有好坏，只有用对地方：三档策略和它的证据边界")]),
    ("第3章 光够不够：照度、亮度与眩光", [("lightcolor-3-01", "3.1 亮不亮，谁说了算：照度这把尺"),
                      ("lightcolor-3-02", "3.2 三种不够：量不够、不均匀、对比太强"),
                      ("lightcolor-3-03", "3.3 多亮才算够：按事定光，不按房间定光"),
                      ("lightcolor-3-04", "3.4 手里的尺：照度怎么量，手机靠不靠")]),
    ("第4章 光像不像：显色性与同色异谱", [("lightcolor-4-01", "4.1 灯的演技：显色性，一把还原度的尺"),
                      ("lightcolor-4-02", "4.2 辣椒案宣判：先别急着怪显色"),
                      ("lightcolor-4-03", "4.3 菜色案宣判：显色和色温的合谋"),
                      ("lightcolor-4-04", "4.4 窗帘案宣判：同色异谱，颜色的塑料友情")]),
    ("第5章 看光的眼睛：适应、年龄与个体差异", [("lightcolor-5-01", "5.1 眼睛会换挡：适应这件事"),
                      ("lightcolor-5-02", "5.2 起夜路线审查：三段光的三个错"),
                      ("lightcolor-5-03", "5.3 同一座宅子，不同的眼：年龄这把尺"),
                      ("lightcolor-5-04", "5.4 眼睛里的第三班岗：管钟的感光细胞"),
                      ("lightcolor-5-05", "5.5 人人不同：色觉、偏好，和为分布设计")]),
    ("第6章 天然采光：天井、窗、朝向与时段", [("lightcolor-6-01", "6.1 白天的光是一套套餐：直射、散射、反射"),
                      ("lightcolor-6-02", "6.2 朝向定性格：四扇窗，四种脾气"),
                      ("lightcolor-6-03", "6.3 天井：老宅的采光芯，白天的钟"),
                      ("lightcolor-6-04", "6.4 时段×空间：采光时刻表，让房间跟着太阳走"),
                      ("lightcolor-6-05", "6.5 控光的手：白天的问题常常是太多")]),
    ("第7章 人工光源谱系：从白炽灯到LED", [("lightcolor-7-01", "7.1 第一家：烧出来的光——白炽与卤素"),
                      ("lightcolor-7-02", "7.2 第二家：激出来的光——荧光与节能灯"),
                      ("lightcolor-7-03", "7.3 第三家：转出来的光——LED"),
                      ("lightcolor-7-04", "7.4 暗病：频闪，与一支免费的探针"),
                      ("lightcolor-7-05", "7.5 采购参数卡：把三家的家底写成一张卡")]),
    ("第8章 灯具与布光：三层光与光色构图", [("lightcolor-8-01", "8.1 先把灯解剖了：光源、灯具、光束"),
                      ("lightcolor-8-02", "8.2 三层光：环境、工作、重点"),
                      ("lightcolor-8-03", "8.3 灯型谱：八种身体，各就各位"),
                      ("lightcolor-8-04", "8.4 回路与分组：开关是布光的另一半"),
                      ("lightcolor-8-05", "8.5 布光推演：把大厅从一盏大灯改成三层光")]),
    ("第9章 光与材质：反射、透光与肌理", [("lightcolor-9-01", "9.1 光的三种下场：反射、透射、吸收"),
                      ("lightcolor-9-02", "9.2 反射的脾气：镜面、漫反射，和那一点高光"),
                      ("lightcolor-9-03", "9.3 肌理的显影师：掠射光"),
                      ("lightcolor-9-04", "9.4 透光的家伙：透明、半透与滤色"),
                      ("lightcolor-9-05", "9.5 材质六人 table：光打上去的样子")]),
    ("第10章 全宅诊断：南院光色体检报告", [("lightcolor-10-01", "10.1 病历本：把散装的发现装进一张表"),
                      ("lightcolor-10-02", "10.2 十七位逐一过堂：全宅诊断总表"),
                      ("lightcolor-10-03", "10.3 三个典型病例：量病、动线病、系统病"),
                      ("lightcolor-10-04", "10.4 排序：安全、功能、氛围、情怀"),
                      ("lightcolor-10-05", "10.5 诊断的边界：这本报告管什么、不管什么")]),
    ("第11章 实施方案：把南院点亮", [("lightcolor-11-01", "11.1 从病历到处方：工程单怎么开"),
                      ("lightcolor-11-02", "11.2 天井夜角色：一个专项的诞生"),
                      ("lightcolor-11-03", "11.3 分期与预算：把钱花在顺序上"),
                      ("lightcolor-11-04", "11.4 回路终图：全宅的场景菜单"),
                      ("lightcolor-11-05", "11.5 维护条款：开业不是竣工")]),
    ("第12章 验收：南院的白天与夜晚", [("lightcolor-12-01", "12.1 验收前：先把尺子校准"),
                      ("lightcolor-12-02", "12.2 白天场：不开灯，先看房子自己会不会亮"),
                      ("lightcolor-12-03", "12.3 蓝调时刻：天光与灯光交班"),
                      ("lightcolor-12-04", "12.4 全黑夜场：五点复测，处方对账"),
                      ("lightcolor-12-05", "12.5 祖母标尺：验收最终是人的事"),
                      ("lightcolor-12-06", "12.6 终局整合工作台 ★：把一间屋子从诊断走到验收")]),
]

LC_PAGE_TPL = """<!doctype html><html><head><meta charset="utf-8">
<title>光与色彩 · 视频课件</title>
<style>
body{margin:0;padding:24px 32px;background:#0f1115;color:#e8e8ea;font:15px/1.6 -apple-system,"Microsoft YaHei",sans-serif}
h1{font-size:22px;margin:0 0 6px} h2{font-size:16px;color:#9ecbff;margin:26px 0 10px;border-bottom:1px solid #23262d;padding-bottom:6px}
.item{background:#161a20;border:1px solid #23262d;border-radius:10px;padding:12px 14px;margin:10px 0}
.item b{font-size:15px} video{width:100%;max-width:960px;margin-top:10px;border-radius:8px;background:#000}
.tag{display:inline-block;font-size:12px;padding:1px 8px;border-radius:10px;margin-left:8px;background:#23262d;color:#9aa4b2}
.tag.seed{background:#3a2f12;color:#f0c060} .tag.ok{background:#12301f;color:#58d68d}
.dur{margin-left:8px;font-size:12px;color:#8b93a1}
.stat{color:#9aa4b2;margin:8px 0 18px}
a{color:#f9a}
</style></head><body>
<h1>《光与色彩》视频课件</h1>
<div class="stat">{{STATS}}</div>
{{BODY}}
<p style="margin-top:28px"><a href="/">◀ 返回总入口</a> · <a href="/colorv.html">《室内色彩与图案设计》</a> · <a href="/drwv.html">《设计制图》</a></p>
</body></html>"""


def _lc_page():
    import json as _json
    parts, have, total, dsum = [], 0, 0, 0.0
    for _chname, _segs in LC_CHAPTERS:
        rows = [f"<h2>{_chname}</h2>"]
        for _run, _title in _segs:
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            total += 1
            if not f.exists():
                rows.append(f'<div class="item"><s><b>{_title}</b></s><span class="tag">待批产</span></div>')
                continue
            have += 1
            dur = ""
            tm_p = ROOT / "audio" / f"timing_{_run}.json"
            if tm_p.exists():
                _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
                dsum += _d
                dur = f'<span class="dur">{_d/60:.1f} min · {int(_d)}s</span>'
            rows.append(
                f'<div class="item"><b>{_title}</b><span class="tag seed">种子片</span>'
                f'<span class="tag ok">门禁通过</span>{dur}'
                f'<video controls preload="metadata" src="/lightcolorv/{_run}.mp4?v={_vtag(_run)}"></video></div>')
        parts.append("".join(rows))
    stats = (f"当前成片 <b>{have}</b> / {total} 节 · 已出片总时长 <b>{dsum/60:.1f} 分钟</b>"
             f"（目标 57 节约 300 分钟）。视觉语法：实景照片证据层＋白底示意层＋同机位 A/B 动态对比。"
             f"生产：GLM-5.3（首选）／MIMO-v2.6-pro（fallback）。")
    return LC_PAGE_TPL.replace("{{STATS}}", stats).replace("{{BODY}}", "".join(parts))


# ---- 《设计制图》视频课件 41 段 · 章节化画廊（drwv.html，2026-11-03 上线） ----
# 段名权威源：设计制图\视频课件_分段方案-v1.md §三（v1.1：正文 38＋绪论 1＋CA 2，时长档 380–430s，门禁 ≥360s）
# D 系画面类型：D1概念关系卡 D2图纸生长 D3对账演绎 D4降维与剖切 D5案例复盘 D6流程拆解
DRW_CHAPTERS = [
    ("课程绪论", [("drw-00-01", "课程绪论：从一把卷尺到一份合同——青枫里401全流程预览", "D5")]),
    ("第1章 概论：图纸是空间的普通话", [("drw-1-01", "1.1+1.2 脑子里的家怎么搬进工地·图纸家族点名七种图", "D1/D6"),
                                   ("drw-1-02", "1.3+1.4 一套图纸装着多少话·四方各读哪一面", "D3/D5"),
                                   ("drw-1-03", "1.5 这本书怎么学：跟一套真图纸从零到交付", "D5")]),
    ("第2章 制图标准：先学好这门语言的语法", [("drw-2-01", "2.1+2.2 图纸都一样大·一族线说一族话", "D1/D2"),
                                        ("drw-2-02", "2.3+2.4 比例是换算合同·把客厅放进一张A4纸", "D1/D3"),
                                        ("drw-2-03", "2.5 让工人下得了尺：标注四要素与路标", "D2")]),
    ("第3章 投影原理：把三维世界压进二维", [("drw-3-01", "3.1+3.2 不是画得像是量得出·一个方向一句真话", "D1/D2"),
                                       ("drw-3-02", "3.3+3.4 客厅三个数图上见分晓·正投影的老实与隐瞒", "D3/D4"),
                                       ("drw-3-03", "3.5 平面图是切出来的", "D4"),
                                       ("drw-3-04", "3.6 眼力是练出来的", "D4")]),
    ("第4章 形体与组合体：从积木到户型", [("drw-4-01", "4.1+4.2 五块积木走天下·搭挖插", "D2"),
                                     ("drw-4-02", "4.3 形体分析法：拆开对投影合回去", "D4"),
                                     ("drw-4-03", "4.4+4.5 601坡屋顶两个视图推第三个·把户型当积木", "D3/D4")]),
    ("第5章 轴测图：立体感的捷径", [("drw-5-01", "5.1+5.2 平面说不了高低·正面斜二测", "D1/D2"),
                                ("drw-5-02", "5.3 一张交底轴测图的三个数", "D3"),
                                ("drw-5-03", "5.4+5.5 正等测·轴测图不是万能的", "D2/D1")]),
    ("第6章 透视图：像眼睛那样看空间", [("drw-6-01", "6.1+6.2 透视为谁而画·灭点家常用词", "D1/D4"),
                                   ("drw-6-02", "6.3 定视点三件事", "D3"),
                                   ("drw-6-03", "6.4+6.5 视线法五步·一点还是两点", "D4")]),
    ("第7章 建筑施工图识读：房子的出厂说明书", [("drw-7-01", "7.1+7.2 一沓图纸从哪读起·定位轴线的深账", "D6/D3"),
                                             ("drw-7-02", "7.3 墙不都是墙：负形里的硬边界", "D4"),
                                             ("drw-7-03", "7.4+7.5 层高2800到梁下2440·三张图咬合成一个房子", "D3/D5")]),
    ("第8章 装饰施工图·平面系统：地面上发生的一切", [("drw-8-01", "8.1+8.2 平面三图各替谁说话·拆改平面图", "D1/D2"),
                                                ("drw-8-02", "8.3 一道缝的两头账", "D3"),
                                                ("drw-8-03", "8.4 脚底下的账：地面铺装图", "D3/D2"),
                                                ("drw-8-04", "8.5 头顶上也有地面：吊顶与竖向总账", "D3/D4")]),
    ("第9章 装饰施工图·立面与节点：墙面上的细节", [("drw-9-01", "9.1+9.2 平面立起来才有立面·立面图标什么", "D4/D2"),
                                                ("drw-9-02", "9.3+9.4 索引与详图配对·一面墙进几张纸", "D4/D3"),
                                                ("drw-9-03", "9.5 把刀切进墙皮里：节点详图", "D4")]),
    ("第10章 图纸目录与深度：一套图的编成", [("drw-10-01", "10.1+10.2 全套多少张·目录是一本账", "D6/D1"),
                                         ("drw-10-02", "10.3+10.4 三笔账·深度的档位与错位", "D3/D1"),
                                         ("drw-10-03", "10.5 协同校核与郑监理两条意见", "D5")]),
    ("第11章 交底、变更与竣工图：图纸的下半生", [("drw-11-01", "11.1+11.2 交底第一天·为什么不能口头改", "D6/D5"),
                                             ("drw-11-02", "11.3+11.4 垫层抬高50逐笔重算·门底那25毫米（对账高光）", "D3"),
                                             ("drw-11-03", "11.5 工做完了图还没完：竣工图与归档", "D6/D5")]),
    ("第12章 综合项目：青枫里401出图与审图答辩", [("drw-12-01", "12.1+12.2 为什么还要过答辩·十九张图点名册", "D6/D5"),
                                              ("drw-12-02", "12.3+12.4 三方三问·答辩前夜三笔账", "D5/D3"),
                                              ("drw-12-03", "12.5 尾声：愿望与合同同一天交付", "D5")]),
    ("案例专题", [("drw-ca-01", "CA-1 青枫里401总复盘：十四类图纸一条产出线", "D5"),
                ("drw-ca-02", "CA-2 三线答辩全账：一张图三种问法", "D5")]),
]

DRW_PAGE_TPL = """<!doctype html><html><head><meta charset="utf-8"><title>设计制图 · 视频课件 41 段</title>
<style>
body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:16px;color:#bce;margin:28px 0 6px;border-bottom:1px solid #2a3542;padding-bottom:4px}
.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
.item{margin:14px 0}.item b{font-size:14px}
.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:0 5px;margin:0 4px}
.tag.seed{color:#f9a;border:1px solid #c56;border-radius:4px;padding:0 5px;margin:0 4px}
.dur{color:#89a;font-size:12px;margin-left:6px}
video{width:100%;border-radius:8px;background:#000;margin-top:6px}
s{color:#667}.ok{color:#7d8}</style></head><body>
<h1>《设计制图》视频课件 · 41 段全量</h1>
<p class="meta">读本 v1.0 十二章 × 章节化分段教学片（41 段，绪论 1 ＋ 正文 38 ＋ 案例专题 2，时长档 380–430s）。
D1–D6 镜头语言（D2 图纸生长 / D4 降维与剖切 / D3 对账演绎为三大主力）；贯穿案例＝青枫里401冻结包；
配音 CosyVoice v2 · 龙小淳（0.92 语速）；sol(gpt-6.1-sol 高推理) 代码确定性渲染；
门禁：时长 ≥360s ＋ 冻结扫描 ＋ 双种子片已验收（含多音字正音）。
{{STATS}}<br>线上实验：<a href="/drwlab/sanshitou_lab.html">DRW-L03 三视图联动工作台</a>（第3章） · <a href="/drwlab/toushi_lab.html">DRW-L06 透视汇报工作台</a>（第6章） · <a href="/drwlab/zhaocuo_lab.html">DRW-L11 图纸找错工作台</a>（第11章 · 十二错四族 · 零AI确定性判定）<br><a href="/">◀ 返回总入口</a> · <a href="/isdv.html">《室内空间设计》51 段</a> · <a href="/colorv.html">《室内色彩与图案设计》49 段</a> · <a href="/muiv.html">《移动UI交互设计》43 段</a></p>
{{BODY}}
</body></html>"""


def _drw_page():
    import json as _json
    parts, have, total, dsum = [], 0, 0, 0.0
    for _chname, _segs in DRW_CHAPTERS:
        rows = [f"<h2>{_chname}</h2>"]
        for _run, _title, _typ in _segs:
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            if not f.exists():
                rows.append(f'<div class="item"><s><b>{_title}</b></s><span class="tag">待批产</span></div>')
                total += 1
                continue
            have += 1
            total += 1
            dur = ""
            tm_p = ROOT / "audio" / f"timing_{_run}.json"
            if tm_p.exists():
                _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
                dsum += _d
                dur = f'<span class="dur">{_d/60:.1f} min · {int(_d)}s</span>'
            seed = '<span class="tag seed">种子片</span>' if _run in ("drw-3-02", "drw-8-02") else ""
            rows.append(
                f'<div class="item"><b>{_title}</b><span class="tag">{_typ}</span>{seed}'
                f'<span class="tag ok">门禁通过</span>{dur}'
                f'<video controls preload="metadata" src="/drwv/{_run}.mp4?v={_vtag(_run)}"></video></div>')
        parts.append("".join(rows))
    stats = f"当前成片 <b>{have}</b> / {total} 段 · 总时长 <b>{dsum/60:.0f} 分钟</b>（目标 ≈276 分钟）。批产四批全部完成：B1(ch1–3) → B2(ch4–6) → B3(ch7–9) → B4(绪论＋ch10–12＋CA)，41 段全量上线。"
    return DRW_PAGE_TPL.replace("{{STATS}}", stats).replace("{{BODY}}", "".join(parts))


# ---- 《移动UI交互设计》视频课件 43 段 · 章节化画廊（muiv.html，2026-10-28 上线·B1 待审） ----
# 段名权威源：移动UI交互设计\视频课件_分段方案-v1.md §三（43 段 × ~300s ≈ 215 分钟）
# U系画面类型：U1概念卡 U2界面状态机 U3图表演绎 U4手指触控 U5案例复盘 U6流程拆解
MUI_CHAPTERS = [
    ("课程绪论", [("mui-0-00", "课程绪论：从八百人群聊到一款App——梧桐市集全流程预览", "U5")]),
    ("第1章 概论", [("mui-1-01", "1.1+1.2 十年资深用户≠会设计·UI/交互/体验三个词", "U1·批1"),
                   ("mui-1-02", "1.3+1.4 App怎么被设计出来·好设计值多少次点击", "U1/U3·批1"),
                   ("mui-1-03", "1.5 这门课要真做一款App", "U5·批1")]),
    ("第2章 用户场景任务", [("mui-2-01", "2.1+2.2 「我觉得好用」不算数·手机在什么情况下被用", "U1·批1"),
                        ("mui-2-02", "2.3 怎么问用户才说真话", "U1/U6·批1"),
                        ("mui-2-03", "2.4+2.5 人物卡与旅程图·42条抱怨→9个机会点", "U3·批1")]),
    ("第3章 平台规范", [("mui-3-01", "3.1 同一页面两部手机：三机变形记", "U2·种子片"),
                     ("mui-3-02", "3.2+3.5 规范是惯例与可达性约定·守规范还是秀个性", "U1·批1"),
                     ("mui-3-03", "3.3+3.4 一稿伺候多机·三种密度屏的像素账", "U2/U3·批1")]),
    ("第4章 信息架构导航", [("mui-4-01", "4.1+4.2 功能清单贴满墙·用户心里的货架", "U1"),
                        ("mui-4-02", "4.3+4.4 一排门还是一条走廊·卖羽毛球拍走多少步", "U1/U3"),
                        ("mui-4-03", "4.5 迷路的人问三个问题", "U1"),
                        ("mui-4-04", "4.6 导航定稿之夜：五标签怎么来", "U5")]),
    ("第5章 布局版式", [("mui-5-01", "5.1+5.3 详情页什么最重要·字有大有小先看什么", "U1"),
                     ("mui-5-02", "5.2+5.4 网格排整齐·一屏宽度去哪儿了", "U2/U3"),
                     ("mui-5-03", "5.5 信息优先级变成清楚的一屏", "U5")]),
    ("第6章 界面色彩", [("mui-6-01", "6.1+6.2 选了主色不算完成·颜色令牌起名字", "U2"),
                     ("mui-6-02", "6.3+6.4 深色模式不是反过来·状态不只靠红黄绿", "U2"),
                     ("mui-6-03", "6.5 一个主色变成一组可检查的页面角色", "U3")]),
    ("第7章 组件设计系统", [("mui-7-01", "7.1 图标不只是小图：猜义测试", "U1"),
                        ("mui-7-02", "7.2+7.3 十七种按钮≠十七个组件·状态比静态重要", "U1/U2"),
                        ("mui-7-03", "7.4+7.5 组件起名与设计系统：零件箱→规则", "U5/U6")]),
    ("第8章 触摸手势", [("mui-8-01", "8.1 拇指的热区是固定地图吗", "U4·种子片"),
                     ("mui-8-02", "8.2 图形大小vs触控目标：36单位账", "U4/U3"),
                     ("mui-8-03", "8.3 手势在帮忙还是出谜语", "U4"),
                     ("mui-8-04", "8.4+8.5 地铁单手实测·入口够得到也找得到", "U4/U5")]),
    ("第9章 动效微交互", [("mui-9-01", "9.1+9.2 动效在解释还是装饰·等待为什么难熬", "U2"),
                       ("mui-9-02", "9.3+9.4+9.5 动效参数写成时间线·什么会抢注意力·能暂停吗", "U3/U2"),
                       ("mui-9-03", "9.6 两秒等待哪种反馈诚实", "U2")]),
    ("第10章 表单反馈状态", [("mui-10-01", "10.1+10.2 表单越长错得越多·标签占位帮助文本各管什么", "U1/U6"),
                         ("mui-10-02", "10.3 八分钟花在哪儿", "U3"),
                         ("mui-10-03", "10.4 看不见的页面：全状态目录", "U2·核心段"),
                         ("mui-10-04", "10.5+10.6 反馈的位置时机语气·状态别各自发明", "U1/U2")]),
    ("第11章 可用性适老化", [("mui-11-01", "11.1+11.2 五个人能发现什么·测试的账怎么记", "U1/U3"),
                         ("mui-11-02", "11.3 无障碍检查：不只是过工具", "U2"),
                         ("mui-11-03", "11.4 适老化：把「老人」拆开看·顾老师四十分钟", "U5·主角段"),
                         ("mui-11-04", "11.5+11.6 几十个问题先改哪个·看见变日常", "U3/U1")]),
    ("第12章 综合项目", [("mui-12-01", "12.1+12.2 做小做完整·十六章排十六周", "U6"),
                      ("mui-12-02", "12.3+12.4 高保真到什么程度·答辩是证据链", "U6"),
                      ("mui-12-03", "12.5+12.6 资产包交出去接得住·路演收官", "U5")]),
    ("案例专题", [("mui-13-01", "CA-1 梧桐市集总复盘：十二章版本演进线串讲", "U5"),
                ("mui-13-02", "CA-2 顾老师的四十分钟：一次测试的完整账", "U5")]),
]

MUI_PAGE_TPL = """<!doctype html><html><head><meta charset="utf-8"><title>移动UI交互设计 · 视频课件 43 段</title>
<style>
body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:16px;color:#bce;margin:28px 0 6px;border-bottom:1px solid #2a3542;padding-bottom:4px}
.meta{color:#9ab;font-size:13px;line-height:1.7}a{color:#7fd}
.item{margin:14px 0}.item b{font-size:14px}
.tag{color:#fc8;font-size:12px;border:1px solid #a80;border-radius:4px;padding:0 5px;margin:0 4px}
.tag.seed{color:#f9a;border:1px solid #c56;border-radius:4px;padding:0 5px;margin:0 4px}
.tag.review{color:#8ff;border:1px solid #48a;border-radius:4px;padding:0 5px;margin:0 4px}
.dur{color:#89a;font-size:12px;margin-left:6px}
video{width:100%;border-radius:8px;background:#000;margin-top:6px}
s{color:#667}.ok{color:#7d8}</style></head><body>
<h1>《移动UI交互设计》视频课件 · 43 段全量 <span class="tag review">B4 批次待审（全量完成）</span></h1>
<p class="meta">读本十二章 × 章节化分段教学片（43 段 ≈ 215 分钟）；画面主体＝自绘梧桐市集 App 界面（U1–U6 类型体系，界面状态机为主力）；
贯穿案例＝梧桐市集冻结包（12 章版本演进线）；配音 CosyVoice v2 · 龙小淳；sol(gpt-6.1-sol 高推理) 代码确定性渲染；
门禁：时长 ≥270s ＋ 冻结扫描 ＋ 底部字幕带 VLM 复核。
{{STATS}}<br><b style="color:#8ff">审片提示</b>：B1（ch1–3）与 B2（ch4–6）已通过用户审核；B3（第7–9章新制九段＋种子 mui-8-01）与 B4（绪论＋第10–12章＋案例专题共14段）已上线待审，至此 43 段全量完成。字幕安全带（y&gt;930）已按帧复核，五段重渲。
<br><a href="/">◀ 返回总入口</a> · <a href="/isdv.html">《室内空间设计》51 段</a> · <a href="/colorv.html">《室内色彩与图案设计》49 段</a></p>
{{BODY}}
</body></html>"""


def _mui_page():
    import json as _json
    parts, have, total, dsum = [], 0, 0, 0.0
    for _chname, _segs in MUI_CHAPTERS:
        rows = [f"<h2>{_chname}</h2>"]
        for _run, _title, _typ in _segs:
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            if not f.exists():
                rows.append(f'<div class="item"><s><b>{_title}</b></s><span class="tag">待批产</span></div>')
                total += 1
                continue
            have += 1
            total += 1
            dur = ""
            tm_p = ROOT / "audio" / f"timing_{_run}.json"
            if tm_p.exists():
                _d = _json.loads(tm_p.read_text(encoding="utf-8"))["total"]
                dsum += _d
                dur = f'<span class="dur">{_d/60:.1f} min · {int(_d)}s</span>'
            cls = "tag seed" if "种子片" in _typ else "tag"
            rows.append(
                f'<div class="item"><b>{_title}</b><span class="{cls}">{_typ}</span>'
                f'<span class="tag ok">门禁通过</span>{dur}'
                f'<video controls preload="metadata" src="/muiv/{_run}.mp4?v={_vtag(_run)}"></video></div>')
        parts.append("".join(rows))
    stats = f"当前成片 <b>{have}</b> / {total} 段 · 总时长 <b>{dsum/60:.0f} 分钟</b>。B1（ch1–3）与 B2（ch4–6）已审核通过；B3（第7–9章）与 B4（绪论＋ch10–12＋案例专题）已上线待审——43 段全量完成。"
    return MUI_PAGE_TPL.replace("{{STATS}}", stats).replace("{{BODY}}", "".join(parts))


def _labs_page():
    rows, featured = [], []
    for _id, _name, _ch, _status in LABS:
        if _status == "online":
            _url = f"/isd-{_id.lower()}.html"
            rows.append(f'<tr><td><b>{_id}</b></td><td><a href="{_url}">{_name}</a></td>'
                        f'<td>{_ch}</td><td><span class="tag">✅ 可玩</span></td></tr>')
            featured.append(f'<div class="item"><b><a href="{_url}">🎮 {_name}</a></b>'
                            f'<span class="tag">✅ 已上线</span><span class="meta"> · {_ch} · '
                            f'{LAB_FEATURED.get(_id, "")}</span></div>')
        elif _status == "preview":
            _url = "/isd-l06-preview.html"
            rows.append(f'<tr><td><b>{_id}</b></td><td><a href="{_url}">{_name}</a></td>'
                        f'<td>{_ch}</td><td><span class="tag">🧪 可体验</span></td></tr>')
            featured.append(f'<div class="item"><b><a href="{_url}">🧊 {_name}</a></b>'
                            f'<span class="tag">双档预演</span><span class="meta"> · Canvas离线兜底 / Three.js PBR增强；同一U90场景可旋转、缩放、切换五个视点并导出PNG。</span></div>')
        else:
            rows.append(f'<tr><td>{_id}</td><td>{_name}</td><td>{_ch}</td>'
                        f'<td><span class="tag todo">规划中</span></td></tr>')
    return LABS_PAGE.replace("{{ROWS}}", "".join(rows)).replace("{{FEATURED}}", "".join(featured))


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
                    f'<video controls preload="metadata" src="/{_k}.mp4?v=b5"></video></div>')
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
# Explicit Unsent production-test allowlist; no directory browsing or arbitrary file exposure.
import json as _unsent_json
_UNSENT_ROUTES = ROOT / "gallery_unsent" / "routes.json"
if _UNSENT_ROUTES.is_file():
    FILES.update({k: Path(v) for k, v in _unsent_json.loads(_UNSENT_ROUTES.read_text(encoding="utf-8")).items()})
_RACE_ROUTES = ROOT / "gallery_race" / "routes.json"
if _RACE_ROUTES.is_file():
    FILES.update({k: Path(v) for k, v in _unsent_json.loads(_RACE_ROUTES.read_text(encoding="utf-8")).items()})
_UNS_V2_ROUTES = ROOT / "gallery_unsent_v2" / "routes.json"
if _UNS_V2_ROUTES.is_file():
    FILES.update({k: Path(v) for k, v in _unsent_json.loads(_UNS_V2_ROUTES.read_text(encoding="utf-8")).items()})
# 《设计制图》线上实验（DRW-L03 三视图联动工作台，2026-11-03，零AI单文件）
FILES["/drwlab/sanshitou_lab.html"] = ROOT / "设计制图" / "线上实践" / "labs" / "DRW-L03" / "sanshitou_lab.html"
# 《设计制图》线上实验（DRW-L06 透视汇报工作台，2026-11-03，零AI单文件）
FILES["/drwlab/toushi_lab.html"] = ROOT / "设计制图" / "线上实践" / "labs" / "DRW-L06" / "toushi_lab.html"
# 《设计制图》线上实验（DRW-L11 图纸找错工作台，2026-11-03，零AI单文件）
FILES["/drwlab/zhaocuo_lab.html"] = ROOT / "设计制图" / "线上实践" / "labs" / "DRW-L11" / "zhaocuo_lab.html"
MIME[".json"] = "application/json; charset=utf-8"
PORT = 8861

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>T1 种子对比 · 个人空间与人际距离</title>
<style>body{background:#10151c;color:#dfe7ee;font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 16px}
h1{font-size:20px}h2{font-size:15px;color:#8fb;margin-top:28px}a{color:#7fd}video{width:100%;border-radius:8px;background:#000}
.meta{color:#9ab;font-size:13px;line-height:1.7}table{border-collapse:collapse;font-size:13px}
td,th{border:1px solid #2a3540;padding:4px 10px;text-align:left}th{color:#8fb}</style></head><body>
<h1>《看不见的气泡》T1 种子 · 两版对比</h1>
<p class="meta"><a href="/dsbb.html" style="color:#e8a07f;font-size:16px">▶《设计基础》视频课件批产画廊（B1—B5）</a><br><br>
<a href="/intros.html">▶ 章绪论十篇（每章 1-2 分钟导览，龙小淳配音）</a><br><a href="/cases.html">▶ 设计案例研究（论文框架教学片）</a><br>
<a href="/case-v2.html" style="color:#fc8">▶ 案例A v2 验收页（定稿）</a><br>
<a href="/case-2.html" style="color:#fc8">▶ 案例B《隔间》验收页（定稿）</a><br>
<a href="/first10.html">▶ 前三十六段正片批产（绪论→10.3 全书收官，龙小淳配音，sol 新制 34 段+换声 2 段）</a><br>
<a href="/dsbv.html" style="color:#e8a07f">▶《设计基础》视频课件 · 种子 1（已通过）</a> · <a href="/dsb5v.html" style="color:#e8a07f">种子 2（dsb-5-05 三层面积账 × 三方案路径）</a><br>
🎧 <a href="/qwen3tts.html" style="color:#fe8">qwen3-tts-flash 百炼试听（Cherry·26s）</a> · 旧课已归档网盘并清理本地（人体工程学/商业空间设计/光与色彩/室内色彩与图案设计/室内空间设计/室内构造与材料学/设计标准与规范/现代设计史/设计制图/移动UI交互设计）</p>
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
        if self.path == "/spikes.html":
            body = SPIKE_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/case-v2.html":
            body = CASE_V2_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/case-2.html":
            body = CASE2_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/cases.html":
            body = _cases_page().encode("utf-8")
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
        if self.path == "/app-pron-test.html":
            body = APP_PRON_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        import re as _re0
        # ===== DSB BATCH BEGIN（2026-11-27）/dsbv/<seg>.(mp4|-sheet.jpg|.md) =====
        _m = _re0.match(r"^/dsbv/(dsb-[A-Za-z0-9\-]+)\.mp4$", self.path.split("?", 1)[0])
        if _m:
            _run = _m.group(1)
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            if f.exists():
                self._send_file(f)
                return
        _m = _re0.match(r"^/dsbv/(dsb-[A-Za-z0-9\-]+)-sheet\.jpg$", self.path.split("?", 1)[0])
        if _m:
            _run = _m.group(1)
            f = ROOT / "runs" / _run / "out" / "qa_sheet.jpg"
            if f.exists():
                self._send_file(f)
                return
        _m = _re0.match(r"^/dsbv/(dsb-[A-Za-z0-9\-]+)\.md$", self.path.split("?", 1)[0])
        if _m:
            _run = _m.group(1)
            f = ROOT / "runs" / _run / f"topic-{_run}.md"
            if f.exists():
                self._send_file(f)
                return
        # ===== DSB BATCH END =====
        _request_path = urllib.parse.unquote(self.path.split("?", 1)[0])
        if _request_path == "/unsent.html" or _request_path.startswith("/unsent/"):
            try:
                _current_unsent = _unsent_json.loads(_UNSENT_ROUTES.read_text(encoding="utf-8"))
                f = Path(_current_unsent[_request_path]) if _request_path in _current_unsent else None
            except (OSError, ValueError):
                f = None
        else:
            f = FILES.get(_request_path)
        if self.path.split("?", 1)[0] == "/spike-evaluation.md":
            f = ROOT / "runs" / "urban-doc-style-spike" / "EVALUATION.md"
        if f and f.exists():
            self._send_file(f)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def do_HEAD(self):
        import re as _reH
        _m = _reH.match(r"^/(?:isdv|colorv|muiv|drwv|lightcolorv)/(isd-|color-|mui-|drw-|lightcolor-)([A-Za-z0-9\-]+)(-sheet)?\.jpg$", self.path.split("?", 1)[0])
        if _m:
            f = (ROOT / "runs" / (_m.group(1) + _m.group(2)) / "out" / "qa_sheet.jpg") if _m.group(3) else None
            if f and f.exists():
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(f.stat().st_size))
                self.end_headers()
                return
        _m = _reH.match(r"^/(?:isdv|colorv|muiv|drwv|lightcolorv)/(isd-|color-|mui-|drw-|lightcolor-)([A-Za-z0-9\-]+)\.mp4$", self.path.split("?", 1)[0])
        if _m:
            _run = _m.group(1) + _m.group(2)
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            if f.exists():
                size = f.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("ETag", f'W/"{int(f.stat().st_mtime)}-{size}"')
                self.end_headers()
                return
        # ===== DSB BATCH HEAD（2026-11-27）/dsbv/<seg>.(mp4|-sheet.jpg|.md) =====
        _m = _reH.match(r"^/dsbv/(dsb-[A-Za-z0-9\-]+)\.mp4$", self.path.split("?", 1)[0])
        if _m:
            _run = _m.group(1)
            f = ROOT / "runs" / _run / "out" / f"final_{_run}.mp4"
            if f.exists():
                size = f.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("ETag", f'W/"{int(f.stat().st_mtime)}-{size}"')
                self.end_headers()
                return
        _m = _reH.match(r"^/dsbv/(dsb-[A-Za-z0-9\-]+)-sheet\.jpg$", self.path.split("?", 1)[0])
        if _m:
            _run = _m.group(1)
            f = ROOT / "runs" / _run / "out" / "qa_sheet.jpg"
            if f.exists():
                size = f.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(size))
                self.end_headers()
                return
        _m = _reH.match(r"^/dsbv/(dsb-[A-Za-z0-9\-]+)\.md$", self.path.split("?", 1)[0])
        if _m:
            _run = _m.group(1)
            f = ROOT / "runs" / _run / f"topic-{_run}.md"
            if f.exists():
                size = f.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type", MIME.get(f.suffix, "application/octet-stream"))
                self.send_header("Content-Length", str(size))
                self.end_headers()
                return
        # ===== DSB BATCH HEAD END =====
        _request_path = urllib.parse.unquote(self.path.split("?", 1)[0])
        if _request_path == "/unsent.html" or _request_path.startswith("/unsent/"):
            try:
                _current_unsent = _unsent_json.loads(_UNSENT_ROUTES.read_text(encoding="utf-8"))
                f = Path(_current_unsent[_request_path]) if _request_path in _current_unsent else None
            except (OSError, ValueError):
                f = None
        else:
            f = FILES.get(_request_path)
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


# ======== LABS AUTO BEGIN (mount_labs.py) ========
# 本块由 _labs/mount_labs.py 生成，勿手改（重跑整块替换）
FILES["/drwlab/liangfang_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L01/liangfang_lab.html"
FILES["/drwlab/liangfang_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L01/qa_initial.png"
FILES["/drwlab/biaozhu_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L02/biaozhu_lab.html"
FILES["/drwlab/biaozhu_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L02/qa_initial.png"
FILES["/drwlab/chaijie_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L04/chaijie_lab.html"
FILES["/drwlab/chaijie_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L04/qa_initial.png"
FILES["/drwlab/zhouce_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L05/zhouce_lab.html"
FILES["/drwlab/zhouce_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L05/qa_initial.png"
FILES["/drwlab/xunbao_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L07/xunbao_lab.html"
FILES["/drwlab/xunbao_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L07/qa_initial.png"
FILES["/drwlab/buju_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L08/buju_lab.html"
FILES["/drwlab/buju_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L08/qa_initial.png"
FILES["/drwlab/pouqie_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L09/pouqie_lab.html"
FILES["/drwlab/pouqie_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L09/qa_initial.png"
FILES["/drwlab/mulu_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L10/mulu_lab.html"
FILES["/drwlab/mulu_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L10/qa_initial.png"
FILES["/drwlab/zhengtao_lab.html"] = ROOT / "设计制图/线上实践/labs/DRW-L12/zhengtao_lab.html"
FILES["/drwlab/zhengtao_lab-qa.png"] = ROOT / "设计制图/线上实践/labs/DRW-L12/qa_initial.png"
FILES["/isd-l01.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L01/friction_lab.html"
FILES["/isd-l01-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L01/qa_initial.png"
FILES["/isd-l02.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L02/human_lab.html"
FILES["/isd-l02-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L02/qa_initial.png"
FILES["/isd-l05.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L05/route_lab.html"
FILES["/isd-l05-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L05/qa_initial.png"
FILES["/isd-l06.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L06/enclosure_lab.html"
FILES["/isd-l06-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L06/qa_initial.png"
FILES["/isd-l07.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L07/daylight_lab.html"
FILES["/isd-l07-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L07/qa_initial.png"
FILES["/isd-l08.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L08/material_lab.html"
FILES["/isd-l08-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L08/qa_initial.png"
FILES["/isd-l09.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L09/storage_lab.html"
FILES["/isd-l09-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L09/qa_initial.png"
FILES["/isd-l10.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L10/techq_lab.html"
FILES["/isd-l10-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L10/qa_initial.png"
FILES["/isd-l11.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L11/review_lab.html"
FILES["/isd-l11-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L11/qa_initial.png"
FILES["/isd-l12.html"] = ROOT / "室内空间设计/线上实践/labs/ISD-L12/portfolio_lab.html"
FILES["/isd-l12-qa.png"] = ROOT / "室内空间设计/线上实践/labs/ISD-L12/qa_initial.png"
FILES["/bsdlab/dongxian_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L05/dongxian_lab.html"
FILES["/bsdlab/dongxian_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L05/qa_initial.png"
FILES["/bsdlab/chenlie_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L07/chenlie_lab.html"
FILES["/bsdlab/chenlie_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L07/qa_initial.png"
FILES["/bsdlab/zhaoming_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L08/zhaoming_lab.html"
FILES["/bsdlab/zhaoming_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L08/qa_initial.png"
FILES["/bsdlab/gainian_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L04/gainian_lab.html"
FILES["/bsdlab/gainian_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L04/qa_initial.png"
FILES["/bsdlab/cailiao_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L09/cailiao_lab.html"
FILES["/bsdlab/cailiao_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L09/qa_initial.png"
FILES["/bsdlab/daopai_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L11/daopai_lab.html"
FILES["/bsdlab/daopai_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L11/qa_initial.png"
FILES["/bsdlab/dutu_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L03/dutu_lab.html"
FILES["/bsdlab/dutu_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L03/qa_initial.png"
FILES["/bsdlab/menmian_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L06/menmian_lab.html"
FILES["/bsdlab/menmian_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L06/qa_initial.png"
FILES["/bsdlab/chudian_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L10/chudian_lab.html"
FILES["/bsdlab/chudian_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L10/qa_initial.png"
FILES["/bsdlab/jingji_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L01/jingji_lab.html"
FILES["/bsdlab/jingji_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L01/qa_initial.png"
FILES["/bsdlab/lvcheng_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L02/lvcheng_lab.html"
FILES["/bsdlab/lvcheng_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L02/qa_initial.png"
FILES["/bsdlab/dabian_lab.html"] = ROOT / "商业空间设计/线上实践/labs/BSD-L12/dabian_lab.html"
FILES["/bsdlab/dabian_lab-qa.png"] = ROOT / "商业空间设计/线上实践/labs/BSD-L12/qa_initial.png"
FILES["/dsslab/biaozhun_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L01/biaozhun_lab.html"
FILES["/dsslab/yiju_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L02/yiju_lab.html"
FILES["/dsslab/mianji_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L03/mianji_lab.html"
FILES["/dsslab/duibiao_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L04/duibiao_lab.html"
FILES["/dsslab/tumian_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L05/tumian_lab.html"
FILES["/dsslab/shusan_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L06/shusan_lab.html"
FILES["/dsslab/wuzhangai_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L07/wuzhangai_lab.html"
FILES["/dsslab/zhaodu_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L08/zhaodu_lab.html"
FILES["/dsslab/huanbao_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L09/huanbao_lab.html"
FILES["/dsslab/lvjian_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L10/lvjian_lab.html"
FILES["/dsslab/jingju_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L11/jingju_lab.html"
FILES["/dsslab/yanshou_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L12/yanshou_lab.html"
FILES["/dsslab/shenbao_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L13/shenbao_lab.html"
FILES["/dsslab/liuhen_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L14/liuhen_lab.html"
FILES["/dsslab/zonghe_lab.html"] = ROOT / "设计标准与规范/线上实践/labs/DSS-L15/zonghe_lab.html"

_ISD_STATUS = {"L03": "online", "L04": "online", "L04K": "online", "L06P": "preview", "L01": "online", "L02": "online", "L05": "online", "L06": "online", "L07": "online", "L08": "online", "L09": "online", "L10": "online", "L11": "online", "L12": "online"}
_LAB_ROUTES = {"L01": "/isd-l01.html", "L02": "/isd-l02.html", "L03": "/isd-l03.html", "L04": "/isd-l04.html", "L04K": "/isd-l04k.html", "L05": "/isd-l05.html", "L06P": "/isd-l06-preview.html", "L06": "/isd-l06.html", "L07": "/isd-l07.html", "L08": "/isd-l08.html", "L09": "/isd-l09.html", "L10": "/isd-l10.html", "L11": "/isd-l11.html", "L12": "/isd-l12.html"}
_ISD_LABS = [["L01", "观察与问题标注：居住摩擦证据图", "第1–2章"], ["L02", "人体尺度与动作包络叠加", "第3章"], ["L03", "居住需求档案与气泡图任务书", "第2章"], ["L04", "U90全户型功能组织与动线冲突", "第4章"], ["L04K", "厨房工作三角与折返计数", "第7章"], ["L05", "动线与通达：起终点与障碍路径", "第4章"], ["L06P", "U90 双档3D渲染预演（L06渲染层）", "第5–6章"], ["L06", "空间围合与视线分析", "第5–6章"], ["L07", "采光与照明四场景切换", "第8章"], ["L08", "材料色彩七属性对比", "第9章"], ["L09", "家具收纳与多情境切换", "第10章"], ["L10", "技术疑点三层分类与待核单", "第11章"], ["L11", "A/B 表达与同伴评议", "第12章"], ["L12", "综合项目作品包（承接各实验）", "第12章"]]
_DRW_ROWS = [["DRW-L01", "量你自己的房间（尺寸账·闭合检查）", "第1章", "online", "/drwlab/liangfang_lab.html"], ["DRW-L02", "尺寸标注工作台★（四要素·三层）", "第2章", "online", "/drwlab/biaozhu_lab.html"], ["DRW-L04", "形体拆解实验（爆炸拆解·三视图）", "第4章", "online", "/drwlab/chaijie_lab.html"], ["DRW-L05", "轴测参数工作台（斜二测/正等测双窗）", "第5章", "online", "/drwlab/zhouce_lab.html"], ["DRW-L07", "建施图寻宝（分层·三问·跨图对数）", "第7章", "online", "/drwlab/xunbao_lab.html"], ["DRW-L08", "平面布置工作台★（家具·动线净宽）", "第8章", "online", "/drwlab/buju_lab.html"], ["DRW-L09", "剖切位置选择器（节点轮廓·索引闭环）", "第9章", "online", "/drwlab/pouqie_lab.html"], ["DRW-L10", "图纸目录拼装（五类错·版本账）", "第10章", "online", "/drwlab/mulu_lab.html"], ["DRW-L12", "全套整合＋答辩导出（三笔账）", "第12章", "online", "/drwlab/zhengtao_lab.html"]]
_BSD_ROWS = [["BSD-L05", "动线与坪效★（拖拽布局·三读数联动）", "第5章", "online", "/bsdlab/dongxian_lab.html"], ["BSD-L07", "陈列布点★（VP/PP/IP分层·五画像路径）", "第7章", "online", "/bsdlab/chenlie_lab.html"], ["BSD-L08", "照明方案与验收★（三层光·E=I÷d²）", "第8章", "online", "/bsdlab/zhaoming_lab.html"], ["BSD-L04", "品牌概念板★（三轨令牌·删词测试）", "第4章", "online", "/bsdlab/gainian_lab.html"], ["BSD-L09", "材料板与工艺方案★（样板·对色·全周期账）", "第9章", "online", "/bsdlab/cailiao_lab.html"], ["BSD-L11", "开业倒排计划与预算表★（关键路径·延误代价）", "第11章", "online", "/bsdlab/daopai_lab.html"], ["BSD-L03", "商场平面读图（业态配比·主力店·走线）", "第3章", "online", "/bsdlab/dutu_lab.html"], ["BSD-L06", "门面三视角（店招·橱窗·三秒可读）", "第6章", "online", "/bsdlab/menmian_lab.html"], ["BSD-L10", "触点地图与整改清单★（旅程×触点·硬规则排期）", "第10章", "online", "/bsdlab/chudian_lab.html"], ["BSD-L01", "同场竞技（三店×指标×时段蹲点对照）", "第1章", "online", "/bsdlab/jingji_lab.html"], ["BSD-L02", "顾客旅程图（时间轴·情绪曲线·掉队标记）", "第2章", "online", "/bsdlab/lvcheng_lab.html"], ["BSD-L12", "课程总答辩★（方案总包·满月对账·一分钟版）", "第12章", "online", "/bsdlab/dabian_lab.html"]]
_DSS_ROWS = [["DSS-L01", "标准登记台★（5部×六项信息·检索渠道）", "第1章", "online", "/dsslab/biaozhun_lab.html"], ["DSS-L02", "设计依据清单编制（六板块·冲突优先次序）", "第2章", "online", "/dsslab/yiju_lab.html"], ["DSS-L03", "面积判定标注（2.20m分界·全面积/1/2）", "第3章", "online", "/dsslab/mianji_lab.html"], ["DSS-L04", "新旧住宅指标对照卡（8组·旧值标废止）", "第4章", "online", "/dsslab/duibiao_lab.html"], ["DSS-L05", "图面符号自查（目录编排·符号必要性）", "第5章", "online", "/dsslab/tumian_lab.html"], ["DSS-L06", "疏散宽度计算台★（四步同屏·双线核净宽）", "第6章", "online", "/dsslab/shusan_lab.html"], ["DSS-L07", "无障碍路径核查（1:12·1.20·850/650·1.50）", "第7章", "online", "/dsslab/wuzhangai_lab.html"], ["DSS-L08", "照度实测比对（测点·均匀度·偏差整改）", "第8章", "online", "/dsslab/zhaodu_lab.html"], ["DSS-L09", "材料环保验收计划（限量·报告·节点）", "第9章", "online", "/dsslab/huanbao_lab.html"], ["DSS-L10", "绿色建材选样表（认证·限量·节能）", "第10章", "online", "/dsslab/lvjian_lab.html"], ["DSS-L11", "家具净距校核（主通道900·次通道600）", "第11章", "online", "/dsslab/jingju_lab.html"], ["DSS-L12", "分项工程验收计划（层级·隐蔽节点）", "第12章", "online", "/dsslab/yanshou_lab.html"], ["DSS-L13", "开工申报材料清单（材料·禁止行为·作业时间）", "第13章", "online", "/dsslab/shenbao_lab.html"], ["DSS-L14", "四阶段合规留痕（方案/初设/施工图/验收）", "第14章", "online", "/dsslab/liuhen_lab.html"], ["DSS-L15", "综合审查台★（四张表＋计算书＋四段报告）", "附录", "online", "/dsslab/zonghe_lab.html"]]
FILES["/dsslab/"] = ROOT / "_labs/dss_labs_index.html"

def _labs_page():
    rows, featured, drw, bsd, dss = [], [], [], [], []
    for _id, _name, _ch in _ISD_LABS:
        _status = _ISD_STATUS.get(_id, "规划中")
        _url = _LAB_ROUTES.get(_id, f"/isd-{_id.lower().replace('isd-', '', 1)}.html")
        if _status == "online":
            rows.append(f'<tr><td><b>{_id}</b></td><td><a href="{_url}">{_name}</a></td>'
                        f'<td>{_ch}</td><td><span class="tag">✅ 可玩</span></td></tr>')
            featured.append(f'<div class="item"><b><a href="{_url}">🎮 {_name}</a></b>'
                            f'<span class="tag">✅ 已上线</span>'
                            f'<span class="meta"> · {_ch}</span></div>')
        elif _status == "preview":
            rows.append(f'<tr><td><b>{_id}</b></td><td><a href="{_url}">{_name}</a></td>'
                        f'<td>{_ch}</td><td><span class="tag">🧪 可体验</span></td></tr>')
        else:
            _t = "试玩" if _status == "试玩" else "规划中"
            rows.append(f'<tr><td>{_id}</td><td>{_name}</td><td>{_ch}</td>'
                        f'<td><span class="tag todo">{_t}</span></td></tr>')
    for _id, _name, _ch, _st, _url in _DRW_ROWS:
        if _st == "online":
            drw.append(f'<tr><td><b>{_id}</b></td><td><a href="{_url}">{_name}</a></td>'
                       f'<td>{_ch}</td><td><span class="tag">✅ 可玩</span></td></tr>')
        else:
            _t = "试玩" if _st == "试玩" else "规划中"
            drw.append(f'<tr><td>{_id}</td><td>{_name}</td><td>{_ch}</td>'
                       f'<td><span class="tag todo">{_t}</span></td></tr>')
    for _id, _name, _ch, _st, _url in _BSD_ROWS:
        if _st == "online":
            bsd.append(f'<tr><td><b>{_id}</b></td><td><a href="{_url}">{_name}</a></td>'
                       f'<td>{_ch}</td><td><span class="tag">✅ 可玩</span></td></tr>')
        else:
            _t = "试玩" if _st == "试玩" else "规划中"
            bsd.append(f'<tr><td>{_id}</td><td>{_name}</td><td>{_ch}</td>'
                       f'<td><span class="tag todo">{_t}</span></td></tr>')
    for _id, _name, _ch, _st, _url in _DSS_ROWS:
        if _st == "online":
            dss.append(f'<tr><td><b>{_id}</b></td><td><a href="{_url}">{_name}</a></td>'
                       f'<td>{_ch}</td><td><span class="tag">✅ 可玩</span></td></tr>')
        else:
            _t = "试玩" if _st == "试玩" else "规划中"
            dss.append(f'<tr><td>{_id}</td><td>{_name}</td><td>{_ch}</td>'
                       f'<td><span class="tag todo">{_t}</span></td></tr>')
    return (LABS_PAGE.replace("{{ROWS}}", "".join(rows))
                     .replace("{{FEATURED}}", "".join(featured))
                     .replace("{{DRWROWS}}", "".join(drw))
                     .replace("{{BSDROWS}}", "".join(bsd))
                     .replace("{{DSSROWS}}", "".join(dss)))


_H1_OLD = "<h1>《室内空间设计》线上实践 · 实验目录</h1>"
_H1_NEW = "<h1>线上实践 · 交互实验目录（《室内空间设计》＋《设计制图》）</h1>"
if _H1_OLD in LABS_PAGE:
    LABS_PAGE = LABS_PAGE.replace(_H1_OLD, _H1_NEW)
LABS_PAGE = LABS_PAGE.replace("（《室内空间设计》＋《设计制图》）</h1>", "（《室内空间设计》＋《设计制图》＋《商业空间设计》）</h1>", 1)
_TBL_ANCHOR = ("<table><tr><th>编号</th><th>实验</th><th>教材锚点</th><th>状态</th></tr>"
               "{{ROWS}}</table>")
if "{{DRWROWS}}" not in LABS_PAGE and _TBL_ANCHOR in LABS_PAGE:
    LABS_PAGE = LABS_PAGE.replace(
        _TBL_ANCHOR,
        _TBL_ANCHOR + '\n<h2>《设计制图》线上实践 · 实验目录</h2>'
        '<p class="meta">配套读本 v1.0（12章）· 一章一实验 · 青枫里401冻结包；'
        '导出契约 drw-lab-v1；三层反馈分列，不合成总分。</p>'
        '<table><tr><th>编号</th><th>实验</th><th>教材锚点</th><th>状态</th></tr>{{DRWROWS}}</table>')
if "{{BSDROWS}}" not in LABS_PAGE and "{{DRWROWS}}</table>" in LABS_PAGE:
    LABS_PAGE = LABS_PAGE.replace(
        "{{DRWROWS}}</table>",
        "{{DRWROWS}}</table>"
        '\n<h2>《商业空间设计》线上实践 · 实验目录</h2>'
        '<p class="meta">配套读本审阅版 v1（12章）· 一章一实验 · 梧桐市集云梧广场店冻结包；'
        '导出契约 lab-submit-v1（window.LAB.submit）· 提交栏常驻可部分提交；三层反馈分列，不合成总分。</p>'
        '<table><tr><th>编号</th><th>实验</th><th>教材锚点</th><th>状态</th></tr>{{BSDROWS}}</table>', 1)
if "{{DSSROWS}}" not in LABS_PAGE and "{{BSDROWS}}</table>" in LABS_PAGE:
    LABS_PAGE = LABS_PAGE.replace(
        "{{BSDROWS}}</table>",
        "{{BSDROWS}}</table>"
        '\n<h2>《设计标准与规范》线上实践 · 实验目录</h2>'
        '<p class="meta">配套教材 14 章 ＋ 附录综合实训（15 个实验，一章一实训）· 云岫路18号 200㎡餐饮空间教学案例；'
        '统一契约 lab-submit-v1（window.LAB.submit）· 提交栏常驻可部分提交；三层反馈分列，不合成总分。</p>'
        '<table><tr><th>编号</th><th>实验</th><th>教材锚点</th><th>状态</th></tr>{{DSSROWS}}</table>', 1)

# ======== LABS AUTO END ========




































































# ======== IJC GALLERY AUTO BEGIN ========
# 本块由 _labs/ijc_gallery.py 生成，勿手改（重跑整块替换）
_ijc_runs = ROOT / "runs"
FILES["/ijc/v/ijc-1-1.mp4"] = _ijc_runs / "ijc-1-1/out/final_ijc-1-1.mp4"
FILES["/ijc/img/ijc-1-1.jpg"] = _ijc_runs / "ijc-1-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-1-2.mp4"] = _ijc_runs / "ijc-1-2/out/final_ijc-1-2.mp4"
FILES["/ijc/img/ijc-1-2.jpg"] = _ijc_runs / "ijc-1-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-10-1.mp4"] = _ijc_runs / "ijc-10-1/out/final_ijc-10-1.mp4"
FILES["/ijc/img/ijc-10-1.jpg"] = _ijc_runs / "ijc-10-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-10-2.mp4"] = _ijc_runs / "ijc-10-2/out/final_ijc-10-2.mp4"
FILES["/ijc/img/ijc-10-2.jpg"] = _ijc_runs / "ijc-10-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-10-3.mp4"] = _ijc_runs / "ijc-10-3/out/final_ijc-10-3.mp4"
FILES["/ijc/img/ijc-10-3.jpg"] = _ijc_runs / "ijc-10-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-11-1.mp4"] = _ijc_runs / "ijc-11-1/out/final_ijc-11-1.mp4"
FILES["/ijc/img/ijc-11-1.jpg"] = _ijc_runs / "ijc-11-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-11-2.mp4"] = _ijc_runs / "ijc-11-2/out/final_ijc-11-2.mp4"
FILES["/ijc/img/ijc-11-2.jpg"] = _ijc_runs / "ijc-11-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-12-1.mp4"] = _ijc_runs / "ijc-12-1/out/final_ijc-12-1.mp4"
FILES["/ijc/img/ijc-12-1.jpg"] = _ijc_runs / "ijc-12-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-12-2.mp4"] = _ijc_runs / "ijc-12-2/out/final_ijc-12-2.mp4"
FILES["/ijc/img/ijc-12-2.jpg"] = _ijc_runs / "ijc-12-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-12-3.mp4"] = _ijc_runs / "ijc-12-3/out/final_ijc-12-3.mp4"
FILES["/ijc/img/ijc-12-3.jpg"] = _ijc_runs / "ijc-12-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-13-1.mp4"] = _ijc_runs / "ijc-13-1/out/final_ijc-13-1.mp4"
FILES["/ijc/img/ijc-13-1.jpg"] = _ijc_runs / "ijc-13-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-13-2.mp4"] = _ijc_runs / "ijc-13-2/out/final_ijc-13-2.mp4"
FILES["/ijc/img/ijc-13-2.jpg"] = _ijc_runs / "ijc-13-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-13-3.mp4"] = _ijc_runs / "ijc-13-3/out/final_ijc-13-3.mp4"
FILES["/ijc/img/ijc-13-3.jpg"] = _ijc_runs / "ijc-13-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-14-1.mp4"] = _ijc_runs / "ijc-14-1/out/final_ijc-14-1.mp4"
FILES["/ijc/img/ijc-14-1.jpg"] = _ijc_runs / "ijc-14-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-14-2.mp4"] = _ijc_runs / "ijc-14-2/out/final_ijc-14-2.mp4"
FILES["/ijc/img/ijc-14-2.jpg"] = _ijc_runs / "ijc-14-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-14-3.mp4"] = _ijc_runs / "ijc-14-3/out/final_ijc-14-3.mp4"
FILES["/ijc/img/ijc-14-3.jpg"] = _ijc_runs / "ijc-14-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-15-1.mp4"] = _ijc_runs / "ijc-15-1/out/final_ijc-15-1.mp4"
FILES["/ijc/img/ijc-15-1.jpg"] = _ijc_runs / "ijc-15-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-15-2.mp4"] = _ijc_runs / "ijc-15-2/out/final_ijc-15-2.mp4"
FILES["/ijc/img/ijc-15-2.jpg"] = _ijc_runs / "ijc-15-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-15-3.mp4"] = _ijc_runs / "ijc-15-3/out/final_ijc-15-3.mp4"
FILES["/ijc/img/ijc-15-3.jpg"] = _ijc_runs / "ijc-15-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-2-1.mp4"] = _ijc_runs / "ijc-2-1/out/final_ijc-2-1.mp4"
FILES["/ijc/img/ijc-2-1.jpg"] = _ijc_runs / "ijc-2-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-2-2.mp4"] = _ijc_runs / "ijc-2-2/out/final_ijc-2-2.mp4"
FILES["/ijc/img/ijc-2-2.jpg"] = _ijc_runs / "ijc-2-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-2-3.mp4"] = _ijc_runs / "ijc-2-3/out/final_ijc-2-3.mp4"
FILES["/ijc/img/ijc-2-3.jpg"] = _ijc_runs / "ijc-2-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-3-1.mp4"] = _ijc_runs / "ijc-3-1/out/final_ijc-3-1.mp4"
FILES["/ijc/img/ijc-3-1.jpg"] = _ijc_runs / "ijc-3-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-3-2.mp4"] = _ijc_runs / "ijc-3-2/out/final_ijc-3-2.mp4"
FILES["/ijc/img/ijc-3-2.jpg"] = _ijc_runs / "ijc-3-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-3-3.mp4"] = _ijc_runs / "ijc-3-3/out/final_ijc-3-3.mp4"
FILES["/ijc/img/ijc-3-3.jpg"] = _ijc_runs / "ijc-3-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-4-1.mp4"] = _ijc_runs / "ijc-4-1/out/final_ijc-4-1.mp4"
FILES["/ijc/img/ijc-4-1.jpg"] = _ijc_runs / "ijc-4-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-4-2.mp4"] = _ijc_runs / "ijc-4-2/out/final_ijc-4-2.mp4"
FILES["/ijc/img/ijc-4-2.jpg"] = _ijc_runs / "ijc-4-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-4-3.mp4"] = _ijc_runs / "ijc-4-3/out/final_ijc-4-3.mp4"
FILES["/ijc/img/ijc-4-3.jpg"] = _ijc_runs / "ijc-4-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-5-1.mp4"] = _ijc_runs / "ijc-5-1/out/final_ijc-5-1.mp4"
FILES["/ijc/img/ijc-5-1.jpg"] = _ijc_runs / "ijc-5-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-5-2.mp4"] = _ijc_runs / "ijc-5-2/out/final_ijc-5-2.mp4"
FILES["/ijc/img/ijc-5-2.jpg"] = _ijc_runs / "ijc-5-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-5-3.mp4"] = _ijc_runs / "ijc-5-3/out/final_ijc-5-3.mp4"
FILES["/ijc/img/ijc-5-3.jpg"] = _ijc_runs / "ijc-5-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-6-1.mp4"] = _ijc_runs / "ijc-6-1/out/final_ijc-6-1.mp4"
FILES["/ijc/img/ijc-6-1.jpg"] = _ijc_runs / "ijc-6-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-6-2.mp4"] = _ijc_runs / "ijc-6-2/out/final_ijc-6-2.mp4"
FILES["/ijc/img/ijc-6-2.jpg"] = _ijc_runs / "ijc-6-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-7-1.mp4"] = _ijc_runs / "ijc-7-1/out/final_ijc-7-1.mp4"
FILES["/ijc/img/ijc-7-1.jpg"] = _ijc_runs / "ijc-7-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-7-2.mp4"] = _ijc_runs / "ijc-7-2/out/final_ijc-7-2.mp4"
FILES["/ijc/img/ijc-7-2.jpg"] = _ijc_runs / "ijc-7-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-8-1.mp4"] = _ijc_runs / "ijc-8-1/out/final_ijc-8-1.mp4"
FILES["/ijc/img/ijc-8-1.jpg"] = _ijc_runs / "ijc-8-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-8-2.mp4"] = _ijc_runs / "ijc-8-2/out/final_ijc-8-2.mp4"
FILES["/ijc/img/ijc-8-2.jpg"] = _ijc_runs / "ijc-8-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-8-3.mp4"] = _ijc_runs / "ijc-8-3/out/final_ijc-8-3.mp4"
FILES["/ijc/img/ijc-8-3.jpg"] = _ijc_runs / "ijc-8-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-9-1.mp4"] = _ijc_runs / "ijc-9-1/out/final_ijc-9-1.mp4"
FILES["/ijc/img/ijc-9-1.jpg"] = _ijc_runs / "ijc-9-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-9-2.mp4"] = _ijc_runs / "ijc-9-2/out/final_ijc-9-2.mp4"
FILES["/ijc/img/ijc-9-2.jpg"] = _ijc_runs / "ijc-9-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-9-3.mp4"] = _ijc_runs / "ijc-9-3/out/final_ijc-9-3.mp4"
FILES["/ijc/img/ijc-9-3.jpg"] = _ijc_runs / "ijc-9-3/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-ca-1.mp4"] = _ijc_runs / "ijc-ca-1/out/final_ijc-ca-1.mp4"
FILES["/ijc/img/ijc-ca-1.jpg"] = _ijc_runs / "ijc-ca-1/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-ca-2.mp4"] = _ijc_runs / "ijc-ca-2/out/final_ijc-ca-2.mp4"
FILES["/ijc/img/ijc-ca-2.jpg"] = _ijc_runs / "ijc-ca-2/out/qa_sheet.jpg"
FILES["/ijc/v/ijc-intro.mp4"] = _ijc_runs / "ijc-intro/out/final_ijc-intro.mp4"
FILES["/ijc/img/ijc-intro.jpg"] = _ijc_runs / "ijc-intro/out/qa_sheet.jpg"
# ======== IJC GALLERY AUTO END ========












# ======== ERG GALLERY AUTO BEGIN ========
# 本块由 _labs/erg_gallery.py 生成，勿手改（重跑整块替换）
_erg_runs = ROOT / "runs"
FILES["/erg/v/erg-1-1.mp4"] = _erg_runs / "erg-1-1/out/final_erg-1-1.mp4"
FILES["/erg/img/erg-1-1.jpg"] = _erg_runs / "erg-1-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-1-2.mp4"] = _erg_runs / "erg-1-2/out/final_erg-1-2.mp4"
FILES["/erg/img/erg-1-2.jpg"] = _erg_runs / "erg-1-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-1-3.mp4"] = _erg_runs / "erg-1-3/out/final_erg-1-3.mp4"
FILES["/erg/img/erg-1-3.jpg"] = _erg_runs / "erg-1-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-2-1.mp4"] = _erg_runs / "erg-2-1/out/final_erg-2-1.mp4"
FILES["/erg/img/erg-2-1.jpg"] = _erg_runs / "erg-2-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-2-2.mp4"] = _erg_runs / "erg-2-2/out/final_erg-2-2.mp4"
FILES["/erg/img/erg-2-2.jpg"] = _erg_runs / "erg-2-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-2-3.mp4"] = _erg_runs / "erg-2-3/out/final_erg-2-3.mp4"
FILES["/erg/img/erg-2-3.jpg"] = _erg_runs / "erg-2-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-2-4.mp4"] = _erg_runs / "erg-2-4/out/final_erg-2-4.mp4"
FILES["/erg/img/erg-2-4.jpg"] = _erg_runs / "erg-2-4/out/qa_sheet.jpg"
FILES["/erg/v/erg-2-5.mp4"] = _erg_runs / "erg-2-5/out/final_erg-2-5.mp4"
FILES["/erg/img/erg-2-5.jpg"] = _erg_runs / "erg-2-5/out/qa_sheet.jpg"
FILES["/erg/v/erg-2-6.mp4"] = _erg_runs / "erg-2-6/out/final_erg-2-6.mp4"
FILES["/erg/img/erg-2-6.jpg"] = _erg_runs / "erg-2-6/out/qa_sheet.jpg"
FILES["/erg/v/erg-3-1.mp4"] = _erg_runs / "erg-3-1/out/final_erg-3-1.mp4"
FILES["/erg/img/erg-3-1.jpg"] = _erg_runs / "erg-3-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-3-2.mp4"] = _erg_runs / "erg-3-2/out/final_erg-3-2.mp4"
FILES["/erg/img/erg-3-2.jpg"] = _erg_runs / "erg-3-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-3-3.mp4"] = _erg_runs / "erg-3-3/out/final_erg-3-3.mp4"
FILES["/erg/img/erg-3-3.jpg"] = _erg_runs / "erg-3-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-3-4.mp4"] = _erg_runs / "erg-3-4/out/final_erg-3-4.mp4"
FILES["/erg/img/erg-3-4.jpg"] = _erg_runs / "erg-3-4/out/qa_sheet.jpg"
FILES["/erg/v/erg-3-5.mp4"] = _erg_runs / "erg-3-5/out/final_erg-3-5.mp4"
FILES["/erg/img/erg-3-5.jpg"] = _erg_runs / "erg-3-5/out/qa_sheet.jpg"
FILES["/erg/v/erg-4-1.mp4"] = _erg_runs / "erg-4-1/out/final_erg-4-1.mp4"
FILES["/erg/img/erg-4-1.jpg"] = _erg_runs / "erg-4-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-4-2.mp4"] = _erg_runs / "erg-4-2/out/final_erg-4-2.mp4"
FILES["/erg/img/erg-4-2.jpg"] = _erg_runs / "erg-4-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-4-3.mp4"] = _erg_runs / "erg-4-3/out/final_erg-4-3.mp4"
FILES["/erg/img/erg-4-3.jpg"] = _erg_runs / "erg-4-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-4-4.mp4"] = _erg_runs / "erg-4-4/out/final_erg-4-4.mp4"
FILES["/erg/img/erg-4-4.jpg"] = _erg_runs / "erg-4-4/out/qa_sheet.jpg"
FILES["/erg/v/erg-4-5.mp4"] = _erg_runs / "erg-4-5/out/final_erg-4-5.mp4"
FILES["/erg/img/erg-4-5.jpg"] = _erg_runs / "erg-4-5/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-1.mp4"] = _erg_runs / "erg-5-1/out/final_erg-5-1.mp4"
FILES["/erg/img/erg-5-1.jpg"] = _erg_runs / "erg-5-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-10.mp4"] = _erg_runs / "erg-5-10/out/final_erg-5-10.mp4"
FILES["/erg/img/erg-5-10.jpg"] = _erg_runs / "erg-5-10/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-2.mp4"] = _erg_runs / "erg-5-2/out/final_erg-5-2.mp4"
FILES["/erg/img/erg-5-2.jpg"] = _erg_runs / "erg-5-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-3.mp4"] = _erg_runs / "erg-5-3/out/final_erg-5-3.mp4"
FILES["/erg/img/erg-5-3.jpg"] = _erg_runs / "erg-5-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-4.mp4"] = _erg_runs / "erg-5-4/out/final_erg-5-4.mp4"
FILES["/erg/img/erg-5-4.jpg"] = _erg_runs / "erg-5-4/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-5.mp4"] = _erg_runs / "erg-5-5/out/final_erg-5-5.mp4"
FILES["/erg/img/erg-5-5.jpg"] = _erg_runs / "erg-5-5/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-6.mp4"] = _erg_runs / "erg-5-6/out/final_erg-5-6.mp4"
FILES["/erg/img/erg-5-6.jpg"] = _erg_runs / "erg-5-6/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-7.mp4"] = _erg_runs / "erg-5-7/out/final_erg-5-7.mp4"
FILES["/erg/img/erg-5-7.jpg"] = _erg_runs / "erg-5-7/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-8.mp4"] = _erg_runs / "erg-5-8/out/final_erg-5-8.mp4"
FILES["/erg/img/erg-5-8.jpg"] = _erg_runs / "erg-5-8/out/qa_sheet.jpg"
FILES["/erg/v/erg-5-9.mp4"] = _erg_runs / "erg-5-9/out/final_erg-5-9.mp4"
FILES["/erg/img/erg-5-9.jpg"] = _erg_runs / "erg-5-9/out/qa_sheet.jpg"
FILES["/erg/v/erg-6-1.mp4"] = _erg_runs / "erg-6-1/out/final_erg-6-1.mp4"
FILES["/erg/img/erg-6-1.jpg"] = _erg_runs / "erg-6-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-6-2.mp4"] = _erg_runs / "erg-6-2/out/final_erg-6-2.mp4"
FILES["/erg/img/erg-6-2.jpg"] = _erg_runs / "erg-6-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-6-3.mp4"] = _erg_runs / "erg-6-3/out/final_erg-6-3.mp4"
FILES["/erg/img/erg-6-3.jpg"] = _erg_runs / "erg-6-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-6-4.mp4"] = _erg_runs / "erg-6-4/out/final_erg-6-4.mp4"
FILES["/erg/img/erg-6-4.jpg"] = _erg_runs / "erg-6-4/out/qa_sheet.jpg"
FILES["/erg/v/erg-6-5.mp4"] = _erg_runs / "erg-6-5/out/final_erg-6-5.mp4"
FILES["/erg/img/erg-6-5.jpg"] = _erg_runs / "erg-6-5/out/qa_sheet.jpg"
FILES["/erg/v/erg-6-6.mp4"] = _erg_runs / "erg-6-6/out/final_erg-6-6.mp4"
FILES["/erg/img/erg-6-6.jpg"] = _erg_runs / "erg-6-6/out/qa_sheet.jpg"
FILES["/erg/v/erg-7-1.mp4"] = _erg_runs / "erg-7-1/out/final_erg-7-1.mp4"
FILES["/erg/img/erg-7-1.jpg"] = _erg_runs / "erg-7-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-7-2.mp4"] = _erg_runs / "erg-7-2/out/final_erg-7-2.mp4"
FILES["/erg/img/erg-7-2.jpg"] = _erg_runs / "erg-7-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-7-3.mp4"] = _erg_runs / "erg-7-3/out/final_erg-7-3.mp4"
FILES["/erg/img/erg-7-3.jpg"] = _erg_runs / "erg-7-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-7-4.mp4"] = _erg_runs / "erg-7-4/out/final_erg-7-4.mp4"
FILES["/erg/img/erg-7-4.jpg"] = _erg_runs / "erg-7-4/out/qa_sheet.jpg"
FILES["/erg/v/erg-7-5.mp4"] = _erg_runs / "erg-7-5/out/final_erg-7-5.mp4"
FILES["/erg/img/erg-7-5.jpg"] = _erg_runs / "erg-7-5/out/qa_sheet.jpg"
FILES["/erg/v/erg-7-6.mp4"] = _erg_runs / "erg-7-6/out/final_erg-7-6.mp4"
FILES["/erg/img/erg-7-6.jpg"] = _erg_runs / "erg-7-6/out/qa_sheet.jpg"
FILES["/erg/v/erg-8-1.mp4"] = _erg_runs / "erg-8-1/out/final_erg-8-1.mp4"
FILES["/erg/img/erg-8-1.jpg"] = _erg_runs / "erg-8-1/out/qa_sheet.jpg"
FILES["/erg/v/erg-8-2.mp4"] = _erg_runs / "erg-8-2/out/final_erg-8-2.mp4"
FILES["/erg/img/erg-8-2.jpg"] = _erg_runs / "erg-8-2/out/qa_sheet.jpg"
FILES["/erg/v/erg-8-3.mp4"] = _erg_runs / "erg-8-3/out/final_erg-8-3.mp4"
FILES["/erg/img/erg-8-3.jpg"] = _erg_runs / "erg-8-3/out/qa_sheet.jpg"
FILES["/erg/v/erg-8-4.mp4"] = _erg_runs / "erg-8-4/out/final_erg-8-4.mp4"
FILES["/erg/img/erg-8-4.jpg"] = _erg_runs / "erg-8-4/out/qa_sheet.jpg"
FILES["/erg/v/erg-CA1.mp4"] = _erg_runs / "erg-CA1/out/final_erg-CA1.mp4"
FILES["/erg/img/erg-CA1.jpg"] = _erg_runs / "erg-CA1/out/qa_sheet.jpg"
FILES["/erg/v/erg-CA2.mp4"] = _erg_runs / "erg-CA2/out/final_erg-CA2.mp4"
FILES["/erg/img/erg-CA2.jpg"] = _erg_runs / "erg-CA2/out/qa_sheet.jpg"
FILES["/erg/v/erg-INTRO.mp4"] = _erg_runs / "erg-INTRO/out/final_erg-INTRO.mp4"
FILES["/erg/img/erg-INTRO.jpg"] = _erg_runs / "erg-INTRO/out/qa_sheet.jpg"
# ======== ERG GALLERY AUTO END ========














# === DSS GALLERY AUTO BEGIN ===
# 本块由 _labs/dss_gallery.py 生成，勿手改（重跑整块替换）
_dss_runs = ROOT / "runs"
FILES["/dss/v/dss-1-1.mp4"] = _dss_runs / "dss-1-1/out/final_dss-1-1.mp4"
FILES["/dss/img/dss-1-1.jpg"] = _dss_runs / "dss-1-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-1-2.mp4"] = _dss_runs / "dss-1-2/out/final_dss-1-2.mp4"
FILES["/dss/img/dss-1-2.jpg"] = _dss_runs / "dss-1-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-2-1.mp4"] = _dss_runs / "dss-2-1/out/final_dss-2-1.mp4"
FILES["/dss/img/dss-2-1.jpg"] = _dss_runs / "dss-2-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-2-2.mp4"] = _dss_runs / "dss-2-2/out/final_dss-2-2.mp4"
FILES["/dss/img/dss-2-2.jpg"] = _dss_runs / "dss-2-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-3-1.mp4"] = _dss_runs / "dss-3-1/out/final_dss-3-1.mp4"
FILES["/dss/img/dss-3-1.jpg"] = _dss_runs / "dss-3-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-3-2.mp4"] = _dss_runs / "dss-3-2/out/final_dss-3-2.mp4"
FILES["/dss/img/dss-3-2.jpg"] = _dss_runs / "dss-3-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-4-1.mp4"] = _dss_runs / "dss-4-1/out/final_dss-4-1.mp4"
FILES["/dss/img/dss-4-1.jpg"] = _dss_runs / "dss-4-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-4-2.mp4"] = _dss_runs / "dss-4-2/out/final_dss-4-2.mp4"
FILES["/dss/img/dss-4-2.jpg"] = _dss_runs / "dss-4-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-4-3.mp4"] = _dss_runs / "dss-4-3/out/final_dss-4-3.mp4"
FILES["/dss/img/dss-4-3.jpg"] = _dss_runs / "dss-4-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-5-1.mp4"] = _dss_runs / "dss-5-1/out/final_dss-5-1.mp4"
FILES["/dss/img/dss-5-1.jpg"] = _dss_runs / "dss-5-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-5-2.mp4"] = _dss_runs / "dss-5-2/out/final_dss-5-2.mp4"
FILES["/dss/img/dss-5-2.jpg"] = _dss_runs / "dss-5-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-5-3.mp4"] = _dss_runs / "dss-5-3/out/final_dss-5-3.mp4"
FILES["/dss/img/dss-5-3.jpg"] = _dss_runs / "dss-5-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-6-1.mp4"] = _dss_runs / "dss-6-1/out/final_dss-6-1.mp4"
FILES["/dss/img/dss-6-1.jpg"] = _dss_runs / "dss-6-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-6-2.mp4"] = _dss_runs / "dss-6-2/out/final_dss-6-2.mp4"
FILES["/dss/img/dss-6-2.jpg"] = _dss_runs / "dss-6-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-6-3.mp4"] = _dss_runs / "dss-6-3/out/final_dss-6-3.mp4"
FILES["/dss/img/dss-6-3.jpg"] = _dss_runs / "dss-6-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-6-4.mp4"] = _dss_runs / "dss-6-4/out/final_dss-6-4.mp4"
FILES["/dss/img/dss-6-4.jpg"] = _dss_runs / "dss-6-4/out/qa_sheet.jpg"
FILES["/dss/v/dss-7-1.mp4"] = _dss_runs / "dss-7-1/out/final_dss-7-1.mp4"
FILES["/dss/img/dss-7-1.jpg"] = _dss_runs / "dss-7-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-7-2.mp4"] = _dss_runs / "dss-7-2/out/final_dss-7-2.mp4"
FILES["/dss/img/dss-7-2.jpg"] = _dss_runs / "dss-7-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-7-3.mp4"] = _dss_runs / "dss-7-3/out/final_dss-7-3.mp4"
FILES["/dss/img/dss-7-3.jpg"] = _dss_runs / "dss-7-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-8-1.mp4"] = _dss_runs / "dss-8-1/out/final_dss-8-1.mp4"
FILES["/dss/img/dss-8-1.jpg"] = _dss_runs / "dss-8-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-8-2.mp4"] = _dss_runs / "dss-8-2/out/final_dss-8-2.mp4"
FILES["/dss/img/dss-8-2.jpg"] = _dss_runs / "dss-8-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-8-3.mp4"] = _dss_runs / "dss-8-3/out/final_dss-8-3.mp4"
FILES["/dss/img/dss-8-3.jpg"] = _dss_runs / "dss-8-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-9-1.mp4"] = _dss_runs / "dss-9-1/out/final_dss-9-1.mp4"
FILES["/dss/img/dss-9-1.jpg"] = _dss_runs / "dss-9-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-9-2.mp4"] = _dss_runs / "dss-9-2/out/final_dss-9-2.mp4"
FILES["/dss/img/dss-9-2.jpg"] = _dss_runs / "dss-9-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-9-3.mp4"] = _dss_runs / "dss-9-3/out/final_dss-9-3.mp4"
FILES["/dss/img/dss-9-3.jpg"] = _dss_runs / "dss-9-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-10-1.mp4"] = _dss_runs / "dss-10-1/out/final_dss-10-1.mp4"
FILES["/dss/img/dss-10-1.jpg"] = _dss_runs / "dss-10-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-10-2.mp4"] = _dss_runs / "dss-10-2/out/final_dss-10-2.mp4"
FILES["/dss/img/dss-10-2.jpg"] = _dss_runs / "dss-10-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-10-3.mp4"] = _dss_runs / "dss-10-3/out/final_dss-10-3.mp4"
FILES["/dss/img/dss-10-3.jpg"] = _dss_runs / "dss-10-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-11-1.mp4"] = _dss_runs / "dss-11-1/out/final_dss-11-1.mp4"
FILES["/dss/img/dss-11-1.jpg"] = _dss_runs / "dss-11-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-11-2.mp4"] = _dss_runs / "dss-11-2/out/final_dss-11-2.mp4"
FILES["/dss/img/dss-11-2.jpg"] = _dss_runs / "dss-11-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-11-3.mp4"] = _dss_runs / "dss-11-3/out/final_dss-11-3.mp4"
FILES["/dss/img/dss-11-3.jpg"] = _dss_runs / "dss-11-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-12-1.mp4"] = _dss_runs / "dss-12-1/out/final_dss-12-1.mp4"
FILES["/dss/img/dss-12-1.jpg"] = _dss_runs / "dss-12-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-12-2.mp4"] = _dss_runs / "dss-12-2/out/final_dss-12-2.mp4"
FILES["/dss/img/dss-12-2.jpg"] = _dss_runs / "dss-12-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-12-3.mp4"] = _dss_runs / "dss-12-3/out/final_dss-12-3.mp4"
FILES["/dss/img/dss-12-3.jpg"] = _dss_runs / "dss-12-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-13-1.mp4"] = _dss_runs / "dss-13-1/out/final_dss-13-1.mp4"
FILES["/dss/img/dss-13-1.jpg"] = _dss_runs / "dss-13-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-13-2.mp4"] = _dss_runs / "dss-13-2/out/final_dss-13-2.mp4"
FILES["/dss/img/dss-13-2.jpg"] = _dss_runs / "dss-13-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-13-3.mp4"] = _dss_runs / "dss-13-3/out/final_dss-13-3.mp4"
FILES["/dss/img/dss-13-3.jpg"] = _dss_runs / "dss-13-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-14-1.mp4"] = _dss_runs / "dss-14-1/out/final_dss-14-1.mp4"
FILES["/dss/img/dss-14-1.jpg"] = _dss_runs / "dss-14-1/out/qa_sheet.jpg"
FILES["/dss/v/dss-14-2.mp4"] = _dss_runs / "dss-14-2/out/final_dss-14-2.mp4"
FILES["/dss/img/dss-14-2.jpg"] = _dss_runs / "dss-14-2/out/qa_sheet.jpg"
FILES["/dss/v/dss-14-3.mp4"] = _dss_runs / "dss-14-3/out/final_dss-14-3.mp4"
FILES["/dss/img/dss-14-3.jpg"] = _dss_runs / "dss-14-3/out/qa_sheet.jpg"
FILES["/dss/v/dss-附-1.mp4"] = _dss_runs / "dss-附-1/out/final_dss-附-1.mp4"
FILES["/dss/img/dss-附-1.jpg"] = _dss_runs / "dss-附-1/out/qa_sheet.jpg"
# === DSS GALLERY AUTO END ===

















socketserver.TCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"serving T1 compare page at http://100.84.28.40:{PORT}/ (0.0.0.0:{PORT})", flush=True)
    httpd.serve_forever()


