"""Media identity and duration probes for Project 103 (no transcoding)."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import wave
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _probe_wav(path: Path) -> dict:
    with wave.open(str(path), "rb") as wav:
        frames, rate = wav.getnframes(), wav.getframerate()
        if rate <= 0:
            raise ValueError(f"Invalid WAV sample rate: {path}")
        return {"duration_ms": round(frames * 1000 / rate), "codec": "wav", "sample_rate": rate, "channels": wav.getnchannels(), "probe": "stdlib"}


def _probe_mp3(path: Path) -> dict:
    """Approximate duration from Layer III frame count; ffprobe is preferred."""
    data = path.read_bytes()
    rates = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}
    bitrates = {
        3: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
        2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
        0: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
    }
    i = total_samples = frames = sample_rate = 0
    while i + 4 <= len(data):
        h = int.from_bytes(data[i:i + 4], "big")
        if h >> 21 != 0x7FF:
            i += 1
            continue
        version, layer = (h >> 19) & 3, (h >> 17) & 3
        bi, si, padding = (h >> 12) & 15, (h >> 10) & 3, (h >> 9) & 1
        if version == 1 or layer != 1 or bi in (0, 15) or si == 3:
            i += 1
            continue
        rate = rates[version][si]
        frame_len = int((144 if version == 3 else 72) * bitrates[version][bi] * 1000 / rate) + padding
        if frame_len < 4 or i + frame_len > len(data):
            i += 1
            continue
        sample_rate = rate
        total_samples += 1152 if version == 3 else 576
        frames += 1
        i += frame_len
    if frames == 0 or sample_rate == 0:
        raise ValueError(f"Could not find valid MPEG Layer III frames: {path}")
    return {"duration_ms": round(total_samples * 1000 / sample_rate), "codec": "mp3", "sample_rate": sample_rate, "frame_count": frames, "probe": "stdlib-estimate"}


def probe_media(path: Path, *, use_ffprobe: bool = True) -> dict:
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    result: dict = {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    ffprobe = shutil.which("ffprobe") if use_ffprobe else None
    if use_ffprobe and not ffprobe:
        # Opportunistic only: Remotion bundles ffprobe internally; its path is not a public API.
        for parent in (path.parent, *path.parents):
            candidate = parent / "node_modules" / "@remotion" / "compositor-win32-x64-msvc" / "ffprobe.exe"
            if candidate.is_file():
                ffprobe = str(candidate)
                break
    if ffprobe:
        command = [ffprobe, "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,sample_rate,channels,width,height,avg_frame_rate,r_frame_rate,duration", "-of", "json", str(path)]
        payload = json.loads(subprocess.run(command, capture_output=True, text=True, check=True).stdout)
        duration = float(payload.get("format", {}).get("duration", 0))
        streams = payload.get("streams", [])
        video = [s for s in streams if s.get("codec_type") == "video"]
        audio = [s for s in streams if s.get("codec_type") == "audio"]
        result.update({"duration_ms": round(duration * 1000), "streams": streams, "has_video": bool(video), "has_audio": bool(audio), "width": video[0].get("width") if video else None, "height": video[0].get("height") if video else None, "fps": video[0].get("avg_frame_rate") or video[0].get("r_frame_rate") if video else None, "probe": "ffprobe"})
    elif path.suffix.lower() in {".wav", ".mp3"} and not use_ffprobe:
        result.update(_probe_wav(path) if path.suffix.lower() == ".wav" else _probe_mp3(path))
    elif path.suffix.lower() == ".wav":
        result.update(_probe_wav(path))
    elif path.suffix.lower() == ".mp3":
        result.update(_probe_mp3(path))
    else:
        raise RuntimeError("ffprobe is unavailable and stdlib probe does not support this media type")
    if result.get("duration_ms", 0) <= 0:
        raise ValueError(f"Media duration is missing or zero: {path}")
    return result
