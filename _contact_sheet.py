# -*- coding: utf-8 -*-
"""_contact_sheet.py — urbandoc 80帧拼 4 张 4x5 网格图。"""
from pathlib import Path
from PIL import Image

D = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103\research\urban-doc")
frames = sorted(D.glob("f_*.jpg"))
TW, TH = 426, 240  # 1280x720 -> /3
COLS, ROWS = 4, 5
for si in range(4):
    sheet = Image.new("RGB", (COLS * TW + (COLS + 1) * 8, ROWS * TH + (ROWS + 1) * 8), (16, 18, 22))
    for k in range(COLS * ROWS):
        idx = si * COLS * ROWS + k
        if idx >= len(frames):
            break
        im = Image.open(frames[idx]).resize((TW, TH))
        r, c = divmod(k, COLS)
        sheet.paste(im, (8 + c * (TW + 8), 8 + r * (TH + 8)))
    out = D / f"sheet{si+1}.jpg"
    sheet.save(out, quality=88)
    print(out.name, sheet.size, f"帧 {si*20+1}-{min((si+1)*20, len(frames))}")
