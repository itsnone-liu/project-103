#!/usr/bin/env python3
"""Contact sheets via p103's video_qa (dependency-free PNG assembly)."""
import sys
from pathlib import Path

ROOT = Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
COMP = (ROOT / 'runs' / 'architecture-smoke' / 'node_modules' /
        '@remotion' / 'compositor-win32-x64-msvc')
import os  # noqa: E402
os.environ['PATH'] = str(COMP) + os.pathsep + os.environ['PATH']
sys.path.insert(0, str(ROOT))          # package parent: import p103.video_qa
import p103.video_qa as video_qa  # noqa: E402


def main() -> int:
    which = sys.argv[1]  # 'opus' | 'glm'
    case = ROOT / 'base-compare' / 'case-a'
    if which == 'opus':
        video = case / 'out' / 'demo_opus_reference.mp4'
        outdir = case / 'out' / 'opus_sheet'
    elif which == 'luna':
        case = ROOT / 'base-compare' / 'case-b'
        video = case / 'out' / 'luna_video.mp4'
        outdir = case / 'out' / 'luna_sheet'
    else:
        video = case / 'out' / 'glm_video.mp4'
        outdir = case / 'out' / 'glm_sheet'
    frames = video_qa.extract_keyframes(
        video, outdir, count=8, tool_root=ROOT)
    sheet = video_qa.create_contact_sheet(
        frames, outdir.parent / f'{which}_contact_sheet.png',
        tool_root=ROOT)
    print(f'{sheet} from {len(frames)} frames')
    return 0


if __name__ == '__main__':
    sys.exit(main())
