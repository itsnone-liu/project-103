# Errors

Command failures and integration errors.

---

## [ERR-20261004-001] edge-tts flags and package workdir

**Logged**: 2026-10-04T01:30:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
Canvas spike TTS/probe/typecheck chain initially used the wrong edge-tts option, then selected the repository root package and assumed ffprobe was on PATH.

### Error
`edge-tts` required `--file`; `ffprobe` was not recognized; `npm run typecheck` ran the root package because the command workdir was the spike parent rather than `attempt-1`.

### Context
Project 103 Canvas wave-interference spike.

### Suggested Fix
Use `edge-tts --file`, run npm inside the exact Remotion package directory, and resolve an installed ffprobe binary explicitly when PATH lacks it.

### Metadata
- Reproducible: yes
- Related Files: spikes/canvas-wave-interference/narration.txt
- See Also: ERR-20261003-001

### Resolution
- **Resolved**: 2026-10-04T01:31:00+08:00
- **Notes**: Split generation, probing and package-local typecheck into correctly anchored commands.

---

## [ERR-20261003-001] edge-tts relative working directory

**Logged**: 2026-10-03T15:30:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
Edge TTS failed twice because the narration input and output directory were resolved relative to the wrong working directory.

### Error
`FileNotFoundError` for narration.txt, then for the output audio directory.

### Context
The project workdir was `project/103`, while the first command assumed the spike directory; the second corrected input path but did not create `attempt-1/public/audio`.

### Suggested Fix
Before Edge TTS, create the output directory explicitly and make all paths relative to the declared `workdir`.

### Metadata
- Reproducible: yes
- Related Files: spikes/remotion-textbook-finance-inventory-turnover/narration.txt

### Resolution
- **Resolved**: 2026-10-03T15:32:00+08:00
- **Notes**: Created the audio directory and reran with paths anchored to project/103.

---

## [ERR-20261004-103] Remotion bundled ffmpeg filters

**Logged**: 2026-10-04
**Priority**: medium
**Status**: resolved
**Area**: tests

### Summary
Remotion's bundled FFmpeg did not support assumed contact-sheet filters.

### Error
The actual executable reported missing `pad`, `tile`, `hstack`, and `color` filters; FFmpeg rejected the generated graph.

### Context
Video QA integration using Remotion's internal Windows compositor package, which is not a general full FFmpeg build.

### Suggested Fix
Use actual tested capabilities only; this project now extracts frames with FFmpeg and composes PNG contact sheets with a standard-library codec. For other deployments, prefer full system FFmpeg/ffprobe.

### Metadata
- Reproducible: yes
- Related Files: p103/video_qa.py, tests/test_video_qa.py

---

## [ERR-20261004-104] capital-turnover setup path errors

**Logged**: 2026-10-04
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
The new video setup repeated two avoidable path mistakes: edge-tts was invoked before its output directory existed, and reference package files were copied using a path relative to the spike parent while the command ran in `final`.

### Error
`FileNotFoundError` for `final/public/audio/narration.mp3`; then `Copy-Item` could not locate the inventory-turnover package and `npm install` fell through to the monorepo workspace package.

### Context
- Edge TTS workdir: capital-turnover spike root.
- Package-copy workdir: capital-turnover `final` directory.

### Suggested Fix
Pre-create TTS output directories. Before copying sibling spike assets, count path levels from the declared command workdir; verify local `package.json` exists before running npm.

### Metadata
- Reproducible: yes
- Related Files: spikes/remotion-textbook-finance-capital-turnover
- See Also: ERR-20261003-001, ERR-20261004-001

### Resolution
- **Resolved**: 2026-10-04
- **Notes**: Created the directory, regenerated TTS, copied package files via `..\..\remotion-textbook-finance-inventory-turnover\final`, and installed locally.

---
