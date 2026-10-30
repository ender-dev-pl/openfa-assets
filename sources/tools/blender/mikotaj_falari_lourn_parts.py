"""First MK2C interpretation: rounded blue hull over a continuous pointed green wing."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_vessels import vessel
from manufactured_surface_mounts import cast_bezel

HULL_PROFILE=[(-.70,.12,0,.10),(-.55,.43,0,.36),(-.15,.67,0,.50),(.20,.65,0,.48),(.55,.40,0,.34),(.70,.12,0,.10)]
BODY_DENT=(0,-.10,.006)
WING_WIDTHS=[(-2.80,.015),(-2.0,.30),(-.65,.76),(.65,.76),(2.0,.30),(2.80,.015)]
WING_DENTS=[(.18,-1.40,.004),(-.16,1.40,.004)]
FIXTURES=[(-.34,-1.35),(.34,-1.35),(-.34,1.35),(.34,1.35)]
GOLD_PROFILE=[(-.015625,.075),(0,.10),(.03125,.095),(.0625,.065),(.09375,.025)]
SOCKETS={'AlignmentForward':((0,-2.82,-.068),(0,-1,0))}
PATCHES=[]


def section(y):
    for a,b in zip(HULL_PROFILE,HULL_PROFILE[1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError(y)


def body_dent(x,y):
    cx,cy,depth=BODY_DENT;return depth*math.exp(-2*(((x-cx)/.10)**2+((y-cy)/.16)**2))


def body_skin(x,y):
    w,z,h=section(y);return z+h*math.sqrt(max(0,1-(x/w)**2))-body_dent(x,y)


def wing_width(y):
    for (a,wa),(b,wb) in zip(WING_WIDTHS,WING_WIDTHS[1:]):
        if a-1e-9<=y<=b+1e-9:return wa+(wb-wa)*(y-a)/(b-a)
    raise ValueError(y)


def wing_base(x,y):return -.08+.012*(1-abs(x)/wing_width(y))


def wing_skin(x,y):
    return wing_base(x,y)-sum(depth*math.exp(-2*(((x-cx)/.10)**2+((y-cy)/.16)**2)) for cx,cy,depth in WING_DENTS)


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def closed_surfaces(name,top,back,width,height,surface):
    size=len(top);vertices=top+back;faces=[]
    for row in range(height-1):
        for col in range(width-1):
            a=row*width+col;f=(a,a+1,a+width+1,a+width);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(width))+[row*width+width-1 for row in range(1,height)]+list(reversed(range((height-1)*width,(height-1)*width+width-1)))+[row*width for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));return mesh(name,vertices,faces,surface)


def hull(surface):
    rows=[];count=128;vertices=[]
    for a,b in zip(HULL_PROFILE,HULL_PROFILE[1:]):
        steps=math.ceil((b[0]-a[0])/.018);rows.extend(a[0]+(b[0]-a[0])*i/steps for i in range(steps))
    rows.append(HULL_PROFILE[-1][0])
    for y in rows:
        w,z,h=section(y)
        for i in range(count):
            phi=i*math.tau/count;x=w*math.cos(phi);height=z+h*math.sin(phi)-(body_dent(x,y) if math.sin(phi)>0 else 0);vertices.append((x,y,height))
    first=len(vertices);last=first+1;vertices.extend([(0,rows[0],0),(0,rows[-1],0)]);end=(len(rows)-1)*count
    faces=[(first,i,(i+1)%count) for i in range(count)]+[(last,end+(i+1)%count,end+i) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(rows)-1) for i in range(count))
    obj=mesh('Falari-Lourn blue pressure hull',vertices,faces,surface)
    for face in obj.data.polygons:face.use_smooth=len(face.vertices)==4
    return obj


def wing(surface):
    columns=33;heights=[-2.8+5.6*i/160 for i in range(161)]
    for y in [y for y,_ in WING_WIDTHS]+[0]:
        if -2.8<y<2.8:heights=[h for h in heights if abs(h-y)>1e-8]+[y]
    heights.sort();top=[];back=[]
    for y in heights:
        for i in range(columns):
            x=wing_width(y)*(-1+2*i/(columns-1));z=wing_skin(x,y);top.append((x,y,z));back.append((x,y,z-(.055+.015*(1-abs(y)/2.8))))
    return closed_surfaces('Falari-Lourn continuous green wing',top,back,columns,len(heights),surface)


def patch(name,domain,cx,cy,width,depth,surface,top=.008,back=-.015,support=None):
    columns=13;rows=17;front=[];rear=[];skin=body_skin if domain=='hull' else wing_skin
    for row in range(rows):
        y=cy+depth*(-.5+row/(rows-1))
        for col in range(columns):
            x=cx+width*(-.5+col/(columns-1));z=skin(x,y);front.append((x,y,z+top));rear.append((x,y,z+back))
    owner='Falari-Lourn blue pressure hull' if domain=='hull' else 'Falari-Lourn continuous green wing'
    obj=closed_surfaces(name,front,rear,columns,rows,surface);PATCHES.append(dict(name=name,domain=domain,cx=cx,cy=cy,width=width,depth=depth,top=top,back=back,support=support or owner));return obj


def roof(x,y):
    obj=bpy.data.objects['Falari-Lourn blue pressure hull'];inverse=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inverse @ Vector((x,y,3)),(inverse.to_3x3() @ Vector((0,0,-1))).normalized());assert hit
    p=obj.matrix_world @ p;normal=(inverse.to_3x3().transposed() @ normal).normalized()
    if normal.z<0:normal=-normal
    return p,normal


def build():
    PATCHES.clear()
    m=dict(hull=material('Falari-Lourn | worn blue pressure shell',(.10,.15,.24),.70,.61),wing=material('Falari-Lourn | worn green wing',(.10,.30,.22),.70,.63),gold=material('Falari-Lourn | dulled gold fixtures',(.32,.28,.08),.72,.63),
        edge=material('Falari-Lourn | oxidized service alloy',(.19,.23,.27),.78,.62),dark=material('Falari-Lourn | carbon dark seams',(.012,.015,.021),.40,.80))
    body=hull(m['hull']);wing(m['wing'])
    for i,(x,y) in enumerate(FIXTURES):
        patch('Falari-Lourn green saddle '+str(i),'wing',x,y,.16,.18,m['wing'],top=.016,back=-.014)
        obj=vessel('Falari-Lourn gold wing fixture '+str(i),GOLD_PROFILE,m['gold'],[]);obj.location=(x,y,wing_skin(x,y)+.015)
    bpy.context.view_layer.update()
    # Paired body-facing details are an authored layout, not five calibrated equipment mounts.
    for side in [-1,1]:
        n=Vector((0,side,0));point=Vector((0,side*.73,-.035))
        cast_bezel('Falari-Lourn body bezel '+str(side),body,point,n,.12,m['gold'])
        cylinder('Falari-Lourn body face '+str(side),point+n*.030,.075,.016,m['edge'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    for i,x in enumerate([-.22,.22]):
        cover='Falari-Lourn hull service cover '+str(i);patch(cover,'hull',x,.10,.16,.28,m['hull'])
        for j,y in enumerate([.035,.165]):patch('Falari-Lourn hull service slot '+str(i)+' '+str(j),'hull',x,y,.10,.012,m['dark'],top=.015,back=.004,support=cover)
        for j,dx in enumerate([-.055,.055]):
            for k,dy in enumerate([-.105,.105]):
                p,n=roof(x+dx,.10+dy);cylinder('Falari-Lourn hull fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.006,.020,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    for side in [-1,1]:patch('Falari-Lourn wing inset '+str(side),'wing',0,side*1.525,.035,1.35,m['dark'],top=.004,back=-.012)
    return m
