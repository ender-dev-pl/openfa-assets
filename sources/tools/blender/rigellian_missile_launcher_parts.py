"""Independent first RI18 silo; closed cap only, exact opening mechanism deferred."""
import math
from mathutils import Vector
from build_openfa_assets import material,cylinder,box,beam
from manufactured_vessels import vessel
from manufactured_annuli import annulus

BASE=[(0,.72,.20),(.04,.80,.20),(.45,.80,.20),(.50,.76,.20)]
UPPER=[(.44,.83,.20),(.50,.86,.20),(.56,.85,.20),(.59,.75,.20),(.62,.77,.20),(.68,.73,.20),(.71,.64,.20),(.74,.66,.20),(.80,.62,.20),(.83,.54,.20),(.86,.56,.20),(.98,.51,.20),(1.12,.45,.20),(1.24,.38,.20),(1.30,.30,.20),(1.35,.30,.20),(1.42,.29,.20),(1.62,.27,.20),(1.65,.25,.20)]
PROFILES={'RI18 closed silo cap':[(1.63,.25),(1.68,.26),(1.75,.24),(1.84,.18),(1.92,.10),(1.97,.02)]}
PAINT={'RI18 closed silo cap':'green','RI18 bronze foundation drum':'bronze','RI18 stepped green silo casing':'green'}
CENTRES={name:(0,0) for name in PAINT}
DENTS={'RI18 closed silo cap':(-1.7,1.78,.002)}
ANNULI={'RI18 bronze foundation drum':BASE,'RI18 stepped green silo casing':UPPER}
ANNULUS_DENTS={'RI18 bronze foundation drum':(-1.8,.25,.003),'RI18 stepped green silo casing':(-1.6,.95,.003)}
ATTACHMENT_START=Vector((.30,.12,1.22))
ATTACHMENT_END=Vector((.90,.36,1.94))


def build():
    m=dict(bronze=material('RI18 | aged bronze foundation',(.29,.19,.065),.73,.54),
        green=material('RI18 | weathered green casing',(.12,.29,.20),.65,.55),
        edge=material('RI18 | bronze exterior ribs',(.28,.18,.06),.74,.55),
        dark=material('RI18 | recessed silo mechanisms',(.018,.026,.029),.48,.72),
        fitting=material('RI18 | bronze angled attachment',(.32,.21,.07),.77,.52),
        connector=material('RI18 | green connector alloy',(.12,.27,.19),.66,.56))
    for name,rows in ANNULI.items(): annulus(name,(0,0),rows,m[PAINT[name]],ANNULUS_DENTS[name])
    vessel('RI18 closed silo cap',PROFILES['RI18 closed silo cap'],m['green'],[DENTS['RI18 closed silo cap']])
    cylinder('RI18 low silo floor',(0,0,.03),.24,.04,m['dark'],vertices=64)
    for i in range(12):
        phi=i*math.tau/12
        rib=box(f'RI18 bronze drum rib {i}',(.795*math.cos(phi),.795*math.sin(phi),.25),(.035,.045,.40),m['edge'],.004)
        rib.rotation_euler.z=phi
    for i,z in enumerate([.17,.34]):
        box(f'RI18 front drum band {i}',(0,-.802,z),(.25,.035,.035),m['edge'],.003)
    direction=(ATTACHMENT_END-ATTACHMENT_START).normalized()
    beam('RI18 angled bronze attachment',ATTACHMENT_START,ATTACHMENT_END,.060,m['fitting'])
    beam('RI18 angled attachment root sleeve',ATTACHMENT_START,ATTACHMENT_START+direction*.20,.090,m['connector'])
    return m
