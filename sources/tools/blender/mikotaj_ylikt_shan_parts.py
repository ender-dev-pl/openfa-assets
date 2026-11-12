"""First MK1A interpretation: twin faceted rails connected by a compact transverse hull."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish

RAIL=[(-1.25,.045,.04,.045),(-1.10,.075,.055,.07),(-.55,.14,.06,.11),(.10,.16,.05,.14),(.60,.12,.025,.10),(1.15,.06,0,.055),(1.28,.035,0,.035)]
PROFILES={'Ylikt-shan port rail':RAIL,'Ylikt-shan starboard rail':RAIL,
 'Ylikt-shan transverse hull':[(-.26,.12,.08,.08),(-.16,.46,.08,.14),(.12,.46,.08,.14),(.24,.18,.07,.10)]}
CENTRES={'Ylikt-shan port rail':-.34,'Ylikt-shan starboard rail':.34,'Ylikt-shan transverse hull':0}
DENTS={'Ylikt-shan port rail':(.03,-.25,.003),'Ylikt-shan starboard rail':(-.025,.88,.003),'Ylikt-shan transverse hull':(.12,-.02,.004)}
SOCKETS={'AlignmentForward':((0,-1.32,.045),(0,-1,0))}
PATCHES=[]
CROSS=[]
for i in range(8):
    a=Vector((math.cos(math.pi/8+i*math.tau/8),math.sin(math.pi/8+i*math.tau/8)))
    b=Vector((math.cos(math.pi/8+(i+1)*math.tau/8),math.sin(math.pi/8+(i+1)*math.tau/8)))
    CROSS.extend(a.lerp(b,j/8) for j in range(8))


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    cx,cy,depth=DENTS[name];return depth*math.exp(-2*(((x-cx)/.08)**2+((y-cy)/.12)**2))


def skin(name,x,y):
    w,z,h=section(name,y);u=abs(x/w);s=math.sin(math.pi/8);c=math.cos(math.pi/8);assert u<=c+1e-7
    return z+h*(c if u<=s else c+s-u)-dent(name,x,y)


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def hull(name,surface):
    profile=PROFILES[name];heights=[];count=len(CROSS);vertices=[]
    for a,b in zip(profile,profile[1:]):
        steps=math.ceil((b[0]-a[0])/.018);heights.extend(a[0]+(b[0]-a[0])*i/steps for i in range(steps))
    heights.append(profile[-1][0])
    for y in heights:
        w,z,h=section(name,y)
        for p in CROSS:
            x=p.x*w;height=z+p.y*h-(dent(name,x,y) if p.y>0 else 0);vertices.append((x,y,height))
    first=len(vertices);last=first+1;vertices.extend([(0,heights[0],profile[0][2]),(0,heights[-1],profile[-1][2])]);end=(len(heights)-1)*count
    faces=[(first,i,(i+1)%count) for i in range(count)]+[(last,end+(i+1)%count,end+i) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(heights)-1) for i in range(count))
    obj=mesh(name,vertices,faces,surface);obj.location.x=CENTRES[name];return obj


def closed_surfaces(name,top,back,width,height,surface):
    size=len(top);vertices=top+back;faces=[]
    for row in range(height-1):
        for col in range(width-1):
            a=row*width+col;f=(a,a+1,a+width+1,a+width);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(width))+[row*width+width-1 for row in range(1,height)]+list(reversed(range((height-1)*width,(height-1)*width+width-1)))+[row*width for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));return mesh(name,vertices,faces,surface)


def patch(name,owner,y0,y1,u0,u1,surface,top=.006,back=-.014,support=None):
    steps=max(8,math.ceil((y1-y0)/.022));heights=[y0+(y1-y0)*i/steps for i in range(steps+1)];us=[u0+(u1-u0)*i/12 for i in range(13)]
    for y,_,_,_ in PROFILES[owner]:
        if y0<y<y1:heights=[h for h in heights if abs(h-y)>1e-8]+[y]
    for u in [-math.sin(math.pi/8),math.sin(math.pi/8)]:
        if u0<u<u1:us=[v for v in us if abs(v-u)>1e-8]+[u]
    heights.sort();us.sort();front=[];rear=[]
    for y in heights:
        w,_,_=section(owner,y)
        for u in us:
            x=w*u;z=skin(owner,x,y);front.append((CENTRES[owner]+x,y,z+top));rear.append((CENTRES[owner]+x,y,z+back))
    obj=closed_surfaces(name,front,rear,len(us),len(heights),surface);PATCHES.append(dict(name=name,owner=owner,y0=y0,y1=y1,u0=u0,u1=u1,top=top,back=back,support=support or owner));return obj


def band(name,owner,surface):
    heights=[-.05,.03];count=len(CROSS);size=count*len(heights);vertices=[]
    for offset in [.008,-.014]:
        for y in heights:
            w,z,h=section(owner,y);vertices.extend((CENTRES[owner]+p.x*(w+offset),y,z+p.y*(h+offset)) for p in CROSS)
    faces=[]
    for row in range(len(heights)-1):
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;faces.extend([(a,b,b+count,a+count),(a+size,a+count+size,b+count+size,b+size)])
    for row in [0,len(heights)-1]:
        for i in range(count):a=row*count+i;b=row*count+(i+1)%count;faces.append((a,a+size,b+size,b))
    return mesh(name,vertices,faces,surface)


def roof(name,x,y):
    obj=bpy.data.objects[name];inverse=obj.matrix_world.inverted();origin=Vector((CENTRES[name]+x,y,3));hit,p,normal,_=obj.ray_cast(inverse @ origin,(inverse.to_3x3() @ Vector((0,0,-1))).normalized());assert hit
    p=obj.matrix_world @ p;normal=(inverse.to_3x3().transposed() @ normal).normalized()
    if normal.z<0:normal=-normal
    return p,normal


def build():
    PATCHES.clear()
    m=dict(hull=material('Ylikt-shan | worn slate blue metal',(.10,.15,.24),.70,.61),gold=material('Ylikt-shan | dulled gold accents',(.32,.28,.08),.72,.63),
        edge=material('Ylikt-shan | oxidized service alloy',(.19,.23,.27),.78,.62),dark=material('Ylikt-shan | carbon dark seams',(.012,.015,.021),.40,.80))
    for name in PROFILES:hull(name,m['hull'])
    bridge='Ylikt-shan transverse hull';patch('Ylikt-shan bridge gold plate',bridge,-.09,.08,-.15,.15,m['gold'])
    for i,owner in enumerate(['Ylikt-shan port rail','Ylikt-shan starboard rail']):
        band('Ylikt-shan rail gold band '+str(i),owner,m['gold'])
        for label,y,depth,radius in [('fore',-1.245,.07,.027),('aft',1.265,.07,.025)]:
            _,z,_=section(owner,y);cylinder('Ylikt-shan '+label+' fitting '+str(i),(CENTRES[owner],y,z),radius,depth,m['edge'],vertices=32,rotation=(-math.pi/2,0,0))
        cover='Ylikt-shan rail service cover '+str(i);patch(cover,owner,.32,.70,-.55,.55,m['hull'])
        for j,y in enumerate([.39,.51,.63]):patch('Ylikt-shan rail service slot '+str(i)+' '+str(j),owner,y-.006,y+.006,-.28,.28,m['dark'],top=.012,back=.003,support=cover)
        patch('Ylikt-shan fore rail inset '+str(i),owner,-.95,-.45,-.20,.20,m['dark'],top=.004,back=-.012)
    bpy.context.view_layer.update()
    for i,owner in enumerate(['Ylikt-shan port rail','Ylikt-shan starboard rail']):
        for j,y in enumerate([.35,.67]):
            w,_,_=section(owner,y)
            for k,u in enumerate([-.33,.33]):
                p,normal=roof(owner,w*u,y);cylinder('Ylikt-shan cover fastener '+str(i)+' '+str(j)+' '+str(k),p+normal*.008,.006,.015,m['edge'],vertices=16,rotation=normal.to_track_quat('Z','Y').to_euler())
    return m
