# Base 对比报告 — Case A (GLM 5.3) vs Case B (gpt-6-luna) vs Opus 参照

日期：2026-10-05 · 方案：mathviz_motion_fast_production_plan.md §3-§4（Stage A 最小 Base 对比）

## 测试条件

| 项 | GLM 5.3（Case A） | gpt-6-luna（Case B） | Opus 5.5（参照） |
|---|---|---|---|
| 通道 | 智谱 coding 端点（直连） | codex-proxy 127.0.0.1:8080 | Claude Code + xhigh（作者环境） |
| 输入 | Guide 全文 + demo.js 格式例 + 一行提示词 | 同左（完全一致） | 仓库全量（含模型设定图、全部源码、agent 循环） |
| 参数 | temp 0.7 · max_tokens 32768 · **思考禁用*** | temp 1.0 · 65536 · 思考开启（276 reasoning tokens） | xhigh effort |
| 调用形态 | one-shot 单次 | one-shot 单次 | 多轮 agent（storyboard→逐镜→自检→修） |
| 耗时 | 71.5s | 77.7s | — |

\* GLM-5.3 官方不再支持禁用思考；开启时一次性大交付会烧满输出上限（16k/32k 两次实测截断于纯思考）。
已验证正确配方：分阶段交付 + reasoning_effort 保持默认 max + max_tokens 65536（storyboard-only 探针 6.3k 思考后自然收尾）。

## 交付结果

| 维度 | GLM | Luna |
|---|---|---|
| storyboard | ✅ 完整（logline/world/motif/情绪弧/3 镜头/转场/带时间戳 reads，八字环 motif 首尾呼应） | ✅ 完整（同结构；"learn to wait"主题变体） |
| 场景代码 | ✅ 11.3KB，一次可渲染 | ✅ 7.2KB，一次可渲染 |
| 渲染 | ✅ 360 帧/15s（~470ms/帧） | ✅ 360 帧/15s（~450ms/帧） |
| 人工修改 | 0 | 0 |
| config 自选 | bpm 96 | bpm 96 |
| 视觉快检（qwen3-vl 8 帧） | 无缺陷帧；叙事完整：打盹→发现→扑空→潜行二扑→花丛跌落→静止→落鼻→温馨收尾 | 无缺陷帧；叙事完整：发现→扑→沮丧→学会等待→落定→爱心收尾；含 1 个环境空镜转场 |

## §3.3 五维度初评（待用户三方向对比确认）

**A 可运行性**：两家均一次成功、零修复 — 远超"需要明显人工指导"档。
**B Motion 质量**：待看片判定（静态帧无法评 anticipation/overshoot/settle 的实际节奏）。
**C 视觉编排**：GLM 三镜头有明确机位变化（远景→中景→特写 iris 收尾）；Luna 有机位推近与空镜转场。初判均非"元素同时出现"的 PPT 模式。
**D Viewer Read**：两家 storyboard 的 reads 都带独立时间窗、无抢读 — 需看片验证实际节奏。
**E 修改成本**：目前均为"无需修改"档（渲染层面）。

## Token 账单（用户要求随交付统计）

| 调用 | prompt | completion（思考） | 有效产出 |
|---|---|---|---|
| GLM 尝试1（16k 截断） | 15,203 | 16,384（16,381） | ❌ |
| GLM 尝试2（32k 截断） | 15,203 | 32,768（32,764） | ❌ |
| GLM 尝试3（成品） | 15,203 | 5,844（37） | ✅ |
| GLM 探针（分阶段+max 档思考） | 10,186 | 8,060（6,301） | ✅ storyboard |
| Luna Case B | 15,070 | 4,133（276） | ✅ |
| **合计** | | **118,851 + Luna** | |

浪费 79,558 于思考截断（新配方可消除）；qwen3-vl 快检 ×2 ≈ 2k（审查辅助，不在生产管线）。

## 已知公平性缺口

1. Opus 参照有：模型设定图（emotions.jpg/views.jpg）、全部 runtime 源码、多轮 agent 自检循环；GLM/Luna 只有 Guide 文本 + demo.js。
2. GLM 成品为思考禁用产物；Luna 为思考开启产物 — 同题不同思考条件，对比时注意。
3. Opus 参照是官方 demo（11s，作者精修），非同题蝴蝶视频（作者测试过该提示词但未随仓库发布成品）。

## 文件

- GLM：`base-compare/case-a/out/glm_video.mp4` + `glm_contact_sheet.png` + `glm/STORYBOARD.md`
- Luna：`base-compare/case-b/out/luna_video.mp4` + `luna_contact_sheet.png` + `luna/STORYBOARD.md`
- Opus 参照：`base-compare/case-a/out/demo_opus_reference.mp4` + `opus_contact_sheet.png`
