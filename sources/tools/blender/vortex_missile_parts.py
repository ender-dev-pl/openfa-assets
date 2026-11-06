"""Independent Vortex source: thick wavy casings, silver shaft and service panel."""
import math

import bpy

from build_openfa_assets import beam,cylinder,finish,material
from build_shield_equipment import shell
from terran_missile_parts import band,revolved


def wavy_casing(name,profile,m,thickness=.06):
    count=96;size=len(profile)*count;vertices=[]
    for inner in [False,True]:
        for z,r,wave in profile:
            radius=r-thickness if inner else r
            vertices += [(radius*math.cos(i*math.tau/count),radius*math.sin(i*math.tau/count),
                          z+wave*math.cos(i*math.tau/count)) for i in range(count)]
    faces=[]
    for row in range(len(profile)-1):
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for row in [0,len(profile)-1]:
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;faces.append((a,a+size,b+size,b))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    finish(obj,name,m['violet'],0)
    for index,face in enumerate(mesh.polygons): face.use_smooth=index<(len(profile)-1)*count*2
    return obj


def build():
    m=dict(violet=material('Vortex | violet titanium',(.16,.13,.22),.58,.42),
           silver=material('Vortex | silver pressure shaft',(.32,.36,.40),.74,.34),
           red=material('Vortex | red service frame',(.40,.045,.045),.38,.44),
           dark=material('Vortex | recessed service graphite',(.020,.016,.028),.3,.48),
           gold=material('Vortex | gold propulsion liner',(.44,.24,.045),.72,.39),
           trim=material('Vortex | machined fittings',(.30,.33,.35),.75,.35))
    revolved('Vortex silver pressure shaft',[(.95,.53),(1.12,.59),(1.70,.60),(4.65,.60),(5.22,.56)],m['silver'])
    wavy_casing('Vortex thick wavy upper casing',[(4.40,.65,-.55),(4.95,.73,-.18),
        (5.28,.75,0),(5.58,.69,0),(5.88,.53,0),(6.10,.33,0),(6.26,.11,0)],m)
    support=shell('Vortex upper annular casing support',[(5.04,.72),(5.13,.72)],0,math.tau,
        dict(shell=m['violet'],dark=m['dark']),64,.22)
    support.rotation_euler.x=math.pi/2
    revolved('Vortex rounded nose closure',[(6.20,.20),(6.29,.11),(6.34,.025)],m['violet'])
    wavy_casing('Vortex thick wavy lower casing',[(.43,.57,-.22),(.68,.69,-.10),
        (1.13,.70,.04),(1.50,.67,.18),(1.88,.60,.48)],m)
    for sign in [-1,1]:
        angle=-math.pi/2+sign*1.07
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,
            location=(.70*math.cos(angle),.70*math.sin(angle),5.43))
        ear=bpy.context.object;ear.scale=(.255,.155,.51)
        ear.rotation_euler.z=angle-math.pi/2
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        finish(ear,'Vortex oval head side form',m['violet'],0)
        for face in ear.data.polygons: face.use_smooth=True
    # Curved service surround follows the shaft instead of floating as a flat box.
    angle=-1.90
    frame=shell('Vortex curved red service surround',[(1.98,.625),(4.12,.625)],
        -angle-.29,-angle+.29,dict(shell=m['red'],dark=m['dark']),32,.035)
    frame.rotation_euler.x=math.pi/2
    inset=shell('Vortex dark service inset',[(2.07,.635),(4.02,.635)],-angle-.20,-angle+.20,
        dict(shell=m['dark'],dark=m['dark']),24,.016)
    inset.rotation_euler.x=math.pi/2
    direction=(math.cos(angle),math.sin(angle),0)
    for z in [2.20,3.85]:
        a=(direction[0]*.628,direction[1]*.628,z)
        b=(direction[0]*.648,direction[1]*.648,z)
        beam('Vortex service captive fastener',a,b,.025,m['gold'])
    latch=cylinder('Vortex silver service latch',(direction[0]*.665,direction[1]*.665,3.46),.070,.06,m['trim'],vertices=12)
    from mathutils import Vector
    latch.rotation_euler=Vector(direction).to_track_quat('Z','Y').to_euler()
    bell=shell('Vortex hollow gold propulsion bell',[(.08,.46),(.22,.57),(.40,.48),(.62,.32),(.80,.21)],
        0,math.tau,dict(shell=m['gold'],dark=m['dark']),96,.04)
    bell.rotation_euler.x=math.pi/2
    # Authored fluted thermal liner follows the visible gold tail character.
    for vertex in bell.data.vertices:
        angle=math.atan2(vertex.co.z,vertex.co.x)
        factor=1+.05*math.cos(12*angle)
        vertex.co.x*=factor;vertex.co.z*=factor
    flange=shell('Vortex annular nozzle flange',[(.77,.32),(.87,.32)],0,math.tau,
        dict(shell=m['gold'],dark=m['dark']),64,.15)
    flange.rotation_euler.x=math.pi/2
    for i in range(12):
        a=i*math.tau/12
        beam('Vortex gold bell reinforcement',(.53*math.cos(a),.53*math.sin(a),.18),
            (.29*math.cos(a),.29*math.sin(a),.63),.025,m['gold'])
    mount=shell('Vortex annular engine mount',[(.83,.66),(1.02,.66)],0,math.tau,
        dict(shell=m['violet'],dark=m['dark']),64,.38)
    mount.rotation_euler.x=math.pi/2
    cylinder('Vortex recessed throat',(0,0,.86),.18,.025,m['dark'],vertices=48)
