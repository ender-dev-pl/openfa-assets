"""First BRM1 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Braccatian Mega Blast axial waist'
NOSE='Braccatian Mega Blast forward gold end'
TUBE='Braccatian Mega Blast copper neck'
COLLAR_A='Braccatian Mega Blast forward expansion'
COLLAR_B='Braccatian Mega Blast rear expansion'
TAIL='Braccatian Mega Blast rear gold end'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-.50,.070),(-.25,.070),(.05,.065),(.30,.070),(.50,.070),(.8125,.045)],NOSE:[(-1.125,.035),(-1.0,.070),(-.925,.070),(-.84375,.045)],TUBE:[(-.90,.05),(-.75,.065),(-.4375,.060)],COLLAR_A:[(-.50,.12),(-.4375,.18),(-.3125,.18),(-.1875,.11)],COLLAR_B:[(.15,.11),(.25,.17),(.4375,.17),(.5625,.10)],TAIL:[(.70,.035),(.78,.080),(.875,.080),(.9375,.035)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi,0,.0015),NOSE:(math.pi,-1.0,.0015),TUBE:(0,-.65,.0025),COLLAR_A:(math.pi,-.36,.004),COLLAR_B:(math.pi,.34,.004),TAIL:(0,.82,.002)}
PANELS=[(COLLAR_A,-.42,-.33,0),(COLLAR_A,-.42,-.33,math.pi),(COLLAR_B,.27,.40,0),(COLLAR_B,.27,.40,math.pi)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.22,0),(0,-1,0))}

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
    m=dict(gold=material('Braccatian Mega Blast | worn gold body alloy',(.30,.23,.075),.76,.70),neck=material('Braccatian Mega Blast | worn copper neck alloy',(.22,.09,.065),.68,.73),dark=material('Braccatian Mega Blast | worn dark waist alloy',(.045,.030,.018),.54,.76),edge=material('Braccatian Mega Blast | oxidized joint alloy',(.15,.12,.06),.70,.72))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['neck' if owner==TUBE else 'gold'],[DENTS[owner]]),Y_AXIS)
    orient(annulus('Braccatian Mega Blast neck collar',(0,0),[(-.56,.085,.045),(-.515625,.090,.045)],m['gold'],(0,-.54,0)),Y_AXIS)
    for i,(y0,y1) in enumerate([(-.07,-.03),(.07,.11)]):
        rows=[(y,profile_radius(PROFILES[CORE],y)+.002,profile_radius(PROFILES[CORE],y)-.010) for y in [y0,y1]]
        orient(annulus('Braccatian Mega Blast dark waist band '+str(i),(0,0),rows,m['dark'],(0,y0,0)),Y_AXIS)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Braccatian Mega Blast service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['gold'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Braccatian Mega Blast service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Braccatian Mega Blast fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
