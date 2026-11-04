"""Independent RI16 shield installation; hidden interfaces are authored interpretations."""
import math
from mathutils import Vector
from build_openfa_assets import material,cylinder,beam
from manufactured_vessels import vessel

PROFILES={'RI16 bronze generator head':[(1.64,.20),(1.66,.24),(1.73,.24),(1.76,.16),(1.80,.17),(1.88,.17),(1.95,.14),(2.00,.105),(2.08,.095),(2.17,.10),(2.24,.16),(2.51,.18),(2.54,.18),(2.553,.170),(2.568,.170),(2.58,.18),(2.66,.18),(2.75,.16),(2.82,.10),(2.86,.07)]}
PAINT={'RI16 bronze generator head':'bronze'}
CENTRES={'RI16 bronze generator head':(0,0)}
DENTS={'RI16 bronze generator head':(-1.6,2.40,.0025)}
ANGLES=[-math.pi/2,math.pi/6,5*math.pi/6]
POD=[(.28,.02),(.30,.14),(.34,.23),(.40,.28),(.50,.30),(.64,.30),(.652,.289),(.668,.289),(.68,.30),(.73,.26),(.80,.15),(.82,.02)]
POD=[(.28+(z-.28)*1.25,r*1.15) for z,r in POD]
FOOT=[(0,.13),(.025,.17),(.055,.17),(.080,.12)]
for i,phi in enumerate(ANGLES):
    pod=f'RI16 green lower housing {i}';rod=f'RI16 vertical alloy support {i}';foot=f'RI16 ground foot {i}'
    PROFILES[pod]=POD;PAINT[pod]='green';CENTRES[pod]=(.45*math.cos(phi),.45*math.sin(phi));DENTS[pod]=(-1.7,.53,.0025)
    PROFILES[rod]=[(.35,.040),(1.71875,.040)];PAINT[rod]='grey';CENTRES[rod]=(.12*math.cos(phi),.12*math.sin(phi));DENTS[rod]=(-1.4,1.20,.0007)
    PROFILES[foot]=FOOT;PAINT[foot]='grey';CENTRES[foot]=CENTRES[pod];DENTS[foot]=(-1.8,.045,.001)


def build():
    m=dict(bronze=material('RI16 | aged bronze head',(.29,.19,.065),.73,.54),
        green=material('RI16 | weathered green housings',(.12,.29,.20),.65,.55),
        grey=material('RI16 | aged support alloy',(.26,.32,.38),.75,.51),
        edge=material('RI16 | machined joint alloy',(.34,.42,.45),.79,.49),
        dark=material('RI16 | recessed joint steel',(.025,.036,.039),.58,.63))
    for name,profile in PROFILES.items():
        obj=vessel(name,profile,m[PAINT[name]],[DENTS[name]])
        obj.location.x,obj.location.y=CENTRES[name]
    for i,phi in enumerate(ANGLES):
        n=Vector((math.cos(phi),math.sin(phi),0))
        cylinder(f'RI16 housing foot stem {i}',n*.45+Vector((0,0,.18)),.055,.25,m['edge'],vertices=32)
        beam(f'RI16 housing radial brace {i}',n*.12+Vector((0,0,.45)),n*.45+Vector((0,0,.55)),.045,m['edge'])
        cylinder(f'RI16 flange captive screw {i}',n*.20+Vector((0,0,1.735)),.011,.024,m['dark'],vertices=6)
    return m
