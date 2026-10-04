import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from p103.artifacts import verify_registered_media
from p103.media import sha256_file

class ArtifactHashTests(unittest.TestCase):
 def test_verify_assets_and_detect_mutation(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'audio').mkdir();p=root/'audio'/'captions.vtt';p.write_text('a',encoding='utf-8')
   manifest={'vtt':{'path':'audio/captions.vtt','sha256':sha256_file(p)}}
   self.assertEqual(len(verify_registered_media(root,manifest)),1)
   p.write_text('changed',encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'E_MEDIA_HASH_MISMATCH'):verify_registered_media(root,manifest)
 def test_reject_path_escape(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'run';root.mkdir()
   with self.assertRaisesRegex(ValueError,'escapes'):verify_registered_media(root,{'vtt':{'path':'../outside','sha256':'x'}})

if __name__=='__main__':unittest.main()
