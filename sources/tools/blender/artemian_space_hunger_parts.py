"""First ARM12 interpretation; tiny flight sprites do not resolve hidden sections."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Artemian Space Hunger green forward shell'
TUBE='Artemian Space Hunger green rear shell'
NOSE='Artemian Space Hunger red forward cap'
TAIL='Artemian Space Hunger red rear cap'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-.34,.34),(-.16,.42),(-.015,.435),(.0625,.42)],TUBE:[(-.0625,.42),(.015,.435),(.16,.42),(.34375,.34)],NOSE:[(-.50,.030),(-.46,.20),(-.34,.34),(-.296875,.36)],TAIL:[(.296875,.36),(.34375,.34),(.46,.20),(.50,.030)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi/2,-.20,.005),TUBE:(3*math.pi/2,.20,.005),NOSE:(math.pi/2,-.40,.003),TAIL:(3*math.pi/2,.40,.003)}
PANELS=[(CORE,-.28,-.12,math.pi/4),(TUBE,.12,.28,5*math.pi/4)]
PATCHES=[]
STRAPS=[(owner,y0,y1,phi) for owner,y0,y1 in [(CORE,-.10,0),(TUBE,0,.10)] for phi in [math.pi/2,3*math.pi/2]]
SOCKETS={'AlignmentForward':((0,-.65,0),(0,-1,0))}


def section_factor(phi):
    # Sixteen shell facets are authored; a five-pixel sprite does not recover sections.
    return math.cos(math.pi/16)/math.cos(phi%(math.pi/8)-math.pi/16)


def primary(owner,profile,surface_material):
    obj=vessel(owner,profile,surface_material,[DENTS[owner]])
    for vertex in obj.data.vertices:
        p=vertex.co;phi=math.atan2(p.y,p.x);r=math.hypot(p.x,p.y);height=max(profile[0][0],min(profile[-1][0],p.z));assert abs(height-p.z)<1e-6
        new_radius=r+profile_radius(profile,height)*(section_factor(phi)-1);p.x*=new_radius/r;p.y*=new_radius/r
    for face in obj.data.polygons:face.use_smooth=False
    obj.data.update();return orient(obj,Y_AXIS)


def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z)*section_factor(phi);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
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
    m=dict(gold=material('Artemian Space Hunger | worn green body alloy',(.085,.22,.16),.76,.70),accent=material('Artemian Space Hunger | worn silver-blue belt alloy',(.28,.40,.46),.68,.73),red=material('Artemian Space Hunger | worn orange polar alloy',(.62,.29,.045),.54,.76),dark=material('Artemian Space Hunger | dark green joints',(.018,.035,.027),.54,.77),edge=material('Artemian Space Hunger | oxidized joint alloy',(.16,.20,.18),.70,.72))
    for owner,profile in PROFILES.items():primary(owner,profile,m['red' if owner in [NOSE,TAIL] else 'gold'])
    orient(annulus('Artemian Space Hunger silver-blue transverse belt',(0,0),[(-.09,.450,.39),(.09,.450,.39)],m['accent'],(0,0,0)),Y_AXIS)
    for i,(owner,y0,y1,phi) in enumerate(STRAPS):patch('Artemian Space Hunger green longitudinal strap '+str(i),owner,y0,y1,phi,.20,m['gold'],.025,-.018)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Artemian Space Hunger service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['gold'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Artemian Space Hunger service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Artemian Space Hunger fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
