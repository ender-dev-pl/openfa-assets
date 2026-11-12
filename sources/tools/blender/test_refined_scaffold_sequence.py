"""Check reverse assembly and an unobstructed final-building reveal contract."""
import json
from pathlib import Path
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from describe_refined_scaffold_sequence import build_contract, interior_node, ROOT


class ConstructionSequenceTests(unittest.TestCase):
    def test_internal_supports_are_distinct_from_perimeter_and_sockets(self):
        for name in ['Tier 2 upright 24','Tier 2 internal tie 0-0-0-0.5','Tier 0 clamp pin 32-0.5-1','Ground foot 32']:
            self.assertTrue(interior_node(name),name)
        for name in ['Tier 2 upright 23','Tier 0 clamp pin 2-0.5-0','Ground foot 0','Tier 2 TopSocket']:
            self.assertFalse(interior_node(name),name)

    def test_every_definition_uses_exact_reverse_sequence(self):
        data=build_contract()
        self.assertEqual(len(data['definitions']),12)
        for definition in data['definitions']:
            self.assertEqual(definition['dismantling_stages'],list(reversed(definition['erection_stages'])))
            heights=[sum(data['stages'][stage-1]['frames']) for stage in definition['dismantling_stages']]
            self.assertTrue(all(a>b for a,b in zip(heights,heights[1:])))
        self.assertEqual(max(d['ceiling'] for d in data['definitions']),17)

    def test_reveal_retains_building_through_completion(self):
        data=build_contract()
        self.assertFalse(data['phases'][0]['target_building_visible'])
        self.assertTrue(all(p['target_building_visible'] for p in data['phases'][1:]))
        self.assertFalse(data['phases'][-1]['scaffold_visible'])
        self.assertEqual(json.loads((ROOT/'construction-sequence.json').read_text()),data)


if __name__=='__main__':
    unittest.main()
