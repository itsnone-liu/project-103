// web2d_capture.mjs — BAC WEB_2D 帧捕获器（pipeline/adapters/）。
// 契约：目标 index.html 暴露 window.P103 = { duration, fps, width, height, renderFrame(t)->truthy }。
// 双通道错误（KP-003）：exit code + errors.json（console error / pageerror / renderFrame 异常 + 帧号）。
import puppeteer from 'puppeteer-core';
import { mkdirSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const argv = Object.fromEntries(process.argv.slice(2).map(a => { const [k, v] = a.replace(/^--/, '').split('='); return [k, v ?? true]; }));
const CHROMES = [argv.chrome, process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  '/usr/bin/google-chrome', '/usr/bin/chromium'];
const CHROME = CHROMES.find(p => p && existsSync(p));
if (!CHROME) { console.error('Chrome not found: --chrome=<path> or CHROME_PATH'); process.exit(2); }

const html = resolve(argv.html), outDir = resolve(argv.out || 'frames');
const fps = argv.fps ? +argv.fps : 24;
rmSync(outDir, { recursive: true, force: true });            // KP-008：渲染前清空
mkdirSync(outDir, { recursive: true });

const errors = [];
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: +argv.width || 1920, height: +argv.height || 1080 });
  page.on('pageerror', e => errors.push({ kind: 'pageerror', message: String(e) }));
  page.on('console', m => { if (m.type() === 'error') errors.push({ kind: 'console', message: m.text().slice(0, 300) }); });
  await page.goto('file:///' + html.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 30000 });
  await page.waitForFunction('window.P103 && typeof window.P103.renderFrame === "function"', { timeout: 15000 });

  const spec = await page.evaluate(() => ({ ...window.P103, renderFrame: null }));
  const duration = argv.duration ? +argv.duration : (spec.duration || 0);
  if (!duration || duration <= 0) throw new Error('P103.duration 缺失/非法');
  const fpsEff = spec.fps || fps, w = spec.width || 1920, h = spec.height || 1080;
  const n = Math.max(1, Math.round(duration * fpsEff));

  for (let i = 0; i < n; i++) {
    const t = i / fpsEff;
    let ok;
    try { ok = await page.evaluate(tt => window.P103.renderFrame(tt), t); }
    catch (e) { errors.push({ kind: 'renderFrame', frame: i, t, message: String(e).slice(0, 300) }); ok = false; }
    if (!ok && ok !== false) { errors.push({ kind: 'contract', frame: i, message: 'renderFrame 未返回真值' }); }
    await page.screenshot({ path: `${outDir}/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92,
      clip: { x: 0, y: 0, width: w, height: h } });
    if (i % 48 === 0) console.log(`frame ${i}/${n} t=${t.toFixed(2)}s`);
  }
  console.log(`captured ${n} frames (${duration}s @ ${fpsEff}fps ${w}x${h})`);
} finally {
  await browser.close();
}
writeFileSync(`${outDir}/../capture_errors.json`, JSON.stringify(errors, null, 1));
if (errors.length) { console.error(`ERRORS: ${errors.length} 条（见 capture_errors.json）`); process.exit(1); }
console.log('capture OK');
