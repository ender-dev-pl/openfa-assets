"""Independently authored RI12 research sensor tower; source pixels are reference only."""
import math
from mathutils import Vector
from build_openfa_assets import box,cylinder,material
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel

PROFILES={
 'RI12 ground pad':[(0,.78),(.035,.85),(.08,.90),(.12,.87),(.17,.70),(.18,.70),(.195,.56),(.205,.56),(.22,.30)],
 'RI12 lower pedestal':[(.14,.25),(.21,.28),(.26,.27),(.76,.24),(.83,.22),(.86,.22),(.87,.235),(.94,.235),(.96,.18)],
 'RI12 mast':[(.90,.145),(.97,.17),(1.04,.16),(2.05,.145),(2.09,.13)],
 'RI12 sensor head':[(2.73,.16),(2.77,.185),(2.81,.19),(3.17,.185),(3.22,.15),(3.25,.10)],
 'RI12 tapered tip':[(3.19,.09),(3.30,.105),(3.36,.095),(3.50,.095),(3.62,.095),(3.65,.105),(3.70,.105),(3.73,.085),(3.94,.085),(3.97,.055),(4.02,.055),(4.04,.03)]}
DENTS={'RI12 ground pad':(-2.2,.12,.003),'RI12 lower pedestal':(-1.7,.58,.003),
       'RI12 mast':(-1.5,1.65,.002),'RI12 sensor head':(-1.8,2.98,.002),'RI12 tapered tip':(-1.9,3.50,.001)}


def build():
    m=dict(body=material('RI12 | aged jade shell',(.12,.29,.22),.68,.53),
        edge=material('RI12 | machined aged neck alloy',(.24,.37,.30),.78,.47),
        dark=material('RI12 | graphite sensor housing',(.018,.027,.031),.50,.66),
        copper=material('RI12 | oxidised copper spindle',(.32,.19,.075),.78,.51),
        red=material('RI12 | worn red sensor inset',(.30,.035,.022),.40,.50),
        gold=material('RI12 | aged brass front fitting',(.39,.27,.08),.78,.49))
    parts={name:vessel(name,profile,m['body'],[DENTS[name]]) for name,profile in PROFILES.items()}
    cylinder('RI12 exposed copper spindle',(0,0,2.43),.065,.80,m['copper'],vertices=64)
    for i,z in enumerate([2.08,2.75]):
        cylinder(f'RI12 neck retaining collar {i}',(0,0,z),.115,.055,m['edge'],vertices=64)
    box('RI12 side sensor housing',(0,-.03,2.43),(.15,.18,.25),m['dark'],.006)
    box('RI12 red sensor inset',(0,-.122,2.43),(.11,.014,.13),m['red'],.002)
    box('RI12 opposite connector cover',(-.09,-.02,2.43),(.075,.08,.14),m['edge'],.005)
    for i,z in enumerate([2.34,2.52]):
        cylinder(f'RI12 housing captive fastener {i}',(0,-.123,z),.009,.012,m['edge'],vertices=6,rotation=(math.pi/2,0,0))
    point=Vector((0,-profile_radius(PROFILES['RI12 ground pad'],.165),.165))
    normal=Vector((0,-.28,.96)).normalized();point+=normal*.025
    cast_bezel('RI12 front fitting cast retaining bezel',parts['RI12 ground pad'],point,normal,.115,m['dark'])
    rotation=normal.to_track_quat('Z','Y');tx=rotation @ Vector((1,0,0));ty=rotation @ Vector((0,1,0))
    cylinder('RI12 brass inset fitting',point+normal*.028,.075,.016,m['gold'],vertices=64,rotation=rotation.to_euler())
    for i in range(4):
        angle=i*math.pi/2;position=point+normal*.028+.095*(math.cos(angle)*tx+math.sin(angle)*ty)
        cylinder(f'RI12 fitting captive screw {i}',position,.006,.012,m['edge'],vertices=6,rotation=rotation.to_euler())
    return m
