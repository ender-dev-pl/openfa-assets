"""Contracts for original functional source bindings and explicitly unresolved coverage."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from index_legacy_functional_text import REPO,TARGET,build_index,split_records,validate_name


class FunctionalTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index,_=build_index();cls.items={item['id']:item for item in cls.index['records']}
        cls.raw=(REPO.parent/'legacy/_TEXT/ENGLISH.TXT').read_bytes();cls.records=split_records(cls.raw)
        cls.buildings=json.loads((REPO/'content/standard/catalogues/legacy-buildings.json').read_text())['buildings']

    def test_current_published_index_matches_source(self):
        self.assertEqual(json.loads(TARGET.read_text()),self.index)
        self.assertEqual(len(self.items),303)

    def test_all_building_long_descriptions_have_real_byte_ranges(self):
        buildings=[item for item in self.items.values() if item['category']=='buildings']
        self.assertEqual(len(buildings),177)
        for item in buildings:
            ref=next(ref for ref in item['descriptions'] if ref['kind']=='building-long')
            payload=self.raw[ref['offset']:ref['offset']+ref['byte_length']]
            self.assertGreater(len(payload),20)
            self.assertEqual(hashlib.sha256(payload).hexdigest(),ref['sha256'])
            self.assertEqual(self.raw[ref['offset']+ref['byte_length']],0)

    def test_ground_deck_links_to_underground_hangar_description(self):
        deck=self.items['openfa:building/legacy/049'];self.assertEqual(deck['explicit_functional_cross_reference'],'terran:landing-pad')
        pad=self.items[deck['explicit_functional_cross_reference']]
        ref=next(ref for ref in pad['descriptions'] if ref['kind']=='building-long')
        self.assertIn('vast underground hangars',self.records[ref['record']]['text'])

    def test_probe_launch_function_is_satellite_construction_and_launch(self):
        item=self.items['openfa:building/legacy/050'];ref=item['descriptions'][0]
        self.assertEqual(ref['record'],911)
        self.assertIn('constructed and launched',self.records[ref['record']]['text'])
        self.assertIn('espionage',self.records[ref['record']]['text'])

    def test_placeholder_missile_text_is_not_promoted_to_function(self):
        placeholders=[item for item in self.items.values() if any(ref['kind']=='missile-short-placeholder' for ref in item['descriptions'])]
        self.assertEqual([item['global_type'] for item in placeholders],[11,12])
        self.assertTrue(all(item['function_review']=='not-reviewed' for item in placeholders))

    def test_unestablished_text_is_not_claimed_absent_or_reviewed(self):
        unknown=[item for item in self.items.values() if not item['descriptions']]
        self.assertEqual(len(unknown),112)
        self.assertTrue(all(item['narrative_coverage']=='not-established-in-mapped-blocks' for item in unknown))
        self.assertTrue(all(not item['geometry_review'] for item in self.items.values()))

    def test_corrupted_catalogue_name_is_rejected(self):
        definition=copy.deepcopy(self.buildings[0]);definition['legacy']['name']='Incorrect function binding'
        with self.assertRaises(AssertionError): validate_name('buildings',definition,self.records)

    def test_shifted_global_type_is_rejected(self):
        definition=copy.deepcopy(self.buildings[0]);definition['legacy']['globalType']=1
        with self.assertRaises(AssertionError): validate_name('buildings',definition,self.records)


if __name__=='__main__': unittest.main()
