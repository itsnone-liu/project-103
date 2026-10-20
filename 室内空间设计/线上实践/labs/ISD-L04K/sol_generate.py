#!/usr/bin/env python3
"""ISD-L04K 厨房实验 · sol 高推理代码生成基建（Level A 单文件 HTML）。

用法（在 103 仓库根目录）:
  D:/ComfyUI_windows_portable/python_embeded/python.exe 室内空间设计/线上实践/labs/ISD-L04K/sol_generate.py
产出（同目录）:
  kitchen_lab.html   sol 生成的单文件实验页
  sol_raw.txt        原始响应
  usage.json         token/耗时审计（exact 优先，否则记 chars 标记估算）
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
from pipeline.llm import call  # noqa: E402  gpt-6.1-sol @ codex-proxy, 45min timeout, retry policy built-in


def load_usage() -> dict:
    p = HERE / 'usage.json'
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return {'calls': []}


def main() -> int:
    brief = (HERE / 'brief.md').read_text(encoding='utf-8')
    lab = (HERE / 'lab.yaml').read_text(encoding='utf-8')
    messages = [
        {'role': 'system', 'content': (
            'You are a senior front-end engineer building a university-level '
            'interactive teaching lab as ONE self-contained HTML file (inline CSS+JS, '
            'no external dependencies, no network). You write clean vanilla JS with a '
            'deterministic rule engine fully separated from rendering, so the same '
            'scene JSON always yields the same metrics. Follow the brief exactly; '
            'output EXACTLY one fenced ```html code block and nothing else. '
            'All UI text in Simplified Chinese.')},
        {'role': 'user', 'content': (
            f'# 实验合同 lab.yaml\n\n```yaml\n{lab}\n```\n\n# 实现简报 brief.md\n\n{brief}\n\n'
            '# 任务\n\n按简报实现完整单文件 kitchen_lab.html。只输出一个 ```html 代码块。')},
    ]
    t0 = time.time()
    content, meta = call('sol', messages, effort='high', temperature=1.0)
    secs = round(time.time() - t0, 1)
    (HERE / 'sol_raw.txt').write_text(content, encoding='utf-8')

    usage = load_usage()
    usage['calls'].append({
        'purpose': 'kitchen_lab.html v1 generation',
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
    (HERE / 'kitchen_lab.html').write_text(html, encoding='utf-8')
    print(json.dumps({'secs': secs, 'html_chars': len(html),
                      'finish': meta.get('finish'),
                      'tokens': (meta.get('usage') or {}).get('total_tokens')},
                     ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
