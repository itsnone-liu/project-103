# -*- coding: utf-8 -*-
"""Generate isolated full-length Times Square visual candidate; reuse audited narration/timing only."""
import json,re,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from pipeline import llm,prompts,profile as profile_mod
from pipeline.produce import parse_storyboard
SRC=ROOT/'runs'/'envpsy-case1'
OUT=ROOT/'runs'/'envpsy-case1-full'
OUT.mkdir(parents=True,exist_ok=True);(OUT/'code').mkdir(exist_ok=True);(OUT/'out').mkdir(exist_ok=True)
# Always take canonical, already-audited content from original source, not partial candidate.
storyboard=(SRC/'storyboard.md').read_text(encoding='utf-8')
topic=(SRC/'topic-case-1.md').read_text(encoding='utf-8')
timing=json.loads((ROOT/'audio'/'timing_envpsy-case1.json').read_text(encoding='utf-8'))
# The measured clock is for the exact narration below.
assert len(parse_storyboard(storyboard)['narration'])==48
assert len(timing['starts'])==48 and abs(timing['total']-601.18)<.1
(OUT/'storyboard.md').write_text(storyboard,encoding='utf-8')
(OUT/'topic-case-1.md').write_text(topic,encoding='utf-8')
(OUT/'timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding='utf-8')
STYLE="""Full-length illustrated urban documentary. User-approved C2 showed clear improvement in animation texture and an integrated card near its ending; retain this qualitative direction. Do not impose a single visual style or layout on all 48 units. Choose precise visual technique by narrative content: matched historical viewpoint for before/after; tactile desk/document staging for decision; distinct inhabited POVs and a convergence into shared street for stakeholders; spatial map with selective translucent overlays for theory; sourced, properly labelled quantitative graphics only for verified metrics; material morphs for temporary-to-permanent; world-integrated ending prompt. Some chapters may use opaque diagram cards, some transparent cards over live scene, some full-bleed illustrated environments, some split views/POVs, kinetic typography, maps, timelines, evidence graphics, or material-match transitions. Vary composition within and between acts; cards are allowed but never one repeated skeleton. Keep stylized illustrated documentary, substantial filled color masses, surface texture/grain/hatching, layered light, shadows and foreground occlusion. Avoid constant thin outlines, generic slide grids, persistent header/footer/progress HUD. No fabricated photorealistic archive footage: draw only clearly illustrative assets. The exact visual grammar should be semantically motivated, not a rigid checklist."""
PLAN="""Visual-director plan based on 48 exact narration cues and source-linked topic:
S1 units 1-3 / opening: use cinematic matched-angle before/after street illustration. Begin with cropped, pressured curb-level movement and noisy car/pedestrian overlap; reveal changed use in same matched geography without inventing exact dimensions. Unit 2 retains ads, tourists and rush-hour bustle: don't depict deserted/silent plaza. Unit 3 asks displacement/legitimacy, switch to an elegant transparent overlay over the street showing competing routes/store access/decision jurisdiction; mark all routes schematic.
S2 units 4-9 / decision: visual mode shifts to tactile top-down office desk, appointment/incident memo/budget ledger/newspaper as generic artifacts (no invented quote/date/amount), clock set only to 2009 if given. Move camera document to document; reveal pen but keep office stakes. Represent danger and budget constraint without fabricated death counts. Unit 7 political support with named figures only as text/reference if accurate; no invented portrait likeness. Unit 8 animate paint, folding chair, planter as reversible tools; unit 9 show management/maintenance/coordination and evaluation criteria.
S3 units 10-19 / stakeholders: compose four distinctive human-scale worlds (shop delivery/storefront, driver windshield and detour map, pedestrian constrained crossing and choice, commuter watch/transit transfer). Use role-voices as dramatized perspectives, never quotation marks suggesting historic verbatim quotes. Vary shot sizes and transitions. Then physically converge scenes into one shared street plan / transparent overlay mapping competing needs; no heroes/villains or invented business results.
S4 units 20-31 / analytical lenses: leave document world for full-bleed roving illustrated street map. Use selectively layered translucent annotations/cards that relate to ground plane: Whyte dwell vs pass observation and Gehl necessary/optional/social activities; overload / qualitative inverted-U only (no fitted curve/threshold); density vs perceived crowding/control; mechanisms as hypotheses, clearly label observed vs hypothesized vs outcome. Lens graphics should illuminate specific places, not become static generic 3-column deck. Unit 29-31 separates hypothesis from evaluation and returns to decision pen.
S5 units 32-41 / evidence: use sourced report pages, gradually reveal data in well-designed data-viz sequences, not merely giant numbers. Exact relative values: car occupants injured -63% (=index 100→37), pedestrians injured -35% (=100→65), pedestrians walking in carriageway -80% (=100→20), Broadway+7th Ave pedestrian volume +11% (=100→111), total pedestrian volume +6% (=100→106), support 74% of survey respondents. Each baseline index independently normalized to 100 and labelled as index, not counts/probabilities. Attribute NYC DOT 2010 evaluation; exact sample n unavailable. Separate walking-volume scopes; do not add. Traffic operation improvement is qualitative, not universal speed gain. Business shift qualitative, no revenue or rent stats. Project post-pilot data: 45 million visits/year and permanent public space doubled only as Snøhetta project description, not trial causal effect. Use transparent result cards overlaying street when useful; preserve source/method caveats readable.
S6 units 42-48 / permanence and transfer: morph paint into black granite pavement, folding chair into permanent bench, then glass gathering steps into a 2017 illustrative wider public-space view (no fake geometry). Mark 2014 phase one/2017 completion appropriately; project scale and bench 10–30 ft only if cited and explained. Show ongoing maintenance/access/use questions. Conclude with three lessons as brief materialized visual callbacks, then leave a distinct local street at dawn; embed final question in environment using half-card or translucent integrated treatment, not generic end slide.
Global semantic accuracy: never confuse visual metaphor with sourced observation; distinguish report values, teaching-normalized index, qualitative role-voice, theoretical mechanism, project description and inference. no unsourced statistics, precise traffic geometry, fabricated archival quotations, fake before-after causal proof.
Animation: 601.18-second measured narration clock, 48 cues; each sentence anchors a distinct meaningful event; avoid static holds throughout long cues by progressive micro-action, camera travel, layering, revealing evidence, or morphs. Each act should have its own visual grammar; within-act shot grammar varies. Transparent card overlays only where they clarify a specific relation and should respond to background contrast. Full bleed, partial frame, scene-integrated text and cards coexist deliberately. Deterministic renderFrame(t), no prior-frame dependency/randomness/unseeded assets/network."""
profile=profile_mod.load(ROOT/'profiles'/'envpsy.profile.yaml')
profile['visual']['style_note']=STYLE
profile['visual']['style_pack']='user_approved_content_selected_visual_grammar'
decision=json.loads((SRC/'decision.json').read_text(encoding='utf-8'))
messages=prompts.codegen_prompt(decision,storyboard,timing,profile,topic=topic,visual_plan=PLAN,include_visual_context=True)
start=time.time(); response,meta=llm.call('sol',messages,think='low',effort='high')
m=re.search(r'```(?:\w+)?\n(.*?)```',response,re.S);code=(m.group(1) if m else response).strip()
if len(code)<5000: raise RuntimeError(f'code too short: {len(code)}')
(OUT/'decision.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'decision_stepA.md').write_text(PLAN,encoding='utf-8')
(OUT/'code'/'index.html').write_text(code,encoding='utf-8')
(OUT/'code'/'.done').write_text('ok')
(OUT/'usage.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'VISUAL_DIRECTION.md').write_text('# User-approved full case direction\n\n'+STYLE+'\n\n## Content-specific beat plan\n\n'+PLAN,encoding='utf-8')
print(f'FULL CODEGEN chars={len(code)} usage={meta.get("usage")} elapsed={time.time()-start:.0f}s',flush=True)
