Logline: Clawd画出一枚三角形，把两个角撕下并搬到第三个顶点，拼成平角，证明内角和为180°。
World: 手绘水彩纸面，背景用柔和奶油色与浅青色；三角形用靛蓝线条，三个角分别绑定蓝、玫红、绿色。开场清爽，拼合时暖金提亮，收尾回到纸面小板。全片平面二维，角色和线条保持轻微手绘抖动。
Motif: 三个彩色角扇最终沿同一直线排开，首尾以三角形与直线的形状呼应。
Clawd's arc: 专注观察 → 动手拆角 → 惊喜发现拼成平角 → 自信确认结论。
节奏目标：约30秒；实际时长随TTS生成。所有动作时点使用旁白句内分数，不写死秒数。

## Parameters
画布：1920×1080 px。代码必须绘制且只使用以下三点作为三角形顶点；所有角度计算均由这些坐标导出。

- A = (610, 820)
- B = (1310, 820)
- C = (1098, 238)

按向量点积求内角：
- ∠A = arccos(((B−A)·(C−A))/(|B−A||C−A|)) ≈ 50.00°
- ∠B = arccos(((A−B)·(C−B))/(|A−B||C−B|)) ≈ 70.00°
- ∠C = arccos(((A−C)·(B−C))/(|A−C||B−C|)) ≈ 60.00°
- 总和 ≈ 180.00°

三个角的角色色：A蓝、B玫红、C绿色；拼合后的平角沿用相同颜色顺序。

## Narration
1. 看，三角形有三个内角。
2. 我们把三个角分别染色。
3. 沿顶点撕下蓝角和红角。
4. 把它们飞到绿色角旁。
5. 三个角排开，正好成直线。
6. 五十加六十加七十，等于一百八十。
7. 所以，三角形内角和是平角。

## Shots
A. 开场，建立图形与三角形顶点。（1, 0.00–0.72）[transition in: 从纸纹缓缓显影，形状由纸面线条接成三角形]  
reads:
- (1, 0.00–0.46) Clawd指向完整三角形，三个顶点清晰可见。[FOCUS_REVEAL] [NARRATION_ANCHOR]
- (1, 0.46–0.72) 三个顶点依次轻亮，提示接下来关注角。[STAGGER_REVEAL] [HOLD]

B. 标角，依次显出三处角弧与度数。（2, 0.00–0.88）  
reads:
- (2, 0.00–0.30) 蓝色角弧在A处描出，出现50°。[TRACE_PATH] [COLOR_BIND] [LIVE_ANNOTATION]
- (2, 0.30–0.58) 玫红角弧在B处描出，出现70°。[STAGGER_REVEAL] [COLOR_BIND] [LIVE_ANNOTATION]
- (2, 0.58–0.88) 绿色角弧在C处描出，出现60°；三角形完整保持可读。[STAGGER_REVEAL] [COLOR_BIND] [HOLD]

C. 拆角，蓝角和红角从各自顶点被轻轻撕离。（3, 0.00–0.82）  
reads:
- (3, 0.00–0.25) Clawd先看向A，手臂蓄势，蓝色扇形边缘起纸纤维撕裂感。[FOCUS_REVEAL] [ANTICIPATION_WINDUP]
- (3, 0.25–0.54) 蓝角沿边界撕下，留下一道蓝色缺口标记。[FREEZE_EVENT] [LEAVE_MARK] [IMPACT_BURST]
- (3, 0.54–0.82) 视线转向B，玫红角随后撕下；绿色角留在C处。[STAGGER_REVEAL] [LEAVE_MARK] [NARRATION_ANCHOR]

D. 搬运，两个彩角沿弧线飞往C点。（4, 0.00–0.88）  
reads:
- (4, 0.00–0.38) 蓝角先沿高弧飞向C，拖出短短的蓝色轨迹。[ARC_TOSS] [TRACE_PATH] [FOCUS_REVEAL]
- (4, 0.38–0.70) 玫红角错开起飞，沿另一条弧线追上；镜头轻推向C。[ARC_TOSS] [STAGGER_REVEAL] [CAMERA_PUSH]
- (4, 0.70–0.88) 两角抵达绿色角旁，Clawd惊喜抬手，短暂停住。[FREEZE_EVENT] [HOLD] [EVENT_EMPHASIS]

E. 拼合，三块彩色角扇依序沿一条直线排开。（5, 0.00–0.92）  
reads:
- (5, 0.00–0.30) 绿色角留在中间作为基准，直线方向先被轻柔引出。[FOCUS_REVEAL] [TRACE_PATH]
- (5, 0.30–0.62) 蓝角旋转就位，玫红角接着旋转到另一侧，边缘严密相接。[SUPERPOSE_COPY] [STAGGER_REVEAL] [COLOR_BIND]
- (5, 0.62–0.92) 三角扇形完全对齐成一条直线；定格并闪光，线两侧出现平角弧。[FREEZE_EVENT] [EVENT_EMPHASIS] [HIGHLIGHT_BOX] [HOLD]

F. 算式，角度依序汇总并确认结果。（6, 0.00–0.95）  
reads:
- (6, 0.00–0.25) 蓝、绿、红三段依序亮起，分别对应50、60、70。[COLOR_BIND] [STAGGER_REVEAL]
- (6, 0.25–0.68) 算式50+60+70从左至右计数累加，结果落在180。[COUNT_UP] [LIVE_READOUT] [NARRATION_ANCHOR]
- (6, 0.68–0.95) 180°盖印确认，Clawd欣喜点头，结果留在画面供阅读。[STAMP_ANSWER] [HOLD] [IMPACT_BURST]

G. 收尾回顾，简洁展示拆前与拼后。（7, 0.00–1.00）[transition out: 三角形外轮廓顺势拉直，化作纸面回顾板，再淡回纸纹]  
reads:
- (7, 0.00–0.42) 左侧显示原三角形与三处彩色内角，右侧显示拼成的平角。[SHOW_BEFORE_AFTER] [COLOR_BIND] [FOCUS_REVEAL]
- (7, 0.42–0.76) 三角形轮廓轻轻淡出，平角与180°结论保持醒目。[STAMP_ANSWER] [HIGHLIGHT_BOX] [HOLD]
- (7, 0.76–1.00) Clawd回到开场的指向姿势，但指向拼合后的直线；纸面温暖收住。[NARRATION_ANCHOR] [HOLD]

## Transitions
- 入片：纸纹显影，三角形由手绘线条逐笔接成。
- A→B：沿顶点方向的轻柔刷痕擦拭，承接画线动作。
- B→C：镜头沿蓝色角弧推近，切在Clawd伸手动作上。
- C→D：蓝角撕离的运动接成飞行弧线，动作连续。
- D→E：玫红角抵达时匹配切至C点附近的拼合构图。
- E→F：定格闪光后，镜头轻推到彩色平角与算式区域。
- F→G：180°印章的圆形轮廓扩展为回顾板的圆弧，再落回纸面。
- 出片：回顾板淡入纸纹，留出结论落点后柔和结束。
