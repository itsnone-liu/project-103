# SVG Direct Geometry Spike 03 — Review

## Attempt 1

`attempt-1.html` was saved before its first browser run and was not modified afterward.

### First run

- Opened directly as a local `file://` page in headless Google Chrome.
- Loaded successfully with no external dependencies.
- Browser console errors: 0.
- Page runtime errors: 0.
- Slider, direct dragging of P, Play/Pause, equal-length jump, reciprocal swap, live curve, and hidden result all worked from the first implementation.

### Mathematics discovered and implemented

The first implementation independently inferred that `AQ=9/AP` and that both points staying on sides of length 6 restricts:

- `1.5 ≤ AP ≤ 6`;
- `AQ=9/AP`;
- `PQ=√(AP²+AQ²)=√(x²+81/x²)`.

It then found:

- minimum `PQ=3√2` at `AP=AQ=3`, so P and Q are the midpoints of AB and AD;
- maximum `PQ=3√17/2` at either `(AP,AQ)=(1.5,6)` or `(6,1.5)`, so Q=D or P=B;
- range `3√2 ≤ PQ ≤ 3√17/2`.

### Live checks

| AP | AQ | AP·AQ | PQ | Expected behavior |
|---:|---:|---:|---:|---|
| 1.5 | 6 | 9 | 6.184658… | endpoint maximum; Q=D |
| 2 | 4.5 | 9 | 4.924429… | decreasing toward equality |
| 3 | 3 | 9 | 4.242641… | minimum; both midpoints |
| 4.5 | 2 | 9 | 4.924429… | reciprocal symmetry |
| 6 | 1.5 | 9 | 6.184658… | endpoint maximum; P=B |

An 1801-state sweep found no NaN/non-finite geometry, found the minimum exactly at AP=3, found the maximum at the endpoints, and measured reciprocal-symmetry error below `1.8×10⁻15`.

### Problems found

The mathematics and geometry were correct. The concentrated review found two presentation issues:

1. The live status text explicitly called the endpoint a “maximum” and the equal-length state a “minimum” before the student chose “Show result”. This weakened the intended discovery sequence even though the exact symbolic answer remained hidden.
2. The small graph had numeric ticks and a descriptive title but no explicit `AP` and `PQ` axis labels. The main-diagram AQ/PQ labels were also close to their paths and could use slightly stronger separation.

## Single repair round

`index.html` was created from the frozen attempt and changed only to:

- make pre-result status text observational rather than announcing “maximum/minimum”;
- add explicit AP and PQ axis labels to the small graph;
- slightly reposition the AQ and PQ labels for clearer separation from points/segments;
- rename the equal-length button to the precise action “定位 AP=AQ=3”.

No mathematical code, parser, capability, Scene IR, framework, benchmark, registry, or external dependency was added.

## Final judgment and design rationale

The final page is mathematically correct. The interaction uses AP as the single free control because AQ is determined by the product constraint. The reciprocal-swap button makes the symmetry `(AP,AQ) ↔ (AQ,AP)` experimentally visible, while the live curve exposes the interior minimum and matching endpoint heights without initially printing the final range. This combination was chosen to help a student discover both extremum mechanisms rather than merely watch a moving diagram.
