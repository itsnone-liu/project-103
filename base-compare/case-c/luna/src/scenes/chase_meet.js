// src/config.js: PROJECT = { duration: 20, bpm: 100, offset: 0 };
(() => {
  const START = 300, MEET = 540;
  const turtleX = t => START + 30 * Math.max(0, t);
  const clawdX = t => START + 60 * Math.max(0, t - 4);
  const PAPER = '#F2E7CC', GROUND = '#B4C7A4', TRACK_T = '#71896F', TRACK_C = '#C8845F';

  function background(t) {
    boilSeed('background');
    paint(rectPts(-500, -300, 2500, 1700, 4), { wash: PAPER, ink: null });
    paint(ellPts(500, 1030, 1400, 340, 40, 5), { wash: GROUND, fill: '#9FB798', fillOp: 80, bleed: .14, tex: .6, ink: null });
    paint(ellPts(490, 870, 950, 90, 32, 4), { wash: '#D9D8B4', fill: '#BBC7A2', fillOp: 65, bleed: .16, tex: .5, ink: null });
    inkLine([[START, 850], [MEET, 850]], 1.1, '#83977B', 'dry', .2);
    // The same left-hand marker anchors every shot.
    boilSeed('start-marker');
    paint(ellPts(START, 850, 12, 24, 14, 1), { wash: '#D19A63', ink: PAL.ink, sw: 1 });
    paint(ellPts(START, 850, 5, 14, 10, .5), { wash: '#E7BD83', ink: null });
  }

  function trail(y, end, col, opacity = 190, width = 7) {
    if (end <= START) return;
    boilSeed('trail-' + y);
    paint(ribbon([[START, y], [lerp(START, end, .33), y + 1], [lerp(START, end, .68), y - 1], [end, y]], width, width), {
      wash: col, washOp: opacity, ink: null
    });
    for (let x = START + 30; x < end; x += 30) {
      inkLine([[x, y - 4], [x + 2, y + 4]], 1, mixCol(col, PAPER, .25), 'dry', 0);
    }
  }

  function turtle(x, y, t, moving = true) {
    const step = moving ? Math.sin(t * 9) : Math.sin(t * 2);
    boilSeed('turtle-shell');
    paint(ellPts(x, y - 23 + Math.abs(step) * 2, 34, 24, 24, 2), { wash: '#81916B', fill: '#A9AD79', fillOp: 80, ink: PAL.ink, sw: 1.3 });
    inkLine([[x - 20, y - 28], [x - 12, y - 42], [x + 8, y - 46], [x + 24, y - 34]], 1, '#D6C998', 'dry', .4);
    paint(ellPts(x + 35, y - 24 + step, 16, 13, 16, 1), { wash: '#B5A979', ink: PAL.ink, sw: 1 });
    paint(ellPts(x + 40, y - 27 + step, 2.2, 2.5, 8, .2), { wash: PAL.ink, ink: null });
    for (const [i, dx] of [-1, 1].entries()) {
      paint(ellPts(x + dx * 20, y - 3 + (i ? step : -step), 8, 6, 10, 1), { wash: '#9D9A6F', ink: PAL.ink, sw: .7 });
    }
    paint(ellPts(x - 34, y - 19, 7, 7, 10, .5), { wash: '#9D9A6F', ink: PAL.ink, sw: .7 });
  }

  function travelerClawd(t, x, y = 850, walking = true, mood = 'curious', extra = {}) {
    const e = emotions(t, [[0, mood]]);
    const walk = walking ? Math.sin((t - 4) * 11) : 0;
    clawd(x, y, 16, {
      ...e, ...extra, view: walking ? 'side' : 'q', walk,
      dy: (e.dy || 0) + (walking ? Math.abs(Math.sin((t - 4) * 11)) * .09 : 0),
      boilKey: 'traveler-clawd'
    });
  }

  function shotA(t, lt, dur) {
    camBegin(420, 540, 1.9 + .025 * lt);
    background(t);
    trail(897, turtleX(t), TRACK_T, 145, 6);
    turtle(turtleX(t), 850, t, t > 0);
    travelerClawd(t, START, 850, false, 'curious', { lookX: .75, aR: .12 * Math.sin(t * 2) });
    camEnd();
    boilSeed('transition-a');
    if (lt < .6) brushWipe(lt / 1.2, [PAPER, '#E9D7B5']);
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, [PAPER, '#E9D7B5']);
  }

  function shotB(t, lt, dur) {
    camBegin(420 + 7 * Math.sin(lt * .45), 540, 1.9);
    background(t);
    trail(897, turtleX(t), TRACK_T, 190, 7);
    trail(919, clawdX(t), TRACK_C, t >= 4 ? 210 : 0, 7);
    turtle(turtleX(t), 850, t, true);
    if (t >= 4) travelerClawd(t, clawdX(t), 850, t < 8, t < 6.3 ? 'excited' : 'surprised', { lookX: .8 });
    else travelerClawd(t, START, 850, false, 'curious', { lookX: .8 });
    camEnd();
    // Match cut is carried by the turtle's exact continuing position and stride.
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, [PAPER, '#E9D7B5']);
  }

  function shotC(t, lt, dur) {
    camBegin(420, 540, 1.9);
    background(t);
    trail(897, MEET, TRACK_T, 205, 7);
    trail(919, MEET, TRACK_C, 220, 7);
    turtle(MEET, 850, t, false);
    travelerClawd(t, MEET, 850, false, t < 10.4 ? 'surprised' : 'thinking', {
      lookX: -.55, aL: -.15 * Math.sin(t * 2), aR: .12 * Math.sin(t * 2.4)
    });
    // PATTERN: FREEZE_EVENT
    // Exact meeting hold: both actors are fixed at the solved x=540 point throughout this shot.
    const hold = clamp(1 - seg(t, 8, 8.5));
    // PATTERN: EVENT_EMPHASIS
    // The ring blooms around the shared contact point, then settles while the actors idle.
    const ringR = 12 + 68 * easeOut(seg(t, 8.05, 8.8));
    boilSeed('meeting-ring');
    paint(ellPts(MEET, 838, ringR, ringR * .42, 32, 2), {
      wash: null, ink: mixCol('#D89A4F', PAPER, .35), sw: 2.2 * (1 - .45 * seg(t, 8.8, 10.4))
    });
    inkLine([[MEET - 7, 850], [MEET + 7, 850]], 2, '#D89A4F', 'dry', .3);
    // PATTERN: TRACE_PATH
    // Both full trails remain visible from the common start to the exact common endpoint.
    camEnd();
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, [PAPER, '#E9D7B5']);
  }

  function shotD(t, lt, dur) {
    camBegin(420, 540, 1.9);
    background(t);
    const reveal = ease(seg(t, 12, 13.2));
    trail(825, lerp(START, MEET, reveal), TRACK_T, 210, 8);
    trail(875, lerp(START, MEET, reveal), TRACK_C, 225, 8);
    boilSeed('endpoint-marks');
    for (const y of [825, 875]) {
      paint(ellPts(MEET, y, 8, 11, 12, 1), { wash: '#D89A4F', ink: PAL.ink, sw: .8 });
    }
    turtle(MEET, 850, t, false);
    travelerClawd(t, MEET, 850, false, 'proud', {
      lookX: t < 14.6 ? -.55 : 0,
      aL: t < 14.6 ? .65 : -.55,
      aR: t < 14.6 ? -.3 : .65
    });
    // PATTERN: STAGGER_REVEAL
    // The turtle track appears first; Clawd's brighter, later-start track follows.
    // PATTERN: SHOW_RELATIVE_DIFFERENCE
    // Parallel trails have identical endpoints and lengths, making the equality legible.
    // PATTERN: DIM_OTHERS
    // Keep the ground subdued so the two colored tracks carry the comparison.
    // PATTERN: FOCUS_REVEAL
    // The paired end markers guide the eye to the common destination.
    // PATTERN: SHOW_BEFORE_AFTER
    // Start and finish markers frame the completed journey comparison.
    camEnd();
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, [PAPER, '#E9D7B5']);
  }

  function shotE(t, lt, dur) {
    camBegin(420, 540, 1.9);
    background(t);
    // PATTERN: MATCH_CUT
    // The two parallel tracks match-cut into a paired before/after distance diagram.
    const revealT = ease(seg(t, 17.2, 18.0));
    const revealC = ease(seg(t, 18.0, 18.8));
    trail(825, lerp(START, MEET, revealT), TRACK_T, 215, 9);
    trail(875, lerp(START, MEET, revealC), TRACK_C, 230, 9);
    for (const y of [825, 875]) {
      boilSeed('final-end-' + y);
      paint(ellPts(MEET, y, 9, 12, 12, 1), { wash: '#D89A4F', ink: PAL.ink, sw: .8 });
    }
    // Paired "before" figures stay at the shared START while the equal-length tracks reveal.
    if (t < 18.8) {
      turtle(START, 850, t, false);
      travelerClawd(t, START + 74, 850, false, 'thoughtful', { lookX: .4 });
    } else {
      turtle(MEET, 850, t, false);
      travelerClawd(t, MEET, 850, false, 'proud', { lookX: -.35, aL: .2, aR: .3 });
    }
    // PATTERN: SHOW_BEFORE_AFTER
    // Paired starting figures precede the completed meeting pose above equal-length paths.
    // PATTERN: STAGGER_REVEAL
    // First reveal the turtle's measured distance, then Clawd's matching distance.
    // PATTERN: SHOW_RELATIVE_DIFFERENCE
    // Their 240-pixel paths share both START=300 and MEET=540.
    // PATTERN: EVENT_EMPHASIS
    // The equal endpoints and warm finish marks make the payoff the visual focal point.
    camEnd();
    boilSeed('transition-e');
    if (lt > dur - .55) brushWipe((lt - (dur - .55)) / 1.1, [PAPER, '#E9D7B5']);
  }

  // PATTERN: FOCUS_REVEAL
  // Opening wipe uncovers the common marker and the two travelers.
  // PATTERN: TRACE_PATH
  // A's turtle trail is drawn from its true x(t)=300+30t position.
  // PATTERN: SHOW_RELATIVE_DIFFERENCE
  // A keeps Clawd at x=300 as the turtle advances from the shared start.
  // PATTERN: STAGGER_REVEAL
  // In B Clawd starts only at t=4, after the turtle's four-second head start.
  // PATTERN: CHASE_MOTION
  // Both x positions use the storyboard's constant speeds and exact start time.
  shots([[0, shotA], [4, shotB], [8, shotC], [12, shotD], [16, shotE]]);
})();
