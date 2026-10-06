"""manim.py — MANIM 适配器。环境探针诚实报缺（未装≠体系故障），装好后 render 直接可用。"""
from __future__ import annotations
import shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FFMPEG = ROOT / "runs" / "architecture-smoke" / "node_modules" / "@remotion" / "compositor-win32-x64-msvc" / "ffmpeg.exe"


def _pythons() -> list[str]:
    cands = [shutil.which("python"), shutil.which("py"),
             r"D:\ComfyUI_windows_portable\python_embeded\python.exe"]
    return [c for c in cands if c]


def probe() -> dict:
    for py in _pythons():
        try:
            r = subprocess.run([py, "-c", "import manim, sys; print(manim.__version__)"],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                return {"ok": True, "python": py, "version": r.stdout.strip()}
        except (subprocess.TimeoutExpired, OSError):
            continue
    return {"ok": False, "hint": "pip install manim（需要 cairo/ffmpeg/pango 系统依赖）"}


def render(workdir: Path, timing: dict, *, scene_py: Path | None = None) -> dict:
    env = probe()
    if not env["ok"]:
        return {"ok": False, "errors": [{"kind": "env", "message": "manim 未安装: " + env["hint"]}]}
    scene_py = scene_py or workdir / "code" / "scene.py"
    if not scene_py.exists():
        return {"ok": False, "errors": [{"kind": "env", "message": f"缺少 {scene_py}"}]}
    media = workdir / "out" / "media"
    import os
    env_path = dict(os.environ)
    comp = str(FFMPEG.parent)                                   # manim 需要 ffmpeg 可执行
    env_path["PATH"] = comp + os.pathsep + env_path.get("PATH", "")
    r = subprocess.run([env["python"], "-m", "manim", "-ql", "--disable_caching",
                        "--media_dir", str(media), str(scene_py), "P103Scene"],
                       capture_output=True, timeout=1800,
                       encoding="utf-8", errors="replace", env=env_path)
    videos = sorted(media.glob("videos/**/*.mp4"))
    if r.returncode != 0 or not videos:                     # KP-003：exit + stderr 通道
        tail = (r.stderr or r.stdout or "")[-600:] or f"exit={r.returncode}, no video"
        return {"ok": False, "errors": [{"kind": "render", "message": tail}]}
    return {"ok": True, "video": str(videos[-1]), "meta": {"manim": env["version"]}}


def smoke(workdir: Path) -> dict:
    return probe()
