import os
#!/usr/bin/env python3
"""Probe: two-phase GLM call with thinking ENABLED.
Phase 1 = storyboard only (small deliverable -> bounded rumination).
max_tokens 65536 headroom so thinking can FINISH and content can start.
"""
from __future__ import annotations
import json
import time
import urllib.request
from pathlib import Path

CASE = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103'
            r'\base-compare\case-a')
OUT = CASE / 'glm_v2'
OUT.mkdir(exist_ok=True)
API = 'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions'
KEY = 'os.environ.get('GLM_API_KEY','')'
TASK = ("Read ANIMATION_GUIDE.md, then make a 15-second video of Clawd "
        "trying to catch a butterfly.")

SYSTEM = (
    "You are a coding animator working inside the ClaudeAnimationBase "
    "runtime (p5.js + p5.brush, hand-painted 2D cartoons). Follow the "
    "guide's workflow. THIS CALL IS PHASE 1 ONLY: produce the "
    "STORYBOARD.md — nothing else. Do not write scene code yet; phase 2 "
    "(a separate call) will write src/scenes code from your storyboard. "
    "Respond with EXACTLY one ```markdown fenced block: logline, world, "
    "motif, Clawd's arc, shots with start-end times, transitions at "
    "every seam, and reads with their own start-end times, bpm choice.")


def call() -> dict:
    guide = (CASE / 'ANIMATION_GUIDE.md').read_text(encoding='utf-8')
    body = json.dumps({
        'model': 'glm-5.3',
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content':
                f'# ANIMATION_GUIDE.md\n\n{guide}\n\n# Task\n\n{TASK}\n'},
        ],
        'temperature': 0.7,
        'max_tokens': 65536,
    }).encode('utf-8')
    req = urllib.request.Request(
        API, data=body, headers={
            'Authorization': f'Bearer {KEY}',
            'Content-Type': 'application/json'})
    t0 = time.time()
    for attempt in range(60):
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                obj = json.loads(r.read().decode('utf-8'))
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                time.sleep(90)
                continue
            raise
    msg = obj['choices'][0]['message']
    content = msg.get('content') or ''
    finish = obj['choices'][0].get('finish_reason')
    usage = obj.get('usage')
    meta = {'secs': round(time.time() - t0, 1), 'finish': finish,
            'usage': usage, 'model': obj.get('model'),
            'content_chars': len(content)}
    (OUT / 'phase1_meta.json').write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'phase1_storyboard.md').write_text(content, encoding='utf-8')
    print(json.dumps(meta, ensure_ascii=False))
    return meta


if __name__ == '__main__':
    call()
