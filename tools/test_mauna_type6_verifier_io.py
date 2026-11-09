"""Exercise report writes without Blender or copying any model payload."""
import hashlib,json,runpy,sys,types,unittest,uuid,shutil
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

@contextmanager
def workspace_fixture():
    parent=(ROOT/'.workspace'/'verifier-io-tests').resolve();parent.mkdir(parents=True,exist_ok=True)
    root=(parent/('openfa-type6-io-'+uuid.uuid4().hex)).resolve();root.mkdir()
    try:yield root
    finally:
        assert root.is_relative_to(parent) and root.parent==parent and root.name.startswith('openfa-type6-io-')
        shutil.rmtree(root)

class ReportIOTests(unittest.TestCase):
    def exercise(self,mutate=False):
        with workspace_fixture() as root:
            folder=root/'model';folder.mkdir()
            def module(label):
                p=root/(label+'.py');p.write_bytes(b'# Input fixture\n');return types.SimpleNamespace(__file__=str(p))
            def function(label):
                p=root/(label+'.py');p.write_bytes(b'def build(): pass\n');scope={};exec(compile(p.read_bytes(),str(p),'exec'),scope);return scope['build']
            author=module('author');common=module('common');details=module('details')
            details.roof_patch=function('geometry');details.box=function('primitives')
            author.detail_parts=details;author.sha=sha;author.folders=lambda key:(folder,None)
            helpers=[Path(details.__file__),Path(details.roof_patch.__code__.co_filename),Path(details.box.__code__.co_filename)]
            before={p:p.read_bytes() for p in helpers}
            metadata=dict(detail_parts_sha256=sha(helpers[0]),detail_baseline_helpers_sha256=sha(helpers[1]),detail_primitives_sha256=sha(helpers[2]))
            (folder/'model.json').write_text(json.dumps(metadata))
            def main(key):
                (folder/'runtime-verification.json').write_text(json.dumps(dict(verifier_sha256=sha(common.__file__))))
                if mutate:helpers[2].write_bytes(b'# Changed during validation\n')
            common.main=main
            script=ROOT/'sources/tools/blender/verify_mauna_type6.py'
            with patch.dict(sys.modules,{'remaster_mauna_type6':author,'verify_mauna_mobile_ship':common}),patch.object(sys,'argv',[str(script),'--','--ship','max-combat-craft-type-6']):
                runpy.run_path(str(script),run_name='__main__')
            self.assertEqual(before,{p:p.read_bytes() for p in helpers})
            report=json.loads((folder/'runtime-verification.json').read_bytes())
            self.assertTrue(report['verifier_inputs_unchanged'])
            self.assertEqual(report['verifier_sha256'],sha(script))
            self.assertEqual(report['detail_primitives_sha256'],sha(helpers[2]))

    def test_report_written_only_to_model_folder(self):self.exercise()
    def test_changed_helper_rejected(self):
        with self.assertRaises(AssertionError):self.exercise(mutate=True)

if __name__=='__main__':unittest.main()
