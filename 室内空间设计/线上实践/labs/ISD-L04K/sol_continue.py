#!/usr/bin/env python3
"""Continue a truncated sol output: send the cut-off text, ask for the exact
continuation, splice, syntax-check by loading in chrome via qa_run."""
from __future__ import annotations
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
from pipeline.llm import call  # noqa: E402


def main() -> int:
    raw = (HERE / 'sol_repair_raw.txt').read_text(encoding='utf-8')
    body = raw.split('```html', 1)[1].lstrip('\n')
    tail = body[-3500:]
    messages = [
        {'role': 'system', 'content': (
            'You were writing a single-file HTML teaching lab and your output was '
            'CUT OFF mid-code. Continue EXACTLY from the cut point to finish the '
            'file. Output ONLY the continuation (raw HTML/JS/CSS text, no fences, '
            'no commentary, no repetition of anything before the cut). End with '
            '</body></html>.')},
        {'role': 'user', 'content': (
            'The file so far ends with:\n\n---CUT---\n' + tail + '\n---CUT---\n\n'
            'Continue from the character immediately after the cut. Remember the '
            'self-test must assert baseline A moveCount=6 and baseline B moveCount=2 '
            'under the chain rule (adjacent sink/prep/stove on the same wall with '
            'gap<=0.05m form one chain; in-chain steps count as 0 moves). Finish '
            'all remaining functions, the init/boot sequence, and close the document.')},
    ]
    t0 = time.time()
    content, meta = call('sol', messages, effort='high', temperature=1.0)
    secs = round(time.time() - t0, 1)
    (HERE / 'sol_continue_raw.txt').write_text(content, encoding='utf-8')
    u = json.loads((HERE / 'usage.json').read_text(encoding='utf-8'))
    u['calls'].append({'purpose': 'repair continue (splice)', 'model': 'gpt-6.1-sol',
                       'effort': 'high', 'secs': secs, 'usage': meta.get('usage'),
                       'finish': meta.get('finish'), 'response_chars': len(content),
                       'exact_tokens': bool((meta.get('usage') or {}).get('total_tokens'))})
    (HERE / 'usage.json').write_text(json.dumps(u, ensure_ascii=False, indent=1), encoding='utf-8')
    # splice: strip any accidental fence, append
    cont = content
    for junk in ('```html', '```'):
        cont = cont.replace(junk, '')
    full = body.rstrip() + '\n' + cont.strip() + '\n'
    if not full.rstrip().endswith('</html>'):
        full = full.rstrip() + '\n</body>\n</html>\n'
    (HERE / 'kitchen_lab.html').write_text(full, encoding='utf-8')
    print(json.dumps({'secs': secs, 'spliced_chars': len(full),
                      'finish': meta.get('finish')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
