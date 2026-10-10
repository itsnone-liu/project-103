"""_bill_all.py — 本轮全部 produce/visual-repair 日志的 token 账单。"""
import re
from pathlib import Path

call_re = re.compile(r'\[[^\]]+\]\s+(storyboard|decide|codegen|repair\S*|visual\S*)\s*[:：](.*)$')
tok_re = re.compile(r'\((\d+)\s*tok\)')
vrep_re = re.compile(r'visual-repair: 新代码 (\d+) chars')

LOGS = [
    ("T3 produce", r"runs\envpsy-t3-intro\produce2.log"),
    ("T4 produce", r"runs\envpsy-t4-91\produce.log"),
    ("T2 vrepair", r"runs\envpsy-t2-94\visual-repair.log"),
    ("T1hr vrepair", r"runs\envpsy-t1-61-hr\visual-repair.log"),
    ("T3 vrepair1(CORS失败)", r"runs\envpsy-t3-intro\visual-repair.log"),
    ("T3 vrepair2", r"runs\envpsy-t3-intro\visual-repair2.log"),
]
for name, path in LOGS:
    raw = Path(path).read_bytes()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    total, parts, vfix = 0, [], None
    for line in text.splitlines():
        m = call_re.search(line)
        if m:
            t = tok_re.search(m.group(2))
            if t:
                parts.append(f"{m.group(1)}={t.group(1)}")
                total += int(t.group(1))
        v = vrep_re.search(line)
        if v:
            vfix = v.group(1)
    detail = " + ".join(parts) if parts else "(visual-repair 调用未记tok)"
    suffix = f" [新代码 {vfix} chars]" if vfix else ""
    print(f"{name}: {detail} => {total} tok{suffix}")
