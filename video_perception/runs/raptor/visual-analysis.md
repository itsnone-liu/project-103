# visual-analysis.md — R1（Inside the Raptor 3，oneshotted.io，34.7s，盲测）

> 首次真盲测：无真值可对照，观察=qwen3-vl-plus 6 张 sheet，推理=本会话。
> 证据等级严格标注；此文件本身即盲测产物。

## 第一问：这个视频如何表达内容
**这不是"动画"，是一个实时交互式 3D 说明应用的屏幕录制**（证据：UI 悬停高亮态、
光标交互、滑杆值随操作变化、左下数值实时小幅更新 281.17→285.17 kN、绿色 Running 态按钮）。
内容=SpaceX Raptor 3 发动机的内部结构教学（全流量分级燃烧循环）。

## Composition
- **视觉中心**：发动机模型恒占画面中心 ~60%，UI 面板右上、文案左上、导航底部——四角分工固定，观者永不迷路。
- **hierarchy 由状态机驱动**：Focus 标签（All/Oxygen/Methane/Fire/Exhaust）切换时部件高亮/其余变暗半透明
  （12-14.5s 分离壳体变浅灰半透明即同机制）——注意力管理是**参数化**的，不是逐帧设计的。
- **negative space**：深蓝黑背景+展台灯光，把金属高光衬成唯一亮度层。

## Motion（证据绑定）
| 主张 | 语义作用 | 证据 | 状态 |
|---|---|---|---|
| 泵壳轴向分离（12-14.5s 渐进） | 揭示"壳里有什么"——转子暴露 | 5 帧连续位移序列 | CONFIRMED |
| **部件分离↔管路粒子流中断同步**（13-14.5s） | 断开的管路不该有流动——物理一致性即教学语言 | 粒子消失与壳体位移同帧段 | CONFIRMED |
| 剖切↔外观切换（18.5s）+冷却回路绿粒子 | "进去看→出来看"的认知往返 | 3 帧 | CONFIRMED |
| 爆炸图（24s）+实时数值随滑杆变化 | 操作→状态的因果闭环（throttle it yourself） | 滑杆位置+数值更新 | CONFIRMED |
| 收拢→特写→转台旋转（31-32.5s） | "One shaft, two jobs"的仪式性收束：一轴双泵 | 4 帧+标题切换 | CONFIRMED |
| 羽流点火增长（0-1s） | Test Run 的即时反馈 | 3 帧 | CONFIRMED |

## Camera
相机基本固定，视角变化少而缓（18.5s 后退、24.5s 微移）；31.5s 起是**模型自身转台旋转**而非环绕相机
（VLM 区分了这一点）——turntable 是展品语义，环绕是电影语义，此片选了前者。

## Transition
无场景切换。章节由**应用内状态切换**承担（标题文字变化、Focus 标签切换、装配态变化）——
教学结构内嵌在交互状态机里，而不是剪辑里。

## Teaching
- **viewer_read**：Raptor 3 内部是什么、推进剂怎么流、为什么叫全流量循环、一轴双泵是什么意思。
- **prerequisite**：观众见过发射（文案自证："Everyone has seen the big launch… Almost nobody has seen what happens inside"）。
- **new_information**：内部结构、流动路径、操作与输出的耦合。
- **visual_encoding**：剖切=内部；爆炸图=空间关系；粒子色=流体种类（白/青=氧化剂系，橙黄=燃料，绿=冷却）；
  高亮/变暗=注意力；实时数值=因果。
- **why_motion_needed**：**去 motion 完全不成立**——静态图无法表达流动方向、装配关系、操作因果。
  更进一步：去**交互**也不成立——滑杆-数值耦合是本片独有的教学通道（观众看到"输入改变→系统响应"）。
- **cognitive_load**：medium-high（同屏 UI+文案+3D+数值），靠状态机聚焦缓解。
- **hold_time_sufficient**：是（每状态停留 >1.5s，60fps 流畅无跳切）。

## 全片位（推断，LIKELY）
airsup.ai 的系列化交互教具之一（Raptor 1/2/3+TurboPump 导航在片内可见）；oneshotted.io 是
"AI 做的 web 应用"展台。本片是该应用的**操作脚本化演示**：它卖的不是视频，是"你可以自己开"。
