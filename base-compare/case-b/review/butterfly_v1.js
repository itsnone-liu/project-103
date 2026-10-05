// config.js line: PROJECT = { duration: 15, bpm: 96, offset: 0 };
(() => {
  const WIPE = [PAL.teal, PAL.sap];

  function garden(t) {
    boilSeed('garden-sky');
    paint(rectPts(-300, -300, W + 600, H + 600, 4), {
      wash: mixCol(PAL.sky, PAL.cream, 0.48), ink: null
    });
    boilSeed('garden-hill');
    paint(ellPts(950, 1040, 1250, 330, 40, 5), {
      wash: mixCol(PAL.sap, PAL.cream, 0.18), fill: PAL.teal,
      fillOp: 45, bleed: 0.18, tex: 0.55, ink: null
    });
    boilSeed('garden-ground');
    paint(ellPts(960, 1120, 1500, 250, 36, 4), {
      wash: PAL.sap, fill: PAL.teal, fillOp: 35,
      bleed: 0.16, tex: 0.55, ink: null
    });
    // A few steady garden stems; their small sway is deliberately separate from their boil.
    for (let i = 0; i < 9; i++) {
      boilSeed('stem' + i);
      const x = 130 + i * 210;
      const sway = 8 * Math.sin(t * 1.2 + i * 1.7);
      inkLine([[x, 970], [x + sway, 900], [x + sway * 1.4, 830 - (i % 3) * 15]], 1.1, mixCol(PAL.sap, PAL.ink, 0.25), 'dry', 0.55);
      paint(ellPts(x + sway * 1.4 - 14, 855 - (i % 3) * 15, 20, 9, 12, 1, -0.45), {
        wash: mixCol(PAL.sap, PAL.teal, 0.25), ink: null
      });
    }
  }

  function flower(x, y, s, t) {
    boilSeed('flower' + x);
    const bob = 3 * Math.sin(t * 2.4 + x);
    inkLine([[x, y + 95], [x + 2, y + 25 + bob]], 2, PAL.sap, 'ink', 0.4);
    for (let i = 0; i < 5; i++) {
      const a = i * TAU / 5;
      paint(ellPts(x + Math.cos(a) * s * 0.62, y + bob + Math.sin(a) * s * 0.62,
        s * 0.48, s * 0.27, 14, 1, a), {
        wash: mixCol(PAL.rose, PAL.cream, 0.25), ink: PAL.ink, sw: 0.7
      });
    }
    paint(ellPts(x, y + bob, s * 0.28, s * 0.28, 16, 1), {
      wash: PAL.ochre, ink: PAL.ink, sw: 0.65
    });
  }

  function butterfly(x, y, s, t, angle = 0) {
    const flap = Math.sin(t * 15);
    const wingY = Math.abs(flap) * s * 0.12;
    boilSeed('butterfly');
    push();
    translate(x, y);
    rotate(angle);
    paint(ellPts(-s * 0.33, -s * 0.2, s * 0.42, s * (0.28 + wingY / s), 16, 1, -0.35), {
      wash: mixCol(PAL.violet, PAL.cream, 0.35), ink: PAL.ink, sw: 0.8
    });
    paint(ellPts(s * 0.33, -s * 0.2, s * 0.42, s * (0.28 + wingY / s), 16, 1, 0.35), {
      wash: mixCol(PAL.rose, PAL.cream, 0.25), ink: PAL.ink, sw: 0.8
    });
    paint(ellPts(-s * 0.26, s * 0.22, s * 0.25, s * 0.2, 12, 1, -0.5), {
      wash: PAL.cream, ink: PAL.ink, sw: 0.55
    });
    paint(ellPts(s * 0.26, s * 0.22, s * 0.25, s * 0.2, 12, 1, 0.5), {
      wash: PAL.cream, ink: PAL.ink, sw: 0.55
    });
    inkLine([[0, -s * 0.45], [0, s * 0.48]], 1.4, PAL.ink, 'ink', 0.15);
    inkLine([[0, -s * 0.32], [-s * 0.12, -s * 0.58]], 0.8, PAL.ink, 'inkfine', 0.2);
    inkLine([[0, -s * 0.32], [s * 0.12, -s * 0.58]], 0.8, PAL.ink, 'inkfine', 0.2);
    pop();
  }

  function shotNotice(t, lt, dur) {
    camBegin(960 + 12 * Math.sin(lt * 0.7), 550, 1.02 + 0.015 * Math.sin(lt * 0.5));
    garden(t);
    flower(1450, 850, 27, t);

    let bx, by;
    if (lt < 1.45) {
      bx = 1330 + 34 * Math.sin(lt * 3);
      by = 330 + 20 * Math.sin(lt * 4);
    } else if (lt < 2.55) {
      const k = ease(seg(lt, 1.45, 2.35));
      bx = lerp(1330, 1550, k);
      by = lerp(330, 360, k) - 45 * Math.sin(k * Math.PI);
    } else {
      const k = ease(seg(lt, 2.55, 4.65));
      bx = lerp(1550, 1120, k) + 32 * Math.sin(lt * 5);
      by = lerp(360, 250, k) + 28 * Math.sin(lt * 4);
    }
    butterfly(bx, by, 38, t, 0.12 * Math.sin(t * 4));

    const mood = emotions(lt, [[0, 'curious'], [1.45, 'excited'], [2.6, 'surprised']]);
    const grab = ease(seg(lt, 1.9, 2.18));
    const recoil = Math.exp(-Math.max(0, lt - 2.4) * 3);
    clawd(790 + 10 * Math.sin(lt * 1.1), 900, 27, {
      ...mood,
      aR: lerp(mood.aR || 0, 1.35, grab) * (lt < 2.55 ? 1 : recoil * 0.3),
      aL: lt < 2.2 ? -0.1 : 0.15,
      sq: (mood.sq || 0) + (lt > 2.35 ? -0.08 * recoil : 0),
      lookX: lt < 1.4 ? 0.7 : 1,
      lookY: lt < 2.3 ? -0.5 : -0.8
    });
    const eye = toScreen(790, 790);
    camEnd();
    if (lt < 0.45) iris(...eye, lerp(0, 1450, easeIn(lt / 0.45)), PAL.cream);
    if (lt > dur - 0.3) brushWipe((lt - (dur - 0.3)) / 0.6, WIPE);
  }

  function shotChase(t, lt, dur) {
    const flowerX = 1420;
    camBegin(960 + 95 * ease(seg(lt, 0, 4.8)), 535, 1.02);
    garden(t);
    flower(flowerX, 850, 29, t);

    let bx, by;
    if (lt < 1.55) {
      const k = ease(seg(lt, 0, 1.55));
      bx = lerp(1130, 1360, k) + 24 * Math.sin(lt * 5);
      by = lerp(250, 330, k) + 28 * Math.sin(lt * 4);
    } else if (lt < 2.0) {
      const k = ease(seg(lt, 1.55, 2.0));
      bx = lerp(1360, 1470, k);
      by = lerp(330, 170, k);
    } else if (lt < 2.75) {
      const k = ease(seg(lt, 2.0, 2.75));
      bx = lerp(1470, flowerX, k);
      by = lerp(170, 780, k);
    } else {
      bx = flowerX + 7 * Math.sin(lt * 1.5);
      by = 790 + 4 * Math.sin(lt * 3);
    }
    butterfly(bx, by, 38, t, lt < 2.75 ? 0.1 * Math.sin(t * 5) : 0);

    const walk = stroll(lt, 0, 1.35, 500, 900, 25);
    const mood = emotions(lt, [[0, 'excited'], [1.65, 'surprised'], [2.85, 'thinking']]);
    const reach = ease(seg(lt, 1.35, 1.6)) * (lt < 1.9 ? 1 : Math.exp(-(lt - 1.9) * 3));
    clawd(lt < 1.35 ? walk.x : 900, 900, 25, {
      ...mood,
      view: lt < 1.35 ? 'side' : 'q',
      walk: lt < 1.35 ? walk.walk : 0,
      dy: (mood.dy || 0) + (lt < 1.35 ? walk.dy : 0),
      aR: lerp(mood.aR || 0, 1.4, reach),
      lookX: lt < 2.7 ? 1 : 0.8,
      lookY: lt < 2.7 ? -0.6 : -0.8
    });
    camEnd();
    if (lt < 0.3) brushWipe(0.5 + lt / 0.6, WIPE);
    if (lt > dur - 0.3) brushWipe((lt - (dur - 0.3)) / 0.6, WIPE);
  }

  function shotPerch(t, lt, dur) {
    camBegin(960 + 8 * Math.sin(lt * 0.5), 545, 1.05);
    garden(t);
    flower(1240, 850, 30, t);

    const land = [1240, 790];
    const hand = [1090, 575];
    let bx, by;
    if (lt < 1.65) {
      const k = ease(seg(lt, 0, 1.65));
      bx = lerp(1240, hand[0], k);
      by = lerp(land[1], hand[1], k) - 55 * Math.sin(Math.PI * k);
    } else {
      bx = hand[0] + 5 * Math.sin(lt * 2);
      by = hand[1] + 3 * Math.sin(t * 15);
    }
    butterfly(bx, by, 38, t, 0.04 * Math.sin(t * 2));

    const offer = backOut(seg(lt, 0.55, 1.1));
    const mood = emotions(lt, [[0, 'hopeful'], [1.8, 'surprised'], [2.45, 'love']]);
    clawd(850, 900, 27, {
      ...mood,
      aR: lerp(0.15, 0.95, offer),
      aL: -0.05,
      lookX: 0.8,
      lookY: -0.55,
      dy: (mood.dy || 0) + 0.06 * Math.sin(lt * 3)
    });
    const eye = toScreen(850, 790);
    camEnd();

    // Wipe completes from the preceding shot as the new composition is revealed.
    if (lt < 0.3) brushWipe(0.5 + lt / 0.6, WIPE);
    if (lt > 4.05) {
      const r = lt < 4.45
        ? lerp(1450, 260, ease(seg(lt, 4.05, 4.45)))
        : lt < 4.72
          ? lerp(260, 240, seg(lt, 4.45, 4.72))
          : lerp(240, 0, easeIn(seg(lt, 4.72, dur)));
      iris(...eye, r, PAL.cream);
    }
  }

  shots([[0, shotNotice], [4.8, shotChase], [10, shotPerch]]);
})();
