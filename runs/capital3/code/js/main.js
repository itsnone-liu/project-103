// main.js — 章节路由 + 全局氛围（渲染入口，t 的纯函数）
'use strict';

const P103Main = (() => {
  function chapterAt(t) {
    for (let i = NARR.length - 2; i >= 0; i--) if (t >= NARR[i]) return i;
    return 0;
  }
  function vignette(ctx) {
    const g = ctx.createRadialGradient(960, 540, 640, 960, 540, 1220);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(4,8,16,0.42)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 1920, 1080);
  }
  function render(t) {
    const ctx = document.getElementById('stage').getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, 1920, 1080);
    bgWash(ctx);
    const i = chapterAt(t);
    const t0 = NARR[i], t1 = NARR[i + 1];
    const tt = { t0, t1, u: clamp01((t - t0) / (t1 - t0)) };
    const f = seg(t, t0, t0 + FADE);
    if (f < 1 && i > 0) {
      // 溶解：前章淡出 + 本章淡入
      const p0 = NARR[i - 1], p1 = NARR[i];
      ctx.save(); ctx.globalAlpha = 1 - f;
      CHAPTERS[i - 1](ctx, t, { t0: p0, t1: p1, u: clamp01((t - p0) / (p1 - p0)) });
      ctx.restore();
      ctx.save(); ctx.globalAlpha = f;
      CHAPTERS[i](ctx, t, tt);
      ctx.restore();
    } else {
      CHAPTERS[i](ctx, t, tt);
    }
    paperGrain(ctx);
    vignette(ctx);
    return true;
  }
  return { render, chapterAt };
})();
