"""Reject broken animation, weakened runtime claims and stale AC12 evidence."""
import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'sources/tools/blender'))
import achaean_animated_building_runtime_evidence as evidence

class AnimationTests(unittest.TestCase):
    def setUp(self):
        folder=ROOT/'sources/objects/achaean/landing-pad';self.meta=json.loads((folder/'model.json').read_bytes());self.report=json.loads((folder/'runtime-review.json').read_bytes());raw=(folder/'model.glb').read_bytes();self.doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    def check(self):evidence.verify_animation_document(self.meta,self.report,self.doc)
    def test_current_actual_motion(self):self.check()
    def test_missing_clip(self):
        self.doc['animations']=[]
        with self.assertRaises(ValueError):self.check()
    def test_missing_leaf_channel(self):
        self.doc['animations'][0]['channels'].pop()
        with self.assertRaises(AssertionError):self.check()
    def test_wrong_channel_target(self):
        self.doc['animations'][0]['channels'][0]['target']['path']='scale'
        with self.assertRaises(AssertionError):self.check()
    def test_changed_timing(self):
        i=self.doc['animations'][0]['samplers'][0]['input'];self.doc['accessors'][i]['max'][0]+=1
        with self.assertRaises(AssertionError):self.check()
    def test_unsampled_state(self):
        self.report['native_motion']['frames'].remove(20)
        with self.assertRaises(AssertionError):self.check()
    def test_collision(self):
        self.report['imported_motion']['surface_intersections']=1
        with self.assertRaises(AssertionError):self.check()
    def test_altered_retained_travel(self):
        self.report['native_motion']['retained_travel_error']=.01
        with self.assertRaises(AssertionError):self.check()
    def test_obstructed_well(self):
        self.report['imported_motion']['open_floor_heights'][3]=.45
        with self.assertRaises(AssertionError):self.check()
    def test_current_complete_source_bound_evidence(self):
        records=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_bytes())['records'];r=next(r for r in records if r['id']==self.meta['id']);self.assertEqual(evidence.verify(ROOT/'sources',r)['views'],10)
    def test_stale_source(self):
        records=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_bytes())['records'];r=copy.deepcopy(next(r for r in records if r['id']==self.meta['id']));key=next(iter(r['reviewed_model']['runtime_evidence']['files']));r['reviewed_model']['runtime_evidence']['files'][key]='0'*64
        with self.assertRaisesRegex(AssertionError,'Changed evidence'):evidence.verify(ROOT/'sources',r)

if __name__=='__main__':unittest.main()
