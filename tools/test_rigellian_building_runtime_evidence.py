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
        result = verify_runtime_evidence(ROOT / 'sources', self.record)
        self.assertEqual(result['views'], 6)
        self.assertFalse(result['game_client_integration'])

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


if __name__ == '__main__':
    unittest.main()
