# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
runs = ["envpsy-intro-cosy", "envpsy-12a", "envpsy-12b", "envpsy-13", "envpsy-14",
        "envpsy-21", "envpsy-22", "envpsy-24", "envpsy-11", "envpsy-31-cosy"]
for r in runs:
    tm = ROOT / "audio" / f"timing_{r}.json"
    qa = ROOT / "runs" / r / "out" / "qa_report.json"
    fin = ROOT / "runs" / r / "out" / f"final_{r}.mp4"
    if tm.exists():
        t = json.loads(tm.read_text(encoding="utf-8"))
        q = json.loads(qa.read_text(encoding="utf-8"))["pass"] if qa.exists() else "-"
        print("%-22s %7.1fs %3d句 QA=%s final=%s" % (r, t["total"], len(t["starts"]), q, fin.exists()))
    else:
        print("%-22s (无 timing)" % r)
