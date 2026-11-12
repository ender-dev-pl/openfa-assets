"""Controlled graph, decoding and comparison checks; no asset writes."""
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from material_input_channels import INPUTS, UnsupportedInput, quantize, material_inputs, compare_input, verified_readback_aliases


def main():
    a = np.array([[[20, 40, 60], [80, 100, 120]]], dtype=np.uint8)
    assert compare_input(a, a)['status'] == 'equal-at-8-bit-readback'
    b = a.copy()
    b[0, 1, 2] += 1
    assert compare_input(a, b)['maximum_channel_difference'] == 1
    constant = np.array([[[20, 40, 60]]], dtype=np.uint8)
    repeated = np.repeat(constant, 2, axis=1)
    assert compare_input(constant, repeated)['status'] == 'equal-at-8-bit-readback'
    assert compare_input(a, np.repeat(a, 2, axis=1))['status'] == 'uninspected'
    for value in [float('nan'), float('inf'), -0.1, 1.1]:
        try:
            quantize([value])
        except UnsupportedInput:
            pass
        else:
            raise AssertionError('Invalid/HDR input must not be silently clipped')
    material = bpy.data.materials.new('Channel regression')
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = nodes.get('Principled BSDF')
    image = bpy.data.images.new('Two distinct pixels', width=2, height=1)
    image.colorspace_settings.name = 'Non-Color'
    image.pixels[:] = [.1, .2, .3, 1, .4, .5, .6, 1]
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = image
    links.new(texture.outputs['Color'], shader.inputs['Base Color'])
    links.new(texture.outputs['Color'], shader.inputs['Roughness'])
    records, pixels = material_inputs(material, {})
    assert records['Base Color']['shape'] == [1, 2, 3]
    assert records['Roughness']['uninspected'].startswith('Non-grey')
    separate = nodes.new('ShaderNodeSeparateColor')
    separate.mode = 'RGB'
    links.new(texture.outputs['Color'], separate.inputs[0])
    links.new(separate.outputs['Green'], shader.inputs['Roughness'])
    records, pixels = material_inputs(material, {})
    assert records['Roughness']['source']['selected_channel'] == 1
    assert np.array_equal(pixels['Roughness'], quantize(np.array([[[.2], [.5]]])))
    math = nodes.new('ShaderNodeMath')
    math.operation = 'MULTIPLY'
    math.inputs[1].default_value = .5
    links.new(separate.outputs['Green'], math.inputs[0])
    links.new(math.outputs[0], shader.inputs['Metallic'])
    records, pixels = material_inputs(material, {})
    assert np.array_equal(pixels['Metallic'], quantize(np.array([[[.1], [.25]]])))
    math.operation = 'DIVIDE'
    records, _ = material_inputs(material, {})
    assert records['Metallic']['uninspected'].startswith('Uninspected node MATH')
    inputs = {channel: constant for channel in INPUTS}
    native, imported = {'Shell': inputs}, {'Shell': inputs, 'Shell.001': inputs}
    assert not verified_readback_aliases(native, imported, ['Shell'])
    assert not verified_readback_aliases(native, imported, ['Shell', 'Shell.001'])
    assert verified_readback_aliases(native, imported, ['Shell', 'Shell'])['Shell.001']['native_name'] == 'Shell'
    changed = dict(imported, **{'Shell.001': dict(inputs, Metallic=constant+1)})
    assert not verified_readback_aliases(native, changed, ['Shell', 'Shell'])
    print('MATERIAL_INPUT_CHANNELS_TEST_OK', flush=True)


if __name__ == '__main__':
    main()
