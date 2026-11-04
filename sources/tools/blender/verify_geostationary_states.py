"""AR5C equipment attachments, axial source fit and scaffold activity verification."""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import verify_artemian_geostationary_construction as original_checker
from refine_geostationary_states import ROOT,INITIAL,EVIDENCE,AXIAL_FIT,PROFILE,HEIGHTS,folders,point,meshes,frame_view,sha
from manufactured_vessels import profile_radius
from verify_skymech_construction import component_volumes,positions
from verify_refined_braccatian_ships import mesh_geometry,materials,compare_materials,helpers
from verify_refined_braccatian_pithoi import tree,inside
from verify_rigellian_crowns import snapshot,drift,compare_render,pixels
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips
FRAMES=list(range(1,182,15))


def structure(meta):
    variant=meta['variant'];root=bpy.data.objects['PlacementRoot'];fit=bpy.data.objects['Authored station axial fit']
    assert root['catalogue_id']==meta['id'] and root['variant']==variant and root['legacy_sprite_frame']==int(variant=='construction')
    assert fit.parent==root and max(abs(float(x)-y) for x,y in zip(fit.scale,[1,1,AXIAL_FIT]))<1e-6
    counts={};volumes={};contacts=[]
    for obj in meshes():
        assert not obj.modifiers and not obj.data.shape_keys;values=component_volumes(obj);counts[obj.name]=len(values);volumes[obj.name]=sum(values)
        if obj.name in meta['added_mesh_names']:assert obj.data.uv_layers
    assert len(meshes())==meta['mesh_objects'];marked=[c for c in bpy.data.collections if c.asset_data];assert len(marked)==1 and all(o.name in marked[0].objects for o in bpy.context.scene.objects if o.type in ['MESH','EMPTY'])
    if variant=='finished':
        assert len(meshes())==132 and len(meta['preserved_mesh_names'])==53 and len(meta['added_mesh_names'])==79 and len(meta['removed_mesh_names'])==12
        assert all(o.parent==fit for o in meshes()) and not any(o.animation_data for o in bpy.context.scene.objects)
        trees={o.name:tree(o) for o in meshes()}
        for spec in meta['attachments']:
            obj=bpy.data.objects[spec['name']];owner=bpy.data.objects[spec['owner']];samples=[obj.matrix_world@v.co for v in obj.data.vertices]+[obj.matrix_world@(f.center-f.normal*.0001) for f in obj.data.polygons];p=next((p for p in samples if inside(trees[owner.name],p)),None)
            if p is None:p=next((owner.matrix_world@f.center for f in owner.data.polygons if inside(trees[obj.name],owner.matrix_world@f.center)),None)
            assert p is not None,(obj.name,owner.name,'New equipment detached');contacts.append(dict(part=obj.name,owner=owner.name,point=list(p)))
        assert len([n for n in counts if n.startswith('AR5C green rim equipment casing')])==6
        assert len([n for n in counts if n.startswith('AR5C pale module bar')])==12
        assert len([n for n in counts if n.startswith('AR5C broad neck equipment shell')])==4 and len([n for n in counts if n.startswith('AR5C neck pale equipment bar')])==12
        assert volumes['AR5C oblique aft shell trim']>.0001
    else:
        assert len(meshes())==151 and len(meta['preserved_mesh_names'])==132 and len(meta['added_mesh_names'])==19
        expected={'AR5C construction circumferential hoops':len(HEIGHTS),'AR5C construction axial ribs':24,'AR5C construction diagonal lattice':(len(HEIGHTS)-1)*24,'AR5C construction body support stays':16}
        for name,value in expected.items():assert counts[name]==value,(name,counts[name],value)
        actor=bpy.data.objects['ConstructionWorkCarriage'];assert actor.parent==root
        for obj in meshes():assert obj.parent==(fit if obj.name in meta['preserved_mesh_names'] else actor if 'construction carriage' in obj.name else root)
        hoops=tree(bpy.data.objects['AR5C construction circumferential hoops']);ribs=tree(bpy.data.objects['AR5C construction axial ribs']);stays=tree(bpy.data.objects['AR5C construction body support stays'])
        for z in [-.55,.55]:
            body=tree(bpy.data.objects['Geostationary green axial body' if z<0 else 'Geostationary green central boss'])
            for i in range(8):
                phi=i*math.tau/8;a=Vector((.20*math.cos(phi),.20*math.sin(phi),z));b=point(phi,z);inner=a.lerp(b,.005);outer=b.lerp(a,.002)
                assert inside(body,inner) and inside(stays,inner),'Body support detached';assert inside(hoops,outer) and inside(stays,outer),'Support misses frame';contacts.append(dict(body=list(inner),frame=list(outer)))
        for i in range(12):
            name=f'AR5C temporary green shield {i}';low=.05 if i%2==0 else -2.95;p=point(i*math.tau/12+.001,low+.003)
            assert counts[name]==1 and volumes[name]>.0001 and inside(ribs,p) and inside(tree(bpy.data.objects[name]),p),(name,'Cover has no frame root')
        exterior={'Geostationary side dish','Geostationary side dish mast','Geostationary side dish feed','Geostationary side amber feed'}
        assert exterior<=set(meta['preserved_mesh_names'])
        for name in set(meta['preserved_mesh_names'])-exterior:
            for vertex in bpy.data.objects[name].data.vertices:
                p=bpy.data.objects[name].matrix_world@vertex.co
                assert PROFILE[0][0]<p.z<PROFILE[-1][0] and math.hypot(p.x,p.y)<profile_radius(PROFILE,p.z)-.008,(name,'Finished part breaches construction envelope',list(p))
        dish=bpy.data.objects['Geostationary side dish'];excess=max(math.hypot(p.x,p.y)-profile_radius(PROFILE,p.z) for p in [dish.matrix_world@v.co for v in dish.data.vertices])
        assert excess>.10,'The source-visible secondary dish must project outside the aft scaffold sleeve'
        contacts.append(dict(external_secondary_fixture_parts=sorted(exterior),dish_radial_projection_beyond_scaffold=excess))
    points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices];bounds=[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)]
    return dict(positive_closed_meshes=len(meshes()),closed_positive_components=sum(counts.values()),components_per_mesh=counts,volumes=volumes,contacts=contacts,bounds=bounds)


def activity(variant):
    if variant=='finished':return {},{},sorted(o.name for o in meshes()),[]
    scene=bpy.context.scene;actor=bpy.data.objects['ConstructionWorkCarriage'];moving=sorted(o.name for o in actor.children);static=sorted(o.name for o in meshes() if o.name not in moving)
    assert len(moving)==3 and [o.name for o in scene.objects if o.animation_data]==[actor.name]
    scene.frame_set(1);base={n:positions(bpy.data.objects[n]) for n in static};states={};transforms={}
    for frame in FRAMES:
        scene.frame_set(frame)
        for name in static:assert np.array_equal(base[name],positions(bpy.data.objects[name])),(name,'Station or framework moves')
        states[frame]={n:sorted(set(tuple(round(float(v),6) for v in p) for p in positions(bpy.data.objects[n]))) for n in moving};transforms[frame]=list(actor.matrix_world.translation)
        rail=tree(bpy.data.objects['AR5C construction circumferential hoops']);nearest=rail.find_nearest(actor.matrix_world.translation)[0];assert nearest is not None and inside(tree(bpy.data.objects['AR5C construction carriage rail clamp']),nearest),'Moving clamp loses rail contact'
    xs=[p[0] for p in transforms.values()];assert .26<max(xs)-min(xs)<.27
    assert states[1]==states[181] and states[1]!=states[61] and states[61]!=states[121]
    scene.frame_set(1);return states,transforms,static,moving

def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['finished','construction'],required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);variant=args.variant
    output,media=folders(variant);meta=json.loads((output/'model.json').read_text());source=ROOT/meta['source_study'];evidence=json.loads(EVIDENCE.read_text())
    assert meta['source_blend_sha256']==sha(source) and meta['source_glb_sha256']==sha(source.with_suffix('.glb')) and meta['generator_sha256']==sha(Path(__file__).with_name('refine_geostationary_states.py')) and meta['evidence_sha256']==sha(EVIDENCE)
    for ext in ['blend','glb']:assert meta[ext+'_sha256']==sha(output/('model.'+ext))
    for n,d in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(n))==d
    for n,d in meta['texture_sha256'].items():assert sha(ROOT/n)==d
    for f in evidence['decoded_frames']:assert sha(ROOT/f['png'])==f['png_sha256']
    original_checker.ROOT=INITIAL.parent
    bpy.ops.wm.open_mainfile(filepath=str(INITIAL));baseline_contract=original_checker.structure(meshes());original_helpers=helpers()
    bpy.ops.wm.open_mainfile(filepath=str(source));original=snapshot();geometry={o.name:mesh_geometry(o) for o in meshes()}
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'));native=snapshot();native_helpers=helpers();native_structure=structure(meta);native_materials=materials();fit_error=0
    for n in meta['preserved_mesh_names']:
        assert mesh_geometry(bpy.data.objects[n])==geometry[n] and native[n]['materials']==original[n]['materials'],(n,'Retained local geometry/UV/normals changed')
        expected=[(p[0],p[1],p[2]*AXIAL_FIT) for p in original[n]['points']] if variant=='finished' else original[n]['points']
        fit_error=max(fit_error,drift(expected,native[n]['points']),drift(native[n]['points'],expected))
    assert fit_error<3e-6
    for name,value in original_helpers.items():assert native_helpers[name]==value
    states,motion,static,moving=activity(variant);scene=bpy.context.scene;views=[('front-quarter',1),('front',1),('rear-quarter',1),('work-detail',1)]+([('work-detail-moved',61)] if variant=='construction' else [('neck-detail',1)])
    for view,frame in views:
        scene.frame_set(frame);frame_view(variant,'work-detail' if view.endswith('-moved') else view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    alpha=pixels(media/'front.png')[:,:,3]>.5;ys,xs=alpha.nonzero();aspect=(int(xs.max())-int(xs.min())+1)/(int(ys.max())-int(ys.min())+1);target=135/74 if variant=='finished' else 141/81;assert abs(aspect-target)<.12,('Source aspect fit',variant,aspect,target)
    collection=next(c for c in bpy.data.collections if c.asset_data)
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name];scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'));scene.frame_set(1)
    imported=snapshot();imported_structure=structure(meta);imported_helpers=helpers();compare_materials(native_materials,materials());assert native_helpers.keys()==imported_helpers.keys();helper_error=0
    for name,a in native_helpers.items():
        b=imported_helpers[name];assert a['parent']==b['parent'];helper_error=max(helper_error,max(abs(x-y) for ra,rb in zip(a['matrix'],b['matrix']) for x,y in zip(ra,rb)))
    assert helper_error<1e-5
    other,other_motion,other_static,other_moving=activity(variant);assert static==other_static and moving==other_moving and native.keys()==imported.keys();assert native_structure['components_per_mesh']==imported_structure['components_per_mesh'];error=0
    for n,a in native.items():
        b=imported[n];error=max(error,drift(a['points'],b['points']),drift(b['points'],a['points']));assert a['materials']==b['materials'] and a['parent']==b['parent']
    for frame in states:
        for name in moving:error=max(error,drift(states[frame][name],other[frame][name]),drift(other[frame][name],states[frame][name]))
    assert error<.0001;clips=glb_clips(output/'model.glb');assert len(clips)==int(variant=='construction')
    if clips:assert clips[0]['name']=='ConstructionActivity' and abs(clips[0]['duration']-6)<1e-5
    renders={}
    for view,frame in views:
        scene.frame_set(frame);frame_view(variant,'work-detail' if view.endswith('-moved') else view);path=media/('imported-'+view+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);renders[view]=compare_render(media/(view+'.png'),path,not view.startswith(('work-detail','neck-detail')))
    deps=['refine_geostationary_states.py','verify_artemian_geostationary_construction.py','verify_skymech_construction.py','verify_refined_braccatian_ships.py','verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py','verify_rigellian_filtration.py']
    report=dict(issue=192,id=meta['id'],variant=variant,legacy_sprite_frame=meta['legacy_sprite_frame'],blender=bpy.app.version_string,source_blend_sha256=sha(source),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},native_mesh_count=len(native),imported_mesh_count=len(imported),native_structure=native_structure,imported_structure=imported_structure,baseline_construction_contract=baseline_contract,maximum_native_imported_position_error=error,maximum_imported_helper_matrix_error=helper_error,maximum_expected_axial_fit_error=fit_error,authored_axial_scale=AXIAL_FIT,retained_geometry_uv_normals_preserved=True,finished_body_geometry_uv_normals_preserved=variant=='construction',finished_helpers_preserved=True,frontal_render_aspect=aspect,source_fixed_state_aspect=target,sampled_frames=FRAMES if variant=='construction' else [1],static_mesh_names=static,moving_mesh_names=moving,native_carriage_positions=motion,imported_carriage_positions=other_motion,authored_clips=clips,renders=renders,evidence_sha256=sha(EVIDENCE),acceptance='Actual native/independent GLB verification; hidden construction and final game calibration remain authored/open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('AR5C_STATE_VERIFIED',variant,len(native),error,helper_error,aspect,flush=True)

if __name__=='__main__':main()
