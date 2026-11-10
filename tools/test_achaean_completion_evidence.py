"""Reject catalogue omissions, duplicate packages and stale completion evidence."""
import copy
import unittest

from audit_achaean_building_completion import DOCS, ROOT, audit, read, selections


class AchaeanCompletionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery = read(DOCS / 'achaean-building-remaster-delivery.json')
        cls.inventory = read(DOCS / 'inventory.json')
        cls.gallery = read(ROOT / 'gallery/catalogue.json')

    def test_current_complete_evidence_matches_recorded_audit(self):
        self.assertEqual(audit(), read(DOCS / 'achaean-building-completion-audit.json'))

    def test_reject_missing_building_even_if_pending_is_empty(self):
        delivery = copy.deepcopy(self.delivery)
        delivery['models'].pop()
        with self.assertRaises(AssertionError):
            selections(delivery, self.inventory, self.gallery)

    def test_reject_duplicate_canonical_pair(self):
        delivery = copy.deepcopy(self.delivery)
        for field in ['blend', 'glb']:
            delivery['models'][-1][field] = delivery['models'][-2][field]
        with self.assertRaises(AssertionError):
            selections(delivery, self.inventory, self.gallery)

    def test_reject_extra_historical_package_choice(self):
        inventory = copy.deepcopy(self.inventory)
        record = next(x for x in inventory['records'] if x['id'] == 'openfa:building/legacy/162')
        record['available_studies'].append(copy.deepcopy(record['historical_studies'][0]))
        with self.assertRaises((AssertionError, ValueError)):
            selections(self.delivery, inventory, self.gallery)

    def test_reject_other_building_glb_in_gallery(self):
        gallery = copy.deepcopy(self.gallery)
        row = next(x for x in gallery if x['id'] == 'openfa:building/legacy/175')
        row['studies'][0]['glb'] = 'sources/objects/achaean/power-tower/model.glb'
        with self.assertRaises(AssertionError):
            selections(self.delivery, self.inventory, gallery)


if __name__ == '__main__':
    unittest.main()
