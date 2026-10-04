import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from p103.cli import main
from p103.core import create_run
from p103.media import sha256_file
class RenderGateTests(unittest.TestCase):
 def test_finalize_requires_matching_report_and_unchanged_bytes(self):
  with tempfile.TemporaryDirectory() as tmp:
   source=ROOT/'spikes'/'canvas-wave-interference'/'final'/'public'/'audio'/'narration.vtt';run=create_run(Path(tmp),'video',source,run_id='qa-gate')
   video=run.artifact('attempt-1/attempt-1.mp4');video.write_bytes(b'first')
   report={'passed':True,'video':'attempt-1/attempt-1.mp4','video_sha256':sha256_file(video)}
   (run.root/'verification'/'report.json').write_text(json.dumps(report),encoding='utf-8')
   self.assertEqual(main(['--workspace',tmp,'finalize',run.run_id]),0)
   self.assertEqual((run.root/'final'/'final.mp4').read_bytes(),b'first')
   video.write_bytes(b'mutated')
   self.assertEqual(main(['--workspace',tmp,'finalize',run.run_id]),2)
if __name__=='__main__':unittest.main()
