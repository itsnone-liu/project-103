# -*- coding: utf-8 -*-
"""_dsb_place_figs.py — 设计基础 DSB 批产对证位真图预置（KP-014）。

背景（2026-11-27 dsb-00 首败复盘）：
  dsb-00 render FAIL = ASSET_MISSING（index.html 的 loadFigure 找不到教材图 1-3）。
  修复轮无法"修"出一个缺失的文件 —— 真图必须在 codegen/render 之前预置进
  runs/<seg>/code/assets/（捕获器 web2d_capture.mjs 会把该目录全量注入为
  P103_ASSET_DATA 等四个全局别名，同时 './assets/<file>' 路径式加载也命中）。

做法：
  对 MAP 中每个段，把 设计基础/_figs_v1/png/figN-M.png 复制为多个别名
  （覆盖各代 codegen 的命名习惯：textbook-fig-N-M.png / fig-N-M.png /
  figN-M.png / textbook-N-M.png / 教材图 N-M.png），落到
  runs/<seg>/code/assets/ 与 runs/<seg>/assets/ 双份（种子期口径）。

用法：
  python _dsb_place_figs.py            # 预置 MAP 全部段
  python _dsb_place_figs.py dsb-00      # 只预置指定段（逗号分隔亦可）

维护：
  B4/B5 的 topic 写完后把对证位图号补进 MAP（分段方案 v1 的对证位分配）。
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIGS = ROOT / "设计基础" / "_figs_v1" / "png"

# seg -> 对证位图号（"N-M"）。对证位每段唯一一张教材原图。
MAP = {
    # B1
    "dsb-00": "1-3",
    "dsb-1-01": "1-1", "dsb-1-02": "1-5", "dsb-1-03": "1-2", "dsb-1-04": "1-4",
    "dsb-2-01": "2-2", "dsb-2-02": "2-3", "dsb-2-04": "2-5", "dsb-2-05": "2-7",
    # B2
    "dsb-3-01": "3-2", "dsb-3-02": "3-4", "dsb-3-03": "3-5", "dsb-3-04": "3-1",
    "dsb-4-01": "4-1", "dsb-4-02": "4-2", "dsb-4-03": "4-5", "dsb-4-04": "4-6",
    "dsb-5-01": "5-1", "dsb-5-02": "5-3", "dsb-5-03": "5-4", "dsb-5-04": "5-5",
    # B3
    "dsb-6-01": "6-1", "dsb-6-02": "6-3", "dsb-6-03": "6-4", "dsb-6-04": "6-5",
    "dsb-7-01": "7-1", "dsb-7-02": "7-2", "dsb-7-03": "7-3", "dsb-7-04": "7-5",
    "dsb-8-01": "8-1", "dsb-8-02": "8-2", "dsb-8-03": "8-3", "dsb-8-04": "8-5",
    # B4 / B5：topic 写完后补（9-x / 10-x / 11-x / 12-x / ca-x）
}


def aliases(fig: str) -> list[str]:
    n, m = fig.split("-")
    return [
        f"textbook-fig-{n}-{m}.png",   # 规范名（真图清单里写这个）
        f"fig-{n}-{m}.png",
        f"fig{n}-{m}.png",             # 种子期命名
        f"textbook-{n}-{m}.png",
        f"教材图 {n}-{m}.png",
    ]


def place(seg: str, fig: str) -> int:
    src = FIGS / f"fig{fig}.png"
    if not src.exists():
        print(f"[MISS] {seg}: 图源不存在 {src}")
        return 0
    count = 0
    for base in (ROOT / "runs" / seg / "code" / "assets", ROOT / "runs" / seg / "assets"):
        base.mkdir(parents=True, exist_ok=True)
        for name in aliases(fig):
            shutil.copy2(src, base / name)
            count += 1
    return count


def main() -> None:
    segs = sys.argv[1].split(",") if len(sys.argv) > 1 else sorted(MAP)
    total = 0
    for seg in segs:
        fig = MAP.get(seg)
        if not fig:
            print(f"[SKIP] {seg}: 不在 MAP（B4/B5 待补）")
            continue
        n = place(seg, fig)
        total += n
        print(f"[OK] {seg} -> 图{fig} x{n} 份（双目录 x 五别名）")
    print(f"完成：{len(segs)} 段 / {total} 份文件")


if __name__ == "__main__":
    main()
