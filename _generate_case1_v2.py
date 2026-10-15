# -*- coding: utf-8 -*-
"""_generate_case1_v2.py — v2 全片代码生成（口语化旁白 + 中段新视觉世界）。

与 v1 (_generate_case1_full.py) 的差异：
  - storyboard/audio 均取 v2（runs/envpsy-case1-v2/storyboard.md + audio/timing_envpsy-case1-v2.json）
  - PLAN 中段（units 7-31）替换为 decision_stepA_v2_midsection.md 的 25 个专属世界；零圈线注解置顶
  - STYLE 追加 v2 硬规则：无字母代号角标、renderFrame 返回真值
"""
import json, re, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from pipeline import llm, prompts, profile as profile_mod
from pipeline.produce import parse_storyboard

SRC = ROOT / 'runs' / 'envpsy-case1'
OUT = ROOT / 'runs' / 'envpsy-case1-v2'
OUT.mkdir(parents=True, exist_ok=True); (OUT / 'code').mkdir(exist_ok=True); (OUT / 'out').mkdir(exist_ok=True)

storyboard = (OUT / 'storyboard.md').read_text(encoding='utf-8')
topic = (SRC / 'topic-case-1.md').read_text(encoding='utf-8')
timing = json.loads((ROOT / 'audio' / 'timing_envpsy-case1-v2.json').read_text(encoding='utf-8'))
assert len(parse_storyboard(storyboard)['narration']) == 48
assert len(timing['starts']) == 48 and timing['total'] > 620, f"timing not ready: {timing.get('total')}"
TOTAL = timing['total']
(OUT / 'timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding='utf-8')

STYLE = """Full-length illustrated urban documentary. User-approved v1 direction retained: do not impose a single visual style or layout on all 48 units; choose technique by narrative content; stylized illustrated documentary, substantial filled color masses, surface texture/grain/hatching, layered light, shadows and foreground occlusion; avoid constant thin outlines, generic slide grids, persistent header/footer/progress HUD. No fabricated photorealistic archive footage: draw only clearly illustrative assets. V2 HARD RULES from user feedback (2026-10-14): (1) The mid-section defect was repeated zoom over one base map with circling/underlining/arrow-drawing annotations — this annotation-grammar is BANNED mid-film: never indicate meaning by drawing circles/lines/arrows onto a persistent base image; use distinct worlds, light effects, counters, staged objects instead. (2) On-screen source captions must be natural language (e.g. 来源：NYC DOT 2010 评估 / 来源：Whyte 1978 研究); NEVER letter codes like 〔B〕〔T〕〔D〕〔S〕 on screen or in narration. (3) renderFrame(t) must return a truthy value; fully deterministic, no prior-frame dependency, no randomness, no network."""

MID = """MID units 7-31 / v2 dedicated worlds (each cue = one dominant visual event on its own stage; verified grammar-spike worlds marked *):
7 newspaper front-page wall: two headline pages nailed up, a third blank page waiting for a possible failure headline; pen hovering. 8 prop landing close-ups: brush paints a green lane, folding chair snaps open, planter thuds into place. 9 ledger pages: management/maintenance/coordination costs line up; pen circles above signature line into a question mark. 10 shop interior looking out through storefront: two-color river of people (warm=stopping, cool=passing) with warm stream entering the shop. 11 storefront counting wall: passer icons stream past, rare stoppers light up enlarged. 12 windshield POV: wiper-rhythm street view, detour route appears like water traces on glass. 13 sign-flip drama: road sign flips 昨日可通 to 今日禁行, headlights halt before it. 14 crossing POV: horn sound becomes visible shockwave ripples, a figure threads between them. 15 triptych corner: three simultaneous safe passages (child, luggage, slow walker) at one corner. 16 platform theater: big clock face, transfer corridor flows, one commuter frowns at timetable. 17 three hourglasses side by side (wait/transfer/cross) draining into one pocket watch. 18 four colored claim tablets (shop/driver/pedestrian/commuter) drop with weight onto a desk street plan. 19 interest-light map: street cross-section with four colored light patches breathing bright/dim, no drawn marks. 20 toolbox opening: three lens plates (observe/activity/feeling) lifted against light. 21 time-lapse theater* (verified in spike): same-angle plaza day compressed, sky tint cycling, warm seated vs cool passing figures, corner counters 经过/停留 ticking; natural caption 来源：Whyte 1978 研究. 22 four-time-of-day theater: same corner in four panels (morning rush / midday sitting / dusk chat / night emptying) evolving. 23 lens over street: through an observation lens, stopping points light up warm one by one (light overlay, never drawing). 24 overload subtraction POV* (verified): horn ripples, cross traffic, crowd layers stack to desaturated overload vignette, then one layer lifts like a sheet and clarity returns — subtraction demonstrated live. 25 hand-feel inverted-U curve grows over street-density background, tiny dead-street / overloaded-street vignettes at both ends; qualitative only. 26 spotlight stage: one empty chair lit, person sits; crossing lines simplify to one calm straight path. 27 same-grid dual fill* (verified): identical dot density both halves; left half walk/stop/choose icons light, figures move freely; right half low walls block, figures bump; bottom line 差别不在人数，在能不能走、能不能停、能不能选. 28 three-door theater: approach/dwell/leave doors, person pushes each; handles always in the person's hand. 29 verified-stamp hovering never landing; two proposition cards (chairs retain people? conflict→safety?) await evidence. 30 dual-camera before/after same-weather labels side by side recording; small counterexample inset (fewer pedestrians ≠ success). 31 three lens plates converge to one focus point, light gathers into the line 让人停下来的条件; pen returns to signature line and the nib falls — bridging into evidence act."""

PLAN = f"""Visual-director plan based on 48 exact narration cues (v2 colloquial rewrite) and source-linked topic:
S1 units 1-3 / opening: keep v1 grammar — cinematic matched-angle before/after street illustration; unit 2 retains ads, tourists, rush-hour bustle; unit 3 elegant transparent overlay over the street showing competing routes/access/jurisdiction, routes schematic.
S2 units 4-6 / decision entry: keep v1 grammar — tactile top-down office desk, memo/ledger/newspaper generic artifacts (no invented quote/date/amount), camera document to document, pen revealed, stakes kept.
{MID}
S5 units 32-41 / evidence: keep v1 grammar (user-praised) — sourced report pages, well-designed data-viz sequences, not giant numbers. Exact relative values: car occupants injured -63% (index 100→37), pedestrians injured -35% (100→65), pedestrians walking in carriageway -80% (100→20), Broadway+7th Ave pedestrian volume +11% (100→111), total volume +6% (100→106), support 74% of survey respondents. Each baseline independently normalized to 100, labelled as index. Attribute NYC DOT 2010; sample n unavailable. Walking-volume scopes separate, do not add. Traffic improvement qualitative. Business shift qualitative. 45M visits/year and doubled public space only as Snøhetta project description, not trial effect. Dark textured background + typography + index-based dataviz per v1 act5.
S6 units 42-48 / permanence and transfer: keep v1 grammar — material morphs paint→granite, chair→bench, glass steps→2017 illustrative view; 2014 phase/2017 completion; ongoing questions; three lessons as materialized callbacks; local street at dawn; final question embedded in environment (integrated card per user praise).
Global semantic accuracy: never confuse visual metaphor with sourced observation; distinguish report values, teaching-normalized index, qualitative role-voice, theoretical mechanism, project description and inference; no unsourced statistics, precise traffic geometry, fabricated archival quotations, fake causal proof. Mid-section annotation grammar ban and natural source captions apply to the whole film.
Animation: {TOTAL:.2f}-second measured narration clock, 48 cues; each sentence anchors a distinct meaningful event; no static holds through long cues (progressive micro-action, camera travel, layering, evidence reveals, morphs). Each act owns its grammar; within-act shot grammar varies. Deterministic renderFrame(t) returning truthy, no prior-frame dependency/randomness/network."""

profile = profile_mod.load(ROOT / 'profiles' / 'envpsy.profile.yaml')
profile['visual']['style_note'] = STYLE
profile['visual']['style_pack'] = 'user_approved_v2_midsection_worlds'
decision = json.loads((SRC / 'decision.json').read_text(encoding='utf-8'))
messages = prompts.codegen_prompt(decision, storyboard, timing, profile, topic=topic, visual_plan=PLAN, include_visual_context=True)
start = time.time(); response, meta = llm.call('sol', messages, think='low', effort='high')
m = re.search(r'```(?:\w+)?\n(.*?)```', response, re.S); code = (m.group(1) if m else response).strip()
if len(code) < 5000: raise RuntimeError(f'code too short: {len(code)}')
(OUT / 'decision.json').write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'decision_stepA.md').write_text(PLAN, encoding='utf-8')
(OUT / 'code' / 'index.html').write_text(code, encoding='utf-8')
(OUT / 'code' / '.done').write_text('ok')
(OUT / 'usage.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'VISUAL_DIRECTION.md').write_text('# v2 direction (user-confirmed tone + full-length)\n\n' + STYLE + '\n\n## Beat plan\n\n' + PLAN, encoding='utf-8')
print(f'V2 CODEGEN chars={len(code)} usage={meta.get("usage")} elapsed={time.time()-start:.0f}s', flush=True)
