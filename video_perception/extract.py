# -*- coding: utf-8 -*-
"""extract.py — 三路抽帧：均匀 / 场景边界 / 帧差分活动度；plus 定点补帧（分析器请求）。

帧差分从 v0.1 禁区豁免（评审修正④）：它是"哪几秒在动"的廉价检测器，
不是 optical flow；对连续 morph 视频（Manim 长镜头）恰好是 scene 检测的替代主干。
"""
import subprocess
from pathlib import Path

FFMPEG = r"D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\architecture-smoke\node_modules\@remotion\compositor-win32-x64-msvc\ffmpeg.exe"


def uniform(video, out_dir, t0, t1, interval=0.5, width=960):
    """[t0,t1] 每 interval 秒一帧，jpg 命名 f_<ts>.jpg（ts=秒，两位小数）。"""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    n = 0
    t = t0
    while t <= t1 + 1e-6:
        f = out / f"f_{t:07.2f}.jpg"
        subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
                        "-i", video, "-frames:v", "1", "-vf", f"scale={width}:-2",
                        "-q:v", "3", str(f)], timeout=60)
        if f.exists():
            n += 1
        t += interval
    return n


def scene_changes(video, t0, t1, threshold=0.22):
    """ffmpeg scene 分数 → 切换时刻列表（对硬切有效；morph 长镜头可能为空）。"""
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", video, "-vf",
                        f"select='gt(scene,{threshold})',metadata=print",
                        "-f", "null", "-"], capture_output=True, text=True, timeout=600)
    pts = []
    for line in r.stderr.splitlines():
        if line.startswith("pts_time:"):
            try:
                t = float(line.split(":")[1])
                if t0 - 0.5 <= t <= t1 + 0.5:
                    pts.append(round(t, 2))
            except ValueError:
                pass
    return pts


def activity(video, out_dir, t0, t1, sample_fps=6, cell=48, native_fps=None):
    """帧差分活动度曲线：原速小帧 PNG → Python 子采样 → 灰度差均值 → {ts: score}。
    （bundled ffmpeg 无 rawvideo muxer / fps 滤镜，全部 Python 侧处理。）
    native_fps 缺省自动 probe（2026-10-06 raptor 盲测：60fps 视频撞 24 假设时间戳全错）。"""
    from PIL import Image
    if native_fps is None:
        import probe
        native_fps = probe.meta(video)["fps"]
        if not native_fps or native_fps <= 0:
            native_fps = 24
    out = Path(out_dir)
    adir = out / "_activity"; adir.mkdir(parents=True, exist_ok=True)
    for old in adir.glob("*.png"):
        old.unlink()
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t0:.2f}",
                    "-t", f"{t1 - t0:.2f}", "-i", video, "-vf",
                    f"scale={cell}:{cell},format=gray",
                    str(adir / "a%05d.png")], timeout=600)
    frames = sorted(adir.glob("a*.png"))
    stride = max(1, round(native_fps / sample_fps))
    curve = {}
    prev = None
    idx = 0
    for fp in frames:
        if idx % stride != 0:
            idx += 1
            continue
        im = Image.open(fp)
        cur = list(im.getdata())
        if prev is not None:
            diff = sum(abs(a - b) for a, b in zip(cur, prev)) / (im.width * im.height)
            ts = t0 + idx / native_fps
            curve[round(ts, 2)] = round(diff, 1)
        prev = cur
        idx += 1
    return curve


def requested(video, out_dir, timestamps, pad=0.3, step=0.1, width=960):
    """分析器请求补帧：每个 ts 在 [ts-pad, ts+pad] 内每 step 秒一帧（运动性质主张的取证协议）。"""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    n = 0
    for ts in timestamps:
        t = ts - pad
        while t <= ts + pad + 1e-6:
            f = out / f"f_{t:07.2f}.jpg"
            subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
                            "-i", video, "-frames:v", "1", "-vf", f"scale={width}:-2",
                            "-q:v", "3", str(f)], timeout=60)
            if f.exists():
                n += 1
            t += step
    return n
