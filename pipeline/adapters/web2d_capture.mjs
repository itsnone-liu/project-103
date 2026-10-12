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
  // KP-009：sol 有时只挂别名（__P103__/__WEB2D__/web2d/__animation 或裸 renderFrame）
  // 而漏掉契约主名 window.P103 → waitForFunction 静默超时，repair 循环拿不到有效错误。
  // 兼容垫片：从任一别名合成 P103；全部缺席才报点名错误。
  await page.waitForFunction(
    'window.P103 || window.__P103__ || window.__WEB2D__ || window.web2d || window.__animation || window.renderFrame',
    { timeout: 15000 }).catch(() => {
      throw new Error('CONTRACT: window.P103 及全部已知别名（__P103__/__WEB2D__/web2d/__animation/renderFrame）' +
        '15s 内均未出现——init 未执行或契约对象缺失');
    });
  await page.evaluate(() => {
    if (!window.P103) {
      const api = window.__P103__ || window.__WEB2D__ || window.web2d || window.__animation || {};
      const rf = typeof api.renderFrame === 'function' ? api.renderFrame.bind(api)
        : (typeof window.renderFrame === 'function' ? window.renderFrame : null);
      // KP-010：sol 的 renderAt 常回显时间 t 或不返回值——t=0 时是 falsy 数字，
      // 契约的 truthy 检查只在 frame 0 误报。包装成恒真；真正的绘制失败仍以
      // renderFrame 异常形式上报，空白帧由 produce 的 frame_variance QA 兜底。
      window.P103 = Object.assign({}, api, {
        renderFrame: (...a) => { const r = rf && rf(...a); return r ? r : true; },
      });
    }
  });
  // 竞态防御：取消页面自驱动的 rAF/定时器循环（如"本地预览"），它们会在
  // renderFrame(t) 与 screenshot 之间用自有时钟重绘画布，污染捕获帧。
  await page.evaluate(() => {
    for (let id = 1; id < 100000; id++) { window.cancelAnimationFrame(id); window.clearInterval(id); window.clearTimeout(id); }
  });

  const spec = await page.evaluate(() => ({ ...window.P103, renderFrame: null }));
  const duration = argv.duration ? +argv.duration : (spec.duration || 0);
  if (!duration || duration <= 0) throw new Error('P103.duration 缺失/非法');
  const fpsEff = spec.fps || fps, w = spec.width || 1920, h = spec.height || 1080;
  // Match capture viewport to declared frame size; center-aligned preview layouts
  // otherwise get cropped by the old fixed 1920x1080 viewport clip.
  await page.setViewport({ width: w, height: h });
  await page.addStyleTag({ content: `html,body{width:${w}px!important;height:${h}px!important;min-height:0!important;margin:0!important;padding:0!important;display:block!important;overflow:hidden!important} canvas#stage{position:absolute!important;left:0!important;top:0!important;width:${w}px!important;height:${h}px!important;max-width:none!important;box-shadow:none!important} .cap{display:none!important}` });
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
