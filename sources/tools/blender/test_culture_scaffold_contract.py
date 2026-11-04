"""All-family progression and user-required reverse reveal regression contracts."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from culture_scaffold_contract import chain,recipe,phases,definitions_for

REPO=Path(__file__).resolve().parents[2]
LIMITS=json.loads((REPO/'docs/reconstruction/models/scaffold-stage-limits.json').read_text())
REFERENCES=json.loads((REPO/'docs/reconstruction/models/shared-construction-references.json').read_text())


class CultureScaffoldContractTests(unittest.TestCase):
    def test_every_required_state_has_exact_carry_and_no_empty_top_tier(self):
        for family in LIMITS['families']:
            if not family['max_required_stage']:continue
            _,capacity,_,pitch=recipe(family,REFERENCES)
            self.assertGreater(pitch,0)
            for stage in range(1,family['max_required_stage']+1):
                frames=chain(stage,capacity)
                self.assertEqual(sum(frames),stage)
                self.assertTrue(all(value==capacity for value in frames[:-1]))
                self.assertTrue(1<=frames[-1]<=capacity)
            self.assertEqual(len(frames),family['max_required_tiers'])

    def test_every_building_has_a_reverse_dismantling_sequence(self):
        definitions=[d for family in LIMITS['families'] for d in definitions_for(family['family'],LIMITS)]
        self.assertEqual(len(definitions),177)
        self.assertEqual(len({d['id'] for d in definitions}),177)
        for definition in definitions:
            self.assertEqual(definition['dismantling_stages'],definition['erection_stages'][::-1])
            self.assertEqual(definition['erection_stages'][-1],definition['ceiling'])

    def test_building_remains_visible_after_full_height_reveal(self):
        states=phases()
        self.assertFalse(states[0]['building_visible'])
        self.assertTrue(all(s['building_visible'] for s in states[1:]))
        self.assertFalse(states[-1]['scaffold_visible'])

    def test_terran_capacities_are_not_collapsed_to_alien_two_stage_modules(self):
        capacities={f['family']:recipe(f,REFERENCES)[1] for f in LIMITS['families']}
        self.assertEqual([capacities[f'PBS{i}'] for i in range(1,5)],[16,8,4,2])
        self.assertEqual({v for k,v in capacities.items() if not k.startswith('PB')},{2})

    def test_empty_or_negative_states_are_rejected(self):
        for stage,capacity in [(0,2),(-1,2),(1,0)]:
            with self.assertRaises(ValueError):chain(stage,capacity)


if __name__=='__main__':unittest.main()
