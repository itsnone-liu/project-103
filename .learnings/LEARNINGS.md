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

## [LRN-20261028-APP] best_practice

**Logged**: 2026-10-28
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
When changing TTS-only normalization while preserving subtitle text, invalidate sentence-level voice caches as well as timing and render artifacts.

### Details
In Project 103, `audio.py` reuses `audio/voice/<title>/sent_NN.wav` when `sent_NN.txt` still equals the original storyboard sentence. Deleting timing, narration, code, and final output alone regenerated timing but reused the old synthesized speech. For a synthesis-only replacement such as `App` → `A P P`, clear the affected `audio/voice/<title>/` directories, then remove timing/narration and output artifacts to force genuine resynthesis and downstream regeneration. Storyboard/decision can remain when unchanged.

### Suggested Action
Before rerunning TTS after synthesis-input normalization changes, inspect cache reuse logic and clear each affected segment's per-sentence audio cache.

### Metadata
- Source: error
- Related Files: `audio.py`, `_mui_batch1.py`
- Tags: project-103, tts-cache, normalization
- Pattern-Key: p103.tts-normalization-cache-invalidation
- Recurrence-Count: 1
- First-Seen: 2026-10-28
- Last-Seen: 2026-10-28

---

## [LRN-20261028-COSY-SSML] correction

**Logged**: 2026-10-28
**Priority**: high
**Status**: resolved_user_approved
**Area**: backend

### Summary
Do not assume letter separators survive CosyVoice normalization or are silent; spaced letters collapsed to App, while hyphens were spoken as “杠”.

### Details
User's target is the English letter names A, P, P, with no audible separators and visible subtitles unchanged as “App”. In the deployed cosyvoice-v2 path, `App` and `A P P` produced byte-identical WAV for the same sentence; `A-P-P` was explicitly heard by the user as “A杠P杠P”. Official CosyVoice SSML docs support `<say-as interpret-as="characters">APP</say-as>` inside `<speak>`. A short sample was generated and exposed for user listening before replacing further final audio. Duration/SSML syntax alone do not prove subjective pronunciation; wait for the user's sample review.

### Suggested Action
For future letter spelling, use a character-reading SSML tag only after an isolated exact-sentence preview is approved; don't publish a full rerender based only on separator/pause inference.

### Metadata
- Source: user_correction
- Related Files: `audio.py`, `cache/app_pron_test/_ssml_letters_probe.py`, `_serve_t1.py`
- Tags: project-103, cosyvoice, pronunciation, ssml

---

## [LRN-20261126-TS-RELAY] correction

**Logged**: 2026-11-26T17:30:00+08:00
**Priority**: high
**Status**: in_progress
**Area**: infra

### Summary
公网画廊应优先走 Tailscale 稳定中继；Cloudflare quick tunnel 只能作为临时兜底，不能替代用户指定的 Tailscale 路径。

### Details
用户明确要求“当然要用 tailscale”。当时本机 Tailscale 处于 NoState/NeedsLogin，节点 key 为空；先用了 Cloudflare quick tunnel 让公网可看，但这是临时地址且无 uptime 保证。应诊断 Tailscale 本地状态，完成重新登录，恢复 100.84.28.40 后再切回 199.68.217.229:8861 中继。

### Suggested Action
遇到 Tailscale NoState 时，先 `tailscale status --json` 做只读诊断。**严禁擅自 `tailscale logout` / `tailscale down` / 结束 `tailscaled` 或 `tailscale` 进程**；只允许调整“直连/非直连”连接方式。若确需重新认证或重启进程，必须先征得用户明确同意。临时隧道不能作为最终方案。

### Metadata
- Source: user_correction
- Related Files: `_serve_t1.py`, `_relay-tangyuan.conf`
- Tags: project-103, tailscale, public-relay, gallery

---

## [LRN-20261126-TS-NO-LOGOUT] hard-rule

**Logged**: 2026-11-26T23:00:00+08:00
**Priority**: critical
**Status**: active
**Area**: infra

### Summary
未经用户明确许可，不得登出 Tailscale、不得结束 Tailscale 进程；只允许切换直连/非直连连接方式。

### Details
用户明确要求：“以后不允许擅自登出tailscale，不允许擅自结束tailscale进程，只能改直连或非直连”。此前为恢复画廊曾考虑 `tailscale logout` + `tailscale up`，该做法今后禁止作为默认排障手段。Tailscale 登录态与进程生命周期属于用户控制边界，任何会改变它们的操作都必须先询问。

### Suggested Action
排障时只做只读检查（`tailscale status --json`、`tailscale netcheck` 等）；需要调整连接时只改直连/非直连偏好；不得执行 `logout`、`down`、停止服务、杀 `tailscaled`/`tailscale` 进程。确需变更登录态或重启进程时，先说明原因并等待用户批准。

### Metadata
- Source: user_correction
- Related Files: `_start_tailscale_gallery.ps1`
- Tags: project-103, tailscale, hard-rule, no-logout
---
