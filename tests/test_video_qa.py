import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from p103.video_qa import extract_keyframes,create_contact_sheet,verify_video

class VideoQaTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.video=ROOT/'runs'/'architecture-smoke'/'attempt-1'/'attempt-1.mp4'
  if not cls.video.is_file():cls.video=ROOT/'runs'/'architecture-smoke'/'out'/'timeline-consumer-smoke.mp4'
 @unittest.skipUnless((ROOT/'runs'/'architecture-smoke'/'out'/'timeline-consumer-smoke.mp4').is_file(),'real Remotion smoke render unavailable')
 def test_keyframes_contact_sheet_and_video_probe(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);frames=extract_keyframes(self.video,root/'keyframes',count=3,tool_root=ROOT);sheet=create_contact_sheet(frames,root/'sheet.png',columns=2,cell_width=240,cell_height=135,tool_root=ROOT)
   size=sheet.stat().st_size;probe=verify_video(self.video,expected_fps=30)
  self.assertEqual(len(frames),3);self.assertGreater(size,1000);self.assertTrue(probe['verification']['passed']);self.assertTrue(probe['has_audio'])

if __name__=='__main__':unittest.main()
