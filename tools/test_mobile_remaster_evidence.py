"""Reject stale/swapped/incomplete evidence without copying any model payload."""
from copy import deepcopy
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sources/tools/blender'))
from model_runtime_evidence import verify_runtime_evidence


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text())['records']
        cls.record=next(r for r in records if r['id']=='openfa:ship/mauna/transportation-craft-type-3')

    def run_check(self,row):return verify_runtime_evidence(ROOT/'sources',row)

    def test_current_exact_bundle(self):
        self.assertFalse(self.run_check(self.record)['game_client_integration'])

    def test_stale_binary(self):
        row=deepcopy(self.record);files=row['reviewed_model']['runtime_evidence']['files'];name=next(k for k in files if k.endswith('/model.glb'));files[name]='0'*64
        with self.assertRaisesRegex(AssertionError,'Runtime evidence changed'):self.run_check(row)

    def test_missing_imported_pixels(self):
        row=deepcopy(self.record);proof=row['reviewed_model']['runtime_evidence'];del proof['files'][proof['imported_render']]
        with self.assertRaisesRegex(AssertionError,'Incomplete bound runtime evidence'):self.run_check(row)

    def test_swapped_identity(self):
        row=deepcopy(self.record);row['id']='openfa:ship/mauna/other'
        with self.assertRaisesRegex(AssertionError,'catalogue identity differs'):self.run_check(row)

    def test_escaping_path(self):
        row=deepcopy(self.record);row['reviewed_model']['runtime_evidence']['files']['../outside']='0'*64
        with self.assertRaisesRegex(AssertionError,'must remain in repository'):self.run_check(row)

    def test_unbound_accepted_gate(self):
        row=deepcopy(self.record);del row['acceptance_evidence']['materials']
        with self.assertRaisesRegex(AssertionError,'Acceptance requires explicit evidence'):self.run_check(row)

    def test_gate_cannot_use_unrelated_bound_file(self):
        row=deepcopy(self.record);proof=row['reviewed_model']['runtime_evidence'];name=proof['native_render']
        row['acceptance_evidence']['materials']=dict(report=name,sha256=proof['files'][name])
        with self.assertRaisesRegex(AssertionError,'wrong report'):self.run_check(row)

    def test_rehashed_report_for_wrong_binary(self):
        row=deepcopy(self.record);proof=row['reviewed_model']['runtime_evidence'];name=proof['runtime_report'];target=(ROOT/name).resolve();data=json.loads(target.read_bytes());data['binaries']['glb']='0'*64;mutant=(json.dumps(data)+'\n').encode();proof['files'][name]=hashlib.sha256(mutant).hexdigest();read=Path.read_bytes
        def bytes_for(path):return mutant if path.resolve()==target else read(path)
        with patch.object(Path,'read_bytes',bytes_for):
            with self.assertRaisesRegex(AssertionError,'report/binary revision differs'):self.run_check(row)

    def test_rehashed_recipe_still_requires_the_reviewed_revision(self):
        row=deepcopy(self.record);proof=row['reviewed_model']['runtime_evidence'];name='sources/'+str(Path(row['reviewed_model']['blend']).parent/'recipe.json').replace('\\','/');target=(ROOT/name).resolve();mutant=target.read_bytes()+b' ';proof['files'][name]=hashlib.sha256(mutant).hexdigest();read=Path.read_bytes
        def bytes_for(path):return mutant if path.resolve()==target else read(path)
        with patch.object(Path,'read_bytes',bytes_for):
            with self.assertRaises(AssertionError):self.run_check(row)


if __name__=='__main__':unittest.main()
