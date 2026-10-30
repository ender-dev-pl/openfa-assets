"""Independent first Mauna transporter: three genuinely notched extruded sections."""
import math
import bpy,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from build_openfa_assets import material,box,cylinder,finish

TOWERS={-1:-1.12,0:0,1:1.12}
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-.70,0),(0,-1,0))}
DENTS={-1:.006,0:.007,1:.008}


def dent(index,y,z):return DENTS[index]*math.exp(-2*((y/.10)**2+((z-1.25)/.13)**2))


def skin(index,side,y,z):return TOWERS[index]+side*(.32-dent(index,y,z))


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def tower(index,surface):
    outline=[(-.28,.35),(.28,.35)]
    for z in [.90,1.40,1.90]:outline.extend([(.28,z),(.10,z),(.10,z+.20),(.28,z+.20)])
    outline.extend([(.28,2.35),(-.28,2.35)])
    polygon=[Vector((0,y,z)) for y,z in outline];triangles=tessellate_polygon([polygon]);vertices=[];faces=[];lookup={};steps=16
    def vertex(side,p):
        key=(side,round(p.y,9),round(p.z,9))
        if key not in lookup:
            lookup[key]=len(vertices);vertices.append((skin(index,side,p.y,p.z),p.y,p.z))
        return lookup[key]
    for side in [-1,1]:
        for triangle in triangles:
            a,b,c=[polygon[i] for i in triangle]
            ids={}
            for i in range(steps+1):
                for j in range(steps+1-i):ids[i,j]=vertex(side,a+(b-a)*(i/steps)+(c-a)*(j/steps))
            for i in range(steps):
                for j in range(steps-i):
                    faces.append((ids[i,j],ids[i+1,j],ids[i,j+1]))
                    if i+j<steps-1:faces.append((ids[i+1,j],ids[i+1,j+1],ids[i,j+1]))
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        for i in range(steps):
            p=a.lerp(b,i/steps);q=a.lerp(b,(i+1)/steps);faces.append((vertex(-1,p),vertex(-1,q),vertex(1,q),vertex(1,p)))
    return mesh('Transport tower '+str(index),vertices,faces,surface)


def patch(name,index,side,y0,y1,z0,z1,surface,top=.008,back=-.015,support=None):
    cols=17;rows=41;vertices=[]
    for offset in [top,back]:
        for r in range(rows):
            z=z0+(z1-z0)*r/(rows-1)
            for c in range(cols):
                y=y0+(y1-y0)*c/(cols-1);vertices.append((skin(index,side,y,z)+side*offset,y,z))
    size=cols*rows;faces=[]
    for r in range(rows-1):
        for c in range(cols-1):
            a=r*cols+c;f=(a,a+1,a+cols+1,a+cols);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[r*cols for r in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));obj=mesh(name,vertices,faces,surface)
    PATCHES.append(dict(name=name,index=index,side=side,y0=y0,y1=y1,z0=z0,z1=z1,top=top,back=back,support=support or 'Transport tower '+str(index)));return obj


def face_frame(index,side,y,z):
    obj=bpy.data.objects['Transport tower '+str(index)];inv=obj.matrix_world.inverted();hit,p,n,_=obj.ray_cast(inv @ Vector((TOWERS[index]+side*2,y,z)),(inv.to_3x3() @ Vector((-side,0,0))).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ n).normalized()


def build():
    hull=material('Transport | worn grey casing',(.23,.24,.25),.72,.70)
    blue=material('Transport | worn pale blue bands',(.20,.32,.38),.58,.72)
    bronze=material('Transport | worn warm lower details',(.30,.18,.08),.72,.72)
    edge=material('Transport | oxidized service alloy',(.17,.19,.20),.78,.65)
    dark=material('Transport | dark recesses',(.012,.016,.018),.40,.80)
    box('Transport lower housing',(0,0,0),(3.40,1.10,.80),hull,.13)
    for index,x in TOWERS.items():
        tower(index,hull)
        for side in [-1,1]:
            label=str(index)+' '+str(side);frame='Transport tower frame '+label
            patch(frame,index,side,-.23,-.03,.60,2.15,hull)
            patch('Transport tower inset '+label,index,side,-.20,-.06,.75,2.00,edge,.015,.003,frame)
            for i,z in enumerate([.95,1.80]):patch('Transport tower strip '+label+' '+str(i),index,side,-.185,-.075,z-.012,z+.012,dark,.022,.010,'Transport tower inset '+label)
            for j,y in enumerate([-.215,-.045]):
                for k,z in enumerate([.66,2.09]):
                    p,n=face_frame(index,side,y,z);cylinder('Transport fastener '+label+' '+str(j)+' '+str(k),p+n*.010,.004,.024,edge,20).rotation_euler=n.to_track_quat('Z','Y').to_euler()
        for j,z in enumerate([.60,1.20,1.70,2.25]):
            box('Transport blue band '+str(index)+' '+str(j),(x,-.281,z),(.56,.025,.08),blue,.004)
        box('Transport rear service plate '+str(index),(x,-.283,1.45),(.44,.030,.32),hull,.008)
    for side in [-1,1]:
        box('Transport lower blue trim '+str(side),(0,side*.546,-.19),(2.95,.028,.07),blue,.004)
        box('Transport long dark seam '+str(side),(0,side*.548,.08),(2.85,.030,.025),dark,.003)
        for i,x in enumerate([-.28,.28]):box('Transport lower service block '+str(side)+' '+str(i),(x,side*.552,-.02),(.20,.035,.22),edge,.006)
    for i,x in enumerate([-1.45,1.45]):
        box('Transport warm lower foot '+str(i),(x,0,-.43),(.22,.42,.25),bronze,.025)
        box('Transport end inset '+str(i),(math.copysign(1.691,x),0,-.02),(.035,.40,.30),edge,.006)
        box('Transport end warm detail '+str(i),(math.copysign(1.713,x),0,-.02),(.025,.14,.13),bronze,.004)
    for i,x in enumerate([-.32,.32]):box('Transport grey lower block '+str(i),(x,0,-.43),(.56,.52,.24),hull,.015)
