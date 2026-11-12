"""Negative evidence checks using actual reviewed models, without mutating user files."""
import copy
from contextlib import contextmanager
import json
import shutil
import sys
import uuid
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_runtime_evidence import verify_runtime_evidence,evidence_digest

ROOT=Path(__file__).resolve().parents[2]
IDS={f'openfa:building/legacy/{number:03}' for number in range(40,46)}


class RuntimeEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inventory=json.loads((ROOT/'docs/reconstruction/models/inventory.json').read_text())
        cls.records=[r for r in inventory['records'] if r['category']=='buildings' and r['id'] in IDS]

    @contextmanager
    def snapshot(self,record):
        proof=record['reviewed_model']['runtime_evidence']
        sandbox=(ROOT/'artifacts'/('runtime-evidence-negative-'+uuid.uuid4().hex)).resolve()
        self.assertTrue(sandbox.is_relative_to((ROOT/'artifacts').resolve()));self.assertFalse(sandbox.exists());sandbox.mkdir()
        try:
            for relative in proof['files']:
                target=sandbox/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/relative,target)
            yield sandbox
        finally:
            self.assertTrue(sandbox.is_relative_to((ROOT/'artifacts').resolve()));shutil.rmtree(sandbox)

    def test_current_six_revisions_have_bound_technical_evidence_only(self):
        self.assertEqual({r['id'] for r in self.records},IDS)
        for record in self.records:
            with self.subTest(model=record['id']):
                result=verify_runtime_evidence(ROOT,record)
                self.assertEqual(result['views'],7)
                self.assertEqual([key for key,value in record['acceptance'].items() if value],['native_and_glb_runtime'])
                self.assertFalse(result['game_client_integration'])

    def test_changed_glb_digest_is_rejected(self):
        record=copy.deepcopy(self.records[0]);model=record['reviewed_model']
        glb=str(Path(model['blend']).with_suffix('.glb')).replace('\\','/')
        model['runtime_evidence']['files'][glb]='0'*64
        with self.assertRaisesRegex(AssertionError,'Runtime evidence changed'):
            verify_runtime_evidence(ROOT,record)

    def test_missing_imported_render_is_rejected(self):
        record=copy.deepcopy(self.records[0]);proof=record['reviewed_model']['runtime_evidence']
        del proof['files'][proof['imported_render']]
        with self.assertRaisesRegex(AssertionError,'Incomplete bound runtime evidence'):
            verify_runtime_evidence(ROOT,record)

    def test_swapped_catalogue_identity_is_rejected(self):
        record=copy.deepcopy(self.records[0]);record['id']='openfa:building/legacy/999'
        with self.assertRaisesRegex(AssertionError,'catalogue identity differs'):
            verify_runtime_evidence(ROOT,record)

    def test_escaping_repository_path_is_rejected(self):
        record=copy.deepcopy(self.records[0]);record['reviewed_model']['runtime_evidence']['files']['../outside-proof']='0'*64
        with self.assertRaisesRegex(AssertionError,'must remain in repository'):
            verify_runtime_evidence(ROOT,record)

    def test_rehashed_report_for_different_model_is_rejected(self):
        record=copy.deepcopy(self.records[0]);proof=record['reviewed_model']['runtime_evidence']
        # Only this test's new temporary checkout is created and removed.
        with self.snapshot(record) as sandbox:
            relative=str(Path(record['reviewed_model']['blend']).parent/'technical-review.json').replace('\\','/')
            report=json.loads((sandbox/relative).read_text());report['blend_sha256']='0'*64
            (sandbox/relative).write_text(json.dumps(report))
            proof['files'][relative]=evidence_digest(sandbox/relative)
            with self.assertRaises(AssertionError): verify_runtime_evidence(sandbox,record)

    def test_lf_checkout_preserves_text_evidence(self):
        record=copy.deepcopy(self.records[0]);proof=record['reviewed_model']['runtime_evidence']
        with self.snapshot(record) as sandbox:
            for relative in proof['files']:
                target=sandbox/relative
                if target.suffix in ['.json','.py']: target.write_bytes(target.read_bytes().replace(b'\r\n',b'\n'))
            self.assertEqual(verify_runtime_evidence(sandbox,record)['id'],record['id'])


if __name__=='__main__': unittest.main()
