import os
#!/usr/bin/env python3
"""Probe: does codex-proxy honor reasoning_effort for gpt-6-luna?"""
import json
import time
import urllib.request

API = 'http://127.0.0.1:8080/v1/chat/completions'
KEY = 'os.environ.get('LUNA_API_KEY','')'

for effort in (None, 'low', 'high'):
    payload = {'model': 'gpt-6-luna',
               'messages': [{'role': 'user',
                             'content': 'A bat and ball cost $1.10 total; '
                                        'the bat costs $1.00 more than the '
                                        'ball. How much is the ball? Answer '
                                        'in one sentence.'}],
               'max_completion_tokens': 4096}
    if effort:
        payload['reasoning_effort'] = effort
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={'Authorization': f'Bearer {KEY}',
                 'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            obj = json.loads(r.read().decode())
        u = obj.get('usage', {})
        det = (u.get('completion_tokens_details') or {})
        msg = obj['choices'][0]['message']
        ans = (msg.get('content') or '')[:60].replace('\n', ' ')
        print(f"effort={effort!s:5} -> {time.time()-t0:.1f}s "
              f"reasoning={det.get('reasoning_tokens')} "
              f"completion={u.get('completion_tokens')} ans={ans!r}")
    except urllib.error.HTTPError as exc:
        print(f'effort={effort!s:5} -> HTTP {exc.code}: '
              f'{exc.read().decode()[:200]}')
    time.sleep(2)
