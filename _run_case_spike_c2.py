# -*- coding: utf-8 -*-
"""C2: content-driven Times Square visual spike with varied hybrid layouts and richer solids."""
import json,re,sys,time
from pathlib import Path
ROOT=Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0,str(ROOT))
from pipeline import llm,prompts
from pipeline.adapters import web2d
from pipeline import qa
BASE=ROOT/"runs"/"urban-doc-style-spike"/"C2_times_square"
BASE.mkdir(parents=True,exist_ok=True)
SB="""## Narration
1. 二〇〇八年，汽车穿过时代广场，行人被挤在路边，车道和人行空间泾渭分明。
2. 决策者要回答的不是“广场漂不漂亮”，而是腾出路面后，风险会转移到哪里。
3. 二〇〇九年，纽约没有先造新广场，而是在街上刷漆、摆花盆和折叠椅，做一场可以撤回的试验。
4. 商户惦记送货和客流，司机担心绕行，行人想知道能否安全停下；争议来自各自不同的街道经历。
5. 椅子给人一个停下来的位置，油漆重新划定谁可以使用路面；这只是机制假说，仍要由观察检验。
6. 评估记录，在车行道行走的行人减少百分之八十；报告讲的是危险接触变化，不是风险归零。
7. 临时方案后来永久化：折叠椅成为长椅、涂装成为铺地，但维护与公众使用仍需长期负责。
8. 轮到你的街道：先听谁担心什么，再看人怎样走，最后商定什么证据足以检验改变。
## Parameters
Duration=60s; eight narration cues; 1920x1080; only verified outcome is 80% decrease in pedestrians walking in the carriageway.
## Math-check
8 narration units; final time=60s; do not invent counts or dimensions.
"""
TIMING={"starts":[0,7.5,15,22.5,30,37.5,45,52.5],"total":60.0}
DEC={"backend":"WEB_2D","reason":"deterministic Canvas 2D custom illustrations; varied scene and hybrid compositions"}
TOPIC="""# Times Square / Broadway public space pilot — visual continuity study
The one-minute teaching sample has eight narrative beats: 2008 traffic-dominated street and constrained pedestrian behavior; the mayor/transport director's unresolved decision about where risk goes; 2009 reversible paint-and-chairs pilot; merchants/drivers/pedestrians with distinct concerns; observation and mechanism hypothesis (chairs enable staying, paint reallocates public space); NYC DOT finding: pedestrians walking in the carriageway decreased 80% (not risk eliminated); pilot becomes permanent public space (folding seats → benches/materials) with stewardship obligations; transfer to viewer's local street as open question. Keep evidence vs causal interpretation clearly distinct. Do not invent additional statistics, precise dimensions, exact geometry or real historical quotations."""
PLAN="""Visual director brief for C2: The user says varied cards are welcome; only repetitive card-only PPT is bad. Build a cohesive richly colored illustrated documentary with tangible, filled-in forms, substantial opaque color masses, warm/cool light, atmospheric layering, visible surface texture/hatching/grain, cast/contact shadows, foreground occlusion and varied silhouettes. Avoid thin wireframe outlines and hollow line drawings. Retain limited palette: deep indigo/plum night + warm amber/pink pavement + teal/coral figures; colors should be saturated enough to feel solid, not washed out. Code-draw every form, no external footage/assets.

CRITICAL: change the visual proposition with each narrative beat. Eight beats require at least six visibly distinct framings/visual ideas (wide street, split/hybrid decision, overhead intervention, character/stakeholder close framing, world-integrated mechanism diagram, number integrated into street scene, before→after material transformation, final urban vista/question). Do not reuse one intersection view with only the painted ground recolored. Make the street a continuous spatial world but motivate camera cuts / push-ins / pans / perspective shift by which issue the narration raises. At 0-7.5s show narrow pedestrian edge versus dominant car lanes at street level, dense figures/cars, constrained perspective. 7.5-15s make a hybrid composition: left half scene of city traffic, right half an unboxed translucent/negative-space decision desk or risk map that grows out of the scene, not a bordered slide; transition using lane stripe. 15-22.5s overhead/slanted close view of hands/tools? Code-drawn simplified hands if practical, oil paint stripe, chairs and planters physically placed; animate chair unfolding and paint widening. 22.5-30s show stakeholder concerns through distinct human-scale POV inserts/half-frame embedded observer portraits or environmental staging (delivery cart at storefront vs driver's windshield view vs seated pedestrian's street level); avoid generic role-label signs. 30-37.5s show actual observation: flows pass vs dwell, paint boundary changes available territory; build a half-scene + translucent annotation overlay integrated in negative space (one varied card-like treatment permitted) with clear labels hypothesis/observation, no result statistic here. 37.5-45s reveal 80% with large number placed as typography in atmospheric sky/façade/surface, while an illustrative path of in-carriageway walkers visibly narrows; don't add fake counts, graph scales or cause claim; caveat remains readable. 45-52.5s show temporary-to-permanent transformation via a clear match cut/morph: folding chair unfolds into permanent bench; paint texture becomes stone paving; street-level closeup then pull to civic plaza, maintenance worker/cleaner/visitors indicate stewardship. 52.5-60s shift to a local street distinct from Times Square, lighter dawn palette/negative space; a listener hears concerns, watches a path and selects a test; end open question in an asymmetric half-card blended into illustration, not a closing slide.

Layout grammar must vary: some beats full bleed; some asymmetrical half-screen/info blend with no hard border; one or two legitimate card-like evidence/decision compositions integrated into environment; some text embedded on building/street sign; some giant kinetic typography over texture. Vary camera angle/scale, color weighting, figure scale, negative space, and scene silhouette. At least 6 distinct camera compositions, 3 kinds of transition (match shape, parallax pass/occlusion, palette/light transformation). No persistent header/sidebar/footer/progress UI, no rounded-card grid, no repetitive same-frame annotation pattern. Content-to-image audit: each narration cue must cause a recognizable, specific action or object change that could not be swapped to another cue. Keep concrete details and avoid a faceless generic dashboard. Motion should be deliberate and readable, with anticipation/ease/settle; camera is restrained and motivated, not constantly zooming. Maintain deterministic renderFrame(t)=F(t), correct cue clock, no accumulating state, exact evidence scope."""
STYLE="Hybrid documentary illustration, variable composition: full-bleed environments, asymmetrical half-scene + unboxed translucent explanation, occasional embedded card, world-space labels, large integrated numbers. No fixed persistent template. Solid saturated forms with painterly hatch/grain, contact shadows, occlusion, layered lighting; not thin outline diagrams or uniform flat boxes. Every narrative beat must introduce a content-specific visual event and at least six distinct compositions over 60s. Use street-level / oblique / overhead / POV framing as motivated by narration; code-draw real-looking but clearly illustrative faces/gestures, vehicles, pavement, chair/planter/bench. Distinct match-cut, occlusion/parallax and material/palette transition. Deterministic WEB_2D code only; no ungrounded statistics, precise city geometry or historical quotes."
PROFILE={"visual":{"style_pack":"hybrid_documentary_illustration","style_note":STYLE},"backend":{"allowed":["web_2d"]}}
msgs=prompts.codegen_prompt(DEC,SB,TIMING,PROFILE,topic=TOPIC,visual_plan=PLAN,include_visual_context=True)
t0=time.time();response,meta=llm.call("sol",msgs,think="low",effort="high")
m=re.search(r"```(?:\w+)?\n(.*?)```",response,re.S);code=(m.group(1) if m else response).strip()
(BASE/"code").mkdir(exist_ok=True);(BASE/"out").mkdir(exist_ok=True)
(BASE/"code"/"index.html").write_text(code,encoding="utf-8");(BASE/"code"/".done").write_text("ok")
(BASE/"usage.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"C2 code chars={len(code)} usage={meta.get('usage')} elapsed={time.time()-t0:.0f}s",flush=True)
res=web2d.render(BASE,TIMING);print("render",res,flush=True)
if res.get("ok"):
 rep=qa.check(res["video"],TIMING,BASE);(BASE/"out"/"qa.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8");print("QA",rep.get("pass"),rep.get("checks",{}).get("frame_variance"),flush=True)
