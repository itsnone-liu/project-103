// patterns_demo2.js — Pattern Library v1 regression scene (teaching structure).
// Covers: NARRATION_ANCHOR, HIGHLIGHT_BOX, LIVE_ANNOTATION(countUp/liveReadout),
// BEAT_GRID, IDEA_BURST, ARC_TOSS, IMPACT_BURST, SHAKE, SETTLE, VOLUME_SQUASH,
// STAMP_ANSWER, LEAVE_MARK family, SUPERPOSE_COPY, COLOR_BIND, letter/sfx layer,
// + all v0 primitives. Math identical to demo1: meet at t=7.2, x=684, 384px each.
// src/config.js: PROJECT = { duration: 12.5, bpm: 120 };
(() => {
  const G = 900, POST = 300, FINISH = 1100;
  const VT = 60, VC = 120, T0 = 0.8, C0 = 4.0;
  const xT = t => POST + VT * Math.max(0, t - T0);
  const xC = t => POST + VC * Math.max(0, t - C0);
  const MEET_T = 7.2, MEET_X = 684, WALKED = 384;
  const S_T = [], S_C = [];
  for (let t = 0; t <= 12.6; t += .1) { S_T.push([t, xT(t), G]); if (t >= C0) S_C.push([t, xC(t), G - 26]); }

  // Timing table = TTS physical truth (audio/timing_patterns_demo2.json, AUDIT PASS
  // +0.02s): starts [0, 3.55, 7.15, 9.861, 13.99], total 19.635. k1 opens at 3.55 →
  // "四秒时" lands ~3.7 (Clawd launches 4.0); k2 opens 7.15 → "七点二秒" lands ~7.3
  // (visual meet 7.2). 差距缩小 is delegated to the live readout (动即推理).
  const N = narr([0, 3.55, 7.15, 9.861, 13.99, 19.635]);
  beatCfg(120, 0);

  function ground(lt) {
    paint(rectPts(-200, G, W + 400, 400, 3), { wash: mixCol(PAL.sap, PAL.cream, .45), fill: mixCol(PAL.sap, PAL.night, .3), fillOp: 80, bleed: .05, tex: .6, ink: null });
    inkLine([[-200, G], [W + 200, G - 6]], 1, PAL.ink, 'ink', .4);
  }

  function shot(t, lt, dur) {
    const rv = staggerReveal(lt, 3, { at: .3, gap: .3, dur: .5 });
    const [shx, shy] = shake(lt, MEET_T, { amp: 10 });                     // SHAKE
    camBegin(clamp((xT(Math.min(lt, MEET_T)) + xC(lt)) / 2 + 140 + shx, 560, 900) + shy * 0, 600 + shy,
             pushIn(lt, { t0: 6.2, t1: 7.2, from: 1, to: 1.1 }));
    ground(lt);
    if (rv[0] > 0) { push(); scale(rv[0], rv[0]); marker(POST, G, 150, { kind: 'post' }); pop(); }
    if (rv[1] > 0) { push(); scale(rv[1], rv[1]); marker(FINISH, G - 4, 160, { kind: 'finish' }); pop(); }
    if (rv[2] > 0) creature(1240, G + 10, 58, { kind: 'snail', walk: lt * .25 });
    // LEAVE_MARK family (world space)
    markRight(POST + 14, G - 4, 26, { col: mixCol(PAL.ink, PAL.cream, .3) });              // 起点桩⊥地面
    if (lt > MEET_T + 1.5) {                                                               // 等分刻度: 相遇点把两段轨迹各分份
      markTicks([POST + 20, G - 24], [MEET_X, G - 24], 4, { col: roleCol('known') });
      markTicks([POST + 20, G - 46], [MEET_X, G - 46], 4, { col: roleCol('ask') });
      markParallel(MEET_X + 90, G - 90, 40, { col: mixCol(PAL.ink, PAL.cream, .25) });     // 两条轨迹平行
      markAngle(MEET_X - 60, G, 54, [MEET_X, G], [POST, G - 260], { k: seg(lt, MEET_T + 2.1, MEET_T + 2.6), col: roleCol('aux') });
    }
    // trails + freeze
    tracePath(S_T, Math.min(lt, MEET_T), { mode: 'dots', tail: 4, col: roleCol('known'), bg: mixCol(PAL.sap, PAL.cream, .45), every: .35, size: 9 });
    if (lt > C0) tracePath(S_C, Math.min(lt, MEET_T + .4), { mode: 'dots', tail: 3, col: roleCol('ask'), bg: mixCol(PAL.sap, PAL.cream, .45), every: .25, size: 7 });
    const ft = freezeFrame(lt, { at: MEET_T, dur: .6, x: MEET_X, y: G - 90, ring: false, flash: false });
    const tt = Math.min(ft, MEET_T);
    creature(xT(tt), G + 14, 95, { kind: 'turtle', walk: tt });
    const ant = anticipation(ft, { t0: 3.5, windup: .35, strike: .15 });
    if (lt < C0 + .1) {
      const mood = emotions(ft, [[0, 'sleepy'], [1.5, 'curious'], [3.0, 'determined']]);
      clawd(POST - 10, G, 26, { ...mood, sq: (mood.sq || 0) - .22 * Math.max(0, -ant), dy: .25 * ant, view: 'side' });
    } else {
      const run = stroll(ft, C0, MEET_T, POST - 10, MEET_X - 170, 26);
      const mood = emotions(ft, [[C0, 'excited'], [MEET_T, 'surprised', { lookX: .8 }], [MEET_T + .8, 'happy']]);
      const still = hold(lt, MEET_T, .6);
      const st = settle(ft, MEET_T, { amp: .3 });                                          // SETTLE after landing
      const pb = still ? 0 : pulseBeat(ft, Math.round((ft - C0) * 2));                      // BEAT_GRID hop kick
      clawd(run.x, G, 26, { ...mood, view: 'side', walk: still ? 0 : run.walk, sq: (mood.sq || 0) + st + .06 * pb, dy: (mood.dy || 0) + .3 * ant + (still ? 0 : run.dy) - .04 * pb });
    }
    // ARC_TOSS: an acorn arcs from turtle to meet point right before freeze
    const ap = arcThrow(lt, 6.3, 6.9, [xT(6.3), G - 60], [MEET_X - 20, G - 140], { h: 160, accel: true });
    if (lt >= 6.3 && lt <= 6.95) { push(); translate(ap[0], ap[1]); rotate(ap[2] * 6.2);
      paint(ellPts(0, 0, 12, 15, 10, 1.5), { wash: PAL.ochre, fill: mixCol(PAL.ochre, PAL.night, .3), fillOp: 80, ink: PAL.ink, sw: .8 }); pop(); }
    // walk-on together
    if (lt > MEET_T + .1) {
      const k2 = easeOut(seg(lt, MEET_T + .7, MEET_T + 2.2));
      creature(lerp(MEET_X, FINISH - 90, k2), G + 14, 95, { kind: 'turtle', walk: lt });
      const w2 = stroll(lt, MEET_T + .7, MEET_T + 2.2, MEET_X - 170, FINISH - 280, 26);
      clawd(w2.x, G, 26, { view: 'side', walk: w2.walk, dy: w2.dy, aR: .6 * seg(lt, MEET_T + 1.2, MEET_T + 1.8) });
    }
    // IMPACT_BURST + IDEA_BURST (world space)
    impactBurst(MEET_X, G - 60, lt, MEET_T, { n: 12, col: roleCol('ask'), v0: 420, spread: 520 });
    ideaBurst(POST - 10, G - 260, lt, 3.5, { n: 7, r1: 200 });                             // 灵感:决定去追
    camEnd();

    // ---- screen space ----
    const eye = toScreen(MEET_X, G - 70);
    if (lt >= MEET_T && lt < MEET_T + .9) dimOthers(eye[0] - 220, eye[1] - 200, 440, 400, seg(lt, MEET_T, MEET_T + .25));
    if (lt > MEET_T + 1.2) pulseRing(eye[0], eye[1], seg(lt, MEET_T + 1.2, MEET_T + 1.8), { r0: 60, r1: 200, col: PAL.rose, double: true });
    // HIGHLIGHT_BOX: 题面卡片 (句0)
    const qk = ease(seg(lt, N.win(0)[0], N.win(0)[1]));
    if (qk > 0 && lt < 5.2) {
      highlightBox(70, 60, 560, 96, qk, { col: roleCol('known') });
      label('乌龟 60 px/s 先出发', 88, 84, 24, { col: PAL.ink });
      label('Clawd 120 px/s 同时同地起追', 88, 118, 24, { col: roleCol('ask') });
    }
    // LIVE_READOUT (句1起常驻): 位置与差距实时更新
    if (lt >= N.at(1, 0)) liveReadout(70, 200, [
      ['乌龟 x', Math.round(xT(Math.min(lt, MEET_T)) - POST) + ' px'],
      ['Clawd x', Math.round(Math.max(0, xC(Math.min(lt, MEET_T)) - POST)) + ' px'],
      ['相差 Δx', Math.round(Math.max(0, (xT(Math.min(lt, MEET_T)) - POST) - Math.max(0, xC(Math.min(lt, MEET_T)) - POST))) + ' px'],
    ], { valCol: roleCol('known') });
    // COUNT_UP at meet: both distances count to 384
    if (lt >= MEET_T + .1) {
      countUp(lt, MEET_T + .1, MEET_T + .9, 0, WALKED, 950, 300, { col: roleCol('known'), size: 26, unit: ' px' });
    }
    // STAMP_ANSWER (k2 相遇句中段)
    if (lt >= N.at(2, .3)) stampAnswer('相遇 t=7.2s', W / 2, 430, lt, N.at(2, .3), { col: roleCol('ask') });
    // SUPERPOSE_COPY proof (k3): clawd 路程条复制到乌龟条上重合
    if (lt > N.at(3, .1)) {
      const pk = ease(seg(lt, N.at(3, .1), N.at(3, .9)));
      const bx = 480, by = 560, bw = 300;
      const barT = rectPts(bx, by, bw, 26, 2), barC = rectPts(bx, by + 50, bw, 26, 2);
      paint(barT, { wash: roleCol('known'), washOp: 90, ink: roleCol('known'), sw: 1.2 });
      paint(barC, { wash: roleCol('ask'), washOp: 90, ink: roleCol('ask'), sw: 1.2 });
      label('乌龟路程', bx + bw + 14, by + 13, 18, { col: roleCol('known') });
      label('Clawd路程', bx + bw + 14, by + 63, 18, { col: roleCol('ask') });
      superposeCopy(barC, 0, -50, 0, pk, { col: roleCol('ask') });
      if (pk >= 1) label('两段路程相等 = 384 px', bx, by + 110, 26, { col: PAL.ink });
    }
    // sfx words (ENGINE signature: txt, x, y, size, color, age, o)
    sfx('嗖!', 700, 380, 46, roleCol('ask'), lt - 3.9, { life: .9 });
    sfx('啪!', 1100, 340, 54, PAL.rose, lt - MEET_T, { life: 1 });
    // SHOW_BEFORE_AFTER (k4) with numbers
    if (lt > N.at(4, 0)) beforeAfter(lt, {
      at: N.at(4, 0), y: 620, w: 900, ticks: 8, span: 800, unit: 'px', numbers: true,
      title: '同起点同相遇点: 路程相等, 时间不同',
      rows: [
        { col: roleCol('known'), from: 0, to: WALKED / 800 * 900, toVal: 384, fromVal: 0, dash: true },
        { col: roleCol('ask'), from: 0, to: WALKED / 800 * 900, toVal: 384, fromVal: 0 },
      ],
    });
    boilSeed('transition');
    if (lt > dur - .5) iris(W / 2, G - 120, lerp(1500, 0, easeIn(seg(lt, dur - .5, dur - .12))));
    flushLetters();                                                       // LAST line: stamp text into scene
  }

  shots([[0, shot]]);
})();
