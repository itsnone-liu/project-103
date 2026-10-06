# 生产硬约束（五关契约，ARCHITECTURE-v2 §4 + BAC）

任何 renderer/技术路线进入生产管线必须满足：

1. **逐帧确定性**：state = F(t)——同一输入、同一 t、同一随机种子 → 同一帧。禁止依赖真实时钟（Date.now/setTimeout 驱动动画）、未种子化随机、累积式 mutate。支持任意帧重渲/并行渲染/精确抽帧
2. **无头离线渲染**：服务器可跑，无 GUI 交互依赖，无网络依赖（资源本地化）
3. **程序化帧输出**：1080p（1920×1080）+ 24fps，帧序列（PNG/JPEG）或等效 mp4，可进统一 mux
4. **CJK 文字/数学表达**：中文渲染正确（字体嵌入/系统字体可寻址），数学量可审计
5. **可归一化错误通道**：渲染失败可被 QA 层以统一语义捕获（BAC §错误通道）

## 输出规格

- 时长 = 旁白 timing 总长（TTS 实测，±0.2s 容差）
- 旁白句起点数组注入模型（**n+1 项，含 tEnd**——KP-002）
- 音频：narration（TTS）+ BGM（-16 LUFS loudnorm）由管线 mux，renderer 只管画面

## 语义标签表（审计词表，不绑定实现）

REVEAL · COMPARE · TRACE · EMPHASIS · DERIVE · FREEZE_EVENT · COUNT_UP · SUPERPOSE · TRANSITION · RECAP —— storyboard 可用作自述结构，QA 用作对齐度量；任何 renderer 不要求实现任何固定 API。

叙事自述词表（可选，来源：外部标杆案例集，见 `knowledge/success-cases/EXTERNAL-opus5-teaching-benchmark-2026-10.md`）：直觉先行 → 机制 → 形式化；每段一个核心类比；结尾回收。仅作 storyboard 自述参考，非必填结构。
