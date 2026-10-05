#!/usr/bin/env python3
"""bgm_gen.py — 本地合成 CC0 教学配乐库（BPM 按构造精确已知）。
三首: musicbox(100BPM 音乐盒五声琶音) / plucky(110BPM 拨弦大调) / calm(70BPM 慢垫)。
风格取向: 低电平、无鼓、无旋律主导 —— 白板教学背景垫,响度留给旁白。
"""
import json, numpy as np
from pathlib import Path
from scipy.io import wavfile  # 若无 scipy 则回退手写 wav
SR = 44100

def note(freq, t0, dur, amp, timbre="sine", decay=6.0):
    n = int(dur * SR); t = np.arange(n) / SR
    w = {"sine": np.sin, "tri": lambda x: 2/np.pi*np.arcsin(np.sin(x)),
         "musicbox": lambda x: np.sin(x) + .35*np.sin(2*x) + .12*np.sin(3*x)}[timbre](2*np.pi*freq*t)
    env = np.minimum(1, t/.004) * np.exp(-t*decay)
    return w * env * amp

def mix(tracks, length):
    out = np.zeros(int(length*SR))
    for x, t0 in tracks: out[int(t0*SR):int(t0*SR)+len(x)] += x[:max(0, len(out)-int(t0*SR))]
    return out

def stereoize(x, detune=0.15, delay=0.012):
    d = np.zeros_like(x); shift = int(delay*SR)
    d[shift:] = x[:-shift] if shift else x
    L, R = x + detune*d, x - detune*d
    m = max(abs(L).max(), abs(R).max()) + 1e-9
    return np.stack([L/m*.7, R/m*.7], 1)

def gen_musicbox(bpm=100, bars=16):
    beat = 60/bpm; total = bars*4*beat
    C_pent = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
    rng = np.random.default_rng(7); tr = []
    pat = [0, 2, 4, 3, 5, 4, 2, 1]           # 上行-回落琶音骨架
    for bar in range(bars):
        for i, p in enumerate(pat):
            f = C_pent[p] * (2 if (bar % 4 == 3 and i % 4 == 2) else 1)
            tr.append((note(f, 0, 1.2, .30, "musicbox", 5.0), bar*4*beat + i*beat/2))
        if bar % 2 == 1:                        # 每两小节补一个低音锚
            tr.append((note(130.81, 0, 2.0, .18, "sine", 2.2), bar*4*beat))
    return stereoize(mix(tr, total)), total

def gen_plucky(bpm=110, bars=16):
    beat = 60/bpm; total = bars*4*beat
    chords = [[261.63, 329.63, 392.0], [220.0, 261.63, 329.63],
              [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]]  # C-Am-F-G
    tr = []
    for bar in range(bars):
        ch = chords[bar % 4]
        for b, div in ((0, 1), (2, 1), (3, 2)):   # 每小节 3 次拨弦
            for j, f in enumerate(ch):
                tr.append((note(f*(2 if j == 2 else 1), 0, .8, .22, "tri", 7.5),
                           bar*4*beat + b*beat + j*.012))
    return stereoize(mix(tr, total)), total

def gen_calm(bpm=70, bars=8):
    beat = 60/bpm; total = bars*4*beat
    prog = [[130.81, 164.81, 196.0], [110.0, 130.81, 164.81],
            [87.31, 103.83, 130.81], [98.0, 123.47, 146.83]]
    tr = []
    for bar in range(bars):
        for f in prog[bar % 4]:
            x = note(f, 0, 4*beat, .16, "sine", .55)   # 慢起慢落垫音
            n = len(x); t = np.arange(n)/SR
            x *= np.minimum(1, t/.6) * np.minimum(1, (4*beat-t)/.8).clip(0)
            tr.append((x, bar*4*beat))
    return stereoize(mix(tr, total)), total

if __name__ == "__main__":
    out = Path(__file__).parent / "audio" / "bgm"; out.mkdir(parents=True, exist_ok=True)
    lib = []
    for name, fn, bpm, mood in [("musicbox", gen_musicbox, 100, "轻快/讲解"),
                                ("plucky", gen_plucky, 110, "活泼/演示"),
                                ("calm", gen_calm, 70, "沉静/总结")]:
        x, total = fn()
        f = out / f"{name}.wav"
        wavfile.write(f, SR, (x*32767).astype(np.int16))
        lib.append({"file": f"bgm/{name}.wav", "bpm": bpm, "mood": mood,
                    "gain": .13, "dur": round(total, 1)})
        print(f"{name}: {total:.0f}s @{bpm}BPM")
    (out / "library.json").write_text(json.dumps({"tracks": lib}, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    print("library.json written")
