# -*- coding: utf-8 -*-
"""_finish_case1.py — 案例 A 收尾：直接打包+入库（final 已过双门禁，跳过重渲）。"""
import sys
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0, str(ROOT))

import _first10 as F   # noqa: E402
import _batch6 as B    # noqa: E402

lesson = B.LESSONS[0]
F.package(lesson)
B.rebuild_course()
print("[done] case1 打包入库")
