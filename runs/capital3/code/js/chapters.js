// chapters.js — 11 章绘制（纯函数：每章 (ctx, t, tt)，tt={t0,t1,u}）
'use strict';

const NARR = [0.0, 7.789, 12.676, 19.796, 27.609, 34.192, 37.862, 44.185, 50.548, 54.953, 60.544, 66.014];
const FADE = 0.45; // 章间溶解

/* ---------- 通用：环世界整图（多章复用） ---------- */
// cfg: {trackR, ringAlpha, stationApp:[5], stationDim, damage, coin:{a, speed…}, cam, tick}
function ringWorld(ctx, t, cfg) {
  const { cx = WORLD.cx, cy = WORLD.cy } = cfg;
  drawTrack(ctx, { cx, cy, r: cfg.r || WORLD.R, t, reveal: cfg.reveal ?? 1, seed: cfg.seed ?? 7 });
  WORLD.stations.forEach((st, i) => {
    const [x, y] = polar(cx, cy, cfg.r || WORLD.R, st.a);
    drawStation(ctx, x, y, st, cfg.stationApp ? cfg.stationApp[i] : 1, t,
      { dim: cfg.stationDim, damage: cfg.damage || 0 });
  });
}

/* ---------- 第 1 章 · 冷开场：币亮 → 环成形 → 五站点亮 → 出发 ---------- */
function ch1(ctx, t, tt) {
  const { t0 } = tt, u = tt.u;
  // 开场机位：环居中（第 2 章起回到默认机位，环让位右侧）
  ctx.save();
  camApply(ctx, { x: WORLD.cx, y: WORLD.cy, zoom: 1 });
  // 币
  const coinIn = seg(t, t0 + 0.3, t0 + 1.5);
  // 环自绘
  const reveal = seg(t, t0 + 1.4, t0 + 3.4);
  drawTrack(ctx, { cx: WORLD.cx, cy: WORLD.cy, r: WORLD.R, t, reveal, seed: 7 });
  // 站点亮（错峰）
  const apps = WORLD.stations.map((_, i) => seg(t, t0 + 3.0 + i * 0.62, t0 + 3.9 + i * 0.62));
  WORLD.stations.forEach((st, i) => {
    const [x, y] = polar(WORLD.cx, WORLD.cy, WORLD.R, st.a);
    drawStation(ctx, x, y, st, apps[i], t);
  });
  // 币从中心升到顶站并出发
  const lift = easeInOut(seg(t, t0 + 5.2, t0 + 6.6));
  const [sx, sy] = [WORLD.cx, WORLD.cy];
  const [tx, ty] = polar(WORLD.cx, WORLD.cy, WORLD.R, -Math.PI / 2);
  const bx = sx + (tx - sx) * lift, by = sy + (ty - sy) * lift;
  const goA = seg(t, t0 + 6.4, t0 + 7.6);
  const a = -Math.PI / 2 + goA * 2 * Math.PI * 0.35; // 起步小段
  const [px, py] = lift >= 1 ? polar(WORLD.cx, WORLD.cy, WORLD.R, a) : [bx, by];
  drawTrail(ctx, tt2 => [px, py], t, { life: 0.35, n: 7, r: 26 });
  if (coinIn > 0) {
    ctx.save(); ctx.globalAlpha = coinIn;
    drawCoin(ctx, px, py, t, { r: 26 });
    ctx.restore();
  }
  // 小注："一笔钱"
  writeText(ctx, '一笔钱', px - 64, py - 70, 34, { t: seg(t, t0 + 0.8, t0 + 1.6), color: PAL.gold });
  ctx.restore();
}

/* ---------- 第 2 章 · 公式 ---------- */
function ch2(ctx, t, tt) {
  const { t0, t1 } = tt;
  ringWorld(ctx, t, { stationDim: false });
  // 币匀速作节拍
  const laps = (t - NARR[0]) / 7.2;
  const a = -Math.PI / 2 + laps * 2 * Math.PI;
  const [px, py] = polar(WORLD.cx, WORLD.cy, WORLD.R, a);
  drawTrail(ctx, s => polar(WORLD.cx, WORLD.cy, WORLD.R, -Math.PI / 2 + ((s - NARR[0]) / 7.2) * 2 * Math.PI), t, { life: 0.3 });
  drawCoin(ctx, px, py, t);
  // 左侧公式板
  const g = seg(t, t0 + 0.2, t0 + 0.9);
  ctx.save(); ctx.globalAlpha = g;
  writeText(ctx, '快不快，看资金周转率', 180, 240, 52, { t: seg(t, t0 + 0.25, t0 + 0.75), weight: 'bold' });
  readout(ctx, 460, 500, [
    { str: '资金周转率 n', t: seg(t, t0 + 1.0, t1 - t0 > 4.8 ? t0 + 1.9 : t0 + 1.5), px: 42 },
    { str: '= 收入 R ÷ 平均占用 A', t: seg(t, t0 + 1.9, t0 + 3.2), px: 46, color: PAL.gold },
    { str: '单位：次 / 年', t: seg(t, t0 + 3.1, t0 + 3.9), px: 30, color: PAL.inkDim },
  ], t);
  ctx.restore();
}

/* ---------- 第 3 章 · 钟面：两圈量出来 ---------- */
function ch3(ctx, t, tt) {
  const { t0, t1 } = tt, dur = t1 - t0;
  const cx = WORLD.cx, cy = WORLD.cy, R = WORLD.R;
  ringWorld(ctx, t, { stationDim: true });
  // 360 刻度
  const tickIn = seg(t, t0 + 0.2, t0 + 1.2);
  ctx.save(); ctx.globalAlpha = tickIn * 0.85;
  for (let d = 0; d < 360; d += 3) {
    const a = -Math.PI / 2 + d / 360 * 2 * Math.PI;
    const long = d % 30 === 0;
    const p0 = polar(cx, cy, R + 18, a), p1 = polar(cx, cy, R + (long ? 34 : 26), a);
    ctx.strokeStyle = long ? PAL.inkDim : 'rgba(242,237,228,0.25)';
    ctx.lineWidth = long ? 2.2 : 1.4;
    ctx.beginPath(); ctx.moveTo(...p0); ctx.lineTo(...p1); ctx.stroke();
  }
  // 基数刻度数字（天）——环内侧，避开外圈天数弧
  ctx.font = fontOf(26, '', '"Microsoft YaHei",serif');
  ctx.fillStyle = PAL.inkDim; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  [[90, -Math.PI / 2 + Math.PI / 2], [180, -Math.PI / 2 + Math.PI], [270, -Math.PI / 2 + Math.PI * 1.5]]
    .forEach(([d, a]) => {
      const [x, y] = polar(cx, cy, R - 72, a);
      ctx.fillText(`${d}天`, x, y);
    });
  ctx.restore();
  // 币跑两圈（留 0.8s 收尾）
  const runT = Math.min(t, t1 - 0.7);
  const laps = clamp01((runT - t0 - 0.9) / (dur - 1.7)) * 2;
  const posOf = s => polar(cx, cy, R, -Math.PI / 2 + clamp01((Math.min(s, t1 - 0.7) - t0 - 0.9) / (dur - 1.7)) * 2 * 2 * Math.PI);
  drawTrail(ctx, posOf, t, { life: 0.4, n: 10 });
  const [px, py] = posOf(t);
  drawCoin(ctx, px, py, t);
  // 圈计数 + 天扫弧
  const lapDone = Math.floor(laps);
  const dayAng = -Math.PI / 2 + laps / 2 * 2 * Math.PI; // 1圈=180天，弧=天数/360*2π
  ctx.save();
  ctx.strokeStyle = PAL.gold; ctx.lineWidth = 6; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(cx, cy, R + 52, -Math.PI / 2, Math.max(-Math.PI / 2 + 0.001, dayAng)); ctx.stroke();
  // 天数数字跟弧头（累计口径，消除"中途数字"歧义）
  const [dx, dy] = polar(cx, cy, R + 52, dayAng);
  ctx.font = fontOf(28, 'bold', '"Microsoft YaHei",serif');
  ctx.fillStyle = PAL.gold; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(`累计 ${Math.round(laps / 2 * 180)} 天`, dx, dy - 36);
  ctx.restore();
  // 中心读数
  readout(ctx, cx, cy - 6, [
    { str: `${lapDone} 圈 / 年`, t: 1, px: 44, color: PAL.gold },
  ], t);
  // 左侧推导（先算率，再算天）
  writeText(ctx, '4000万 ÷ 2000万', 250, 350, 44, { t: seg(t, t0 + 0.8, t0 + 1.5) });
  writeText(ctx, '= 2 次/年', 250, 420, 44, { t: seg(t, t0 + 1.4, t0 + 2.0), color: PAL.gold });
  writeText(ctx, '360 ÷ 2 = 180 天/圈', 250, 520, 44, { t: seg(t, t0 + 3.2, t0 + 4.0) });
  // 每圈落地提示
  if (lapDone >= 1) writeText(ctx, '第 1 圈 · 180 天', cx - R * 0.0, cy + R + 92, 32, { t: seg(t, t0 + 4.3, t0 + 4.8), align: 'center', color: PAL.inkDim });
  if (lapDone >= 2) writeText(ctx, '第 2 圈 · 又 180 天', cx, cy + R + 132, 32, { t: seg(t, t0 + 6.2, t0 + 6.7), align: 'center', color: PAL.inkDim });
}

/* ---------- 第 4 章 · 双环对照 ---------- */
function ch4(ctx, t, tt) {
  const { t0, t1 } = tt, dur = t1 - t0;
  const runDur = dur - 1.0;
  const L = { cx: 600, cy: 500 }, Rt = { cx: 1320, cy: 500 }, r = 265;
  const moveIn = easeInOut(seg(t, t0, t0 + 0.7));
  // 顶部共同收入
  writeText(ctx, '收入同为 4000 万', 960, 150, 44, { t: seg(t, t0 + 0.4, t0 + 1.0), align: 'center', color: PAL.ink });
  [[L, '左'], [Rt, '右']].forEach(([C]) => {
    drawTrack(ctx, { cx: C.cx, cy: C.cy, r, t, reveal: 1, seed: 7 });
    WORLD.stations.forEach((st, i) => {
      const [x, y] = polar(C.cx, C.cy, r, st.a);
      drawStation(ctx, x, y, st, seg(t, t0 + 0.2 + i * 0.1, t0 + 0.8 + i * 0.1), t, {});
    });
  });
  // 币：左 2 圈，右 4 圈
  const runT = Math.min(Math.max(t - t0 - 0.8, 0), runDur);
  const f = runT / runDur;
  const aL = -Math.PI / 2 + f * 2 * 2 * Math.PI;
  const aR = -Math.PI / 2 + f * 4 * 2 * Math.PI;
  const [lx, ly] = polar(L.cx, L.cy, r, aL);
  const [rx, ry] = polar(Rt.cx, Rt.cy, r, aR);
  drawTrail(ctx, s => polar(L.cx, L.cy, r, -Math.PI / 2 + clamp01((Math.min(Math.max(s - t0 - 0.8, 0), runDur)) / runDur) * 4 * Math.PI), t, { life: 0.3, r: 22 });
  drawTrail(ctx, s => polar(Rt.cx, Rt.cy, r, -Math.PI / 2 + clamp01((Math.min(Math.max(s - t0 - 0.8, 0), runDur)) / runDur) * 8 * Math.PI), t, { life: 0.2, r: 22 });
  drawCoin(ctx, lx, ly, t, { r: 22 });
  drawCoin(ctx, rx, ry, t, { r: 22 });
  // 圈计数
  writeText(ctx, `${Math.floor(f * 2)} 圈`, L.cx, L.cy, 52, { t: 1, align: 'center', color: PAL.gold });
  writeText(ctx, `${Math.floor(f * 4)} 圈`, Rt.cx, Rt.cy, 52, { t: 1, align: 'center', color: PAL.gold });
  // 资金池（带半池基准线，减半有据可查）
  drawPool(ctx, L.cx, 900, 300, 1.0 * easeOut(seg(t, t0 + 0.6, t0 + 1.4)), '占用 2000 万', t, { halfMark: true });
  drawPool(ctx, Rt.cx, 900, 300, 0.5 * easeOut(seg(t, t0 + 0.6, t0 + 1.4)), '占用 1000 万', t, { halfMark: true });
  // 中央结论（两环间隙窄，竖排两行，与旁白"速度翻倍，占用减半"同锚）
  writeText(ctx, '速度翻倍', 960, 505, 38, { t: seg(t, t0 + 4.0, t0 + 4.6), align: 'center', color: PAL.gold, weight: 'bold' });
  writeText(ctx, '占用减半', 960, 565, 38, { t: seg(t, t0 + 4.5, t0 + 5.1), align: 'center', color: PAL.gold, weight: 'bold' });
}

/* ---------- 第 5 章 · 双节奏层 ---------- */
function ch5(ctx, t, tt) {
  const { t0, t1 } = tt;
  const cx = WORLD.cx, cy = WORLD.cy;
  // 外弧：固定资金（粗、缓）——提亮石板色保对比
  ctx.save();
  ctx.strokeStyle = '#5d7490'; ctx.lineWidth = 13; ctx.lineCap = 'round';
  inkCircle(ctx, cx, cy, WORLD.R + 46, { seed: 71, amp: 2 }); ctx.stroke();
  ctx.restore();
  // 内弧：流动资金（细、快）
  ctx.save();
  ctx.strokeStyle = PAL.cyan; ctx.lineWidth = 4.5;
  inkCircle(ctx, cx, cy, WORLD.R - 46, { seed: 72, amp: 1.6 }); ctx.stroke();
  ctx.strokeStyle = 'rgba(127,180,199,0.5)'; ctx.lineWidth = 3;
  ctx.setLineDash([14, 16]); ctx.lineDashOffset = -(t * 90) % 30;
  ctx.beginPath(); ctx.arc(cx, cy, WORLD.R - 62, 0, Math.PI * 2); ctx.stroke();
  ctx.restore();
  // 两枚币：外重缓 / 内轻快
  const oL = (t - t0) / 6.5, iL = (t - t0) / 1.7; // 外 1 圈 vs 内 ~4 圈
  const oa = -Math.PI / 2 + oL * 2 * Math.PI, ia = -Math.PI / 2 + iL * 2 * Math.PI;
  const [ox, oy] = polar(cx, cy, WORLD.R + 46, oa);
  const [ix, iy] = polar(cx, cy, WORLD.R - 46, ia);
  // 外：重盘（更大更重）
  ctx.save(); ctx.translate(ox, oy);
  ctx.fillStyle = '#5d7490'; ctx.beginPath(); ctx.arc(0, 0, 36, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = '#0d1420'; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.arc(0, 0, 36, 0, Math.PI * 2); ctx.stroke();
  ctx.font = fontOf(30, 'bold', '"Microsoft YaHei",sans-serif'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = '#0d1420'; ctx.fillText('厂', 0, 2);
  ctx.restore();
  drawTrail(ctx, s => polar(cx, cy, WORLD.R - 46, -Math.PI / 2 + ((s - t0) / 1.7) * 2 * Math.PI), t, { life: 0.25, r: 18 });
  drawCoin(ctx, ix, iy, t, { r: 18 });
  // 标注（左置，远离弧线）
  writeText(ctx, '固定资金：厂房 · 设备', 190, 320, 38, { t: seg(t, t0 + 0.3, t0 + 0.9), color: '#8fa6c4' });
  writeText(ctx, '转得慢', 190, 384, 34, { t: seg(t, t0 + 0.8, t0 + 1.3), color: PAL.inkDim });
  writeText(ctx, '流动资金：材料 · 存货', 190, 640, 38, { t: seg(t, t0 + 1.5, t0 + 2.1), color: PAL.cyan });
  writeText(ctx, '转得快', 190, 704, 34, { t: seg(t, t0 + 2.0, t0 + 2.5), color: PAL.inkDim });
}

/* ---------- 第 6 章 · 编织成总资金 ---------- */
function ch6(ctx, t, tt) {
  const { t0, t1 } = tt, u = tt.u;
  const cx = WORLD.cx, cy = WORLD.cy, R = WORLD.R;
  // 双股从分离到绞合：振幅 46 → 0
  const amp = 46 * (1 - easeInOut(clamp01(u * 2.4)));
  const turns = 3;
  const braidR = a => R + Math.sin(a * turns) * amp;   // 币走的编织中线
  [PAL.slate, PAL.cyan].forEach((col, s) => {
    ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = s === 0 ? 9 : 4;
    ctx.beginPath();
    const n = 160;
    for (let i = 0; i <= n; i++) {
      const a = -Math.PI / 2 + i / n * 2 * Math.PI;
      const rr = R + Math.sin(a * turns + s * Math.PI) * amp;
      const [x, y] = polar(cx, cy, rr, a);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.closePath(); ctx.stroke(); ctx.restore();
  });
  // 合股后浮现主轨金色
  const merged = seg(t, t0 + (t1 - t0) * 0.55, t0 + (t1 - t0) * 0.85);
  if (merged > 0) {
    ctx.save(); ctx.globalAlpha = merged;
    drawTrack(ctx, { cx, cy, r: R, t });
    ctx.restore();
  }
  writeText(ctx, '总资金 = 两种节奏的混合', 250, 540, 46, { t: seg(t, t0 + 0.5, t0 + 1.1), weight: 'bold' });
  // 币沿编织线行进（先骑缝，合股后落主轨）
  const ca = -Math.PI / 2 + (t - t0) * 1.6;
  const rr = amp > 1 ? braidR(ca) : R;
  const [px, py] = polar(cx, cy, rr, ca);
  drawTrail(ctx, s => {
    const sa = -Math.PI / 2 + (s - t0) * 1.6;
    return polar(cx, cy, amp > 1 ? braidR(sa) : R, sa);
  }, t, { life: 0.5, n: 12, r: 24 });
  drawCoin(ctx, px, py, t, { r: 24 });
  // 编织流粒子（沿两股游走的小点）
  for (let k = 0; k < 5; k++) {
    const pa = -Math.PI / 2 + ((t * 0.9 + k * 1.25) % (Math.PI * 2));
    const strand = k % 2;
    const pr = R + Math.sin(pa * turns + strand * Math.PI) * amp;
    const [qx, qy] = polar(cx, cy, pr, pa);
    ctx.save(); ctx.globalAlpha = 0.5 * (amp / 46);
    ctx.fillStyle = strand ? PAL.cyan : '#5d7490';
    ctx.beginPath(); ctx.arc(qx, qy, 5, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }
}

/* ---------- 第 7 章 · 三只量杯 ---------- */
function ch7(ctx, t, tt) {
  const { t0, t1 } = tt;
  const cups = [
    { x: 560,  name: '全部资金周转率', den: '分母：全部资金', lv: 0.62 },
    { x: 960,  name: '分项资金周转率', den: '分母：固定资金 或 流动资金', lv: 0.80 },
    { x: 1360, name: '营运资金周转率', den: '分母：流动资产 − 流动负债', lv: 0.44 },
  ];
  const bw = 250, bh = 300, by = 760;
  writeText(ctx, '口径别混', 180, 220, 54, { t: seg(t, t0 + 0.1, t0 + 0.6), weight: 'bold' });
  cups.forEach((c, i) => {
    const app = seg(t, t0 + 0.2 + i * 0.25, t0 + 0.9 + i * 0.25);
    if (app <= 0) return;
    ctx.save(); ctx.globalAlpha = app;
    const y0 = by, x0 = c.x - bw / 2;
    // 杯体（微梯形）
    ctx.strokeStyle = PAL.ink; ctx.lineWidth = 3.2;
    inkLine(ctx, [[x0 + 14, y0], [x0, y0 - bh], [x0 + bw, y0 - bh], [x0 + bw - 14, y0]], { seed: 50 + i }); ctx.stroke();
    // 刻度（分母不同 → 刻度位置不同）
    ctx.strokeStyle = 'rgba(242,237,228,0.3)'; ctx.lineWidth = 1.6;
    for (let k = 1; k <= 4; k++) {
      const yy = y0 - bh * k / 5;
      const inset = 14 * (1 - k / 5);
      ctx.beginPath(); ctx.moveTo(x0 + inset + 8, yy); ctx.lineTo(x0 + bw / 2 - 30, yy); ctx.stroke();
    }
    // 注入（壶嘴在上，依次）
    const pour = seg(t, t0 + 0.9 + i * 0.55, t0 + 1.7 + i * 0.55);
    const lv = c.lv * easeOut(seg(t, t0 + 0.9 + i * 0.55, t0 + 2.0 + i * 0.55));
    if (lv > 0) {
      const ly = y0 - (bh - 16) * lv;
      ctx.fillStyle = PAL.goldSoft;
      ctx.beginPath();
      ctx.moveTo(x0 + 16, y0 - 2); ctx.lineTo(x0 + 16, ly);
      ctx.bezierCurveTo(x0 + bw / 3, ly + 3, x0 + bw * 2 / 3, ly - 3, x0 + bw - 16, ly);
      ctx.lineTo(x0 + bw - 16, y0 - 2); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = PAL.goldLine; ctx.lineWidth = 2.4;
      ctx.beginPath(); ctx.moveTo(x0 + 16, ly);
      ctx.bezierCurveTo(x0 + bw / 3, ly + 3, x0 + bw * 2 / 3, ly - 3, x0 + bw - 16, ly); ctx.stroke();
    }
    if (pour > 0 && pour < 1) { // 倒入液流
      ctx.strokeStyle = PAL.cyan; ctx.lineWidth = 5; ctx.lineCap = 'round';
      ctx.globalAlpha = app * (0.5 + Math.sin(t * 20) * 0.2);
      ctx.beginPath(); ctx.moveTo(c.x + 90, 150);
      ctx.bezierCurveTo(c.x + 80, 260, c.x + 40, y0 - bh - 40, c.x + 30, ly0(c, lv, y0, bh));
      ctx.stroke();
    }
    // 名称/分母
    writeText(ctx, c.name, c.x, y0 - bh - 92, 34, { t: app, align: 'center' });
    writeText(ctx, c.den, c.x, y0 + 44, 28, { t: seg(t, t0 + 1.6 + i * 0.55, t0 + 2.1 + i * 0.55), align: 'center', color: PAL.inkDim });
    ctx.restore();
  });
  // 误比的 = 被划掉（放大提亮，一眼可见）
  const strike = seg(t, t0 + 3.4, t0 + 3.9);
  if (strike > 0) {
    ctx.save(); ctx.globalAlpha = strike;
    writeText(ctx, '=', 760, 560, 84, { t: strike, align: 'center', color: PAL.ink });
    writeText(ctx, '=', 1160, 560, 84, { t: strike, align: 'center', color: PAL.ink });
    ctx.strokeStyle = PAL.slate; ctx.lineWidth = 8; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(714, 560 - 34); ctx.lineTo(806, 560 + 34); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(1114, 560 - 34); ctx.lineTo(1206, 560 + 34); ctx.stroke();
    writeText(ctx, '分母不同，不能硬比', 960, 930, 44, { t: seg(t, t0 + 3.8, t0 + 4.4), align: 'center', color: PAL.ink });
    ctx.restore();
  }
}
function ly0(c, lv, y0, bh) { return y0 - (bh - 16) * Math.max(lv, 0.04); }

/* ---------- 第 8 章 · 带伤加速（唯一红章） ---------- */
function ch8(ctx, t, tt) {
  const { t0, t1 } = tt, u = tt.u;
  const cx = WORLD.cx, cy = WORLD.cy, R = WORLD.R;
  const dmg = easeInOut(seg(t, t0 + 0.9, t0 + 4.2)) * 0.62;
  const speed = 1 + easeInOut(seg(t, t0 + 0.3, t0 + 2.0)) * 1.8; // 基速→2.8x
  const a = -Math.PI / 2 + (t - t0) * 1.9 * speed;
  // 红色警示晕
  const pulse = 0.5 + Math.sin(t * 6) * 0.5;
  const g = ctx.createRadialGradient(cx, cy, R * 0.4, cx, cy, R * 1.9);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(208,83,83,${0.16 * pulse * dmg / 0.62})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, 1920, 1080);
  // 断裂轨道（断口更宽，撕裂感）
  ctx.save();
  ctx.strokeStyle = PAL.goldLine; ctx.lineWidth = 5;
  const gaps = [[0.36, 0.62], [2.28, 2.74], [4.2, 4.66]]; // 弧度断口
  let a0 = -Math.PI / 2;
  const segsArc = [];
  for (const [gs, ge] of gaps) {
    const s0 = -Math.PI / 2 + gs, s1 = -Math.PI / 2 + ge;
    if (s0 > a0) segsArc.push([a0, s0]);
    a0 = s1;
  }
  segsArc.push([a0, -Math.PI / 2 + Math.PI * 2]);
  segsArc.forEach(([s, e], i) => {
    inkCircle(ctx, cx, cy, R, { seed: 7 + Math.floor(t * 12) % 7, amp: 1.8 + dmg * 2.4, a0: s, a1: e }); ctx.stroke();
    if (dmg > 0.25) { // 断口错位撕裂线（更长更重）+ 断口震颤电火花
      [s, e].forEach((aa, j) => {
        const p0 = polar(cx, cy, R - 20 - dmg * 8, aa), p1 = polar(cx, cy, R + 20 + dmg * 12, aa + 0.08);
        ctx.strokeStyle = PAL.red; ctx.lineWidth = 4;
        inkLine(ctx, [p0, polar(cx, cy, R, aa + 0.04), p1], { seed: i * 9 + j }); ctx.stroke();
        // 电火花：断口处闪烁锯齿
        const flick = boil(t, i * 2 + j) > 0.35;
        if (flick && dmg > 0.4) {
          const pm = polar(cx, cy, R, (s + e) / 2);
          ctx.strokeStyle = PAL.red; ctx.lineWidth = 2.2;
          const zz = [[pm[0] - 16, pm[1] - 10], [pm[0] + 4, pm[1] + 6], [pm[0] - 6, pm[1] + 2], [pm[0] + 14, pm[1] + 12]];
          inkLine(ctx, zz, { seed: i * 17 + j + Math.floor(t * 12), amp: 2.4 }); ctx.stroke();
        }
        ctx.strokeStyle = PAL.goldLine;
      });
    }
  });
  ctx.restore();
  // 站点（受损）
  WORLD.stations.forEach((st, i) => {
    const [x, y] = polar(cx, cy, R, st.a);
    drawStation(ctx, x, y, st, 1, t, { damage: dmg });
  });
  // 币（狂奔，拖尾加剧）
  drawTrail(ctx, s => polar(cx, cy, R, -Math.PI / 2 + (s - t0) * 1.9 * speed), t, { life: 0.55, n: 16 });
  const [px, py] = polar(cx, cy, R, a);
  drawCoin(ctx, px, py, t, { r: 26 });
  // 标注
  writeText(ctx, '硬压库存 · 猛催账期', 250, 400, 46, { t: seg(t, t0 + 0.4, t0 + 1.0), color: PAL.red, weight: 'bold' });
  writeText(ctx, '也能"催"出快数字', 250, 470, 38, { t: seg(t, t0 + 1.1, t0 + 1.7), color: PAL.inkDim });
  writeText(ctx, '但机器在受伤', 250, 545, 42, { t: seg(t, t0 + 3.0, t0 + 3.6), color: PAL.red });
}

/* ---------- 第 9 章 · 水电站 ---------- */
function ch9(ctx, t, tt) {
  const { t0, t1 } = tt, u = tt.u;
  const fadeIn = seg(t, t0, t0 + 0.5);
  ctx.save(); ctx.globalAlpha = fadeIn;
  // 山谷剪影
  ctx.fillStyle = '#131e30';
  ctx.beginPath(); ctx.moveTo(0, 1080);
  ctx.lineTo(0, 660); ctx.lineTo(360, 430); ctx.lineTo(760, 640); ctx.lineTo(1100, 380); ctx.lineTo(1500, 610); ctx.lineTo(1920, 460); ctx.lineTo(1920, 1080);
  ctx.closePath(); ctx.fill();
  // 坝体（有厚度的实体弧带，嵌入两山之间）
  ctx.fillStyle = '#2a3a52';
  ctx.beginPath();
  ctx.moveTo(600, 545);
  ctx.quadraticCurveTo(830, 705, 1060, 545);   // 外弧
  ctx.lineTo(1060, 585);
  ctx.quadraticCurveTo(830, 745, 600, 585);     // 内弧（更低的下游面）
  ctx.closePath(); ctx.fill();
  ctx.strokeStyle = '#42557a'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(600, 545); ctx.quadraticCurveTo(830, 705, 1060, 545); ctx.stroke();
  // 坝顶栏杆小刻线
  ctx.strokeStyle = 'rgba(242,237,228,0.3)'; ctx.lineWidth = 1.6;
  for (let i = 1; i <= 6; i++) {
    const f = i / 7;
    const x = 600 + 460 * f, y = 545 + Math.sin(Math.PI * f) * 158;
    ctx.beginPath(); ctx.moveTo(x, y - 12); ctx.lineTo(x, y); ctx.stroke();
  }
  // 库水（高水位、静；岸线勾边）
  ctx.fillStyle = 'rgba(127,180,199,0.30)';
  ctx.beginPath(); ctx.moveTo(0, 620);
  for (let x = 0; x <= 640; x += 16) ctx.lineTo(x, 620 + Math.sin(x * 0.02 + t * 1.1) * 3);
  ctx.lineTo(640, 780); ctx.lineTo(0, 780); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = 'rgba(127,180,199,0.55)'; ctx.lineWidth = 2;
  ctx.beginPath();
  for (let x = 0; x <= 640; x += 16) { const y = 620 + Math.sin(x * 0.02 + t * 1.1) * 3; x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
  ctx.stroke();
  // 泄流（从坝体闸口射向水轮，双股+水花）
  ctx.strokeStyle = PAL.cyan; ctx.lineWidth = 4.5; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(1010, 668);
  ctx.bezierCurveTo(1100, 730, 1170, 760, 1268, 782); ctx.stroke();
  ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(1000, 680);
  ctx.bezierCurveTo(1080, 745, 1140, 775, 1232, 802); ctx.stroke();
  // 大水轮（沉稳慢转；闭式斗勺）
  const wx = 1360, wy = 830, wr = 170;
  const wa = t * 0.32; // 慢
  ctx.save(); ctx.translate(wx, wy); ctx.rotate(wa);
  // 轮影（地面阴影=重量感）
  ctx.save(); ctx.rotate(-wa); // 阴影不随轮转
  ctx.fillStyle = 'rgba(0,0,0,0.35)';
  ctx.beginPath(); ctx.ellipse(0, wr + 42, wr * 0.92, 22, 0, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
  ctx.strokeStyle = '#9fb2cc'; ctx.lineWidth = 13;
  ctx.beginPath(); ctx.arc(0, 0, wr, 0, Math.PI * 2); ctx.stroke();
  ctx.strokeStyle = 'rgba(159,178,204,0.4)'; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.arc(0, 0, wr - 16, 0, Math.PI * 2); ctx.stroke();
  ctx.lineWidth = 8;
  for (let i = 0; i < 8; i++) {
    const a = i * Math.PI / 4;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * wr, Math.sin(a) * wr); ctx.stroke();
    // 闭式斗勺（弦+弧围成的水斗）
    const bx = Math.cos(a) * wr, by = Math.sin(a) * wr;
    ctx.fillStyle = '#9fb2cc';
    ctx.beginPath();
    ctx.arc(bx, by, 20, a + Math.PI / 2, a - Math.PI / 2); // 外弧
    ctx.closePath();
    ctx.fill();
  }
  ctx.fillStyle = '#c6d4e6';
  ctx.beginPath(); ctx.arc(0, 0, 24, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
  // 尾水波纹
  ctx.strokeStyle = 'rgba(127,180,199,0.4)'; ctx.lineWidth = 2;
  for (let i = 0; i < 3; i++) {
    const ph = (t * 0.5 + i / 3) % 1;
    ctx.globalAlpha = fadeIn * (1 - ph) * 0.6;
    ctx.beginPath(); ctx.ellipse(wx + 60, 1010, 120 + ph * 260, 18 + ph * 30, 0, 0, Math.PI * 2); ctx.stroke();
  }
  ctx.restore();
  writeText(ctx, '水电站 · 天生慢', 250, 380, 46, { t: seg(t, t0 + 0.6, t0 + 1.2), weight: 'bold' });
  writeText(ctx, '结构性慢 ≠ 低效', 250, 452, 42, { t: seg(t, t0 + 1.6, t0 + 2.2), color: PAL.cyan });
}

/* ---------- 第 10 章 · 三问清单 ---------- */
function ch10(ctx, t, tt) {
  const { t0, t1 } = tt;
  const px = 960, py = 560;
  const app = seg(t, t0 + 0.1, t0 + 0.6);
  ctx.save();
  ctx.translate(px, py); ctx.rotate(-0.015);
  ctx.globalAlpha = app;
  // 纸板
  ctx.fillStyle = 'rgba(20,30,48,0.9)';
  ctx.strokeStyle = PAL.ink; ctx.lineWidth = 3;
  inkLine(ctx, [[-560, -330], [560, -330], [560, 330], [-560, 330], [-560, -330]], { seed: 60 }); ctx.stroke();
  ctx.restore();
  writeText(ctx, '先问三件事', px, py - 220, 52, { t: seg(t, t0 + 0.4, t0 + 0.9), align: 'center', weight: 'bold' });
  const items = ['口径对不对？', '跟谁比？', '为什么快 / 慢？'];
  items.forEach((s, i) => {
    const y = py - 80 + i * 150;
    const wIn = seg(t, t0 + 0.9 + i * 0.85, t0 + 1.5 + i * 0.85);
    writeText(ctx, `${'①②③'[i]} ${s}`, px - 380, y, 46, { t: wIn });
    // 勾
    const ck = seg(t, t0 + 1.5 + i * 0.85, t0 + 1.85 + i * 0.85);
    if (ck > 0) {
      ctx.save(); ctx.strokeStyle = PAL.gold; ctx.lineWidth = 7; ctx.lineCap = 'round';
      const bx = px + 380;
      ctx.beginPath(); ctx.moveTo(bx - 26, y + 2); ctx.lineTo(bx - 6, y + 22); ctx.stroke();
      const p2 = seg(t, t0 + 1.68 + i * 0.85, t0 + 1.95 + i * 0.85);
      if (p2 > 0) { ctx.beginPath(); ctx.moveTo(bx - 6, y + 22); ctx.lineTo(bx + 30, y - 26); ctx.stroke(); }
      ctx.restore();
    }
  });
}

/* ---------- 第 11 章 · 回收 ---------- */
function ch11(ctx, t, tt) {
  const { t0, t1 } = tt, u = tt.u;
  const cx = WORLD.cx, cy = WORLD.cy, R = WORLD.R;
  // 缓慢拉远
  const zoom = 1 - easeInOut(seg(t, t0, t1)) * 0.07;
  ctx.save();
  camApply(ctx, { x: 1060, y: 560, zoom });
  ringWorld(ctx, t, {});
  // 健康匀速（速度感：拖尾 + 切向亮弧）
  const a = -Math.PI / 2 + (t - t0) * 1.5;
  drawTrail(ctx, s => polar(cx, cy, R, -Math.PI / 2 + (s - t0) * 1.5), t, { life: 0.7, n: 16 });
  ctx.save();
  ctx.strokeStyle = 'rgba(233,180,76,0.5)'; ctx.lineWidth = 4; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(cx, cy, R, a - 0.5, a - 0.06); ctx.stroke();
  ctx.restore();
  const [px, py] = polar(cx, cy, R, a);
  drawCoin(ctx, px, py, t, { r: 26 });
  ctx.restore();
  writeText(ctx, '让钱一圈一圈健康地转', 300, 500, 54, { t: seg(t, t0 + 0.4, t0 + 1.2), weight: 'bold', color: '#f0c768' });
  // 收暗（推迟到最后一刻）
  const dark = easeInOut(seg(t, t1 - 1.3, t1 - 0.1));
  if (dark > 0) { ctx.fillStyle = `rgba(13,20,32,${dark})`; ctx.fillRect(0, 0, 1920, 1080); }
  // 币最后的小光点
  const lastGlow = seg(t, t1 - 1.2, t1 - 0.1);
  if (lastGlow > 0 && dark > 0.4) {
    ctx.save(); ctx.globalAlpha = Math.sin(lastGlow * Math.PI) * 0.9;
    ctx.fillStyle = PAL.gold;
    ctx.beginPath(); ctx.arc(1500, 560, 10, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }
}

const CHAPTERS = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11];
