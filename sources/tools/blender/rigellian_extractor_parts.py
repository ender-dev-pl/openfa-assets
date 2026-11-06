"""First RI20 mining installation; no unsupported drilling mechanism is inferred."""
import math
from mathutils import Vector
from build_openfa_assets import material,cylinder
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel
from manufactured_profile_strips import strip

PROFILES={
 'RI20 bronze main housing':[(.30,.40),(.38,.49),(.60,.52),(1.10,.52),(1.26,.49),(1.60,.47),(1.73,.39),(1.85,.25),(1.92,.12),(1.94,.03)],
 'RI20 lower stepped drum':[(0,.25),(.04,.31),(.09,.32),(.12,.29),(.16,.29),(.18,.33),(.27,.33),(.31,.30),(.40,.30)],
 'RI20 bronze side module':[(.45,.08),(.50,.14),(1.17,.15),(1.24,.08)],
 'RI20 green lower fitting':[(.01,.03),(.04,.045),(.30,.045),(.36,.03)]}
PAINT={name:('green' if 'green' in name else 'bronze') for name in PROFILES}
CENTRES={name:(0,0) for name in PROFILES};CENTRES['RI20 bronze side module']=(-.43,-.12);CENTRES['RI20 green lower fitting']=(.26,-.20)
DENTS={'RI20 bronze main housing':(.5,.90,.003),'RI20 lower stepped drum':(-1.9,.20,.002),'RI20 bronze side module':(-1.5,.85,.002),'RI20 green lower fitting':(-1.6,.18,.001)}
SLOTS=[('RI20 lower dark inset 0',-1.25,.60,1.10,.045),('RI20 lower dark inset 1',-.95,.60,1.10,.045),('RI20 upper dark inset 0',-1.25,1.53,1.63,.070),('RI20 upper dark inset 1',-.95,1.53,1.63,.070)]


def stud(name,centre,phi,z,radius,surface,face_radius=.025):
    n=Vector((math.cos(phi),math.sin(phi),0));p=Vector((centre[0],centre[1],z))+n*(radius+.012)
    cylinder(name,p,face_radius,.040,surface,vertices=48,rotation=n.to_track_quat('Z','Y').to_euler())


def build():
    m=dict(bronze=material('RI20 | weathered bronze casing',(.29,.19,.065),.73,.56),
        green=material('RI20 | aged green lower alloy',(.12,.27,.18),.65,.56),
        edge=material('RI20 | worn brass fittings',(.42,.29,.085),.78,.49),
        dark=material('RI20 | recessed dark insets',(.048,.035,.016),.55,.68),
        steel=material('RI20 | dark bronze retaining alloy',(.15,.12,.048),.75,.54))
    objects={}
    for name,profile in PROFILES.items():
        obj=vessel(name,profile,m[PAINT[name]],[DENTS[name]]);obj.location.x,obj.location.y=CENTRES[name];objects[name]=obj
    for name,phi,low,high,width in SLOTS: strip(name,PROFILES['RI20 bronze main housing'],phi,low,high,width,m['dark'])
    for i,z in enumerate([.70,1.00]):
        stud(f'RI20 side round detail {i}',CENTRES['RI20 bronze side module'],-math.pi/2,z,profile_radius(PROFILES['RI20 bronze side module'],z),m['edge'])
    for i,z in enumerate([.69,.96]):
        stud(f'RI20 front round detail {i}',(0,0),-math.radians(115),z,profile_radius(PROFILES['RI20 bronze main housing'],z),m['edge'])
    for i,phi in enumerate([math.radians(-130),math.radians(-95),math.radians(-60)]):
        stud(f'RI20 lower service contact {i}',(0,0),phi,.22,profile_radius(PROFILES['RI20 lower stepped drum'],.22),m['edge'],.026)
    phi=-math.radians(115);z=1.53;r=profile_radius(PROFILES['RI20 bronze main housing'],z);n=Vector((math.cos(phi),math.sin(phi),.059)).normalized()
    p=Vector((r*math.cos(phi),r*math.sin(phi),z))+n*.025
    cast_bezel('RI20 upper round fitting bezel',objects['RI20 bronze main housing'],p,n,.105,m['steel'])
    cylinder('RI20 upper round fitting face',p+n*.028,.072,.016,m['edge'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
