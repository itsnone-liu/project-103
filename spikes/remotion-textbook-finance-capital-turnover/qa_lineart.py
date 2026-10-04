from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from p103.media import sha256_file
from p103.video_qa import extract_keyframes,create_contact_sheet,verify_video
HERE=Path(__file__).resolve().parent
video=HERE/'lineart-final'/'out'/'capital-turnover-lineart.mp4'
if not video.is_file():raise SystemExit('lineart video missing')
probe=verify_video(video,expected_fps=30,expected_audio=True,expected_width=1920,expected_height=1080)
verify_dir=HERE/'lineart-final'/'verification'
frames=extract_keyframes(video,verify_dir/'keyframes',count=12,tool_root=ROOT)
sheet=create_contact_sheet(frames,verify_dir/'contact-sheet.png',columns=4,cell_width=480,cell_height=270)
report={'passed':True,'video':str(video.relative_to(HERE)).replace('\\','/'),'video_sha256':sha256_file(video),'probe':probe,'keyframes':[str(x.relative_to(HERE)).replace('\\','/') for x in frames],'contact_sheet':str(sheet.relative_to(HERE)).replace('\\','/')}
(verify_dir/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
