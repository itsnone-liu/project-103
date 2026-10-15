# -*- coding:utf-8 -*-
import json,re,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'runs'/'envpsy-case1'
OUT=ROOT/'runs'/'envpsy-case1-full'
html=(OUT/'code'/'index.html').read_text(encoding='utf-8')
sb=(SRC/'storyboard.md').read_text(encoding='utf-8')
units=re.findall(r'^\d+\.\s+(.+?)(?=\n\d+\.|\n\n## Parameters)',sb,re.M|re.S)
timing=json.loads((ROOT/'audio'/'timing_envpsy-case1.json').read_text(encoding='utf-8'))
scene=json.loads((ROOT/'audio'/'scene_envpsy-case1.json').read_text(encoding='utf-8'))
full=json.loads((OUT/'timing.json').read_text(encoding='utf-8'))
assert len(units)==48 and len(scene['sentences'])==48 and len(timing['starts'])==48
assert timing['total']==601.18 and full==timing
script=re.search(r'const narration=\[(.*?)\n\];',html,re.S).group(1)
assert len(re.findall(r'^"',script,re.M))==48
assert 'const duration=601.18;' in html
assert all(x in html for x in ['"80%"','80%','63%','35%','11%','6%','74%','4500万'])
assert 'HUD' not in html or 'chrome' in html
print(json.dumps({'narration_cues':len(units),'script_cues':48,'duration':timing['total'],'narration_source_sha256':hashlib.sha256((ROOT/'audio'/'narration_envpsy-case1.wav').read_bytes()).hexdigest(),'candidate_code_bytes':len(html.encode()),'checks':'PASS'},ensure_ascii=False))
