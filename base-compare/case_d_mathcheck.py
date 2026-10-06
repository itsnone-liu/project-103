#!/usr/bin/env python3
"""case_d_mathcheck.py — fail-closed math audit for case D storyboards.

Parses STORYBOARD.md Parameters block for three vertices (px) and three
declared angles; recomputes angles via atan2 and checks: (1) each declared
angle matches geometry within tol, (2) sum == 180 within tol.
Usage: python case_d_mathcheck.py case-d/<model>/<model>/STORYBOARD.md
"""
from __future__ import annotations
import math
import re
import sys
from pathlib import Path


def angle_at(v, a, b):  # angle at vertex v between rays to a and b
    u = (a[0] - v[0], a[1] - v[1]); w = (b[0] - v[0], b[1] - v[1])
    cos = (u[0] * w[0] + u[1] * w[1]) / (
        math.hypot(*u) * math.hypot(*w) + 1e-12)
    return math.degrees(math.acos(max(-1, min(1, cos))))


def main() -> int:
    md = Path(sys.argv[1]).read_text(encoding='utf-8')
    nums = [float(x) for x in re.findall(
        r'(?<![\d.])-?\d+(?:\.\d+)?', md)]
    # vertices: find lines mentioning vertices/顶点 and pick 6 numbers
    verts = None
    for m in re.finditer(r'([A-C]|顶点|vert)[^\n]{0,120}', md, re.I):
        pass  # heuristic fallback below: storyboard must be explicit
    vm = re.search(r'([A-C])\s*[=:：]\s*\((\d+)[,，]\s*(\d+)\)', md)
    coords = re.findall(r'\(?\b([5-9]\d{2}|1[0-9]{3})\b\s*[,，]\s*'
                        r'([1-9]\d{2})\b', md)
    angles_declared = [float(x) for x in re.findall(
        r'(?<![\d.])(\d{2}(?:\.\d+)?)\s*°', md)]
    ok = True
    if len(coords) >= 3:
        (ax, ay), (bx, by), (cx, cy) = [(float(a), float(b))
                                        for a, b in coords[:3]]
        A, B, C = (ax, ay), (bx, by), (cx, cy)
        geom = [angle_at(A, B, C), angle_at(B, A, C), angle_at(C, A, B)]
        print(f'vertices parsed: A={A} B={B} C={C}')
        print(f'geometry angles: {[round(g, 2) for g in geom]} '
              f'sum={round(sum(geom), 3)}')
        if abs(sum(geom) - 180) > 0.01:
            print('!! atan2 sum != 180 (parser bug?)'); ok = False
        if angles_declared:
            ds = angles_declared[:3]
            print(f'declared angles: {ds}')
            if abs(sum(ds) - 180) > 0.5:
                print('!! declared angles do not sum to 180'); ok = False
            for d, g in zip(sorted(ds), sorted(geom)):
                if abs(d - g) > 0.6:
                    print(f'!! declared {d} vs geometry {g:.2f} drift >0.6')
                    ok = False
        else:
            print('no declared ° values found — check storyboard manually')
            ok = False
    else:
        print(f'!! could not parse 3 vertices (found {len(coords)} coord '
              'pairs) — check storyboard manually'); ok = False
    print('MATHCHECK', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
