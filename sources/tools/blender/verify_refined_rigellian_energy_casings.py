"""Verify RI14 broad casing divisions, conduit clearance and independent GLB."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_energy_casings import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, BODY, PROFILES, profile_radius, selected_view, fit_camera, sha
from verify_rigellian_crowns import snapshot, drift, compare_render


def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [list(p.vertices) for p in obj.data.polygons])


def inside(bvh, point):
    direction = Vector((.173, .291, .941)).normalized()
    point = Vector(point)
    hit, normal, _, _ = bvh.ray_cast(point, direction, 10)
    return hit is not None and normal.dot(direction) > 0


def structure():
    root=bpy.data.objects['PlacementRoot']
    assert root['catalogue_id']=='openfa:building/legacy/053'
    assert root['footprint_width']==root['footprint_height']==2
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    trees={}
    for obj in objects:
        assert obj.parent==root,(obj.name,'Detached component')
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data=evaluated.to_mesh()
        bm=bmesh.new();bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent physical surface')
        assert bm.calc_volume(signed=True)>0,(obj.name,'Inverted/empty physical component')
        bm.free();evaluated.to_mesh_clear()
        trees[obj.name]=tree(obj)
    contacts=[]
    for label,z in [('lower',.32),('upper',1.17)]:
        phi=-1.9;r=profile_radius(PROFILES[BODY],z)-.008
        p=(r*math.cos(phi),r*math.sin(phi),z)
        name='RI14 refined casing '+label+' backing'
        assert inside(trees[BODY],p) and inside(trees[name],p),('Backing/body root gap',label)
        contacts.append(dict(name=name,point=p))
    for label in ['upper horizontal','lower vertical']:
        for i in range(3):
            name=f'RI14 refined casing {label} rib {i}'
            obj=bpy.data.objects[name]
            points=[obj.matrix_world@v.co for v in obj.data.vertices]
            height=max(p.z for p in points)-min(p.z for p in points)
            angles=[math.atan2(p.y,p.x) for p in points]
            span=max(angles)-min(angles)
            if label.startswith('upper'):
                assert height<.075 and span>1.20,'Upper casing must have broad horizontal divisions'
                phi,z=-1.9,[1.05,1.23,1.41][i]
                backing='RI14 refined casing upper backing'
            else:
                assert height>.43 and span<.25,'Lower casing must have long vertical divisions'
                phi,z=[-2.335,-1.935,-1.545][i],.40
                backing='RI14 refined casing lower backing'
            r=profile_radius(PROFILES[BODY],z)+.012
            p=(r*math.cos(phi),r*math.sin(phi),z)
            assert inside(trees[name],p) and inside(trees[backing],p),('Rib/backing gap',name)
            contacts.append(dict(name=name,point=p))
    # Actual front rays through the original pale conduit must not meet new casings.
    new=[trees[o.name] for o in objects if 'refined casing' in o.name]
    for z in [.22,.40,.58,1.05,1.23,1.41]:
        origin=Vector((.20,-2,z));direction=Vector((0,1,0))
        assert all(t.ray_cast(origin,direction,3)[0] is None for t in new),('New casing hides conduit',z)
        assert trees['RI14 silver front conduit'].ray_cast(origin,direction,3)[0] is not None
    crown=trees['RI14 open upturned crown'];floor=trees['RI14 crown floor']
    for r in [.12,.20,.28]:
        origin=Vector((r,0,4));direction=Vector((0,0,-1))
        a=crown.ray_cast(origin,direction,4)[0];b=floor.ray_cast(origin,direction,4)[0]
        assert b is not None and (a is None or a.z<b.z),'Crown opening is closed above the floor'
    shader=bpy.data.materials['RI14 | worn recessed bronze casing'].node_tree.nodes.get('Principled BSDF')
    image=shader.inputs['Base Color'].links[0].from_node.image
    assert image.packed_file and list(image.size)==[512,512]
    assert shader.inputs['Roughness'].links
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unverified energy-generation loop'
    return dict(positive_closed_meshes=len(objects),solid_casing_contacts=contacts,
                three_upper_horizontal_ribs=True,three_lower_vertical_ribs=True,
                pale_conduit_clear_of_new_casings=True,open_crown_retained=True,packed_authored_wear=True)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_rigellian_energy_casings.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    assert meta['reference_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json')
    assert meta['functional_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json')
    for name, value in meta['dependency_sha256'].items():
        assert value == sha(Path(__file__).with_name(name))
    for path, value in meta['texture_sha256'].items():
        assert sha(ROOT/path) == value
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    original = snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native = snapshot()
    retained = 0
    for name in meta['preserved_objects']:
        retained = max(retained, drift(original[name]['points'], native[name]['points']))
        assert original[name]['materials'] == native[name]['materials'] and original[name]['parent'] == native[name]['parent']
    assert retained < 1e-6
    assert set(native) == set(meta['preserved_objects']+meta['modified_objects']+meta['added_objects'])
    assert (set(original)-set(meta['removed_objects'])) | set(meta['added_objects']) == set(native), 'Unexpected model population change'
    collections = [c for c in bpy.data.collections if c.asset_data]
    assert len(collections) == 1 and all(o.name in collections[0].objects for o in bpy.context.scene.objects if o.type in ['MESH', 'EMPTY'])
    native_structure = structure()
    views = ['front-quarter', 'front', 'casing-detail']
    for view in views:
        fit_camera(VIEWS[view], selected_view(view))
        bpy.context.scene.render.filepath = str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT/'model.glb'))
    imported = snapshot()
    assert set(native) == set(imported)
    error = 0
    for name in native:
        error = max(error, drift(native[name]['points'], imported[name]['points']), drift(imported[name]['points'], native[name]['points']))
        assert native[name]['materials'] == imported[name]['materials'] and native[name]['parent'] == imported[name]['parent']
    assert error < .0001
    imported_structure = structure()
    renders = {}
    for view in views:
        fit_camera(VIEWS[view], selected_view(view))
        path = MEDIA/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[view] = compare_render(MEDIA/(view+'.png'), path, view != 'casing-detail')
    report = dict(issue=185, model='ri14', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=retained,
                  maximum_native_imported_position_error=error, native_structure=native_structure,
                  imported_structure=imported_structure, renders=renders,
                  acceptance='Verified source-bound static body refinement; final artistic acceptance and game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RI14_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
