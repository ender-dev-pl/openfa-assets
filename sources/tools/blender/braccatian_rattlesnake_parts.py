"""First slender BR0A craft; fine ornament and hidden sections are authored inference."""
import math
import bpy
from build_openfa_assets import material,cylinder,finish

PROFILES={'Rattlesnake copper body':[(-1.5,.14,.08,.12),(-1.2,.27,.08,.21),(-.65,.30,.02,.20),(.05,.25,.015,.18),(.85,.20,.06,.17),(1.25,.23,.13,.23),(1.65,.22,.18,.26),(1.78,.06,.18,.11)],
 'Rattlesnake pale gold prow':[(-2.1,.018,.32,.028),(-1.95,.12,.28,.09),(-1.7,.24,.22,.17),(-1.42,.25,.12,.19),(-1.18,.18,.08,.15)]}
POWERS={'Rattlesnake copper body':3,'Rattlesnake pale gold prow':2}
DENTS={'Rattlesnake copper body':(.10,.40,.004),'Rattlesnake pale gold prow':(.08,-1.70,.003)}
SOCKETS={'AlignmentForward':((0,-2.14,.32),(0,-1,0))}
CROSS_BANDS=[-.98,-.50,.60,.90,1.10]
PATCHES=[]


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    cx,cy,depth=DENTS[name];return depth*math.exp(-2*(((x-cx)/.08)**2+((y-cy)/.11)**2))


def skin(name,x,y,upper=True):
    w,z,h=section(name,y);power=POWERS[name];q=h*max(0,1-abs(x/w)**power)**(1/power)
    return z+q-dent(name,x,y) if upper else z-q


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def hull(name,surface):
    rows=[];profile=PROFILES[name];count=96;power=POWERS[name]
    for a,b in zip(profile,profile[1:]):
        steps=math.ceil((b[0]-a[0])/.020);rows.extend(a[0]+(b[0]-a[0])*i/steps for i in range(steps))
    rows.append(profile[-1][0]);vertices=[]
    for y in rows:
        w,z,h=section(name,y)
        for i in range(count):
            phi=i*math.tau/count;c=math.cos(phi);s=math.sin(phi);x=w*math.copysign(abs(c)**(2/power),c);height=z+h*math.copysign(abs(s)**(2/power),s)
            if s>0:height-=dent(name,x,y)
            vertices.append((x,y,height))
    first=len(vertices);last=first+1;vertices.extend([(0,rows[0],profile[0][2]),(0,rows[-1],profile[-1][2])]);end=(len(rows)-1)*count
    faces=[(first,i,(i+1)%count) for i in range(count)]+[(last,end+(i+1)%count,end+i) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(rows)-1) for i in range(count))
    obj=mesh(name,vertices,faces,surface)
    for face in obj.data.polygons:face.use_smooth=len(face.vertices)==4
    return obj


def patch(name,owner,y0,y1,u0,u1,surface,lift=.007,depth=.025,upper=True):
    width=13;height=max(9,math.ceil((y1-y0)/.025)+1);size=width*height;vertices=[];direction=1 if upper else -1
    heights=[y0+(y1-y0)*i/(height-1) for i in range(height)]
    for y,_,_,_ in PROFILES[owner]:
        if y0<y<y1:heights=[h for h in heights if abs(h-y)>1e-8]+[y]
    heights.sort();height=len(heights);size=width*height
    for offset in [lift,lift-depth]:
        for y in heights:
            w,_,_=section(owner,y)
            for i in range(width):
                x=w*(u0+(u1-u0)*i/(width-1));vertices.append((x,y,skin(owner,x,y,upper)+direction*offset))
    faces=[]
    for row in range(height-1):
        for col in range(width-1):
            a=row*width+col;f=(a,a+1,a+width+1,a+width);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(width))+[row*width+width-1 for row in range(1,height)]+list(reversed(range((height-1)*width,(height-1)*width+width-1)))+[row*width for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    obj=mesh(name,vertices,faces,surface);PATCHES.append(dict(name=name,owner=owner,y0=y0,y1=y1,u0=u0,u1=u1,lift=lift,depth=depth,upper=upper));return obj


def fastener(name,owner,u,y,surface):
    w,_,_=section(owner,y);x=w*u;cylinder(name,(x,y,skin(owner,x,y)+.003),.012,.024,surface,vertices=16)


def build():
    PATCHES.clear()
    m=dict(hull=material('Rattlesnake | worn red copper hull',(.32,.125,.10),.68,.56),gold=material('Rattlesnake | tarnished pale gold',(.44,.32,.15),.75,.57),
        edge=material('Rattlesnake | oxidized service alloy',(.28,.22,.19),.72,.50),dark=material('Rattlesnake | carbon dark joints',(.018,.012,.012),.40,.78))
    owner='Rattlesnake copper body';prow='Rattlesnake pale gold prow'
    hull(owner,m['hull']);hull(prow,m['gold'])
    # A small, lavishly edged surface treatment is cultural extrapolation, not a clan insignia.
    for side in [-1,1]:
        patch('Rattlesnake long gold inlay '+str(side),owner,-.80,1.12,min(side*.62,side*.72),max(side*.62,side*.72),m['gold'])
    for i,y in enumerate(CROSS_BANDS):patch('Rattlesnake transverse gold inlay '+str(i),owner,y-.012,y+.012,-.58,.58,m['gold'])
    patch('Rattlesnake central service cover',owner,-.16,.34,-.45,.45,m['hull'])
    for i in range(4):
        y=-.08+i*.11;patch('Rattlesnake central service slot '+str(i),owner,y-.006,y+.006,-.32,.32,m['dark'],lift=.014,depth=.010)
    for side in [-1,1]:
        for i,y in enumerate([-.12,.30]):fastener('Rattlesnake cover fastener '+str(side)+' '+str(i),owner,side*.40,y,m['edge'])
    patch('Rattlesnake aft access panel',owner,1.24,1.55,-.62,.62,m['hull'])
    for i in range(3):
        y=1.29+i*.095;patch('Rattlesnake aft access slot '+str(i),owner,y-.006,y+.006,-.42,.42,m['dark'],lift=.014,depth=.010)
    for side in [-1,1]:fastener('Rattlesnake aft fastener '+str(side),owner,side*.53,1.40,m['edge'])
    patch('Rattlesnake copper prow stripe',prow,-1.86,-1.48,-.19,.19,m['hull'])
    for side in [-1,1]:
        for i,y in enumerate([-1.79,-1.52]):fastener('Rattlesnake prow fitting '+str(side)+' '+str(i),prow,side*.44,y,m['edge'])
    patch('Rattlesnake ventral service keel',owner,-.60,.90,-.48,.48,m['hull'],upper=False)
    for i in range(3):
        y=-.35+i*.44;patch('Rattlesnake ventral service slot '+str(i),owner,y-.008,y+.008,-.34,.34,m['dark'],lift=.014,depth=.010,upper=False)
    return m
