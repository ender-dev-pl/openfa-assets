"""First AR1A interpretation: broad green delta with separate central and lateral grey cowls."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_surface_mounts import cast_bezel

GREEN='All-Purpose green delta hull'
ROOF='All-Purpose central grey cowl'
PORT='All-Purpose port grey cowl'
STARBOARD='All-Purpose starboard grey cowl'
PROFILES={GREEN:[(-1.40,.025,.020,.010),(-.90,.38,.040,.018),(-.10,.70,.055,.025),(.55,1.05,.065,.025),(.85,.95,.045,.022),(1.0,.88,.030,.018)],
 ROOF:[(-.55,.03,.06,.035),(-.30,.22,.075,.16),(.05,.36,.075,.22),(.40,.34,.075,.20),(.70,.14,.055,.10),(.78,.04,.05,.035)]}
SIDE_PROFILE=[(-.05,.025,.045,.03),(.12,.18,.05,.10),(.45,.24,.05,.13),(.72,.16,.045,.09),(.82,.035,.04,.025)]
PROFILES[PORT]=SIDE_PROFILE;PROFILES[STARBOARD]=SIDE_PROFILE
CENTRES={GREEN:0,ROOF:0,PORT:-1.12,STARBOARD:1.12}
DENTS={GREEN:(-.70,.40,.004),ROOF:(0,-.05,.005),PORT:(0,.10,.004),STARBOARD:(0,.10,.004)}
SOCKETS={'AlignmentForward':((0,-1.42,-.02),(0,-1,0))}
PATCHES=[]
COVERS=[(ROOF,.18,.45,-.70,-.30),(ROOF,.18,.45,.30,.70),(PORT,.25,.60,-.40,.40),(STARBOARD,.25,.60,-.40,.40),(GREEN,.55,.80,-.73,-.56),(GREEN,.55,.80,.56,.73)]


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    cx,cy,depth=DENTS[name];return depth*math.exp(-2*(((x-cx)/.08)**2+((y-cy)/.10)**2))


def skin(name,x,y):
    width,z,height=section(name,y);u=abs(x/width)
    return (z-height*u*u if name==GREEN else z+height*math.sqrt(max(0,1-u*u)))-dent(name,x,y)


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
    if name!=GREEN:return cowl(name,surface)
    ys,us=grid(name,PROFILES[name][0][0],PROFILES[name][-1][0],-1,1,.022);top=[];back=[]
    for y in ys:
        width,_,_=section(name,y)
        for u in us:
            x=width*u;top.append((x,y,skin(name,x,y)));back.append((x,y,-.11-.025*(1-abs(y)/1.5) if name==GREEN else -.015))
    return closed_surfaces(name,top,back,len(us),len(ys),surface)



def cowl(name,surface):
    rows=[];count=128;vertices=[]
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        steps=math.ceil((b[0]-a[0])/.018);rows.extend(a[0]+(b[0]-a[0])*i/steps for i in range(steps))
    rows.append(PROFILES[name][-1][0])
    for y in rows:
        w,z,h=section(name,y)
        for i in range(count):
            phi=i*math.tau/count;x=w*math.cos(phi);height=z+h*math.sin(phi)-(dent(name,x,y) if math.sin(phi)>0 else 0);vertices.append((CENTRES[name]+x,y,height))
    first=len(vertices);last=first+1;vertices.extend([(CENTRES[name],rows[0],section(name,rows[0])[1]),(CENTRES[name],rows[-1],section(name,rows[-1])[1])]);end=(len(rows)-1)*count
    faces=[(first,i,(i+1)%count) for i in range(count)]+[(last,end+(i+1)%count,end+i) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(rows)-1) for i in range(count))
    obj=mesh(name,vertices,faces,surface)
    for face in obj.data.polygons:face.use_smooth=len(face.vertices)==4
    return obj


def patch(name,owner,y0,y1,u0,u1,surface,top=.008,back=-.015,support=None):
    ys,us=grid(owner,y0,y1,u0,u1,.022);front=[];rear=[]
    for y in ys:
        width,_,_=section(owner,y)
        for u in us:
            x=width*u;z=skin(owner,x,y);front.append((CENTRES[owner]+x,y,z+top));rear.append((CENTRES[owner]+x,y,z+back))
    obj=closed_surfaces(name,front,rear,len(us),len(ys),surface);PATCHES.append(dict(name=name,owner=owner,y0=y0,y1=y1,u0=u0,u1=u1,top=top,back=back,support=support or owner));return obj


def roof(owner,x,y):
    obj=bpy.data.objects[owner];inverse=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inverse @ Vector((CENTRES[owner]+x,y,3)),(inverse.to_3x3() @ Vector((0,0,-1))).normalized());assert hit
    p=obj.matrix_world @ p;n=(inverse.to_3x3().transposed() @ n).normalized()
    if n.z<0:n=-n
    return p,n


def build():
    PATCHES.clear()
    m=dict(hull=material('All-Purpose | worn grey alloy shell',(.27,.29,.30),.78,.64),green=material('All-Purpose | worn green lower hull',(.10,.28,.12),.68,.64),edge=material('All-Purpose | oxidized service alloy',(.19,.22,.24),.78,.63),dark=material('All-Purpose | carbon dark seams',(.012,.016,.018),.40,.80))
    shell(GREEN,m['green'])
    for owner in [ROOF,PORT,STARBOARD]:shell(owner,m['hull'])
    bpy.context.view_layer.update()
    for i,(owner,y0,y1,u0,u1) in enumerate(COVERS):
        cover='All-Purpose service cover '+str(i);patch(cover,owner,y0,y1,u0,u1,m['green' if owner==GREEN else 'hull'])
        for j,f in enumerate([.32,.68]):
            y=y0+(y1-y0)*f;patch('All-Purpose service slot '+str(i)+' '+str(j),owner,y-.007,y+.007,u0+(u1-u0)*.18,u1-(u1-u0)*.18,m['dark'],top=.015,back=.004,support=cover)
        for j,f in enumerate([.16,.84]):
            y=y0+(y1-y0)*f;w,_,_=section(owner,y)
            for k,uf in enumerate([.18,.82]):
                x=w*(u0+(u1-u0)*uf);p,n=roof(owner,x,y);cylinder('All-Purpose fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.0045,.020,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    owner=ROOF;panel='All-Purpose forward service inset';patch(panel,owner,-.25,-.10,-.24,.24,m['dark'])
    for j,y in enumerate([-.225,-.175,-.125]):patch('All-Purpose forward alloy slat '+str(j),owner,y-.006,y+.006,-.16,.16,m['edge'],top=.015,back=.003,support=panel)
    for side in [-1,1]:
        n=Vector((0,1,0));p=Vector((side*.30,1.02,-.045));cast_bezel('All-Purpose rear bezel '+str(side),bpy.data.objects[GREEN],p,n,.040,m['edge'])
        cylinder('All-Purpose rear interface '+str(side),p+n*.030,.026,.012,m['dark'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
