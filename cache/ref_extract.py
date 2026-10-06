import re, html, sys
from pathlib import Path

CACHE = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103\cache")


def text_of(p):
    raw = p.read_text(encoding="utf-8", errors="replace")
    txt = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
    return re.sub(r"\s+", " ", txt)


name = sys.argv[1] if len(sys.argv) > 1 else "transformer"
txt = text_of(CACHE / f"ref_{name}.html")
if name == "transformer":
    m = re.search(r"Creator's brief.{0,60}?chars.{0,200}?(.{20,400}?)(Source:|Tools the)", txt)
    print("PROMPT:", m.group(1).strip()[:400] if m else "(no match) " + txt[:500])
elif name == "jev":
    # 复盘文：抽叙事要点（Manim/narration/fact-check/chapter/thumbnail 关键词附近）
    keys = ["fact", "Manim", "narration", "chapter", "thumbnail", "correction", "mistake",
            "workflow", "hours", "cost", "prompt"]
    hits = []
    for k in keys:
        for m in re.finditer(rf".{{120}}{k}.{{200}}", txt, re.I):
            s = m.group(0).strip()
            if s not in hits:
                hits.append(s)
            break
    print("\n---\n".join(hits[:14]))
