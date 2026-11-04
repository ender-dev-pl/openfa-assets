"""Permit isolated antialias samples while rejecting actual coverage regressions."""
from pathlib import Path
import sys
import unittest
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scaffold_render_coverage import compare_coverage


class CoverageTests(unittest.TestCase):
    def image(self):
        image=Image.new('RGBA',(32,32));ImageDraw.Draw(image).rectangle((8,8,23,23),fill=(100,100,100,255))
        return image

    def test_identical_coverage(self):
        image=self.image();self.assertEqual(compare_coverage(image,image)['alpha_coverage_error_pixels'],0)

    def test_one_subpixel_boundary_sample(self):
        a=self.image();b=a.copy();a.putpixel((8,12),(100,100,100,127));b.putpixel((8,12),(100,100,100,138))
        self.assertEqual(compare_coverage(a,b)['binary_silhouette_differing_pixels'],1)

    def test_missing_interior_pixel_is_not_antialiasing(self):
        a=self.image();b=a.copy();b.putpixel((15,15),(0,0,0,0))
        with self.assertRaises(AssertionError):compare_coverage(a,b)

    def test_subpixel_slot_crossing_threshold(self):
        a=self.image();b=a.copy();a.putpixel((15,15),(100,100,100,117));b.putpixel((15,15),(100,100,100,128))
        self.assertEqual(compare_coverage(a,b)['binary_silhouette_differing_pixels'],1)

    def test_shifted_geometry_fails(self):
        a=self.image();b=Image.new('RGBA',a.size);b.paste(a,(1,0))
        with self.assertRaises(AssertionError):compare_coverage(a,b)

    def test_removed_corner_piece_fails(self):
        a=self.image();b=a.copy();ImageDraw.Draw(b).rectangle((8,8,13,13),fill=(0,0,0,0))
        with self.assertRaises(AssertionError):compare_coverage(a,b)


if __name__=='__main__':unittest.main()
