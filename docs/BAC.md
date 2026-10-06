# BAC — Backend Adapter Contract（后端适配契约）

ARCHITECTURE-v2 附录补丁 2。任何 renderer 接入统一管线须实现本契约。

## 接口

每个后端模块 `pipeline/adapters/<name>.py` 提供：

```python
render(workdir: Path, timing: dict, **kw) -> dict
# ok: bool
# video: str            # mp4 路径（或 frames 目录 + 由适配器负责编码）
# errors: list[dict]    # 归一化错误通道
# meta: dict            # 帧数/版本等

smoke(workdir: Path) -> dict   # 环境探针 + ≥10 帧冒烟（60-90s 判决）
```

## 归一化错误通道（KP-003）

`errors: [{kind, frame?, t?, message}]`，kind ∈：

| kind | 语义 |
|---|---|
| `env` | 环境/依赖缺失（安装提示即可修复） |
| `contract` | 交付物违反契约（如缺 window.P103、duration 非法） |
| `render` | 渲染过程失败（编译错/运行时崩溃） |
| `frame` | 特定帧异常（附 frame/t 坐标，定向修复用） |

**判定规则：exit code ≠ 0 或 errors 非空，任一即失败**（双通道教训）。

## WEB_2D 页面契约

交付自包含 `index.html`（无网络依赖），暴露：

```js
window.P103 = {
  duration: <秒>, fps: 24, width: 1920, height: 1080,
  renderFrame(t) { /* 按 t 纯函数式重建整帧；返回 true */ }
};
```

捕获器：`web2d_capture.mjs`（puppeteer-core + 系统 Chrome）逐帧调用 renderFrame → JPEG → ffmpeg 编码。禁止真实时钟驱动、未种子化随机（五关契约第 1 关）。

## MANIM 契约

交付 `scene.py`：`class P103Scene(Scene)`，`construct()` 按旁白句起点排布，总时长=timing total。错误通道=exit code + stderr。中文必须 `font="Microsoft YaHei"`（KP-006）。

## CUSTOM 否决门

提名 JSON：`{tech, env_check, frame_check, frame_out, min_frames}`。`backends.smoke_gate()` 自动执行：环境命令 → 10 帧渲染命令 → 帧数断言。失败自动回退 web_2d 并记录 verdict（菜单盲测与逃生日志的数据源）。
