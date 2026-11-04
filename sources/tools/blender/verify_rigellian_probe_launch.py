"""Reopen RI11 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_rigellian_cpu_contacts import audit
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from build_rigellian_probe_launch import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_probe_launch_parts import PROFILE,DENT
from manufactured_vessels import profile_radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI11 | aged jade shell',1024),('RI11 | worn planar end caps',512)]:
        material=bpy.data.materials[name];shader=material.node_tree.nodes.get('Principled BSDF')
        texture=shader.inputs['Base Color'].links[0].from_node;colour=texture.image
        assert list(colour.size)==[size,size] and colour.packed_file
        rough=shader.inputs['Roughness'].links[0].from_node;channel=0
        if rough.type in ['SEPARATE_COLOR','SEPRGB']: channel=1;rough=rough.inputs[0].links[0].from_node
        assert rough.type=='TEX_IMAGE' and rough.image.packed_file
        evidence[name]=dict(colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in colour.pixels[:])).hexdigest(),
            roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    cap_planes=0
    for obj in meshes:
        if not (obj.name in ['RI11 stepped launch housing']): continue
        vertices=[obj.matrix_world @ v.co for v in obj.data.vertices];low=min(p.z for p in vertices);high=max(p.z for p in vertices)
        radii={z:max(math.hypot(p.x,p.y) for p in vertices if abs(p.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name=='RI11 | worn planar end caps'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=='RI11 | aged jade shell'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/.75)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==2
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
    body=bpy.data.objects['RI11 stepped launch housing']
    liner=bpy.data.objects['RI11 embedded open port liner']
    floor=bpy.data.objects['RI11 recessed launch mechanism floor']
    # Actual centre rays must traverse the open port to its low floor.
    for x,y in [(0,0),(.08,0),(-.08,0),(0,-.08)]:
        hits=[(ray(obj,(x,y,2),(0,0,-1)),obj.name) for obj in meshes]
        hits=[(point.z,name) for point,name in hits if point is not None]
        z,name=max(hits)
        assert name==floor.name and .06<z<.07,(x,y,z,name)
    for i in range(8):
        angle=i*math.tau/8;normal=Vector((math.cos(angle),math.sin(angle),0));axis=Vector((0,0,.3))
        inner=ray(liner,axis,normal);outer=ray(liner,axis+normal*2,-normal)
        skin=ray(body,axis,normal)
        assert inner.dot(normal)<skin.dot(normal)<outer.dot(normal)
    for i in range(3):
        guide=bpy.data.objects[f'RI11 internal port guide {i}'];normal=guide.matrix_world.translation.copy();normal.z=0;normal.normalize()
        axis=Vector((0,0,.3))
        assert ray(guide,axis,normal).dot(normal)<ray(liner,axis,normal).dot(normal)<ray(guide,axis+normal*2,-normal).dot(normal)
        tangent=Vector((-normal.y,normal.x,0))
        track=bpy.data.objects[f'RI11 guide {i} recessed running track']
        for z in [.12,.3,.51]:
            axis=Vector((0,0,z))
            assert ray(track,axis,normal).dot(normal)<ray(guide,axis,normal).dot(normal)<ray(track,axis+normal*2,-normal).dot(normal),'Track must embed in guide web'
            for side in [-1,1]:
                strip=bpy.data.objects[f'RI11 guide {i} wear strip {side}'];point=axis+tangent*(side*.020)
                assert ray(strip,point,normal).dot(normal)<ray(guide,point,normal).dot(normal)<ray(strip,point+normal*2,-normal).dot(normal),'Wear strip must embed in guide web'
        assert ray(strip,axis+tangent*.020,normal).dot(normal)<ray(track,axis,normal).dot(normal),'Running track must sit behind wear-strip faces'
    assert ray(body,(2,0,.45),(-1,0,0)).x<.4,'Raised port collar must remain distinct from the broad lower shoulder'
    assert ray(body,(2,0,.29),(-1,0,0)).x>.7,'Lower shoulder must retain its broad stepped ledge'
    phi,z,depth=DENT;normal=Vector((math.cos(phi),math.sin(phi),0))
    hit=ray(body,normal*2+Vector((0,0,z)),-normal)
    assert depth*.7<profile_radius(PROFILE,z)-math.hypot(hit.x,hit.y)<depth*1.4
    bezel=bpy.data.objects['RI11 front fitting cast retaining bezel']
    face=bpy.data.objects['RI11 front brass inset fitting'];normal=face.matrix_world.to_3x3() @ Vector((0,0,1));centre=face.matrix_world.translation
    tx=face.matrix_world.to_3x3() @ Vector((1,0,0));ty=face.matrix_world.to_3x3() @ Vector((0,1,0))
    for i in range(32):
        angle=i*math.tau/32;point=centre+.09*(tx*math.cos(angle)+ty*math.sin(angle))
        back=ray(bezel,point-normal*2,normal);front=ray(bezel,point+normal*2,-normal);skin=ray(body,point+normal*2,-normal)
        assert back is not None and front is not None and skin is not None
        assert back.dot(normal)<skin.dot(normal)<front.dot(normal),('Bezel root gap',i)
    assert ray(face,centre-normal*2,normal).dot(normal)<ray(bezel,centre+normal*2,-normal).dot(normal)<ray(face,centre+normal*2,-normal).dot(normal)
    for i in range(4):
        screw=bpy.data.objects[f'RI11 front fitting captive screw {i}'];point=screw.matrix_world.translation
        assert ray(screw,point-normal*2,normal).dot(normal)<ray(bezel,point+normal*2,-normal).dot(normal)<ray(screw,point+normal*2,-normal).dot(normal)
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,audit()


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,name in [('generator_sha256','build_rigellian_probe_launch.py'),('parts_sha256','rigellian_probe_launch_parts.py')]:
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==meta[field]
    assert hashlib.sha256(Path(__file__).with_name('author_probe_launch_wear.py').read_bytes()).hexdigest()==wear['generator_sha256']
    for name,digest in meta['helper_sha256'].items():
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native,contacts=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes)
    assert len(meshes)==meta['mesh_objects'] and len(materials)==6
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==2
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    detail_target=Vector((0,0,.48));offset=Vector((4,-10,7)).normalized()*20
    camera.location=detail_target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.62
    detail_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'port-detail.png')
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in scene.objects if obj.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    exported,imported_contacts=structure(imported);assert texture_evidence(imported)==textures
    imported_materials=material_values(imported);assert materials.keys()==imported_materials.keys()
    for name,value in materials.items():
        other=imported_materials[name]
        assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[0]+other[1:]))<1/255+.00001
    assert len(meshes)==len(imported) and max(abs(a-b) for a,b in zip(native,exported))<.002
    scene.camera.location=native_camera[0];scene.camera.rotation_euler=native_camera[1];scene.camera.data.ortho_scale=native_camera[2]
    render_to(scene,ROOT/'imported-glb-front-quarter.png')
    scene.camera.location=detail_camera[0];scene.camera.rotation_euler=detail_camera[1];scene.camera.data.ortho_scale=detail_camera[2]
    render_to(scene,ROOT/'imported-glb-port-detail.png')
    report=dict(issue=982,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Open port centre rays, embedded liner and three attached flat channel guides; track/strip contact rays at three heights',
                'Measured geometric dent, 32 bezel perimeter root contacts and embedded fitting/screws',
                'Packed authored images, matching colour/roughness pixels and mapped UVs'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_PROBE_LAUNCH_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
