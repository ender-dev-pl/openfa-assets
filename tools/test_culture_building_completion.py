"""Completion rejects missing scope,duplicate delivery and stale gallery/history."""
import copy
import unittest
from unittest.mock import patch
import audit_culture_building_completion as auditor


class CompletedCultureAuditTests(unittest.TestCase):
    def mutate(self, suffix, change):
        original = auditor.load
        def altered(path):
            data = original(path)
            if path.as_posix().endswith(suffix):
                data = copy.deepcopy(data)
                change(data)
            return data
        return patch.object(auditor, 'load', altered)

    def test_actual_completed_mikotaj(self):
        result = auditor.audit('mikotaj')
        self.assertEqual(result['model_count'], 21)
        self.assertEqual(result['render_pairs'], 63)
        self.assertTrue(all(not r['game_client_integration'] for r in result['models']))

    def test_missing_model_rejected(self):
        with self.mutate('mikotaj-building-remaster-delivery.json', lambda d: d['models'].pop()):
            with self.assertRaisesRegex(AssertionError, 'Missing or duplicate'):
                auditor.audit('mikotaj')

    def test_duplicate_model_rejected(self):
        def duplicate(data):
            data['models'][-1] = copy.deepcopy(data['models'][0])
        with self.mutate('mikotaj-building-remaster-delivery.json', duplicate):
            with self.assertRaisesRegex(AssertionError, 'Missing or duplicate'):
                auditor.audit('mikotaj')

    def test_wrong_gallery_selection_rejected(self):
        def stale(data):
            row = next(r for r in data if r['id'] == 'openfa:building/legacy/086')
            row['studies'][0]['glb'] = 'old/model.glb'
        with self.mutate('gallery/catalogue.json', stale):
            with self.assertRaisesRegex(AssertionError, 'Gallery canonical mismatch'):
                auditor.audit('mikotaj')

    def test_wrong_function_record_rejected(self):
        def unrelated(data):
            data['functional_source']['records'] = [999999]
        with self.mutate('mk01-concept-review.json', unrelated):
            with self.assertRaisesRegex(AssertionError, 'Functional source record mismatch'):
                auditor.audit('mikotaj')

    def test_missing_historical_pair_rejected(self):
        def missing(data):
            row = next(r for r in data['records'] if r['id'] == 'openfa:building/legacy/086')
            row['historical_studies'] = []
        with self.mutate('inventory.json', missing):
            with self.assertRaisesRegex(AssertionError, 'Missing historical selection'):
                auditor.audit('mikotaj')


if __name__ == '__main__':
    unittest.main()
