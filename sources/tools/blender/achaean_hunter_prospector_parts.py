"""First independent AC0A interpretation: green spine and two swept red lobes."""
import math
import bpy,bmesh
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,finish

BODY='Hunter green body'
PROFILES={BODY:[(-1.65,0,.015,.015),(-1.40,0,.04,.04),(-.50,0,.20,.18),(0,0,.22,.20),(.45,0,.10,.10)]}
for side in [-1,1]:PROFILES['Hunter red lobe '+str(side)]=[(y,side*x,w,h) for y,x,w,h in [(-.25,.15,.13,.12),(0,.45,.22,.14),(.50,.70,.15,.10),(1.20,.82,.08,.06),(1.55,.86,.012,.012)]]
DENTS={BODY:(-.10,.005),'Hunter red lobe -1':(.60,.004),'Hunter red lobe 1':(.60,.005)}
PATCHES=[]
PANELS=[(BODY,-.22,.05),('Hunter red lobe -1',.35,.75),('Hunter red lobe 1',.35,.75)]
SOCKETS={'AlignmentForward':((0,-1.70,0),(0,-1,0))}


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


def build():
    m=dict(green=material('Hunter | worn green shell',(.09,.26,.10),.65,.70),red=material('Hunter | worn red lobes',(.37,.075,.07),.65,.72),bronze=material('Hunter | worn warm central spar',(.27,.18,.075),.72,.70),edge=material('Hunter | oxidized service alloy',(.16,.20,.19),.78,.65),dark=material('Hunter | dark recesses',(.012,.016,.018),.40,.80))
    for owner in PROFILES:loft(owner,m['green' if owner==BODY else 'red'])
    box('Hunter central warm spar',(0,.55,0),(.12,1.25,.10),m['bronze'],.015)
    box('Hunter central red tip',(0,1.20,0),(.10,.18,.08),m['red'],.010)
    for i,(owner,y0,y1) in enumerate(PANELS):
        cover='Hunter service cover '+str(i);patch(cover,owner,y0,y1,.45,m['green' if owner==BODY else 'red'])
        for j,f in enumerate([.32,.68]):
            y=y0+(y1-y0)*f;patch('Hunter service strip '+str(i)+' '+str(j),owner,y-.006,y+.006,.30,m['dark'],.016,.003,cover)
        for j,f in enumerate([.15,.85]):
            y=y0+(y1-y0)*f
            for k,u in enumerate([-.34,.34]):
                p,n=hull_frame(owner,u,y);cylinder('Hunter fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16).rotation_euler=n.to_track_quat('Z','Y').to_euler()
    return m
