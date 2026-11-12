"""Focused Blender-runtime tests for changed-tessellation UV correspondence."""
import sys
from pathlib import Path
import unittest
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from rigellian_surface_uv_checks import interpolate_uv,compare_surface_uv


class SurfaceUV(unittest.TestCase):
    def test_regular_and_thin_triangles(self):
        for height in [1,1e-9]:
            points = [Vector((0,0,0)),Vector((1,0,0)),Vector((1,height,0))]
            uvs = [Vector((0,0)),Vector((1,0)),Vector((1,1))]
            result = interpolate_uv(Vector((.75,height*.25,0)),points,uvs)
            self.assertLess((result[0]-Vector((.75,.25))).length,1e-6)

    def test_collinear_edge_and_coincident_vertices(self):
        points = [Vector((0,0,0)),Vector((1,0,0)),Vector((2,0,0))]
        uvs = [Vector((0,0)),Vector((.5,0)),Vector((1,0))]
        result = interpolate_uv(Vector((.5,0,0)),points,uvs)
        self.assertTrue(result)
        self.assertTrue(all((uv-Vector((.25,0))).length<1e-6 for uv in result))
        coincident = [Vector((0,0,0)) for _ in range(3)]
        self.assertTrue(interpolate_uv(coincident[0],coincident,uvs))

    def test_uv_correspondence_rejects_changed_mapping(self):
        points = [Vector((0,0,0)),Vector((1,0,0)),Vector((0,1,0))]
        def snapshot(offset):
            uvs = [Vector((offset,0)),Vector((1+offset,0)),Vector((offset,1))]
            group = dict(points=points,faces=[(0,1,2)],uvs=[uvs],
                samples={i:(point,uv) for i,(point,uv) in enumerate(zip(points,uvs))},repeat=False,
                tree=BVHTree.FromPolygons(points,[(0,1,2)],all_triangles=True))
            return {'part':{'material':group}}
        self.assertEqual(compare_surface_uv(snapshot(0),snapshot(0))['matched_directed_corners'],6)
        with self.assertRaises(AssertionError):
            compare_surface_uv(snapshot(0),snapshot(.1))


if __name__=='__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SurfaceUV)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError('Surface UV checks failed')
