#!/usr/bin/env python3
"""Install Luna scene into case-b runtime, render, contact sheet."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
CASE = ROOT / 'base-compare' / 'case-b'
scene_src = CASE / 'luna' / 'butterfly.js'
text = scene_src.read_text(encoding='utf-8')
(CASE / 'src' / 'scenes' / 'butterfly.js').write_text(text, encoding='utf-8')

m = re.search(r'duration\s*[:=]\s*([\d.]+).*?bpm\s*[:=]\s*(\d+)', text, re.S)
dur, bpm = (float(m.group(1)), int(m.group(2))) if m else (15.0, 120)
(CASE / 'src' / 'config.js').write_text(
    '// config.js: set by luna_install_and_render.\n'
    f'const PROJECT = {{ duration: {dur:g}, bpm: {bpm}, offset: 0 }};\n',
    encoding='utf-8')
html = (CASE / 'studio.html').read_text(encoding='utf-8')
(CASE / 'studio.html').write_text(
    html.replace('src/scenes/demo.js', 'src/scenes/butterfly.js'),
    encoding='utf-8')
print(f'installed dur={dur:g} bpm={bpm}')

r = subprocess.run(
    ['node', 'render.mjs', '--clip', '--out=out/luna_video.mp4'],
    cwd=str(CASE), capture_output=True, text=True,
    encoding='utf-8', errors='replace', timeout=7200)
print((r.stdout or '')[-400:])
if r.returncode != 0:
    print('RENDER FAILED:', (r.stderr or '')[-1200:])
    sys.exit(1)

sys.path.insert(0, str(ROOT))
import os
COMP = (ROOT / 'runs' / 'architecture-smoke' / 'node_modules' /
        '@remotion' / 'compositor-win32-x64-msvc')
os.environ['PATH'] = str(COMP) + os.pathsep + os.environ['PATH']
import p103.video_qa as video_qa
frames = video_qa.extract_keyframes(
    CASE / 'out' / 'luna_video.mp4', CASE / 'out' / 'luna_sheet',
    count=8, tool_root=ROOT)
sheet = video_qa.create_contact_sheet(
    frames, CASE / 'out' / 'luna_contact_sheet.png', tool_root=ROOT)
print(f'OK sheet={sheet} frames={len(frames)}')
