"""produce.py — v2 生产编排 CLI。

  python -m pipeline.produce <workdir> --topic <topic.md> [--model luna|glm]
       [--mode open|assisted|project-route] [--profile profiles/xxx.yaml]
       [--repair-rounds 1] [--blind-sample] [--stage <name>] [--dry-audio]

阶段（产物落 workdir，断点续跑——产物存在即跳过）：
  storyboard → tts(timing) → decide(两步决策) → codegen → smoke →
  render → qa → repair(≤N) → mux → final
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import llm, prompts, qa, profile as prof_mod          # noqa: E402
from pipeline.backends import smoke_gate                              # noqa: E402
from pipeline.adapters import web2d, manim                            # noqa: E402


def _sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print("  $", " ".join(map(str, cmd[:8])), "..." if len(cmd) > 8 else "")
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


def parse_storyboard(text: str) -> dict:
    def sec(name):
        m = re.search(rf"##\s*{name}.*?\n(.*?)(?=\n##|\Z)", text, re.S)
        return m.group(1).strip() if m else ""
    narr = [ln.split(". ", 1)[1].strip() for ln in sec("Narration").splitlines() if re.match(r"\s*\d+\.", ln)]
    if not narr:
        raise ValueError("分镜缺 ## Narration 编号句")
    return {"narration": narr, "parameters": sec("Parameters"), "math_check": sec("Math-check"), "raw": text}


def scene_json(sb: dict, title: str) -> dict:
    return {"title": title, "voice": "zh-CN-XiaoxiaoNeural",
            "bgm": {"file": "bgm/Wholesome.mp3", "gain": 0.13},
            "gap": 0.25, "tail": 1.5, "sentences": [{"text": s, "pause_after": 0.25} for s in sb["narration"]]}


def visual_repair(args) -> int:
    """视觉迭代轮（ARCHITECTURE-v2 附录补丁1配套）：VLM/人工看 qa_sheet 后的定向修复。
    输入=既有完整产物（timing/decision/code）+ 视觉问题笔记；动作=repair→render→qa→mux。"""
    from pipeline.adapters import web2d, manim
    wd = args.workdir.resolve()
    title = args.title or wd.name
    timing = json.loads((ROOT / "audio" / f"timing_{title}.json").read_text(encoding="utf-8"))
    decision = json.loads((wd / "decision.json").read_text(encoding="utf-8"))
    backend = (decision.get("backend") or "WEB_2D").lower()
    code_path = wd / "code" / ("index.html" if backend in ("web_2d", "three_3d") else "scene.py")
    code = code_path.read_text(encoding="utf-8")
    notes = args.visual_repair.read_text(encoding="utf-8")
    print(f"[{title}] visual-repair: 注入视觉反馈\n---\n{notes[:400]}\n---", flush=True)
    fixed, meta = llm.call(args.model, prompts.repair_prompt(
        decision, code,
        [{"kind": "visual", "message": "视觉迭代反馈（比错误修复优先级低，改画面不改数学）：\n" + notes}],
        "qa_sheet.jpg 拼图已人审/VLM审，问题清单见上"))
    import re as _re
    m = _re.search(r"```(?:\w+)?\n(.*?)```", fixed, _re.S)
    if not m or len(m.group(1)) < 200:
        print("visual-repair: 修复产出无效（无代码块/过短）"); return 1
    code_path.write_text(m.group(1).strip(), encoding="utf-8")
    print(f"visual-repair: 新代码 {len(m.group(1))} chars")
    adapter = web2d if backend in ("web_2d", "three_3d") else manim
    res = adapter.render(wd, timing)
    if not res["ok"]:
        print("visual-repair: 重渲失败", res["errors"][:3]); return 1
    report = qa.check(res["video"], timing, wd)
    print("visual-repair qa:", "PASS" if report["pass"] else "FAIL",
          json.dumps(report["checks"].get("frame_variance", {}), ensure_ascii=False)[:100])
    final = wd / "out" / f"final_{title}.mp4"
    r = _sh([sys.executable, str(ROOT / "audio.py"), "mux", str(res["video"]), str(timing_path_of(title)), str(final)])
    if r.returncode != 0:
        print("mux 失败:", r.stderr[-300:]); return 1
    print("final:", [l for l in r.stdout.splitlines() if l.startswith("final:")])
    return 0


def timing_path_of(title: str) -> Path:
    return ROOT / "audio" / f"timing_{title}.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir", type=Path)
    ap.add_argument("--topic", type=Path, required=True)
    ap.add_argument("--model", default="luna", choices=["luna", "glm"])
    ap.add_argument("--mode", default=None, choices=["open", "assisted", "project-route"])
    ap.add_argument("--profile", type=Path, default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--repair-rounds", type=int, default=1)
    ap.add_argument("--blind-sample", action="store_true", help="菜单盲测采样：decide/codegen 只见契约不见菜单")
    ap.add_argument("--visual-repair", type=Path, default=None, metavar="NOTES.md",
                    help="视觉迭代轮：用笔记中的视觉问题做一轮定向修复+重渲+重QA+重mux（需先有完整产物）")
    ap.add_argument("--stage", default=None, help="只跑到该阶段（storyboard|tts|decide|codegen|smoke|render|qa|mux|final）")
    args = ap.parse_args()

    if args.visual_repair:
        return visual_repair(args)

    wd = args.workdir.resolve(); wd.mkdir(parents=True, exist_ok=True)
    (wd / "code").mkdir(exist_ok=True); (wd / "out").mkdir(exist_ok=True)
    prof = prof_mod.load(args.profile)
    if args.mode:
        prof["mode"] = args.mode.upper()
    title = args.title or wd.name
    topic = args.topic.read_text(encoding="utf-8")
    log = lambda *a: print(f"[{title}]", *a, flush=True)

    # ---------- storyboard ----------
    sb_path = wd / "storyboard.md"
    if sb_path.exists():
        sb = parse_storyboard(sb_path.read_text(encoding="utf-8")); log("storyboard: 复用")
    else:
        log("storyboard: 生成中…")
        out, meta = llm.call(args.model, prompts.storyboard_prompt(topic, prof), think="on")
        sb_path.write_text(out, encoding="utf-8")
        sb = parse_storyboard(out); log(f"storyboard: {len(sb['narration'])} 句 ({meta['usage'].get('completion_tokens', '?')} tok)")

    # ---------- tts → timing（音频物理时钟，audio.py 已验证链） ----------
    timing_path = ROOT / "audio" / f"timing_{title}.json"
    if timing_path.exists():
        log("tts: 复用", timing_path.name)
    else:
        scene_path = ROOT / "audio" / f"scene_{title}.json"
        scene_path.write_text(json.dumps(scene_json(sb, title), ensure_ascii=False, indent=2), encoding="utf-8")
        r = _sh([sys.executable, str(ROOT / "audio.py"), "tts", str(scene_path)])
        if r.returncode != 0:
            log("tts 失败:", r.stdout[-300:], r.stderr[-300:]); return 1
        log("tts:", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "done")
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    log(f"timing: total={timing['total']}s starts(n)={len(timing['starts'])}")

    # ---------- narration 轨 ----------
    nar_path = ROOT / "audio" / f"narration_{title}.wav"
    if not nar_path.exists():
        r = _sh([sys.executable, str(ROOT / "audio.py"), "narration", str(timing_path)])
        if r.returncode != 0:
            log("narration 失败:", r.stderr[-200:]); return 1
    r = _sh([sys.executable, str(ROOT / "audio.py"), "audit", str(nar_path), str(timing_path)])
    log("narration audit:", [l for l in r.stdout.splitlines() if "AUDIT" in l] or r.stdout[-100:])

    if args.stage in ("storyboard", "tts"):
        return 0

    # ---------- decide（两步：无菜单自由规划 → 菜单匹配 + why-not） ----------
    dec_path = wd / "decision.json"
    if dec_path.exists():
        decision = json.loads(dec_path.read_text(encoding="utf-8")); log("decide: 复用", decision.get("backend"))
    else:
        steps = prompts.decision_prompts(topic, sb_path.read_text(encoding="utf-8"), prof, blind=args.blind_sample)
        plan_free, _ = llm.call(args.model, steps[0], think="on")
        (wd / "decision_stepA.md").write_text(plan_free, encoding="utf-8")
        if args.blind_sample:
            decision = {"backend": "CUSTOM", "blind_sample": True, "reason": plan_free[:400],
                        "alternative": None, "risk": None, "why_not": {}}
        else:
            raw, _ = llm.call(args.model, steps[1], think="on")
            m = re.search(r"\{.*\}", raw, re.S)
            decision = json.loads(m.group(0)) if m else {"backend": prof["backend"]["preferred"] or "WEB_2D",
                                                          "reason": "fallback(决策解析失败)", "alternative": None,
                                                          "risk": None, "why_not": {}}
        dec_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
        log("decide:", decision.get("backend"), "—", str(decision.get("reason"))[:80])

    backend = (decision.get("backend") or "WEB_2D").lower()

    # ---------- codegen ----------
    code_path = wd / "code" / ("index.html" if backend in ("web_2d", "three_3d") else "scene.py")
    code_sig = wd / "code" / ".done"
    if code_path.exists() and code_sig.exists():
        code = code_path.read_text(encoding="utf-8"); log("codegen: 复用", code_path.name)
    else:
        log(f"codegen ({backend}): 生成中…")
        code, meta = llm.call(args.model, prompts.codegen_prompt(decision, sb_path.read_text(encoding="utf-8"), timing, prof), think="off")
        m = re.search(r"```(?:\w+)?\n(.*?)```", code, re.S)
        code = (m.group(1) if m else code).strip()
        if len(code) < 200:
            log("codegen 产出过短，失败"); return 1
        code_path.write_text(code, encoding="utf-8"); code_sig.write_text("ok")
        log(f"codegen: {len(code)} chars ({meta['usage'].get('completion_tokens', '?')} tok)")

    if args.stage == "codegen":
        return 0

    # ---------- CUSTOM 否决门 ----------
    if backend == "custom" and not args.blind_sample:
        nom = decision.get("nomination") or {}
        verdict = smoke_gate(nom, wd)
        log("smoke gate:", "PASS" if verdict["ok"] else "FAIL — 回退 web_2d", verdict["evidence"][:1])
        if not verdict["ok"]:
            backend, decision["backend"] = "web_2d", "WEB_2D"
            if not (wd / "code" / "index.html").exists():
                log("codegen: 回退 web_2d 重新生成…")
                code, _ = llm.call(args.model, prompts.codegen_prompt(decision, sb_path.read_text(encoding="utf-8"), timing, prof), think="off")
                m = re.search(r"```(?:\w+)?\n(.*?)```", code, re.S)
                (wd / "code" / "index.html").write_text((m.group(1) if m else code).strip(), encoding="utf-8")

    # ---------- render（+repair 环） ----------
    adapter = web2d if backend in ("web_2d", "three_3d") else manim
    errors: list = []
    for round_i in range(args.repair_rounds + 1):
        res = adapter.render(wd, timing)
        if res["ok"]:
            log(f"render: OK → {Path(res['video']).name}"); break
        errors = res["errors"]
        log(f"render: FAIL ({len(errors)} errors)"); log("  ", *errors[:3])
        if round_i >= args.repair_rounds:
            log("repair 轮次耗尽，终止"); return 1
        log(f"repair round {round_i + 1}…")
        fixed, _ = llm.call(args.model, think="off", messages=prompts.repair_prompt(decision, code, errors, "（帧证据见 qa_report）"), think="off")
        m = re.search(r"```(?:\w+)?\n(.*?)```", fixed, re.S)
        if m:
            code = m.group(1).strip(); code_path.write_text(code, encoding="utf-8")
    else:
        return 1
    video = res["video"]

    # ---------- qa ----------
    report = qa.check(video, timing, wd)
    log("qa:", "PASS" if report["pass"] else "FAIL", json.dumps(report["checks"].get("frame_variance", {}), ensure_ascii=False)[:120])
    if not report["pass"] and args.repair_rounds > 0 and not report["checks"]["frame_variance"]["pass"]:
        log("qa: 空帧率超标 → repair…")
        fixed, _ = llm.call(args.model, think="off", messages=prompts.repair_prompt(
            decision, code,
            [{"kind": "frame", "message": f"blank_frames={report['checks']['frame_variance']['blank_frames']} — 大量帧接近纯色，元素疑似未绘制"}],
            "qa_sheet.jpg"))
        m = re.search(r"```(?:\w+)?\n(.*?)```", fixed, re.S)
        if m:
            code_path.write_text(m.group(1).strip(), encoding="utf-8")
        res = adapter.render(wd, timing)
        if not res["ok"]:
            log("repair 后仍失败"); return 1
        video = res["video"]; report = qa.check(video, timing, wd)
        log("qa(repair):", "PASS" if report["pass"] else "FAIL")

    # ---------- mux（BGM + loudnorm，audio.py） ----------
    final = wd / "out" / f"final_{title}.mp4"
    r = _sh([sys.executable, str(ROOT / "audio.py"), "mux", str(video), str(timing_path), str(final)])
    if r.returncode != 0:
        log("mux 失败:", r.stderr[-300:]); return 1
    log("final:", [l for l in r.stdout.splitlines() if l.startswith("final:")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
