"""prompts.py — v2 提示词族。铁律（ARCHITECTURE-v2 §3/§15）：
默认注入 = 内容 + 目标 + 数学约束 + TTS timing + 五关生产契约 + 后端能力/限制 + 输出要求。
绝不默认注入：Pattern API / 固定美学 / scene grammar / 成功案例。
风格包（hand-drawn）仅在 profile.visual.style_pack 显式设定时加载（§5.2）。
"""
from __future__ import annotations
import json
from pathlib import Path
from .backends import BACKENDS, menu_text

ROOT = Path(__file__).resolve().parent.parent
KNOW = ROOT / "knowledge"

PRODUCTION_CONTRACT = (KNOW / "hard-facts" / "production-contract.md").read_text(encoding="utf-8")


def _pitfalls(tags: list[str]) -> str:
    src = (KNOW / "known-pitfalls" / "INDEX.md").read_text(encoding="utf-8")
    hits = []
    for block in src.split("\n# "):
        if not block.strip() or block.startswith("# "):
            head = block.split("\n")[0]
        else:
            head = block.split("\n")[0]
        if any(t in head or t in block[:200] for t in ["全后端", "QA", "codegen", *tags]):
            hits.append("# " + block.strip()[:400])
    return "\n\n".join(hits[:6]) if hits else "（暂无该栈坑记录）"


def storyboard_prompt(topic: str, profile: dict) -> list[dict]:
    """分镜=内容+旁白+数学，渲染器中立。视觉设计留给 decide/codegen 阶段。
    旁白规格可由 profile["narration"] 覆盖（sentences/duration/note），
    缺省 8-12 句 / 20-35 秒（envpsy 5 分钟长片走 profile 覆盖）。"""
    # Storyboard 阶段只写内容/旁白/数学，不把任意 style_pack 误称为“手绘”。
    # 视觉规范在 codegen 阶段由原始 brief、决策方案与 profile.visual 显式注入。
    pk = ""
    nar = profile.get("narration") or {}
    sentences = nar.get("sentences", "8-12 句")
    duration = nar.get("duration", "约 20-35 秒")
    note = f"\n{nar['note']}" if nar.get("note") else ""
    return [{"role": "user", "content": f"""你是教学视频编剧。为主题写分镜脚本——只管内容、旁白与数学，不管视觉实现（视觉在后续阶段由设计决策独立完成）。

主题/教学内容：
{topic}

输出（纯文本，严格遵守）：
1. `## Narration` 段：中文旁白，每行一句并编号（1. 2. 3. …），{sentences}，口语化、可直接朗读，总朗读时长{duration}。
2. `## Parameters` 段：本题全部数学量的精确值（坐标/角度/长度/数值），带单位，供代码阶段直接使用与审计。
3. `## Math-check` 段：一行一个可机器验证的事实（如 三角度之和=180），供数学审计。

约束：数学必须自洽（Parameters 里的数值经得起重算）；旁白句即 TTS 单位；不要描述任何视觉/动画实现细节。{pk}{note}"""}]


def decision_prompts(topic: str, storyboard: str, profile: dict, blind: bool = False,
                     visual_plan: str = "") -> list[list[dict]]:
    """两步决策：A从brief+分镜+项目视觉约束独立规划；B收到A的明确文本后做后端选择。"""
    style_note = (profile.get("visual") or {}).get("style_note", "")
    step_a = [{"role": "user", "content": f"""你是视频技术总监。基于原始brief、教学分镜和项目视觉约束，规划视觉与渲染方案。

原始brief：
{topic}

分镜（内容+旁白+数学）：
{storyboard}

项目视觉约束：
{style_note or '无项目指定，按内容自主设计。'}

先回答（自由作答，不受任何选项限制）：
1. 这个内容最适合的视觉语言是什么？（风格、质感、信息层级）
2. 需要哪类渲染技术？（2D矢量/数学域引擎/3D/其他——按内容需求说，不要按熟悉度说）
3. 视觉方案最大的风险是什么？
简洁作答，这是设计判断，不是选择题。"""}]
    if blind:
        return [step_a]
    allowed = profile.get("backend", {}).get("allowed", list(BACKENDS))
    why_not = {k: "<一行理由>" for k in allowed}
    step_b = [{"role": "user", "content": f"""以下是步A刚生成的自由视觉规划（真实文本，非隐含对话上下文）：
{visual_plan or '（尚无自由规划文本）'}

基于这份规划，从可用后端中做出正式选择。

可用后端：
{menu_text(profile)}

五关生产契约（任何选择必须满足）：
{PRODUCTION_CONTRACT}

{'当前项目偏好后端: ' + str(profile['backend'].get('preferred')) + '（可偏离，须给理由）' if profile.get('backend', {}).get('preferred') else '无项目偏好。'}

输出 JSON（只输出 JSON）：
{{
  "backend": "WEB_2D|MANIM|THREE_3D|CUSTOM",
  "reason": "<为何最优，联系步A的自由规划>",
  "alternative": "<备选>",
  "risk": "<最大风险及对策，如风格同质化>",
  "why_not": {json.dumps(why_not, ensure_ascii=False)}
}}
CUSTOM 时额外字段 "nomination": {{"tech": "<技术名>", "env_check": "<环境验证命令>", "frame_check": "<10帧渲染命令>", "frame_out": "<帧输出目录>"}}。
菜单外提名若更合适是正确行为，不是违规。"""}]
    return [step_a, step_b]


def codegen_prompt(decision: dict, storyboard: str, timing: dict, profile: dict,
                   topic: str = "", visual_plan: str = "",
                   include_visual_context: bool = False) -> list[dict]:
    """自主代码生成。默认保持旧路径；仅显式 include_visual_context 时注入原始brief/设计方案/profile视觉契约。"""
    backend = decision["backend"].lower()
    b = BACKENDS[backend]
    visual = profile.get("visual") or {}
    style_pack = visual.get("style_pack")
    style_note = visual.get("style_note", "")
    pack = ""
    if style_pack == "hand-drawn":
        pat = (ROOT / "styles" / "hand-drawn" / "PATTERNS.md").read_text(encoding="utf-8")
        pack = f"\n## 风格包规范（显式启用 hand-drawn）\n{pat[:6000]}\n"
    elif style_pack:
        pack = f"\n## 项目显式视觉风格包：{style_pack}\n此名称本身不是API；请按下方项目视觉规范实现，不要虚构不存在的库。\n"
    visual_context = ""
    if include_visual_context:
        visual_context = f"""
## 原始教学/视觉 brief（旁白不是视觉分镜）
{topic or '（未提供原始brief）'}

## 技术总监视觉方案
{visual_plan or '（无额外自由规划文本）'}

## 项目视觉硬约束（profile.visual.style_note）
{style_note or '（项目未指定视觉硬约束，按内容自主设计）'}
{pack}
"""
    starts = timing["starts"] + [timing["total"]]          # KP-002：n+1，含 tEnd
    api_notes = ""
    if backend == "manim":                                  # 硬事实：API 签名卡（反幻觉）
        api_notes = "\n## Manim 0.21 API 事实卡（严格按签名写，勿发明参数）\n" + \
                    (KNOW / "hard-facts" / "manim-api-notes.md").read_text(encoding="utf-8")
    return [{"role": "user", "content": f"""你是自主动画工程师。为以下教学视频编写渲染代码——视觉方案由技术总监已定，实现方式完全由你决定。

## 分镜（内容/旁白/数学——数学量必须原样使用，可机器审计）
{storyboard}
{visual_context}

## 旁白物理时钟（TTS 实测；n+1 项=句起点+终点，最后一项是 tEnd，不是句子）
narr_starts = {json.dumps(starts)}
total = {timing['total']} 秒

## 生产契约（硬约束）
{PRODUCTION_CONTRACT}

## 后端契约（{b['name']}）
{b['contract']}

## 该栈已知坑（避坑用，不限制设计）
{_pitfalls(b['pitfall_tags'])}{api_notes}

## 输出要求
只输出一个代码块，内容为一个完整可运行文件（{ 'index.html（自包含，无网络依赖）' if backend == 'web_2d' else 'scene.py' }），不要解释。
质量标准：教学清晰第一；帧率 24；1920x1080；旁白句起点即事件锚点；同一 t 渲染结果必须可复现。"""}]


def repair_prompt(decision: dict, code: str, errors: list, frames_note: str) -> list[dict]:
    """定向修复：只喂归一化错误+帧证据，不重写全案。"""
    return [{"role": "user", "content": f"""渲染代码未通过 QA。请修复后重新输出完整文件（只输出代码块）。

## 后端
{decision['backend']}

## 归一化错误（QA 统一语义）
{json.dumps(errors[:20], ensure_ascii=False, indent=1)}

## 帧证据
{frames_note}

## 原代码
```
{code}
```

只修错误，不要改变视觉设计。"""}]
