#!/usr/bin/env python3
"""ISD-L04K repair round: send current HTML + failing selftest + revised spec
to sol (effort=high) for a focused fix. Outputs kitchen_lab.html (replaced,
backup kept as kitchen_lab_v1.html)."""
from __future__ import annotations
import json, re, shutil, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
from pipeline.llm import call  # noqa: E402


def load_usage() -> dict:
    p = HERE / 'usage.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'calls': []}


def main() -> int:
    html = (HERE / 'kitchen_lab.html').read_text(encoding='utf-8')
    qa = (HERE / 'qa_result.json').read_text(encoding='utf-8') if (HERE / 'qa_result.json').exists() else '{}'
    lab = (HERE / 'lab.yaml').read_text(encoding='utf-8')
    messages = [
        {'role': 'system', 'content': (
            'You are the same senior front-end engineer who built this teaching lab. '
            'A QA harness ran your page: the self-test FAILED and several QA hook APIs '
            'are missing. Apply a focused repair to the SAME single-file HTML. Keep '
            'everything that already works (visual style, layout, three-layer feedback, '
            'A/B snapshots, exports). Output EXACTLY one fenced ```html block with the '
            'complete repaired file and nothing else.')},
        {'role': 'user', 'content': (
            '# 当前 kitchen_lab.html（你上一轮的产物，视觉QA已通过——不要改风格）\n\n'
            f'```html\n{html}\n```\n\n'
            '# QA 结果（失败项）\n\n```json\n{qa}\n```\n\n'
            '# 修订后的实验合同（折返计数规则重定义）\n\n```yaml\n{lab}\n```\n\n'
            '# 修复清单（按序）\n\n'
            '1. **折返计数规则重写**（根因：旧实现用固定分组序列，moveCount恒为4，与布局无关）：'
            '按合同 errand_task 新规则——距离≤1.0m走"一次取齐"短序列，否则走"分批3趟往返"序列；'
            'sink/prep/stove 同墙且间隙≤0.05m 构成连续作业链，链内步进不计数；'
            '自检断言：基线A=6、基线B=2，必须算得出。\n'
            '2. **补齐 QA 钩子 API**（页面加载完成后设 true，供同源测试iframe调用）：'
            'window.__LAB_READY__=true；window.__LAB_SET_LEVEL__(n)；'
            'window.__LAB_LOAD_BASELINE__(\'A\'|\'B\')；window.__LAB_EVALUATE__() 返回完整 report 对象；'
            'window.__LAB_CONSOLE_ERRORS__（数组，页面启动起捕获 console.error）；'
            'window.__LAB_SELFTEST__() 保持并确保6条断言全过。\n'
            '3. 基线A/B 的预置布局要精确：A=冰箱在西墙中段对侧、操作链沿北墙连续排布；'
            'B=同一链 + 冰箱紧贴链头（北墙最西侧）。\n'
            '4. 动画小人路径按新序列走；handsFullMoves 段落路径用更粗虚线区分。\n\n'
            '只输出修复后的完整 ```html 代码块。')},
    ]
    t0 = time.time()
    content, meta = call('sol', messages, effort='high', temperature=1.0)
    secs = round(time.time() - t0, 1)
    (HERE / 'sol_repair_raw.txt').write_text(content, encoding='utf-8')
    usage = load_usage()
    usage['calls'].append({'purpose': 'kitchen_lab.html repair round 1',
                           'model': 'gpt-6.1-sol', 'effort': 'high', 'secs': secs,
                           'usage': meta.get('usage'), 'finish': meta.get('finish'),
                           'response_chars': len(content),
                           'exact_tokens': bool(meta.get('usage', {}).get('total_tokens'))})
    (HERE / 'usage.json').write_text(json.dumps(usage, ensure_ascii=False, indent=1), encoding='utf-8')
    m = re.search(r'```html\s*\n(.*?)```', content, re.S)
    if not m:
        print('NO HTML BLOCK IN REPAIR — inspect sol_repair_raw.txt')
        return 1
    shutil.copy2(HERE / 'kitchen_lab.html', HERE / 'kitchen_lab_v1.html')
    (HERE / 'kitchen_lab.html').write_text(m.group(1).strip() + '\n', encoding='utf-8')
    print(json.dumps({'secs': secs, 'html_chars': len(m.group(1)),
                      'finish': meta.get('finish'),
                      'tokens': (meta.get('usage') or {}).get('total_tokens')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
