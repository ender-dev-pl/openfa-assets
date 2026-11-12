"""Independent first RI3C transport; inline module depths and hidden joints inferred."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,material
from terran_light_ship_parts import loft

PROFILES={'Transportation slate forward module':[(-2.10,.08,.02,.06),(-1.90,.45,.08,.22),(-1.35,.78,.11,.40),(-.85,.74,.12,.38),(-.40,.38,.08,.22),(-.25,.17,.05,.12)],
 'Transportation green aft module':[(-.35,.16,.05,.12),(-.10,.40,.10,.23),(.45,.65,.14,.34),(.95,.54,.12,.27),(1.40,.25,.06,.12),(1.75,.04,.02,.04)]}
DENTS={'Transportation slate forward module':(.30,-1.30,.005),'Transportation green aft module':(-.28,.60,.004)}
SOCKETS={'AlignmentForward':((0,-2.24,.02),(0,-1,0))}


def section(name,y):
    rows=PROFILES[name]
    for a,b in zip(rows,rows[1:]):
        if a[0]-1e-8<=y<=b[0]+1e-8:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    cx,cy,d=DENTS[name];return d*math.exp(-2*(((x-cx)/.09)**2+((y-cy)/.12)**2))


def skin(name,x,y):
    w,z,h=section(name,y);return z+h*math.sqrt(max(0,1-(x/w)**2))-dent(name,x,y)


def closed_grid(name,top,width,height,surface):
    size=len(top);vertices=top+[(x,y,z-.014) for x,y,z in top];faces=[]
    for row in range(height-1):
        for col in range(width-1):
            a=row*width+col;f=(a,a+1,a+width+1,a+width);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(width))+[row*width+width-1 for row in range(1,height)]+list(reversed(range((height-1)*width,(height-1)*width+width-1)))+[row*width for row in reversed(range(1,height-1))]
    for a,b in zip(edge,edge[1:]+edge[:1]):faces.append((a,a+size,b+size,b))
    return mesh(name,vertices,faces,surface)


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.data.materials.append(surface);return obj


def oval_patch(surface):
    owner='Transportation slate forward module';count=64;rows=10;top=[(0,-1.20,skin(owner,0,-1.20)+.005)]
    for row in range(1,rows+1):
        for i in range(count):
            phi=i*math.tau/count;x=.18*row/rows*math.cos(phi);y=-1.20+.26*row/rows*math.sin(phi);top.append((x,y,skin(owner,x,y)+.005))
    size=len(top);vertices=top+[(x,y,z-.014) for x,y,z in top];faces=[(0,1+i,1+(i+1)%count) for i in range(count)]
    for row in range(rows-1):
        a=1+row*count;b=a+count
        for i in range(count):j=(i+1)%count;faces.append((a+i,b+i,b+j,a+j))
    faces += [tuple(size+i for i in reversed(f)) for f in list(faces)]
    a=1+(rows-1)*count
    for i in range(count):j=(i+1)%count;faces.append((a+i,a+j,a+j+size,a+i+size))
    return mesh('Transportation gold forward patch',vertices,faces,surface)


def build():
    m=dict(hull=material('Transportation | worn slate hull',(.13,.24,.25),.65,.56),aft=material('Transportation | worn green aft hull',(.10,.25,.16),.65,.56),bronze=material('Transportation | aged copper details',(.30,.15,.08),.74,.61),
        edge=material('Transportation | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Transportation | soot graphite',(.012,.013,.017),.45,.76),gold=material('Transportation | heat stained bronze',(.40,.30,.10),.78,.66))
    for name,profile in PROFILES.items():
        refined=[]
        for a,b in zip(profile,profile[1:]):
            n=math.ceil((b[0]-a[0])/.025);refined.extend((y,*section(name,y)) for y in [a[0]+(b[0]-a[0])*i/n for i in range(n)])
        refined.append(profile[-1]);obj=loft(name,refined,m['aft' if 'aft' in name else 'hull'],rings=96)
        for v in obj.data.vertices:
            if v.co.z>.08:v.co.z-=dent(name,v.co.x,v.co.y)
        obj.data.update()
    loft('Transportation copper terminal',[(-2.24,.035,.02,.035),(-2.14,.13,.025,.10),(-1.98,.15,.045,.11)],m['bronze'],rings=48)
    oval_patch(m['gold'])
    owner='Transportation green aft module'
    for side in [-1,1]:
        top=[];width=7;height=25
        for row in range(height):
            y=.15+.71*row/(height-1);w,z,h=section(owner,y)
            for col in range(width):
                x=side*w*(.55+.09*col/(width-1));top.append((x,y,skin(owner,x,y)+.005))
        closed_grid('Transportation copper aft trim '+str(side),top,width,height,m['bronze'])
    for i,(name,y) in enumerate([('Transportation slate forward module',-.65),('Transportation green aft module',.54)]):
        x=0;z=skin(name,x,y);box('Transportation service cover '+str(i),(x,y,z+.002),(.13,.19,.028),m['aft' if 'aft' in name else 'hull'],.003)
        for j in range(3):box('Transportation service slot '+str(i)+' '+str(j),(x,y-.06+j*.06,z+.02),(.09,.01,.008),m['dark'],.001)
        for side in [-1,1]:
            x=side*.12;z=skin(name,x,y);cylinder('Transportation service fastener '+str(i)+' '+str(side),(x,y,z+.010),.015,.025,m['gold'],vertices=16)
    box('Transportation ventral connecting saddle',(0,-.30,-.06),(.25,.25,.08),m['edge'],.006)
    return m
