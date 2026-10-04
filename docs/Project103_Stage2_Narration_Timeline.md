# Project 103 — Stage 2 Narration, Media & Render Infrastructure

**Status:** Stage 2 operational infrastructure slice implemented and tested; live TTS provider success remains dependent on external network/service availability.

## Contract

Each cue keeps three text layers distinct:

- `display_text`: screen-facing notation/caption; may contain symbols and concise labels.
- `narration_text`: canonical spoken transcript for audit/transcript use.
- `tts_text`: exact string sent to a TTS provider.

Timeline cues additionally contain `id`, `scene_id`, `start_ms`, `end_ms`, `tts_cue_text`, and `source`. Times are integer milliseconds from the final rendered audio origin. The JSON is versioned as `p103.narration/v1`; optional source VTT metadata records its path and SHA-256. Cue intervals may overlap slightly: the Canvas wave-interference Spike has 50 ms segmentation overlaps. Import clamps only overlaps within the configured 50 ms tolerance to guarantee non-overlapping display cues; larger overlaps fail. Consumers can derive relative event times via `at_ms(progress)` and `during_ms(start,end)`. Float-second accessors remain as compatibility conveniences.

## Timeline and media adapters

`p103.timeline` provides:

- SRT/VTT timestamp parser (`MM:SS.mmm`, `HH:MM:SS.mmm`, comma or dot milliseconds; returns integer milliseconds);
- VTT/SRT cue import and optional separately supplied display-text JSON array;
- normalization: stable cue ordering, small-overlap clamp, larger-overlap rejection;
- normalized JSON output `audio/timeline.json`;
- SRT output `audio/subtitles.srt`, CRLF UTF-8 without BOM, choosing a declared text layer;
- Remotion-facing half-open cue frame map `audio/remotion-frames.json` using floor(start)/ceil(end);
- validation for cue order, positive duration, all three text fields, timeline duration and frame collapse;
- stdlib-first WAV/MP3 media identity and duration probe, with optional ffprobe when present;
- Remotion JSON + AUTO-GENERATED TypeScript timeline, duration derived from probed audio and anchors expressed as segment ID + offset_ms.
- Run-local media registration and SHA-256 revalidation before rendering. Inputs are copied under `runs/<run-id>/audio/` so outside paths cannot change unnoticed.
- Exact normalized transcript coverage check with sentence-level time mapping (`align_tts_cues`); character-proportional mapping is used only when provider cue boundaries cross narration segment boundaries, never presented as word alignment.
- `p103.tts` adapter for installed `edge-tts` CLI: writes MP3 and provider cue VTT, records engine/voice/rate/hash/duration. It is a live network adapter, not an offline guarantee.
- ffprobe metadata verification (audio/video streams, duration, dimensions, frame rate) plus evenly-spaced FFmpeg keyframes and a dependency-free PNG contact sheet.
- A configurable Remotion scene-slot shell anchored by `segment_id + offset_ms`, with bounded `duration_ms` and `cut`/`fade` transition option. The appearance is a minimal scaffold intended for later authorable scene components.

This imports provider sentence timestamps but does not claim phoneme/word forced alignment or ASR.

## CLI

From project root:

```powershell
python p103_cli.py --workspace . timeline <run-id> path\to\narration.vtt --scene interference --fps 30 --audio path\to\narration.mp3
python p103_cli.py --workspace . probe path\to\narration.mp3
python p103_cli.py --workspace . tts <run-id> path\to\tts-input.txt --voice zh-CN-XiaoxiaoNeural
python p103_cli.py --workspace . align-tts <run-id>
python p103_cli.py --workspace . verify-media <run-id>
python p103_cli.py --workspace . remotion-consumer <run-id> --scene-spec path\to\scenes.json
python p103_cli.py --workspace . render <run-id>
python p103_cli.py --workspace . video-qa <run-id>
python p103_cli.py --workspace . finalize <run-id>
```

For separate display strings:

```powershell
python p103_cli.py --workspace . timeline <run-id> path\to\narration.vtt --display-texts path\to\display-lines.json
```

The JSON file must contain one display string for each subtitle cue, in cue order. Without it, imported speech populates all three text layers. This is a practical compatibility default, not a claim that the layers are conceptually interchangeable.

Optional anchors are a JSON array such as `[{"segment_id":"interference-line-07","offset_ms":1200}]`; the generated TypeScript exports `FPS`, `DURATION_IN_FRAMES`, `CUES`, and `SEGMENT_ANCHORS`. Anchors beyond a shortened segment clamp to its end and mark `clamped: true`. `align-tts` checks the provider VTT's normalized concatenated cue text against every manifest `tts_text`, maps its sentence-level timestamps to segment ranges and registers the VTT hash. It does not establish per-word timing.

## Verification

```powershell
python -m unittest discover -s tests -v
```

The suite covers Stage 1 runtime, timestamp/subtitle normalization, media probes, segment anchors and generated Remotion output. The actual Canvas wave-interference MP3 probes to 58,728 ms (stdlib MP3 frame count; independently verified equal to the installed Remotion ffprobe); its VTT ends at 58,660 ms. With `--audio`, Remotion duration therefore becomes 1,762 frames at 30fps, not the VTT-only 1,760. Integration outputs land in the run's `audio/` and `src/generated/` directories.

`scenes.json` is an array of entries such as `{"id":"diagram-1","segment_id":"interference-line-07","offset_ms":200,"duration_ms":1200,"title":"Wave","color":"#17324d","transition":"fade"}`. A scene must fit wholly within its anchored narration segment.

## Remotion consumer smoke test

For an existing run with `audio/timeline.json` and generated `src/generated/timeline.ts`:

```powershell
python p103_cli.py --workspace . remotion-consumer <run-id>
```

This writes a run-local audio+subtitle consumer and replaces that run's `src/Root.tsx` / `src/index.ts` with a composition driven by generated `FPS` and `DURATION_IN_FRAMES`. Optional scene slots are supplied in a JSON array and remain bounded by cue timing. Existing spikes are not modified. Copy/reference the run-local audio into Remotion's `public/audio/` directory under the requested `--audio-static-path` before invoking render.

Real Canvas fixture verification: isolated copy under `runs/architecture-smoke/` passed `npm run typecheck`; Remotion reported `P103TimelineConsumer 30 1920x1080 1762 (58.73 sec)` and rendered `out/timeline-consumer-smoke.mp4` (2,830,090 bytes). A still frame was also rendered at frame 800. The demo visually exercises subtitle selection from generated half-open cue ranges and audio playback.

## Canonical artifacts and scope

The CLI render flow writes `attempt-1/attempt-1.mp4`; render fails closed if registered audio/subtitle hashes no longer match. `video-qa` writes `verification/report.json`, `verification/keyframes/`, and `verification/contact-sheet.png`; `finalize` checks that report and the current MP4 hash before copying to `final/final.mp4`. ffprobe verification expects 1920x1080/30fps by default and requires both audio and video streams. This exact path was run end to end against the Canvas wave-interference fixture: 12 cues, 58,728ms narration, 1,762 frames, render passed, QA passed, and `final/final.mp4` was promoted. Resulting attempt was 2,815,869 bytes and 1920×1080 H.264 + AAC at 30fps.

The project environment has no standalone ffmpeg/ffprobe on PATH. Media probing and rendering currently use Remotion's bundled ffprobe/Remotion CLI when discoverable. Its ffmpeg is a restricted build without common montage filters, so contact-sheet composition uses a small dependency-free PNG reader/writer. Outside this environment, install full ffmpeg/ffprobe on PATH for a stable, supported deployment. The edge-tts adapter is implemented but a live service call was not attempted during this verification; provider/network success is not claimed.

Remaining boundaries: live edge-tts invocation depends on network/provider availability; provider sentence cues are not word/phoneme alignment. The scene shell is a minimal configurable scaffold, not Stage 4 lesson/storyboard generation or Stage 5 visual review. Those remain out of Stage 2.
