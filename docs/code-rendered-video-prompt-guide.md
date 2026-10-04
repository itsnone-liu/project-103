# 代码渲染视频 · 提示词细化指南（调研 2026-10-04）

> 来源：joeseesun/opus-video-prompts（18 份完整提示词/54 案例，本地缓存
> cache/opus-video-prompts-README.md）+ waytoagi/apiyi 指南 + X 原帖。
> 适用：103 类课程/科普视频的"概念演示段"。

## 一、提示词四级光谱（按细化程度）

### L1 一句话（模型全自由）
- "make a modern slick and punchy video for a modern startup that works on inference"（Deedy，1分钟/$2）
- "做一个动画，快速回顾中华五千年的历史。风格轻松有趣，动画格式为线稿，添加合适的音乐，请务必做到引人入胜"（WY）
- 适用：探索/测试。赌模型审美。

### L2 角色+结构模板（填空即用）
Alex Prompter 30 秒企业讲解片：
```
Adopt the role of an expert motion designer. Build a 30-second animated
explainer for my business as a single HTML page. 5 scenes. The customer's
problem, what I do, how it works in 3 steps, one proof point, and my name
at the end. Bold text, smooth transitions, my brand colours.
My business [描述产品/受众/品牌色]
```
关键：**角色（专家动效师）+ 载体（单HTML）+ 时长 + 场景数 + 每场内容清单**。

### L3 知识点讲解+接线（103 直接原型，WY 大气环流式）
```
做一个动画，讲解[知识点]。风格轻松有趣，动画格式为线稿，添加合适的音乐，
请务必做到引人入胜，字幕用中英双语，解说用TTS，如果TTS接口有关闭水印的
参数就关掉，文档在TTS.md，API KEY和音色分别是.env里的APIKEY和VOICE，
最终视频要能直接导出。
```
配套：TTS 文档(TTS.md) + .env + .claude/settings.json 加 `"deny":["Read(./.env)"]`。
实测 26 分钟出近 5 分钟片，token 消耗低；同一提示词换知识点即可复用。

### L4 六段式专业模板（zero，最成熟结构）
`<inputs>` `<direction>` `<structure>` `<build>` `<gotchas>` `<start>`：
- inputs：**让模型先反问你要什么**（UI states/音乐 BPM/真实素材）
- direction：艺术方向一句话 + **Banned 清单**（粒子爆炸/RGB分离/光晕/霓虹/弹跳缓动=模板味来源）
- structure：**节拍表**——120BPM 每拍有事，逐小节写内容
- build：工程约束——`seek(t)` 纯时间函数、无 CSS transition/计时器/跨帧状态、
  numpy 分析音乐节拍网格、Playwright 子帧渲染 + ffmpeg tmix 动态模糊、
  **正式渲染前先渲每拍一帧抽查**
- gotchas：已知坑（will-change 模糊、文字进出时序、循环首尾帧一致）
- start：**先给节拍表/分镜，确认后再写代码**

## 二、写法经验七条（54 案例共性）

1. **先分镜后代码**：高质量案例全部要求先交分镜/节拍表，确认再写码 → 后续可单镜修改
2. **像导演一样给结构**：总时长/场景数/每场讲什么；镜头语言词汇（dramatic cuts、
   match cut、kinetic typography、orbiting camera）比形容词有效
3. **参考图/参考视频 > 形容词**（奥斯特里茨给战争油画："要它们的氛围不是它们的形式"）
4. **禁用清单反模板味**：负面约束比正面描述更决定观感档次
5. **确定性渲染**：每帧只由时间 t 决定，否则并行渲染会闪（PDoomVideo ANIMATION_GUIDE）
6. **自看片自返工**：渲染前抽查关键帧截图，修重叠/拥挤/看不清
7. **迭代一次一条意见**："慢一点""更有活力""加一个讲价格的场景"——不整篇重写

另：effort 开 high/xhigh；TTS/音乐 API 文档放项目目录、key 放 .env；
对话内直接播→录屏也是合法交付路径（Alex 模板）。

## 三、口播改造模板（103 已有成片的升级路径，Axton）
```
把 [成片.mp4] 做成一条新的竖屏短片：
1. 人像缩小成右下角圆形画中画，能看清讲话，不遮字幕。
2. 主画面换成动画B-roll，跟着讲的内容走：讲到哪个概念，画面就画哪个概念。
   风格轻松有趣，线稿动画就可以，不要写实。
3. 原声、原字幕、时长都不变。
```
实测 28 分 53 秒、约 30 个镜头、零人工介入。

## 四、局限与成本
- 产物是代码不是视频：本地要 Node/Chrome/FFmpeg（无头浏览器截帧→ffmpeg 合成）
- 强项=动态图形/线稿水墨/科普讲解/产品片；弱项=写实真人（写实仍需视频模型，Opus 只做编排）
- 成本谱系：一句话短片 $2 → 26 分钟 $低 token → MV 类 $200/单次或 Max 周额 7-10%
- "一次成型"多数实跑 2+ 轮，预算按迭代估

## 五、技术路线速查（9 条）
单HTML+Canvas逐帧 / p5.js+笔刷(手绘感) / Remotion(React) / HyperFrames /
Manim(数学) / Python逐像素线稿(WY系) / Three.js 三维 / 操控AE/Blender/视频模型 /
纯剪辑素材。103 概念段推荐：L3 知识点模板 + Python/单HTML 路线起步。
