# -*- coding: utf-8 -*-
"""_dsb_gallery.py — 设计基础批产画廊页生成器（B1–B5 复用）。

用法:
    python -X utf8 _dsb_gallery.py [B1 B2 ...]

读 _dsb_batch_state.json（驱动器门禁结果）+ runs/<seg>/out/（final_*.mp4、qa_sheet.jpg）
+ runs/<seg>/topic-*.md（标题），生成 设计基础/_gallery_dsb_batches.html。
路由约定（需在 _serve_t1.py 的动态正则里加 dsbv 前缀）:
    /dsbv/<seg>.mp4 → runs/<seg>/out/final_<seg>.mp4
    /dsbv/<seg>-sheet.jpg → runs/<seg>/out/qa_sheet.jpg
    /dsbv/<seg>.md → runs/<seg>/topic-<seg>.md
页面按批次分节，只列 PASS 段；未跑批次整节省略。
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "_dsb_batch_state.json"

BATCHES = {
    "B1": ["dsb-00", "dsb-1-01", "dsb-1-02", "dsb-1-03", "dsb-1-04",
           "dsb-2-01", "dsb-2-02", "dsb-2-04", "dsb-2-05"],
    "B2": ["dsb-3-01", "dsb-3-02", "dsb-3-03", "dsb-3-04",
           "dsb-4-01", "dsb-4-02", "dsb-4-03", "dsb-4-04",
           "dsb-5-01", "dsb-5-02", "dsb-5-03", "dsb-5-04"],
    "B3": ["dsb-6-01", "dsb-6-02", "dsb-6-03", "dsb-6-04",
           "dsb-7-01", "dsb-7-02", "dsb-7-03", "dsb-7-04",
           "dsb-8-01", "dsb-8-02", "dsb-8-03", "dsb-8-04"],
    "B4": ["dsb-9-01", "dsb-9-02", "dsb-9-03", "dsb-9-04",
           "dsb-10-01", "dsb-10-02", "dsb-10-03", "dsb-10-04", "dsb-10-05"],
    "B5": ["dsb-11-01", "dsb-11-02", "dsb-11-03", "dsb-11-04", "dsb-11-05",
           "dsb-12-01", "dsb-12-02", "dsb-12-03", "dsb-12-04", "dsb-12-05",
           "dsb-ca1", "dsb-ca2"],
}
BATCH_DESC = {
    "B1": "第 1 批 · 前言与第 1—2 章（看见与记录）",
    "B2": "第 2 批 · 第 3—5 章（构成、秩序与空间）",
    "B3": "第 3 批 · 第 6—8 章（身体、材料与光）",
    "B4": "第 4 批 · 第 9—10 章（色彩与建造）",
    "B5": "第 5 批 · 第 11—12 章与案例专题（表达与综合）",
}

TITLE_FALLBACK = {
    "dsb-2-03": "42 个人经过，需要几把椅子（种子 1）",
    "dsb-5-05": "54㎡里，路、坐、转身、树池之后还剩多少（种子 2）",
}


def seg_title(seg: str) -> str:
    if seg in TITLE_FALLBACK:
        return TITLE_FALLBACK[seg]
    topic = ROOT / "runs" / seg / f"topic-{seg}.md"
    if topic.exists():
        m = re.search(r"^#\s*topic-\S+\s+(.+)$",
                      topic.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip()
    return seg


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def main() -> None:
    want = [b for b in sys.argv[1:] if b in BATCHES] or list(BATCHES)
    state: dict = {}
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding="utf-8"))

    cards: list[str] = []
    n_pass = 0
    for b in want:
        segs = BATCHES[b]
        passed = [s for s in segs if state.get(s, {}).get("pass")]
        if not passed:
            continue
        n_pass += len(passed)
        cards.append(f'<section class="section"><h2>{esc(BATCH_DESC[b])}'
                     f'<span class="count">{len(passed)}/{len(segs)} 段 · 全 PASS</span></h2>')
        cards.append('<div class="grid">')
        for seg in passed:
            info = state[seg]
            title = esc(seg_title(seg))
            dur = info.get("duration_s")
            sents = info.get("sentences")
            mins = info.get("minutes")
            model = info.get("model", "?")
            cards.append(
                f'<figure class="card"><video controls preload="metadata" '
                f'poster="/dsbv/{esc(seg)}-sheet.jpg">'
                f'<source src="/dsbv/{esc(seg)}.mp4?v={int(float(dur))}" type="video/mp4">'
                f"</video>"
                f'<figcaption><b>{esc(seg)}</b> {title}'
                f'<span class="meta">{dur:.0f}s · {sents} 句 · {model} · {mins:.0f}min</span>'
                f'<a class="doc" href="/dsbv/{esc(seg)}.md">课件脚本</a></figcaption></figure>')
        cards.append("</div></section>")

    total = len(state)
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>《设计基础》视频课件 · 批产画廊</title>
<style>
:root{{--bg:#0c0d10;--panel:#14161b;--line:#2a2e37;--ink:#f1eee7;--sub:#a7a399;
--muted:#706d65;--accent:#c46d4e;--accent2:#e0a07f;--ok:#7cc6a1}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(1200px 600px at 75% -10%,#2a1b16 0,var(--bg) 55%);
color:var(--ink);font:16px/1.75 system-ui,"Microsoft YaHei","PingFang SC",sans-serif}}
a{{color:var(--accent2);text-decoration:none}}a:hover{{text-decoration:underline}}
.wrap{{max-width:1180px;margin:0 auto;padding:46px 22px 70px}}
.eyebrow{{font-size:12px;letter-spacing:.18em;color:var(--accent2);text-transform:uppercase}}
h1{{font-size:clamp(26px,4vw,46px);line-height:1.2;margin:14px 0 10px;font-weight:650;letter-spacing:-.02em}}
.lead{{color:var(--sub);max-width:860px;margin:0 0 10px;font-size:16.5px}}
.badges{{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 26px}}
.badge{{font-size:12px;color:var(--sub);border:1px solid var(--line);background:#111318;
border-radius:999px;padding:4px 11px}}
.badge.ok{{color:var(--ok);border-color:#2e5544}}
.section{{margin-top:36px}}
.section h2{{font-size:20px;margin:0 0 4px;font-weight:620}}
.count{{font-size:12.5px;color:var(--muted);margin-left:12px;font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px;margin-top:14px}}
.card{{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden}}
.card video{{display:block;width:100%;aspect-ratio:16/9;background:#000}}
.card figcaption{{padding:10px 13px 12px;font-size:13.5px;color:var(--ink)}}
.card figcaption b{{color:var(--accent2);font-weight:600;margin-right:6px}}
.card .meta{{display:block;font-size:11.5px;color:var(--muted);margin-top:3px}}
.card .doc{{display:inline-block;margin-top:7px;border:1px solid var(--line);
background:#101216;border-radius:7px;padding:3px 9px;font-size:11.5px}}
.foot{{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
color:var(--muted);font-size:12px}}
</style>
</head>
<body><div class="wrap">
<div class="eyebrow">103 · 视频课件画廊 · 设计基础</div>
<h1>批产画廊 · {n_pass} 段出片</h1>
<p class="lead">《设计基础：观察、构成与微空间建造》54 段批产成片：每段 290—345s、
50—54 句、龙小淳配音、字幕单层烧录、对证位教材真图（KP-014）。
种子 1（dsb-2-03）与种子 2（dsb-5-05）在各自专页；本页列 B1—B5 批产段。</p>
<div class="badges">
<span class="badge ok">{n_pass} 段门禁全 PASS</span>
<span class="badge">1920×1080 / 24fps</span>
<span class="badge">时长门禁 ≥270s</span>
<span class="badge">QA: blank 0 / 无冻结帧</span>
<span class="badge">对证位真图预置</span>
</div>
{''.join(cards)}
<div class="foot">口径：视频内数字均为教材口径并分层标注（已核实/教学常用值/教学假设/须核验）；
结构与节点做法须专业核验。页面由 _dsb_gallery.py 生成（{total} 段已记录）。</div>
</div></body></html>"""
    out = ROOT / "设计基础" / "_gallery_dsb_batches.html"
    out.write_text(html, encoding="utf-8")
    print(f"[OK] {out} — {n_pass} 段（{total} 段在册）")


if __name__ == "__main__":
    main()
