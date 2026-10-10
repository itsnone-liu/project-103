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

## [LRN-20261009-MOYUN] correction

**Logged**: 2026-10-09
**Priority**: medium
**Status**: resolved
**Area**: docs

### Summary
A technically correct literal blessing and paper-ink Foley did not match the user's final visual/pacing preference: the comma felt extra, and qin sounded preferable for this ancient-style birthday piece.

### Details
The user first specified 「岁岁欢喜，年年胜意」 and paper-ink sound effects; after reviewing both MP4 variants, they said: 「效果不错。文字多了逗号，音效看来还是琴音更好。不用改了，沉淀。」 Under this condition, copying punctuation faithfully did not guarantee preferred on-screen typography, and literal requested Foley did not guarantee the preferred final sound. This is not a request to change the accepted outputs. The code-animation render, legible blessing, and sound delivery themselves worked, so preserve them as the salvageable part.

### Suggested Action
For similar ancient-style greeting videos, explicitly confirm *visible* punctuation separately from semantic wording and offer a short sound preview comparing subtle qin with paper-ink Foley; only change a released cut when the user asks. Keep this a project-scoped candidate rather than a universal style mandate.

### Metadata
- Source: user_feedback
- Related Files: experiments/moyun-birthday/RESULT.md, knowledge/success-cases/PROJECT-moyun-birthday-user-review-2026-10.md
- Tags: moyun, typography, audio, review, user-feedback

---
