// world.js — 环世界物件：轨道 / 五站 / 金币 / 资金池 / 机位
// 全部为"参数 → 绘制"的纯函数，无跨帧状态。
'use strict';

/* ---------- 世界坐标（默认机位下） ---------- */
const WORLD = {
  cx: 1160, cy: 560, R: 380,
  // 站点角度（顺时针旅程）：现金(顶) → 采购材料 → 生产 → 销售成品 → 回款
  stations: [
    { a: -Math.PI / 2,     name: '现金',   kind: 'cash' },
    { a: -Math.PI / 2 + 1.2566, name: '材料', kind: 'crate' },
    { a: -Math.PI / 2 + 2.5132, name: '生产', kind: 'gear' },
    { a: -Math.PI / 2 + 3.7698, name: '销售', kind: 'shop' },
    { a: -Math.PI / 2 + 5.0264, name: '回款', kind: 'flow' },
  ],
};

function polar(cx, cy, r, a) { return [cx + Math.cos(a) * r, cy + Math.sin(a) * r]; }

/* ---------- 机位：world→screen 变换 ---------- */
function camApply(ctx, cam) {
  // cam = {x, y, zoom}：先平移到焦点，缩放，再平移回
  const { x = 960, y = 540, zoom = 1 } = cam;
  ctx.translate(960, 540);
  ctx.scale(zoom, zoom);
  ctx.translate(-x, -y);
}

/* ---------- 轨道：双同心手绘圆 + 内侧虚线（双线复描保证闭合） ---------- */
function drawTrack(ctx, { cx = WORLD.cx, cy = WORLD.cy, r = WORLD.R, t = 0, reveal = 1, seed = 7 } = {}) {
  const a0 = -Math.PI / 2, a1 = a0 + Math.PI * 2 * clamp01(reveal);
  ctx.save();
  // 主笔
  ctx.strokeStyle = PAL.goldLine; ctx.lineWidth = 5; ctx.lineCap = 'round';
  inkCircle(ctx, cx, cy, r, { seed: seed + Math.floor(t * 12) % 7, amp: 1.8, a0, a1 });
  ctx.stroke();
  // 复描（旋转半格的轻线，手绘双勾，兼保闭合）
  if (reveal >= 1) {
    ctx.strokeStyle = 'rgba(233,180,76,0.45)'; ctx.lineWidth = 2.5;
    inkCircle(ctx, cx, cy, r, { seed: seed + 3 + Math.floor(t * 12) % 7, amp: 2.2, a0: a0 + 0.04, a1: a1 + 0.1 });
    ctx.stroke();
    // 内衬虚线（行进方向暗示）
    ctx.strokeStyle = 'rgba(233,180,76,0.3)'; ctx.lineWidth = 2.4;
    ctx.setLineDash([5, 11]); ctx.lineDashOffset = -(t * 40) % 16;
    ctx.beginPath(); ctx.arc(cx, cy, r - 14, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);
  }
  ctx.restore();
}

/* ---------- 站点 ---------- */
// app ∈ [0,1] 入场；opts: {dim, damage(0-1 第8章收缩), labelSize}
function drawStation(ctx, x, y, st, app, t, opts = {}) {
  if (app <= 0) return;
  const s = easeBack(app);
  const dmg = opts.damage || 0;
  const shrink = 1 - dmg * 0.42;
  const wob = dmg * Math.sin(t * 24 + st.a * 3) * 5;
  ctx.save();
  ctx.translate(x + wob, y);
  ctx.scale(s * shrink, s * shrink);
  ctx.globalAlpha = clamp01(app * 1.2) * (opts.dim ? 0.35 : 1);

  const r = 46;
  // 底盘
  ctx.fillStyle = 'rgba(16,27,46,0.92)';
  ctx.beginPath(); ctx.arc(0, 0, r + 6, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = dmg > 0 ? PAL.red : PAL.goldLine; ctx.lineWidth = 3;
  inkCircle(ctx, 0, 0, r + 6, { seed: st.a * 100 | 0, amp: 1.4 }); ctx.stroke();
  if (dmg > 0) { // 裂纹（放射+中心，加深）
    ctx.strokeStyle = PAL.red; ctx.lineWidth = 3;
    for (let i = 0; i < 4; i++) {
      const a = st.a + i * 1.62;
      const p0 = polar(0, 0, 8, a), pm = polar(0, 0, (r + 6) * 0.55, a + 0.18), p1 = polar(0, 0, r + 14 + dmg * 14, a + 0.34);
      inkLine(ctx, [p0, pm, p1], { seed: i * 31, amp: 1.2 }); ctx.stroke();
    }
  }

  ctx.strokeStyle = opts.dim ? PAL.inkDim : PAL.ink;
  ctx.fillStyle = ctx.strokeStyle;
  ctx.lineWidth = 3.4; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  iconOf[st.kind](ctx, t);

  // 标签（径向外置，避开轨道）
  ctx.globalAlpha *= opts.dim ? 0.6 : 1;
  const [lx2, ly2] = [Math.cos(st.a) * (r + 52), Math.sin(st.a) * (r + 52)];
  ctx.font = fontOf(30);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = opts.dim ? PAL.inkDim : PAL.ink;
  ctx.fillText(st.name, lx2, ly2);
  ctx.restore();
}

/* 站点小图标（手绘线） */
const iconOf = {
  cash(ctx) { // ¥ 圆
    ctx.beginPath(); ctx.arc(0, 0, 24, 0, Math.PI * 2); ctx.stroke();
    ctx.font = fontOf(34, 'bold', '"Microsoft YaHei",sans-serif');
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('¥', 0, 3);
  },
  crate(ctx, t) { // 材料箱
    inkLine(ctx, [[-24, -16], [24, -16], [24, 18], [-24, 18], [-24, -16]], { seed: 11 }); ctx.stroke();
    inkLine(ctx, [[-24, -2], [24, -2]], { seed: 12 }); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-8, -16); ctx.lineTo(-8, -2); ctx.stroke();
  },
  gear(ctx, t) { // 生产齿轮
    const a = t * 1.1;
    ctx.save(); ctx.rotate(a);
    inkCircle(ctx, 0, 0, 16, { seed: 13 }); ctx.stroke();
    for (let i = 0; i < 8; i++) {
      const ang = i * Math.PI / 4;
      const p0 = polar(0, 0, 16, ang), p1 = polar(0, 0, 26, ang);
      inkLine(ctx, [p0, p1], { seed: 14 + i, amp: 0.8 }); ctx.stroke();
    }
    ctx.restore();
  },
  shop(ctx) { // 销售门面
    inkLine(ctx, [[-26, 20], [-26, -6], [26, -6], [26, 20]], { seed: 21 }); ctx.stroke();
    // 雨棚弧
    ctx.beginPath(); ctx.moveTo(-30, -6);
    for (let i = 0; i <= 8; i++) { const x = -30 + 60 * i / 8; ctx.lineTo(x, -6 - Math.sin(Math.PI * i / 8) * 12); }
    ctx.stroke();
    inkLine(ctx, [[-10, 20], [-10, 4], [10, 4], [10, 20]], { seed: 22 }); ctx.stroke();
  },
  flow(ctx, t) { // 回款：环形箭头
    const a0 = t * 1.4 % (Math.PI * 2);
    ctx.beginPath(); ctx.arc(0, 0, 20, a0, a0 + Math.PI * 1.5); ctx.stroke();
    const tip = polar(0, 0, 20, a0 + Math.PI * 1.5);
    const dir = a0 + Math.PI * 1.5 + Math.PI / 2;
    inkLine(ctx, [tip, [tip[0] + Math.cos(dir - 0.5) * 12, tip[1] + Math.sin(dir - 0.5) * 12]], { seed: 31 }); ctx.stroke();
    inkLine(ctx, [tip, [tip[0] + Math.cos(dir + 0.5) * 12, tip[1] + Math.sin(dir + 0.5) * 12]], { seed: 32 }); ctx.stroke();
  },
};

/* ---------- 金币（主角） ---------- */
// opts: {r, trail:(dt)->[x,y], damage, dim}
function drawCoin(ctx, x, y, t, opts = {}) {
  const r = opts.r || 26;
  const breath = 1 + Math.sin(t * 2.2) * 0.035;
  ctx.save();
  ctx.translate(x, y);
  // 光晕
  ctx.globalAlpha = 0.25 + Math.sin(t * 2.2) * 0.05;
  ctx.fillStyle = PAL.goldSoft;
  ctx.beginPath(); ctx.arc(0, 0, r * 2.1, 0, Math.PI * 2); ctx.fill();
  ctx.globalAlpha = 1;
  ctx.scale(breath, breath);
  // 币体
  ctx.fillStyle = PAL.gold;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = '#8a6420'; ctx.lineWidth = 3;
  inkCircle(ctx, 0, 0, r, { seed: 5, amp: 1 }); ctx.stroke();
  inkCircle(ctx, 0, 0, r * 0.66, { seed: 6, amp: 0.8 }); ctx.stroke();
  ctx.font = fontOf(r * 1.1, 'bold', '"Microsoft YaHei",sans-serif');
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = '#5c4110';
  ctx.fillText('¥', 0, 2);
  ctx.restore();
}
// 拖尾：沿路径函数回溯采样（含速度感增强）
function drawTrail(ctx, posOf, t, { life = 0.5, n = 9, r = 26 } = {}) {
  ctx.save();
  for (let i = 1; i <= n; i++) {
    const dt = i / n * life;
    const [x, y] = posOf(t - dt);
    if (x === undefined) continue;
    const a = (1 - i / n) * 0.45;
    ctx.globalAlpha = a;
    ctx.fillStyle = PAL.gold;
    ctx.beginPath(); ctx.arc(x, y, r * (1 - i / n) * 0.55, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
}

/* ---------- 资金池（占用额容器） ---------- */
// level01: 液位 0-1; label: 万元数值
function drawPool(ctx, x, y, w, level01, label, t, opts = {}) {
  const h = 120;
  ctx.save();
  ctx.translate(x, y);
  // 池体
  ctx.strokeStyle = PAL.ink; ctx.lineWidth = 3;
  inkLine(ctx, [[-w / 2, 0], [-w / 2, -h], [w / 2, -h], [w / 2, 0]], { seed: 41 }); ctx.stroke();
  ctx.strokeStyle = 'rgba(242,237,228,0.25)';
  ctx.beginPath(); ctx.moveTo(-w / 2 - 6, 0); ctx.lineTo(w / 2 + 6, 0); ctx.stroke();
  // 液体
  const lv = clamp01(level01) * h;
  const wob = Math.sin(t * 3) * 2;
  // 半池基准线（对照用）
  if (opts.halfMark) {
    ctx.strokeStyle = 'rgba(242,237,228,0.35)'; ctx.lineWidth = 1.6;
    ctx.setLineDash([6, 8]);
    ctx.beginPath(); ctx.moveTo(-w / 2 - 8, -h / 2); ctx.lineTo(w / 2 + 8, -h / 2); ctx.stroke();
    ctx.setLineDash([]);
  }
  ctx.fillStyle = PAL.goldSoft;
  ctx.beginPath();
  ctx.moveTo(-w / 2 + 3, -lv);
  ctx.bezierCurveTo(-w / 6, -lv + wob, w / 6, -lv - wob, w / 2 - 3, -lv);
  ctx.lineTo(w / 2 - 3, -1); ctx.lineTo(-w / 2 + 3, -1); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = PAL.goldLine; ctx.lineWidth = 2.4;
  ctx.beginPath();
  ctx.moveTo(-w / 2 + 3, -lv);
  ctx.bezierCurveTo(-w / 6, -lv + wob, w / 6, -lv - wob, w / 2 - 3, -lv);
  ctx.stroke();
  // 刻字（池体下方，固定位置）
  ctx.font = fontOf(30, '', '"Microsoft YaHei",sans-serif');
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = PAL.ink;
  ctx.fillText(label, 0, 42);
  ctx.restore();
}

/* ---------- 数字框（公式/读数） ---------- */
function readout(ctx, x, y, lines, t, opts = {}) {
  const px = opts.px || 40;
  ctx.save();
  ctx.font = fontOf(px, opts.weight || '', '"Microsoft YaHei",serif');
  const w = Math.max(...lines.map(l => ctx.measureText(l.str).width)) + 56;
  const h = lines.length * (px + 18) + 30;
  ctx.fillStyle = 'rgba(13,20,32,0.72)';
  ctx.strokeStyle = opts.accent ? PAL.goldLine : 'rgba(242,237,228,0.3)';
  ctx.lineWidth = 2.4;
  // 手绘圆角框
  const rr = 14;
  ctx.beginPath();
  ctx.moveTo(x - w / 2 + rr, y - h / 2);
  ctx.arcTo(x + w / 2, y - h / 2, x + w / 2, y + h / 2, rr);
  ctx.arcTo(x + w / 2, y + h / 2, x - w / 2, y + h / 2, rr);
  ctx.arcTo(x - w / 2, y + h / 2, x - w / 2, y - h / 2, rr);
  ctx.arcTo(x - w / 2, y - h / 2, x + w / 2, y - h / 2, rr);
  ctx.closePath(); ctx.fill(); ctx.stroke();
  lines.forEach((l, i) => {
    writeText(ctx, l.str, x, y - h / 2 + 15 + (px + 18) * (i + 0.5) - 9, l.px || px,
      { t: l.t !== undefined ? l.t : t, color: l.color || PAL.ink, align: 'center', family: '"Microsoft YaHei",serif' });
  });
  ctx.restore();
  return { w, h };
}
