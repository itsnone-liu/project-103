"""_s1_check.py — 修后 S1 页码验证拼图。"""
from PIL import Image, ImageDraw, ImageFont
import shutil
from pathlib import Path

STARTS = [0, 4.507, 11.024, 22.053, 27.73, 36.049, 41.102, 49.397, 55.001, 59.5, 67.867,
          75.906, 85.547, 94.332, 99.362, 105.662, 114.444, 126.782, 132.629, 140.264,
          150.021, 156.006, 160.535, 168.434, 176.088, 180.395, 188.766, 193.725, 199.598,
          206.978, 217.209, 221.125, 227.745, 234.919, 240.811, 247.064, 250.39, 259.119,
          264.436, 270.859]

def page_of(t):
    return 1 + max(i for i, s in enumerate(STARTS) if t >= s)

src = Path(r"runs\envpsy-glm-t1-31\out\frames")
dst = Path(r"D:\AI-Teaching-Assistant\.tmp_glm")
ts = [3, 9, 15, 21, 60, 145]
picked = []
for t in ts:
    for delta in (0, 1, -1, 2, -2):
        p = src / f"f{t*24+delta:05d}.jpg"
        if p.exists():
            picked.append((t, p))
            break
thumbs = [Image.open(p).resize((640, 360)) for _, p in picked]
canvas = Image.new("RGB", (640 * 3, (360 + 24) * 2), "#444")
d = ImageDraw.Draw(canvas)
try:
    font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 18)
except Exception:
    font = ImageFont.load_default()
for i, ((t, p), im) in enumerate(zip(picked, thumbs)):
    r, c = divmod(i, 3)
    y = r * (360 + 24)
    d.text((c * 640 + 8, y + 2), f"t={t}s expected page {page_of(t)}", fill="#ff0", font=font)
    canvas.paste(im, (c * 640, y + 24))
canvas.save(dst / "s1_fixed.jpg", quality=88)
print("ok", [(t, page_of(t)) for t, _ in picked])
