# Case C 协议规格 — 追及相遇教学动画（双模型同题，pattern 注解协议）

状态：待修正循环验证后启动

## 任务（发给两个模型的唯一提示词，20 秒）

> Read ANIMATION_GUIDE.md, then make a 20-second teaching animation:
> a turtle has a head start from the left marker and walks at a steady
> slow speed; Clawd starts later from the same marker and moves faster.
> They meet at the mathematically correct point — freeze and highlight
> the moment they meet, show both trajectories as trails, and end with
> a before/after summary comparing how far each walked.

数学要求：storyboard 必须显式声明数值（v_turtle, v_clawd, head_start 时长，
meet 时刻与位置），代码中的位置函数必须与声明一致（fail-closed 检查素材）。

## 协议（两模型完全一致）

1. **两段式调用**：
   - Phase 1（storyboard）：Guide 全文 + 任务 → pattern 注解式分镜。
   - Phase 2（code）：Guide 全文 + 自己的 Phase 1 分镜 + demo.js 格式例
     → 完整场景代码。
2. **GLM 配方**：thinking 默认开启（effort=max 不降档）、max_tokens 65536、
   temperature 1.0（已验证：小交付下思考自然收敛）。
   **Luna**：temp 1.0、max_completion_tokens 65536。
3. **修正循环 v1 介入**：渲染 → 视觉审查 → 单轮修复 → v2（两个模型都走）。

## pattern 注解式分镜格式（Phase 1 强制输出格式）

每条 read 追加 pattern 标签，取自 v0 词表：

```
FOCUS_REVEAL, STAGGER_REVEAL, FREEZE_EVENT, TRACE_PATH,
ACCELERATE_AND_SETTLE, CHASE_MOTION, CAMERA_PUSH, DIM_OTHERS,
MATCH_CUT, EVENT_EMPHASIS, SHOW_RELATIVE_DIFFERENCE, SHOW_BEFORE_AFTER
```

示例行：
```
reads:  8.2-9.0  两主体距离明显缩短  [CHASE_MOTION]
       12.0-12.6  相遇瞬间冻结+高亮  [FREEZE_EVENT][DIM_OTHERS]
```

## 代码侧对齐 lint（承诺-调用对齐率）

Phase 2 要求：每处实现某 pattern 的代码段前写标记注释
`/* PATTERN: FREEZE_EVENT */`（对齐分镜标签）。
渲染前机械检查：分镜标签集合 vs 代码标记集合 →
**对齐率 = |交集| / |分镜标签集合|**，进 BASE_COMPARE 报告。

## 验收（方案 §3.3 五维度 + C 专属）

- 相遇点正确性：按 storyboard 声明的速度/时刻，检查冻结帧位置
  （Phase 5 fail-closed 验证的前身，v1 人工+视觉确认）
- 对齐率 ≥ 80% 视为分镜-代码保真合格
- 双模型同题直比 + 修正循环前后对比（v1→v2 改善幅度）
