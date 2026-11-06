"""First MN0A scout: chamfered slab, interrupted crown and warm lower tabs."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,finish

BODY='Type 5 chamfered slab body'
DENTS={-1:(0,-.10,.005),1:(0,.10,.006)}
CROWN=[-.60,-.20,.20,.60]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-.90,0),(0,-1,0))}


def dent(side,y,z):
    cy,cz,depth=DENTS[side];return depth*math.exp(-2*(((y-cy)/.10)**2+((z-cz)/.12)**2))


def skin(side,y,z):return side*(.325-dent(side,y,z))


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def body(surface):
    outline=[(-.30,-.85),(.30,-.85),(.325,-.825),(.325,.825),(.30,.85),(-.30,.85),(-.325,.825),(-.325,-.825)];cross=[]
    for a,b in zip(outline,outline[1:]+outline[:1]):
        a=Vector(a);b=Vector(b);steps=math.ceil((b-a).length/.03);ts=[i/steps for i in range(steps)]
        if a.y*b.y<0 and not any(abs(t-.5)<1e-8 for t in ts):ts.append(.5)
        cross.extend(a.lerp(b,t) for t in sorted(ts))
    zs=[-.70+1.35*i/54 for i in range(55)]
    for z in [-.675,.625]:zs=[v for v in zs if abs(v-z)>1e-8]+[z]
    zs.sort();count=len(cross);vertices=[]
    for z in zs:
        inset=max(0,.025-min(z+.70,.65-z))
        for p in cross:
            x=p.x*(1-inset/.325);y=p.y*(1-inset/.85)
            if abs(abs(p.x)-.325)<1e-7:x-=math.copysign(dent(1 if p.x>0 else -1,y,z),p.x)
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
    PATCHES.append(dict(name=name,side=side,y0=y0,y1=y1,z0=z0,z1=z1,top=top,back=back,support=support));return obj


def face_frame(side,y,z):
    obj=bpy.data.objects[BODY];inv=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inv @ Vector((side*3,y,z)),(inv.to_3x3() @ Vector((-side,0,0))).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ n).normalized()


def build():
    PATCHES.clear()
    m=dict(hull=material('Type 5 | worn grey metal slab',(.19,.21,.22),.72,.68),rust=material('Type 5 | worn warm lower tabs',(.28,.11,.085),.65,.69),blue=material('Type 5 | dull blue grey insets',(.12,.17,.22),.55,.72),edge=material('Type 5 | oxidized service alloy',(.19,.22,.24),.78,.65),dark=material('Type 5 | carbon dark strips',(.012,.016,.018),.40,.80))
    body(m['hull'])
    for i,y in enumerate(CROWN):box('Type 5 crown tab '+str(i),(0,y,.69),(.58,.15,.12),m['hull'],.008)
    for i,y in enumerate([-.40,.40]):box('Type 5 warm lower tab '+str(i),(0,y,-.77),(.34,.26,.18),m['rust'],.010)
    for side in [-1,1]:
        box('Type 5 side seam strip '+str(side),(side*.33,0,-.56),(.03,1.62,.05),m['hull'],.003)
        box('Type 5 end seam strip '+str(side),(0,side*.84,-.56),(.67,.03,.05),m['hull'],.003)
    bpy.context.view_layer.update()
    for side in [-1,1]:
        for i,y in enumerate([-.30,.30]):
            label=str(side)+' '+str(i);cover='Type 5 service frame '+label;inset='Type 5 blue grey inset '+label
            patch(cover,side,y-.125,y+.125,-.20,.30,m['hull'])
            patch(inset,side,y-.085,y+.085,-.12,.22,m['blue'],top=.015,back=.003,support=cover)
            for j,z in enumerate([-.06,.05,.16]):patch('Type 5 dark service strip '+label+' '+str(j),side,y-.06,y+.06,z-.007,z+.007,m['dark'],top=.022,back=.010,support=inset)
            for j,dy in enumerate([-.09,.09]):
                for k,z in enumerate([-.16,.26]):
                    p,n=face_frame(side,y+dy,z);cylinder('Type 5 frame fastener '+label+' '+str(j)+' '+str(k),p+n*.010,.0045,.024,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
