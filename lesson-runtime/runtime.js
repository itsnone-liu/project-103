/* Web Lesson Runtime MVP —— 讨论稿 Phase I1 + I2-lite + I4
 * 1 套 Runtime + N 个 Lesson Package（?p=course/chapter-xx/lesson-id）
 * 播放全程 0 token：判分/摘要/进度/疑问标记全部本地。LLM 仅 Phase AI1（此处只做上下文预览，不调用）。
 */
"use strict";
const $ = (s) => document.querySelector(s);
const qs = new URLSearchParams(location.search);
const PKG = qs.get("p") || "course/chapter-06/lesson-t1-personal-space";
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { localStorage.setItem(k, JSON.stringify(v)); },
};
const fmt = (t) => `${String(Math.floor(t / 60)).padStart(2, "0")}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

let course, lesson, interactions, summary;
let cues = [], firedSet = new Set();
let answers = [];   // 答题历史（供 AI1 上下文）
let markers = [];   // 疑问标记（§15：不调 LLM）
const video = $("#video");

async function jget(p) { const r = await fetch(p); if (!r.ok) throw new Error(p + " " + r.status); return r.json(); }

async function init() {
  course = await jget("course/course.json");
  lesson = await jget(`${PKG}/lesson.json`);
  interactions = await jget(`${PKG}/interactions.json`).catch(() => ({ cues: [] }));
  summary = await jget(`${PKG}/summary.json`).catch(() => null);
  cues = interactions.cues || [];
  answers = store.get(`ans:${lesson.lesson_id}`, []);
  markers = store.get(`mk:${lesson.lesson_id}`, []);

  document.title = `${lesson.title} · ${course.title}`;
  $("#course-title").textContent = course.title;
  const ch = course.chapters.find((c) => c.chapter_id === lesson.chapter_id);
  $("#chapter-title").textContent = ch ? ch.title : lesson.chapter_id;
  $("#lesson-title").textContent = lesson.title;

  video.src = `${PKG}/${lesson.video}`;
  const tr = document.createElement("track");
  tr.src = `${PKG}/${lesson.transcript}`; tr.kind = "subtitles"; tr.srclang = "zh"; tr.label = "中文"; tr.default = true;
  video.appendChild(tr);

  $("#video-meta").innerHTML =
    `<span>⏱ ${Math.round(lesson.duration)}s</span><span>🎯 ${cues.length} 个互动点</span>` +
    `<span>📝 ${lesson.knowledge_points.length} 个知识点</span><span class="dim">schema ${lesson.schema}</span>`;

  buildTimeline(); buildKP(); buildSummary(); renderAnswers(); renderMarkers();
  wireCueCard(); wireAsk(); wireNav(); wireProgress();
  restoreProgress();
}

/* ── 时间轴条：结构段 + cue 刻度（点击 seek） ── */
function buildTimeline() {
  const bar = $("#timeline-bar");
  const segs = lesson.timeline || [];
  bar.innerHTML = segs.map((s) =>
    `<i data-s="${s.start}" data-e="${s.end}" style="left:${(s.start / lesson.duration) * 100}%;width:${((s.end - s.start) / lesson.duration) * 100}%"></i>`).join("") +
    cues.map((c) => `<b data-t="${c.time}" style="left:${(c.time / lesson.duration) * 100}%" title="${c.id}"></b>`).join("");
  bar.onclick = (e) => { const el = e.target.closest("[data-s],[data-t]"); if (el) video.currentTime = +(el.dataset.t || el.dataset.s); };
}
function buildKP() {
  $("#kp-list").innerHTML = (lesson.timeline || []).map((s) =>
    `<div class="tl-seg" data-t="${s.start}"><span class="tl-time">${fmt(s.start)}</span><span class="tl-type">${{intro:"引入",concept:"概念",example:"例题",application:"应用",summary:"小结"}[s.type] || s.type}</span><span class="tl-topic">${s.topic || ""}</span></div>`).join("");
  $("#kp-list").onclick = (e) => { const el = e.target.closest("[data-t]"); if (el) video.currentTime = +el.dataset.t; };
  $("#kp-points").innerHTML = lesson.knowledge_points.map((k) => `<span class="chip">${k}</span>`).join("");
}
function buildSummary() {
  if (!summary) { $("#sum-card").classList.add("hidden"); return; }
  const li = (a) => a.map((x) => `<li>${x}</li>`).join("");
  $("#sum-body").innerHTML =
    `<b style="color:var(--gold)">知识点</b><ul>${li(summary.knowledge_points)}</ul>` +
    `<b style="color:var(--red)">易错点</b><ul>${li(summary.common_mistakes)}</ul>` +
    `<b style="color:var(--teal)">下一课衔接</b><p>${summary.next_lesson}</p>`;
}

/* ── Cue 引擎（§3.1 / §32：不重复触发；回退 1.5s+ 才重置；seek 跳过窗口不触发） ── */
let activeCue = null;
video.addEventListener("timeupdate", () => {
  const t = video.currentTime;
  for (const c of cues) if (firedSet.has(c.id) && t < c.time - 1.5) firedSet.delete(c.id);
  if (video.paused || activeCue) return;
  const hit = cues.find((c) => !firedSet.has(c.id) && t >= c.time && t < c.time + 2.5);
  if (hit) { firedSet.add(hit.id); if (hit.pause !== false) { video.pause(); showCue(hit); } }
});
function showCue(c) {
  activeCue = c; $("#cue-card").classList.remove("hidden");
  $("#cue-card").scrollIntoView({ behavior: "smooth", block: "nearest" });
  $("#cue-q").textContent = c.question;
  $("#cue-feedback").className = ""; $("#cue-feedback").textContent = "";
  $("#cue-submit").disabled = false;
  const body = $("#cue-body");
  const typeNames = { single_choice: "单选", multiple_choice: "多选", true_false: "判断", short_numeric: "数值" };
  $("#cue-tag").textContent = `互动 · ${typeNames[c.type]} · ${fmt(c.time)}`;
  if (c.type === "single_choice" || c.type === "multiple_choice") {
    const multi = c.type === "multiple_choice";
    body.innerHTML = c.options.map((o, i) => `<button class="opt" data-i="${i}">${multi ? "□ " : ""}${o}</button>`).join("");
    body.querySelectorAll(".opt").forEach((b) => b.onclick = () => {
      if (multi) { b.classList.toggle("sel"); b.textContent = (b.classList.contains("sel") ? "☑ " : "□ ") + c.options[+b.dataset.i]; }
      else { body.querySelectorAll(".opt").forEach((x) => x.classList.remove("sel")); b.classList.add("sel"); }
    });
  } else if (c.type === "true_false") {
    body.innerHTML = `<div class="tf-row"><button class="opt" data-v="true">✓ 正确</button><button class="opt" data-v="false">✗ 错误</button></div>`;
    body.querySelectorAll(".opt").forEach((b) => b.onclick = () => { body.querySelectorAll(".opt").forEach((x) => x.classList.remove("sel")); b.classList.add("sel"); });
  } else {
    body.innerHTML = `<input id="num-input" type="text" inputmode="decimal" placeholder="输入数值${c.unit ? "（" + c.unit + "）" : ""}">`;
  }
  $("#cue-submit").onclick = () => judge(c);
  $("#cue-skip").onclick = () => { recordAnswer(c, null, "skipped"); closeCue(true); };
}
function judge(c) {
  let picked = null, ok = false;
  if (c.type === "single_choice") {
    const sel = $("#cue-body .opt.sel"); if (!sel) return toast("先选择一项");
    picked = +sel.dataset.i; ok = picked === c.correct;
    document.querySelectorAll("#cue-body .opt").forEach((b, i) => { if (i === c.correct) b.classList.add("right"); else if (+b.dataset.i === picked) b.classList.add("wrong"); });
  } else if (c.type === "multiple_choice") {
    picked = [...$("#cue-body .opt.sel")].map((b) => +b.dataset.i);
    if (!picked.length) return toast("至少选择一项");
    ok = picked.length === c.correct.length && c.correct.every((x) => picked.includes(x));
  } else if (c.type === "true_false") {
    const sel = $("#cue-body .opt.sel"); if (!sel) return toast("先做个判断");
    picked = sel.dataset.v === "true"; ok = picked === c.correct;
    document.querySelectorAll("#cue-body .opt").forEach((b) => { if ((b.dataset.v === "true") === c.correct) b.classList.add("right"); else if (b.classList.contains("sel")) b.classList.add("wrong"); });
  } else {
    const raw = $("#num-input").value.trim().replace("，", ".");
    if (!raw) return toast("输入数值");
    picked = parseFloat(raw); ok = Math.abs(picked - c.answer) <= (c.tolerance ?? 1e-9);
  }
  const fb = $("#cue-feedback");
  fb.className = ok ? "ok" : "no";
  fb.textContent = (ok ? "✓ " : "✗ ") + c.feedback[ok ? "correct" : "incorrect"];
  $("#cue-submit").disabled = true;
  recordAnswer(c, picked, ok ? "correct" : "wrong");
}
function closeCue(resume) { activeCue = null; $("#cue-card").classList.add("hidden"); if (resume) video.play(); }
function wireCueCard() { }

function recordAnswer(c, picked, result) {
  answers.push({ id: c.id, time: c.time, type: c.type, picked, result });
  store.set(`ans:${lesson.lesson_id}`, answers); renderAnswers();
}
function renderAnswers() {
  const el = $("#ans-list");
  if (!answers.length) return;
  const rn = { correct: "✓", wrong: "✗", skipped: "–" };
  el.innerHTML = answers.map((a) =>
    `<div>${rn[a.result]} <b>${fmt(a.time)}</b> ${a.id} <span class="dim">${a.type}</span> → ${a.picked === null ? "跳过" : String(a.picked)}</div>`).join("");
}

/* ── 疑问标记（§15：只记录，0 token） ── */
function wireAsk() {
  $("#ask-count").textContent = markers.length;
  $("#ask-fab").onclick = () => {
    const t = video.currentTime;
    const m = document.createElement("div"); m.id = "ask-modal";
    m.innerHTML = `<div class="card"><div class="card-tag gold">标记疑问 @ ${fmt(t)}</div>
      <textarea placeholder="例如：为什么这里 D1 要除以 D2？"></textarea>
      <div class="row" style="margin-top:10px"><button class="btn primary" id="mk-save">保存</button><button class="btn ghost" id="mk-cancel">取消</button></div></div>`;
    document.body.appendChild(m);
    m.querySelector("textarea").focus();
    const close = () => m.remove();
    m.querySelector("#mk-cancel").onclick = close;
    m.querySelector("#mk-save").onclick = () => {
      const q = m.querySelector("textarea").value.trim();
      if (q) { markers.push({ lesson_id: lesson.lesson_id, timestamp: Math.round(t * 10) / 10, question: q }); store.set(`mk:${lesson.lesson_id}`, markers); renderMarkers(); }
      close(); toast("已记录，看完视频后在右侧统一提问");
    };
  };
}
function renderMarkers() {
  $("#ask-count").textContent = markers.length; $("#qa-count2").textContent = markers.length;
  if (markers.length) $("#qa-list").innerHTML = markers.map((m) => `<div><b style="color:var(--gold)">${fmt(m.timestamp)}</b>　${m.question}</div>`).join("");
  else $("#qa-list").innerHTML = `<span class="dim">暂无。看视频时随时点左下角「我有疑问」，看完后在这里统一向 AI 提问。</span>`;
}

/* ── Phase AI1 预览：展示后端将拼装的上下文（§20），本 MVP 不调用 LLM ── */
$("#qa-preview-btn").onclick = () => {
  const el = $("#qa-preview"); el.classList.toggle("hidden");
  if (el.classList.contains("hidden")) return;
  const ctx = {
    course: { course_id: course.course_id, title: course.title },
    lesson: { lesson_id: lesson.lesson_id, title: lesson.title, knowledge_points: lesson.knowledge_points },
    student_questions: markers,
    student_answers: answers,
    transcript: `（transcript.vtt · ${PKG}/${lesson.transcript}，后端按 timestamp 取 ±20s 窗口）`,
    note: "以上为 Phase AI1 将发给后端的上下文骨架（§20）。MVP 阶段仅演示，不调用模型。",
  };
  el.textContent = JSON.stringify(ctx, null, 2);
};

/* ── 进度 / 导航 ── */
function wireProgress() {
  video.addEventListener("timeupdate", () => {
    $("#progress-fill").style.width = `${(video.currentTime / lesson.duration) * 100}%`;
    $("#progress-text").textContent = `${Math.round((video.currentTime / lesson.duration) * 100)}% · ${fmt(video.currentTime)}`;
    store.set(`pg:${lesson.lesson_id}`, { lastTime: video.currentTime, completed: video.ended });
  });
  video.addEventListener("ended", () => { store.set(`pg:${lesson.lesson_id}`, { lastTime: lesson.duration, completed: true }); toast("本节完成 ✔ 摘要与疑问卡在右侧"); });
}
function restoreProgress() {
  const pg = store.get(`pg:${lesson.lesson_id}`, null);
  if (pg && pg.lastTime > 8 && !pg.completed) {
    const m = document.createElement("div"); m.id = "ask-modal";
    m.innerHTML = `<div class="card"><div class="card-tag">继续学习？</div><p>上次看到 <b style="color:var(--gold)">${fmt(pg.lastTime)}</b></p>
      <div class="row"><button class="btn primary" id="rs-go">继续</button><button class="btn ghost" id="rs-no">从头看</button></div></div>`;
    document.body.appendChild(m);
    const close = () => m.remove();
    m.querySelector("#rs-go").onclick = () => { video.currentTime = pg.lastTime; close(); };
    m.querySelector("#rs-no").onclick = close;
  }
}
function wireNav() {
  const all = course.chapters.flatMap((c) => c.lessons);
  const i = all.findIndex((l) => l.lesson_id === lesson.lesson_id);
  const set = (sel, l, dir) => { const b = $(sel); if (l) { b.disabled = false; b.onclick = () => (location.search = `?p=${l.package}`); } b.title = l ? l.title : dir; };
  set("#prev-btn", all[i - 1], "没有上一课"); set("#next-btn", all[i + 1], "没有下一课");
}

let toastTimer;
function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove("show"), 2200);
}

init().catch((e) => { document.body.insertAdjacentHTML("afterbegin", `<div style="color:#F56565;padding:20px">加载失败：${e.message}（需通过 http 访问，file:// 不行）</div>`); });
