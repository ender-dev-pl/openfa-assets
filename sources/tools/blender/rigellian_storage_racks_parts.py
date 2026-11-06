"""First RI21 ore rack: six authored housings; hidden rack construction is inferred."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,box,beam
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel

ANGLES=[math.pi/2,7*math.pi/6,11*math.pi/6]
POD=[(.08,.12),(.12,.21),(.22,.28),(.68,.28),(.78,.22),(.86,.10),(.89,.02)]
PROFILES={};PAINT={};CENTRES={};DENTS={};LAYOUT={}
for tier in range(2):
    for index,phi in enumerate(ANGLES):
        name=f'RI21 storage housing {tier} {index}';offset=tier*.92
        PROFILES[name]=[(z+offset,r) for z,r in POD];PAINT[name]='bronze'
        CENTRES[name]=(.43*math.cos(phi),.43*math.sin(phi));DENTS[name]=(-1.7,.48+offset,.002)
        LAYOUT[(tier,index)]=name
FACE_KEYS=[key for key in LAYOUT if key!=(0,0)]
LEVELS=[.105,1.025]


def build():
    m=dict(bronze=material('RI21 | weathered bronze housings',(.29,.19,.065),.73,.56),
        green=material('RI21 | green oval faces',(.105,.29,.20),.55,.57),
        steel=material('RI21 | worn rack alloy',(.28,.36,.40),.78,.52),
        rim=material('RI21 | aged bronze face rims',(.24,.16,.05),.74,.59))
    objects={}
    for name,profile in PROFILES.items():
        obj=vessel(name,profile,m['bronze'],[DENTS[name]]);obj.location.x,obj.location.y=CENTRES[name];objects[name]=obj
    bpy.context.view_layer.update()
    n=Vector((0,-1,0))
    for tier,index in FACE_KEYS:
        name=LAYOUT[(tier,index)];cx,cy=CENTRES[name];z=.48+tier*.92;r=profile_radius(PROFILES[name],z)
        p=Vector((cx,cy-r,z))+n*.025
        cast_bezel(f'RI21 face bezel {tier} {index}',objects[name],p,n,.13,m['rim'])
        face=cylinder(f'RI21 green oval face {tier} {index}',p+n*.028,.10,.016,m['green'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
        face.scale.x=.72;face.scale.y=1.18
        bpy.context.view_layer.objects.active=face;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for side in [-1,1]:
        box(f'RI21 rear rack spine {side}',(side*.55,.30,.55),(.04,.05,1.10),m['steel'],.004)
        box(f'RI21 front guide {side}',(side*.13,-.36,.31),(.04,.05,.62),m['steel'],.004)
    for tier,z in enumerate(LEVELS):
        points=[Vector((*CENTRES[LAYOUT[(tier,i)]],z)) for i in range(3)]
        for i in range(3): beam(f'RI21 cradle edge {tier} {i}',points[i],points[(i+1)%3],.025,m['steel'])
        for side,index in [(-1,1),(1,2)]:
            beam(f'RI21 rear cradle tie {tier} {side}',(side*.55,.30,z),points[index],.025,m['steel'])
    for side in [-1,1]:
        beam(f'RI21 front guide foot tie {side}',(side*.13,-.215,.105),(side*.13,-.36,.105),.025,m['steel'])
    return m
