"""Integration checks against actual installed original scaffold limits."""
import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from index_scaffold_stage_limits import build_index,REPO


@unittest.skipUnless((REPO.parent/'legacy/FRAGILE.LE').is_file(),'Requires installed original LE')
class ScaffoldLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=build_index();cls.records={r['id']:r for r in cls.index['records']}

    def test_every_original_building_has_a_limit(self):
        self.assertEqual(sorted(r['global_type'] for r in self.records.values()),list(range(177)))

    def test_probe_launch_does_not_inherit_databank_stack_height(self):
        probe=self.records['openfa:building/legacy/050'];data=self.records['openfa:building/legacy/047']
        self.assertEqual(probe['family'],data['family'])
        self.assertEqual((probe['stage_ceiling_raw'],probe['max_tiers']),(2,1))
        self.assertEqual((data['stage_ceiling_raw'],data['max_tiers']),(17,9))
        self.assertEqual([r['frame'] for r in data['max_stage_chain']],[2]*8+[1])

    def test_actual_largest_stack_has_eleven_levels(self):
        record=self.records['openfa:building/legacy/136']
        self.assertEqual(record['name'],'Elite Block')
        self.assertEqual((record['stage_ceiling_raw'],record['max_tiers']),(22,11))
        self.assertEqual([r['frame'] for r in record['max_stage_chain']],[2]*11)

    def test_duration_is_not_a_substitute_for_height_ceiling(self):
        self.assertGreater(sum(r['construction_updates']!=r['stage_ceiling_raw'] for r in self.records.values()),150)
        self.assertEqual(self.index['buildings_requiring_stacking'],155)

    def test_family_required_range_covers_every_dependent_definition(self):
        families={f['family']:f for f in self.index['families']}
        for r in self.records.values():
            self.assertLessEqual(r['max_tiers'],families[r['family']]['max_required_tiers'])
            self.assertEqual(sum(v['frame'] for v in r['max_stage_chain']),r['max_stage_while_constructing'])

    def test_ris2_prototype_covers_the_source_required_range(self):
        directory=REPO/'docs/assets/reconstruction/scaffolds/rigellian/size-2'
        meta=json.loads((directory/'model.json').read_text())
        family=next(f for f in self.index['families'] if f['family']=='RIS2')
        self.assertEqual([c['total_stage'] for c in meta['cases']],list(range(1,family['max_required_stage']+1)))
        self.assertEqual(len(meta['cases'][-1]['frames']),family['max_required_tiers'])

    def test_glb_mesh_reuse_preserves_all_scaffold_object_nodes(self):
        directory=REPO/'docs/assets/reconstruction/scaffolds/rigellian/size-2'
        meta=json.loads((directory/'model.json').read_text())
        for case in meta['cases']:
            raw=(directory/f"stage-{case['total_stage']:02}/model.glb").read_bytes()
            length=struct.unpack_from('<I',raw,12)[0];document=json.loads(raw[20:20+length])
            self.assertEqual(len(document['meshes']),case['unique_meshes'])
            self.assertEqual(sum('mesh' in node for node in document['nodes']),case['mesh_objects'])
            self.assertLess(case['unique_meshes'],case['mesh_objects'])


    def test_signed_counter_is_backed_by_original_opcode(self):
        self.assertEqual(self.index['instruction_evidence']['0x44a27']['bytes'],'0fbe490a')
        self.assertEqual(self.index['data_object_base'],'0xB0000')


if __name__=='__main__': unittest.main()
