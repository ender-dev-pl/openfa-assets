"""Body-mounted lift cylinders, slotted rack guides and geared leaf bearings."""
import math
import bpy
from mathutils import Vector


def linear_action(obj):
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation='LINEAR'


def frame(name,parent):
    obj=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(obj);obj.parent=parent
    return obj


def cylinder(name,centre,radius,depth,material,parent):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=radius,depth=depth)
    obj=bpy.context.object;obj.name=name;obj.parent=parent;obj.location=centre;obj.data.materials.append(material)
    return obj


def merge(name,parts,parent):
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();vertices=[];faces=[];indices=[];materials=[]
    for part in parts:
        obj=part.evaluated_get(deps);mesh=obj.to_mesh();base=len(vertices)
        vertices.extend(tuple(part.matrix_local@v.co) for v in mesh.vertices)
        for polygon in mesh.polygons:
            material=part.material_slots[polygon.material_index].material
            assert material is not None
            if material not in materials:materials.append(material)
            faces.append(tuple(base+i for i in polygon.vertices));indices.append(materials.index(material))
        obj.to_mesh_clear()
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    for material in materials:data.materials.append(material)
    for polygon,index in zip(data.polygons,indices):polygon.material_index=index
    result=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(result);result.parent=parent
    for part in parts:bpy.data.objects.remove(part,do_unlink=True)
    return result


def drive(root,index,radial,angle,leaf,box,mesh_object):
    number=f'{index+1:02}';dark=bpy.data.materials['Refined | dark'];edge=bpy.data.materials['Refined | edge'];bronze=bpy.data.materials['Refined | bronze']
    base=frame('Iris mount '+number,root)
    parts=[box('Mount foot',(0,0,.425),(.22,.20,.14),dark,base),cylinder('Lift barrel',(0,0,.52),.060,.13,dark,base),cylinder('Lift collar',(0,0,.582),.067,.025,edge,base)]
    for x in [-.075,.075]:
        for y in [-.065,.065]:parts.append(cylinder('Mount bolt',(x,y,.504),.014,.020,edge,base))
    merge('Iris mount body '+number,parts,base);base.location=radial*1.08;base.rotation_euler.z=angle
    base['attachment']='Bolted foot embeds into bunker side; fixed support for lift barrel'
    head=frame('Iris lift carriage '+number,root)
    parts=[box('Guide floor',(x,0,-.045),(.07,.18,.020),dark,head) for x in [-.105,.105]]
    parts += [box('Guide cheek',(0,y,-.015),(.28,.04,.04),edge,head) for y in [-.07,.07]]
    parts += [box('Drive gearbox',(0,-.075,-.070),(.10,.10,.10),dark,head),cylinder('Lift piston',(0,0,-.1125),.029,.135,edge,head)]
    merge('Iris lift carriage body '+number,parts,head);head.rotation_euler.z=angle
    head['attachment']='Piston overlaps fixed barrel through full stroke; slotted guide retains moving rack'
    rack=box('Iris sliding guide '+number,(0,0,0),(.70,.075,.035),edge,root);rack.rotation_euler.z=angle
    rack['attachment']='Constant-length rack passes through supported guide; minimum axial engagement0.10'
    axle=cylinder('Iris hinge axle '+number,(0,0,.025),.075,.11,dark,leaf)
    axle['attachment']='Broad bearing boss engages leaf underside and rack, parented rigidly to leaf'
    # Toothed external drive wheel; its shaft enters the side gearbox.
    n=64;vertices=[]
    for y in [-.016,.016]:
        for i in range(n):
            radius=.060 if i%4 in [1,2] else .052;a=math.tau*i/n
            vertices.append((radius*math.cos(a),y,radius*math.sin(a)))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    wheel=mesh_object('Iris drive wheel '+number,vertices,faces,bronze,head);wheel.location=(0,-.135,-.0875);wheel.rotation_mode='XYZ'
    return head,wheel,rack


def key_drive(head,wheel,rack,radial,amount,lift,frame_number):
    head.location=radial*1.08+Vector((0,0,.615+lift));head.keyframe_insert('location',frame=frame_number)
    wheel.rotation_euler.y=-.60*amount/.060;wheel.keyframe_insert('rotation_euler',frame=frame_number)
    rack.location=radial*(.87+.60*amount)+Vector((0,0,.605+lift));rack.keyframe_insert('location',frame=frame_number)
