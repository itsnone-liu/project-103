"""web2d.py — WEB_2D 适配器：puppeteer-core 帧捕获（web2d_capture.mjs）+ ffmpeg 编码。"""
from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
NODE_MODULES = ROOT / "pipeline" / "node_modules"          # junction → case-c/luna（puppeteer-core）
FFMPEG = ROOT / "runs" / "architecture-smoke" / "node_modules" / "@remotion" / "compositor-win32-x64-msvc" / "ffmpeg.exe"


def render(workdir: Path, timing: dict, *, html: Path | None = None) -> dict:
    html = html or workdir / "code" / "index.html"
    if not html.exists():
        return {"ok": False, "errors": [{"kind": "env", "message": f"缺少 {html}"}]}
    frames = workdir / "out" / "frames"
    r = subprocess.run(["node", str(Path(__file__).parent / "web2d_capture.mjs"),
                        f"--html={html}", f"--out={frames}", f"--duration={timing['total']}"],
                       capture_output=True, text=True, timeout=1800, cwd=str(ROOT))
    err_path = workdir / "out" / "capture_errors.json"
    page_errors = json.loads(err_path.read_text(encoding="utf-8")) if err_path.exists() else []
    if r.returncode != 0 or page_errors:                    # KP-003 双通道
        return {"ok": False, "errors": page_errors or [{"kind": "render", "message": r.stderr[-500:]}]}
    video = workdir / "out" / "video.mp4"
    enc = subprocess.run([str(FFMPEG), "-y", "-loglevel", "error", "-framerate", "24",
                          "-i", str(frames / "f%05d.jpg"), "-c:v", "libx264", "-preset", "medium",
                          "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)],
                         capture_output=True, text=True, timeout=600)
    if enc.returncode != 0:
        return {"ok": False, "errors": [{"kind": "render", "message": enc.stderr[-500:]}]}
    return {"ok": True, "video": str(video),
            "meta": {"frames": len(list(frames.glob("f*.jpg")))}}


def smoke(workdir: Path) -> dict:
    """环境探针 + 10 帧冒烟：用内置 fixture 页验证捕获链本身健康。"""
    fx = Path(__file__).parent / "fixture_smoke.html"
    return render(workdir, {"total": 10 / 24}, html=fx)
