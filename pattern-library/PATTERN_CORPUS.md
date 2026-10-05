# PATTERN_CORPUS.md — Pattern Library 语料挖掘与核心库裁决 v1.0

七源语料 → beat/代码拆解打标 → 跨源频次 → §10 五标（高频/实现不稳定/参数可标准化/视觉增益明显/教学通用）→ 裁决。本文是"为什么收/不收"的证据账本。子报告全文：`corpus/edu-math-video-mining.md`（S4），其余报告在会话记录。

## 语料源

| # | 源 | 形态 | 规模 |
|---|---|---|---|
| S1 | opus-video-prompts | 18 条完整提示词 | 40KB |
| S2 | PDoomVideo 引擎+分镜+终章 | 制作级代码+文档 | core/timeline/props/cast + c08/c09 + STORYBOARD |
| S3 | PDoomVideo c01-c02（c07 待收；c03-c06 判定边际收益不足已略） | 制作级场景代码 | 105KB |
| S4 | edulab 方法论 | 教学动画方法论全套 | 7 文件 |
| S5 | awesome-opus-5.5-video | 1309 作品需求统计（8 类） | 链接表+提示词 335 条 |
| S6 | ClaudeAnimationBase demo.js | 官方示范代码 | 全读 |
| S7 | ANIMATION_GUIDE | 引擎指南 | v0 已验证 |

## 需求侧定调（S5 → 库的形态）

1. **教学类=高产出×极短提示词洼地**（130 作品、30% 有提示词但 74% 为一句话）→ 库的价值=**填空式结构**，用户保持一句话输入成本。
2. 教育时长双峰（35.9% <1min；26.6% >3min）→ 骨架分两档：30 秒单概念 / 3-8 分钟多章节。
3. 纪录片式教学=提示词率冠军（52.8%）→ 默认叙事档位之一；风格预设按"名字"表达（3B1B/手绘/BBC 纪录片三档起手）。
4. 爆款 pattern 的真实用法是**分叉**（单条自荐片提示词催生 15+ 变体）→ CUSTOM 缺口日志要记"变体轴"。

## 技术翻案（影响库设计）

**文字层可移植**（S2 core.js:117-151，已验证并入 v1）：letter 队列 → canvas2D 画进
独立 Graphics → flushLetters 离屏微型水彩 fill 强制 p5.brush 合成。解锁数字标注/
实时读数/拟声词/板书。v0"引擎无文字"结论作废。

## 跨源频次汇总（关键行）

| 形状 | S1 提示词 | S2/S3 PDoom | S4 edulab | S6 demo | 裁决 |
|---|---|---|---|---|---|
| EVENT_EMPHASIS（强调/暗角/脉冲） | 6 条 9 次 | EVENT_EMPHASIS 5 + CAM-PULSE 8 | 5 文件「提到即点亮」 | sparkle/glow | **收（v0 已有，证据最强）** |
| BEAT_GRID（拍钟/节拍网格） | 4 条（强式 numpy） | BEAT 30+、POGO、FLIP | — | — | **收（beatAt/pulseBeat）** |
| TRACE_PATH（描线/轨迹） | 4 条（机制级） | TRACE 5（弧长裁剪/贝塞尔） | 1（拖点描径+叠方程） | — | **收（v0 已有；机制级=recipe）** |
| STAGGER_REVEAL | 4 条 | 9（波次签名） | — | — | **收（v0 已有）** |
| CAMERA_PUSH（推近/几何推/前瞻） | 3 条 7 次 | 17/17 镜头 + 指数推 + LEAD | CAM_CONTINUITY 4 | camBegin | **收（v0 pushIn 扩指数+前瞻）** |
| ACCELERATE_AND_SETTLE | 2 条 | ANTIC 5 + 弹簧 6 | — | — | **收（v0 anticipation）+ settle 新增** |
| FREEZE_EVENT | **0**（负结果：代码生成偏好永动） | 2（"冻结是笑点标点"） | 3（"到最值处停下闪一下"） | — | **收（教学强/展示弱，标注边界）** |
| HOLD | 4 条 5 次 | 2（hold 慢漂） | — | — | **收（v0 已有）** |
| IMPACT_BURST（碎片弹道粒子） | — | HASH-PARTICLES 9+、IMPACT 8 | — | sparkle 家族 | **收（impactBurst）** |
| ARC_TOSS（拍上抛物+空翻） | — | 4 | — | arcPt 9 残影 | **收（arcThrow+trail）** |
| SHAKE（震屏衰减包络） | SCREEN_SHAKE 1（1-2px 克制） | SHAKE 10+7 | — | — | **收（shake→camBegin 偏移）** |
| IDEA_BURST（灵感爆闪） | — | — | — | :75-76 | **收（ideaBurst：glow+扇形错峰）** |
| VOLUME_SQUASH（保体积挤压通道） | — | 约定级 | — | — | **收（squash(k)→{sx,sy}）** |
| LIVE_ANNOTATION/COUNT_UP | 1（用量实时弹/计数器/进度条） | letter/sfx 层 | COUNT_UP 4 文件、LIVE_READOUT 2 | — | **收（countUp+liveReadout，Case C 缺口直接补）** |
| STAMP_ANSWER（盖章确认） | — | — | 5 文件 | — | **收（stampAnswer）** |
| LEAVE_MARK（几何标记语汇族） | — | — | B6 rightM/tickM/paraM/angM + 4 文件 | — | **收（markRight/ticks/parallel/angle）** |
| HIGHLIGHT_BOX（框选条件） | — | — | GIVEN_REVEAL 5 文件 + hiBox | — | **收（highlightBox）** |
| SUPERPOSE_COPY（叠合副本证相等） | — | — | 4 文件（slideSeg） | — | **收（superposeCopy）** |
| NARR 锚定（旁白=时钟，S.at(k,f)+动作窗） | NARRATION_SYNC 2 | — | 4 文件（一句一动 +15%-80% 窗） | — | **收（narr() 时序助手）+ MOTION_SKILL 主规则** |
| 语义四色（known/ask/aux/hi） | — | — | B1 3 文件 | — | **收（ROLE 常量+roleCol）** |
| SHOW_BEFORE_AFTER | 1 | — | 1（同图两态+代回） | — | **收（v0 已有+数字升级）** |
| SEAMLESS_MORPH_CHAIN | 2 | morph 家族 | — | — | 不收原语→MOTION_SKILL recipe（形状插值工程大，v2 候选） |
| NESTED_SCALE_ZOOM | 1 经典 | c07 待收 | CAM_CONTINUITY 相邻 | — | 不收独立原语→pushIn 链式 recipe |
| CURSOR_AS_PERFORMER | 2 | — | DRAG_EXPLORE 相邻（AG 交互侧） | — | 不收（引擎无 UI 层）→MOTION_SKILL 手法条目 |
| KINETIC_TYPOGRAPHY | 3 | letter 层 | TYPEWRITE_BOARD 3 | — | 部分收（letter 层承载），板书 recipe 进 SKILL |
| PICTURE_IN_PICTURE_DOCK | 1 | — | — | — | 不收（构图调度规则） |
| ANTI_TEMPLATE_BAN | 3 | — | — | — | 不收原语→SKILL"反模式清单"节 |
| PERFECT_LOOP / MICRO_IDLE_LOOP | 2/2 | idle sway | idle | — | 不收原语→SKILL 待机微动规则 |
| PHASE_MACHINE / ESCALATION_TABLE / DOOR_CHASE / POSE_TABLE 等 S2/S3 编排件 | — | 多 | — | — | 不收原语→MOTION_SKILL 编排规则 + 分镜模板吸收 |
| METER_CLAIM（道具认领协议） | — | 4 | — | — | v2（需 timeline 层改造） |
| irisShape 任意洞形 | — | 3 | — | — | v2（引擎 CAB 需移植） |

## 教学侧结构差异（S4，三条全部进 MOTION_SKILL 主干）

1. **动作即推理**：一句旁白必有一个"演出推理"的动作（只出现/只闪=STATIC 拒绝）；
   推理→动作映射表（相等→叠合 / 立体↔平面→转相机 / 求值→计数 / 验算→代回）。
2. **旁白是时钟**：一切时刻=第 k 句的 f 比例处；动作窗句内 15%-80%、0.6-1.5s；绝不写死秒数。
3. **视觉服从数学真值**：位置按数据计算不许目测；题目说的每个对象必画（漏画比难看更严重）；
   答案多源一致（图/板/字幕/重算）；结尾验证拍。

## 分镜结构惯例（S2，进分镜模板）

章节头三件套（N·标题·起止秒·调色板）/ 四列镜头表（Time|Lyric|Shot|Out）/ Out 转场必填 /
前置铁律（every shot something happens、text-light、情绪永不瞬变、镜镜有相机运动、主体占帧高 40%）/
道具入 Cast 表 / 客串必回归 / 副歌同舞台逐级升级 / 节拍锚定措辞。
S4 教学版：四拍列（指→动→留→板书）+ 每句一行 + 参数块数值强制。

## 编排级金律（S3）

拍钟跨章连续且转场锁拍；追逐=时间相位差非位置差；波次=缓动窗按索引平移；
离散状态由时刻表 filter 导出（无状态机）；身体/表情/气泡三轨分离；
"先给预告再给事件"；冻结用作节拍重音。

## 核心库 v1 规格结论

patterns.js v1 = v0 全保留（10 原语+kit）+ 新增：
beatAt/pulseBeat、impactBurst、arcThrow、shake、settle、ideaBurst、squash、
countUp、liveReadout、stampAnswer、markRight/markTicks/markParallel/markAngle、
highlightBox、superposeCopy、narr、ROLE/roleCol + 文字层（letter/label/sfx/flushLetters 已并入）。
合计 ~30 原语。其余形状以 recipe/规则形式进 MOTION_SKILL v1 与分镜模板。

## S3·c07 尺度章（已回收）

独有 pattern（≥2 次）：BALLISTIC_DEBRIS(9，≡impactBurst 已覆盖)、CONVEYOR_BEZ_FLOW(4)、
BEAT_RESEEDED_LIGHTS(3)、WEIGHT_ON_ENV(3)、SPEED_STREAKS(3)、RUNAWAY_QUAD_ACCEL(3)、
DUTCH_TILT_SLIDE、SCENE_HANDOFF、VIB_RATTLE（≡anticipation 物体变体）。
NEW 候选 11 条：SCALE_LADDER、LOG_SCALE_TRAVEL、SCALE_ARCS、SQUARE_ROLL、
CRUNCH_TO_DENSE_OBJECT、STEP_GROWTH_ON_BEAT、PSEUDO_3D_CORRIDOR、LIGHT_FRONT_REVEAL、
ELASTIC_BULGE_SNAP、CHEEK_CAPACITY_METER、WAVY_FLOOD_RISE。
核心思路："不直接缩放主体，让世界按比例回应主体"（环境应变当秤/密度写成能量泄漏/
以层为单位的相机/节拍阶梯生长）。
**裁决：全部单源单用 → 不进 v1，列 v2 回流候选**（第二次同形状出现才固化）。
编排思想"环境应变当秤"记入 MOTION_SKILL 教学条目（测量类动画可用痕迹表达量）。
