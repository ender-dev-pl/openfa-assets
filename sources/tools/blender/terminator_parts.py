"""Independent first PS04 hull/wing layout; hidden geometry is interpreted."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,finish,material
from build_assault_fighter import plate
from terran_light_ship_parts import loft
from manufactured_annuli import annulus

SECTIONS=[(-1.65,.16,.02,.10),(-1.25,.35,.06,.17),(-.55,.58,.12,.34),(.15,.68,.13,.43),(.90,.65,.12,.40),(1.25,.53,.07,.30)]
DENTS=[(-.24,-.30,.007),(.27,.55,.006)]
CROSS=[(-1,-.55),(-1,.25),(-.65,.85),(0,1),(.65,.85),(1,.25),(1,-.55),(0,-1)]
SOCKETS={'Hardpoint forward':((0,-.67,.45),(0,-1,0)),'Hardpoint dorsal':((0,.50,.56),(0,0,1)),
 'Hardpoint port':((-1.05,.10,.075),(0,-1,0)),'Hardpoint starboard':((1.05,.10,.075),(0,-1,0)),
 'Engine port':((-.43,1.82,-.06),(0,1,0)),'Engine starboard':((.43,1.82,-.06),(0,1,0))}


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
    return mesh_object('Terminator continuous faceted hull',vertices,faces,surface)



def wing_point(side,u,t,lift=0):
    # Bilinear planform; height remains a single outward-sloping plane.
    inner=Vector((.48,-1.30,0)).lerp(Vector((.56,1.10,0)),t)
    outer=Vector((1.55,-.45,0)).lerp(Vector((2.10,1.65,0)),t)
    p=inner.lerp(outer,u);return (side*p.x,p.y,.09-.025*p.x+lift)


def build():
    m=dict(hull=material('Terminator | worn violet hull',(.15,.14,.21),.65,.56),red=material('Terminator | worn red markings',(.46,.025,.016),.45,.58),
        edge=material('Terminator | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Terminator | soot graphite',(.012,.013,.017),.45,.76),gold=material('Terminator | heat stained bronze',(.31,.20,.08),.78,.66))
    hull(m['hull'])
    for side in [-1,1]:
        plate('Terminator swept outer wing '+str(side),[wing_point(side,u,t) for u,t in [(0,0),(1,0),(1,1),(0,1)]],.11,m['hull'],.008)
        for i,(a,b) in enumerate([(.60,.78),(.83,.94)]):
            plate('Terminator red wing band '+str(side)+' '+str(i),[wing_point(side,u,t,.004) for u,t in [(.1,a),(1,a),(1,b),(.1,b)]],.012,m['red'],.001)
        # Raised longitudinal inner wing fairing enters the central hull.
        pod=loft('Terminator inner wing fairing '+str(side),[(-1.30,.085,.055,.09),(-.95,.17,.06,.14),(-.15,.21,.07,.17),(.72,.19,.07,.14),(1.12,.10,.05,.08)],m['hull'],rings=32);pod.location.x=side*.56
        engine=loft('Terminator aft engine housing '+str(side),[(.70,.23,-.065,.23),(1.15,.28,-.065,.26),(1.56,.24,-.065,.21)],m['hull'],rings=48);engine.location.x=side*.43
        nozzle=annulus('Terminator exhaust '+str(side),(0,0),[(0,.22,.16),(.10,.24,.165),(.30,.22,.155)],m['gold'],(0,.15,0));nozzle.rotation_euler=(-math.pi/2,0,0);nozzle.location=(side*.43,1.52,-.06)
        cylinder('Terminator exhaust throat '+str(side),(side*.43,1.56,-.06),.166,.025,m['dark'],vertices=64,rotation=(-math.pi/2,0,0))
        for i in range(10):
            a=i*math.tau/10;beam('Terminator cooling rib '+str(side)+' '+str(i),(side*.43+.224*math.cos(a),1.58,-.06+.224*math.sin(a)),(side*.43+.216*math.cos(a),1.80,-.06+.216*math.sin(a)),.009,m['edge'])
        beam('Terminator forward barrel '+str(side),(side*.11,-1.43,.025),(side*.11,-2.02,.025),.033,m['edge'])
        cylinder('Terminator bow collar '+str(side),(side*.11,-1.98,.025),.042,.09,m['gold'],vertices=32,rotation=(math.pi/2,0,0))
        beam('Terminator bow probe '+str(side),(side*.11,-2.01,.025),(side*.11,-2.18,.025),.010,m['edge'])
        # Flush maintenance strips along the body shoulder.
        points=[]
        for y,u in [(-.38,.66),(-.38,.83),(.63,.83),(.63,.66)]:
            w,z,h=section(y);v=.85-(u-.65)*(.60/.35);x=side*w*u;points.append((x,y,z+h*v-dent(x,y)+.007))
        plate('Terminator shoulder service strip '+str(side),points,.015,m['edge'],.001)
    # A sloping service vent sits on the crown, not in a floating rectangular box.
    points=[]
    for x,y in [(-.16,.10),(.16,.10),(.16,.42),(-.16,.42)]:
        w,z,h=section(y);points.append((x,y,z+h*(1-abs(x)/w*.15/.65)-dent(x,y)+.005))
    plate('Terminator crown vent frame',points,.022,m['edge'],.002)
    points=[]
    for x,y in [(-.12,.14),(.12,.14),(.12,.38),(-.12,.38)]:
        w,z,h=section(y);points.append((x,y,z+h*(1-abs(x)/w*.15/.65)-dent(x,y)+.009))
    plate('Terminator crown vent dark inset',points,.010,m['dark'],.001)
    for i in range(5):
        y=.16+i*.047;w,z,h=section(y)
        beam('Terminator crown vent fin '+str(i),(-.115,y,z+h*(1-.115/w*.15/.65)+.012),(.115,y,z+h*(1-.115/w*.15/.65)+.012),.006,m['edge'])
    plate('Terminator aft dorsal tab',[(-.19,1.02,.29),(.19,1.02,.29),(.19,1.73,.22),(-.19,1.73,.22)],.07,m['hull'],.005)
    return m
