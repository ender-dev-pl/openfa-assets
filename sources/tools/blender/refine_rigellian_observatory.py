"""Restore RI4C's readable equatorial equipment belt, axial fittings and fork aerial."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_crowns import fit_camera, sha
from refine_rigellian_extractor import box, cylinder, mesh
from rigellian_observatory_parts import PROFILES, SCALE_Y, radius

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'sources/docs/assets/reconstruction/ships/rigellian/observatory/model.blend'
REL = Path('docs/assets/reconstruction/rigellian-refined/observatory')
OUTPUT, MEDIA = ROOT/'sources'/REL, ROOT/'gallery/media'/REL
VIEWS = {'front-quarter': (6, -13, 5), 'front': (0, -16, 1), 'rear-quarter': (-7, 12, 5),
         'side': (16, 0, 1), 'belt-detail': (0, -16, 1), 'lower-quarter': (6, -13, -7)}
HULL = 'Observatory saucer pressure hull'
CHAMBER = 'Observatory axial green chambers'
BAYS = [-math.pi/2-1.08, -math.pi/2+1.08, math.pi/2-1.08, math.pi/2+1.08]
PLANFORM_SCALE = 1.18


def material(name, colour, metal=.6, rough=.55, light=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Metallic'].default_value = metal
    shader.inputs['Roughness'].default_value = rough
    if light:
        shader.inputs['Emission Color'].default_value = (*colour, 1)
        shader.inputs['Emission Strength'].default_value = light
    return mat


def sector(name, owner, phi0, phi1, low, high, material, lift=.035, depth=.055):
    angles = [phi0+(phi1-phi0)*i/24 for i in range(25)]
    heights = sorted(set([low, high]+[z for z, _ in PROFILES[owner] if low < z < high]))
    points = []
    for offset in [lift, lift-depth]:
        for z in heights:
            for phi in angles:
                r = radius(owner, phi, z)+offset
                points.append((r*math.cos(phi), r*math.sin(phi)*SCALE_Y[owner], z))
    width, rows = len(angles), len(heights)
    layer = width*rows
    faces = []
    for row in range(rows-1):
        for col in range(width-1):
            a = row*width+col
            faces += [(a, a+1, a+width+1, a+width),
                      (a+layer, a+width+layer, a+width+1+layer, a+1+layer)]
    edge = (list(range(width))+[i*width+width-1 for i in range(1, rows)]+
            list(range(layer-2, layer-width-1, -1))+[i*width for i in range(rows-2, 0, -1)])
    for i, a in enumerate(edge):
        b = edge[(i+1)%len(edge)]
        faces.append((a, a+layer, b+layer, b))
    obj = mesh(name, points, faces, material)
    # Existing authored materials use an explicit UV map. Keep their packed
    # wear usable on new fittings without importing any original-game pixels.
    for node in material.node_tree.nodes:
        if node.type == 'UVMAP' and node.uv_map and node.uv_map not in obj.data.uv_layers:
            layer = obj.data.uv_layers.new(name=node.uv_map)
            for a, b in zip(layer.data, obj.data.uv_layers[0].data):
                a.uv = b.uv
    return obj


def rod(name, a, b, radius, material):
    delta = Vector(b)-Vector(a)
    return cylinder(name, (Vector(a)+Vector(b))/2, radius, delta.length, material, delta)


def build():
    bronze = bpy.data.materials['Observatory | aged copper details']
    pale = material('RI4C refined | worn pale alloy frames', (.29, .31, .34), .75, .57)
    dark = material('RI4C refined | recessed equipment belt', (.016, .025, .035), .45, .69)
    blue = material('RI4C refined | blue equipment insets', (.07, .20, .48), .20, .34, .65)
    amber = material('RI4C refined | amber equipment insets', (.65, .16, .035), .20, .37, .65)
    green = material('RI4C refined | pale green equipment insets', (.38, .63, .43), .20, .38, .5)
    jade = bpy.data.materials['Observatory | worn green chambers']
    # Near-full arcs leave a small manufacturing split at the hidden rear axis;
    # each sector is a real closed body-following casting, not a painted band.
    for i, (low, high, mat, lift) in enumerate([(-.11, .11, dark, .035), (-.16, -.11, bronze, .045), (.11, .16, pale, .045)]):
        sector(f'RI4C equatorial equipment band {i}', HULL, -.999*math.pi, .999*math.pi, low, high, mat, lift, .065)
    for i, phi in enumerate(BAYS):
        tint = blue if i == 0 else amber if i == 1 else green
        for side in [-1, 1]:
            sector(f'RI4C bay {i} outer side frame {side}', HULL, phi+side*.35-.025, phi+side*.35+.025,
                   -.10, .10, bronze, .075, .07)
            z = side*.092
            sector(f'RI4C bay {i} horizontal frame {side}', HULL, phi-.35, phi+.35,
                   z-.015, z+.015, pale, .072, .07)
        for index in range(5):
            angle = phi+(index-2)*.12
            sector(f'RI4C bay {i} bright inset {index}', HULL, angle-.036, angle+.036,
                   -.043, .043, tint, .068, .045)
    for i, phi in enumerate([0, math.pi]):
        sector(f'RI4C copper terminal housing {i}', HULL, phi-.10, phi+.10, -.13, .13, bronze, .065, .08)
    for row, z in enumerate([-.030, .030]):
        for col, x in enumerate([-.115, 0, .115]):
            box(f'RI4C central pale inset {row} {col}', (x, -1.312, z), (.060, .020, .024), green, .004)
    for side, z in [(1, .96), (-1, -1.20)]:
        box(f'RI4C chamber equipment face {side}', (0, -.30, z), (.42, .18, .29), jade, .035)
        for i in range(3):
            box(f'RI4C chamber pale bar {side} {i}', (0, -.395, z+(i-1)*.065), (.235, .018, .026), green, .006)
        for phi in [-math.pi, 0]:
            sector(f'RI4C chamber copper cheek {side} {phi}', CHAMBER, phi-.18, phi+.18,
                   z-.19, z+.19, bronze, .035, .065)
    # The fixed-state source clearly shows a three-prong copper terminal.
    # Its exact section is authored, and it is not an equipment-slot transform.
    rod('RI4C fork central terminal', (0, 0, 1.96), (0, 0, 2.88), .022, bronze)
    for side in [-1, 1]:
        points = [(side*.025, 0, 2.02), (side*.12, 0, 2.20), (side*.15, 0, 2.36), (side*.15, 0, 2.67)]
        for i, (a, b) in enumerate(zip(points, points[1:])):
            rod(f'RI4C fork lateral prong {side} {i}', a, b, .025, bronze)
        rod(f'RI4C lower axial side terminal {side}', (side*.13, 0, -1.88),
            (side*.13, 0, -2.63), .018, bronze)


def selected_view(view):
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    return [o for o in meshes if o.name.startswith(('RI4C bay', 'RI4C equatorial', 'RI4C central', 'RI4C copper terminal'))] if view == 'belt-detail' else meshes


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    root = bpy.data.objects['PlacementRoot']
    removed = []
    for obj in list(scene.objects):
        if obj.name.startswith(('Observatory equatorial copper rim', 'Observatory central face marker',
                                'Observatory chamber service plate', 'Observatory chamber service slot')) or obj.name == 'Observatory axial aerial 1':
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    preserved = [o.name for o in scene.objects if o.type == 'MESH']
    modified = []
    for obj in scene.objects:
        if obj.name.startswith('Observatory pointed fin'):
            obj.rotation_euler.z += math.pi/4
            modified.append(obj.name)
    build()
    new_parts = []
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.name in preserved:
            continue
        new_parts.append(obj.name)
        obj.parent = root
        uv_names = {node.uv_map for mat in obj.data.materials for node in mat.node_tree.nodes
                    if node.type == 'UVMAP' and node.uv_map}
        if len(uv_names) == 1:
            expected = next(iter(uv_names))
            if expected not in obj.data.uv_layers:
                obj.data.uv_layers[0].name = expected
            for uv in list(obj.data.uv_layers):
                if uv.name != expected:
                    obj.data.uv_layers.remove(uv)
        for mat in obj.data.materials:
            for node in mat.node_tree.nodes:
                if node.type == 'UVMAP' and node.uv_map and node.uv_map not in obj.data.uv_layers:
                    uv = obj.data.uv_layers.new(name=node.uv_map)
                    for a, b in zip(uv.data, obj.data.uv_layers[0].data):
                        a.uv = b.uv
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new('Explicit portable tessellation', 'TRIANGULATE')
        mod.keep_custom_normals = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    planform = bpy.data.objects.new('Authored station planform fit', None)
    scene.collection.objects.link(planform)
    planform.parent = root
    planform.scale = (PLANFORM_SCALE, PLANFORM_SCALE, 1)
    for obj in list(scene.objects):
        if obj.type == 'MESH':
            original = obj.matrix_world.copy()
            obj.parent = planform
            obj.matrix_parent_inverse = Matrix.Identity(4)
            obj.matrix_basis = original
    collection = bpy.data.collections.new('Rigellian Observatory refined editable source')
    scene.collection.children.link(collection)
    for old in bpy.data.collections:
        if old.asset_data:
            old.asset_clear()
    for obj in list(scene.objects):
        if obj.type in ['MESH', 'EMPTY']:
            collection.objects.link(obj)
            for previous in list(obj.users_collection):
                if previous != collection:
                    previous.objects.unlink(obj)
    collection.asset_mark()
    collection.asset_data.description = 'RI4C refined equipment belt, axial instrumentation and fork; uncalibrated authored alignment axis'
    light = bpy.data.lights.new('Lower hemisphere preview fill', 'AREA')
    light.energy, light.shape, light.size = 250, 'DISK', 5
    lamp = bpy.data.objects.new(light.name, light)
    scene.collection.objects.link(lamp)
    lamp.location = (0, -6, -4)
    lamp.rotation_euler = (-lamp.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 32
    fit_camera(VIEWS['front-quarter'], selected_view('front-quarter'))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH', 'EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'), export_format='GLB', use_selection=True,
                             export_apply=True, export_extras=True, export_animations=False)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    for view, direction in VIEWS.items():
        fit_camera(direction, selected_view(view))
        scene.render.filepath = str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    meta = dict(issue=185, id='openfa:ship/rigellian/observatory', culture='rigellian', name='Observatory',
                stage='structural-detail-refinement', source_study=SOURCE.relative_to(ROOT).as_posix(),
                source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                generator_sha256=sha(Path(__file__)), removed_objects=removed, added_objects=new_parts,
                preserved_objects=[name for name in preserved if name not in modified], modified_objects=modified,
                planform_scale=PLANFORM_SCALE,
                views=list(VIEWS), blender=bpy.app.version_string,
                lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
                dependencies_sha256={name: sha(Path(__file__).with_name(name)) for name in
                                     ['refine_rigellian_crowns.py', 'refine_rigellian_extractor.py', 'rigellian_observatory_parts.py']},
                observed=['Substantial equatorial equipment belt with blue/amber side regions and pale central features',
                          'Upper fork terminal and distinct equipment on green axial chambers'],
                inferred=['Exact bay sections, emitted brightness and rear repeated equipment',
                          'Diagonal fin orientation keeps the front chamber faces visible; exact radial arrangement remains inferred',
                          '1.18 radial planform fit improves the 94x126 fixed-state frontal aspect; actual legacy camera and hidden depth remain unresolved',
                          'Material identity and instrument functions; no calibrated mount transforms'],
                state_policy='Second fixed wireframe-like state remains unresolved; no deployment or process loop invented',
                acceptance='Refined static visible-equipment study; final artistic acceptance and gameplay calibration open')
    (OUTPUT/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('RI4C_OBSERVATORY_VISIBLE_EQUIPMENT_REFINED', len(preserved), len(new_parts), flush=True)


if __name__ == '__main__':
    main()
