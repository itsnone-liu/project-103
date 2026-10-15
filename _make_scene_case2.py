#!/usr/bin/env python3
"""_make_scene_case2.py — 案例B《隔间》narration_draft.md → scene JSON。
text=纯净口语（无标记）；sources=代码数组；代码→自然写法映射由 codegen STYLE 承载。
用法：python _make_scene_case2.py [--emit DRAFT|FINAL]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUD = ROOT / "audio"
DRAFT_MD = ROOT / "runs" / "envpsy-case2-cubicle" / "narration_draft.md"
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([A-Za-z算,\s]*)\|?\s*$")
CODE_OK = set("LBPTOHCD算")

emit = "DRAFT"
if "--emit" in sys.argv:
    emit = sys.argv[emit.index(sys.argv) + 1] if False else sys.argv[sys.argv.index("--emit") + 1]

rows = []
for line in DRAFT_MD.read_text(encoding="utf-8").splitlines():
    m = ROW_RE.match(line)
    if m and m.group(1) != "cue":
        text, codes = m.group(2).strip(), m.group(3).strip()
        src = [c for c in re.split(r"[,\s]+", codes) if c] if codes else []
        for c in src:
            assert c in CODE_OK, f"未知来源代码 {c} (cue {m.group(1)})"
        assert "〔" not in text and "〕" not in text, f"cue {m.group(1)} 残留标记"
        rows.append((int(m.group(1)), text, src))

n = len(rows)
assert [r[0] for r in rows] == list(range(1, n + 1)), "cue 编号必须连续"
total = sum(len(r[1]) for r in rows)
sentences = [{"text": r[1], "pause_after": 0.25, "sources": r[2]} for r in rows]
title = "envpsy-case2-cubicle-DRAFT" if emit == "DRAFT" else "envpsy-case2-cubicle"
scene = {
    "title": title,
    "voice": "cosy:cosyvoice-v2/longxiaochun_v2",
    "bgm": {"file": "bgm/Wholesome.mp3", "gain": 0.13},
    "gap": 0.25,
    "tail": 1.5,
    "sentences": sentences,
}
out = AUD / f"scene_{title}.json"
out.write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"cues={n} chars={total} avg={total//n} with_sources={sum(1 for s in sentences if s['sources'])}")
print(f"out={out} emit={emit}")
