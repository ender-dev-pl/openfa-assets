"""Independent first RI17 weapons factory model; hidden machinery is not established."""
import math
from mathutils import Vector
from build_openfa_assets import material,cylinder,box
from manufactured_vessels import vessel
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

PROFILES={
 'RI17 green mast':[(0,.13),(.25,.13),(.28,.09),(1.43,.08),(1.50,.07)],
 'RI17 bronze mast head':[(1.40,.10),(1.48,.16),(1.58,.18),(1.72,.14),(1.78,.06),(2.28,.035),(2.32,.015)],
 'RI17 green interior unit':[(.12,.11),(.20,.12),(.62,.12),(.67,.10),(.72,.05),(.75,.025)]}
PAINT={'RI17 green mast':'green','RI17 bronze mast head':'bronze','RI17 green interior unit':'green','RI17 annular factory casing':'grey'}
CENTRES={'RI17 green mast':(-.55,-.50),'RI17 bronze mast head':(-.55,-.50),'RI17 green interior unit':(.12,0),'RI17 annular factory casing':(0,0)}
DENTS={'RI17 green mast':(-1.7,.80,.002),'RI17 bronze mast head':(-1.6,1.62,.002),'RI17 green interior unit':(-1.7,.50,.0015)}
CASING=[(.08,.78,.42),(.18,.94,.44),(.28,1.00,.45),(.42,1.02,.46),(.60,.96,.47),(.69,.83,.49),(.72,.75,.49)]
CASING_DENT=(-1.5,.44,.003)


def build():
    m=dict(bronze=material('RI17 | aged bronze head',(.29,.19,.065),.73,.54),
        green=material('RI17 | weathered green fittings',(.12,.29,.20),.65,.55),
        grey=material('RI17 | aged grey casing',(.26,.32,.38),.75,.53),
        edge=material('RI17 | machined joint alloy',(.34,.42,.45),.79,.49),
        dark=material('RI17 | recessed joint steel',(.025,.036,.039),.58,.67),
        red=material('RI17 | red inner panel',(.31,.028,.018),.40,.56))
    for name,profile in PROFILES.items():
        obj=vessel(name,profile,m[PAINT[name]],[DENTS[name]]);obj.location.x,obj.location.y=CENTRES[name]
    casing=annulus('RI17 annular factory casing',(0,0),CASING,m['grey'],CASING_DENT)
    cylinder('RI17 recessed assembly floor',(0,0,.10),.51,.08,m['dark'],vertices=96)
    for i in range(12):
        phi=i*math.tau/12
        rib=box(f'RI17 underside rib {i}',(.73*math.cos(phi),.73*math.sin(phi),.10),(.24,.09,.20),m['edge'],.008)
        rib.rotation_euler.z=phi
    box('RI17 red panel retaining frame',(-.22,.43,.42),(.14,.055,.38),m['dark'],.004)
    box('RI17 red inner wall panel',(-.22,.397,.42),(.095,.025,.34),m['red'],.003)
    p=Vector((-.12,-.66,.745));n=Vector((0,0,1))
    cast_bezel('RI17 front roof fitting bezel',casing,p,n,.09,m['edge'])
    cylinder('RI17 front roof fitting face',p+n*.028,.056,.018,m['edge'],vertices=64)
    return m
