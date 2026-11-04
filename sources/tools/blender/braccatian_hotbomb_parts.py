"""First BRM6 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Braccatian HotBomb copper axial body'
NOSE='Braccatian HotBomb gold forward terminal'
TUBE='Braccatian HotBomb brown forward connector'
TAIL='Braccatian HotBomb gold rear terminal'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-.6875,.060),(-.625,.16),(-.46,.16),(-.34,.075),(.28,.075),(.40,.16),(.60,.16),(.6875,.060)],NOSE:[(-1,.045),(-.96,.09),(-.84,.09),(-.80,.055)],TUBE:[(-.86,.055),(-.78,.055),(-.60,.065)],TAIL:[(.58,.060),(.72,.080),(.81,.080),(.875,.035)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi,0,.004),NOSE:(math.pi,-.90,.002),TUBE:(0,-.74,.002),TAIL:(0,.77,.002)}
PANELS=[(CORE,-.18,.15,math.pi/2),(CORE,-.18,.15,-math.pi/2)]
PATCHES=[]
BANDS=[('gold',-.59,-.53),('gold',.47,.53)]
SOCKETS={'AlignmentForward':((0,-1.06,0),(0,-1,0))}

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





def build():
    PATCHES.clear()
    m=dict(gold=material('Braccatian HotBomb | worn gold body alloy',(.30,.23,.075),.76,.70),accent=material('Braccatian HotBomb | worn brown connector alloy',(.13,.075,.035),.68,.73),red=material('Braccatian HotBomb | worn copper body alloy',(.24,.095,.075),.54,.76),dark=material('Braccatian HotBomb | dark red joints',(.09,.012,.009),.54,.77),edge=material('Braccatian HotBomb | oxidized joint alloy',(.15,.12,.06),.70,.72))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['gold' if owner in [NOSE,TAIL] else 'accent' if owner==TUBE else 'red'],[DENTS[owner]]),Y_AXIS)
    for i,(style,y0,y1) in enumerate(BANDS):
        top=.020
        rows=[(y,profile_radius(PROFILES[CORE],y)+top,profile_radius(PROFILES[CORE],y)-.015) for y in [y0,y1]]
        orient(annulus('Braccatian HotBomb body band '+str(i),(0,0),rows,m[style],(0,y0,0)),Y_AXIS)
    for i,(z0,z1) in enumerate([(-.60,-.36),(.30,.57)]):
        for j,phi in enumerate([0,math.pi]):patch('Braccatian HotBomb gold end casting '+str(i)+' '+str(j),CORE,z0,z1,phi,.40,m['gold'],.035,-.012)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Braccatian HotBomb service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['gold'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Braccatian HotBomb service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Braccatian HotBomb fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
