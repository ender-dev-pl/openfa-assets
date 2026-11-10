"""Regression checks for Achaean canonical evidence and export/pixel gates."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sources/tools/blender'))
import achaean_static_building_runtime_evidence as evidence

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=next(r for r in json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_bytes())['records'] if r['id']=='openfa:building/legacy/152')
    def test_current_runtime_and_pixels(self):
        result=evidence.verify(ROOT/'sources',self.record)
        self.assertEqual(result['views'],6)
        self.assertFalse(result['game_client_integration'])
    def test_all_current_static_deliveries_have_valid_runtime_evidence(self):
        records=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_bytes())['records']
        selected=[]
        for record in records:
            reviewed=record.get('reviewed_model')
            proof=reviewed.get('runtime_evidence') if isinstance(reviewed,dict) else None
            if isinstance(proof,dict) and proof.get('format')=='achaean-static-building-remaster-v2':selected.append(record)
        self.assertTrue(selected)
        for record in selected:
            with self.subTest(id=record['id']):evidence.verify(ROOT/'sources',record)
    def test_changed_source_is_rejected_before_acceptance(self):
        r=copy.deepcopy(self.record);key=next(iter(r['reviewed_model']['runtime_evidence']['files']));r['reviewed_model']['runtime_evidence']['files'][key]='0'*64
        with self.assertRaisesRegex(AssertionError,'Changed evidence'):evidence.verify(ROOT/'sources',r)
    def test_export_accessor_budget_is_independently_checked(self):
        original=json.loads
        def decode(*a,**k):
            value=original(*a,**k)
            if isinstance(value,dict) and value.get('asset',{}).get('version')=='2.0':
                accessor=value['meshes'][0]['primitives'][0]['indices'];value['accessors'][accessor]['count']+=3
            return value
        with patch.object(evidence.json,'loads',side_effect=decode),self.assertRaises(AssertionError):evidence.verify(ROOT/'sources',self.record)
    def test_materially_different_render_is_rejected(self):
        a=Image.new('RGBA',(512,512));b=a.copy();ImageDraw.Draw(a).rectangle((64,64,448,448),fill=(100,100,100,255));ImageDraw.Draw(b).rectangle((64,64,448,448),fill=(200,200,200,255))
        with patch('achaean_building_runtime_evidence.Image.open',side_effect=[a,b]),self.assertRaises(AssertionError):evidence.pixel_pairs(Path('.'))
    def test_catalogue_spatial_contract_mismatch_is_rejected(self):
        r=copy.deepcopy(self.record);r['footprint']=[4,4]
        with self.assertRaises(AssertionError):evidence.verify(ROOT/'sources',r)
    def test_export_budget_counts_instances_not_just_unique_meshes(self):
        document=dict(nodes=[dict(mesh=0),dict(mesh=0)],meshes=[dict(primitives=[dict(indices=0)])],accessors=[dict(count=9)])
        self.assertEqual(evidence.exported_triangles(document),6)
    def test_inconsistent_current_binary_selection_is_rejected(self):
        r=copy.deepcopy(self.record);r['reviewed_model']['sha256']='0'*64
        with self.assertRaises(AssertionError):evidence.verify(ROOT/'sources',r)

if __name__=='__main__':unittest.main()
