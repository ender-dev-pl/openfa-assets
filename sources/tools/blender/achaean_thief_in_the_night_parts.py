"""Independent first Thief-in-the-Night: profile dimensions are interpretations, not sprite extraction."""
import math,bpy
from mathutils import Matrix,Vector
from build_openfa_assets import material,box,cylinder
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
PREFIX='Achaean Night Thief '
PROFILES={};LOCATIONS={};ROTATIONS={};PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.30,0),(0,-1,0))}
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
SHAPES={'shaft':[(-.96,.045),(-.85,.12),(.28,.12),(.34,.10)],'shoulder':[(.25,.11),(.40,.20),(.72,.21),(.85,.13)],'rear':[(.80,.12),(1.04,.12)],'tip':[(-1.20,.015),(-1.10,.055),(-.90,.055)]}
DENTS=[('shaft',-.50,.12,.006),('shoulder',.55,.21,.008)]
def orient(obj):
    for v in obj.data.vertices:v.co=Y_AXIS @ v.co
    obj.data.update();return obj
def build():
    m=dict(gold=material('Achaean Night Thief | worn brown shaft',(.115,.055,.04),.62,.72),red=material('Achaean Night Thief | worn pink shoulder',(.46,.20,.16),.60,.72),accent=material('Achaean Night Thief | worn ochre highlight',(.20,.135,.06),.63,.75),dark=material('Achaean Night Thief | dark joints',(.035,.025,.02),.5,.80),edge=material('Achaean Night Thief | cool pale alloy',(.25,.36,.55),.65,.72))
    m['rear']=material('Achaean Night Thief | red rear alloy',(.30,.025,.012),.63,.75)
    for name,profile in SHAPES.items():
        dents=[(3*math.pi/2,y,depth) for owner,y,r,depth in DENTS if owner==name]
        orient(vessel(PREFIX+name,profile,m[dict(shaft='gold',shoulder='red',rear='rear',tip='edge')[name]],dents))
    shaft=bpy.data.objects[PREFIX+'shaft'];shaft.data.materials.append(m['accent'])
    m['pale']=material('Achaean Night Thief | pink shaft markings',(.42,.18,.14),.45,.78);shaft.data.materials.append(m['pale'])
    for face in shaft.data.polygons:
        if face.center.z>.07: face.material_index=2 if (-.57<face.center.y<-.49 or .07<face.center.y<.15) else 1
    for i,x in enumerate([-.25,.25]):box(PREFIX+'lateral shoulder '+str(i),(x,.70,0),(.22,.10,.09),m['red'],.012)
    for i,y in enumerate([.46,.66]):
        box(PREFIX+'service cover '+str(i),(0,y,.205),(.12,.10,.045),m['red'],.008)
        for j,x in enumerate([-.035,.035]):cylinder(PREFIX+'fastener '+str(i)+' '+str(j),(x,y,.23),.009,.03,m['edge'],16)
    return m
