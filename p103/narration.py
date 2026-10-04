"""Narration/TTS text coverage checks for imported cue timelines."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    segment_id: str | None
    detail: str

    def to_dict(self) -> dict:
        return {"code": self.code, "severity": self.severity, "segment_id": self.segment_id, "detail": self.detail}


def normalize_speech(text: str) -> str:
    """Normalize whitespace, punctuation and VTT tags for coverage comparison."""
    text = re.sub(r"<[^>]*>", "", text)
    chars = []
    for char in unicodedata.normalize("NFKC", text).casefold():
        category = unicodedata.category(char)
        if category.startswith("P") or category.startswith("Z") or char.isspace():
            continue
        chars.append(char)
    return "".join(chars)


def validate_text_coverage(narration_segments: Iterable[dict], cue_texts: Iterable[str]) -> list[Finding]:
    expected_items = list(narration_segments)
    actual_items = list(cue_texts)
    expected = normalize_speech("".join(str(item.get("tts_text", "")) for item in expected_items))
    actual = normalize_speech("".join(str(text) for text in actual_items))
    if not expected:
        return [Finding("E_NARR_EMPTY", "error", None, "No TTS text supplied")]
    if expected == actual:
        return []
    # Find first differing normalized position; do not attempt unsafe auto-correction.
    limit = min(len(expected), len(actual))
    mismatch = next((i for i in range(limit) if expected[i] != actual[i]), limit)
    return [Finding(
        "E_NARR_TEXT_MISMATCH", "error", None,
        f"Normalized TTS/cue coverage differs at char {mismatch}; expected_length={len(expected)}, cue_length={len(actual)}",
    )]
