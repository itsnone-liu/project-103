# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20261004-103] knowledge_gap

**Logged**: 2026-10-04
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Remotion's bundled Windows ffmpeg is a restricted build and cannot be assumed to provide ordinary montage filters.

### Details
An initial contact-sheet implementation used `pad`, `tile`, `hstack` and `color`; runtime inspection showed the bundled ffmpeg omitted these filters. In this environment keyframe extraction still worked, while PNG contact sheet generation was made dependency-free in Python. On deployments with full system ffmpeg, a filter-based approach remains suitable.

### Suggested Action
Use system ffmpeg/ffprobe for supported deployments; if relying on Remotion-bundled binaries, feature-detect capabilities and keep the pure Python PNG fallback tested.

### Metadata
- Source: error
- Related Files: p103/video_qa.py, tests/test_video_qa.py
- Tags: ffmpeg, remotion, contact-sheet, windows

---
