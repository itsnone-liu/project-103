# -*- coding: utf-8 -*-
"""_isd_batch2.py — 《室内空间设计》批2驱动（ch3余3段+ch4余4段+ch5首段，共8段）。
门禁/断点续跑/结果文件与批1相同。"""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
LESSONS = ["isd-3-01", "isd-3-03", "isd-3-04", "isd-4-01",
           "isd-4-03", "isd-4-04", "isd-4-05", "isd-5-01"]
MIN_TOTAL = 270.0
RESULT = ROOT / "_isd_batch2_result.json"

def gate_duration(title):
    tm = json.loads((ROOT / "audio" / f"timing_{title}.json").read_text(encoding="utf-8"))
    return tm["total"] >= MIN_TOTAL, tm["total"]

def gate_freeze(final_path):
    sys.path.insert(0, str(ROOT))
    import _freeze_check as FC
    FC.FF = str(ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe")
    runs, _ = FC.freeze_windows(str(final_path))
    return not runs, runs

def main():
    results = {}
    if RESULT.exists():
        results = json.loads(RESULT.read_text(encoding="utf-8"))
    env = dict(os.environ); env["P103_RENDER_SHARDS"] = "4"; env["PYTHONUTF8"] = "1"
    for title in LESSONS:
        run_dir = ROOT / "runs" / title
        final = run_dir / "out" / f"final_{title}.mp4"
        if final.exists() and results.get(title, {}).get("pass"):
            print(f"[skip] {title} already passed", flush=True); continue
        t0 = time.time()
        r = subprocess.run([PY, "-X", "utf8", str(ROOT / "_run_produce.py"), f"runs/{title}",
                            "--topic", f"runs/{title}/topic-{title}.md",
                            "--model", "sol", "--effort", "high",
                            "--profile", "profiles/isd.profile.yaml", "--title", title],
                           cwd=str(ROOT), env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        ok = r.returncode == 0 and final.exists()
        dur_ok, total = (None, None)
        frz_ok, frz_runs = (None, None)
        if ok:
            try:
                dur_ok, total = gate_duration(title)
                frz_ok, frz_runs = gate_freeze(final)
                ok = dur_ok and frz_ok
            except Exception as e:  # noqa: BLE001
                ok = False; frz_runs = [f"gate-error: {e}"]
        results[title] = {"pass": bool(ok), "minutes": round((time.time() - t0) / 60, 1),
                          "total_s": total, "freeze": frz_runs if frz_runs else [],
                          "tail": (r.stdout or "").strip().splitlines()[-3:] if r.stdout else [],
                          "err": (r.stderr or "").strip()[-300:] if not ok else ""}
        RESULT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{'PASS' if ok else 'FAIL'}] {title} total={total} freeze={frz_runs} "
              f"({results[title]['minutes']}min)", flush=True)
    print("BATCH DONE:", {k: v["pass"] for k, v in results.items()}, flush=True)

if __name__ == "__main__":
    main()
