"""backends.py — renderer 注册表 + 五关契约文本 + 冒烟否决门（ARCHITECTURE-v2 §6-§7 + 附录补丁1/2）。"""
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BACKENDS = {
    "web_2d": {
        "name": "WEB_2D",
        "capabilities": "SVG / Canvas 2D / GSAP / HTML+CSS / 现代 motion graphics；任意视觉风格；文字排版最强",
        "limitations": "几何精度取决于自绘代码质量；无自带数学对象",
        "contract": "交付单个自包含 index.html（无网络依赖），实现 window.P103 = {duration, fps, width, height, renderFrame(t)}。"
                    "renderFrame(t) 必须纯函数式按 t 重建整帧（state=F(t)），返回 true；禁止真实时钟/未种子化随机。"
                    "禁止任何自驱动渲染循环（requestAnimationFrame/setInterval/setTimeout 反复调用 render 或 renderFrame，含所谓'本地预览'）——"
                    "捕获器外部驱动 renderFrame(t)，页面自驱动画布重绘会与截图竞态、污染捕获帧。",
        "pitfall_tags": ["web_2d", "generic"],
    },
    "manim": {
        "name": "MANIM",
        "capabilities": "数学对象/坐标系/函数曲线/几何变换/公式推导原生支持；3B1B 级数学表达",
        "limitations": "默认审美强（易同质化——决策时必须声明风格差异化方案）；中文需 font='Microsoft YaHei'；"
                       "LaTeX(MathTex) 依赖重，优先 Text+unicode",
        "contract": "交付单个 scene.py，定义 class P103Scene(Scene)：construct() 中按旁白句起点排布动画，"
                    "总时长=timing total。动画时间=物理秒。需确定性（同 seed 同输出）。",
        "pitfall_tags": ["manim"],
    },
    "three_3d": {
        "name": "THREE_3D",
        "capabilities": "立体几何/空间结构/三维物理关系；相机语言丰富",
        "limitations": "构图与灯光质量方差大；CJK 文字需 sprite/canvas 贴图",
        "contract": "同 WEB_2D 宿主（无头 Chrome + WebGL 软件渲染可行），window.P103 契约一致；"
                    "渲染体积大，帧预算注意。",
        "pitfall_tags": ["web_2d", "generic"],
    },
    "custom": {
        "name": "CUSTOM",
        "capabilities": "Blender/D3/Vega-Lite/Motion Canvas/Remotion/Godot/TikZ/Asymptote 等一切满足五关契约的技术",
        "limitations": "必须过自动否决门：环境探针 + 10 帧冒烟渲染 60s 判决；失败即回退菜单",
        "contract": "提名时给出：技术名、确定性保证方案、帧输出命令（10 帧样例）、mp4/帧序列产出方式。",
        "pitfall_tags": ["generic"],
    },
}


def menu_text(profile: dict | None = None) -> str:
    allowed = (profile or {}).get("backend", {}).get("allowed", list(BACKENDS))
    rows = []
    for k in allowed:
        b = BACKENDS[k]
        rows.append(f"- {b['name']}: {b['capabilities']}\n  限制: {b['limitations']}")
    return "\n".join(rows)


def smoke_gate(nomination: dict, workdir: Path) -> dict:
    """CUSTOM 否决门（附录补丁1）：一句提名 → 自动验证，30-60s 判决。不问模型要辩护文。"""
    verdict = {"ok": False, "nomination": nomination, "evidence": []}
    env_cmd = nomination.get("env_check")
    if env_cmd:
        try:
            r = subprocess.run(env_cmd, capture_output=True, text=True, timeout=30, shell=True)
            ok = r.returncode == 0
            verdict["evidence"].append({"env_check": ok, "out": (r.stdout + r.stderr)[:200]})
            if not ok:
                return verdict
        except (subprocess.TimeoutExpired, OSError) as e:
            verdict["evidence"].append({"env_check": f"error: {e}"})
            return verdict
    frame_cmd = nomination.get("frame_check")          # 例：python gen.py --frames 10 --out <dir>
    if frame_cmd:
        out_dir = nomination.get("frame_out", str(workdir / "smoke_frames"))
        shutil.rmtree(out_dir, ignore_errors=True)
        try:
            r = subprocess.run(frame_cmd, capture_output=True, text=True, timeout=90, shell=True,
                               cwd=str(workdir))
            n = len(list(Path(out_dir).glob("*.png"))) + len(list(Path(out_dir).glob("*.jpg")))
            ok = r.returncode == 0 and n >= nomination.get("min_frames", 10)
            verdict["evidence"].append({"frame_check": ok, "frames": n, "out": (r.stdout + r.stderr)[-300:]})
            if not ok:
                return verdict
        except (subprocess.TimeoutExpired, OSError) as e:
            verdict["evidence"].append({"frame_check": f"error: {e}"})
            return verdict
    verdict["ok"] = True
    (workdir / "smoke_verdict.json").write_text(json.dumps(verdict, ensure_ascii=False, indent=2),
                                                encoding="utf-8")
    return verdict
