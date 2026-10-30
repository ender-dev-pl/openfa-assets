"""First MKM6 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Mikotaj Convulsion green axial spine'
TUBE='Mikotaj Convulsion green compact centre'
NOSE='Mikotaj Convulsion green extended section'
REAR='Mikotaj Convulsion grey rear stem'
TAIL='Mikotaj Convulsion orange rear coupling'
TIP='Mikotaj Convulsion grey left edging'
SIDER='Mikotaj Convulsion grey right edging'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-1,.005),(-.85,.010),(-.20,.014),(.20,.014),(.90,.008),(1,.004)],TUBE:[(-.02,.025),(.02,.070),(.12,.075),(.21,.060),(.25,.020)],NOSE:[(-.875,.012),(-.78,.045),(-.30,.045),(-.21875,.012)],REAR:[(.28,.012),(.32,.022),(.58,.022),(.625,.010)],TAIL:[(.35,.026),(.48,.026)],TIP:[(-.78,.006),(-.70,.010),(-.30,.010),(-.21875,.006)],SIDER:[(-.78,.006),(-.70,.010),(-.30,.010),(-.21875,.006)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES};LOCATIONS[TIP]=Vector((-.052,0,0));LOCATIONS[SIDER]=Vector((.052,0,0))
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi/2,.80,.0005),TUBE:(math.pi/2,.12,.002),NOSE:(math.pi/2,-.55,.002),REAR:(math.pi/2,.53,.0008),TAIL:(math.pi/2,.41,.0008),TIP:(math.pi,-.50,.0006),SIDER:(0,-.50,.0006)}
PANELS=[(NOSE,-.58,-.42,math.pi/4)]
PATCHES=[]
BANDS=[(TUBE,'accent',.04,.065),(TUBE,'dark',.11,.13),(TUBE,'accent',.18,.205),(NOSE,'dark',-.52,-.49)]
CASTINGS=[(TUBE,.025,.215,phi,.004) for phi in [math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4]]+[(NOSE,-.70,-.32,phi,.003) for phi in [math.pi/2,3*math.pi/2]]
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
    m=dict(orange=material('Mikotaj Convulsion | worn ochre coupling alloy',(.40,.19,.035),.61,.74),gold=material('Mikotaj Convulsion | worn green body alloy',(.055,.15,.09),.76,.70),accent=material('Mikotaj Convulsion | worn pale green band alloy',(.07,.19,.12),.68,.73),red=material('Mikotaj Convulsion | worn grey side alloy',(.12,.155,.18),.54,.76),dark=material('Mikotaj Convulsion | dark green joints',(.018,.035,.027),.54,.77),edge=material('Mikotaj Convulsion | oxidized joint alloy',(.16,.20,.18),.70,.72))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['red' if owner in [REAR,TIP,SIDER] else 'orange' if owner==TAIL else 'gold'],[DENTS[owner]]),Y_AXIS,LOCATIONS[owner])
    for i,(owner,style,y0,y1) in enumerate(BANDS):
        top=.003 if style=='accent' else .004
        rows=[(y,profile_radius(PROFILES[owner],y)+top,profile_radius(PROFILES[owner],y)-.012) for y in [y0,y1]]
        orient(annulus('Mikotaj Convulsion body band '+str(i),(0,0),rows,m[style],(0,y0,0)),Y_AXIS)
    for i,(owner,z0,z1,phi,top) in enumerate(CASTINGS):patch('Mikotaj Convulsion pale longitudinal casting '+str(i),owner,z0,z1,phi,.14,m['accent'],top,-.012)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Mikotaj Convulsion service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['gold'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Mikotaj Convulsion service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Mikotaj Convulsion fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
