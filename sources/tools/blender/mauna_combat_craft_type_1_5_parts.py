"""First MN1A interpretation: low grey beam, stepped upper decks and pale end detail."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,finish

BODY='Type 1.5 chamfered low body'
DENTS={-1:(0,0,.004),1:(0,0,.005)}
DECK='Type 1.5 aft raised deck'
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.15,-.04),(0,-1,0))}


def dent(side,y,z):
    cy,cz,depth=DENTS[side];return depth*math.exp(-2*(((y-cy)/.12)**2+((z-cz)/.05)**2))


def skin(side,y,z):return side*(.32-dent(side,y,z))


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def body(surface):
    outline=[(-.295,-1.10),(.295,-1.10),(.32,-1.075),(.32,1.075),(.295,1.10),(-.295,1.10),(-.32,1.075),(-.32,-1.075)];cross=[]
    for a,b in zip(outline,outline[1:]+outline[:1]):
        a=Vector(a);b=Vector(b);steps=math.ceil((b-a).length/.03);ts=[i/steps for i in range(steps)]
        if a.y*b.y<0 and not any(abs(t-.5)<1e-8 for t in ts):ts.append(.5)
        cross.extend(a.lerp(b,t) for t in sorted(ts))
    zs=[-.17+.30*i/30 for i in range(31)]
    for z in [-.15,.11]:zs=[v for v in zs if abs(v-z)>1e-8]+[z]
    zs.sort();count=len(cross);vertices=[]
    for z in zs:
        inset=max(0,.020-min(z+.17,.13-z))
        for p in cross:
            x=p.x*(1-inset/.32);y=p.y*(1-inset/1.10)
            if abs(abs(p.x)-.32)<1e-7:x-=math.copysign(dent(1 if p.x>0 else -1,y,z),p.x)
            vertices.append((x,y,z))
    first=len(vertices);last=first+1;vertices.extend([(0,0,zs[0]),(0,0,zs[-1])]);end=(len(zs)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(zs)-1) for i in range(count))
    return mesh(BODY,vertices,faces,surface)


def patch(name,side,y0,y1,z0,z1,surface,top=.008,back=-.015,support=BODY):
    columns=13;rows=17;front=[];rear=[]
    for row in range(rows):
        z=z0+(z1-z0)*row/(rows-1)
        for col in range(columns):
            y=y0+(y1-y0)*col/(columns-1);x=skin(side,y,z);front.append((x+side*top,y,z));rear.append((x+side*back,y,z))
    size=len(front);faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,front+rear,faces,surface)
    PATCHES.append(dict(name=name,domain='face',side=side,y0=y0,y1=y1,z0=z0,z1=z1,top=top,back=back,support=support));return obj


def face_frame(side,y,z):
    obj=bpy.data.objects[BODY];inv=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inv @ Vector((side*3,y,z)),(inv.to_3x3() @ Vector((-side,0,0))).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ n).normalized()



def deck_skin(x,y):return .23-.004*math.exp(-2*((x/.08)**2+((y-.18)/.12)**2))


def deck_grid(name,x0,x1,y0,y1,surface,top=0,back=None,support=None):
    xs=[x0+(x1-x0)*i/32 for i in range(33)];rows=max(16,math.ceil((y1-y0)/.020));ys=[y0+(y1-y0)*i/rows for i in range(rows+1)]
    if y0<.18<y1:ys=[y for y in ys if abs(y-.18)>1e-8]+[.18];ys.sort()
    front=[];rear=[]
    for y in ys:
        for x in xs:
            z=deck_skin(x,y);front.append((x,y,z+top));rear.append((x,y,.105 if back is None else z+back))
    columns=len(xs);rows=len(ys);size=len(front);faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,front+rear,faces,surface)
    if support is not None:PATCHES.append(dict(name=name,domain='deck',x0=x0,x1=x1,y0=y0,y1=y1,top=top,back=back,support=support))
    return obj


def build():
    PATCHES.clear()
    m=dict(hull=material('Type 1.5 | worn grey low hull',(.24,.25,.26),.72,.68),blue=material('Type 1.5 | dull pale blue grey end',(.18,.28,.32),.55,.72),edge=material('Type 1.5 | oxidized service alloy',(.19,.22,.24),.78,.65),dark=material('Type 1.5 | carbon dark strips',(.012,.016,.018),.40,.80))
    body(m['hull']);deck_grid('Type 1.5 fore raised deck',-.26,.26,-.95,-.65,m['hull']);deck_grid(DECK,-.26,.26,-.52,.92,m['hull'])
    for side in [-1,1]:
        box('Type 1.5 end interface '+str(side),(0,side*1.108,-.04),(.46,.025,.10),m['blue' if side==-1 else 'hull'],.003)
        box('Type 1.5 side seam strip '+str(side),(side*.325,0,-.105),(.025,2.08,.030),m['edge'],.002)
        box('Type 1.5 end seam strip '+str(side),(0,side*1.09,-.105),(.66,.025,.030),m['edge'],.002)
    bpy.context.view_layer.update()
    for side in [-1,1]:
        for i,y in enumerate([-.45,.45]):
            label=str(side)+' '+str(i);cover='Type 1.5 service frame '+label;inset='Type 1.5 grey inset '+label
            patch(cover,side,y-.19,y+.19,-.075,.065,m['hull'])
            patch(inset,side,y-.15,y+.15,-.060,.050,m['edge'],top=.015,back=.003,support=cover)
            for j,z in enumerate([-.040,.025]):patch('Type 1.5 dark service strip '+label+' '+str(j),side,y-.125,y+.125,z-.0045,z+.0045,m['dark'],top=.022,back=.010,support=inset)
            for j,dy in enumerate([-.155,.155]):
                for k,z in enumerate([-.060,.050]):
                    p,n=face_frame(side,y+dy,z);cylinder('Type 1.5 frame fastener '+label+' '+str(j)+' '+str(k),p+n*.010,.003,.024,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    hatch='Type 1.5 deck hatch';deck_grid(hatch,-.175,.175,.25,.65,m['hull'],top=.008,back=-.015,support=DECK)
    for i,y in enumerate([.35,.45,.55]):deck_grid('Type 1.5 deck dark strip '+str(i),-.12,.12,y-.007,y+.007,m['dark'],top=.015,back=.003,support=hatch)
    for i,x in enumerate([-.13,.13]):
        for j,y in enumerate([.30,.60]):cylinder('Type 1.5 deck fastener '+str(i)+' '+str(j),(x,y,deck_skin(x,y)+.010),.004,.024,m['edge'],vertices=16)
    return m
