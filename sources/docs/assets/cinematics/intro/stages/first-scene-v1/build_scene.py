"""Editable reconstruction of the INTRO.GDV opening, based on frames 0..95."""
import argparse
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--out', default=str(Path(__file__).resolve().parent))
parser.add_argument('--preview', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT = Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)
random.seed(28)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.cycles.transparent_max_bounces = 32
scene.render.resolution_x = 960
scene.render.resolution_y = 840
scene.render.resolution_percentage = 100
scene.render.fps = 12
scene.frame_start = 1
scene.frame_end = 96
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.world = bpy.data.worlds.new('Deep space')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.0006, 0.0008, 0.0015, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.12


def collection(name):
    group = bpy.data.collections.new(name)
    scene.collection.children.link(group)
    return group


SHIP = collection('01 — Reconstructed ship / editable geometry')
SKY = collection('02 — Eclipse and procedural corona')
STARS = collection('03 — Stars and nebula')
RIG = collection('04 — Camera, animation and lights')


def move(obj, group):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    group.objects.link(obj)
    return obj


def empty(name, group):
    obj = bpy.data.objects.new(name, None)
    group.objects.link(obj)
    return obj


camera = bpy.data.objects.new('Camera — 8 second opening', bpy.data.cameras.new('Opening lens 45mm'))
RIG.objects.link(camera)
camera.location = (8, -15, 9)
camera.rotation_euler = (Vector((0, 1, 2)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.lens = 45
camera.data.clip_end = 250
scene.camera = camera
bpy.context.view_layer.update()
ship = empty('SHIP — twin-engine silhouette and trajectory', SHIP)
eclipse = empty('ECLIPSE — camera-space composition', SKY)
eclipse.parent = camera


def fade(value, keys):
    for frame, amount in keys:
        value.default_value = amount
        value.keyframe_insert('default_value', frame=frame)


def material(name, base, metal=0.0, worn=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*base, 1)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*base, 1)
    shader.inputs['Metallic'].default_value = metal
    shader.inputs['Roughness'].default_value = 0.48
    if worn:
        tex = nodes.new('ShaderNodeTexNoise')
        tex.name = 'Oxidation, ingrained grime and paint mottling'
        tex.inputs['Scale'].default_value = 11
        tex.inputs['Detail'].default_value = 4
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.23
        ramp.color_ramp.elements[0].color = (*(x * 0.22 for x in base), 1)
        ramp.color_ramp.elements[1].position = 0.78
        ramp.color_ramp.elements[1].color = (*(min(1, x * 1.5) for x in base), 1)
        links.new(tex.outputs['Fac'], ramp.inputs[0])
        links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
        coord = nodes.new('ShaderNodeTexCoord')
        stretch = nodes.new('ShaderNodeVectorMath')
        stretch.operation = 'MULTIPLY'
        stretch.inputs[1].default_value = (5, 100, 9)
        fine = nodes.new('ShaderNodeTexNoise')
        fine.inputs['Scale'].default_value = 4
        fine.inputs['Detail'].default_value = 2
        bump = nodes.new('ShaderNodeBump')
        bump.name = 'Small scratches and material wear'
        bump.inputs['Strength'].default_value = 0.22
        bump.inputs['Distance'].default_value = 0.018
        links.new(coord.outputs['Generated'], stretch.inputs[0])
        links.new(stretch.outputs[0], fine.inputs[0])
        links.new(fine.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs[0], shader.inputs['Normal'])
    return mat


olive = material('Olive paint — worn, mottled and scratched', (0.16, 0.205, 0.084), 0.55, True)
dark = material('Recesses — soot and blackened steel', (0.018, 0.025, 0.022), 0.5, True)
steel = material('Exposed edges — worn titanium', (0.25, 0.29, 0.27), 0.75, True)
light_olive = material('Wing plating — faded olive', (0.14, 0.19, 0.07), 0.4, True)
ochre = material('Old identification paint — ochre', (0.38, 0.25, 0.055), 0.2, True)
glass = material('Recessed cockpit glazing', (0.008, 0.04, 0.055), 0.65)
glass.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.17


def emissive(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs[0].default_value = (*color, 1)
    emission.inputs[1].default_value = strength
    mat.node_tree.links.new(emission.outputs[0], out.inputs['Surface'])
    return mat


engine_blue = emissive('Thruster throat — ion blue', (0.015, 0.32, 1), 5)


def mesh(name, vertices, faces, mat, group=SHIP, parent=ship, bevel=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    obj.parent = parent
    if bevel:
        modifier = obj.modifiers.new('Small worn edge highlights', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 2
    return obj


def box(name, location, scale, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = move(bpy.context.object, SHIP)
    obj.name = name
    obj.parent = ship
    obj.location = location
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj


def plate(name, outline, z, thickness, mat):
    n = len(outline)
    vertices = [(x, y, z - thickness / 2) for x, y in outline] + [(x, y, z + thickness / 2) for x, y in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return mesh(name, vertices, faces, mat, bevel=0.025)


def pod(name, x, profile, mat, sides=12):
    vertices = [(x + radius * math.cos(a * 2 * math.pi / sides), y,
                 radius * math.sin(a * 2 * math.pi / sides))
                for y, radius in profile for a in range(sides)]
    faces = []
    for section in range(len(profile) - 1):
        for a in range(sides):
            b = (a + 1) % sides
            faces.append((section * sides + a, section * sides + b,
                          (section + 1) * sides + b, (section + 1) * sides + a))
    return mesh(name, vertices, faces, mat)


plate('Central hull — tapered structural spine', [(-0.82, -1.85), (0.82, -1.85), (0.62, 2.3), (0, 3.85), (-0.62, 2.3)], 0.08, 0.62, olive)
box('Engine mounting crossbeam', (0, -0.7, -0.12), (3.5, 0.55, 0.35), dark)
for side in (-1, 1):
    x = side * 1.35
    tag = 'PORT' if side < 0 else 'STARBOARD'
    outline = [(side * 0.7, -1.9), (side * 3.9, -2.7), (side * 2.8, 0.65), (side * 0.7, 2.9)]
    plate(tag + ' — swept planar wing', outline, -0.18, 0.11, light_olive)
    pod(tag + ' — long faceted engine gondola', x,
        [(-2.75, 0.72), (-2.46, 0.76), (-1.75, 0.61), (0.9, 0.54), (2.6, 0.25), (3.3, 0.02)], olive)
    pod(tag + ' — nozzle dark inner cavity', x, [(-2.79, 0.62), (-2.3, 0.38)], dark)
    for index, (radius, y, mat) in enumerate([(0.67, -2.78, steel), (0.48, -2.64, engine_blue)]):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.045, major_segments=32, minor_segments=8)
        obj = move(bpy.context.object, SHIP)
        obj.name = f'{tag} — nozzle ring {index}'
        obj.parent = ship
        obj.location = (x, y, 0)
        obj.rotation_euler = (math.pi / 2, 0, 0)
        obj.data.materials.append(mat)
    # The long, pointed dorsal blades are the principal source-frame silhouette cue.
    profile = [(-1.85, 0.48), (-0.35, 1.62), (3.65, 2.02), (1.92, 1.17), (0.15, 0.48)]
    profile = [(y, 0.48 + (z - 0.48) * 0.65) for y, z in profile]
    verts = [(x + offset, y, z) for offset in (-0.10, 0.10) for y, z in profile]
    faces = [tuple(reversed(range(5))), tuple(range(5, 10))] + [(i, (i+1)%5, (i+1)%5+5, i+5) for i in range(5)]
    mesh(tag + ' — raised swept dorsal blade', verts, faces, steel, bevel=0.02)
    inset = [(x + side * 0.103, -0.05, 1.43), (x + side * 0.103, 3.15, 1.88),
             (x + side * 0.103, 1.83, 1.25), (x + side * 0.103, 0.2, 0.62)]
    inset = [(px, py, 0.48 + (pz - 0.48) * 0.65) for px, py, pz in inset]
    mesh(tag + ' — olive blade inset', inset, [(0, 1, 2, 3)], olive)
    for i in range(8):
        y = -1.8 + i * 0.49
        box(f'{tag} — gondola longitudinal panel {i:02d}', (x + side * 0.48, y, 0.28), (0.16, 0.34, 0.09), dark, 0.012)
        box(f'{tag} — abraded panel edge {i:02d}', (x + side * 0.49, y, 0.34), (0.18, 0.025, 0.025), steel, 0.006)
    for i in range(6):
        y = -1.65 + i * 0.6
        seam = box(f'{tag} — wing panel seam {i:02d}', (side * (2.3 - i * 0.12), y, -0.107), (1.5 - i * 0.09, 0.018, 0.009), dark, 0)
        seam.rotation_euler.z = side * 0.2
    for i in range(9):
        y = -1.7 + i * 0.4
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.033)
        obj = move(bpy.context.object, SHIP)
        obj.name = f'{tag} — exposed fastener {i:02d}'
        obj.parent = ship
        obj.location = (side * 2.14, y, -0.085)
        obj.data.materials.append(steel)

plate('Recessed dorsal service deck', [(-0.62, -0.6), (0.62, -0.6), (0.44, 1.65), (-0.44, 1.65)], 0.43, 0.13, dark)
for i in range(7):
    box(f'Central radiator slat {i:02d}', (0, -0.36 + i * 0.22, 0.53), (0.9, 0.075, 0.055), steel, 0.008)
plate('Faceted cockpit housing', [(-0.48, 1.15), (0.48, 1.15), (0.35, 2.3), (0, 2.85), (-0.35, 2.3)], 0.57, 0.28, olive)
plate('Smoked cockpit glazing', [(-0.35, 1.55), (0.35, 1.55), (0.25, 2.22), (0, 2.57), (-0.25, 2.22)], 0.728, 0.014, glass)
for side in (-1, 1):
    box('Faded ochre service stripe', (side * 0.55, 0.2, 0.45), (0.11, 0.74, 0.012), ochre, 0.003)


def transparent_emission(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs[0].default_value = (*color, 1)
    emission.inputs[1].default_value = strength
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader')
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs[0])
    mat.surface_render_method = 'DITHERED'
    return mat, nodes, links, mix


for side in (-1, 1):
    for layer, radius, length, color, opacity in [
        (0, 0.38, 3.1, (0.16, 0.055, 0.8), 0.13),
        (1, 0.27, 2.4, (0.015, 0.48, 1), 0.18),
        (2, 0.12, 1.7, (0.45, 0.7, 1), 0.25),
    ]:
        mat, nodes, links, mix = transparent_emission(f'Ion plume {side} layer {layer}', color, 2)
        coords = nodes.new('ShaderNodeTexCoord')
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 9
        noise.inputs['Detail'].default_value = 3
        links.new(coords.outputs['Generated'], noise.inputs[0])
        separate = nodes.new('ShaderNodeSeparateXYZ')
        links.new(coords.outputs['Generated'], separate.inputs[0])
        product = nodes.new('ShaderNodeMath')
        product.operation = 'MULTIPLY'
        links.new(noise.outputs['Fac'], product.inputs[0])
        links.new(separate.outputs['Y'], product.inputs[1])
        amount = nodes.new('ShaderNodeMath')
        amount.operation = 'MULTIPLY'
        amount.inputs[1].default_value = opacity * 1.5
        links.new(product.outputs[0], amount.inputs[0])
        links.new(amount.outputs[0], mix.inputs[0])
        obj = pod(f'Ion exhaust {side} layer {layer}', side * 1.35,
                  [(-2.81, radius), (-3.2, radius * 1.1), (-3.2-length*0.35, radius*0.8),
                   (-2.81-length, 0.005)], mat, 32)
        for frame in range(1, 98, 8):
            obj.scale.y = 1 + 0.025 * math.sin(frame * 1.2 + layer)
            obj.keyframe_insert('scale', frame=frame)


def math_node(nodes, links, operation, a, b=None):
    node = nodes.new('ShaderNodeMath')
    node.operation = operation
    if hasattr(a, 'node'):
        links.new(a, node.inputs[0])
    else:
        node.inputs[0].default_value = a
    if b is not None:
        if hasattr(b, 'node'):
            links.new(b, node.inputs[1])
        else:
            node.inputs[1].default_value = b
    return node.outputs[0]


def radial(nodes, links):
    uv = nodes.new('ShaderNodeTexCoord')
    subtract = nodes.new('ShaderNodeVectorMath')
    subtract.operation = 'SUBTRACT'
    subtract.inputs[1].default_value = (0.5, 0.5, 0)
    links.new(uv.outputs['UV'], subtract.inputs[0])
    length = nodes.new('ShaderNodeVectorMath')
    length.operation = 'LENGTH'
    links.new(subtract.outputs[0], length.inputs[0])
    return math_node(nodes, links, 'MULTIPLY', length.outputs['Value'], 2), subtract.outputs[0]


def card(name, mat, location, scale, group=SKY, parent=eclipse):
    obj = mesh(name, [(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)], [(0,1,2,3)], mat, group, parent)
    layer = obj.data.uv_layers.new()
    for loop, uv in zip(layer.data, [(0,0),(1,0),(1,1),(0,1)]):
        loop.uv = uv
    obj.location = location
    obj.scale = (*scale, 1)
    return obj


corona, nodes, links, mix = transparent_emission('Corona — procedural streamers and warm halo', (1, 0.22, 0.018), 5)
r, coordinate = radial(nodes, links)
ring = math_node(nodes, links, 'SUBTRACT', r, 0.52)
ring = math_node(nodes, links, 'ABSOLUTE', ring)
ring = math_node(nodes, links, 'MULTIPLY', ring, -11)
ring = math_node(nodes, links, 'EXPONENT', ring)
sep = nodes.new('ShaderNodeSeparateXYZ')
links.new(coordinate, sep.inputs[0])
angle = math_node(nodes, links, 'ARCTAN2', sep.outputs['Y'], sep.outputs['X'])
mapping = nodes.new('ShaderNodeCombineXYZ')
links.new(math_node(nodes, links, 'MULTIPLY', angle, 2), mapping.inputs['X'])
links.new(r, mapping.inputs['Y'])
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 7
noise.inputs['Detail'].default_value = 3
links.new(mapping.outputs[0], noise.inputs[0])
variation = math_node(nodes, links, 'ADD', math_node(nodes, links, 'MULTIPLY', noise.outputs['Fac'], 0.75), 0.25)
visibility = nodes.new('ShaderNodeValue')
visibility.name = 'Eclipse dissolve / source frames 72—84'
fade(visibility.outputs[0], [(1,1), (61,1), (73,0.65), (85,0), (96,0)])
edge = math_node(nodes, links, 'MINIMUM', math_node(nodes, links, 'MAXIMUM',
    math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'SUBTRACT', 0.96, r), 10), 0), 1)
links.new(math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'MULTIPLY',
    math_node(nodes, links, 'MULTIPLY', ring, variation), edge), visibility.outputs[0]), mix.inputs[0])
card('Solar corona / procedural radiation', corona, (-1.3, 3.0, -27), (4.7, 7.1))

sun, nodes, links, mix = transparent_emission('Solar photosphere — pale gold', (1, 0.4, 0.015), 5)
fade(mix.inputs[0], [(1,1), (61,1), (73,0.65), (85,0), (96,0)])
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32)
obj = move(bpy.context.object, SKY)
obj.name = 'SUN — elongated source-frame projection'
obj.parent = eclipse
obj.location = (-1.3, 3, -27)
obj.scale = (1.85, 3.95, 1.1)
obj.data.materials.append(sun)
for face in obj.data.polygons:
    face.use_smooth = True

moon = material('Occulting body — dark cratered basalt', (0.0008, 0.0006, 0.0005), 0.0, True)
nodes, links = moon.node_tree.nodes, moon.node_tree.links
shader = nodes.get('Principled BSDF')
shader.inputs['Roughness'].default_value = 0.95
shader.inputs['Specular IOR Level'].default_value = 0.08
output = nodes.get('Material Output')
mix = nodes.new('ShaderNodeMixShader')
transparent = nodes.new('ShaderNodeBsdfTransparent')
links.new(transparent.outputs[0], mix.inputs[1])
links.new(shader.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], output.inputs[0])
fade(mix.inputs[0], [(1,1), (85,1), (96,0)])
moon.surface_render_method = 'DITHERED'
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=64)
obj = move(bpy.context.object, SKY)
obj.name = 'OCCULTING BODY — source-shaped silhouette'
obj.parent = eclipse
obj.scale = (1.95, 3.65, 1.4)
obj.data.materials.append(moon)
for face in obj.data.polygons:
    face.use_smooth = True
for frame, x in [(1,-1.155), (37,-3.0), (73,-6.8), (97,-8.5)]:
    obj.location = (x,3.0,-24)
    obj.keyframe_insert('location',frame=frame)

# Background geometry is in camera space to make shot composition easy to edit.
star_mats = [emissive('Star temperature ' + str(i), color, power) for i, (color, power) in enumerate([
    ((0.7,0.8,1), 0.35), ((1,0.88,0.7), 0.5), ((0.8,0.9,1), 1.2), ((1,1,1), 3)])]
vertices, faces, slots = [], [], []
for i in range(800):
    x, y = random.uniform(-21,21), random.uniform(-18,18)
    radius = random.uniform(0.004,0.014) if i > 14 else random.uniform(0.03,0.045)
    z = -49
    start = len(vertices)
    vertices.extend([(x-radius,y-radius,z),(x+radius,y-radius,z),(x+radius,y+radius,z),(x-radius,y+radius,z)])
    faces.append((start,start+1,start+2,start+3))
    slots.append(3 if i < 14 else random.randrange(3))
    if i < 9:
        for sx, sy in [(radius*5, radius*0.17),(radius*0.17,radius*5)]:
            start = len(vertices)
            vertices.extend([(x-sx,y-sy,z),(x+sx,y-sy,z),(x+sx,y+sy,z),(x-sx,y+sy,z)])
            faces.append((start,start+1,start+2,start+3));slots.append(2)
stars = mesh('Star field — fixed seed 28', vertices, faces, None, STARS, camera)
for mat in star_mats:
    stars.data.materials.append(mat)
for face, slot in zip(stars.data.polygons, slots):
    face.material_index = slot

nebula, nodes, links, mix = transparent_emission('Nebula — violet-blue procedural cloud', (0.09,0.12,0.32), 1.1)
uv = nodes.new('ShaderNodeTexCoord')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 4
noise.inputs['Detail'].default_value = 6
noise.inputs['Roughness'].default_value = 0.7
links.new(uv.outputs['UV'], noise.inputs[0])
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.4
ramp.color_ramp.elements[0].color = (0,0,0,1)
ramp.color_ramp.elements[1].position = 0.7
ramp.color_ramp.elements[1].color = (0.8,0.8,0.8,1)
links.new(noise.outputs['Fac'], ramp.inputs[0])
visibility = nodes.new('ShaderNodeValue')
fade(visibility.outputs[0], [(1,0), (69,0), (85,0.28), (96,0.32)])
radius, _ = radial(nodes, links)
soft_edge = math_node(nodes, links, 'MAXIMUM', math_node(nodes, links, 'SUBTRACT', 1, radius), 0)
links.new(math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'MULTIPLY',
    ramp.outputs['Color'], soft_edge), visibility.outputs[0]), mix.inputs[0])
card('Following shot — nebula transition layer', nebula, (-5,2,-43), (9,16), STARS, camera)

for i, (center, scale, color, amount) in enumerate([
    ((1.05,-0.8,-10),(2.3,3.4),(0.025,0.18,0.55),0.09),
    ((0.05,0.2,-9),(0.55,0.8),(0.6,0.38,0.035),0.025),
]):
    mat, nodes, links, mix = transparent_emission(f'Lens ghost {i} — controllable optical ring', color, 1.2)
    r, _ = radial(nodes, links)
    ring = math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'SUBTRACT', r, 0.82), 7)
    ring = math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'MULTIPLY', ring, ring), -1)
    ring = math_node(nodes, links, 'EXPONENT', ring)
    strength = nodes.new('ShaderNodeValue')
    fade(strength.outputs[0], [(1,0), (25,amount*0.2), (61,amount), (73,amount*0.6), (85,0), (96,0)])
    links.new(math_node(nodes, links, 'MULTIPLY', ring, strength.outputs[0]), mix.inputs[0])
    card(f'Lens reflection {i}', mat, center, scale, RIG, camera)


def area(name, location, target, energy, color, size):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.color = color
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    RIG.objects.link(obj)
    obj.parent = camera
    obj.location = location
    obj.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z','Y').to_euler()
    return obj


area('Warm solar rim on occulting body', (1.5,4,-26), (-1.7,3,-24), 1800, (1,0.6,0.28), 2)
area('Ship — broad cool readability fill', (-5,6,-3), (0,-3,-13), 1600, (0.68,0.8,1), 8)
area('Ship — warm aft edge', (-2,6,-20), (0,-3,-13), 2100, (1,0.76,0.43), 7)
area('Ship — subtle starboard bounce', (7,-3,-7), (0,-3,-13), 450, (0.2,0.38,0.65), 6)

for frame, position, angle in [
    (1,(-3.3,-4.1,-10.5),-22), (25,(-0.7,-4.1,-12.0),-18),
    (49,(2.6,-5.1,-17.0),-14), (73,(5.9,-6.7,-23.5),-11),
    (97,(8.5,-8.3,-30),-8),
]:
    adjusted = Vector(position)
    adjusted.y += -position[2] * 0.085
    ship.location = camera.matrix_world @ adjusted
    ship.scale = (0.78, 0.78, 0.78)
    ship.rotation_euler = (math.radians(-2), math.radians(5), math.radians(angle))
    ship.keyframe_insert('location', frame=frame)
    ship.keyframe_insert('rotation_euler', frame=frame)
for frame, x, y in [(1,0,0),(37,-0.3,0.1),(73,-1.35,0.45),(97,-1.8,0.6)]:
    eclipse.location = (x,y,0)
    eclipse.keyframe_insert('location', frame=frame)

# One restrained bloom pass; the large colored flare rings are editable geometry.
scene.use_nodes = True
nodes, links = scene.node_tree.nodes, scene.node_tree.links
nodes.clear()
render = nodes.new('CompositorNodeRLayers')
glow = nodes.new('CompositorNodeGlare')
glow.glare_type = 'FOG_GLOW'
glow.quality = 'HIGH'
glow.threshold = 2.5
glow.size = 8
output = nodes.new('CompositorNodeComposite')
links.new(render.outputs['Image'], glow.inputs['Image'])
links.new(glow.outputs['Image'], output.inputs[0])

scene['reference'] = 'Fragile Allegiance INTRO.GDV, source frames 0..95, 320x280, 12 fps'
scene['scope'] = 'First-pass reconstruction: visible silhouette/composition inferred from supplied source frames, not recovered original 3D geometry.'
scene['timeline'] = 'Blender frame 1 = source frame 0; 96 frames at 12 fps.'
scene['materials'] = 'Procedural worn olive plating, metal edge wear, soot, scratches; no original frame projected into the render.'
scene.frame_set(37)
for screen in bpy.data.screens:
    for region in screen.areas:
        if region.type == 'VIEW_3D':
            region.spaces.active.region_3d.view_perspective = 'CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'opening-reconstruction.blend'))
(OUT/'scene-manifest.json').write_text(json.dumps({'fps':12,'frames':96,'native_resolution':[960,840],
    'ship_meshes':sum(obj.type=='MESH' for obj in SHIP.objects), 'reference_frames':[0,36,72],
    'geometry_is_inferred':True,'render_engine':'Cycles CPU'},indent=2)+'\n')
if args.preview:
    scene.render.resolution_x = 480
    scene.render.resolution_y = 420
    scene.cycles.samples = 12
    target=OUT/'layout'
    target.mkdir(exist_ok=True)
    for frame in (1,37,73):
        scene.frame_set(frame)
        scene.render.filepath=str(target/f'frame-{frame:03d}.png')
        bpy.ops.render.render(write_still=True)
print('OPENING_SCENE_BUILT',OUT)
