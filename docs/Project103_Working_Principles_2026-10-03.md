# Project 103 工作原则与生产方法

**日期：2026-10-03**  
**性质：阶段性工作原则；用于指导正常生产，不构成全题型或全教材完备性证明。**  
**依据：** `Project103_LLM_Native_MathViz_LessonVideo_Phase_Conclusion_2026-10-03.md`、已确认的 G-001，以及海陆风、扩散与渗透、存货周转率等实验。

---

## 1. 项目总定位：两条相邻的 LLM-native 产品线

Project 103 不再以“为每一种题型建立完整 capability”作为唯一主线，而是维护两条相邻但生产目标不同的路线：

### A. Interactive MathViz

```text
数学题 + 可选教学意图
→ 强模型理解、参数化、交互设计、代码生成
→ 自包含 HTML + SVG + JavaScript
→ 浏览器运行
→ 薄验证
→ 最多一次集中 repair
→ 可探索交互页面
```

适合通过连续变化理解的二维几何、临界状态、极值、轨迹、条件松弛、充分必要关系等问题。

### B. LessonVideo

```text
教材 source
→ 教学预处理
→ Lesson Brief
→ Storyboard
→ 视觉形式选择
→ Remotion 总装配
→ TTS / 字幕
→ 薄审核
→ 最多一次集中 repair
→ MP4
```

目标不是把教材朗读成视频，而是把教材重构为可学习的教学经历。

两条路线共享 LLM-native、薄验证和最多一次 repair 的原则，但不能把交互页面的验收方法机械套到视频上，也不能把视频剪辑流程机械套到数学交互题上。

---

## 2. 总体生产哲学

### 2.1 强模型负责高层创作，系统负责稳定落地

强模型负责：

- 内容理解与数学/学科推理；
- 学习目标提炼；
- 信息取舍与重组；
- 教学结构和叙事顺序；
- 教学导演指令的解释；
- 视觉表达形式选择；
- SVG / Canvas / Manim / React / Remotion 代码生成；
- 对结果进行一次有边界的自我修复。

生产系统负责：

- 运行、渲染、编排与装配；
- 错误捕获和媒体探测；
- 数值、声明、时长和字幕等薄验证；
- 关键帧截图与视觉审查；
- 记录输入、输出、Token、TTS、渲染和 repair 账目。

系统不应为了替代强模型而重新建立一个覆盖所有学科的形式化编译器。

### 2.2 LLM 生成的是“程序和教学设计”，不是每一帧像素

视频模型的主要产物是 Lesson Brief、Storyboard、旁白、场景代码和样式代码。真实帧由 Remotion、Chromium、TTS 与 FFmpeg 生成。因此应优先优化：

- 教学结构；
- 程序可读性与可修复性；
- 时间轴和字幕稳定性；
- 薄验证覆盖；
- 可重复渲染。

不要把本地逐帧渲染时间误记为 LLM Token，也不要把视频帧数当成模型生成量。

### 2.3 不追求“所有内容都动画化”

视觉表现按知识性质选择，而不是按技术能力选择：

- 定义、原则、结论：`TEXT_CARD`；
- 公式与数值依赖：`FORMULA` / `FORMULA_BUILD`；
- 口径、概念差异：`TABLE` / `COMPARE`；
- 有身份的少量对象和关系：`SVG`；
- 大量逐帧粒子、流场和扩散：`Canvas`；
- 老师按时间顺序讲公式、极限、证明：`Manim`；
- 经营事件、物理过程和状态改变：`PROCESS` / 时间线；
- 章节方法论：`SUMMARY`。

核心原则：**该静则静，该动则动。** 动画只有在表达过程、因果、依赖、方向、连续变化或结构重构时才有教学价值。

---

## 3. LessonVideo 固定生产阶段

任何中等以上复杂度的教材视频，必须按以下顺序推进，不得跳过教学预处理直接边写代码边改：

```text
source.md
→ lesson-brief.md
→ storyboard.md
→ Remotion implementation
→ TTS
→ 字幕
→ 首次完整 MP4
→ review
→ 最多一次集中 repair
→ final.mp4
```

### 3.1 `source.md`：锁定事实源

- 原文或用户提供材料必须先保存；
- OCR 数学符号、单位和标点要在 source 中明确规范化；
- 不把模型推测写成教材原文；
- 将生产约束、目标学生和目标时长一并记录。

### 3.2 `lesson-brief.md`：固定的教学加工层

Lesson Brief 不是摘要，而是教师式重构。至少应包括：

1. `Core Learning Objective`：学生看完后最重要的可观察能力；
2. `Must Teach`：不可删除的概念、计算、边界和误区；
3. `Secondary`：可压缩的信息；
4. `Can Omit / Compress`：明确删除什么以及为什么；
5. `Misconception Risks`：学生可能形成的错误理解及画面/旁白防护；
6. 教学主线与内容重组；
7. 视觉分工：哪些静态、哪些图示、哪些过程动画。

判断标准不是“覆盖了多少原文”，而是“学生是否获得了目标能力”。

### 3.3 `storyboard.md`：先决定教什么，再决定怎么画

每个 scene 必须说明：

- 教学目的；
- 时长；
- 旁白承担什么；
- 屏幕文字承担什么；
- 视觉形式；
- 是否需要动画；
- 选择该表现形式的理由。

旁白不能只是屏幕文字的重复朗读。应明确动画、字幕、公式和旁白之间的分工。

### 3.4 实现、TTS 和字幕

- 先完成首次完整实现，再集中渲染；
- 中文旁白优先使用自然口语，不逐句抄教材；
- 公式主要由屏幕呈现，旁白解释含义和原因；
- 字幕服务于听觉确认和无障碍，不应成为第二块教材正文；
- TTS 时长必须反向检查时间轴，不能只按预估字数排 scene。

### 3.5 首次版本与唯一 repair

首次 MP4 必须完整渲染后再审查，不能无限边写边修。`review.md` 应先记录问题，再集中执行一次 repair。

repair 优先级：

1. 学科事实、公式、数值和方向错误；
2. 教学主线与误区防护；
3. 内容取舍和案例因果；
4. 场景选择与节奏；
5. 视觉美化。

repair 使用次数必须记录在 `usage.json`，正常生产最多 1 次。

---

## 4. 学科正确性与薄审核

薄验证不是放弃正确性，而是把验证集中在高价值、跨题型、可自动化的风险上。

### 4.1 通用运行与媒体检查

- TypeScript / 构建检查；
- HTML、React、SVG 能否运行；
- console error、runtime exception；
- 音视频是否存在、时长是否匹配；
- 分辨率、帧率、编码和文件完整性；
- 外链、字体和资源是否破坏自包含与离线稳定性。

### 4.2 教材与学科检查

- 公式符号、单位和数值独立复算；
- source-claim 与旁白/屏幕声明一致；
- OCR 错误不能进入最终成片；
- 不把“相关”讲成“因果”，不把“可能”讲成“一定”；
- 口径、适用条件和反例必须保留；
- 对数学交互题检查边界、临界点、极值、NaN/Infinity 与参数扫描。

### 4.3 教学检查

- 是否过早泄露应让学生观察或猜想的结论；
- 是否把观察、猜想、验证和结论混成一句；
- 交互变量是否真的对应数学变量；
- 动画是否增加理解，而不是只增加装饰；
- 公式、案例和结论是否有足够停留时间；
- 字幕是否过密、是否遮挡关键视觉区域。

### 4.4 视觉检查

使用关键帧截图，至少覆盖：开场、每个公式/核心场景、关键转折、总结。检查：

- 裁切、遮挡、重叠；
- 标签、单位、页码和控件可读性；
- 方向、箭头和状态是否容易误读；
- 颜色和层级是否把重点放在教学信息上；
- 关键结构是否在静帧中仍可理解。

外部视觉模型的意见只作为线索；涉及公式、箭头方向和学科事实时，以 source、代码、数值和多帧状态为准。

---

## 5. 工具与模型分工

### 5.1 Sol 与辅助模型

当前证据支持：

```text
Sol = 主创 / 导演 / difficult-case solver
Luna 或较便宜模型 = 辅助制作
```

主创任务包括教材重构、教学判断、复杂数学理解、视觉形式选择和整体 Remotion 设计。辅助模型可以承担：

- 字幕切分；
- TTS 文本清洗；
- metadata；
- 格式整理；
- 已冻结方案下的机械代码；
- 批量检查和媒体探测。

在没有新证据前，不应假设辅助模型可以替代主创模型完成整条 LessonVideo 链。

### 5.2 Remotion 的定位

Remotion 是 LessonVideo 的总导演/总装配层，而不仅是剪辑器。它统一：

- React / SVG / CSS / Canvas 场景；
- Manim 片段、图片和已有视频素材；
- 时间轴、字幕、音频和转场；
- 逐帧渲染与 MP4 输出。

复杂视频应采用“多个合适表达器 + Remotion 统一装配”，而不是强迫一个渲染技术覆盖所有内容。

### 5.3 旧 capability 系统的定位

既有 Geometry DSL、Function2D、SymPy、`stateAt(t)`、Runtime、SVG helper、deterministic solver 和测试设施保留为：

- `optional helper`；
- `optional verifier`；
- `optional fallback`。

除非新证据表明某类任务必须依赖它们，否则不作为所有题目的强制前置路径，也不为追求覆盖率继续无边界扩展题型 capability。

---

## 6. 长教材与批量生产方法

对于 8–15 分钟甚至更长的章节，不应一次生成完整视频。采用：

```text
chapter
→ lesson architecture
→ segments
→ segment source / brief / storyboard
→ segment production
→ segment review
→ final assembly
```

切片原则：

- 每段有一个可验证的核心学习目标；
- 段间保留概念依赖关系；
- 公式、案例和结论不要在切片边界被截断；
- 先冻结章节架构，再分别制作 segment；
- 最终由 Remotion 统一音频、字幕、片头片尾和章节过渡。

当 Lesson Brief 和 Storyboard 已经冻结后，可以测试把具体实现交给较便宜模型；但必须通过同一套薄审核和一次 repair 门槛。

---

## 7. Token、成本与可审计性

每个 spike 必须维护 `usage.json`：

- 优先记录供应商返回的 `input_tokens`、`output_tokens`、`total_tokens`；
- 若供应商未提供精确值，保留 exact 字段为 `null`；
- 记录 UTF-8/Unicode 字符数，并明确这是替代指标，不冒充 Token；
- 记录 TTS 引擎、声音、字符数、音频时长和成本；
- 记录渲染帧数、媒体时长、输出大小和 repair 次数；
- 本地读写、浏览器运行、Remotion、Chromium、FFmpeg 和 TTS 不计入 LLM Token；
- 不因“需要统计”而编造供应商用量。

这使模型创作成本和本地生产成本分离，后续才能比较 Sol 主创、辅助模型和批量生产的真实经济性。

---

## 8. 当前决策与边界

当前正式原则：

```text
Interactive MathViz: LLM-native SVG/HTML PRIMARY
LessonVideo: LLM-native 教材预处理 + 多形式表达 + Remotion PRIMARY
教材预处理: 固定阶段
预定义 capability: 非主路径
验证: 薄验证
repair: 最多一次
Sol: PRIMARY CREATIVE MODEL
Luna: AUXILIARY MODEL，暂不足以作为主创
```

这些原则是基于目前实验的阶段性结论，不是以下强断言：

- 不是所有数学题都适合 LLM-native SVG；
- 不是所有教材都能一次生成高质量视频；
- 不是模型永远不会出现学科错误；
- 不是薄验证可以替代学科专家验收；
- 不是一次 repair 能解决所有生产问题；
- 不是当前工具选择永远固定。

新实验应报告成功边界、失败类型、修复成本和适用条件，以便逐步修订本原则，而不是只记录成功案例。

---

## 9. 每次新实验的最小交付清单

### Interactive MathViz

- `source` / prompt 与教学意图；
- 自包含 HTML/SVG/JS；
- 运行检查与 console 日志；
- 参数扫描、边界/临界 spot check；
- 关键帧截图；
- repair 记录；
- 最终交互页面与结果说明。

### LessonVideo

- `source.md`；
- `lesson-brief.md`；
- `storyboard.md`；
- `attempt-1/`；
- `final/`；
- `review.md`；
- `usage.json`；
- `final.mp4`；
- `representative.png`；
- 财务/数学/学科数值核验与媒体 probe 结果。

实验不只要交付成品，还要留下“为什么这样教、为什么这样画、哪些内容被删掉、验证发现了什么”的证据链。
