"""Independent first PH02 interpretation: low shells, spherical tip and transverse rail."""
import math
import bpy
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius

CORE='Napalm low front shell'
REAR='Napalm bronze rear shell'
TIP='Napalm spherical forward tip'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-1.20,.04),(-.80,.23),(-.20,.35),(.15625,.27)],REAR:[(-.15,.28),(.20,.35),(.55,.32),(.875,.15)]}
PROFILES[TIP]=[(z,math.sqrt(.08**2-z*z)) for z in [-.078125+i*.15625/32 for i in range(33)]]
LOCATIONS={CORE:Vector((0,0,0)),REAR:Vector((0,0,0)),TIP:Vector((0,-1.32,0))}
ROTATIONS={name:Y_AXIS for name in PROFILES}
SCALES={CORE:Vector((1,.55,1)),REAR:Vector((1,.55,1)),TIP:Vector((1,1,1))}
DENTS={CORE:(0,-.50,.005),REAR:(0,.40,.006),TIP:(0,0,0)}
PANELS=[(CORE,-.65,-.35,-math.pi/2),(REAR,.25,.55,-math.pi/2)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.45,0),(0,-1,0))}


def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return LOCATIONS[owner]+ROTATIONS[owner] @ (Vector((r*math.cos(phi),r*math.sin(phi),z))*SCALES[owner])


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=(ROTATIONS[owner] @ Vector((math.cos(phi)/SCALES[owner].x,math.sin(phi)/SCALES[owner].y,0))).normalized();inv=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
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
    m=dict(hull=material('Napalm | worn grey olive shell',(.27,.28,.23),.70,.72),bronze=material('Napalm | worn bronze shell and frame',(.30,.20,.115),.74,.72),edge=material('Napalm | oxidized service alloy',(.19,.22,.23),.78,.65),dark=material('Napalm | dark side fittings',(.018,.028,.04),.48,.80))
    for owner,profile in PROFILES.items():
        obj=vessel(owner,profile,m['bronze' if owner==REAR else 'hull'],[DENTS[owner]])
        for v in obj.data.vertices:v.co*=SCALES[owner]
        orient(obj,ROTATIONS[owner],LOCATIONS[owner])
    beam('Napalm forward neck',(0,-1.15,0),(0,-1.30,0),.025,m['hull'])
    for i,x in enumerate([-.31,0,.31]):cylinder('Napalm transverse rail segment '+str(i),(x,.90,.07),.065,.32,m['hull'],48,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    for i,x in enumerate([-.155,.155]):cylinder('Napalm transverse rail collar '+str(i),(x,.90,.07),.071,.045,m['edge'],48,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    for side in [-1,1]:beam('Napalm side frame '+str(side),(side*.20,.15,-.04),(side*.31,.90,.07),.025,m['bronze'])
    bpy.context.view_layer.update()
    for i,y in enumerate([.25,.48]):
        p,n=hull_frame(REAR,0,y)
        cylinder('Napalm fitting base '+str(i),p+n*.010,.032,.040,m['edge'],32,rotation=n.to_track_quat('Z','Y').to_euler())
        cylinder('Napalm dark fitting '+str(i),p+n*.034,.026,.016,m['dark'],32,rotation=n.to_track_quat('Z','Y').to_euler())
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Napalm service cover '+str(i);patch(panel,owner,z0,z1,phi,.23,m['bronze' if owner==REAR else 'hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Napalm service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.15,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.17,.17]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Napalm fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.007,.003,.018,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
