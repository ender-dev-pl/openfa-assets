"""Verify RI2C body fields, real terminal recess and standalone GLB fidelity."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_messier_visible_sections import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, HULL, TERMINAL, section, skin, side_skin, selected_view, fit_camera, sha
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
    assert root['catalogue_id']=='openfa:ship/rigellian/messier-lukannon'
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
    sections=[]
    for y in [-1.20,-.5,.2,.95]:
        w,z,h=section(y)
        hit=trees[HULL].ray_cast(Vector((3,y,z)),Vector((-1,0,0)),5)[0]
        assert hit is not None and abs(hit.x-w)<.0015
        sections.append(dict(y=y,width=hit.x*2))
    ring=trees[TERMINAL]
    direction=Vector((0,1,0))
    assert ring.ray_cast(Vector((0,-3,0)),direction,4)[0] is None,'Central terminal opening obstructed by copper'
    lip=ring.ray_cast(Vector((.18,-3,0)),direction,4)[0]
    face=trees['RI2C recessed dark terminal face'].ray_cast(Vector((0,-3,0)),direction,4)[0]
    assert lip is not None and face is not None and .14<face.y-lip.y<.18,'Missing physical terminal recess'
    inward=ring.ray_cast(Vector((0,-1.765,0)),Vector((1,0,0)),1)
    assert inward[0] is not None and inward[1].x<-.8,'No inward-facing copper mouth wall'
    p=(.155,-1.615,.02)
    assert inside(ring,p) and inside(trees['RI2C recessed dark terminal face'],p),'Recess backing does not meet ring'
    p=(.21,-1.45,.04)
    assert inside(ring,p) and inside(trees[HULL],p),'Copper terminal body root gap'
    contacts=[]
    for side in [-1,1]:
        name='RI2C green aft body field '+str(side)
        for y in [.20,.65,1.10]:
            x=side*section(y)[0]*.55
            p=(x,y,skin(x,y)-.003)
            assert inside(trees[name],p) and inside(trees[HULL],p),(name,'Green field gap')
            contacts.append(dict(name=name,point=p))
        wing='Messier-Lukannon copper ventral wing '+str(side)
        p=(side*.50,.32,-.12)
        assert inside(trees[wing],p) and inside(trees[HULL],p),'Ventral wing root gap'
        for i,yc in enumerate([-.56,.43]):
            bezel='Messier-Lukannon side boss bezel '+str(side)+' '+str(i)
            cap='Messier-Lukannon side boss face '+str(side)+' '+str(i)
            for j in range(8):
                phi=math.tau*j/8
                y,z=yc+.075*math.cos(phi),.075*math.sin(phi)
                p=(side*(side_skin(y,z)-.010),y,z)
                assert inside(trees[bezel],p) and inside(trees[HULL],p),(bezel,'Cast root gap',p)
            p=(side*(side_skin(yc,0)+.071),yc,0)
            assert inside(trees[bezel],p) and inside(trees[cap],p),(cap,'Face/bezel gap')
        for i,y in enumerate([-.72,.10]):
            x=side*.30
            p=(x,y,skin(x,y)-.003)
            name='Messier-Lukannon gold dorsal fitting '+str(side)+' '+str(i)
            assert inside(trees[name],p) and inside(trees[HULL],p),(name,'Dorsal fitting gap')
    shader=bpy.data.materials['RI2C | worn green aft fields'].node_tree.nodes.get('Principled BSDF')
    image=shader.inputs['Base Color'].links[0].from_node.image
    assert image.packed_file and list(image.size)==[512,512]
    assert shader.inputs['Roughness'].links
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unverified process/flight loop'
    return dict(positive_closed_meshes=len(objects),body_sections=sections,solid_green_field_contacts=contacts,
                measured_authored_recess_depth=face.y-lip.y,open_copper_mouth=True,backing_and_ring_connected=True,
                side_boss_root_samples=32,side_face_overlaps=4,retained_ventral_wings_attached=True,packed_authored_wear=True)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_messier_visible_sections.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    assert meta['reference_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json')
    for name, value in meta['dependency_sha256'].items():
        assert value == sha(Path(__file__).with_name(name))
    for path, value in meta['texture_sha256'].items():
        assert sha(ROOT/path) == value
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    original = snapshot()
    alignment = [list(row) for row in bpy.data.objects['AlignmentForward'].matrix_world]
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native = snapshot()
    retained = 0
    for name in meta['preserved_objects']:
        retained = max(retained, drift(original[name]['points'], native[name]['points']))
        assert original[name]['materials'] == native[name]['materials'] and original[name]['parent'] == native[name]['parent']
    assert retained < 1e-6
    assert set(native) == set(meta['preserved_objects']+meta['modified_objects']+meta['added_objects'])
    assert (set(original)-set(meta['removed_objects'])) | set(meta['added_objects']) == set(native), 'Unexpected model population change'
    assert alignment == [list(row) for row in bpy.data.objects['AlignmentForward'].matrix_world]
    collections = [c for c in bpy.data.collections if c.asset_data]
    assert len(collections) == 1 and all(o.name in collections[0].objects for o in bpy.context.scene.objects if o.type in ['MESH', 'EMPTY'])
    native_structure = structure()
    views = ['front-quarter', 'top', 'terminal-detail']
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
    assert max(abs(alignment[i][j]-bpy.data.objects['AlignmentForward'].matrix_world[i][j]) for i in range(4) for j in range(4)) < 1e-6
    imported_structure = structure()
    renders = {}
    for view in views:
        fit_camera(VIEWS[view], selected_view(view))
        path = MEDIA/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[view] = compare_render(MEDIA/(view+'.png'), path, view != 'terminal-detail')
    report = dict(issue=185, model='messier-lukannon', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=retained,
                  maximum_native_imported_position_error=error, native_structure=native_structure,
                  imported_structure=imported_structure, renders=renders,
                  acceptance='Verified source-bound static body refinement; final artistic acceptance and game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('MESSIER_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
