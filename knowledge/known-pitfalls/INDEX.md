# KP-001 · web canvas：两点样条 + 曲率>0 会静默不画

- **栈**：WEB_2D（p5.js/brush 类样条描线 API 通用风险）
- **症状**：`spline(points, curvature)` 在 points.length===2 且 curvature>0 时不画任何内容、不报错——整段元素无声消失（Case D：Luna 三角形全片不可见，靛蓝像素探针=0）
- **机理**：样条需要 ≥3 个控制点；二点+正曲率走了空分支。curvature=0 时降级为直线段正常
- **规避**：二点线段一律 curvature=0；或在描线库内加守卫（两点+curv>0 → 自动降级直线）
- **验证法**：渲染后像素探针（目标色计数），不能只看渲染 exit 0
- **来源**：Case D Luna 诊断，2026-10-06，隔离探针 5 变体对照实证

# KP-002 · 旁白时钟数组必须 n+1 项（句起点 + 终点 tEnd）

- **栈**：全后端（时序契约）
- **症状**：只给 n 个句起点时，最后一句的插值 `at(n-1, f)` 外推出 NaN，尾段全部元素永不绘制/报 NaN——视频尾部整段空白
- **机理**：`at(k,f) = starts[k] + (starts[k+1]-starts[k])*f`，starts[n] 不存在 → NaN；NaN 参与比较恒 false
- **规避**：管线喂给模型的 always 是 `[s0..s(n-1), total]`；模型侧数组长度=句数+1
- **来源**：Case D 双模型同坑（GLM 还叠了 at(8,*) 越界分区）；管线与文档同责

# KP-003 · QA 必须双通道查错：exit code AND 运行时错误串

- **栈**：QA 层（BAC 归一化错误通道的动因）
- **症状**：浏览器页面异常（'page error'）时 node 进程可以 exit 0——只查返回码会漏判；反之渲染崩溃走未捕获异常时 exit≠0 但无 'page error' 字样
- **规避**：渲染判定 = 返回码 ≠ 0 **或** 归一化错误通道非空，两者任一即失败
- **来源**：Case C/D 渲染判定反复打补丁的总结

# KP-004 · GLM coding 端点 thinking 烧穿：瘦身+关 thinking 或通用端点 budget

- **栈**：LLM 调用层（glm-5.3, open.bigmodel.cn/api/coding/paas/v4）
- **症状**：大 prompt（~21k token）代码生成任务中推理烧满 65536 token、内容 0、finish=length；`reasoning_effort` 与 `thinking.budget_tokens` 均无效（coding 端点不认 budget）
- **已验证缓解**：瘦身 prompt 到 ~14k + `thinking:{type:'disabled'}` → 8.2k 内容/91s 成功。**注意 thinking 关闭损质量**——slim+thinking 开的组合是首选实验（未测完，被 key 失效中断）；备选换通用端点 /api/paas/v4 + budget_tokens 硬封
- **边界**：故事板阶段（12k prompt）默认 thinking 工作正常（15.3k 推理→优秀输出）——烧穿与任务形态+prompt 尺寸强相关，不是 thinking 本身不可用
- **来源**：Case D GLM phase-2 三次烧穿实证，2026-10-06

# KP-005 · GLM/Luna 长输出后段漂移：用结构化契约+lint 闸门兜底

- **栈**：codegen 层（弱长输出模型通用）
- **症状**：GLM 在 240+ 行场景代码后半段出现越界索引（at(8,*) 超出 narr 范围）——前半段结构精确
- **规避**：先签名后填体的分节契约；生成后 lint（词表对齐、narr 范围、越界引用模式）；QA 环自动定向修复提示，不靠模型自检
- **来源**：Case D GLM narr 越界诊断

# KP-006 · Manim 中文文本必须指定 CJK 字体

- **栈**：MANIM 后端
- **内容**：ManimCE `Text()` 默认字体无 CJK 字形，中文渲染为方块/空白。Windows 环境用 `Text("中文", font="Microsoft YaHei")`；`MathTex` 走 LaTeX 需 xelatex+ctex（重依赖，教学片优先 Text+unicode 公式符号）
- **状态**：candidate（环境经验，未在本机实证——manim 安装后验证）

# KP-007 · studio.html 场景标签替换必须通配，字面 replace 是静默 NO-OP

- **栈**：WEB_2D / hand-drawn 宿主
- **内容**：复用旧 runtime 时场景 `<script src>` 标签残留旧文件名，`html.replace('src/scenes/demo.js', ...)` 匹配不到 → 静默渲染旧场景。必须 `re.sub(r'src/scenes/[\w.-]+\.js', new, html, count=1)`
- **泛化**：一切"模板+替换"注入点都要断言替换真的发生了（count>0）
- **来源**：Case D 事故（继承 chase_meet.js 标签，渲染了默认帧）

# KP-008 · 无头渲染帧循环的输出目录必须先清空

- **栈**：WEB_2D 帧循环
- **内容**：断点续渲/重渲时旧帧残留会与新帧混编（帧号连续性假象）；渲染前清空 out/frames 或按帧号断言连续
- **来源**：render.mjs --frames 恢复机制的经验面
