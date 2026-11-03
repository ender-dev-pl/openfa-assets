"""Verify actual BR4C construction solids, support roots, preserved finished body and GLB activity poses."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_skymech_construction import ROOT,SOURCE,OUTPUT,MEDIA,HEIGHTS,radius,point,frame_view,meshes,sha
from verify_refined_braccatian_pithoi import tree,inside
from verify_refined_braccatian_ships import mesh_geometry,materials,compare_materials,helpers
from verify_rigellian_crowns import snapshot,drift,compare_render
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips

FRAMES=list(range(1,182,15))


def component_volumes(obj):
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent physical surface')
    remaining=set(bm.verts);volumes=[]
    while remaining:
        seed=next(iter(remaining));region=set();queue=[seed]
        while queue:
            v=queue.pop()
            if v in region:continue
            region.add(v);queue += [e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in region]
        remaining-=region;faces={f for v in region for f in v.link_faces};volume=0
        for f in faces:
            verts=[v.co for v in f.verts]
            volume+=sum(verts[0].dot(verts[i].cross(verts[i+1]))/6 for i in range(1,len(verts)-1))
        assert volume>1e-11,(obj.name,'Nonpositive component',volume);volumes.append(volume)
    bm.free();return volumes


def structure(meta):
    scene=bpy.context.scene;scene.frame_set(1);root=bpy.data.objects['PlacementRoot'];actor=bpy.data.objects['ConstructionWorkCarriage']
    assert root['catalogue_id']==meta['id'] and root['variant']=='construction' and root['legacy_sprite_frame']==1
    assert actor.parent==root and len(actor.children)==3
    assert [o.name for o in scene.objects if o.animation_data]==['ConstructionWorkCarriage']
    marked=[c for c in bpy.data.collections if c.asset_data];assert len(marked)==1
    assert all(o.name in marked[0].objects for o in meshes()+[root,actor])
    counts={};volumes={}
    for obj in meshes():
        assert obj.parent in [root,actor] and not obj.modifiers and not obj.data.shape_keys
        values=component_volumes(obj);counts[obj.name]=len(values);volumes[obj.name]=sum(values)
    assert len(meshes())==138 and len(meta['preserved_mesh_names'])==112 and len(meta['added_mesh_names'])==26
    expected={'Construction outer horizontal scaffold hoops':len(HEIGHTS),'Construction outer longitudinal scaffold ribs':24,
      'Construction alternating diagonal lattice':(len(HEIGHTS)-1)*24,'Construction body anchored support stays':16}
    for name,count in expected.items():assert counts[name]==count,(name,'Lost physical scaffold members')
    assert len(meta['temporary_cover_names'])==16
    for name in meta['temporary_cover_names']:assert counts[name]==1 and volumes[name]>.001
    points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    bounds=[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)]
    assert bounds[2]<-3.28 and bounds[5]>3.28 and 4.0<bounds[3]-bounds[0]<4.15,'Construction envelope missing'
    hoop=tree(bpy.data.objects['Construction outer horizontal scaffold hoops']);ribs=tree(bpy.data.objects['Construction outer longitudinal scaffold ribs'])
    stays=tree(bpy.data.objects['Construction body anchored support stays']);core=tree(bpy.data.objects['SkyMech expanded axial pressure core']);contacts=[]
    for z in [-1.2,1.2]:
        for i in range(8):
            phi=i*math.tau/8;a=Vector((.74*math.cos(phi),.74*math.sin(phi),-.96 if z<0 else 1.0));b=point(phi,z)
            inner=a+(b-a)*.01;outer=b+(a-b)*.01
            assert inside(core,inner) and inside(stays,inner),'Construction cage has no body attachment'
            assert inside(hoop,outer) and inside(stays,outer),'Support stay misses outer framework'
            contacts.append(dict(body=list(inner),framework=list(outer)))
    for i,z in enumerate([-1.2,0,1.2]):
        deck=tree(bpy.data.objects[f'Construction temporary annular work deck {i}']);p=point(0,z)
        assert inside(hoop,p) and inside(deck,p),'Floating work deck'
    cover_contacts=[]
    for i,name in enumerate(meta['temporary_cover_names']):
        if i<12:low=.42 if i%2==0 else -1.26;phi=i*math.tau/12
        else:low=-.21;phi=(i-12)*math.pi/2+math.pi/12
        p=point(phi+.001,low+.003)
        assert inside(tree(bpy.data.objects[name]),p) and inside(ribs,p),(name,'Temporary cover has no scaffold root')
        cover_contacts.append(dict(name=name,point=list(p)))
    return dict(positive_closed_meshes=len(meshes()),closed_positive_components=sum(counts.values()),components_per_mesh=counts,volumes=volumes,bounds=bounds,
      body_to_framework_supports=contacts,temporary_cover_roots=cover_contacts,physical_scaffold_members=expected)


def positions(obj):
    deps=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(deps);data=evaluated.to_mesh()
    local=np.empty(len(data.vertices)*3,dtype=np.float32);data.vertices.foreach_get('co',local);local=local.reshape(-1,3)
    matrix=np.array(evaluated.matrix_world,dtype=np.float32);world=np.ascontiguousarray(local@matrix[:3,:3].T+matrix[:3,3]);evaluated.to_mesh_clear();return world


def sampled_activity(meta):
    moving={o.name for o in bpy.data.objects['ConstructionWorkCarriage'].children};static={o.name for o in meshes()}-moving
    assert moving=={n for n in meta['added_mesh_names'] if n.startswith('Construction carriage')}
    scene=bpy.context.scene;scene.frame_set(1);base={n:positions(bpy.data.objects[n]) for n in static};states={};helpers_at={}
    for frame in FRAMES:
        scene.frame_set(frame)
        for name in static:assert np.array_equal(base[name],positions(bpy.data.objects[name])),(name,'Station/scaffold moved')
        states[frame]={n:dict(points=sorted(set(tuple(round(float(v),6) for v in p) for p in positions(bpy.data.objects[n]))),parent=bpy.data.objects[n].parent.name) for n in moving}
        helpers_at[frame]=list(bpy.data.objects['ConstructionWorkCarriage'].matrix_world.translation)
    assert states[1]==states[181] and states[1]!=states[61] and states[61]!=states[121]
    xs=[p[0] for p in helpers_at.values()];assert .29<max(xs)-min(xs)<.31 and max(abs(x) for x in xs)<.20
    scene.frame_set(1);return states,helpers_at,sorted(static),sorted(moving)


def main():
    meta=json.loads((OUTPUT/'model.json').read_text());assert meta['source_blend_sha256']==sha(SOURCE) and meta['source_glb_sha256']==sha(SOURCE.with_suffix('.glb'))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('build_skymech_construction.py'))
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    assert meta['reference_sha256']==sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json')
    assert meta['lore_sha256']==sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json')
    assert sha(ROOT/meta['source_frame_one']['png'])==meta['source_frame_one']['png_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));original=snapshot();geometry={o.name:mesh_geometry(o) for o in meshes()};original_helpers=helpers()
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'));native=snapshot();native_helpers=helpers();native_structure=structure(meta);native_materials=materials()
    assert set(native)==set(original)|set(meta['added_mesh_names'])
    for name in original:
        assert native[name]==original[name] and mesh_geometry(bpy.data.objects[name])==geometry[name],(name,'Finished body changed')
    for name,value in original_helpers.items():assert native_helpers[name]==value
    native_states,native_motion,static,moving=sampled_activity(meta)
    views=[('front-quarter',1),('front',1),('rear-quarter',1),('work-detail',1),('work-detail-moved',61)]
    for view,frame in views:
        bpy.context.scene.frame_set(frame);frame_view('work-detail' if view=='work-detail-moved' else view);bpy.context.scene.render.filepath=str(MEDIA/(view+'.png'));bpy.ops.render.render(write_still=True)
    scene=bpy.context.scene;collection=next(c for c in bpy.data.collections if c.asset_data)
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(OUTPUT/'model.glb'));scene.frame_set(1)
    imported=snapshot();imported_structure=structure(meta);compare_materials(native_materials,materials())
    assert native_structure['components_per_mesh']==imported_structure['components_per_mesh']
    imported_states,imported_motion,other_static,other_moving=sampled_activity(meta);assert static==other_static and moving==other_moving
    error=0;assert native.keys()==imported.keys()
    for name in native:
        a,b=native[name],imported[name];error=max(error,drift(a['points'],b['points']),drift(b['points'],a['points']));assert a['materials']==b['materials'] and a['parent']==b['parent']
    for frame in FRAMES:
        for name in moving:error=max(error,drift(native_states[frame][name]['points'],imported_states[frame][name]['points']))
    assert error<.0001
    clips=glb_clips(OUTPUT/'model.glb');assert len(clips)==1 and clips[0]['name']=='ConstructionActivity' and abs(clips[0]['duration']-6)<1e-5
    renders={}
    for view,frame in views:
        scene.frame_set(frame);frame_view('work-detail' if view=='work-detail-moved' else view);path=MEDIA/('imported-'+view+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);renders[view]=compare_render(MEDIA/(view+'.png'),path,not view.startswith('work-detail'))
    dependencies=['verify_refined_braccatian_pithoi.py','verify_refined_braccatian_ships.py','verify_rigellian_crowns.py','verify_rigellian_filtration.py']
    report=dict(issue=192,id=meta['id'],variant='construction',legacy_sprite_frame=1,blender=bpy.app.version_string,source_blend_sha256=sha(SOURCE),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),
      generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},native_mesh_count=len(native),imported_mesh_count=len(imported),
      native_structure=native_structure,imported_structure=imported_structure,maximum_native_imported_position_error=error,finished_body_geometry_uv_normals_preserved=True,finished_helpers_preserved=True,
      sampled_frames=FRAMES,static_mesh_names=static,moving_mesh_names=moving,native_carriage_positions=native_motion,imported_carriage_positions=imported_motion,authored_clips=clips,renders=renders,
      timing_provenance='Six-second subtle service movement authored for construction variant; not recovered legacy timing',acceptance='Actual native/imported construction and activity checks; final game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('SKYMECH_CONSTRUCTION_NATIVE_GLB_VERIFIED',len(native),error,native_structure['closed_positive_components'],flush=True)


if __name__=='__main__':main()
