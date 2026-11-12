"""Verify the RI23 tapered segmented base and retained native/imported yaw rig."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_lance_base import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, SKIRT, PROFILE, MOVING, PIVOT, LANCE_TIPS, LANCE_AXIS, profile_radius, selected_view, fit_camera, sha
from verify_rigellian_crowns import snapshot, drift, compare_render


def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [list(p.vertices) for p in obj.data.polygons])


def inside(bvh, point):
    direction = Vector((.173, .291, .941)).normalized()
    point = Vector(point)
    hit, normal, _, _ = bvh.ray_cast(point, direction, 10)
    return hit is not None and normal.dot(direction) > 0


def empty_state():
    return {o.name:dict(parent=o.parent.name if o.parent else None,matrix=[list(row) for row in o.matrix_world])
            for o in bpy.context.scene.objects if o.type=='EMPTY'}


def bounds(obj):
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    return [min(p[i] for p in pts) for i in range(3)]+[max(p[i] for p in pts) for i in range(3)]


def yaw_evidence(objects):
    yaw=bpy.data.objects['YawPivot']
    assert yaw.parent==bpy.data.objects['PlacementRoot'] and (yaw.location-PIVOT).length<1e-6
    fixed={o.name:bounds(o) for o in objects if o.name not in MOVING}
    result=[]
    yaw.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        yaw.rotation_quaternion=Quaternion((0,0,1),angle)
        bpy.context.view_layer.update()
        rotation=Matrix.Rotation(angle,3,'Z')
        tips={}
        for side,tip in LANCE_TIPS.items():
            socket=bpy.data.objects['LanceTipSocket '+str(side)]
            lance=bpy.data.objects['RI23 bronze lance '+str(side)]
            expected=PIVOT+rotation@(tip-PIVOT)
            forward=rotation@LANCE_AXIS
            assert socket.parent==yaw and socket['forward_axis']=='local +Z'
            assert (socket.matrix_world.translation-expected).length<1e-5
            assert ((socket.matrix_world.to_3x3()@Vector((0,0,1))).normalized()-forward).length<1e-5
            projections=[(lance.matrix_world@v.co-expected).dot(forward) for v in lance.data.vertices]
            assert abs(max(projections))<1e-4 and min(projections)<-.90,'Actual lance endpoint/extent changed'
            tips[str(side)]=dict(position=list(socket.matrix_world.translation),forward=list(forward))
        for name,old_bounds in fixed.items():
            assert max(abs(a-b) for a,b in zip(old_bounds,bounds(bpy.data.objects[name])))<1e-6,'Fixed base moved during yaw'
        result.append(dict(yaw_degrees=round(math.degrees(angle)),tip_sockets=tips))
    yaw.rotation_quaternion=Quaternion((0,0,1),0)
    bpy.context.view_layer.update()
    return result


def structure():
    root=bpy.data.objects['PlacementRoot']
    assert root['catalogue_id']=='openfa:building/legacy/062'
    assert root['footprint_width']==root['footprint_height']==3
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    trees={}
    for obj in objects:
        assert obj.parent==(bpy.data.objects['YawPivot'] if obj.name in MOVING else root),(obj.name,'Wrong rigid assembly')
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data=evaluated.to_mesh()
        bm=bmesh.new();bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent physical surface')
        assert bm.calc_volume(signed=True)>0,(obj.name,'Inverted/empty physical component')
        bm.free();evaluated.to_mesh_clear()
        trees[obj.name]=tree(obj)
    vertices=[bpy.data.objects[SKIRT].matrix_world@v.co for v in bpy.data.objects[SKIRT].data.vertices]
    bottom=max(math.hypot(p.x,p.y) for p in vertices if abs(p.z)<1e-6)
    top=max(math.hypot(p.x,p.y) for p in vertices if .19<p.z<.22)
    assert bottom/top<.62,'Bronze foot is still a nearly cylindrical skirt'
    contacts=[]
    for i in range(12):
        name=f'RI23 bronze skirt segment {i:02}'
        n=Vector((math.cos(math.tau*i/12),math.sin(math.tau*i/12),0))
        bvh=trees[name]
        for z in [.07,.13,.20]:
            r=profile_radius(PROFILE,z)-.005
            p=n*r+Vector((0,0,z))
            assert inside(trees[SKIRT],p) and inside(bvh,p),(name,'Segment/skirt gap')
            contacts.append(list(p))
        relief=[]
        for z in [.103,.125,.165]:
            axis=Vector((0,0,z))
            hit=bvh.ray_cast(axis+n*2,-n,3)[0]
            assert hit is not None
            relief.append(hit.dot(n)-profile_radius(PROFILE,z))
        assert relief[1]-max(relief[0],relief[2])>.008,'Horizontal segment relief is missing'
    for a,b,p in [(SKIRT,'RI23 fixed green pedestal',(0,0,.235)),
                  ('RI23 fixed green pedestal','RI23 static yaw bearing',(0,0,.98)),
                  ('RI23 static yaw bearing','RI23 rotating green head',(0,0,1.015))]:
        assert inside(trees[a],p) and inside(trees[b],p),(a,b,'Assembly root gap')
    for side in [-1,1]:
        p=LANCE_TIPS[side]-LANCE_AXIS*.93
        assert inside(trees['RI23 bronze lance '+str(side)],p) and inside(trees['RI23 rotating green head'],p),'Lance/head root gap'
    shader=bpy.data.materials['RI23 | worn recessed bronze skirt'].node_tree.nodes.get('Principled BSDF')
    image=shader.inputs['Base Color'].links[0].from_node.image
    assert image.packed_file and list(image.size)==[512,512] and shader.inputs['Roughness'].links
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Yaw rig must not become an invented idle/firing loop'
    poses=yaw_evidence(objects)
    return dict(positive_closed_meshes=len(objects),tapered_foot_radius_ratio=bottom/top,
                segment_root_contacts=contacts,horizontal_segment_relief=True,yaw_poses=poses,
                preserved_two_lance_rig=True,packed_authored_wear=True)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_rigellian_lance_base.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    assert meta['reference_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json')
    assert meta['functional_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json')
    for name, value in meta['dependency_sha256'].items():
        assert value == sha(Path(__file__).with_name(name))
    for path, value in meta['texture_sha256'].items():
        assert sha(ROOT/path) == value
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    original = snapshot()
    original_helpers = empty_state()
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native = snapshot()
    native_helpers = empty_state()
    assert original_helpers == native_helpers, 'Yaw/socket helper changed'
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
    views = ['front-quarter', 'front', 'skirt-detail']
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
    imported_helpers = empty_state()
    assert imported_helpers.keys() == native_helpers.keys()
    for name, helper in native_helpers.items():
        other = imported_helpers[name]
        assert helper['parent'] == other['parent']
        assert max(abs(helper['matrix'][i][j]-other['matrix'][i][j]) for i in range(4) for j in range(4)) < 1e-5
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
        renders[view] = compare_render(MEDIA/(view+'.png'), path, view != 'skirt-detail')
    report = dict(issue=185, model='ri23', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=retained,
                  maximum_native_imported_position_error=error, native_structure=native_structure,
                  imported_structure=imported_structure, renders=renders,
                  acceptance='Verified source-bound static body refinement; final artistic acceptance and game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RI23_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
