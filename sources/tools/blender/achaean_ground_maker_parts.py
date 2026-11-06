"""Independent first Ground Maker: profile dimensions are interpretations, not sprite extraction."""
import math
from mathutils import Matrix,Vector
from build_openfa_assets import material,box,cylinder
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
PREFIX='Achaean Ground Maker '
PROFILES={};LOCATIONS={};ROTATIONS={};PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.30,0),(0,-1,0))}
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
SHAPES={'shaft':[(-.96,.045),(-.85,.12),(.28,.12),(.34,.10)],'shoulder':[(.25,.11),(.40,.20),(.72,.21),(.85,.13)],'rear':[(.80,.12),(1.04,.12)],'tip':[(-1.20,.015),(-1.10,.055),(-.90,.055)]}
DENTS=[('shaft',-.50,.12,.006),('shoulder',.55,.21,.008)]
def orient(obj):
    for v in obj.data.vertices:v.co=Y_AXIS @ v.co
    obj.data.update();return obj
def build():
    m=dict(gold=material('Achaean Ground Maker | worn yellow olive shaft',(.18,.18,.025),.62,.72),red=material('Achaean Ground Maker | worn pink shoulder',(.46,.20,.16),.60,.72),accent=material('Achaean Ground Maker | worn green bands',(.10,.30,.08),.63,.75),dark=material('Achaean Ground Maker | dark joints',(.035,.025,.02),.5,.80),edge=material('Achaean Ground Maker | warm pale alloy',(.48,.31,.14),.65,.72))
    m['rear']=material('Achaean Ground Maker | red rear alloy',(.30,.025,.012),.63,.75)
    for name,profile in SHAPES.items():
        dents=[(3*math.pi/2,y,depth) for owner,y,r,depth in DENTS if owner==name]
        orient(vessel(PREFIX+name,profile,m[dict(shaft='gold',shoulder='red',rear='rear',tip='edge')[name]],dents))
    for i,y in enumerate([-.80,-.46,-.12,.20]):orient(annulus(PREFIX+'shaft band '+str(i),(0,0),[(y-.045,.13,.105),(y+.045,.13,.105)],m['accent'],(0,0,0)))
    for i,x in enumerate([-.25,.25]):box(PREFIX+'lateral shoulder '+str(i),(x,.70,0),(.22,.10,.09),m['red'],.012)
    for i,y in enumerate([.46,.66]):
        box(PREFIX+'service cover '+str(i),(0,y,.205),(.12,.10,.045),m['red'],.008)
        for j,x in enumerate([-.035,.035]):cylinder(PREFIX+'fastener '+str(i)+' '+str(j),(x,y,.23),.009,.03,m['edge'],16)
    orient(annulus(PREFIX+'red tip collar',(0,0),[(-1.02,.075,.040),(-.94,.075,.040)],m['rear'],(0,0,0)))
    return m
