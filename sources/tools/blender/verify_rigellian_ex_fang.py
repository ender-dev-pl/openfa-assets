"""Reopen RI22 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_ex_fang import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_ex_fang_parts import PROFILES,DENTS,PAINT,CENTRES,PIVOT,FEED_TIP,DISH_AXIS,MOVING,RADIUS,DEPTH,THICKNESS,DISH_CENTER,surface_z
from manufactured_vessels import profile_radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI22 | weathered green armour',1024),('RI22 | green planar caps',512),('RI22 | aged copper feed',1024),('RI22 | bronze planar caps',512)]:
        material=bpy.data.materials[name];shader=material.node_tree.nodes.get('Principled BSDF')
        texture=shader.inputs['Base Color'].links[0].from_node;colour=texture.image
        assert list(colour.size)==[size,size] and colour.packed_file
        rough=shader.inputs['Roughness'].links[0].from_node;channel=0
        if rough.type in ['SEPARATE_COLOR','SEPRGB']: channel=1;rough=rough.inputs[0].links[0].from_node
        assert rough.type=='TEX_IMAGE' and rough.image.packed_file
        evidence[name]=dict(colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in colour.pixels[:])).hexdigest(),
            roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    plate_uv=False
    cap_planes=0
    for obj in meshes:
        if obj.name not in PAINT: continue
        style=PAINT[obj.name];cx,cy=CENTRES[obj.name]
        if obj.name=='RI22 concave collector shell':
            uv=obj.data.uv_layers.active
            for face in obj.data.polygons:
                assert obj.data.materials[face.material_index].name=='RI22 | green planar caps'
                for index in face.loop_indices:
                    p=obj.data.vertices[obj.data.loops[index].vertex_index].co;u,v=uv.data[index].uv
                    assert abs(u-(.5+p.x/(2*RADIUS)))<1e-5 and abs(v-(.5+p.y/(2*RADIUS)))<1e-5
            plate_uv=True;continue
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
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI22 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name==('RI22 | weathered green armour' if style=='green' else 'RI22 | aged copper feed')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/3.0)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==6 and plate_uv
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes,collector_planar_uv=plate_uv)


def rigid_yaw(meshes):
    from mathutils import Matrix,Quaternion
    root=bpy.data.objects['PlacementRoot'];yaw=bpy.data.objects['YawPivot'];socket=bpy.data.objects['CollectorAxisSocket'];lance=bpy.data.objects['RI22 copper collector feed']
    assert yaw.parent==root and socket.parent==yaw
    assert (yaw.location-PIVOT).length<1e-5 and socket['forward_axis']=='local +Z'
    fixed={obj.name:geometry_bounds([obj]) for obj in meshes if obj.name not in MOVING};evidence=[]
    yaw.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        yaw.rotation_quaternion=Quaternion((0,0,1),angle);bpy.context.view_layer.update();rotation=Matrix.Rotation(angle,3,'Z')
        expected=PIVOT+rotation @ (FEED_TIP-PIVOT);forward=(socket.matrix_world.to_3x3() @ Vector((0,0,1))).normalized()
        assert (socket.matrix_world.translation-expected).length<1e-4,('Tip socket moved incorrectly',angle,list(socket.matrix_world.translation),list(expected))
        assert (lance.matrix_world @ Vector((0,0,.40))-expected).length<1e-4,'Lance tip separated from socket'
        assert (forward-rotation @ DISH_AXIS).length<1e-4,'Socket forward axis differs'
        for name,bounds in fixed.items(): assert max(abs(a-b) for a,b in zip(geometry_bounds([bpy.data.objects[name]]),bounds))<1e-6,'Fixed base moved with turret'
        evidence.append(dict(yaw_degrees=round(math.degrees(angle)),socket=list(socket.matrix_world.translation),forward=list(forward)))
    yaw.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    return evidence


def inside(obj,p):
    n=Vector((.173,.291,.941)).normalized();near=ray(obj,p-n*3,n);far=ray(obj,p+n*3,-n)
    return near is not None and far is not None and near.dot(n)<p.dot(n)<far.dot(n)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot'];yaw=bpy.data.objects['YawPivot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==(yaw if obj.name in MOVING else root) for obj in meshes)
    for name,profile in PROFILES.items():
        obj=bpy.data.objects[name];phi,z,depth=DENTS[name];n=Vector((math.cos(phi),math.sin(phi),0))
        hit=ray(obj,obj.matrix_world @ (Vector((0,0,z))+n*2),-(obj.matrix_world.to_3x3() @ n));hit=obj.matrix_world.inverted() @ hit
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x,hit.y)<depth*1.45,(name,'Geometric dent missing')
    dish=bpy.data.objects['RI22 concave collector shell'];matrix=dish.matrix_world;inverse=matrix.inverted();axis=matrix.to_3x3() @ Vector((0,0,1))
    samples=[]
    for x,y in [(.015,.010),(.31,.12),(.62,.013)]:
        front=inverse @ ray(dish,matrix @ Vector((x,y,.8)),-axis);back=inverse @ ray(dish,matrix @ Vector((x,y,-.6)),axis)
        assert abs(front.z-surface_z(x,y))<.0006,'Collector front profile differs'
        assert abs(front.z-back.z-THICKNESS)<.0001,'Collector shell thickness differs'
        samples.append(front.z)
    assert samples[2]>samples[0]+.10,'Collector must be concave, not a flat disc'
    x,y=.359,.001;front=inverse @ ray(dish,matrix @ Vector((x,y,.8)),-axis)
    difference=DEPTH*(x*x+y*y)/(RADIUS*RADIUS)-front.z
    assert .0013<difference<.0028,'Collector geometric dent missing'
    base=bpy.data.objects['RI22 fixed green pedestal'];head=bpy.data.objects['RI22 green yaw housing'];bearing=bpy.data.objects['RI22 static yaw bearing']
    for a,b,z in [(base,bearing,.58),(bearing,head,.61)]:
        assert ray(a,(0,0,z),(1,0,0)) is not None and ray(b,(0,0,z),(1,0,0)) is not None,'Yaw joint missing'
    end=DISH_CENTER-DISH_AXIS*.02
    for name,start in [('RI22 inclined green support',Vector((0,0,.75))),('RI22 copper rear support',Vector((.10,0,.76)))]:
        support=bpy.data.objects[name];direction=(end-start).normalized()
        assert inside(support,start+direction*.02) and inside(head,start+direction*.02),'Support/head gap'
        assert inside(support,end-direction*.003) and inside(dish,end-direction*.003),'Support/shell gap'
    feed=bpy.data.objects['RI22 copper collector feed']
    assert inside(feed,feed.matrix_world @ Vector((0,0,.004))) and inside(dish,feed.matrix_world @ Vector((0,0,.004))),'Collector feed must be rooted at shell apex'
    for side in [-1,1]:
        cap=bpy.data.objects[f'RI22 copper yoke cap {side}'];n=Vector((side,0,0));c=cap.matrix_world.translation
        assert ray(cap,c-n*2,n).dot(n)<ray(head,c+n*2,-n).dot(n)<ray(cap,c+n*2,-n).dot(n)
    for i in range(4):
        bolt=bpy.data.objects[f'RI22 collector fastener {i}'];c=bolt.matrix_world.translation;n=bolt.matrix_world.to_3x3() @ Vector((0,0,1))
        tx=bolt.matrix_world.to_3x3() @ Vector((1,0,0));ty=bolt.matrix_world.to_3x3() @ Vector((0,1,0))
        for x,y in [(0,0),(.008,0),(-.008,0),(0,.008),(0,-.008)]:
            p=c+tx*x+ty*y;skin=ray(dish,p+n*2,-n).dot(n)
            assert ray(bolt,p-n*2,n).dot(n)<skin<ray(bolt,p+n*2,-n).dot(n),'Collector fastener gap'
    for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6]):
        inset=bpy.data.objects[f'RI22 lower base inset {i}'];n=Vector((math.cos(phi),math.sin(phi),0))
        for z in [.08,.18,.29]:
            o=Vector((0,0,z));skin=ray(base,o+n*2,-n).dot(n)
            assert ray(inset,o,n).dot(n)<skin<ray(inset,o+n*2,-n).dot(n)
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-2 and max(bounds[3:5])<=2 and abs(bounds[2])<.001 and 1.70<bounds[5]<2.05
    assert not any(obj.animation_data for obj in meshes)
    return bounds,dict(contact_samples=audit(),collector_surface_samples=samples,rigid_yaw=rigid_yaw(meshes))


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,name in [('generator_sha256','build_rigellian_ex_fang.py'),('parts_sha256','rigellian_ex_fang_parts.py')]:
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==meta[field]
    assert hashlib.sha256(Path(__file__).with_name('author_ex_fang_wear.py').read_bytes()).hexdigest()==wear['generator_sha256']
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
    assert len(meshes)==meta['mesh_objects'] and len(materials)==9
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==4
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    detail_target=Vector((0,.15,1.15));offset=Vector((4,-10,7)).normalized()*20
    camera.location=detail_target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.6
    detail_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'collector-detail.png')
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
    render_to(scene,ROOT/'imported-glb-collector-detail.png')
    scene.camera.location=base_camera[0];scene.camera.rotation_euler=base_camera[1];scene.camera.data.ortho_scale=base_camera[2]
    render_to(scene,ROOT/'imported-glb-base-detail.png')
    report=dict(issue=994,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Concave closed shell/thickness, support/yoke/feed/fastener contacts and fitted base insets',
                'Four geometric dents; yaw hierarchy and collector-axis socket at four orientations in native/imported assets',
                'Packed authored images, matching colour/roughness pixels and mapped UVs'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_EX_FANG_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
