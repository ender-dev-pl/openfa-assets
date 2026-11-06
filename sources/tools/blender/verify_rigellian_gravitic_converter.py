"""Reopen RI13 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_gravitic_converter import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_gravitic_converter_parts import PROFILES,DENTS,PAINT,CENTRES,curve_shift
from manufactured_vessels import profile_radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI13 | weathered green alloy',1024),('RI13 | aged grey housing',1024),('RI13 | green planar caps',512),('RI13 | grey planar caps',512)]:
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
        if obj.name not in PROFILES: continue
        style=PAINT[obj.name];cx,cy=CENTRES[obj.name]
        vertices=[(obj.matrix_world @ v.co)-Vector((cx,cy+curve_shift(obj.name,(obj.matrix_world @ v.co).z),0)) for v in obj.data.vertices];low=min(p.z for p in vertices);high=max(p.z for p in vertices)
        radii={z:max(math.hypot(p.x,p.y) for p in vertices if abs(p.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[(obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co) for index in face.loop_indices]
            points=[point-Vector((cx,cy+curve_shift(obj.name,point.z),0)) for point in points]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI13 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name==('RI13 | weathered green alloy' if style=='green' else 'RI13 | aged grey housing')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-(point.z/4.2))<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==12
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==root for obj in meshes)
    for name,profile in PROFILES.items():
        body=bpy.data.objects[name];phi,z,depth=DENTS[name];normal=Vector((math.cos(phi),math.sin(phi),0));cx,cy=CENTRES[name]
        cy+=curve_shift(name,z)
        hit=ray(body,Vector((cx,cy,z))+normal*2,-normal)
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x-cx,hit.y-cy)<depth*1.45,(name,'Missing actual geometric dent')
    sphere=bpy.data.objects['RI13 spherical converter housing'];drum=bpy.data.objects['RI13 lower equipment drum']
    for a,b,z in [('RI13 flared ground foot','RI13 lower equipment drum',.81),('RI13 lower equipment drum','RI13 spherical converter housing',1.64),('RI13 spherical converter housing','RI13 segmented upper probe',2.86)]:
        assert ray(bpy.data.objects[a],(0,0,z),(1,0,0)) is not None and ray(bpy.data.objects[b],(0,0,z),(1,0,0)) is not None,(a,b,'No overlap at assembly joint')
    for side in [-1,1]:
        riser=bpy.data.objects[f'RI13 green side riser {side}'];pod=bpy.data.objects[f'RI13 side service pod {side}']
        for z in [1.95,2.15,2.35,2.55]:
            skin=ray(sphere,(side*.48,-2,z),(0,1,0)).y
            assert ray(riser,(side*.48,-2,z),(0,1,0)).y<skin<ray(riser,(side*.48,2,z),(0,-1,0)).y,'Riser must stay visible and rooted along sphere front'
        for i,z in enumerate([1.09,1.55]):
            support=bpy.data.objects[f'RI13 riser support {side} {i}']
            assert ray(support,(side*.48,-2,z),(0,1,0)).y<ray(riser,(side*.48,2,z),(0,-1,0)).y
            assert ray(drum,(side*.30,-2,z),(0,1,0)).y<ray(support,(side*.30,2,z),(0,-1,0)).y
        inset=bpy.data.objects[f'RI13 side red inset {side}']
        assert ray(inset,(side*.48,-2,1.23),(0,1,0)).y<ray(pod,(side*.48,-2,1.23),(0,1,0)).y<ray(inset,(side*.48,2,1.23),(0,-1,0)).y
    frame=bpy.data.objects['RI13 lower front panel frame'];panel=bpy.data.objects['RI13 lower front panel']
    for z in [1.10,1.28,1.46]:
        assert ray(frame,(.12,2,z),(0,-1,0)).y>ray(drum,(.12,-2,z),(0,1,0)).y
        assert ray(panel,(.12,2,z),(0,-1,0)).y>ray(frame,(.12,-2,z),(0,1,0)).y
    for i,x in enumerate([-.23,-.15,-.07]):
        bar=bpy.data.objects[f'RI13 lower front vertical stiffener {i}']
        for z in [1.12,1.28,1.44]:
            skin=ray(drum,(x,-2,z),(0,1,0)).y
            assert ray(bar,(x,-2,z),(0,1,0)).y<skin<ray(bar,(x,2,z),(0,-1,0)).y
    bezel=bpy.data.objects['RI13 spherical front fitting bezel'];face=bpy.data.objects['RI13 green front inspection face']
    normal=face.matrix_world.to_3x3() @ Vector((0,0,1));centre=face.matrix_world.translation
    tx=face.matrix_world.to_3x3() @ Vector((1,0,0));ty=face.matrix_world.to_3x3() @ Vector((0,1,0))
    for i in range(32):
        angle=i*math.tau/32;point=centre+.15*(tx*math.cos(angle)+ty*math.sin(angle))
        back=ray(bezel,point-normal*2,normal);front=ray(bezel,point+normal*2,-normal);skin=ray(sphere,point+normal*2,-normal)
        assert back is not None and front is not None and skin is not None
        assert back.dot(normal)<skin.dot(normal)<front.dot(normal),('Bezel root gap',i)
    assert ray(face,centre-normal*2,normal).dot(normal)<ray(bezel,centre+normal*2,-normal).dot(normal)<ray(face,centre+normal*2,-normal).dot(normal)
    foot=bpy.data.objects['RI13 flared ground foot'];foot_bezel=bpy.data.objects['RI13 foot service fitting bezel'];foot_face=bpy.data.objects['RI13 foot service fitting face']
    n=foot_face.matrix_world.to_3x3() @ Vector((0,0,1));c=foot_face.matrix_world.translation
    tx=foot_face.matrix_world.to_3x3() @ Vector((1,0,0));ty=foot_face.matrix_world.to_3x3() @ Vector((0,1,0))
    for i in range(32):
        a=i*math.tau/32;p=c+.09*(tx*math.cos(a)+ty*math.sin(a))
        back=ray(foot_bezel,p-n*2,n);front=ray(foot_bezel,p+n*2,-n);skin=ray(foot,p+n*2,-n)
        assert back is not None and front is not None and skin is not None
        assert back.dot(n)<skin.dot(n)<front.dot(n),'Foot fitting root gap'
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001
    assert abs(bounds[5]-4.10)<.001 and not any(obj.animation_data for obj in meshes)
    return bounds,audit()


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,name in [('generator_sha256','build_rigellian_gravitic_converter.py'),('parts_sha256','rigellian_gravitic_converter_parts.py')]:
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==meta[field]
    assert hashlib.sha256(Path(__file__).with_name('author_gravitic_converter_wear.py').read_bytes()).hexdigest()==wear['generator_sha256']
    for name,digest in meta['helper_sha256'].items():
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native,contacts=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes)
    transforms={obj.name:([list(row) for row in obj.matrix_world],geometry_bounds([obj])) for obj in meshes}
    assert len(meshes)==meta['mesh_objects'] and len(materials)==8
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==2
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    detail_target=Vector((0,0,2.25));offset=Vector((4,-10,7)).normalized()*20
    camera.location=detail_target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.65
    detail_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'body-detail.png')
    camera.location=Vector((0,0,.30))+offset;camera.data.ortho_scale=1.9
    base_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'base-detail.png')
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in scene.objects if obj.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    exported,imported_contacts=structure(imported);assert texture_evidence(imported)==textures
    assert {obj.name for obj in imported}==set(transforms)
    for obj in imported:
        matrix,bounds=transforms[obj.name]
        assert max(abs(obj.matrix_world[i][j]-matrix[i][j]) for i in range(4) for j in range(4))<1e-5
        assert max(abs(a-b) for a,b in zip(geometry_bounds([obj]),bounds))<.002
    imported_materials=material_values(imported);assert materials.keys()==imported_materials.keys()
    for name,value in materials.items():
        other=imported_materials[name]
        assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[0]+other[1:]))<1/255+.00001
    assert len(meshes)==len(imported) and max(abs(a-b) for a,b in zip(native,exported))<.002
    scene.camera.location=native_camera[0];scene.camera.rotation_euler=native_camera[1];scene.camera.data.ortho_scale=native_camera[2]
    render_to(scene,ROOT/'imported-glb-front-quarter.png')
    scene.camera.location=detail_camera[0];scene.camera.rotation_euler=detail_camera[1];scene.camera.data.ortho_scale=detail_camera[2]
    render_to(scene,ROOT/'imported-glb-body-detail.png')
    scene.camera.location=base_camera[0];scene.camera.rotation_euler=base_camera[1];scene.camera.data.ortho_scale=base_camera[2]
    render_to(scene,ROOT/'imported-glb-base-detail.png')
    report=dict(issue=985,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Foot/drum/sphere/probe overlap, sphere/riser and bracket/drum contacts; side insets and lower panel contacts',
                'Six measured geometric dents, 32 spherical fitting flange root contacts and embedded face',
                'Packed authored images, matching colour/roughness pixels and mapped UVs'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_GRAVITIC_CONVERTER_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
