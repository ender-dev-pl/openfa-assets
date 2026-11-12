"""First AC3C state-zero interpretation; no second-state mechanism is inferred."""
import math
import bpy
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius

CORE='Shipyard axial spine'
PROFILES={CORE:[(-3.80,.025),(-3.50,.07),(-2.40,.10),(-1.60,.16),(-.50,.19),(0,.32),(.50,.20),(1.60,.17),(2.80,.12),(3.80,.03),(4.0,.015)]}
POST_X=[-1.35,-.95,-.55,.55,.95,1.35]
LOCATIONS={CORE:Vector((0,0,0))}
ROTATIONS={CORE:Matrix(((0,0,1),(0,1,0),(-1,0,0)))}
DENTS={CORE:(-math.pi/2,0,.006)}
for i,x in enumerate(POST_X):
    name='Shipyard vertical segment '+str(i);PROFILES[name]=[(-.875,.025),(-.70,.065),(-.40,.09),(0,.12),(.40,.09),(.70,.065),(.875,.025)];LOCATIONS[name]=Vector((x,0,0));ROTATIONS[name]=Matrix.Identity(3);DENTS[name]=(-math.pi/2,.10,.003+i*.0002)
PANELS=[('Shipyard vertical segment '+str(i),-.20,.20,-math.pi/2) for i in range(6)]
PATCHES=[]
WINDOW_X=[-3.30,-2.90,-.30,.30,1.80,2.50,3.30]
SOCKETS={'AlignmentAxis':((4.30,0,0),(1,0,0))}


def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return LOCATIONS[owner]+ROTATIONS[owner] @ Vector((r*math.cos(phi),r*math.sin(phi),z))


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=ROTATIONS[owner] @ Vector((math.cos(phi),math.sin(phi),0));inv=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ normal).normalized()


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
    m=dict(copper=material('Shipyard | worn warm spine',(.29,.16,.075),.74,.70),pink=material('Shipyard | worn rose segments',(.37,.15,.12),.68,.72),edge=material('Shipyard | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Shipyard | dark recesses',(.012,.016,.018),.40,.80),blue=material('Shipyard | dull blue fields',(.18,.30,.36),.50,.72),orange=material('Shipyard | dull orange central field',(.48,.09,.025),.50,.73))
    for owner,profile in PROFILES.items():
        obj=vessel(owner,profile,m['copper' if owner==CORE else 'pink'],[DENTS[owner]])
        for v in obj.data.vertices:v.co=LOCATIONS[owner]+ROTATIONS[owner] @ v.co
        obj.data.update()
    for i,x in enumerate(POST_X):
        for j,z in enumerate([-.60,-.30,.30,.60]):cylinder('Shipyard segment collar '+str(i)+' '+str(j),(x,0,z),.115,.055,m['copper'],48)
    for i,x in enumerate(WINDOW_X):
        r=profile_radius(PROFILES[CORE],x)
        box('Shipyard field mount '+str(i),(x,0,r+.025),(.15,.17,.09),m['edge'],.006)
        box('Shipyard blue field '+str(i),(x,-.087,r+.025),(.10,.025,.055),m['blue'],.003)
    patch('Shipyard central orange field',CORE,-.32,.32,-math.pi/2,.48,m['orange'])
    for i,x in enumerate([-.10,.10]):patch('Shipyard central field divider '+str(i),CORE,x-.012,x+.012,-math.pi/2,.49,m['edge'],.016,.003,'Shipyard central orange field')
    for side in [-1,1]:
        beam('Shipyard axial terminal stem '+str(side),(side*(3.75 if side==-1 else 3.95),0,0),(side*4.20,0,0),.010,m['edge'])
        cylinder('Shipyard axial orange terminal '+str(side),(side*4.20,0,0),.020,.035,m['orange'],32,rotation=Vector((1,0,0)).to_track_quat('Z','Y').to_euler())
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Shipyard service cover '+str(i);patch(panel,owner,z0,z1,phi,.30,m['pink'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Shipyard service slot '+str(i)+' '+str(j),owner,z-.006,z+.006,phi,.19,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.23,.23]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Shipyard fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
