# -*- coding: utf-8 -*-
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from pipeline.qa import check
OUT=ROOT/'runs'/'envpsy-case1-full'; timing=json.loads((ROOT/'audio'/'timing_envpsy-case1.json').read_text(encoding='utf-8'))
video=OUT/'out'/'final_envpsy-case1-full.mp4'
if not video.exists(): raise SystemExit(f'missing muxed candidate {video}')
rep=check(str(video),timing,OUT);print(json.dumps(rep,ensure_ascii=False,indent=2));
if not rep.get('pass'):raise SystemExit(2)
