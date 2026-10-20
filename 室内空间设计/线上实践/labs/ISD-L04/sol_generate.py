#!/usr/bin/env python3
"""ISD-L04 全户型实验 · sol 高推理代码生成（Level A 单文件 HTML）。"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
from pipeline.llm import call  # noqa: E402


def load_usage() -> dict:
    p = HERE / 'usage.json'
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return {'calls': []}


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    brief = (HERE / 'brief.md').read_text(encoding='utf-8')
    lab = (HERE / 'lab.yaml').read_text(encoding='utf-8')
    messages = [
        {'role': 'system', 'content': (
            'You are a senior front-end engineer building a university-level '
            'interactive teaching lab as ONE self-contained HTML file (inline CSS+JS, '
            'no external dependencies, no network). You write clean vanilla JS with a '
            'deterministic pure-function rule engine fully separated from rendering, so '
            'the same state JSON always yields the same report JSON. Follow the brief '
            'exactly; output EXACTLY one fenced ```html code block and nothing else. '
            'All UI text in Simplified Chinese. Be extremely economical with code size.')},
        {'role': 'user', 'content': (
            f'# 实验合同 lab.yaml\n\n```yaml\n{lab}\n```\n\n# 实现简报 brief.md\n\n{brief}\n\n'
            '# 任务\n\n按简报实现完整单文件 unit_lab.html（文件内 <title> U90全户型功能组织与动线冲突）。'
            '所有冻结数据表照抄；8条自检必须全部可过。只输出一个 ```html 代码块。')},
    ]
    t0 = time.time()
    content, meta = call('sol', messages, effort='high', temperature=1.0)
    secs = round(time.time() - t0, 1)
    (HERE / 'sol_raw.txt').write_text(content, encoding='utf-8')

    usage = load_usage()
    usage['calls'].append({
        'purpose': 'unit_lab.html v1 generation',
        'model': 'gpt-6.1-sol', 'effort': 'high',
        'secs': secs, 'usage': meta.get('usage'),
        'finish': meta.get('finish'), 'response_chars': len(content),
        'exact_tokens': bool(meta.get('usage', {}).get('total_tokens')),
    })
    (HERE / 'usage.json').write_text(
        json.dumps(usage, ensure_ascii=False, indent=1), encoding='utf-8')

    m = re.search(r'```html\s*\n(.*?)```', content, re.S)
    if not m:
        print('NO HTML BLOCK EXTRACTED — inspect sol_raw.txt')
        return 1
    html = m.group(1).strip() + '\n'
    (HERE / 'unit_lab.html').write_text(html, encoding='utf-8')
    print(json.dumps({'secs': secs, 'html_chars': len(html),
                      'finish': meta.get('finish'),
                      'tokens': (meta.get('usage') or {}).get('total_tokens')},
                     ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
