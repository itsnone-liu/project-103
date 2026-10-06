"""adapters — Backend Adapter Contract 实现（docs/BAC.md）。

每个后端实现 render(workdir, timing) -> {ok, video|frames, errors[归一化], meta}。
归一化错误通道（KP-003）：kind ∈ {render, env, contract, frame}，附 frame/t 坐标。
"""
