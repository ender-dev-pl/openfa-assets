"""Regression checks for accidental model duplication and engineering retirement."""
import hashlib,json,tempfile,unittest
from pathlib import Path
import canonical_assets as canonical
class CanonicalBoundaryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);(self.root/'project').mkdir();self.models=[]
  for culture in ['achaean','artemian','braccatian','mauna','mikotaj','rigellian','terran']:
   for role in ['repair','terraform']:
    for ext in ['blend','glb']:
     name=f'sources/proposals/engineering-ships/{culture}/{role}/model.{ext}';p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'fixture');self.models.append(dict(path=name,sha256=hashlib.sha256(b'fixture').hexdigest()))
  self.data=dict(models=self.models,catalogue=[dict(id='test',studies=[dict(blend=self.models[0]['path'],glb=self.models[1]['path'])])],archive=dict(files=[dict(path='sources/old/model.glb')]))
  self.save()
 def save(self):(self.root/'project/canonical-assets.json').write_text(json.dumps(self.data))
 def test_rejects_unregistered_alternative_geometry(self):
  p=self.root/'sources/alternative.glb';p.write_bytes(b'old')
  with self.assertRaisesRegex(ValueError,'Unregistered or missing'):canonical.verify(self.root)
 def test_rejects_retirement_of_engineering_source_even_if_registry_is_changed(self):
  row=self.models.pop();(self.root/row['path']).unlink();self.save()
  with self.assertRaisesRegex(ValueError,'Engineering ships must remain'):canonical.verify(self.root)
 def test_rejects_changed_payload(self):
  (self.root/self.models[0]['path']).write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'Changed canonical model'):canonical.verify(self.root)
 def test_accepts_one_pair_and_rejects_restored_historical_file(self):
  canonical.verify(self.root);p=self.root/'sources/old/model.glb';p.parent.mkdir();p.write_bytes(b'old')
  with self.assertRaises(ValueError):canonical.verify(self.root)
if __name__=='__main__':unittest.main()
