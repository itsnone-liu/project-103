// _probe_frame.mjs — 加载 html，渲染指定 t，回读 canvas 像素 + 落一张 PNG
import puppeteer from 'puppeteer-core';
import { resolve } from 'node:path';

const html = resolve(process.argv[2]);
const t = +process.argv[3];
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto('file:///' + html.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 30000 });
  await page.waitForFunction('window.P103', { timeout: 15000 });
  const r = await page.evaluate((tt) => {
    window.P103.renderFrame(tt);
    const cv = document.querySelector('canvas');
    const c2 = cv.getContext('2d');
    const px = (x, y) => Array.from(c2.getImageData(x, y, 1, 1).data).slice(0, 3).join(',');
    return { glow: px(740, 713), near: px(760, 700), topright: px(1800, 80), far: px(200, 150), cw: cv.width, ch: cv.height };
  }, t);
  console.log(JSON.stringify(r));
} finally { await browser.close(); }
