# -*- coding: utf-8 -*-
"""冻结检测：每 2s 抽一帧 → 相邻帧差异 → 报告连续低差区间。"""
import subprocess, sys, tempfile
from pathlib import Path

FF = r"D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\architecture-smoke\node_modules\@remotion\compositor-win32-x64-msvc\ffmpeg.exe"

def freeze_windows(video: str, step: float = 2.0):
    tmp = Path(tempfile.mkdtemp(prefix="frz_"))
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", video,
                    "-r", str(1 / step),
                    str(tmp / "f%05d.jpg")], check=True, timeout=600)
    from PIL import Image, ImageChops
    import PIL.ImageStat as Stat
    frames = sorted(tmp.glob("f*.jpg"))
    prev = None
    diffs = []
    for i, fp in enumerate(frames):
        im = Image.open(fp).convert("L")
        if prev is None:
            diffs.append(0.0)
        else:
            st = Stat.Stat(ImageChops.difference(im, prev))
            diffs.append(sum(st.mean) / len(st.mean))
        prev = im
    # 连续 diff < 阈值 视为冻结
    TH = 1.2
    runs = []
    i = 0
    while i < len(diffs):
        if diffs[i] < TH:
            j = i
            while j + 1 < len(diffs) and diffs[j + 1] < TH:
                j += 1
            dur = (j - i + 1) * step
            if dur >= 20:  # ≥20s 才报
                runs.append((i * step, j * step, round(dur, 1)))
            i = j + 1
        else:
            i += 1
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return runs, [round(d, 1) for d in diffs]

if __name__ == "__main__":
    for vid in sys.argv[1:]:
        runs, _ = freeze_windows(vid)
        name = Path(vid).stem
        print(f"{name}: 冻结段(≥20s) -> {runs if runs else '无'}")
