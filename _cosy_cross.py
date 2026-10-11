# -*- coding: utf-8 -*-
"""_cosy_cross.py — model × voice 交叉验证（打印错误体）。"""
import json
import os
import urllib.request
import urllib.error

KEY = os.environ.get("DASHSCOPE_API_KEY", "")
TEXT = "霍尔在一九六三年把研究这类距离行为的领域称为空间接近学。"


def call(model, voice):
    body = json.dumps({"model": model, "input": {
        "text": TEXT, "voice": voice, "format": "mp3", "sample_rate": 24000}}).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer",
        data=body, headers={"Authorization": "Bearer " + KEY,
                            "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            js = json.loads(r.read())
        au = (js.get("output") or {}).get("audio") or {}
        print(f"{model} / {voice}: OK url={au.get('url', '')[:70]}")
    except urllib.error.HTTPError as e:
        print(f"{model} / {voice}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:250]}")
    except Exception as e:
        print(f"{model} / {voice}: {e}")


if __name__ == "__main__":
    for model in ["cosyvoice-v3-plus", "cosyvoice-v3"]:
        for voice in ["longanyang", "longshu_v3", "longshu"]:
            call(model, voice)
