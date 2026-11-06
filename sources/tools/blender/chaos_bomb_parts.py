"""First independent PH03 interpretation: opposed six/three banks with true tiers."""
import math
import bpy
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius

Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
TUBE_POSITIONS=[(x,z) for z in [-.28,0,.28] for x in [-.16,.16]]+[(-.15,-.15),(.15,-.15),(0,.10)]
PROFILES={};LOCATIONS={};ROTATIONS={};DENTS={}
for i,(x,z) in enumerate(TUBE_POSITIONS):
    owner='Chaos cylinder '+str(i);cap='Chaos red end '+str(i)
    PROFILES[owner]=[(-1.0,.10),(-.90,.105),(.0625,.105)] if i<6 else [(-.0625,.12),(.75,.12)]
    PROFILES[cap]=[(-1.15,.010),(-1.10,.070),(-1.02,.105),(-.9375,.10)] if i<6 else [(.6875,.10),(.75,.12),(.85,.08),(.90625,.01)]
    for name in [owner,cap]:LOCATIONS[name]=Vector((x,0,z));ROTATIONS[name]=Y_AXIS;DENTS[name]=(0,-.40 if i<6 else .40,.0025+i*.0001 if name==owner else 0)
PANELS=[('Chaos cylinder 4',-.65,-.35,-math.pi/2),('Chaos cylinder 5',-.65,-.35,-math.pi/2),('Chaos cylinder 8',.25,.55,-math.pi/2)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.20,0),(0,-1,0))}


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
    m=dict(hull=material('Chaos | worn grey cylinder alloy',(.24,.27,.25),.72,.70),red=material('Chaos | worn red end caps',(.36,.095,.085),.65,.72),copper=material('Chaos | worn warm support rails',(.30,.18,.09),.74,.72),edge=material('Chaos | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Chaos | dark service recesses',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['red' if 'red end' in owner else 'hull'],[DENTS[owner]]),ROTATIONS[owner],LOCATIONS[owner])
    box('Chaos central support',(0,0,0),(.64,.18,.86),m['hull'],.015)
    for i,(x,z) in enumerate(TUBE_POSITIONS):cylinder('Chaos cylinder collar '+str(i),(x,-.90 if i<6 else .70,z),.113 if i<6 else .128,.04,m['hull'],48,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    for side in [-1,1]:box('Chaos bracket upright '+str(side),(side*.24,.08,.47),(.10,.16,.35),m['copper'],.006)
    box('Chaos bracket top',(0,.08,.65),(.65,.50,.12),m['hull'],.008)
    for side in [-1,1]:beam('Chaos lower rail '+str(side),(side*.15,.05,-.26),(side*.15,.78,-.26),.020,m['copper'])
    beam('Chaos lower cross rail',(-.24,.78,-.26),(.24,.78,-.26),.020,m['copper'])
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Chaos service cover '+str(i);patch(panel,owner,z0,z1,phi,.23,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Chaos service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.15,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.17,.17]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Chaos fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
