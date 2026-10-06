"""pipeline — 103 v2 自主生成脊柱（ARCHITECTURE-v2）。

渲染器无关生产链：
  topic → storyboard(内容/旁白/数学) → TTS→timing(音频物理时钟)
        → renderer decision(两步+why-not) → autonomous codegen
        → smoke/veto gate → deterministic render → QA(归一化错误通道)
        → repair(受控轮次) → mux → final QA

原则：系统约束"不能错什么"，模型自主决定"怎么表现"。
"""
__version__ = "2.0.0"
