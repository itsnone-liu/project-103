#!/usr/bin/env python3
"""ISD-L04K QA runner: local http server + chrome headless dump-dom + screenshots.

Steps:
  1. serve lab dir on 127.0.0.1:8477
  2. chrome headless loads qa_harness.html, dumps DOM -> parse QA_RESULT_JSON
  3. screenshots: lab initial view + harness result view
Exit code 0 iff selftest passed, determinism true, no console errors.
"""
from __future__ import annotations
import http.server, json, re, socketserver, subprocess, sys, threading, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = 8477
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def log_message(self, *a):
        pass


def shot(url: str, out: str, w=1440, h=900, budget=9000):
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-first-run',
                    '--hide-scrollbars', f'--user-data-dir={HERE}/.qa_profile-shot-{uuid.uuid4().hex}',
                    f'--virtual-time-budget={budget}', f'--screenshot={out}',
                    f'--window-size={w},{h}', url],
                   capture_output=True, timeout=120)


def dump(url: str, budget=45000) -> str:
    r = subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-first-run',
                        '--hide-scrollbars', f'--user-data-dir={HERE}/.qa_profile-dump-{uuid.uuid4().hex}',
                        f'--virtual-time-budget={budget}', '--dump-dom', url],
                       capture_output=True, timeout=180, text=True,
                       encoding='utf-8', errors='replace')
    return r.stdout or ''


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as srv:
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        base = f'http://127.0.0.1:{PORT}'
        # initial view screenshot (level 1)
        shot(f'{base}/kitchen_lab.html', str(HERE / 'qa_initial.png'))
        # programmatic harness
        dom = dump(f'{base}/qa_harness.html')
        m = re.search(r'QA_RESULT_JSON:(\{.*?\})</pre>', dom, re.S)
        if not m:
            (HERE / 'qa_dom.txt').write_text(dom, encoding='utf-8')
            print('NO QA RESULT IN DOM — see qa_dom.txt')
            return 2
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            (HERE / 'qa_dom.txt').write_text(dom, encoding='utf-8')
            print('QA JSON parse failed — see qa_dom.txt')
            return 2
        (HERE / 'qa_result.json').write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        srv.shutdown()
    st = data.get('selftest') or {}
    steps = dict(data.get('steps', []))
    ok = (steps.get('selftest') == 'PASS'
          and steps.get('challengeEnabled') is True
          and steps.get('challengeActive') is True
          and steps.get('determinism') is True
          and not data.get('errors')
          and not (steps.get('consoleErrors')))
    print(json.dumps({'pass': ok, 'steps': steps,
                      'selftest': st, 'errors': data.get('errors'),
                      'evaluate': data.get('evaluate', {}).get('errand')},
                     ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
