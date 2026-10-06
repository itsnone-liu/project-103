# Manim 0.21 API 事实卡（codegen 注入用——GLM/Luna 高频幻觉点，2026-10-06 capital2 实证）

构造器签名（**严格按此写，不要发明参数**）：

- `Arc(radius, start_angle, angle, ...)` —— 弧长参数是 **angle**，没有 `end_angle`（幻觉高发）
- `Circle(radius=...)`、`Square(side_length=...)`、`Rectangle(width, height)`
- `Line(start, end)`、`Brace(obj, direction)`、`Arrow(start, end)`
- `Text("中文", font="Microsoft YaHei", font_size=...)` —— 中文必须给 font
- `MathTex(...)` 需要 LaTeX 工具链，**本环境未装**；数学式用 Text + unicode（÷ × ½ ≈ °）或 `MathTex` 禁用
- `DecimalNumber(0, num_decimal_places=...)` 数字变化配合 `ChangingDecimal` 或 `add_updater`
- `Axes(x_range=[a, b, step], y_range=[...], axis_config={...})`；`axes.plot(lambda x: ..., x_range)`
- `ValueTracker(v)` + `always_redraw(lambda: ...)` —— 参数化连续动画的标准式
- `VGroup(*objs).arrange(direction=RIGHT, buff=0.5)`

动画/时间：

- `self.play(Create(m), run_time=2, rate_func=smooth)`；`self.wait(1)` 单位是秒
- `Transform(a, b)` 保留原对象句柄；连续变换用 `ReplacementTransform` 或 `FadeTransform`
- 旋转/缩放锚点参数是 **about_point=**（没有 `about_point_axis`，幻觉高发，capital2 实证）
- `m.animate.shift(RIGHT * 2).set_color(RED)` 链式
- `Indicate / Flash / Circumscribe / FocusOn` 强调动效现成
- 场景总时长必须 = timing total（wait 补齐到秒）

渲染环境：

- 类名固定 `class P103Scene(Scene)`，渲染命令 `python -m manim -ql --disable_caching`
- **镜头动画（zoom/pan）必须继承 `MovingCameraScene`**：`class P103Scene(MovingCameraScene)` 然后才能用 `self.camera.frame.animate.scale(...)`——普通 Scene 的 camera 没有 frame 属性（2026-10-06 capital2 实证）
- ffmpeg 由管线注入 PATH，勿在代码里调用外部命令
- 确定性：不用 random（要用则 `random.Random(42)` 实例）
