from __future__ import annotations

import sys
import unittest
from pathlib import Path

import torch


sys.path.insert(0, str(Path(__file__).parent))
from rrdbnet_x2 import RrdbNetX2  # noqa: E402


class RrdbNetX2Tests(unittest.TestCase):
    def test_minimal_network_doubles_spatial_dimensions(self) -> None:
        model = RrdbNetX2(feature_count=4, block_count=1, growth_count=2).eval()

        with torch.inference_mode():
            output = model(torch.zeros((1, 3, 8, 10), dtype=torch.float32))

        self.assertEqual((1, 3, 16, 20), tuple(output.shape))


if __name__ == "__main__":
    unittest.main()
