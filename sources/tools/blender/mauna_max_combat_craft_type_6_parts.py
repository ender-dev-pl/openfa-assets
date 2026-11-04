"""First MN2C interpretation: layered grey hull, brown bands and separate red raised pieces."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,finish

BODY='Type 6 main hull'
BASE='Type 6 lower base'
DENTS={-1:(0,.10,.005),1:(0,.10,.006)}
ROOF='Type 6 sloped upper roof'
ROOF_PROFILE=[(-.40,.46,.23),(.20,.44,.52),(.65,.40,.64),(1.35,.43,.25),(1.60,.46,.21)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.90,-.02),(0,-1,0))}


def dent(side,y,z):
    cy,cz,depth=DENTS[side];return depth*math.exp(-2*(((y-cy)/.16)**2+((z-cz)/.04)**2))


def skin(side,y,z):return side*(.55-dent(side,y,z))


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def body(surface):
    outline=[(-.52,-1.80),(.52,-1.80),(.55,-1.77),(.55,1.77),(.52,1.80),(-.52,1.80),(-.55,1.77),(-.55,-1.77)];cross=[]
    for a,b in zip(outline,outline[1:]+outline[:1]):
        a=Vector(a);b=Vector(b);steps=math.ceil((b-a).length/.03);ts=[i/steps for i in range(steps)]
        if a.y*b.y<0 and not any(abs(t-.5)<1e-8 for t in ts):ts.append(.5)
        cross.extend(a.lerp(b,t) for t in sorted(ts))
    zs=[-.24+.40*i/40 for i in range(41)]
    for z in [-.215,.135]:zs=[v for v in zs if abs(v-z)>1e-8]+[z]
    zs.sort();count=len(cross);vertices=[]
    for z in zs:
        inset=max(0,.025-min(z+.24,.16-z))
        for p in cross:
            x=p.x*(1-inset/.55);y=p.y*(1-inset/1.80)
            if abs(abs(p.x)-.55)<1e-7:x-=math.copysign(dent(1 if p.x>0 else -1,y,z),p.x)
            vertices.append((x,y,z))
    first=len(vertices);last=first+1;vertices.extend([(0,0,zs[0]),(0,0,zs[-1])]);end=(len(zs)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(zs)-1) for i in range(count))
    return mesh(BODY,vertices,faces,surface)


def patch(name,side,y0,y1,z0,z1,surface,top=.008,back=-.015,support=BASE):
    columns=13;rows=17;front=[];rear=[]
    for row in range(rows):
        z=z0+(z1-z0)*row/(rows-1)
        for col in range(columns):
            y=y0+(y1-y0)*col/(columns-1);x=side*.60;front.append((x+side*top,y,z));rear.append((x+side*back,y,z))
    size=len(front);faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,front+rear,faces,surface)
    PATCHES.append(dict(name=name,domain='base-face',side=side,y0=y0,y1=y1,z0=z0,z1=z1,top=top,back=back,support=support));return obj


def face_frame(side,y,z):
    obj=bpy.data.objects[BASE];inv=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inv @ Vector((side*3,y,z)),(inv.to_3x3() @ Vector((-side,0,0))).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ n).normalized()



def roof_section(y):
    for (a,wa,za),(b,wb,zb) in zip(ROOF_PROFILE,ROOF_PROFILE[1:]):
        if a-1e-9<=y<=b+1e-9:
            t=(y-a)/(b-a);return wa+(wb-wa)*t,za+(zb-za)*t
    raise ValueError(y)


def roof_skin(x,y):
    w,z=roof_section(y);return z-.035*abs(x)/w-.005*math.exp(-2*((x/.08)**2+((y-.75)/.12)**2))


def closed_grid(name,front,rear,columns,rows,surface):
    size=len(front);faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));return mesh(name,front+rear,faces,surface)


def roof_mesh(surface):
    ys=[-.40+2*i/100 for i in range(101)]
    for y in [y for y,_,_ in ROOF_PROFILE]+[.75]:
        if -.40<y<1.60:ys=[v for v in ys if abs(v-y)>1e-8]+[y]
    ys.sort();front=[];rear=[]
    for y in ys:
        w,_=roof_section(y)
        for i in range(33):
            x=w*(-1+2*i/32);front.append((x,y,roof_skin(x,y)));rear.append((x,y,.12))
    return closed_grid(ROOF,front,rear,33,len(ys),surface)


def roof_patch(name,x0,x1,y0,y1,surface,top=.008,back=-.015,support=ROOF):
    front=[];rear=[];columns=17;rows=25
    for row in range(rows):
        y=y0+(y1-y0)*row/(rows-1)
        for col in range(columns):
            x=x0+(x1-x0)*col/(columns-1);z=roof_skin(x,y);front.append((x,y,z+top));rear.append((x,y,z+back))
    obj=closed_grid(name,front,rear,columns,rows,surface);PATCHES.append(dict(name=name,domain='roof',x0=x0,x1=x1,y0=y0,y1=y1,top=top,back=back,support=support));return obj


def roof_frame(x,y):
    obj=bpy.data.objects[ROOF];inv=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inv @ Vector((x,y,3)),(inv.to_3x3() @ Vector((0,0,-1))).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ n).normalized()


def red_piece(side,surface):
    front=[];rear=[];ys=[-1.10+.40*i/32 for i in range(33)]+[-.95];ys.sort()
    for y in ys:
        z=.25+(.47-.25)*(y+1.10)/.15 if y<=-.95 else .47+(.40-.47)*(y+.95)/.25
        for i in range(17):
            x=side*.28-.10+.20*i/16;front.append((x,y,z));rear.append((x,y,.14))
    return closed_grid('Type 6 red raised piece '+str(side),front,rear,17,len(ys),surface)


def build():
    PATCHES.clear()
    m=dict(hull=material('Type 6 | worn grey layered hull',(.24,.25,.26),.72,.68),red=material('Type 6 | worn red raised pieces',(.38,.07,.06),.62,.70),bronze=material('Type 6 | worn brown side details',(.28,.17,.075),.73,.69),blue=material('Type 6 | dull pale blue end',(.18,.28,.32),.55,.72),edge=material('Type 6 | oxidized service alloy',(.19,.22,.24),.78,.65),dark=material('Type 6 | carbon dark strips',(.012,.016,.018),.40,.80))
    body(m['hull']);box(BASE,(0,0,-.22),(1.20,3.70,.16),m['hull'],.018);roof_mesh(m['hull'])
    for side in [-1,1]:
        box('Type 6 red mount '+str(side),(side*.28,-.90,.16),(.23,.43,.04),m['dark'],.003);red_piece(side,m['red'])
        box('Type 6 brown side band '+str(side),(side*.557,0,-.02),(.030,2.80,.14),m['bronze'],.004)
    box('Type 6 brown rear panel',(0,1.81,-.03),(.90,.04,.30),m['bronze'],.004)
    box('Type 6 pale fore panel',(0,-1.81,-.02),(.90,.04,.14),m['blue'],.004)
    for i,x in enumerate([-.30,-.10,.10,.30]):box('Type 6 rear dark strip '+str(i),(x,1.833,-.03),(.015,.012,.21),m['dark'],.001)
    for i,(x,y) in enumerate([(-.30,-1.55),(.30,-1.55),(0,1.50)]):box('Type 6 warm lower block '+str(i),(x,y,-.335),(.16 if i<2 else .20,.32 if i<2 else .30,.12),m['bronze'],.006)
    bpy.context.view_layer.update()
    for side in [-1,1]:
        for i,y in enumerate([-.70,.70]):
            label=str(side)+' '+str(i);cover='Type 6 base service frame '+label;inset='Type 6 base grey inset '+label
            patch(cover,side,y-.225,y+.225,-.265,-.175,m['hull'])
            patch(inset,side,y-.16,y+.16,-.25,-.19,m['edge'],top=.015,back=.003,support=cover)
            for j,z in enumerate([-.235,-.205]):patch('Type 6 dark service strip '+label+' '+str(j),side,y-.135,y+.135,z-.004,z+.004,m['dark'],top=.022,back=.010,support=inset)
            for j,dy in enumerate([-.18,.18]):
                for k,z in enumerate([-.255,-.185]):
                    p,n=face_frame(side,y+dy,z);cylinder('Type 6 frame fastener '+label+' '+str(j)+' '+str(k),p+n*.010,.0025,.024,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    hatch='Type 6 roof hatch';roof_patch(hatch,-.18,.18,.85,1.20,m['hull'])
    for i,y in enumerate([.93,1.025,1.12]):roof_patch('Type 6 roof dark strip '+str(i),-.12,.12,y-.006,y+.006,m['dark'],top=.015,back=.003,support=hatch)
    for i,x in enumerate([-.14,.14]):
        for j,y in enumerate([.89,1.16]):
            p,n=roof_frame(x,y);cylinder('Type 6 roof fastener '+str(i)+' '+str(j),p+n*.010,.004,.024,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
