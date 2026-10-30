"""First AR0A scout: pointed green lower wedge and a raised faceted alloy shell."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_surface_mounts import cast_bezel

GREEN='Gerla-Kans green lower hull'
ROOF='Gerla-Kans grey upper shell'
PROFILES={GREEN:[(-1.50,.02,.015,.010),(-1.20,.17,.035,.018),(-.30,.46,.055,.025),(.65,.70,.065,.025),(1.0,.65,.045,.022),(1.15,.50,.025,.018)],
 ROOF:[(-1.10,.03,.025,.04),(-.60,.19,.03,.15),(.05,.34,.03,.25),(.60,.45,.03,.21),(.95,.40,.025,.09)]}
DENTS={GREEN:(-.54,.45,.004),ROOF:(0,.05,.005)}
SOCKETS={'AlignmentForward':((0,-1.52,-.02),(0,-1,0))}
PATCHES=[]
COVERS=[(ROOF,.18,.52,-.68,-.32),(ROOF,.18,.52,.32,.68),(GREEN,.40,.80,-.95,-.78),(GREEN,.40,.80,.78,.95)]


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    cx,cy,depth=DENTS[name];return depth*math.exp(-2*(((x-cx)/.08)**2+((y-cy)/.10)**2))


def skin(name,x,y):
    width,z,height=section(name,y);u=abs(x/width)
    return (z-height*u*u if name==GREEN else z+height*(1-.55*max(0,(u-.30)/.70)))-dent(name,x,y)


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def closed_surfaces(name,top,back,columns,rows,surface):
    size=len(top);vertices=top+back;faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));return mesh(name,vertices,faces,surface)


def grid(name,y0,y1,u0,u1,step):
    rows=max(16,math.ceil((y1-y0)/step));ys=[y0+(y1-y0)*i/rows for i in range(rows+1)];us=[u0+(u1-u0)*i/32 for i in range(33)]
    for y,_,_,_ in PROFILES[name]:
        if y0<y<y1:ys=[v for v in ys if abs(v-y)>1e-8]+[y]
    for u in [-.30,0,.30]:
        if u0<u<u1:us=[v for v in us if abs(v-u)>1e-8]+[u]
    return sorted(ys),sorted(us)


def shell(name,surface):
    ys,us=grid(name,PROFILES[name][0][0],PROFILES[name][-1][0],-1,1,.022);top=[];back=[]
    for y in ys:
        width,_,_=section(name,y)
        for u in us:
            x=width*u;top.append((x,y,skin(name,x,y)));back.append((x,y,-.11-.025*(1-abs(y)/1.5) if name==GREEN else -.015))
    return closed_surfaces(name,top,back,len(us),len(ys),surface)


def patch(name,owner,y0,y1,u0,u1,surface,top=.008,back=-.015,support=None):
    ys,us=grid(owner,y0,y1,u0,u1,.022);front=[];rear=[]
    for y in ys:
        width,_,_=section(owner,y)
        for u in us:
            x=width*u;z=skin(owner,x,y);front.append((x,y,z+top));rear.append((x,y,z+back))
    obj=closed_surfaces(name,front,rear,len(us),len(ys),surface);PATCHES.append(dict(name=name,owner=owner,y0=y0,y1=y1,u0=u0,u1=u1,top=top,back=back,support=support or owner));return obj


def roof(owner,x,y):
    obj=bpy.data.objects[owner];inverse=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inverse @ Vector((x,y,3)),(inverse.to_3x3() @ Vector((0,0,-1))).normalized());assert hit
    p=obj.matrix_world @ p;n=(inverse.to_3x3().transposed() @ n).normalized()
    if n.z<0:n=-n
    return p,n


def build():
    PATCHES.clear()
    m=dict(hull=material('Gerla-Kans | worn grey alloy shell',(.27,.29,.30),.78,.64),green=material('Gerla-Kans | worn green lower hull',(.10,.28,.12),.68,.64),edge=material('Gerla-Kans | oxidized service alloy',(.19,.22,.24),.78,.63),dark=material('Gerla-Kans | carbon dark seams',(.012,.016,.018),.40,.80))
    shell(GREEN,m['green']);shell(ROOF,m['hull']);bpy.context.view_layer.update()
    for i,(owner,y0,y1,u0,u1) in enumerate(COVERS):
        cover='Gerla-Kans service cover '+str(i);patch(cover,owner,y0,y1,u0,u1,m['hull' if owner==ROOF else 'green'])
        for j,f in enumerate([.32,.68]):
            y=y0+(y1-y0)*f;patch('Gerla-Kans service slot '+str(i)+' '+str(j),owner,y-.007,y+.007,u0+(u1-u0)*.18,u1-(u1-u0)*.18,m['dark'],top=.015,back=.004,support=cover)
        for j,f in enumerate([.16,.84]):
            y=y0+(y1-y0)*f;w,_,_=section(owner,y)
            for k,uf in enumerate([.18,.82]):
                x=w*(u0+(u1-u0)*uf);p,n=roof(owner,x,y);cylinder('Gerla-Kans fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.0045,.020,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    owner=ROOF;panel='Gerla-Kans forward service inset';patch(panel,owner,-.50,-.30,-.24,.24,m['dark'])
    for j,y in enumerate([-.46,-.40,-.34]):patch('Gerla-Kans forward alloy slat '+str(j),owner,y-.006,y+.006,-.16,.16,m['edge'],top=.015,back=.003,support=panel)
    for side in [-1,1]:
        n=Vector((0,1,0));p=Vector((side*.22,1.17,-.045));cast_bezel('Gerla-Kans rear bezel '+str(side),bpy.data.objects[GREEN],p,n,.040,m['edge'])
        cylinder('Gerla-Kans rear interface '+str(side),p+n*.030,.026,.012,m['dark'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
