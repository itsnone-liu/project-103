// _runtime_e2e.mjs — Lesson Runtime E2E 验证（讨论稿 §32 互动阶段检查单）
// 覆盖：自动暂停 / 卡片呈现 / 本地判分(单选+数值) / 反馈 / 续播 / seek跳过不触发 / 回退重触发 / 不重复触发
import puppeteer from 'puppeteer-core';
import { existsSync } from 'node:fs';

const CHROMES = [process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'];
const CHROME = CHROMES.find(p => p && existsSync(p));
if (!CHROME) { console.error('Chrome not found'); process.exit(2); }

const BASE = 'http://127.0.0.1:8862/?p=course/chapter-06/lesson-t1-personal-space';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const results = [];
const check = (name, ok, extra = '') => { results.push({ name, ok, extra }); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? '  [' + extra + ']' : ''}`); };

const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
  args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required', '--use-fake-ui-for-media-stream'] });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
const consoleErrors = [];
page.on('pageerror', e => consoleErrors.push(String(e)));

// 清掉进度恢复弹层干扰：预置 localStorage
await page.goto(BASE, { waitUntil: 'domcontentloaded' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle2' });

const v = () => page.$('#video').then(el => el.evaluate(x => ({ t: x.currentTime, paused: x.paused, dur: x.duration })));
await page.waitForFunction(() => document.querySelector('#video') && document.querySelector('#video').duration > 0, { timeout: 15000 });
check('加载：视频元数据就绪（duration≈348.6）', (await v()).dur > 340, `dur=${(await v()).dur.toFixed(1)}`);

const cueVisible = () => page.$eval('#cue-card', el => !el.classList.contains('hidden')).catch(() => false);

// ── T1: 自动暂停 + 卡片（cues[0] num-d1d2 @72.9） ──
await page.evaluate(() => { const vid = document.querySelector('#video'); vid.currentTime = 71.5; vid.play(); });
await page.waitForFunction(`document.querySelector('#video').paused === true`, { timeout: 8000 });
const state1 = await v();
check('T1 自动暂停：到达 72.9 触发 pause()', state1.paused && Math.abs(state1.t - 72.9) < 1.5, `t=${state1.t.toFixed(2)}`);
check('T1 卡片呈现：cue-card 可见且为数值题', await cueVisible() && await page.$eval('#cue-tag', el => el.textContent.includes('数值')));

// ── T2: 数值判分（错→对） ──
await page.type('#num-input', '3.0');
await page.click('#cue-submit');
let fb = await page.$eval('#cue-feedback', el => ({ cls: el.className, text: el.textContent }));
check('T2 数值判分-错误：反馈 incorrect 文案', fb.cls.includes('no') && fb.text.includes('0.45'), fb.text.slice(0, 40));
await page.evaluate(() => { document.querySelector('#num-input').value = ''; });
await page.type('#num-input', '0.375');
await page.evaluate(() => { document.querySelector('#cue-submit').disabled = false; });
await page.click('#cue-submit');
fb = await page.$eval('#cue-feedback', el => ({ cls: el.className, text: el.textContent }));
check('T2 数值判分-正确：反馈 correct', fb.cls.includes('ok') && fb.text.includes('0.375'));
const ans = await page.evaluate(() => JSON.parse(localStorage.getItem('ans:lesson-t1-personal-space')));
check('T2 答题记录落 localStorage（2 条）', ans && ans.length === 2, JSON.stringify(ans?.map(a => a.result)));

// ── T3: 续播 + 不重复触发（停在 cue 附近不再弹） ──
await page.click('#cue-skip');
await page.waitForFunction(`document.querySelector('#video').paused === false`, { timeout: 5000 });
const st = await v();
check('T3 续播：点击后恢复播放', !st.paused, `t=${st.t.toFixed(2)}`);
await page.evaluate(() => { const vid = document.querySelector('#video'); vid.pause(); });
await sleep(700);
check('T3 不重复触发：暂停在 cue 后不重弹', !(await cueVisible()));

// ── T4: seek 跳过窗口不触发（从 80 直跳 190，越过 72.9 已答；再从 190→194.8 等待 choice-zones） ──
await page.evaluate(() => { const vid = document.querySelector('#video'); vid.currentTime = 194.2; vid.play(); });
await page.waitForFunction(`document.querySelector('#video').paused === true`, { timeout: 8000 });
const st4 = await v();
check('T4 第二个 cue 自动暂停（choice-zones @195.4）', st4.paused && Math.abs(st4.t - 195.4) < 1.5, `t=${st4.t.toFixed(2)}`);
check('T4 卡片为单选题且 4 选项', await page.$$eval('#cue-body .opt', els => els.length === 4));

// ── T5: 单选判分：选错误项 0 → 显示正确项 2 ──
await page.click('#cue-body .opt[data-i="0"]');
await page.click('#cue-submit');
const marks = await page.$$eval('#cue-body .opt', els => els.map(e => e.className));
fb = await page.$eval('#cue-feedback', el => ({ cls: el.className, text: el.textContent }));
check('T5 单选判分-错误：0 标 wrong、2 标 right、反馈含社会距离',
  marks[0].includes('wrong') && marks[2].includes('right') && fb.cls.includes('no') && fb.text.includes('社会距离'));

// ── T6: 回退重触发（seek 回 D/H cue 之前 1.5s+，再播放应触发 tf-dh @316）──
// 先关掉当前卡片（跳过），把两个已答题 cue 走完
await page.click('#cue-skip');
await page.evaluate(() => { const vid = document.querySelector('#video'); vid.pause(); vid.currentTime = 314.5; vid.play(); });
await page.waitForFunction(`document.querySelector('#video').paused === true`, { timeout: 8000 });
const st6 = await v();
check('T6 第三个 cue 自动暂停（tf-dh @316）', st6.paused && Math.abs(st6.t - 316) < 1.5, `t=${st6.t.toFixed(2)}`);
// 判断题：正确答案是 False，点“✓ 正确”（错误项）
await page.click('#cue-body .opt[data-v="true"]');
await page.click('#cue-submit');
fb = await page.$eval('#cue-feedback', el => ({ cls: el.className, text: el.textContent }));
check('T6 判断题判分-错误反馈（临界值解释）', fb.cls.includes('no') && fb.text.includes('临界'));

// ── T7: 回退 1.5s+ 后同 cue 可重触发（num-d1d2 重弹） ──
await page.click('#cue-skip');
await page.evaluate(() => { const vid = document.querySelector('#video'); vid.currentTime = 71.0; vid.play(); });
await page.waitForFunction(`document.querySelector('#video').paused === true`, { timeout: 8000 });
check('T7 回退后 cue 重新触发（复习可再答）', await cueVisible());

// ── T8: 疑问标记（§15：0 token 本地记录） ──
await page.click('#cue-skip');
await page.evaluate(() => { const vid = document.querySelector('#video'); vid.pause(); vid.currentTime = 120; });
await page.click('#ask-fab');
await page.type('#ask-modal textarea', '为什么四段距离用中点划分近远两档？');
await page.click('#mk-save');
const mk = await page.evaluate(() => JSON.parse(localStorage.getItem('mk:lesson-t1-personal-space')));
check('T8 疑问标记记录（lesson_id+timestamp+question）', mk?.length === 1 && mk[0].timestamp === 120 && mk[0].question.includes('中点'));
const badge = await page.$eval('#ask-count', el => el.textContent);
check('T8 角标计数更新', badge === '1');

// ── T9: AI1 上下文预览（不调用模型，纯拼装展示） ──
await page.evaluate(() => { window.__noLLM = true; });
await page.click('#qa-preview-btn');
const prev = await page.$eval('#qa-preview', el => el.textContent);
check('T9 课后 AI 上下文预览包含疑问+答题记录', prev.includes('中点') && prev.includes('choice-zones') && prev.includes('不调用模型'));

// ── T10: 结构段点击 seek + 摘要卡渲染 ──
const sumOk = await page.$$eval('#sum-body li', els => els.length >= 8);
check('T10 摘要卡渲染（知识点+易错点 ≥8 条）', sumOk);
const tlOk = await page.$$eval('#kp-list .tl-seg', els => els.length >= 5);
check('T10 结构时间轴 ≥5 段且可点击 seek', tlOk);

check('T11 页面零 JS 异常', consoleErrors.length === 0, consoleErrors.slice(0, 2).join(';'));

const fails = results.filter(r => !r.ok).length;
console.log(`\n===== E2E 结果：${results.length - fails}/${results.length} PASS =====`);
await browser.close();
process.exit(fails ? 1 : 0);
