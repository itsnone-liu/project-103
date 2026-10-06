#!/usr/bin/env python3
"""Review loop v1 (Stage D): render -> vision critique -> one repair -> v2.

Usage: python review_loop.py <case-dir> <glm|luna>
  <case-dir> contains src/scenes/butterfly.js (installed), out/<tag>_video.mp4
Writes: review/ (backup v1 code, sheets, critique json, repair meta, report)
"""
from __future__ import annotations
import base64
import http.client
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
COMP = (ROOT / 'runs' / 'architecture-smoke' / 'node_modules' /
        '@remotion' / 'compositor-win32-x64-msvc')
import os  # noqa: E402
os.environ['PATH'] = str(COMP) + os.pathsep + os.environ['PATH']
sys.path.insert(0, str(ROOT))
import p103.video_qa as video_qa  # noqa: E402

VISION_API = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
VISION_KEY = 'sk-50103d72d57446bcaa3b1bce37609c07'
VISION_MODEL = 'qwen3-vl-plus'
GLM_API = 'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions'
GLM_KEY = os.environ.get('GLM_API_KEY', '')
LUNA_API = 'http://127.0.0.1:8080/v1/chat/completions'
LUNA_KEY = os.environ.get('LUNA_API_KEY', '')

CHECKLIST = (
    "1.主体是否明确 2.每个read是否清楚 3.是否同时出现过多信息 "
    "4.motion是否自然 5.transition是否生硬 6.是否存在视觉遮挡 "
    "7.是否存在无意义motion 8.scene continuity是否成立 "
    "9.关键事件是否被motion强化(有无冻结/强调/停留) 10.整体是否低于参考质量")


def http_json(url: str, key: str, payload: dict, timeout: int,
              retry_on_429: bool = True) -> dict:
    body = json.dumps(payload).encode('utf-8')
    for attempt in range(40):
        try:
            req = urllib.request.Request(
                url, data=body, headers={
                    'Authorization': f'Bearer {key}',
                    'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as exc:
            if retry_on_429 and exc.code == 429:
                time.sleep(75)
                continue
            raise
        except (http.client.RemoteDisconnected, ConnectionError,
                TimeoutError, urllib.error.URLError) as exc:
            print(f'attempt {attempt}: transport {exc!r}', flush=True)
            time.sleep(60)
    raise RuntimeError('unreachable')


def extract_js(text: str) -> str:
    blocks = re.findall(r'```(?:javascript|js)?\s*\n(.*?)```', text, re.S)
    js = max(blocks, key=len) if blocks else ''
    return js.strip()


def extract_json(text: str) -> dict:
    m = re.search(r'\{.*\}', text, re.S)
    if not m:
        return {'verdict': 'revise', 'issues': [], 'note': 'unparseable',
                'raw': text[:500]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {'verdict': 'revise', 'issues': [], 'note': 'unparseable',
                'raw': text[:500]}


def vision_review(sheet_png: Path, storyboard: str, task: str) -> tuple[dict, dict]:
    b64 = base64.b64encode(sheet_png.read_bytes()).decode()
    prompt = (
        f"这是一段动画的8个关键帧拼图(按时间顺序)。任务: {task}\n"
        f"审查清单: {CHECKLIST}\n\n"
        f"该片的分镜表(STORYBOARD.md):\n{storyboard}\n\n"
        f"对照分镜表检查实际渲染结果,特别注意: 分镜承诺的视觉元素"
        f"(轨迹线/冻结强调/对比总结/角色区分等)是否真的出现在画面里。"
        f"仅输出一个JSON对象,不要其他文字:\n"
        f'{{"verdict": "pass" 或 "revise", '
        f'"issues": [{{"severity": "high|mid|low", "time": "大致秒数", '
        f'"dimension": "清单第几项", "problem": "问题描述", '
        f'"fix": "具体可执行的修改建议"}}], '
        f'"storyboard_alignment": "分镜承诺vs实际画面的一致性评价"}}')
    payload = {
        'model': VISION_MODEL,
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'image_url', 'image_url':
                    {'url': f'data:image/png;base64,{b64}'}},
                {'type': 'text', 'text': prompt},
            ]}],
        'max_tokens': 3000, 'temperature': 0.2}
    obj = http_json(VISION_API, VISION_KEY, payload, 180, retry_on_429=False)
    msg = obj['choices'][0]['message']
    content = msg.get('content') or ''
    return extract_json(content), {'usage': obj.get('usage'),
                                   'secs': None, 'raw': content[:300]}


def repair_call(model: str, storyboard: str, code: str,
                critique: dict) -> tuple[str, dict]:
    sysp = (
        "You are a coding animator in the ClaudeAnimationBase runtime. "
        "A rendered preview of your scene was reviewed against your "
        "storyboard by a critic. Revise the scene code to fix the issues. "
        "Rules: keep the same total duration and bpm; keep what works; "
        "only change what the critique requires; the file stays "
        "self-contained using only the documented engine API. Respond "
        "with EXACTLY one ```javascript fenced block containing the "
        "COMPLETE revised contents of src/scenes/butterfly.js.")
    user = (
        f'# STORYBOARD.md (your plan)\n\n{storyboard}\n\n'
        f'# CURRENT src/scenes/butterfly.js\n\n'
        f'```javascript\n{code}\n```\n\n'
        f'# Critic findings (JSON)\n\n'
        f'```json\n{json.dumps(critique, ensure_ascii=False, indent=1)}\n```\n\n'
        f'# Task\n\nFix the issues and output the complete revised file.')
    if model == 'glm':
        payload = {'model': 'glm-5.3',
                   'messages': [{'role': 'system', 'content': sysp},
                                {'role': 'user', 'content': user}],
                   'temperature': 1.0, 'max_tokens': 65536}
        t0 = time.time()
        obj = http_json(GLM_API, GLM_KEY, payload, 1800)
    else:
        payload = {'model': 'gpt-6-luna',
                   'messages': [{'role': 'system', 'content': sysp},
                                {'role': 'user', 'content': user}],
                   'temperature': 1.0, 'max_completion_tokens': 65536}
        t0 = time.time()
        obj = http_json(LUNA_API, LUNA_KEY, payload, 1800)
    msg = obj['choices'][0]['message']
    content = msg.get('content') or ''
    meta = {'secs': round(time.time() - t0, 1),
            'finish': obj['choices'][0].get('finish_reason'),
            'usage': obj.get('usage')}
    return content, meta


def render(case: Path, out_name: str) -> bool:
    r = subprocess.run(['node', 'render.mjs', '--clip', f'--out={out_name}'],
                       cwd=str(case), capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=7200)
    return r.returncode == 0


def main() -> int:
    case = Path(sys.argv[1])
    model = sys.argv[2]                      # glm | luna
    scene_name = sys.argv[3] if len(sys.argv) > 3 else 'butterfly'
    video_name = (sys.argv[4] if len(sys.argv) > 4
                  else f'{model}_video.mp4')
    task_desc = (sys.argv[5] if len(sys.argv) > 5
                 else 'Clawd追蝴蝶(15秒手绘动画)')
    tag = 'glm' if model == 'glm' else 'luna'
    rev = case / 'review'
    rev.mkdir(exist_ok=True)
    storyboard = (case / tag / 'STORYBOARD.md').read_text(encoding='utf-8')
    scene_path = case / 'src' / 'scenes' / f'{scene_name}.js'
    code = scene_path.read_text(encoding='utf-8')
    (rev / f'{scene_name}_v1.js').write_text(code, encoding='utf-8')
    video1 = case / 'out' / video_name

    # 1. keyframes + compact sheet
    frames = video_qa.extract_keyframes(
        video1, rev / 'frames_v1', count=8, tool_root=ROOT)
    sheet1 = video_qa.create_contact_sheet(
        frames, rev / 'sheet_v1.png', tool_root=ROOT)
    print(f'sheet v1: {sheet1}')

    # 2. vision review
    critique, vmeta = vision_review(sheet1, storyboard, task=task_desc)
    (rev / 'critique_v1.json').write_text(
        json.dumps(critique, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"critique verdict={critique.get('verdict')} "
          f"issues={len(critique.get('issues', []))}")
    if critique.get('verdict') == 'pass':
        print('review says PASS - no repair needed')
        return 0

    # 3. one repair round
    raw, rmeta = repair_call(model, storyboard, code, critique)
    (rev / 'repair_meta.json').write_text(
        json.dumps(rmeta, ensure_ascii=False, indent=1), encoding='utf-8')
    (rev / 'repair_raw.txt').write_text(raw, encoding='utf-8')
    js = extract_js(raw)
    if len(js) < 500:
        print(f'REPAIR FAILED (extracted {len(js)} chars)')
        return 1
    (case / 'src' / 'scenes' / 'butterfly.js').write_text(js + '\n',
                                                          encoding='utf-8')
    print(f'repair code: {len(js)} chars')

    # 4. re-render + v2 sheet
    video2_name = video_name.replace('.mp4', '_v2.mp4')
    if not render(case, f'out/{video2_name}'):
        print('v2 RENDER FAILED')
        return 1
    frames2 = video_qa.extract_keyframes(
        case / 'out' / video2_name, rev / 'frames_v2',
        count=8, tool_root=ROOT)
    sheet2 = video_qa.create_contact_sheet(
        frames2, rev / 'sheet_v2.png', tool_root=ROOT)

    # 5. second vision pass on v2 (for the report only, no further repair)
    critique2, vmeta2 = vision_review(sheet2, storyboard, task=task_desc)
    (rev / 'critique_v2.json').write_text(
        json.dumps(critique2, ensure_ascii=False, indent=1), encoding='utf-8')

    report = (
        f'# Review loop report — {model} {scene_name}\n\n'
        f"## v1 critique: {critique.get('verdict')} "
        f"({len(critique.get('issues', []))} issues)\n"
        f"storyboard_alignment: {critique.get('storyboard_alignment')}\n\n"
        + '\n'.join(f"- [{i.get('severity')}] {i.get('time','?')}s "
                    f"dim{i.get('dimension')}: {i.get('problem')} "
                    f"→ {i.get('fix')}"
                    for i in critique.get('issues', [])) + '\n\n'
        f"## v2 critique: {critique2.get('verdict')} "
        f"({len(critique2.get('issues', []))} issues)\n"
        f"storyboard_alignment: {critique2.get('storyboard_alignment')}\n\n"
        f"## tokens\n- vision v1/v2: "
        f"{json.dumps(vmeta.get('usage'))} / {json.dumps(vmeta2.get('usage'))}\n"
        f"- repair ({model}): {json.dumps(rmeta)}\n")
    (rev / 'review_report.md').write_text(report, encoding='utf-8')
    print('DONE: v2 + report written')
    return 0


if __name__ == '__main__':
    sys.exit(main())
