"""Check BR18/20/23 construction, all headings, retained controls and independent GLB renders."""
import argparse
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
from refine_braccatian_weapons import ROOT,CASES,folders,source,objects,frame_view,sha
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import snapshot,drift,compare_render
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips


def action_signature():
    head=bpy.data.objects['DirectionalHead'];action=head.animation_data.action
    curves=[]
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    curves.append(dict(path=curve.data_path,index=curve.array_index,keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right)) for k in curve.keyframe_points]))
    assert curves,'Missing directional action'
    return dict(name=action.name,location=list(head.location),rotation_mode=head.rotation_mode,curves=curves)


def poses():
    result={}
    for frame in range(1,18):bpy.context.scene.frame_set(frame);result[frame]=snapshot()
    return result


def structure(key,meta):
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update();number,_=CASES[key]
    root=bpy.data.objects['PlacementRoot'];head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase']
    assert root['catalogue_id']==f'openfa:building/legacy/{number:03}'
    assert [root['footprint_width'],root['footprint_height']]==meta['footprint']
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    assert head.parent==base.parent==root
    meshes=objects();names=[o.name for o in meshes];p=key.upper()+' '
    assert len(meshes)=={'br18':10,'br20':17,'br23':10}[key]
    collections=[c for c in bpy.data.collections if c.asset_data];assert len(collections)==1
    assert all(o.name in collections[0].objects for o in meshes+[root,head,base])
    assert {o.name for o in meshes if o.parent==head}==set(meta['rotation_rig']['moving_meshes'])
    assert {o.name for o in meshes if o.parent==base}==set(meta['rotation_rig']['static_meshes'])
    assert [o.name for o in scene.objects if o.animation_data]==['DirectionalHead']
    trees={};samples={};bounds={}
    for obj in meshes:
        assert obj.parent in [head,base] and obj.data.uv_layers and not obj.modifiers,obj.name
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent solid')
        assert bm.calc_volume(signed=True)>1e-9,(obj.name,'Nonpositive solid');bm.free();trees[obj.name]=tree(obj)
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        bounds[obj.name]=[(min(v[i] for v in points),max(v[i] for v in points)) for i in range(3)]
        samples[obj.name]=points[::max(1,len(points)//1500)]
        samples[obj.name]+=[obj.matrix_world@(f.center-f.normal*.0001) for f in list(obj.data.polygons)[::max(1,len(obj.data.polygons)//1500)]]
    contacts=[];graph={n:set() for n in names}
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if any(bounds[a][k][1]<bounds[b][k][0] or bounds[b][k][1]<bounds[a][k][0] for k in range(3)):continue
            hit=next((point for point in samples[a] if inside(trees[b],point)),None)
            if hit is None:hit=next((point for point in samples[b] if inside(trees[a],point)),None)
            if hit is not None:contacts.append(dict(parts=[a,b],point=list(hit)));graph[a].add(b);graph[b].add(a)
    seen=set();queue=[names[0]]
    while queue:
        name=queue.pop()
        if name in seen:continue
        seen.add(name);queue+=list(graph[name]-seen)
    assert seen==set(names),('Disconnected construction',set(names)-seen)
    body=trees[p+'rose domed pedestal and narrow neck'];radii=[]
    for z in [.20,.50,.95]:
        hit=body.ray_cast(Vector((2,0,z)),Vector((-1,0,0)),4)[0];assert hit is not None;radii.append(hit.x)
    assert radii[0]>.75 and .56<radii[1]<.63 and radii[2]<.11,'Domed body/narrow neck lost'
    assert min(bound[2][0] for bound in bounds.values())>=-1e-6
    count=6 if key=='br20' else 4
    assert sum(n.startswith(p+'gold radial foot ') for n in names)==count
    assert sum(n.startswith(p+'foot upper cap ') for n in names)==count
    for i in range(count):
        cap=bpy.data.objects[p+f'foot upper cap {i}'];styles={mat.name for mat in cap.data.materials}
        assert any(('blue-cap' if key=='br20' else 'red-cap' if key=='br23' else 'gold-casting') in s for s in styles)
    if key=='br20':
        # Cast through the distal three fingers and the two gaps in the actual meshes.
        fingers=[trees[p+f'separate emitter prong {i}'] for i in range(3)]
        for x in [-.17,0,.17]:assert any(t.ray_cast(Vector((x,-3,1.86)),Vector((0,1,0)),4)[0] is not None for t in fingers)
        for x in [-.085,.085]:assert not any(t.ray_cast(Vector((x,-3,1.86)),Vector((0,1,0)),4)[0] is not None for t in fingers),'Fingers fused across visible gaps'
        assert len(head.children)==4
    else:
        assert len(head.children)==1,'Source has a single emitter'
        emitter=head.children[0];vertices=[emitter.matrix_world@v.co for v in emitter.data.vertices]
        tip=[v for v in vertices if v.z>(2.10 if key=='br23' else 1.70)]
        shoulder=[v for v in vertices if 1.12<v.z<1.35]
        assert tip and shoulder and max(abs(v.x) for v in shoulder)>3*max(abs(v.x) for v in tip),'Emitter taper lost'
        assert max(v.z for v in vertices)>(2.17 if key=='br23' else 1.76)
    bearing=[]
    for frame in range(1,17):
        scene.frame_set(frame);bpy.context.view_layer.update();point=Vector((0,0,1.00))
        assert inside(tree(bpy.data.objects[p+'rose domed pedestal and narrow neck']),point)
        assert any(inside(tree(o),point) for o in head.children),'Rotated head lost contact with its bearing'
        bearing.append(frame)
    scene.frame_set(1);maps={}
    for mat in {m for o in meshes for m in o.data.materials}:
        shader=mat.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind);assert np.ptp(values)>.005
            maps[mat.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)==(4 if key=='br18' else 6)
    return dict(positive_closed_meshes=len(meshes),part_contacts=contacts,all_parts_contact_checked=True,joined_assembly=True,packed_maps=maps,
      measured_pedestal_radial_sections=radii,separated_prong_count=3 if key=='br20' else 1,radial_foot_count=count,connected_bearing_heading_frames=bearing)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;output,media=folders(key);meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source(key))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_weapons.py'))
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    bpy.ops.wm.open_mainfile(filepath=str(source(key)));original_action=action_signature()
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'));assert action_signature()==original_action,'Original heading action changed'
    native=poses();native_structure=structure(key,meta);views=[('front-quarter',1),('front',1),('equipment-detail',1),('rear-quarter',9)]
    for view,frame in views:
        bpy.context.scene.frame_set(frame);frame_view(view);bpy.context.scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    collection=next(c for c in bpy.data.collections if c.asset_data)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.scene.render.fps=16;bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'))
    imported=poses();imported_structure=structure(key,meta);assert native_structure['packed_maps']==imported_structure['packed_maps']
    error=0
    for frame in range(1,18):
        assert native[frame].keys()==imported[frame].keys()
        for name in native[frame]:
            a,b=native[frame][name],imported[frame][name];error=max(error,drift(a['points'],b['points']),drift(b['points'],a['points']))
            assert a['parent']==b['parent'] and a['materials']==b['materials']
            if name in meta['rotation_rig']['static_meshes']:assert native[frame][name]==native[1][name] and imported[frame][name]==imported[1][name]
    assert error<.0001
    assert all(native[1][n]['points']!=native[5][n]['points'] for n in meta['rotation_rig']['moving_meshes'])
    clips=glb_clips(output/'model.glb');assert clips==glb_clips(source(key).with_suffix('.glb')),'Heading preview clip identity/timing changed'
    renders={}
    for view,frame in views:
        bpy.context.scene.frame_set(frame);frame_view(view);path=media/('imported-'+view+'.png');bpy.context.scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        renders[view]=compare_render(media/(view+'.png'),path,True)
    report=dict(issue=190,model=key,blender=bpy.app.version_string,source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),
      verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in ['verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py']},native_mesh_count=len(native[1]),imported_mesh_count=len(imported[1]),maximum_native_imported_position_error=error,
      native_structure=native_structure,imported_structure=imported_structure,retained_heading_controller_and_action=original_action,pose_frames=list(range(1,18)),authored_clips=clips,renders=renders,
      preserved_geometry_claim='None: complete old placeholder preserved separately; only source controller/action retained',acceptance='Actual native/import validation; final artistic/game calibration open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_WEAPON_NATIVE_GLB_VERIFIED',key,len(native[1]),error,flush=True)


if __name__=='__main__':main()
