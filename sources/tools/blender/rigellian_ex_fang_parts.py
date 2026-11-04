"""First RI22 collector weapon; hierarchy and concavity are authored interpretations."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,beam,finish
from manufactured_vessels import vessel
from manufactured_profile_strips import strip

RADIUS=.72;DEPTH=.16;THICKNESS=.035
DISH_CENTER=Vector((0,.15,1.15));DISH_AXIS=Vector((.85,.25,.46)).normalized();DISH_ROTATION=DISH_AXIS.to_track_quat('Z','Y')
PIVOT=Vector((0,0,.58));FEED_ORIGIN=DISH_CENTER-DISH_AXIS*.01;FEED_TIP=FEED_ORIGIN+DISH_AXIS*.40
PROFILES={
 'RI22 fixed green pedestal':[(0,.24),(.035,.31),(.35,.31),(.40,.34),(.46,.34),(.50,.25),(.60,.16)],
 'RI22 green yaw housing':[(.60,.12),(.65,.17),(.73,.17),(.80,.11),(.83,.04)],
 'RI22 copper collector feed':[(0,.09),(.05,.10),(.14,.065),(.30,.026),(.40,.009)]}
PAINT={name:('bronze' if 'copper' in name else 'green') for name in PROFILES};PAINT['RI22 concave collector shell']='green'
CENTRES={name:(0,0) for name in PAINT}
DENTS={'RI22 fixed green pedestal':(-1.7,.18,.002),'RI22 green yaw housing':(-1.6,.70,.001),'RI22 copper collector feed':(-1.7,.15,.001)}
MOVING=['RI22 green yaw housing','RI22 copper collector feed','RI22 concave collector shell','RI22 inclined green support','RI22 copper rear support']+[f'RI22 copper yoke cap {side}' for side in [-1,1]]+[f'RI22 collector fastener {i}' for i in range(4)]


def surface_z(x,y):
    dent=.002*math.exp(-2*(((x-.36)/.07)**2+(y/.06)**2))
    return DEPTH*(x*x+y*y)/(RADIUS*RADIUS)-dent


def collector(surface):
    count=128;rows=24;front=[(0,0,surface_z(0,0))]
    for row in range(1,rows+1):
        r=RADIUS*row/rows
        for i in range(count):
            phi=i*math.tau/count;x=r*math.cos(phi);y=r*math.sin(phi);front.append((x,y,surface_z(x,y)))
    size=len(front);vertices=front+[(x,y,z-THICKNESS) for x,y,z in front]
    faces=[(0,1+i,1+(i+1)%count) for i in range(count)]
    for row in range(rows-1):
        a=1+row*count;b=a+count
        for i in range(count):
            j=(i+1)%count;faces.append((a+i,b+i,b+j,a+j))
    faces += [tuple(size+i for i in reversed(face)) for face in list(faces)]
    a=1+(rows-1)*count
    faces += [(a+i,a+(i+1)%count,a+(i+1)%count+size,a+i+size) for i in range(count)]
    mesh=bpy.data.meshes.new('RI22 editable closed concave shell');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('RI22 concave collector shell',mesh);bpy.context.collection.objects.link(obj);finish(obj,obj.name,surface,0)
    for face in mesh.polygons: face.use_smooth=True
    obj.location=DISH_CENTER;obj.rotation_euler=DISH_ROTATION.to_euler()
    return obj


def build():
    m=dict(green=material('RI22 | weathered green armour',(.12,.29,.20),.65,.55),
        bronze=material('RI22 | aged copper feed',(.29,.15,.08),.73,.55),
        steel=material('RI22 | bearing alloy',(.20,.29,.27),.78,.51),
        frame=material('RI22 | green support alloy',(.09,.23,.16),.68,.57),
        copper=material('RI22 | worn copper fittings',(.30,.16,.08),.76,.55),
        gold=material('RI22 | bronze collector fittings',(.38,.27,.08),.77,.53),
        dark=material('RI22 | recessed base insets',(.02,.034,.03),.56,.67))
    parts={name:vessel(name,profile,m[PAINT[name]],[DENTS[name]]) for name,profile in PROFILES.items()}
    parts['RI22 copper collector feed'].location=FEED_ORIGIN;parts['RI22 copper collector feed'].rotation_euler=DISH_ROTATION.to_euler()
    collector(m['green'])
    cylinder('RI22 static yaw bearing',(0,0,.585),.135,.060,m['steel'],vertices=64)
    end=DISH_CENTER-DISH_AXIS*.02
    beam('RI22 inclined green support',(0,0,.75),end,.035,m['frame'])
    beam('RI22 copper rear support',(.10,0,.76),end,.045,m['copper'])
    for side in [-1,1]:
        n=Vector((side,0,0));cylinder(f'RI22 copper yoke cap {side}',(side*.18,0,.72),.065,.050,m['copper'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    for i in range(4):
        phi=math.pi/4+i*math.pi/2;x=.55*math.cos(phi);y=.55*math.sin(phi)
        local_n=Vector((-2*DEPTH*x/RADIUS**2,-2*DEPTH*y/RADIUS**2,1)).normalized();n=DISH_ROTATION @ local_n
        p=DISH_CENTER+DISH_ROTATION @ Vector((x,y,surface_z(x,y)))+n*.005
        cylinder(f'RI22 collector fastener {i}',p,.025,.030,m['gold'],vertices=6,rotation=n.to_track_quat('Z','Y').to_euler())
    for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6]):
        strip(f'RI22 lower base inset {i}',PROFILES['RI22 fixed green pedestal'],phi,.05,.32,.030,m['dark'])
    return m
