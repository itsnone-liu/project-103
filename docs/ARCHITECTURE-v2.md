# 103 教学视频体系 · 自主生成恢复与知识增强架构方案（权威版 v2）

**日期**：2026-10-06
**性质**：架构转向实施方案（用户裁决定稿）
**定位**：本文为 103 体系权威架构文档；证据链与推导过程见同目录《architecture-pivot-discussion-2026-10-06.md》。

---

## 一、总体裁决

103 教学视频体系不再以 "ClaudeAnimationBase + patterns.js + Motion Skill" 作为默认动画语言。

新的核心原则是：

«系统约束"不能错什么"，模型自主决定"怎么表现"。»

因此体系调整为三部分：

1. **自主生成主路径**：默认路径；不预设手绘风格；不强制 Pattern API；不强制某一 renderer；模型根据具体内容自主决定视觉表达和技术实现。

2. **知识/经验增强路径**：保留并建设知识库、经验库；默认不参与所有任务；是否启用、启用到什么程度，由具体生产项目决定；可以用于建立某一系列课程或项目的稳定路线。

3. **视频识别分析能力**：作为未来能力预留；当前只冻结接口、数据结构和使用场景；暂不实现视频抽帧、视觉分析、reference→code 闭环。

---

## 二、这次调整解决的根本问题

旧体系原本希望：

```
Opus 优秀经验
    ↓
ClaudeAnimationBase
    ↓
Motion Skill / Pattern
    ↓
GLM / Luna
    ↓
获得接近 Opus 的动画能力
```

实际结果却变成：

```
ClaudeAnimationBase 的默认视觉语言
        ↓
brush / watercolor / handwritten
        ↓
patterns.js 再次固化
        ↓
prompt 再次强化
        ↓
所有模型输出向手绘收敛
```

问题不是某几个 API 写错，而是：

«我们试图把强模型开放式设计能力提前压缩成一套有限的表达语言。»

结果产生 **architecture-induced capability collapse**——体系本身降低了模型原来可能拥有的能力。

因此本次不是修补 "inkLine"、"markAngle"、"superposeCopy" 等技术细节，而是重新划分**生产约束**与**创作自由**的边界。

---

## 三、新体系的第一原则：默认自主

默认生产路径中，模型只接收：教学内容、教学目标、数学/事实约束、TTS/timing、生产技术条件、可用 renderer/工具、输出要求。

**不默认接收**：固定 Motion Pattern、固定美学、固定 scene grammar、固定 animation API、固定成功案例、固定视觉套路。

模型自行决定：怎么讲 → 怎么分 scene → 什么视觉语言合适 → 是否需要 2D/3D → 使用 Manim / SVG / Canvas / Three.js / 其他 → 构图 → motion → transition → camera → 代码实现。

---

## 四、保留的生产脊柱

**4.1 内容生产流程**：教学内容 → Storyboard → Narration → TTS → Physical Timing → Code Generation → Render → Audit → Repair → Mux → Final QA。这是整个 103 的核心生产流水线。

**4.2 TTS → Timing 倒置**：坚持 Narration → TTS → 实际音频时间 → narration timing → 动画依据真实时间编排。不恢复"先猜 timing 再硬塞语音"。

**4.3 确定性渲染**：同一输入、同一时间 t、同一随机种子，应得到相同状态。优先 state = F(t) 而非 state[n] = mutate(state[n-1])，从而支持任意帧重渲、并行渲染、故障恢复、精确抽帧、QA、reference comparison。

**4.4 数学和事实审计**：继续强化数学真值、事实依据、对象身份、数值、公式、几何关系、字幕/旁白一致性。视觉自由不意味着数学自由。

**4.5 Render / QA / Repair**：保留 page error 检测、渲染失败检测、帧抽取、contact sheet、VLM 抽检、narration alignment lint、subtitle lint、mux、loudnorm、输出完整性检查。

---

## 五、手绘体系正式降级

原 ClaudeAnimationBase / patterns.js / MOTION_SKILL / brush renderer **不删除，整体降级为 "HAND_DRAWN_STYLE_PACK"**。

定位：«一种特殊视觉风格，而不是教学视频默认 runtime。»

**5.1 适用场景**：儿童内容、童书、手绘解释、水彩、人文故事、柔和视觉、创意 sketch、用户明确指定手绘风格。

**5.2 不再自动启用**：禁止"教学视频→默认 hand-drawn"。新逻辑是用户/项目明确选择 → 加载 STYLE_PACK，否则完全不进入模型上下文。

**5.3 原 Pattern 的重新定位**：
- **A. 实现 API**（markAngle/superposeCopy/inkLine 等）：只属于 HAND_DRAWN_STYLE_PACK，不再进入通用教学 runtime。
- **B. 教学语义词汇**（COMPARE/FREEZE_EVENT/REVEAL/TRACE/EMPHASIS/DERIVE）：保留为 storyboard 标签、audit 标签、分析词汇、评估指标，不要求对应任何固定实现。
- **C. Motion Pattern**：不再作为系统强制 vocabulary；保留历史资料，不默认加载。

---

## 六、Renderer 架构恢复开放

系统不再规定所有视频必须通过一个统一 animation runtime，改为**统一生产管线 + 多个 renderer backend**。

初期核心后端：

| 后端 | 适合 |
|---|---|
| **WEB_2D** | 普通知识讲解；SVG；Canvas；GSAP；HTML/CSS；UI 风格；现代 motion graphics |
| **MANIM** | 数学；坐标；函数；几何；公式推导；数学证明 |
| **THREE_3D** | 立体几何；空间结构；三维物理关系 |
| **CUSTOM** | 允许模型在明确理由下选择其他技术：Blender、D3、Vega-Lite、Motion Canvas、Remotion、Godot、TikZ、Asymptote 等 |

---

## 七、Renderer Selection 不代替模型决策

系统可向模型提供 Available Backends / Capabilities / Known Limitations / Rendering Requirements，但原则上由模型根据任务决定。决策结构示例：

```json
{
  "backend": "manim",
  "reason": "本题核心是函数变换和坐标几何，Manim 的数学对象和公式支持最直接。",
  "alternative": "web_2d",
  "risk": "需要控制默认 Manim 风格，避免所有内容视觉同质化。"
}
```

作用是«让决策显式化»，而不是«替模型决定»。

---

## 八、知识库 / 经验库继续建设

角色从«默认指导所有视频»改为«项目级可选生产资产»。

## 九、知识体系分三类

**9.1 硬知识**（可默认使用）：数学事实、教材知识、API 文档、renderer API、版本信息、已确认 bug、已知 API 陷阱、渲染环境信息、生产协议。这类信息不会明显限制创作空间。

**9.2 失败经验**（相关任务中条件性检索）：某 renderer 哪个 API 容易误解、某种写法会渲染为空、哪些 timing 容易越界、哪些实现容易出现遮挡、哪些 API 参数是 delta 而不是 absolute。作用是«避坑»，不是«指挥设计»。

**9.3 成功设计经验**（默认不加载）：某课程系列已验证的视觉路线、某种题型成功 storyboard、某一风格的成熟构图、某项目固定 transition、某项目统一镜头语法。只有在项目明确选择后使用。

---

## 十、知识库采用"项目级启用"——三个运行模式

**MODE A — OPEN**（默认）：经验库/成功案例/固定 style 均不加载，模型拥有最大创作空间。适合新题型、创意探索、新课程、capability test、architecture spike。

**MODE B — ASSISTED**：用户允许使用知识库但不强制。系统可检索相似失败、已知坑、可参考成功案例。所有成功案例明确标记 REFERENCE ONLY / NON-BINDING，模型可采用、修改、忽略。

**MODE C — PROJECT_ROUTE**：用户明确决定"这个生产项目就沿用已验证路线"，允许建立固定生产 profile。目的不是探索，而是«稳定批量生产»。

---

## 十一、项目级固定路线是有意的路径依赖

**不好的路径依赖**：系统替所有未来任务决定"教学视频就应该这样做"。
**有价值的路径依赖**：用户决定"这一套 80 集课程已经找到满意风格，后面的 70 集保持一致"。

原则：«体系层不锁死，项目层允许锁死。»

---

## 十二、Production Profile

每个固定路线项目拥有自己的 production-profile.yaml：

```yaml
mode: PROJECT_ROUTE
visual:
  style: clean_vector
  reference_project: algebra-grade7-v1
backend:
  preferred: manim
  allowed: [manim, web_2d]
storyboard:
  pacing: medium
  intro_max_seconds: 8
knowledge:
  use_project_cases: true
  use_global_success_cases: false
  use_failure_memory: true
creative_freedom:
  allow_new_layout: true
  allow_new_transition: true
  backend_escape_hatch: true
```

即使 PROJECT_ROUTE，也可继续保留一定自由度。

---

## 十三、知识库不直接等于 Prompt 注入

知识资产存储在外部。不要每次任务把整个知识库塞进 prompt。正确方式：当前任务 → 根据 project mode 决定是否检索 → 只取少量相关内容 → 送给模型。

---

## 十四、知识的生命周期

与现有 agent skill 生命周期类似：candidate → validated → project-proven → production → deprecated/archived。

任何一条成功经验都不能因为一次成功就升格成"全局规则"。

---

## 十五、默认禁止的做法

- 为了帮助弱模型 → 给所有模型默认塞大量 design skill
- 从 100 个优秀视频 → 提炼 100 个 pattern → 要求所有模型使用
- 发现一个成功视觉方案 → 自动升格成全局默认
- 某 renderer 当前效果不错 → 把整个系统绑定到该 renderer

---

## 十六～二十、视频识别分析能力：只做预案

**Video Perception Layer** 为未来预留，当前不实现。目标场景：A 参考优秀视频分析（scene/composition/timing/camera/motion/transition → 模型重新设计）；B 分析自己输出（遮挡/僵硬/hierarchy/transition/timing → 自动 repair）；C Reference vs Render 比较输出定向修复建议。

**v0 预案**：MP4 → ffprobe → shot/timestamp 抽取 → 关键帧 → contact sheet → 字幕/transcript → 视觉模型 → structured analysis。不要求 coding model 原生支持 MP4。预留 analyze_video() 接口（输出 duration/shots/keyframes/visual_hierarchy/motion_events/camera_events/transitions/viewer_reads/implementation_hypotheses），同时保留关键帧图片。

**当前明确不做**（全部进 future backlog）：视频自动 scene detection、optical flow、object tracking、motion vector extraction、video embedding、自动参考视频检索、reference→code 自动重建。只有真实生产证明"没有视频感知能力已成为明显瓶颈"才启动。

---

## 二十一、新生产架构

```
        教学内容 → Storyboard → Narration/TTS → Physical Timing
                          ↓
                   Renderer Decision
          ┌───────────────┼───────────────┐
        WEB_2D         MANIM          THREE_3D
          └───────────────┼───────────────┘
                          ↓
                  Autonomous Codegen
                          ↓
                Deterministic Render
                          ↓
             Frame / Visual / Math QA ──fail→ Repair ─┐
                          ↓                            │
                        Mux ←──────────────────────────┘
                          ↓
                     Final Video

知识系统从侧面接入：Knowledge/Experience → project mode decides access → model context when needed
视频感知层：Reference/Own Video → Video Perception → visual evidence → design/repair model（当前保持关闭）
```

---

## 二十二、实施阶段

- **Phase 1 — 恢复自主主路径**：移除 ClaudeAnimationBase 默认 runtime 地位；移除 hand-drawn 默认 prompt；Pattern API 不再进入通用模型上下文；恢复 renderer 自主选择；保留生产流水线。
- **Phase 2 — 手绘风格包隔离**：brush engine / patterns.js / MOTION_SKILL 整理为 styles/hand-drawn/，只有显式请求时加载。
- **Phase 3 — 项目模式**：实现 OPEN / ASSISTED / PROJECT_ROUTE，建立 production-profile。
- **Phase 4 — 知识资产整理**：分类 hard-facts/ known-pitfalls/ failure-cases/ success-cases/ project-routes/；不一次性大规模建设，从真实生产逐步增长。
- **Phase 5 — 自主生产验证**：真实教学题目测试（geometry / function / motion / general explainer），检查视觉多样性、renderer 合理性、修补次数、数学准确性、生产成功率。
- **Phase 6 — Video Perception**：暂不执行，只保留设计文档和接口。

---

## 二十三、成功标准

不以"是否建立了足够多的 Pattern"衡量，而以：

- **生产能力**：能稳定生成、自动渲染、自动 QA、能 repair、能批量生产
- **模型能力释放**：不同任务出现不同视觉语言；不同 renderer 自然出现；不再全部向某个 Style Pack 收敛
- **项目一致性**：需要一致性的项目通过 PROJECT_ROUTE 稳定生产
- **系统开放性**：新 renderer、新模型、新视觉技术能够接入，无需重新设计整个体系

---

## 二十四、最终定位

103 不再是«一个教学动画引擎»，而是«一个 AI 教学视频生产系统»。

它真正拥有的是：内容组织 + TTS 与时间系统 + 数学/事实契约 + 多 renderer 生产能力 + 确定性渲染 + 自动审计 + 自动修复 + 项目知识资产 + 项目级生产路线。

具体怎么画、怎么动、是什么视觉语言——默认交还给模型和成熟生态。

---

## 二十五、最终原则（冻结）

- **P1** 体系层默认开放，项目层允许固定。
- **P2** 硬约束用于保证正确性，不用于规定创作方式。
- **P3** 成功经验可以保存，但不得自动升格为全局规则。
- **P4** Style Pack 是可选能力，不是默认世界。
- **P5** 视频感知是未来增强能力，在出现真实生产需求之前不提前建设。

**最终目标**：

«既不重新发明 Opus，也不把 GLM/Luna 塞进我们设计的小世界。系统负责让模型能够可靠生产，而不是替模型决定应该怎样创作。»

---

## 附录：实现补丁（讨论 appendix；1-4 已随 v2.1 体系调整落地，2026-10-06）

以下五项来自架构讨论的工程缺口。落地状态（v2.1 = pipeline/ + knowledge/ + styles/ + profiles/ 重构）：

1. **CUSTOM 逃生自动否决门**（并入 §6/§7）：一句提名 → 自动环境探针 + 10 帧冒烟渲染 30 秒判决；菜单项强制逐项 why-not；定期菜单盲测采样度量"菜单税"。**已落地**：`pipeline/backends.py smoke_gate()` + 两步决策提示词 + `produce.py --blind-sample`。
2. **Backend Adapter Contract / BAC**（新增章节）：每后端实现 ①确定性帧导出（t→PNG）②归一化错误通道（'page error' 是浏览器方言，Manim 是 stderr/exit code，QA 层需统一语义）③时长/音频钟注入约定 ④帧抽取兼容。**已落地**：`docs/BAC.md` + `pipeline/adapters/`（web_2d 全链路实测通过，manim 契约就绪）。
3. **Phase 5 指标与对照组现在钉死**：修补次数、数学准确率、生产成功率、**视觉多样性度量**（防 manim-collapse）+ 同故事板多后端对照。**待 Phase 5 启动时实现**（指标定义已冻结，本补丁即依据）。
4. **GLM thinking 配置先于 Phase 5 解决**（或 Phase 5 仅跑 Luna）：实验序已备，当前被 key 失效阻塞；`pipeline/llm.py` 已留 GLM_THINK=on|off|budget 实验位。
5. **知识资产 first batch 仅灌 known-pitfalls**（已实证条目：Case D 四歧义、inkLine 尖刺、GLM thinking 配置等），success-cases 留空等真实生产攒。**已落地**：`knowledge/known-pitfalls/INDEX.md`（KP-001..008）+ `knowledge/hard-facts/production-contract.md`。
