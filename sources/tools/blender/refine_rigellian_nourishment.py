"""RI03: restore the broad pale equipment face without distorting the established stack."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_crowns import fit_camera, sha
from refine_rigellian_extractor import box, mesh
from rigellian_nourishment_parts import MODULE_STARTS, module_profile, radius, vessel

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'sources/docs/assets/reconstruction/buildings/rigellian/nourishment-bank/model.blend'
REL = Path('docs/assets/reconstruction/rigellian-refined/ri03')
OUTPUT, MEDIA = ROOT/'sources'/REL, ROOT/'gallery/media'/REL
VIEWS = {'front-quarter': (6, -13, 8), 'front': (0, -16, 4), 'side': (16, 0, 4),
         'rear-quarter': (-7, 12, 7), 'service-detail': (3, -15, 3)}


def frame_outline(width, height, r):
    points = []
    for cx, cz, base in [(width/2-r, height/2-r, 0), (-width/2+r, height/2-r, math.pi/2),
                         (-width/2+r, -height/2+r, math.pi), (width/2-r, -height/2+r, 3*math.pi/2)]:
        for i in range(7):
            phi = base+math.pi/2*i/6
            points.append((.08+cx+r*math.cos(phi), .45+cz+r*math.sin(phi)))
    # Sample straight spans as well as rounded corners: a straight chord
    # through the curved casing can otherwise hide the middle of the rim.
    sampled = []
    for i, point in enumerate(points):
        other = points[(i+1)%len(points)]
        for step in range(6):
            t = step/6
            sampled.append((point[0]*(1-t)+other[0]*t, point[1]*(1-t)+other[1]*t))
    return sampled


def fitted_frame(index, start, material):
    outer, inner = frame_outline(.40, .68, .08), frame_outline(.22, .49, .055)
    points = []
    rows = 5
    for offset in [-.032, .022]:
        for row in range(rows):
            t = row/(rows-1)
            outline = [(a[0]*(1-t)+b[0]*t, a[1]*(1-t)+b[1]*t) for a, b in zip(outer, inner)]
            for x, z in outline:
                r = radius(module_profile(start), start+z)
                points.append((x, -math.sqrt(max(.001, r*r-x*x))+offset, start+z))
    count = len(outer)
    layer = rows*count
    faces = []
    for row in range(rows-1):
        for i in range(count):
            j = (i+1)%count
            a, b = row*count+i, row*count+j
            faces += [(a, b, b+count, a+count), (a+layer, a+count+layer, b+count+layer, b+layer)]
    for i in range(count):
        j = (i+1)%count
        a, b = (rows-1)*count+i, (rows-1)*count+j
        faces += [(i, i+layer, j+layer, j), (a, b, b+layer, a+layer)]
    return mesh(f'RI03 broad pale service frame {index}', points, faces, material)


def new_vessel(index, start, materials):
    obj = vessel(f'RI03 renewed process vessel {index}', module_profile(start), {'body': materials['body']})
    cutter = box('Temporary enlarged front service recess', (.08, -.47, start+.45), (.28, .25, .58), materials['dark'], .055)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new('Readable recessed service assembly', 'BOOLEAN')
    modifier.operation = 'DIFFERENCE'
    modifier.solver = 'EXACT'
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm, dist=1e-7, edges=list(bm.edges))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.append(materials['cap'])
    while obj.data.uv_layers:
        obj.data.uv_layers.remove(obj.data.uv_layers[0])
    uv = obj.data.uv_layers.new(name='Authored surface wear')
    low, high = start, start+.90
    for face in obj.data.polygons:
        coords = [obj.data.vertices[obj.data.loops[i].vertex_index].co for i in face.loop_indices]
        cap = next((z for z in [low, high] if all(abs(p.z-z) < 1e-6 for p in coords)), None)
        face.material_index = 1 if cap is not None else 0
        values = [(math.atan2(p.y, p.x)+math.pi)/math.tau for p in coords]
        wraps = max(values)-min(values) > .5
        for loop, p, u in zip(face.loop_indices, coords, values):
            uv.data[loop].uv = ((.5+p.x/(2*radius(module_profile(start), cap)),
                                .5+p.y/(2*radius(module_profile(start), cap))) if cap is not None
                               else (u+1 if wraps and u < .5 else u, p.z/4.2))
    return obj


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    root = bpy.data.objects['PlacementRoot']
    materials = {key: bpy.data.materials['RI03 | '+name] for key, name in
                 [('body', 'aged jade coating'), ('edge', 'abraded pale alloy'),
                  ('dark', 'recessed service equipment'), ('cap', 'worn planar end caps')]}
    remove = ('RI03 rounded vessel', 'RI03 vessel', 'RI03 continuous rounded pocket return',
              'RI03 recessed service cooling louvre', 'RI03 continuous pale service spine', 'RI03 spine mounting standoff')
    removed = []
    for obj in list(scene.objects):
        if obj.name.startswith(remove):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    preserved = {obj.name for obj in scene.objects if obj.type == 'MESH'}
    for i, start in enumerate(MODULE_STARTS):
        new_vessel(i, start, materials)
        fitted_frame(i, start, materials['edge'])
        box(f'RI03 broad service recess backing {i}', (.08, -.348, start+.45), (.25, .045, .53), materials['dark'], .035)
        box(f'RI03 pale recessed upright insert {i}', (.105, -.385, start+.45), (.065, .055, .34), materials['edge'], .018)
        box(f'RI03 upright insert dark division {i}', (.105, -.414, start+.45), (.022, .009, .23), materials['dark'], .004)
        box(f'RI03 broad spine saddle {i}', (-.17, -.435, start+.45), (.13, .12, .12), materials['edge'], .018)
    box('RI03 continuous flat equipment spine', (-.17, -.47, 2.125), (.095, .085, 3.85), materials['edge'], .014)
    for i, z in enumerate([.97, 2.02, 3.12]):
        box(f'RI03 interstage spine bridge {i}', (-.17, -.345, z), (.09, .26, .075), materials['edge'], .012)
    new_parts = []
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.name in preserved:
            continue
        new_parts.append(obj.name)
        obj.parent = root
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new('Explicit portable tessellation', 'TRIANGULATE')
        mod.keep_custom_normals = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 32
    meshes = [o for o in scene.objects if o.type == 'MESH']
    fit_camera(VIEWS['front-quarter'], meshes)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'), export_format='GLB', use_selection=True,
                             export_apply=True, export_extras=True, export_animations=False)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    for name, direction in VIEWS.items():
        selected = [o for o in meshes if o.name in new_parts and any(w in o.name for w in ['frame 1', 'insert 1', 'backing 1'])] if name == 'service-detail' else meshes
        fit_camera(direction, selected)
        scene.render.filepath = str(MEDIA/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    meta = dict(issue=185, id='openfa:building/legacy/042', culture='rigellian', name='Nourishment Bank',
                stage='structural-detail-refinement', source_study=SOURCE.relative_to(ROOT).as_posix(),
                source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                generator_sha256=sha(Path(__file__)), removed_objects=removed, added_objects=new_parts,
                preserved_objects=sorted(preserved),
                dependencies_sha256={name: sha(Path(__file__).with_name(name)) for name in
                                     ['refine_rigellian_crowns.py', 'refine_rigellian_extractor.py', 'rigellian_nourishment_parts.py']},
                lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
                observed=['Three jade sections, gold interstages and flared base',
                          'Broad pale vertical equipment and repeated front features'],
                inferred=['Readable body-following service housings, upright inset interpretation and support bridges',
                          'Exact recess sections, hidden mechanisms and material identity'],
                preserved='Original overall body profiles, foundation, interstage necks and low foot fitting',
                footprint=[2, 2], views=list(VIEWS), blender=bpy.app.version_string,
                acceptance='Visible equipment refinement study; user artistic acceptance and gameplay calibration open')
    (OUTPUT/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('RI03_VISIBLE_EQUIPMENT_REFINED', len(meshes), flush=True)


if __name__ == '__main__':
    main()
