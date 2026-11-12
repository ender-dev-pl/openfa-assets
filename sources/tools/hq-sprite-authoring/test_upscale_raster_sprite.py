from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image


sys.path.insert(0, str(Path(__file__).parent))
import upscale_raster_sprite as module  # noqa: E402


class UpscaleRasterSpriteTests(unittest.TestCase):
    def test_edge_reconstruction_uses_nearest_opaque_colour(self) -> None:
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[1, 1] = (210, 80, 30, 255)

        reconstructed = module.reconstruct_edge_colours(rgba)

        np.testing.assert_array_equal(
            reconstructed,
            np.full((3, 3, 3), (210, 80, 30), dtype=np.uint8),
        )

    def test_upscale_produces_smooth_alpha_without_hidden_rgb(self) -> None:
        source = Image.new("RGBA", (3, 3), (0, 0, 0, 0))
        source.putpixel((1, 1), (220, 100, 40, 255))

        result = module.upscale_crop(
            source,
            0.025,
            0.9,
            0.9,
            0.7,
            0.12,
            0.35,
            0.55,
            None,
            0.55,
        )

        rgba = np.asarray(result)
        self.assertEqual((6, 6), result.size)
        self.assertGreater(np.count_nonzero((rgba[..., 3] > 0) & (rgba[..., 3] < 255)), 0)
        self.assertFalse(np.any(rgba[rgba[..., 3] == 0, :3]))

    def test_signed_distance_alpha_rounds_a_binary_corner(self) -> None:
        alpha = np.zeros((7, 7), dtype=np.float32)
        alpha[2:5, 2:5] = 1.0

        result = module.smooth_signed_distance_alpha(alpha, (14, 14), 0.35, 0.55)

        self.assertGreater(np.count_nonzero((result > 0) & (result < 1)), 0)
        self.assertEqual(1.0, float(result[7, 7]))
        self.assertEqual(0.0, float(result[0, 0]))

    def test_limited_sharpening_stays_inside_local_range(self) -> None:
        ramp = np.linspace(0.1, 0.9, 25, dtype=np.float32).reshape(5, 5)
        image = np.dstack((ramp, ramp, ramp))

        sharpened = module.limited_unsharp_mask(image, 0.8, 0.65, 0.1)

        self.assertGreaterEqual(float(sharpened.min()), float(image.min()))
        self.assertLessEqual(float(sharpened.max()), float(image.max()))


if __name__ == "__main__":
    unittest.main()
