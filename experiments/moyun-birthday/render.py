"""Render the approved 103 birthday experiment arms via the existing WEB_2D capture adapter.

Explicit entry, separate from the narration-first teaching CLI. Captures source HTML frames,
encodes MP4, and muxes the same deterministic paper-ink Foley onto both. No video-model API.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pipeline.adapters import web2d

BASE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / "moyun-birthday"
FFMPEG = web2d.FFMPEG
FFPROBE = FFMPEG.with_name("ffprobe.exe")
EXPECTED = "岁岁欢喜，年年胜意"


def run(arm: str):
    if arm not in ("open", "assisted"):
        raise ValueError("arm must be open or assisted")
    html = BASE / arm / "index.html"
    text = html.read_text(encoding="utf-8")
    if EXPECTED not in text or "生辰快乐" in text:
        raise RuntimeError(f"Incorrect wording in {arm}/index.html")
    wd = OUT / arm
    (wd / "out").mkdir(parents=True, exist_ok=True)
    result = web2d.render(wd, {"total": 12}, html=html)
    if not result["ok"]:
        raise RuntimeError(f"{arm} capture failed: {result['errors']}")
    if result["meta"]["frames"] != 288:
        raise RuntimeError(f"Unexpected frame count: {result['meta']}")
    final = wd / "out" / f"birthday_{arm}.mp4"
    sound = OUT / "paper_ink.wav"
    if not sound.exists():
        raise RuntimeError("Missing paper_ink.wav; generate via sound.py")
    cmd = [str(FFMPEG), "-y", "-loglevel", "error", "-i", result["video"],
           "-i", str(sound), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "160k", "-t", "12", "-movflags", "+faststart", str(final)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if p.returncode or not final.is_file():
        raise RuntimeError(f"Mux failure: {p.stderr[-1000:]}")
    probe = subprocess.run([str(FFPROBE), "-v", "error", "-show_entries",
                            "stream=codec_type,codec_name,width,height,r_frame_rate,duration", "-show_entries",
                            "format=duration", "-of", "json", str(final)],
                           capture_output=True, text=True, timeout=30, check=True)
    meta = json.loads(probe.stdout)
    video = next(s for s in meta["streams"] if s["codec_type"] == "video")
    audio = next(s for s in meta["streams"] if s["codec_type"] == "audio")
    duration = float(meta["format"]["duration"])
    if (video["width"], video["height"], video["r_frame_rate"]) != (1280, 720, "24/1") or abs(duration-12) > .12:
        raise RuntimeError(f"Unexpected video format: {meta}")
    (wd / "out" / "render_report.json").write_text(json.dumps({"arm": arm,
        "frames": result["meta"]["frames"], "output": str(final), "ffprobe": meta,
        "sound": str(sound), "note": "No external video generation model used"}, indent=2), encoding="utf-8")
    print(f"{arm}: {final} {result['meta']['frames']} frames, audio {audio['codec_name']}, {duration:.3f}s", flush=True)


if __name__ == "__main__":
    arms = sys.argv[1:] or ["open", "assisted"]
    for arm in arms:
        run(arm)
