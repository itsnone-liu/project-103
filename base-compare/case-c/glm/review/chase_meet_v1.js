// src/config.js — PROJECT = { duration: 20, bpm: 120, offset: 0 };
// chase_meet.js: "The Slow and the Late" (20.0 s). Clawd naps through the start of a walk-race; the turtle takes a
// 4 s head start at 60 px/s, Clawd runs at exactly twice that (120 px/s), and they meet at x = 880, t = 11.2 s:
//   60·T = 120·(T−4)  →  T = 8.0  →  MEET_X = 400 + 60·8 = 880 = 400 + 120·4  ✓  (gap at Clawd's start: 240 px)
//   Shot A 0–3.2   iris onto the START post; turtle waits, Clawd hops in, ties a sweatband, flops — cool.
//   Shot B 3.2–7.2 turtle plods off alone (head start happening, prints lengthen); butterfly wakes Clawd; crouch.
//   Shot C 7.2–9.2 the launch at 120 px/s, dust ribbon vs dotted prints; whip-pan smear out.
//   Shot D 9.2–11.2 gap melts; nose meets shell exactly at MEET_X on the last frame; spark.
//   Shot E 11.2–14.4 SMASH freeze at x=880; flash-ring; checkered flag stamps in; both trails re-trace 400→880.
//   Shot F 14.4–18.2 meadow dims; BEFORE ghosts (turtle at 640, Clawd at 400, 240 px bracket) → MATCH-CUT to AFTER
//                     (both at the flag, trails equal, ticks align, bulb, turtle nods).
//   Shot G 18.2–20.0 golden tableau at the flag; turtle bows; iris to paper, rhyming with the opening.
(() => {
  // ---------- the Parameters (from the storyboard; all motion is derived from these, nothing else) ----------
  const TURTLE_SPEED = 60, CLAWD_SPEED = 120, HEAD_START = 4.0;
  const START_X = 400, MEET_T = 8.0, MEET_X = 880;
  const T0 = 3.2;                                   // turtle starts walking (video s)
  const C0 = T0 + HEAD_START;                       // 7.2  — Clawd starts
  const TF = T0 + MEET_T;                           // 11.2 — the freeze / meet
  // PATTERN: FREEZE_EVENT — both positions are closed-form and pinned at MEET_X for t ≥ 11.2 (the freeze)
  const turtleX = t => START_X + TURTLE_SPEED * clamp(t - T0, 0, MEET_T);                    // 400 + 60·8 = 880
  const clawdX  = t => START_X + CLAWD_SPEED * clamp(t - C0, 0, MEET_T - HEAD_START);        // 400 + 120·4 = 880

  const HORIZON = 780, PATH_TOP = 842, PATH_BOT = 962, FAR_Y = 906, NEAR_Y = 956;
  const U = 22, CW = 5 * U;                          // Clawd unit; his nose leads his ground point by 5u
  const WIPE = [mixCol(PAL.ochre, PAL.cream, .45), PAL.cream];
  const warmK = t => seg(t, TF, 18.6);               // cool morning → golden, from the meet on
  const blinkK = t => Math.max(0, 1 - Math.abs(t - 1.15) / .14, 1 - Math.abs(t - 2.55) / .14,
    1 - Math.abs(t - 5.1) / .13, 1 - Math.abs(t - 9.6) / .13, 1 - Math.abs(t - 13.9) / .14, 1 - Math.abs(t - 17.2) / .13);

  // ---------- shared set pieces ----------
  function meadow(t, warm) {
    boilSeed('sky');
    paint(rectPts(-900, -520, W + 1800, H + 1200), { wash: mixCol(PAL.cream, '#FFECC9', .55 * warm), ink: null });
    glow(255, 165, 230 + 210 * warm, '#FFDFA0', .2 + .32 * warm);                       // the one real light
    paint(ellPts(255, 165, 44, 44, 20, 1.5), { wash: mixCol(PAL.cream, '#FFE9B0', .5 + .4 * warm), fill: PAL.ochre, fillOp: 35, ink: null });
    boilSeed('hills');
    paint(ellPts(420, HORIZON + 70, 950, 200, 26, 5), { fill: mixCol(PAL.sap, PAL.sky, .55), fillOp: 125, bleed: .25, tex: .55, ink: null });
    paint(ellPts(1700, HORIZON + 95, 1050, 235, 26, 5), { fill: mixCol(PAL.teal, PAL.sky, .5), fillOp: 105, bleed: .25, tex: .55, ink: null });
    boilSeed('ground');
    paint(rectPts(-900, HORIZON - 60, W + 1800, H - HORIZON + 700, 4), { wash: mixCol(PAL.sap, PAL.cream, .2 + .14 * warm), fill: mixCol(PAL.sap, PAL.cream, .32), fillOp: 70, bleed: .06, tex: .5, ink: null });
    for (let i = 0; i < 9; i++) { boilSeed('gr' + i); const x = 60 + hash(i) * 1800, y = HORIZON + 8 + hash(i + 30) * 26, sw = wob(t, .5, hash(i) * 3) * 4;
      for (const k of [-1, 0, 1]) inkLine([[x + k * 6, y], [x + k * 10 + sw, y - 16 - 7 * hash(i + k + 50)]], .7, mixCol(PAL.sap, PAL.ink, .35), 'inkfine', .3); }
    for (let i = 0; i < 4; i++) { boilSeed('fl' + i); paint(ellPts(120 + hash(i + 70) * 1700, HORIZON + 36 + hash(i + 80) * 26, 5, 5, 8, 1), { wash: i % 2 ? PAL.rose : mixCol(PAL.cream, PAL.rose, .4), ink: null }); }
    boilSeed('path');
    paint(rectPts(-900, PATH_TOP, W + 1800, PATH_BOT - PATH_TOP + 14, 3), { wash: mixCol(PAL.ochre, PAL.cream, .28 + .12 * warm), fill: PAL.ochre, fillOp: 55, bleed: .12, tex: .5, ink: null });
    inkLine([[-900, PATH_TOP - 2], [620, PATH_TOP - 9], [2500, PATH_TOP - 4]], 1.1, mixCol(PAL.ink, PAL.ochre, .35), 'ink', .5);
    inkLine([[-900, PATH_BOT], [720, PATH_BOT + 7], [2500, PATH_BOT + 3]], 1.1, mixCol(PAL.ink, PAL.ochre, .35), 'ink', .5);
  }
  function startPost() {                              // the striped START post + the line across the path
    boilSeed('post');
    inkLine([[START_X, PATH_BOT - 4], [START_X, PATH_TOP + 6]], 4, PAL.cream, 'ink', .2);
    const pt = HORIZON - 55;
    for (let i = 0; i < 6; i++) { const y0 = lerp(PATH_BOT + 10, pt, i / 6), y1 = lerp(PATH_BOT + 10, pt, (i + 1) / 6);
      paint(rectPts(START_X - 9, y0, 18, y1 - y0 + 1, 1), { wash: i % 2 ? PAL.cream : mixCol(PAL.clay, PAL.rose, .35), ink: PAL.ink, sw: .9 }); }
    paint(ellPts(START_X, pt - 3, 13, 7, 10, 1), { wash: mixCol(PAL.clay, PAL.rose, .35), ink: PAL.ink, sw: .9 });
  }
  function flagIn(t) {                                // the checkered MEET flag; stamps into the ground at 12.38
    const k = seg(t, 12.08, 12.38); if (k <= 0) return;
    // PATTERN: FOCUS_REVEAL — the flag, twin of the START post, lands beside the frozen pair and takes the eye
    const dy = -640 * (1 - easeIn(k)), wig = t > 12.38 ? spring(t, 12.38, .1, 9) * .16 : 0;
    boilSeed('flag');
    push(); translate(MEET_X + 66, PATH_BOT + 12 + dy); rotate(wig);
    inkLine([[0, 6], [0, -208]], 4.5, mixCol(PAL.ochre, PAL.ink, .3), 'ink', .1);
    paint(rrPts(1, -206, 84, 50, 5, 1.2), { wash: PAL.cream, ink: PAL.ink, sw: 1 });
    for (let r = 0; r < 2; r++) for (let c = 0; c < 3; c++) if ((r + c) % 2 === 0)
      paint(rectPts(3 + c * 27.6, -203 + r * 24, 27.6, 24, 1), { wash: PAL.ink, ink: null });
    pop();
    const a = (t - 12.38) / .5;
    if (a > 0 && a < 1) { boilSeed('flagdust');
      for (let i = 0; i < 5; i++) paint(ellPts(MEET_X + 66 + (i - 2) * 24, PATH_BOT + 8 - a * 16, 9 + 18 * a, 5 + 9 * a, 8, 2), { fill: mixCol(PAL.ochre, PAL.cream, .5), fillOp: 95 * (1 - a), bleed: .3, ink: null });
      pulseRing(MEET_X + 66, PATH_BOT + 6, 12.38, t, 90, mixCol(PAL.ochre, PAL.cream, .5));
      glow(MEET_X + 66, 830, 70 * (1 - a), '#FFE9A8', .45 * (1 - a)); }
  }

  // ---------- the turtle: new painted character, always on model (teal-sap shell, pale belly, half-lidded) ----------
  // x = rear-of-shell anchor on the ground = its race position turtleX(t); faces right, never hurried.
  // PATTERN: CHASE_MOTION — the plod: 60 px/s, stubby legs on a slow phase, tiny bob, breathing when still
  function turtle(x, y, s, t, o = {}) {
    const walking = !o.still, ph = Math.max(0, (t - T0) * TAU * 1.45), ghost = !!o.ghost, op = ghost ? 105 : 255;
    const skin = ghost ? mixCol(PAL.paper, PAL.sap, .4) : mixCol(PAL.sap, PAL.cream, .3);
    const shellC = ghost ? mixCol(PAL.paper, PAL.teal, .35) : mixCol(PAL.teal, PAL.sap, .45);
    const inkC = ghost ? mixCol(PAL.paper, PAL.ink, .4) : PAL.ink;
    const bob = walking ? -1.7 * Math.abs(Math.sin(ph)) : 0, breath = walking ? 1 : 1 + .02 * Math.sin(t * 2.3);
    boilSeed(o.boilKey || 'turtle');
    push(); translate(x, y); scale(s);
    if (o.bow) { translate(56, -46); rotate(-o.bow); translate(-56, 46); }
    if (o.preStep) rotate(.05 * o.preStep);                       // leans into its very first step (cut on action)
    translate(0, bob);
    const leg = (lx, phase, col) => { const lift = walking ? Math.max(0, Math.sin(ph + phase)) * 8 : (o.preStep && phase === 0 ? o.preStep * 6 : 0);
      paint(rrPts(lx - 8, -32 - lift, 16, 32 + lift, 6, 1.2), { wash: col, washOp: op, ink: inkC, sw: .9 }); };
    leg(34, Math.PI * .8, mixCol(skin, PAL.ink, .18)); leg(88, Math.PI * 1.4, mixCol(skin, PAL.ink, .18));   // far pair
    paint(rrPts(4, -34, 96, 20, 9, 1.5), { wash: ghost ? mixCol(PAL.paper, PAL.cream, .5) : mixCol(PAL.cream, PAL.ochre, .15), washOp: op, ink: inkC, sw: .9 });
    paint(ellPts(52, -52, 50 * breath, 40 * breath, 26, 1.6), { wash: shellC, washOp: op, fill: mixCol(shellC, PAL.ink, .25), fillOp: ghost ? 0 : 45, bleed: .08, tex: .5, ink: inkC, sw: 1.1 });
    if (!ghost) { boilSeed('shellpat');
      inkLine([[18, -66], [52, -74], [86, -66]], .9, mixCol(inkC, shellC, .3), 'ink', .5);
      inkLine([[30, -46], [52, -50], [74, -46]], .8, mixCol(inkC, shellC, .3), 'ink', .5); }
    leg(16, 0, skin); leg(80, Math.PI, skin);                     // near pair
    const look = o.lookBack ? -4 : 0, nod = o.nod ? o.nod * 7 : 0;
    paint(ellPts(98 + look * .4, -44 + nod, 18, 13, 16, 1.2), { wash: skin, washOp: op, ink: inkC, sw: 1 });
    if (!ghost) { boilSeed('tface');
      const bl = o.blink || 0, ex = 103 + look, ey = -47 + nod;
      paint(ellPts(ex, ey, 4.2, 4.8, 8, .6), { wash: PAL.cream, ink: inkC, sw: .6 });
      paint(ellPts(ex, ey + (1 - bl) * 1.5, 4.2, Math.max(.6, 4.6 * (1 - bl * .92)), 8, .5), { wash: PAL.ink, ink: null });
      inkLine([[ex - 4.6, ey - 2.8 + bl], [ex + 4.6, ey - 4.2 + bl]], 1.1, inkC, 'ink', .2);   // the heavy half-lid
      inkLine([[ex + 3, ey + 7], [ex + 8.5, ey + 5.5]], .9, inkC, 'ink', .3); }                // tiny calm smirk
    pop();
  }

  // ---------- Clawd as one puppet, a pure function of video time (poses continue across the cuts) ----------
  function bandOverEyes(u, sw) {                      // the sweatband, slipped down over the eyes in his sleep
    paint(rrPts(-4.7 * u, -7.15 * u, 9.4 * u, 1.75 * u, .8 * u, 1.2), { wash: mixCol(PAL.rose, PAL.cream, .25), ink: PAL.ink, sw: sw * .75 });
    inkLine([[-4.5 * u, -6.3 * u], [-6.1 * u, -5.5 * u]], sw * .9, mixCol(PAL.rose, PAL.cream, .25), 'ink', .2);
  }
  function racer(t) {
    const mood = emotions(t, [[0, 'cool'], [2.5, 'sleepy'], [6.02, 'surprised', { lookX: .3, lookY: -.7 }],
      [6.6, 'determined'], [8.3, 'excited'], [11.15, 'surprised', { lookX: .6 }], [11.9, 'relieved', { lookX: .6 }],
      [12.7, 'happy', { lookX: -.9, lookY: .2 }], [15.55, 'thinking', { lookX: .7 }], [16.6, 'idea'],
      [18.15, 'happy'], [18.55, 'love']]);
    let pose = {};
    if (t < 1.15) {                                                // at the line, bouncing on the beat
      pose = { view: 'q', dy: -.9 * Math.abs(Math.sin(bpOf(t) * Math.PI)), sq: .1 * pulse(t, 1), aR: .3, aL: -.1 };
    } else if (t < 1.95) {
      // PATTERN: STAGGER_REVEAL — only after the course is read does Clawd hop in, turtle already settled at the line
      const a = seg(t, 1.15, 1.95), i = Math.min(2, Math.floor(a * 3)), k = frac(a * 3);
      pose = { view: 'q', dx: -150 / U + (150 / U) * (i + k) / 3, dy: -2.2 * Math.sin(Math.PI * k) - .3, sq: .18 * Math.max(0, 1 - k * 3.5) };
    } else if (t < 2.3) {                                          // settles; ties on the sweatband
      pose = { view: 'q', dy: -.7 * Math.abs(Math.sin(bpOf(t) * Math.PI)),
        aR: .2 + 1.1 * Math.sin(Math.PI * seg(t, 1.98, 2.22)), aL: -.1 + .5 * Math.sin(Math.PI * seg(t, 2.04, 2.28)),
        hat: t > 2.08 ? 'sweatband' : null };
    } else if (t < 6.6) {
      // PATTERN: FOCUS_REVEAL — the flop: cocky lean against the post, then out like a light (the failure to start)
      const f = backOut(seg(t, 2.3, 2.95));
      pose = { view: 'q', rot: .52 * f, dy: .55 * f - .1, sq: .08 * f + .03 * Math.sin(t * 2.1),
        hat: t < 3 ? 'sweatband' : null, draw: t >= 3 ? bandOverEyes : null, eyes: t >= 3 ? 'closed' : undefined };
    } else if (t < 7.2) {
      // PATTERN: ACCELERATE_AND_SETTLE — snaps upright with overshoot, then coils into the crouch (the wind-up)
      const up = seg(t, 6.6, 6.8), cr = ease(seg(t, 6.78, 7.02)), tt = Math.max(0, t - 6.8);
      pose = { ...turn(t, 6.6, 6.8, 0, .25), rot: .52 * (1 - backOut(up)), dy: .55 * (1 - up) + .95 * cr,
        sq: .32 * cr + .12 * Math.exp(-tt * 7) * Math.sin(tt * 26), aR: -.95 * cr, aL: -.7 * cr, hat: 'sweatband' };
    } else if (t < TF) {
      // PATTERN: CHASE_MOTION — the run at 120 px/s: beat-locked stride, arms pumping offset, lean into it
      // PATTERN: ACCELERATE_AND_SETTLE — burst off the line (stretch + smear), then settle into the stride
      const ph = (t - C0) * TAU * 2.05, str = -.55 * Math.exp(-(t - C0) * 9) * Math.cos((t - C0) * 16);
      pose = { view: 'side', walk: ph, dy: -1.9 * Math.abs(Math.sin(ph)) - 1, rot: .1,
        sq: -.12 * Math.abs(Math.sin(ph)) + .16 * Math.max(0, Math.cos(ph)) + str,
        aR: .55 + .6 * Math.sin(ph), aL: -.3 + .5 * Math.sin(ph + 2.6), hat: 'sweatband',
        smear: t < C0 + .18 ? .55 : 0, smearDir: 1 };
    } else {
      // PATTERN: FREEZE_EVENT — from the meet on, clawdX(t) is pinned at MEET_X; only the acting (and boil) moves
      const pant = Math.exp(-(t - TF) * 2.2);
      const v = t < 12.5 ? { view: 'side' } : t < 12.72 ? turn(t, 12.5, 12.72, .25, .125)
        : t < 18.3 ? { view: 'q' } : t < 18.5 ? turn(t, 18.3, 18.5, .125, 0) : { view: 'front' };
      pose = { ...v, dy: -.4 - .55 * pant * Math.abs(Math.sin(t * 6.5)), sq: .05 * Math.sin(t * 6.5) * pant,
        hat: 'sweatband', aR: t > 16.4 ? 1 : .3, aL: t > 18.5 ? .7 + .12 * Math.sin(t * 5) : -.2 };
    }
    return { ...mood, ...pose, dy: (mood.dy || 0) * .6 + (pose.dy || 0), sq: (mood.sq || 0) + (pose.sq || 0) };
  }
  const drawClawd = (t, extra = {}) => { const r = racer(t); return clawd(clawdX(t) - CW, NEAR_Y, U, { ...r, ...extra, sq: r.sq + (extra.sq || 0) }); };

  // ---------- trails, marks, effects ----------
  // PATTERN: CHASE_MOTION — each print appears at the exact world x the turtle (60 px/s) has passed
  function printTrail(t, boostFn) {
    for (let i = 0; i < 16; i++) { const x = START_X + 26 + i * 30; if (x > MEET_X - 8) break;
      const appear = T0 + (x - START_X) / TURTLE_SPEED; if (t < appear) break;
      const k = boostFn ? boostFn(x) : 0; boilSeed('pr' + i);
      for (const f of [-1, 1]) paint(ellPts(x + f * 5 + hash(i + 40) * 6, FAR_Y - 2 + (f > 0 ? 9 : 1) + hash(i * 2 + (f > 0 ? 1 : 0)) * 4, 4.6 + hash(i + 9) * 1.6, 3, 8, 1),
        { wash: mixCol(PAL.teal, PAL.ink, .3), washOp: 110 + 130 * k, ink: null }); }
  }
  // PATTERN: CHASE_MOTION — dust puffs anchor where Clawd (120 px/s) passed; they fade into the persistent ribbon
  function dustTrail(t, boostFn) {
    for (let i = 0; i < 11; i++) { const x = 434 + i * 44; if (x > MEET_X - 20) break;
      const appear = C0 + (x - START_X) / CLAWD_SPEED; if (t < appear) break;
      const k = boostFn ? boostFn(x) : 0, a = clamp((t - appear) / 1.1, 0, 1); boilSeed('du' + i);
      paint(ellPts(x + hash(i) * 10, NEAR_Y - 10 - a * 12 - hash(i + 3) * 6, 15 + 20 * hash(i + 5) + 10 * a, 8 + 9 * hash(i + 7) + 5 * a, 10, 2),
        { fill: mixCol(PAL.ochre, PAL.cream, .45), fillOp: (38 + 62 * k) * (1 - a * .55), bleed: .3, tex: .5, ink: null }); }
  }
  // PATTERN: TRACE_PATH — a bright head sweeps each trail from START_X to MEET_X (turtle first, Clawd twice as fast)
  const sweepB = (t, a, b) => { const k = seg(t, a, b); const x = k <= 0 ? -1e3 : k >= 1 ? 1e5 : lerp(START_X, MEET_X, ease(k)); return x0 => clamp(1 - (x - x0) / 55, 0, 1); };
  function sweepHeads(t) {
    for (const [a, b, y] of [[13.05, 14.0, FAR_Y - 2], [13.6, 14.3, NEAR_Y - 8]]) { const k = seg(t, a, b);
      if (k > 0 && k < 1) { const x = lerp(START_X, MEET_X, ease(k)); glow(x, y, 30, '#FFF3C4', .55); sparkPop(x, y, t - .12, t, 16); } }
  }
  function pulseRing(x, y, t0, t, r1, col) { const k = seg(t, t0, t0 + .55); if (k <= 0 || k >= 1) return; boilSeed('rg' + Math.round(t0 * 10));
    inkLine(ellPts(x, y, lerp(12, r1, easeOut(k)), lerp(5, r1 * .42, easeOut(k)), 30, 2), Math.max(.5, 7 * (1 - k)), col, 'ink', .8); }
  function sparkPop(x, y, t0, t, s) { const k = seg(t, t0, t0 + .45); if (k <= 0 || k >= 1) return; boilSeed('sp' + Math.round(t0 * 20) + Math.round(x));
    paint(starPts(x, y, Math.max(2, s * backOut(k)) * (1 - k * .45), .3, 4, k * 2.4), { wash: PAL.cream, washOp: 255 * (1 - k * k), ink: null }); }
  function speedStreaks(t, k) { if (k <= 0 || k >= 1) return; boilSeed('streak' + Math.floor(k * 6));   // whip-pan smear
    for (let i = 0; i < 13; i++) { const y = 100 + hash(i) * 880, l = (180 + 520 * hash(i + 40)) * k, x = W + 120 - hash(i + 80) * 500 - k * 700;
      inkLine([[x, y], [x - l, y]], 2.5 + 5 * hash(i + 7), i % 3 ? PAL.cream : mixCol(PAL.ochre, PAL.cream, .5), 'ink', 0); } }
  function butterfly(x, y, t) {
    boilSeed('bfly'); const flap = .3 + .7 * Math.abs(Math.sin(t * 14));
    push(); translate(x, y + wob(t, 2.4, 1) * 2.5); rotate(.14 * Math.sin(t * 2.1));
    for (const sd of [-1, 1]) { push(); scale(sd * (.45 + .55 * flap), 1);
      paint(ellPts(10, -8, 12, 8.5, 10, .8, -.55), { wash: mixCol(PAL.rose, PAL.cream, .3), ink: PAL.ink, sw: .7 });
      paint(ellPts(8.5, 3, 8.5, 6, 10, .8, .45), { wash: mixCol(PAL.ochre, PAL.cream, .25), ink: PAL.ink, sw: .6 }); pop(); }
    inkLine([[0, -9], [0, 8]], 1.5, PAL.ink, 'ink', .2);
    inkLine([[0, -9], [-3.5, -14]], .7, PAL.ink, 'inkfine', 0); inkLine([[0, -9], [3.5, -13]], .7, PAL.ink, 'inkfine', 0);
    pop();
  }
  function bfly(t) {                                  // the butterfly: cause, then the take
    if (t < 4.95 || t > 6.95) return;
    const nose = [315, NEAR_Y - 6.2 * U];
    let p; if (t < 5.7) p = arcPt([150, 795], nose, 70, ease(seg(t, 4.95, 5.7)));
    else if (t < 6.15) p = [nose[0] + 4 * Math.sin(t * 2.2), nose[1] + wob(t, 2.4, 1) * 2];
    else p = arcPt(nose, [720, 610], 150, ease(seg(t, 6.15, 6.9)));
    butterfly(p[0], p[1], t);
  }
  function bracket(x0, x1, y, grow, col) {            // the gap, bracketed — no letters, just marks
    const xe = lerp(x0, x1, ease(grow)); boilSeed('brk');
    inkLine([[x0, y], [xe, y]], 2, mixCol(PAL.ink, col, .2), 'ink', .2);
    inkLine([[x0, y], [x0, y + 16]], 2, mixCol(PAL.ink, col, .2), 'ink', .2);
    if (grow >= 1) inkLine([[x1, y], [x1, y + 16]], 2, mixCol(PAL.ink, col, .2), 'ink', .2);
    glow(x0, y + 8, 20, '#FFE9A8', .3);
    if (grow >= 1) glow(x1, y + 8, 20 + 8 * Math.sin(T * 4), '#FFE9A8', .35);
  }
  function endTick(t, x, y, col, t0) { const k = seg(t, t0, t0 + .22); if (k <= 0) return; boilSeed('tick' + t0);
    const b = 15 * backOut(k); inkLine([[x, y - b], [x, y + b]], 3.5, col, 'ink', .1); pulseRing(x, y, t0, t, 55, col); }

  // ---------- Shot A · 0–3.2 · iris opens from paper onto the START post ----------
  function shotA(t, lt, dur) {
    camBegin(kf(lt, [[0, 830], [dur, 622]]), 758, kf(lt, [[0, .9], [dur, 1]]));
    meadow(t, warmK(t)); startPost();
    turtle(turtleX(t), FAR_Y, .85, t, { still: true, blink: blinkK(t), preStep: seg(t, 3, 3.2) });  // first step begins — cut on action
    drawClawd(t);                                     // hop-in, bounce, sweatband, flop (see racer's branches)
    const post = toScreen(START_X, HORIZON + 20);
    camEnd();
    // PATTERN: FOCUS_REVEAL — the iris opens onto the striped post: this is the start
    if (lt < .7) iris(post[0], post[1], lerp(0, 1750, easeIn(lt / .7)), PAL.paper);
  }

  // ---------- Shot B · 3.2–7.2 · the head start, happening ----------
  function shotB(t, lt, dur) {
    camBegin(622 + 12 * Math.sin(lt * .45), 752, kf(lt, [[0, 1], [dur, .965]]));
    meadow(t, warmK(t)); startPost();
    // PATTERN: SHOW_RELATIVE_DIFFERENCE — the turtle's prints lengthen away from the sleeper: the head start itself
    printTrail(t);
    turtle(turtleX(t), FAR_Y, .85, t, { blink: blinkK(t) });
    drawClawd(t);                                     // asleep at the post: zzz drifts, sweatband over the eyes
    // PATTERN: EVENT_EMPHASIS — the butterfly lands on his nose; the '!' take fires on it (cause, then reaction)
    bfly(t);
    camEnd();
  }

  // ---------- Shot C · 7.2–9.2 · the launch, twice the pace ----------
  function shotC(t, lt, dur) {
    const whip = 430 * easeIn(seg(lt, dur - .2, dur));
    camBegin(clawdX(t) + 235 + whip, 750, 1.02);
    meadow(t, warmK(t)); startPost();
    // PATTERN: SHOW_RELATIVE_DIFFERENCE — dust ribbon eats the dotted prints: 60 px/s of closing speed, visible
    printTrail(t); dustTrail(t);
    turtle(turtleX(t), FAR_Y, .85, t, { blink: blinkK(t) });
    drawClawd(t, { smear: Math.max(t < C0 + .18 ? .55 : 0, .75 * seg(lt, dur - .2, dur)), smearDir: 1 });
    pulseRing(START_X - 60, NEAR_Y - 4, C0, t, 120, PAL.cream);   // the launch burst
    camEnd();
    speedStreaks(t, seg(lt, dur - .22, dur));         // whip-pan smear carries out of the cut
  }

  // ---------- Shot D · 9.2–11.2 · one stride behind, then level ----------
  function shotD(t, lt, dur) {
    camBegin(kf(lt, [[0, 965], [1.1, 915], [2, 897]]), kf(lt, [[0, 748], [2, 735]]), kf(lt, [[0, 1.05], [2, 1.17]]));
    meadow(t, warmK(t)); startPost();
    printTrail(t); dustTrail(t);
    // PATTERN: CHASE_MOTION — Clawd's nose column closes on the shell's rear column; both hit 880 at t = 11.2 exactly
    turtle(turtleX(t), FAR_Y, .85, t, { blink: blinkK(t) });
    drawClawd(t);
    // PATTERN: EVENT_EMPHASIS — the touch: a spark where nose meets shell, on the exact meet frame
    if (t >= TF - .02) { sparkPop(MEET_X, (FAR_Y + NEAR_Y) / 2, TF, t, 54); pulseRing(MEET_X, (FAR_Y + NEAR_Y) / 2, TF, t, 260, PAL.cream); }
    camEnd();
    speedStreaks(t, 1 - lt / .14);                    // the whip settles out over the cut
  }

  // ---------- Shot E · 11.2–14.4 · SMASH into the freeze; flash, flag, trails ----------
  function shotE(t, lt, dur) {
    const my = (FAR_Y + NEAR_Y) / 2;
    const sh1 = t > TF ? shakeXY(t, 9 * Math.exp(-(t - TF) * 4.2)) : [0, 0];
    const sh2 = t > 12.38 ? shakeXY(t, 4 * Math.exp(-(t - 12.38) * 6)) : [0, 0];
    // PATTERN: CAMERA_PUSH — pull back from the pair until the whole 400→880 course sits in one frame
    camBegin(kf(lt, [[0, 897], [1, 884], [dur, 640]]) + sh1[0] + sh2[0], kf(lt, [[0, 735], [dur, 765]]) + sh1[1] + sh2[1],
      kf(lt, [[0, 1.17], [1, 1.06], [dur, .78]]));
    meadow(t, warmK(t)); startPost();
    // PATTERN: TRACE_PATH — both trails re-trace the one course from the same post (turtle's sweep first, Clawd's 2× fast)
    printTrail(t, sweepB(t, 13.05, 14.0)); dustTrail(t, sweepB(t, 13.6, 14.3)); sweepHeads(t);
    // PATTERN: FREEZE_EVENT — the meet, held: positions are pinned at MEET_X by the capped position functions
    turtle(turtleX(t), FAR_Y, .85, t, { still: true, lookBack: seg(t, 12.3, 12.65), blink: Math.max(blinkK(t), .35 * seg(t, 12.6, 12.9)) });
    drawClawd(t);
    flagIn(t);
    // PATTERN: EVENT_EMPHASIS — the world stops on the contact frame: flash, ring and flying sparks at MEET_X
    sparkPop(MEET_X, my, TF, t, 60);
    for (let i = 0; i < 6; i++) { const a = -Math.PI * (.12 + .76 * hash(i)), d = 70 + 150 * hash(i + 20), t0 = TF + .06 + i * .05;
      sparkPop(MEET_X + Math.cos(a) * d, my + Math.sin(a) * d * .7, t0, t, 14 + 10 * hash(i + 5)); }
    pulseRing(MEET_X, my, TF, t, 900, PAL.cream);
    camEnd();
    if (t > TF && t < TF + .8) flash(.9 * Math.exp(-(t - TF) * 3.2), '#FFF3D0');   // the smash-cut's blink
  }

  // ---------- Shot F · 14.4–18.2 · BEFORE → MATCH-CUT → AFTER (camera carries, no cut) ----------
  function shotF(t, lt, dur) {
    const after = t >= 15.5;                          // 15.5 lands on a beat
    const sh = after ? shakeXY(t, 3.5 * Math.exp(-(t - 15.5) * 5)) : [0, 0];
    camBegin(640 + 8 * Math.sin(lt * .4) + sh[0], 765 + 4 * Math.sin(lt * .31) + sh[1], .78 + .004 * Math.sin(lt * .5));
    meadow(t, warmK(t)); startPost(); flagIn(t);
    if (!after) { printTrail(t); dustTrail(t); turtle(MEET_X, FAR_Y, .85, t, { still: true, blink: blinkK(t) }); drawClawd(t); }
    // PATTERN: DIM_OTHERS — the meadow falls back to pale watercolour; only the lesson stays lit
    paint(rectPts(-900, -500, W + 1800, H + 1200, 4), { wash: mixCol(PAL.paper, PAL.sky, .45), washOp: 130 * ease(seg(t, 14.4, 15.35)), ink: null });
    if (!after) {
      // PATTERN: SHOW_BEFORE_AFTER — BEFORE, at Clawd's start: turtle at 400 + 60·4 = 640 with its short trail,
      // Clawd still at the post with none — the 240 px gap bracketed in glow
      for (let i = 0; i < 8; i++) { const x = START_X + 26 + i * 30; boilSeed('gp' + i);
        paint(ellPts(x, FAR_Y + 2 + (i % 2) * 8 + hash(i) * 3, 4.4, 2.8, 8, 1), { wash: mixCol(PAL.teal, PAL.paper, .35), washOp: 80, ink: null }); }
      turtle(640, FAR_Y, .85, t, { still: true, ghost: true, boilKey: 'gTurt' });
      clawd(START_X - CW, NEAR_Y, U, { view: 'q', rot: .52, dy: .5, sq: .05, eyes: 'closed', boilKey: 'gClawd',
        col: mixCol(PAL.paper, PAL.clay, .3), dk: mixCol(PAL.paper, PAL.clay, .05), lt: mixCol(PAL.paper, PAL.cream, .55) });
      bracket(START_X, 640, 742, seg(t, 14.95, 15.32), PAL.teal);
    } else {
      // PATTERN: MATCH_CUT — same framing, one beat: the ghosts swap for the real pair at the flag, trails full length
      printTrail(t, () => 1); dustTrail(t, () => 1);
      turtle(MEET_X, FAR_Y, .85, t, { still: true, lookBack: 1, blink: .45, nod: Math.sin(Math.PI * clamp(seg(t, 16.85, 17.5))) });
      drawClawd(t);                                   // thinking → idea: the bulb pops over him (16.6)
      bracket(START_X, MEET_X, 742, seg(t, 15.65, 16.05), PAL.teal);
      // PATTERN: SHOW_RELATIVE_DIFFERENCE — the punchline: both trail ends tick onto the same finish, equal
      endTick(t, MEET_X, FAR_Y - 8, mixCol(PAL.teal, PAL.ink, .3), 15.75);
      endTick(t, MEET_X, NEAR_Y - 6, mixCol(PAL.ochre, PAL.ink, .25), 15.98);
      pulseRing(MEET_X, (FAR_Y + NEAR_Y) / 2, 16.2, t, 170, PAL.cream);
      if (t > 16.2) glow(MEET_X, (FAR_Y + NEAR_Y) / 2, 40 + 10 * Math.sin(t * 3), '#FFE9A8', .4 * clamp(seg(t, 16.2, 16.5)));
    }
    camEnd();
    if (after && t < 15.5 + .7) flash(.5 * Math.exp(-(t - 15.5) * 5), '#FFF6DC');   // the match-cut's blink
    if (lt > dur - .35) brushWipe((lt - (dur - .35)) / .7, WIPE);                   // hand off to the tableau
  }

  // ---------- Shot G · 18.2–20.0 · the golden tableau at the flag ----------
  function shotG(t, lt, dur) {
    camBegin(kf(lt, [[0, 910], [dur, 890]]), 752, kf(lt, [[0, .97], [dur, 1.03]]));
    meadow(t, 1); startPost(); flagIn(t);
    printTrail(t, () => 1); dustTrail(t, () => 1);    // the whole course, both trails equal, post at the left edge
    // PATTERN: FOCUS_REVEAL — together at the flag: turtle unbothered and tipping a tiny bow, Clawd beaming (hearts)
    turtle(MEET_X, FAR_Y, .85, t, { still: true, lookBack: 1, blink: .5, bow: .22 * Math.sin(Math.PI * clamp(seg(t, 18.75, 19.4))) });
    drawClawd(t);
    const pair = toScreen(MEET_X - 20, 850);
    camEnd();
    if (lt < .3) brushWipe(.5 + lt / .6, WIPE);
    // PATTERN: CAMERA_PUSH — drift in, then the iris closes on the pair and holds a beat before paper
    if (lt > dur - .78) { const r = lt < dur - .12 ? lerp(1600, 275, ease(seg(lt, dur - .78, dur - .3)))
      : lerp(275, 0, easeIn(seg(lt, dur - .12, dur - .02))); iris(pair[0], pair[1], r, PAL.paper); }
  }

  shots([[0, shotA], [3.2, shotB], [7.2, shotC], [9.2, shotD], [11.2, shotE], [14.4, shotF], [18.2, shotG]]);
})();
