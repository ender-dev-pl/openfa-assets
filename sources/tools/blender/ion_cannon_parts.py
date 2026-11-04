"""Independent first PH00 equipment; no aiming/recoil mechanism is inferred."""
import math
import bpy
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus

CORE='Ion axial housing'
NOSE='Ion red front'
POD='Ion side flare'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
X_AXIS=Matrix(((0,0,1),(0,1,0),(-1,0,0)))
PROFILES={CORE:[(-1.10,.12),(-.90,.28),(-.50,.31),(.50,.31),(.8125,.30)],NOSE:[(-1.625,.015),(-1.50,.09),(-1.25,.12),(-1.1875,.11)],POD:[(.65,.12),(.80,.14),(.95,.25),(1.0,.25)]}
LOCATIONS={CORE:Vector((0,0,0)),NOSE:Vector((0,0,0)),POD:Vector((0,.15,0))}
ROTATIONS={CORE:Y_AXIS,NOSE:Y_AXIS,POD:X_AXIS}
DENTS={CORE:(0,-.50,.006),NOSE:(0,-1.40,.004),POD:(math.pi/2,.88,.004)}
PANELS=[(CORE,-.65,-.35,0),(CORE,-.65,-.35,math.pi),(POD,.78,.88,-math.pi/2)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.70,0),(0,-1,0))}


def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return LOCATIONS[owner]+ROTATIONS[owner] @ Vector((r*math.cos(phi),r*math.sin(phi),z))


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=ROTATIONS[owner] @ Vector((math.cos(phi),math.sin(phi),0));inv=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ normal).normalized()


def orient(obj,rotation,origin=(0,0,0)):
    for v in obj.data.vertices:v.co=Vector(origin)+rotation @ v.co
    obj.data.update();return obj


def patch(name,owner,z0,z1,phi,width,surface_material,top=.008,back=-.018,support=None):
    spec=dict(name=name,owner=owner,z0=z0,z1=z1,phi=phi,width=width,top=top,back=back,support=support or owner)
    columns=17;steps=max(8,math.ceil((z1-z0)/.022));heights=[z0+(z1-z0)*i/steps for i in range(steps+1)]
    for z,_ in PROFILES[owner]:
        if z0<z<z1:heights=[h for h in heights if abs(h-z)>1e-8]+[z]
    heights.sort();height=len(heights);size=columns*height;vertices=[]
    for offset in [top,back]:vertices.extend(surface(owner,phi+width*(-1+2*i/(columns-1)),z,offset) for z in heights for i in range(columns))
    faces=[]
    for row in range(height-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,height)]+list(reversed(range((height-1)*columns,(height-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);PATCHES.append(spec);return obj




def build():
    PATCHES.clear()
    m=dict(hull=material('Ion | worn pale alloy housing',(.29,.30,.31),.72,.70),red=material('Ion | worn red copper ends',(.32,.10,.085),.72,.72),edge=material('Ion | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Ion | dark recessed faces',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['red' if owner==NOSE else 'hull'],[DENTS[owner]]),ROTATIONS[owner],LOCATIONS[owner])
    cylinder('Ion front neck',(0,-1.09,0),.13,.38,m['hull'],64,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    cylinder('Ion transverse stem',(.55,.15,0),.11,.60,m['hull'],64,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    cylinder('Ion side dark backing',(1.01,.15,0),.19,.030,m['dark'],64,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    orient(annulus('Ion red side rim',(0,0),[(.96,.265,.18),(1.0,.265,.18),(1.0625,.25,.18)],m['red'],(0,1.0,0)),X_AXIS,(0,.15,0))
    orient(annulus('Ion rear collar',(0,0),[(.62,.36,.28),(.70,.38,.28),(.78125,.36,.28)],m['hull'],(0,.7,0)),Y_AXIS)
    for i,phi in enumerate([0,math.tau/3,2*math.tau/3]):
        x=.17*math.cos(phi);z=.17*math.sin(phi)
        cylinder('Ion rear prong '+str(i),(x,.98,z),.035,.45,m['hull'],32,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
        cylinder('Ion rear red tip '+str(i),(x,1.20,z),.037,.055,m['red'],32,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    for i,y in enumerate([-.02,.38]):box('Ion bracket upright '+str(i),(0,y,.43),(.13,.09,.35),m['hull'],.005)
    box('Ion bracket top',(0,.18,.62),(.13,.50,.09),m['hull'],.005)
    for i,x in enumerate([-.035,.035]):
        # Dark marks are shallow inlays, not an unproven through-bore.
        patch('Ion front dark mark '+str(i),NOSE,-1.46,-1.42,-math.pi/2+(-.35 if i==0 else .35),.08,m['dark'],.006,-.012)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Ion service cover '+str(i);patch(panel,owner,z0,z1,phi,.23,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Ion service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.15,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.17,.17]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Ion fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
