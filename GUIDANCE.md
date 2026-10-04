# Project 103 — Confirmed Guidance

## Status

This file indexes the confirmed guidance documents for the project production system.

## G-001 — MathViz Geometry LLM-Native Phase Summary

- **Status:** CONFIRMED
- **Confirmed by:** Project owner
- **Confirmed on:** 2026-10-03
- **Document:** [`docs/MathViz_Geometry_LLM_Native_Phase_Summary_2026-10-03.md`](docs/MathViz_Geometry_LLM_Native_Phase_Summary_2026-10-03.md)
- **Role:** First confirmed guiding document for the Project 103 production system.

### Governing direction

1. **Primary path for suitable 2D dynamic geometry:** strong-model-native generation of self-contained HTML + SVG + vanilla JavaScript.
2. **Input:** problem plus optional teaching intent; teaching intent is a high-level directing language, not a low-level problem-type capability.
3. **System responsibility:** browser execution, runtime/error checks, numerical parameter sweeps, critical spot checks, screenshot review, teaching-leak review, and at most one concentrated repair.
4. **Predefined capability/parser/Scene IR:** no longer the primary geometry generation path.
5. **Existing strict MathViz infrastructure:** retain as optional helper, verifier, or fallback; do not delete it and do not force every problem through it.
6. **Selection principle:** prioritize problems where continuous interaction reveals structure that static text or diagrams do not show clearly; do not animate everything merely because it is possible.
7. **Boundary:** this is a directional phase conclusion based on four successful exploratory spikes, not a proof of full problem-type coverage.

## G-002 — LLM-Native MathViz + LessonVideo Production Principles

- **Status:** CONFIRMED
- **Confirmed by:** Project owner direction and accepted phase conclusion
- **Confirmed on:** 2026-10-03
- **Document:** [`docs/Project103_Working_Principles_2026-10-03.md`](Project103_Working_Principles_2026-10-03.md)
- **Source:** `Project103_LLM_Native_MathViz_LessonVideo_Phase_Conclusion_2026-10-03.md`
- **Role:** Working principles and normal-production method for both Project 103 product lines.

### Governing direction

1. Project 103 has two adjacent LLM-native lines: Interactive MathViz and LessonVideo.
2. Strong models own high-level understanding, teaching design, visual design and program generation; the system owns execution, rendering, thin verification, error capture and at most one concentrated repair.
3. LessonVideo must use fixed preprocessing for non-trivial textbook material: `source.md → lesson-brief.md → storyboard.md → implementation → TTS/subtitles → first complete MP4 → review → at most one repair → final MP4`.
4. Lesson Brief is a real teaching transformation layer, not a summary. It must state the core objective, must-teach content, secondary/compressible content, omissions and reasons, misconception risks, reorganization and visual division of labor.
5. Choose TEXT_CARD, FORMULA, COMPARE, SVG, Canvas, Manim, PROCESS and SUMMARY by knowledge/visual expression type. **Animate only when motion adds explanatory value; keep definitions, comparisons and summaries quiet when appropriate.**
6. Remotion is the LessonVideo total assembly layer for scenes, audio, subtitles, timing and final rendering.
7. Existing capability/parser/strict infrastructure remains optional helper, verifier or fallback, not a mandatory primary path.
8. Sol is currently the primary creative/director model; Luna or cheaper models may assist with mechanical, fixed-plan and batch tasks but are not presumed sufficient as primary creative models.
9. Long textbook chapters should be architected and segmented before segment production and final assembly.
10. Every spike maintains auditable `usage.json`; exact provider token fields remain null when unavailable, with character counts recorded as a clearly non-token fallback. Local rendering and TTS are not LLM tokens.
11. These are phase-bounded working principles, not claims of full coverage or zero-error generation; new experiments must record boundaries, failures, repair cost and evidence.

## Stage 1 implementation status — Core Runtime

- **Status:** IMPLEMENTED (2026-10-04)
- **Document:** [`docs/Project103_Stage1_Core_Runtime.md`](docs/Project103_Stage1_Core_Runtime.md)
- **Scope:** run workspace, minimal project/run contracts, state machine, safe artifact paths, event log, resume/status CLI, and enforced maximum-one repair counter.
- **Boundary:** no model orchestration, TTS, renderer adapters, or complete media pipeline yet.

## Stage 2 implementation status — Narration, Media & Render Infrastructure

- **Status:** IMPLEMENTED (2026-10-04), with external TTS invocation dependent on network/provider availability.
- **Document:** [`docs/Project103_Stage2_Narration_Timeline.md`](docs/Project103_Stage2_Narration_Timeline.md)
- **Scope:** versioned `p103.narration/v1`; integer-ms VTT/SRT; 50ms overlap clamp; text layers and exact normalized transcript coverage; edge-tts CLI adapter and sentence cue mapping; run-local audio/subtitle hash registration/recheck; ffprobe stream/duration/FPS/dimensions checks; FFmpeg keyframes and contact sheet; bounded configurable Remotion scene slots; render `attempt-1/attempt-1.mp4` → `verification/report.json`/keyframes/contact-sheet → hash-gated `final/final.mp4`.
- **Verification:** all 31 Project 103 tests passed, including CLI sentence cue alignment, media hash mutation rejection, strict Remotion package typecheck and actual 1920x1080 MP4 render → QA → final promotion. Existing Remotion spike files remain unchanged.
- **Boundary:** no word/phoneme forced alignment, full lesson/storyboard generation or Stage 5 visual review; Remotion-bundled FFmpeg is a restricted internal build and full deployment should use supported system ffmpeg/ffprobe.

## Production doctrine

```text
Interactive MathViz:
Problem + teaching intent
→ strong model
→ self-contained HTML/SVG/JS
→ browser
→ thin verification
→ at most one repair
→ interactive page

LessonVideo:
Textbook source
→ teaching preprocessing
→ Lesson Brief
→ Storyboard
→ visual-form selection
→ Remotion assembly
→ TTS/subtitles
→ thin review
→ at most one repair
→ MP4
```

In ambiguity, the full documents linked above are authoritative; this index is not a substitute for them.
