# -*- coding: utf-8 -*-
"""_dashscope_tts_probe.py — 百炼 2026 新端点实测：/api/v1/services/audio/tts/SpeechSynthesizer（voice 入 input）。"""
import json
import os
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path

KEY = os.environ.get("DASHSCOPE_API_KEY") or subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "[Environment]::GetEnvironmentVariable('DASHSCOPE_API_KEY','User')"],
    capture_output=True, text=True).stdout.strip()

URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer"
OUT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103\cache\rh_tts_out")
OUT.mkdir(parents=True, exist_ok=True)

TEXT = ("霍尔在一九六三年把研究这类距离行为的领域称为“空间接近学”，英文是 Proxemics。"
        "你可以把个人空间想象成身体周围一只看不见的气泡。")


def synth(model, voice, fmt="mp3", url=URL):
    body = json.dumps({
        "model": model,
        "input": {"text": TEXT, "voice": voice, "format": fmt, "sample_rate": 24000},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()
        try:
            js = json.loads(raw)
        except Exception:
            dest = OUT / f"{model.replace('/', '_')}_{voice}.{fmt}"
            dest.write_bytes(raw)
            print(f"[{model} / {voice}] OK(binary) {time.time()-t0:.1f}s {len(raw)} bytes -> {dest.name}")
            return True
        au = (js.get("output") or {}).get("audio") or {}
        aurl = au.get("url") or (js.get("output") or {}).get("audio_url")
        if aurl:
            audio = urllib.request.urlopen(aurl, timeout=60).read()
            dest = OUT / f"{model.replace('/', '_')}_{voice}.{fmt}"
            dest.write_bytes(audio)
            print(f"[{model} / {voice}] OK {time.time()-t0:.1f}s {len(audio)} bytes -> {dest.name}")
            return True
        print(f"[{model} / {voice}] resp no audio: {json.dumps(js, ensure_ascii=False)[:300]}")
        return False
    except urllib.error.HTTPError as e:
        print(f"[{model} / {voice}] HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}")
        return False
    except Exception as e:
        print(f"[{model} / {voice}] ERR {e}")
        return False


if __name__ == "__main__":
    synth("cosyvoice-v3-plus", "longanyang", "mp3")
    synth("qwen3-tts-flash", "Cherry", "mp3")
