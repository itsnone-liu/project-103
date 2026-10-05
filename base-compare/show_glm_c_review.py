#!/usr/bin/env python3
import json
B = (r'D:\qjcNetDiskDownload\deepseek-harness\project\103'
     r'\base-compare\case-c\glm\review')
for v in ('v1', 'v2'):
    c = json.load(open(fr'{B}\critique_{v}.json', encoding='utf-8'))
    print(f"== {v}: {c.get('verdict')}, {len(c.get('issues', []))} issues, "
          f"align={str(c.get('storyboard_alignment'))[:120]}")
    for i in c.get('issues', []):
        print(f"  [{i.get('severity')}] dim{i.get('dimension')}: "
              f"{(i.get('problem') or '')[:90]}")
m = json.load(open(fr'{B}\repair_meta.json', encoding='utf-8'))
u = m.get('usage', {})
print('repair:', m.get('secs'), 's finish', m.get('finish'),
      'in', u.get('prompt_tokens'), 'out', u.get('completion_tokens'),
      'reasoning', (u.get('completion_tokens_details') or {}).get('reasoning_tokens'))
