"""First AC1C interpretation: paired upright grey crescents with fitted red fields."""
import math
import bpy,bmesh
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,beam,finish

BODY='Fighter warm axial body'
PROFILES={BODY:[(-1.50,0,.015,.015),(-.80,0,.12,.10),(0,0,.22,.22),(.45,0,.16,.16),(.80,0,.030,.030)]}
DENTS={BODY:(.03,.005)}
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.55,0),(0,-1,0))}


def section(owner,y):
    for (a,xa,wa,ha),(b,xb,wb,hb) in zip(PROFILES[owner],PROFILES[owner][1:]):
        if a-1e-8<=y<=b+1e-8:
            t=(y-a)/(b-a);return xa+(xb-xa)*t,wa+(wb-wa)*t,ha+(hb-ha)*t
    raise ValueError(y)


def dent(owner,u,y):
    cy,depth=DENTS[owner];return depth*math.exp(-2*((u/.24)**2+((y-cy)/.12)**2))


def crown(owner,u,y):
    x,w,h=section(owner,y);return Vector((x+w*u,y,h*math.sqrt(max(0,1-u*u))-dent(owner,u,y)))


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def loft(owner,surface):
    p=PROFILES[owner];ys=[p[0][0]+(p[-1][0]-p[0][0])*i/160 for i in range(161)]
    for y in [r[0] for r in p]+[DENTS[owner][0]]:ys=[v for v in ys if abs(v-y)>1e-7]+[y]
    ys.sort();count=64;vertices=[]
    for y in ys:
        x,w,h=section(owner,y)
        for i in range(count):
            phi=math.tau*i/count;u=math.cos(phi);z=h*math.sin(phi)
            if math.sin(phi)>0:z-=dent(owner,u,y)*math.sin(phi)**4
            vertices.append((x+w*u,y,z))
    faces=[tuple(reversed(range(count))),tuple((len(ys)-1)*count+i for i in range(count))]
    faces.extend((r*count+i,r*count+(i+1)%count,(r+1)*count+(i+1)%count,(r+1)*count+i) for r in range(len(ys)-1) for i in range(count))
    return mesh(owner,vertices,faces,surface)


def patch(name,owner,y0,y1,width,surface,top=.008,back=-.015,support=None):
    cols=17;rows=25;vertices=[]
    for offset in [top,back]:
        for r in range(rows):
            y=y0+(y1-y0)*r/(rows-1)
            for c in range(cols):
                p=crown(owner,width*(-1+2*c/(cols-1)),y);p.z+=offset;vertices.append(p)
    size=cols*rows;faces=[]
    for r in range(rows-1):
        for c in range(cols-1):
            a=r*cols+c;f=(a,a+1,a+cols+1,a+cols);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[r*cols for r in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,vertices,faces,surface)
    PATCHES.append(dict(name=name,owner=owner,y0=y0,y1=y1,width=width,top=top,back=back,support=support or owner));return obj


def hull_frame(owner,u,y):
    obj=bpy.data.objects[owner];p=crown(owner,u,y);inv=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inv @ (p+Vector((0,0,2))),inv.to_3x3() @ Vector((0,0,-1)));assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ n).normalized()



def plate_dent(side,t,v):return (.005 if side==-1 else .006)*math.exp(-2*((t/.16)**2+((v-.5)/.18)**2))


def plate_surface(side,t,v,offset=0):
    return Vector((side*(.69-plate_dent(side,t,v)+offset),(.40+.20*v)*math.cos(t)-(1.10+.12*v)*math.sin(t)**2,(.43+.17*v)*math.sin(t)))


def plate_grid(name,side,t0,t1,v0,v1,surface,top=0,back=-.08,support=None):
    cols=17;rows=129;vertices=[]
    for offset in [top,back]:
        for r in range(rows):
            t=t0+(t1-t0)*r/(rows-1)
            for c in range(cols):vertices.append(plate_surface(side,t,v0+(v1-v0)*c/(cols-1),offset))
    size=cols*rows;faces=[]
    for r in range(rows-1):
        for c in range(cols-1):
            a=r*cols+c;f=(a,a+1,a+cols+1,a+cols);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[r*cols for r in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,vertices,faces,surface)
    if support:PATCHES.append(dict(name=name,side=side,t0=t0,t1=t1,v0=v0,v1=v1,top=top,back=back,support=support,domain='crescent'))
    return obj


def plate_frame(side,t,v):
    obj=bpy.data.objects['Fighter crescent '+str(side)];p=plate_surface(side,t,v);hit,where,n,_=obj.ray_cast(p+Vector((side*2,0,0)),Vector((-side,0,0)));assert hit;return where,n.normalized()


def build():
    m=dict(bronze=material('Fighter | worn warm axial body',(.28,.16,.065),.72,.70),hull=material('Fighter | worn grey crescents',(.25,.27,.28),.72,.68),red=material('Fighter | worn red crescent fields',(.38,.075,.07),.62,.72),edge=material('Fighter | oxidized service alloy',(.16,.20,.21),.78,.65),dark=material('Fighter | dark recesses',(.012,.016,.018),.40,.80),amber=material('Fighter | dull yellow axial tip',(.44,.32,.035),.50,.72))
    loft(BODY,m['bronze'])
    for side in [-1,1]:
        owner='Fighter crescent '+str(side);plate_grid(owner,side,-1.75,1.75,0,1,m['hull'])
        beam('Fighter transverse link '+str(side),(0,.50,0),(side*.67,.50,0),.025,m['bronze'])
        red='Fighter red field '+str(side);plate_grid(red,side,-1.45,1.45,.15,.72,m['red'],.008,-.015,owner)
        cover='Fighter plate cover '+str(side);plate_grid(cover,side,-.27,.27,.30,.65,m['hull'],.016,.003,red)
        for j,t in enumerate([-.11,.11]):plate_grid('Fighter plate strip '+str(side)+' '+str(j),side,t-.012,t+.012,.36,.59,m['dark'],.024,.010,cover)
        for j,t in enumerate([-.21,.21]):
            for k,v in enumerate([.36,.59]):
                p,n=plate_frame(side,t,v);cylinder('Fighter plate fastener '+str(side)+' '+str(j)+' '+str(k),p+n*.016,.003,.022,m['edge'],16).rotation_euler=n.to_track_quat('Z','Y').to_euler()
    beam('Fighter axial stem',(0,.75,0),(0,1.06,0),.018,m['bronze'])
    cylinder('Fighter yellow terminal',(0,1.06,0),.030,.045,m['amber'],32,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    cover='Fighter body cover';patch(cover,BODY,-.16,.15,.44,m['bronze'])
    for j,y in enumerate([-.06,.06]):patch('Fighter body strip '+str(j),BODY,y-.006,y+.006,.30,m['dark'],.016,.003,cover)
    for j,y in enumerate([-.11,.10]):
        for k,u in enumerate([-.33,.33]):
            p,n=hull_frame(BODY,u,y);cylinder('Fighter body fastener '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16).rotation_euler=n.to_track_quat('Z','Y').to_euler()
    return m
