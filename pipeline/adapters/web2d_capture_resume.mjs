// web2d_capture_resume.mjs — WEB_2D 断点续捕器（pipeline/adapters/）。
// 用途：确定性候选的长片渲染超过 web2d_capture.mjs 的 1800s 子进程超时被杀后，
//       不重捕全片：数出 out 目录中连续存在的 fNNNNN.jpg 前缀数，只补缺失后缀。
// 前提：候选 renderFrame(t) 完全确定（无随机/无前帧依赖），同一 HTML 重开页面能逐帧复现。
// 与 web2d_capture.mjs 的差异：不清空 out（ KP-008 反向）、--duration 缺省读页面契约、
//       错误写入同目录 capture_resume_errors.json（不覆盖主捕的 capture_errors.json）。
// 用法：node web2d_capture_resume.mjs --html=<path> --out=<framesDir> [--duration=<s>] [--fps=24]
import puppeteer from 'puppeteer-core';
import { mkdirSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';

const argv = Object.fromEntries(process.argv.slice(2).map(a => { const [k, v] = a.replace(/^--/, '').split('='); return [k, v ?? true]; }));
const CHROMES = [argv.chrome, process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  '/usr/bin/google-chrome', '/usr/bin/chromium'];
const CHROME = CHROMES.find(p => p && existsSync(p));
if (!CHROME) { console.error('Chrome not found: --chrome=<path> or CHROME_PATH'); process.exit(2); }
if (!argv.html) { console.error('usage: --html=<index.html> --out=<framesDir> [--duration=<s>] [--fps=24]'); process.exit(2); }

const html = resolve(argv.html), outDir = resolve(argv.out || 'frames');
mkdirSync(outDir, { recursive: true });

const errors = [];
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'] });
try {
  const page = await browser.newPage();
  const W = +argv.width || 1920, H = +argv.height || 1080;
  await page.setViewport({ width: W, height: H });
  page.on('pageerror', e => errors.push({ kind: 'pageerror', message: String(e) }));
  page.on('console', m => { if (m.type() === 'error') errors.push({ kind: 'console', message: m.text().slice(0, 300) }); });
  await page.goto('file:///' + html.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 30000 });
  await page.waitForFunction('window.P103', { timeout: 15000 });
  const spec = await page.evaluate(() => ({ duration: P103.duration, fps: P103.fps, width: P103.width, height: P103.height }));
  const fps = argv.fps ? +argv.fps : (Number(spec.fps) || 24);
  const duration = argv.duration ? +argv.duration : Number(spec.duration);
  const n = Math.ceil(duration * fps);
  if (spec.width !== W || spec.height !== H) throw new Error(`viewport mismatch page=${spec.width}x${spec.height} args=${W}x${H}`);
  if (argv.duration && Math.abs(spec.duration - duration) > 0.001)
    throw new Error(`duration mismatch page=${spec.duration} arg=${duration}`);
  await page.addStyleTag({ content: `html,body{width:${W}px!important;height:${H}px!important;margin:0!important;overflow:hidden!important} canvas{position:absolute!important;left:0!important;top:0!important;width:${W}px!important;height:${H}px!important}` });

  const present = new Set(readdirSync(outDir).filter(x => /^f\d{5}\.jpg$/.test(x)).map(x => Number(x.slice(1, 6))));
  let contiguous = 0; while (present.has(contiguous)) contiguous++;
  console.log(`resume at ${contiguous}/${n}, existing=${present.size}, duration=${duration}s fps=${fps}`);
  if (contiguous >= n) { console.log('nothing to do: all frames present'); }

  for (let i = contiguous; i < n; i++) {
    let ok = false;
    try { ok = await page.evaluate(t => window.P103.renderFrame(t), i / fps); }
    catch (e) { errors.push({ kind: 'renderFrame', frame: i, t: i / fps, message: String(e).slice(0, 300) }); break; }
    if (!ok) { errors.push({ kind: 'contract', frame: i, message: 'renderFrame 未返回真值' }); break; }
    await page.screenshot({ path: join(outDir, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 88, clip: { x: 0, y: 0, width: W, height: H } });
    if (i % 240 === 0) console.log(`frame ${i}/${n} t=${(i / fps).toFixed(1)} errors=${errors.length}`);
  }
  writeFileSync(join(outDir, '..', 'capture_resume_errors.json'), JSON.stringify(errors, null, 2));
  const now = readdirSync(outDir).filter(x => /^f\d{5}\.jpg$/.test(x)).length;
  console.log(`resume done; frames now ${now}/${n}; errors=${errors.length}`);
  if (errors.length) process.exitCode = 1;
} finally { await browser.close(); }
