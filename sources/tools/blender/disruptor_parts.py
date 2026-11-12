"""Independent first PH01 equipment, without inferred aiming or internal mechanisms."""
import math
import bpy
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus

CORE='Disruptor tapered body'
SPHERE='Disruptor large spherical front'
DOME='Disruptor rounded upper fitting'
BLUE_CORE='Disruptor blue rear cap'
BLUE_SPHERE='Disruptor blue spherical back'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-1.10,.07),(-.70,.28),(.20,.32),(.50,.31),(.6875,.20)],DOME:[(.25,.12),(.35,.16),(.50,.08),(.53125,.015)],BLUE_CORE:[(.50,.30),(.65,.32),(.80,.20),(.875,.03)]}
for name,a,b in [(SPHERE,-.359375,.359375),(BLUE_SPHERE,-.015625,.359375)]:PROFILES[name]=[(a+(b-a)*i/32,math.sqrt(.36**2-(a+(b-a)*i/32)**2)) for i in range(33)]
PROFILES[BLUE_SPHERE]=[(z,r+.004) for z,r in PROFILES[BLUE_SPHERE]]
LOCATIONS={CORE:Vector((0,0,0)),DOME:Vector((0,.15,0)),BLUE_CORE:Vector((0,0,0)),SPHERE:Vector((-.48,.62,.35)),BLUE_SPHERE:Vector((-.48,.62,.35))}
ROTATIONS={name:(Matrix.Identity(3) if name==DOME else Y_AXIS) for name in PROFILES}
DENTS={CORE:(0,-.50,.006),SPHERE:(0,-.10,.004),DOME:(-math.pi/2,.40,.003),BLUE_CORE:(0,.60,0),BLUE_SPHERE:(0,.10,0)}
PANELS=[(CORE,-.60,-.30,0),(CORE,-.60,-.30,math.pi),(SPHERE,-.22,-.08,-math.pi/2)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.20,0),(0,-1,0))}
PIPE_ENDPOINTS=[]


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





def pipe(name,start,end,surface,offset):
    a=Vector(start);d=Vector(end);b=a+Vector((0,.55,offset));c=d+Vector((.10,.40,offset))
    points=[a*(1-t)**3+3*b*(1-t)**2*t+3*c*(1-t)*t*t+d*t**3 for t in [i/48 for i in range(49)]]
    count=32;vertices=[];faces=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();rotation=tangent.to_track_quat('Z','Y').to_matrix()
        vertices.extend(p+rotation @ Vector((.016*math.cos(j*math.tau/count),.016*math.sin(j*math.tau/count),0)) for j in range(count))
    for i in range(len(points)-1):
        for j in range(count):faces.append((i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j))
    start=len(vertices);vertices.extend([points[0],points[-1]]);end=(len(points)-1)*count
    faces.extend((start,(j+1)%count,j) for j in range(count));faces.extend((start+1,end+j,end+(j+1)%count) for j in range(count))
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    PIPE_ENDPOINTS.append(dict(name=name,start=list(a),end=list(d)));return obj


def build():
    PATCHES.clear();PIPE_ENDPOINTS.clear()
    m=dict(hull=material('Disruptor | worn olive alloy',(.27,.27,.21),.72,.70),red=material('Disruptor | worn red end details',(.31,.10,.085),.68,.72),copper=material('Disruptor | worn copper pipes',(.34,.16,.075),.76,.68),blue=material('Disruptor | dull blue rear surfaces',(.09,.14,.24),.54,.72),edge=material('Disruptor | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Disruptor | dark recessed face',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['blue' if owner in [BLUE_CORE,BLUE_SPHERE] else 'hull'],[DENTS[owner]]),ROTATIONS[owner],LOCATIONS[owner])
    beam('Disruptor spherical support',(-.15,.25,.12),(-.48,.62,.35),.060,m['hull'])
    for side in [-1,1]:box('Disruptor angular side shield '+str(side),(side*.28,-.05,-.23),(.22,.65,.18),m['hull'],.025)
    cylinder('Disruptor red side boss',(.34,-.05,0),.075,.12,m['red'],48,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    orient(annulus('Disruptor front annular rim',(0,0),[(-1.15625,.090,.045),(-1.10,.095,.045),(-1.046875,.105,.045)],m['hull'],(0,-1.1,0)),Y_AXIS)
    cylinder('Disruptor aperture backing',(0,-1.105,0),.060,.025,m['dark'],64,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    for i,x in enumerate([-.05,.05]):pipe('Disruptor rear copper pipe '+str(i),(x,.70,.10),(-.48+(i-.5)*.14,.90,.35),m['copper'],.08 if i==0 else -.08)
    for i,phi in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):patch('Disruptor front red mark '+str(i),CORE,-.94,-.86,phi,.14,m['red'])
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Disruptor service cover '+str(i);patch(panel,owner,z0,z1,phi,.23,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Disruptor service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.15,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.17,.17]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Disruptor fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
