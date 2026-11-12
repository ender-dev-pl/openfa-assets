"""RI17 retained open body, fittings, maps and current three-prong crown."""
import hashlib
import math
import bpy
import bmesh
from mathutils import Vector
from verify_rigellian_arms_unit import (PROFILES,DENTS,PAINT,CENTRES,CASING,CASING_DENT,profile_radius,ray,geometry_bounds,audit)
from verify_rigellian_crowns import form


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI17 | aged grey casing',1024),('RI17 | weathered green fittings',1024)]+[(f'RI17 | {style} planar caps',512) for style in ['grey','green']]:
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
        vertices=[(obj.matrix_world @ v.co)-Vector((cx,cy,0)) for v in obj.data.vertices];low=min(p.z for p in vertices);high=max(p.z for p in vertices)
        radii={z:max(math.hypot(p.x,p.y) for p in vertices if abs(p.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[(obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co)-Vector((cx,cy,0)) for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI17 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=={'bronze':'RI17 | aged bronze head','grey':'RI17 | aged grey casing','green':'RI17 | weathered green fittings'}[style]
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/3.0)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==6
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def retained_body_structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==root for obj in meshes)
    for name,profile in PROFILES.items():
        if name == 'RI17 bronze mast head': continue
        phi,z,depth=DENTS[name];n=Vector((math.cos(phi),math.sin(phi),0));cx,cy=CENTRES[name]
        hit=ray(bpy.data.objects[name],Vector((cx,cy,z))+n*2,-n)
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x-cx,hit.y-cy)<depth*1.45,(name,'Geometric dent missing')
    casing=bpy.data.objects['RI17 annular factory casing'];floor=bpy.data.objects['RI17 recessed assembly floor']
    phi,z,depth=CASING_DENT;n=Vector((math.cos(phi),math.sin(phi),0));hit=ray(casing,n*2+Vector((0,0,z)),-n)
    radius=profile_radius([(z,outer) for z,outer,_ in CASING],z)
    assert depth*.65<radius-math.hypot(hit.x,hit.y)<depth*1.45,'Casing dent missing'
    assert ray(casing,(2,0,.12),(-1,0,0)).x>ray(floor,(0,0,.12),(1,0,0)).x>ray(casing,(0,0,.12),(1,0,0)).x
    for x,y in [(-.10,-.15),(.0,-.20),(.20,-.15)]:
        assert ray(casing,(x,y,3),(0,0,-1)) is None,'Factory recess must remain open'
        assert abs(ray(floor,(x,y,3),(0,0,-1)).z-.14)<.001
    pillar=bpy.data.objects['RI17 green interior unit']
    assert ray(pillar,(.12,0,.13),(1,0,0)) is not None and ray(floor,(.12,0,.13),(1,0,0)) is not None
    mast=bpy.data.objects['RI17 green mast'];head=bpy.data.objects['RI17 refined crown central stem']
    assert ray(mast,(-.55,-.5,1.45),(1,0,0)) is not None and ray(head,(-.55,-.5,1.45),(1,0,0)) is not None
    assert ray(casing,(-2,-.5,.4),(1,0,0)).x<-.55<ray(casing,(2,-.5,.4),(-1,0,0)).x
    for i in range(12):
        phi=i*math.tau/12;n=Vector((math.cos(phi),math.sin(phi),0));o=Vector((0,0,.15));rib=bpy.data.objects[f'RI17 underside rib {i}']
        assert max(ray(casing,o,n).dot(n),ray(rib,o,n).dot(n))<min(ray(casing,n*2+o,-n).dot(n),ray(rib,n*2+o,-n).dot(n)),'Underside rib gap'
    frame=bpy.data.objects['RI17 red panel retaining frame'];panel=bpy.data.objects['RI17 red inner wall panel']
    for z in [.30,.42,.54]:
        wall=ray(casing,(-.22,0,z),(0,1,0)).y
        assert ray(frame,(-.22,2,z),(0,-1,0)).y>wall
        assert ray(panel,(-.22,0,z),(0,1,0)).y<wall
        assert ray(panel,(-.22,2,z),(0,-1,0)).y>ray(frame,(-.22,0,z),(0,1,0)).y
    bezel=bpy.data.objects['RI17 front roof fitting bezel'];face=bpy.data.objects['RI17 front roof fitting face'];c=face.matrix_world.translation;n=Vector((0,0,1))
    for i in range(32):
        a=i*math.tau/32;p=c+Vector((.078*math.cos(a),.078*math.sin(a),0))
        back=ray(bezel,p-n*2,n);front=ray(bezel,p+n*2,-n);skin=ray(casing,p+n*2,-n)
        assert back is not None and front is not None and skin is not None
        assert back.z<skin.z<front.z,'Roof fitting flange gap'
    assert ray(face,c-n*2,n).z<ray(bezel,c+n*2,-n).z<ray(face,c+n*2,-n).z
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-1.5 and max(bounds[3:5])<=1.5 and abs(bounds[2])<.001 and abs(bounds[5]-2.32)<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,audit()


def structure():
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
            assert all(edge.is_manifold for edge in bm.edges), obj.name
            assert bm.calc_volume(signed=True) > 0, obj.name
        finally:
            bm.free()
    bounds, contacts = retained_body_structure(meshes)
    assert len(contacts['components']) == 1
    crown = form('ri17')
    centre = Vector((-.55,-.5,1.445))
    middle = bpy.data.objects['RI17 refined crown central stem']
    for side, sign in [('left',-1),('right',1)]:
        n = Vector((sign,0,0))
        arm = bpy.data.objects['RI17 refined crown arm '+side]
        near = ray(arm,centre,n)
        far = ray(middle,centre+n*2,-n)
        assert near is not None and far is not None and near.dot(n)<far.dot(n)
    textures = texture_evidence(meshes)
    material = bpy.data.materials['Rigellian refined crown | aged conductor brass']
    shader = material.node_tree.nodes.get('Principled BSDF')
    pair = {}
    for socket, key in [('Base Color','colour'),('Roughness','roughness')]:
        node = shader.inputs[socket].links[0].from_node
        channel = None if key == 'colour' else 0
        if node.type in ['SEPARATE_COLOR','SEPRGB']:
            channel = 1
            node = node.inputs[0].links[0].from_node
        assert node.type == 'TEX_IMAGE'
        image = node.image
        assert image.packed_file and list(image.size)==[256,256]
        values = image.pixels[:] if channel is None else image.pixels[:][channel::4]
        pair[key] = hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in values)).hexdigest()
    textures['materials'][material.name] = pair
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=True, crown=crown,
                open_recess_floor_interior_red_panel_ribs_and_three_body_dents=True,
                three_crown_roots_overlap=True, texture_pixels_and_uvs=textures,
                contact_scope='Retained local attachment rays plus crown-root rays and sampled contact graph; not exhaustive intersection proof.')
