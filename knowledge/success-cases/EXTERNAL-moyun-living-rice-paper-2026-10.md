# 外部案例：墨韵 Moyun（Living rice-paper painting）

> 状态：EXTERNAL / candidate / REFERENCE ONLY / NON-BINDING。2026-10-09 整理；未由 103 复现，不得自动注入默认生产 prompt、不得升格为全局成功规则。

## 来源与证据层级

- 原作者作品及实现：[axtonliu/moyun](https://github.com/axtonliu/moyun)（[README](https://github.com/axtonliu/moyun/blob/main/README.md)、[在线交互页面](https://axtonliu.github.io/moyun/)）；[原帖/39 秒视频](https://x.com/AxtonLiu/status/2103288413969621231)；[作者复盘](https://www.axtonliu.ai/newsletters/ai-2/posts/opus-5-5-real-practice-reflection)。
- [Vidily 收录卡](https://vidily.ai/explore/opus-5-5) 标题为 Living rice-paper painting，标注 Procedural 2D / Code animation。其英语句子 “Make a rice-paper ink painting ... restrained camera movement” **是 Vidily adapted prompt，不是原始提示词**；不能当作作者的制作输入。
- [原提示词存档](https://jasonzhu.ai/zh/prompts/claude-opus-5-5/2103288413969621231) 收录作者的开放式 111 字中文指令：「你是 opus 5.5，当前世界最强模型，请发挥你的想象力，动用你所有的能力，做一件事情，让每一个看到你的结果的人，无论是 AI 专家还是不懂科技的文科生、小孩子，看到后都会惊叹，opus 你真是太厉害了。你会做什么事呢？」原文**没有**指定水墨/宣纸/WebGL。
- 本地原片证据：`video_perception/runs/breathing_ink/source.mp4`，取自上述提示词存档页面的 video.twimg.com 原视频 URL；SHA-256 `435f2839489e10e3e839428c45081ec0bd9c0cc3bf80b776a1bf0b6f4d6f0560`。下载仅供参考分析，不意味着取得二次发行授权。

## 作者源码 / README 可以支持的事实

作品是单文件 HTML 交互画布（不是逐帧由 Opus 视觉推理绘制，也没有调用 Runway 的证据）；运行时由 WebGL2 fragment shaders 在 GPU 上算不可压流体，RGBA 纹理保存墨/水/沉淀墨/朱砂，宣纸纤维和扩散为程序化生成；笔刷用高斯印章及飞白；古琴用 WebAudio 的 Karplus–Strong 合成；景观由带种子的生成器组织远山、皴染、松、水、船、飞鸟、朱砂日、题诗与印章。仓库另有 Playwright/CDP 屏幕录制脚本与 WebAudio 录制混流；**原帖视频是否由该脚本录制尚未核实**。这些是作者 README 和可查代码声明，不是视频抽帧能独立证明的算法。作者称单次会话、约 23 分钟生成并自行迭代 v1→v4，依赖作者陈述；不当作独立验证的性能指标。

## 对 103 的可检验启发（尚非经验结论）

1. 分清「Opus 写交互引擎」与「Opus 直接生成每帧」：视频是代码作品的一种**录屏呈现**，真正的资产可能是可交互作品。测 103 时先确认交付目标是网页交互还是最终 MP4。
2. 用 `CUSTOM`（WebGL2）或 `WEB_2D` 实施自由选择；这种连续墨流适于检验现有 renderer 菜单是否阻碍合理选择，不能因原作者选 WebGL 就预设被测模型也必须使用 WebGL。
3. 初次测试先取短、可核验的独立题目，不逐帧复刻原作者山水构图/题诗/印章；对照 OPEN 与可选 ASSISTED 参考案例，测视觉效果、时间一致性、可控性与成本。
4. 源视频的视觉观察与源码可证实的制作事实必须分层，实验失败教训待独立复现后再进入 `known-pitfalls/`。

## 禁止推断

- 不能将 Vidily 的 adapted prompt 当作者原话，不能宣称原作者使用 Runway、源视频录制方式已证实，不能因有源码就判定 103 已能复现。
- 此卡放入 `success-cases/` 是为了**可检索的外部标杆**，不是 103 的已验证成功案例；不创建默认水墨风格包、不改全局 Prompt。
