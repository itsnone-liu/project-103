// keyframes.mjs — 关键时点快照探针（章节构图自查 + 错误检查）
// 用法: node keyframes.mjs --html=<abs> --out=<abs> --times=6,10,17,25,31,36,42,48,53,58,63
import puppeteer from 'puppeteer-core';
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const argv = Object.fromEntries(process.argv.slice(2).map(a => { const [k, v] = a.replace(/^--/, '').split('='); return [k, v ?? true]; }));
const CHROMES = [argv.chrome, process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'];
const CHROME = CHROMES.find(p => p && existsSync(p));
if (!CHROME) { console.error('Chrome not found'); process.exit(2); }

const html = resolve(argv.html), outDir = resolve(argv.out || 'keyframes');
mkdirSync(outDir, { recursive: true });
const times = (argv.times || '6,10,17,25,31,36,42,48,53,58,63').split(',').map(Number);

const errors = [];
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox', '--force-device-scale-factor=1'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  page.on('pageerror', e => errors.push({ kind: 'pageerror', message: String(e) }));
  page.on('console', m => { if (m.type() === 'error') errors.push({ kind: 'console', message: m.text().slice(0, 300) }); });
  await page.goto('file:///' + html.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 30000 });
  await page.waitForFunction('window.P103 && typeof window.P103.renderFrame === "function"', { timeout: 15000 });
  for (const t of times) {
    let ok;
    try { ok = await page.evaluate(tt => window.P103.renderFrame(tt), t); }
    catch (e) { errors.push({ kind: 'renderFrame', t, message: String(e).slice(0, 400) }); ok = false; }
    await page.screenshot({ path: `${outDir}/kf_t${t}.jpg`, type: 'jpeg', quality: 90, clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    console.log(`t=${t} ok=${!!ok}`);
  }
} finally { await browser.close(); }
writeFileSync(`${outDir}/keyframe_errors.json`, JSON.stringify(errors, null, 1));
console.log(errors.length ? `ERRORS: ${errors.length}` : 'keyframes OK');
if (errors.length) process.exit(1);
