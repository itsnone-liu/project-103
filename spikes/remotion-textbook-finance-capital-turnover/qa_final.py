from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from p103.media import probe_media,sha256_file
from p103.video_qa import extract_keyframes,create_contact_sheet,verify_video
HERE=Path(__file__).resolve().parent
# Probe discovery walks video ancestors; use the package-local output so it can find final/node_modules.
video=HERE/'final'/'out'/'capital-turnover.mp4'
if not video.is_file():raise SystemExit('final.mp4 missing')
probe=verify_video(video,expected_fps=30,expected_audio=True,expected_width=1920,expected_height=1080)
frames=extract_keyframes(video,HERE/'verification'/'keyframes',count=8,tool_root=ROOT)
sheet=create_contact_sheet(frames,HERE/'verification'/'contact-sheet.png',columns=4,cell_width=480,cell_height=270)
report={'passed':True,'video':'final.mp4','video_sha256':sha256_file(video),'probe':probe,'keyframes':[str(x.relative_to(HERE)).replace('\\','/') for x in frames],'contact_sheet':str(sheet.relative_to(HERE)).replace('\\','/')}
(HERE/'verification'/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
