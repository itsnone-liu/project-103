import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from p103.cli import main
from p103.core import create_run
from p103.media import sha256_file
class AlignmentCliTests(unittest.TestCase):
 def test_provider_sentence_cues_align_and_register_hash(self):
  src=ROOT/'spikes'/'canvas-wave-interference'/'final'/'public'/'audio'/'narration.vtt'
  audio=ROOT/'spikes'/'canvas-wave-interference'/'final'/'public'/'audio'/'narration.mp3'
  with tempfile.TemporaryDirectory() as tmp:
   run=create_run(Path(tmp),'video',src,run_id='align-cli')
   self.assertEqual(main(['--workspace',tmp,'timeline',run.run_id,str(src),'--audio',str(audio)]),0)
   from p103.timeline import parse_cues
   actual,_=parse_cues(src.read_text(encoding='utf-8-sig'),source_format='vtt')
   provider=run.root/'audio'/'provider-cues.vtt';provider.write_text('WEBVTT\n\n'+'\n\n'.join(f'{i+1}\n{start//3600000:02d}:{(start//60000)%60:02d}:{(start//1000)%60:02d}.{start%1000:03d} --> {end//3600000:02d}:{(end//60000)%60:02d}:{(end//1000)%60:02d}.{end%1000:03d}\n{text}' for i,(start,end,text) in enumerate(actual)),encoding='utf-8')
   manifest=json.loads((run.root/'audio'/'timeline.json').read_text(encoding='utf-8'))
   manifest['tts_cues']={'path':'audio/provider-cues.vtt','sha256':sha256_file(provider)}
   (run.root/'audio'/'timeline.json').write_text(json.dumps(manifest),encoding='utf-8')
   self.assertEqual(main(['--workspace',tmp,'align-tts',run.run_id]),0)
   result=json.loads((run.root/'audio'/'timeline.json').read_text(encoding='utf-8'))
   self.assertEqual(result['tts_alignment']['coverage'],'exact-normalized')
   self.assertEqual(len(result['tts_alignment']['segments']),12)
if __name__=='__main__':unittest.main()
