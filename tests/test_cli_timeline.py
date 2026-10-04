import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from p103.cli import main
from p103.core import create_run


class TimelineCliTests(unittest.TestCase):
    def test_timeline_cli_registers_audio_and_writes_remotion_ts(self):
        source = ROOT / "spikes" / "canvas-wave-interference" / "final" / "public" / "audio" / "narration.vtt"
        audio = ROOT / "spikes" / "canvas-wave-interference" / "final" / "public" / "audio" / "narration.mp3"
        if not source.is_file() or not audio.is_file():
            self.skipTest("wave spike VTT/MP3 unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            run = create_run(workspace, "video", source, run_id="timeline-cli")
            result = main(["--workspace", str(workspace), "timeline", run.run_id, str(source), "--audio", str(audio), "--scene", "interference", "--fps", "30"])
            self.assertEqual(result, 0)
            manifest = json.loads((run.root / "audio" / "timeline.json").read_text(encoding="utf-8"))
            generated = (run.root / "src" / "generated" / "timeline.ts").read_text(encoding="utf-8")
            frames = json.loads((run.root / "audio" / "remotion-frames.json").read_text(encoding="utf-8"))
            public_audio = run.root / "public" / "audio" / "narration.mp3"
            self.assertTrue(public_audio.is_file())
        self.assertEqual(manifest["tts"]["audio_duration_ms"], 58728)
        self.assertEqual(len(manifest["tts"]["sha256"]), 64)
        self.assertEqual(frames["durationInFrames"], 1762)
        self.assertIn("DURATION_IN_FRAMES = 1762", generated)


if __name__ == "__main__":
    unittest.main()
