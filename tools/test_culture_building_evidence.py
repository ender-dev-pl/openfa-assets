"""Reject broken identity, stale runtime proofs and duplicate canonical selections."""
import copy,hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sources/tools/blender'))
from culture_building_remaster_runtime_evidence import verify,FORMAT

class CultureBuildingEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=[]
        for row in json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text())['records']:
            reviewed=row.get('reviewed_model');proof=reviewed.get('runtime_evidence') if isinstance(reviewed,dict) else None
            if isinstance(proof,dict) and proof.get('format')==FORMAT:cls.records.append(row)
        assert cls.records,'Expected a current culture-building runtime proof';cls.record=cls.records[0]
    def check(self,row):return verify(ROOT/'sources',row)
    def test_all_current_exact_bundles(self):
        for row in self.records:
            with self.subTest(asset=row['id']):self.assertFalse(self.check(row)['game_client_integration'])
    def test_changed_binary(self):
        row=copy.deepcopy(self.record);files=row['reviewed_model']['runtime_evidence']['files'];name=next(p for p in files if p.endswith('/model.glb'));files[name]='0'*64
        with self.assertRaisesRegex(AssertionError,'Changed runtime evidence'):self.check(row)
    def test_duplicate_canonical_selection(self):
        row=copy.deepcopy(self.record);row['available_studies'].append(copy.deepcopy(row['available_studies'][0]))
        with self.assertRaises(ValueError):self.check(row)
    def test_escape_evidence_path(self):
        row=copy.deepcopy(self.record);row['reviewed_model']['runtime_evidence']['files']['../outside']='0'*64
        with self.assertRaisesRegex(AssertionError,'must remain in repository'):self.check(row)
    def test_missing_runtime_report(self):
        row=copy.deepcopy(self.record);files=row['reviewed_model']['runtime_evidence']['files'];del files[next(p for p in files if p.endswith('/runtime-review.json'))]
        with self.assertRaisesRegex(AssertionError,'Incomplete canonical runtime evidence'):self.check(row)
    def mutate_report(self,row,suffix,change):
        files=row['reviewed_model']['runtime_evidence']['files'];name=next(p for p in files if p.endswith(suffix));target=(ROOT/name).resolve();data=json.loads(target.read_bytes());change(data);mutant=(json.dumps(data)+'\n').encode();files[name]=hashlib.sha256(mutant).hexdigest();read=Path.read_bytes
        return patch.object(Path,'read_bytes',lambda path:mutant if path.resolve()==target else read(path))
    def test_rehashed_wrong_visual_identity(self):
        row=copy.deepcopy(self.record)
        with self.mutate_report(row,'/visual-review.json',lambda data:data.update(id='unrelated-building')):
            with self.assertRaisesRegex(AssertionError,'Model identity mismatch'):self.check(row)
    def test_rehashed_failed_import_is_not_acceptance(self):
        row=copy.deepcopy(self.record)
        with self.mutate_report(row,'/runtime-review.json',lambda data:data.update(maximum_bidirectional_surface_error=.1)):
            with self.assertRaises(AssertionError):self.check(row)
    def test_rehashed_wrong_concept_pointer(self):
        row=copy.deepcopy(self.record)
        with self.mutate_report(row,'/model.json',lambda data:data.update(concept_review='unbound-concept.json')):
            with self.assertRaisesRegex(AssertionError,'Concept reference is not bound'):self.check(row)
    def test_rehashed_wrong_concept_identity(self):
        row=copy.deepcopy(self.record)
        with self.mutate_report(row,'concept-review.json',lambda data:data.update(id='unrelated-building')):
            with self.assertRaisesRegex(AssertionError,'Concept identity mismatch'):self.check(row)
    def test_unbound_accepted_gate(self):
        row=copy.deepcopy(self.record);row['acceptance_evidence'].pop('native_and_glb_runtime')
        with self.assertRaisesRegex(AssertionError,'Unbound acceptance gate'):self.check(row)

if __name__=='__main__':unittest.main()
