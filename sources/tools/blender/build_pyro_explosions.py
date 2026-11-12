"""Author reusable procedural 3D explosion variants (no external simulation cache).

Blender --background --factory-startup --python build_pyro_explosions.py --
    --variant compact --seed 17 [--preview] [--generate-only]
"""
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2] / 'docs/assets/reconstruction/effects/pyro'
VARIANTS = {'compact': 17, 'rising': 53, 'asymmetric': 91}


def key(socket, values):
    for frame, value in values:
        socket.default_value = value
        socket.keyframe_insert('default_value', frame=frame)


def node(tree, kind, name):
    result = tree.nodes.new(kind); result.name = name; result.label = name
    return result


def control(socket, root, property_name):
    driver = socket.driver_add('default_value').driver
    variable = driver.variables.new(); variable.name = 'control'
    variable.targets[0].id = root
    variable.targets[0].data_path = f'["{property_name}"]'
    driver.expression = 'control'


def volume_material(index, rng, delay, root):
    mat = bpy.data.materials.new(f'Pyro {index:02} | animated fire to smoke')
    mat.use_nodes = True
    tree = mat.node_tree; tree.nodes.clear(); link = tree.links.new
    output = node(tree, 'ShaderNodeOutputMaterial', 'Volume output / transparent surface')
    shader = node(tree, 'ShaderNodeVolumePrincipled', 'Soot scattering and incandescent gas')
    shader.inputs['Color'].default_value = (.065, .07, .08, 1)
    shader.inputs['Blackbody Intensity'].default_value = 0
    shader.inputs['Anisotropy'].default_value = .15
    shader.inputs['Temperature Attribute'].default_value = ''
    shader.inputs['Density Attribute'].default_value = ''
    link(shader.outputs['Volume'], output.inputs['Volume'])
    coordinates = node(tree, 'ShaderNodeTexCoord', 'Local volume coordinates')
    centred = node(tree, 'ShaderNodeVectorMath', 'Centred cloud'); centred.operation = 'SUBTRACT'
    centred.inputs[1].default_value = (.5, .5, .5)
    link(coordinates.outputs['Generated'], centred.inputs[0])
    radius = node(tree, 'ShaderNodeVectorMath', 'Radius'); radius.operation = 'LENGTH'
    link(centred.outputs['Vector'], radius.inputs[0])
    edge = node(tree, 'ShaderNodeMapRange', 'Soft transparent cloud boundary')
    edge.interpolation_type = 'SMOOTHERSTEP'
    edge.inputs['From Min'].default_value = .1
    edge.inputs['From Max'].default_value = .47
    edge.inputs['To Min'].default_value = 1
    edge.inputs['To Max'].default_value = 0
    link(radius.outputs['Value'], edge.inputs['Value'])
    noise = node(tree, 'ShaderNodeTexNoise', 'Evolving 4D billows'); noise.noise_dimensions = '4D'
    noise.inputs['Scale'].default_value = rng.uniform(5, 7)
    noise.inputs['Detail'].default_value = 5
    noise.inputs['Roughness'].default_value = .72
    noise.inputs['Distortion'].default_value = .4
    link(coordinates.outputs['Generated'], noise.inputs['Vector'])
    offset = rng.uniform(0, 50)
    key(noise.inputs['W'], [(1, offset), (96, offset + 1.7)])
    density = node(tree, 'ShaderNodeMapRange', 'Turbulent porous density')
    density.interpolation_type = 'SMOOTHSTEP'
    density.inputs['From Min'].default_value = .5
    density.inputs['From Max'].default_value = .65
    density.inputs['To Min'].default_value = 0
    density.inputs['To Max'].default_value = 8.0
    link(noise.outputs['Fac'], density.inputs['Value'])
    masked = node(tree, 'ShaderNodeMath', 'Billows inside soft boundary'); masked.operation = 'MULTIPLY'
    link(edge.outputs['Result'], masked.inputs[0]); link(density.outputs['Result'], masked.inputs[1])
    fade = node(tree, 'ShaderNodeMath', 'Density envelope / dissipate'); fade.operation = 'MULTIPLY'
    link(masked.outputs[0], fade.inputs[0])
    key(fade.inputs[1], [(1, 0), (3 + delay, 1.0), (18 + delay, 1), (48, .55), (72, .13), (86, .015), (96, 0)])
    controlled_density = node(tree, 'ShaderNodeMath', 'Root density control'); controlled_density.operation = 'MULTIPLY'
    link(fade.outputs[0], controlled_density.inputs[0]); control(controlled_density.inputs[1], root, 'density')
    link(controlled_density.outputs[0], shader.inputs['Density'])
    # An art-directed incandescent ramp retains orange/yellow legacy character.
    # Density masks emission too, so porous regions do not glow as opaque shells.
    flame = node(tree, 'ShaderNodeValToRGB', 'Fire palette / red orange gold hot core')
    ramp = flame.color_ramp
    ramp.elements.remove(ramp.elements[1])
    ramp.elements[0].position = .22; ramp.elements[0].color = (.1, .0008, 0, 1)
    for position, color in [(.48, (.45, .002, .0001, 1)), (.54, (1, .055, .0005, 1)),
                            (.6, (1, .4, .008, 1)), (.68, (1, .85, .3, 1))]:
        ramp.elements.new(position).color = color
    link(noise.outputs['Fac'], flame.inputs['Fac'])
    link(flame.outputs['Color'], shader.inputs['Emission Color'])
    glow = node(tree, 'ShaderNodeMath', 'Flame emission envelope'); glow.operation = 'MULTIPLY'
    link(fade.outputs[0], glow.inputs[0])
    controlled_fire = node(tree, 'ShaderNodeMath', 'Root fire intensity control'); controlled_fire.operation = 'MULTIPLY'
    link(glow.outputs[0], controlled_fire.inputs[0]); control(controlled_fire.inputs[1], root, 'fire_intensity')
    link(controlled_fire.outputs[0], shader.inputs['Emission Strength'])
    key(glow.inputs[1], [(1, 0), (4 + delay, 6), (14 + delay, 4), (28 + delay, 1.5), (42, .04), (50, 0), (96, 0)])
    # Arrange the editable shader graph by its data flow.
    for i, item in enumerate(tree.nodes):
        item.location = ((i % 5) * 240, -(i // 5) * 310)
    return mat


def animate_cloud(index, target, radius, rng, root, delay=0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
    obj = bpy.context.object; obj.name = f'Pyro cloud {index:02}'
    obj.parent = root
    obj.data.materials.append(volume_material(index, rng, delay, root))
    ratios = (rng.uniform(.8, 1.2), rng.uniform(.8, 1.2), rng.uniform(.9, 1.3))
    for frame, expansion, drift in [(1, .01, 0), (6 + delay, .5, .5), (16 + delay, 1, 1),
                                     (40, 1.25, 1), (70, 1.65, 1.3), (96, 1.9, 1.5)]:
        obj.scale = tuple(radius * expansion * value for value in ratios)
        obj.location = (target[0] * drift, target[1] * drift,
                        .2 + target[2] * drift + max(0, frame - 18) * .025)
        obj.rotation_euler = (frame * .001, frame * .003, frame * .002 + index)
        for prop in ['location', 'scale', 'rotation_euler']:
            obj.keyframe_insert(prop, frame=frame)
    return obj


def sparks(rng, root):
    mat = bpy.data.materials.new('Incandescent sparks / no solid debris'); mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.4, .025, .001, 1)
    shader.inputs['Emission Color'].default_value = (1, .12, .008, 1)
    shader.inputs['Emission Strength'].default_value = 12
    for index in range(32):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
        obj = bpy.context.object; obj.name = f'Ember {index:02}'; obj.parent = root
        obj.data.materials.append(mat)
        angle = rng.uniform(0, math.tau); speed = rng.uniform(1, 3)
        velocity = Vector((math.cos(angle) * speed, math.sin(angle) * speed, rng.uniform(.5, 3)))
        size = rng.uniform(.008, .024)
        for frame in [1, 4, 14, 28, 42, 60, 96]:
            time = (frame - 1) / 24
            obj.location = velocity * time
            obj.location.z += .35 - .75 * time * time
            obj.scale = (size,) * 3 if 4 <= frame <= 28 else ((size * .3,) * 3 if frame == 42 else (0, 0, 0))
            obj.keyframe_insert('location', frame=frame); obj.keyframe_insert('scale', frame=frame)


def build(variant, seed):
    rng = random.Random(seed)
    root = bpy.data.objects.new('ExplosionRoot | move rotate scale or append collection', None)
    bpy.context.collection.objects.link(root)
    root['seed'] = seed; root['variant'] = variant
    root['lifetime_seconds'] = 4.0
    root['density'] = 3.0; root['fire_intensity'] = 1.0
    root.id_properties_ui('density').update(min=0, max=4, description='Global volume density multiplier')
    root.id_properties_ui('fire_intensity').update(min=0, max=10, description='Global flame emission multiplier')
    root['usage'] = 'Append Pyro collection; transform this root; keyframes 1-96 at 24 fps'
    for index in range(10):
        angle = index * math.tau / 7 + rng.uniform(-.4, .4)
        if variant == 'rising':
            r = rng.uniform(.9, 1.6) if index < 7 else rng.uniform(0, .35)
            z = rng.uniform(1.6, 2.3) if index < 7 else .2 + (index - 7) * .55
            radius = rng.uniform(.9, 1.3) if index < 7 else .8
        else:
            r = rng.uniform(.9, 1.8) if index < 7 else rng.uniform(0, .4)
            z = rng.uniform(.3, 1.5)
            radius = rng.uniform(.9, 1.25)
        target = (r * math.cos(angle), r * math.sin(angle), z)
        if variant == 'asymmetric':
            target = (target[0] * 1.5 + .5, target[1] * .8, target[2] * .75)
        animate_cloud(index, target, radius, rng, root, rng.randrange(0, 5))
    sparks(rng, root)
    bpy.context.collection.asset_mark()
    bpy.context.collection.asset_data.description = f'Procedural 3D {variant} explosion; seed {seed}; fire, soot, dissipation, alpha'
    return root


def setup(preview):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    collection = bpy.data.collections.new('Pyro | append this collection')
    scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    scene.render.resolution_x = 300
    scene.render.resolution_y = 300
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    scene.render.fps = 24; scene.frame_start = 1; scene.frame_end = 96
    scene.world.color = (.15, .15, .15)
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = -1.2
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples = 128
    scene.eevee.volumetric_tile_size = '2'
    scene.eevee.volumetric_samples = 128
    scene.eevee.use_volumetric_shadows = True
    scene.eevee.volumetric_shadow_samples = 32
    return scene


def rig(scene):
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection']
    bpy.ops.object.camera_add(location=(9, -15, 8))
    camera = bpy.context.object; camera.name = 'Review camera'
    camera.rotation_euler = (Vector((0, 0, 2.8)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'; camera.data.ortho_scale = 14; scene.camera = camera
    for name, position, energy, color in [('Cool rim', (2, 4, 7), 1800, (.6, .75, 1)),
                                           ('Soft key', (-4, -4, 7), 2200, (1, .85, .7))]:
        bpy.ops.object.light_add(type='AREA', location=position)
        light = bpy.context.object; light.name = name; light.data.energy = energy
        light.data.color = color; light.data.size = 7
        light.rotation_euler = (Vector((0, 0, 2)) - light.location).to_track_quat('-Z', 'Y').to_euler()


def fit_animation(scene):
    """Keep one fixed square framing around the complete visible 3D trajectory."""
    scene.frame_set(16); bpy.context.view_layer.update()
    inverse = scene.camera.matrix_world.inverted()
    points = []
    for frame in range(4, 94, 3):
        scene.frame_set(frame); bpy.context.view_layer.update()
        for obj in bpy.data.collections['Pyro | append this collection'].objects:
            if obj.type != 'MESH' or max(obj.scale) < .001:
                continue
            points.extend(inverse @ (obj.matrix_world @ Vector(corner)) for corner in obj.bound_box)
    low_x, high_x = min(p.x for p in points), max(p.x for p in points)
    low_y, high_y = min(p.y for p in points), max(p.y for p in points)
    shift = Vector(((low_x + high_x) / 2, (low_y + high_y) / 2, 0))
    scene.camera.location += scene.camera.rotation_euler.to_quaternion() @ shift
    scene.camera.data.ortho_scale = max(high_x - low_x, high_y - low_y) * 1.08


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=VARIANTS, default='compact')
    parser.add_argument('--seed', type=int)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--generate-only', action='store_true')
    parser.add_argument('--output', type=Path, help='Alternate variant directory; preserves standard deliverables')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    seed = args.seed if args.seed is not None else VARIANTS[args.variant]
    output = args.output or ROOT / args.variant; output.mkdir(parents=True, exist_ok=True)
    scene = setup(args.preview); build(args.variant, seed); rig(scene); fit_animation(scene)
    scene.frame_set(16)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / 'explosion.blend'))
    if not args.generate_only:
        directory = output / ('preview' if args.preview else 'frames'); directory.mkdir(exist_ok=True)
        for frame in ([8, 16, 30, 48, 72, 90] if args.preview else range(1, 97)):
            scene.frame_set(frame); scene.render.filepath = str(directory / f'{frame:03}.png')
            bpy.ops.render.render(write_still=True)
    (output / 'model.json').write_text(json.dumps(dict(variant=args.variant, seed=seed, frames=96,
        fps=24, blender=bpy.app.version_string, engine=scene.render.engine, device='GPU',
        resolution=[scene.render.resolution_x, scene.render.resolution_y],
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        controls=dict(density=3.0, fire_intensity=1.0),
        colour_management=dict(view_transform='Standard', exposure=-1.2),
        technique='Animated 3D volumes with evolving 4D noise, incandescent palette, soot and dissipation',
        simulation_cache=False, external_textures=False, append_collection='Pyro | append this collection'), indent=2) + '\n')
    print('PYRO_OK', args.variant, seed, flush=True)


if __name__ == '__main__':
    main()
