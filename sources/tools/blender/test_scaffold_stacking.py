"""Boundary contracts recovered from construction descriptor chaining; analytical only."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from analyse_scaffold_stacking import scaffold_chain


class ScaffoldStackingTests(unittest.TestCase):
    def test_alien_stage_boundary(self):
        for stage,expected in [(1,[1]),(2,[2]),(3,[2,1]),(4,[2,2]),(5,[2,2,1])]:
            self.assertEqual([r['frame'] for r in scaffold_chain(stage-1,0,255,2)],expected)

    def test_all_terran_capacities_carry_into_new_tier(self):
        for capacity in [2,4,8,16]:
            self.assertEqual([r['frame'] for r in scaffold_chain(capacity,0,255,capacity)],[capacity,1])

    def test_exact_multiple_does_not_add_empty_tier(self):
        self.assertEqual([r['frame'] for r in scaffold_chain(31,0,255,16)],[16,16])

    def test_each_alien_tier_moves_eight_pixels_at_full_scale(self):
        self.assertEqual([r['screen_y_offset_pixels'] for r in scaffold_chain(6,0,255,2)],[0,-8,-16,-24])

    def test_scale_byte_zero_means_256_and_128_means_half(self):
        a=scaffold_chain(4,0,255,2,0);b=scaffold_chain(4,0,255,2,128)
        self.assertEqual(a[2]['screen_y_offset_fixed'],2*b[2]['screen_y_offset_fixed'])
        self.assertEqual(a[2]['screen_y_offset_fixed'],-16*65536)

    def test_resource_byte_caps_total_stage_not_frame_count(self):
        self.assertEqual([r['frame'] for r in scaffold_chain(24,0,5,2)],[2,2,1])

    def test_signed_remaining_can_raise_stage_above_duration(self):
        self.assertEqual([r['frame'] for r in scaffold_chain(2,-2,255,2)],[2,2,1])

    def test_initial_stage_clamps_to_one(self):
        self.assertEqual([r['frame'] for r in scaffold_chain(0,1,255,2)],[1])


if __name__=='__main__': unittest.main()
