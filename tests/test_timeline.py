import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from p103.timeline import (
    NarrationLine, SCHEMA_VERSION, Timeline, generate_srt, import_subtitles,
    normalize_cues, parse_cues, parse_timestamp, remotion_frames, validate_timeline,
)
from p103.remotion import generate_remotion_timeline, resolve_anchor


class TimelineTests(unittest.TestCase):
    def test_timestamp_uses_integer_milliseconds_and_accepts_short_form(self):
        self.assertEqual(parse_timestamp("00:01:02,345"), 62_345)
        self.assertEqual(parse_timestamp("01:02.345"), 62_345)
        self.assertEqual(parse_timestamp("01:02:03.004"), 3_723_004)
        with self.assertRaises(ValueError):
            parse_timestamp("00:60:00.000")

    def test_parse_headerless_vtt_bom_crlf_settings_and_tags(self):
        text = "\ufeff1\r\n00:00.000 --> 00:01.250 align:start\r\n<v Narrator>hello</v>\r\n"
        cues, fmt = parse_cues(text)
        self.assertEqual(fmt, "srt")  # format inference needs the optional hint for headerless VTT
        cues, fmt = parse_cues(text, source_format="vtt")
        self.assertEqual(fmt, "vtt")
        self.assertEqual(cues, [(0, 1250, "hello")])

    def test_import_realistic_vtt_clamps_50ms_overlap(self):
        text = """WEBVTT

1
00:00:00,100 --> 00:00:05,853
第一句。

2
00:00:05,803 --> 00:00:09,387
第二句。
"""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.vtt"
            source.write_text(text, encoding="utf-8")
            timeline = import_subtitles(source, display_texts=["第一行", "第二行"])
        self.assertEqual(timeline.source_format, "vtt")
        self.assertEqual(timeline.version, SCHEMA_VERSION)
        self.assertEqual(timeline.vtt["sha256"].__len__(), 64)
        self.assertEqual(timeline.cues[0].end_ms, 5803)
        self.assertEqual(timeline.cues[1].start_ms, 5803)
        self.assertEqual(timeline.cues[1].display_text, "第二行")
        self.assertEqual(timeline.cues[1].tts_cue_text, "第二句。")
        self.assertEqual(validate_timeline(timeline, frame_rate=30), [])

    def test_normalization_rejects_overlap_above_tolerance(self):
        with self.assertRaisesRegex(ValueError, "E_NARR_OVERLAP"):
            normalize_cues([(0, 2000, "a"), (1900, 3000, "b")])

    def test_import_generated_wave_spike_vtt(self):
        source = ROOT / "spikes" / "canvas-wave-interference" / "final" / "public" / "audio" / "narration.vtt"
        timeline = import_subtitles(source, scene_id="interference")
        self.assertEqual(len(timeline.cues), 12)
        self.assertEqual(timeline.duration_ms, 58_660)
        frames = remotion_frames(timeline, 30)
        self.assertEqual(frames[0]["startFrame"], 3)
        self.assertEqual(frames[-1]["endFrame"], 1760)
        anchored = resolve_anchor(timeline, "interference-line-07", 1000)
        self.assertEqual(anchored["time_ms"], timeline.cues[6].start_ms + 1000)
        with tempfile.TemporaryDirectory() as tmp:
            generated = generate_remotion_timeline(timeline, Path(tmp), anchors=[{"segment_id": "interference-line-07", "offset_ms": 1000}], audio_duration_ms=58728)
            source = (Path(tmp) / "timeline.ts").read_text(encoding="utf-8")
        self.assertEqual(generated["durationInFrames"], 1762)
        self.assertIn("DURATION_IN_FRAMES = 1762", source)

    def test_floor_start_ceil_end_frame_mapping(self):
        timeline = Timeline(SCHEMA_VERSION, 1001, (NarrationLine("l1", "s1", "d", "n", "t", 101, 1001),), "test")
        self.assertEqual(remotion_frames(timeline, 30), [{"id": "l1", "startFrame": 3, "endFrame": 31}])

    def test_at_and_during_are_relative_to_line(self):
        cue = NarrationLine("l1", "s1", "d", "n", "t", 10_000, 14_000)
        self.assertEqual(cue.at_ms(0.25), 11_000)
        self.assertEqual(cue.during_ms(0.25, 0.75), (11_000, 13_000))
        with self.assertRaises(ValueError):
            cue.at_ms(1.1)

    def test_srt_round_trip_no_bom_crlf_and_choose_text_layer(self):
        with tempfile.TemporaryDirectory() as tmp:
            vtt = Path(tmp) / "in.vtt"
            vtt.write_text("WEBVTT\n\n00:00.000 --> 00:02.500\nSpoken text\n", encoding="utf-8")
            timeline = import_subtitles(vtt, display_texts=["Displayed text"])
            out = Path(tmp) / "subtitles.srt"
            generate_srt(timeline, out, text_layer="display_text")
            raw = out.read_bytes()
            result = raw.decode("utf-8")
            round_trip = import_subtitles(out)
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertIn("\r\n", result)
        self.assertIn("00:00:00,000 --> 00:00:02,500", result)
        self.assertIn("Displayed text", result)
        self.assertEqual(round_trip.cues[0].start_ms, timeline.cues[0].start_ms)

    def test_rejects_bad_intervals_and_mismatched_display_layer(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.srt"
            bad.write_text("1\n00:00:02,000 --> 00:00:01,000\nBad\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "end must be after start"):
                import_subtitles(bad)
            good = Path(tmp) / "good.srt"
            good.write_text("1\n00:00:00,000 --> 00:00:01,000\nGood\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "count"):
                import_subtitles(good, display_texts=["a", "b"])

    def test_empty_text_layers_fail_validation(self):
        cue = NarrationLine("l1", "s1", "", "spoken", "spoken", 0, 1)
        timeline = Timeline(SCHEMA_VERSION, 1, (cue,), "fixture")
        self.assertTrue(any("display_text is empty" in e for e in validate_timeline(timeline)))


if __name__ == "__main__":
    unittest.main()
