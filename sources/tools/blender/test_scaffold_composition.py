"""Regression checks for original-instruction scaffold ordering fixtures."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe_scaffold_composition import build_evidence,REPO


@unittest.skipUnless((REPO.parent/'legacy/FRAGILE.LE').is_file(),'Requires installed original LE')
class ScaffoldCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.evidence=build_evidence()

    def test_child_keys_increase_through_catalogue_maximum_tiers(self):
        chain=next(c['child_chain'] for c in self.evidence['cases'] if c.get('child_chain',{}).get('levels')==11)
        self.assertEqual(chain['keys'],list(range(100,111)))
        self.assertEqual(chain['allocator_calls'],10)
        self.assertTrue(chain['existing_child_reused'])

    def test_original_sort_and_callback_dispatch_agree_for_reversed_chains(self):
        for case in self.evidence['cases']:
            dispatch=case['dispatch']
            self.assertEqual(dispatch['prepared_keys'],sorted(dispatch['input_keys']))
            self.assertEqual(dispatch['callback_keys'],dispatch['prepared_keys'])
            self.assertTrue(dispatch['executed_code_unchanged'])

    def test_mixed_insertion_order_does_not_determine_paint_order(self):
        case=self.evidence['cases'][-1]['dispatch']
        self.assertEqual(case['input_keys'],[103,100,102,101])
        self.assertEqual(case['callback_keys'],[100,101,102,103])

    def test_evidence_does_not_claim_pixel_rasterizer_execution(self):
        self.assertTrue(self.evidence['body_order_verified'])
        self.assertFalse(self.evidence['full_pixel_composition_verified'])
        self.assertIn('0x7FC5A',self.evidence['substitutions'])
        self.assertIn('0x72393',self.evidence['substitutions'])


if __name__=='__main__': unittest.main()
