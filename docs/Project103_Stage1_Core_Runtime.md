# Project 103 — Stage 1 Core Runtime

**Status:** implemented as the first infrastructure slice, 2026-10-04  
**Source of direction:** `Project103_System_Architecture_and_Infrastructure_Plan_2026-10-04.md`

## Scope

This slice implements only the plan's Stage 1 essentials:

- unified `runs/<run-id>/` workspace layout;
- minimal `project.json` and `run.json` contracts;
- explicit run state transitions and event log;
- safe artifact-path resolution;
- resume/status operations;
- a one-repair counter enforced by the runtime;
- a small CLI (`python p103_cli.py ...`, or installed `p103`).

No LLM calls, content planning, TTS, renderer adapters, HTML runtime, or automatic repair are included. This is a durable production shell, not yet a complete production pipeline.

## Commands

Run from the Project 103 repository root:

```powershell
python p103_cli.py --workspace . video path\to\source.md
python p103_cli.py --workspace . interactive path\to\problem.md
python p103_cli.py --workspace . status <run-id>
python p103_cli.py --workspace . resume <run-id>
python p103_cli.py --workspace . artifact <run-id> plan\lesson-brief.md
```

Optional editable install:

```powershell
python -m pip install -e .
p103 --workspace . video path\to\source.md
```

The source is copied into `runs/<run-id>/input/`; the project contract references the copied relative path, not the mutable original path. IDs are filesystem-safe slugs. Runs are never overwritten.

## State machine

```text
CREATED → PLANNING → BUILDING → RENDERING → VERIFYING → FINAL
                                                     ↘ REPAIRING → RENDERING
Any non-terminal state → FAILED
```

`REPAIRING` is reachable only from `VERIFYING`; the counter is persisted and constrained by `max_repairs` (0 or 1). Only explicit legal transitions are accepted. State changes update `run.json` atomically and append a line to `run.log`.

## Contracts

`project.json` stores task identity, mode, language, source path, selected model label, optional target-duration range, and repair limit. `run.json` stores lifecycle state, timestamps, repair count, and state history. These are operational contracts, not lesson/storyboard IR.

## Verification

Run from the Project 103 root:

```powershell
python -m unittest discover -s tests -v
```

Six standard-library tests cover run scaffolding/source copy, legal and illegal state transitions, resume readback, artifact traversal rejection, single-repair limit, contract validation, and duplicate-run protection. A CLI smoke test also created and inspected a run using `spikes/canvas-wave-interference/source.md`.

## Deliberate non-goals

- no universal parser or Scene IR;
- no topic capability registry or scene-template library;
- no implicit model/provider credential discovery;
- no speculative copying of EduLab internals;
- no full video build until Stage 2 is implemented.

## Next build slice

Stage 2 should be split into testable vertical primitives: narration/timeline contract and parser, subtitle normalization, media probing/keyframe/contact-sheet utilities, then a Remotion shell integration. Keep existing successful sea-breeze, inventory-turnover, diffusion, and Canvas spikes intact as integration evidence; do not rewrite them as a prerequisite.
