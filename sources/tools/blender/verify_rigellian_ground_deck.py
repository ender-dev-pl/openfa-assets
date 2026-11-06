"""Verify actual RI10 native and imported GLB moving assemblies and rendered states."""
import hashlib
import json
import sys
import struct
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_rigellian_ground_deck import ROOT
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_shaft_preview import asset_meshes,ground_mask,surface_points
from verify_assault_fighter import check_meshes
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values

FRAMES=list(range(1,62))


def moving(obj):
    while obj.parent:
        obj=obj.parent
        if obj.name in ['CoverLeft','CoverRight']: return True
    return False


def tree(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    result=BVHTree.FromPolygons([evaluated.matrix_world @ v.co for v in mesh.vertices],[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
    evaluated.to_mesh_clear();return result


def indicator_visibility(meshes,visible):
    direction=Vector((0,16,-7)).normalized();shapes={obj.name:tree(obj) for obj in meshes};checks=[]
    targets=[obj for obj in meshes if obj.name.startswith('RI10 interior recessed red indicator')]
    assert len(targets)==2
    for obj in targets:
        passed=0
        for x in [-.03,0,.03]:
            for y in [-.02,0,.02]:
                point=obj.matrix_world @ Vector((x,-.007,y));origin=point-direction*10
                hits=[]
                for name,shape in shapes.items():
                    position,_,_,distance=shape.ray_cast(origin,direction)
                    if position is not None: hits.append((distance,name))
                nearest=min(hits)[1];seen=nearest==obj.name
                assert seen==visible,('Indicator visibility differs',obj.name,x,y,visible,nearest)
                passed+=int(seen)
        checks.append(dict(object=obj.name,visible_sample_rays=passed,total_sample_rays=9))
    return checks


def clear_shaft(meshes):
    shapes={obj.name:tree(obj) for obj in meshes};depths=[]
    for x in [-.3,0,.3]:
        for y in [-.25,0,.25]:
            hits=[]
            for name,shape in shapes.items():
                point,_,_,distance=shape.ray_cast(Vector((x,y,2)),Vector((0,0,-1)))
                if point is not None: hits.append((distance,name,point.z))
            _,name,z=min(hits)
            assert name=='RI10 shaft distant dark bottom' and z<-1.9,('Shaft is blocked by shallow geometry',x,y,name,z)
            depths.append(z)
    return depths


def inspect(meshes):
    scene=bpy.context.scene;scene.frame_set(1);check_meshes(meshes,allow_packed_images=True)
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/049'
    assert root['footprint_width']==root['footprint_height']==3
    assert root.matrix_world.is_identity
    assert len([o for o in meshes if o.name.startswith('RI10 shaft wall vertical guide')])==3
    movers=[o for o in meshes if moving(o)];assert len(movers)==8
    assert all(tuple(o.scale)==(1,1,1) for o in meshes)
    fixed=[o for o in meshes if not moving(o)];snapshots={};collisions=[]
    for frame in FRAMES:
        scene.frame_set(frame);bpy.context.view_layer.update()
        snapshots[str(frame)]={o.name:[v for row in o.matrix_world for v in row] for o in meshes}
        fixed_trees={o.name:tree(o) for o in fixed}
        for obj in movers:
            shape=tree(obj)
            for target in fixed:
                overlaps=shape.overlap(fixed_trees[target.name])
                if overlaps: collisions.append(dict(frame=frame,moving=obj.name,fixed=target.name,triangles=len(overlaps)))
        for index,obj in enumerate(movers):
            for target in movers[index+1:]:
                if obj.parent==target.parent: continue  # inset plate is intentionally embedded in its own shell
                overlaps=tree(obj).overlap(tree(target))
                if overlaps: collisions.append(dict(frame=frame,moving=obj.name,other_segment=target.name,triangles=len(overlaps)))
        assert all(geometry_bounds([obj])[2]>=-.001 for obj in meshes if not obj.name.startswith('RI10 shaft'))
        bounds=geometry_bounds(meshes)
        assert min(bounds[:2])>=-1.5 and max(bounds[3:5])<=1.5 and -2.05<bounds[2]<-1.9
    # A failed sweep is evidence requiring repair; never suppress it as intentional contact.
    assert not collisions,collisions[:20]
    assert snapshots['1']==snapshots['61'],'Cycle must return exactly to closed pose'
    for obj in fixed:
        assert all(snapshots[str(frame)][obj.name]==snapshots['1'][obj.name] for frame in FRAMES)
    assert any(snapshots['31'][obj.name]!=snapshots['1'][obj.name] for obj in movers)
    visibility={}
    for frame,visible in [(1,False),(31,True)]:
        scene.frame_set(frame);visibility[str(frame)]=indicator_visibility(meshes,visible)
        if visible: clear_shaft(meshes)
    scene.frame_set(1)
    return snapshots,dict(indicator_visibility=visibility,sampled_frames=FRAMES,moving_meshes=len(movers),fixed_meshes=len(fixed),surface_intersections=collisions)


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI10 | worn green casting',1024),('RI10 | worn planar casting caps',512)]:
        material=bpy.data.materials[name];shader=material.node_tree.nodes.get('Principled BSDF')
        texture=shader.inputs['Base Color'].links[0].from_node;colour=texture.image
        assert list(colour.size)==[size,size] and colour.packed_file
        rough=shader.inputs['Roughness'].links[0].from_node;channel=0
        if rough.type in ['SEPARATE_COLOR','SEPRGB']: channel=1;rough=rough.inputs[0].links[0].from_node
        assert rough.type=='TEX_IMAGE' and rough.image.packed_file
        evidence[name]=dict(colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in colour.pixels[:])).hexdigest(),
            roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    return evidence


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((Path(__file__).resolve().parents[2]/'docs/reconstruction/models/rigellian-ground-deck-mechanism.json').read_bytes()).hexdigest()==meta['functional_evidence_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    raw=(ROOT/'model.glb').read_bytes();length,kind=struct.unpack_from('<II',raw,12)
    assert kind==0x4e4f534a
    gltf=json.loads(raw[20:20+length]);clips=gltf['animations']
    assert len(clips)==1 and clips[0]['name']=='GroundDeckCoverCycle'
    channels=clips[0]['channels'];assert len(channels)==6
    assert all(channel['target']['path']=='translation' for channel in channels)
    targets={gltf['nodes'][channel['target']['node']]['name'] for channel in channels}
    assert targets=={'CoverLeft','CoverRight','CoverLeftInner','CoverLeftOuter','CoverRightInner','CoverRightOuter'}
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=asset_meshes(bpy.context.scene);native,sweep=inspect(meshes);textures=texture_evidence(meshes)
    assert len(meshes)==meta['mesh_objects'];materials=material_values(meshes)
    for image in bpy.data.images:
        if image.source=='FILE': assert image.packed_file and hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    camera=bpy.context.scene.camera;view=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    bpy.context.scene.frame_set(1);fit_camera(bpy.context.scene,surface_points(meshes),(0,-16,7))
    reference_camera=bpy.context.scene.camera
    reference_view=(reference_camera.location.copy(),reference_camera.rotation_euler.copy(),reference_camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'reference-facing.png')
    bpy.context.scene.frame_set(31);fit_camera(bpy.context.scene,surface_points(meshes),(0,0,20))
    top_camera=bpy.context.scene.camera
    top_view=(top_camera.location.copy(),top_camera.rotation_euler.copy(),top_camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'open-top.png')
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=asset_meshes(scene);other,imported_sweep=inspect(imported);assert texture_evidence(imported)==textures
    assert native.keys()==other.keys()
    error=max(abs(a-b) for frame in native for name in native[frame] for a,b in zip(native[frame][name],other[frame][name]))
    assert error<.00003,('Animation transform mismatch',error)
    imported_materials=material_values(imported);assert materials.keys()==imported_materials.keys()
    for name,value in materials.items():
        target=imported_materials[name];assert max(abs(a-b) for a,b in zip(value[0]+value[1:],target[0]+target[1:]))<1/255+.00001
    ground_mask()
    scene.camera.location=view[0];scene.camera.rotation_euler=view[1];scene.camera.data.ortho_scale=view[2]
    for frame,label in [(1,'front-quarter'),(16,'half-open'),(31,'open')]:
        scene.frame_set(frame);render_to(scene,ROOT/('imported-glb-'+label+'.png'))
    scene.camera.location=top_view[0];scene.camera.rotation_euler=top_view[1];scene.camera.data.ortho_scale=top_view[2]
    scene.frame_set(31);render_to(scene,ROOT/'imported-glb-open-top.png')
    scene.camera.location=reference_view[0];scene.camera.rotation_euler=reference_view[1];scene.camera.data.ortho_scale=reference_view[2]
    scene.frame_set(1);render_to(scene,ROOT/'imported-glb-reference-facing.png')
    report=dict(issue=980,revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        preview_helper_sha256=hashlib.sha256(Path(__file__).with_name('rigellian_shaft_preview.py').read_bytes()).hexdigest(),
        functional_evidence_sha256=meta['functional_evidence_sha256'],mesh_objects=len(meshes),materials=materials,native_sweep=sweep,imported_sweep=imported_sweep,
        maximum_native_imported_transform_error=error,animation_cycle_verified=True,glb_clip=dict(name=clips[0]['name'],channels=len(channels),targets=sorted(targets)),
        checks=['Native/imported topology, identity placement and catalogue footprint','Actual moving meshes and fixed-body hierarchy; preview ground mask excluded',
                'Rigid animation transforms at every integer frame in the 61-frame preview','Moving/fixed and separate moving-segment evaluated triangle intersection checks at 61 sampled poses',
                'Nine vertical rays prove an unobstructed deep shaft; wall lights visible only after opening','Authored packed image hashes and material values','Actual imported closed/intermediate/open rendering'],
        limitations=['Sampled poses do not prove continuous swept-volume clearance','Telescopic mechanism and preview timing are inferred','Final art, complete state composition and game integration remain open'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RI10_NATIVE_GLB_ANIMATION_OK',len(meshes),flush=True)


if __name__=='__main__': main()
