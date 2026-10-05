import os
#!/usr/bin/env python3
"""Probe codex-proxy / gpt-6-luna channel for Case B."""
import json
import urllib.request

KEY = 'os.environ.get('LUNA_API_KEY','')'
body = json.dumps({
    'model': 'gpt-6-luna',
    'messages': [{'role': 'user', 'content': 'Reply with exactly: LUNA-OK'}],
    'max_completion_tokens': 2000,
}).encode()
for path in ('/v1/chat/completions', '/chat/completions'):
    try:
        req = urllib.request.Request(
            f'http://127.0.0.1:8080{path}', data=body, headers={
                'Authorization': f'Bearer {KEY}',
                'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=120) as r:
            obj = json.loads(r.read().decode())
        msg = obj['choices'][0]['message']
        print(path, '->', json.dumps({
            'model': obj.get('model'),
            'content': (msg.get('content') or '')[:60],
            'usage': obj.get('usage')}, ensure_ascii=False)[:400])
        break
    except Exception as exc:
        print(path, 'FAILED:', repr(exc)[:200])
