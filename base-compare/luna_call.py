import os
#!/usr/bin/env python3
"""Case B Base run: one-shot gpt-6-luna (codex-proxy) over the same
ClaudeAnimationBase context GLM got for Case A. Same task prompt,
same guide, same demo.js format reference. Reasoning left ON (default).
"""
from __future__ import annotations
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

CASE = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103'
            r'\base-compare\case-b')
OUT_DIR = CASE / 'luna'
OUT_DIR.mkdir(exist_ok=True)
API = 'http://127.0.0.1:8080/v1/chat/completions'
KEY = 'os.environ.get('LUNA_API_KEY','')'
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
    "documented in the guide. Set no globals; duration/bpm go in "
    "config.js — state the exact config.js line as a JS comment at the "
    "top of the file."
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
        'model': 'gpt-6-luna',
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': user},
        ],
        'temperature': 1.0,
        'max_completion_tokens': 65536,
    }).encode('utf-8')
    req = urllib.request.Request(
        API, data=body, headers={
            'Authorization': f'Bearer {KEY}',
            'Content-Type': 'application/json'})
    t0 = time.time()
    for attempt in range(30):
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                obj = json.loads(r.read().decode('utf-8'))
            break
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503):
                time.sleep(60)
                continue
            raise
    msg = obj['choices'][0]['message']
    content = msg.get('content') or ''
    meta = {'secs': round(time.time() - t0, 1),
            'finish': obj['choices'][0].get('finish_reason'),
            'usage': obj.get('usage'), 'model': obj.get('model'),
            'content_chars': len(content)}
    (OUT_DIR / 'luna_call_meta.json').write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT_DIR / 'luna_raw_response.txt').write_text(content, encoding='utf-8')
    print(json.dumps(meta, ensure_ascii=False))
    return content


def extract(text: str) -> tuple[str, str]:
    blocks = re.findall(r'```(\w+)?\s*\n(.*?)```', text, re.S)
    md = js = ''
    for lang, body in blocks:
        if not md and (lang in ('markdown', 'md')
                       or body.lstrip().startswith('#')):
            md = body
        elif not js and (lang in ('javascript', 'js') or 'shots(' in body):
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
        print('NO SCENE CODE EXTRACTED — inspect luna_raw_response.txt')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
