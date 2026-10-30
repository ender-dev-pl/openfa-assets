"""First BR3A interpretation: narrow gold spindle and broad rose/gold terminal."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_annuli import annulus

PROFILES={'Morning Glory gold spindle':[(-.90,.26,0,.26),(-.60,.28,0,.28),(-.20,.22,0,.22),(.55,.16,0,.16),(1.25,.09,0,.09),(1.80,.04,0,.04)],
 'Morning Glory rose terminal':[(-1.24,.10,0,.10),(-1.18,.31,0,.31),(-1.10,.46,0,.46),(-.98,.51,0,.51),(-.80,.49,0,.49),(-.68,.30,0,.30),(-.55,.26,0,.26)],
 'Morning Glory gold terminal face':[(-1.27,.10,0,.10),(-1.23,.21,0,.21),(-1.18,.285,0,.285),(-1.135,.30,0,.30)],
 'Morning Glory rose axial tip':[(-1.48,.04,0,.04),(-1.40,.085,0,.085),(-1.24,.105,0,.105),(-1.21,.09,0,.09)]}
DENTS={'Morning Glory gold spindle':(.07,.30,.003),'Morning Glory rose terminal':(.22,-.92,.004)}
SOCKETS={'AlignmentForward':((0,-1.50,0),(0,-1,0))}
PATCHES=[]
BANDS=[('Morning Glory terminal gold rim','Morning Glory rose terminal',-1.10,-1.035,.008,.018,'gold'),
 ('Morning Glory shaft grey collar','Morning Glory gold spindle',1.55,1.65,.008,.012,'edge'),
 ('Morning Glory axial tip band','Morning Glory rose axial tip',-1.39,-1.34,.006,.012,'gold')]


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    if name not in DENTS:return 0
    cx,cy,depth=DENTS[name];return depth*math.exp(-2*(((x-cx)/.08)**2+((y-cy)/.12)**2))


def surface(name,phi,y,offset=0):
    w,z,h=section(name,y);x=w*math.cos(phi);height=z+h*math.sin(phi)
    if math.sin(phi)>0:height-=dent(name,x,y)
    return Vector((x,y,height))+Vector((math.cos(phi),0,math.sin(phi)))*offset


def mesh(name,vertices,faces,surface_material):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);return obj


def hull(name,surface_material):
    rows=[];profile=PROFILES[name];count=128
    for a,b in zip(profile,profile[1:]):
        steps=math.ceil((b[0]-a[0])/.018);rows.extend(a[0]+(b[0]-a[0])*i/steps for i in range(steps))
    rows.append(profile[-1][0]);vertices=[surface(name,i*math.tau/count,y) for y in rows for i in range(count)]
    first=len(vertices);last=first+1;vertices.extend([(0,rows[0],profile[0][2]),(0,rows[-1],profile[-1][2])]);end=(len(rows)-1)*count
    faces=[(first,i,(i+1)%count) for i in range(count)]+[(last,end+(i+1)%count,end+i) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(rows)-1) for i in range(count))
    obj=mesh(name,vertices,faces,surface_material)
    for face in obj.data.polygons:face.use_smooth=len(face.vertices)==4
    return obj


def patch(name,owner,y0,y1,phi,width,surface_material,top=.007,back=-.016,support=None):
    spec=dict(name=name,owner=owner,y0=y0,y1=y1,phi=phi,width=width,top=top,back=back,support=support or owner)
    columns=17;steps=max(8,math.ceil((y1-y0)/.022));heights=[y0+(y1-y0)*i/steps for i in range(steps+1)]
    for y,_,_,_ in PROFILES[owner]:
        if y0<y<y1:heights=[h for h in heights if abs(h-y)>1e-8]+[y]
    heights.sort();height=len(heights);size=columns*height;vertices=[]
    for offset in [top,back]:
        vertices.extend(surface(owner,phi+width*(-1+2*i/(columns-1)),y,offset) for y in heights for i in range(columns))
    faces=[]
    for row in range(height-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,height)]+list(reversed(range((height-1)*columns,(height-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    obj=mesh(name,vertices,faces,surface_material);PATCHES.append(spec);return obj


def build():
    PATCHES.clear()
    m=dict(gold=material('Morning Glory | worn gold spindle',(.50,.34,.12),.72,.57),hull=material('Morning Glory | worn rose copper',(.40,.17,.15),.68,.58),
        edge=material('Morning Glory | oxidized titanium',(.23,.25,.28),.78,.58),dark=material('Morning Glory | carbon dark joints',(.016,.018,.020),.40,.80))
    for name in PROFILES:hull(name,m['gold' if 'gold' in name else 'hull'])
    for name,owner,low,high,outside,inside,key in BANDS:
        heights=sorted(set([low,high]+[y for y,_,_,_ in PROFILES[owner] if low<y<high]))
        rows=[(y,section(owner,y)[0]+outside,section(owner,y)[0]-inside) for y in heights]
        obj=annulus(name,(0,0),rows,m[key],(0,(low+high)/2,0));obj.rotation_euler=(-math.pi/2,0,0)
    cylinder('Morning Glory grey shaft terminal',(0,1.80,0),.045,.10,m['edge'],vertices=48,rotation=(-math.pi/2,0,0))
    rose='Morning Glory rose terminal';spindle='Morning Glory gold spindle'
    for i in range(4):
        phi=i*math.pi/2
        patch('Morning Glory gold crown applique '+str(i),rose,-1.12,-.78,phi,.04,m['gold'])
        patch('Morning Glory rose shaft inlay '+str(i),spindle,-.40,.75,phi,.035,m['hull'],top=.006,back=-.015)
    for side in [-1,1]:
        phi=side*math.pi/2;cover='Morning Glory shaft service cover '+str(side)
        patch(cover,spindle,.15,.65,phi,.16,m['hull'],top=.012,back=-.014)
        for i,y in enumerate([.25,.40,.55]):patch('Morning Glory shaft service slot '+str(side)+' '+str(i),spindle,y-.006,y+.006,phi,.10,m['dark'],top=.018,back=.006,support=cover)
        for j,angle in enumerate([phi-.12,phi+.12]):
            n=Vector((math.cos(angle),0,math.sin(angle)))
            for k,y in enumerate([.22,.58]):
                cylinder('Morning Glory cover fastener '+str(side)+' '+str(j)+' '+str(k),surface(spindle,angle,y,.013),.006,.014,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    bpy.context.view_layer.update();body=bpy.data.objects[rose]
    for i in range(8):
        phi=(i+.5)*math.pi/4;x=.38*math.cos(phi);z=.38*math.sin(phi);hit,p,_,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        cylinder('Morning Glory terminal rim stud '+str(i),(x,p.y-.002,z),.010,.018,m['gold'],vertices=16,rotation=(math.pi/2,0,0))
    return m
