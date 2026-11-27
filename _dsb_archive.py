# -*- coding: utf-8 -*-
"""_dsb_archive.py — 设计基础批产归档暂存器（B1–B5 复用）。

用法:
    python -X utf8 _dsb_archive.py B1

从 _dsb_batch_state.json 取 PASS 段，把每段结果文件复制进 _archive_stage/<批次>/<段>/:
    final_<seg>.mp4 / final_<seg>.ass / qa_report.json / qa_sheet.jpg / topic-<seg>.md
并在 _archive_stage/<批次>/ 生成 manifest.json（sha256 + 标题 + 门禁摘要 + 汇总）。
随后手动执行:
    python D:\\baidu-sync\\bdpan.py put _archive_stage\\<批次> /apps/ss2archive/103/设计基础/视频课件/<批次>
上传后 ls 核对字节数，再删暂存目录（runs/ 原件保留供画廊服务）。
"""
from __future__ import annotations
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "_dsb_batch_state.json"
STAGE = ROOT / "_archive_stage"

BATCH_SEGMENTS = {
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

RESULT_FILES = ("final_{seg}.mp4", "final_{seg}.ass",
                "qa_report.json", "qa_sheet.jpg", "topic-{seg}.md")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def seg_title(seg: str) -> str:
    topic = ROOT / "runs" / seg / f"topic-{seg}.md"
    if topic.exists():
        m = re.search(r"^#\s*topic-\S+\s+(.+)$",
                      topic.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip()
    return seg


def main() -> None:
    batch = sys.argv[1] if len(sys.argv) > 1 else ""
    if batch not in BATCH_SEGMENTS:
        print(f"用法: python -X utf8 _dsb_archive.py B1|B2|B3|B4|B5")
        sys.exit(2)
    if not STATE.exists():
        print("[ERR] 无 _dsb_batch_state.json")
        sys.exit(1)
    state = json.loads(STATE.read_text(encoding="utf-8"))

    dst = STAGE / batch
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)

    segs_out, n_files, n_bytes, missing = [], 0, 0, []
    for seg in BATCH_SEGMENTS[batch]:
        info = state.get(seg)
        if not info or not info.get("pass"):
            missing.append(seg)
            continue
        seg_dir = dst / seg
        seg_dir.mkdir()
        files = []
        for pat in RESULT_FILES:
            name = pat.format(seg=seg)
            if name.startswith("topic-"):
                src = ROOT / "runs" / seg / name
            else:
                src = ROOT / "runs" / seg / "out" / name
            if not src.exists():
                print(f"[WARN] {seg}: 缺 {src.relative_to(ROOT)}")
                continue
            shutil.copy2(src, seg_dir / name)
            b = src.stat().st_size
            files.append({"name": f"{seg}/{name}", "bytes": b, "sha256": sha256(src)})
            n_files += 1
            n_bytes += b
        segs_out.append({
            "segment": seg, "title": seg_title(seg),
            "duration_s": info.get("duration_s"), "sentences": info.get("sentences"),
            "model": info.get("model"), "produce_minutes": info.get("minutes"),
            "qa": {k: info.get(k) for k in ("qa_pass", "blank_frames",
                                            "freeze_windows", "max_diff")},
            "files": files,
        })

    manifest = {
        "course": "设计基础",
        "batch": batch,
        "created": "2026-11-27",
        "pipeline": "103 _dsb_batch.py 批产（sol→ds→glm 链，门禁: 时长≥270s/QA pass/blank 0/无冻结）",
        "segments": segs_out,
        "totals": {"segments_pass": len(segs_out), "segments_pending": missing,
                   "files": n_files, "bytes": n_bytes},
    }
    (dst / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    print(f"[OK] 暂存 {dst} — {len(segs_out)} 段 {n_files} 文件 "
          f"{n_bytes/1e6:.1f}MB；未出片: {missing or '无'}")
    print(f"     下一步: python D:\\baidu-sync\\bdpan.py put {dst} "
          f"/apps/ss2archive/103/设计基础/视频课件/{batch}")


if __name__ == "__main__":
    main()
