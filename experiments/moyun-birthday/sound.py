"""Generate reproducible quiet paper/ink Foley (no music, no network or model)."""
from array import array
import math
from pathlib import Path
import random
import wave

RATE = 32000
DURATION = 12
EVENTS = ((0.45, 0.31, 0.16), (2.2, 0.24, 0.07), (3.0, 0.28, 0.06),
          (4.1, 0.36, 0.07), (5.3, 0.34, 0.07), (6.7, 0.34, 0.05),
          (8.0, 0.4, 0.08), (9.4, 0.32, 0.07))


def create(out: Path) -> None:
    rng = random.Random(1032026)
    pcm = array("h")
    low = 0.0
    for i in range(RATE * DURATION):
        t = i / RATE
        white = rng.uniform(-1.0, 1.0)
        low = low * 0.82 + white * 0.18
        # Soft, continuous paper fibre movement, fading around the final title.
        paper = (white * 0.56 + low * 0.44) * (0.019 if t < 9.8 else 0.006)
        wet = 0.0
        for onset, length, gain in EVENTS:
            u = t - onset
            if 0 <= u < length:
                e = math.sin(math.pi * u / length) ** 2
                wet += (0.67 * low + 0.33 * white) * e * gain
        # A soft liquid plop when the first ink drop touches paper.
        u = t - 0.52
        plop = math.sin(2 * math.pi * (119 - 30 * u) * u) * math.exp(-19 * u) * 0.16 if 0 <= u < 0.4 else 0
        value = max(-0.94, min(0.94, paper + wet + plop))
        pcm.append(int(value * 32767))
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(pcm.tobytes())


if __name__ == "__main__":
    create(Path(__file__).resolve().parent / "paper_ink.wav")
