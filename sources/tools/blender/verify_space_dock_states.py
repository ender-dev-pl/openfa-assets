"""Verify PS7C refinement/source preservation and physical construction activity in actual Blender/GLB."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from refine_space_dock_states import ROOT,INITIAL,EVIDENCE,HEIGHTS,folders,frame_view,meshes,square,sha,front_y,PROFILES
from verify_skymech_construction import component_volumes,positions
from verify_refined_braccatian_ships import mesh_geometry,materials,compare_materials,helpers
from verify_refined_braccatian_pithoi import tree,inside
from verify_rigellian_crowns import snapshot,drift,compare_render
from verify_space_dock import structure as original_structure
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips

FRAMES=list(range(1,182,15))


def structure(meta):
    variant=meta['variant'];root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['variant']==variant
    assert root['legacy_sprite_frame']==int(variant=='construction')
    marked=[c for c in bpy.data.collections if c.asset_data];assert len(marked)==1
    counts={};volumes={}
    for obj in meshes():
        assert obj.name in marked[0].objects and not obj.modifiers and not obj.data.shape_keys
        parts=component_volumes(obj);counts[obj.name]=len(parts);volumes[obj.name]=sum(parts)
        if obj.name in meta['added_mesh_names']:assert obj.data.uv_layers and all(p.loop_total==3 for p in obj.data.polygons)
    assert len(meshes())==meta['mesh_objects']
    points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices];bounds=[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)]
    contacts=[];hull=tree(bpy.data.objects['Space Dock lower tapered hull'])
    if variant=='finished':
        assert len(meshes())==72 and len(meta['added_mesh_names'])==35 and len(meta['preserved_mesh_names'])==37
        assert not any(o.animation_data for o in bpy.context.scene.objects)
        # Every added visible face/rail has its own material thickness inside the real lower shell.
        for i in range(4):
            phi=i*math.pi/2
            for side in [-1,1]:
                for z in [-1.8,-1.0,-.30]:
                    r=__import__('manufactured_vessels').profile_radius(PROFILES['Space Dock lower tapered hull'],z)
                    p=Vector((side*.30*r,front_y(PROFILES['Space Dock lower tapered hull'],z)+.008,z));p.rotate(__import__('mathutils').Matrix.Rotation(phi,3,'Z'))
                    name=f'Space Dock pale longitudinal hull stiffener {i} {side}'
                    assert inside(hull,p) and inside(tree(bpy.data.objects[name]),p),(name,'Hull stiffener floats')
                    contacts.append(dict(part=name,point=list(p)))
            p=Vector((0,front_y(PROFILES['Space Dock lower tapered hull'],-1.0)+.008,-1.0));p.rotate(__import__('mathutils').Matrix.Rotation(phi,3,'Z'))
            assert inside(hull,p) and inside(tree(bpy.data.objects[f'Space Dock broad dark lower face {i}']),p)
            p=Vector((0,front_y(PROFILES['Space Dock lower tapered hull'],-.48)+.04,-.48));p.rotate(__import__('mathutils').Matrix.Rotation(phi,3,'Z'))
            assert inside(hull,p) and inside(tree(bpy.data.objects[f'Space Dock projecting service case {i}']),p),'Service assembly is detached'
            roof=tree(bpy.data.objects['Space Dock pyramidal upper hull'])
            for side in [-1,1]:
                z=.5;r=__import__('manufactured_vessels').profile_radius(PROFILES['Space Dock pyramidal upper hull'],z)
                p=Vector((side*.20*r,front_y(PROFILES['Space Dock pyramidal upper hull'],z)+.005,z));p.rotate(__import__('mathutils').Matrix.Rotation(phi,3,'Z'))
                name=f'Space Dock broad roof armour field {i} {side}'
                assert inside(roof,p) and inside(tree(bpy.data.objects[name]),p),'Roof armour root detached'
                contacts.append(dict(part=name,point=list(p)))
        assert volumes['Space Dock broad stepped red roof field']>.0005
        roof=tree(bpy.data.objects['Space Dock pyramidal upper hull'])
        for name in ['Space Dock broad stepped red roof field']+[f'Space Dock roof pale service field {s}' for s in [-1,1]]:
            obj=bpy.data.objects[name];n=len(obj.data.vertices)
            # All back-plane points must penetrate the real octagonal roof; sampling inwards avoids boundary ambiguity.
            centre=sum((v.co for v in obj.data.vertices),Vector())/n
            hits=0
            for v in obj.data.vertices:
                p=v.co.lerp(centre,.08)
                if inside(roof,p):hits+=1
            assert hits>=n//2,(name,'A fitted roof field overhangs its actual face',hits,n)
            contacts.append(dict(part=name,penetrating_samples=hits,total_samples=n))
    else:
        assert len(meta['preserved_mesh_names'])==72 and len(meshes())==91 and len(meta['added_mesh_names'])==19
        expected={'Space Dock construction horizontal frames':len(HEIGHTS),'Space Dock construction longitudinal girders':24,'Space Dock construction diagonal lattice':(len(HEIGHTS)-1)*24,'Space Dock construction body support stays':16}
        for name,value in expected.items():assert counts[name]==value
        for i in range(12):assert counts[f'Space Dock temporary shield {i}']==1 and volumes[f'Space Dock temporary shield {i}']>.0001
        stays=tree(bpy.data.objects['Space Dock construction body support stays']);girders=tree(bpy.data.objects['Space Dock construction longitudinal girders'])
        upper=tree(bpy.data.objects['Space Dock pyramidal upper hull'])
        for z in [-1.10,.55]:
            for i in range(8):
                end=square(i*math.tau/8,z);start=end*.5;start.z=z;inner=start.lerp(end,.01);outer=end.lerp(start,.01)
                assert inside(hull if z<0 else upper,inner) and inside(stays,inner),'No real body attachment'
                assert inside(girders,outer) and inside(stays,outer),'Cage support detached'
                contacts.append(dict(body=list(inner),framework=list(outer)))
        for i in range(12):
            z=-1.82 if i%2 else .16;p=square(i*math.tau/12+.001,z+.003)
            assert inside(girders,p) and inside(tree(bpy.data.objects[f'Space Dock temporary shield {i}']),p),'Cover detached'
        assert bounds[2]<-2.89 and bounds[5]>2.04 and bounds[3]-bounds[0]>3.9,bounds
        # Four original berth pods must sit inside the scaffold envelope; the first draft was too narrow at berth height.
        for i in range(4):
            for vertex in bpy.data.objects[f'Space Dock berth pod {i}'].data.vertices:
                p=bpy.data.objects[f'Space Dock berth pod {i}'].matrix_world@vertex.co
                boundary=square(math.atan2(p.y,p.x),p.z)
                assert math.hypot(p.x,p.y)<math.hypot(boundary.x,boundary.y)-.015,'Berth protrudes through construction cage'
    return dict(positive_closed_meshes=len(meshes()),closed_positive_components=sum(counts.values()),components_per_mesh=counts,volumes=volumes,bounds=bounds,support_contacts=contacts)


def activity(variant):
    scene=bpy.context.scene
    if variant=='finished':return {},{},sorted(o.name for o in meshes()),[]
    actor=bpy.data.objects['ConstructionWorkCarriage'];moving=sorted(o.name for o in actor.children);static=sorted(o.name for o in meshes() if o.name not in moving)
    assert len(moving)==3 and actor.parent==bpy.data.objects['PlacementRoot']
    assert [o.name for o in scene.objects if o.animation_data]==[actor.name]
    scene.frame_set(1);base={n:positions(bpy.data.objects[n]) for n in static};states={};transforms={}
    for frame in FRAMES:
        scene.frame_set(frame)
        for name in static:assert np.array_equal(base[name],positions(bpy.data.objects[name])),(name,'Station/cage moves')
        states[frame]={n:sorted(set(tuple(round(float(v),6) for v in p) for p in positions(bpy.data.objects[n]))) for n in moving};transforms[frame]=list(actor.matrix_world.translation)
    assert states[1]==states[181] and states[1]!=states[61] and states[61]!=states[121]
    xs=[p[0] for p in transforms.values()];assert .279<max(xs)-min(xs)<.281
    scene.frame_set(1);return states,transforms,static,moving


def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['finished','construction'],required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);variant=args.variant
    output,media=folders(variant);meta=json.loads((output/'model.json').read_text());source=ROOT/meta['source_study']
    assert sha(source)==meta['source_blend_sha256'] and sha(source.with_suffix('.glb'))==meta['source_glb_sha256']
    for ext in ['blend','glb']:assert meta[ext+'_sha256']==sha(output/('model.'+ext))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_space_dock_states.py')) and meta['evidence_sha256']==sha(EVIDENCE)
    for name,digest in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    for name,digest in meta['texture_sha256'].items():assert sha(ROOT/name)==digest
    evidence=json.loads(EVIDENCE.read_text())
    for frame in evidence['decoded_frames']:assert sha(ROOT/frame['png'])==frame['png_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(INITIAL));baseline_contract=original_structure(meshes());initial_helpers=helpers()
    bpy.ops.wm.open_mainfile(filepath=str(source));original=snapshot();geometry={o.name:mesh_geometry(o) for o in meshes()}
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'));native=snapshot();native_helpers=helpers();native_structure=structure(meta);native_materials=materials()
    assert set(native)==set(meta['preserved_mesh_names'])|set(meta['added_mesh_names'])
    for name in meta['preserved_mesh_names']:assert native[name]==original[name] and mesh_geometry(bpy.data.objects[name])==geometry[name],(name,'Earlier structure changed')
    for name,value in initial_helpers.items():assert native_helpers[name]==value
    states,motion,static,moving=activity(variant)
    views=[('front-quarter',1),('front',1),('rear-quarter',1),('equipment-detail',1)]+([('equipment-detail-moved',61)] if variant=='construction' else [])
    scene=bpy.context.scene
    for view,frame in views:
        scene.frame_set(frame);frame_view(variant,'equipment-detail' if view.endswith('-moved') else view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    collection=next(c for c in bpy.data.collections if c.asset_data)
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name];scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'));scene.frame_set(1)
    imported=snapshot();imported_structure=structure(meta);imported_helpers=helpers();compare_materials(native_materials,materials());other,other_motion,other_static,other_moving=activity(variant)
    assert native_helpers.keys()==imported_helpers.keys()
    helper_error=0
    for name,value in native_helpers.items():
        other_helper=imported_helpers[name];assert value['parent']==other_helper['parent']
        helper_error=max(helper_error,max(abs(a-b) for row_a,row_b in zip(value['matrix'],other_helper['matrix']) for a,b in zip(row_a,row_b)))
    assert helper_error<1e-5,'Export changed a placement/equipment helper'
    assert static==other_static and moving==other_moving and native.keys()==imported.keys();assert native_structure['components_per_mesh']==imported_structure['components_per_mesh']
    error=0
    for name in native:
        a,b=native[name],imported[name];error=max(error,drift(a['points'],b['points']),drift(b['points'],a['points']));assert a['materials']==b['materials'] and a['parent']==b['parent']
    for frame in states:
        for name in moving:error=max(error,drift(states[frame][name],other[frame][name]),drift(other[frame][name],states[frame][name]))
    assert error<.0001
    clips=glb_clips(output/'model.glb');assert len(clips)==int(variant=='construction')
    if clips:assert clips[0]['name']=='ConstructionActivity' and abs(clips[0]['duration']-6)<1e-5
    renders={}
    for view,frame in views:
        scene.frame_set(frame);frame_view(variant,'equipment-detail' if view.endswith('-moved') else view);path=media/('imported-'+view+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);renders[view]=compare_render(media/(view+'.png'),path,not view.startswith('equipment-detail'))
    deps=['verify_skymech_construction.py','verify_refined_braccatian_ships.py','verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py','verify_rigellian_filtration.py','verify_space_dock.py']
    report=dict(issue=192,id=meta['id'],variant=variant,legacy_sprite_frame=meta['legacy_sprite_frame'],blender=bpy.app.version_string,source_blend_sha256=sha(source),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},native_mesh_count=len(native),imported_mesh_count=len(imported),native_structure=native_structure,imported_structure=imported_structure,baseline_construction_contract=baseline_contract,maximum_native_imported_position_error=error,retained_geometry_uv_normals_preserved=True,finished_body_geometry_uv_normals_preserved=variant=='construction',finished_helpers_preserved=True,sampled_frames=FRAMES if variant=='construction' else [1],static_mesh_names=static,moving_mesh_names=moving,native_carriage_positions=motion,imported_carriage_positions=other_motion,authored_clips=clips,renders=renders,acceptance='Actual native/independent import validation; game calibration and final artistic acceptance remain open')
    report['maximum_imported_helper_matrix_error']=helper_error
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('SPACE_DOCK_STATE_VERIFIED',variant,len(native),error,helper_error,flush=True)


if __name__=='__main__':main()
