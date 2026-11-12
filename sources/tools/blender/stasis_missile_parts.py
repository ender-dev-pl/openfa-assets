"""Independent Stasis pressure casing, conformal markings and open tail frame."""
import math

import bpy
from mathutils import Vector

from build_openfa_assets import beam,cylinder,finish,material
from build_shield_equipment import shell
from terran_missile_parts import band,revolved


def round_mark(angle,surface):
    # Dense polar grid follows the cylindrical collar; inner back is embedded.
    count=48;rings=9;size=1+rings*count;vertices=[]
    for lift in [.003,-.005]:
        vertices.append(((.49+lift)*math.cos(angle),(.49+lift)*math.sin(angle),1.35))
        for j in range(1,rings+1):
            r=.15*j/rings
            for i in range(count):
                theta=i*math.tau/count;phi=angle+r*math.cos(theta)/.49;z=1.35+r*math.sin(theta)
                vertices.append(((.49+lift)*math.cos(phi),(.49+lift)*math.sin(phi),z))
    faces=[]
    for i in range(count):
        a=1+i;b=1+(i+1)%count
        faces += [(0,a,b),(size,b+size,a+size)]
    for row in range(rings-1):
        for i in range(count):
            a=1+row*count+i;b=1+row*count+(i+1)%count;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for i in range(count):
        a=1+(rings-1)*count+i;b=1+(rings-1)*count+(i+1)%count
        faces.append((a,a+size,b+size,b))
    mesh=bpy.data.meshes.new('Conformal maroon collar mark');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('Stasis conformal maroon round marking',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,surface,0)


def build():
    m=dict(green=material('Stasis | green titanium casing',(.045,.17,.11),.54,.43),
           pale=material('Stasis | pale collar alloy',(.50,.52,.44),.45,.43),
           maroon=material('Stasis | maroon identification',(.28,.045,.10),.32,.45),
           red=material('Stasis | red propulsion jacket',(.46,.055,.025),.50,.38),
           dark=material('Stasis | graphite frame',(.015,.022,.035),.65,.43),
           trim=material('Stasis | machined fittings',(.30,.33,.32),.75,.35))
    revolved('Stasis straight green pressure casing',[(1.04,.44),(1.15,.46),(5.44,.46)],m['green'])
    revolved('Stasis rounded green head',[(5.42,.46),(5.62,.43),(5.83,.34),(6.02,.22),(6.12,.13)],m['green'])
    band('Stasis pale upper band',5.46,.472,.16,m['pale'],.035)
    band('Stasis thin pale body joint',4.22,.466,.038,m['pale'],.022)
    revolved('Stasis broad pale lower collar',[(1.08,.465),(1.12,.49),(1.57,.49),(1.62,.465)],m['pale'])
    band('Stasis green lower collar lip',1.08,.48,.08,m['green'],.04)
    for angle in [-math.pi/2+i*math.pi/2 for i in range(4)]: round_mark(angle,m['maroon'])
    revolved('Stasis small red nose cap',[(6.08,.14),(6.16,.10),(6.20,.03)],m['red'])
    cylinder('Stasis short nose pin',(0,0,6.30),.017,.22,m['trim'],vertices=24)
    mount=shell('Stasis annular engine mount',[(.91,.44),(1.08,.44)],0,math.tau,
        dict(shell=m['green'],dark=m['dark']),64,.20)
    mount.rotation_euler.x=math.pi/2
    flange=shell('Stasis annular nozzle flange',[(.88,.30),(1.01,.30)],0,math.tau,
        dict(shell=m['red'],dark=m['dark']),64,.20)
    flange.rotation_euler.x=math.pi/2
    bell=shell('Stasis hollow red propulsion bell',[(.10,.36),(.22,.385),(.40,.28),(.65,.16),(.92,.14)],
        0,math.tau,dict(shell=m['red'],dark=m['dark']),96,.038)
    bell.rotation_euler.x=math.pi/2
    for i in range(4):
        angle=math.pi/4+i*math.pi/2;radial=Vector((math.cos(angle),math.sin(angle),0))
        beam('Stasis open tail frame brace',radial*.40+Vector((0,0,.22)),radial*.42+Vector((0,0,1.04)),.022,m['dark'])
        beam('Stasis lower frame anchor',radial*.345+Vector((0,0,.22)),radial*.405+Vector((0,0,.22)),.022,m['trim'])
        cylinder('Stasis mount captive fastener',(radial.x*.39,radial.y*.39,1.07),.018,.035,m['trim'],vertices=12)
    cylinder('Stasis recessed throat',(0,0,.965),.10,.025,m['dark'],vertices=48)

    # Transverse silhouette refinement uses world coordinates, preserving Z.
    for obj in list(bpy.context.collection.objects):
        if obj.type=='MESH':
            inverse=obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                point=obj.matrix_world @ vertex.co;point.x*=1.18;point.y*=1.18
                vertex.co=inverse @ point
