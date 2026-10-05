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
    paint(ellPts(START, 850, 14, 27, 14, 1), { wash: '#B96E42', ink: '#713F2D', sw: 2.2 });
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

  function turtle(x, y, t, moving = true, size = 1) {
    const step = moving ? Math.sin(t * 9) : Math.sin(t * 2);
    const p = (dx, dy) => [x + dx * size, y + dy * size];
    boilSeed('turtle-shell');
    paint(ellPts(...p(0, -23 + Math.abs(step) * 2), 34 * size, 24 * size, 24, 2), { wash: '#81916B', fill: '#A9AD79', fillOp: 80, ink: PAL.ink, sw: 1.3 * size });
    inkLine([p(-20, -28), p(-12, -42), p(8, -46), p(24, -34)], 1 * size, '#D6C998', 'dry', .4);
    paint(ellPts(...p(35, -24 + step), 16 * size, 13 * size, 16, 1), { wash: '#B5A979', ink: PAL.ink, sw: 1 * size });
    paint(ellPts(...p(40, -27 + step), 2.2 * size, 2.5 * size, 8, .2), { wash: PAL.ink, ink: null });
    for (const [i, dx] of [-1, 1].entries()) {
      paint(ellPts(...p(dx * 20, -3 + (i ? step : -step)), 8 * size, 6 * size, 10, 1), { wash: '#9D9A6F', ink: PAL.ink, sw: .7 * size });
    }
    paint(ellPts(...p(-34, -19), 7 * size, 7 * size, 10, .5), { wash: '#9D9A6F', ink: PAL.ink, sw: .7 * size });
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
    // A brief framing emphasis makes the shared marker and first steps easy to read.
    const focus = .35 * (1 - ease(seg(lt, .7, 1.0)));
    camBegin(420, 540, 1.9 + focus + .025 * lt);
    background(t);
    trail(897, turtleX(t), '#C8845F', 102, 7);
    turtle(turtleX(t), 850, t, t > 0, 1.25);
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
    // Each trail endpoint is the traveler's current position, so the brush grows with its motion.
    trail(919, clawdX(t), TRACK_C, t >= 4 ? 210 : 0, 7);
    turtle(turtleX(t), 850, t, true);
    if (t >= 4) {
      const launch = 1 - ease(seg(t, 4, 4.3));
      travelerClawd(t, clawdX(t), 850, t < 8, t < 6.3 ? 'excited' : 'surprised', {
        lookX: .8, dy: -2 * launch, aL: -.65 * launch, aR: -.7 * launch
      });
    } else travelerClawd(t, START, 850, false, 'curious', { lookX: .8 });
    camEnd();
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, [PAPER, '#E9D7B5']);
  }

  function shotC(t, lt, dur) {
    camBegin(420, 540, 1.9);
    background(t);
    trail(897, MEET, TRACK_T, 225, 9);
    trail(919, MEET, TRACK_C, 235, 9);
    // The first 0.8 seconds after the exact arrival are held as a still event.
    turtle(MEET, 850, t, false);
    travelerClawd(t, MEET, 850, false, t < 10.4 ? 'surprised' : 'thinking', {
      lookX: -.55, aL: -.15 * Math.sin(t * 2), aR: .12 * Math.sin(t * 2.4)
    });
    const ringR = 14 + 68 * easeOut(seg(t, 8.05, 8.8));
    boilSeed('meeting-ring');
    paint(ellPts(MEET, 838, ringR, ringR * .42, 32, 2), {
      wash: '#E9AC58', washOp: 34, ink: '#D1843F', sw: 3.5 * (1 - .35 * seg(t, 8.8, 10.4))
    });
    // Warm strokes visibly gather both trails at the shared feet/contact point.
    inkLine([[MEET - 18, 897], [MEET, 850], [MEET + 18, 897]], 3, '#D1843F', 'dry', .25);
    inkLine([[MEET - 18, 919], [MEET, 850], [MEET + 18, 919]], 3, '#D1843F', 'dry', .25);
    inkLine([[MEET - 9, 850], [MEET + 9, 850]], 3, '#D89A4F', 'dry', .2);
    camEnd();
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, [PAPER, '#E9D7B5']);
  }

  function shotD(t, lt, dur) {
    camBegin(420, 540, 1.9);
    background(t);
    const reveal = ease(seg(t, 12, 13.2));
    trail(825, lerp(START, MEET, reveal), TRACK_C, 225, 8);
    trail(875, lerp(START, MEET, reveal), TRACK_T, 210, 8);
    boilSeed('endpoint-marks');
    for (const y of [825, 875]) {
      paint(ellPts(MEET, y, 8, 11, 12, 1), { wash: '#D89A4F', ink: PAL.ink, sw: .8 });
    }
    // Clawd belongs with the upper (later-start) path; the turtle with the lower path.
    travelerClawd(t, MEET, 825, false, 'proud', {
      lookX: t < 14.6 ? -.55 : 0, aL: t < 14.6 ? .65 : -.55, aR: .65
    });
    turtle(MEET, 875, t, false, 1.15);
    camEnd();
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, [PAPER, '#E9D7B5']);
  }

  function shotE(t, lt, dur) {
    camBegin(420, 540, 1.9);
    background(t);
    const revealT = ease(seg(t, 17.2, 18.0));
    const revealC = ease(seg(t, 18.0, 18.8));
    // Paired equal-distance lanes; both figures begin precisely at the shared x=300 marker.
    trail(825, lerp(START, MEET, revealC), TRACK_C, 230, 9);
    trail(875, lerp(START, MEET, revealT), TRACK_T, 215, 9);
    inkLine([[START, 850], [MEET, 850]], 2, '#9FB798', 'dry', .15);
    for (const x of [START, MEET]) {
      boilSeed('comparison-baseline-' + x);
      paint(ellPts(x, 850, 6, 8, 10, .5), { wash: '#9FB798', ink: '#71896F', sw: .8 });
    }
    for (const y of [825, 875]) {
      boilSeed('final-end-' + y);
      paint(ellPts(MEET, y, 9, 12, 12, 1), { wash: '#D89A4F', ink: PAL.ink, sw: .8 });
    }
    if (t < 18.8) {
      travelerClawd(t, START, 825, false, 'thoughtful', { lookX: .4 });
      turtle(START, 875, t, false, 1.15);
    } else {
      travelerClawd(t, MEET, 825, false, 'proud', { lookX: -.35, aL: .2, aR: .3 });
      turtle(MEET, 875, t, false, 1.15);
    }
    camEnd();
    boilSeed('transition-e');
    if (lt > dur - .55) brushWipe((lt - (dur - .55)) / 1.1, [PAPER, '#E9D7B5']);
  }

  shots([[0, shotA], [4, shotB], [8, shotC], [12, shotD], [16, shotE]]);
})();
