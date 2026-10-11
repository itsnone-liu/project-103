# -*- coding: utf-8 -*-
"""_cosy_cross3.py — 限流退避后精探：v3-plus 可用集 + cosyvoice-v2 通道。"""
import json
import os
import time
import urllib.request
import urllib.error

KEY = os.environ.get("DASHSCOPE_API_KEY", "")
TEXT = "测试一句话。"


def call(model, voice, timeout=300):
    body = json.dumps({"model": model, "input": {
        "text": TEXT, "voice": voice, "format": "mp3", "sample_rate": 24000}}).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer",
        data=body, headers={"Authorization": "Bearer " + KEY,
                            "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read()
        return "OK"
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        if "418" in msg:
            return "418"
        if "Throttl" in msg or "Rate" in msg:
            return "THROTTLE"
        if "not exist" in msg.lower():
            return "404model"
        return msg[:90]
    except Exception as e:
        return str(e)[:90]


if __name__ == "__main__":
    time.sleep(60)
    tests = [
        ("cosyvoice-v3-plus", "longanyang"),     # 已证可用(对照)
        ("cosyvoice-v3-plus", "longhuhu"),       # 标杆童声
        ("cosyvoice-v3-plus", "longanhuan"),     # 标杆女
        ("cosyvoice-v3-plus", "longtian_v2"),    # 上轮 THROTTLE 存疑
        ("cosyvoice-v3-plus", "longze_v2"),      # 上轮 THROTTLE 存疑
        ("cosyvoice-v3-plus", "longnan"),        # 上轮 ssl 超时存疑
        ("cosyvoice-v2", "longxiaochun_v2"),     # v2 通道
        ("cosyvoice-v2", "longshu_v2"),          # v2 通道·沉稳青年男
        ("cosyvoice-v2", "longsanshu_v2"),       # v2 通道·沉稳质感男
    ]
    for model, voice in tests:
        st = call(model, voice)
        print(f"{model:>16} / {voice:>14}: {st}", flush=True)
        time.sleep(8)
