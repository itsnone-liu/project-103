import os
#!/usr/bin/env python3
"""Case A Base run: one-shot GLM 5.3 call over the ClaudeAnimationBase
context (same inputs Opus gets: ANIMATION_GUIDE.md + demo.js as format
example + the original task prompt). Writes GLM's scene + storyboard to
disk for rendering. Base test = no extra hints beyond the guide."""
from __future__ import annotations
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

CASE = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103'
            r'\base-compare\case-a')
OUT_DIR = CASE / 'glm'
OUT_DIR.mkdir(exist_ok=True)
API = 'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions'
KEY = 'os.environ.get('GLM_API_KEY','')'

TASK_PROMPT = ("Read ANIMATION_GUIDE.md, then make a 15-second video of "
               "Clawd trying to catch a butterfly.")

SYSTEM = (
    "You are a coding animator working inside the ClaudeAnimationBase "
    "runtime (p5.js + p5.brush, hand-painted 2D cartoons). You have read "
    "the repository's ANIMATION_GUIDE.md (provided below in full) and the "
    "existing example scene src/scenes/demo.js (provided below as a format "
    "reference — do not copy its content). "
    "Follow the guide's rules and workflow: storyboard first, then one "
    "scene file wrapped in an IIFE ending with shots([...]), transitions "
    "at every seam, reads with time to land, no text, brush strokes only. "
    "Respond with EXACTLY two fenced code blocks and nothing else:\n"
    "1) ```markdown fenced block: the full STORYBOARD.md (logline, world, "
    "motif, Clawd's arc, shots with transitions and reads with times).\n"
    "2) ```javascript fenced block: the complete contents of "
    "src/scenes/butterfly.js — self-contained, only using the engine API "
    "documented in the guide (paint, inkLine, clawd, emotions, jump, "
    "camBegin/camEnd, iris, brushWipe, shots, LOOPS etc.). Set no globals; "
    "duration/bpm go in config.js — state the exact config.js line as a "
    "JS comment at the top of the file."
)


def call() -> str:
    guide = (CASE / 'ANIMATION_GUIDE.md').read_text(encoding='utf-8')
    demo = (CASE / 'src' / 'scenes' / 'demo.js').read_text(encoding='utf-8')
    user = (
        f'# ANIMATION_GUIDE.md\n\n{guide}\n\n'
        f'# src/scenes/demo.js (format reference only)\n\n'
        f'```javascript\n{demo}\n```\n\n'
        f'# Task\n\n{TASK_PROMPT}\n')
    body = json.dumps({
        'model': 'glm-5.3',
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': user},
        ],
        'temperature': 0.7,
        'max_tokens': 32768,
        'thinking': {'type': 'disabled'},
    }).encode('utf-8')
    req = urllib.request.Request(
        API, data=body, headers={
            'Authorization': f'Bearer {KEY}',
            'Content-Type': 'application/json'})
    t0 = time.time()
    last_err = None
    for attempt in range(60):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                obj = json.loads(r.read().decode('utf-8'))
            break
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code == 429:
                time.sleep(90)
                continue
            raise
    else:
        raise RuntimeError(f'GLM API still 429 after retries: {last_err}')
    usage = obj.get('usage')
    content = obj['choices'][0]['message']['content']
    (OUT_DIR / 'glm_raw_response.txt').write_text(
        content, encoding='utf-8')
    meta = {'secs': round(time.time() - t0, 1),
            'usage': usage, 'model': obj.get('model')}
    (OUT_DIR / 'glm_call_meta.json').write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(meta, ensure_ascii=False))
    return content


def extract(text: str) -> tuple[str, str]:
    blocks = re.findall(r'```(\w+)?\s*\n(.*?)```', text, re.S)
    md = js = ''
    for lang, body in blocks:
        if not md and (lang in ('markdown', 'md') or body.lstrip().startswith('#')):
            md = body
        elif not js and lang in ('javascript', 'js') or (not js and 'shots(' in body):
            js = body
    return md, js


def main() -> int:
    text = call()
    md, js = extract(text)
    if md:
        (OUT_DIR / 'STORYBOARD.md').write_text(md.strip() + '\n',
                                               encoding='utf-8')
    if js:
        (OUT_DIR / 'butterfly.js').write_text(js.strip() + '\n',
                                              encoding='utf-8')
    print(f'storyboard: {len(md)} chars; scene: {len(js)} chars')
    if not js:
        print('NO SCENE CODE EXTRACTED — inspect glm_raw_response.txt')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
