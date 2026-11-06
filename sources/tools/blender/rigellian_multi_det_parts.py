"""First RIM2 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Rigellian Multi-det green core'
NOSE='Rigellian Multi-det gold forward fitting'
TUBE='Rigellian Multi-det forward neck'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-.45,.10),(-.25,.18),(0,.20),(.20,.16),(.3125,.12)],NOSE:[(-1.0625,.027),(-.95,.05),(-.75,.05),(-.70,.065),(-.50,.065)],TUBE:[(-.70,.065),(-.28,.10)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi,.0,.004),NOSE:(math.pi,-.85,.002),TUBE:(0,-.60,.002)}
PANELS=[(CORE,-.18,.10,0),(CORE,-.18,.10,math.pi)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.16,0),(0,-1,0))}

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
    columns=65 if 'dome sector' in name else 17;steps=max(8,math.ceil((z1-z0)/.022));heights=[z0+(z1-z0)*i/steps for i in range(steps+1)]
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
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);PATCHES.append(spec)
    skin_faces=2*(height-1)*(columns-1)
    for face in data.polygons:face.use_smooth=face.index<skin_faces
    # Preserve the finite edge wall as a sharp boundary of each curved skin.
    uses={}
    for face in data.polygons:
        for edge in face.edge_keys:uses.setdefault(tuple(sorted(edge)),[]).append(face.use_smooth)
    for edge in data.edges:edge.use_edge_sharp=len(set(uses[tuple(sorted(edge.vertices))]))>1
    return obj





def prong(name,side,surface_material):
    outline=[(.09,-.05),(.20,-.05),(.23,.30),(.20,.85),(.18,1.35),(.12,1.35),(.105,.85),(.09,.30)]
    vertices=[(side*x,y,z) for z in [-.065,.065] for x,y in outline];n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,.008);return obj


def build():
    PATCHES.clear()
    m=dict(hull=material('Rigellian Multi-det | worn green shell alloy',(.055,.14,.095),.72,.70),red=material('Rigellian Multi-det | worn red forward band',(.31,.085,.07),.52,.73),gold=material('Rigellian Multi-det | worn gold forward fitting',(.30,.23,.075),.76,.70),edge=material('Rigellian Multi-det | oxidized joint alloy',(.09,.14,.18),.65,.71),purple=material('Rigellian Multi-det | dull purple forward band',(.18,.065,.24),.46,.75),dark=material('Rigellian Multi-det | dark service slots',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['gold' if owner==NOSE else 'hull'],[DENTS[owner]]),Y_AXIS)
    for i,side in enumerate([-1,1]):prong('Rigellian Multi-det rear prong '+str(i),side,m['hull'])
    orient(annulus('Rigellian Multi-det red forward band',(0,0),[(-.82,.057,.040),(-.76,.058,.040)],m['red'],(0,-.75,0)),Y_AXIS)
    orient(annulus('Rigellian Multi-det purple forward band',(0,0),[(-.89,.057,.040),(-.828125,.057,.040)],m['purple'],(0,-.85,0)),Y_AXIS)
    orient(annulus('Rigellian Multi-det grey forward collar',(0,0),[(-.765,.060,.040),(-.703125,.070,.045)],m['edge'],(0,-.74,0)),Y_AXIS)
    patch('Rigellian Multi-det gold neck insert',TUBE,-.65,-.31,-math.pi/2,.75,m['gold'],.006,-.014)
    box('Rigellian Multi-det fork base gold fitting',(0,.28,.11),(.16,.06,.08),m['gold'],.004)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Rigellian Multi-det service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Rigellian Multi-det service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Rigellian Multi-det fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
