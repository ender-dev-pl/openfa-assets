from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image


MODULE_PATH = Path(__file__).with_name("render_directional_sprite.py")
SPEC = importlib.util.spec_from_file_location("render_directional_sprite", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RenderDirectionalSpriteTests(unittest.TestCase):
    def test_srgb_round_trip_preserves_eight_bit_values(self) -> None:
        values = np.arange(256, dtype=np.float32) / 255.0
        encoded = MODULE.linear_to_srgb(MODULE.srgb_to_linear(values))
        actual = np.clip(encoded * 255.0 + 0.5, 0, 255).astype(np.uint8)
        np.testing.assert_array_equal(actual, np.arange(256, dtype=np.uint8))

    def test_resize_uses_straight_alpha_without_dark_edge_colours(self) -> None:
        source = Image.new("RGBA", (2, 1), (0, 0, 0, 0))
        source.putpixel((0, 0), (220, 120, 40, 255))
        resized = MODULE.resize_straight_alpha(source, (8, 4))
        rgba = np.asarray(resized)
        translucent = rgba[(rgba[..., 3] > 0) & (rgba[..., 3] < 255)]
        self.assertGreater(len(translucent), 0)
        self.assertTrue(np.all(translucent[:, 0] >= 210))
        self.assertTrue(np.all(translucent[:, 1] >= 110))

    def test_logical_frame_reports_exact_2x_bounds(self) -> None:
        frame = MODULE.LogicalFrame(0, 208, 128, 54, 9, 103, 106)
        self.assertEqual((108, 18, 206, 212), frame.physical_bounds)

    def test_tiny_island_is_removed_without_removing_main_components(self) -> None:
        image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        for y in range(10, 40):
            for x in range(10, 40):
                image.putpixel((x, y), (255, 0, 0, 255))
        for y in range(60, 80):
            for x in range(60, 80):
                image.putpixel((x, y), (0, 255, 0, 255))
        image.putpixel((99, 99), (0, 0, 255, 255))

        cleaned = MODULE.remove_tiny_components(image)

        self.assertEqual((255, 0, 0, 255), cleaned.getpixel((20, 20)))
        self.assertEqual((0, 255, 0, 255), cleaned.getpixel((70, 70)))
        self.assertEqual((0, 0, 0, 0), cleaned.getpixel((99, 99)))


if __name__ == "__main__":
    unittest.main()
