"""Verify actual RI1C colour sections, attachments and standalone GLB fidelity."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_delphini_visible_sections import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, HULL, old, section, selected_view, fit_camera, sha
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
    assert root['catalogue_id']=='openfa:ship/rigellian/delphini-assault'
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
    for y in [-1.0,-.5,.2,.65]:
        w,z,h=section(y)
        hit=trees[HULL].ray_cast(Vector((3,y,z)),Vector((-1,0,0)),5)[0]
        assert hit is not None and abs(hit.x-w)<.0015,(y,'Unexpected actual main body section')
        sections.append(dict(y=y,width=hit.x*2))
    contacts=[]
    for side in [-1,1]:
        name='Delphini Assault gold upper patch '+str(side)
        obj=bpy.data.objects[name]
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        length=max(p.y for p in points)-min(p.y for p in points)
        assert length>.75,'Gold side field is still a small square'
        for y in [-.20,.05,.30]:
            w,z,h=section(y)
            phi=.65
            x=side*(w-.003)*math.cos(phi)
            p=(x,y,z+(h-.003)*math.sin(phi)-old.dent(x,y))
            assert inside(trees[name],p) and inside(trees[HULL],p),(name,'Conformal side field gap',p)
            contacts.append(dict(name=name,point=p))
        name='Delphini Assault brown ventral body '+str(side)
        p=(side*.50,.18,-.04)
        assert inside(trees[name],p) and inside(trees[HULL],p),(name,'Lower copper body gap')
        contacts.append(dict(name=name,point=p))
    for y in [-.6,0,.7]:
        w,z,h=section(y)
        p=(0,y,z-h+.003)
        name='RI1C lower slate casing'
        assert inside(trees[name],p) and inside(trees[HULL],p),('Lower slate skin is detached',y)
        contacts.append(dict(name=name,point=p))
    for name,p in [('Delphini Assault narrow fore projection',(0,-1.28,.035)),
                   ('Delphini Assault brown tail detail',(0,1.02,.08)),
                   ('Delphini Assault small gold dorsal crest',(0,.64,.47))]:
        assert inside(trees[name],p) and inside(trees[HULL],p),(name,'Root no longer intersects body')
    for mat_name in ['RI1C | aged copper lower casings','RI1C | worn gold side fields','RI1C | worn slate lower skin']:
        shader=bpy.data.materials[mat_name].node_tree.nodes.get('Principled BSDF')
        image=shader.inputs['Base Color'].links[0].from_node.image
        assert image.packed_file and list(image.size)==[512,512]
        assert shader.inputs['Roughness'].links
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unverified process/flight loop'
    return dict(positive_closed_meshes=len(objects),body_sections=sections,solid_skin_contacts=contacts,
                elongated_gold_fields=True,lower_copper_bodies_attached=True,packed_authored_wear=True)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_delphini_visible_sections.py'))
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
    views = ['front-quarter', 'side', 'underside']
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
        renders[view] = compare_render(MEDIA/(view+'.png'), path, True)
    report = dict(issue=185, model='delphini-assault', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=retained,
                  maximum_native_imported_position_error=error, native_structure=native_structure,
                  imported_structure=imported_structure, renders=renders,
                  acceptance='Verified source-bound static body refinement; final artistic acceptance and game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('DELPHINI_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
