# reason.md — 推理层提示词纪律（v0.2）

输入：observation.json（事实层）+ 关键帧/sheet。GLM 5.3（或会话内 agent）负责解释与归纳。

## 第一问（每次必须先答）
«不要告诉我这个视频在讲什么内容。我要分析：这个知识/效果是如何通过画面被表达的。»

## 分析维度
- **Composition**：视觉中心、hierarchy 变化、前景/背景分层、negative space
- **Motion**：运动的语义作用（变化/比较/因果）；运动分类（此时才允许 overshoot 等词，
  每个分类主张必须引用观察层 ≥2 个证据时间戳；性质类主张需 ≥4 帧补帧证据）
- **Camera**：zoom/reframe 是否随语义重点改变
- **Transition**：装饰性 vs 保持对象/概念连续性
- **Teaching**：viewer_read（这一段观众被要求理解什么）、prerequisite、new_information、
  visual_encoding、why_motion_needed、cognitive_load、hold_time_sufficient
- **去运动判别**：«把 motion 去掉，这一段表达是否仍成立？» 成立→motion 主要是美学；
  不成立→motion 是语义组成部分

## 实现逆向层（第三层，前两层完成后才做）
输出 implementation hypothesis，明确«不判断原作者真正用了什么，只判断重建需要什么»：
- likely_primitives（对齐 103 已有词汇：inkLine/writeText/canvas transform/...）
- recommended_backend（web_2d / manim / ae / i2v / 混合）
- possible_implementation（layout/timeline/formula 的候选栈）
- 哪些部分容易失败（复现风险点）
- confidence + 理由

## 证据等级
CONFIRMED（跨通道一致）/ LIKELY（单通道+多帧）/ UNCERTAIN（冲突或单帧）——不强迫结论。
