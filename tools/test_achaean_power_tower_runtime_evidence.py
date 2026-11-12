"""Keep AC26 heading and sampled-clearance evidence fail-closed."""
import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'sources/tools/blender'))
from archive_aware_achaean_power_tower_runtime_evidence import verify,verify_animation_document

class DirectionalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=next(r for r in json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_bytes())['records'] if r['id']=='openfa:building/legacy/176')
        folder=ROOT/'sources/objects/achaean/power-tower';cls.meta=json.loads((folder/'model.json').read_bytes());cls.report=json.loads((folder/'runtime-review.json').read_bytes());raw=(folder/'model.glb').read_bytes();cls.doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    def test_current_complete_bound_evidence(self):
        result=verify(ROOT/'sources',self.record);self.assertEqual(result['views'],6);self.assertFalse(result['game_client_integration'])
    def test_reject_heading_channel_replaced_by_translation(self):
        d=copy.deepcopy(self.doc);d['animations'][0]['channels'][0]['target']['path']='translation'
        with self.assertRaises(AssertionError):verify_animation_document(self.meta,self.report,d)
    def test_reject_sparse_export_sampling(self):
        d=copy.deepcopy(self.doc);d['accessors'][d['animations'][0]['samplers'][0]['input']]['count']=17
        with self.assertRaises(AssertionError):verify_animation_document(self.meta,self.report,d)
    def test_reject_missing_bearing_pose(self):
        r=copy.deepcopy(self.report);r['imported_motion']['bearing_contact_checks']=64
        with self.assertRaises(AssertionError):verify_animation_document(self.meta,r,self.doc)
    def test_reject_intersection(self):
        r=copy.deepcopy(self.report);r['native_motion']['nonbearing_surface_intersections']=1
        with self.assertRaises(AssertionError):verify_animation_document(self.meta,r,self.doc)
    def test_reject_false_continuous_sweep_claim(self):
        r=copy.deepcopy(self.report);r['continuous_sweep_proven']=True
        with self.assertRaises(AssertionError):verify_animation_document(self.meta,r,self.doc)
    def test_reject_missing_nozzle_bore_check(self):
        r=copy.deepcopy(self.report);r['imported_motion']['emitter_lugs_support_bore_lip_checks']=519
        with self.assertRaises(AssertionError):verify_animation_document(self.meta,r,self.doc)
    def test_reject_nozzle_outside_rotating_head(self):
        m=copy.deepcopy(self.meta);m['animation']['moving_meshes'].remove('AC26 long central emitter')
        with self.assertRaises(AssertionError):verify_animation_document(m,self.report,self.doc)

if __name__=='__main__':unittest.main()
