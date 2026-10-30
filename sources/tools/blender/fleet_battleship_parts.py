"""Independent first PS06 arched-wing ship; hidden sections and joints are interpreted."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,finish,material
from build_assault_fighter import plate
from terran_light_ship_parts import loft
from manufactured_annuli import annulus

SECTIONS=[(-2.75,.065,.04,.06),(-2.50,.20,.05,.15),(-2.0,.25,.05,.19),(-.85,.28,.06,.22),(-.48,.42,.07,.29),(.15,.48,.07,.32),(.72,.36,.04,.25)]
WING=[(-2.4,-.48,.22,.21,.085),(-2.10,-.35,.40,.26,.12),(-1.35,.04,.54,.35,.14),(-.6,.37,.58,.40,.16),(0,.45,.60,.42,.17),(.6,.37,.58,.40,.16),(1.35,.04,.54,.35,.14),(2.10,-.35,.40,.26,.12),(2.4,-.48,.22,.21,.085)]
CROSS=[(-1,-.55),(-1,.25),(-.65,.85),(0,1),(.65,.85),(1,.25),(1,-.55),(0,-1)]
DENTS=[(0,-1.70,.007),(0,-.67,.006)]
SOCKETS={'Hardpoint bow':((0,-1.55,.26),(0,-1,0)),'Hardpoint dorsal':((0,.28,.60),(0,0,1)),
 'Hardpoint port outer':((-2.10,-.35,.40),(0,0,1)),'Hardpoint port inner':((-.9,.20,.55),(0,0,1)),
 'Hardpoint starboard inner':((.9,.20,.55),(0,0,1)),'Hardpoint starboard outer':((2.10,-.35,.40),(0,0,1)),
 'Engine central':((0,1.39,-.18),(0,1,0))}


def interpolate(rows,value):
    for a,b in zip(rows,rows[1:]):
        if a[0]-1e-8<=value<=b[0]+1e-8:
            t=(value-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in range(1,len(a))]
    raise ValueError(value)


def section(y): return interpolate(SECTIONS,y)


def dent(x,y):return sum(d*math.exp(-2*(((x-cx)/.10)**2+((y-cy)/.16)**2)) for cx,cy,d in DENTS)


def mesh_object(name,vertices,faces,surface):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def wing_top(x,v):
    cy,depth,z,h=interpolate(WING,x);return (x,cy+depth*v,z+h*(1-abs(v)*.15/.65))


def wing(surface):
    stations=[]
    for a,b in zip(WING,WING[1:]):
        n=math.ceil((b[0]-a[0])/.04);stations.extend(a[0]+(b[0]-a[0])*i/n for i in range(n))
    stations.append(WING[-1][0]);cross=[]
    for a,b in zip(CROSS,CROSS[1:]+CROSS[:1]):cross.extend((a[0]+(b[0]-a[0])*i/4,a[1]+(b[1]-a[1])*i/4) for i in range(4))
    vertices=[]
    for x in stations:
        cy,depth,z,h=interpolate(WING,x);vertices.extend((x,cy+depth*u,z+h*v) for u,v in cross)
    count=len(cross);first=len(vertices);last=first+1;vertices.extend([(stations[0],WING[0][1],WING[0][3]),(stations[-1],WING[-1][1],WING[-1][3])]);end=(len(stations)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces += [(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(len(stations)-1) for i in range(count)]
    return mesh_object('Fleet Battleship continuous arched wing',vertices,faces,surface)


def marking(name,low,high,v0,v1,surface):
    count=math.ceil((high-low)/.035)+1;vertices=[]
    ring=[(v0,-.006),(v0,.006),(0,.006),(v1,.006),(v1,-.006),(0,-.006)] if v0<0<v1 else [(v0,-.006),(v0,.006),(v1,.006),(v1,-.006)]
    size=len(ring)
    for i in range(count):
        x=low+(high-low)*i/(count-1)
        for v,lift in ring:
            p=Vector(wing_top(x,v));p.z+=lift;vertices.append(tuple(p))
    faces=[tuple(reversed(range(size)))]
    for i in range(count-1):
        a=i*size;b=a+size;faces.extend((a+j,a+(j+1)%size,b+(j+1)%size,b+j) for j in range(size))
    faces.append(tuple((count-1)*size+j for j in range(size)))
    return mesh_object(name,vertices,faces,surface)


def build():
    m=dict(hull=material('Fleet Battleship | worn violet hull',(.15,.14,.21),.65,.56),red=material('Fleet Battleship | worn red markings',(.46,.025,.016),.45,.58),
        edge=material('Fleet Battleship | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Fleet Battleship | soot graphite',(.012,.013,.017),.45,.76),gold=material('Fleet Battleship | heat stained bronze',(.31,.20,.08),.78,.66))
    refined=[]
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        n=math.ceil((b[0]-a[0])/.035)
        refined.extend((y,*section(y)) for y in [a[0]+(b[0]-a[0])*i/n for i in range(n)])
    refined.append(SECTIONS[-1]);body=loft('Fleet Battleship long central hull',refined,m['hull'],rings=64)
    for vertex in body.data.vertices:
        if vertex.co.z>.05:vertex.co.z-=dent(vertex.co.x,vertex.co.y)
    body.data.update();wing(m['hull'])
    marking('Fleet Battleship broad red wing stripe',-2.24,2.24,-.20,.30,m['red'])
    for side in [-1,1]:
        a,b=sorted([side*.72,side*2.20]);marking('Fleet Battleship narrow red wing stripe '+str(side),a,b,.43,.54,m['red'])
        # Small solid tip shells and forward probes follow source projections.
        x=side*2.35;cy,depth,z,h=interpolate(WING,x)
        cylinder('Fleet Battleship tip fairing '+str(side),(x,cy,z),.10,.30,m['edge'],vertices=32,rotation=(math.pi/2,0,0))
        beam('Fleet Battleship tip probe '+str(side),(x,cy-.11,z),(x,cy-.37,z),.009,m['gold'])
    engine=loft('Fleet Battleship central engine housing',[(.15,.34,-.18,.29),(.55,.49,-.18,.38),(1.10,.40,-.18,.30)],m['hull'],rings=64)
    nozzle=annulus('Fleet Battleship central exhaust',(0,0),[(0,.36,.26),(.12,.39,.27),(.33,.36,.25)],m['gold'],(0,.15,0));nozzle.rotation_euler=(-math.pi/2,0,0);nozzle.location=(0,1.06,-.18)
    cylinder('Fleet Battleship exhaust throat',(0,1.10,-.18),.271,.025,m['dark'],vertices=64,rotation=(-math.pi/2,0,0))
    for i in range(16):
        a=i*math.tau/16;beam('Fleet Battleship cooling rib '+str(i),(.365*math.cos(a),1.12,-.18+.365*math.sin(a)),(.355*math.cos(a),1.37,-.18+.355*math.sin(a)),.009,m['edge'])
    # Transverse service collars on the narrow forward spine.
    for i,y in enumerate([-2.34,-1.95,-1.25,-.82]):
        w,z,h=section(y);points=[]
        for x,yy in [(-w*.60,y-.025),(w*.60,y-.025),(w*.60,y+.025),(-w*.60,y+.025)]:
            ww,zz,hh=section(yy);points.append((x,yy,zz+hh*math.sqrt(max(0,1-(x/ww)**2))+.004-dent(x,yy)))
        plate('Fleet Battleship spine service collar '+str(i),points,.018,m['edge'],.001)
    cylinder('Fleet Battleship red bow ring',(0,-2.50,.05),.205,.12,m['red'],vertices=64,rotation=(math.pi/2,0,0))
    beam('Fleet Battleship bow probe',(0,-2.65,.04),(0,-3.00,.04),.010,m['gold'])
    # Small crown service cover; exact panel layout remains interpreted.
    plate('Fleet Battleship dorsal service cover',[(-.16,-.40,.36),(.16,-.40,.36),(.16,-.12,.40),(-.16,-.12,.40)],.035,m['edge'],.002)
    return m
