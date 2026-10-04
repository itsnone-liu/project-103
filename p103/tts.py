"""Small subprocess adapter for installed edge-tts CLI.

External network/service availability remains an environment prerequisite; this
module records exact TTS input plus provider-returned subtitles without claiming
word-level forced alignment.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .media import probe_media


def generate_edge_tts(text: str, audio_path: Path, subtitle_path: Path, *, voice: str = "zh-CN-XiaoxiaoNeural", rate: str = "+0%") -> dict:
    if not text.strip():
        raise ValueError("TTS text must not be empty")
    executable = shutil.which("edge-tts")
    if not executable:
        raise RuntimeError("edge-tts CLI not found; install the provider adapter executable")
    audio_path, subtitle_path = Path(audio_path), Path(subtitle_path)
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    subtitle_path.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "--text", text, "--voice", voice, "--rate", rate, "--write-media", str(audio_path), "--write-subtitles", str(subtitle_path)]
    subprocess.run(command, check=True)
    if not audio_path.is_file() or not subtitle_path.is_file():
        raise RuntimeError("edge-tts returned without both audio and subtitles")
    probe = probe_media(audio_path)
    return {"engine": "edge-tts", "voice": voice, "rate": rate, "audio": str(audio_path), "subtitles": str(subtitle_path), "audio_duration_ms": probe["duration_ms"], "sha256": probe["sha256"], "probe": probe["probe"]}
