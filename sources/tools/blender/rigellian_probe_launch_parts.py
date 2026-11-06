"""Independent RI11 satellite construction/launch housing and genuinely open port."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,material
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel
from rigellian_construction_parts import subtract,tidy

PROFILE=[(0,.78),(.035,.84),(.075,.90),(.15,.90),(.205,.84),(.23,.81),(.28,.80),(.30,.74),(.32,.43),(.35,.36),(.57,.34),(.60,.33)]
DENT=(-2.2,.25,.003)
FITTING_Z=.245


def build():
    m=dict(body=material('RI11 | aged jade shell',(.12,.29,.22),.68,.53),
        edge=material('RI11 | machined aged port alloy',(.24,.37,.30),.78,.47),
        dark=material('RI11 | recessed graphite mechanisms',(.018,.027,.031),.50,.66),
        pale=material('RI11 | worn guide alloy',(.43,.50,.49),.80,.46),
        gold=material('RI11 | aged brass front fitting',(.39,.27,.08),.78,.49))
    body=vessel('RI11 stepped launch housing',PROFILE,m['body'],[DENT])
    cutter=cylinder('Temporary launch bore',(0,0,.45),.205,1.20,m['dark'],vertices=128)
    for modifier in list(cutter.modifiers): cutter.modifiers.remove(modifier)
    subtract(body,cutter);tidy(body)
    annulus('RI11 embedded open port liner',(0,0),[(.055,.212,.190),(.598,.212,.190)],m['edge'],(0,.3,0))
    cylinder('RI11 recessed launch mechanism floor',(0,0,.035),.218,.060,m['dark'],vertices=64)
    for i,phi in enumerate([math.pi/2-.45,math.pi/2,math.pi/2+.45]):
        normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-math.sin(phi),math.cos(phi),0))
        guide=box(f'RI11 internal port guide {i}',normal*.187+Vector((0,0,.315)),(.054,.020,.490),m['pale'],.002)
        guide.rotation_euler.z=phi-math.pi/2
        # A dark recessed track behind two attached wear strips; all remain on the wall.
        track=box(f'RI11 guide {i} recessed running track',normal*.176+Vector((0,0,.315)),(.026,.008,.450),m['dark'],.001)
        track.rotation_euler.z=phi-math.pi/2
        for side in [-1,1]:
            strip=box(f'RI11 guide {i} wear strip {side}',normal*.172+tangent*(side*.020)+Vector((0,0,.315)),(.010,.016,.466),m['pale'],.001)
            strip.rotation_euler.z=phi-math.pi/2
    point=Vector((0,-profile_radius(PROFILE,FITTING_Z),FITTING_Z));normal=Vector((0,-1,.5)).normalized();point+=normal*.035
    cast_bezel('RI11 front fitting cast retaining bezel',body,point,normal,.105,m['dark'])
    rotation=normal.to_track_quat('Z','Y');x_axis=rotation @ Vector((1,0,0));y_axis=rotation @ Vector((0,1,0))
    cylinder('RI11 front brass inset fitting',point+normal*.028,.064,.016,m['gold'],vertices=64,rotation=rotation.to_euler())
    for i in range(4):
        angle=i*math.pi/2;position=point+normal*.028+.083*(math.cos(angle)*x_axis+math.sin(angle)*y_axis)
        cylinder(f'RI11 front fitting captive screw {i}',position,.006,.012,m['edge'],vertices=6,rotation=rotation.to_euler())
    return m
