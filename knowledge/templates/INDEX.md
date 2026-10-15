# 生产模板库（Production Template Library）

建立日期：2026-10-14 ｜ 依据：用户对 Times Square 动画式全片的验收定调（"突破性成果……可以记录成一个模板，供以后的课件视频学习采纳"）

## 定位

模板 = **视觉制作路线**（画面语法 + 管线配置 + 验收纪律），与 `docs/envpsy-video-type-taxonomy-v1.md` 的内容类型（T1-T5）是两个正交轴：任一内容类型可任选制作模板。准入纪律沿用 ARCHITECTURE-v2 §15：模板只登记**经用户看片验收**的路线，一次成功不升格为全局默认；每次使用按内容重新裁剪，不是机械套用。

## 现有模板

| 模板 | 状态 | 代表作 | 文档 |
|---|---|---|---|
| 卡片式（card-lecture） | v1 正式成文，生产可用（多支章节片） | `runs/envpsy-t2-94/` 等 | [card-lecture-v1.md](card-lecture-v1.md) |
| 动画纪录片式（animation-documentary） | **v2 已产出待验收**（v1 用户已验收 2026-10-14；v2=口语化旁白+中段一句一世界，16 帧 VLM 实证） | v1=`runs/envpsy-case1-full/`（601.18s）；v2=`runs/envpsy-case1-v2/`（661.29s） | [animation-documentary-v1.md](animation-documentary-v1.md) |
| 表达方式库（跨模板素材） | v0.1 采样分析中（已含《大同》《城市梦》分析卡+新语法短样片验证） | — | [expression-bank-urban-doc-v0.md](expression-bank-urban-doc-v0.md) |

## 预留扩展位（用户点名方向）

- **数学式**：公式推导/几何动画为主语言（可借鉴 project/926 MathViz 经验）
- **真人式**：真人出镜/实拍+后期注解
- 后续每加一个模板 = 一个新 md 文档 + 一次用户验收记录，不空占位。
