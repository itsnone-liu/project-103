// 实测 index.html 在多个时间点的画面差异
import puppeteer from 'puppeteer-core';
import { writeFileSync } from 'node:fs';

const html = process.argv[2].replace(/\\/g, '/');
const times = [5, 50, 100, 154, 200, 300, 350];
const browser = await puppeteer.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage'],
});
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  page.on('pageerror', e => console.log(`[pageerror] ${String(e).slice(0, 150)}`));
  await page.goto('file:///' + html, { waitUntil: 'load', timeout: 30000 });
  await page.waitForFunction('window.P103 || window.__P103__ || window.__WEB2D__ || window.web2d || window.__animation || window.renderFrame', { timeout: 15000 });
  await page.evaluate(() => {
    if (!window.P103) {
      const api = window.__P103__ || window.__WEB2D__ || window.web2d || window.__animation || {};
      const rf = typeof api.renderFrame === 'function' ? api.renderFrame.bind(api) : window.renderFrame;
      window.P103 = Object.assign({}, api, { renderFrame: (...a) => { const r = rf && rf(...a); return r ? r : true; } });
    }
    const P = window.P103;
    const fps = (P && Number(P.fps)) || 24;
    const raw = P.renderFrame.bind(P);
    let pr = NaN;
    try { const r = raw(1); pr = r && typeof r === 'object' ? Number(r.time) : Number(r); } catch (e) { pr = NaN; }
    if (Number.isFinite(pr) && Math.abs(pr - 1) > 0.05 && Math.abs(pr - 1 / fps) < 0.02) {
      window.P103.renderFrame = (t) => { const r = raw(t * fps); return r ? r : true; };
      window.__P103_FRAME_SEMANTICS__ = true;
    }
  });
  console.log('frame_semantics bridged:', await page.evaluate(() => !!window.__P103_FRAME_SEMANTICS__));
  for (const t of times) {
    const r = await page.evaluate(tt => window.P103.renderFrame(tt), t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 80 });
    writeFileSync(`${process.env.TEMP.replace(/\\/g, '/')}/sc_t${String(t).padStart(3, '0')}.jpg`, buf);
    console.log(`t=${t}s ret=${JSON.stringify(r).slice(0, 60)}`);
  }
} finally { await browser.close(); }
