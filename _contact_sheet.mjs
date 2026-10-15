// _contact_sheet.mjs — 48 cue stills → 6x8 contact sheet (JPEG).
// 用法: node _contact_sheet.mjs <dirWithSheet_XX.jpg> <out.jpg>
// 原因: remotion compositor ffmpeg 无 tile 滤镜，改用纯 Node 拼装
// (baseline JPEG 解码：全 480x270 灰底 + 每格右下角行号由文件名序保证，不写文字)。
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const dir = path.resolve(process.argv[2]);
const out = path.resolve(process.argv[3]);
const files = readdirSync(dir).filter(f => /^sheet_\d{2}\.jpg$/.test(f)).sort();
const N = files.length;
if (![39, 48].includes(N)) throw new Error(`unexpected still count ${N}`);
const COLS = 6, ROWS = Math.ceil(N / COLS);

// 读取每张的宽高（JPEG SOF0/SOF2 扫描）
function jpegSize(buf) {
  let i = 2;
  while (i < buf.length) {
    if (buf[i] !== 0xFF) { i++; continue; }
    const m = buf[i + 1];
    if (m >= 0xC0 && m <= 0xCF && m !== 0xC4 && m !== 0xC8 && m !== 0xCC) {
      return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7) };
    }
    i += 2 + buf.readUInt16BE(i + 2);
  }
  throw new Error('no SOF');
}
const { w: TW, h: TH } = jpegSize(readFileSync(path.join(dir, files[0])));
const CW = 480, CH = 270, PAD = 3;
const W = COLS * CW + (COLS + 1) * PAD, H = ROWS * CH + (ROWS + 1) * PAD;

// ---- 最小基线 JPEG 编码器（灰度已不行——需要彩色缩略。改用策略：
// 不解码！直接把每张 480x270 JPEG 原样嵌入 PNG容器? 不可行。
// 方案B：调用 Chrome(puppeteer) 渲染 <img> 网格截图 —— 管线内已有 puppeteer-core。----
import puppeteer from 'puppeteer-core';
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body{margin:0;background:#101b29;font-family:sans-serif}
.grid{display:grid;grid-template-columns:repeat(6,480px);gap:3px;padding:3px;width:${W}px}
.cell{position:relative;width:480px;height:270px;background:#0c1724}
.cell img{width:480px;height:270px;object-fit:cover;display:block}
.cell .n{position:absolute;right:6px;bottom:4px;font-size:20px;color:#fff;background:rgba(12,23,36,.75);padding:1px 8px;border-radius:4px}
</style></head><body><div class="grid">${files.map((f, i) =>
  `<div class="cell"><img src="file:///${path.join(dir, f).replace(/\\/g, '/')}"><span class="n">${i + 1}</span></div>`).join('')}</div></body></html>`;
const htmlPath = path.join(dir, '_sheet.html');
writeFileSync(htmlPath, html, 'utf-8');
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H });
  await page.goto('file:///' + htmlPath.replace(/\\/g, '/'), { waitUntil: 'networkidle0', timeout: 30000 });
  await page.screenshot({ path: out, type: 'jpeg', quality: 82, clip: { x: 0, y: 0, width: W, height: H } });
  console.log('sheet:', out, `${W}x${H}`);
} finally { await browser.close(); }
