"""Fresh RI4C finished retention and construction/rail activity checks in Blender and GLB."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_observatory_construction import ROOT,SOURCE,OUTPUT,MEDIA,EVIDENCE,FINISHED_REVIEW,HEIGHTS,SCALE_Y,point,meshes,frame_view,sha
from verify_refined_rigellian_observatory import structure as finished_contract
from verify_skymech_construction import component_volumes,positions
from verify_refined_braccatian_ships import mesh_geometry,materials,compare_materials,helpers
from verify_refined_braccatian_pithoi import tree,inside
from verify_rigellian_crowns import snapshot,drift,compare_render
from verify_rigellian_filtration import socket_value
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips

FRAMES=list(range(1,182,15))


def emission():
    result={}
    for mat in {m for o in meshes() for m in o.data.materials}:
        shader=mat.node_tree.nodes.get('Principled BSDF');colour=socket_value(shader.inputs['Emission Color'],(.37,.52));strength=socket_value(shader.inputs['Emission Strength'],(.37,.52));result[mat.name]=[float(x*strength) for x in colour[:3]]
    return result


def structure(variant,meta):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:ship/rigellian/observatory'
    counts={};volumes={};contacts=[]
    for obj in meshes():
        assert not obj.modifiers and not obj.data.shape_keys
        values=component_volumes(obj);counts[obj.name]=len(values);volumes[obj.name]=sum(values)
    if variant=='finished':
        assert len(meshes())==118
        contract=finished_contract()
        return dict(positive_closed_meshes=len(meshes()),closed_positive_components=sum(counts.values()),components_per_mesh=counts,volumes=volumes,finished_contract=contract)
    assert root['variant']=='construction' and root['legacy_sprite_frame']==1
    assert len(meshes())==146 and len(meta['preserved_mesh_names'])==118 and len(meta['added_mesh_names'])==28
    planform=bpy.data.objects['Authored station planform fit'];actor=bpy.data.objects['ConstructionWorkCarriage']
    for o in meshes():assert o.parent==(planform if o.name in meta['preserved_mesh_names'] else actor if 'construction carriage' in o.name else root)
    marked=[c for c in bpy.data.collections if c.asset_data];assert len(marked)==1 and all(o.name in marked[0].objects for o in meshes()+[root,actor,planform,bpy.data.objects['AlignmentAxis']])
    expected={'RI4C construction elliptical hoops':len(HEIGHTS),'RI4C construction meridian ribs':24,'RI4C construction diagonal lattice':(len(HEIGHTS)-1)*24,'RI4C construction axial body stays':16,'RI4C temporary outboard support booms':4}
    for name,value in expected.items():assert counts[name]==value
    core=tree(bpy.data.objects['Observatory axial green chambers']);stays=tree(bpy.data.objects['RI4C construction axial body stays']);hoops=tree(bpy.data.objects['RI4C construction elliptical hoops']);ribs=tree(bpy.data.objects['RI4C construction meridian ribs'])
    for z in [-.6,.6]:
        for i in range(8):
            phi=i*math.tau/8;a=Vector((.20*math.cos(phi),.20*SCALE_Y*math.sin(phi),z));b=point(phi,z);inner=a.lerp(b,.01);outer=b.lerp(a,.005)
            assert inside(core,inner) and inside(stays,inner),'Construction has no axial body support'
            assert inside(hoops,outer) and inside(stays,outer),'Body stay misses cage'
            contacts.append(dict(body=list(inner),frame=list(outer)))
    for i,name in enumerate(meta['temporary_cover_names']):
        assert counts[name]==1 and volumes[name]>.0001
        low=.65 if i%2==0 else -2.55;p=point(i*math.tau/12+.001,low+.003)
        assert inside(ribs,p) and inside(tree(bpy.data.objects[name]),p),(name,'Floating temporary shield')
    booms=tree(bpy.data.objects['RI4C temporary outboard support booms']);body=tree(bpy.data.objects['Observatory saucer pressure hull'])
    for i in range(4):
        phi=i*math.pi/2;start=Vector((1.90*math.cos(phi),1.90*.7*math.sin(phi),0));end=Vector((3.2*math.cos(phi),3.2*SCALE_Y*math.sin(phi),0))
        assert inside(body,start.lerp(end,.01)) and inside(booms,start.lerp(end,.01)),'Outboard work station has no hull root'
        assert inside(booms,end.lerp(start,.01)) and inside(tree(bpy.data.objects[f'RI4C outboard temporary service casing {i}']),end.lerp(start,.01)),'Work station misses its support boom'
    points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices];bounds=[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)]
    assert bounds[2]<-3.09 and bounds[5]>3.09 and bounds[3]-bounds[0]>6.60,bounds
    return dict(positive_closed_meshes=len(meshes()),closed_positive_components=sum(counts.values()),components_per_mesh=counts,volumes=volumes,body_support_contacts=contacts,bounds=bounds,physical_members=expected)


def activity(variant):
    if variant=='finished':return {},{},sorted(o.name for o in meshes()),[]
    scene=bpy.context.scene;actor=bpy.data.objects['ConstructionWorkCarriage'];moving=sorted(o.name for o in actor.children);static=sorted(o.name for o in meshes() if o.name not in moving);assert len(moving)==3
    assert [o.name for o in scene.objects if o.animation_data]==[actor.name]
    scene.frame_set(1);base={n:positions(bpy.data.objects[n]) for n in static};states={};transforms={}
    for frame in FRAMES:
        scene.frame_set(frame)
        for name in static:assert np.array_equal(base[name],positions(bpy.data.objects[name])),(name,'Station/framework moves')
        states[frame]={n:sorted(set(tuple(round(float(v),6) for v in p) for p in positions(bpy.data.objects[n]))) for n in moving};transforms[frame]=list(actor.matrix_world.translation)
        # The moving clamp must continue to physically enclose the nearest guide-rail surface.
        rail=tree(bpy.data.objects['RI4C construction elliptical hoops']);nearest=rail.find_nearest(actor.matrix_world.translation)[0]
        assert nearest is not None and inside(tree(bpy.data.objects['RI4C construction carriage rail clamp']),nearest),'Carriage loses its guide rail'
    xs=[p[0] for p in transforms.values()];assert .36<max(xs)-min(xs)<.37
    assert states[1]==states[181] and states[1]!=states[61] and states[61]!=states[121]
    scene.frame_set(1);return states,transforms,static,moving


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--variant',choices=['finished','construction'],required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);variant=args.variant
    evidence=json.loads(EVIDENCE.read_text())
    for f in evidence['decoded_frames']:assert sha(ROOT/f['png'])==f['png_sha256']
    lore=ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json';assert sha(lore)==evidence['lore_evidence_sha256']
    old=json.loads(SOURCE.with_suffix('.json').read_text());assert old['blend_sha256']==sha(SOURCE) and old['glb_sha256']==sha(SOURCE.with_suffix('.glb'))
    assert old['generator_sha256']==sha(Path(__file__).with_name('refine_rigellian_observatory.py')) and old['lore_sha256']==sha(lore)
    for n,d in old['dependencies_sha256'].items():assert sha(Path(__file__).with_name(n))==d
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));original=snapshot();geometry={o.name:mesh_geometry(o) for o in meshes()};source_helpers=helpers();contract=finished_contract()
    output=SOURCE.parent if variant=='finished' else OUTPUT;media=FINISHED_REVIEW if variant=='finished' else MEDIA;media.mkdir(parents=True,exist_ok=True)
    meta=old if variant=='finished' else json.loads((OUTPUT/'model.json').read_text())
    if variant=='construction':
        assert meta['source_blend_sha256']==sha(SOURCE) and meta['source_glb_sha256']==sha(SOURCE.with_suffix('.glb')) and meta['evidence_sha256']==sha(EVIDENCE)
        assert meta['generator_sha256']==sha(Path(__file__).with_name('build_observatory_construction.py'))
        for n,d in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(n))==d
        for n,d in meta['texture_sha256'].items():assert sha(ROOT/n)==d
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'));native=snapshot();native_helpers=helpers();native_structure=structure(variant,meta);native_materials=materials();native_emission=emission()
    for name in original:assert native[name]==original[name] and mesh_geometry(bpy.data.objects[name])==geometry[name],(name,'Finished source changed')
    for name,value in source_helpers.items():assert native_helpers[name]==value
    states,motion,static,moving=activity(variant);scene=bpy.context.scene
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.samples=24
    views=[('front-quarter',1),('front',1),('rear-quarter',1),('work-detail',1)]+([('work-detail-moved',61)] if variant=='construction' else [])
    for view,frame in views:
        scene.frame_set(frame);frame_view('work-detail' if view.endswith('-moved') else view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    collection=next(c for c in bpy.data.collections if c.asset_data)
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name];scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'));scene.frame_set(1)
    imported=snapshot();imported_structure=structure(variant,meta);imported_helpers=helpers();compare_materials(native_materials,materials());other_emission=emission()
    assert native_emission.keys()==other_emission.keys()
    for n,values in native_emission.items():assert max(abs(a-b) for a,b in zip(values,other_emission[n]))<.005,(n,'Effective emission changed')
    assert native_helpers.keys()==imported_helpers.keys();helper_error=0
    for name,value in native_helpers.items():
        other=imported_helpers[name];assert value['parent']==other['parent'];helper_error=max(helper_error,max(abs(a-b) for ra,rb in zip(value['matrix'],other['matrix']) for a,b in zip(ra,rb)))
    assert helper_error<1e-5
    other,other_motion,other_static,other_moving=activity(variant);assert static==other_static and moving==other_moving
    assert native.keys()==imported.keys() and native_structure['components_per_mesh']==imported_structure['components_per_mesh'];error=0
    for n,a in native.items():
        b=imported[n];error=max(error,drift(a['points'],b['points']),drift(b['points'],a['points']));assert a['materials']==b['materials'] and a['parent']==b['parent']
    for frame in states:
        for name in moving:error=max(error,drift(states[frame][name],other[frame][name]),drift(other[frame][name],states[frame][name]))
    assert error<.0001;clips=glb_clips(output/'model.glb');assert len(clips)==int(variant=='construction')
    if clips:assert clips[0]['name']=='ConstructionActivity' and abs(clips[0]['duration']-6)<1e-5
    renders={}
    for view,frame in views:
        scene.frame_set(frame);frame_view('work-detail' if view.endswith('-moved') else view);path=media/('imported-'+view+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);renders[view]=compare_render(media/(view+'.png'),path,not view.startswith('work-detail'))
    deps=['build_observatory_construction.py','verify_refined_rigellian_observatory.py','verify_skymech_construction.py','verify_refined_braccatian_ships.py','verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py','verify_rigellian_filtration.py']
    report=dict(issue=192,id=old['id'],variant=variant,legacy_sprite_frame=int(variant=='construction'),decision='retained-refined-after-focused-review' if variant=='finished' else 'new-construction-variant',blender=bpy.app.version_string,source_blend_sha256=sha(SOURCE),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},native_mesh_count=len(native),imported_mesh_count=len(imported),native_structure=native_structure,imported_structure=imported_structure,original_finished_contract=contract,maximum_native_imported_position_error=error,maximum_imported_helper_matrix_error=helper_error,finished_body_geometry_uv_normals_preserved=True,finished_helpers_preserved=True,effective_emission_verified=True,native_materials=native_materials,native_emission=native_emission,sampled_frames=FRAMES if variant=='construction' else [1],native_carriage_positions=motion,imported_carriage_positions=other_motion,static_mesh_names=static,moving_mesh_names=moving,authored_clips=clips,renders=renders,evidence_sha256=sha(EVIDENCE),acceptance='Actual asset runtime validation; hidden construction and final game calibration remain authored/open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('RI4C_STATION_STATE_VERIFIED',variant,len(native),error,helper_error,flush=True)


if __name__=='__main__':main()
