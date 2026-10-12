# -*- coding: utf-8 -*-
"""重渲染 4.3(envpsy-43) 与 5.1(envpsy-51)：帧号语义桥接修复后的完整出片。
代码/音频/timing 全部复用，只重跑 render→qa→mux→package→course。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import json  # noqa: E402
import _first10 as F  # noqa: E402
import _next10 as N  # noqa: E402
import audio  # noqa: E402
from pipeline import qa  # noqa: E402
from pipeline.adapters import web2d  # noqa: E402


def rerender(run: str) -> bool:
    wd = ROOT / "runs" / run
    timing_p = ROOT / "audio" / f"timing_{run}.json"
    tm = json.loads(timing_p.read_text(encoding="utf-8"))
    print(f"[rerender] {run}: total={tm['total']:.1f}s", flush=True)

    res = web2d.render(wd, tm)
    if not res["ok"]:
        print(f"[rerender] {run} render FAIL: {res.get('errors', [])[:2]}", flush=True)
        return False
    report = qa.check(res["video"], tm, wd)
    if not report["pass"]:
        print(f"[rerender] {run} QA FAIL: {json.dumps(report.get('checks', {}), ensure_ascii=False)[:300]}", flush=True)
        return False
    print(f"[rerender] {run} QA pass dur={report['checks']['duration']['value']:.1f}s", flush=True)

    final = wd / "out" / f"final_{run}.mp4"
    audio.cmd_mux(res["video"], str(timing_p), str(final))
    print(f"[rerender] {run} muxed -> {final.name} {final.stat().st_size/1e6:.1f}MB", flush=True)
    return True


def main():
    targets = [l for l in N.LESSONS if l["run"] in ("envpsy-43", "envpsy-51")]
    assert len(targets) == 2, targets
    ok_all = True
    for lesson in targets:
        if rerender(lesson["run"]):
            F.package(lesson)
            print(f"[rerender] packaged {lesson['lesson_id']}", flush=True)
        else:
            ok_all = False
    N.rebuild_course()
    print("[rerender] course.json rebuilt", flush=True)
    print("RESULT:", "ALL OK" if ok_all else "HAS FAILURES", flush=True)


if __name__ == "__main__":
    main()
