# 外部标杆：Opus 5.5 教学视频案例集（2026-09 传播波）

> **状态：EXTERNAL / REFERENCE ONLY / NON-BINDING**（冻结原则 P3：成功经验不得升格为全局规则）
> **用途**：Phase 5 真实题目验证的靶子与设计词汇来源；"系统该管什么/不该管什么"的反证材料
> **来源**：x.com 原帖，经 [zhuyansen/awesome-opus-5.5-video](https://github.com/zhuyansen/awesome-opus-5.5-video)（cases.json）与 [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) 收录；PDoom 全套设计文档来自 [JohnHeibel/PDoomVideo](https://github.com/JohnHeibel/PDoomVideo)。本地缓存 `cache/ref_*`（STORYBOARD.md / ANIMATION_GUIDE.md / cases.json / 两份 prompt 页）。

## 案例事实

| 案例 | 时长 | 工具栈（模型自选） | prompt 长度 |
|---|---|---|---|
| 《什么是 Transformer》（dotey，高中生向，直觉→数学） | 12:12 | Claude Code + **Remotion** + KaTeX + EdgeTTS | **117 字符** |
| Manim 导数概念课（LinearUncle，通俗+例子+引人思考） | 7:37 | **Manim** + edge-tts | **53 字符** |
| 高中地理·大气环流（akokoi1，线稿风，中英字幕+BGM） | 4:48 | 自选线稿引擎 + edge-tts（prompt 内含 API 接线说明） | 150 字符 |
| 研究论文→3B1B 风格（deedydas） | 8:39 | 未公开 | 未公开 |
| Jev/Laya 三集完整课程（每集 ~18 分钟） | ~54:00 | Manim + narration + 字幕/缩略图/章节/构建文件全自动 | 短 |
| PDoom 音乐片（JohnHeibel，非教学，看 Motion） | 2:37 | p5.brush 手绘引擎（与我们 styles/hand-drawn 同源家族） | 短 |

**Prompt 原文（逐字，证明"极短输入→完整教学片"）**：

- 导数课（53 字）：「请用Manim给我制作一个导数概念学习的视频，要求通俗易懂，并且有例子，引人思考。配音使用edge-tts」
- 大气环流（150 字）：「做一个动画，讲解高中地理知识点"大气环流"。风格轻松有趣，动画格式为线稿，添加合适的音乐，请务必做到引人入胜，字幕用中英双语，解说用TTS，如果 TTS 接口有关闭水印的参数就关掉，文档在TTS.md，API KEY 和音色分别是 .env 里的 APIKEY 和 VOICE，最终视频要能直接导出。」
- Transformer（117 字，原文未抓到，长度经案例库证实）：要求高中生可懂、含 attention 与数学解释。

## 跨案例可借鉴模式（审计词表级素材，非默认注入）

1. **极短 prompt → 模型自主补全教学设计**。53-150 字符产出 5-12 分钟完整教学片：分镜、例子选取、数学呈现、节奏全部模型自主决定。**直接验证 ARCHITECTURE-v2 主路径方向**——强模型不需要系统喂设计词汇；系统的职责是保正确、确定性、QA，不是教它设计。
2. **工具栈/后端自选是常态**。同为教学片：Transformer 选 Remotion+KaTeX，导数选 Manim，地理选线稿引擎。没有"一个 renderer 打天下"——印证 renderer 菜单+两步决策+CUSTOM 逃生舱的必要性。
3. **教学叙事公共型**（三案例共同）：直觉/现象先行 → 机制展开 → 数学形式化后置；每段一个核心类比；结尾回收（导数课"引人思考"=反思问题收尾）。可作为 storyboard 阶段的**自述词表**（与 REVEAL/TRACE/… 并列），不构成强制结构。
4. **PDoom 镜头词表**（STORYBOARD.md 全文在缓存）：每镜头"something happens"（无一帧静止说明）、sets-not-cards（场景内运镜，非卡片切换）、motivated transitions（动作带过切点）、emotion morphs（情绪不瞬切：squash-stretch+emote 过渡）、palette arc（全片色相弧线）、readability rule（一镜头一焦点动作+大剪影，镜头 1.4-5s）、text-light（图优先于字）。教学片不需要全盘照搬，但"每秒都有事件发生/一个焦点"两条与教学节奏直接通用。
5. **ANIMATION_GUIDE 印证我们五关契约**（同源引擎的 Opus 版指南原文）："Frames render in parallel and out of order. Every shot must be a pure function of t: no state that carries between frames, no Math.random. Use hash(i) for stable randomness." —— 与五关第 1 关逐字同义；其 `jit` 12 次/秒重播种=手绘 boil 技法（我们引擎同款）。
6. **帧成本预算显式化**："aim for ≤2.5s per frame and never more than about 4s…… Prefer fewer, bigger shapes"——帧耗时是设计约束。我们 QA 层可加渲染耗时统计（尚未实现）。
7. **多智能体文件所有权**："Only edit your own chapter file…… If you find a real bug in a shared file, report it; don't edit it."——章节化拆分+共享层冻结+上报制。对长片（>3 分钟）多 agent 并行生产的组织模式可直接借鉴。
8. **人审后置**（Jev 案例）：Opus 全自动产出 narration/动画/字幕/缩略图/章节/构建文件后，作者做的是**事实核查与修正**——审"对不对"，不重做"怎么讲"。与我们 OPEN 模式+数学审计+QA 的分工完全一致。
9. **手绘引擎家族的产能实证**：PDoom 用 p5.brush 家族（paint/inkLine/PAL/chapter/studio.html/render.mjs）完成 156.6s 完整音乐片——`styles/hand-drawn` 风格包保留价值的直接证据（风格包路线无产能天花板问题，问题只在"曾是默认"）。

## 对 103 v2 管线的映射

| 借鉴点 | 103 v2 对应 | 状态 |
|---|---|---|
| 短 prompt 自主设计 | storyboard prompt（只给内容约束，零设计词汇） | 已支持 |
| 后端自选 | 两步决策 + 菜单 + why-not + CUSTOM 否决门 | 已支持 |
| 教学叙事自述词表 | 语义标签表（production-contract.md）可扩一条"叙事自述" | 小改 |
| 镜头/节奏审计词表 | QA 层视觉多样性度量（Phase 5 指标） | Phase 5 |
| 纯函数逐帧 | 五关契约第 1 关 + web2d_capture 逐帧调用 | 已支持 |
| 帧成本预算 | 渲染耗时统计 | 未实现（建议 Phase 5 前加） |
| 章节化多 agent 生产 | 长片组织模式 | 未实现（>3min 片时启用） |
| 人审后置 | 数学审计 + QA + 用户验收门 | 已支持 |

## 禁止事项（对齐 §15）

- 本文件任何内容**不得进入默认 prompt**（`use_global_success_cases=false`）
- 不因"Opus 用 Remotion/Manim"就固化后端偏好；不把 PDoom 镜头词表做成必填结构
- 成片效果与标杆的差距，先归因模型能力差距（长输出稳定性、自验循环深度、迭代轮数），后归因系统——Phase 5 的测量目标正是这个归因的分界线
