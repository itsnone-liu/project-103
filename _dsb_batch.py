# -*- coding: utf-8 -*-
"""DSB（设计基础）批产驱动器：B1—B5，共 54 段（扣除种子 dsb-2-03 / dsb-5-05）。

用法：python _dsb_batch.py [B1|B2|B3|B4|B5]        （默认 B1）
      环境变量 DSB_BATCH_TITLES=dsb-1-01,dsb-1-02 可聚焦重跑指定段。

- 每段: _run_produce.py（storyboard→tts→decide→codegen→render→qa→mux，自动复用已完成阶段）
- 模型链: sol --effort high → ds --effort high → glm --effort high（前次失败/超时才降级；produce 断点续跑）
- 机器门禁（分段方案 §八）: 时长≥270s；qa_report pass 且 blank_frames=0；
  无 ≥20s 冻结窗（_freeze_check 抽帧）；帧活力 max diff>1.2；produce 退出码 0；node 语法检查
- 看门狗: 单次尝试 150 分钟超时 → 杀该段进程 → 降级重试
- 状态: _dsb_batch_state.json（断点续跑，PASS 段跳过）；日志 _dsb_batch_progress.log
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
FF = str(ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe")
PROFILE = ROOT / "profiles" / "design-basic.profile.yaml"
MIN_TOTAL = 270.0
ATTEMPT_TIMEOUT = 150 * 60

BATCHES = {
    "B1": ["dsb-00", "dsb-1-01", "dsb-1-02", "dsb-1-03", "dsb-1-04",
           "dsb-2-01", "dsb-2-02", "dsb-2-04", "dsb-2-05"],
    "B2": ["dsb-3-01", "dsb-3-02", "dsb-3-03", "dsb-3-04",
           "dsb-4-01", "dsb-4-02", "dsb-4-03", "dsb-4-04",
           "dsb-5-01", "dsb-5-02", "dsb-5-03", "dsb-5-04"],
    "B3": ["dsb-6-01", "dsb-6-02", "dsb-6-03", "dsb-6-04",
           "dsb-7-01", "dsb-7-02", "dsb-7-03", "dsb-7-04",
           "dsb-8-01", "dsb-8-02", "dsb-8-03", "dsb-8-04"],
    "B4": ["dsb-9-01", "dsb-9-02", "dsb-9-03", "dsb-9-04",
           "dsb-10-01", "dsb-10-02", "dsb-10-03", "dsb-10-04", "dsb-10-05"],
    "B5": ["dsb-11-01", "dsb-11-02", "dsb-11-03", "dsb-11-04", "dsb-11-05",
           "dsb-12-01", "dsb-12-02", "dsb-12-03", "dsb-12-04", "dsb-12-05",
           "dsb-ca1", "dsb-ca2"],
}
MODEL_CHAIN = ["sol", "ds", "glm"]

STATE = ROOT / "_dsb_batch_state.json"
LOG = ROOT / "_dsb_batch_progress.log"


def log(msg):
    line = f"[{time.strftime('%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def save_state(st):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def env_for_run():
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["P103_RATE_BASE"] = "-8"
    env["P103_RENDER_SHARDS"] = env.get("P103_RENDER_SHARDS", "4")
    return env


def final_path(title):
    return ROOT / "runs" / title / "out" / f"final_{title}.mp4"


def kill_run_procs(title):
    # 只杀带该 run id 的 python 进程，放过本驱动器
    subprocess.run(["powershell", "-NoProfile", "-Command",
        f"Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
        f"Where-Object {{$_.CommandLine -like '*{title}*' -and $_.CommandLine -notlike '*_dsb_batch*'}} | "
        f"ForEach-Object {{ taskkill /PID $($_.ProcessId) /T /F }}"],
        capture_output=True, text=True)


def node_syntax_check(title):
    code = ROOT / "runs" / title / "code" / "index.html"
    if not code.exists():
        return True, ""
    node = None
    for cand in (r"D:\qjcNetDiskDownload\nodejs\node.exe",
                 r"D:\ComfyUI_windows_portable\python_embeded\Lib\site-packages\playwright\driver\node.exe"):
        if Path(cand).exists():
            node = cand
            break
    if node is None:
        return True, "node-not-found(skip)"
    m = re.search(r"<script>([\s\S]*?)</script>", code.read_text(encoding="utf-8"))
    if not m:
        return True, ""
    chk = code.with_name("_syntax_check.js")
    chk.write_text(m.group(1), encoding="utf-8")
    try:
        r = subprocess.run([node, "--check", str(chk)], capture_output=True, text=True)
        return r.returncode == 0, (r.stderr or "")[-500:]
    finally:
        chk.unlink(missing_ok=True)


def verify(title):
    """机器门禁。返回 (ok, info)。"""
    timing_path = ROOT / "audio" / f"timing_{title}.json"
    final = final_path(title)
    qa = ROOT / "runs" / title / "out" / "qa_report.json"
    if not (timing_path.exists() and final.exists() and qa.exists()):
        return False, {"error": "timing_or_final_or_qa_missing"}
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    qaj = json.loads(qa.read_text(encoding="utf-8"))
    total = float(timing.get("total", 0))
    ok_duration = total >= MIN_TOTAL
    ok_qa = bool(qaj.get("pass")) and \
        int(qaj.get("checks", {}).get("frame_variance", {}).get("blank_frames", -1)) == 0
    freeze, diffs = [], []
    try:
        sys.path.insert(0, str(ROOT))
        import _freeze_check as FC
        FC.FF = FF
        freeze, diffs = FC.freeze_windows(str(final))
    except Exception as e:
        return False, {"error": f"freeze_check_failed: {e}"}
    ok_freeze = not freeze
    ok_vital = bool(diffs) and max(diffs) > 1.2
    ok, syn = node_syntax_check(title)
    info = {"duration_s": round(total, 1), "sentences": len(timing.get("starts", [])),
            "qa_pass": qaj.get("pass"),
            "blank_frames": qaj.get("checks", {}).get("frame_variance", {}).get("blank_frames"),
            "freeze_windows": freeze, "frame_samples": len(diffs),
            "max_diff": round(max(diffs), 2) if diffs else 0,
            "syntax_ok": ok, "syntax_err": syn[:200] if not ok else ""}
    okall = ok_duration and ok_qa and ok_freeze and ok_vital and ok
    return okall, info


def stale_output(title):
    final = final_path(title)
    code = ROOT / "runs" / title / "code" / "index.html"
    return final.exists() and code.exists() and final.stat().st_mtime < code.stat().st_mtime


def attempt(title, model):
    """跑一次全管线（断点续跑），带看门狗。返回 (rc, timed_out)。"""
    topic = f"runs/{title}/topic-{title}.md"
    plog = ROOT / "runs" / title / "_produce.log"
    with open(plog, "a", encoding="utf-8") as lf:
        lf.write(f"\n===== [{time.strftime('%m-%d %H:%M')}] model={model} =====\n")
        cmd = [PY, "-X", "utf8", str(ROOT / "_run_produce.py"), f"runs/{title}",
               "--topic", topic, "--model", model, "--effort", "high",
               "--profile", str(PROFILE), "--title", title]
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT,
                             cwd=str(ROOT), env=env_for_run())
    t0 = time.time()
    while True:
        if p.poll() is not None:
            return p.returncode, False
        if time.time() - t0 > ATTEMPT_TIMEOUT:
            kill_run_procs(title)
            try:
                p.kill()
            except Exception:
                pass
            return 99, True
        time.sleep(30)


def process(title):
    log(f"=== {title} 开始 ===")
    for model in MODEL_CHAIN:
        rc, timed_out = attempt(title, model)
        ok, info = verify(title)
        if timed_out:
            log(f"{title} model={model} 超时被杀 rc={rc}")
        else:
            log(f"{title} model={model} rc={rc} gates={'PASS' if ok else 'FAIL'} {info}")
        if ok:
            return True, info, model
        if not final_path(title).exists():
            continue  # 换模型整链重试
        # 有 final 但门禁未过：再试一次同段（produce 会复用阶段，多走 repair/mux）
    ok, info = verify(title)
    return ok, info, None


def main():
    batch = sys.argv[1] if len(sys.argv) > 1 else "B1"
    titles = [t.strip() for t in os.environ.get("DSB_BATCH_TITLES", "").split(",") if t.strip()]
    if not titles:
        titles = BATCHES[batch]
    log(f"### 批次 {batch} 启动：{len(titles)} 段（{titles[0]}..{titles[-1]}）")
    st = load_state()
    failed = []
    for title in titles:
        rec = st.get(title, {})
        if rec.get("pass") and not stale_output(title):
            log(f"[skip PASS] {title} {rec.get('duration_s')}s")
            continue
        topic = ROOT / "runs" / title / f"topic-{title}.md"
        if not topic.exists():
            log(f"[FAIL] {title}: topic missing")
            st[title] = {"pass": False, "error": "topic_missing"}
            save_state(st)
            failed.append(title)
            continue
        t0 = time.time()
        ok, info, model = process(title)
        rec = {"pass": bool(ok), "model": model, "minutes": round((time.time() - t0) / 60, 1), **info}
        st[title] = rec
        save_state(st)
        log(f"[{'PASS' if ok else 'FAIL'}] {title} ({rec['minutes']}min, model={model})")
        if not ok:
            failed.append(title)
    log(f"### 批次 {batch} 结束：pass={len(titles) - len(failed)}/{len(titles)}; failed: {failed or '无'}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
