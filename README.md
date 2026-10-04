# Project 103 — LLM-native Teaching Media Engine

Project 103 provides shared production infrastructure for two adjacent outputs:

- Interactive MathViz: strong-model-generated interactive HTML/SVG/Canvas/Three.js with browser execution and thin verification.
- LessonVideo: source → teaching brief → storyboard → renderer output → Remotion/TTS/subtitles → verified MP4.

## Stage 1 core runtime

The first infrastructure slice is implemented in `p103/` and documented in [`docs/Project103_Stage1_Core_Runtime.md`](docs/Project103_Stage1_Core_Runtime.md).

```powershell
python p103_cli.py --workspace . video path\to\source.md
python p103_cli.py --workspace . status <run-id>
python -m unittest discover -s tests -v
```

Stage 1 manages runs, artifacts, state transitions, logs, and the one-repair limit. Stage 2 adds VTT/SRT narration timelines, a live edge-tts CLI adapter with provider cue ingestion, exact normalized text-coverage checks, run-local media hash verification, ffprobe stream/resolution/FPS checks, FFmpeg keyframes, contact sheets, bounded multi-scene Remotion slots, and attempt-1 → verification → final artifact paths. See [`docs/Project103_Stage2_Narration_Timeline.md`](docs/Project103_Stage2_Narration_Timeline.md). Provider calls still require external network/service availability; no forced word alignment or lesson/storyboard generator is claimed. Existing spikes remain unchanged as integration fixtures.
