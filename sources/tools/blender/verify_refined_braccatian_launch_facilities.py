"""Verify retained launch geometry/curves, new moving face fittings, open bores and independent GLB poses."""
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
from refine_braccatian_launch_facilities import ROOT,CASES,folders,source,real_meshes,frame_view,sha
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import drift,compare_render
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips

FRAMES=[1,8,16,24,31,38,46,54,61]


def snapshot():
    deps=bpy.context.evaluated_depsgraph_get();result={}
    for obj in real_meshes():
        evaluated=obj.evaluated_get(deps);data=evaluated.to_mesh()
        points=sorted(set(tuple(round(v,6) for v in evaluated.matrix_world@vertex.co) for vertex in data.vertices))
        result[obj.name]=dict(points=points,parent=obj.parent.name if obj.parent else None,materials=sorted({data.materials[p.material_index].name for p in data.polygons}))
        evaluated.to_mesh_clear()
    return result


def poses():
    states={}
    for frame in FRAMES:bpy.context.scene.frame_set(frame);states[frame]=snapshot()
    return states


def curves():
    result={}
    for obj in bpy.context.scene.objects:
        if not obj.animation_data:continue
        tracks=[]
        for track in obj.animation_data.nla_tracks:
            strips=[]
            for strip in track.strips:
                action=strip.action
                strips.append(dict(name=strip.name,start=strip.frame_start,end=strip.frame_end,scale=strip.scale,repeat=strip.repeat,
                  curves=[dict(path=c.data_path,index=c.array_index,keys=[dict(co=list(k.co),interpolation=k.interpolation,handle_left=list(k.handle_left),handle_right=list(k.handle_right)) for k in c.keyframe_points]) for c in action.fcurves]))
            tracks.append(dict(name=track.name,mute=track.mute,strips=strips))
        result[obj.name]=tracks
    return result


def clear_bore(meta):
    radius=meta['aperture_radius'];floor=meta['floor_height'];trees=[tree(o) for o in real_meshes()]
    points=[(0,0)]+[(radius*fraction*math.cos(i*math.tau/count),radius*fraction*math.sin(i*math.tau/count))
        for fraction,count in [(.5,16),(.95,32)] for i in range(count)]
    heights=[]
    for x,y in points:
        hits=[hit.z for bvh in trees if (hit:=bvh.ray_cast(Vector((x,y,10)),Vector((0,0,-1)),30)[0]) is not None]
        heights.append(max(hits,default=-20))
    assert max(heights)<=floor+.015,('Blocked proven launch bore',max(heights),floor)
    assert min(heights)>=floor-.01,'Retained well floor missing'
    return heights


def structure(key,meta):
    bpy.context.scene.frame_set(1);objects=real_meshes();root=bpy.data.objects['PlacementRoot']
    assert len(objects)=={'br11':10,'br12':7,'br19':9}[key]
    assert root['catalogue_id']==meta['id'] and [root['footprint_width'],root['footprint_height']]==meta['footprint']
    if key=='br11':assert root['preserve_ground_origin']
    assets=[c for c in bpy.data.collections if c.asset_data]
    structural=[o for o in bpy.context.scene.objects if o.type in ['MESH','EMPTY'] and not o.get('preview_only')]
    assert len(assets)==1 and all(o.name in assets[0].objects for o in structural)
    trees={};samples={};bounds={}
    for obj in objects:
        assert obj.data.uv_layers and not obj.modifiers,obj.name
        assert obj.parent is not None and (obj==root or root in ancestors(obj)),obj.name
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent solid')
        assert bm.calc_volume(signed=True)>1e-10,(obj.name,'Nonpositive solid');bm.free()
        trees[obj.name]=tree(obj);pts=[obj.matrix_world@v.co for v in obj.data.vertices]
        bounds[obj.name]=[(min(p[k] for p in pts),max(p[k] for p in pts)) for k in range(3)]
        samples[obj.name]=[obj.matrix_world@(p.center-p.normal*.0001) for p in list(obj.data.polygons)[::max(1,len(obj.data.polygons)//1000)]]
        samples[obj.name]+=pts[::max(1,len(pts)//1000)]
    # The unchanged historical well floor has a tiny radial seating gap; its actual
    # geometry is checked against the source, rather than inventing a new support.
    names=[o.name for o in objects if o.name!='Recessed launch well floor'];graph={n:set() for n in names};contacts=[]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if any(bounds[a][k][1]<bounds[b][k][0] or bounds[b][k][1]<bounds[a][k][0] for k in range(3)):continue
            hit=next((p for p in samples[a] if inside(trees[b],p)),None)
            if hit is None:hit=next((p for p in samples[b] if inside(trees[a],p)),None)
            if hit is not None:graph[a].add(b);graph[b].add(a);contacts.append(dict(parts=[a,b],point=list(hit)))
    reached=set();queue=[names[0]]
    while queue:
        name=queue.pop()
        if name in reached:continue
        reached.add(name);queue+=list(graph[name]-reached)
    assert reached==set(names),('Disconnected closed casing/fitting assembly',set(names)-reached)
    if key=='br11':
        parent=bpy.data.objects['Pyramidal hatch petal.003']
        for name in ['BR11 moving gold face rim','BR11 moving dark face backing','BR11 moving gold face centre']:
            assert bpy.data.objects[name].parent==parent,'Face fitting does not follow its hatch leaf'
        assert len(curves())==4
        features=dict(moving_fitting_parent=parent.name,retained_controls=4)
    else:
        assert not curves(),'Unsupported opening/idle animation introduced'
        liner=bpy.data.objects[key.upper()+' inner structural liner'];accent_faces=[p for p in liner.data.polygons if p.material_index==1]
        assert accent_faces and all(math.hypot(liner.data.vertices[i].co.x,liner.data.vertices[i].co.y)>=.61-1e-5 for p in accent_faces for i in p.vertices),'Inner colour region intrudes into the bore'
        shell=trees[key.upper()+' tapered rose shell'];radii=[]
        for z in [.12,.63]:
            hit=shell.ray_cast(Vector((2,0,z)),Vector((-1,0,0)),4)[0];assert hit is not None;radii.append(hit.x)
        assert radii[0]/radii[1]>1.3 and radii[0]>.97,'Tapered shell regressed to broad torus'
        base=bounds[key.upper()+' square hollow foundation']
        if key=='br19':
            assert abs(base[0][1]-1.40)<1e-5 and base[0][1]/max(abs(v) for v in bounds['BR19 tapered rose shell'][0])>1.35,'Battery lost its broad square foundation'
            lower=shell.ray_cast(Vector((2,0,.18)),Vector((-1,0,0)),4)[0];assert lower.x>1.025,'Battery lower shoulder is not rounded'
        features=dict(measured_shell_sections=radii,inner_finish_faces=len(accent_faces),permanently_open=True)
    maps={}
    for material in {m for o in objects for m in o.data.materials}:
        shader=material.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind);assert np.ptp(values)>.005
            maps[material.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)==(6 if key=='br11' else 8)
    return dict(positive_closed_meshes=len(objects),part_contacts=contacts,all_new_parts_contact_checked=True,
      retained_floor_exception='Original tiny radial seating gap; exact source floor geometry checked separately',packed_maps=maps,**features)


def ancestors(obj):
    result=[]
    while obj.parent:obj=obj.parent;result.append(obj)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;output,media=folders(key);meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source(key))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_launch_facilities.py'))
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    bpy.ops.wm.open_mainfile(filepath=str(source(key)));original=poses();original_curves=curves()
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'));native=poses();assert curves()==original_curves,'Retained animation curves changed'
    preservation_error=0
    for frame in FRAMES:
        for name in meta['retained_mesh_names']:
            preservation_error=max(preservation_error,drift(original[frame][name]['points'],native[frame][name]['points']))
            assert original[frame][name]['parent']==native[frame][name]['parent']
    assert preservation_error<2e-6
    assert native[1]==native[61]
    native_structure=structure(key,meta);bpy.context.scene.frame_set(31);native_clearance=clear_bore(meta)
    views=['front-quarter','front','equipment-detail']+(['open'] if key=='br11' else [])
    for view in views:
        bpy.context.scene.frame_set(31 if view=='open' else 1);frame_view(key,view);bpy.context.scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    keep_materials={m for o in bpy.context.scene.objects if o.type=='MESH' and o.get('preview_only') for m in o.data.materials}
    for obj in list(bpy.context.scene.objects):
        if obj.type in ['MESH','EMPTY'] and not obj.get('preview_only'):bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):
        if mat not in keep_materials:bpy.data.materials.remove(mat,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'));bpy.context.scene.render.fps=30
    imported=poses();imported_structure=structure(key,meta)
    assert native_structure['packed_maps']==imported_structure['packed_maps']
    error=0
    for frame in FRAMES:
        assert native[frame].keys()==imported[frame].keys()
        for name in native[frame]:
            error=max(error,drift(native[frame][name]['points'],imported[frame][name]['points']))
            assert native[frame][name]['materials']==imported[frame][name]['materials'] and native[frame][name]['parent']==imported[frame][name]['parent']
    assert error<.0001
    bpy.context.scene.frame_set(31);imported_clearance=clear_bore(meta)
    actual_clips=glb_clips(output/'model.glb');assert actual_clips==glb_clips(source(key).with_suffix('.glb')),'Clip identity/timing changed'
    moving=[name for name in native[1] if native[1][name]['points']!=native[31][name]['points']]
    assert len(moving)==(7 if key=='br11' else 0)
    renders={}
    for view in views:
        bpy.context.scene.frame_set(31 if view=='open' else 1);frame_view(key,view);path=media/('imported-'+view+'.png');bpy.context.scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        renders[view]=compare_render(media/(view+'.png'),path,view!='equipment-detail')
    report=dict(issue=190,model=key,blender=bpy.app.version_string,source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),
      verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in ['verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py']},native_mesh_count=len(native[1]),imported_mesh_count=len(imported[1]),maximum_native_imported_position_error=error,
      retained_mesh_names=meta['retained_mesh_names'],source_preservation_position_error=preservation_error,retained_animation_curves_equal=True,pose_frames=FRAMES,moving_mesh_names=moving,authored_clips=actual_clips,
      native_structure=native_structure,imported_structure=imported_structure,native_open_aperture_heights=native_clearance,imported_open_aperture_heights=imported_clearance,renders=renders,
      preserved_geometry_claim='Named historical floor/shaft/leaves at all sampled poses and original native NLA curves; generic outer casings/scuff overlays replaced',acceptance='Actual native/import validation; final artistic/game calibration open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_LAUNCH_NATIVE_GLB_VERIFIED',key,len(native[1]),error,preservation_error,flush=True)


if __name__=='__main__':main()
