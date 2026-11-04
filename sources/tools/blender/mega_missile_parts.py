"""Independent Mega casing, substantial diamond vanes and copper base fittings."""
import math

import bpy
from mathutils import Vector

from build_openfa_assets import beam,cylinder,finish,material
from build_shield_equipment import shell
from terran_missile_parts import band,revolved

BODY=[(.25,.38),(.50,.52),(.95,.54),(1.20,.47),(1.70,.44),(2.90,.44),(4.20,.44),(4.99,.46)]
OUTLINE=[(.40,1.25),(.40,4.40),(.48,4.35),(.58,3.65),(.88,2.72),(.78,2.35),(.62,1.55)]


def outer_radius(z):
    edge=[(1.25,.40),(1.55,.62),(2.35,.78),(2.72,.88),(3.65,.58),(4.35,.48),(4.40,.40)]
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(edge,edge[1:]) if za<=z<=zb)


def vane(angle,m):
    radial=Vector((math.cos(angle),math.sin(angle),0));tangent=Vector((-math.sin(angle),math.cos(angle),0))
    vertices=[tuple(radial*r+tangent*t+Vector((0,0,z))) for t in [-.035,.035] for r,z in OUTLINE]
    count=len(OUTLINE);faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh=bpy.data.meshes.new('Solid diamond vane');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('Mega solid diamond vane',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,m['body'],0)
    for z in [2.15,2.35,2.55,2.75,2.95,3.15]:
        for sign in [-1,1]:
            start=radial*.475+tangent*(sign*.038)+Vector((0,0,z))
            end=radial*(outer_radius(z)-.035)+tangent*(sign*.038)+Vector((0,0,z))
            beam('Mega vane transverse rib',start,end,.006,m['trim'])
    for (r0,z0),(r1,z1) in zip(OUTLINE[2:],OUTLINE[3:]):
        beam('Mega vane edge rail',radial*r0+Vector((0,0,z0)),radial*r1+Vector((0,0,z1)),.012,m['trim'])


def lower_panel(angle,surface):
    count=33;rows=17;size=count*rows;vertices=[]
    for inner in [False,True]:
        for j in range(rows):
            v=j/(rows-1)
            for i in range(count):
                t=-1+2*i/(count-1);phi=angle+.64*t
                top=.42+.60*math.sqrt(max(0,1-t*t));z=.30+(top-.30)*v
                r=next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(BODY,BODY[1:]) if za<=z<=zb)
                offset=-.025 if inner else .035+.065*math.sin(math.pi*v)
                vertices.append(((r+offset)*math.cos(phi),(r+offset)*math.sin(phi),z))
    faces=[]
    for row in range(rows-1):
        for i in range(count-1):
            a=row*count+i;b=a+1;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for row in [0,rows-1]:
        for i in range(count-1):
            a=row*count+i;b=a+1;faces.append((a,a+size,b+size,b))
    for i in [0,count-1]:
        for row in range(rows-1):
            a=row*count+i;b=a+count;faces.append((a,b,b+size,a+size))
    mesh=bpy.data.meshes.new('Shaped copper lower panel');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('Mega thick copper lower panel',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,surface,0)
    for face in mesh.polygons: face.use_smooth=True


def build():
    m=dict(body=material('Mega | olive gray titanium',(.23,.245,.23),.65,.43),
           ivory=material('Mega | ivory nose ceramic',(.54,.52,.40),.22,.46),
           copper=material('Mega | copper fittings',(.34,.14,.075),.66,.40),
           trim=material('Mega | machined vane ribs',(.34,.36,.35),.76,.34),
           dark=material('Mega | recessed graphite',(.012,.016,.02),.3,.5))
    revolved('Mega cylindrical pressure casing',[(.65,.53)]+BODY[2:],m['body'])
    band('Mega copper nose retaining band',4.70,.458,.14,m['copper'],.04)
    band('Mega upper silver nose collar',4.95,.472,.10,m['trim'],.04)
    revolved('Mega ivory nose cone',[(4.98,.46),(5.15,.43),(5.48,.31),(5.80,.20),(6.07,.105)],m['ivory'])
    revolved('Mega copper nose tip',[(6.01,.125),(6.16,.075),(6.28,.018)],m['copper'])
    cylinder('Mega short nose pin',(0,0,6.39),.015,.25,m['trim'],vertices=24)
    for angle in [-math.pi/2,math.pi/6,5*math.pi/6]:
        vane(angle,m)
        lower_panel(angle,m['copper'])
    cup=shell('Mega hollow lower casing',[(.22,.38),(.50,.52),(.70,.54)],0,math.tau,
        dict(shell=m['body'],dark=m['dark']),64,.06)
    cup.rotation_euler.x=math.pi/2
    bell=shell('Mega hollow copper nozzle',[(.05,.28),(.18,.33),(.34,.28),(.53,.16)],0,math.tau,
        dict(shell=m['copper'],dark=m['dark']),64,.035)
    bell.rotation_euler.x=math.pi/2
    flange=shell('Mega annular nozzle support',[(.30,.43),(.40,.43)],0,math.tau,
        dict(shell=m['copper'],dark=m['dark']),64,.28)
    flange.rotation_euler.x=math.pi/2
    cylinder('Mega recessed throat',(0,0,.60),.13,.025,m['dark'],vertices=48)

    # Authored width refinement follows the management silhouette in world axes.
    for obj in list(bpy.context.collection.objects):
        if obj.type=='MESH':
            inverse=obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                point=obj.matrix_world @ vertex.co;point.x*=1.15;point.y*=1.15
                vertex.co=inverse @ point
