#!/usr/bin/env python3
"""ISD-L04 QA 门禁：本地 http + chrome headless。

用法: D:/ComfyUI_windows_portable/python_embeded/python.exe qa_run.py
PASS 标准: ready + 0 控制台错误 + selftest 8/8 + 基线A/B可载入评估 + B夜起<A + 确定性。
"""
from __future__ import annotations
import http.server, json, re, socketserver, subprocess, sys, threading, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = 8479
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def log_message(self, *a):
        pass


def shot(url: str, out: str, w=1600, h=1000, budget=12000):
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-first-run',
                    '--hide-scrollbars', f'--user-data-dir={HERE}/.qa_profile-shot-{uuid.uuid4().hex}',
                    f'--virtual-time-budget={budget}', f'--screenshot={out}',
                    f'--window-size={w},{h}', url],
                   capture_output=True, timeout=180)


def dump(url: str, budget=60000) -> str:
    r = subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-first-run',
                        '--hide-scrollbars', f'--user-data-dir={HERE}/.qa_profile-dump-{uuid.uuid4().hex}',
                        f'--virtual-time-budget={budget}', '--dump-dom', url],
                       capture_output=True, timeout=240, text=True,
                       encoding='utf-8', errors='replace')
    return r.stdout or ''


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as srv:
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        base = f'http://127.0.0.1:{PORT}'
        shot(f'{base}/unit_lab.html', str(HERE / 'qa_initial.png'))
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
    steps = dict(data.get('steps') or [])
    st = data.get('selftest') or {}
    errors = data.get('errors') or []
    ok = (steps.get('ready') is True
          and steps.get('consoleErrors') == []
          and steps.get('selftest') == 'PASS'
          and st.get('passed') == 8 and not st.get('failed')
          and steps.get('baselineA_loaded') is True
          and steps.get('baselineB_loaded') is True
          and steps.get('nightB_lt_A') is True
          and steps.get('determinism') is True
          and not errors)
    print(json.dumps({'pass': ok, 'steps': steps,
                      'selftest': {k: st.get(k) for k in ('passed', 'failed', 'total')},
                      'evaluateA': data.get('evaluateA'),
                      'evaluateB': data.get('evaluateB'),
                      'errors': errors}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
