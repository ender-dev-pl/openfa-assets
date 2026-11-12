"""Independent first RI23 twin-lance assembly; unseen joints are interpretations."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel
from manufactured_profile_strips import strip

PROFILES={
 'RI23 fixed bronze skirt':[(0,.36),(.035,.46),(.22,.46),(.25,.43)],
 'RI23 fixed green pedestal':[(.22,.43),(.28,.49),(.44,.48),(.65,.36),(.84,.27),(.96,.23),(1.00,.21)],
 'RI23 rotating green head':[(.99,.15),(1.04,.22),(1.12,.25),(1.24,.23),(1.30,.17),(1.34,.06)],
 'RI23 bronze lance -1':[(0,.095),(.10,.095),(.29,.078),(.65,.044),(.95,.009)],
 'RI23 bronze lance 1':[(0,.095),(.10,.095),(.29,.078),(.65,.044),(.95,.009)]}
PAINT={name:('bronze' if 'bronze' in name else 'green') for name in PROFILES}
CENTRES={name:(0,0) for name in PROFILES}
DENTS={'RI23 fixed bronze skirt':(-2.2,.13,.002),'RI23 fixed green pedestal':(-2.2,.50,.003),
 'RI23 rotating green head':(-1.9,1.18,.002),'RI23 bronze lance -1':(-1.7,.45,.0015),'RI23 bronze lance 1':(-1.9,.60,.0015)}
PIVOT=Vector((0,0,1.0));LANCE_AXIS=Vector((.64,.12,.76)).normalized()
LANCE_STARTS={side:Vector((0,side*.18,1.17)) for side in [-1,1]}
LANCE_TIPS={side:start+LANCE_AXIS*.95 for side,start in LANCE_STARTS.items()}
MOVING=['RI23 rotating green head','RI23 bronze lance -1','RI23 bronze lance 1']


def build():
    m=dict(green=material('RI23 | weathered green armour',(.12,.29,.20),.65,.55),
        bronze=material('RI23 | aged bronze fittings',(.34,.23,.09),.74,.54),
        edge=material('RI23 | bearing alloy',(.25,.34,.32),.78,.48),
        dark=material('RI23 | recessed joint steel',(.021,.032,.034),.55,.67))
    parts={name:vessel(name,profile,m[PAINT[name]],[DENTS[name]]) for name,profile in PROFILES.items()}
    for side,start in LANCE_STARTS.items():
        lance=parts['RI23 bronze lance '+str(side)];lance.location=start;lance.rotation_euler=LANCE_AXIS.to_track_quat('Z','Y').to_euler()
    cylinder('RI23 static yaw bearing',(0,0,.995),.17,.090,m['edge'],vertices=64)
    strip('RI23 bronze front strip',PROFILES['RI23 fixed green pedestal'],-math.pi/2,.30,.82,.055,m['bronze'])
    for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6]):
        strip(f'RI23 lower base inset {i}',PROFILES['RI23 fixed bronze skirt'],phi,.055,.205,.045,m['dark'])
    body=parts['RI23 fixed green pedestal'];z=.49;phi=-math.radians(115);r=profile_radius(PROFILES[body.name],z)
    normal=Vector((math.cos(phi),math.sin(phi),.57)).normalized();point=Vector((r*math.cos(phi),r*math.sin(phi),z))+normal*.025
    cast_bezel('RI23 base fitting bezel',body,point,normal,.09,m['edge'])
    cylinder('RI23 bronze base fitting',point+normal*.028,.055,.016,m['bronze'],vertices=64,rotation=normal.to_track_quat('Z','Y').to_euler())
    # A small fixed green spur is visible in the source base; its cross-section is inferred.
    from build_openfa_assets import beam
    beam('RI23 fixed green spur',(.13,.07,.75),(.45,.11,.91),.025,material('RI23 | worn green spur',(.10,.24,.16),.68,.61))
    return m
