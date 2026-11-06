"""First independent MN3C interpretation: paired angular sections and axial projections."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,finish

PODS={-1:-.62,1:.62}
DENTS={-1:(-1,.62-.02,.12,.006),1:(1,-.62-.02,.12,.007)}
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-2.24,0),(0,-1,0))}


def dent(side,y,z):
    return sum(depth*math.exp(-2*(((y-cy)/.13)**2+((z-cz)/.09)**2)) for _,(s,cy,cz,depth) in DENTS.items() if side==s)


def skin(side,y,z):return side*(.52-dent(side,y,z))


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def pod(index,surface):
    cy=PODS[index];outline=[(-.44,-.50),(.44,-.50),(.52,-.42),(.52,.42),(.44,.50),(-.44,.50),(-.52,.42),(-.52,-.42)];cross=[]
    for a,b in zip(outline,outline[1:]+outline[:1]):
        a=Vector(a);b=Vector(b);steps=math.ceil((b-a).length/.025);ts=[i/steps for i in range(steps)]
        if a.y<-.02<b.y:ts.append((-.02-a.y)/(b.y-a.y))
        cross.extend(a.lerp(b,t) for t in sorted(set(ts)))
    zs=[-.42+.84*i/84 for i in range(85)]
    for z in [-.37,.12,.37]:zs=[v for v in zs if abs(v-z)>1e-8]+[z]
    zs.sort();count=len(cross);vertices=[]
    for z in zs:
        inset=max(0,.05-min(z+.42,.42-z))
        for p in cross:
            x=p.x*(1-inset/.52);y=cy+p.y*(1-inset/.50)
            if abs(abs(p.x)-.52)<1e-7:x-=math.copysign(dent(1 if p.x>0 else -1,y,z),p.x)
            vertices.append((x,y,z))
    first=len(vertices);last=first+1;vertices.extend([(0,cy,zs[0]),(0,cy,zs[-1])]);end=(len(zs)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(zs)-1) for i in range(count))
    return mesh('Elite pod '+str(index),vertices,faces,surface)


def patch(name,index,side,y0,y1,z0,z1,surface,top=.008,back=-.015,support=None):
    cols=17;rows=25;vertices=[]
    for offset in [top,back]:
        for r in range(rows):
            z=z0+(z1-z0)*r/(rows-1)
            for c in range(cols):
                y=y0+(y1-y0)*c/(cols-1);vertices.append((skin(side,y,z)+side*offset,y,z))
    size=cols*rows;faces=[]
    for r in range(rows-1):
        for c in range(cols-1):
            a=r*cols+c;f=(a,a+1,a+cols+1,a+cols);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[r*cols for r in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,vertices,faces,surface)
    PATCHES.append(dict(name=name,index=index,side=side,y0=y0,y1=y1,z0=z0,z1=z1,top=top,back=back,support=support or 'Elite pod '+str(index)));return obj


def face_frame(index,side,y,z):
    obj=bpy.data.objects['Elite pod '+str(index)];inv=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inv @ Vector((side*3,y,z)),(inv.to_3x3() @ Vector((-side,0,0))).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ n).normalized()


def build():
    hull=material('Elite | worn grey armour',(.23,.24,.25),.72,.70)
    blue=material('Elite | worn pale blue bands',(.20,.32,.38),.58,.72)
    red=material('Elite | worn red tips',(.35,.055,.045),.55,.74)
    edge=material('Elite | oxidized service alloy',(.17,.19,.20),.78,.65)
    dark=material('Elite | dark recesses',(.012,.016,.018),.40,.80)
    box('Elite central connection',(0,0,-.04),(.64,.50,.42),edge,.025)
    for index,cy in PODS.items():
        pod(index,hull)
        box('Elite axial root '+str(index),(0,index*1.13,0),(.32,.28,.30),hull,.025)
        box('Elite axial projection '+str(index),(0,index*1.62,0),(.095,1.00,.10),edge,.012)
        box('Elite red tip '+str(index),(0,index*2.12,0),(.070,.20,.075),red,.008)
        for side in [-1,1]:
            label=str(index)+' '+str(side)
            patch('Elite blue side band '+label,index,side,cy-.32,cy-.13,-.30,.30,blue)
            frame='Elite service frame '+label
            patch(frame,index,side,cy-.08,cy+.32,-.27,.27,hull)
            patch('Elite service inset '+label,index,side,cy-.025,cy+.265,-.20,.20,edge,.015,.003,frame)
            for n,z in enumerate([-.13,0,.13]):patch('Elite service strip '+label+' '+str(n),index,side,cy+.015,cy+.225,z-.009,z+.009,dark,.022,.010,'Elite service inset '+label)
            for j,y in enumerate([cy-.045,cy+.285]):
                for k,z in enumerate([-.235,.235]):
                    p,n=face_frame(index,side,y,z);cylinder('Elite frame fastener '+label+' '+str(j)+' '+str(k),p+n*.010,.005,.024,edge,20).rotation_euler=n.to_track_quat('Z','Y').to_euler()
            box('Elite small red marker '+label,(side*.38,cy-index*.36,.397),(.075,.09,.07),red,.005)
        box('Elite upper blue band '+str(index),(0,cy-.225,.418),(.76,.19,.025),blue,.004)
        for j,y in enumerate([cy-.35,cy-.10]):box('Elite upper rail '+str(index)+' '+str(j),(0,y,.422),(.80,.035,.045),edge,.004)
