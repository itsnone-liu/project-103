#!/usr/bin/env python3
"""_make_storyboard_case2.py — case2 scene JSON + timing → storyboard.md（含参数区+算式区）。
规则延续案例A v2：正文零来源角标；来源只在参数区与画面自然角标。
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "envpsy-case2-cubicle"
scene = json.loads((ROOT / "audio" / "scene_envpsy-case2-cubicle.json").read_text(encoding="utf-8"))
timing = json.loads((ROOT / "audio" / "timing_envpsy-case2-cubicle.json").read_text(encoding="utf-8"))
S = scene["sentences"]
n = len(S)
assert n == len(timing["starts"]) == len(timing["ends"])
counts = [len(s["text"]) for s in S]
total = sum(counts)

ACTS = [  # (名, 起cue, 止cue) 1-based inclusive
    ("S1，尺度跃迁冷开场", 1, 4),
    ("S2，田野观察", 5, 10),
    ("S3，理想装配", 11, 18),
    ("S4，三重推手异化", 19, 26),
    ("S5，证据钟摆", 27, 32),
    ("S6，控制权收束", 33, 39),
]

SRC_KEY = """来源键（画面自然角标写法，无字母代号）：
L＝美国国会图书馆《办公室与办公设备史》资源指南。
P＝Auscherman《Robert Propst: Utopian Technocrat》（2020）及 Herman Miller 档案；Propst 晚年批评采用安全转述，不引具体原话。
T＝美国税务局 Rev. Proc. 62-21（1962）：设备折旧年限缩短；不展开具体年限数字。
C＝Saval《Cubed》（2014）办公室史叙事。
O＝Oldham 系办公室环境研究（1979 起）方向的定性转述；不报具体样本量与效应量。
H＝Bernstein & Turban 2018（Phil. Trans. R. Soc. B）：两家《财富》五百强实测。
D＝《呆伯特》1989 年起连载（公共常识级）。
B＝本课程教材：Altman 私密调节理论（私密＝对边界的控制）。"""

lines = []
lines.append("## Narration")
lines.append("")
for i, s in enumerate(S, 1):
    lines.append(f"{i}. {s['text']}")
lines.append("")
lines.append("## Parameters")
lines.append("")
lines.append("> **v1（2026-10-15）**：案例B《隔间》初版；39 单元全部口语化；正文零来源角标——来源只保留在本参数区与画面自然角标；透视设计图语法（E组）为本片主打，spike 已验证（runs/cubicle-spike/）。")
lines.append("")
lines.append(SRC_KEY)
lines.append("")
lines.append("旁白与时间参数：")
lines.append(f"TTS单元数＝{n}个。")
lines.append(f"正文字符总数＝{total}字。")
lines.append(f"平均单元长度＝{total/n:.2f}字/单元。")
lines.append(f"实测时钟（timing_envpsy-case2-cubicle.json）总时长＝{timing['total']:.3f}秒；以实测为准，不用名义速率折算。")
lines.append(f"每单元正文字符数＝{counts}字。")
lines.append("")
lines.append("六幕内容分配（秒数以实测时钟为准）：")
for name, a, b in ACTS:
    ch = sum(counts[a-1:b])
    t0, t1 = timing["starts"][a-1], timing["ends"][b-1]
    lines.append(f"{name}：单元{a}—{b}；{ch}字；实测 {t0:.3f}–{t1:.3f} 秒。")
lines.append("")
lines.append("历史时间参数：")
lines.append("第一代 Action Office 年份＝1964年。〔P〕")
lines.append("第二代 Action Office 定型年份＝1968年；间隔＝1968-1964＝4年，称「四年之后」。〔P〕")
lines.append("税务规程年份＝1962年（Rev. Proc. 62-21）；早于第二代6年，不表述为同年因果。〔T〕")
lines.append("《呆伯特》连载起始＝1989年；「八十年代末」为定性表述。〔D〕")
lines.append("开放工位实测年份＝2018年；两项实测均为《财富》五百强公司。〔H〕")
lines.append("")
lines.append("量化与口径：")
lines.append("面对面交流降幅＝约70%＝0.7（定性「约」，为两项实测的合并量级表述；不拆分单一公司数字）。〔H〕")
lines.append("「满意度和效率往往好过完全开放」＝研究方向的定性转述，不报效应量、不称「证明」。〔O〕")
lines.append("「塞进多得多的人」＝教学示意表述，非实测密度数字；不使用具体倍数。")
lines.append("「比流行早了四十年」＝以1968年对2000年代站立办公流行潮的粗略对照，教学性表述。〔P〕")
lines.append("第1—4、19、23—26、32、34—36、39单元的画面年份/公司名以自然角标标注，不进语音。")
lines.append("")
lines.append("算式（教学推导，供画面指数化使用）：")
lines.append("1968 - 1964 = 4")
lines.append("1968 - 1962 = 6")
lines.append("70 / 100 = 0.70")
lines.append("100 * (1 - 0.70) = 30")
lines.append("1989 - 1968 = 21")
lines.append("2018 - 1989 = 29")

out = RUN / "storyboard.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"storyboard: {out} ({n} cues, {total} chars, total {timing['total']:.3f}s)")
