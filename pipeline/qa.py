"""qa.py — 归一化 QA 层：时长/帧活力（反空帧）/contact sheet/报告。视觉抽检留人+VLM。"""
from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FFPROBE = ROOT / "runs" / "architecture-smoke" / "node_modules" / "@remotion" / "compositor-win32-x64-msvc" / "ffprobe.exe"
FFMPEG = FFPROBE.parent / "ffmpeg.exe"


def duration(video: str) -> float:
    r = subprocess.run([str(FFPROBE), "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", video], capture_output=True, text=True)
    return float(r.stdout.strip())


def frame_variance(video: str, n: int = 12) -> list[float]:
    """采样 n 帧算像素标准差——捕全片空白/死帧（Case D 教训：exit 0 也能全空）。"""
    from PIL import Image
    vd = duration(video)
    out = []
    for i in range(n):
        t = vd * (i + 0.5) / n
        png = Path(video).parent / f"_qa_{i}.png"
        subprocess.run([str(FFMPEG), "-y", "-loglevel", "error", "-ss", str(t), "-i", video,
                        "-frames:v", "1", str(png)], capture_output=True)
        if not png.exists():
            out.append(-1.0); continue
        im = Image.open(png).convert("L").resize((320, 180))
        px = list(im.getdata())
        mean = sum(px) / len(px)
        out.append(round((sum((p - mean) ** 2 for p in px) / len(px)) ** 0.5, 2))
        png.unlink()
    return out


def contact_sheet(video: str, out_jpg: str, times: str = "0.5,3,6,9,12,15,18,21") -> str:
    """PIL 拼接抽帧网格（ffmpeg 多输入滤镜语法过脆，弃用）。"""
    from PIL import Image
    ts = [float(t) for t in times.split(",")]
    vd = duration(video)
    ts = [min(t, vd - 0.1) for t in ts]
    tiles = []
    tmp = Path(out_jpg).parent
    for i, t in enumerate(ts):
        png = tmp / f"_sheet_{i}.png"
        subprocess.run([str(FFMPEG), "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video,
                        "-frames:v", "1", str(png)], capture_output=True)
        if png.exists():
            tiles.append(Image.open(png).resize((480, 270))); png.unlink()
    if not tiles:
        return out_jpg
    cols = min(4, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 480, rows * 270), "white")
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 480, (i // cols) * 270))
    sheet.save(out_jpg, quality=88)
    return out_jpg


def check(video: str, timing: dict, workdir: Path) -> dict:
    report = {"video": video, "checks": {}}
    c = report["checks"]
    vd = duration(video)
    c["duration"] = {"value": round(vd, 2), "expect": timing["total"],
                     "pass": abs(vd - timing["total"]) <= 0.25}
    var = frame_variance(video)
    blank = sum(1 for v in var if v < 3.0)          # std<3 ≈ 纯色帧
    c["frame_variance"] = {"samples": var, "blank_frames": blank, "pass": blank <= max(1, len(var) // 6)}
    sheet = contact_sheet(video, str(workdir / "out" / "qa_sheet.jpg"))
    c["contact_sheet"] = {"path": sheet, "pass": Path(sheet).exists()}
    report["pass"] = all(v["pass"] for v in c.values())
    (workdir / "out" / "qa_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                                    encoding="utf-8")
    return report
