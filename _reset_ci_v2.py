# -*- coding: utf-8 -*-
"""_reset_ci_v2.py — 音画错位彻底重置：ci1..ci8（复用第一跑旧音频所致）。
清 runs 产物（留 topic）+ audio/{scene,timing,narration} + audio/voice/ 子目录。
ci9/ci10 无旧账不动。幂等。"""
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
COURSE = ROOT / "lesson-runtime" / "course"
BAD = list(range(1, 9))          # ci1..ci8 音画错位
INTRO_IDS = {f"lesson-{n}-0-chapter-intro" for n in range(1, 11)}

for i in BAD:
    run = f"envpsy-ci{i}"
    rd = ROOT / "runs" / run
    if rd.exists():
        for p in rd.iterdir():
            if p.is_file() and p.name.startswith("topic-"):
                continue
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
    for f in (ROOT / "audio").glob(f"{run}.*"):
        f.unlink()
    for f in (ROOT / "audio").glob(f"*_{run}.json"):
        f.unlink()
    v = ROOT / "audio" / "voice" / run
    if v.exists():
        shutil.rmtree(v, ignore_errors=True)
    print(f"[reset] {run}: runs+audio+voice 已清")

# 包目录 + course.json 条目
for n in BAD:
    ch = f"chapter-{n:02d}"
    lid = f"lesson-{n}-0-chapter-intro"
    pkg = COURSE / ch / lid
    if pkg.exists():
        shutil.rmtree(pkg, ignore_errors=True)
        print(f"[pkg] {ch}/{lid} 删除")

cp = COURSE / "course.json"
import json
course = json.loads(cp.read_text(encoding="utf-8"))
removed = 0
for c in course["chapters"]:
    before = len(c["lessons"])
    c["lessons"] = [l for l in c["lessons"] if l["lesson_id"] not in
                    {f"lesson-{n}-0-chapter-intro" for n in BAD}]
    removed += before - len(c["lessons"])
cp.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[course.json] 移除 {removed} 条；ci9/ci10 保留")
