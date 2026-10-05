// src/scenes/butterfly.js — "The Butterfly", 15 s.
// config.js must contain:  duration: 15,  (bpm: 96 recommended)
(() => {
  const WIPE = [mixCol(PAL.ochre, PAL.cream, .4), mixCol(PAL.rose, PAL.cream, .3)];
  const GRASS = mixCol(PAL.sap, PAL.cream, .18);
  const GRASSD = mixCol(PAL.sap, PAL.night, .3);

  // ---------- the butterfly: two painted wings flapping on the beat, a body, a flutter path ----------
  function butterfly(x, y, s, ang, flap, colA = '#F28DB2', colB = '#F4C95D') {
    boilSeed('butterfly');
    push(); translate(x, y); rotate(ang);
    const w = Math.sin(flap * TAU);           // 1 open .. -1 folded
    for (const side of [-1, 1]) {
      const wx = side * (0.55 + 0.45 * w) * s; // wings fold toward the body
      paint(ellPts(wx * .6, -s * .42, s * .62 * (0.4 + 0.6 * w), s * .5, 14, 1.5),
        { wash: colA, ink: PAL.ink, sw: Math.max(.4, s / 30), curv: .8 });
      paint(ellPts(wx * .62, s * .18, s * .42 * (0.4 + 0.6 * w), s * .34, 12, 1.5),
        { wash: colB, ink: PAL.ink, sw: Math.max(.35, s / 34), curv: .8 });
    }
    paint(ellPts(0, 0, s * .1, s * .45, 10, .6), { wash: PAL.ink, ink: null });
    pop();
  }
  // fluttering position: figure-eight-ish wander around (cx, cy), always moving, never still
  const flutter = (t, cx, cy, r, ph = 0) => [
    cx + Math.sin(t * 2.1 + ph) * r + Math.sin(t * 5.3 + ph) * r * .2,
    cy + Math.sin(t * 4.2 + ph * 2) * r * .45 + Math.cos(t * 3.1) * r * .12
  ];

  // ---------- meadow ----------
  // fgFlowers: detailed foreground blooms (shots A/B) or soft out-of-focus dots only (the close-up,
  // so nothing sits in front of Clawd's face)
  function meadow(t, wide = true, fgFlowers = true) {
    boilSeed('sky');
    paint(rectPts(-400, -300, W + 800, H + 600), { wash: mixCol(PAL.cream, PAL.sky, .35), ink: null });
    paint(ellPts(W * .5, -160, W * .9, 380, 30, 12), { fill: PAL.ochre, fillOp: 60, bleed: .3, tex: .5, ink: null });
    if (wide) {
      boilSeed('hills');
      paint(ellPts(W * .25, 980, 1100, 300, 30, 6), { fill: mixCol(PAL.ochre, PAL.cream, .3), fillOp: 160, bleed: .2, tex: .5, ink: null });
      paint(ellPts(W * .82, 1020, 1000, 280, 30, 6), { fill: mixCol(PAL.sap, PAL.cream, .4), fillOp: 150, bleed: .2, tex: .5, ink: null });
    }
    boilSeed('ground');
    paint(ellPts(W / 2, H + 320, W * .95, 440, 40, 8), { wash: GRASS, fill: GRASSD, fillOp: 70, bleed: .06, tex: .6, ink: null });
    if (fgFlowers) {
      // 30% fewer flowers than before: the butterfly stays the one moving thing that reads
      for (let i = 0; i < 18; i++) {
        boilSeed('fl' + i);
        const fx = hash(i) * (W + 300) - 150, fy = 800 + hash(i + 50) * 280;
        const sway = wob(t, .4, hash(i + 9) * 3) * 6;
        inkLine([[fx, fy], [fx + sway, fy - 46 - 14 * hash(i + 7)]], .8, mixCol(GRASS, PAL.night, .3), 'inkfine', .4);
        paint(ellPts(fx + sway, fy - 50 - 14 * hash(i + 7), 11, 11, 8, 1), { wash: hash(i + 3) > .5 ? PAL.rose : '#F4C95D', ink: PAL.ink, sw: .6 });
      }
    } else {
      // blurred background blooms only — the flower patch stays, the face stays clear
      for (let i = 0; i < 10; i++) {
        boilSeed('bfl' + i);
        const fx = hash(i + 31) * (W + 400) - 200, fy = 780 + hash(i + 77) * 240;
        if (Math.abs(fx - 960) < 430 && fy < 900) continue;   // keep the space behind the face empty
        paint(ellPts(fx, fy, 30, 24, 10, 1.5), { wash: hash(i + 3) > .5 ? PAL.rose : '#F4C95D', washOp: 80, ink: null, bleed: .5, tex: .5 });
      }
    }
  }
  const petalBurst = (x, y, t0, t) => {
    for (let i = 0; i < 9; i++) {
      const k = seg(t - t0, i * .02, .6 + i * .04); if (k <= 0 || k >= 1) continue;
      const a = -Math.PI / 2 + (i - 4) * .4, d = 60 + 130 * easeOut(k);
      boilSeed('pet' + i);
      paint(ellPts(x + Math.cos(a) * d, y + Math.sin(a) * d + 60 * k * k, 9 * (1 - k * .5), 6, 8, 1), { wash: PAL.rose, washOp: 255 * (1 - k), ink: null, rot: a });
    }
  };
  // grass flecks kicked up by the face-plant (the miss needs a bit of the meadow to answer back)
  const grassPuff = (x, y, t0, t) => {
    for (let i = 0; i < 7; i++) {
      const k = seg(t - t0, i * .02, .5 + i * .05); if (k <= 0 || k >= 1) continue;
      const a = -Math.PI / 2 + (i - 3) * .45, d = 30 + 95 * easeOut(k);
      boilSeed('gp' + i);
      paint(ellPts(x + Math.cos(a) * d, y + Math.sin(a) * d + 70 * k * k, 11 * (1 - k * .4), 4, 6, 1),
        { wash: GRASSD, washOp: 220 * (1 - k), ink: null, rot: a });
    }
  };

  // ---------- shot A: dozing, the visit, the first pounce (0 – 5.2) ----------
  function shotA(t, lt, dur) {
    const CX = 700, CY = 890, u = 21;
    const tWake = 2.1, tIdea = 2.9, tJump = 3.7, tLand = 4.1;
    camBegin(kf(t, [[0, 900], [3, 860], [dur, 820]]), kf(t, [[0, 560], [dur, 530]]), kf(t, [[0, 1], [1.8, 1.05], [3, 1.1], [dur, 1.06]]));
    meadow(t);
    // the butterfly: BIG in the opening loops (starts in the upper-left third — the rhyme with the ending),
    // a dotted trail spells out the figure-eight, then it circles down over Clawd, then flits away upward
    const bfPos = (tt) => {
      const cc = ease(seg(tt, .6, 1.8));                     // drifts down from the upper-left third to the flowers
      const cx = lerp(550, 640, cc), cy = lerp(400, 620, cc);
      if (tt < tWake) {
        let [x, y] = flutter(tt, cx, cy, 90);
        if (tt > 1.6) { const k = ease(seg(tt, 1.6, 2.4)); x = lerp(x, CX + 120, k * .6); y = lerp(y, CY - 190, k * .6); }
        return [x, y];
      }
      if (tt < tJump) { const k = tt - tWake; return [CX + 120 * Math.cos(k * 3.2), CY - 190 - 30 * Math.sin(k * 4) - 10 * k]; }
      const k = easeOut(seg(tt, tJump, tJump + .6));
      return [CX + 120 + 320 * k, CY - 220 - 420 * k + (tt > tJump + .3 ? flutter(tt, 0, 0, 14)[1] * .2 : 0)];
    };
    const [bx, by] = bfPos(t);
    if (t < tWake) {   // fading trail dots behind it — the eye reads the loop it draws
      for (let i = 1; i <= 9; i++) {
        const [tx, ty] = bfPos(t - i * .055);
        paint(ellPts(tx, ty, 7 * (1 - i / 11), 5.5 * (1 - i / 11), 6, .8), { wash: '#FFE9B0', washOp: 150 * (1 - i / 10), ink: null });
      }
    }
    const bs = t < tJump ? lerp(44, 20, ease(seg(t, .2, 2))) : 17;   // opens ≈ 1/6 of frame height, settles to scene scale
    glow(bx, by, lerp(95, 55, ease(seg(t, 0, 2))), '#FFF3C0', .2 + .05 * (1 - seg(t, 0, 1.2)));
    butterfly(bx, by, bs, Math.cos(t * 2.1) * .3, frac(t * 2.4));

    // Clawd: dozing → wake → idea → pounce → plant (with aftershock) → slow wobbly lift → dizzy
    const mood = emotions(lt, [[0, 'sleepy'], [tWake, 'surprised', { lookX: .6, lookY: -.5 }], [tIdea, 'idea'], [tJump + .05, 'excited', { lookX: .8, lookY: -.6 }], [tLand + .3, 'dizzy']]);
    let pose;
    if (lt < tJump) {
      const watch = Math.min(1, (lt - 1.9) / .5);   // eyes lead: look up at it before anything else
      pose = { lookX: .6 * watch, lookY: -.6 * watch, rot: -.06 * watch };
    } else if (lt < tLand + .25) {
      const j = jump(lt, tJump, tLand, 4);
      const miss = seg(lt, tJump + .1, tLand), since = lt - tLand;
      pose = { ...j, view: 'side', flip: true, rot: lerp(.4, 1.35, easeIn(miss)),
        sq: (j.sq || 0) + .35 * miss + (since > 0 ? .05 * Math.sin(since * 26) * Math.exp(-since * 9) : 0) }; // planted: body shudders once
    } else if (lt < tLand + .65) {   // head lifts slowly out of the grass, wobbling with the effort
      const k = easeOut(seg(lt, tLand + .25, tLand + .65));
      pose = { view: 'q', rot: lerp(1.35, .05, k) + .09 * Math.sin((lt - tLand - .25) * 17) * (1 - k),
        dy: -1.5 * k, sq: .3 * (1 - k) - .1 * k, lookX: .2, lookY: -.2 };
    } else {   // dizzy hold: head sways, eyes circle each other, stars orbit above
      pose = { view: 'q', rot: wob(lt, 2.2, 0) * .13, dy: -1.5 + .35 * Math.sin((lt - tLand) * 2.2), sq: -.1,
        lookX: Math.cos(lt * 9) * .5, lookY: Math.sin(lt * 9) * .4 };
    }
    clawd(CX, CY, u, { ...mood, ...pose, sq: (mood.sq || 0) + (pose.sq || 0), dy: (mood.dy || 0) + (pose.dy || 0) });
    if (lt > tLand) grassPuff(CX + 40, CY - u, tLand, lt);
    if (lt > tLand + .5) {   // dizzy stars orbiting the raised head
      for (let i = 0; i < 3; i++) {
        const a = lt * 5 + i * TAU / 3;
        boilSeed('dizzy' + i);
        paint(ellPts(CX + Math.cos(a) * 58, CY - 5.7 * u - 22 + Math.sin(a) * 15, 7, 7, 6, .6), { wash: '#F4C95D', ink: PAL.ink, sw: .7 });
      }
    }
    const eye = toScreen(CX, CY - 4 * u);
    const bScr = lt < .6 ? toScreen(bx, by) : eye;   // the iris opens ON the butterfly
    camEnd();
    boilSeed('tr');
    if (lt < .5) iris(bScr[0], bScr[1], lerp(0, 1500, easeIn(lt / .5)));
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, WIPE);
  }

  // ---------- shot B: the sneak and the second miss (5.2 – 10.4) ----------
  function shotB(t, lt, dur) {
    const u = 23, G = 940;
    const tSneak = 0.2, tWind = 2.4, tJump = 2.7, tLand = 3.1;
    const walk = stroll(lt, tSneak, tWind, 260, 1180, u);
    const camX = t < tSneak ? 260 : lerp(260, 1240, ease(seg(lt, tSneak, tJump + .4)));
    camBegin(camX + 15 * Math.sin(lt * .7), kf(lt, [[0, 545], [tJump, 520], [dur, 545]]), kf(lt, [[0, 1.05], [tWind, 1.12], [dur, 1.05]]));
    meadow(t, false);
    // the butterfly ahead, drifting further each approach
    const drift = 300 + 140 * ease(seg(lt, 1.2, tWind));
    const [bx, by] = flutter(t, 260 + drift, G - 260, 46, 1.7);
    glow(bx, by, 60, '#FFF3C0', .18);
    if (lt <= tJump) butterfly(bx, by, 17, Math.cos(t * 2.3) * .3, frac(t * 2.4));   // single path: it escapes at the leap
    // Clawd: low crouch tiptoe → wind-up → leap under it → flower-patch crash
    const mood = emotions(lt, [[0, 'determined'], [1.6, 'mischief'], [tWind, 'determined'], [tJump + .05, 'excited'], [tLand + .2, 'dizzy'], [dur - 1, 'sad']]);
    let pose;
    if (lt < tWind) {
      const crouch = .22 * Math.min(1, (lt - tSneak) / .8);
      pose = { view: 'side', walk: lt > tSneak ? walk.walk : 0, dy: walk.dy + crouch, sq: crouch, lookX: .9, lookY: -.5, aL: -.9, aR: -.5 };
      if (lt > tWind - .8) {   // the wind-up: deep crouch, arms hauled back — then ~0.3 s of squinting shiver up on tiptoe
        const w = ease(seg(lt, tWind - .8, tWind - .2));
        const shake = seg(lt, tWind - .35, tJump);
        pose = { ...pose, walk: 0, dy: crouch + .1 * w - .06 * shake, sq: crouch + .18 * w,
          aL: -1.3 * w, aR: -.7 * w, squint: .75 * w, rot: .045 * Math.sin(lt * 32) * shake };
      }
    } else {
      const j = jump(lt, tJump, tLand, 5), land = lt - tLand;
      pose = { view: 'side', ...j, lookX: .9, lookY: -.8 };
      if (lt > tLand) pose = { view: 'front', dy: (j.dy || 0) - .8 * Math.exp(-land * 4), sq: .3 - .25 * backOut(seg(lt, tLand, tLand + .4)), aL: .6, aR: .6 };
    }
    const x = lt < tSneak ? 260 : walk.x;
    clawd(x, G, u, { ...mood, ...pose, sq: (mood.sq || 0) + (pose.sq || 0), dy: (mood.dy || 0) * .5 + (pose.dy || 0) });
    if (lt > tLand) petalBurst(x + 30, G - 40, tLand, lt);
    // "!" — the intent pops above his head and holds through the wind-up
    if (lt > tWind - .7 && lt < tJump + .12) {
      const s = backOut(seg(lt, tWind - .7, tWind - .55)) * (1 - seg(lt, tJump, tJump + .12));
      if (s > .02) {
        const hx = x, hy = G - 5.6 * u - 46;
        paint(ellPts(hx, hy, 30 * s + 2, 30 * s + 2, 10, .5), { wash: PAL.cream, ink: PAL.ink, sw: 2.2 });
        paint(ellPts(hx, hy - 9 * s, 4.5 * s, 12 * s, 6, .3), { wash: PAL.ink, ink: null });
        paint(ellPts(hx, hy + 12 * s, 4.5 * s, 4.5 * s, 6, .3), { wash: PAL.ink, ink: null });
      }
    }
    // the butterfly's escape hop up and over the leap
    if (lt > tJump) {
      const k = seg(lt, tJump, tJump + .9);
      const ox = bx - 420 * easeIn(k), oy = by - 260 * Math.sin(Math.PI * Math.min(1, k));
      glow(ox, oy, 60, '#FFF3C0', .18);
      butterfly(ox, oy, 17, -.2 - k, frac(t * 2.4));
    }
    const eye = toScreen(x, G - 4 * u);
    camEnd();
    boilSeed('tr');
    if (lt < .3) brushWipe(.5 + lt / .6, WIPE);
    if (lt > dur - .45) { const r = lerp(1500, 300, easeIn(seg(lt, dur - .45, dur - .1))); iris(...eye, r); }
  }

  // ---------- shot C: stillness wins (10.4 – 15.0) ----------
  function shotC(t, lt, dur) {
    const u = 46, CX = 960, CY = 980;
    const tNotice = .8, tChoice = 1.6, tStill = 2.4, tLandN = 3.4, tJoy = 3.6, tIris = 3.8;
    const nose = [CX, CY - 6.4 * u];   // dead-centre on his face: the landing rhymes with the opening
    const settle = 1 - seg(lt, tStill, tStill + .5);   // the camera rests while he holds still
    camBegin(960 + 10 * Math.sin(lt * .5) * settle, kf(lt, [[0, 772], [tLandN, 762], [dur, 768]]), kf(lt, [[0, 2.0], [tLandN, 2.12], [dur, 2.16]]));
    meadow(t, false, false);
    // the butterfly comes home: drifts in from the right, then one slow, even spiral down to the nose
    let bx, by, done = false, flap = frac(t * 2.4);
    if (lt < tStill) { [bx, by] = flutter(t, 1430 - 400 * easeOut(seg(lt, .2, tStill)), 560, 34, 2.4); }
    else if (lt < tLandN) {
      const k = seg(lt, tStill, tLandN);           // linear k — an unhurried, even descent
      const a = 2.4 + k * 4.6, rr = 120 * (1 - k);
      bx = lerp(1060, nose[0], k) + Math.cos(a) * rr;
      by = lerp(540, nose[1] - 12, k) + Math.sin(a) * rr * .6;
      flap = frac(t * 1.7);
    } else {
      const frozen = lt < tJoy;                    // 0.2 s freeze frame right on the landing
      done = true; bx = nose[0];
      by = nose[1] - 12 + (frozen ? 0 : 2.3 * Math.sin((lt - tJoy) * 2.6));   // rides his happy bounce in phase
      flap = frozen ? .3 : .16 + .3 * pulse(t, .5);
    }
    glow(bx, by, 90, '#FFE9B0', .22);
    butterfly(bx, by, 19, done ? 0 : Math.cos(t * 2) * .3, flap);
    // Clawd: worn out (gaze low) → notices → wants to pounce → chooses stillness → the landing → love
    const mood = emotions(lt, [[0, 'sad'], [tNotice, 'surprised', { lookX: .8, lookY: -.4 }], [tChoice, 'mischief'], [tStill + .1, 'shy', { squint: .9 }], [tJoy, 'love']]);
    let pose = { lookY: .35 };                     // worn out: eyes down (the 'sad' mouth carries the rest)
    if (lt > tNotice) { const k = Math.min(1, (lt - tNotice) / .3); pose.lookX = .8 * k; pose.lookY = lerp(.35, -.4, k); }
    if (lt > tChoice && lt < tStill) { const w = Math.sin(seg(lt, tChoice, tStill) * Math.PI * 3) * .1; pose.sq = .15 + w; pose.dy = .15; } // twitchy, almost-pounce shivers
    if (lt >= tStill) {                            // the hold: everything about him stops — no breathing bob, nothing
      const s = backOut(seg(lt, tStill, tStill + .5));
      pose = { ...pose, sq: .1 * (1 - s) - .04 * s, dy: 0,
        squint: .9 - .2 * seg(lt, tLandN + .2, tLandN + .5),
        lookY: lerp(-.4, .6, seg(lt, tLandN + .2, tLandN + .6)) };   // eyes cross down at it — after the freeze
    }
    if (lt >= tJoy) { pose.dy = .05 * Math.sin((lt - tJoy) * 2.6); }   // a tiny relieved bounce, nose steady
    clawd(CX, CY, u, { ...mood, ...pose, sq: (mood.sq || 0) + (pose.sq || 0), dy: (mood.dy || 0) * .5 + (pose.dy || 0), blush: .5 + .3 * seg(lt, tJoy, tJoy + .4) });
    // the payoff warms: layered gold around the pair, then a soft tint across the whole frame
    if (lt > tLandN) {
      const k = seg(lt, tLandN, tJoy + .4);
      glow(nose[0], nose[1] - 40, 200 + 130 * k, '#FFD98F', .16 + .15 * k);
      if (k > 0) paint(ellPts(W * .5, H * .45, W * .85, H * .85, 30, 6), { fill: '#FFD98F', fillOp: 22 * k, ink: null, bleed: .4, tex: .4 });
    }
    const eye = toScreen(CX, CY - 6.4 * u - 22);   // the iris centres just above the butterfly on his nose
    const faceC = toScreen(CX, CY - 4.5 * u);
    camEnd();
    boilSeed('tr');
    if (lt < .45) { const k = easeOut(lt / .45); iris(960, lerp(830, faceC[1] - 40, k), lerp(300, 1600, k)); }
    if (lt > tIris) {
      const r = lt < tIris + .45 ? lerp(1600, 340, ease(seg(lt, tIris, tIris + .45)))
        : lt < dur - .35 ? lerp(340, 315, seg(lt, tIris + .45, dur - .35))
        : lerp(315, 0, easeIn(seg(lt, dur - .35, dur - .08)));
      iris(eye[0], eye[1], r);
    }
  }

  shots([[0, shotA], [5.2, shotB], [10.4, shotC]]);
})();
