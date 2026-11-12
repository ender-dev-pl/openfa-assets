"""Regression coverage for explicit historical inputs and current-byte checks."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sources/tools/blender'))
from archive_evidence import verify_bound_input
class ArchivedInputTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);(self.root/'project').mkdir();self.name='sources/old/model.blend';self.digest=hashlib.sha256(b'original').hexdigest();self.entry=dict(path=self.name,sha256=self.digest,source_blob='a'*40);self.policy=dict(models=[],archive=dict(commit='b'*40,files=[self.entry]));self.ref=dict(archive_path=self.name,sha256=self.digest,source_blob='a'*40,archive_commit='b'*40);self.proof=dict(files={},archived_inputs={self.name:self.ref});self.save()
 def save(self):(self.root/'project/canonical-assets.json').write_text(json.dumps(self.policy))
 def test_historical_reference_requires_exact_digest_blob_and_commit(self):
  self.assertEqual(verify_bound_input(self.root,self.proof,self.name,self.digest),'historical-input-provenance')
  for key in ['sha256','source_blob','archive_commit']:
   value=self.ref[key];self.ref[key]='tampered'
   with self.subTest(key=key),self.assertRaises(AssertionError):verify_bound_input(self.root,self.proof,self.name,self.digest)
   self.ref[key]=value
 def test_cannot_treat_current_model_as_archived(self):
  self.policy['models']=[dict(path=self.name)];self.save()
  with self.assertRaises(AssertionError):verify_bound_input(self.root,self.proof,self.name,self.digest)
 def test_ledger_does_not_replace_an_explicit_bound_input(self):
  self.proof['archived_inputs']={}
  with self.assertRaisesRegex(AssertionError,'Unbound input'):verify_bound_input(self.root,self.proof,self.name,self.digest)
 def test_current_input_still_requires_actual_original_bytes(self):
  self.proof['files'][self.name]=self.digest;p=self.root/self.name;p.parent.mkdir(parents=True);p.write_bytes(b'original')
  self.assertEqual(verify_bound_input(self.root,self.proof,self.name,self.digest),'current-bytes')
  p.write_bytes(b'corrupted')
  with self.assertRaisesRegex(AssertionError,'Changed bound input'):verify_bound_input(self.root,self.proof,self.name,self.digest)
if __name__=='__main__':unittest.main()
