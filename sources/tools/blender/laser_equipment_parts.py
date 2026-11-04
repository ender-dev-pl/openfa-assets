"""Independent first PH05 interpretation with a genuinely open side equipment bay."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius

NOSE='Laser tapered front shell'
CORE='Laser open rear shell'
TUBE='Laser red dorsal tube'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={NOSE:[(-1.35,.02),(-1.20,.08),(-.75,.24),(-.30,.28),(-.1875,.28)],CORE:[(-.30,.28),(.80,.28)],TUBE:[(-.50,.03),(-.40,.055),(.80,.055),(.875,.025)]}
LOCATIONS={NOSE:Vector((0,0,0)),CORE:Vector((0,0,0)),TUBE:Vector((0,0,.345))}
ROTATIONS={name:Y_AXIS for name in PROFILES}
DENTS={NOSE:(math.pi,-.65,.005),CORE:(math.pi,.25,.006),TUBE:(0,.30,.002)}
PANELS=[(NOSE,-.75,-.45,math.pi),(CORE,.10,.50,math.pi)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.60,0),(0,-1,0))}


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





def open_shell(surface_material):
    cols=129;rows=61;vertices=[]
    for inner in [False,True]:
        for row in range(rows):
            y=-.30+1.10*row/(rows-1)
            for col in range(cols):
                phi=.65+(math.tau-1.30)*col/(cols-1)
                if inner:p=Vector((.18*math.cos(phi),.18*math.sin(phi),y));p=Y_AXIS @ p
                else:p=surface(CORE,phi,y)
                vertices.append(p)
    size=cols*rows;faces=[]
    for row in range(rows-1):
        for col in range(cols-1):
            a=row*cols+col;f=(a,a+1,a+cols+1,a+cols);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[r*cols for r in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));data=bpy.data.meshes.new(CORE);data.from_pydata(vertices,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();obj=bpy.data.objects.new(CORE,data);bpy.context.collection.objects.link(obj);finish(obj,CORE,surface_material,0)
    return obj


def build():
    PATCHES.clear()
    m=dict(hull=material('Laser | worn pale shell alloy',(.28,.29,.26),.72,.70),red=material('Laser | worn red dorsal and rear details',(.36,.095,.085),.66,.72),copper=material('Laser | worn copper dorsal lead',(.34,.18,.075),.76,.70),edge=material('Laser | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Laser | dark bay lining',(.012,.016,.018),.40,.80),blue=material('Laser | dull blue bay fittings',(.025,.045,.12),.48,.74))
    for owner in [NOSE,TUBE]:orient(vessel(owner,PROFILES[owner],m['red' if owner==TUBE else 'hull'],[DENTS[owner]]),Y_AXIS,LOCATIONS[owner])
    open_shell(m['hull'])
    beam('Laser thin forward stem',(0,-1.32,0),(0,-1.55,0),.014,m['hull'])
    cylinder('Laser pale forward terminal',(0,-1.55,0),.025,.030,m['hull'],32,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    box('Laser recessed bay floor',(.03,.25,0),(.05,1.10,.26),m['dark'],.003)
    for i,y in enumerate([-.28,.78]):box('Laser bay end wall '+str(i),(0,y,0),(.44,.05,.34),m['hull'],.004)
    for i,y in enumerate([-.10,.20,.50]):
        cylinder('Laser blue fitting base '+str(i),(.055,y,0),.052,.040,m['edge'],32,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
        cylinder('Laser blue bay fitting '+str(i),(.13,y,0),.045,.16,m['blue'],48,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    for i,x in enumerate([-.14,.14]):
        cylinder('Laser red rear port '+str(i),(x,.84,-.10),.065,.18,m['red'],48,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
        cylinder('Laser dark rear inlay '+str(i),(x,.935,-.10),.040,.020,m['dark'],48,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    for i,y in enumerate([-.20,.65]):box('Laser dorsal support '+str(i),(0,y,.29),(.07,.09,.14),m['hull'],.004)
    beam('Laser copper dorsal lead',(0,-.42,.345),(0,-.65,.24),.015,m['copper'])
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Laser service cover '+str(i);patch(panel,owner,z0,z1,phi,.23,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Laser service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.15,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.17,.17]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Laser fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
