"""RI0A visible body/lobes; tiny source pixels do not establish hidden mechanisms."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lazzaro_research_parts as old
from refine_rigellian_crowns import fit_camera, sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'sources/docs/assets/reconstruction/ships/rigellian/lazzaro-research/model.blend'
REL = Path('docs/assets/reconstruction/rigellian-refined/lazzaro-research')
OUTPUT, MEDIA = ROOT/'sources'/REL, ROOT/'gallery/media'/REL
TEXTURES = ROOT/'sources/materials/reconstruction/rigellian-refined/lazzaro-research'
HULL = 'Lazzaro Research compact green hull'
CROWN = 'Lazzaro Research gold central crown'
CROWN_ROWS = [(-.64, .06, .14, .05), (-.35, .28, .20, .14),
              (.26, .33, .21, .16), (.57, .15, .18, .10), (.63, .03, .15, .04)]
VIEWS = {'front-quarter': (7, -12, 9), 'rear-quarter': (-7, 12, 8),
         'top': (0, 0, 20), 'side': (16, 0, 4), 'lobe-detail': (4, -5, 14)}


def interpolate(rows, y):
    index = next(i for i, (a, b) in enumerate(zip(rows, rows[1:])) if a[0]-1e-8 <= y <= b[0]+1e-8)
    a, b = rows[index:index+2]
    h, t = b[0]-a[0], (y-a[0])/(b[0]-a[0])
    result = []
    for axis in [1, 2, 3]:
        slopes = [(q[axis]-p[axis])/(q[0]-p[0]) for p, q in zip(rows, rows[1:])]
        def tangent(i):
            if i in [0, len(rows)-1]:
                return slopes[0 if i == 0 else -1]
            left, right = slopes[i-1:i+1]
            if left*right <= 0:
                return 0
            hp, hn = rows[i][0]-rows[i-1][0], rows[i+1][0]-rows[i][0]
            return 3*(hp+hn)/((2*hn+hp)/left+(hn+2*hp)/right)
        result.append((2*t**3-3*t*t+1)*a[axis]+(t**3-2*t*t+t)*h*tangent(index)
                      +(-2*t**3+3*t*t)*b[axis]+(t**3-t*t)*h*tangent(index+1))
    return result


def section(y):
    return interpolate(old.SECTIONS, y)


def skin(y, x, original=False):
    w, z, h = old.section(y) if original else section(y)
    return z+h*math.sqrt(max(0, 1-(x/w)**2))-old.dent(x, y)


def finish_material(original, name, colour, filename):
    """Preserve authored wear variation, changing its broad material colour."""
    mat = original.copy()
    mat.name = name
    node = mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node
    image = node.image
    data = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(data)
    data = data.reshape(image.size[1], image.size[0], 4)
    size = 512
    values = data[np.linspace(0, image.size[1]-1, size).astype(int)[:, None],
                  np.linspace(0, image.size[0]-1, size).astype(int)[None, :]].copy()
    luminance = np.mean(values[:, :, :3], axis=2)
    variation = np.clip(luminance/max(.01, float(np.median(luminance))), .65, 1.35)
    values[:, :, :3] = np.asarray(colour)[None, None, :]*variation[:, :, None]
    authored = bpy.data.images.new(name+' authored colour wear', width=size, height=size)
    authored.pixels.foreach_set(values.ravel())
    TEXTURES.mkdir(parents=True, exist_ok=True)
    path = TEXTURES/filename
    authored.filepath_raw, authored.file_format = str(path), 'PNG'
    authored.save()
    authored = bpy.data.images.load(str(path), check_existing=False)
    authored.colorspace_settings.name = 'sRGB'
    authored.pack()
    node.image = authored
    return mat


def lobe(side, end, gray, bronze):
    rows, rings = 81, 64
    points = []
    for row in range(rows):
        u = -1+2*row/(rows-1)
        factor = max(.02, 1-u**4)**.25
        for i in range(rings):
            phi = math.tau*i/rings
            points.append((side*(.63+.34*u), end*(.46+.06*u+.22*factor*math.cos(phi)),
                           .025+.092*factor*math.sin(phi)))
    faces = [tuple(reversed(range(rings))), tuple(range((rows-1)*rings, rows*rings))]
    for row in range(rows-1):
        for i in range(rings):
            j = (i+1)%rings
            faces.append((row*rings+i, row*rings+j, (row+1)*rings+j, (row+1)*rings+i))
    name = f'Lazzaro Research grey lobe {side} {end}'
    obj = mesh(name, points, faces, gray)
    obj.data.materials.append(bronze)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
        if abs(sum(obj.data.vertices[i].co.x for i in face.vertices)/len(face.vertices)) > .82:
            face.material_index = 1
    return obj


def selected_view(view):
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene, root = bpy.context.scene, bpy.data.objects['PlacementRoot']
    original_names = {o.name for o in scene.objects if o.type == 'MESH'}
    removed = []
    for obj in list(scene.objects):
        if obj.name.startswith(('Lazzaro Research grey lobe', 'Lazzaro Research brown tip',
                                'Lazzaro Research lobe brace', 'Lazzaro Research lobe fastener')):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    hull = bpy.data.objects[HULL]
    for v in hull.data.vertices:
        x, y, z = v.co
        ow, oz, oh = old.section(y)
        nw, nz, nh = section(y)
        previous_dent = old.dent(x, y) if z > .04 else 0
        v.co.x = x*nw/ow
        v.co.z = nz+(z+previous_dent-oz)*nh/oh
        if v.co.z > .04:
            v.co.z -= old.dent(v.co.x, y)
    bronze = bpy.data.objects[CROWN].data.materials[0]
    gray = finish_material(hull.data.materials[0], 'RI0A | worn slate lateral shells', (.27, .30, .34), 'slate-lobes.png')
    gold = finish_material(bronze, 'RI0A | worn gold crown finish', (.48, .35, .105), 'gold-crown.png')
    bpy.data.objects.remove(bpy.data.objects[CROWN], do_unlink=True)
    points, faces = [], []
    rows, rings = 161, 96
    for row in range(rows):
        y = CROWN_ROWS[0][0]+(CROWN_ROWS[-1][0]-CROWN_ROWS[0][0])*row/(rows-1)
        w, z, h = interpolate(CROWN_ROWS, y)
        for i in range(rings):
            phi = math.tau*i/rings
            points.append((1.25*w*math.cos(phi), y, z+h*math.sin(phi)))
    faces = [tuple(reversed(range(rings))), tuple(range((rows-1)*rings, rows*rings))]
    for row in range(rows-1):
        for i in range(rings):
            j = (i+1)%rings
            faces.append((row*rings+i, row*rings+j, (row+1)*rings+j, (row+1)*rings+i))
    crown = mesh(CROWN, points, faces, gold)
    for face in crown.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    modified = [HULL, CROWN]
    for obj in scene.objects:
        if not obj.name.startswith('Lazzaro Research shoulder'):
            continue
        inverse = obj.matrix_world.inverted()
        for v in obj.data.vertices:
            point = obj.matrix_world@v.co
            point.z += skin(point.y, point.x)-skin(point.y, point.x, True)
            v.co = inverse@point
        modified.append(obj.name)
    for side in [-1, 1]:
        for end in [-1, 1]:
            modified.append(lobe(side, end, gray, bronze).name)
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        obj.parent = root
        obj.data.normals_split_custom_set([(0, 0, 0)]*len(obj.data.loops))
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
    collection = bpy.data.collections.new('Lazzaro refined complete editable source')
    scene.collection.children.link(collection)
    for previous in bpy.data.collections:
        if previous.asset_data:
            previous.asset_clear()
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
    final_names = {o.name for o in scene.objects if o.type == 'MESH'}
    meta = dict(issue=185, id='openfa:ship/rigellian/lazzaro-research', culture='rigellian', name='Lazzaro Research',
                stage='visible-form-refinement', source_study=SOURCE.relative_to(ROOT).as_posix(),
                source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                generator_sha256=sha(Path(__file__)), preserved_objects=[], modified_objects=modified,
                removed_objects=sorted(set(removed)-final_names), added_objects=sorted(final_names-set(modified)),
                views=list(VIEWS), blender=bpy.app.version_string,
                lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
                reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json'),
                dependency_sha256={name: sha(Path(__file__).with_name(name)) for name in
                    ['lazzaro_research_parts.py', 'refine_rigellian_crowns.py', 'refine_rigellian_extractor.py', 'refine_rigellian_missiles.py']},
                texture_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in TEXTURES.glob('*.png')},
                observed=['Broad gold central region, green shoulders and gray lateral lobes with brown extremities in all 32 tiny RI0A headings'],
                inferred=['Four-lobe separation and hidden lobe thickness/curves remain authored interpretation',
                          'Material identity and interface purpose are not established by CDB architectural context'],
                original_mesh_count=len(original_names),
                acceptance='Visible-form refinement; final artistic acceptance and game calibration remain open')
    (OUTPUT/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('LAZZARO_VISIBLE_FORMS_REFINED', len(final_names), flush=True)


if __name__ == '__main__':
    main()
