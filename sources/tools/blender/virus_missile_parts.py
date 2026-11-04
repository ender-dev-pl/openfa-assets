"""Independent PM07/PM08 studies; matching runtime sprites do not imply one model."""
import math

import bpy

from build_openfa_assets import cylinder,finish,material
from build_shield_equipment import shell
from cannon_equipment_parts import oval
from terran_missile_parts import band,revolved

VIRUS=[(1.30,.36),(1.55,.48),(2.0,.60),(2.70,.65),(3.40,.61),(4.0,.48),(4.35,.34),(4.70,.29),(5.15,.26)]
ANTI=[(1.30,.36),(1.55,.45),(2.0,.55),(2.60,.60),(3.20,.56),(3.80,.46),(4.40,.35),(5.15,.27)]


def radius_at(profile,z):
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(profile,profile[1:]) if za<=z<=zb)


def side_form(name,z0,height,width,depth,angle,profile,surface):
    sections=[]
    for i in range(25):
        theta=math.pi*i/24;z=z0-height*math.cos(theta);s=math.sin(theta)
        sections.append((z,max(.008,width*s),.012+depth*s,radius_at(profile,z)-.03))
    obj=oval(name,[(z,rx,ry) for z,rx,ry,offset in sections],surface)
    for j,(_,_,_,offset) in enumerate(sections):
        for vertex in list(obj.data.vertices)[j*64:(j+1)*64]: vertex.co.y+=offset
    obj.rotation_euler.z=angle-math.pi/2
    return obj


def skirt(m):
    revolved('Virus family violet skirt underlayer',[(.46,.44),(.65,.48),(.95,.43),(1.40,.33)],m['violet'])
    count=96;profile=[(.65,.50,.27),(.98,.49,0),(1.43,.34,0)];size=len(profile)*count;vertices=[]
    for inner in [False,True]:
        for z,r,wave in profile:
            rad=r-.06 if inner else r
            vertices += [(rad*math.cos(i*math.tau/count),rad*math.sin(i*math.tau/count),
                          z+wave*math.cos(4*i*math.tau/count)) for i in range(count)]
    faces=[]
    for row in range(len(profile)-1):
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for row in [0,len(profile)-1]:
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;faces.append((a,a+size,b+size,b))
    mesh=bpy.data.meshes.new('Thick four-lobed skirt');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('Virus family scalloped olive skirt',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,m['body'],0)
    for index,face in enumerate(mesh.polygons): face.use_smooth=index<(len(profile)-1)*count*2


def build(anti=False):
    m=dict(body=material('Virus family | olive titanium',(.19,.195,.155),.65,.44),
           bronze=material('Virus | bronze side capsules',(.35,.20,.105),.67,.38),
           violet=material('Anti Virus | violet side casing',(.16,.11,.23),.57,.41),
           red=material('Virus family | red nozzle jackets',(.36,.065,.055),.43,.43),
           trim=material('Virus family | antenna alloy',(.33,.36,.37),.78,.34),
           dark=material('Virus family | recessed graphite',(.012,.017,.02),.3,.5),
           yellow=material('Virus | yellow nose collar',(.52,.45,.045),.3,.44),
           white=material('Anti Virus | pale nose insulator',(.50,.51,.44),.15,.48))
    profile=ANTI if anti else VIRUS
    revolved('Anti Virus long-neck pressure casing' if anti else 'Virus two-row pressure casing',profile,m['body'])
    band('Virus family upper neck joint',4.40,.355 if anti else .334,.026,m['body'],.035)
    if anti:
        for i in range(4):
            side_form('Anti Virus long violet side form',2.90,.75,.22,.19,-math.pi/2+i*math.pi/2,profile,m['violet'])
    else:
        for z,h,w,d in [(2.25,.55,.22,.19),(3.52,.62,.24,.22)]:
            for i in range(4):
                side_form('Virus bronze side form',z,h,w,d,-math.pi/2+i*math.pi/2,profile,m['bronze'])
    skirt(m)
    band('Anti Virus pale nose collar' if anti else 'Virus yellow nose collar',5.18,.275,.15,
         m['white'] if anti else m['yellow'],.04)
    revolved('Virus family red nose cap',[(5.22,.25),(5.35,.19),(5.49,.055)],m['red'])
    cylinder('Virus family long antenna' if not anti else 'Anti Virus shorter antenna',
        (0,0,6.08 if not anti else 5.80),.016,1.20 if not anti else .66,m['trim'],vertices=24)
    for i,(x,y) in enumerate([(-.16,-.16),(.16,-.16),(-.16,.16),(.16,.16)]):
        nozzle=shell('Virus family hollow red nozzle',[(.07,.11),(.16,.115),(.43,.105),(.49,.10)],
            0,math.tau,dict(shell=m['red'],dark=m['dark']),48,.025)
        nozzle.rotation_euler.x=math.pi/2;nozzle.location=(x,y,0)
        cylinder('Virus family recessed nozzle throat',(x,y,.405),.075,.025,m['dark'],vertices=32)

    # Reference-based transverse proportions, applied in world coordinates.
    for obj in list(bpy.context.collection.objects):
        if obj.type=='MESH':
            inverse=obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                point=obj.matrix_world @ vertex.co;point.x*=1.10;point.y*=1.10
                vertex.co=inverse @ point
