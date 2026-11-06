"""First BR1C craft; hollow housings and hidden assemblies are authored interpretation."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

PROFILES={'WidowMaker gold pressure hull':[(-1.55,.35,0,.35),(-1.40,.44,0,.44),(-.75,.50,0,.50),(0,.61,0,.61),(.80,.75,0,.75),(1.30,.77,0,.77),(1.52,.72,0,.72)],
 'WidowMaker rose nose':[(-2.05,.04,0,.04),(-2.01,.28,0,.28),(-1.90,.59,0,.59),(-1.78,.67,0,.67),(-1.64,.64,0,.64),(-1.55,.44,0,.44),(-1.45,.38,0,.38)]}
DENTS={'WidowMaker gold pressure hull':(.35,.15,.005),'WidowMaker rose nose':(.25,-1.84,.004)}
SOCKETS={'AlignmentForward':((0,-2.14,0),(0,-1,0))}
PATCHES=[]
STRAKE_OUTLINE=[(-.60,.49),(.30,.82),(1.45,.93),(1.54,.78),(.40,.64)]
DUCT_ROWS=[(0,.23,.145),(.05,.25,.15),(.26,.24,.17),(.32,.22,.17),(.36,.23,.17)]


def section(name,y):
    for a,b in zip(PROFILES[name],PROFILES[name][1:]):
        if a[0]-1e-9<=y<=b[0]+1e-9:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError((name,y))


def dent(name,x,y):
    cx,cy,depth=DENTS[name];return depth*math.exp(-2*(((x-cx)/.10)**2+((y-cy)/.12)**2))


def surface(name,phi,y,offset=0):
    w,z,h=section(name,y);x=w*math.cos(phi);height=z+h*math.sin(phi)
    if math.sin(phi)>0:height-=dent(name,x,y)
    return Vector((x,y,height))+Vector((math.cos(phi),0,math.sin(phi)))*offset


def mesh(name,vertices,faces,surface_material):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);return obj


def hull(name,surface_material):
    rows=[];profile=PROFILES[name];count=128
    for a,b in zip(profile,profile[1:]):
        steps=math.ceil((b[0]-a[0])/.020);rows.extend(a[0]+(b[0]-a[0])*i/steps for i in range(steps))
    rows.append(profile[-1][0]);vertices=[surface(name,i*math.tau/count,y) for y in rows for i in range(count)]
    first=len(vertices);last=first+1;vertices.extend([(0,rows[0],profile[0][2]),(0,rows[-1],profile[-1][2])]);end=(len(rows)-1)*count
    faces=[(first,i,(i+1)%count) for i in range(count)]+[(last,end+(i+1)%count,end+i) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(rows)-1) for i in range(count))
    obj=mesh(name,vertices,faces,surface_material)
    for face in obj.data.polygons:face.use_smooth=len(face.vertices)==4
    return obj


def patch_halfwidth(spec,y):
    for (a,wa),(b,wb) in zip(spec['widths'],spec['widths'][1:]):
        if a-1e-9<=y<=b+1e-9:return wa+(wb-wa)*(y-a)/(b-a)
    raise ValueError((spec['name'],y))


def patch(name,owner,y0,y1,phi,width,surface_material,top=.028,back=-.022,widths=None,drift=0,support=None):
    spec=dict(name=name,owner=owner,y0=y0,y1=y1,phi=phi,widths=widths or [(y0,width),(y1,width)],drift=drift,top=top,back=back,support=support or owner)
    width=17;steps=max(8,math.ceil((y1-y0)/.025));heights=[y0+(y1-y0)*i/steps for i in range(steps+1)]
    breaks=[y for y,_,_,_ in PROFILES[owner]]+[y for y,_ in spec['widths']]
    for y in breaks:
        if y0<y<y1:heights=[h for h in heights if abs(h-y)>1e-8]+[y]
    heights.sort();height=len(heights);size=width*height;vertices=[]
    for offset in [top,back]:
        for y in heights:
            centre=phi+drift*(y-y0)/(y1-y0);half=patch_halfwidth(spec,y)
            vertices.extend(surface(owner,centre+half*(-1+2*i/(width-1)),y,offset) for i in range(width))
    faces=[]
    for row in range(height-1):
        for col in range(width-1):
            a=row*width+col;f=(a,a+1,a+width+1,a+width);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(width))+[row*width+width-1 for row in range(1,height)]+list(reversed(range((height-1)*width,(height-1)*width+width-1)))+[row*width for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    obj=mesh(name,vertices,faces,surface_material);PATCHES.append(spec);return obj


def strake(name,phi,surface_material):
    n=Vector((math.cos(phi),0,math.sin(phi)));t=Vector((-math.sin(phi),0,math.cos(phi)));count=len(STRAKE_OUTLINE)
    vertices=[n*r+t*thickness+Vector((0,y,0)) for thickness in [-.022,.022] for y,r in STRAKE_OUTLINE]
    faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    obj=mesh(name,vertices,faces,surface_material);bevel=obj.modifiers.new('Small strake edge','BEVEL');bevel.width=.006;bevel.segments=2;return obj


def build():
    PATCHES.clear()
    m=dict(gold=material('WidowMaker | worn gold hull',(.50,.34,.12),.72,.57),hull=material('WidowMaker | worn rose copper',(.40,.17,.15),.68,.58),slate=material('WidowMaker | worn grey armour',(.18,.20,.22),.72,.61),
        edge=material('WidowMaker | oxidized titanium',(.23,.25,.28),.78,.49),dark=material('WidowMaker | carbon dark recesses',(.016,.018,.020),.40,.80))
    owner='WidowMaker gold pressure hull';nose='WidowMaker rose nose';hull(owner,m['gold']);cap=hull(nose,m['hull'])
    for i in range(4):
        phi=i*math.pi/2
        patch('WidowMaker grey cheek '+str(i),owner,-.55,1.42,phi,.46,m['slate'],widths=[(-.55,.02),(.65,.46),(1.42,.36)])
        strake('WidowMaker diagonal strake '+str(i),phi+math.pi/4,m['slate'])
        # Four round openings are observed; their exact function is not established.
        x=.39*math.cos(phi);z=.39*math.sin(phi)
        obj=annulus('WidowMaker aft duct housing '+str(i),(0,0),DUCT_ROWS,m['slate'],(0,.18,0));obj.location=(x,1.38,z);obj.rotation_euler=(-math.pi/2,0,0)
        cylinder('WidowMaker recessed duct floor '+str(i),(x,1.52,z),.165,.04,m['dark'],vertices=64,rotation=(-math.pi/2,0,0))
        for side in [-1,1]:
            patch('WidowMaker rose neck accent '+str(i)+' '+str(side),owner,-1.25,-.60,phi+side*.07,.035,m['hull'],top=.008,back=-.017,drift=side*.14)
    normal=Vector((0,-1,0));point=Vector((0,-2.065,0))
    cast_bezel('WidowMaker central nose bezel',cap,point,normal,.13,m['edge'])
    cylinder('WidowMaker central nose face',(0,-2.095,0),.085,.018,m['dark'],vertices=64,rotation=(math.pi/2,0,0))
    bpy.context.view_layer.update()
    for i in range(4):
        phi=i*math.pi/2;x=.40*math.cos(phi);z=.40*math.sin(phi);hit,p,_,_=cap.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        cylinder('WidowMaker gold nose stud '+str(i),(x,p.y-.005,z),.045,.030,m['gold'],vertices=32,rotation=(math.pi/2,0,0))
    for side in [-1,1]:
        phi=side*math.pi/2;cheek='WidowMaker grey cheek '+str(1 if side==1 else 3)
        cover='WidowMaker service cover '+str(side)
        patch(cover,owner,.30,.85,phi,.16,m['gold'],top=.045,back=.015,support=cheek)
        for i,y in enumerate([.40,.56,.72]):patch('WidowMaker service slot '+str(side)+' '+str(i),owner,y-.008,y+.008,phi,.10,m['dark'],top=.052,back=.038,support=cover)
        for j,angle in enumerate([phi-.12,phi+.12]):
            n=Vector((math.cos(angle),0,math.sin(angle)))
            for k,y in enumerate([.36,.80]):
                cylinder('WidowMaker cover fastener '+str(side)+' '+str(j)+' '+str(k),surface(owner,angle,y,.047),.012,.024,m['gold'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
