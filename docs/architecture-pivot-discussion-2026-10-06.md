# 103 教学视频体系 · 架构复盘与转向讨论纪要

**日期**：2026-10-06
**性质**：讨论决议文档（未动任何代码，待用户裁决后执行）
**触发**：Case D 双模型几何测试（三角形内角和，撕角拼平角）验收发现双片视觉缺陷，引出体系级追问。

---

## 一、Case D 验收缺陷与根因定位

### 1.1 现象
- **Luna**：三角形从未出现，全片只有角扇（靛蓝像素探针 ≈ 0，全片实测）
- **GLM**：最后拼平角时有一个楔形没嵌进槽位（偏移约 45px）

### 1.2 根因（全部定位到行级，均有实证）

| 缺陷 | 根因 | 责任方 |
|---|---|---|
| Luna 三角形消失 | 引擎 `inkLine`（p5.brush spline）在**恰好 2 点 + curv>0** 时静默不画任何内容；curv=0 或 ≥3 点才画。Luna 所有边线/撕痕/基准线全是二点+curv0.2 调用 | **库缺守卫**（隔离探针 5 变体对照渲染证实） |
| Luna 绿楔 0 秒浮空 | 扇形 sweep 忘乘进度参数 + 两个 sweep=0 退化扇形画出径向线 | 模型代码 bug |
| Luna 尾段回顾板死区 | `narr()` 数组少 tEnd（n+1 约定），`N.at(6,f)` 外推 NaN | **管线喂给模型的数据就不含 tEnd**（文档要求 n+1，实际给了 n） |
| GLM 楔形错位 | `superposeCopy(pts, dx, dy, ...)` 的 dx/dy 是**位移增量**（Luna 用对：`O[0]-A[0]`），GLM 传成**绝对目标坐标** | **PATTERNS.md 未写明 delta 语义**（文档歧义第 3 例） |

### 1.3 失败模式四分类（本次讨论的核心证据）

| 类别 | 实例 | 责任方 |
|---|---|---|
| 契约精确处：**零失误** | narr 时钟、TTS 起点注入、数学参数块（两模型都 atan2 预计算，60/70/50 全对）、Luna 词表对齐 20/20 | ——体系正常工作 |
| API 语义歧义 | markAngle 点/弧度两义、ROLE 键名/颜色、superposeCopy 增量/绝对、narr 少 tEnd（两模型各中两个） | 我们的文档没写死 |
| 引擎尖刺 | inkLine 二点+curv 静默不画 | 库缺守卫 |
| 通用代码 bug | lt 模块层闭包、sweep 未门控 | 模型（与 pattern 体系无关） |

**结论：契约写得死的地方模型全部满分；翻车全部落在契约没写死的地方。**

---

## 二、手绘风格的考古：从哪一层开始锁死

```
引擎层（ClaudeAnimationBase）        ← 风格原生地
  全部绘画仪器都是毛笔：inkLine=刷子、paint=水彩(wash/bleed/tex)、
  boilSeed=线条沸腾、letters=手写体、PAL=水彩童书色。
  不存在任何"精确矢量"一等原语；平涂只能压参数归零（能力存在但非公民）。
        ↓
pattern 层（patterns.js ~30 原语）   ← ★ 选择权在这里塌缩
  每个教学原语的默认实现都选了 brush 味（markAngle='ink'笔刷、
  度数=手写letters、刻度=inkfine）。手绘从"可选"变成"API 语法本身"。
        ↓
提示词层（PATTERNS.md / MOTION_SKILL）← 只是补刀，把默认写成规范
        ↓
LLM 输出（全片手绘，无替代语法可用）
```

关键实证：**引擎的参数级逃生舱（平涂模式）从来存在，两模型从未使用**——默认值的引力连参数级选择都能吸死。

---

## 三、用户裁决：体系推倒

> "要彻底考虑前面的这些体系建设的推倒，最多只能用于特殊情况。这个体系现在是从根本上限制了 llm 的能力，哪怕换 opus 来也只会手绘。而手绘只是我所要的场景里偏少的一种。"

讨论确认的完整判断：
1. "换 Opus 也只会手绘"成立——提示词宇宙里只有一种语法，天花板是体系设的，不是模型能力设的
2. 我们在**用自己的小 API 换模型训练语料里的大 API**（Manim/SVG/Canvas 语料海量，我们的 pattern 库要靠自写文档现场教）
3. 本轮建设路径偏离了用户最早的方向备忘录（"capability-free Spike 测裸能力，而非继续扩细粒度 capability"）；Case D 的证据恰好实证了原始判断

### 3.1 保留 / 降级 / 废弃

**保留（渲染器无关的生产脊柱）**
- 音频时序倒置：TTS→timing→narration 物理时钟（两轮验证，任何后端通用）
- storyboard→codegen→render→audit→mux 链结构 + 数学审计 + 对齐 lint
- 逐帧确定性求值契约（状态只依赖 t、随机种子化——一句话提示词契约即可强制）
- 渲染/QA 管线（帧循环、'page error'检查、帧抽取、VLM 抽检、mux/loudnorm）

**降级（特殊风格包）**
- patterns.js + MOTION_SKILL + brush 引擎 → "手绘风格包"，只在明确要童书温度的内容上启用
- pattern **标签**留作评估词表（对齐 lint 的度量衡），不再是实现 API

**废弃**
- "ClaudeAnimationBase 是唯一 runtime"的提示词预设
- "教学片=手绘"的默认美学（语料铁律本来是"几何精确、注释手绘"）

---

## 四、视频生成底层技术版图（重查，2026-10-06 搜索）

### 4.1 四层分类

**L1 图形内核（画什么）**：Canvas 2D/WebGL/WebGPU（栅格立即模式）· SVG+flubber（矢量保留模式）· Three.js/Babylon.js/R3F（3D）· Manim CE/GL+JSXGraph（数学域引擎）· p5/Processing+brush 生态（创意编码，手绘包归此）

**L2 时间线编排（怎么动）**：Motion Canvas（TS 场景=逐帧确定性，专为讲解视频）· Remotion（React 组件=帧，生态最成熟）· GSAP（Webflow 收购后 100% 免费全插件）· Lottie/Rive/Theatre.js（按需选配）

**L3 合成编码**：FFmpeg 滤镜图（现有 mux/loudnorm）· Remotion compositor（在用）· Shotstack/Creatomate/JSON2Video（商业 JSON→片 API）

**L4 帧采集**：无头浏览器逐帧截图（现有 render.mjs 即此）· WebCodecs · Manim 自带（cairo→PNG 序列）

（边界外：扩散视频 Sora/Veo/Kling 是实拍感 B-roll 互补项，不是程序化渲染替代。）

**对照我们**：L3/L4 全部达标可复用；**唯一自造轮子的是 L2（pattern 库）——恰是生态里 Motion Canvas/Remotion 已解决得更好的层**。转向后 L2 换成熟轮子，L1 按决策菜单自选。

### 4.2 生态关键发现（"模型自选技术栈"已有成熟形态）

- Remotion 官方 AI 线：Prompt→Motion Graphics SaaS 模板（remotion.dev/docs/ai/ai-saas-template）+ template-prompt-to-video
- Manim-MCP（github.com/paulnegz/manim-mcp）：Text→Code→Video，CLI+agent 模式+MCP server，已迭代 multi-agent 流水线+RAG
- StemViz（github.com/ken2190/stemviz）：STEM 概念→Manim 有旁白教学片——**与我们场景完全同构的先例**
- Eduvideo（HF space）：教学管线带 render/motion-canvas 可换后端
- video-framework-selector skill（skillsmp.com）：专干"让 Claude 按内容自选视频框架"；另有 claude-creative-stack animation-composer 技能

**结论："Agent + 技能/工具菜单 + 渲染验证环"是正在成型的行业标准形态**；承载件是 Agent Skills / MCP（我们 harness 的 dsh-evolve 技能系统同构，地基已打）。

---

## 五、后端菜单设计

### 5.1 准入五关（生产契约，非工具枚举）

1. 逐帧确定性（状态只依赖 t，可复渲）2. 无头离线渲染 3. 程序化帧输出（1080p+ PNG 序列可进 mux）4. CJK 文字/公式 5. LLM 语料覆盖（决定修补率）

### 5.2 初始菜单（按内容类扩充至 ~9 项）

| 内容类 | 后端 |
|---|---|
| 几何/数学证明 | Manim、精确 SVG、TikZ/Asymptote（教辅印刷级） |
| 图表/数据教学 | Vega-Lite（声明式图形语法，LLM 写 JSON 比写动画稳）、D3/ECharts |
| 3D 立体几何 | Blender bpy（语料海量、确定性渲染）、Three.js |
| 物理/交互感 | Godot 电影模式（--write-movie 确定性捕获） |
| 叙事童趣 | 手绘风格包（原 brush 引擎+pattern 库） |
| 氛围 B-roll | GLSL shader 族 |

### 5.3 菜单的元问题（本次讨论最重要的机制设计）

**菜单本身会成为新的 pattern 库**——"我们定义选择空间"的错误不会因空间变大而消失，只是上移一层。

且**靠模型自发逃生不现实**：锚定引力（菜单项显著性加成，实证=参数级平涂逃生舱从未被使用）+ 顺从压力（逃生=对管线设计者说"我知道得更好"）+ 验证不对称（野生栈要自扛适配），三股力全往菜单里压。

### 5.4 逃生机制七条（把"逃"从勇气问题改成结构问题）

| 机制 | 内容 | 对冲 |
|---|---|---|
| 契约先行菜单垫后 | phase-1 先只见五关约束（约束语言非工具语言），先答"这类内容需要什么画法"再亮菜单 | 锚定 |
| 两步决策 | 步 A 无菜单自由作答，步 B 菜单匹配（先独立判断再看锚） | 锚定 |
| 强制逐项否决 | 决策 JSON 须给每个菜单项一行 why-not，禁止默认滑入 | 锚定 |
| 否决门自动化 | 逃生只需一句提名，系统自动环境探针+10 帧冒烟渲染 30 秒判决 | 顺从+验证不对称 |
| 反顺从明示 | 提示词明写"菜单外提名若更合适是正确行为"，few-shot 放成功逃生案例 | 顺从 |
| 逃生日志 | 提名+结局入库；败→沉淀坑文档，连赢→转正 | 防固化 |
| **菜单盲测采样** | 按比例抽任务 codegen 只给契约不给菜单，与菜单组对比结局——度量"菜单税"，让野生栈在系统级获得出场 | 总对冲 |

菜单进出数据驱动（修补率升/降级、归档、转正）——与 dsh-evolve 技能生命周期（load/success/error→archive/promote）同构。

---

## 六、强模型 vs 弱模型的流程差距与补偿

**差距不在"会不会选"，在四个流程能力**：

| # | Opus 优势 | GLM 表现 | 补偿（外部化机制） |
|---|---|---|---|
| 1 | 冷门框架语料覆盖广 | 只会主流路径 | 选型菜单+每后端"已知坑"薄文档 |
| 2 | 长输出指令保持（300 行不漂） | 后段漂移（narr 越界实例） | 结构化代码契约（先签名后填体）+ lint 闸门 |
| 3 | 自我验证自治 | 需外部回路 | 管线内建验证环（渲染→错误检查→帧抽取→VLM 抽检→定向修复）——已有八成且模型无关 |
| 4 | 决策元认知 | 理由模板化 | 决策结构化产物 JSON（backend+理由+备选+风险）+预检规则机器校验 |

**核心公式：把"信任模型内部能力"换成"菜单+验证环+结构化决策"后，GLM+好流程 ≈ Opus+裸流程**——Opus 的优势从必需品降级为省轮次。

---

## 七、GLM thinking 问题（必须解决，当前被 key 失效阻塞）

已实测事实：
- 故事板阶段（12k prompt）thinking 默认开：正常优秀（15.3k 推理→3,975 字符故事板）
- 代码阶段 21k prompt：3 次烧穿（65,450 推理/0 内容/finish=length）；`reasoning_effort` 与 `thinking.budget_tokens` 均未封顶（coding 端点不认 budget）
- 瘦身 14k + thinking 关：成功（2.9k 推理 + 8.2k 内容/91s/finish=stop）——**两变量同时改，slim+thinking 开的组合未测**
- A/B 实验（slim+thinking 开）已发起，被 401"令牌已过期"挡住（key 会话中途失效，未耗额度，需用户刷新 key）

**恢复后的执行序**：① slim+thinking 开（最可能正解，prompt 尺寸与烧穿强相关）→ ② 若仍烧穿：换通用端点 /api/paas/v4 + budget_tokens 硬封（通用端点文档明确支持）→ ③ 质量可用则定为生产配置。

---

## 八、裁决实验（验证"推倒"的数据背书，待批）

同一份故事板+timing，三个代码目标各跑：brush 风格包 vs Manim vs 自由 SVG/Canvas。
**度量修补次数+视觉验收+用户目检**——若裸目标显著优于 pattern 库路线，推倒有数据背书。即用户备忘录中两个 capability-free Spike 的延迟兑现+本次挣到的对照组。

## 九、待用户裁决事项

1. 本文档的保留/降级/废弃清单是否定稿为架构决议
2. 裁决实验（第八节）是否执行、何时执行
3. GLM key 刷新后 thinking 实验序（第七节）是否按序执行
4. 初始菜单 9 项名单是否认可/增删
5. Manim 后端的 spike 优先级（几何内容类最急用）
