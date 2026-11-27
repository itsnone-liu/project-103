# -*- coding: utf-8 -*-
"""_dsb_append_assetlist.py — 给 DSB topic 追加"真图清单"（KP-014）。

真图文件已由 _dsb_place_figs.py 预置进 runs/<seg>/code/assets/（五别名×双目录）。
本脚本把规范名写进 topic，使 codegen 按 KP-014 契约用
assets/textbook-fig-N-M.png 精确加载对证位原图，杜绝命名漂移与静默退化。
幂等：文末已有的真图清单块会被本脚本整体替换为最新版。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 直接读 _dsb_place_figs.py 的 MAP，单一事实源（findall 抓同行的多个条目）
sys_map: dict[str, str] = {}
for line in (ROOT / "_dsb_place_figs.py").read_text(encoding="utf-8").splitlines():
    for seg, fig in re.findall(r'"((?:dsb)[\w-]*)":\s*"(\d+-\d+)"', line):
        sys_map[seg] = fig

BLOCK = """## 真图清单（对证位真图，KP-014）

- `assets/textbook-fig-{fig}.png` = 教材图 {fig}（本片唯一真图）：严格按上文"对证位"小节的装帧出现一次（原图裁切叠出 → 角标"教材图 {fig}" → 立即回到 Canvas 重绘），不铺底、不连用超过一句。文件已预置在 code/assets/（别名 `fig{nf}.png` / `fig-{fig}.png` / `textbook-{fig}.png` / `教材图 {fig}.png` 同源同图，任一命中即可）。
"""

TAIL_RE = re.compile(r"\n## 真图清单（对证位真图，KP-014）\n.*\Z", re.S)


def main() -> None:
    done = 0
    for seg, fig in sorted(sys_map.items()):
        topic = ROOT / "runs" / seg / f"topic-{seg}.md"
        if not topic.exists():
            continue
        text = topic.read_text(encoding="utf-8")
        n, m = fig.split("-")
        block = BLOCK.format(fig=fig, nf=f"{n}-{m}")
        text = TAIL_RE.sub("", text).rstrip("\n") + "\n" + block
        topic.write_text(text + "\n", encoding="utf-8")
        done += 1
    print(f"真图清单就位：{done} 个 topic（含替换旧块）")


if __name__ == "__main__":
    main()
