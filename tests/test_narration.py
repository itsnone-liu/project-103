import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from p103.timeline import import_subtitles,align_tts_cues

class NarrationAlignmentTests(unittest.TestCase):
 def test_exact_coverage_and_provider_sentence_times(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'x.vtt';p.write_text('WEBVTT\n\n00:00.000 --> 00:01.000\n你好，\n\n00:01.000 --> 00:02.000\n世界！\n',encoding='utf-8')
   t=import_subtitles(p,narration_texts=['你好，','世界！'],tts_texts=['你好','世界'],scene_id='s')
  mapped=align_tts_cues(t,['你','好世','界'],[(0,300),(300,1200),(1200,2000)])
  self.assertEqual([x['segment_id'] for x in mapped],['s-line-01','s-line-02'])
  self.assertEqual(mapped[0]['start_ms'],0);self.assertEqual(mapped[-1]['end_ms'],2000)
 def test_missing_or_extra_text_fails_loudly(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'x.srt';p.write_text('1\n00:00:00,000 --> 00:00:01,000\nspoken\n',encoding='utf-8')
   t=import_subtitles(p,tts_texts=['spoken'])
  with self.assertRaisesRegex(ValueError,'E_NARR_TEXT_MISMATCH'):
   align_tts_cues(t,['spoken missing'])

if __name__=='__main__':unittest.main()
