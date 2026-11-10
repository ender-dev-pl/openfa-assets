"""RI23 latest segmented foot plus unchanged upper details and two-tip yaw rig."""
import hashlib
import math
import bpy
from mathutils import Matrix,Quaternion,Vector
from verify_refined_rigellian_lance_base import structure as refined_structure
from verify_rigellian_ultrathermal_lance import PROFILES,DENTS,PAINT,CENTRES,profile_radius,ray,inside,geometry_bounds
from rigellian_ultrathermal_lance_parts import PIVOT,LANCE_TIPS,LANCE_AXIS,MOVING
from refine_rigellian_lance_base import PROFILE as SKIRT_PROFILE
from audit_rigellian_cpu_contacts import audit
from repair_detail_uvs import verify_detail_uvs


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI23 | weathered green armour',1024),('RI23 | green planar caps',512),('RI23 | aged bronze fittings',1024),('RI23 | bronze planar caps',512),('RI23 | worn recessed bronze skirt',512)]:
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
        if obj.name not in PAINT or obj.name=='RI23 fixed bronze skirt': continue
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
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI23 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name==('RI23 | weathered green armour' if style=='green' else 'RI23 | aged bronze fittings')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/3.0)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    verify_detail_uvs(meshes)
    assert cap_planes==8
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def textures():
    return texture_evidence([o for o in bpy.context.scene.objects if o.type=='MESH'])


def yaw_pose(angle):
    yaw = bpy.data.objects['YawPivot']
    yaw.rotation_mode = 'QUATERNION'
    yaw.rotation_quaternion = Quaternion((0,0,1),angle)
    bpy.context.view_layer.update()


def upper_details():
    dents = []
    for name,profile in PROFILES.items():
        if name=='RI23 fixed bronze skirt':
            continue
        obj = bpy.data.objects[name]
        phi,z,depth = DENTS[name]
        n = Vector((math.cos(phi),math.sin(phi),0))
        hit = ray(obj,obj.matrix_world@(Vector((0,0,z))+n*2),-(obj.matrix_world.to_3x3()@n))
        local = obj.matrix_world.inverted()@hit
        actual = profile_radius(profile,z)-math.hypot(local.x,local.y)
        assert depth*.65<actual<depth*1.45,(name,actual)
        dents.append(dict(name=name,depth=actual))
    skirt = bpy.data.objects['RI23 fixed bronze skirt']
    n = Vector((math.cos(-2.2),math.sin(-2.2),0))
    hit = ray(skirt,n*2+Vector((0,0,.13)),-n)
    depth = profile_radius(SKIRT_PROFILE,.13)-math.hypot(hit.x,hit.y)
    assert .0008<depth<.003,(skirt.name,depth)
    dents.append(dict(name=skirt.name,depth=depth))
    base = bpy.data.objects['RI23 fixed green pedestal']
    spur = bpy.data.objects['RI23 fixed green spur']
    p = Vector((.14,.071,.755))
    assert inside(base,p) and inside(spur,p)
    bezel = bpy.data.objects['RI23 base fitting bezel']
    face = bpy.data.objects['RI23 bronze base fitting']
    n = face.matrix_world.to_3x3()@Vector((0,0,1))
    c = face.matrix_world.translation
    tx,ty = [face.matrix_world.to_3x3()@Vector(v) for v in [(1,0,0),(0,1,0)]]
    for i in range(32):
        angle = i*math.tau/32
        p = c+.078*(tx*math.cos(angle)+ty*math.sin(angle))
        back,front,skin = ray(bezel,p-n*2,n),ray(bezel,p+n*2,-n),ray(base,p+n*2,-n)
        assert back is not None and front is not None and skin is not None
        assert back.dot(n)<skin.dot(n)<front.dot(n)
    assert ray(face,c-n*2,n).dot(n)<ray(bezel,c+n*2,-n).dot(n)<ray(face,c+n*2,-n).dot(n)
    strip = bpy.data.objects['RI23 bronze front strip']
    for z in [.32,.50,.75]:
        n = Vector((0,-1,0));o = Vector((0,0,z))
        skin = ray(base,n*2+o,-n).dot(n)
        assert ray(strip,o,n).dot(n)<skin<ray(strip,n*2+o,-n).dot(n)
    assert not any(o.name.startswith('RI23 lower base inset') for o in bpy.context.scene.objects)
    return dict(measured_dents=dents,spur_root_and_front_strip_seated=True,front_fitting_root_samples=32)


def structure():
    yaw_pose(0)
    form = refined_structure()
    details = upper_details()
    meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(meshes)==22
    maps = textures()
    contacts = audit()
    assert len(contacts['components'])==1
    fixed = {o.name:o.matrix_world.copy() for o in meshes if o.name not in MOVING}
    poses = []
    maximum = 0.0
    separation = (LANCE_TIPS[-1]-LANCE_TIPS[1]).length
    for index in range(16):
        angle = index*math.tau/16
        yaw_pose(angle)
        rotation = Matrix.Rotation(angle,3,'Z')
        tips = {}
        for side,tip in LANCE_TIPS.items():
            socket = bpy.data.objects['LanceTipSocket '+str(side)]
            lance = bpy.data.objects['RI23 bronze lance '+str(side)]
            expected = PIVOT+rotation@(tip-PIVOT)
            forward = (socket.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
            error = max((socket.matrix_world.translation-expected).length,(forward-rotation@LANCE_AXIS).length,(lance.matrix_world@Vector((0,0,.95))-expected).length)
            assert error<1e-5,(index,side,error)
            projections = [(lance.matrix_world@v.co-expected).dot(forward) for v in lance.data.vertices]
            assert abs(max(projections))<1e-4 and min(projections)<-.90
            tips[str(side)] = dict(position=list(socket.matrix_world.translation),forward=list(forward))
            maximum = max(maximum,error)
        actual = (Vector(tips['-1']['position'])-Vector(tips['1']['position'])).length
        assert abs(actual-separation)<1e-5 and actual>.35
        for name,matrix in fixed.items():
            assert max(abs(matrix[i][j]-bpy.data.objects[name].matrix_world[i][j]) for i in range(4) for j in range(4))<1e-6
        poses.append(dict(index=index,authored_yaw_degrees=index*22.5,tip_sockets=tips,tip_separation=actual,moving_world_matrices={name:[float(v) for row in bpy.data.objects[name].matrix_world for v in row] for name in MOVING},fixed_base_unchanged=True))
    yaw_pose(0)
    return dict(positive_closed_meshes=len(meshes),body_bounds=geometry_bounds(meshes),retained_refined_foot=form,retained_upper_details=details,sampled_contact_graph=contacts,texture_pixels_and_uvs=maps,yaw_validation=dict(poses=poses,maximum_socket_error=maximum,fixed_base_unchanged=True,model_yaw_phase_sign_calibrated=False,continuous_collision_sweep_proven=False))
