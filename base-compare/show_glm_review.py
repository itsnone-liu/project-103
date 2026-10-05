#!/usr/bin/env python3
import json
BASE = (r'D:\qjcNetDiskDownload\deepseek-harness\project\103'
        r'\base-compare\case-a\review')
for v in ('v1', 'v2'):
    c = json.load(open(fr'{BASE}\critique_{v}.json', encoding='utf-8'))
    verdict = c.get('verdict')
    issues = c.get('issues', [])
    print(f'--- {v}: {verdict}, {len(issues)} issues')
    for i in issues:
        sev = i.get('severity')
        t = i.get('time')
        dim = i.get('dimension')
        prob = (i.get('problem') or '')[:70]
        print(f'  [{sev}] {t} dim{dim}: {prob}')
m = json.load(open(fr'{BASE}\repair_meta.json', encoding='utf-8'))
print('repair meta:', json.dumps(m, ensure_ascii=False)[:300])
