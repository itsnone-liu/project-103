#!/usr/bin/env python3
"""sol 截断续写（proxy ~58k 截断时）：把最后未完成文件续完并拼接。

用法：先 sol_generate.py 得到 sol_raw.txt；若截断（finish=stop 但无闭合```），
运行本脚本：读取 unit_lab.html 当前内容，请求 sol 从该内容末尾继续输出剩余部分，
直到 </html>，拼接写回。可重复运行。
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
from pipeline.llm import call  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    target = HERE / 'unit_lab.html'
    if not target.exists():
        print('unit_lab.html not found — run sol_generate.py first')
        return 1
    cur = target.read_text(encoding='utf-8').rstrip()
    if cur.rstrip().endswith('</html>'):
        print('already complete')
        return 0
    brief = (HERE / 'brief.md').read_text(encoding='utf-8')
    tail = cur[-6000:]
    messages = [
        {'role': 'system', 'content': (
            'You are continuing a truncated self-contained HTML teaching-lab file. '
            'Output ONLY the continuation text (no fences, no commentary, no repeat of '
            'existing content). Continue exactly from where the file stops, complete the '
            'file per the original brief, and end with </html>.')},
        {'role': 'user', 'content': (
            f'# 原始简报（节选要求不变）\n{brief[:8000]}\n\n'
            f'# 当前文件末尾（从此处继续，不得重复任何已有行）\n```\n{tail}\n```\n\n'
            '继续输出剩余全部内容直到 </html>。只输出续写内容本身。')},
    ]
    t0 = time.time()
    content, meta = call('sol', messages, effort='high', temperature=0.7)
    secs = round(time.time() - t0, 1)
    (HERE / 'sol_continue_raw.txt').write_text(content, encoding='utf-8')
    spliced = cur + '\n' + content.strip()
    # 去除 sol 可能重复的结尾片段（简单重叠消解：若续写开头与现文件尾部有≥40字符重叠则去掉一份）
    for k in range(min(2000, len(cur), len(content)), 40, -1):
        if cur.endswith(content.strip()[:k]):
            spliced = cur + content.strip()[k:]
            break
    if not spliced.rstrip().endswith('</html>'):
        spliced += '\n</html>'
    target.write_text(spliced + '\n', encoding='utf-8')

    usage_p = HERE / 'usage.json'
    usage = json.loads(usage_p.read_text(encoding='utf-8')) if usage_p.exists() else {'calls': []}
    usage['calls'].append({'purpose': 'unit_lab.html continuation splice',
                           'model': 'gpt-6.1-sol', 'effort': 'high', 'secs': secs,
                           'finish': meta.get('finish'), 'response_chars': len(content),
                           'exact_tokens': bool((meta.get('usage') or {}).get('total_tokens'))})
    usage_p.write_text(json.dumps(usage, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'secs': secs, 'continue_chars': len(content),
                      'total_chars': len(spliced), 'finish': meta.get('finish')},
                     ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
