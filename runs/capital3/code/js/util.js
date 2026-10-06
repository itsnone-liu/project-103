// util.js — 工具层：确定性随机 / 手绘线 / 缓动 / 色板 / 文字
// 五关契约#1：一切函数为 t 的纯函数；随机只来自 hash(i) 离散种子，跨帧无状态。
'use strict';

/* ---------- 色板（DESIGN.md palette arc） ---------- */
const PAL = {
  bg0: '#0d1420', bg1: '#101b2e',
  ink: '#f2ede4',          // 象牙白主文字
  inkDim: 'rgba(242,237,228,0.55)',
  gold: '#e9b44c',         // 主角金
  goldSoft: 'rgba(233,180,76,0.35)',
  goldLine: 'rgba(233,180,76,0.85)',
  cyan: '#7fb4c7',         // 流动层/水
  cyanSoft: 'rgba(127,180,199,0.4)',
  slate: '#3d4d63',        // 固定层/结构线
  red: '#d05353',          // 仅第 8 章
  redSoft: 'rgba(208,83,83,0.35)',
};

/* ---------- 确定性 hash（ANIMATION_GUIDE 同款技法） ---------- */
function hash(n) {
  n = Math.imul(n ^ (n >>> 15), 2246822519);
  n = Math.imul(n ^ (n >>> 13), 3266489917);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
// boil：12fps 重播种（手绘沸腾）
function boil(i, k) { return hash((Math.floor(i * 12) & 0xffff) * 131 + k * 7919); }

/* ---------- 缓动 ---------- */
const clamp01 = x => Math.max(0, Math.min(1, x));
const easeOut = x => 1 - Math.pow(1 - clamp01(x), 3);
const easeInOut = x => { x = clamp01(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const easeBack = x => { x = clamp01(x); const c = 1.70158; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
// 章内进度：局部时间 u ∈ [0,1)，p = u / frac
function seg(t, t0, t1) { return clamp01((t - t0) / (t1 - t0)); }

/* ---------- 手绘线（inkLine）：折线段上叠加 hash 垂直扰动 ---------- */
// pts: [[x,y],...]；seed: 抖动种子；amp: 扰动幅度(px)；分段越多越碎
function inkLine(ctx, pts, { seed = 0, amp = 1.6, segs = 3, close = false } = {}) {
  if (pts.length < 2) return;
  ctx.beginPath();
  const all = close ? pts.concat([pts[0]]) : pts;
  // 展开成细分点
  const dense = [];
  for (let i = 0; i < all.length - 1; i++) {
    const [x0, y0] = all[i], [x1, y1] = all[i + 1];
    for (let s = 0; s < segs; s++) {
      const f = s / segs;
      dense.push([x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, i * segs + s]);
    }
  }
  const [lx, ly] = all[all.length - 1];
  dense.push([lx, ly, (all.length - 1) * segs]);
  dense.forEach(([x, y, k], idx) => {
    // 垂直扰动
    const nx = (x - dense[Math.max(0, idx - 1)][0]) || 0.01, ny = (y - dense[Math.max(0, idx - 1)][1]) || 0.01;
    const len = Math.hypot(nx, ny) || 1;
    const j = (hash(k * 2654435761 + seed * 97) - 0.5) * 2 * amp;
    const px = x + (-ny / len) * j, py = y + (nx / len) * j;
    if (idx === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  });
}

// 手绘圆弧/圆
function inkCircle(ctx, cx, cy, r, { seed = 0, amp = 1.6, a0 = 0, a1 = Math.PI * 2, steps = 0 } = {}) {
  let sweep = a1 - a0;
  if (sweep >= Math.PI * 2 - 0.01) sweep = Math.PI * 2 + 0.07; // 整圆接缝重叠，避免 12 点缺口
  const n = steps || Math.max(24, Math.floor(r * 0.9 * Math.abs(sweep) / (Math.PI * 2) + 24));
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const a = a0 + sweep * i / n;
    pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]);
  }
  inkLine(ctx, pts, { seed, amp, segs: 1 });
}

/* ---------- 文字 ---------- */
function fontOf(px, weight = '', family = '"KaiTi","STKaiti","Microsoft YaHei",serif') {
  return `${weight} ${px}px ${family}`;
}
// 手写浮现：逐字透明度+轻微上移（write-on 而非整块闪现）
function writeText(ctx, str, x, y, px, { t = 1, color = PAL.ink, weight = '', align = 'left', family, charDelay = 0.045, bob = 0 } = {}) {
  ctx.save();
  ctx.font = fontOf(px, weight, family);
  ctx.textAlign = align; ctx.textBaseline = 'middle';
  const chars = [...str];
  const total = chars.length * charDelay;
  const shown = clamp01(t) * total;
  let cx = x;
  if (align === 'center') cx = x - ctx.measureText(str).width / 2;
  if (align === 'right') cx = x - ctx.measureText(str).width;
  chars.forEach((ch, i) => {
    const a = clamp01(shown - i * charDelay);
    if (a <= 0) return;
    ctx.globalAlpha = a;
    const w = ctx.measureText(ch).width;
    ctx.fillStyle = color;
    const dy = (1 - easeOut(a)) * 8;
    ctx.fillText(ch, cx + w / 2, y + dy + Math.sin(i * 1.3 + bob) * 0.6);
    cx += w;
  });
  ctx.restore();
}

/* ---------- 通用装饰 ---------- */
// 纸面微颗粒（静态，hash 网格）
let _grain = null;
function paperGrain(ctx) {
  if (!_grain) {
    const c = document.createElement('canvas'); c.width = 480; c.height = 270;
    const g = c.getContext('2d');
    const img = g.createImageData(480, 270);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = 24 + hash(i / 4 | 0) * 14;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    _grain = c;
  }
  ctx.save();
  ctx.globalAlpha = 0.05;
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(_grain, 0, 0, 1920, 1080);
  ctx.restore();
}

function bgWash(ctx) {
  const g = ctx.createLinearGradient(0, 0, 0, 1080);
  g.addColorStop(0, PAL.bg1); g.addColorStop(1, PAL.bg0);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 1920, 1080);
}
