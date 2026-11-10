"""Exercise current proof and reject misbound canonical building evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sources/tools/blender'))
from model_runtime_evidence import verify_runtime_evidence


class Evidence(unittest.TestCase):
    def setUp(self):
        data = json.loads((ROOT / 'sources/docs/reconstruction/models/inventory.json').read_bytes())
        self.record = next(row for row in data['records'] if row['id'] == 'openfa:building/legacy/042')

    def test_current_runtime_and_canonical_selection(self):
        data = json.loads((ROOT / 'sources/docs/reconstruction/models/inventory.json').read_bytes())
        checked = []
        for record in data['records']:
            reviewed = record.get('reviewed_model')
            proof = reviewed.get('runtime_evidence') if isinstance(reviewed, dict) else None
            if isinstance(proof, dict) and proof.get('format') == 'rigellian-building-remaster-v1':
                result = verify_runtime_evidence(ROOT / 'sources', record)
                folder = ROOT / 'sources' / Path(record['reviewed_model']['blend']).parent
                metadata = json.loads((folder / 'model.json').read_bytes())
                expected_views = 16 if metadata.get('animation',{}).get('mechanism_kind') == 'ri18-supported-dome-v1' else (40 if metadata.get('animation') else 6)
                if metadata.get('articulation'):
                    expected_views = 38
                self.assertEqual(result['views'], expected_views)
                self.assertFalse(result['game_client_integration'])
                checked.append(record['id'])
        self.assertIn('openfa:building/legacy/042', checked)

    def test_reject_changed_imported_render_identity(self):
        proof = self.record['reviewed_model']['runtime_evidence']
        key = next(key for key in proof['files'] if key.endswith('imported-front-quarter.png'))
        proof['files'][key] = '0' * 64
        with self.assertRaises(AssertionError):
            verify_runtime_evidence(ROOT / 'sources', self.record)

    def test_reject_duplicate_current_payload(self):
        self.record['available_studies'].append(deepcopy(self.record['available_studies'][0]))
        with self.assertRaises(ValueError):
            verify_runtime_evidence(ROOT / 'sources', self.record)

    def test_reject_unproven_game_client_promotion(self):
        self.record['reviewed_model']['runtime_evidence']['game_client_integration'] = True
        with self.assertRaises(AssertionError):
            verify_runtime_evidence(ROOT / 'sources', self.record)

    def test_animated_contract_rejects_missing_state_or_weakened_sweep(self):
        import struct
        from rigellian_building_runtime_evidence import verify_animation_contract
        folder = ROOT / 'sources/objects/rigellian/ground-deck'
        metadata = json.loads((folder / 'model.json').read_bytes())
        report = json.loads((folder / 'runtime-review.json').read_bytes())
        raw = (folder / 'model.glb').read_bytes()
        document = json.loads(raw[20:20+struct.unpack_from('<I', raw, 12)[0]])
        verify_animation_contract(metadata, report, document)
        wrong = deepcopy(metadata)
        wrong['states'].pop()
        with self.assertRaises(AssertionError):
            verify_animation_contract(wrong, report, document)
        wrong = deepcopy(report)
        wrong['animation_validation']['cycle_integer_frames'] = 60
        with self.assertRaises(AssertionError):
            verify_animation_contract(metadata, wrong, document)
        wrong = deepcopy(document)
        for clip in wrong['animations']:
            if clip['name'] == metadata['animation']['descriptor_clip']:
                clip['samplers'][0]['interpolation'] = 'LINEAR'
        with self.assertRaises(AssertionError):
            verify_animation_contract(metadata, report, wrong)

    def test_supported_dome_contract_rejects_weakened_hardware_or_wrong_motion(self):
        import struct
        from rigellian_building_runtime_evidence import verify_animation_contract
        folder = ROOT / 'sources/objects/rigellian/missile-launcher'
        metadata = json.loads((folder / 'model.json').read_bytes())
        report = json.loads((folder / 'runtime-review.json').read_bytes())
        raw = (folder / 'model.glb').read_bytes()
        document = json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
        verify_animation_contract(metadata,report,document)
        wrong = deepcopy(report)
        wrong['supported_hardware_sweep']['imported']['samples'][20]['opposite_hardware_contacts'] = 1
        with self.assertRaises(AssertionError):
            verify_animation_contract(metadata,wrong,document)
        wrong = deepcopy(report)
        wrong['sampled_motion']['cycle_frames'].pop()
        with self.assertRaises(AssertionError):
            verify_animation_contract(metadata,wrong,document)
        wrong = deepcopy(metadata)
        wrong['states'][5]['angle_degrees'] += 5
        with self.assertRaises(AssertionError):
            verify_animation_contract(wrong,report,document)
        wrong = deepcopy(document)
        wrong['animations'][0]['channels'][0]['target']['path'] = 'translation'
        with self.assertRaises(AssertionError):
            verify_animation_contract(metadata,report,wrong)

    def test_manual_yaw_contract_rejects_wrong_hierarchy_or_incomplete_poses(self):
        import struct
        from rigellian_building_runtime_evidence import verify_manual_yaw_contract
        folder = ROOT/'sources/objects/rigellian/thermal-lance'
        metadata = json.loads((folder/'model.json').read_bytes())
        report = json.loads((folder/'runtime-review.json').read_bytes())
        raw = (folder/'model.glb').read_bytes()
        document = json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
        verify_manual_yaw_contract(metadata,report,document)
        wrong = deepcopy(report)
        wrong['imported']['yaw_validation']['poses'].pop()
        with self.assertRaises(AssertionError):
            verify_manual_yaw_contract(metadata,wrong,document)
        wrong = deepcopy(report)
        wrong['native']['yaw_validation']['poses'][4]['fixed_base_unchanged'] = False
        with self.assertRaises(AssertionError):
            verify_manual_yaw_contract(metadata,wrong,document)
        wrong = deepcopy(document)
        pivot = next(n for n in wrong['nodes'] if n['name']=='YawPivot')
        pivot['children'].pop()
        with self.assertRaises(AssertionError):
            verify_manual_yaw_contract(metadata,report,wrong)
        wrong = deepcopy(metadata)
        wrong['articulation']['model_yaw_phase_sign_calibrated'] = True
        with self.assertRaises(AssertionError):
            verify_manual_yaw_contract(wrong,report,document)

    def test_retained_extractor_rejects_missing_or_changed_uv_evidence(self):
        from rigellian_building_runtime_evidence import verify_retained_extractor_contract
        folder = ROOT/'sources/objects/rigellian/extractor'
        metadata = json.loads((folder/'model.json').read_bytes())
        report = json.loads((folder/'runtime-review.json').read_bytes())
        verify_retained_extractor_contract(metadata,report)
        wrong = deepcopy(report)
        wrong['exported_uv_comparison']['maximum_uv_corner_error'] = .01
        with self.assertRaises(AssertionError):
            verify_retained_extractor_contract(metadata,wrong)
        wrong = deepcopy(report)
        wrong['source_uv_comparison']['matched_directed_corners'] = 0
        with self.assertRaises(AssertionError):
            verify_retained_extractor_contract(metadata,wrong)
        wrong = deepcopy(report)
        wrong['protected_parts'].pop()
        with self.assertRaises(AssertionError):
            verify_retained_extractor_contract(metadata,wrong)

    def test_static_open_port_evidence_cannot_be_omitted(self):
        data = json.loads((ROOT / 'sources/docs/reconstruction/models/inventory.json').read_bytes())
        record = next(row for row in data['records'] if row['id'] == 'openfa:building/legacy/050')
        proof = record['reviewed_model']['runtime_evidence']
        del proof['files']['sources/docs/reconstruction/models/launch-facility-animation-audit.json']
        with self.assertRaises(AssertionError):
            verify_runtime_evidence(ROOT / 'sources', record)


if __name__ == '__main__':
    unittest.main()
