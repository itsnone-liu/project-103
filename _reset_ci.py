# -*- coding: utf-8 -*-
"""_reset_ci.py — 批5规格错误重置：清 ci1..ci10 的产物/包/course 条目/audio 清单。
保留 topic-ci-*.md（brief 本身无误）。幂等。"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
COURSE = ROOT / "lesson-runtime" / "course"

INTRO_IDS = {f"lesson-{n}-0-chapter-intro" for n in range(1, 11)}
CHAPTERS = [f"chapter-{n:02d}" for n in range(1, 11)]

# 1) runs 目录：保留 topic-*.md，其余全清
for i in range(1, 11):
    rd = ROOT / "runs" / f"envpsy-ci{i}"
    if not rd.exists():
        continue
    for p in rd.iterdir():
        if p.is_file() and p.name.startswith("topic-"):
            continue
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            p.unlink(missing_ok=True)
    print(f"[runs] envpsy-ci{i} 重置（保留 brief）")

# 2) 包目录
for ch in CHAPTERS:
    pkg = COURSE / ch
    if not pkg.exists():
        continue
    for lid in list(INTRO_IDS):
        d = pkg / lid
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
            print(f"[pkg] {ch}/{lid} 删除")

# 3) course.json 条目
cp = COURSE / "course.json"
course = json.loads(cp.read_text(encoding="utf-8"))
removed = 0
for c in course["chapters"]:
    before = len(c["lessons"])
    c["lessons"] = [l for l in c["lessons"] if l["lesson_id"] not in INTRO_IDS]
    removed += before - len(c["lessons"])
course["title"] = "环境心理学·系列课件（第一至四批共三十八课·全书完整版）"
cp.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[course.json] 移除 {removed} 条 intro，恢复 38 课标题")

# 4) audio 清单
for pat in ("scene_envpsy-ci*.json", "timing_envpsy-ci*.json"):
    for p in (ROOT / "audio").glob(pat):
        p.unlink()
        print(f"[audio] {p.name} 删除")
print("重置完成")
