"""Acceptance binding must reject stale or incomplete hidef evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sources/tools/blender'))
from rigellian_mobile_runtime_evidence import verify

class HidefEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inventory=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text(encoding='utf-8'))
        ids={s['id'] for s in json.loads((ROOT/'sources/objects/rigellian/fleet-style.json').read_text(encoding='utf-8'))['ships']}
        cls.records=[r for r in inventory['records'] if r['id'] in ids]
        assert len(cls.records)==4

    def test_current_native_and_imported_evidence(self):
        for record in self.records:
            with self.subTest(model=record['id']):verify(ROOT/'sources',record)

    def test_missing_bound_input_is_rejected(self):
        record=copy.deepcopy(self.records[0]);proof=record['reviewed_model']['runtime_evidence']
        del proof['files'][proof['visual_report']]
        with self.assertRaises(AssertionError):verify(ROOT/'sources',record)

    def test_stale_evidence_is_rejected(self):
        record=copy.deepcopy(self.records[0]);proof=record['reviewed_model']['runtime_evidence']
        proof['files'][proof['report']]='0'*64
        with self.assertRaises(AssertionError):verify(ROOT/'sources',record)

    def test_changed_model_and_unearned_game_acceptance_are_rejected(self):
        for mutation in ['model','game']:
            record=copy.deepcopy(self.records[0])
            if mutation=='model':record['reviewed_model']['sha256']='0'*64
            else:record['reviewed_model']['runtime_evidence']['game_client_integration']=True
            with self.subTest(mutation=mutation),self.assertRaises(AssertionError):verify(ROOT/'sources',record)

if __name__=='__main__':unittest.main()
