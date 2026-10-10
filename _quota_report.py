"""_quota_report.py — 从 produce.log 汇总每次 LLM 调用的 token 消耗（额度账单）。
用法: python _quota_report.py [runs/envpsy-t1-61/produce.log]
"""
import re, sys
from pathlib import Path

log = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/envpsy-t1-61/produce.log")
text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
lines = [l for l in text.splitlines() if l.strip()]

# produce.py 的日志行形如: [title] storyboard: 40 句 (12345 tok) / codegen: 88231 chars (23456 tok)
call_re = re.compile(r'\[(?P<title>[^\]]+)\]\s+(?P<stage>storyboard|decide|codegen|repair\(?[^\):]*\)?|visual.repair)\s*[:：](?P<rest>.*)$')
tok_re = re.compile(r'\((\d+)\s*tok\)')

total = 0
rows = []
pending_stage = None
for l in lines:
    m = call_re.search(l)
    if m:
        pending_stage = m.group('stage').strip()
        t = tok_re.search(m.group('rest'))
        if t:
            rows.append((pending_stage, int(t.group(1))))
            pending_stage = None

print(f"{'阶段':<14}{'completion tok':>14}")
print('-' * 30)
for stage, tok in rows:
    print(f"{stage:<14}{tok:>14,}")
    total += tok
print('-' * 30)
print(f"{'合计':<14}{total:>14,}")
print(f"\n（注：仅 completion tokens——5h 窗口额度主要按输出/请求次数计；prompt tokens 各阶段 3k-15k 不等）")
