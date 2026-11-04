"""First MKM8 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Mikotaj Kal-Na-Xanth green axial spine'
TUBE='Mikotaj Kal-Na-Xanth green forward section'
REAR='Mikotaj Kal-Na-Xanth green rear section'
NOSE='Mikotaj Kal-Na-Xanth grey left frame'
TAIL='Mikotaj Kal-Na-Xanth grey right frame'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-1,.004),(-.82,.007),(-.20,.012),(.20,.012),(.82,.007),(1,.004)],TUBE:[(-.8125,.010),(-.70,.028),(-.20,.028),(-.125,.010)],REAR:[(.125,.010),(.20,.028),(.70,.028),(.8125,.010)],NOSE:[(-.8125,.010),(-.74,.016),(.74,.016),(.8125,.010)],TAIL:[(-.8125,.010),(-.74,.016),(.74,.016),(.8125,.010)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES};LOCATIONS[NOSE]=Vector((-.082,0,0));LOCATIONS[TAIL]=Vector((.082,0,0))
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(0,0,.0006),TUBE:(0,-.40,.0015),REAR:(0,.40,.0015),NOSE:(math.pi,0,.0008),TAIL:(0,0,.0008)}
PANELS=[(TUBE,-.52,-.30,3*math.pi/2)]
PATCHES=[]
BRACES=[(-.66,TUBE),(0,CORE),(.66,REAR)]
CASTINGS=[(owner,z0,z1,phi,'red',.006,-.010,.25) for owner,z0,z1 in [(TUBE,-.63,-.23),(REAR,.23,.63)] for phi in [0,math.pi]]+[(TUBE,-.50,-.25,math.pi/2,'accent',.003,-.010,.18),(REAR,.25,.50,math.pi/2,'accent',.003,-.010,.18)]+[(TUBE,-.64,-.58,math.pi/2,'red',.005,-.012,.80),(REAR,.58,.64,math.pi/2,'red',.005,-.012,.80)]
SOCKETS={'AlignmentForward':((0,-1.1,0),(0,-1,0))}


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
    m=dict(gold=material('Mikotaj Kal-Na-Xanth | worn green body alloy',(.055,.15,.09),.76,.70),accent=material('Mikotaj Kal-Na-Xanth | worn pale green band alloy',(.07,.19,.12),.68,.73),red=material('Mikotaj Kal-Na-Xanth | worn grey side alloy',(.12,.155,.18),.54,.76),dark=material('Mikotaj Kal-Na-Xanth | dark green joints',(.018,.035,.027),.54,.77),edge=material('Mikotaj Kal-Na-Xanth | oxidized joint alloy',(.16,.20,.18),.70,.72))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['red' if owner in [NOSE,TAIL] else 'gold'],[DENTS[owner]]),Y_AXIS,LOCATIONS[owner])
    for i,(y,owner) in enumerate(BRACES):
        for sign in [-1,1]:box('Mikotaj Kal-Na-Xanth cross brace '+str(i)+' '+str(sign),(sign*.046,y,0),(.076,.055,.040),m['red'],.002)
    for i,(owner,z0,z1,phi,style,top,back,width) in enumerate(CASTINGS):patch('Mikotaj Kal-Na-Xanth fitted casting '+str(i),owner,z0,z1,phi,width,m[style],top,back)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Mikotaj Kal-Na-Xanth service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['gold'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Mikotaj Kal-Na-Xanth service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Mikotaj Kal-Na-Xanth fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
