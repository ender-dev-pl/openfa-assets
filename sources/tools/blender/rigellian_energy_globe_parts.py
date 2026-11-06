"""RI15 storage globe; source pixels are references, hidden engineering is inferred."""
import math
from mathutils import Vector
from build_openfa_assets import box,cylinder,material
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel

SPHERE=[(.55,.006)]+[(1.35+.80*math.sin(-math.pi/2+i*math.pi/96),.80*math.cos(-math.pi/2+i*math.pi/96)) for i in range(1,96)]+[(2.15,.006)]
SPHERE=[p for p in SPHERE if abs(p[0]-1.35)>.025]+[(1.325,.7996),(1.338,.786),(1.362,.786),(1.375,.7996)]
SPHERE.sort()
PROFILES={
 'RI15 low ground base':[(0,.45),(.04,.54),(.09,.60),(.14,.60),(.19,.56),(.23,.43),(.26,.28),(.29,.22)],
 'RI15 exposed brass stem':[(.17,.17),(.22,.18),(.26,.16),(.53,.16),(.57,.18),(.62,.17),(.68,.12)],
 'RI15 segmented storage globe':SPHERE}
PAINT={name:('bronze' if 'brass' in name else 'grey') for name in PROFILES}
CENTRES={name:(0,0) for name in PROFILES}
DENTS={'RI15 low ground base':(-1.7,.16,.003),'RI15 exposed brass stem':(-1.5,.42,.002),'RI15 segmented storage globe':(-2.2,1.62,.004)}
SEAMS=[-.9+i*math.pi/2 for i in range(4)]


def seam_depth(phi,z):
    return .014*max(0,1-((z-1.35)/.80)**2)*sum(math.exp(-(math.atan2(math.sin(phi-a),math.cos(phi-a))/.055)**2) for a in SEAMS)


def build():
    m=dict(bronze=material('RI15 | aged bronze housing',(.29,.19,.065),.73,.54),
        grey=material('RI15 | weathered grey alloy',(.26,.32,.38),.75,.53),
        edge=material('RI15 | fitting alloy',(.33,.41,.44),.78,.48),
        green=material('RI15 | green inspection face',(.105,.30,.20),.60,.54),
        dark=material('RI15 | graphite fitting recess',(.019,.030,.031),.48,.67),
        gold=material('RI15 | small brass base fitting',(.34,.23,.07),.76,.52))
    parts={name:vessel(name,profile,m[PAINT[name]],[DENTS[name]]) for name,profile in PROFILES.items()}
    globe=parts['RI15 segmented storage globe']
    for vertex in globe.data.vertices:
        x,y,z=vertex.co;phi=math.atan2(y,x);r=math.hypot(x,y);depth=seam_depth(phi,z)
        vertex.co.x*=1-depth/r;vertex.co.y*=1-depth/r
    globe.data.update()
    phi=-math.radians(45);z=1.30;r=profile_radius(SPHERE,z);normal=Vector((math.cos(phi),math.sin(phi),(z-1.35)/r)).normalized()
    point=Vector((r*math.cos(phi),r*math.sin(phi),z))+normal*.025
    cast_bezel('RI15 green face retaining bezel',globe,point,normal,.235,m['edge'])
    rotation=normal.to_track_quat('Z','Y')
    cylinder('RI15 green circular face',point+normal*.028,.180,.018,m['green'],vertices=96,rotation=rotation.to_euler())
    slit=box('RI15 dark vertical face inset',point+normal*.038,(.033,.102,.008),m['dark'],.002);slit.rotation_euler=rotation.to_euler()
    tx=rotation @ Vector((1,0,0));ty=rotation @ Vector((0,1,0))
    for i in range(6):
        a=i*math.tau/6
        cylinder(f'RI15 face captive fastener {i}',point+normal*.028+.207*(tx*math.cos(a)+ty*math.sin(a)),.008,.014,m['dark'],vertices=6,rotation=rotation.to_euler())
    phi=-math.radians(100);z=1.30;r=profile_radius(SPHERE,z)
    n=Vector((math.cos(phi),math.sin(phi),(z-1.35)/r)).normalized()
    p=Vector((r*math.cos(phi),r*math.sin(phi),z))+n*.025
    cast_bezel('RI15 small grey fitting bezel',globe,p,n,.135,m['edge'])
    cylinder('RI15 small grey fitting face',p+n*.028,.095,.018,m['edge'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    base=parts['RI15 low ground base'];z=.20;r=profile_radius(PROFILES['RI15 low ground base'],z)
    p=Vector((-.18,-math.sqrt(r*r-.18**2),z));n=Vector((p.x/r,p.y/r,3.25)).normalized();p+=n*.025
    cast_bezel('RI15 base brass fitting bezel',base,p,n,.090,m['dark'])
    cylinder('RI15 base brass fitting',p+n*.028,.054,.016,m['gold'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
