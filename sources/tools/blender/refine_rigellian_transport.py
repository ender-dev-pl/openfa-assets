"""RI3C: round the two inline bodies and restore broad source colour sections."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rigellian_transportation_parts as old
from refine_rigellian_crowns import fit_camera, sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'sources/docs/assets/reconstruction/ships/rigellian/transportation/model.blend'
REL = Path('docs/assets/reconstruction/rigellian-refined/transportation')
OUTPUT, MEDIA = ROOT/'sources'/REL, ROOT/'gallery/media'/REL
FRONT, AFT = list(old.PROFILES)
VIEWS = {'front-quarter': (7, -12, 9), 'rear-quarter': (-7, 12, 8),
         'top': (0, 0, 20), 'side': (16, 0, 4), 'body-detail': (4, -5, 14)}


def section(owner, y):
    """Shape-preserving cubic slopes round profile joins without overshoot."""
    rows = old.PROFILES[owner]
    index = next(i for i, (a, b) in enumerate(zip(rows, rows[1:])) if a[0]-1e-8 <= y <= b[0]+1e-8)
    a, b = rows[index:index+2]
    h = b[0]-a[0]
    t = min(1, max(0, (y-a[0])/h))
    values = []
    for axis in [1, 2, 3]:
        slopes = [(q[axis]-p[axis])/(q[0]-p[0]) for p, q in zip(rows, rows[1:])]
        def tangent(i):
            if i == 0:
                return slopes[0]
            if i == len(rows)-1:
                return slopes[-1]
            left, right = slopes[i-1:i+1]
            if left*right <= 0:
                return 0
            hp, hn = rows[i][0]-rows[i-1][0], rows[i+1][0]-rows[i][0]
            return (3*(hp+hn))/((2*hn+hp)/left+(hn+2*hp)/right)
        values.append((2*t**3-3*t*t+1)*a[axis]+(t**3-2*t*t+t)*h*tangent(index)
                      +(-2*t**3+3*t*t)*b[axis]+(t**3-t*t)*h*tangent(index+1))
    return values


def skin(owner, x, y):
    w, z, h = section(owner, y)
    return z+h*math.sqrt(max(0, 1-(x/w)**2))-old.dent(owner, x, y)


def body(owner, material):
    rows, rings = 201, 96
    start, end = old.PROFILES[owner][0][0], old.PROFILES[owner][-1][0]
    points = []
    for j in range(rows):
        y = start+(end-start)*j/(rows-1)
        w, z, h = section(owner, y)
        for i in range(rings):
            phi = i*math.tau/rings
            x, height = w*math.cos(phi), z+h*math.sin(phi)
            if height > .08:
                height -= old.dent(owner, x, y)
            points.append((x, y, height))
    faces = [tuple(reversed(range(rings))), tuple(range((rows-1)*rings, rows*rings))]
    for j in range(rows-1):
        for i in range(rings):
            k = (i+1)%rings
            faces.append((j*rings+i, j*rings+k, (j+1)*rings+k, (j+1)*rings+i))
    obj = mesh(owner, points, faces, material)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def patch(name, owner, y0, y1, u0, u1, material):
    width, height = 25, 65
    top = []
    for row in range(height):
        y = y0+(y1-y0)*row/(height-1)
        w, _, _ = section(owner, y)
        for col in range(width):
            x = w*(u0+(u1-u0)*col/(width-1))
            top.append((x, y, skin(owner, x, y)+.006))
    return old.closed_grid(name, top, width, height, material)


def gold_patch(material):
    count, rows = 96, 16
    top = [(0, -1.22, skin(FRONT, 0, -1.22)+.006)]
    for row in range(1, rows+1):
        for i in range(count):
            phi = i*math.tau/count
            x, y = .265*row/rows*math.cos(phi), -1.22+.32*row/rows*math.sin(phi)
            top.append((x, y, skin(FRONT, x, y)+.006))
    n = len(top)
    vertices = top+[(x, y, z-.016) for x, y, z in top]
    faces = [(0, 1+i, 1+(i+1)%count) for i in range(count)]
    for row in range(rows-1):
        a, b = 1+row*count, 1+(row+1)*count
        for i in range(count):
            k = (i+1)%count
            faces.append((a+i, b+i, b+k, a+k))
    faces += [tuple(n+i for i in reversed(face)) for face in list(faces)]
    a = 1+(rows-1)*count
    for i in range(count):
        k = (i+1)%count
        faces.append((a+i, a+k, a+k+n, a+i+n))
    return mesh('Transportation gold forward patch', vertices, faces, material)


def selected_view(view):
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    root = bpy.data.objects['PlacementRoot']
    originals = {o.name for o in scene.objects if o.type == 'MESH'}
    rebuilt = [FRONT, AFT, 'Transportation gold forward patch']
    rebuilt += ['Transportation copper aft trim '+str(side) for side in [-1, 1]]
    materials = {name: bpy.data.objects[name].data.materials[0] for name in rebuilt}
    modified = []
    # Surface fittings follow the new bodies; the actual alignment helper and
    # ventral saddle/forward terminal keep their established transforms.
    for obj in scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith('Transportation service'):
            continue
        owner = FRONT if obj.name.split()[3] == '0' else AFT
        inverse = obj.matrix_world.inverted()
        for v in obj.data.vertices:
            point = obj.matrix_world@v.co
            y = min(old.PROFILES[owner][-1][0], max(old.PROFILES[owner][0][0], point.y))
            old_w = old.section(owner, y)[0]
            point.x *= section(owner, y)[0]/old_w
            point.z += skin(owner, point.x, y)-old.skin(owner, point.x*old_w/section(owner, y)[0], y)
            v.co = inverse@point
        obj.data.normals_split_custom_set([(0, 0, 0)]*len(obj.data.loops))
        modified.append(obj.name)
    for name in rebuilt:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    body(FRONT, materials[FRONT])
    body(AFT, materials[AFT])
    gold_patch(materials['Transportation gold forward patch'])
    for side in [-1, 1]:
        name = 'Transportation copper aft trim '+str(side)
        patch(name, AFT, .06, 1.12, *sorted([side*.48, side*.86]), materials[name])
    patch('RI3C pale aft upper field', AFT, -.005, 1.06, -.40, .40, materials[FRONT])
    # Large bronze shoulder masses are visible across several headings. Their
    # exact hidden sections are authored; they are not recovered thrusters.
    for side in [-1, 1]:
        points, faces = [], []
        rings, rows = 48, 49
        for j in range(rows):
            t = j/(rows-1)
            radius = .016+.984*math.sin(math.pi*t)
            for i in range(rings):
                phi = math.tau*i/rings
                points.append((side*.54+.16*radius*math.cos(phi), .10+.90*t, .035+.14*radius*math.sin(phi)))
        faces = [tuple(reversed(range(rings))), tuple(range((rows-1)*rings, rows*rings))]
        for j in range(rows-1):
            for i in range(rings):
                k = (i+1)%rings
                faces.append((j*rings+i, j*rings+k, (j+1)*rings+k, (j+1)*rings+i))
        mesh('RI3C copper shoulder pod '+str(side), points, faces, materials['Transportation copper aft trim '+str(side)])
    changed = set(rebuilt+modified)
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.name in originals-changed:
            continue
        obj.parent = root
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        uv(obj)
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new('Portable explicit tessellation', 'TRIANGULATE')
        mod.keep_custom_normals = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    collection = bpy.data.collections.new('Rigellian Transportation refined complete source')
    scene.collection.children.link(collection)
    for old_collection in bpy.data.collections:
        if old_collection.asset_data:
            old_collection.asset_clear()
    for obj in list(scene.objects):
        if obj.type in ['MESH', 'EMPTY']:
            collection.objects.link(obj)
            for previous in list(obj.users_collection):
                if previous != collection:
                    previous.objects.unlink(obj)
    collection.asset_mark()
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
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
    new_names = {o.name for o in scene.objects if o.type == 'MESH'}
    meta = dict(issue=185, id='openfa:ship/rigellian/transportation', culture='rigellian', name='Transportation',
                stage='body-section-refinement', source_study=SOURCE.relative_to(ROOT).as_posix(),
                source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                generator_sha256=sha(Path(__file__)), preserved_objects=sorted(originals-changed),
                modified_objects=sorted(changed), added_objects=sorted(new_names-originals),
                views=list(VIEWS), blender=bpy.app.version_string,
                lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
                reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json'),
                dependency_sha256={name: sha(Path(__file__).with_name(name)) for name in
                    ['rigellian_transportation_parts.py', 'refine_rigellian_crowns.py', 'refine_rigellian_extractor.py', 'refine_rigellian_missiles.py']},
                observed=['Two rounded inline masses and narrow connecting waist in 16 nonempty RI3C headings',
                          'Broad gold forward region, pale aft upper region and bronze aft lateral masses'],
                inferred=['Exact cubic body sections and hidden bronze pod surfaces; architectural guidance is contextual',
                          'Alloy identity, equipment purpose and actual game scale/alignment remain unresolved'],
                acceptance='Static visible-body refinement; final artistic acceptance remains open')
    (OUTPUT/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('RI3C_TRANSPORTATION_REFINED', len(new_names), flush=True)


if __name__ == '__main__':
    main()
