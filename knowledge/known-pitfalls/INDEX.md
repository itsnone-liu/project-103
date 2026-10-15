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

# KP-004 · GLM coding 端点 thinking 烧穿 → 已终解：顶层 `reasoning_effort` 分档

- **栈**：LLM 调用层（glm-5.3, open.bigmodel.cn/api/coding/paas/v4）
- **症状**：代码生成任务推理烧满上限、内容 0、finish=length——271 token slim prompt 也烧（与 prompt 大小无关）
- **根因与终解（2026-10-06 二轮实验+官方文档定稿）**：烧穿是 **max 档**对代码任务的行为；Coding Plan 支持**顶层** `reasoning_effort` 字段（不是 `thinking.type`，也不是 `thinking.budget_tokens`——两者在 coding 端点无效/被忽略，第一轮实验被嵌套形状误导）。档位映射：`none/minimal/low`→low、`medium/high`→high、`xhigh/max`→max
- **已验证**：`reasoning_effort:'low'` + 真实 codegen prompt → 341 推理 + 5,073 内容，52s，finish=stop 自然收敛✓；slim 空泛 prompt 下 low 档也花 14k 推理后照常出内容✓；`high` 档照烧✗；glm-5.2+`none` 文档说放弃思考但实测仍烧✗（文档与实现不符，勿用）
- **管线配置**（pipeline/llm.py GLM_THINK 策略）：storyboard/decide=默认 max 档（分镜实测 22k tok 优秀）；codegen/repair=`low`（think='low'）
- **教训**：参数无效 ≠ 该端点不支持此能力——先查官方文档的参数**位置**（顶层 vs 嵌套）再下结论
- **来源**：Case D 三次烧穿 + 2026-10-06 capital2 五组对照实验 + [官方 thinking 文档](https://docs.bigmodel.cn/cn/guide/capabilities/thinking)

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

# KP-009 · 概念错位不能用执行迭代补偿：先过概念闸，再进生产线

- **栈**：全流程（创意→生产）
- **症状**：capital2 v2 被用户否决（«数学感不是三行字一次出现的意思…这一段内容不适合这个数学感»），但同一版本的 VLM 执行评审是 9/10——**执行分数与用户满意完全脱钩**。两轮视觉迭代把执行磨得更好，方向却越磨越偏
- **机理**：视觉迭代环（渲染→VLM 评审→修复）只能优化"概念给定的执行"，无法发现"概念本身选错"。评审者（VLM）默认按帧质量打分，不质疑选题
- **规避**：概念方向（视觉隐喻、数字呈现方式、章-概念映射）必须在写码/渲染前单独定稿并让用户确认；capital3 用 DESIGN.md 概念先行 + 用户认可的"钱是角色、环是舞台、数字从画面量出来"方向，一次通过
- **判别法**：用户否决语里出现"不是…的意思 / 不适合…"（定义级措辞）= 概念错位，停止迭代先重谈概念；出现"太暗/太快/看不清"（参数级措辞）= 执行问题，进迭代环
- **来源**：capital2 拒收 → capital3 重设计（2026-10-06），capital3 被认定为系列最佳

# KP-010 · GLM thinking 烧穿是任务形态依赖：max 档在 agent 小步形态下健康

- **栈**：LLM 调用层（KP-004 的后续定稿）
- **发现**：烧穿（推理烧满/内容 0）只发生在"整文件单发 codegen"任务形态；同模型同 max 档在分镜、决策、对话、**会话内 agent 分步写码**形态下全部健康
- **生产解**：capital3 全片（4 个 JS、11 章、两轮视觉迭代）由会话内 agent（glm-5.3 max 档）分步亲自完成——**GLM API codegen 调用次数为零、零烧穿**；管线里的 API codegen（think='low'）降级为无会话时的后备
- **副产物**：会话内 agent 写码自带全项目记忆（用户否决理由、历轮 VLM 评审教训、风格纪律），冷启动 API 调用塞不下这些上下文——质量与稳定双收益
- **来源**：capital3 全程实证（2026-10-06，提交 a133525）

# KP-011 · ffmpeg 报"滤镜语法错误"先查构建能力：Remotion 自带的是裁剪版

- **栈**：合成/调色层（pad/eq/subtitles/libass 全链路）
- **症状**：`pad=1280:720:...` 连续报 `No option name near '...'` / `Filter not found`；按滤镜语法三次返工全失败
- **机理**：Remotion compositor 自带 ffmpeg（`node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe`，n7.1）是 `--disable-filters` 构建，只有 scale/format——报错文案像语法错，实为滤镜根本不存在
- **规避**：遇到滤镜报错先 `ffmpeg -filters` 验证构建能力再改语法。本机全功能版：`D:\ComfyUI_windows_portable\...\tonyhub\ffmpeg\bin\ffmpeg.exe`（pad/eq/noise/subtitles/libass 齐）；ffprobe 用 Remotion 目录的即可
- **来源**：Case C 渲染，2026-10-15

# KP-012 · Canvas 卡片与字幕禁止同义叠加；QA 必须多时间点抽帧

- **栈**：合成层 + VLM 审片
- **症状**：证据卡段落底部悬浮一行以"："开头、末尾截断的重复结论（"：树景组住院更短…不能证明窗景"），看起来像卡片排版错误
- **机理**：build_timeline 给卡片场景叠加了 43 字长字幕，内容与卡内要点同义；字幕区超出画面底被裁，残行视觉上污染卡片页脚——两层互不知情
- **规避**：①卡片已呈现的信息一律不再叠加同义字幕，字幕只放卡上没有的内容（如来源引文），长度 ≤25 字；②QA 不能单帧放行——本例首帧审过 PASS，六时间点抽帧（30/35/38/42/46/48s）才暴露
- **来源**：Case C 三轮重渲实证，2026-10-15

# KP-013 · RunningHub API 陷阱集：计费口径 / 804 语义 / 任务可挽回

- **栈**：RunningHub WebAPI（820/821/103 共用）
- **计费口径**：task_outputs 返回的每个输出行（mp4+zip 伴随文件）都带 consumeCoins——**按 taskId 去重取一次**，直接求和翻倍。账户 remainCoins 余额 ≠ 项目成本（可能含无关任务），台账以任务级输出元数据为准
- **804 语义**：task_outputs 在任务运行中返回 `[804] APIKEY_TASK_IS_RUNNING`——先 poll task_status 到 SUCCESS 再取 outputs
- **任务可挽回**：脚本在任务创建**之后**崩（如记账 KeyError）不会杀 RH 任务——手动 poll status/outputs 恢复，勿重建任务重复扣币
- **来源**：Case C（213/400 币全链路核算 + P01_A 崩溃挽回），2026-10-15

# KP-014 · H3 人物视频生产纪律：参考图、身份门、音轨替换

- **栈**：MiniMaxH3 Ref2VA + 文生图参考 + CosyVoice
- **参考图生成**：带图/复杂负向的提示词会跑偏（老年脸、无关 UI 截图）；**纯文字提示词**一次出合格中年华人候选（Case C 15 币 2 张可用）
- **身份锚定**：选定候选锁为 canonical（记 SHA256），全部镜头共用单参考图；SFace 相似度抽帧验证（Case C 0.8268/0.8925，同人阈 0.363，镜头门中位 ≥0.60）
- **音轨纪律**：H3 生成音轨一律弃用；旁白/台词全部 CosyVoice 重配（角色台词标注"虚构情景台词"）
- **已知偏差**：VLM 对生成帧的年龄判断偏老约 5-10 岁 vs 用户指定年龄——按身份一致性放行前，若用户对年龄敏感需提前说明或预留 ReActor 修复预算
- **来源**：Case C 全程，2026-10-15

# KP-015 · PowerShell ConvertTo-Json 写文件带 UTF-16 BOM

- **栈**：工具链（Windows 环境 JSON 台账）
- **症状**：`ConvertTo-Json | Out-File` 写的 usage.json 后续 `python -m json.tool` 报 `Unexpected UTF-8 BOM`（UTF-16 编码+BOM）
- **规避**：JSON 台账统一用 python `json.dumps(..., ensure_ascii=False)` + `encoding='utf-8'` 写；读取方用 `utf-8-sig` 兜底
- **来源**：Case C 成本台账事故，2026-10-15

