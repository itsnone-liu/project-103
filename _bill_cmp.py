"""_bill_cmp.py — v1 vs hr 两个 produce.log 的 token 账单对比。"""
import re
from pathlib import Path

call_re = re.compile(r'\[[^\]]+\]\s+(storyboard|decide|codegen|repair\S*|visual\S*)\s*[:：](.*)$')
tok_re = re.compile(r'\((\d+)\s*tok\)')

for name, path in [("v1 默认推理", "runs/envpsy-t1-61/produce.log"),
                   ("hr 高推理", "runs/envpsy-t1-61-hr/produce.log")]:
    raw = Path(path).read_bytes()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    total, parts = 0, []
    for line in text.splitlines():
        m = call_re.search(line)
        if m:
            t = tok_re.search(m.group(2))
            if t:
                parts.append(f"{m.group(1)}={t.group(1)}")
                total += int(t.group(1))
    print(f"{name}: {' + '.join(parts) or '(无记录)'} => {total:,} tok (logged)")
