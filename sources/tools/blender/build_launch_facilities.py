"""Author missing launch-facility motion as additional studies, preserving previous sources."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from launch_facility_recipes import RECIPES, CONFIRMED
ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT/'sources/docs/reconstruction/models/launch-facility-animation-audit.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def material(name, colour, metallic=.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Roughness'].default_value = .73
    shader.inputs['Metallic'].default_value = metallic
    return mat


def mesh_object(name, vertices, faces, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj



def box(name, low, high, mat):
    return mesh_object(name,[(x,y,z) for x,y,z in [(low[0],low[1],low[2]),(high[0],low[1],low[2]),(high[0],high[1],low[2]),(low[0],high[1],low[2]),(low[0],low[1],high[2]),(high[0],low[1],high[2]),(high[0],high[1],high[2]),(low[0],high[1],high[2])]],
        [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)


def hemisphere_lid(radius, top, mats):
    count=96; rings=20
    rows=[]
    for inner in [False,True]:
        r=radius-(.026 if inner else 0)
        angles=[i*math.pi/2/(rings-1) for i in range(rings)]
        if inner:angles.reverse()
        rows += [(top+r*math.sin(angle),max(.0001,r*math.cos(angle))) for angle in angles]
    points=[(r*math.cos(i*math.tau/count),r*math.sin(i*math.tau/count),z) for z,r in rows for i in range(count)]
    faces=[(row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(rows)-1) for i in range(count)]
    for i in range(count):faces.append((i,(len(rows)-1)*count+i,(len(rows)-1)*count+(i+1)%count,(i+1)%count))
    lid=mesh_object('Hemispherical hinged dome',points,faces,mats['body'])
    for polygon in lid.data.polygons:polygon.use_smooth=True
    return lid


def cylinder(name, radius, bottom, top, mat, inner=0):
    count = 64
    vertices = []
    rings = [(radius, bottom), (radius, top)]
    if inner:
        rings += [(inner, bottom), (inner, top)]
    for r,z in rings:
        vertices += [(r*math.cos(i*math.tau/count), r*math.sin(i*math.tau/count), z) for i in range(count)]
    faces = [(i, (i+1)%count, (i+1)%count+count, i+count) for i in range(count)]
    if inner:
        for i in range(count):
            j = (i+1)%count
            faces += [(i+2*count, i+3*count, j+3*count, j+2*count),
                      (i, i+2*count, j+2*count, j), (i+count,j+count,j+3*count,i+3*count)]
    else:
        faces += [tuple(reversed(range(count))), tuple(range(count, 2*count))]
    return mesh_object(name, vertices, faces, mat)


def bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [min(v[i] for v in points) for i in range(3)], [max(v[i] for v in points) for i in range(3)]


def clipped(obj, name, axis, low=None, high=None):
    mesh = obj.data.copy()
    mesh.transform(obj.matrix_world)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for value, inner in [(low, True), (high, False)]:
        if value is None:
            continue
        point = [0,0,0]; point[axis] = value
        normal = [0,0,0]; normal[axis] = 1
        result = bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
            plane_co=point, plane_no=normal, clear_inner=inner, clear_outer=not inner, dist=.000001)
        edges = [e for e in result['geom_cut'] if isinstance(e, bmesh.types.BMEdge) and e.is_boundary]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    if not mesh.polygons:
        bpy.data.meshes.remove(mesh)
        return None
    result = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(result)
    return result


def remove(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def move_control(obj, name, origin=(0,0,0), translation=(0,0,0), rotation=(0,0,0), axis_angle=None):
    pivot = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(pivot)
    pivot.location = origin
    obj.parent = pivot
    obj.matrix_parent_inverse = Matrix.Translation(Vector(origin)).inverted()
    for frame, fraction in [(1,0), (31,1), (61,0)]:
        pivot.location = Vector(origin) + Vector(translation)*fraction
        if axis_angle is None:
            pivot.rotation_euler = Vector(rotation)*fraction
        else:
            pivot.rotation_mode='QUATERNION'
            pivot.rotation_quaternion=Quaternion(Vector(axis_angle[0]), axis_angle[1]*fraction)
        pivot.keyframe_insert(data_path='location', frame=frame)
        pivot.keyframe_insert(data_path='rotation_euler' if axis_angle is None else 'rotation_quaternion', frame=frame)
    action = pivot.animation_data.action
    for curve in action.fcurves:
        for key in curve.keyframe_points:
            key.interpolation = 'LINEAR'
    action.name = name+' motion'
    track = pivot.animation_data.nla_tracks.new()
    track.name = 'LaunchFacilityCycle'
    track.strips.new('LaunchFacilityCycle', 1, action)
    pivot.animation_data.action = None
    return pivot


def wear(obj, mats):
    # Actual small surface scuffs on newly separated/authored leaves; no procedural-only textures.
    made = 0
    for polygon in list(obj.data.polygons):
        if polygon.area < .003:
            continue
        centre = polygon.center.copy()
        tangent = polygon.normal.cross(Vector((0,1,0)))
        if tangent.length < .1: tangent = polygon.normal.cross(Vector((1,0,0)))
        tangent.normalize()
        other = polygon.normal.cross(tangent).normalized()
        centre += polygon.normal*.0005
        w = min(.009, math.sqrt(polygon.area)*.09)
        h = min(.04, math.sqrt(polygon.area)*.17)
        points = [centre + tangent*x*w + other*y*h for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        mark = mesh_object(obj.name+' edge scuff', points, [(0,1,2,3)], mats['scuff'])
        mark.parent = obj
        if polygon.index % 3 == 0:
            mark.data.materials[0] = mats['grime']
        made += 1
        if made == 3: break


def slices(objects, radius, mats, axis=0):
    for obj in objects:
        for sign in [-1,1]:
            for index in range(6):
                a = radius*index/6; b = radius*(index+1)/6
                leaf = clipped(obj, obj.name+f' leaf {sign} {index}', axis,
                               a+.0006 if sign>0 else -b+.0006, b-.0006 if sign>0 else -a-.0006)
                if leaf is None:
                    continue
                shift = [0,0,0]; shift[axis] = sign*(radius*1.10-(a+b)/2)
                shift[2] = -.012*index
                wear(leaf, mats)
                move_control(leaf, f'LaunchLeaf {obj.name} {sign} {index}', translation=shift)
        remove(obj)


def bore(radius, mats, moving, floor=.05, square=False):
    cutter = box('Temporary bore cutter',(-radius,-radius,min(.045,floor-.01)),(radius,radius,8),mats['dark']) if square else cylinder('Temporary bore cutter', radius, min(.045,floor-.01), 8, mats['dark'])
    for obj in list(bpy.context.scene.objects):
        if obj.type!='MESH' or obj==cutter or obj in moving or any(p.name.startswith('LaunchLeaf') for p in parents(obj)):
            continue
        low,high=bounds(obj)
        if high[2] <= .046 or low[0]>radius or high[0]<-radius or low[1]>radius or high[1]<-radius:
            continue
        bpy.context.view_layer.objects.active=obj
        modifier=obj.modifiers.new('Clear launch passage','BOOLEAN')
        modifier.operation='DIFFERENCE'; modifier.solver='EXACT'; modifier.object=cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        if not obj.data.polygons:
            remove(obj)
    remove(cutter)
    if square:box('Recessed launch well floor',(-radius,-radius,floor-.004),(radius,radius,floor),mats['dark'])
    else:cylinder('Recessed launch well floor', radius*.995, floor-.004, floor, mats['dark'])


def parents(obj):
    while obj.parent:
        obj=obj.parent
        yield obj


def crown(radius, top, mats):
    # Shallow terraced crown; segment it for sliding storage inside the surrounding rim.
    lower = cylinder('Crown lower shutter tier', radius, top, top+.035, mats['cap'])
    upper = cylinder('Crown upper shutter tier', radius*.84, top+.035, top+.075, mats['cap'])
    button = cylinder('Crown central shutter tier', radius*.61, top+.075, top+.105, mats['cap'])
    return [lower,upper,button]





def lathe_profile(name, rows, mat):
    count=96
    points=[(r*math.cos(i*math.tau/count),r*math.sin(i*math.tau/count),z) for z,r in rows for i in range(count)]
    faces=[(row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i)
           for row in range(len(rows)-1) for i in range(count)]
    faces += [tuple(reversed(range(count))),tuple(range((len(rows)-1)*count,len(rows)*count))]
    obj=mesh_object(name,points,faces,mat)
    for polygon in obj.data.polygons:polygon.use_smooth=True
    return obj


def mushroom_lid(radius, top, mats):
    count=96
    rings=[(radius*.99,top),(radius*1.04,top+.025),(radius,top+.06),
           (radius*.88,top+.10),(radius*.72,top+.15),(radius*.50,top+.205),
           (radius*.25,top+.24),(.002,top+.25)]
    points=[(r*math.cos(i*math.tau/count),r*math.sin(i*math.tau/count),z) for r,z in rings for i in range(count)]
    faces=[(row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i)
           for row in range(len(rings)-1) for i in range(count)]
    faces += [tuple(reversed(range(count))),tuple(range((len(rings)-1)*count,len(rings)*count))]
    lid=mesh_object('Mushroom cap shutter',points,faces,mats['cap'])
    # Spiral rib follows the hat surface and moves with the entire one-piece cap.
    curve=bpy.data.curves.new('Mushroom spiral relief','CURVE');curve.dimensions='3D';curve.bevel_depth=.006;curve.bevel_resolution=2
    line=curve.splines.new('POLY');line.points.add(240)
    for i,point in enumerate(line.points):
        t=i/240;r=radius*(.08+.87*t);angle=math.tau*3.2*t
        z=top+.25*(1-(r/radius)**1.5)+.012
        point.co=(r*math.cos(angle),r*math.sin(angle),z,1)
    rib=bpy.data.objects.new('Mushroom spiral raised rib',curve);bpy.context.scene.collection.objects.link(rib);rib.data.materials.append(mats['trim'])
    bpy.ops.object.select_all(action='DESELECT');rib.select_set(True);bpy.context.view_layer.objects.active=rib;bpy.ops.object.convert(target='MESH')
    rib=bpy.context.object;rib.parent=lid
    return lid


def energy_spiral(radius, top, mats, upward=False):
    energy=material('MK11 | upward spiral ribbon' if upward else 'MK12 | yellow energetic ribbon',(.75,.55,.005),.25 if upward else 0)
    shader=energy.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Emission Color'].default_value=(.75,.65,0,1)
    shader.inputs['Emission Strength'].default_value=.15 if upward else .8
    def position(t):
        r=.025+(radius-.025)*min(t,1)+.035*max(0,t-1)
        angle=math.tau*3.5*t
        z=top+.22*max(0,1-t)**.8
        return Vector((r*math.cos(angle),r*math.sin(angle),z))
    for i in range(160):
        obj=mesh_object('Energy ribbon strip '+str(i),
            [(x*.5,y*.5,z*.5) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],
            [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],energy)
        control=bpy.data.objects.new('LaunchLeaf energetic ribbon '+str(i),None)
        bpy.context.scene.collection.objects.link(control);obj.parent=control;control.rotation_mode='QUATERNION'
        for frame in range(1,62):
            fraction=(frame-1)/30 if frame<=31 else (61-frame)/30
            t=i/160-fraction*1.02 if upward else i/160+fraction
            hidden=upward and t<0
            a=position(max(t,0));b=position(max(t+1/160,0))
            tangent=(b-a).normalized() if (b-a).length>.000001 else Vector((1,0,0))
            radial=Vector(((a.x+b.x)/2,(a.y+b.y)/2,0)).normalized()
            normal=tangent.cross(radial).normalized()
            if normal.z<0:normal=-normal
            side=normal.cross(tangent).normalized()
            rotation=Matrix(((tangent.x,side.x,normal.x),(tangent.y,side.y,normal.y),(tangent.z,side.z,normal.z)))
            control.location=(a+b)/2;control.rotation_quaternion=rotation.to_quaternion()
            control.scale=((b-a).length*1.03,.210 if upward else .110,.009)
            if hidden:
                control.location=(0,0,.01);control.scale=(.00001,.00001,.00001);control.rotation_quaternion=(1,0,0,0)
            for path in ['location','rotation_quaternion','scale']:control.keyframe_insert(data_path=path,frame=frame)
        action=control.animation_data.action
        for curve in action.fcurves:
            for key in curve.keyframe_points:key.interpolation='LINEAR'
        action.name='Energetic ribbon winding '+str(i)
        track=control.animation_data.nla_tracks.new();track.name='LaunchFacilityCycle'
        track.strips.new('LaunchFacilityCycle',1,action);control.animation_data.action=None


def prepare(record, spec, mats):
    scene=bpy.context.scene
    for obj in list(scene.objects):
        if obj.type=='MESH':
            evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            mesh=bpy.data.meshes.new_from_object(evaluated)
            mesh.transform(obj.matrix_world)
            obj.modifiers.clear(); obj.parent=None; obj.matrix_world=Matrix.Identity(4); obj.data=mesh
        if obj.animation_data:
            obj.animation_data_clear()
    mode=spec['mode']; top=spec['top']; radius=spec.get('radius',spec['mouth'])
    if mode in ['roof','fold-down','open-roof','open-emitter']:
        for obj in scene.objects:
            if obj.type=='MESH' and obj.name.startswith('Aerial'):
                obj.location.x-=.72; obj.location.y+=.72
    if mode in ['roof','fold-down','open-roof']:
        for obj in list(scene.objects):
            if obj.type=='MESH' and obj.name.startswith(('Roof recessed opening','Weapon pivot','Weapon barrel','Weapon dark bore')):
                remove(obj)
    original_meshes = set(obj for obj in scene.objects if obj.type=='MESH')
    movers=[]
    if mode=='quarters':
        for hinge in scene.objects:
            if hinge.type=='MESH' and hinge.name.startswith('Silo lid hinge'):
                hinge.data.transform(Matrix.Rotation(math.pi/4,4,'Z'))
        for obj in [o for o in list(scene.objects) if o.name in spec['targets']]:
            for sx in [-1,1]:
                half=clipped(obj,'Temporary half',0,0 if sx>0 else None,0 if sx<0 else None)
                for sy in [-1,1]:
                    leaf=clipped(half,'Quarter dome '+str((sx,sy)),1,0 if sy>0 else None,0 if sy<0 else None)
                    if leaf is not None:
                        wear(leaf,mats)
                        axis=Vector((-sy,sx,0)).normalized()
                        move_control(leaf,'LaunchLeaf quarter '+obj.name+str((sx,sy)),
                            origin=(sx*radius*.72,sy*radius*.72,top),axis_angle=(axis,math.radians(108)))
                remove(half)
            remove(obj)
    elif mode=='slice':
        targets=[obj for obj in scene.objects if obj.name in spec['targets']]
        slices(targets,radius,mats,spec['axis'])
    elif mode=='hinged-cap':
        original=bpy.data.objects[spec['targets'][0]]
        for sign in [-1,1]:
            leaf=clipped(original,'Split pointed cap '+str(sign),spec['axis'],0 if sign>0 else None,0 if sign<0 else None)
            wear(leaf,mats)
            move_control(leaf,'LaunchLeaf pointed cap '+str(sign),origin=(sign*radius,0,top) if spec['axis']==0 else (0,sign*radius,top),rotation=(0,sign*math.radians(110),0) if spec['axis']==0 else (-sign*math.radians(110),0,0))
        remove(original)
    elif mode=='single-lid':
        obj=bpy.data.objects[spec['targets'][0]]
        lid=hemisphere_lid(radius*.98,top,mats)
        base=clipped(obj,'Hollow tower casing',2,None,top)
        remove(obj)
        hinge=cylinder('Rear lid hinge axle',.055,-.16,.16,mats['trim'])
        hinge.rotation_euler.y=math.pi/2;hinge.location=(0,radius,top)
        wear(hinge,mats)
        wear(lid,mats)
        move_control(lid,'LaunchLeaf rear hinge',origin=(0,radius,top),rotation=(-math.radians(110),0,0))
    elif mode=='fold-down':
        roof=bpy.data.objects['Block roof ledge']
        centre=clipped(roof,'Temporary central roof',0,-spec['mouth'],spec['mouth'])
        inner=clipped(centre,'Temporary central hatch',1,-spec['mouth'],spec['mouth']);remove(centre)
        for sign in [-1,1]:
            leaf=clipped(inner,'Down-folding red hatch '+str(sign),0,0 if sign>0 else None,0 if sign<0 else None)
            leaf.data.materials.clear();leaf.data.materials.append(mats['accent']);wear(leaf,mats)
            move_control(leaf,'LaunchLeaf inward hinge '+str(sign),origin=(sign*spec['mouth'],0,top),rotation=(0,-sign*math.radians(92),0))
        remove(inner)
    elif mode=='roof':
        slices([bpy.data.objects['Block roof ledge']],radius,mats)
    elif mode=='organic-upward-spiral':
        for obj in list(scene.objects):
            if obj.type=='MESH':remove(obj)
        cylinder('MK11 circular organic footing',.95,0,.12,mats['body'])
        lathe_profile('MK11 organic hemisphere and hollow trunk',[(.10,.77),(.16,.82),(.30,.78),(.46,.66),(.60,.43),(.68,.39),(.88,.35),(1.08,.40),(1.19,.51),(1.25,.75)],mats['body'])
        cylinder('MK11 upper organic ring',.82,1.18,1.27,mats['body'],inner=spec['mouth']+.025)
        energy_spiral(radius,top,mats,upward=True)
    elif mode in ['crown','tower-crown','energy-spiral','mushroom-retract']:
        if mode=='crown':
            obj=bpy.data.objects['Flared spindle column']
            base=clipped(obj,'Hollow spindle support',2,None,spec['trim_above']); remove(obj)
        else:
            remove(bpy.data.objects['Faceted crystal tower'])
            cylinder('Segmented hollow launch tower',.48,.08,spec['height'],mats['body'],inner=spec['mouth']+.015)
            for i in range(11):
                z=.12+i*(spec['height']-.12)/11
                cylinder('Tower exterior band',.50,z,z+.028,mats['trim'],inner=.475)
        cylinder('Crown fixed support rim',radius*1.13,top-.07,top,mats['body'],inner=spec['mouth']+.02)
        if mode=='mushroom-retract':
            for obj in list(scene.objects):
                if obj.type=='MESH' and obj.name.startswith(('Faceted crystal tower','Crystal radial strut','Crystal luminous node')): remove(obj)
            for x in [-.67,.67]:
                bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(x,0,.48))
                lobe=bpy.context.object;lobe.name='Rounded side chamber';lobe.scale=(.55,.53,.48)
                bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);lobe.data.materials.append(mats['body'])
                for polygon in lobe.data.polygons: polygon.use_smooth=True
            lid=mushroom_lid(radius,top,mats)
            wear(lid,mats)
            move_control(lid,'LaunchLeaf rear-stowing mushroom cap',translation=(0,radius*2.15,.035))
        elif mode=='energy-spiral': energy_spiral(radius,top,mats)
        else: slices(crown(radius,top,mats),radius,mats)
    elif mode=='strip-cover':
        plate=cylinder('Transverse green cover',radius,top,top+.025,mats['body'])
        targets=[plate]
        for x in [-.32,0,.32]:
            targets.append(box('Red transverse cover marking',(x-.06,-.55,top+.026),(x+.06,.55,top+.028),mats['accent']))
        slices(targets,radius,mats,axis=0)
    elif mode=='pyramid':
        for obj in list(scene.objects):
            if obj.type=='MESH' and obj.name.startswith(('Landing pad','Landing deck')):
                remove(obj)
        for i in range(4):
            a=i*math.pi/2; b=(i+1)*math.pi/2
            vertices=[(radius*math.cos(a)-radius*math.sin(a),radius*math.sin(a)+radius*math.cos(a),top),
                      (radius*math.cos(b)-radius*math.sin(b),radius*math.sin(b)+radius*math.cos(b),top),(0,0,top+.70)]
            leaf=mesh_object('Pyramidal hatch petal',vertices,[(0,1,2)],mats['body'])
            solid=leaf.modifiers.new('Hatch thickness','SOLIDIFY');solid.thickness=.025
            leaf.data.materials.append(mats['inner']);solid.material_offset=1
            bpy.context.view_layer.objects.active=leaf;bpy.ops.object.modifier_apply(modifier=solid.name)
            midpoint=(Vector(vertices[0])+Vector(vertices[1]))/2
            direction=(Vector(vertices[1])-Vector(vertices[0])).normalized()
            rotation=direction*math.radians(112)
            # All edge axes are cardinal, so XYZ Euler is unambiguous here.
            wear(leaf,mats);move_control(leaf,'LaunchLeaf pyramidal petal '+str(i),origin=midpoint,rotation=rotation)
    elif mode=='open-silo':
        for obj in list(scene.objects):
            if obj.type=='MESH' and obj.name.startswith('Silo armoured lid'):
                remove(obj)
        cylinder('Permanently exposed silo throat',.82,top-.07,top+.05,mats['body'],inner=spec['mouth']+.015)
    elif mode=='open-roof':
        cylinder('Permanently exposed roof well',.68,top-.03,top+.08,mats['trim'],inner=spec['mouth']+.015)
    elif mode=='open-emitter':
        cylinder('Permanently exposed emitter collar',.25,top-.03,top+.035,mats['trim'],inner=spec['mouth']+.008)
    else:
        raise ValueError(mode)
    bpy.context.view_layer.update()
    movers=[obj for obj in scene.objects if obj.type=='MESH' and any(p.name.startswith('LaunchLeaf') for p in parents(obj))]
    bore(spec['mouth'],mats,movers,spec.get('floor',.05),spec.get('square',False))
    if mode=='pyramid':
        cylinder('Vertical hangar shaft walls',spec['mouth']+.025,spec['floor'],top,mats['dark'],inner=spec['mouth'])
    if mode=='crown':
        cylinder('Hollow spindle structural throat',.35,.30,.97,mats['body'],inner=.24)
    for obj in list(scene.objects):
        if obj.type=='MESH' and obj not in original_meshes and 'scuff' not in obj.name and not obj.children and not obj.name.startswith('Energy ribbon'):
            wear(obj,mats)
    root=bpy.data.objects.new('PlacementRoot',None);scene.collection.objects.link(root)
    for obj in list(scene.objects):
        if obj.type in ['MESH','EMPTY'] and obj!=root and obj.parent is None: obj.parent=root
    root['catalogue_id']=record['id'];root['footprint_width'],root['footprint_height']=record['footprint']
    if spec.get('terrain_cutout_fraction'):
        root['preserve_ground_origin']=True
    return root, movers



def preview_ground(radius):
    dark=bpy.data.materials.new('Preview terrain holdout')
    dark.use_nodes=True
    tree=dark.node_tree;tree.nodes.clear()
    out=tree.nodes.new('ShaderNodeOutputMaterial');holdout=tree.nodes.new('ShaderNodeHoldout')
    tree.links.new(holdout.outputs[0],out.inputs['Surface'])
    obj=mesh_object('Preview ground mask',[(x*30,y*30,z) for x,y,z in [(-1,-1,-.012),(1,-1,-.012),(1,1,-.012),(-1,1,-.012),(-1,-1,-.002),(1,-1,-.002),(1,1,-.002),(-1,1,-.002)]],
        [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],dark)
    cutter=cylinder('Preview mouth cutter',radius,-2,2,dark)
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Preview shaft opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);remove(cutter)
    obj['preview_only']=True


def frame_camera(scene):
    points=[]
    for frame in [1,31]:
        scene.frame_set(frame)
        points += [obj.matrix_world @ v.co for obj in scene.objects if obj.type=='MESH' and not obj.get('preview_only') for v in obj.data.vertices if (obj.matrix_world @ v.co).z>=-.001]
    low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)])
    centre=(low+high)/2
    camera=scene.camera
    direction=Vector((6,-10,7)).normalized()
    camera.location=centre+direction*15
    camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    local=[camera.matrix_world.inverted()@p for p in points]
    camera.data.type='ORTHO';camera.data.ortho_scale=max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.18


def build(record):
    spec=RECIPES[record['key']]
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/record['source']))
    scene=bpy.context.scene; scene.frame_set(1);scene.render.fps=30
    culture=record['culture']
    colours={'terran':(.35,.36,.34),'rigellian':(.14,.29,.20),'braccatian':(.39,.21,.14),
             'mikotaj':(.10,.25,.19),'artemian':(.13,.28,.22),'mauna':(.28,.38,.47),'achaean':(.42,.23,.17)}
    mats=dict(body=material('Launch | '+culture+' casing',colours[culture]),
              trim=material('Launch | worn structural metal',(.30,.32,.31)),
              cap=material('Launch | crown finish',(.59,.46,.17) if spec.get('colour')!='silver' else (.56,.65,.66)),
              accent=material('Launch | red panel markings',(.44,.045,.028)),
              dark=material('Launch | dark interior',(.012,.016,.019)),
              inner=material('Launch | green inner panels',(.10,.25,.18)),
              scuff=material('Launch | edge abrasions',(.43,.44,.38)),
              grime=material('Launch | joint grime',(.035,.027,.019)))
    root,movers=prepare(record,spec,mats)
    scene.frame_start=1;scene.frame_end=61
    scene.render.resolution_x=scene.render.resolution_y=512
    scene.render.resolution_percentage=100
    if scene.render.engine=='CYCLES':scene.cycles.samples=24
    frame_camera(scene);scene.frame_set(1)
    if spec.get('terrain_cutout_fraction'): preview_ground(spec['mouth'])
    folder=ROOT/'sources/docs/assets/reconstruction/launch-facilities'/culture/record['key'].lower()
    media=ROOT/'gallery/media/docs/assets/reconstruction/launch-facilities'/culture/record['key'].lower()
    folder.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY'] and not obj.get('preview_only'):obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(folder/'model.glb'),export_format='GLB',use_selection=True,
        export_extras=True,export_apply=True,export_animations=bool(movers),export_animation_mode='NLA_TRACKS',export_frame_range=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'model.blend'))
    for name,frame in [('front-quarter',1),('half-open',16),('open',31)]:
        scene.frame_set(frame);scene.render.filepath=str(media/(name+'.png'));bpy.ops.render.render(write_still=True)
    meta=dict(id=record['id'],culture=culture,key=record['key'],issue=179,footprint=record['footprint'],
        source_study=record['source'],source_blend_sha256=record['source_blend_sha256'],
        blend_sha256=sha(folder/'model.blend'),glb_sha256=sha(folder/'model.glb'),
        generator_sha256=sha(Path(__file__)),recipe_sha256=sha(Path(__file__).with_name('launch_facility_recipes.py')),
        legacy_evidence='sources/docs/reconstruction/models/launch-facility-animation-audit.json',
        observed=record['observed'],mechanism=spec['mode'],aperture_radius=spec['mouth'],floor_height=spec.get('floor',.05),terrain_cutout_fraction=spec.get('terrain_cutout_fraction',0),
        moving_meshes=len(movers),launch_animation=dict(kind={9:'satellite',14:'iris',26:'deck'}[record['definition_class']],
        clip='LaunchFacilityCycle' if movers else None,closed_frame=1,open_frame=31,end_frame=61),
        inferred=['Hidden hinge/telescopic engineering, dimensions, shaft depths and continuous motion timing'],
        wear='New leaves have actual surface abrasion/grime patches; original fixed model materials preserved',
        fixed_open=not movers,blender=bpy.app.version_string)
    (folder/'model.json').write_bytes((json.dumps(meta,indent=2)+'\n').encode())
    print('LAUNCH_FACILITY_AUTHORED',record['key'],len(movers),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('keys',nargs='*');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for record in json.loads(AUDIT.read_text())['records']:
        if record['key'] in RECIPES and (record['key'] in (args.keys or CONFIRMED)):build(record)


if __name__=='__main__':main()
