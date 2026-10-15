#!/usr/bin/env python3
"""_make_scene_v2.py — 从 narration_v2_draft.md 生成 v2 scene JSON（TTS 输入线与来源元数据线分离）。

规则（对应 2026-10-14 用户反馈的 B/T 泄漏根因）：
  - sentences[].text = 纯净口语文本，绝不携带〔B〕〔T〕〔D〕〔S〕〔算〕等任何标记
  - 来源归属放进每句独立 sources 数组（从 v1 scene JSON 旧文本的尾标继承，机器可读）
  - 句数必须 = 48，与 v1 一一对应
用法：python _make_scene_v2.py [--emit DRAFT|FINAL]
  DRAFT（默认）写 audio/scene_envpsy-case1-v2.json 且 title 带 -DRAFT，提醒不得直接用于重录；
  FINAL 需显式 --emit FINAL（用户确认语气后使用），title 去掉 DRAFT 后缀。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUD = ROOT / "audio"
V1_SCENE = AUD / "scene_envpsy-case1.json"
DRAFT_MD = ROOT / "runs" / "envpsy-case1-full" / "narration_v2_draft.md"
LABEL_RE = re.compile(r"〔(B|T|D|S|算)〕")
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*$")

def main() -> int:
    emit = "DRAFT"
    if "--emit" in sys.argv:
        emit = sys.argv[sys.argv.index("--emit") + 1]

    v1 = json.loads(V1_SCENE.read_text(encoding="utf-8"))
    old = v1["sentences"]
    assert len(old) == 48, f"v1 sentence count {len(old)} != 48"

    rows = []
    for line in DRAFT_MD.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if m:
            rows.append((int(m.group(1)), m.group(2).strip()))
    assert len(rows) == 48, f"draft rows {len(rows)} != 48"
    assert [n for n, _ in rows] == list(range(1, 49)), "draft cue numbering not 1..48"

    sentences = []
    problems = []
    total_chars = 0
    for idx, (cue_no, new_text) in enumerate(rows):
        old_text = old[idx]["text"]
        labels = LABEL_RE.findall(old_text)
        clean = LABEL_RE.sub("", new_text).strip()
        clean = re.sub(r"\s+", " ", clean)
        if "〔" in clean or "〕" in clean:
            problems.append(f"cue {cue_no}: residual bracket mark")
        total_chars += len(clean)
        sentences.append({
            "text": clean,
            "pause_after": old[idx].get("pause_after", 0.25),
            "sources": labels,
        })

    if problems:
        for p in problems:
            print("ERROR:", p)
        return 1

    title = "envpsy-case1-v2-DRAFT" if emit == "DRAFT" else "envpsy-case1-v2"
    scene = {
        "title": title,
        "voice": v1["voice"],
        "bgm": v1["bgm"],
        "gap": v1.get("gap", 0.25),
        "tail": v1.get("tail", 1.5),
        "sentences": sentences,
    }
    out = AUD / "scene_envpsy-case1-v2.json"
    out.write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")

    n_src = sum(1 for s in sentences if s["sources"])
    print(f"OK wrote {out.name} ({emit})")
    print(f"sentences={len(sentences)} chars={total_chars} (v1 text-only="
          f"{sum(len(LABEL_RE.sub('', s['text'])) for s in old)})")
    print(f"cues_with_sources={n_src}/48; all texts label-free: True")
    return 0

if __name__ == "__main__":
    sys.exit(main())
