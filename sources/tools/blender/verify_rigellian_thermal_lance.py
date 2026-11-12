"""Reopen RI19 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_thermal_lance import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_thermal_lance_parts import PROFILES,DENTS,PAINT,CENTRES,PIVOT,LANCE_TIP,LANCE_AXIS,MOVING
from manufactured_vessels import profile_radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI19 | weathered green armour',1024),('RI19 | green planar caps',512)]:
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
        if obj.name not in PAINT: continue
        style=PAINT[obj.name];cx,cy=CENTRES[obj.name]
        vertices=[v.co for v in obj.data.vertices];low=min(p.z for p in vertices);high=max(p.z for p in vertices)
        radii={z:max(math.hypot(p.x,p.y) for p in vertices if abs(p.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI19 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=='RI19 | weathered green armour'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/3.0)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==6
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def rigid_yaw(meshes):
    from mathutils import Matrix,Quaternion
    root=bpy.data.objects['PlacementRoot'];yaw=bpy.data.objects['YawPivot'];socket=bpy.data.objects['LanceTipSocket'];lance=bpy.data.objects['RI19 tapered thermal lance']
    assert yaw.parent==root and socket.parent==yaw
    assert (yaw.location-PIVOT).length<1e-5 and socket['forward_axis']=='local +Z'
    fixed={obj.name:geometry_bounds([obj]) for obj in meshes if obj.name not in MOVING};evidence=[]
    yaw.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        yaw.rotation_quaternion=Quaternion((0,0,1),angle);bpy.context.view_layer.update();rotation=Matrix.Rotation(angle,3,'Z')
        expected=PIVOT+rotation @ (LANCE_TIP-PIVOT);forward=(socket.matrix_world.to_3x3() @ Vector((0,0,1))).normalized()
        assert (socket.matrix_world.translation-expected).length<1e-4,('Tip socket moved incorrectly',angle,list(socket.matrix_world.translation),list(expected))
        assert (lance.matrix_world @ Vector((0,0,.90))-expected).length<1e-4,'Lance tip separated from socket'
        assert (forward-rotation @ LANCE_AXIS).length<1e-4,'Socket forward axis differs'
        for name,bounds in fixed.items(): assert max(abs(a-b) for a,b in zip(geometry_bounds([bpy.data.objects[name]]),bounds))<1e-6,'Fixed base moved with turret'
        evidence.append(dict(yaw_degrees=round(math.degrees(angle)),socket=list(socket.matrix_world.translation),forward=list(forward)))
    yaw.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    return evidence


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot'];yaw=bpy.data.objects['YawPivot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==(yaw if obj.name in MOVING else root) for obj in meshes)
    for name,profile in PROFILES.items():
        obj=bpy.data.objects[name];phi,z,depth=DENTS[name];n=Vector((math.cos(phi),math.sin(phi),0));local=Vector((0,0,z))+n*2
        hit=ray(obj,obj.matrix_world @ local,-(obj.matrix_world.to_3x3() @ n));hit=obj.matrix_world.inverted() @ hit
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x,hit.y)<depth*1.45,(name,'Geometric dent missing')
    base=bpy.data.objects['RI19 fixed green pedestal'];head=bpy.data.objects['RI19 rotating green head'];bearing=bpy.data.objects['RI19 static yaw bearing'];lance=bpy.data.objects['RI19 tapered thermal lance']
    for a,b,z in [(base,bearing,.98),(bearing,head,1.015)]:
        assert ray(a,(0,0,z),(1,0,0)) is not None and ray(b,(0,0,z),(1,0,0)) is not None,'Yaw bearing joint missing'
    assert ray(head,lance.matrix_world.translation,LANCE_AXIS) is not None,'Lance root must enter head'
    for body_name,bezel_name,face_name,radius in [('RI19 fixed green pedestal','RI19 base fitting bezel','RI19 bronze base fitting',.078),('RI19 rotating green head','RI19 head fitting bezel','RI19 bronze head fitting',.061)]:
        body=bpy.data.objects[body_name];bezel=bpy.data.objects[bezel_name];face=bpy.data.objects[face_name];n=face.matrix_world.to_3x3() @ Vector((0,0,1));c=face.matrix_world.translation
        tx=face.matrix_world.to_3x3() @ Vector((1,0,0));ty=face.matrix_world.to_3x3() @ Vector((0,1,0))
        for i in range(32):
            a=i*math.tau/32;p=c+radius*(tx*math.cos(a)+ty*math.sin(a))
            back=ray(bezel,p-n*2,n);front=ray(bezel,p+n*2,-n);skin=ray(body,p+n*2,-n)
            assert back is not None and front is not None and skin is not None
            assert back.dot(n)<skin.dot(n)<front.dot(n),(bezel_name,'Flange root gap',i)
        assert ray(face,c-n*2,n).dot(n)<ray(bezel,c+n*2,-n).dot(n)<ray(face,c+n*2,-n).dot(n)
    for name,phi,heights in [('RI19 bronze front strip',-math.pi/2,[.30,.50,.75])]+[(f'RI19 lower base inset {i}',phi,[.08,.15,.23]) for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6])]:
        n=Vector((math.cos(phi),math.sin(phi),0));strip=bpy.data.objects[name]
        for z in heights:
            o=Vector((0,0,z));skin=ray(base,n*2+o,-n).dot(n)
            assert ray(strip,o,n).dot(n)<skin<ray(strip,n*2+o,-n).dot(n),'Fitted base strip gap'
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-1.5 and max(bounds[3:5])<=1.5 and abs(bounds[2])<.001 and 1.70<bounds[5]<1.90
    assert not any(obj.animation_data for obj in meshes)
    return bounds,dict(contact_samples=audit(),rigid_yaw=rigid_yaw(meshes))


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,name in [('generator_sha256','build_rigellian_thermal_lance.py'),('parts_sha256','rigellian_thermal_lance_parts.py')]:
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==meta[field]
    assert hashlib.sha256(Path(__file__).with_name('author_thermal_lance_wear.py').read_bytes()).hexdigest()==wear['generator_sha256']
    for name,digest in meta['helper_sha256'].items():
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    repo=Path(__file__).resolve().parents[2]
    for field,name in [('reference_sha256','rigellian-building-references.json'),('functional_source_sha256','functional-text-index.json')]:
        assert hashlib.sha256((repo/'docs/reconstruction/models'/name).read_bytes()).hexdigest()==meta[field]
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native,contacts=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes)
    transforms={obj.name:([list(row) for row in obj.matrix_world],geometry_bounds([obj])) for obj in meshes}
    assert len(meshes)==meta['mesh_objects'] and len(materials)==5
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==3
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    detail_target=Vector((0,0,1.16));offset=Vector((4,-10,7)).normalized()*20
    camera.location=detail_target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.05
    detail_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'turret-detail.png')
    camera.location=Vector((0,0,.40))+offset;camera.data.ortho_scale=1.2
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
    render_to(scene,ROOT/'imported-glb-turret-detail.png')
    scene.camera.location=base_camera[0];scene.camera.rotation_euler=base_camera[1];scene.camera.data.ortho_scale=base_camera[2]
    render_to(scene,ROOT/'imported-glb-base-detail.png')
    report=dict(issue=991,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Fixed base, yaw bearing/head/lance contacts, fitted base strips and 64 fitting-root samples',
                'Three geometric dents; yaw hierarchy and tip socket at four orientations in native and imported assets',
                'Packed authored images, matching colour/roughness pixels and mapped UVs'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_THERMAL_LANCE_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
