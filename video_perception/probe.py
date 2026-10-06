# -*- coding: utf-8 -*-
"""probe.py — 视频元信息 + 旁白静音切分（章节假设），零模型成本。"""
import json, re, subprocess
from pathlib import Path

FFPROBE = r"D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\architecture-smoke\node_modules\@remotion\compositor-win32-x64-msvc\ffprobe.exe"
FFMPEG = r"D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\architecture-smoke\node_modules\@remotion\compositor-win32-x64-msvc\ffmpeg.exe"


def meta(video: str) -> dict:
    r = subprocess.run([FFPROBE, "-v", "quiet", "-print_format", "json",
                        "-show_format", "-show_streams", video],
                       capture_output=True, text=True, timeout=60)
    d = json.loads(r.stdout or "{}")
    fmt = d.get("format", {})
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), {})
    return {"duration": float(fmt.get("duration", 0)),
            "width": v.get("width"), "height": v.get("height"),
            "fps": eval(v.get("r_frame_rate", "0/1")) if v else None,
            "has_audio": bool(a)}


def silence_boundaries(video: str, min_silence=0.35, noise_db=-32) -> list:
    """ffmpeg silencedetect → 静音中点作为章节边界假设（旁白驱动的教学片）。"""
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", video, "-af",
                        f"silencedetect=noise={noise_db}dB:d={min_silence}",
                        "-f", "null", "-"], capture_output=True, text=True, timeout=300)
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [round((s + e) / 2, 2) for s, e in zip(starts, ends)]


def probe(video: str) -> dict:
    m = meta(video)
    m["chapter_hypothesis"] = silence_boundaries(video) if m["has_audio"] else []
    return m


if __name__ == "__main__":
    import sys
    print(json.dumps(probe(sys.argv[1]), ensure_ascii=False, indent=1))
