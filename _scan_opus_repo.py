# -*- coding: utf-8 -*-
import csv

rows = list(csv.DictReader(open(
    r"D:\qjcNetDiskDownload\deepseek-harness\project\103\research\awesome-opus-5.5-video\cases\_classified.csv",
    encoding="utf-8-sig")))
print("total", len(rows))

kw = ["建筑", "城市", "街道", "广场", "都市", "规划", "空间", "景观", "桥梁", "地铁", "地图",
      "house", "city", "urban", "street", "plaza", "architect", "building", "town", "bridge",
      "metro", "map", "纪录片", "documentary", "案例", "复盘", "改造", "五千年", "历史"]
seen = set()
for r in rows:
    t = r["title"]
    if any(k.lower() in t.lower() for k in kw) and t not in seen:
        seen.add(t)
        print(f"{r['cat'][:6]:<8} | {t} | full提示词={'Y' if r['full'] else 'N'}")
