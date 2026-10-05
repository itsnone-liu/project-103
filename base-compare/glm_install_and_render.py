#!/usr/bin/env python3
"""Install GLM's scene into the runtime and render + contact sheet.

Usage: python glm_install_and_render.py
Reads glm/butterfly.js (+ glm/STORYBOARD.md), patches studio.html and
src/config.js (duration parsed from the JS comment GLM was told to write,
fallback 15s/120bpm), renders out/glm_video.mp4, builds glm_contact_sheet.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
CASE = ROOT / 'base-compare' / 'case-a'
COMP = (ROOT / 'runs' / 'architecture-smoke' / 'node_modules' /
        '@remotion' / 'compositor-win32-x64-msvc')
os.environ['PATH'] = str(COMP) + os.pathsep + os.environ['PATH']
sys.path.insert(0, str(ROOT))
import p103.video_qa as video_qa  # noqa: E402


def parse_config(scene: str) -> tuple[float, float]:
    m = re.search(
        r'duration\s*[:=]\s*([\d.]+).*?bpm\s*[:=]\s*(\d+)', scene, re.S)
    if m:
        return float(m.group(1)), int(m.group(2))
    return 15.0, 120


def main() -> int:
    scene_path = CASE / 'glm' / 'butterfly.js'
    scene = scene_path.read_text(encoding='utf-8')
    (CASE / 'src' / 'scenes' / 'butterfly.js').write_text(
        scene, encoding='utf-8')

    dur, bpm = parse_config(scene)
    (CASE / 'src' / 'config.js').write_text(
        '// config.js: project settings.\n'
        '// Set by glm_install_and_render.py for the GLM base run.\n'
        f'const PROJECT = {{ duration: {dur:g}, bpm: {bpm}, offset: 0 }};\n',
        encoding='utf-8')

    html = (CASE / 'studio.html').read_text(encoding='utf-8')
    html2 = html.replace('src/scenes/demo.js', 'src/scenes/butterfly.js')
    (CASE / 'studio.html').write_text(html2, encoding='utf-8')
    print(f'installed: duration={dur:g}s bpm={bpm}')

    r = subprocess.run(
        ['node', 'render.mjs', '--clip', '--out=out/glm_video.mp4'],
        cwd=str(CASE), capture_output=True, text=True,
        encoding='utf-8', errors='replace', timeout=7200)
    print((r.stdout or '')[-500:])
    if r.returncode != 0:
        print('RENDER FAILED:', (r.stderr or '')[-1500:])
        return 1
    video = CASE / 'out' / 'glm_video.mp4'
    frames = video_qa.extract_keyframes(
        video, CASE / 'out' / 'glm_sheet', count=8, tool_root=ROOT)
    sheet = video_qa.create_contact_sheet(
        frames, CASE / 'out' / 'glm_contact_sheet.png', tool_root=ROOT)
    print(f'OK {video} + {sheet} ({len(frames)} frames)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
