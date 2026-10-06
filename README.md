# 103 — AI 教学视频生产系统（ARCHITECTURE-v2）

> 系统约束"不能错什么"，模型自主决定"怎么表现"。权威架构：[`docs/ARCHITECTURE-v2.md`](docs/ARCHITECTURE-v2.md)

2026-10-06 架构转向：废弃"ClaudeAnimationBase+patterns.js 默认动画语言"，改为**自主生成主路径 + 项目级知识增强 + 多 renderer 后端**。转向证据链见 `docs/architecture-pivot-discussion-2026-10-06.md`；上一代 Stage1/2 文档见 `docs/Project103_Stage1_Core_Runtime.md` / `docs/Project103_Stage2_Narration_Timeline.md`。

## 布局

| 目录 | 内容 |
|---|---|
| `pipeline/` | **v2 自主生成脊柱**：storyboard→TTS→timing→renderer 决策（两步+why-not）→codegen→否决门→确定性渲染→QA→repair→mux。入口 `python -m pipeline.produce` |
| `knowledge/` | 知识库五分类（hard-facts / known-pitfalls / failure-cases / success-cases / project-routes），按模式条件检索 |
| `styles/hand-drawn/` | HAND_DRAWN_STYLE_PACK（可选风格包，显式请求才加载；原 pattern-library） |
| `profiles/` | production-profile（OPEN / ASSISTED / PROJECT_ROUTE） |
| `audio.py` + `audio/` | TTS→时序倒置→narration→audit→mux 链（已验证，脊柱复用） |
| `docs/` | ARCHITECTURE-v2 / 讨论纪要 / BAC（后端适配契约） |
| `spikes/` | capability-free spike 存档（svg-direct / remotion-textbook 等） |
| `base-compare/` | Case A-D 双模型对照实验存档（回归基线，含手绘宿主 runtime） |
| `runs/architecture-smoke/` | 无头渲染设施（compositor/ffmpeg 依赖宿主） |
| `p103/` | 上一代 Remotion 线包（run 管理/tts/timeline/video_qa） |

## 快速开始

```powershell
# 生产（默认 OPEN 模式，luna）
python -m pipeline.produce runs/my-topic --topic topic.md --title mytopic

# 项目固定路线
python -m pipeline.produce runs/g7-ep5 --topic topic.md --profile profiles/example.profile.yaml

# 菜单盲测采样（度量菜单税）
python -m pipeline.produce runs/blind-1 --topic topic.md --blind-sample

# 离线脊柱自测（零 LLM 消耗）
python -m pipeline.tests.test_offline
```

## 原则（冻结）

P1 体系层默认开放，项目层允许固定 · P2 硬约束保正确不规定创作 · P3 成功经验不得自动升格全局 · P4 Style Pack 可选非默认 · P5 视频感知无真实需求不建
