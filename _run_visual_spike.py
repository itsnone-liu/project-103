# -*- coding: utf-8 -*-
"""Paired Sol codegen/render experiment: legacy context vs explicit documentary visual design."""
import json, re, sys, time
from pathlib import Path
ROOT=Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0,str(ROOT))
from pipeline import llm, prompts, profile
from pipeline.adapters import web2d
from pipeline import qa

BASE=ROOT/"runs"/"urban-doc-style-spike"
BASE.mkdir(parents=True,exist_ok=True)
SB="""## Narration
1. At dawn, a worker leaves a quiet village and follows the rail line toward the city.
2. The old map shows one distant center; the new city is a web of neighborhoods.
3. Distance used to cost a day; now a railway compresses the journey into an hour.
4. At the station, people, jobs, shops and homes gather around a single platform.
5. Each arriving train adds paths; those paths meet, cross and create new choices.
6. But the center grows crowded, and the same network pushes housing outward.
7. Pull back: the city is not a dot, but a living field of connections and tradeoffs.
8. One question remains: what does the next connection make possible, and for whom?
## Parameters
Duration=60s; eight narration cues; 1920x1080.
## Math-check
8 cues; final end=60s.
"""
TIMING={"starts":[0,7.5,15,22.5,30,37.5,45,52.5],"total":60.0}
DEC={"backend":"WEB_2D","reason":"2D canvas for deterministic full-frame illustration and motion"}
TOPIC="""# Urbanization mini-documentary visual subject
Show one worker's journey from rural edge into an expanding city; visualize how transport compresses distance and creates agglomeration, then reveal crowding and outward housing pressure. This is an explanatory documentary scene, not a slide deck."""
PLAN="""Free visual direction: a coherent, full-bleed illustrated world, not a deck of slides. Establish a recurring tiny amber commuter and a twilight city palette. Compose layered foreground/midground/background: field, rail, station, city silhouette. Let the rail become a glowing route; let route intersections grow into blocks, windows and people. Use continuous spatial staging and graphic match cuts: the map line becomes the railway, station platform becomes a city street, expanding rings become housing blocks. Change composition scale and silhouette between beats (wide landscape, lateral journey, overhead network, compressed crowded street, high pullback), but keep one visual world. Minimal typography integrated into negative space; no persistent header/right sidebar/bottom caption panel; no rounded-card grid, border boxes or repeated slide template. Illustrations should be concrete and recognizable rather than abstract rectangles and arrows. Every cue changes a visible object or spatial relation; animate paths and city layers deterministically as a pure function of t. End with a clear, authored image, not a generic summary card."""
STYLE="Full-bleed illustrated documentary world, layered city scenes, one recurring commuter, lateral travel and overhead spatial reveals. Ban fixed card/template layout: no persistent header, right panel, bottom narration strip, rounded-card grids. Use few concrete recognizable objects (rail, station, blocks, windows, people), changing composition and scale; transitions should carry one shape into the next. Motion must depict the narrated process (path travels, blocks emerge, crowd compresses, camera pullback), not decorative pulses. Typography embedded sparingly in scene negative space. Deterministic state=F(t); no true photography required."
PROFILE_B={"visual":{"style_pack":"urban_documentary_spatial","style_note":STYLE},"backend":{"allowed":["web_2d"]}}

def save_code(label, text, meta):
    d=BASE/label; (d/"code").mkdir(parents=True,exist_ok=True); (d/"out").mkdir(exist_ok=True)
    m=re.search(r"```(?:\w+)?\n(.*?)```",text,re.S)
    code=(m.group(1) if m else text).strip()
    (d/"code"/"index.html").write_text(code,encoding="utf-8")
    (d/"code"/".done").write_text("ok",encoding="utf-8")
    (d/"usage.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    return d,code

for label, prof, topic, plan, rich in [
    ("A_legacy",{},"","",False),
    ("B_explicit",PROFILE_B,TOPIC,PLAN,True),
]:
    started=time.time()
    msgs=prompts.codegen_prompt(DEC,SB,TIMING,prof,topic=topic,visual_plan=plan,include_visual_context=rich)
    response,meta=llm.call("sol",msgs,think="low",effort="high")
    d,code=save_code(label,response,meta)
    print(f"[{label}] code chars={len(code)} usage={meta.get('usage')} elapsed={time.time()-started:.0f}s",flush=True)
    res=web2d.render(d,TIMING)
    if not res.get("ok"):
        print(f"[{label}] RENDER FAIL {res.get('errors')}",flush=True); continue
    rep=qa.check(res["video"],TIMING,d)
    print(f"[{label}] render={res['video']} QA={rep.get('pass')} frame_variance={rep.get('checks',{}).get('frame_variance')}",flush=True)
    (d/"qa.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8")
print("DONE",flush=True)
