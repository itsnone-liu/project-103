// patterns.js v0 — Pattern Library runtime primitives (project 103).
// Loaded AFTER src/timeline.js and BEFORE the scene file (see studio.html).
// Design rules: every primitive is t-stateless (call with local time lt),
// world-space unless documented screen-space (call after camEnd), and built
// only on the documented engine API (paint/inkLine/glow/seg/ease/kf/...).
// Companion doc: PATTERNS.md. Do not rename: storyboards cite these names
// as [PATTERN: X] tags and the alignment lint greps `PATTERN: NAME`.

/* PATTERN: TRACE_PATH */
// Draw the recent trail of a moving subject. samples: [[t, x, y], ...] in
// shot-local time (call with lt). Modes: 'dots' (footprints), 'line' (ink
// ribbon), 'dash' (dashed path). Trail fades with age over o.tail seconds.
function tracePath(samples, lt, o = {}) {
  const tail = o.tail ?? 1.4, mode = o.mode ?? 'dots';
  const bg = o.bg ?? PAL.cream, col = o.col ?? PAL.teal;
  const every = o.every ?? .22, size = o.size ?? 5;
  const recent = samples.filter(s => s[0] <= lt && s[0] >= lt - tail);
  if (recent.length < 2) return;
  const at = (t) => {                       // linear interp of position at t
    if (t <= recent[0][0]) return recent[0];
    for (let i = 1; i < recent.length; i++) if (recent[i][0] >= t) {
      const a = recent[i - 1], b = recent[i], k = (t - a[0]) / Math.max(1e-6, b[0] - a[0]);
      return [t, lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
    }
    return recent[recent.length - 1];
  };
  if (mode === 'line') {                    // one fading ribbon stroke
    boilSeed('trace' + Math.round(lt * 24));
    const P = recent.map(s => [s[1], s[2]]);
    if (P.length > 1) paint(ribbon(P, o.weight ?? 2.4, 14), { wash: col, fill: col, fillOp: 120, ink: null });
    return;
  }
  const tLo = Math.max(lt - tail, recent[0][0] + .02);
  for (let t = tLo; t <= lt - .02; t += every) {        // dotted footprints
    const p = at(t), age = (lt - t) / tail, s = size * Math.max(.45, 1 - .55 * age);
    const fade = mixCol(col, bg, .1 + .55 * age);
    paint(ellPts(p[1], p[2], s, s * .7, 8, 1.2), { wash: fade, washOp: 255, ink: null });
  }
}

/* PATTERN: FREEZE_EVENT */
// Time gate + emphasis for THE key moment. Returns the time the scene
// should draw with: frozen (constant) inside [at, at+dur], lt otherwise.
// Call ONCE per frame near the top of the shot fn:  const ft = freezeFrame(lt, ...)
// then draw everything with ft. Draws its own overlays (edge flash + pulse
// ring at o.x,o.y world position) when active — so call AFTER content if
// you want the ring on top, or pass ring:false and call pulseRing yourself.
function freezeFrame(lt, o) {
  const at = o.at ?? 0, dur = o.dur ?? .5;
  const frozen = lt >= at && lt < at + dur;
  if (frozen) {
    const k = (lt - at) / dur;
    if (o.flash !== false) flash(.25 * (1 - k), '#FFFDF6');
    if (o.ring !== false && o.x != null) pulseRing(o.x, o.y, k, { r0: o.r0 ?? 40, r1: o.r1 ?? 150, col: o.col ?? PAL.rose });
  }
  return frozen ? at : lt;
}

/* PATTERN: EVENT_EMPHASIS */
// Screen-space dim of everything outside a focus rect, so the eye lands
// on the event. Call AFTER camEnd (screen coordinates).
function dimOthers(x, y, w, h, k = .55, col = PAL.night) {
  const m = 80, op = Math.round(150 * clamp(k));
  paint(rectPts(-m, -m, W + 2 * m, y + m, 2), { wash: col, washOp: op, ink: null });
  paint(rectPts(-m, y + h, W + 2 * m, H - y - h + m, 2), { wash: col, washOp: op, ink: null });
  paint(rectPts(-m, y, x + m, h, 2), { wash: col, washOp: op, ink: null });
  paint(rectPts(x + w, y, W - x - w + m, h, 2), { wash: col, washOp: op, ink: null });
}

/* PATTERN: EVENT_EMPHASIS */
// Expanding pulse ring at a world or screen position (draws wherever you
// call it). k: 0..1 progress; ring grows and fades.
function pulseRing(x, y, k, o = {}) {
  if (k <= 0 || k >= 1) return;
  const r = lerp(o.r0 ?? 40, o.r1 ?? 150, easeOut(k)), col = o.col ?? PAL.rose;
  paint(ellPts(x, y, r, r * .9, 40, 2), { ink: col, sw: 2.6 * (1 - k * .6) + .4 });
  if (o.double) paint(ellPts(x, y, r * .62, r * .56, 32, 2), { ink: col, sw: 1.6 * (1 - k * .6) });
}

/* PATTERN: FREEZE_EVENT *//* PATTERN: ACCELERATE_AND_SETTLE */
// Timing curve for anticipation -> strike -> settle. Returns k in [-1, 1]:
// windup sinks to -1 (crouch / pull back), strike overshoots toward +1
// fast, settle springs back through damped oscillation to 0. Map k to
// pose offsets:  sq: -.25*max(0,-k) + .2*max(0,k)   arm: .5*k  dy: .3*k
function anticipation(t, o = {}) {
  const t0 = o.t0 ?? 0, w = o.windup ?? .3, s = o.strike ?? .14, st = o.settle ?? .5;
  if (t < t0) return 0;
  if (t < t0 + w) return -easeIn(seg(t, t0, t0 + w));
  if (t < t0 + w + s) return lerp(-1, 1, easeOut(seg(t, t0 + w, t0 + w + s)));
  const a = t - t0 - w - s;                  // damped spring to 0
  return Math.exp(-a * 6) * Math.cos(a * 14);
}

/* PATTERN: CAMERA_PUSH */
// Zoom curve for a slow push-in on the payoff moment. Feed the return
// value into camBegin's zoom argument. geo:true uses exponential zoom
// (constant on-screen speed — use for long deep pushes, e.g. into an eye).
function pushIn(t, o = {}) {
  const k = ease(seg(t, o.t0 ?? 0, o.t1 ?? 1));
  const from = o.from ?? 1, to = o.to ?? 1.12;
  return o.geo ? from * Math.pow(to / from, k) : lerp(from, to, k);
}

/* PATTERN: STAGGER_REVEAL */
// Per-item reveal progress after o.at, items o.gap apart, each easing in
// over o.dur. Returns array of k (0..1) — map each to alpha/scale/position.
function staggerReveal(lt, n, o = {}) {
  const at = o.at ?? 0, gap = o.gap ?? .12, dur = o.dur ?? .4;
  return Array.from({ length: n }, (_, i) => ease(seg(lt, at + i * gap, at + i * gap + dur)));
}

/* PATTERN: HOLD */
// Boolean gate: true while lt is inside [at, at+dur]. Use to enforce a
// beat of stillness: when hold is true, draw the subject with pose frozen
// (no micro-motion: pass walk:0, fixed bob, emotions key at the held mood).
function hold(lt, at, dur) { return lt >= at && lt < at + dur; }

/* PATTERN: SHOW_BEFORE_AFTER */
// End-of-video summary panel (screen space: call AFTER camEnd). Two rows,
// one per subject: a ruler strip from x0 to x1 with ticks; hollow dot at
// the subject's start, filled dot at its end, a bar between them = the
// distance walked. numbers:true adds p5 text labels (unit + delta ticks)
// if the platform renders text.
function beforeAfter(lt, o = {}) {
  const k = ease(seg(lt, o.at ?? 0, (o.at ?? 0) + .6));
  if (k <= 0) return;
  const W0 = o.w ?? 1000, X = (W - W0) / 2, Y = o.y ?? 300;
  const rowH = 64, n = o.rows.length;
  boilSeed('ba');
  push(); translate(X, Y); scale(k);
  paint(rectPts(-30, -26, W0 + 60, rowH * n + 62, 3), { wash: PAL.cream, washOp: 235, fill: PAL.cream, fillOp: 40, ink: PAL.ink, sw: 1 });
  for (let r = 0; r < n; r++) {
    const row = o.rows[r], y = 12 + r * rowH + rowH / 2;
    const a = row.from, b = row.to;    // ruler-space px
    // ruler strip
    inkLine([[-10, y + 18], [W0 + 10, y + 18]], .8, mixCol(PAL.ink, PAL.cream, .4), 'inkfine', .3);
    const ticks = o.ticks ?? 10;
    for (let i = 0; i <= ticks; i++) {
      const tx = lerp(0, W0, i / ticks);
      inkLine([[tx, y + 12], [tx, y + (i % 5 === 0 ? 24 : 18)]], .7, mixCol(PAL.ink, PAL.cream, .3), 'inkfine', 0);
    }
    // distance bar + endpoints
    const x0 = clamp(a, 0, W0) , x1 = clamp(b, 0, W0);
    paint(rectPts(Math.min(x0, x1), y - 1, Math.max(2, Math.abs(x1 - x0)), 9, 1), { wash: row.col, fill: row.col, fillOp: 110, ink: null });
    paint(ellPts(x0, y + 3, 7, 7, 10, 1), { wash: PAL.cream, ink: row.col, sw: 1.2 });        // start: hollow
    paint(ellPts(x1, y + 3, 9, 9, 10, 1), { wash: row.col, ink: PAL.ink, sw: .8 });           // end: filled
    if (row.dash) for (let tx = Math.min(x0, x1); tx < Math.max(x0, x1); tx += 26)
      inkLine([[tx + 8, y - 8], [tx + 16, y - 8]], .7, mixCol(row.col, PAL.cream, .35), 'inkfine', 0);
  }
  // numeric labels via the letter layer (screen space; after pop-in settles)
  if (o.numbers && k >= 1) {
    const ticks = o.ticks ?? 10, unit = o.unit ?? 'px', span = o.span ?? W0;
    const vx = px => Math.round(px / W0 * span);            // ruler px -> value
    if (o.title) label(o.title, X + W0 / 2, Y - 4, 26, { col: PAL.ink, align: 'center' });
    label(Math.round(span / ticks) + ' ' + unit + '/刻', X, Y - 6, 15, { col: mixCol(PAL.ink, PAL.cream, .3), align: 'left' });
    for (let r = 0; r < n; r++) {
      const row = o.rows[r], y = 12 + r * rowH + rowH / 2;
      const x1 = clamp(row.to, 0, W0), val = row.toVal ?? vx(row.to);
      label(String(val) + ' ' + unit, X + Math.min(x1 + 14, W0 - 90), Y + y - 10, 17, { col: row.col });
      if (row.fromVal != null) label(String(row.fromVal), X + clamp(row.from, 0, W0) - 10, Y + y - 10, 14, { col: mixCol(PAL.ink, PAL.cream, .4) });
    }
  }
  pop();
}

/* PATTERN: CHASE_MOTION *//* creature kit v0 */
// creature(x, y, s, o) — a second actor distinct from clawd. Feet stand on
// y, like clawd. kind: 'turtle' | 'snail' | 'ball'. o: { col, shell, walk
// (0..1 gait phase, or pass t), dir (1 right / -1 left), bob }.
function creature(x, y, s, o = {}) {
  const kind = o.kind ?? 'turtle', dir = o.dir ?? 1;
  const col = o.col ?? mixCol(PAL.teal, PAL.night, .25);
  const shell = o.shell ?? mixCol(PAL.teal, PAL.cream, .35);
  boilSeed('cr' + kind);
  push(); translate(x, y); scale(dir, 1);
  if (kind === 'ball') {
    const roll = (o.walk ?? 0) * 2, c = o.col ?? PAL.ochre;
    paint(ellPts(0, -s, s, s, 24, 2), { wash: c, fill: mixCol(c, PAL.night, .3), fillOp: 70, ink: PAL.ink, sw: 1 });
    inkLine([[Math.cos(roll) * s * .6, -s + Math.sin(roll) * s * .6], [Math.cos(roll + 3.1) * s * .55, -s + Math.sin(roll + 3.1) * s * .55]], 1.1, mixCol(c, PAL.night, .5), 'ink', .2);
    pop();
    return;
  }
  if (kind === 'snail') {
    const bob = Math.sin((o.walk ?? 0) * 6) * s * .05;
    paint(rectPts(-s * 1.2, -s * .5 + bob, s * 2.2, s * .5, 2), { wash: mixCol(col, PAL.cream, .3), ink: PAL.ink, sw: .8 });
    paint(ellPts(s * 1.1, -s * 1.05 + bob, s * .38, s * .3, 8, 1), { wash: mixCol(col, PAL.cream, .3), ink: PAL.ink, sw: .7 });  // head up
    paint(ellPts(s * 1.15, -s * 1.3 + bob, s * .07, s * .07, 6), { wash: PAL.ink, ink: null });
    for (let a = 0; a < 10; a++) { const r = s * .15 + a * s * .055;   // spiral shell
      paint(ellPts(-s * .1, -s * .8 + bob, r, r * .92, 26 - a, 2), { ink: a % 2 ? PAL.ink : mixCol(shell, PAL.night, .2), sw: .55 });
    }
    paint(ellPts(-s * .1, -s * .8 + bob, s * .7, s * .65, 24, 2), { wash: shell, washOp: 60, fill: shell, fillOp: 45, ink: PAL.ink, sw: .8 });
    pop();
    return;
  }
  // turtle: shell + head + 4 phase-offset legs + tail. walk: pass gait t.
  const w = o.walk ?? 0, bob = Math.abs(Math.sin(w * 5)) * s * .06;
  for (let i = 0; i < 4; i++) {           // legs, alternating phase
    const lx = (i < 2 ? -1 : 1) * s * .42 + (i % 2 ? s * .18 : -s * .05);
    const ph = Math.sin(w * 5 + i * Math.PI / 2);
    paint(ellPts(lx + ph * s * .12, -s * .12 + bob, s * .14, s * .1, 8, 1), { wash: mixCol(col, PAL.night, .2), ink: PAL.ink, sw: .6 });
  }
  paint(ellPts(0, -s * .62 + bob, s * .62, s * .45, 22, 2), { wash: shell, fill: mixCol(shell, PAL.night, .3), fillOp: 60, ink: PAL.ink, sw: .9 });  // shell
  paint(ellPts(0, -s * .62 + bob, s * .38, s * .26, 18, 2), { wash: mixCol(shell, PAL.cream, .4), washOp: 90, ink: null });                            // plate
  paint(ellPts(s * .66, -s * .42 + bob, s * .18, s * .14, 10, 1), { wash: mixCol(col, PAL.cream, .3), ink: PAL.ink, sw: .7 });                          // head
  paint(ellPts(s * .72, -s * .47 + bob, s * .035, s * .035, 6), { wash: PAL.ink, ink: null });
  inkLine([[-s * .62, -s * .5 + bob], [-s * .8, -s * .42 + bob]], .7, mixCol(col, PAL.night, .2), 'ink', .3);                                            // tail
  pop();
}

/* PATTERN: CHASE_MOTION */
// Start/finish posts for track problems. kind: 'post' | 'flag' | 'finish'.
function marker(x, y, s, o = {}) {
  const kind = o.kind ?? 'post', col = o.col ?? PAL.ochre;
  boilSeed('mk' + kind);
  paint(ellPts(x, y, s * .1, s * .06, 10, 1), { wash: mixCol(PAL.ink, PAL.cream, .55), fill: mixCol(PAL.ink, PAL.cream, .55), fillOp: 80, ink: null });  // base mound
  paint(rectPts(x - s * .018, y - s, s * .036, s, 0), { wash: mixCol(PAL.ink, PAL.cream, .15), fill: mixCol(PAL.ink, PAL.cream, .15), fillOp: 200, ink: null });  // pole (solid)
  if (kind === 'post') {
    paint(ellPts(x, y - s, s * .12, s * .12, 10, 1), { wash: col, fill: col, fillOp: 140, ink: PAL.ink, sw: .8 });
    paint([[x, y - s], [x + s * .5, y - s + s * .13], [x, y - s + s * .26]], { wash: col, fill: col, fillOp: 90, ink: PAL.ink, sw: .7 });  // small pennant
  }
  if (kind === 'flag' || kind === 'finish') {
    paint([[x, y - s], [x + s * .55, y - s + s * .16], [x, y - s + s * .32]], { wash: kind === 'finish' ? PAL.cream : col, fill: col, fillOp: 80, ink: PAL.ink, sw: .7 });
    if (kind === 'finish') for (let i = 0; i < 3; i++)                      // checker hint
      paint(rectPts(x + i * s * .18, y - s + i * s * .1, s * .09, s * .11, 0), { wash: PAL.ink, ink: null });
  }
}

/* ---------- letter layer: the ENGINE already ships letter/sfx/flushLetters
   (core.js: letter auto-projects through the active camera; world space by
   default, screen space when CAM is off or o.screen). We only add a thin
   convenience wrapper. Letters composite on top by default; call the engine's
   flushLetters() at the end of a shot if later strokes (iris/wipe) must
   cover them. ---------- */
/* PATTERN: LIVE_ANNOTATION */
// Static label. o: { col, align:'left'|'center'|'right', rot, alpha, screen }
function label(txt, x, y, size, o = {}) {
  if (!txt) return;
  letter(txt, x, y, size, o.col ?? PAL.ink, { align: o.align ?? 'left', rot: o.rot, alpha: o.alpha, screen: o.screen });
}

/* ================= v1 additions (PATTERN_CORPUS.md verdicts) ================= */

/* PATTERN: BEAT_GRID */
// Beat clock. Configure once per shot: beatCfg(120, .21). beatAt(n) = absolute
// time of beat n (fractions ok: beatAt(6.5)); pulseBeat(t, n) = 1 on the beat,
// exponentially decaying before the next (k: sharpness). Sync anything to music.
const PAT_BEAT = { bpm: 120, off: 0 };
function beatCfg(bpm, off = 0) { PAT_BEAT.bpm = bpm; PAT_BEAT.off = off; }
function beatAt(n) { return PAT_BEAT.off + n * 60 / PAT_BEAT.bpm; }
function pulseBeat(t, n, o = {}) {
  const x = (t - PAT_BEAT.off) * PAT_BEAT.bpm / 60 - n;
  if (x < 0) return 0;
  const f = x - Math.floor(x);
  return Math.exp(-f * (o.k ?? 6));
}

/* PATTERN: EVENT_EMPHASIS *//* PATTERN: IMPACT_BURST */
// Deterministic debris burst at t0: n shards, each on a hash-seeded fan angle
// and velocity, with gravity and spin. Zero randomness across renders.
function impactBurst(x, y, t, t0, o = {}) {
  const life = o.life ?? .8, age = t - t0; if (age < 0 || age > life) return;
  const n = o.n ?? 10, g = o.g ?? 1400, col = o.col ?? PAL.ochre;
  const fade = 1 - seg(age, life * .6, life);
  for (let i = 0; i < n; i++) {
    const a = -Math.PI * (.08 + .84 * hash(i * 7 + 1)), v = (o.v0 ?? 520) + (o.spread ?? 700) * hash(i * 13 + 5);
    const px = x + Math.cos(a) * v * age, py = y + Math.sin(a) * v * age + g * age * age;
    const s = (o.size ?? 9) * (.5 + hash(i * 3 + 2) * .8) * fade;
    push(); translate(px, py); rotate(age * (4 + hash(i) * 8) + i);
    paint(rectPts(-s, -s * .35, s * 2, s * .7, 0), { wash: mixCol(col, PAL.night, .25 * hash(i * 11)), fill: col, fillOp: 90, ink: null });
    pop();
  }
}

/* PATTERN: ARC_TOSS */
// Parabolic toss position from a to b over [t0,t1], apex h px above the chord.
// Returns [x, y, p] — draw the object at [x,y]; use p for spin (rot = p*TAU).
// o.accel:true makes the flight accelerate (pow 1.7) — use when falling to target.
function arcThrow(t, t0, t1, a, b, o = {}) {
  let p = seg(t, t0, t1); if (p <= 0) return [a[0], a[1], 0]; if (p >= 1) return [b[0], b[1], 1];
  if (o.accel) p = Math.pow(p, 1.7); else p = ease(p);
  return [lerp(a[0], b[0], p), lerp(a[1], b[1], p) - Math.sin(p * Math.PI) * (o.h ?? 200), p];
}

/* PATTERN: SHAKE */
// Impact shake with exponential decay. Returns [dx, dy] — ADD to camBegin's
// cx/cy (or to a subject position). Deterministic per frame index.
function shake(t, t0, o = {}) {
  const dt = t - t0; if (dt < 0 || dt > 1.5) return [0, 0];
  const A = (o.amp ?? 12) * Math.exp(-dt * (o.decay ?? 6));
  if (A < .3) return [0, 0];
  const q = Math.floor(dt * 60);
  return [Math.sin(q * 12.9898) * A, Math.cos(q * 78.233) * A];
}

/* PATTERN: ACCELERATE_AND_SETTLE */
// Damped-spring settle value after an impact at t0 — feed into sq / dy of the
// subject that just landed. Pairs with anticipation (which covers the windup).
function settle(t, t0, o = {}) {
  const dt = t - t0; if (dt < 0) return 0;
  return (o.amp ?? .25) * Math.exp(-dt * (o.decay ?? 9)) * Math.cos(dt * (o.freq ?? 30));
}

/* PATTERN: EVENT_EMPHASIS *//* IDEA_BURST: glow rise + staggered sparkle fan (demo.js idiom) */
function ideaBurst(x, y, t, t0, o = {}) {
  const life = o.life ?? .9, age = t - t0; if (age < 0 || age > life) return;
  const k = age / life, col = o.col ?? '#FFD96A', n = o.n ?? 7;
  glow(x, y, (o.r0 ?? 60) + (o.r1 ?? 240) * (1 - Math.exp(-k * 5)), col, .25 + .6 * (1 - k));
  for (let i = 0; i < n; i++) {
    const q = clamp(seg(k, i * .04, .55 + i * .04));
    const ang = -Math.PI / 2 + (i - n / 2 + .5) * (o.spread ?? .35);
    const d = (o.dist ?? 180) * easeOut(q), s = 16 * (1 - q * .7);
    paint(starPts(x + Math.cos(ang) * d, y + Math.sin(ang) * d, s, s * .45, 5, 1.5), { wash: col, fill: col, fillOp: 80, ink: null });
  }
}

/* PATTERN: VOLUME_SQUASH */
// Volume-preserving squash/stretch factor k → scale pair for push();scale().
// k>0 squashes (landing), k<0 stretches (rising).
function squash(k, amt = .6) { return [1 + k * amt, 1 - k]; }

/* PATTERN: LIVE_ANNOTATION */
// Number counting from a to b over [t0,t1] with a screen-space label. Draws the
// label itself (letter layer). Returns current value.
function countUp(t, t0, t1, a, b, x, y, o = {}) {
  const k = seg(t, t0, t1); if (k <= 0) return null;
  const v = lerp(a, b, ease(k));
  label(v.toFixed(o.dec ?? 0) + (o.unit ?? ''), x, y, o.size ?? 22, { col: o.col ?? PAL.ink, align: o.align ?? 'left' });
  return v;
}

/* PATTERN: LIVE_ANNOTATION */
// Always-on readout panel (screen space): lines of [name, value] refreshed per
// frame — live x/y, clock, distance... THE quantitative-teaching widget.
function liveReadout(x, y, lines, o = {}) {
  const w = o.w ?? 250, lh = o.lh ?? 28, n = lines.length;
  paint(rectPts(x, y, w, lh * n + 14, 2), { wash: PAL.cream, washOp: 215, fill: PAL.cream, fillOp: 30, ink: PAL.ink, sw: .8 });
  lines.forEach((L, i) => {
    label(L[0], x + 12, y + 14 + i * lh, o.size ?? 15, { col: mixCol(PAL.ink, PAL.cream, .35) });
    label(String(L[1]), x + w - 12, y + 14 + i * lh, o.size ?? 15, { col: o.valCol ?? PAL.teal, align: 'right' });
  });
}

/* PATTERN: STAMP_ANSWER */
// Rubber-stamp answer confirmation: angled box thumps in, word inside, ring
// pulse. Screen space. The "this is THE answer" moment.
function stampAnswer(txt, x, y, t, t0, o = {}) {
  const dt = t - t0; if (dt < 0) return;
  const k = backOut(clamp(dt / .22)), fade = dt > 2.4 ? 1 - seg(dt, 2.4, 2.8) : 1;
  if (fade <= 0) return;
  const col = o.col ?? PAL.rose, w = o.w ?? 200, h = o.h ?? 66, rot = o.rot ?? -.12;
  push(); translate(x, y); rotate(rot); scale(k * fade, k * fade);
  paint(rectPts(-w / 2, -h / 2, w, h, 6), { wash: col, washOp: 55, fill: col, fillOp: 24, ink: col, sw: 2.6 });
  pop();
  letter(txt, x, y, o.size ?? 36, col, { rot, align: 'center', pop: Math.min(dt / .22, 1), alpha: fade });
  pulseRing(x, y, seg(dt, .06, .5), { r0: 30, r1: w * .85, col });
}

/* PATTERN: LEAVE_MARK *//* Geometry annotation marks (world space, inside camBegin). */
function markRight(x, y, s, o = {}) {          // right-angle square
  const c = o.col ?? PAL.ink;
  inkLine([[x + s, y], [x + s, y - s], [x, y - s]], o.sw ?? 1.2, c, 'ink', .2);
  if (o.dot) paint(ellPts(x + s * .5, y - s * .5, s * .1, s * .1, 6), { wash: c, ink: null });
}
function markTicks(a, b, n, o = {}) {          // n equal-part ticks across segment
  const c = o.col ?? PAL.rose;
  for (let i = 1; i < n; i++) {
    const x = lerp(a[0], b[0], i / n), y = lerp(a[1], b[1], i / n);
    inkLine([[x - 4, y - 8], [x + 4, y + 8]], 1.4, c, 'ink', .1);
  }
}
function markParallel(x, y, s, o = {}) {       // double chevron
  const c = o.col ?? PAL.ink;
  inkLine([[x - s * .5, y], [x + s * .5, y - s * .4]], 1.1, c, 'ink', .15);
  inkLine([[x - s * .5, y + s * .35], [x + s * .5, y - s * .05]], 1.1, c, 'ink', .15);
}
function markAngle(x, y, r, p0, p1, o = {}) {  // angle arc + sector, k animates the sweep
  const c = o.col ?? PAL.rose, k = ease(o.k ?? 1);
  const a0 = Math.atan2(p0[1] - y, p0[0] - x), a1 = Math.atan2(p1[1] - y, p1[0] - x);
  let d = a1 - a0; while (d < -Math.PI) d += Math.PI * 2; while (d > Math.PI) d -= Math.PI * 2;
  const P = [];
  for (let i = 0; i <= 18; i++) { const a = a0 + d * k * i / 18; P.push([x + Math.cos(a) * r, y + Math.sin(a) * r]); }
  inkLine(P, 1.3, c, 'ink', .1);
  if (o.fill !== false) paint([[x, y], ...P], { wash: c, washOp: 60, ink: null });
}

/* PATTERN: HIGHLIGHT_BOX */
// Screen-space box highlight around a condition/element — corner ticks first,
// then frame + tint. The "reading the problem aloud" widget.
function highlightBox(x, y, w, h, k, o = {}) {
  if (k <= 0) return;
  const col = o.col ?? PAL.rose, m = 10;
  if (k > .35) paint(rectPts(x - m, y - m, w + 2 * m, h + 2 * m, 4), { wash: col, washOp: Math.round(40 * clamp((k - .35) / .65)), ink: col, sw: 1.6 });
  const L = Math.min(22, w * .25) * clamp(k / .35);
  [[x - m, y - m, 1, 1], [x + w + m, y - m, -1, 1], [x - m, y + h + m, 1, -1], [x + w + m, y + h + m, -1, -1]]
    .forEach(([cx, cy, sx, sy]) => inkLine([[cx, cy + sy * L], [cx, cy], [cx + sx * L, cy]], 2.2, col, 'ink', .05));
}

/* PATTERN: SUPERPOSE_COPY */
// Ghost copy of a point-list shape, translating+rotating from its own pose
// onto a target — the "copy it onto the other one" proof move. k: 0..1.
function superposeCopy(pts, dx, dy, rot, k, o = {}) {
  if (k <= 0) return;
  const e = ease(k), col = o.col ?? PAL.teal;
  let cx = 0, cy = 0; pts.forEach(p => { cx += p[0]; cy += p[1]; }); cx /= pts.length; cy /= pts.length;
  push(); translate(cx + dx * e, cy + dy * e); rotate(rot * e); translate(-cx, -cy);
  paint(pts, { wash: col, washOp: 70, fill: col, fillOp: 0, ink: mixCol(col, PAL.night, .2), sw: .9 });
  pop();
}

/* PATTERN: NARRATION_ANCHOR */
// Narration clock: pass sentence start times [t0, t1, ..., tEnd]. Everything
// anchors to sentences, never to raw seconds. N.at(k,f) = time at fraction f
// of sentence k; N.win(k) = action window (15%..80% of the sentence); N.k(t)
// = current sentence index.
function narr(starts) {
  return {
    at: (k, f = 0) => starts[k] + (starts[k + 1] - starts[k]) * f,
    win: (k) => { const a = starts[k], b = starts[k + 1]; return [a + (b - a) * .15, a + (b - a) * .8]; },
    k: (t) => { for (let i = starts.length - 2; i >= 0; i--) if (t >= starts[i]) return i; return 0; },
  };
}

/* PATTERN: COLOR_BIND */
// Semantic role colors (edulab convention): known/blue, ask/red, aux/green,
// highlight/yellow. Bind figure parts, board rows and conclusions to the same
// color per role — never re-use a role color for another meaning in a shot.
const ROLE = { known: 'teal', ask: 'rose', aux: 'sap', hi: 'sun' };
function roleCol(r) { return r === 'hi' ? '#FFD96A' : PAL[ROLE[r] ?? 'teal']; }
