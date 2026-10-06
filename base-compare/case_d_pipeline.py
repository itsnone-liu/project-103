#!/usr/bin/env python3
"""Case D pipeline: geometry proof (triangle interior-angle sum, tear-and-
reassemble) with the audio timing inversion — narration is the physical clock.

Usage: python case_d_pipeline.py glm|luna [effort]
Phase 1: guide+PATTERNS+MOTION_SKILL+task -> storyboard (Parameters block with
         vertices+angles, numbered Narration list for TTS, [PATTERN tags]).
TTS    : narration lines -> audio.py tts -> timing.json (starts/total).
Phase 2: + timing starts -> scene code using patterns.js v1 primitives.
Post   : install, render, narration wav, alignment audit, mux (BGM+loudnorm).
"""
from __future__ import annotations
import http.client
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
BASE = ROOT / 'base-compare'
COMP = (ROOT / 'runs' / 'architecture-smoke' / 'node_modules' /
        '@remotion' / 'compositor-win32-x64-msvc')
import os  # noqa: E402
os.environ['PATH'] = str(COMP) + os.pathsep + os.environ['PATH']
sys.path.insert(0, str(ROOT))
import p103.video_qa as video_qa  # noqa: E402
import audio  # noqa: E402

GLM_API = 'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions'
GLM_KEY = os.environ.get('GLM_API_KEY', '')
LUNA_API = 'http://127.0.0.1:8080/v1/chat/completions'
LUNA_KEY = os.environ.get('LUNA_API_KEY', '')
THINK_BUDGET = int(os.environ.get('GLM_THINK_BUDGET', '12288'))

TASK = (
    "Make a ~30-second teaching animation proving the triangle interior "
    "angle sum is 180 degrees, using the classic tear-and-reassemble proof: "
    "draw a triangle (angles near 50/60/70 degrees), mark each interior "
    "angle with its own role color and an angle-arc, then tear off two of "
    "the angles, fly them (arc toss) to the third vertex, rotate each copy "
    "so all three wedges assemble side by side into one straight angle on "
    "a straight line. Freeze+flash when they align, count up 50+60+70=180, "
    "stamp the conclusion, end with a brief before/after recap board.")

VOCAB = ("FOCUS_REVEAL, STAGGER_REVEAL, FREEZE_EVENT, HOLD, EVENT_EMPHASIS, "
         "IMPACT_BURST, ARC_TOSS, IDEA_BURST, ANTICIPATION_WINDUP, "
         "CAMERA_PUSH, BEAT_GRID, TRACE_PATH, NARRATION_ANCHOR, "
         "LIVE_ANNOTATION, COUNT_UP, LIVE_READOUT, STAMP_ANSWER, "
         "HIGHLIGHT_BOX, LEAVE_MARK, SUPERPOSE_COPY, SHOW_BEFORE_AFTER, "
         "COLOR_BIND")

PHASE1_SYS = (
    "You are a coding animator in the ClaudeAnimationBase runtime. "
    "THIS CALL IS PHASE 1 ONLY: produce the storyboard. Requirements:\n"
    "1. 'Parameters' block: triangle vertex coordinates (px, 1920x1080 "
    "canvas), the three interior angles in degrees computed from those "
    "vertices, and their sum. The code phase must draw exactly these "
    "vertices; all angle math derives from them.\n"
    "2. '## Narration' section: 6-8 numbered plain-Chinese sentences "
    "(k. sentence per line) — these go to TTS, so keep each under ~18 "
    "chars of speech budget awareness (normal pace ~4 chars/sec).\n"
    "3. Annotate every read with pattern tags from this vocabulary "
    f"(one or more, in [BRACKETS]): {VOCAB}\n"
    "4. Shots: anchor every action to a narration sentence as (k, f) "
    "fractions, never raw seconds. Duration comes from TTS later.\n"
    "5. Format: logline, world, Parameters, Narration, shots, transitions.\n"
    "Respond with EXACTLY one ```markdown fenced block.")

PHASE2_SYS = (
    "You are a coding animator in the ClaudeAnimationBase runtime. "
    "PHASE 2: implement the storyboard below as one scene file, USING the "
    "pattern library (patterns.js is loaded before scenes; its API doc "
    "PATTERNS.md is provided). Hard requirements:\n"
    "1. Geometry truth: draw the storyboard's exact vertices; compute all "
    "angles/positions with atan2/lerp from them — never eyeball. Angle "
    "wedges must visually match the declared degrees.\n"
    "2. Narration clock: use narr(STARTS) with the provided TTS-measured "
    "starts; every action anchors to N.at(k, f) / N.win(k) — no raw "
    "seconds except the TTS table itself. Config duration = TOTAL.\n"
    "3. Use library primitives (tracePath/markAngle/superposeCopy/"
    "countUp/stampAnswer/highlightBox/ROLE colors/letter labels/sfx...). "
    "Before each pattern passage write // PATTERN: TAG (exact bracket "
    "spelling from your storyboard). Anything outside the vocabulary: "
    "// PATTERN: CUSTOM:short-name.\n"
    "4. superposeCopy must use a NON-ZERO rotation for the torn-angle "
    "copies. End with flushLetters() as the last line of the shot fn.\n"
    "5. Self-contained IIFE ending with shots([[0, shot]]); only "
    "documented engine+library API; 1920x1080.\n"
    "6. Line 1 comment: the exact config.js line (duration from TOTAL).\n"
    "Respond with EXACTLY one ```javascript fenced block containing the "
    "complete src/scenes/triangle180.js.")


def call(model: str, messages: list, max_tok: int,
         effort: str | None = None) -> tuple[str, dict]:
    if model == 'glm':
        url, key = GLM_API, GLM_KEY
        payload = {'model': 'glm-5.3', 'messages': messages,
                   'temperature': 1.0, 'max_tokens': max_tok}
        # case-d lesson x3: on the ~21k-token phase-2 prompt GLM spirals into
        # endless reasoning (65k reasoning, zero content, finish=length);
        # reasoning_effort AND thinking.budget_tokens both failed to cap it
        # on the coding endpoint. Working fix: DISABLE thinking for phase-2
        # codegen + slim the prompt (see main()); storyboard keeps thinking.
        if os.environ.get('GLM_THINK_OFF') == '1':
            payload['thinking'] = {'type': 'disabled'}
    else:
        url, key = LUNA_API, LUNA_KEY
        payload = {'model': 'gpt-6-luna', 'messages': messages,
                   'temperature': 1.0, 'max_completion_tokens': max_tok}
        if effort:
            payload['reasoning_effort'] = effort
    body = json.dumps(payload).encode('utf-8')
    t0 = time.time()
    for attempt in range(30):
        try:
            req = urllib.request.Request(
                url, data=body, headers={
                    'Authorization': f'Bearer {key}',
                    'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=1800) as r:
                obj = json.loads(r.read().decode('utf-8'))
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', 'replace')[:300]
            if '1308' in detail or '上限' in detail:
                wait = 900   # 5h-window limit: NO rapid retry (1308 storm lesson)
                print(f'attempt {attempt}: 1308 window limit, sleep {wait}s',
                      flush=True)
                time.sleep(wait)
                continue
            if exc.code in (429, 500, 502, 503):
                print(f'attempt {attempt}: HTTP {exc.code}, sleep 75',
                      flush=True)
                time.sleep(75)
                continue
            raise
        except (http.client.RemoteDisconnected, ConnectionError,
                TimeoutError, urllib.error.URLError) as exc:
            print(f'attempt {attempt}: transport {exc!r}, sleep 60',
                  flush=True)
            time.sleep(60)
            continue
    msg = obj['choices'][0]['message']
    meta = {'secs': round(time.time() - t0, 1),
            'finish': obj['choices'][0].get('finish_reason'),
            'usage': obj.get('usage')}
    return msg.get('content') or '', meta


def fenced(text: str, kinds: tuple) -> str:
    blocks = re.findall(r'```(\w+)?\s*\n(.*?)```', text, re.S)
    best = ''
    for lang, body in blocks:
        if lang and lang.lower() in kinds:
            if len(body) > len(best):
                best = body
    if not best and blocks:
        best = max((b for _, b in blocks), key=len)
    return best.strip()


def parse_narration(storyboard: str) -> list[str]:
    """Pull 'k. text' lines from the ## Narration section."""
    m = re.search(r'##\s*Narration(.*?)(?=\n#|\Z)', storyboard, re.S | re.I)
    if not m:
        return []
    lines = re.findall(r'^\s*(\d+)[.、]\s*(.+?)\s*$', m.group(1), re.M)
    return [t for _, t in sorted(lines, key=lambda x: int(x[0]))]


def lint_alignment(storyboard: str, code: str) -> dict:
    tags = set(re.findall(r'\[([A-Z_]+)\]', storyboard))
    markers = set(re.findall(r'PATTERN:\s*\[?([A-Z_]+)', code))
    inter = tags & markers
    return {
        'storyboard_tags': sorted(tags), 'code_markers': sorted(markers),
        'alignment': round(len(inter) / len(tags), 3) if tags else None,
        'missing_in_code': sorted(tags - markers)}


def main() -> int:
    model = sys.argv[1]
    effort = sys.argv[2] if len(sys.argv) > 2 else None
    case = BASE / 'case-d' / model
    out = case / model
    out.mkdir(parents=True, exist_ok=True)
    guide = (case / 'ANIMATION_GUIDE.md').read_text(encoding='utf-8')
    patterns_doc = (ROOT / 'pattern-library' / 'PATTERNS.md').read_text(
        encoding='utf-8')
    skill_doc = (ROOT / 'pattern-library' / 'MOTION_SKILL.md').read_text(
        encoding='utf-8')
    demo = (case / 'src' / 'scenes' / 'demo.js').read_text(encoding='utf-8')

    # ---- phase 1: storyboard
    sb_path = out / 'STORYBOARD.md'
    if sb_path.exists() and len(sb_path.read_text(encoding='utf-8')) >= 300:
        storyboard = sb_path.read_text(encoding='utf-8')
        print(f'[{model}] phase 1 SKIPPED (resume): {len(storyboard)} chars')
    else:
        print(f'[{model}] phase 1 storyboard...')
        sb_raw, m1 = call(model, [
            {'role': 'system', 'content': PHASE1_SYS},
            {'role': 'user', 'content':
                f'# ANIMATION_GUIDE.md\n\n{guide}\n\n'
                f'# PATTERNS.md (library API — v1)\n\n{patterns_doc}\n\n'
                f'# Task\n\n{TASK}\n'}], 65536, effort=effort)
        (out / 'phase1_meta.json').write_text(
            json.dumps(m1, ensure_ascii=False, indent=1), encoding='utf-8')
        storyboard = fenced(sb_raw, ('markdown', 'md'))
        sb_path.write_text(storyboard + '\n', encoding='utf-8')
        (out / 'phase1_raw.txt').write_text(sb_raw, encoding='utf-8')
        print(f'[{model}] storyboard {len(storyboard)} chars meta={m1}')
        if len(storyboard) < 300:
            print('storyboard too short - abort')
            return 1

    # ---- TTS timing inversion
    sentences = parse_narration(storyboard)
    if len(sentences) < 4:
        print(f'[{model}] narration parse FAILED ({len(sentences)} lines) '
              '- abort (fix storyboard manually or rerun)')
        return 1
    scene = {'title': f'cased_{model}', 'voice': 'zh-CN-XiaoxiaoNeural',
             'bgm': {'file': 'bgm/musicbox.wav', 'gain': 0.13},
             'gap': 0.3, 'tail': 1.8,
             'sentences': [{'text': s} for s in sentences]}
    scene_path = ROOT / 'audio' / f'scene_cased_{model}.json'
    scene_path.write_text(json.dumps(scene, ensure_ascii=False, indent=1),
                          encoding='utf-8')
    audio.cmd_tts(str(scene_path))
    timing = json.loads(
        (ROOT / 'audio' / f'timing_cased_{model}.json').read_text(
            encoding='utf-8'))
    print(f'[{model}] TTS total={timing["total"]}s starts={timing["starts"]}')

    # ---- phase 2: code with real timing (glm prompt slimmed: drop
    # MOTION_SKILL + demo.js — the ~21k prompt triggers GLM's reasoning
    # spiral; slim + no-thinking is the working config for codegen)
    print(f'[{model}] phase 2 code (effort={effort})...')
    p2 = [f'# ANIMATION_GUIDE.md\n\n{guide}\n\n',
          f'# PATTERNS.md (library API — use these primitives)\n\n'
          f'{patterns_doc}\n\n',
          f'# Your phase-1 storyboard (implement THIS)\n\n{storyboard}\n\n',
          f'# TTS timing (physical narration clock)\n\n'
          f'narr starts (sentence starts PLUS final tEnd as last entry '
          f'— narr() needs n+1): '
          f'{json.dumps(timing["starts"] + [timing["total"]])}\n'
          f'TOTAL duration: {timing["total"]}\n\n']
    if model != 'glm':
        p2.append(f'# MOTION_SKILL.md (director rules)\n\n{skill_doc}\n\n'
                  f'# src/scenes/demo.js (engine format reference only)\n\n'
                  f'```javascript\n{demo}\n```\n')
    else:
        p2.append(
            '# Output discipline\n\n'
            'Think briefly. Write the complete file in ONE pass. Do NOT '
            're-derive the storyboard math — copy its Parameters block '
            'verbatim into consts.\n')
    code_raw, m2 = call(model, [
        {'role': 'system', 'content': PHASE2_SYS},
        {'role': 'user', 'content': ''.join(p2)}], 65536, effort=effort)
    (out / 'phase2_meta.json').write_text(
        json.dumps(m2, ensure_ascii=False, indent=1), encoding='utf-8')
    code = fenced(code_raw, ('javascript', 'js'))
    (out / 'phase2_raw.txt').write_text(code_raw, encoding='utf-8')
    print(f'[{model}] code {len(code)} chars meta={m2}')
    if len(code) < 500:
        print('no code extracted - abort')
        return 1

    # ---- install (timing total is the duration truth)
    (case / 'src' / 'scenes' / 'triangle180.js').write_text(
        code + '\n', encoding='utf-8')
    (case / 'src' / 'config.js').write_text(
        '// config.js: set by case_d pipeline (TTS timing).\n'
        f'const PROJECT = {{ duration: {timing["total"]:g}, bpm: 120, '
        'offset: 0 };\n', encoding='utf-8')
    html = (case / 'studio.html').read_text(encoding='utf-8')
    html = re.sub(r'src/scenes/[\w.-]+\.js', 'src/scenes/triangle180.js',
                  html, count=1)
    (case / 'studio.html').write_text(html, encoding='utf-8')

    align = lint_alignment(storyboard, code)
    (out / 'alignment.json').write_text(
        json.dumps(align, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'[{model}] alignment={align["alignment"]} '
          f'missing={align["missing_in_code"]}')

    # ---- render
    r = subprocess.run(
        ['node', 'render.mjs', '--clip', '--out=out/triangle180.mp4'],
        cwd=str(case), capture_output=True, text=True,
        encoding='utf-8', errors='replace', timeout=10800)
    log = (r.stdout or '') + (r.stderr or '')
    if r.returncode != 0 or 'page error' in log:
        print(f'[{model}] RENDER FAIL / page errors:',
              log[-1200:])
        return 1
    frames = video_qa.extract_keyframes(
        case / 'out' / 'triangle180.mp4', case / 'out' / 'sheet_frames',
        count=8, tool_root=ROOT)
    sheet = video_qa.create_contact_sheet(
        frames, case / 'out' / f'triangle_sheet_{model}.png', tool_root=ROOT)

    # ---- audio chain: narration + audit + mux
    audio.cmd_narration(str(ROOT / 'audio' / f'timing_cased_{model}.json'))
    ok = audio.cmd_audit(str(ROOT / 'audio' / f'narration_cased_{model}.wav'),
                         str(ROOT / 'audio' / f'timing_cased_{model}.json'))
    final = audio.cmd_mux(str(case / 'out' / 'triangle180.mp4'),
                          str(ROOT / 'audio' / f'timing_cased_{model}.json'),
                          str(case / 'out' / f'final_{model}.mp4'))
    print(f'[{model}] DONE video={case / "out" / "triangle180.mp4"} '
          f'sheet={sheet} audit={"PASS" if ok else "FAIL"} final={final}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
