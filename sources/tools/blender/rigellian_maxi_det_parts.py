"""First RIM4 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Rigellian Maxi-det green core'
NOSE='Rigellian Maxi-det gold forward fitting'
TUBE='Rigellian Maxi-det forward neck'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-.65,.16),(-.40,.21),(-.15,.16),(.10,.14),(.375,.12)],NOSE:[(-.9375,.035),(-.85,.05),(-.70,.055),(-.60,.07)],TUBE:[(-.75,.08),(-.65,.11),(-.50,.14)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi,.0,.004),NOSE:(math.pi,-.85,.002),TUBE:(0,-.65,.002)}
PANELS=[(CORE,-.18,.10,0),(CORE,-.18,.10,math.pi)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.04,0),(0,-1,0))}

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





def prong(name,side,surface_material):
    outline=[(.08,.08),(.17,.08),(.19,.40),(.175,1.15),(.115,1.15),(.09,.40)]
    vertices=[(side*x,y,z) for z in [-.055,.055] for x,y in outline];n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,.008);return obj


def build():
    PATCHES.clear()
    m=dict(hull=material('Rigellian Maxi-det | worn green shell alloy',(.055,.14,.095),.72,.70),blue=material('Rigellian Maxi-det | worn blue centre inserts',(.055,.09,.16),.52,.73),gold=material('Rigellian Maxi-det | worn gold forward fitting',(.30,.23,.075),.76,.70),edge=material('Rigellian Maxi-det | oxidized joint alloy',(.09,.14,.18),.65,.71),purple=material('Rigellian Maxi-det | dull purple side fittings',(.18,.065,.24),.46,.75),red=material('Rigellian Maxi-det | dull red side fittings',(.25,.045,.04),.48,.73),mint=material('Rigellian Maxi-det | pale green bands',(.12,.25,.17),.52,.75),dark=material('Rigellian Maxi-det | dark service slots',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['gold' if owner==NOSE else 'hull'],[DENTS[owner]]),Y_AXIS)
    for i,side in enumerate([-1,1]):prong('Rigellian Maxi-det rear prong '+str(i),side,m['hull'])
    for i,(y0,y1) in enumerate([(-.53,-.49),(-.31,-.27)]):
        rows=[(y,profile_radius(PROFILES[CORE],y)+.005,profile_radius(PROFILES[CORE],y)-.012) for y in [y0,y1]]
        orient(annulus('Rigellian Maxi-det pale band '+str(i),(0,0),rows,m['mint'],(0,y0,0)),Y_AXIS)
    box('Rigellian Maxi-det fork base gold fitting',(0,.30,.10),(.16,.07,.08),m['gold'],.004)
    patch('Rigellian Maxi-det centre recess surround',CORE,-.04,.20,-math.pi/2,.30,m['dark'],.002,-.018)
    for i,y0 in enumerate([-.02,.045,.11]):patch('Rigellian Maxi-det blue centre insert '+str(i),CORE,y0,y0+.05,-math.pi/2,.20,m['blue'],.009,-.010,'Rigellian Maxi-det centre recess surround')
    for i,side in enumerate([-1,1]):
        rotation=Vector((side,0,0)).to_track_quat('Z','Y').to_euler()
        cylinder('Rigellian Maxi-det side fitting base '+str(i),(side*.205,-.45,0),.035,.080,m['edge'],32,rotation=rotation)
        cylinder('Rigellian Maxi-det red side fitting '+str(i),(side*.25,-.45,0),.028,.040,m['red'],32,rotation=rotation)
        cylinder('Rigellian Maxi-det purple side fitting '+str(i),(side*.28,-.45,0),.024,.035,m['purple'],32,rotation=rotation)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Rigellian Maxi-det service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Rigellian Maxi-det service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Rigellian Maxi-det fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
