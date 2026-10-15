// _rerender_range.mjs — 只重捕指定帧号区间的已渲染序列（同帧号覆盖）。
// 用法: node _rerender_range.mjs <html> <framesDir> <fromFrame> <toFrameExclusive>
import puppeteer from 'puppeteer-core';
import { readdirSync } from 'node:fs';
import { resolve, join } from 'node:path';

const [html, outDir, fromS, toS] = [resolve(process.argv[2]), resolve(process.argv[3]), +process.argv[4], +process.argv[5]];
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto('file:///' + html.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 30000 });
  await page.waitForFunction('window.P103', { timeout: 15000 });
  await page.addStyleTag({ content: 'html,body{width:1920px!important;height:1080px!important;margin:0!important;overflow:hidden!important} canvas{position:absolute!important;left:0!important;top:0!important;width:1920px!important;height:1080px!important}' });
  let done = 0, bad = 0;
  for (let i = fromS; i < toS; i++) {
    const ok = await page.evaluate(t => window.P103.renderFrame(t), i / 24);
    if (!ok) { bad++; continue; }
    await page.screenshot({ path: join(outDir, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 88, clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    done++;
  }
  const total = readdirSync(outDir).filter(x => /^f\d{5}\.jpg$/.test(x)).length;
  console.log(`rerendered ${done} frames [${fromS},${toS}), bad=${bad}, dir total=${total}`);
} finally { await browser.close(); }
