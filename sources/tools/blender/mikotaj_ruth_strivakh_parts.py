"""First MK3C transporter: central shell, open copper beam assembly and terminal pods."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,finish
from manufactured_vessels import vessel
from manufactured_surface_mounts import cast_bezel

BODY='Ruth-Strivakh central pressure body'
KEEL='Ruth-Strivakh lower keel'
PROFILES={BODY:[(-1.05,.10,.03,.10),(-.80,.36,.03,.28),(-.35,.72,.03,.42),(.35,.72,.03,.42),(.80,.36,.03,.28),(1.05,.10,.03,.10)],
 KEEL:[(-1.30,.02,-.20,.04),(-1.0,.40,-.20,.10),(-.45,.60,-.20,.12),(.45,.60,-.20,.12),(1.0,.40,-.20,.10),(1.30,.02,-.20,.04)]}
CENTRES={BODY:0,KEEL:0}
DENTS={BODY:(0,-.18,.006)}
for side in [-1,1]:
    name='Ruth-Strivakh terminal pod '+str(side);PROFILES[name]=[(-.32,.03,-.02,.04),(-.24,.24,-.02,.18),(0,.38,-.02,.26),(.24,.24,-.02,.18),(.32,.03,-.02,.04)];CENTRES[name]=side*3.0;DENTS[name]=(.12,.04,.004)
GREEN_PROFILE=[(0,.075),(.03125,.085),(.09375,.065),(.15625,.025)]
SOCKETS={'AlignmentForward':((0,-1.32,-.2),(0,-1,0))}
PATCHES=[]


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    if name not in DENTS:return 0
    cx,cy,depth=DENTS[name];return depth*math.exp(-2*(((x-cx)/.10)**2+((y-cy)/.12)**2))


def skin(name,x,y):
    w,z,h=section(name,y);return z+h*math.sqrt(max(0,1-(x/w)**2))-dent(name,x,y)


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def shell(name,surface):
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


def patch(name,owner,cx,cy,width,depth,surface,top=.008,back=-.015,support=None):
    columns=13;rows=17;front=[];rear=[]
    for row in range(rows):
        y=cy+depth*(-.5+row/(rows-1))
        for col in range(columns):
            x=cx+width*(-.5+col/(columns-1));z=skin(owner,x,y);front.append((CENTRES[owner]+x,y,z+top));rear.append((CENTRES[owner]+x,y,z+back))
    size=len(front);vertices=front+rear;faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,vertices,faces,surface)
    PATCHES.append(dict(name=name,owner=owner,cx=cx,cy=cy,width=width,depth=depth,top=top,back=back,support=support or owner));return obj


def roof(owner,x,y):
    obj=bpy.data.objects[owner];inverse=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inverse @ Vector((CENTRES[owner]+x,y,3)),(inverse.to_3x3() @ Vector((0,0,-1))).normalized());assert hit
    p=obj.matrix_world @ p;normal=(inverse.to_3x3().transposed() @ normal).normalized()
    if normal.z<0:normal=-normal
    return p,normal


def build():
    PATCHES.clear()
    m=dict(hull=material('Ruth-Strivakh | worn blue grey shell',(.13,.17,.24),.72,.63),copper=material('Ruth-Strivakh | worn copper assembly',(.28,.12,.075),.78,.65),green=material('Ruth-Strivakh | worn opaque green fixtures',(.12,.30,.20),.63,.60),
        gold=material('Ruth-Strivakh | dulled gold interfaces',(.32,.28,.08),.72,.64),edge=material('Ruth-Strivakh | oxidized service alloy',(.19,.23,.27),.78,.62),dark=material('Ruth-Strivakh | carbon dark seams',(.012,.015,.021),.40,.80))
    for name in PROFILES:shell(name,m['hull'])
    for side in [-1,1]:
        for rail in [-1,1]:
            box('Ruth-Strivakh copper rail '+str(side)+' '+str(rail),(side*1.80,rail*.22,-.04),(2.36,.12,.12),m['copper'],.008)
            box('Ruth-Strivakh rail inset '+str(side)+' '+str(rail),(side*1.80,rail*.22,.023),(1.65,.04,.014),m['dark'],.002)
        for i,x in enumerate([.95,1.55,2.20,2.65]):
            box('Ruth-Strivakh crossmember '+str(side)+' '+str(i),(side*x,0,-.04),(.10,.56,.13),m['copper'],.008)
        for i,x in enumerate([.95,2.20]):
            for rail in [-1,1]:
                label=str(side)+' '+str(i)+' '+str(rail);box('Ruth-Strivakh fixture base '+label,(side*x,rail*.22,.045),(.22,.18,.08),m['copper'],.008)
                obj=vessel('Ruth-Strivakh green fixture '+label,GREEN_PROFILE,m['green'],[]);obj.location=(side*x,rail*.22,.07)
    bpy.context.view_layer.update()
    for side in [-1,1]:
        n=Vector((0,side,0));point=Vector((0,side*1.08,.03));cast_bezel('Ruth-Strivakh body bezel '+str(side),bpy.data.objects[BODY],point,n,.085,m['gold'])
        cylinder('Ruth-Strivakh body face '+str(side),point+n*.030,.052,.016,m['edge'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    specs=[(BODY,-.24,.10,.18,.32),(BODY,.24,.10,.18,.32)]+[('Ruth-Strivakh terminal pod '+str(side),0,0,.18,.16) for side in [-1,1]]
    for i,(owner,x,y,width,depth) in enumerate(specs):
        cover='Ruth-Strivakh service cover '+str(i);patch(cover,owner,x,y,width,depth,m['hull'])
        for j,dy in enumerate([-.22*depth,.22*depth]):patch('Ruth-Strivakh service slot '+str(i)+' '+str(j),owner,x,y+dy,width*.60,.012,m['dark'],top=.015,back=.004,support=cover)
        for j,dx in enumerate([-.34*width,.34*width]):
            for k,dy in enumerate([-.34*depth,.34*depth]):
                p,n=roof(owner,x+dx,y+dy);cylinder('Ruth-Strivakh fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.005,.020,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
