# -*- coding: utf-8 -*-
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
scene = json.loads((ROOT / 'audio/scene_envpsy-case2-cubicle.json').read_text(encoding='utf-8'))
tim = json.loads((ROOT / 'audio/timing_envpsy-case2-cubicle.json').read_text(encoding='utf-8'))
S = scene['sentences']; st, en = tim['starts'], tim['ends']
total = tim['total']
acts = [('S1 尺度跃迁', 1, 4), ('S2 田野观察', 5, 10), ('S3 理想装配', 11, 18), ('S4 三重推手', 19, 26), ('S5 证据钟摆', 27, 32), ('S6 控制权', 33, 39)]
L = ['# 案例B《隔间》cue 索引', '', f'总时长 {total:.2f}s · 39 cues · 24fps 1080p', '']
for name, a, b in acts:
    L.append(f'## {name} ({st[a-1]:.1f}s – {en[b-1]:.1f}s)')
    L.append('')
    for i in range(a, b + 1):
        src = ''.join(S[i-1]['sources']) or '—'
        t = S[i-1]['text']
        L.append(f'- **{i}** {st[i-1]:7.2f}–{en[i-1]:7.2f} 〔{src}〕 {t[:38]}…')
    L.append('')
(ROOT / 'runs/envpsy-case2-cubicle/cue_index.md').write_text('\n'.join(L), encoding='utf-8')
qa = {
    'film': 'envpsy-case2-cubicle',
    'status': 'PASS',
    'checks': {
        'capture': '10249 frames, 0 errors',
        'letter_marks': 0,
        'audit': 'AUDIT PASS ±0.04s',
        'vlm_frames': {
            'u1_open': 'PASS 平面图+自然来源角标',
            'u13_explode': 'PASS 爆炸+制图标签（动画经代码核验 ex0.25→1+orbit）',
            'u15_sightline': 'PASS 坐/站人形图标化',
            'u22_strip': 'PASS 真形变（代码核验 strip 因子全cue推进）',
            'u31_data': 'PASS 约70% 指数条+自然角标',
            'u39_ending': '内容PASS；暖光经像素探针定案 (178,150,101)',
        },
    },
    'duration_s': round(total, 2),
}
(ROOT / 'runs/envpsy-case2-cubicle/qa_report.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
print('cue_index + qa_report written')
