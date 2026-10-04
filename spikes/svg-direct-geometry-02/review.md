# SVG Direct Geometry Spike 02 — Review

## Attempt 1

`attempt-1.html` was saved before its first browser run and was not modified afterward.

### First run

- Opened directly as a local `file://` page in headless Google Chrome.
- Loaded successfully with no external dependencies.
- Browser console errors: 0.
- Page runtime errors: 0.
- Slider-driven updates, Play/Pause, midpoint jump, reset, result reveal, and the SVG point-drag implementation were present in the first attempt.

### Mathematics discovered and implemented

The first implementation independently parameterized P from A to B by `t ∈ [0,1]`:

- `A=(6,0)`, `B=(0,8)`
- `P=(6(1−t),8t)`
- `M=(0,8t)`, `N=(6(1−t),0)`
- `S=48t(1−t)=12−48(t−1/2)²`

It therefore found:

- area range: `0 ≤ S ≤ 12`;
- maximum area: `12`;
- maximizing position: `t=1/2`, so P is the midpoint of AB;
- maximizing rectangle side lengths: `3` and `4`.

The result was initially hidden behind “Show result”; the first attempt also proactively added a live area graph, current-state teaching text, auto-play, direct point dragging, and a midpoint jump.

### Live mathematical checks

| t (A→B) | Rectangle sides | Area S | Result |
|---:|---:|---:|---|
| 0 | 6 × 0 | 0 | PASS |
| 0.001 | 5.994 × 0.008 | 0.047952 | PASS; near A tends to 0 |
| 0.25 | 4.5 × 2 | 9 | PASS |
| 0.5 | 3 × 4 | 12 | PASS; maximum at midpoint |
| 0.75 | 1.5 × 6 | 9 | PASS |
| 0.999 | 0.006 × 7.992 | 0.047952 | PASS; near B tends to 0 |
| 1 | 0 × 8 | 0 | PASS |

A 1001-state sweep over `t∈[0,1]` found:

- no NaN or non-finite geometry;
- no detected area jumps;
- sampled maximum exactly `S=12` at `t=0.5`.

### Visual review finding

At the midpoint, the point N label at the rectangle's lower-right corner overlapped the centered `OA = 6` side-length label. This made N look missing even though the point and label existed in the SVG. The in-rectangle area label could also become cramped when the rectangle approached either endpoint.

No mathematical repair was required.

## Single repair round

`index.html` was created from the frozen attempt and changed only to improve labeling robustness:

1. move the fixed `OA = 6` label lower so it cannot collide with the moving N label;
2. place the live area label above the rectangle when the rectangle is too narrow or too short, while keeping it centered inside for ordinary states;
3. clarify the position readout as the ratio `AP/AB = t` rather than an unexplained decimal.

No parser, capability, Scene IR, framework, external dependency, benchmark, or registry was introduced.
