"""Independent Nuclear missile study: dark casing, shaped pods and conformal mark."""
import math

import bpy

from build_openfa_assets import cylinder,finish,material
from build_shield_equipment import shell
from cannon_equipment_parts import oval
from terran_missile_parts import band,revolved

BODY=[(.55,.40),(.85,.50),(1.50,.61),(2.40,.65),(3.20,.61),(4.0,.50),(4.70,.36),(5.25,.24)]


def body_radius(z):
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(BODY,BODY[1:]) if za<=z<=zb)


def swept_pod(name,sections,angle,surface):
    obj=oval(name,[(z,r,r) for z,r,offset in sections],surface)
    for j,(_,_,offset) in enumerate(sections):
        for vertex in list(obj.data.vertices)[j*64:(j+1)*64]: vertex.co.y+=offset
    obj.rotation_euler.z=angle-math.pi/2
    smooth=obj.modifiers.new('Continuous swept pod skin','SUBSURF')
    smooth.levels=2;smooth.render_levels=2
    return obj


def trefoil_blade(name,angle,surface):
    count=25;rings=9;vertices=[]
    for lift in [.003,-.005]:
        for j in range(rings):
            radius=.10+.19*j/(rings-1)
            for i in range(count):
                theta=angle-.43+.86*i/(count-1)
                arc=radius*math.cos(theta);z=2.90+radius*math.sin(theta)
                r=body_radius(z);phi=-math.pi/2+arc/r
                vertices.append(((r+lift)*math.cos(phi),(r+lift)*math.sin(phi),z))
    size=count*rings;faces=[]
    for row in range(rings-1):
        for i in range(count-1):
            a=row*count+i;b=a+1;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for row in [0,rings-1]:
        for i in range(count-1):
            a=row*count+i;b=a+1;faces.append((a,a+size,b+size,b))
    for i in [0,count-1]:
        for row in range(rings-1):
            a=row*count+i;b=a+count;faces.append((a,b,b+size,a+size))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    finish(obj,name,surface,0)


def build():
    m=dict(body=material('Nuclear | deep blue titanium',(.018,.027,.055),.68,.39),
           yellow=material('Nuclear | yellow identification enamel',(.63,.49,.025),.30,.42),
           red=material('Nuclear | red ceramic tail shells',(.39,.085,.075),.42,.43),
           silver=material('Nuclear | silver side fittings',(.32,.36,.40),.74,.34),
           dark=material('Nuclear | recessed graphite',(.012,.015,.021),.30,.5),
           liner=material('Nuclear | refractory propulsion liner',(.17,.15,.13),.65,.45))
    revolved('Nuclear tapered dark pressure casing',BODY,m['body'])
    revolved('Nuclear long yellow tip',[(5.23,.245),(5.46,.205),(5.75,.135),(6.04,.065),(6.25,.012)],m['yellow'])
    band('Nuclear yellow tip seating ring',5.25,.247,.025,m['body'],.028)
    for angle in [math.pi/4+i*math.pi/2 for i in range(4)]:
        swept_pod('Nuclear swept red tail pod',[(.28,.10,.50),(.40,.18,.60),(.70,.25,.72),
            (1.10,.27,.76),(1.50,.20,.73),(1.80,.09,.65),(1.88,.02,.61)],angle,m['red'])
        foot=revolved('Nuclear silver tail foot',[(.20,.11),(.25,.14),(.30,.14),(.34,.095)],m['silver'])
        foot.location=(.50*math.cos(angle),.50*math.sin(angle),0)
    for sign in [-1,1]:
        angle=-math.pi/2+sign*1.0
        swept_pod('Nuclear upper silver side form',[(3.94,.02,.53),(4.13,.08,.50),
            (4.46,.13,.44),(4.72,.15,.39),(4.83,.10,.36)],angle,m['silver'])
    for angle in [math.pi/2,7*math.pi/6,11*math.pi/6]:
        trefoil_blade('Nuclear conformal yellow trefoil blade',angle,m['yellow'])
    skirt=shell('Nuclear hollow aft casing',[(.18,.28),(.35,.38),(.60,.44)],0,math.tau,
        dict(shell=m['body'],dark=m['dark']),64,.05)
    skirt.rotation_euler.x=math.pi/2
    bell=shell('Nuclear hollow propulsion bell',[(.07,.20),(.20,.23),(.32,.17),(.44,.10)],
        0,math.tau,dict(shell=m['liner'],dark=m['dark']),64,.03)
    bell.rotation_euler.x=math.pi/2
    cylinder('Nuclear recessed throat',(0,0,.49),.09,.025,m['dark'],vertices=48)
    # Transverse width is authored against the management silhouette; do this
    # in world space so rings and pod orientations preserve their height.
    for obj in list(bpy.context.collection.objects):
        if obj.type=='MESH':
            inverse=obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                point=obj.matrix_world @ vertex.co;point.x*=1.10;point.y*=1.10
                vertex.co=inverse @ point
