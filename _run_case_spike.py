# -*- coding: utf-8 -*-
"""60s Times Square scene-grammar spike; same Sol + deterministic WEB_2D pipeline."""
import json,re,sys,time
from pathlib import Path
ROOT=Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0,str(ROOT))
from pipeline import llm,prompts
from pipeline.adapters import web2d
from pipeline import qa
BASE=ROOT/"runs"/"urban-doc-style-spike"/"C_times_square"
BASE.mkdir(parents=True,exist_ok=True)
SB="""## Narration
1. 二〇〇八年的时代广场，汽车占住路面，人群沿着狭窄的边缘匆匆穿过。
2. 决策者面前有个问题：腾出车道，会把风险和拥堵带到哪里？
3. 试点没有先盖新建筑，几桶油漆、折叠椅和花盆，先改变了街道怎么用。
4. 商户看送货，司机看通行，行人看能不能安全地停下；同一条街，各人处境不同。
5. 留出地方让人坐下，经过不再是唯一的活动；这是一种待检验的机制，不是成功证明。
6. 评估记录，在车行道行走的行人减少百分之八十；这说的是危险接触的变化，不是风险归零。
7. 临时试点后来走向永久改造，但永久化仍需要维护、倾听和继续检查。
8. 轮到你的街道：先听谁在担心，再看人怎么走，最后决定用什么证据检验。
## Parameters
Duration=60s; eight narration cues; 1920x1080; 80% only verified quantitative result in sample.
## Math-check
Eight cues; 60s total; no fabricated quantities.
"""
TIMING={"starts":[0,7.5,15,22.5,30,37.5,45,52.5],"total":60.0}
DEC={"backend":"WEB_2D","reason":"2D deterministic full-frame illustrated street scenes"}
TOPIC="""# Times Square public-space case, one-minute visual prototype
Show the transformation of the Times Square/Broadway street from traffic-dominated intersection to experimental public space and the decision/evidence limits. Educational intent: let the viewer feel street scale, encounter the people affected, understand the reversible test and distinguish evidence from mechanism. Only use the fact in the storyboard; do not invent dimensions, counts or percentages beyond the stated 80%."""
PLAN="""Visual director plan: create an illustrated documentary, not an infographic deck. Use scene-specific full-frame compositions with a consistent authored style and a recurring street geometry. Begin with a wide oblique city intersection at dusk, concrete road surface, crosswalk stripes, blocky but recognizable tall buildings, moving cars, small pedestrians squeezed at curb. Descend/lateral travel to pedestrian scale. Use a shape-match transition from lane stripe to temporary paint; chairs and planters physically occupy curb/road; make the street change legible through the environment. Stage merchants, driver and pedestrians inside one connected street world, changing camera angle / framing, never four panels. Reveal 80% as restrained oversized typography spatially integrated into street/night-sky negative space while the pedestrian-in-car-lane path visibly shortens; no card or dashboard. End on a permanent plaza-like scene and one open question. Use painterly/vector illustration with gradients, texture hatching, atmospheric depth, varied building silhouettes, warm practical lights against indigo/plum night. Do not claim realistic film footage; code-render all assets. Use smooth continuous camera pans/zooms/tilts and authored transitions where the same line/object transforms into next scene; every cue changes the viewer's vantage or a meaningful object. No persistent header, title bar, subtitle strip, right sidebar, rounded cards, boxed panels, repeated slide layout, or all-purpose rectangles-and-connectors infographic. Build scene as a single full bleed world at each beat."""
STYLE="Full-bleed, scene-led illustrated documentary, painterly vector 2.5D with atmospheric depth and concrete street-scale objects (crosswalks, cars, sidewalk, chairs, planters, people, building facades). New composition per beat, linked by spatial continuity/match transitions; visibly move viewpoint (pan/zoom/tilt) and animate meaningful object changes. Ban persistent slide shell, card grids, panels, header/footer/subtitle bands/sidebar. Avoid abstract rectangle-and-line diagrams except brief evidence graphic integrated into a scene. Do not fake exact urban geometry. Restrained dark indigo/plum + warm amber light, textured layered shapes, varied silhouette; title/numbers sparse and integrated in negative space. Deterministic renderFrame(t)=F(t), no external network assets."
PROFILE={"visual":{"style_pack":"urban_documentary_spatial","style_note":STYLE},"backend":{"allowed":["web_2d"]}}
msgs=prompts.codegen_prompt(DEC,SB,TIMING,PROFILE,topic=TOPIC,visual_plan=PLAN,include_visual_context=True)
t0=time.time();response,meta=llm.call("sol",msgs,think="low",effort="high")
m=re.search(r"```(?:\w+)?\n(.*?)```",response,re.S);code=(m.group(1) if m else response).strip()
(BASE/"code").mkdir(exist_ok=True);(BASE/"out").mkdir(exist_ok=True)
(BASE/"code"/"index.html").write_text(code,encoding="utf-8");(BASE/"code"/".done").write_text("ok")
(BASE/"usage.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"C code chars={len(code)} usage={meta.get('usage')} elapsed={time.time()-t0:.0f}s",flush=True)
res=web2d.render(BASE,TIMING);print("render",res,flush=True)
if res.get("ok"):
 rep=qa.check(res["video"],TIMING,BASE);(BASE/"out"/"qa.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8");print("QA",rep.get("pass"),rep.get("checks",{}).get("frame_variance"),flush=True)
