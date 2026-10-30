"""First MKM9 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Mikotaj Bruj-Garor green central body'
TUBE='Mikotaj Bruj-Garor grey forward section'
REAR='Mikotaj Bruj-Garor grey rear section'
NOSE='Mikotaj Bruj-Garor grey left outer rail'
TAIL='Mikotaj Bruj-Garor grey right outer rail'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-1,.006),(-.82,.012),(-.45,.025),(-.32,.050),(.32,.050),(.45,.025),(.82,.012),(1,.006)],TUBE:[(-.875,.012),(-.76,.055),(-.52,.055),(-.4375,.025)],REAR:[(.4375,.025),(.52,.055),(.76,.055),(.875,.012)],NOSE:[(-.75,.008),(-.68,.014),(.68,.014),(.75,.008)],TAIL:[(-.75,.008),(-.68,.014),(.68,.014),(.75,.008)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES};LOCATIONS[NOSE]=Vector((-.10,0,0));LOCATIONS[TAIL]=Vector((.10,0,0))
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(0,.20,.002),TUBE:(0,-.60,.002),REAR:(0,.60,.002),NOSE:(math.pi,0,.0008),TAIL:(0,0,.0008)}
PANELS=[(TUBE,-.68,-.56,math.pi/4)]
PATCHES=[]
BRIDGES=[(-1,-.55),(-1,.55),(1,-.55),(1,.55)]
CASTINGS=[(CORE,-.30,.30,phi,'accent',.003,-.010,.18) for phi in [math.pi/2,3*math.pi/2]]+[(owner,-.42,.42,phi,'orange',.004,-.007,.45) for owner,phi in [(NOSE,math.pi),(TAIL,0)]]+[(owner,z0,z1,phi,'gold',.003,-.010,.22) for owner,z0,z1 in [(TUBE,-.70,-.55),(REAR,.55,.70)] for phi in [math.pi/2,3*math.pi/2]]
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
    m=dict(orange=material('Mikotaj Bruj-Garor | worn copper seam alloy',(.25,.115,.095),.61,.74),gold=material('Mikotaj Bruj-Garor | worn green body alloy',(.055,.15,.09),.76,.70),accent=material('Mikotaj Bruj-Garor | worn pale green band alloy',(.07,.19,.12),.68,.73),red=material('Mikotaj Bruj-Garor | worn grey side alloy',(.12,.155,.18),.54,.76),dark=material('Mikotaj Bruj-Garor | dark green joints',(.018,.035,.027),.54,.77),edge=material('Mikotaj Bruj-Garor | oxidized joint alloy',(.16,.20,.18),.70,.72))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['gold' if owner==CORE else 'red'],[DENTS[owner]]),Y_AXIS,LOCATIONS[owner])
    for i,(sign,y) in enumerate(BRIDGES):beam('Mikotaj Bruj-Garor rail bridge '+str(i),(0,y,0),(sign*.10,y,0),.012,m['red'])
    orient(annulus('Mikotaj Bruj-Garor dark central band',(0,0),[(-.025,.052,.038),(.025,.052,.038)],m['dark'],(0,0,0)),Y_AXIS)
    for i,(owner,z0,z1,phi,style,top,back,width) in enumerate(CASTINGS):patch('Mikotaj Bruj-Garor fitted casting '+str(i),owner,z0,z1,phi,width,m[style],top,back)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Mikotaj Bruj-Garor service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['gold'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Mikotaj Bruj-Garor service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Mikotaj Bruj-Garor fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
