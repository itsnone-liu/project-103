#!/usr/bin/env python3
"""audio.py — 103 教学动画音频管线：TTS → 时序倒置 → 混音。

管线（时序倒置：旁白是时钟）:
  1. tts      : edge-tts 逐句合成 + ffprobe 实测时长 → 锚点贴合(语速自适应) → timing.json
  2. narration: 按 timing.json 把逐句 mp3 对齐成整轨 narration.wav
  3. audit    : silencedetect 反查 narration.wav 实际句起点 vs 计划(±0.15s)
  4. mux      : 视频 + narration + BGM(循环/电平/fade) + loudnorm(-16 LUFS) → 成片
  5. bpm      : numpy 自相关估 BGM 曲目 BPM(写入 library.json 用)

分镜 JSON(audio/scene_<name>.json):
  { "title": "...", "voice": "zh-CN-XiaoxiaoNeural",
    "bgm": {"file": "bgm/Wholesome.mp3", "gain": 0.16},
    "gap": 0.25, "tail": 1.5,
    "sentences": [ {"text": "...", "pause_after": 0.25,
                    "anchor_start": 6.7, "rate_cap": 30} ] }
anchor_start: 该句必须不晚于此刻开口(数学锚,如相遇 t=7.2 前说完铺垫);
              说早了→垫空拍等待,说晚了→按 rate 阶梯加速(%5 步进),仍不够则报错改文案。
代码生成阶段把 timing.json 的 starts 直接注入 narr([...]) — 旁白表=物理事实。
"""
import asyncio, json, subprocess, sys, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUD = ROOT / "audio"
COMP = ROOT / "runs" / "architecture-smoke" / "node_modules" / "@remotion" / "compositor-win32-x64-msvc"

def _ffmpeg_path():
    p = shutil_which()
    if p: return p
    return str(COMP / "ffmpeg.exe")
def _ffprobe(): return str(COMP / "ffprobe.exe")
def shutil_which():
    from shutil import which
    for d in (str(COMP),):
        os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]
    return which("ffmpeg")

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r

def dur_of(path):
    r = run([_ffprobe(), "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)])
    return float(r.stdout.strip())

# ---------- 1. TTS + 锚点贴合 ----------
async def _tts_one(text, out, voice, rate_pct):
    import edge_tts
    rate = f"+{rate_pct}%" if rate_pct else "+0%"
    c = edge_tts.Communicate(text, voice, rate=rate)
    await c.save(str(out))

# --- cosyvoice（百炼 cosyvoice-v3-plus，voice 形如 "cosy:longshu_v3"）---
COSY_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer"

def _cosy_tts(text, out, voice_spec, rate_pct):
    """voice_spec: "<voice_id>" 或 "<model>/<voice_id>"（默认 cosyvoice-v3-plus）。
    v3-plus 仅开放标杆音色(longanyang/longanhuan)；完整龙家班音色库在 cosyvoice-v2。"""
    import urllib.request, urllib.error
    if "/" in voice_spec:
        model, voice_id = voice_spec.split("/", 1)
    else:
        model, voice_id = os.environ.get("COSY_MODEL", "cosyvoice-v3-plus"), voice_spec
    key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not key:
        raise RuntimeError("DASHSCOPE_API_KEY 未设置（User 级环境变量）")
    body = json.dumps({"model": model,
                       "input": {"text": text, "voice": voice_id, "format": "mp3",
                                 "sample_rate": 24000,
                                 **({"speech_rate": round(1 + rate_pct / 100, 3)}
                                    if rate_pct else {})}}).encode("utf-8")
    last = None
    for attempt in range(4):                      # 冷启动可能慢；SSL 悬挂快速失败
        req = urllib.request.Request(COSY_URL, data=body, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                js = json.loads(r.read())
            url = ((js.get("output") or {}).get("audio") or {}).get("url")
            if not url:
                raise RuntimeError(f"cosy 无音频: {json.dumps(js, ensure_ascii=False)[:200]}")
            out.write_bytes(urllib.request.urlopen(url, timeout=120).read())
            return
        except Exception as e:                    # noqa: BLE001
            last = e
            print(f"  cosy retry {attempt+1}: {e}", file=sys.stderr)
            import time as _t; _t.sleep(3 * (attempt + 1))
    raise last

def tts_sentence(text, out, voice, rate_pct=0):
    if voice.startswith("cosy:"):
        _cosy_tts(text, out, voice[5:], rate_pct)
    else:
        asyncio.run(_tts_one(text, out, voice, rate_pct))
    # edge-tts 带 ~0.15-0.2s 头静音;本 ffmpeg 无 silenceremove → silencedetect 量出后 ss 裁剪存 wav
    wav = out.with_suffix(".wav")
    r = run([_ffmpeg_path(), "-i", str(out), "-af", "silencedetect=noise=-45dB:d=0.05",
             "-f", "null", "-"])
    ss = re.search(r"silence_start: ([\d.]+)", r.stderr)
    se = re.search(r"silence_end: ([\d.]+)", r.stderr)
    onset = float(se.group(1)) if (ss and float(ss.group(1)) < 0.15 and se
                                   and float(se.group(1)) < 0.6) else 0.0
    run([_ffmpeg_path(), "-y", "-ss", f"{onset:.3f}", "-i", str(out),
         "-c:a", "pcm_s16le", str(wav)])
    out.unlink()
    return dur_of(wav)

def cmd_tts(scene_json):
    sc = json.loads(Path(scene_json).read_text(encoding="utf-8"))
    name = sc.get("title", Path(scene_json).stem)
    vdir = AUD / "voice" / name; vdir.mkdir(parents=True, exist_ok=True)
    voice = sc.get("voice", "zh-CN-XiaoxiaoNeural")
    gap = sc.get("gap", 0.25); tail = sc.get("tail", 1.5)
    t, starts, ends, rates, texts = 0.0, [], [], [], []
    for k, s in enumerate(sc["sentences"]):
        f = vdir / f"sent_{k:02d}.mp3"
        wav = vdir / f"sent_{k:02d}.wav"
        rate = 0; cap = s.get("rate_cap", 30)
        if wav.exists() and wav.stat().st_size > 40000:   # 断点续跑：已合成句直接量时长
            dur = dur_of(wav)
        else:
            dur = tts_sentence(s["text"], f, voice, 0)
        # 锚点 = 开口时刻: 说早了→垫拍等待; 说晚了(t>锚)→按 5% 阶梯加速语速
        anchor = s.get("anchor_start")
        if anchor is not None and t > anchor + 0.05:
            while rate < cap and t > anchor + 0.05:
                rate = min(cap, rate + 5)
                dur = tts_sentence(s["text"], f, voice, rate)
            if t > anchor + 0.15:
                print(f"!! 句{k} 开口迟于锚点 {anchor}s (最早 {t:.2f}s) — 请缩文案", file=sys.stderr)
        start = max(t, anchor) if anchor is not None else t
        starts.append(round(start, 3)); ends.append(round(start + dur, 3))
        rates.append(rate); texts.append(s["text"])
        t = start + dur + s.get("pause_after", gap)
    total = round(ends[-1] + tail, 3)
    timing = {"title": name, "voice": voice, "starts": starts, "ends": ends,
              "rates": rates, "texts": texts, "total": total,
              "narr": [round(x, 3) for x in starts] + [total], "bgm": sc.get("bgm")}
    out = AUD / f"timing_{name}.json"
    out.write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: timing[k] for k in ("starts", "ends", "rates", "total")}, ensure_ascii=False))
    return out

# ---------- 2. narration.wav ----------
def cmd_narration(timing_json):
    tm = json.loads(Path(timing_json).read_text(encoding="utf-8"))
    name = tm["title"]; vdir = AUD / "voice" / name
    inputs, filters, labels = ["-f", "lavfi", "-t", str(tm["total"]),
                               "-i", "anullsrc=r=44100:cl=stereo"], [], []
    for k, st in enumerate(tm["starts"]):
        ms = int(st * 1000)
        inputs += ["-i", str(vdir / f"sent_{k:02d}.wav")]
        filters.append(f"[{k+1}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={ms}|{ms}[s{k}]")
        labels.append(f"[s{k}]")
    filters.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0[nar]")
    out = AUD / f"narration_{name}.wav"
    run([_ffmpeg_path(), "-y", *inputs, "-filter_complex", ";".join(filters),
         "-map", "[nar]", "-c:a", "pcm_s16le", "-t", str(tm["total"]), str(out)])
    print("narration:", out, f"{dur_of(out):.2f}s")
    return out

# ---------- 3. 对齐审计 ----------
def cmd_audit(nar_wav, timing_json):
    tm = json.loads(Path(timing_json).read_text(encoding="utf-8"))
    r = run([_ffmpeg_path(), "-i", str(nar_wav), "-af", "silencedetect=noise=-35dB:d=0.30",
             "-f", "null", "-"])
    onsets = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    first_ss = re.search(r"silence_start: ([\d.]+)", r.stderr)
    if first_ss and float(first_ss.group(1)) > 0.2:
        onsets.insert(0, 0.0)   # 文件以语音开头时 silencedetect 不报首句起点
    print(f"{'k':>2} {'plan':>7} {'actual':>7} {'delta':>7}")
    bad = 0
    for k, st in enumerate(tm["starts"]):
        near = min(onsets, key=lambda x: abs(x - st)) if onsets else -1
        d = near - st
        flag = "" if abs(d) <= 0.15 else "  << DRIFT"
        bad += abs(d) > 0.15
        print(f"{k:>2} {st:7.2f} {near:7.2f} {d:+7.2f}{flag}")
    print("AUDIT", "PASS" if bad == 0 else f"FAIL({bad})")
    return bad == 0

# ---------- 4. mux ----------
def cmd_mux(video, timing_json, out=None):
    tm = json.loads(Path(timing_json).read_text(encoding="utf-8"))
    name = tm["title"]
    nar = AUD / f"narration_{name}.wav"
    bgm = AUD / tm["bgm"]["file"] if tm.get("bgm") else None
    vd = dur_of(video)
    inputs = ["-i", str(video), "-i", str(nar)]
    fc = []
    if bgm and bgm.exists():
        inputs += ["-stream_loop", "-1", "-i", str(bgm)]
        g = tm["bgm"].get("gain", 0.16); fi, fo = 0.8, min(1.5, vd / 4)
        # 本 ffmpeg 无 afade → volume 帧表达式做淡入淡出
        fade = f"min(1,t/{fi})*min(1,max(0,({vd:.2f}-t)/{fo:.2f}))"   # 引号内逗号免转义
        fc.append(f"[2:a]aresample=44100,aformat=channel_layouts=stereo,"
                  f"volume='{fade}':eval=frame,volume={g}[b]")
        mix = "[1:a][b]amix=inputs=2:normalize=0[m]"
    else:
        mix = "[1:a]anull[m]"
    fc.append(mix)
    fc.append("[m]loudnorm=I=-16:TP=-1.5:LRA=11[a]")   # 标签后必须 ; 分段,不能逗号续链
    out = out or str(ROOT / "base-compare" / "pattern-test" / "out" / f"final_{name}.mp4")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    run([_ffmpeg_path(), "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(vd), str(out)])
    print("final:", out, f"{dur_of(out):.2f}s  bgm={'yes' if bgm else 'no'}")
    return out

# ---------- 5. BPM 估计 ----------
def cmd_bgm(path):
    import numpy as np
    r = subprocess.run([_ffmpeg_path(), "-v", "error", "-i", str(path), "-t", "60",
                        "-f", "f32le", "-ac", "1", "-ar", "22050", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, dtype=np.float32); x = x[: 22050 * 60]
    hop, win = 512, 2048
    n = (len(x) - win) // hop
    env = np.array([np.abs(x[i * hop: i * hop + win]).mean() for i in range(n)])
    env = np.diff(env); env[env < 0] = 0
    env = env / (env.max() + 1e-9)
    fps = 22050 / hop
    lag_min, lag_max = int(fps * 60 / 180), int(fps * 60 / 60)   # 180..60 BPM
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    seg = ac[lag_min:lag_max]
    peak = lag_min + int(np.argmax(seg))
    bpm = 60 * fps / peak
    while bpm > 180: bpm /= 2
    while bpm < 60: bpm *= 2
    print(f"{Path(path).name}: ~{bpm:.0f} BPM")
    return round(bpm)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "tts": cmd_tts(sys.argv[2])
    elif cmd == "narration": cmd_narration(sys.argv[2])
    elif cmd == "audit": cmd_audit(sys.argv[2], sys.argv[3])
    elif cmd == "mux": cmd_mux(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "bpm": cmd_bgm(sys.argv[2])
    else: print(__doc__)
