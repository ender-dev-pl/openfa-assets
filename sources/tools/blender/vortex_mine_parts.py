"""Independent first PH04 segmented equipment; no launch mechanics inferred."""
import math
import bpy
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

CORE='Vortex central casing'
NOSE='Vortex tapered front'
REAR='Vortex red rear end'
PRONG='Vortex small rear prong'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(-.90,.25),(-.50,.28),(.75,.28),(.9375,.23)],NOSE:[(-1.20,.10),(-1.05,.19),(-.80,.25),(-.75,.25)],REAR:[(.875,.12),(.95,.16),(1.0625,.15),(1.09375,.10)],PRONG:[(.8125,.040),(1.0625,.040),(1.125,.025)]}
SLEEVES=[(-.50,-.203125),(-.18,.25),(.27,.6875)]
for i,(a,b) in enumerate(SLEEVES):PROFILES['Vortex casing sleeve '+str(i)]=[(a,.291),(b,.291)]
LOCATIONS={name:Vector((.21,0,-.10) if name==PRONG else (0,0,0)) for name in PROFILES}
ROTATIONS={name:Y_AXIS for name in PROFILES}
DENTS={name:(0,0,0) for name in PROFILES};DENTS.update({CORE:(0,-.65,.006),NOSE:(0,-1.0,.004),REAR:(0,1.0,.003)})
PANELS=[('Vortex casing sleeve 1',-.10,.15,0),('Vortex casing sleeve 1',-.10,.15,math.pi),(NOSE,-1.10,-.99,-math.pi/2)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.30,0),(0,-1,0))}


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
    m=dict(hull=material('Vortex | worn pale casing alloy',(.28,.29,.28),.74,.70),red=material('Vortex | worn red end details',(.33,.095,.08),.66,.73),edge=material('Vortex | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Vortex | dark small recess',(.012,.016,.018),.40,.80),blue=material('Vortex | dull blue frontal field',(.025,.045,.16),.48,.75))
    for owner,profile in PROFILES.items():
        if 'casing sleeve' in owner:continue
        orient(vessel(owner,profile,m['red' if owner in [REAR,PRONG] else 'hull'],[DENTS[owner]]),ROTATIONS[owner],LOCATIONS[owner])
    for i,(a,b) in enumerate(SLEEVES):orient(annulus('Vortex casing sleeve '+str(i),(0,0),[(a,.291,.270),(b,.291,.270)],m['hull'],(0,(a+b)/2,0)),Y_AXIS)
    orient(annulus('Vortex nose rim',(0,0),[(-1.25,.10,.055),(-1.15,.115,.055)],m['hull'],(0,-1.2,0)),Y_AXIS)
    cylinder('Vortex blue blind backing',(0,-1.19,0),.070,.040,m['blue'],64,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    cylinder('Vortex clipped rear collar',(0,.83,0),.34,.10,m['hull'],8,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    cylinder('Vortex small rear dark face',(.21,1.124,-.10),.016,.014,m['dark'],32,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())
    bpy.context.view_layer.update()
    for side in [-1,1]:
        p,n=hull_frame(NOSE,0 if side==1 else math.pi,-1.05)
        cast_bezel('Vortex nose bezel '+str(side),bpy.data.objects[NOSE],p,n,.055,m['hull'])
        cylinder('Vortex red nose insert '+str(side),p+n*.027,.040,.020,m['red'],48,rotation=n.to_track_quat('Z','Y').to_euler())
        cylinder('Vortex lower side boss '+str(side),(side*.27,-.72,-.10),.045,.14,m['hull'],48,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
        cylinder('Vortex lower red tip '+str(side),(side*.34,-.72,-.10),.035,.025,m['red'],48,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Vortex service cover '+str(i);patch(panel,owner,z0,z1,phi,.23,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Vortex service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.15,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.17,.17]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Vortex fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
