# implementation-notes.md — R1 复现假设（hypothesis，非原作者事实）

## 一句话定性
**实时 WebGL 交互应用的脚本化屏幕录制**，不是时间轴渲染的动画视频。

## recommended_backend
**web_3d（three.js 系）+ HTML/UI 层 + 脚本化操作录制**，confidence 0.9

## 判断依据（全部来自观察层）
1. UI 悬停高亮态（Oxygen/Expanded 悬停变浅蓝）——浏览器 DOM 事件行为，非绘制动画（证据 t=8.5, 24s）；
2. 左下数值实时小幅更新（281.17→285.17 kN / 345→348 bar）——运行中状态量，非烘焙字幕（t=24-24.5s）；
3. 滑杆值多路独立（Oxygen:48 / Fuel:79 / Thrust:100%）——交互面板；
4. 60fps 流畅、光标可见、无剪辑痕迹——屏幕采集。

## likely_primitives（按功能层）
| 功能 | 候选实现 |
|---|---|
| 模型 | glTF：部件级命名层级（泵壳/转子/燃烧室/喷管独立 node），PBR 金属材质 |
| 剖切视图 | three.js clipping plane（localClippingEnabled）或预剖几何 |
| 爆炸图/分离 | 每部件 target offset + 缓动（lerp/GSAP），轴向分离沿部件局部轴 |
| 高亮/变暗 | material emissive 切换 + 其余部件材质降饱和/透明度（Focus 状态机驱动） |
| 管路粒子 | CatmullRomCurve3/TubeGeometry 路径 + instanced points/sprite 沿弧长推进；**可见性绑定装配态**（部件分离→该路 flow.disable()）——观察证实此耦合存在 |
| 羽流 | 锥形 shader 渐变（白核→紫→蓝缘）+ 噪声扰动，长度/亮度绑定油门参数 |
| UI | HTML/CSS 覆盖层（标签/按钮/滑杆），非 canvas 内绘制 |
| 实时数值 | 简化仿真或查表（throttle→推力/压力/流量），DOM 更新 |
| 相机 | 基本固定 + 少量 tween；31.5s 起模型自身 turntable 旋转 |
| 采集 | puppeteer 脚本化输入（click/hover/drag 序列）+ headless 60fps 录屏，或真机 OBS |

## possible_implementation（复现两条路线）
**路线 A：交互应用 + 脚本化录制**（原作路线推断）
1. three.js 场景 + glTF + Focus/装配/流动三状态机 + HTML UI；
2. 写 input-script（操作剧本：hover→tab→slider→explode→turntable）；
3. puppeteer 驱动 + MediaRecorder/帧采集 → mp4。
- 优点：一次开发，视频与可交互产物双得；演示即视频。
- 缺点：时序不可逆推（录出来什么样就是什么样），QA 无逐帧锚点。

**路线 B：确定性时间轴（103 生产线路线）**
把同一场景图的所有状态参数写成 t 的纯函数：cut(t)∈{0,1}、explode_k(t)、flow_k(t)、
highlight(t)、camera(t)、数值=表驱动——renderFrame(t) 逐帧离屏渲染。
- 优点：接入现有 P103 QA 管线（keyframes.mjs 探针、VLM 审帧、帧级回修）；
- 缺点：失去"交互感"（悬停态、即时反馈要伪造），文案卖点（throttle it yourself）不可表达。

**结论：此类内容的教学视频版应走 B（生产质量可控），产品版走 A；B 可复用 A 的全部 3D 资产与状态机逻辑。**

## failure_risks（复现容易失败的地方）
1. **部件级建模深度**是真正的成本项：泵壳可分离+转子暴露+喷注器阵列可见，意味着 glTF 里
   有真实工程级内部结构，不是外观壳——没有 CAD 源几乎无法低成本复刻；
2. 粒子-装配态耦合逻辑：断管断流是最有说服力的细节，漏掉就露馅；
3. UI 悬停态与光标时序：路线 B 伪造这些容易穿帮（悬停高亮出现却没有光标靠近的过程）；
4. 实时数值的可信度：查表值要随滑杆即时刷新且量级自洽（kN/bar/kg/s 三者联动），硬编码会假；
5. 60fps 金属高光对 PBR 环境贴图敏感，光照错则"廉价感"立刻出现。

## 与 103 体系的映射
- 新增渲染后端类型：**WEB_3D**（three.js，P103 契约可扩展为 renderFrame(t) 驱动场景图状态）；
- 对应用户二期方向①「精密器械实验项目」：此风格正是该方向的目标形态之一；
- 素材路线：glTF 资产（自建或 CC0 工程模型）→ 状态机 → 时间轴脚本 → 现有 QA/VLM 管线复用。
