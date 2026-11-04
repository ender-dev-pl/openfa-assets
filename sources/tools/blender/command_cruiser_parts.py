"""First independent PS08 long-deck ship; unseen construction remains interpretation."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,finish,material
from build_assault_fighter import plate
from terran_light_ship_parts import loft
from manufactured_annuli import annulus

SECTIONS=[(-2.0,.48,0,.24),(-1.75,.72,0,.28),(1.70,.72,0,.28),(1.95,.60,0,.23)]
CROSS=[(-1,-.55),(-1,.25),(-.65,1),(.65,1),(1,.25),(1,-.55),(.65,-1),(-.65,-1)]
DENTS=[(0,-1.15,.007),(.31,.62,.006)]
SOCKETS={'Hardpoint bow port':((-.24,-1.30,.30),(0,0,1)),'Hardpoint bow starboard':((.24,-1.30,.30),(0,0,1)),
 'Hardpoint aft port':((-.24,.60,.31),(0,0,1)),'Hardpoint aft starboard':((.24,.60,.31),(0,0,1)),
 'Hardpoint wing port':((-1.05,1.10,.06),(0,0,1)),'Hardpoint wing starboard':((1.05,1.10,.06),(0,0,1)),
 'Engine port':((-.30,2.30,-.10),(0,1,0)),'Engine starboard':((.30,2.30,-.10),(0,1,0))}


def section(y):
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        if a[0]-1e-8<=y<=b[0]+1e-8:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError(y)


def dent(x,y):return sum(d*math.exp(-2*(((x-cx)/.11)**2+((y-cy)/.16)**2)) for cx,cy,d in DENTS)


def mesh_object(name,vertices,faces,surface):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def hull(surface):
    rings=[]
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        n=math.ceil((b[0]-a[0])/.04)
        rings.extend(a[0]+(b[0]-a[0])*i/n for i in range(n))
    rings.append(SECTIONS[-1][0]);vertices=[]
    cross=[]
    for a,b in zip(CROSS,CROSS[1:]+CROSS[:1]):
        cross.extend((a[0]+(b[0]-a[0])*i/6,a[1]+(b[1]-a[1])*i/6) for i in range(6))
    for y in rings:
        w,z,h=section(y)
        for u,v in cross:
            x=w*u;vertices.append((x,y,z+h*v-(dent(x,y) if v>.25 else 0)))
    count=len(cross);first=len(vertices);last=first+1
    vertices.extend([(0,rings[0],section(rings[0])[1]),(0,rings[-1],section(rings[-1])[1])])
    end=(len(rings)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces += [(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(len(rings)-1) for i in range(count)]
    return mesh_object('Command Cruiser continuous faceted hull',vertices,faces,surface)




def build():
    m=dict(hull=material('Command Cruiser | worn violet hull',(.15,.14,.21),.65,.56),red=material('Command Cruiser | worn red markings',(.46,.025,.016),.45,.58),
        edge=material('Command Cruiser | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Command Cruiser | soot graphite',(.012,.013,.017),.45,.76),gold=material('Command Cruiser | heat stained bronze',(.31,.20,.08),.78,.66))
    hull(m['hull'])
    loft('Command Cruiser rounded bow',[(-2.94,.035,0,.04),(-2.70,.33,0,.22),(-2.36,.52,0,.28),(-2.02,.53,0,.26),(-1.83,.48,0,.20)],m['hull'],rings=64)
    box('Command Cruiser raised aft block',(0,1.36,.46),(1.10,.64,.46),m['hull'],.07)
    box('Command Cruiser aft dark grille',(0,1.693,.47),(.73,.025,.22),m['dark'],.006)
    for i in range(7):box('Command Cruiser aft grille bar '+str(i),(-.30+i*.10,1.713,.47),(.020,.018,.18),m['edge'],.002)
    for side in [-1,1]:
        # Continuous red edge band follows the vertical rectangular mid-body flank.
        box('Command Cruiser red flank '+str(side),(side*.722,0,.015),(.018,3.38,.055),m['red'],.002)
        points=[(side*.60,.58,.045),(side*1.28,.78,.025),(side*1.33,1.52,.025),(side*.61,1.58,.045)]
        plate('Command Cruiser outrigger wing '+str(side),points,.095,m['hull'],.008)
        for i,(a,b) in enumerate([(.83,1.05),(1.15,1.38)]):
            plate('Command Cruiser red outrigger band '+str(side)+' '+str(i),[(side*.75,a,.041),(side*1.28,a,.034),(side*1.30,b,.034),(side*.75,b,.041)],.015,m['red'],.001)
        beam('Command Cruiser outboard probe '+str(side),(side*1.25,1.23,.035),(side*1.25,.36,.035),.012,m['edge'])
        loft_obj=loft('Command Cruiser engine housing '+str(side),[(1.44,.18,-.10,.18),(1.75,.24,-.10,.22),(2.08,.21,-.10,.19)],m['hull'],rings=48);loft_obj.location.x=side*.30
        nozzle=annulus('Command Cruiser exhaust '+str(side),(0,0),[(0,.18,.125),(.10,.20,.135),(.28,.18,.125)],m['gold'],(0,.15,0));nozzle.rotation_euler=(-math.pi/2,0,0);nozzle.location=(side*.30,2.02,-.10)
        cylinder('Command Cruiser exhaust throat '+str(side),(side*.30,2.07,-.10),.136,.025,m['dark'],vertices=64,rotation=(-math.pi/2,0,0))
        for i in range(10):
            a=i*math.tau/10;beam('Command Cruiser cooling rib '+str(side)+' '+str(i),(side*.30+.185*math.cos(a),2.08,-.10+.185*math.sin(a)),(side*.30+.175*math.cos(a),2.28,-.10+.175*math.sin(a)),.007,m['edge'])
    # Dorsal service panels and edge framing interpret the visible rectangular divisions.
    for i,y in enumerate([-.76,.32]):
        box('Command Cruiser dorsal panel '+str(i),(0,y,.285),(.78,.66,.035),m['hull'],.012)
        for side in [-1,1]:box('Command Cruiser dorsal panel side rail '+str(i)+' '+str(side),(side*.40,y,.292),(.027,.70,.037),m['edge'],.003)
        for yy in [y-.34,y+.34]:box('Command Cruiser dorsal panel end rail '+str(i)+' '+str(yy),(0,yy,.292),(.80,.027,.037),m['edge'],.003)
        box('Command Cruiser dorsal panel inset '+str(i),(0,y,.307),(.24,.26,.016),m['dark'],.004)
        for j in range(4):box('Command Cruiser vent fin '+str(i)+' '+str(j),(0,y-.09+j*.06,.318),(.20,.012,.015),m['edge'],.002)
    for side in [-1,1]:
        for y in [-1.55,.90]:
            box('Command Cruiser small service cover '+str(side)+' '+str(y),(side*.36,y,.282),(.13,.22,.035),m['edge'],.004)
            cylinder('Command Cruiser service marker '+str(side)+' '+str(y),(side*.36,y,.309),.024,.012,m['gold'],vertices=24)
    # Narrow forehead collar embeds into both bow and deck.
    box('Command Cruiser bow collar',(0,-1.96,.18),(.77,.12,.10),m['edge'],.012)
    return m
