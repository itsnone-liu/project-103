# STORYBOARD — "The Slow and the Late" (20.0 s)

**Logline:** Clawd wants to win a walk across the meadow, but he naps through the start and the turtle gets a head start, so Clawd must run twice as fast and catches up at exactly the point where his speed pays off the turtle's lead.

**World:** A flat, sunny morning meadow — cream paper sky, soft sap-green ground, one ochre dirt path running left to right. A striped wooden post marks START; a checkered flag marks MEET. Cool pale morning light warms toward golden as the race resolves; the meet-flash is the brightest moment in the film. Turtle is a new painted character: round teal-sap shell, pale belly, stubby plodding legs, calm half-lidded eyes — always on model, always unhurried. No lettering anywhere: markers, trails and emotes carry all meaning.

**Motif:** Markers and trails. The striped START post opens the film; the checkered flag rhymes with it at the end. Two trails — the turtle's dotted footprints and Clawd's dust ribbon — trace the same path from the same post, and their equal length IS the lesson.

**Parameters (the code phase must use exactly these):**
- TURTLE_SPEED = 60 px/s
- CLAWD_SPEED = 120 px/s (exactly 2× turtle)
- HEAD_START = 4.0 s (turtle walks alone before Clawd starts)
- START_X = 400 (world px, striped post)
- MEET_T = 8.0 s after the turtle starts — solved: 60·T = 120·(T−4) → 60T = 120T − 480 → T = 8.0
- MEET_X = 880 (world px, 480 px from START) — check: turtle 400 + 60·8 = 880; Clawd 400 + 120·(8−4) = 880 ✓
- Video clock mapping: turtle starts walking at video t = 3.2; Clawd starts at video t = 7.2 (head start = 7.2 − 3.2 = 4.0); FREEZE at video t = 11.2 (= 3.2 + 8.0), both at x = 880
- Used in the summary: at Clawd's start the turtle is at 400 + 60·4 = 640 (gap = 240 px, closed at 60 px/s of relative speed over 4.0 s)

**Clawd's arc:** cool → sleepy → surprised panic → determined → strained excitement → relieved joy at the meet → idea (understands the math) → warm respect.

**Shots:**

**A · 0.0–3.2 · [in: iris opens from paper onto the START post]** Wide meadow, path running right, striped post at x=400. Turtle sits at the line, slow-blinking; Clawd bounces on his toes, ties on a sweatband, then flops back lazily at the post. · Camera drifts slowly toward the post, gentle zoom from 0.9 to 1.0.
- reads: 0.3–1.2 the course and the striped START post — the eye lands on the post as the iris opens [FOCUS_REVEAL]
- reads: 1.2–2.2 two racers at the line — turtle first, then Clawd bouncing beside it [STAGGER_REVEAL]
- reads: 2.2–3.1 Clawd flops down at the post, cocky — he isn't racing yet [FOCUS_REVEAL]

**B · 3.2–7.2 · [cut on action: turtle's first step]** Turtle crosses the line at 60 px/s and plods right; Clawd dozes at x=400 (zzz emote, hat over eyes). The gap grows to 240 px. A butterfly lands on Clawd's nose; he snaps awake ('!' take), scrambles up into a crouch. · Camera holds on the post, turtle shrinking into the distance.
- reads: 3.3–4.5 the turtle steps off alone, steady plodding gait — Clawd stays put [CHASE_MOTION]
- reads: 4.5–5.7 Clawd sleeps through it: the turtle shrinks away while he snores — the head start, happening [SHOW_RELATIVE_DIFFERENCE]
- reads: 5.7–6.6 the butterfly; Clawd's eyes snap open, huge take, '!' emote [EVENT_EMPHASIS]
- reads: 6.6–7.2 scramble and crouch — wind-up, coiled to launch [ACCELERATE_AND_SETTLE]

**C · 7.2–9.2 · [cut on action: mid-launch]** Clawd bursts from x=400 at 120 px/s — visibly twice the turtle's pace, dust puffs, run cycle on the beat. Turtle ahead at 640→760. The gap visibly melts. · Camera whips right to track Clawd, turtle held in frame ahead.
- reads: 7.2–8.1 the launch: Clawd explodes off the line, snap out then settle into stride [ACCELERATE_AND_SETTLE, CHASE_MOTION]
- reads: 8.1–9.2 the gap shrinks — turtle far ahead but Clawd is eating it up fast [SHOW_RELATIVE_DIFFERENCE, CHASE_MOTION]

**D · 9.2–11.2 · [whip pan with smear, same screen direction]** Clawd 640→880, turtle 760→880. One stride behind, then level: Clawd's nose reaches the turtle's shell exactly at x=880, video t=11.2. · Camera tracks, tightening on the pair as they converge.
- reads: 9.2–10.1 a stride behind and closing — Clawd straining, turtle serene [CHASE_MOTION]
- reads: 10.1–11.2 level … touch — the contact frame lands at t=11.2 [CHASE_MOTION, EVENT_EMPHASIS]

**E · 11.2–14.4 · [SMASH into freeze on the contact frame]** FREEZE: both hold exactly at x=880 (boil and emotes stay alive; positions locked to MEET_X). A flash-ring blooms at the meet point and a checkered flag stamps into the ground beside them. Then both trails trace themselves along the course: turtle's dotted prints from 400, Clawd's dust ribbon from 400 — one path, drawn twice. · Camera pulls back from the pair to frame the whole 400→880 course.
- reads: 11.2–12.1 the world stops and a flash-ring marks the spot: they meet, HERE [FREEZE_EVENT, EVENT_EMPHASIS]
- reads: 12.1–13.1 the checkered flag stamps in at the meet point — the twin of the START post [FOCUS_REVEAL]
- reads: 13.1–14.4 both trails trace the full course, overlapping end to end — the camera eases back until START and MEET are in one frame [TRACE_PATH, CAMERA_PUSH]

**F · 14.4–18.2 · [camera pull-back carries through; no cut]** The wide course holds; the meadow dims to pale watercolour. Ghost replay: pale turtle ghost at 640 with its short dotted trail, pale Clawd ghost at 400 with no trail, the 240 px gap bracketed in glow. On a beat it MATCH-CUTS to the after: the real pair together at 880, both trails full length — and their ends tick into alignment, equal. Clawd's bulb emote pops; the turtle gives a slow smug nod. · Static wide; only the ghosts/bracket move.
- reads: 14.4–15.5 the world dims; BEFORE — ghost turtle a chunk down the course with a short trail, ghost Clawd still at the post with none [DIM_OTHERS, SHOW_BEFORE_AFTER]
- reads: 15.5–16.5 the snap to AFTER — both at the flag, both trails now reach all the way: same start, same finish [MATCH_CUT, SHOW_BEFORE_AFTER]
- reads: 16.5–17.9 the punchline lands: the two trail lengths sit equal over the same ground — bulb emote over Clawd, turtle nods [SHOW_RELATIVE_DIFFERENCE, EVENT_EMPHASIS]

**G · 18.2–20.0 · [brush wipe into the final tableau]** Framing rhymes with shot A, now at the checkered flag: turtle and Clawd side by side at x=880. Turtle tips into a tiny bow, cool; Clawd beams, hearts emote. The morning light is fully golden. · Camera at rest, slight drift in.
- reads: 18.2–19.2 together at the flag — the turtle unbothered, Clawd warm with respect [FOCUS_REVEAL]
- reads: 19.2–20.0 the iris closes on the pair and holds one beat before paper [CAMERA_PUSH]

**[transition out: iris to paper, mirroring the opening iris]**

**Check:** event in every shot ✓ · reads sequential with landing time ✓ · transition at every seam (iris / cut-on-action ×2 / whip / smash-freeze / camera-carry / brush wipe / iris) ✓ · no text — striped post, checkered flag, trails and emotes only ✓ · ending rhymes with opening (post→flag, cool→warm) ✓ · all motion uses exactly the Parameters numbers; the freeze at video t=11.2 is MEET_X=880 ✓
