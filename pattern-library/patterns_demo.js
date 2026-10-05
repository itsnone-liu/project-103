// patterns_demo.js — regression scene for Pattern Library v0 primitives.
// Exercises: STAGGER_REVEAL, TRACE_PATH, ACCELERATE_AND_SETTLE, CHASE_MOTION,
// CAMERA_PUSH, FREEZE_EVENT, EVENT_EMPHASIS(dimOthers/pulseRing), HOLD,
// SHOW_BEFORE_AFTER, creature kit (turtle/snail), marker kit.
// Math (declared, fail-closed): turtle 60 px/s from t=0.8 at post x=300;
// Clawd 120 px/s from t=4.0 at the SAME post; meet at 60(t-.8)=120(t-4)
// => t=7.2, x=684; both walked 384 px.
// src/config.js: PROJECT = { duration: 12.5, bpm: 120 };
(() => {
  const G = 900;                                   // ground line y
  const POST = 300, FINISH = 1100;
  const VT = 60, VC = 120, T0 = 0.8, C0 = 4.0;     // declared parameters
  const xT = t => POST + VT * Math.max(0, t - T0);
  const xC = t => POST + VC * Math.max(0, t - C0);
  const MEET_T = 7.2, MEET_X = 684, WALKED = 384;  // derived, checked above

  // precomputed trail samples (shot-local t)
  const S_T = [], S_C = [];
  for (let t = 0; t <= 12.6; t += .1) {
    S_T.push([t, xT(t), G]);
    if (t >= C0) S_C.push([t, xC(t), G - 26]);
  }

  function ground(lt) {
    paint(rectPts(-200, G, W + 400, 400, 3), { wash: mixCol(PAL.sap, PAL.cream, .45), fill: mixCol(PAL.sap, PAL.night, .3), fillOp: 80, bleed: .05, tex: .6, ink: null });
    inkLine([[-200, G], [W + 200, G - 6]], 1, PAL.ink, 'ink', .4);
  }

  function shot(t, lt, dur) {
    // PATTERN: STAGGER_REVEAL — world appears before the actors
    const rv = staggerReveal(lt, 5, { at: .4, gap: .3, dur: .5 });
    camBegin(clamp((xT(Math.min(lt, MEET_T)) + xC(lt)) / 2 + 140, 560, 900), 600,
             pushIn(lt, { t0: 6.2, t1: 7.2, from: 1, to: 1.12 }));   // PATTERN: CAMERA_PUSH
    ground(lt);
    if (rv[0] > 0) { push(); scale(rv[0], rv[0]); marker(POST, G, 150, { kind: 'post' }); pop(); }        // start post
    if (rv[1] > 0) { push(); scale(rv[1], rv[1]); marker(FINISH, G - 4, 160, { kind: 'finish' }); pop(); } // finish flag
    if (rv[2] > 0) for (let i = 0; i < 8; i++) {                                                        // grass tufts (bold leaf blobs)
      const gx = 340 + i * 120, k = rv[Math.min(4, 2 + (i % 3))];
      boilSeed('g' + i);
      const gc = mixCol(PAL.sap, PAL.night, .3);
      for (const [dx, h] of [[-10, 46], [2, 60], [14, 42]])
        paint(ellPts(gx + dx + h * .12, G + 4 - h * k * .5, 6, h * k * .62, 8, 1.5, .25), { wash: gc, fill: gc, fillOp: 140, ink: null });
    }
    if (rv[3] > 0) creature(1240, G + 10, 58, { kind: 'snail', walk: lt * .25 });                         // spectator snail

    // PATTERN: TRACE_PATH — both trails, dotted, fading
    tracePath(S_T, Math.min(lt, MEET_T), { mode: 'dots', tail: 4, col: PAL.teal, bg: mixCol(PAL.sap, PAL.cream, .45), every: .35, size: 9 });
    if (lt > C0) tracePath(S_C, Math.min(lt, MEET_T + .4), { mode: 'dots', tail: 3, col: PAL.ochre, bg: mixCol(PAL.sap, PAL.cream, .45), every: .25, size: 7 });

    // PATTERN: FREEZE_EVENT — draw everything with ft
    const ft = freezeFrame(lt, { at: MEET_T, dur: .6, x: MEET_X, y: G - 90, flash: false });
    const tt = Math.min(ft, MEET_T), tc = Math.min(ft, MEET_T);
    creature(xT(tt), G + 14, 95, { kind: 'turtle', walk: tt });                                          // the turtle
    const ant = anticipation(ft, { t0: 3.5, windup: .35, strike: .15 });                                 // PATTERN: ACCELERATE_AND_SETTLE
    if (lt < C0 + .1) {                                                                                  // waiting + pounce prep
      const mood = emotions(ft, [[0, 'sleepy'], [1.5, 'curious'], [3.0, 'determined']]);
      clawd(POST - 10, G, 26, { ...mood, sq: (mood.sq || 0) - .22 * Math.max(0, -ant), dy: .25 * ant, view: 'side' });
    } else {
      const run = stroll(ft, C0, MEET_T, POST - 10, MEET_X - 170, 26);
      const mood = emotions(ft, [[C0, 'excited'], [MEET_T, 'surprised', { lookX: .8 }], [MEET_T + .8, 'happy']]);
      const still = hold(lt, MEET_T, .6);                                                                // PATTERN: HOLD
      clawd(run.x, G, 26, { ...mood, view: 'side', walk: still ? 0 : run.walk, dy: (mood.dy || 0) + .3 * ant + (still ? 0 : run.dy) });
    }
    if (lt > MEET_T + .1) {                                                                              // walk on together
      const k2 = easeOut(seg(lt, MEET_T + .7, MEET_T + 2.2));
      creature(lerp(MEET_X, FINISH - 90, k2), G + 14, 95, { kind: 'turtle', walk: lt });
      const w2 = stroll(lt, MEET_T + .7, MEET_T + 2.2, MEET_X - 170, FINISH - 280, 26);
      clawd(w2.x, G, 26, { view: 'side', walk: w2.walk, dy: w2.dy, aR: .6 * seg(lt, MEET_T + 1.2, MEET_T + 1.8) });
    }
    const eye = toScreen(MEET_X, G - 70);
    camEnd();

    // PATTERN: EVENT_EMPHASIS — screen-space focus on the freeze
    if (lt >= MEET_T && lt < MEET_T + .9) dimOthers(eye[0] - 220, eye[1] - 200, 440, 400, seg(lt, MEET_T, MEET_T + .25));
    if (lt > MEET_T + 1.2) pulseRing(eye[0], eye[1], seg(lt, MEET_T + 1.2, MEET_T + 1.8), { r0: 60, r1: 200, col: PAL.rose, double: true });

    // PATTERN: SHOW_BEFORE_AFTER — summary panel (screen space)
    if (lt > 9.6) beforeAfter(lt, {
      at: 9.6, y: 250, w: 1000, ticks: 8, span: 800, unit: 'px', numbers: true,
      rows: [
        { col: PAL.teal, from: 0, to: WALKED / 800 * 1000, dash: true },
        { col: PAL.ochre, from: 0, to: WALKED / 800 * 1000 },
      ],
    });
    boilSeed('transition');
    if (lt > dur - .5) iris(W / 2, G - 120, lerp(1500, 0, easeIn(seg(lt, dur - .5, dur - .12))));
  }

  shots([[0, shot]]);
})();
