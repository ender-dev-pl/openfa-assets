"""Author an XS01-inspired spatial airburst with flash, fragments and a shell."""
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pyro_explosions import setup, key, node, control

ROOT = Path(__file__).resolve().parents[2] / 'docs/assets/reconstruction/effects/pyro/airborne'
COLLECTION = 'Pyro | append this collection'


def volume(index, rng, root):
    mat = bpy.data.materials.new(f'Airburst {index:02} | incandescent porous gas'); mat.use_nodes = True
    tree = mat.node_tree; tree.nodes.clear(); link = tree.links.new
    output = node(tree, 'ShaderNodeOutputMaterial', 'Transparent volume output')
    shader = node(tree, 'ShaderNodeVolumePrincipled', 'Airborne incandescent gas')
    shader.inputs['Color'].default_value = (.12, .14, .17, 1)
    shader.inputs['Density Attribute'].default_value = ''
    shader.inputs['Temperature Attribute'].default_value = ''
    link(shader.outputs['Volume'], output.inputs['Volume'])
    coord = node(tree, 'ShaderNodeTexCoord', 'Stable local coordinates')
    centre = node(tree, 'ShaderNodeVectorMath', 'Centred gas'); centre.operation = 'SUBTRACT'
    centre.inputs[1].default_value = (.5, .5, .5); link(coord.outputs['Generated'], centre.inputs[0])
    length = node(tree, 'ShaderNodeVectorMath', 'Gas radius'); length.operation = 'LENGTH'
    link(centre.outputs['Vector'], length.inputs[0])
    edge = node(tree, 'ShaderNodeMapRange', 'Soft volume boundary'); edge.interpolation_type = 'SMOOTHERSTEP'
    for name, value in [('From Min', .08), ('From Max', .47), ('To Min', 1), ('To Max', 0)]:
        edge.inputs[name].default_value = value
    link(length.outputs['Value'], edge.inputs['Value'])
    noise = node(tree, 'ShaderNodeTexNoise', 'Evolving fragmentation'); noise.noise_dimensions = '4D'
    noise.inputs['Scale'].default_value = rng.uniform(4.5, 6.5); noise.inputs['Detail'].default_value = 4
    noise.inputs['Roughness'].default_value = .75; noise.inputs['Distortion'].default_value = .7
    link(coord.outputs['Generated'], noise.inputs['Vector'])
    start = rng.uniform(0, 40); key(noise.inputs['W'], [(1, start), (40, start + 1.4)])
    porous = node(tree, 'ShaderNodeMapRange', 'Fragmented density')
    for name, value in [('From Min', .46), ('From Max', .65), ('To Min', 0), ('To Max', 12)]:
        porous.inputs[name].default_value = value
    link(noise.outputs['Fac'], porous.inputs['Value'])
    mask = node(tree, 'ShaderNodeMath', 'Soft porous gas'); mask.operation = 'MULTIPLY'
    link(porous.outputs[0], mask.inputs[0]); link(edge.outputs[0], mask.inputs[1])
    envelope = node(tree, 'ShaderNodeMath', 'Gas envelope'); envelope.operation = 'MULTIPLY'
    link(mask.outputs[0], envelope.inputs[0])
    key(envelope.inputs[1], [(1, 0), (3, .75), (9, 1), (16, .65), (24, .18), (32, .025), (40, 0)])
    density = node(tree, 'ShaderNodeMath', 'Root density control'); density.operation = 'MULTIPLY'
    link(envelope.outputs[0], density.inputs[0]); control(density.inputs[1], root, 'density')
    link(density.outputs[0], shader.inputs['Density'])
    ramp = node(tree, 'ShaderNodeValToRGB', 'Warm fragmented lobes')
    ramp.color_ramp.elements[0].position = .35; ramp.color_ramp.elements[0].color = (.4, .012, .001, 1)
    ramp.color_ramp.elements[1].position = .68; ramp.color_ramp.elements[1].color = (1, .86, .46, 1)
    ramp.color_ramp.elements.new(.54).color = (1, .21, .008, 1)
    link(noise.outputs['Fac'], ramp.inputs['Fac'])
    colour = node(tree, 'ShaderNodeMixRGB', 'White cyan flash cooling into warm fragments')
    link(ramp.outputs['Color'], colour.inputs[1]); colour.inputs[2].default_value = (.62, .88, 1, 1)
    key(colour.inputs[0], [(1, 1), (7, .9), (15, .8), (20, .12), (25, 0), (40, 0)])
    link(colour.outputs[0], shader.inputs['Emission Color'])
    glow = node(tree, 'ShaderNodeMath', 'Flame envelope'); glow.operation = 'MULTIPLY'
    link(envelope.outputs[0], glow.inputs[0])
    key(glow.inputs[1], [(1, 0), (3, 10), (8, 8), (15, 4), (22, 2), (29, .3), (34, 0), (40, 0)])
    controlled = node(tree, 'ShaderNodeMath', 'Root fire control'); controlled.operation = 'MULTIPLY'
    link(glow.outputs[0], controlled.inputs[0]); control(controlled.inputs[1], root, 'fire_intensity')
    link(controlled.outputs[0], shader.inputs['Emission Strength'])
    return mat


def shell(root):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1)
    obj = bpy.context.object; obj.name = 'Expanding fragmented spherical shell'; obj.parent = root
    for polygon in obj.data.polygons: polygon.use_smooth = True
    turbulence = bpy.data.textures.new('Spatial shell turbulence', type='CLOUDS')
    turbulence.noise_scale = .3; turbulence.noise_depth = 2
    displacement = obj.modifiers.new('Irregular spherical wavefront', 'DISPLACE')
    displacement.texture = turbulence; displacement.strength = .06; displacement.mid_level = .5
    mat = bpy.data.materials.new('Thin shock-shell interpretation / transparent gaps'); mat.use_nodes = True
    tree = mat.node_tree; tree.nodes.clear(); link = tree.links.new
    output = node(tree, 'ShaderNodeOutputMaterial', 'Shell output')
    transparent = node(tree, 'ShaderNodeBsdfTransparent', 'Open air')
    emission = node(tree, 'ShaderNodeEmission', 'Luminous shell edge')
    emission.inputs['Color'].default_value = (1, .61, .2, 1); emission.inputs['Strength'].default_value = 2
    fresnel = node(tree, 'ShaderNodeFresnel', 'Thin rim in any view'); fresnel.inputs['IOR'].default_value = 1.035
    coordinates = node(tree, 'ShaderNodeTexCoord', 'Shell coordinates')
    noise = node(tree, 'ShaderNodeTexNoise', 'Broken perimeter'); noise.inputs['Scale'].default_value = 14
    noise.inputs['Detail'].default_value = 3; link(coordinates.outputs['Generated'], noise.inputs['Vector'])
    gaps = node(tree, 'ShaderNodeMapRange', 'Perimeter gaps')
    gaps.inputs['From Min'].default_value = .37; gaps.inputs['From Max'].default_value = .6
    link(noise.outputs['Fac'], gaps.inputs['Value'])
    rim = node(tree, 'ShaderNodeMath', 'Fragmented rim'); rim.operation = 'MULTIPLY'
    link(fresnel.outputs[0], rim.inputs[0]); link(gaps.outputs[0], rim.inputs[1])
    envelope = node(tree, 'ShaderNodeMath', 'Shell envelope'); envelope.operation = 'MULTIPLY'
    link(rim.outputs[0], envelope.inputs[0])
    key(envelope.inputs[1], [(1, 0), (9, 0), (15, .5), (22, .85), (30, .6), (36, .18), (40, 0)])
    opacity = node(tree, 'ShaderNodeMath', 'Root shell opacity'); opacity.operation = 'MULTIPLY'
    link(envelope.outputs[0], opacity.inputs[0]); control(opacity.inputs[1], root, 'shell_opacity')
    mix = node(tree, 'ShaderNodeMixShader', 'Transparent shell')
    link(opacity.outputs[0], mix.inputs[0]); link(transparent.outputs[0], mix.inputs[1])
    link(emission.outputs[0], mix.inputs[2]); link(mix.outputs[0], output.inputs['Surface'])
    obj.data.materials.append(mat)
    for frame, radius in [(1, .01), (8, .6), (15, 1.5), (22, 2.6), (30, 3.7), (40, 4.6)]:
        obj.scale = (radius,) * 3; obj.keyframe_insert('scale', frame=frame)
    return obj


def build(seed):
    rng = random.Random(seed)
    root = bpy.data.objects.new('AirburstRoot | transform complete spatial effect', None)
    bpy.context.collection.objects.link(root)
    for name, value in [('density', 2.5), ('fire_intensity', 1.0), ('shell_opacity', 1.0)]:
        root[name] = value; root.id_properties_ui(name).update(min=0, max=8)
    root['seed'] = seed; root['variant'] = 'airborne'; root['lifetime_seconds'] = 40 / 30
    root['reference'] = '_P/XS01.256; inferred 3D depth and spherical shell'
    for index in range(9):
        direction = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))).normalized()
        target = direction * (rng.uniform(.6, 1.4) if index else 0)
        radius = 1.05 if index == 0 else rng.uniform(.65, .95)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
        obj = bpy.context.object; obj.name = f'Airborne gas lobe {index:02}'; obj.parent = root
        obj.data.materials.append(volume(index, rng, root))
        for frame, expansion, drift in [(1, .01, 0), (4, .35, .2), (10, .8, .7),
                                         (18, 1.1, 1), (28, 1.3, 1.45), (40, 1.5, 1.9)]:
            obj.location = target * drift
            obj.scale = (radius * expansion,) * 3
            obj.rotation_euler = (index + frame * .015, index * .3, frame * .02)
            for prop in ['location', 'scale', 'rotation_euler']: obj.keyframe_insert(prop, frame=frame)
    shell(root)
    spark_mat = bpy.data.materials.new('Airborne incandescent particles'); spark_mat.use_nodes = True
    shader = spark_mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Emission Color'].default_value = (1, .43, .035, 1)
    shader.inputs['Emission Strength'].default_value = 7
    for index in range(40):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
        obj = bpy.context.object; obj.name = f'Radial spark {index:02}'; obj.parent = root
        obj.data.materials.append(spark_mat)
        direction = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))).normalized()
        speed = rng.uniform(2, 4); size = rng.uniform(.009, .023)
        for frame, visibility in [(1, 0), (4, 1), (14, 1), (24, .6), (32, .1), (40, 0)]:
            obj.location = direction * speed * ((frame - 1) / 30)
            obj.scale = (size * visibility,) * 3
            obj.keyframe_insert('location', frame=frame); obj.keyframe_insert('scale', frame=frame)
    bpy.context.collection.asset_mark()
    bpy.context.collection.asset_data.description = 'XS01-inspired spatial airburst; flash, fragments, radial sparks and dissolving shell'
    return root


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--preview', action='store_true')
    parser.add_argument('--seed', type=int, default=137); parser.add_argument('--output', type=Path, default=ROOT)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    args.output.mkdir(parents=True, exist_ok=True)
    scene = setup(False); scene.frame_end = 40; scene.render.fps = 30
    build(args.seed)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection']
    bpy.ops.object.camera_add(location=(8, -14, 7))
    camera = bpy.context.object; camera.name = 'Airburst camera'
    camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'; camera.data.ortho_scale = 10.3; scene.camera = camera
    for position in [(-4, -4, 6), (3, 4, 4)]:
        bpy.ops.object.light_add(type='AREA', location=position)
        light = bpy.context.object; light.data.energy = 1200; light.data.size = 6
        light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.frame_set(15); bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output / 'explosion.blend'))
    directory = args.output / ('preview' if args.preview else 'frames'); directory.mkdir(exist_ok=True)
    for frame in ([4, 10, 16, 23, 30, 37] if args.preview else range(1, 41)):
        scene.frame_set(frame); scene.render.filepath = str(directory / f'{frame:03}.png')
        bpy.ops.render.render(write_still=True)
    metadata = dict(issue=1035, variant='airborne', seed=args.seed, frames=40, fps=30, resolution=[300, 300],
                    blender=bpy.app.version_string, source_reference='_P/XS01.256',
                    technique='Procedural 3D gas volumes, transparent spherical shell and radial sparks',
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    shell_interpretation='Authored spatial interpretation of the observed thin perimeter',
                    external_dependencies=False, append_collection=COLLECTION)
    (args.output / 'model.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print('AIRBURST_OK', flush=True)


if __name__ == '__main__': main()
