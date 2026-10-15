#!/usr/bin/env python3
"""_make_storyboard_v2.py — 由 v1 storyboard + FINAL v2 scene JSON 生成 v2 storyboard。

改动面（其余所有数值/来源参数原样保留）：
  1. 48 行编号旁白 → v2 口语稿（零〔X〕标记，与 scene_envpsy-case1-v2.json 完全一致）
  2. Parameters 计数行按 3564 字更新；每单元字数重算；六幕时间区间改注"以 v2 实测时钟为准"
  3. 插入 v2 修订记录块（用户 2026-10-14 确认语气+全长版）
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "runs" / "envpsy-case1" / "storyboard.md"
SCENE = ROOT / "audio" / "scene_envpsy-case1-v2.json"
OUT = ROOT / "runs" / "envpsy-case1-v2" / "storyboard.md"

def main():
    sc = json.loads(SCENE.read_text(encoding="utf-8"))
    assert "DRAFT" not in sc["title"], "scene json 仍是 DRAFT——先 --emit FINAL"
    texts = [s["text"] for s in sc["sentences"]]
    assert len(texts) == 48

    lines = SRC.read_text(encoding="utf-8").splitlines()
    out, i, replaced = [], 0, 0
    counts = [len(t) for t in texts]
    for ln in lines:
        m = re.match(r"^(\d+)\. .+$", ln)
        if m and int(m.group(1)) == replaced + 1:
            replaced += 1
            out.append(f"{replaced}. {texts[replaced-1]}")
            continue
        if ln.startswith("正文字符总数＝"):
            out.append(f"正文字符总数＝{sum(counts)}字。"); continue
        if ln.startswith("平均单元长度＝"):
            out.append(f"平均单元长度＝{sum(counts)/48:.2f}字/单元。"); continue
        if ln.startswith("按5.1字/秒计算的总时长＝"):
            out.append(f"按5.1字/秒计算的总时长＝约{sum(counts)/5.1:.0f}秒。"); continue
        if ln.startswith("按5.13字/秒计算的总时长＝"):
            out.append("（v2 废止名义速率折算——时长以 TTS 实测时钟为准。）"); continue
        if ln.startswith("成片允许时长区间＝"):
            out.append(f"成片允许时长区间＝[{sum(counts)/5.1*0.94:.0f}，{sum(counts)/5.1*1.12:.0f}]秒。"); continue
        if ln.startswith("每单元正文字符数＝"):
            out.append("每单元正文字符数＝" + json.dumps(counts, ensure_ascii=False).replace(", ", ",") + "字。"); continue
        m2 = re.match(r"^(S[1-6]，.{1,12}：单元\d+—\d+；\d+)字；\d+秒；时间区间.*$", ln)
        if m2:
            out.append(m2.group(1) + "字；v2 秒数与区间以实测时钟 timing_envpsy-case1-v2.json 为准。"); continue
        if ln.startswith("## Parameters"):
            out.append(ln)
            out.append("")
            out.append("> **v2 修订（2026-10-14，用户确认「语气样稿+全长版」）**：48 单元全部口语化重写；"
                       "正文零〔来源角标〕——来源只保留在本参数区与画面自然角标（如「来源：NYC DOT 2010」），"
                       "不上屏字母代号、不进语音；语义锚点与全部数字口径与 v1 一一对应，未增删单元。")
            continue
        out.append(ln)
    assert replaced == 48, f"narration replaced {replaced}/48"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"OK wrote {OUT} chars={sum(counts)} per-unit={counts}")

if __name__ == "__main__":
    sys.exit(main())
