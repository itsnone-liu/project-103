# 知识库索引（ARCHITECTURE-v2 §9-§14）

五分类，生命周期 candidate→validated→project-proven→production→deprecated。**默认不进入上下文**，按生产模式条件性检索（OPEN 不加载 / ASSISTED 按需 / PROJECT_ROUTE 按配置）。

| 目录 | 内容 | 默认 |
|---|---|---|
| `hard-facts/` | 数学事实、API 文档、渲染环境、生产协议、语义标签表 | 可默认使用 |
| `known-pitfalls/` | 已实证 API 陷阱/环境坑——作用是**避坑**不是指挥设计 | 相关任务条件检索 |
| `failure-cases/` | 完整失败案例（Case A-D 复盘） | 相关任务条件检索 |
| `success-cases/` | 成功设计经验——REFERENCE ONLY / NON-BINDING | 仅项目显式选择后 |
| `project-routes/` | 项目级固定生产路线 | 仅 PROJECT_ROUTE |

准入纪律（§15）：任何一条成功经验不得因一次成功升格为全局规则。
