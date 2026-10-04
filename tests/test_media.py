import tempfile
import unittest
import wave
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from p103.media import probe_media


class MediaProbeTests(unittest.TestCase):
    def test_probe_wav_duration_and_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "voice.wav"
            with wave.open(str(path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(b"\0\0" * 16000)
            result = probe_media(path, use_ffprobe=False)
        self.assertEqual(result["duration_ms"], 1000)
        self.assertEqual(result["size_bytes"], 32044)
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["probe"], "stdlib")

    def test_probe_real_spike_mp3(self):
        candidates = [ROOT / "spikes" / "canvas-wave-interference" / "final" / "public" / "audio" / "narration.mp3",
                      ROOT / "spikes" / "remotion-textbook-01-sea-breeze" / "final" / "public" / "audio" / "narration.mp3"]
        path = next((p for p in candidates if p.is_file()), None)
        if not path:
            self.skipTest("No spike MP3 fixture available")
        result = probe_media(path, use_ffprobe=False)
        self.assertEqual(result["duration_ms"], 58728)
        self.assertEqual(result["codec"], "mp3")
        self.assertEqual(result["sample_rate"], 24000)
        self.assertEqual(len(result["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
