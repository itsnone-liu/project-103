// PROJECT = { duration: 24.566, bpm: 96 };
(() => {
  // ===== Parameters (verbatim from storyboard) =====
  const A = [700, 800], B = [1220, 800], C = [1019, 248];
  const r = 110;
  const D = Math.PI / 180;
  // derived ray directions (y-up CCW), computed with atan2 — never eyeballed
  const ang = (v, w) => Math.atan2(-(w[1] - v[1]), w[0] - v[0]);
  const aAB = ang(A, B), aAC = ang(A, C);           // 0°, 60°  -> ∠A = 60°
  const aBC = ang(B, C), aBA = ang(B, A);           // 110°,180°-> ∠B = 70°
  const aCA = ang(C, A), aCB = ang(C, B);           // 240°,290°-> ∠C = 50°
  const HR = [540, 380], HS = [1350, 300];          // hover points
  // NOTE(pipeline-fix): ROLE.* are palette KEY strings, not colors —
  // 'wash: "rose"' throws p5 "Invalid color string". Use roleCol().
  const colR = roleCol('ask'), colT = roleCol('known'), colS = roleCol('aux'), colH = roleCol('hi');

  // NOTE(pipeline-fix): narr() needs n+1 entries (sentence starts + tEnd);
  // without tEnd N.at(7,f) extrapolates to NaN and the whole tail never draws.
  const N = narr([0.0, 3.304, 5.822, 8.127, 11.07, 13.32, 15.807, 19.664, 24.566]);
  const K = t => N.k(t);

  // wedge polygon centered on its own vertex (vertex at origin, y-up dirs)
  function wedgePts(rad, d0, d1, n = 18) {
    const pts = [[0, 0]];
    for (let i = 0; i <= n; i++) {
      const a = lerp(d0, d1, i / n) * D;
      pts.push([rad * Math.cos(a), -rad * Math.sin(a)]);
    }
    return pts;
  }
  const wR = wedgePts(r, 0, 60);        // rose ∠A copy (goes to B as [0,60])
  const wT = wedgePts(r, 110, 180);     // teal host ∠B at B
  const wS = wedgePts(r, 240, 290);     // sap ∠C copy (rotates 180° -> [60,110])
  const midPt = (v, d0, d1, rad) => [v[0] + rad * Math.cos(lerp(d0, d1, .5) * D), v[1] - rad * Math.sin(lerp(d0, d1, .5) * D)];

  function drawWedge(pts, x, y, rot, col, kIn, o = {}) {
    if (kIn <= 0) return;
    boilSeed('w' + col + x.toFixed(0));
    push(); translate(x, y); rotate(rot || 0);
    paint(pts, { wash: col, washOp: 255 * kIn * (o.dim || 1), ink: PAL.ink, sw: 1.2, curv: 0 });
    pop();
  }
  function ghostWedge(pts, x, y, rot, col, kIn) {
    if (kIn <= 0) return;
    boilSeed('gh' + x);
    push(); translate(x, y); rotate(rot || 0);
    inkLine(pts.map(p => [p[0] + jit(3), p[1] + jit(3)]), .9, col, 'dry', 0);
    pop();
  }

  function shot(t, lt, dur) {
    const k = K(t);
    const at = (kk, f) => N.at(kk, f);
    const g = (kk, f0, f1) => seg(lt, at(kk, f0), at(kk, f1));

    // PATTERN: FREEZE_EVENT (snap moment in k=5)
    const ft = freezeFrame(lt, { at: at(5, .30), dur: .45, x: 1120, y: 680, flash: true, ring: true });
    const T = ft;

    // camera arc across narration
    const cam = kf(T, [
      [at(1, 0), [960, 620, 1.00]],
      [at(4, 0), [960, 620, 1.05]],
      [at(5, .5), [1120, 680, 1.18]],
      [at(7, 0), [960, 560, 1.00]],
      [dur, [960, 560, 1.00]],
    ], ease);
    const sh = shake(T, at(5, .30), { amp: 8, decay: 6 });
    camBegin(cam[0] + 12 * Math.sin(T * .5) + sh[0], cam[1] + 8 * Math.cos(T * .4) + sh[1], cam[2]);

    // background paper
    boilSeed('bg');
    paint(rectPts(-300, -300, W + 600, H + 600), { wash: PAL.paper, ink: null });
    paint(ellPts(960, 500, 1100, 620, 40, 3), { fill: PAL.sky, fillOp: 60, bleed: .2, tex: .4, ink: null });

    // triangle body (fades slightly once wedges torn)
    boilSeed('tri');
    paint([A, C, B], { wash: mixCol(PAL.paper, PAL.sky, .25), ink: PAL.ink, sw: 1.6, curv: 0 });

    // PATTERN: TRACE_PATH — three edges drawn one stroke
    const edge = (p, q, kk, f0, f1) => {
      const s = [];
      for (let i = 0; i <= 40; i++) { const u = i / 40; s.push([lerp(p[0], q[0], u), lerp(p[1], q[1], u)]); }
      tracePath(s, T, { mode: 'line', tail: .35, col: PAL.ink, every: 1, size: 2, t0: at(kk, f0), t1: at(kk, f1) });
    };
    edge(A, B, 1, .10, .22); edge(B, C, 1, .18, .32); edge(C, A, 1, .28, .45);
    // vertex ink dots
    [[A, 'A'], [B, 'B'], [C, 'C']].forEach(([v, nm], i) => {
      if (lt > at(1, .40)) { boilSeed('v' + nm); paint(ellPts(v[0], v[1], 7, 7, 10, 1), { wash: PAL.ink, ink: null }); }
    });

    // PATTERN: STAGGER_REVEAL — three angle arcs, rose→teal→sap
    const st = staggerReveal(lt, 3, { at: at(1, .45), gap: .12, dur: .4 });
    // PATTERN: COLOR_BIND — ∠A rose(ask) ∠B teal(known host) ∠C sap(aux)
    // PATTERN: CUSTOM:angle-wedge — filled wedges + arcs at original vertices
    const live = [g(2, .30, 1) > 0 ? 0 : 1, 1, g(3, .30, 1) > 0 ? 0 : 1]; // A and C wedges leave when torn
    const kR0 = st[0] * live[0], kT0 = st[1] * live[1], kS0 = st[2] * live[2];
    drawWedge(wR, A[0], A[1], 0, colR, kR0, { dim: 1 });
    drawWedge(wT, B[0], B[1], 0, colT, kT0);
    drawWedge(wS, C[0], C[1], 0, colS, kS0);

    // PATTERN: LEAVE_MARK — dashed ghosts where wedges were torn
    ghostWedge(wR, A[0], A[1], 0, colR, g(2, .30, .34));
    ghostWedge(wS, C[0], C[1], 0, colS, g(3, .30, .34));

    // PATTERN: NARRATION_ANCHOR / LIVE_ANNOTATION — numbers land and hold
    // PATTERN: HOLD
    const nums = [
      ['60', midPt(A, 0, 60, r + 80), colR, g(1, .72, .78)],
      ['70', midPt(B, 110, 180, r + 80), colT, g(1, .80, .86)],
      ['50', midPt(C, 240, 290, r + 80), colS, g(1, .88, .94)],
    ];
    nums.forEach(([txt, p, c, kk]) => { if (kk > 0) sfx(txt, p[0], p[1], 46, c, (lt - at(1, .7)) * 2); });

    // ===== torn-wedge state machines (closed form) =====
    function roseState() {
      if (k < 2) return { x: A[0], y: A[1], rot: 0, vis: 0 };
      // PATTERN: ANTICIPATION_WINDUP — shudder/curl before the tear
      const an = anticipation(T, { t0: at(2, .05), windup: N.win(2)[1] * .0 + (at(2, .30) - at(2, .05)), strike: .1, settle: .2 });
      const jx = (an.w > 0 && an.w < 1) ? jit(6) : 0;
      if (lt < at(2, .30)) return { x: A[0] + jx, y: A[1] - 3 * (an.w || 0), rot: -.06 * (an.w || 0), vis: 1 };
      // PATTERN: ARC_TOSS — A -> hover -> B
      if (lt < at(2, .62)) { const f = arcThrow(T, at(2, .30), at(2, .62), [A[0], A[1] - 40], HR, { h: 180 }); return { x: f[0], y: f[1], rot: .15 * Math.sin(f[2] * 6.28), vis: 1 }; }
      if (k < 4 || lt < at(4, .05)) return { x: HR[0], y: HR[1] + 7 * Math.sin(T * 2.2), rot: .04 * Math.sin(T * 1.7), vis: 1 };
      if (lt < at(4, .35)) { const f = arcThrow(T, at(4, .05), at(4, .35), HR, [B[0], B[1] - 30], { h: 180 }); return { x: f[0], y: f[1], rot: .1 * Math.sin(f[2] * 9), vis: 1 }; }
      if (lt < at(5, .30)) return { x: B[0], y: B[1] - 34 + 5 * Math.sin(T * 3), rot: 0, vis: 1 };
      return null; // assembled
    }
    function sapState() {
      if (k < 3) return { x: C[0], y: C[1], rot: 0, vis: 0 };
      const an = anticipation(T, { t0: at(3, .05), windup: at(3, .30) - at(3, .05), strike: .1, settle: .2 });
      const jx = (an.w > 0 && an.w < 1) ? jit(6) : 0;
      if (lt < at(3, .30)) return { x: C[0] + jx, y: C[1] - 3 * (an.w || 0), rot: .06 * (an.w || 0), vis: 1 };
      if (lt < at(3, .62)) { const f = arcThrow(T, at(3, .30), at(3, .62), [C[0], C[1] + 30], HS, { h: 180 }); return { x: f[0], y: f[1], rot: .2 * Math.sin(f[2] * 6.28), vis: 1 }; }
      if (k < 4 || lt < at(4, .35)) return { x: HS[0], y: HS[1] + 7 * Math.sin(T * 2.4 + 1), rot: -.04 * Math.sin(T * 1.9), vis: 1 };
      if (lt < at(4, .68)) { // staggered launch, rotating half turn (180°) to aim at the gap
        const f = arcThrow(T, at(4, .35), at(4, .68), HS, [B[0], B[1] - 30], { h: 200 });
        return { x: f[0], y: f[1], rot: lerp(0, Math.PI, ease(f[2])), vis: 1 };
      }
      if (lt < at(5, .05)) return { x: B[0], y: B[1] - 40 + 5 * Math.sin(T * 3 + 2), rot: Math.PI, vis: 1 };
      return null;
    }
    const rs = roseState(), ss = sapState();
    if (rs && rs.vis) drawWedge(wR, rs.x, rs.y, rs.rot, colR, 1);
    if (ss && ss.vis) drawWedge(wS, ss.x, ss.y, ss.rot, colS, 1);

    // PATTERN: EVENT_EMPHASIS — gap edge flashes while wedges hover over B
    const flash2 = (k === 4) ? (pulse2(T, 8) * g(4, .68, 1)) : 0;
    if (flash2 > 0) {
      boilSeed('gap');
      const gp = midPt(B, 0, 110, r * .8);
      glow(gp[0], gp[1], 60, colH, 120 * flash2);
    }

    // ===== k=5 assembly =====
    if (lt >= at(5, .05)) {
      const spin = g(5, .05, .30);
      // PATTERN: SUPERPOSE_COPY — copies snapped onto vertex B, non-zero rotations
      const rr = (rs === null);
      if (rr) superposeCopy(wR, B[0], B[1], 0.03, g(5, .28, .34), { col: colR });
      if (ss === null) superposeCopy(wS, B[0], B[1], Math.PI, g(5, .28, .34), { col: colS });
      if (spin > 0 && spin < 1) { // wedges spiralling into their slots (pre-snap)
        const e = easeIn(spin);
        if (rs) drawWedge(wR, lerp(rs.x, B[0], e), lerp(rs.y, B[1], e), lerp(rs.rot, .03, e), colR, 1);
        if (ss) drawWedge(wS, lerp(ss.x, B[0], e), lerp(ss.y, B[1], e), lerp(ss.rot, Math.PI, e), colS, 1);
      }
      // PATTERN: IMPACT_BURST — snap sparks
      impactBurst(B[0], B[1] - 20, T, at(5, .30), { n: 12, g: 900, col: colH, size: 7, life: .5 });
    }

    // ===== k=6 straight line =====
    if (lt > at(6, .08)) {
      // PATTERN: TRACE_PATH — the straight edge sweeps out from B
      const lp = [];
      for (let i = 0; i <= 40; i++) lp.push([lerp(1500, 940, i / 40), 800]);
      tracePath(lp, T, { mode: 'line', tail: .3, col: PAL.ink, t0: at(6, .08), t1: at(6, .45), every: 1, size: 2.2 });
      // PATTERN: BEAT_GRID — wedges light up one per beat
      beatCfg(96);
      const b1 = pulseBeat(T, 1), b2 = pulseBeat(T, 2), b3 = pulseBeat(T, 3);
      const hl = g(6, .45, 1);
      if (hl > 0) {
        if (lt > at(6, .45)) glow(B[0] + r * .5, B[1] - 30, 70, colR, 130 * b1 * hl);
        if (lt > at(6, .62)) glow(B[0] - 10, B[1] - 70, 70, colS, 130 * b2 * hl);
        if (lt > at(6, .80)) glow(B[0] - r * .6, B[1] - 40, 70, colT, 130 * b3 * hl);
      }
    }
    camEnd();

    // ===== screen-space widgets =====
    // PATTERN: FOCUS_REVEAL — dim the frame during each tear
    const dimR = g(2, .05, .30) * (1 - g(2, .28, .34)), dimS = g(3, .05, .30) * (1 - g(3, .28, .34));
    if (dimR > 0) dimOthers(540, 380, 500, 500, .5 * dimR, PAL.ink);
    if (dimS > 0) dimOthers(1350, 300, 500, 500, .5 * dimS, PAL.ink);

    // ===== k=7 equation =====
    if (lt > at(7, .05)) {
      // PATTERN: COUNT_UP — 60 + 70 + 50, colour-matched
      countUp(T, at(7, .05), at(7, .25), 0, 60, 700, 190, { col: colR, size: 60, unit: '°' });
      countUp(T, at(7, .20), at(7, .40), 0, 70, 890, 190, { col: colT, size: 60, unit: '°' });
      countUp(T, at(7, .35), at(7, .55), 0, 50, 1080, 190, { col: colS, size: 60, unit: '°' });
      // PATTERN: LIVE_READOUT / EVENT_EMPHASIS — total rolls to 180
      countUp(T, at(7, .55), at(7, .85), 0, 180, 1300, 190, { col: colH, size: 72, unit: '°' });
      if (lt > at(7, .85)) pulseRing(1300, 190, g(7, .85, 1), { r0: 20, r1: 140, col: colH, double: true });
      label('+', 800, 190, 48, { col: PAL.ink }); label('+', 990, 190, 48, { col: PAL.ink }); label('=', 1200, 190, 48, { col: PAL.ink });
    }

    // ===== k=8 stamp + recap =====
    // NOTE(pipeline-fix): at(8,*) is out of range (8 sentences => at() max k=7
    // with tEnd appended). Remapped the tail zone onto sentence-7 fractions.
    if (lt > at(7, .70)) {
      // PATTERN: STAMP_ANSWER
      stampAnswer('180°', 1120, 330, T, at(7, .73), { col: colH, w: 360, h: 150, size: 96, rot: -.08 });
      impactBurst(1120, 330, T, at(7, .75), { n: 14, g: 700, col: colH, size: 8, life: .5 });
      // PATTERN: SHOW_BEFORE_AFTER / HIGHLIGHT_BOX — recap board
      const bk = g(7, .80, .90);
      if (bk > 0) {
        highlightBox(210, 830, 1500, 200, bk, { col: PAL.ink });
        beforeAfter(lt, {
          at: at(7, .82), y: 930, w: 1300, span: 180, unit: '°', numbers: true,
          rows: [
            { col: colR, from: 0, to: 60, fromVal: 0, toVal: 60 },
            { col: colT, from: 60, to: 130, fromVal: 0, toVal: 70 },
            { col: colS, from: 130, to: 180, fromVal: 0, toVal: 50 },
          ],
        });
      }
      // golden close
      const gl = g(7, .90, 1);
      if (gl > 0) glow(960, 540, 700, colH, 40 * gl);
    }

    // ===== transitions =====
    if (lt < .5) iris(980, 616, lerp(0, 1600, easeOut(lt / .5)), PAL.paper);                       // in
    const w3 = N.at(3, 0), w7 = N.at(7, 0);
    if (lt > w3 && lt < w3 + .8) brushWipe((lt - w3) / 1.1, [colS, PAL.paper]);                     // B->C sap wipe
    if (lt > w7 && lt < w7 + .8) brushWipe((lt - w7) / 1.1, [PAL.paper, PAL.paper]);                // F->G paper wipe
    const w8 = N.at(7, .78);
    if (lt > w8 && lt < w8 + .5) {                                                                  // G->H triangle iris
      const hole = [[960, 340], [1210, 740], [710, 740]].map(p => [lerp(960, p[0], .9), lerp(540, p[1], .9)]);
      irisShape(hole, PAL.paper);
    }
    if (lt > dur - .7) { flushLetters(); iris(1120, 330, lerp(1500, 0, easeIn((lt - (dur - .7)) / .7)), PAL.paper); } // out
  }
  shots([[0, shot]]);
})();
