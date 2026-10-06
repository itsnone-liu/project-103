# -*- coding: utf-8 -*-
"""sheets.py — contact sheet 生成：≤6 格/张，时间戳+shot-id 大字烧进画格内部（防 VLM 网格错位）。

评审修正②：qwen3-vl-plus 实测在 12 格拼图上两次格子错位。
规则：每张最多 6 格（2x3 或 3x2），格内底部烧半透明黑条 + 大号时间戳 + shot-id。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = "C:/Windows/Fonts/msyhbd.ttc"


def make_sheet(frame_paths, out_path, shot_id="S00", cols=3, cell_w=620, bar_h=54):
    imgs = []
    for p in frame_paths:
        im = Image.open(p)
        h = int(im.height * cell_w / im.width)
        imgs.append((p, im.resize((cell_w, h))))
    rows = (len(imgs) + cols - 1) // cols
    cell_h = max(im.height for _, im in imgs) + bar_h
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * 8,
                              rows * cell_h + (rows + 1) * 8), (12, 18, 30))
    try:
        font = ImageFont.truetype(FONT, 34)
    except OSError:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(imgs):
        r, c = divmod(i, cols)
        x = 8 + c * (cell_w + 8)
        y = 8 + r * (cell_h + 8)
        sheet.paste(im, (x, y + bar_h))
        # 半透明条：时间戳 + shot-id 烧在格内顶部
        d.rectangle([x, y, x + cell_w, y + bar_h], fill=(0, 0, 0))
        ts = Path(p).stem.replace("f_", "")
        d.text((x + 12, y + 8), f"{shot_id}  t={ts}s", font=font, fill=(255, 210, 90))
    sheet.save(out_path, quality=90)
    return out_path


def batch(frames_dir, out_dir, shot_id="S00", per_sheet=6, pattern="f_*.jpg"):
    """按时间顺序把帧目录切成分片 sheet，返回 sheet 路径列表。"""
    frames = sorted(Path(frames_dir).glob(pattern))
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    sheets = []
    for i in range(0, len(frames), per_sheet):
        chunk = frames[i:i + per_sheet]
        sp = out / f"sheet_{shot_id}_{i // per_sheet:02d}.jpg"
        make_sheet(chunk, sp, shot_id=shot_id)
        sheets.append(str(sp))
    return sheets
