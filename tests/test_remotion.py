import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from p103.remotion import generate_remotion_timeline, resolve_anchor
from p103.timeline import SCHEMA_VERSION, NarrationLine, Timeline


class RemotionTimelineTests(unittest.TestCase):
    def fixture_timeline(self):
        cues = (
            NarrationLine("seg-a", "s1", "A", "spoken A", "tts A", 1000, 3000),
            NarrationLine("seg-b", "s2", "B", "spoken B", "tts B", 3000, 5000),
        )
        return Timeline(SCHEMA_VERSION, 5000, cues, "fixture", fps=30)

    def test_segment_anchor_rebases_and_clamps_after_rerender(self):
        timeline = self.fixture_timeline()
        self.assertEqual(resolve_anchor(timeline, "seg-b", 500), {"segment_id": "seg-b", "offset_ms": 500, "time_ms": 3500, "clamped": False})
        shortened = Timeline(SCHEMA_VERSION, 3200, (NarrationLine("seg-b", "s2", "B", "spoken", "tts", 2000, 3200),), "fixture")
        self.assertTrue(resolve_anchor(shortened, "seg-b", 1500)["clamped"])

    def test_generated_json_and_typescript(self):
        timeline = self.fixture_timeline()
        with tempfile.TemporaryDirectory() as tmp:
            data = generate_remotion_timeline(timeline, Path(tmp), anchors=[{"segment_id": "seg-b", "offset_ms": 500}], audio_duration_ms=5200)
            ts = (Path(tmp) / "timeline.ts").read_text(encoding="utf-8")
        self.assertEqual(data["durationInFrames"], 156)
        self.assertIn("AUTO-GENERATED", ts)
        self.assertIn("export const DURATION_IN_FRAMES = 156;", ts)
        self.assertEqual(data["anchors"][0]["time_ms"], 3500)

    def test_unknown_anchor_fails(self):
        with self.assertRaisesRegex(ValueError, "Unknown narration segment"):
            resolve_anchor(self.fixture_timeline(), "missing", 100)


if __name__ == "__main__":
    unittest.main()
