# -*- coding: utf-8 -*-
"""_verify_ci.py — 章绪论三方验收：①句时长↔sidecar 字数相关性（音频是所配文本的物理证明）
②timing 总长∈[70,110] ③vtt 轴=timing 轴 ④sidecar 文本=storyboard 句。"""
import json
import re
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
COURSE = ROOT / "lesson-runtime" / "course"


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs) ** 0.5
    vy = sum((y - my) ** 2 for y in ys) ** 0.5
    return cov / (vx * vy) if vx and vy else 0.0


all_ok = True
for i in range(1, 11):
    run = f"envpsy-ci{i}"
    sb = (ROOT / "runs" / run / "storyboard.md").read_text(encoding="utf-8")
    sents = [m.group(1).strip() for m in re.finditer(r"(?m)^\d+\.\s*(.+)$", sb)]
    tm = json.loads((ROOT / "audio" / f"timing_{run}.json").read_text(encoding="utf-8"))
    vdir = ROOT / "audio" / "voice" / run
    notes = []
    # ① 相关性：句时长 vs sidecar 字数（sidecar 缺失=未走新校验，旧片）
    durs, chrs, missing = [], [], 0
    starts, ends = tm["starts"], tm["ends"]
    for k, txt in enumerate(sents):
        sf = vdir / f"sent_{k:02d}.txt"
        if not sf.exists():
            missing += 1
            continue
        chk = sf.read_text(encoding="utf-8").strip()
        if chk != txt:
            notes.append(f"句{k} sidecar≠storyboard")
        durs.append(ends[k] - starts[k])
        chrs.append(len(txt))
    r = corr(durs, chrs) if len(durs) > 2 else -1
    # ② 时长
    total = tm["total"]
    dur_ok = 70 <= total <= 110
    # ③ vtt 轴
    vtt = (COURSE / f"chapter-{i:02d}" / f"lesson-{i}-0-chapter-intro" / "transcript.vtt")
    vtail = re.findall(r"(\d{2}):(\d{2}):(\d{2})\.", vtt.read_text(encoding="utf-8"))
    vt = int(vtail[-1][0]) * 3600 + int(vtail[-1][1]) * 60 + int(vtail[-1][2]) if vtail else 0
    vtt_ok = abs(vt - total) < 2.5
    ok = r > 0.85 and dur_ok and vtt_ok and not notes and missing == 0
    all_ok &= ok
    flag = "✓" if ok else "✗"
    print(f"ci{i:<2} {flag} total={total:6.1f}s corr={r:5.2f} 句数={len(sents)} "
          f"sidecar缺={missing} vtt差={abs(vt-total):.2f}s {' '.join(notes)}")

print("====", "ALL PASS" if all_ok else "存在未过项")
