# -*- coding: utf-8 -*-
"""_cosy_samples.py — CosyVoice 候选音色试听包（同一句 T1 旁白，双模型）。"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import audio  # noqa: E402

OUT = ROOT / "cache" / "cosy_voices"
OUT.mkdir(parents=True, exist_ok=True)

TEXT = ("我们每个人都有一个看不见的气泡，它跟着我们走，随我们坐。"
        "陌生人靠得太近，我们会不由自主地后退。"
        "一九六六年，人类第一次给这个现象起了名字：个人空间。")

VOICES = [
    ("cosyvoice-v2/longshu_v2",       "龙书·沉稳青年男·新闻播报(v2)"),
    ("cosyvoice-v2/longxiaochun_v2",  "龙小淳·知性积极女(v2)"),
    ("cosyvoice-v2/longxiaocheng_v2", "龙小诚·磁性低音男(v2)"),
    ("cosyvoice-v2/longtian_v2",      "龙天·磁性理智男(v2)"),
    ("cosyvoice-v2/longze_v2",        "龙泽·温暖元气男(v2)"),
    ("cosyvoice-v2/longbaizhi",       "龙白芷·睿气旁白女(v2)"),
    ("cosyvoice-v2/longwan_v2",       "龙婉·积极知性女(v2)"),
    ("cosyvoice-v3-plus/longanyang",  "龙安洋·阳光大男孩(v3-plus标杆)"),
]


def main():
    for spec, label in VOICES:
        fname = spec.replace("/", "_") + ".mp3"
        f = OUT / fname
        if f.exists() and f.stat().st_size > 10000:
            print("skip", spec, flush=True)
            continue
        try:
            audio._cosy_tts(TEXT, f, spec, 0)
            print("ok", label, f.stat().st_size, "bytes", flush=True)
        except Exception as e:  # noqa: BLE001
            print("FAIL", spec, str(e)[:120], flush=True)
        time.sleep(6)


if __name__ == "__main__":
    main()
