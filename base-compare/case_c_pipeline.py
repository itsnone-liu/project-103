#!/usr/bin/env python3
"""Case C pipeline: pattern-annotated two-phase run for one model.

Usage: python case_c_pipeline.py glm|luna
Phase 1: guide + task -> pattern-annotated storyboard (numeric params).
Phase 2: guide + own storyboard + demo.js -> complete scene code with
         /* PATTERN: X */ markers. Then install, render, sheet, lint.
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

GLM_API = 'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions'
GLM_KEY = os.environ.get('GLM_API_KEY', '')
LUNA_API = 'http://127.0.0.1:8080/v1/chat/completions'
LUNA_KEY = os.environ.get('LUNA_API_KEY', '')

TASK = (
    "Read ANIMATION_GUIDE.md, then make a 20-second teaching animation: "
    "a turtle has a head start from the left marker and walks at a "
    "steady slow speed; Clawd starts later from the same marker and "
    "moves faster. They meet at the mathematically correct point — "
    "freeze and highlight the moment they meet, show both trajectories "
    "as trails, and end with a before/after summary comparing how far "
    "each walked.")

PATTERNS = ("FOCUS_REVEAL, STAGGER_REVEAL, FREEZE_EVENT, TRACE_PATH, "
            "ACCELERATE_AND_SETTLE, CHASE_MOTION, CAMERA_PUSH, DIM_OTHERS, "
            "MATCH_CUT, EVENT_EMPHASIS, SHOW_RELATIVE_DIFFERENCE, "
            "SHOW_BEFORE_AFTER")

PHASE1_SYS = (
    "You are a coding animator in the ClaudeAnimationBase runtime. "
    "THIS CALL IS PHASE 1 ONLY: produce the storyboard. Requirements:\n"
    "1. Declare the math explicitly in a 'Parameters' block: turtle speed "
    "(px/s), clawd speed (px/s), head-start seconds, START x, MEET time "
    "and MEET x computed from those numbers. The code phase must use "
    "exactly these numbers.\n"
    f"2. Annotate every read with pattern tags from this vocabulary "
    f"(one or more, in [BRACKETS]): {PATTERNS}\n"
    "3. Format: logline, world, motif, Parameters block, Clawd's arc, "
    "shots A/B/... with start-end, transitions, reads (each with time "
    "window + [PATTERN tags]).\n"
    "Respond with EXACTLY one ```markdown fenced block.")

PHASE2_SYS = (
    "You are a coding animator in the ClaudeAnimationBase runtime. "
    "PHASE 2: implement the storyboard you wrote in phase 1 (provided "
    "below) as one scene file. Hard requirements:\n"
    "1. Positions must come from the storyboard's declared Parameters "
    "(speeds, head start, meet time/x) — the meet must be mathematically "
    "exact.\n"
    "2. Implement every [PATTERN tag] from the storyboard. Before each "
    "code passage implementing a pattern, write a marker comment like "
    "// PATTERN: FREEZE_EVENT (exact tag spelling).\n"
    "3. Self-contained IIFE ending with shots([...]); only documented "
    "engine API; 1920x1080; duration 20.\n"
    "4. State the exact config.js line as a JS comment on line 1.\n"
    "Respond with EXACTLY one ```javascript fenced block containing the "
    "complete src/scenes/chase_meet.js.")


def call(model: str, messages: list, max_tok: int,
         effort: str | None = None) -> tuple[str, dict]:
    if model == 'glm':
        url, key = GLM_API, GLM_KEY
        payload = {'model': 'glm-5.3', 'messages': messages,
                   'temperature': 1.0, 'max_tokens': max_tok}
        if effort:
            payload['reasoning_effort'] = effort
    else:
        url, key = LUNA_API, LUNA_KEY
        payload = {'model': 'gpt-6-luna', 'messages': messages,
                   'temperature': 1.0, 'max_completion_tokens': max_tok}
        if effort:
            payload['reasoning_effort'] = effort
    body = json.dumps(payload).encode('utf-8')
    t0 = time.time()
    for attempt in range(40):
        try:
            req = urllib.request.Request(
                url, data=body, headers={
                    'Authorization': f'Bearer {key}',
                    'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=1800) as r:
                obj = json.loads(r.read().decode('utf-8'))
            break
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503):
                print(f'attempt {attempt}: HTTP {exc.code}, sleep', flush=True)
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


def lint_alignment(storyboard: str, code: str) -> dict:
    tags = set(re.findall(r'\[([A-Z_]+)\]', storyboard))
    markers = set(re.findall(r'PATTERN:\s*([A-Z_]+)', code))
    inter = tags & markers
    return {
        'storyboard_tags': sorted(tags),
        'code_markers': sorted(markers),
        'alignment': round(len(inter) / len(tags), 3) if tags else None,
        'missing_in_code': sorted(tags - markers)}


def render(case: Path, out_name: str) -> bool:
    r = subprocess.run(['node', 'render.mjs', '--clip', f'--out={out_name}'],
                       cwd=str(case), capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=10800)
    if r.returncode != 0:
        print('RENDER FAIL:', (r.stderr or '')[-800:])
    return r.returncode == 0


def main() -> int:
    model = sys.argv[1]
    subdir = sys.argv[2] if len(sys.argv) > 2 else model
    effort_arg = sys.argv[3] if len(sys.argv) > 3 else None
    case = BASE / 'case-c' / subdir
    out = case / model
    out.mkdir(parents=True, exist_ok=True)
    guide = (case / 'ANIMATION_GUIDE.md').read_text(encoding='utf-8')
    demo = (case / 'src' / 'scenes' / 'demo.js').read_text(encoding='utf-8')

    # phase 1: storyboard (skip if a good one already exists)
    sb_path = out / 'STORYBOARD.md'
    if sb_path.exists() and len(sb_path.read_text(encoding='utf-8')) >= 300:
        storyboard = sb_path.read_text(encoding='utf-8')
        print(f'[{model}] phase 1 SKIPPED (resume): {len(storyboard)} chars')
    else:
        print(f'[{model}] phase 1 storyboard...')
        sb_raw, m1 = call(model, [
            {'role': 'system', 'content': PHASE1_SYS},
            {'role': 'user', 'content':
                f'# ANIMATION_GUIDE.md\n\n{guide}\n\n# Task\n\n{TASK}\n'}],
            65536)
        (out / 'phase1_meta.json').write_text(
            json.dumps(m1, ensure_ascii=False, indent=1), encoding='utf-8')
        storyboard = fenced(sb_raw, ('markdown', 'md'))
        sb_path.write_text(storyboard + '\n', encoding='utf-8')
        (out / 'phase1_raw.txt').write_text(sb_raw, encoding='utf-8')
        print(f'[{model}] storyboard {len(storyboard)} chars meta={m1}')
        if len(storyboard) < 300:
            print('storyboard too short - abort')
            return 1

    # phase 2: code (own storyboard + demo format ref)
    # effort: GLM default (max) lands big code deliverables; 'high' was
    # observed burning the whole budget in reasoning with zero content.
    # For luna, an explicit effort can be passed (e.g. 'high') to test
    # whether deeper reasoning closes its realization gap.
    p2_effort = effort_arg if model != 'glm' else None
    print(f'[{model}] phase 2 code (effort={p2_effort})...')
    code_raw, m2 = call(model, [
        {'role': 'system', 'content': PHASE2_SYS},
        {'role': 'user', 'content':
            f'# ANIMATION_GUIDE.md\n\n{guide}\n\n'
            f'# Your phase-1 storyboard (implement THIS)\n\n{storyboard}\n\n'
            f'# src/scenes/demo.js (format reference only)\n\n'
            f'```javascript\n{demo}\n```\n'}],
        65536, effort=p2_effort)
    (out / 'phase2_meta.json').write_text(
        json.dumps(m2, ensure_ascii=False, indent=1), encoding='utf-8')
    code = fenced(code_raw, ('javascript', 'js'))
    (out / 'phase2_raw.txt').write_text(code_raw, encoding='utf-8')
    print(f'[{model}] code {len(code)} chars meta={m2}')
    if len(code) < 500:
        print('no code extracted - abort')
        return 1

    # install
    (case / 'src' / 'scenes' / 'chase_meet.js').write_text(
        code + '\n', encoding='utf-8')
    m = re.search(r'duration\s*[:=]\s*([\d.]+).*?bpm\s*[:=]\s*(\d+)',
                  code, re.S)
    dur, bpm = (float(m.group(1)), int(m.group(2))) if m else (20.0, 120)
    (case / 'src' / 'config.js').write_text(
        '// config.js: set by case_c pipeline.\n'
        f'const PROJECT = {{ duration: {dur:g}, bpm: {bpm}, offset: 0 }};\n',
        encoding='utf-8')
    html = (case / 'studio.html').read_text(encoding='utf-8')
    (case / 'studio.html').write_text(
        html.replace('src/scenes/demo.js', 'src/scenes/chase_meet.js'),
        encoding='utf-8')

    # lint
    align = lint_alignment(storyboard, code)
    (out / 'alignment.json').write_text(
        json.dumps(align, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'[{model}] alignment={align["alignment"]} '
          f'missing={align["missing_in_code"]}')

    # render + sheet
    ok = render(case, f'out/{model}_chase_meet.mp4')
    if not ok:
        return 1
    frames = video_qa.extract_keyframes(
        case / 'out' / f'{model}_chase_meet.mp4',
        case / 'out' / 'sheet_frames', count=8, tool_root=ROOT)
    sheet = video_qa.create_contact_sheet(
        frames, case / 'out' / f'{model}_chase_sheet.png', tool_root=ROOT)
    print(f'[{model}] DONE video + {sheet}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
