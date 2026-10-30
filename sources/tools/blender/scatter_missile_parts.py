"""Original Scatter missile pressure shaft and thick sculpted tail vanes."""
import math

import bpy

from build_openfa_assets import finish,material,cylinder
from build_shield_equipment import shell
from terran_missile_parts import band,revolved

PROFILE=[(.60,.47,.09),(.82,.64,.39),(1.10,.79,.48),(1.45,.82,.43),
         (1.85,.77,.32),(2.25,.68,.18),(2.60,.61,.045)]


def vane(name,angle,profile,surface,thickness=.09):
    segments=16;count=segments+1;size=len(profile)*count
    vertices=[]
    for inner in [False,True]:
        for z,r,half in profile:
            radius=r-thickness if inner else r
            vertices += [(radius*math.cos(angle-half+2*half*i/segments),
                          radius*math.sin(angle-half+2*half*i/segments),z) for i in range(count)]
    faces=[]
    for row in range(len(profile)-1):
        for i in range(segments):
            a=row*count+i;b=a+1;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for row in [0,len(profile)-1]:
        for i in range(segments):
            a=row*count+i;b=a+1;faces.append((a,a+size,b+size,b))
    for i in [0,segments]:
        for row in range(len(profile)-1):
            a=row*count+i;b=a+count;faces.append((a,b,b+size,a+size))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    finish(obj,name,surface,0)
    for face in mesh.polygons: face.use_smooth=len(face.vertices)==4
    return obj


def build():
    m=dict(body=material('Scatter | brushed titanium',(.20,.22,.29),.68,.42),
           trim=material('Scatter | exposed alloy',(.39,.41,.43),.75,.36),
           dark=material('Scatter | dark nose sleeve',(.018,.022,.040),.42,.42),
           red=material('Scatter | red enamel',(.44,.045,.035),.42,.40),
           gold=material('Scatter | bronze gold vane skin',(.47,.235,.065),.68,.39),
           liner=material('Scatter | refractory bell',(.16,.13,.11),.6,.48))
    revolved('Scatter silver pressure shaft',[(.56,.43),(.82,.50),(1.6,.58),(2.7,.60),(3.97,.60)],m['body'])
    revolved('Scatter broad dark nose band',[(3.94,.603),(4.03,.61),(4.87,.61),(4.98,.595)],m['dark'])
    revolved('Scatter red tapered warhead',[(4.95,.595),(5.12,.59),(5.51,.55),(5.91,.47)],m['red'])
    revolved('Scatter silver nose collar',[(5.88,.474),(5.98,.43),(6.08,.33),(6.13,.28)],m['trim'])
    revolved('Scatter rounded red nose tip',[(6.10,.285),(6.19,.20),(6.27,.10),(6.30,.025)],m['red'])
    for z,r in [(3.14,.605),(1.04,.529)]:
        band('Scatter pressure shaft joint',z,r,.024,m['trim'],.035)
    for i in range(4):
        angle=math.pi/4+i*math.pi/2
        vane('Scatter thick swept gold vane',angle,PROFILE,m['gold'])
        # Narrow pale inserts are authored service construction, not legacy wear pixels.
        inset=[(z,r+.008,half*.28) for z,r,half in PROFILE[2:5]]
        vane('Scatter vane thermal insert',angle,inset,m['trim'],.012)
    skirt=shell('Scatter hollow aft skirt',[(.12,.25),(.28,.34),(.46,.40),(.60,.44)],
        0,math.tau,dict(shell=m['body'],dark=m['dark']),64,.045)
    skirt.rotation_euler.x=math.pi/2
    bell=shell('Scatter hollow propulsion bell',[(.07,.20),(.15,.20),(.27,.16),(.36,.10)],
        0,math.tau,dict(shell=m['liner'],dark=m['dark']),64,.03)
    bell.rotation_euler.x=math.pi/2
    band('Scatter red nozzle retaining rim',.13,.235,.06,m['red'],.025)
    cylinder('Scatter recessed throat',(0,0,.42),.09,.025,m['dark'],vertices=48)
