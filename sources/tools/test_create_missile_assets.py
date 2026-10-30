"""Run with python -m unittest discover -s tools -p test_create_missile_assets.py."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw


TOOL = Path(__file__).with_name("create_missile_assets.py")


class MissileAssetCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "source.png"
        self.output = self.root / "output"

    def run_tool(self, *options):
        return subprocess.run(
            [sys.executable, str(TOOL), str(self.source), "--output", str(self.output), *options],
            capture_output=True, text=True, check=False)

    def test_black_border_is_removed_without_erasing_enclosed_dark_detail(self):
        image = Image.new("RGB", (30, 60))
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 4, 21, 55), fill="yellow")
        draw.rectangle((12, 15, 17, 35), fill="black")
        image.save(self.source)
        result = self.run_tool()
        self.assertEqual(0, result.returncode, result.stderr)
        with Image.open(self.output / "cutout.png") as cutout:
            self.assertEqual((14, 52), cutout.size)
            self.assertEqual((0, 0, 0, 255), cutout.getpixel((5, 20)))
        metadata = json.loads((self.output / "flight-frames.json").read_text())
        self.assertEqual(14, len(metadata))
        with Image.open(self.output / "flight-atlas.png") as atlas:
            for row in metadata:
                with Image.open(self.output / f"flight-{row['index']:02}.png") as frame:
                    rectangle = (row["x"], row["y"], row["x"] + row["width"], row["y"] + row["height"])
                    self.assertEqual(frame.tobytes(), atlas.crop(rectangle).tobytes())

    def test_auto_preserves_existing_partial_alpha_and_black(self):
        image = Image.new("RGBA", (20, 40))
        ImageDraw.Draw(image).rectangle((4, 4, 15, 35), fill=(0, 0, 0, 128))
        image.save(self.source)
        result = self.run_tool()
        self.assertEqual(0, result.returncode, result.stderr)
        with Image.open(self.output / "cutout.png") as cutout:
            self.assertEqual((0, 0, 0, 128), cutout.getpixel((0, 0)))

    def test_empty_input_fails_without_creating_output(self):
        Image.new("RGBA", (20, 40)).save(self.source)
        self.assertNotEqual(0, self.run_tool().returncode)
        self.assertFalse(self.output.exists())

    def test_input_cannot_be_overwritten(self):
        self.output.mkdir()
        self.source = self.output / "preview.png"
        Image.new("RGB", (20, 40), "yellow").save(self.source)
        original = self.source.read_bytes()
        self.assertNotEqual(0, self.run_tool().returncode)
        self.assertEqual(original, self.source.read_bytes())


if __name__ == "__main__":
    unittest.main()
