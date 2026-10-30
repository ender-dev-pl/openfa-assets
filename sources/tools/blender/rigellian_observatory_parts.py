"""First RI4C station: paletted silhouette guides independently authored solid parts."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

PROFILES={'Observatory saucer pressure hull':[(-.625,.18),(-.5625,.70),(-.375,1.25),(-.125,1.65),(0,1.75),(.125,1.66),(.3125,1.40),(.5,.90),(.625,.25)],
 'Observatory axial green chambers':[(-2.125,.04),(-1.9375,.12),(-1.75,.18),(-1.375,.32),(-1.0,.34),(-.5625,.24),(.4375,.27),(.875,.35),(1.1875,.24),(1.3125,.17),(1.75,.16),(2.0,.07)]}
DENTS={'Observatory saucer pressure hull':(-.95,.32,.006),'Observatory axial green chambers':(-math.pi/2,1.50,.004)}
SCALE_Y={'Observatory saucer pressure hull':.70,'Observatory axial green chambers':1.0}
SOCKETS={'AlignmentAxis':((0,0,2.88),(0,0,1))}
BANDS=[('Observatory equatorial copper rim','Observatory saucer pressure hull',-.035,.035)]+[
 ('Observatory axial copper collar '+str(i),'Observatory axial green chambers',z-.025,z+.025)
 for i,z in enumerate([-1.88,-1.48,-1.03,.75,1.08,1.36,1.72])]
FIN_OUTLINE=[(.54,.48),(1.10,.32),(.90,.92),(.65,1.88),(.60,1.05),(.42,.65)]


def radius(name,phi,z):
    angle,height,depth=DENTS[name];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle))
    return profile_radius(PROFILES[name],z)-depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2))


def surface(name,phi,z,offset=0):
    r=radius(name,phi,z)+offset;return Vector((r*math.cos(phi),r*math.sin(phi)*SCALE_Y[name],z))


def patch(name,owner,z0,z1,phi0,phi1,surface_material):
    width=17;height=13;size=width*height;vertices=[]
    for offset in [.007,-.018]:
        vertices.extend(surface(owner,phi0+(phi1-phi0)*col/(width-1),z0+(z1-z0)*row/(height-1),offset)
            for row in range(height) for col in range(width))
    faces=[]
    for row in range(height-1):
        for col in range(width-1):
            a=row*width+col;f=(a,a+1,a+width+1,a+width);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(width))+[row*width+width-1 for row in range(1,height)]+list(reversed(range((height-1)*width,(height-1)*width+width-1)))+[row*width for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    return mesh(name,vertices,faces,surface_material)


def mesh(name,vertices,faces,surface_material):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0)
    return obj


def fin(name,phi,side,surface_material):
    radial=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-math.sin(phi),math.cos(phi),0));outline=FIN_OUTLINE;count=len(outline)
    vertices=[radial*r+tangent*t+Vector((0,0,side*z)) for t in [-.025,.025] for r,z in outline]
    faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    obj=mesh(name,vertices,faces,surface_material)
    bevel=obj.modifiers.new('Small cast fin edge','BEVEL');bevel.width=.007;bevel.segments=2
    return obj


def build():
    m=dict(hull=material('Observatory | worn slate hull',(.12,.17,.24),.65,.56),aft=material('Observatory | worn green chambers',(.10,.25,.16),.65,.56),bronze=material('Observatory | aged copper details',(.30,.15,.08),.74,.61),
        edge=material('Observatory | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Observatory | soot graphite',(.012,.013,.017),.45,.76),gold=material('Observatory | dull gold fittings',(.40,.30,.10),.78,.66))
    parts={}
    for name,profile in PROFILES.items():
        obj=vessel(name,profile,m['hull' if 'saucer' in name else 'aft'],[DENTS[name]])
        for v in obj.data.vertices:v.co.y*=SCALE_Y[name]
        parts[name]=obj
    for name,owner,low,high in BANDS:
        heights=sorted(set([low,high]+[z for z,_ in PROFILES[owner] if low<z<high]))
        rows=[(z,profile_radius(PROFILES[owner],z)+.012,profile_radius(PROFILES[owner],z)-.020) for z in heights]
        obj=annulus(name,(0,0),rows,m['bronze'],(0,(low+high)/2,0))
        for v in obj.data.vertices:v.co.y*=SCALE_Y[owner]
    for side in [-1,1]:
        beam('Observatory axial aerial '+str(side),(0,0,side*1.96),(0,0,side*2.87),.012,m['bronze'])
        cylinder('Observatory aerial collar '+str(side),(0,0,side*2.0),.075,.11,m['bronze'],vertices=32)
        # The number, radial placement and hidden backs of the separated fins are inferred.
        for i in range(4):fin('Observatory pointed fin '+str(side)+' '+str(i),i*math.pi/2,side,m['hull'])
        for i in range(4):
            phi=math.pi/4+i*math.pi/2;n=Vector((math.cos(phi),math.sin(phi),0));a=n*.23+Vector((0,0,side*.64));b=n*.11+Vector((0,0,side*1.92))
            beam('Observatory axial copper rail '+str(side)+' '+str(i),a,b,.018,m['bronze'])
    owner='Observatory saucer pressure hull'
    for i in range(8):
        phi=i*math.tau/8
        patch('Observatory upper service plate '+str(i),owner,.19,.39,phi-.12,phi+.12,m['hull'])
        patch('Observatory lower service inset '+str(i),owner,-.36,-.27,phi-.09,phi+.09,m['dark'])
    body=parts[owner];normal=Vector((0,-1,0));point=Vector((0,-1.265,0))
    # Flattened body-fitted casting: original oval centre motivates a distinct face,
    # but optics and electronic function are not established by the name alone.
    bezel=cast_bezel('Observatory central oval bezel',body,point,normal,.23,m['edge'])
    for v in bezel.data.vertices:v.co.x*=1.55;v.co.z*=.52
    # Recast the transformed rear surface rather than leaving a scaled root floating.
    size=len(bezel.data.vertices)//2
    for v in list(bezel.data.vertices)[size:]:
        origin=Vector((v.co.x,-4,v.co.z));hit,where,_,_=body.ray_cast(origin,Vector((0,1,0)));assert hit
        v.co.y=where.y+.020
    face=cylinder('Observatory dark oval face',(0,-1.296,0),.18,.018,m['dark'],vertices=64,rotation=(math.pi/2,0,0))
    for v in face.data.vertices:v.co.x*=1.55;v.co.y*=.52
    for i in range(3):
        cylinder('Observatory central face marker '+str(i),((i-1)*.115,-1.310,0),.014,.012,m['gold'],vertices=16,rotation=(math.pi/2,0,0))
    for side in [-1,1]:
        phi=-math.pi/2+side*.67;z=0;p=surface(owner,phi,z);n=Vector((p.x,p.y/.49,0)).normalized()
        point=p+n*.055;cast_bezel('Observatory lateral copper boss '+str(side),body,point,n,.095,m['bronze'])
        cylinder('Observatory boss cap '+str(side),point+n*.028,.066,.018,m['gold'],vertices=32,rotation=n.to_track_quat('Z','Y').to_euler())
    # Legible independent low-profile maintenance treatment on the exposed green chambers.
    for side in [-1,1]:
        owner='Observatory axial green chambers';z=side*1.14
        patch('Observatory chamber service plate '+str(side),owner,z-.07,z+.07,-math.pi/2-.30,-math.pi/2+.30,m['aft'])
        for j in range(3):
            height=z-.04+j*.04
            patch('Observatory chamber service slot '+str(side)+' '+str(j),owner,height-.005,height+.005,-math.pi/2-.22,-math.pi/2+.22,m['dark'])
    return m
