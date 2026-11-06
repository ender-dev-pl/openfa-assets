"""First AR2C interpretation: broad silver/gold wing, raised pressure body and blue-grey fittings."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish

WING='Shielded Multi broad metal wing'
ROOF='Shielded Multi central pressure body'
PROFILES={WING:[(-2.20,.02,-.04,.02),(-1.70,.36,-.04,.02),(-.70,1.15,-.04,.02),(0,1.60,-.04,.02),(.70,1.15,-.04,.02),(1.70,.36,-.04,.02),(2.20,.02,-.04,.02)],
 ROOF:[(-.95,.04,0,.04),(-.70,.40,.04,.24),(-.20,.70,.06,.38),(.30,.72,.06,.38),(.75,.40,.04,.24),(.95,.04,0,.04)]}
CENTRES={WING:0,ROOF:0}
DENTS={ROOF:(0,-.15,.005)}
WING_DENTS=[(-.80,.70,.004),(.80,.70,.004)]
SOCKETS={'AlignmentForward':((0,-2.22,-.04),(0,-1,0))}
PATCHES=[]
COVERS=[(ROOF,.10,.45,-.60,-.30),(ROOF,.10,.45,.30,.60),(WING,-.25,.25,-.72,-.56),(WING,-.25,.25,.56,.72)]


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    samples=WING_DENTS if name==WING else [DENTS[name]]
    return sum(depth*math.exp(-2*(((x-cx)/.08)**2+((y-cy)/.10)**2)) for cx,cy,depth in samples)


def skin(name,x,y):
    width,z,height=section(name,y);u=abs(x/width)
    return (z-height*u*u if name==WING else z+height*math.sqrt(max(0,1-u*u)))-dent(name,x,y)


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
    if name!=WING:return cowl(name,surface)
    ys,us=grid(name,PROFILES[name][0][0],PROFILES[name][-1][0],-1,1,.022);top=[];back=[]
    for y in ys:
        width,_,_=section(name,y)
        for u in us:
            x=width*u;top.append((x,y,skin(name,x,y)));back.append((x,y,skin(name,x,y)-.07))
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


def colour_halves(obj,gold):
    obj.data.materials.append(gold)
    for face in obj.data.polygons:
        face.material_index=1 if sum(obj.data.vertices[i].co.x for i in face.vertices)<0 else 0
    obj['material_layout']='Authored port gold / starboard silver interpretation; exact source division unresolved'


def build():
    PATCHES.clear()
    m=dict(hull=material('Shielded Multi | worn silver alloy',(.27,.29,.30),.78,.64),gold=material('Shielded Multi | worn gold alloy',(.32,.23,.10),.76,.64),edge=material('Shielded Multi | oxidized blue grey fittings',(.12,.17,.24),.72,.65),dark=material('Shielded Multi | carbon dark seams',(.012,.016,.018),.40,.80),amber=material('Shielded Multi | dull amber inserts',(.46,.29,.08),.55,.68))
    for owner in [WING,ROOF]:colour_halves(shell(owner,m['hull']),m['gold'])
    bpy.context.view_layer.update()
    for i,(owner,y0,y1,u0,u1) in enumerate(COVERS):
        cover='Shielded Multi service cover '+str(i);patch(cover,owner,y0,y1,u0,u1,m['gold' if u0<0 else 'hull'])
        for j,f in enumerate([.32,.68]):
            y=y0+(y1-y0)*f;patch('Shielded Multi service slot '+str(i)+' '+str(j),owner,y-.007,y+.007,u0+(u1-u0)*.18,u1-(u1-u0)*.18,m['dark'],top=.015,back=.004,support=cover)
        for j,f in enumerate([.16,.84]):
            y=y0+(y1-y0)*f;w,_,_=section(owner,y)
            for k,uf in enumerate([.18,.82]):
                x=w*(u0+(u1-u0)*uf);p,n=roof(owner,x,y);cylinder('Shielded Multi fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.0045,.020,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    owner=ROOF;panel='Shielded Multi forward service inset';patch(panel,owner,-.55,-.35,-.20,.20,m['dark'])
    for j,y in enumerate([-.52,-.45,-.38]):patch('Shielded Multi forward alloy slat '+str(j),owner,y-.006,y+.006,-.14,.14,m['edge'],top=.015,back=.003,support=panel)
    for side in [-1,1]:
        a,b=(.82,.92) if side==1 else (-.92,-.82);saddle='Shielded Multi fitting saddle '+str(side)
        patch(saddle,WING,-.18,.18,a,b,m['gold' if side==-1 else 'hull'],top=.024,back=-.015)
        a,b=(.84,.90) if side==1 else (-.90,-.84)
        patch('Shielded Multi blue grey fitting '+str(side),WING,-.16,.16,a,b,m['edge'],top=.11,back=.012,support=saddle)
        owner=ROOF;a,b=(.78,.90) if side==1 else (-.90,-.78);panel='Shielded Multi side dark inset '+str(side)
        patch(panel,owner,-.12,.12,a,b,m['dark'])
        a,b=(.81,.87) if side==1 else (-.87,-.81)
        for j,y in enumerate([-.085,0,.085]):patch('Shielded Multi side amber insert '+str(side)+' '+str(j),owner,y-.015,y+.015,a,b,m['amber'],top=.016,back=.003,support=panel)
    return m
