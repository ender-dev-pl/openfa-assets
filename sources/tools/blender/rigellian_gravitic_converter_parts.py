"""Independently authored RI13 converter; exact hidden engineering is inferred."""
import math
from mathutils import Vector
from build_openfa_assets import box,cylinder,material,beam
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel

SPHERE=[(1.60,.09)]+[(2.25+.65*math.sin(a),.65*math.cos(a)) for a in [(-math.pi/2)+i*math.pi/64 for i in range(3,62)]]+[(2.90,.09)]
SPHERE=sorted(SPHERE)
# An authored shallow assembly seam, rather than an unsupported moving mechanism.
SPHERE=[pair for pair in SPHERE if abs(pair[0]-2.25)>.02]+[(2.23,.649),(2.242,.637),(2.258,.637),(2.27,.649)]
SPHERE.sort()
PROFILES={
 'RI13 flared ground foot':[(0,.55),(.05,.66),(.11,.73),(.16,.72),(.20,.66),(.26,.57),(.56,.32),(.67,.29),(.70,.30),(.76,.30),(.80,.27),(.84,.27)],
 'RI13 lower equipment drum':[(.78,.25),(.85,.31),(.91,.35),(1.00,.36),(1.03,.36),(1.045,.349),(1.06,.36),(1.57,.34),(1.61,.32),(1.68,.24)],
 'RI13 spherical converter housing':SPHERE,
 'RI13 segmented upper probe':[(2.82,.07),(2.97,.07),(3.00,.10),(3.12,.10),(3.15,.135),(3.50,.135),(3.54,.10),(3.57,.08),(3.64,.08),(3.66,.095),(3.70,.095),(3.72,.08),(3.82,.08),(3.84,.095),(3.88,.095),(3.90,.08),(4.01,.08),(4.05,.05),(4.10,.04)]}
PAINT={name:('green' if 'foot' in name else 'grey') for name in PROFILES}
CENTRES={name:(0,0) for name in PROFILES}
DENTS={'RI13 flared ground foot':(-2.2,.20,.003),'RI13 lower equipment drum':(-1.9,1.35,.003),
 'RI13 spherical converter housing':(-1.7,2.43,.004),'RI13 segmented upper probe':(-1.5,3.34,.002)}
for side in [-1,1]:
    name=f'RI13 green side riser {side}'
    PROFILES[name]=[(.94,.07),(1.01,.095),(1.06,.095),(1.10,.055),(2.57,.055),(2.60,.045)]
    PAINT[name]='green';CENTRES[name]=(side*.48,-.30);DENTS[name]=(-1.5,1.86,.0015)


def curve_shift(name,z):
    if 'side riser' not in name or z<=1.70: return 0.0
    target=-math.sqrt(max(.001,profile_radius(SPHERE,max(1.85,min(2.60,z)))**2-.48**2))-.015
    blend=min(1,(z-1.70)/.20)
    return (target+.30)*blend


def build():
    m=dict(detailgreen=material('RI13 | green fitting alloy',(.10,.23,.16),.65,.55),
        green=material('RI13 | weathered green alloy',(.10,.23,.16),.65,.55),
        grey=material('RI13 | aged grey housing',(.26,.32,.34),.73,.50),
        dark=material('RI13 | graphite joints',(.018,.027,.031),.50,.65),
        red=material('RI13 | red service insets',(.31,.035,.022),.40,.52),
        edge=material('RI13 | machined fitting alloy',(.34,.42,.43),.78,.44))
    parts={}
    for name,profile in PROFILES.items():
        obj=vessel(name,profile,m[PAINT[name]],[DENTS[name]])
        for vertex in obj.data.vertices: vertex.co.y+=curve_shift(name,vertex.co.z)
        obj.data.update()
        obj.location.x,obj.location.y=CENTRES[name];parts[name]=obj
    cylinder('RI13 red neck collar',(0,0,2.955),.073,.055,m['red'],vertices=64)
    for side in [-1,1]:
        for i,z in enumerate([1.09,1.55]):
            box(f'RI13 riser support {side} {i}',(side*.40,-.20,z),(.26,.24,.10),m['detailgreen'],.01)
        cylinder(f'RI13 side service pod {side}',(side*.48,-.30,1.23),.12,.30,m['edge'],vertices=64)
        cylinder(f'RI13 side red inset {side}',(side*.48,-.417,1.23),.065,.024,m['red'],vertices=64,rotation=(math.pi/2,0,0))
        for z in [1.14,1.32]:
            cylinder(f'RI13 side pod captive screw {side} {z}',(side*.48,-.411,z),.009,.018,m['dark'],vertices=6,rotation=(math.pi/2,0,0))
    box('RI13 lower front panel frame',(.12,-.34,1.28),(.24,.045,.51),m['dark'],.007)
    box('RI13 lower front panel',(.12,-.37,1.28),(.18,.035,.45),m['edge'],.005)
    for i,x in enumerate([-.23,-.15,-.07]):
        ends=[]
        for z in [1.08,1.48]:
            r=profile_radius(PROFILES['RI13 lower equipment drum'],z)
            ends.append((x,-math.sqrt(r*r-x*x)-.006,z))
        beam(f'RI13 lower front vertical stiffener {i}',ends[0],ends[1],.016,m['edge'])
    foot=parts['RI13 flared ground foot'];r=profile_radius(PROFILES['RI13 flared ground foot'],.32)
    point=Vector((.18,-math.sqrt(r*r-.18**2),.32));normal=Vector((point.x/r,point.y/r,.8333333333)).normalized();point+=normal*.025
    cast_bezel('RI13 foot service fitting bezel',foot,point,normal,.105,m['edge'])
    cylinder('RI13 foot service fitting face',point+normal*.028,.067,.018,m['edge'],vertices=64,rotation=normal.to_track_quat('Z','Y').to_euler())
    body=parts['RI13 spherical converter housing'];point=Vector((0,-profile_radius(SPHERE,2.30),2.30));normal=Vector((0,-1,0));point+=normal*.025
    cast_bezel('RI13 spherical front fitting bezel',body,point,normal,.17,m['edge'])
    rotation=normal.to_track_quat('Z','Y')
    cylinder('RI13 green front inspection face',point+normal*.028,.115,.018,m['detailgreen'],vertices=64,rotation=rotation.to_euler())
    tx=rotation @ Vector((1,0,0));ty=rotation @ Vector((0,1,0))
    for i in range(6):
        phi=i*math.tau/6
        cylinder(f'RI13 fitting captive fastener {i}',point+normal*.028+.145*(tx*math.cos(phi)+ty*math.sin(phi)),.008,.014,m['dark'],vertices=6,rotation=rotation.to_euler())
    return m
