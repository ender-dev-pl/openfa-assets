"""Actual native/imported RI02 used-map and material-variant regressions."""
from pathlib import Path
import sys
import unittest
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from rigellian_filtration_preservation_checks import textures
ROOT = Path(__file__).resolve().parents[3]


class Materials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT/'sources/objects/rigellian/filtration-plant'
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False)
        cls.native = textures()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))

    def test_native_imported_used_properties_and_maps(self):
        self.assertEqual(self.native,textures())

    def test_unequal_uv_index_material_variant_is_rejected(self):
        variants = [m for m in bpy.data.materials if m.name.startswith('RI02 | aged jade shell.')]
        self.assertTrue(variants)
        shader = variants[0].node_tree.nodes.get('Principled BSDF')
        alpha = shader.inputs['Alpha']
        self.assertFalse(alpha.is_linked)
        previous = alpha.default_value
        try:
            alpha.default_value = .5
            with self.assertRaisesRegex(AssertionError,'Unequal exported UV-index material variants'):
                textures()
        finally:
            alpha.default_value = previous

    def test_changed_used_colour_texel_is_detected(self):
        material = bpy.data.materials['RI02 | aged jade shell']
        shader = material.node_tree.nodes.get('Principled BSDF')
        image = shader.inputs['Base Color'].links[0].from_node.image
        previous = image.pixels[0]
        try:
            image.pixels[0] = .9 if previous<.5 else .1
            self.assertNotEqual(self.native,textures())
        finally:
            image.pixels[0] = previous


if __name__=='__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Materials))
    if not result.wasSuccessful():
        raise RuntimeError('RI02 material regressions failed')
