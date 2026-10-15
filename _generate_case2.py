# -*- coding: utf-8 -*-
"""_generate_case2.py — 案例B《隔间》全片代码生成（E组透视设计图语法主打）。

复用案例A v2 的生产教训：sol 长响应可能截断 → 生成后必须完整性三查；
renderFrame 返回真值；确定性；text/sources 分离的来源角标自然写法。
"""
import json, re, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from pipeline import llm, prompts, profile as profile_mod
from pipeline.produce import parse_storyboard

SRC = ROOT / 'runs' / 'envpsy-case1'          # 仅复用 decision.json（后端选型记录）
OUT = ROOT / 'runs' / 'envpsy-case2-cubicle'
OUT.mkdir(parents=True, exist_ok=True); (OUT / 'code').mkdir(exist_ok=True); (OUT / 'out').mkdir(exist_ok=True)

storyboard = (OUT / 'storyboard.md').read_text(encoding='utf-8')
topic = (OUT / 'topic-case-2.md').read_text(encoding='utf-8')
timing = json.loads((ROOT / 'audio' / 'timing_envpsy-case2-cubicle.json').read_text(encoding='utf-8'))
assert len(parse_storyboard(storyboard)['narration']) == 39
assert len(timing['starts']) == 39 and timing['total'] > 400, f"timing not ready: {timing.get('total')}"
TOTAL = timing['total']
(OUT / 'timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding='utf-8')

STYLE = """Illustrated documentary with architectural-drawing 3D grammar (spike-verified engine). Base quality bar (user-approved animation-documentary v2): choose technique by narrative content per cue, never one layout for all units; stylized illustrative masses, surface texture/grain, layered light, shadows, foreground occlusion; avoid generic slide grids, persistent header/footer/HUD, constant thin outlines. No fabricated photorealistic archive imagery; draw clearly illustrative assets only.
THIS FILM'S SIGNATURE GRAMMAR (E-group, validated in runs/cubicle-spike — implement the same engine, hand-rolled, NO three.js/WebGL):
- A tiny deterministic 3D layer inside Canvas 2D: world vertices as [x,y,z]; camera = yaw/pitch rotation then perspective divide (project(v,yaw,pitch,dist,fov)->{x,y,z}); faces sorted by centroid depth (painter's algorithm, far-to-near); back-face culling via signed polygon area; flat shading with fixed light direction; ground grid projected in 3D; soft ground shadow ellipses.
- E1 orbit: yaw sweeps slowly with time; E2 explode-assemble: parts displaced along axes by eased factor, then close FULLY (factor reaches exactly 0 at assemble end); E3 scale-jump: pitch rotates from top-down plan to ~30deg perspective while yaw sweeps; E4 drafting annotations: dimension lines with arrow ticks and labels offset per drafting convention (never overlapping shape edges, never readable as part of the scene), leader lines with dots; E5 freedom-strip: parts lock flat one by one, teal-to-gray gradient takeover, grid self-replicating outward.
- Polishing rules from spike: sightline semantics must be iconic (draw a seated figure and a standing figure at the arc origins, color coding secondary); dimension text offset from the dimension line by drafting convention.
HARD RULES (carried from v2 user feedback): (1) annotation-grammar BANNED: never indicate meaning by circling/underlining/arrows over a persistent base image — use distinct worlds, 3D assembly events, staged objects, light effects; (2) on-screen source captions natural language only (来源：Bernstein & Turban 2018 实测 / 来源：Auscherman 2020 / 来源：Rev. Proc. 62-21, IRS 1962), NEVER letter codes; (3) renderFrame(t) must return truthy; fully deterministic: no prior-frame dependency, no randomness, no network, no async."""

PLAN = f"""Visual-director plan: 39 narration cues, one dedicated world per cue, six acts.
S1 units 1-4 / scale-jump cold open: 1940s-50s open-plan office as clean 3D floor model. u1 top-down plan: rows of typewriter desks snap into grid, fluorescent wash; u2 camera begins rising, pitch tilting: supervisor's glass-corner office glows, sightlines rake across the floor; u3 full perspective orbit mid-air, the whole floor as one supervised machine, era label plate; u4 ground-level POV between desks: heads silhouettes, moving legs, overhead glare, claustrophobic rhythm (no horror, restrained).
S2 units 5-10 / field observation: u5 a furniture-company studio in Michigan: draftsman's desk, sculptor's tools, a restless inventor figure silhouette (no portrait likeness, generic), map pin to Michigan; u6 observation kit laid out on field-desk: stopwatch, tally counter, notebook pages fanning with observed minutes; u7 typographic-3D hybrid: a desk cross-section where paper stacks grow, arrows of interruption as physical swinging pendulums striking a thinking bubble (physicalized, not drawn-on annotations); u8 two-faced work theater: one desk splits into two stages — left sealed focus cell (deep work glow), right conversation cluster (talk ripples) — both faces alternating like stage lights; u9 the bullpen floor returns as surveillance lantern: one giant supervising eye-of-light sweeping rows (light effect, not drawn eye); u10 three-path diagram in 3D: box-in / runway / morphing-third-path whose walls hinge open and closed — the third path wins a warm light.
S3 units 11-18 / the ideal, exploded: u11 1964 first-gen Action Office as museum vitrine: parts displayed, sparse audience silhouettes drift past (cold reception); u12 1968 second-gen on rotating plinth, confident studio light, part count settles; u13 FULL EXPLODE: the system separates into floating labeled parts (desk slab / legs / half screen with angled top / shelf / connectors / chair), slow orbit (E1+E2); u14 the desk slab rises to standing height with an ergonomic dimension bracket drawing itself (E4) + seated/standing figure silhouettes; u15 the half screen close-up orbit: sightline theater — seated figure's peripheral field filtered (motion ghosts blocked), standing figure's gaze passes over the angled top; light and sound waves pass through as translucent ripples; u16 reconfiguration ballet: the same parts form three layouts in sequence (writing nook / meeting cluster / new orientation), camera orbiting (E1); u17 the assembly reassembles fully (explode factor to exactly 0) into one system; caption plate 不是一件家具，是一套自由度; u18 a physical boundary-switch object: a half-height wall with an actual hinge-and-lever knob a hand silhouette toggles — open/close states breathe light (Altman privacy-as-control, textbook anchor 来源：课程教材·Altman 私密调节).
S4 units 19-26 / three hands of distortion: u19 pivot turn: the warm studio flips to fluorescent gray; first hand = imitation: duplicate silhouettes of the screen part copied across a factory conveyor, moving parts snapping off and dropping (E5 begins); u20 second hand = tax: two amortization timelines as physical hourglasses/rulers of different lengths, equipment short vs building long, calendar plates flip to 1962, caption 来源：Rev. Proc. 62-21, IRS 1962; u21 ledger theater: buying partitions priced cheaper than masonry walls — coin stacks vs brick stack on a scale beam; u22 third hand = area algorithm: a floor plan fills with replicating grid cells, density counter climbs, desk units shrink; u23 THE STRIP (spike-verified E5): standing desk locks flat, shelf detaches and drops, angled top straightens, color drains teal-to-gray — one continuous transformation, parts freeze mid-motion; u24 grid self-replication: one cell to a floor to a tower of floors (3D array growth), quiet and orderly and suffocating; u25 1989 culture plate: a comic-strip framed panel world (clearly illustrative, generic office character with tie) inside a gray cubicle; caption 来源：《呆伯特》1989 年起连载; u26 the inventor's late-years desk: the original exploded system hologram-ghost floating above a gray grid floor; caption 来源：Auscherman 2020（晚年批评，安全转述）; his sentence lands as quiet typographic plate.
S5 units 27-32 / evidence & pendulum (user-praised grammar retained): dark textured background + typography + index data-viz. u27 research-verse opening: stacks of journal pages becoming a bar; u28 the half-height partition finding: dual-panel comparison world (semi-enclosed vs fully open) with satisfaction/efficiency index bars, TEAL vs GRAY, index normalized to 100 independently, labeled 指数化示意·来源：Oldham 系办公室研究（1979 起）·定性转述; u29 the same partition drawn twice: tool vs cage — left: chosen, territory marked by objects, screen angled thoughtfully; right: uniform grid, monitor faces aisle, passersby glances; both worlds side by side in 3D; u30 2018 field lab: two office-floor dioramas wired with sensor threads, caption 来源：Bernstein & Turban 2018 实测·两家《财富》500 强; u31 the 70% finding: face-to-face interaction index bar 100→30 (about 70% drop), while email/message line rises; strict index labeling per case-A discipline (指数=实测口径归一); u32 the pendulum machine: a physical pendulum sweeping across four era stations (大排档/格子间/开放平面/回到隔断), each station a small 3D vignette.
S6 units 33-39 / control, not walls: u33 split-world callback: left warm handoff of a choice-dial, right cold container box stamped 最优解; between them the tax/procurement/packaging funnels as physical chutes (illustrative); u34 a good-intent token traveling through a narrowing funnel gate and coming out reshaped (E-lite morph, clearly metaphorical); u35 hybrid-era diorama: home desk with lamp + office collaboration table, commute line connecting them, calendar pages flipping to today; u36 the original system's control-key close-up: a boundary switch key on a ring, textbook plate 环境是行为的容器，钥匙在使用者手里 来源：课程教材; u37 the half screen's last orbit: seated/standing sightline theater once more, calm dusk light, dimension line 挡视线，不挡光; u38 invisible-screen montage: classroom / hospital bay / library desk / home study — four small vignettes each with a half-height boundary element, unified composition; u39 integrated ending card: one cubicle unit at dusk, desk lamp on, screen at half height, the boundary switch resting on the desk; final question typeset into the environment (no HUD), film ends quiet.
Global semantic accuracy: never confuse visual metaphor with sourced observation; the ONLY quantitative claims are 1964/1968/4-year gap, 1962 tax rule (no year-span numbers), ~70% face-to-face drop (Bernstein & Turban 2018, two Fortune 500 firms, about-qualifier), 1989 Dilbert start; everything else qualitative; no unsourced statistics, no invented quotes (Propst late-years criticism as safe paraphrase), no fabricated archive.
Animation: {TOTAL:.2f}-second measured narration clock, 39 cues; each sentence anchors a distinct meaningful event; no static holds (progressive micro-action, orbit travel, layering, morphs); each act owns its grammar; deterministic renderFrame(t) returning truthy."""

profile = profile_mod.load(ROOT / 'profiles' / 'envpsy.profile.yaml')
profile['visual']['style_note'] = STYLE
profile['visual']['style_pack'] = 'case2_e_group_3d_documentary'
decision = json.loads((SRC / 'decision.json').read_text(encoding='utf-8'))
messages = prompts.codegen_prompt(decision, storyboard, timing, profile, topic=topic, visual_plan=PLAN, include_visual_context=True)
start = time.time(); response, meta = llm.call('sol', messages, think='low', effort='high')
m = re.search(r'```(?:\w+)?\n(.*?)```', response, re.S); code = (m.group(1) if m else response).strip()
(OUT / 'decision.json').write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'VISUAL_DIRECTION.md').write_text('# case2 direction (E-group 3D documentary)\n\n' + STYLE + '\n\n## Beat plan\n\n' + PLAN, encoding='utf-8')
(OUT / 'usage.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'RAW chars={len(response)}', flush=True)
# 完整性三查（2026-10-14 教训）：代码过短直接报错；截断特征检测
problems = []
if len(code) < 5000: problems.append(f'code too short: {len(code)}')
if '</html>' not in code: problems.append('missing </html>')
if 'window.P103' not in code: problems.append('missing window.P103 contract')
if problems:
    (OUT / 'code' / 'index_truncated.html').write_text(code, encoding='utf-8')
    raise RuntimeError('COMPLETENESS: ' + '; '.join(problems) + f' (saved to index_truncated.html, {len(code)} chars)')
(OUT / 'code' / 'index.html').write_text(code, encoding='utf-8')
(OUT / 'code' / '.done').write_text('ok')
print(f'CASE2 CODEGEN chars={len(code)} usage={meta.get("usage")} elapsed={time.time()-start:.0f}s', flush=True)
