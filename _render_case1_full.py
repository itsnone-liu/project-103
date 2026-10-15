# -*- coding: utf-8 -*-
"""Render and QA isolated candidate using shared audited narration/timing."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from pipeline.adapters import web2d
from pipeline import qa
OUT=ROOT/'runs'/'envpsy-case1-full'
timing=json.loads((ROOT/'audio'/'timing_envpsy-case1.json').read_text(encoding='utf-8'))
# Candidate index has exact 48-cue measured timing; web2d capture loads local fonts and checks every frame.
res=web2d.render(OUT,timing)
print('render',res,flush=True)
if not res.get('ok'):
 print('RENDER FAILED',res.get('errors',[])[:4],flush=True);sys.exit(1)
rep=qa.check(res['video'],timing,OUT)
(OUT/'out'/'qa_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print('QA',rep.get('pass'),rep.get('checks',{}).get('duration'),rep.get('checks',{}).get('frame_variance'),flush=True)
if not rep.get('pass'):sys.exit(2)
