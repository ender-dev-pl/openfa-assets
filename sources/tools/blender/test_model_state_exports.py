"""Regression contracts for registered model-state evidence, using current real artifacts."""
import copy
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_state_exports import verify_state_exports,verify_state_export_data,digest

ROOT=Path(__file__).resolve().parents[2]
IDENTITY='openfa:building/legacy/049'


class StateEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        programme=json.loads((ROOT/'docs/reconstruction/models/programme.json').read_text())
        cls.study=next(item for item in programme['additional_studies'] if item['id']==IDENTITY)
        cls.path=ROOT/cls.study['state_exports']['index'];cls.index=json.loads(cls.path.read_text())

    def check_mutation(self,change):
        index=copy.deepcopy(self.index);change(index)
        with self.assertRaises(AssertionError): verify_state_export_data(ROOT,IDENTITY,self.study,self.path,index)

    def test_current_registered_exports(self):
        self.assertEqual(verify_state_exports(ROOT,IDENTITY,self.study),14)

    def test_line_endings_do_not_invalidate_json_evidence(self):
        with patch.object(Path,'read_bytes',return_value=b'{\r\n  "pose": 2\r\n}\r\n'):
            windows=digest(Path('state.json'))
        with patch.object(Path,'read_bytes',return_value=b'{\n  "pose": 2\n}\n'):
            portable=digest(Path('state.json'))
        self.assertEqual(windows,portable)

    def test_outdated_base_model_rejected(self):
        self.check_mutation(lambda index:index.update(source_blend_sha256='0'*64))

    def test_duplicate_descriptor_rejected(self):
        self.check_mutation(lambda index:index['states'].__setitem__(0,copy.deepcopy(index['states'][1])))

    def test_changed_export_digest_rejected(self):
        self.check_mutation(lambda index:index['exports'][0].update(glb_sha256='0'*64))

    def test_missing_final_descriptor_rejected(self):
        self.check_mutation(lambda index:index['exports'][-1]['descriptors'].remove(17))

    def test_hidden_open_indicator_rejected(self):
        self.check_mutation(lambda index:index['exports'][-1]['indicator_visibility'][0].update(visible_sample_rays=0))

    def test_pose_artifact_path_escape_rejected(self):
        self.check_mutation(lambda index:index['exports'][0].update(glb='../model.glb'))

    def test_registered_index_path_escape_rejected(self):
        study=copy.deepcopy(self.study);study['state_exports']['index']='../legacy/AGENTS.md'
        with self.assertRaises(AssertionError): verify_state_exports(ROOT,IDENTITY,study)


if __name__=='__main__': unittest.main()
