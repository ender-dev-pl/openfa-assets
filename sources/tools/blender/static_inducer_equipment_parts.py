"""Independent first PH08 assembly; no original geometry or pixels imported."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Static Inducer central shell'
NOSE='Static Inducer studded dome'
TUBE='Static Inducer blue terminal 0'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={NOSE:[(-.95,.025),(-.92,.16),(-.85,.28),(-.75,.37),(-.60,.43),(-.45,.46),(-.375,.46)],CORE:[(-.50,.41),(-.35,.43),(.20,.43),(.375,.40)]}
for i in range(3):PROFILES['Static Inducer blue terminal '+str(i)]=[(.32,.08),(.40,.17),(.55,.205),(.70,.20),(.82,.15),(.875,.105)]
LOCATIONS={NOSE:Vector((0,0,0)),CORE:Vector((0,0,0))}
for i in range(3):
 a=math.pi/2+i*math.tau/3;LOCATIONS['Static Inducer blue terminal '+str(i)]=Vector((.25*math.cos(a),0,.25*math.sin(a)))
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={NOSE:(math.pi,-.65,.006),CORE:(math.pi,0,.005)}
for i in range(3):DENTS['Static Inducer blue terminal '+str(i)]=(math.pi,.60,.003)
PANELS=[(CORE,-.25,.08,math.pi),(CORE,-.25,.08,0)]
PATCHES=[]
STUDS=[]
SOCKETS={'AlignmentForward':((0,-1.10,0),(0,-1,0))}

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
    PATCHES.clear();STUDS.clear()
    m=dict(hull=material('Static Inducer | worn pale shell alloy',(.28,.29,.26),.72,.70),red=material('Static Inducer | worn red stud tips',(.36,.095,.085),.66,.72),blue=material('Static Inducer | worn blue terminal alloy',(.045,.045,.12),.65,.70),edge=material('Static Inducer | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Static Inducer | dark terminal lining',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['blue' if 'blue terminal' in owner else 'hull'],[DENTS[owner]]),Y_AXIS,LOCATIONS[owner])
    for i,y in enumerate([-.43,.29]):
        obj=annulus('Static Inducer collar '+str(i),(0,0),[(y-.065,.50,.38),(y-.045,.52,.38),(y+.045,.52,.38),(y+.0625,.50,.38)],m['hull'],(0,y,.003))
        orient(obj,Y_AXIS)
    bpy.context.view_layer.update()
    # Studs follow the actual curved dome normals, not an enclosing sphere.
    for i,(phi,y) in enumerate([(j*math.tau/6,-.62) for j in range(6)]+[(j*math.tau/6+math.pi/6,-.81) for j in range(6)]):
        p,n=hull_frame(NOSE,phi,y);STUDS.append(dict(position=list(p),normal=list(n)))
        cylinder('Static Inducer stud base '+str(i),p+n*.012,.032,.045,m['edge'],24,rotation=n.to_track_quat('Z','Y').to_euler())
        cylinder('Static Inducer stud tip '+str(i),p+n*.039,.022,.027,m['red' if i%2==0 else 'hull'],24,rotation=n.to_track_quat('Z','Y').to_euler())
    cylinder('Static Inducer axial red terminal',(0,-.964,0),.04,.065,m['red'],32,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    for i in range(3):
        loc=LOCATIONS['Static Inducer blue terminal '+str(i)]
        # The terminal is a blind recess, with finite inner wall and a dark back.
        obj=annulus('Static Inducer recessed rim '+str(i),(0,0),[(.82,.14,.055),(.90,.12,.055),(.9375,.095,.055)],m['blue'],(0,.88,.001))
        orient(obj,Y_AXIS,loc)
        cylinder('Static Inducer recess floor '+str(i),loc+Vector((0,.882,0)),.060,.015,m['dark'],48,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Static Inducer service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Static Inducer service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Static Inducer fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
