import sys, json, subprocess
sys.path.insert(0, r"D:\qjcNetDiskDownload\deepseek-harness\project\103")

from pathlib import Path
from pipeline import qa
from pipeline.adapters import web2d

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
WD = ROOT / "runs" / "capital3"
timing = json.loads((ROOT / "audio" / "timing_capital2.json").read_text(encoding="utf-8"))
timing["title"] = "capital3"

mode = sys.argv[1] if len(sys.argv) > 1 else "all"

if mode in ("all", "render"):
    res = web2d.render(WD, timing)
    print("render:", "OK" if res.get("ok") else res)
    if not res.get("ok"):
        sys.exit(1)
    video = res["video"]
    (WD / "out" / "video_path.txt").write_text(video, encoding="utf-8")
else:
    video = (WD / "out" / "video_path.txt").read_text(encoding="utf-8").strip()

if mode in ("all", "qa"):
    report = qa.check(video, timing, WD)
    print("qa:", "PASS" if report["pass"] else "FAIL", json.dumps(report["checks"], ensure_ascii=False)[:300])

if mode in ("all", "mux"):
    out = WD / "out" / "final_capital3.mp4"
    r = subprocess.run([sys.executable, str(ROOT / "audio.py"), "mux", video,
                        str(ROOT / "audio" / "timing_capital2.json"), str(out)],
                       capture_output=True, text=True, timeout=300)
    print("mux:", (r.stdout or r.stderr)[-200:])
