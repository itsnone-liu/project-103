"""_tts_ab.py — TTS 音色 A/B：同一段旁白 × 候选音色，输出 mp3 供试听。"""
import asyncio
from pathlib import Path

import edge_tts

OUT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103\audio\tts-ab")
OUT.mkdir(parents=True, exist_ok=True)

# T1-hr 开头三句（有叙事感、含数字，便于听断句/语速/情感）
TEXT = (
    "我们每个人都有一个看不见的气泡，它跟着我们走，随我们坐。"
    "陌生人靠得太近，我们会不由自主地后退。"
    "一九六六年，人类第一次给这个现象起了名字：个人空间。"
)

VARIANTS = [
    ("A-xiaoxiao-current", "zh-CN-XiaoxiaoNeural", "+0%", "现状：晓晓，标准女声"),
    ("B-yunxi", "zh-CN-YunxiNeural", "+0%", "云希：男声，自然对话感最强"),
    ("C-yunjian", "zh-CN-YunjianNeural", "+0%", "云健：男声，沉稳纪录片感"),
    ("D-yunyang", "zh-CN-YunyangNeural", "+0%", "云扬：男声，新闻播报感"),
    ("E-xiaoyi", "zh-CN-XiaoyiNeural", "+0%", "晓伊：女声，年轻 softer"),
    ("F-xiaoxiao-slow", "zh-CN-XiaoxiaoNeural", "-5%", "晓晓降速 5%：检验语速对 AI 感的影响"),
]

async def gen(name, voice, rate):
    c = edge_tts.Communicate(TEXT, voice, rate=rate)
    await c.save(str(OUT / f"{name}.mp3"))
    print("ok", name)

async def main():
    await asyncio.gather(*(gen(n, v, r) for n, v, r, _ in VARIANTS))

asyncio.run(main())
print("done ->", OUT)
