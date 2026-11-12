"""RI18 fixed anatomy, authored maps, floor seating and compact hinge contacts."""
import hashlib
import math
import bpy
import bmesh
from mathutils import Vector
from verify_rigellian_missile_launcher import (PAINT,CENTRES,ANNULI,ANNULUS_DENTS,ATTACHMENT_START,ATTACHMENT_END,profile_radius,ray,geometry_bounds)
from audit_rigellian_launcher_source import tree


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI18 | aged bronze foundation',1024),('RI18 | weathered green casing',1024)]+[(f'RI18 | {style} planar caps',512) for style in ['bronze','green']]:
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
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI18 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=={'bronze':'RI18 | aged bronze foundation','green':'RI18 | weathered green casing'}[style]
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/3.0)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==4
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def inside(obj,point):
    direction = Vector((.173,.291,.941)).normalized()
    hit,normal,_,_ = tree(obj).ray_cast(Vector(point),direction,10)
    return hit is not None and normal.dot(direction)>0


def structure():
    meshes = [obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
            assert all(e.is_manifold for e in bm.edges),obj.name
            assert bm.calc_volume(signed=True)>0,obj.name
        finally:
            bm.free()
    root = bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    base = bpy.data.objects['RI18 bronze foundation drum']
    upper = bpy.data.objects['RI18 stepped green silo casing']
    floor = bpy.data.objects['Recessed launch well floor']
    ring = bpy.data.objects['RI18 low silo floor']
    for name,rows in ANNULI.items():
        phi,z,depth = ANNULUS_DENTS[name]
        n = Vector((math.cos(phi),math.sin(phi),0))
        hit = ray(bpy.data.objects[name],n*2+Vector((0,0,z)),-n)
        radius = profile_radius([(z,outer) for z,outer,_ in rows],z)
        assert depth*.65<radius-math.hypot(hit.x,hit.y)<depth*1.45
    for x,y in [(0,0),(.10,0),(-.10,0),(0,.10),(0,-.10)]:
        assert ray(base,(x,y,3),(0,0,-1)) is None
        assert ray(upper,(x,y,3),(0,0,-1)) is None
        assert abs(ray(floor,(x,y,3),(0,0,-1)).z-.05)<.001
        leaves = [bpy.data.objects['Split pointed cap '+str(s)] for s in [-1,1]]
        # Rays exactly coplanar with the deliberate split seam are numerically
        # ambiguous; bound that sampling tolerance to ten microunits.
        hits = [h.z for leaf in leaves for dx in [0,-1e-5,1e-5]
                if (h:=ray(leaf,(x+dx,y,3),(0,0,-1))) is not None]
        assert max(hits,default=0)>1.65
    assert ray(base,(0,0,.03),(1,0,0)).x<ray(ring,(0,0,.03),(1,0,0)).x<ray(base,(2,0,.03),(-1,0,0)).x
    assert inside(floor,(.1805,0,.048)) and inside(ring,(.1805,0,.048))
    assert ray(base,(0,0,.47),(1,0,0)).x<ray(upper,(2,0,.47),(-1,0,0)).x
    for i in range(12):
        phi=i*math.tau/12;n=Vector((math.cos(phi),math.sin(phi),0));o=Vector((0,0,.25));rib=bpy.data.objects[f'RI18 bronze drum rib {i}']
        assert max(ray(base,o,n).dot(n),ray(rib,o,n).dot(n))<min(ray(base,n*2+o,-n).dot(n),ray(rib,n*2+o,-n).dot(n)),'Drum rib gap'
    for i,z in enumerate([.17,.34]):
        band=bpy.data.objects[f'RI18 front drum band {i}'];skin=ray(base,(0,-2,z),(0,1,0)).y
        assert ray(band,(0,-2,z),(0,1,0)).y<skin<ray(band,(0,2,z),(0,-1,0)).y
    p=ATTACHMENT_START;n=(ATTACHMENT_END-p).normalized();sleeve=bpy.data.objects['RI18 angled attachment root sleeve'];attachment=bpy.data.objects['RI18 angled bronze attachment']
    skin=ray(upper,p,n);assert skin is not None and (skin-p).dot(n)>0
    assert (ray(sleeve,p-n*2,n)-p).dot(n)<(skin-p).dot(n)<(ray(sleeve,p+n*2,-n)-p).dot(n)
    assert (ray(attachment,p-n*2,n)-p).dot(n)<(ray(sleeve,p+n*2,-n)-p).dot(n)<(ray(attachment,p+n*2,-n)-p).dot(n)
    for sign in [-1,1]:
        axle = bpy.data.objects[f'RI18 hinge axle {sign}']
        for side in [-1,1]:
            bearing = bpy.data.objects[f'RI18 hinge bearing {sign} {side}']
            bracket = bpy.data.objects[f'RI18 hinge root bracket {sign} {side}']
            assert inside(axle,(sign*.26,side*.072,1.63))
            assert inside(bearing,(sign*.26,side*.072,1.63))
            assert inside(bracket,(sign*.26,side*.072,1.618))
            assert inside(bearing,(sign*.26,side*.072,1.618))
            assert inside(bracket,(sign*.26,side*.072,1.600))
            assert inside(upper,(sign*.26,side*.072,1.600))
    textures = texture_evidence(meshes)
    for obj in meshes:
        if not obj.name.startswith('RI18 hinge '):
            continue
        assert len(obj.data.uv_layers)==1
        material = obj.data.materials[0]
        shader = material.node_tree.nodes.get('Principled BSDF')
        texture = shader.inputs['Base Color'].links[0].from_node
        assert texture.type=='TEX_IMAGE' and texture.image.packed_file
        uv_name = texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
        mapped_uv = obj.data.uv_layers.get(uv_name) if uv_name else obj.data.uv_layers.active
        assert mapped_uv is not None and mapped_uv==obj.data.uv_layers.active
        assert all(-1e-5<=v<=1.00001 for item in obj.data.uv_layers.active.data for v in item.uv)
    return dict(positive_closed_meshes=len(meshes),body_bounds=geometry_bounds(meshes),
                retained_fixed_dents_and_attachment_checks=True,
                low_floor_seated_in_original_ring=True,supported_hardware_contact_points=24,
                texture_pixels_and_uvs=textures)


def hardware_sweep(select_clip,clip):
    """Classify sampled surface contacts only inside each supported axle seat."""
    maximum_radius = 0.0
    samples = []
    for frame in range(1,62):
        select_clip(clip,frame)
        contacts = []
        for sign in [-1,1]:
            leaf = bpy.data.objects['Split pointed cap '+str(sign)]
            leaf_tree = tree(leaf)
            leaf_points = [leaf.matrix_world@v.co for v in leaf.data.vertices]
            for hardware in [o for o in bpy.context.scene.objects if o.name.startswith('RI18 hinge ')]:
                pairs = leaf_tree.overlap(tree(hardware))
                if not pairs:
                    continue
                own = hardware.name.split()[4 if 'root bracket' in hardware.name else 3]==str(sign)
                assert own,(frame,leaf.name,'Opposite hinge collision',hardware.name)
                hardware_points = [hardware.matrix_world@v.co for v in hardware.data.vertices]
                for a,b in pairs:
                    left = [leaf_points[i] for i in leaf.data.polygons[a].vertices]
                    right = [hardware_points[i] for i in hardware.data.polygons[b].vertices]
                    low = [max(min(p[i] for p in left),min(p[i] for p in right)) for i in range(3)]
                    high = [min(max(p[i] for p in left),max(p[i] for p in right)) for i in range(3)]
                    # Bounds enclose potential contacts; they are not penetration
                    # depths or exact intersection volumes.
                    radius = math.hypot(max(abs(low[0]-sign*.26),abs(high[0]-sign*.26)),
                                        max(abs(low[2]-1.63),abs(high[2]-1.63)))
                    assert radius<.065 and max(abs(low[1]),abs(high[1]))<.096,(frame,hardware.name,radius)
                    maximum_radius = max(maximum_radius,radius)
                contacts.append(dict(leaf=leaf.name,hardware=hardware.name,triangle_pairs=len(pairs)))
        samples.append(dict(frame=frame,own_axis_seat_contacts=contacts,opposite_hardware_contacts=0))
    return dict(samples=samples,maximum_contact_envelope_radius=maximum_radius,
                allowed_axis_seat_radius=.065,allowed_axis_half_length=.096,
                scope='Integer cycle-frame triangle surface contacts within compact own-axis hardware seats; no continuous-time or contact-volume proof.')
