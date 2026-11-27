# -*- coding: utf-8 -*-
"""考务五件套通用一致性检查（12 章课程）。

用法:
  python _qa_kaowu_generic.py <课程目录> <视频段号前缀> <成片段数>

检查:
  1) 考试大纲：12 章全覆盖、权重合计 100%；
  2) 样卷：题号 1..24 连续、各题型分值与总分 100 一致；
  3) 样卷答案：题号集合与样卷一致；
  4) 题库：252 题、每章 21 题、题型 96/36/72/36/12、答案与依据齐全、题号唯一；
  5) 随堂测验：段号覆盖全部成片、索引行数一致、每题有答案与依据。
"""
import re
import sys
from pathlib import Path

DIR = Path(sys.argv[1]).resolve()
PREFIX = sys.argv[2] if len(sys.argv) > 2 else "seg"
NSEG = int(sys.argv[3]) if len(sys.argv) > 3 else 0
KAO = DIR / "考务"

FILES = {
    "大纲": KAO / "考试大纲_v0.1.md",
    "样卷": KAO / "样卷_v1.md",
    "答案": KAO / "样卷_答案_v1.md",
    "题库": KAO / "题库_v1.md",
    "随堂": KAO / "随堂测验题_v1.md",
}

problems = []


def need(cond, msg):
    if not cond:
        problems.append(msg)


def read(name):
    p = FILES[name]
    if not p.exists():
        problems.append(f"缺少文件：{p}")
        return ""
    return p.read_text(encoding="utf-8")


def check_outline(t):
    chs = set(int(x) for x in re.findall(r"第(\d{1,2})章", t))
    need(chs >= set(range(1, 13)), f"大纲缺章：{sorted(set(range(1, 13)) - chs)}")
    pcts = [int(x) for x in re.findall(r"\|\s*(\d{1,2})%\s*\|", t)]
    if pcts:
        total = sum(pcts[:12])
        need(total == 100, f"大纲前 12 个权重合计 {total}% ≠ 100%")
    else:
        problems.append("大纲未找到权重百分比行")
    return f"大纲：12 章覆盖，权重行 {len(pcts)} 个"


def check_paper(t):
    nums = sorted(set(int(n) for n in re.findall(r"^\s*(?:###\s*)?(\d{1,2})[．.、]", t, re.M)))
    need(nums == list(range(1, 25)), f"样卷题号异常：{nums}")
    pts = [int(x) for x in re.findall(r"每题\s*(\d{1,2})\s*分", t)]
    total = sum(int(n) * p for n, p in zip([8, 5, 6, 3, 1, 1], pts)) if len(pts) >= 6 else None
    if total is not None:
        need(total == 100, f"样卷按各段「每题 N 分」折算总分 {total} ≠ 100")
    return f"样卷：题号 1–24（{len(nums)} 个），分段分值 {pts[:6]}，折算 {total}"


def check_answers(t):
    nums = set(int(n) for n in re.findall(r"^\s*(?:###\s*)?(\d{1,2})[．.、]", t, re.M))
    nums |= set(int(n) for n in re.findall(r"^\|\s*(\d{1,2})\s*\|", t, re.M))
    nums = sorted(nums)
    need(nums == list(range(1, 25)), f"答案题号异常：{nums}")
    return f"答案：题号 1–24（{len(nums)} 个）"


def check_bank(t):
    ids = re.findall(r"^### (Z\d+[DMPSC]\d+)\s*$", t, re.M)
    need(len(ids) == 252, f"题库题数 {len(ids)} ≠ 252")
    need(len(set(ids)) == len(ids), "题库存在重复题号")
    per, types = {}, {}
    for q in ids:
        m = re.fullmatch(r"Z(\d+)([DMPSC])(\d+)", q)
        per[int(m.group(1))] = per.get(int(m.group(1)), 0) + 1
        types[m.group(2)] = types.get(m.group(2), 0) + 1
    need(all(v == 21 for v in per.values()) and len(per) == 12, f"题库分章不均：{per}")
    need(types == {"D": 96, "M": 36, "P": 72, "S": 36, "C": 12}, f"题库题型分布异常：{types}")
    blocks = re.split(r"^### Z\d+[DMPSC]\d+\s*$", t, flags=re.M)[1:]
    need(all(re.search(r"\*\*(参考)?答案", b) for b in blocks), "题库有题缺答案")
    need(all("依据" in b for b in blocks), "题库有题缺依据")
    return f"题库：{len(ids)} 题，12 章 × 21，题型 {types}"


def check_quiz(t):
    segs = set(re.findall(rf"{re.escape(PREFIX)}-\d+-\d+", t))
    if NSEG:
        need(len(segs) == NSEG, f"随堂测验段号 {len(segs)} ≠ {NSEG}")
    idx = re.search(r"## 总索引表(.*?)\n## ", t, re.S)
    rows = re.findall(r"^\|\s*\d+\s*\|", idx.group(1), re.M) if idx else []
    if NSEG:
        need(len(rows) == NSEG, f"随堂索引表 {len(rows)} 行 ≠ {NSEG}")
    na = len(re.findall(r"\*\*答案\*\*", t))
    nb = len(re.findall(r"\*\*依据\*\*", t))
    if NSEG:
        need(na >= NSEG, f"随堂答案 {na} 条 < {NSEG}")
        need(nb >= NSEG, f"随堂依据 {nb} 条 < {NSEG}")
    dist = {k: len(re.findall(r"\*\*答案\*\*[：:]" + k, t)) for k in "ABCD"}
    return f"随堂：{len(segs)} 段 / 索引 {len(rows)} 行，单选分布 {dist}"


def main():
    print(f"== {DIR.name} 考务五件套检查 ==")
    for name, fn in [("大纲", check_outline), ("样卷", check_paper), ("答案", check_answers),
                     ("题库", check_bank), ("随堂", check_quiz)]:
        t = read(name)
        if t:
            print("·", fn(t))
    print()
    if problems:
        print("未通过：")
        for p in problems:
            print("  ✗", p)
        return 2
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())