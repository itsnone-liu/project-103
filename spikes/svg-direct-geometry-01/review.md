# SVG Direct Geometry Spike 01 — Review

## Attempt 1

`attempt-1.html` was saved before its first browser run and was not modified afterward.

### First run

- Opened directly as a local `file://` page in headless Google Chrome.
- Loaded successfully with no external dependencies.
- Browser console errors: 0.
- Page runtime errors: 0.
- The first direct Puppeteer browser-launch attempt failed at the local automation-process boundary; attaching Puppeteer to a separately started headless Chrome succeeded. This was an automation-environment issue, not an HTML runtime failure.

### Mathematical checks from the live page

The checks called the same `intersectionsFor(x)` / `update(x)` calculation used by the UI; the displayed count was not separately hard-coded.

| x | Line intersections | Intersections on segment AC | Observed result |
|---|---:|---:|---|
| 0 | 0 | 0 | PASS |
| 2 | 0 | 0 | PASS |
| 6(√2−1) ≈ 2.485281 | 1 (tangent) | 1 | PASS |
| 2.7 | 2 | 2 | PASS |
| 3 | 2 | 2; roots t=3 and t=6=C | PASS |
| 4 | 2 | 1; other root t≈7.6458 beyond C | PASS |
| 6 | 2 | 1; other root t≈10.2426 beyond C | PASS |

A continuity sweep sampled x=0 through x=6 in steps of 0.01 (601 states). It found no NaN or non-finite SVG circle/intersection coordinates.

### Visual review findings

The primary geometry and the x=3 critical state were clear: P was at the midpoint of BC, one highlighted intersection was inside AC, and the other was at C.

Two visual issues were selected for the single concentrated repair:

1. The dashed continuation of AC ended around parameter t=8.5. At x=6 the computed outside intersection is at t≈10.2426, so the point was correctly computed and drawn but appeared beyond the visible dashed continuation. The extension should reach every outside intersection in the requested x range.
2. The diagonal labels sat relatively close to the geometry/intersections. They should be repositioned slightly and use stronger white paint-order backing for legibility.

No mathematical repair was required.

## Single repair round

`index.html` was created from the frozen attempt and changed only to:

- lengthen the dashed C-side extension far enough to contain the outside intersection at x=6;
- reposition the extension label and improve diagonal-label legibility.

No parser, capability, Scene IR, framework, external dependency, benchmark, or registry was introduced.
