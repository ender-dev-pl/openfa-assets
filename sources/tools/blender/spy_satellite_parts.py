"""Independent first PS09 observation satellite; camera axis and hidden joints inferred."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,material
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

PROFILES={'Spy Satellite stem and lower globe':[(-1.1875,.035),(-1.09375,.22),(-.9375,.34),(-.75,.35),(-.5625,.26),(-.40625,.23),(-.34375,.25),(.4375,.29),(.75,.32),(.875,.30)],
 'Spy Satellite wide upper dome':[(.78125,.31),(.8125,1.03),(.90625,1.02),(1.03125,.85),(1.1875,.48),(1.25,.20),(1.28125,.11)]}
DENTS={'Spy Satellite stem and lower globe':(-math.pi/2,.12,.004),'Spy Satellite wide upper dome':(-math.pi/2,1.04,.004)}
SOCKETS={'SensorAxis':((0,-.405,-.90),(0,-1,0))}
BANDS=[('Spy Satellite stem band 0','Spy Satellite stem and lower globe',-.30,-.26),('Spy Satellite stem band 1','Spy Satellite stem and lower globe',.08,.12),('Spy Satellite stem band 2','Spy Satellite stem and lower globe',.47,.51),('Spy Satellite dome band','Spy Satellite wide upper dome',1.07,1.10)]


def build():
    m=dict(hull=material('Spy Satellite | worn green hull',(.10,.25,.16),.65,.56),bronze=material('Spy Satellite | aged bronze bands',(.31,.20,.08),.74,.61),
        edge=material('Spy Satellite | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Spy Satellite | soot graphite',(.012,.013,.017),.45,.76),gold=material('Spy Satellite | heat stained bronze',(.31,.20,.08),.78,.66))
    parts={name:vessel(name,profile,m['hull'],[DENTS[name]]) for name,profile in PROFILES.items()}
    for name,body,low,high in BANDS:
        rows=[(z,profile_radius(PROFILES[body],z)+.009,profile_radius(PROFILES[body],z)-.015) for z in [low,high]]
        annulus(name,(0,0),rows,m['bronze'],(0,(low+high)/2,0))
    cylinder('Spy Satellite crown cap',(0,0,1.282),.12,.025,m['edge'],vertices=64)
    for side in [-1,1]:
        # Small opaque plates are visible; photovoltaic function is not established.
        beam('Spy Satellite lateral strut '+str(side),(side*.74,0,.84),(side*1.24,0,.72),.022,m['edge'])
        box('Spy Satellite lateral plate '+str(side),(side*1.19,0,.715),(.45,.30,.045),m['hull'],.008)
        for i in range(4):box('Spy Satellite plate inset '+str(side)+' '+str(i),(side*1.19,-.11+i*.073,.741),(.35,.012,.012),m['dark'],.001)
        beam('Spy Satellite lower probe '+str(side),(side*.28,0,-.79),(side*.63,0,-.84),.007,m['edge'])
    body=parts['Spy Satellite stem and lower globe'];z=-.90;r=profile_radius(PROFILES[body.name],z);normal=Vector((0,-1,0));point=Vector((0,-r,z))+normal*.025
    cast_bezel('Spy Satellite sensor bezel',body,point,normal,.115,m['gold'])
    cylinder('Spy Satellite sensor dark face',point+normal*.028,.075,.018,m['dark'],vertices=64,rotation=normal.to_track_quat('Z','Y').to_euler())
    beam('Spy Satellite lower aerial',(0,0,-1.16),(0,0,-1.58),.007,m['edge'])
    cylinder('Spy Satellite aerial collar',(0,0,-1.18),.045,.08,m['bronze'],vertices=32)
    for i in range(6):
        phi=i*math.tau/6;r=profile_radius(PROFILES['Spy Satellite wide upper dome'],.87)
        cylinder('Spy Satellite rim fastener '+str(i),(r*math.cos(phi),r*math.sin(phi),.87),.012,.025,m['edge'],vertices=12,rotation=(Vector((math.cos(phi),math.sin(phi),0))).to_track_quat('Z','Y').to_euler())
    return m
