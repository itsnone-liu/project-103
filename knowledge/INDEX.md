# 知识库索引（ARCHITECTURE-v2 §9-§14）

五分类，生命周期 candidate→validated→project-proven→production→deprecated。**默认不进入上下文**，按生产模式条件性检索（OPEN 不加载 / ASSISTED 按需 / PROJECT_ROUTE 按配置）。

| 目录 | 内容 | 默认 |
|---|---|---|
| `hard-facts/` | 数学事实、API 文档、渲染环境、生产协议、语义标签表 | 可默认使用 |
| `known-pitfalls/` | 已实证 API 陷阱/环境坑——作用是**避坑**不是指挥设计 | 相关任务条件检索 |
| `failure-cases/` | 完整失败案例（Case A-D 复盘） | 相关任务条件检索 |
| `success-cases/` | 成功设计经验——REFERENCE ONLY / NON-BINDING | 仅项目显式选择后 |
| `project-routes/` | 项目级固定生产路线 | 仅 PROJECT_ROUTE |
| `templates/` | 生产模板库（卡片式 / 动画纪录片式 v1 + 表达方式库）——每条路线须用户看片验收后才入册 | 项目选用时整册或单篇检索 |

准入纪律（§15）：任何一条成功经验不得因一次成功升格为全局规则。

近期案例：`success-cases/EXTERNAL-moyun-living-rice-paper-2026-10.md` 是外部作品考据；`success-cases/PROJECT-moyun-birthday-user-review-2026-10.md` 记录 103《岁添一枝春》两组 MP4 的用户审片（效果不错；逗号多余、下次可试琴音；本版不改）。两者均为条件性参考，**不是**全局默认注入，也不能据单次两臂对照宣称知识库有效。

2026-10-15 收录：Case C《一扇窗的处方》（H3 访谈式教学片）经验入 `known-pitfalls/`（KP-011~015：ffmpeg 裁剪构建、卡片/字幕同义碰撞、RH 计费与 API 陷阱、H3 人物生产纪律、PowerShell JSON BOM）。案例底稿在 `runs/envpsy-case3-interview/LESSONS_CASE_C.md`（runs/ 不入库，知识库为正式落点）。
