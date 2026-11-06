"""First RIM5 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Rigellian Flare green core'
NOSE='Rigellian Flare gold forward fitting'
TUBE='Rigellian Flare forward neck'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-.55,.10),(-.30,.15),(0,.16),(.25,.13),(.50,.10),(.5625,.08)],NOSE:[(-1.0625,.025),(-.95,.045),(-.875,.045)],TUBE:[(-.90,.055),(-.72,.075),(-.50,.10),(-.40,.10)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi,.0,.004),NOSE:(math.pi,-.95,.0015),TUBE:(0,-.65,.0025)}
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
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);PATCHES.append(spec)
    skin_faces=2*(height-1)*(columns-1)
    for face in data.polygons:face.use_smooth=face.index<skin_faces
    # Preserve the finite edge wall as a sharp boundary of each curved skin.
    uses={}
    for face in data.polygons:
        for edge in face.edge_keys:uses.setdefault(tuple(sorted(edge)),[]).append(face.use_smooth)
    for edge in data.edges:edge.use_edge_sharp=len(set(uses[tuple(sorted(edge.vertices))]))>1
    return obj





def prism(name,side,outline,depth,surface_material):
    vertices=[(side*x,y,z) for z in [-depth,depth] for x,y in outline];n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,.004);return obj


def build():
    PATCHES.clear()
    m=dict(hull=material('Rigellian Flare | worn green shell alloy',(.055,.14,.095),.72,.70),blue=material('Rigellian Flare | worn blue centre inserts',(.055,.09,.16),.52,.73),gold=material('Rigellian Flare | worn gold forward fitting',(.30,.23,.075),.76,.70),edge=material('Rigellian Flare | oxidized joint alloy',(.09,.14,.18),.65,.71),mint=material('Rigellian Flare | pale green bands',(.12,.25,.17),.52,.75),dark=material('Rigellian Flare | dark service slots',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['gold' if owner==NOSE else 'hull'],[DENTS[owner]]),Y_AXIS)
    for i,side in enumerate([-1,1]):
        prism('Rigellian Flare rear prong '+str(i),side,[(.07,.20),(.15,.20),(.18,.65),(.17,1.30),(.12,1.30),(.09,.65)],.045,m['hull'])
        prism('Rigellian Flare gold rail '+str(i),side,[(.115,.25),(.135,.25),(.17,.65),(.16,1.20),(.14,1.20),(.15,.65)],.050,m['gold'])
    for i,(y0,y1) in enumerate([(-.83,-.79),(-.68,-.64),(-.61,-.57)]):
        rows=[(y,profile_radius(PROFILES[TUBE],y)+.004,profile_radius(PROFILES[TUBE],y)-.012) for y in [y0,y1]]
        orient(annulus('Rigellian Flare pale band '+str(i),(0,0),rows,m['mint'],(0,y0,0)),Y_AXIS)
    for i,(y0,y1) in enumerate([(-.15,.10),(.30,.525)]):
        surround='Rigellian Flare centre recess surround '+str(i);patch(surround,CORE,y0,y1,-math.pi/2,.25,m['dark'],.002,-.018)
        for j,(a,b) in enumerate([(-.13,-.04),(-.015,.075)] if i==0 else [(.32,.40),(.425,.505)]):patch('Rigellian Flare blue centre insert '+str(i)+' '+str(j),CORE,a,b,-math.pi/2,.18,m['blue'],.009,-.010,surround)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Rigellian Flare service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Rigellian Flare service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Rigellian Flare fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
