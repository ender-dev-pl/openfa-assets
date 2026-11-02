"""Refine all seven Rigellian missile families from paletted flight/launch evidence."""
import argparse
import importlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_crowns import fit_camera, sha
from refine_rigellian_extractor import mesh

ROOT = Path(__file__).resolve().parents[3]
KEYS = ['detonator', 'multi-det', 'flamejell', 'maxi-det', 'flare', 'viral-repair', 'temporal-stasis']
VIEWS = {'front-quarter': (7, -12, 9), 'top': (0, 0, 20), 'side': (16, 0, 4),
         'rear-quarter': (-7, 12, 8), 'body-detail': (4, -8, 14)}


def paths(key):
    rel = Path('docs/assets/reconstruction/rigellian-refined/missiles')/key
    return (ROOT/'sources/docs/assets/reconstruction/missiles/rigellian'/key/'model.blend',
            ROOT/'sources'/rel, ROOT/'gallery/media'/rel)


def branch(name, side, low, high, outer, half_depth, material, gold=False):
    points = []
    rows = 25
    for row in range(rows):
        t = row/(rows-1)
        inner = outer*(.35+.25*t)
        edge = outer*(.85+.18*math.sin(math.pi*t)-.02*t)
        y = low+(high-low)*t
        if gold:
            inner = inner+(edge-inner)*.55
        width = edge-inner
        section = [(inner, -.5), (inner+width*.15, -1), (edge-width*.15, -1), (edge, -.5),
                   (edge, .5), (edge-width*.15, 1), (inner+width*.15, 1), (inner, .5)]
        for x, z in section:
            points.append((side*x, y, z*half_depth))
    faces = [tuple(reversed(range(8)))]
    for row in range(rows-1):
        for i in range(8):
            j = (i+1)%8
            faces.append((row*8+i, row*8+j, (row+1)*8+j, (row+1)*8+i))
    faces.append(tuple((rows-1)*8+i for i in range(8)))
    obj = mesh(name, points, faces, material, smooth=False)
    # The long planes remain readable facets, not a rectangular extrusion.
    return obj


def uv(obj):
    data = obj.data
    while data.uv_layers:
        data.uv_layers.remove(data.uv_layers[0])
    names = {node.uv_map for mat in data.materials for node in mat.node_tree.nodes
             if node.type == 'UVMAP' and node.uv_map}
    assert len(names) <= 1, (obj.name, names)
    layer = data.uv_layers.new(name=next(iter(names)) if names else 'Authored detail UV')
    for face in data.polygons:
        axis = max(range(3), key=lambda i: abs(face.normal[i]))
        a, b = [i for i in range(3) if i != axis]
        for index in face.loop_indices:
            p = data.vertices[data.loops[index].vertex_index].co
            layer.data[index].uv = (.5+p[a]*.65, .5+p[b]*.65)


def band(module, name, owner, low, high, material):
    profile = module.PROFILES[owner]
    heights = sorted(set([low, high]+[z for z, _ in profile if low < z < high]))
    rows = [(y, module.profile_radius(profile, y)+.005, module.profile_radius(profile, y)-.018) for y in heights]
    return module.orient(module.annulus(name, (0, 0), rows, material, (0, (low+high)/2, 0)), module.Y_AXIS)


def select_view(view):
    objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if view == 'body-detail':
        return [obj for obj in objects if 'rear prong' not in obj.name and 'gold rail' not in obj.name]
    return objects


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=KEYS, required=True)
    key = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model
    module_name = 'rigellian_'+key.replace('-', '_')+'_parts'
    module = importlib.import_module(module_name)
    source, output, media = paths(key)
    output.mkdir(parents=True, exist_ok=True)
    media.mkdir(parents=True, exist_ok=True)
    old_meta = json.loads(source.with_suffix('.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    root = bpy.data.objects['PlacementRoot']
    original_names = {o.name for o in scene.objects if o.type == 'MESH'}
    removed, created, modified = [], [], []
    specs = []
    prongs = [o for o in scene.objects if 'rear prong' in o.name]
    assert len(prongs) == 2
    bounds = [p.matrix_world@v.co for p in prongs for v in p.data.vertices]
    low, high = min(p.y for p in bounds), max(p.y for p in bounds)
    outer = max(abs(p.x) for p in bounds)
    half_depth = max(abs(p.z) for p in bounds)
    hull_material = prongs[0].data.materials[0]
    rails = [o for o in scene.objects if 'gold rail' in o.name]
    gold_material = rails[0].data.materials[0] if rails else None
    prefix = prongs[0].name.split(' rear prong')[0]
    for obj in prongs+rails:
        removed.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
    for i, side in enumerate([-1, 1]):
        created.append(branch(prefix+' rear prong '+str(i), side, low, high, outer, half_depth, hull_material).name)
        if gold_material:
            created.append(branch(prefix+' gold rail '+str(i), side, low, high, outer, half_depth+.004, gold_material, True).name)
    for spec in old_meta['conformal_panels']:
        name = spec['name']
        if 'service' in name:
            continue
        factor = 1.3 if 'pale body' in name else 1.8 if key == 'temporal-stasis' else 2.2
        if key == 'multi-det':
            continue  # Its gold neck area is already broad and source-supported.
        obj = bpy.data.objects[name]
        material = obj.data.materials[0]
        removed.append(name)
        bpy.data.objects.remove(obj, do_unlink=True)
        updated = dict(spec)
        updated['width'] *= factor
        obj = module.patch(name, updated['owner'], updated['z0'], updated['z1'], updated['phi'], updated['width'],
                           material, updated['top'], updated['back'], updated['support'])
        created.append(obj.name)
        specs.append(updated)
    collars = []
    for obj in list(scene.objects):
        if 'pale band' not in obj.name:
            continue
        coords = [obj.matrix_world@v.co for v in obj.data.vertices]
        centre = (min(p.y for p in coords)+max(p.y for p in coords))/2
        old_width = max(p.y for p in coords)-min(p.y for p in coords)
        r = max(math.hypot(p.x, p.z) for p in coords)-.005
        candidates = [(abs(module.profile_radius(profile, centre)-r), owner) for owner, profile in module.PROFILES.items()
                      if profile[0][0] <= centre <= profile[-1][0]]
        owner = min(candidates)[1]
        profile = module.PROFILES[owner]
        a = max(profile[0][0]+.001, centre-old_width*.85)
        b = min(profile[-1][0]-.001, centre+old_width*.85)
        name, material = obj.name, obj.data.materials[0]
        removed.append(name)
        bpy.data.objects.remove(obj, do_unlink=True)
        created.append(band(module, name, owner, a, b, material).name)
        collars.append(dict(name=name, owner=owner, low=a, high=b, old_width=old_width))
    if key == 'detonator':
        mat = bpy.data.materials.new('Rigellian Detonator | purple forward colour collar')
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (.18, .065, .24, 1)
        shader.inputs['Metallic'].default_value = .46
        shader.inputs['Roughness'].default_value = .75
        created.append(band(module, prefix+' purple forward collar', module.NOSE, -.845, -.785, mat).name)
    if key in ['detonator', 'multi-det']:
        tip = bpy.data.objects[module.NOSE]
        threshold = -.845 if key == 'detonator' else -.89
        end = min(v.co.y for v in tip.data.vertices)
        for vertex in tip.data.vertices:
            y = vertex.co.y
            if y < threshold:
                t = (threshold-y)/(threshold-end)
                vertex.co.y = threshold+(y-threshold)*.55
                vertex.co.x *= 1+.3*t*t
                vertex.co.z *= 1+.3*t*t
        tip.data.normals_split_custom_set([(0, 0, 0)]*len(tip.data.loops))
        modified.append(tip.name)
    for name in created:
        obj = bpy.data.objects[name]
        obj.parent = root
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        uv(obj)
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new('Explicit portable tessellation', 'TRIANGULATE')
        mod.keep_custom_normals = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    collection = bpy.data.collections.new(prefix+' refined complete source')
    scene.collection.children.link(collection)
    for old in bpy.data.collections:
        if old.asset_data:
            old.asset_clear()
    for obj in list(scene.objects):
        if obj.type in ['MESH', 'EMPTY']:
            collection.objects.link(obj)
            for old in list(obj.users_collection):
                if old != collection:
                    old.objects.unlink(obj)
    collection.asset_mark()
    collection.asset_data.description = 'Refined Rigellian missile; colour regions, fitted collars and open faceted fork; no exhaust or calibrated mount'
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 24
    fit_camera(VIEWS['front-quarter'], select_view('front-quarter'))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH', 'EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'), export_format='GLB', use_selection=True,
                             export_apply=True, export_extras=True, export_animations=False)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    for view, direction in VIEWS.items():
        fit_camera(direction, select_view(view))
        scene.render.filepath = str(media/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    meta = dict(issue=185, id='openfa:missile/rigellian/'+key, culture='rigellian', name=key,
                stage='visible-section-refinement', source_study=source.relative_to(ROOT).as_posix(),
                source_blend_sha256=sha(source), blend_sha256=sha(output/'model.blend'), glb_sha256=sha(output/'model.glb'),
                generator_sha256=sha(Path(__file__)), parts_module=module_name,
                parts_sha256=sha(Path(__file__).with_name(module_name+'.py')),
                dependency_sha256={name: sha(Path(__file__).with_name(name)) for name in ['refine_rigellian_crowns.py', 'refine_rigellian_extractor.py']},
                removed_objects=removed, added_objects=created, modified_objects=modified,
                preserved_objects=sorted(original_names-set(removed)-set(modified)),
                broad_panels=specs, fitted_collars=collars,
                fork=dict(low=low, high=high, outer_radius=outer, half_depth=half_depth, gold_outer_edges=bool(gold_material)),
                lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
                reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/missile-reference-index.json'),
                observed=['Open green fork, distinct central colour fields and forward colour subdivisions',
                          'Gold fork edges on Flare/Temporal Stasis; Detonator purple forward region'],
                inferred=['Faceted fork sections, exact panel/collar dimensions and hidden surfaces',
                          'Colour regions do not establish a cockpit, propulsion mechanism or missile articulation'],
                state_policy='Static solid-body study; exhaust/effects excluded; alignment helper remains uncalibrated',
                views=list(VIEWS), blender=bpy.app.version_string,
                acceptance='Visible section refinement; final artistic acceptance and calibrated gameplay mounting open')
    (output/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('RIGELLIAN_MISSILE_SECTIONS_REFINED', key, len([o for o in scene.objects if o.type == 'MESH']), flush=True)


if __name__ == '__main__':
    main()
