# -*- coding: utf-8 -*-
"""_cosy_cross2.py — v3-plus 可用音色批量探测。"""
import json
import os
import urllib.request
import urllib.error

KEY = os.environ.get("DASHSCOPE_API_KEY", "")
TEXT = "测试一句话。"

CANDIDATES = [
    "longshu_v2", "longsanshu", "longsanshu_v2", "longxiaochun", "longxiaochun_v2",
    "longbaizhi", "longtian", "longtian_v2", "longxiaocheng_v2", "longfei", "longfei_v2",
    "longwan", "longwan_v2", "longhao_v2", "longze_v2", "longcheng_v2",
    "longnan", "longnan_v2", "longyuan_v2", "longyue_v2", "longmiao_v2", "longxiu_v2",
    "longshuo_v2", "longxiaobai_v2", "longjin_v2", "longanzhi", "longanshuo",
]


def call(voice):
    body = json.dumps({"model": "cosyvoice-v3-plus", "input": {
        "text": TEXT, "voice": voice, "format": "mp3", "sample_rate": 24000}}).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer",
        data=body, headers={"Authorization": "Bearer " + KEY,
                            "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            r.read()
        return "OK"
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        return "418" if "418" in msg else ("404m" if "not exist" in msg.lower() or "Model" in msg else msg[:80])
    except Exception as e:
        return str(e)[:80]


if __name__ == "__main__":
    ok = []
    for v in CANDIDATES:
        st = call(v)
        print(f"{v:>18}: {st}", flush=True)
        if st == "OK":
            ok.append(v)
    print("USABLE:", ok)
