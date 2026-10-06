# 教学侧语料挖掘：edu-math-video 方法论（7 文件）

文件代号（下文引文均出自这 7 个文件，已完整读取）：
- **SKILL** = `research/edulab/skills/edu-math-video/SKILL.md`
- **VD** = `…/edu-math-video/reference/visual-design.md`
- **ANI** = `…/edu-math-video/reference/animation.md`
- **TSB** = `…/edu-math-video/template/storyboard.md`
- **CSB** = `…/edu-math-video/examples/cone-parallel/storyboard.md`
- **AG** = `…/skills/edu-analytic-geometry/references/conventions.md`
- **SG** = `…/skills/edu-solid-geometry/references/conventions.md`

「出现 N 文件」= 上述 7 个文件中有直接文本证据的文件数。TSB/CSB 是同一方法论的模板层与实例层，计数天然反映"规则+模板+实例"三层印证。★ = 种子标签。

## 教学 pattern 清单

| TAG | 语义 | 出处文件+短引文 | 出现在几个文件 |
|---|---|---|---|
| EVENT_EMPHASIS ★ | 提到即点亮：旁白念到的元素被荧光笔脉冲强调，无关元素同时变淡 | VD:「旁白提到哪个元素，它就被点亮；无关元素变淡 → `glow(pts, col, bump(lt, at(k,f)))`」；ANI:「bump…配合 glow 在'提到'时闪一下」 | 5（SKILL/VD/ANI/TSB/CSB） |
| FREEZE_EVENT ★ | 动点在关键处停住再强调：滑到目标点停、最值处停下闪一下 | VD:「到最值处停下闪一下」；TSB:「红点沿 AB 从 A 滑到中点 D」；CSB:「点从 P 滑到 PA 中点 Q」 | 3（VD/TSB/CSB） |
| TRACE_PATH ★ | 轨迹题：拖驱动点实时描路径，再叠加轨迹方程 | AG:「拖驱动点 + `trace` 描路径 + 叠加方程」 | 1（AG） |
| SHOW_BEFORE_AFTER ★ | 同图两态对比：分类讨论依次切换（或左右双小图）；验算前后数值替换 | VD:「分类讨论｜同一张图画两种情况：依次切换，或左右各一个小图」；VD:「把答案代回：图上的数值更新到答案」 | 1（VD） |
| NEW_SENTENCE_ACTION | 一句旁白必有一个"演出推理"的动作；只出现/只闪不算动（图会讲题） | SKILL:「每句旁白，图上都有一个动作把这句推理演出来……不是只多出一条线、一个标签」；VD:「图形一次画好……所有解释都写在右边板子上」＝差的做法 | 4（SKILL/VD/TSB/CSB） |
| NEW_FOUR_BEAT | 每句旁白按 指→动→留→连 四拍组织，是分镜表的固定列 | VD:「每句旁白的四个动作：指 → 动 → 留 → 连」；TSB 表头:「｜句｜旁白要点｜指｜动｜留｜板书｜」 | 4（SKILL/VD/TSB/CSB） |
| NEW_GIVEN_REVEAL | 第一幕亮原题，逐条读条件、逐条框选（hiBox）+条件 chip 标签 | SKILL:「旁白逐条读条件，每读一条就在图上框出那一条」 | 5（SKILL/VD/ANI/TSB/CSB） |
| NEW_SUPERPOSE_COPY | 复制-搬运-叠合：线段/三角形/角/平面的着色复制品平移+旋转(+缩放 k)后与目标重合，演示相等/平行/全等/相似/面面平行 | VD:「两条线段相等｜一条的复制品平移+旋转到另一条上重合｜`slideSeg`」；CSB:「平面 QOC 沿向量 OB 平移，正好落进平面 PBD」 | 4（SKILL/VD/TSB/CSB） |
| NEW_LEAVE_MARK | 动作结束留痕（直角/等长/平行/角标记、数值、着色），后续句子可引用 | VD:「留｜动作结束后留下标记，后面的句子可以引用｜`rightM` 直角、`tickM` 等长、`paraM` 平行」 | 4（SKILL/VD/TSB/CSB） |
| NEW_STAMP_ANSWER | 答案用盖章动画 + 图上对应元素 glow 双重确认 | VD:「需要强调答案时：`stamp` 盖章 + 图上对应元素 glow」；CSB 多幕行尾「盖章」 | 5（SKILL/VD/ANI/TSB/CSB） |
| NEW_COUNT_UP | 求出的量：数字从 0 数到结果，同时线段 glow 从一端扫到另一端 | VD:「求出一个长度｜这条线 glow 从一端扫到另一端，旁边数字从 0 数到结果｜`countTo`」；TSB:「AB 旁数字从 0 数到 5」 | 4（SKILL/VD/TSB/CSB） |
| NEW_CAM_CONTINUITY | 立体↔俯视：同一 3D 模型连续转相机（pitch→π/2），禁止硬切另一张图 | VD:「同一个 3D 模型把相机转到正上方，不要硬切换到另一张图」；CSB:「相机从斜视转到正俯视（同一模型）」 | 4（SKILL/VD/ANI/CSB） |
| NEW_RECAP_CARDS | 结尾回顾卡片组 + 答案播报（收束拍） | ANI:「outro 幕：3 张卡片中心 x=400/960/1520，y=450」；SKILL:「最后一幕 outro 回顾 + 报答案」 | 4（SKILL/ANI/TSB/CSB） |
| NEW_MULTI_SOURCE_ASSERT | 答案多源一致：kernel＝答案卡＝末步骤展示＝前端重算；图/板/字幕与解答一致 | AG:「kernel 算出的答案 == 答案卡 lesson.answer == 末步骤展示值 == 前端 JS…重算值，四者一致」；SG:「三者一致」；ANI:「图上数值、板子算式、字幕与你第 1 步的解答完全一致」 | 4（SKILL/ANI/AG/SG） |
| NEW_COLOR_BIND | 图上量、板子行、结论同色绑定，复杂时 callout 连线（语义四色见规范 B1） | VD:「板子上的算式和图上的量用同一种颜色……复杂时用 `callout` 箭头从图指向板子那一行」 | 3（SKILL/VD/ANI） |
| NEW_NARRATION_ANCHORED_TIME | 一切时刻＝「第 k 句的 f 比例处」`S.at(k,f)`，绝不写死秒数（换配音不错位） | SKILL:「每个动画都用'第 k 句旁白开始的时刻'`S.at(k, f)` 定时，绝不写死秒数」 | 3（SKILL/VD/ANI） |
| NEW_SCENE_CONTINUITY | 幕开头以参数=1 复现上一幕终态再开始新动作（图形状态机） | VD:「每幕开头承接上一幕结尾的状态（同一个画图函数，参数设为 1）」；ANI:「下一幕开头把上一幕结尾的状态直接设为 1」 | 2（VD/ANI） |
| NEW_FIGURE_INVENTORY | 先列图形清单：题目每个点/线/关系必须画出；位置按数据计算不许目测 | VD:「漏画（例如题目说 DE∥BC 却没画 DE）是严重错误，比动画不好看更严重」；「用 `mix2(A, B, 2/5)` 这样算坐标，不要目测」 | 3（SKILL/VD/ANI） |
| NEW_MOTION_LINT | 机器审"每句有动"（STATIC 必须修、每幕≥1 句 MOVE）+ 人工看截图，两层缺一不可 | VD:「STATIC：这句图上完全没变化 → 必须改」；SKILL:「打开 build/sheet.png 亲眼检查……不能只看命令有没有报错」 | 3（SKILL/VD/ANI） |
| NEW_INVARIANT_MOTION | 动点来回移动、相关元素跟随，性质（颜色/标记/从属）全程保持 | VD:「点在线段上来回移动，相关直线跟着动，始终保持性质（颜色不变、标记不变）」；CSB:「T 沿 OC 来回移动，QT 跟着动，始终在绿色平面内」 | 3（SKILL/VD/CSB） |
| NEW_DRAW_ON | 按作图/推理顺序逐笔"长"出来：三边依次画、辅助线虚线长出、弧长出、半径扫过 | VD:「作辅助线｜虚线从起点'长'出来｜`draw([P,Q],{dash:[12,10],p:P(…)})`」；TSB:「三边依次画出，直角符号画出」 | 3（VD/TSB/CSB） |
| NEW_UNROLL_TRANSFORM | 剪开-摊平/压扁的 2D↔3D 连续形变（圆锥侧面→扇形、线段→射影）；中间态示意即可 | VD:「中间过程不必是严格的几何展开，观众看到'剪开—摊平'就懂了」；CSB:「侧面沿 PA 剪开，展开成半径 2 的半圆」 | 3（SKILL/VD/CSB） |
| NEW_LIVE_READOUT | 动点/动参数旁的实时读数：(x,y)、时间、路程随动更新 | VD:「用'题目时间'驱动人物移动，旁边时钟和路程读数实时变化」；ANI:「在图形区左上角实时显示时间和路程」 | 2（VD/ANI） |
| NEW_TYPEWRITE_BOARD | 板书逐行逐字写出，与旁白同步（打字机），重点行放大变色 | ANI:「`bl(i, str, t, lt, o)`｜板子第 i 行……从 t 时刻逐字写出」；SKILL:「逐行写推导（与图同色）」 | 3（SKILL/VD/ANI） |
| NEW_VERIFY_BEAT | 验证拍：答案代回使图上数值/性质标记更新亮起；或动点遍历展示"任意位置都成立" | VD:「验算｜把答案代回：图上的数值更新到答案，性质标记（平行、相等）亮起」；CSB outro2:「T 任意位置都成立……T 来回移动」 | 2（VD/CSB） |
| NEW_PROJECT_DROP | 投影"落下"：点沿虚线落到面/轴，落点出直角符号；原线段被"压"到射影 | VD:「从点'落下'一条虚线到底面，落点出现直角符号」；CSB:「P 沿轴落到 O，PA 跟着被'压'到 AO 上」 | 2（VD/CSB） |
| NEW_ANGLE_CARRY | 角的搬运：着色扇形/角弧复制后旋转/平移到另一角上（内错角、同位角） | VD:「一个角的弧 + 着色扇形复制后移到另一个角上」；CSB:「O 处 60° 扇形绕 OC 中点转半圈落到 C（内错角）」 | 2（VD/CSB） |
| NEW_FLY_INTO_FORMULA | 计算幕图上也要动：数值标签从图沿弧线飞进板子算式；移项＝该项文字滑到对侧并变号 | VD:「图上对应的数值标签飞进板子上的算式：`flyText('2', 图上2的位置, blPos(1,180), …)`」；「移项时让那一项的文字从左边滑到右边并变号」 | 1（VD） |
| NEW_ACTION_WINDOW | 动作时长 0.6–1.5s，置于句内 15%–80%（头留"指"、尾留"留"）；一句只做一个主动作 | VD:「动作放在句子的 15%~80% 之间：开头留给'指'，结尾留给'留'」；「一句话里只做一个主要动作」 | 1（VD） |
| NEW_ONE_POINT_PER_LINE | 一句旁白一个知识点（≤36 汉字宽、分句≤18 字），画面同步只添一个元素 | SKILL:「每句旁白 ≤ 36 个汉字宽……一句只讲一件事」；错误表:「一句旁白塞三四个知识点｜一句一个点，画面同步出现一个元素」 | 1（SKILL） |
| NEW_STEP_HIGHLIGHT_CAMERA | 分步揭示（交互）：每步给定应可见元素集合 + 专用相机视角；建系步亮坐标轴 | SG:「每步 `highlight` 给出该步应可见的元素（绝对集合）……每步 `cameraPos` 给一个能看清当前重点的视角」 | 1（SG） |
| NEW_DRAG_EXPLORE | 题型→交互范式固定：弦长/面积＝转直线+范围条；定值＝转动点；定点＝动直线穿定点 | AG 解法配方表交互范式列:「转直线 + 范围条」「转参数 + 动直线穿定点(`emphasis`)」 | 1（AG） |
| NEW_PARAM_SLIDER_BAND | 参数滑块直接驱动曲线形变；答案区间在参数轴高亮（answerBand）；NaN 点自动隐藏＝直观"不存在" | AG:「用 `answerBand` 在参数轴上高亮答案区间（如 e∈(1,2]）」；「表达式算出 NaN 的点会自动隐藏，直观表现'不存在'」 | 1（AG） |
| NEW_ENDPOINT_REACHABLE | 端点开闭＝能否被真实合法图形取到；交互件必须能拖到答案端点且读数＝答案 | AG:「端点是否'闭' = 是否被某条真实合法直线取到」；「滑块能拖到端点对应的 θ 时，读数应正好等于答案端点值」 | 1（AG） |

### 与现有 Pattern Library 原语的粗对应（供合并参考）
- EVENT_EMPHASIS ≈ `pulseRing` + `dimOthers`（glow 点亮 + `grp(0.3,…)` 变淡是同一拍的两个半边）
- FREEZE_EVENT ≈ `freezeFrame`（到点停住再强调）；TRACE_PATH ≈ `tracePath`（拖动描迹）；SHOW_BEFORE_AFTER ≈ `beforeAfter`（两态切换 / 数值代回前后）
- NEW_COUNT_UP / NEW_LIVE_READOUT 正对 Case C 发现的"量化总结（Δx/刻度/时间轴）两模型全缺"缺口，建议列为标准件
- NEW_STAMP_ANSWER / NEW_LEAVE_MARK / NEW_FOUR_BEAT 是本仓库特有、库里尚无的"结论确认"与"节奏骨架"件

## 可代码化的视觉规范

**B1 语义四色系统（配色＝角色，不是审美）**
- 规则：已知量蓝、所求/答案红、辅助线/关键结论绿、强调黄；同一幕内颜色含义不得改变。
- 引文：ANI:「约定配色：已知量蓝色，所求量/答案红色，辅助线/关键结论绿色，强调黄色」；VD:「同一幕里用过的颜色含义不要变」。
- 原语草案：`const ROLE = {given: C.blue, ask: C.red, aux: C.green, hi: C.yellow}`；`bindRole(el, 'given'|'ask'|'aux'|'hi')` → 返回颜色，图/板/标记共用同一取色函数。

**B2 画布分区与安全框（1920×1080 固定网格）**
- 规则：图形区 x 60–900 / y 130–860；横线板 x 930–1870、第 i 行 y = 192 + 62·i；标签条 y 40–105；字幕框 y 914–1044；一切内容 y ≤ 860、板书 x ≤ 1850。
- 引文：ANI 版面图:「x 60 ~ 900｜y 130 ~ 860」「x 930 ~ 1870, y 130 ~ 880｜bl() 第 0~10 行，行距 62」；SKILL:「所有画面内容在 y ≤ 860 以内（y≈914~1044 是字幕框）」。
- 原语草案：`layout1080() → {figure, board, subtitle, tag}`；`boardRowY(i) => 192 + 62*i`；`assertInBounds(el, zone)`（出界即 lint 报错）。

**B3 手绘线型默认值**
- 规则：线宽 4、抖动 rough 1.7（0＝直线）、虚线 [12,10]；面着色透明度 0.1–0.25，叠加不得更高（会挡线）。
- 引文：ANI:「o.w 线宽(4)，o.rough 抖动(1.7，0=直)，o.dash:[12,10]」「着色用 a ≤ 0.25」。
- 原语草案：`HAND = {w: 4, rough: 1.7, dash: [12,10]}`；`fillPoly(pts, col, a = 0.2)` 内部 `clamp(a, 0, 0.25)`。

**B4 荧光笔置底 + 提到即脉冲**
- 规则：glow 画在元素**下面**（先调 glow 再画元素）；脉冲 bump 为 t0 起 0→1→0、默认 1.2s。
- 引文：ANI:「glow(pts, col, a, w=22)｜荧光笔：在元素下面画粗的半透明线（先调用它再画元素）」「bump(lt, t0, dur=1.2)｜t0 起 0→1→0 的脉冲值」。
- 原语草案：`glowUnder(pts, {color, w=22})`（与元素绑定成对调用，保证层级）；`pulse(t0, dur=1.2)`。

**B5 点标签外偏移**
- 规则：点名字母偏移朝图形外侧约 30–40px，避免压线。
- 引文：ANI:「ptLabel('A', q, dx, dy, p, col)｜……偏移朝图形外侧，约 30~40px」。
- 原语草案：`labelPoint(name, pt, {offset: outward(pt, shapeHull, 35)})`。

**B6 几何标记语汇族（"留"的标准件）**
- 规则：直角 `rightM`、等长 `tickM`（n 条短杠＝分组）、平行 `paraM`（中点处 >）、角弧 `angM`；标记在动作完成后出现并可被后续句引用。
- 引文：ANI 几何标注表；VD:「留｜`rightM` 直角、`tickM` 等长、`paraM` 平行、`angM` 角、数值标签、半透明着色」。
- 原语草案：`mark.right(v,a,b)` / `mark.tick(p,q,n)` / `mark.parallel(p,q)` / `mark.angle(v,a,b,{r})`，均接 `{t0}` 定时、返回可引用的 mark id。

**B7 旁白锚定时间原语**
- 规则：一切时刻＝第 k 句的 f 比例处；进度 `P(a, dd=0.7)`；动作时长 0.6–1.5s 且落在句内 15%–80%。
- 引文：ANI:「S.at(k, f)：第 k 句旁白（从 0 数）开始后，经过这句时长的 f 比例的时刻」；VD:「动作放在句子的 15%~80% 之间」。
- 原语草案：`at(k, f=0)`、`prog(a, dur=0.7)`、`actionWindow(k) => {from: at(k,.15), to: at(k,.8), dur: clampSpan(.6, 1.5)}`。

**B8 确定性帧函数**
- 规则：同一 t 画同一张图；禁 `Math.random()/Date.now()/setTimeout/跨帧累加`；随机用 `hash(n)`，持续动作用 `NOW`；动点位置＝路程函数(时间)。
- 引文：ANI:「renderFrame(t) 必须是确定性的：同一个 t 画出同一张图」；「用时间参数算位置，不要逐帧累加」。
- 原语草案：`renderFrame(t: number): Frame`（纯函数契约）；`posAt(pathSpec, t)`；`hash(n)`。

**B9 幕切换交叉淡化 + 状态承接**
- 规则：幕间自动交叉淡化 0.75s；下一幕以"参数=1"复现上一幕终态。
- 引文：ANI:「幕切换时自动交叉淡化 0.75 秒」；VD:「每幕开头承接上一幕结尾的状态（同一个画图函数，参数设为 1）」。
- 原语草案：`crossFade(dur=0.75)`；场景函数约定 `fig(state=1)`，`carryState(prevScene.finalState)`。

**B10 3D 渲染规范：隐藏棱 / 关键线 / 坐标轴 / 静息微动**
- 规则：被挡住的棱画虚线（课本规范）；所求线用 emphasis 色 + `depthTest:false` 始终可见；辅助线 aux 色 + dashed；坐标轴一般只在建系步显示；可让相机 yaw 缓慢正弦摆动增立体感（每帧重设保确定性）。
- 引文：ANI:「被挡住的棱画虚线（课本规范），画完看截图确认哪些该虚」；SG:「关键线（所求直线）用 emphasis 色并 depthTest:false（始终可见）……坐标轴用 axes，一般只在建系那步显示」；ANI:「CAM.yaw = 0.2 + 0.14 * Math.sin(NOW * 0.42)」。
- 原语草案：`edge3(a, b, {hidden: true}) → dashed`；`alwaysOnTop(line, role='ask')`；`axesVisibleStep = 'setup'`；`idleSway(cam, {amp:0.14, speed:0.42, now})`。

**B11 坐标映射（数学→屏幕，三套约定）**
- 规则：平面 `sx = offX + x·scale, sy = offY − y·scale`（y 翻转）；3D 渲染 `three = (x, z, y)·scale`；`camTween` 中 `pitch: PI/2`＝正俯视。
- 引文：AG:「sx = offX + x·scale，sy = offY − y·scale（y 翻转）」；SG:「three = (x, z, y) * scale」；ANI:「camTween(A, B, e)……pitch: PI/2 为正俯视图」。
- 原语草案：`toScreen(xy)`、`toThree(xyz)`、`topView(cam) => ({...cam, pitch: PI/2})`。

**B12 视窗自适应边距**
- 规则：曲线主体四周留约 10–15% 边距；开口方向多留；参数范围避开退化值。
- 引文：AG:「让曲线主体留约 10–15% 边距：椭圆 xRange≈[-1.8a,1.8a]；抛物线开口方向多留」。
- 原语草案：`fitView(curveBounds, {margin: 0.125, bias: 'opening'})`。

**B13 交互读数与答案带**
- 规则：滑块/动点配 `status` 实时读数；答案区间用 `answerBand` 在参数轴高亮（端点开闭可视化）；表达式为 NaN 的点自动隐藏。
- 引文：AG:「用 status 读数显示存在性/不等式是否成立……表达式算出 NaN 的点会自动隐藏」；「用 answerBand 在参数轴上高亮答案区间」。
- 原语草案：`readout(bindTo, fmt)`；`answerBand(axis, [lo, hi], {loClosed, hiClosed})`；`plot(f)` 内部 NaN→skip。

**B14 板书排版约束**
- 规则：每行 ≤ 约 40 字符；一幕 ≤ ~9 行（再多分两幕）；默认字号 38、重点行 44–50；每句旁白 ≤ 36 汉字宽、分句 ≤ 18 字。
- 引文：ANI:「每行 ≤ 约 40 个字符，超出会出板」「板子一幕内最多 ~9 行」；SKILL:「每句旁白 ≤ 36 个汉字宽（否则字幕折两行）」。
- 原语草案：`boardLine(i, text, {size=38, role})` + `fitBoard(lines) → assert(len≤40 && rows≤9)`。

**B15 图↔板连线**
- 规则：图上量与板书行的对应复杂时，用弯曲虚线箭头从图指向板子该行。
- 引文：ANI:「callout(from, to, p, col)｜从图上一点到板子某行的弯曲虚线箭头」。
- 原语草案：`callout(figPoint, boardRow(i), {p})`。

## 这套方法论与通用动画最重要的 3 个差异点

1. **动作即推理，且有映射表和 lint 强制——运动承担证明职能，不是表达职能。** 通用动画里运动服务节奏/氛围/吸睛；这里每句旁白必须有一个把推理"演出来"的动作，且推理→动作是可查表的：相等→复制品叠合、全等→三角形叠上去、立体↔平面→转相机、求值→数字计数、验算→代回更新（VD 动作表 20+ 行）。"只出现/只闪"会被 `render.mjs motion` 判 `STATIC`/`POP` 拒绝（SKILL:「图一次画好，之后每句只多一条线/一个标签」列为真实发生过的错误）。运动的正确性标准是"观众只看图能不能看懂这一步为什么成立"。

2. **旁白是时钟：相对句锚点 + 句内动作窗，而不是绝对时间轴/节拍点。** 所有元素的出现时刻＝"旁白提到它的时刻"，写成 `S.at(k, f)`（第 k 句的 f 比例处），绝不写死秒数——重配音、改一句词都不破坏全局同步；动作被约束在句内 15%–80%（头留"指"、尾留"留"），一句只做一个主动作、只讲一个知识点。通用动画按秒/节拍自由编排；这里时序的第一公民是"讲解句"。

3. **视觉服从数学真值的硬约束：数据驱动几何 + 留痕 + 多源一致 + 验证拍。** 通用动画可以夸张、示意、糊弄比例；这里几何位置必须按数据计算（「用 mix2(A, B, 2/5) 这样算坐标，不要目测」），题目每个对象必须画出（「漏画 DE 比动画不好看更严重」），"直角看起来是直角，等长看起来等长"，被挡棱按课本规范画虚线；答案必须 kernel＝答案卡＝末步骤展示＝前端重算四者一致；结尾还有验算拍/动点遍历证明一般性（"T 任意位置都成立"）。视觉永远让位于正确性。

---
*挖掘忠实性说明：以上全部引文逐字取自 7 个源文件；无仓库文本支撑的内容未收录。TRACE_PATH / SHOW_BEFORE_AFTER 在本批语料中各只有 1 个文件的直接证据（AG / VD），系种子标签在交互式与视频式两个子仓库中的分布所致，非臆断。*
