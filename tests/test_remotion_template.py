import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from p103.remotion_template import write_consumer
class RemotionTemplateTests(unittest.TestCase):
 def test_scene_slots_bounded_transition_and_public_audio_copy(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'audio').mkdir();(root/'audio'/'timeline.json').write_text(json.dumps({'tts':{'path':'audio/narration.mp3'},'cues':[{'id':'s-line-01','start_ms':0,'end_ms':1000}]}),encoding='utf-8');(root/'audio'/'narration.mp3').write_bytes(b'audio')
   write_consumer(root,scene_specs=[{'segment_id':'s-line-01','offset_ms':100,'duration_ms':800,'title':'A','transition':'fade'}])
   scene=json.loads((root/'src'/'generated'/'scene-specs.json').read_text(encoding='utf-8'))[0];code=(root/'src'/'generated'/'TimelineConsumer.tsx').read_text(encoding='utf-8')
   self.assertEqual(scene['duration_ms'],800);self.assertIn("transition==='fade'",code);self.assertTrue((root/'public'/'audio'/'narration.mp3').is_file())
   with self.assertRaisesRegex(ValueError,'exceeds its segment'):write_consumer(root,scene_specs=[{'segment_id':'s-line-01','offset_ms':100,'duration_ms':901}])
 def test_unknown_segment_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'audio').mkdir();(root/'audio'/'timeline.json').write_text('{"cues":[]}',encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'unknown segment_id'):write_consumer(root,scene_specs=[{'segment_id':'missing','duration_ms':10}])
if __name__=='__main__':unittest.main()
