# HAND_DRAWN_STYLE_PACK — 手绘风格包

**地位**（ARCHITECTURE-v2 §5）：一种可选视觉风格，**不是**教学视频默认 runtime。仅在以下场景由用户/项目显式启用：

- 儿童内容 / 童书 / 水彩 / 人文故事 / 柔和视觉 / 创意 sketch / 用户点名手绘

## 内容物

| 文件 | 角色 |
|---|---|
| `patterns.js` | 实现 API（markAngle/superposeCopy/countUp/…）——**只属于本包**，不进入通用模型上下文 |
| `PATTERNS.md` | 本包 API 文档（含 2026-10-06 修订：markAngle 多态、superposeCopy delta 语义、narr n+1、ROLE/roleCol） |
| `MOTION_SKILL.md` | 手绘导演法——本包专用 |
| `PATTERN_CORPUS.md` + `corpus/` | 语料证据（历史资料） |
| `patterns_demo*.js` | 本包演示场景 |

## 启用方式

production-profile 中：

```yaml
visual:
  style_pack: hand-drawn      # 仅此一个字段即可激活
backend:
  preferred: web_2d           # 引擎宿主：无头 Chrome + runs/architecture-smoke 渲染设施
```

激活时 codegen 提示词注入 PATTERNS.md（含坑文档）；未激活时本目录内容**完全不进入模型上下文**。

## 引擎宿主

运行时引擎（core.js/render.mjs/studio.html，ClaudeAnimationBase）在 `runs/architecture-smoke/` 与 `base-compare/case-*/`（历史回归基线）。本包与引擎解耦：引擎是 WEB_2D 后端的一种宿主实现，不再是体系默认。

## 教学语义标签（已从本包剥离）

COMPARE / FREEZE_EVENT / REVEAL / TRACE / EMPHASIS / DERIVE 等标签现为全局审计词表（见 `knowledge/hard-facts/semantic-tags.md`），不绑定任何本包实现。
