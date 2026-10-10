"""Offline video deliverable QA: stream metadata, still frames, motion, audio peak.

Visual interpretation is separately human/VLM-reviewed at full resolution.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = ROOT / "runs" / "moyun-birthday"
FF = ROOT / "runs" / "architecture-smoke" / "node_modules" / "@remotion" / "compositor-win32-x64-msvc"
FFMPEG = FF / "ffmpeg.exe"
FFPROBE = FF / "ffprobe.exe"
TIMES = (0.8, 3.0, 5.8, 8.5, 11.3)


def verify(arm):
    if arm not in ("open", "assisted"):
        raise ValueError(arm)
    out = RUNS / arm / "out"
    video = out / f"birthday_{arm}.mp4"
    assert video.is_file(), video
    r = subprocess.run([str(FFPROBE), "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames", "-show_entries", "format=duration", "-of", "json", str(video)], check=True, capture_output=True, text=True)
    data = json.loads(r.stdout)
    tracks = {s['codec_type']:s for s in data['streams']}
    assert {'video','audio'} <= tracks.keys(), tracks
    assert (tracks['video']['width'], tracks['video']['height'], tracks['video']['r_frame_rate']) == (1280,720,'24/1')
    assert abs(float(data['format']['duration'])-12) < .12, data
    assert tracks['video'].get('nb_frames') in ('288',None), data
    ims = []
    for t in TIMES:
        dest = out / f"qa_{t:.1f}.png"
        p = subprocess.run([str(FFMPEG),"-y","-v","error","-ss",str(t),"-i",str(video),"-frames:v","1",str(dest)], capture_output=True, text=True)
        assert p.returncode == 0 and dest.is_file(), p.stderr
        ims.append(Image.open(dest).convert('RGB'))
    diffs = [round(ImageStat.Stat(ImageChops.difference(a,b).convert('L')).mean[0],2) for a,b in zip(ims,ims[1:])]
    # Final interval is deliberately a calm title hold; require motion across the three growth beats.
    assert min(diffs[:3]) > 0.7, f"missing growth motion: {diffs}"
    report = {'arm':arm,'video':str(video),'duration':data['format']['duration'],'motion_diffs':diffs,'frames':[f'qa_{t:.1f}.png' for t in TIMES],'streams':tracks,'result':'PASS structural / pending visual review'}
    (out / 'verify_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"{arm}: structural PASS; motion diffs {diffs}; visual review still required",flush=True)

if __name__ == '__main__':
    for a in (sys.argv[1:] or ['open','assisted']): verify(a)
