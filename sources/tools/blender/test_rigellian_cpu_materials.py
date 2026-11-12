"""Actual native/imported material regressions for RI01 channel packing."""
from pathlib import Path
import sys
import unittest
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from rigellian_cpu_preservation_checks import textures
ROOT = Path(__file__).resolve().parents[3]


class Materials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT/'sources/objects/rigellian/central-unit'
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False)
        cls.native = textures()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))

    def test_native_imported_values_and_maps(self):
        self.assertEqual(self.native,textures())

    def test_changed_exported_metallic_factor_is_detected(self):
        material = bpy.data.materials['Rigellian refined crown | aged conductor brass']
        shader = material.node_tree.nodes.get('Principled BSDF')
        node = shader.inputs['Metallic'].links[0].from_node
        self.assertEqual(node.type,'MATH')
        previous = node.inputs[1].default_value
        try:
            node.inputs[1].default_value = .1
            self.assertNotEqual(self.native,textures())
        finally:
            node.inputs[1].default_value = previous

    def test_changed_used_colour_texel_is_detected(self):
        material = bpy.data.materials['Rigellian refined crown | aged conductor brass']
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
        raise RuntimeError('RI01 material regressions failed')
