"""Registration and integrity verification for timeline media inputs."""
from __future__ import annotations

import json
from pathlib import Path

from .media import probe_media, sha256_file


def _resolve_artifact(run_root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = run_root / path
    resolved = path.resolve()
    root = run_root.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Registered media path escapes run root: {value}")
    return resolved


def register_media(run_root: Path, timeline: dict) -> list[dict]:
    """Canonicalize run-local asset references and register stable file identity."""
    root = Path(run_root).resolve()
    records = []
    for key in ("tts", "vtt", "tts_cues"):
        descriptor = timeline.get(key)
        if not descriptor:
            continue
        path = _resolve_artifact(root, descriptor["path"])
        if not path.is_file():
            raise FileNotFoundError(f"Missing {key} asset: {path}")
        actual_sha = sha256_file(path)
        if descriptor.get("sha256") and descriptor["sha256"] != actual_sha:
            raise ValueError(f"E_MEDIA_HASH_MISMATCH: {key} hash differs from manifest")
        descriptor["path"] = str(path.relative_to(root)).replace("\\", "/")
        descriptor["sha256"] = actual_sha
        if key == "tts" and path.suffix.lower() in {".wav", ".mp3"}:
            probe = probe_media(path)
            descriptor["audio_duration_ms"] = probe["duration_ms"]
            descriptor["probe"] = probe["probe"]
            descriptor["size_bytes"] = probe["size_bytes"]
            records.append(probe)
        else:
            descriptor["size_bytes"] = path.stat().st_size
    return records


def verify_registered_media(run_root: Path, timeline: dict) -> list[dict]:
    """Fail closed if any registered file is missing or its bytes changed."""
    root = Path(run_root)
    verified = []
    for key in ("tts", "vtt", "tts_cues"):
        descriptor = timeline.get(key)
        if not descriptor:
            continue
        path = _resolve_artifact(root, descriptor["path"])
        if not path.is_file():
            raise FileNotFoundError(f"E_MEDIA_MISSING: registered {key} missing: {path}")
        actual = sha256_file(path)
        if actual != descriptor.get("sha256"):
            raise ValueError(f"E_MEDIA_HASH_MISMATCH: registered {key} bytes changed")
        verified.append({"kind": key, "path": descriptor["path"], "sha256": actual, "size_bytes": path.stat().st_size})
    return verified


def read_manifest(run_root: Path) -> dict:
    path = Path(run_root) / "audio" / "timeline.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("timeline manifest must be a JSON object")
    return value
