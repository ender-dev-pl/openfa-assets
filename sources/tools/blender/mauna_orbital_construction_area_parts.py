"""First MN5C state-zero station; second fixed-state presentation remains unresolved."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius

CORE='Orbital broad casing'
CAP='Orbital copper upper shell'
LOWER='Orbital tapered lower shell'
PROFILES={CORE:[(-.3125,.70),(-.20,1),(.10,1),(.3125,.70)],CAP:[(.25,.65),(.40,.70),(.60,.35),(.6875,.20)],LOWER:[(-1.25,.055),(-.95,.16),(-.65,.30),(-.28125,.50)]}
DENTS={CORE:(-math.pi/2,0,.008),CAP:(-math.pi/2,.48,.007),LOWER:(-math.pi/2,-.80,.005)}
SCALES={CORE:Vector((1.80,.72,1)),CAP:Vector((1.80,.72,1)),LOWER:Vector((1.1,.8,1))}
PATCHES=[]
PANELS=[(CORE,-.13,.06,-math.pi/2-.50),(CORE,-.13,.06,-math.pi/2+.50),(CAP,.42,.54,-math.pi/2-.40),(CAP,.42,.54,-math.pi/2+.40)]
SOCKETS={'AlignmentAxis':((0,0,1.90),(0,0,1))}


def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return Vector((r*math.cos(phi),r*math.sin(phi),z))*SCALES[owner]


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=Vector((math.cos(phi)/SCALES[owner].x,math.sin(phi)/SCALES[owner].y,0)).normalized();inv=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
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
    m=dict(hull=material('Orbital | worn grey casing',(.22,.25,.27),.74,.67),copper=material('Orbital | worn copper shell',(.29,.12,.065),.76,.70),edge=material('Orbital | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Orbital | dark recesses',(.012,.016,.018),.40,.80),green=material('Orbital | dull green inserts',(.12,.36,.23),.52,.72),amber=material('Orbital | dull orange bands',(.46,.13,.025),.50,.73))
    for owner,profile in PROFILES.items():
        obj=vessel(owner,profile,m['copper' if owner!=CORE else 'hull'],[DENTS[owner]])
        for v in obj.data.vertices:v.co*=SCALES[owner]
        obj.data.update()
    cylinder('Orbital central tower',(0,0,.94),.14,.68,m['copper'],64)
    cylinder('Orbital central spire',(0,0,1.53),.042,.62,m['edge'],48)
    for i,z in enumerate([1.30,1.45,1.60,1.75]):cylinder('Orbital central orange collar '+str(i),(0,0,z),.052,.035,m['amber'],48)
    for side in [-1,1]:
        cylinder('Orbital secondary tower '+str(side),(side*.65,0,.70),.09,.66,m['copper'],48)
        cylinder('Orbital secondary stem '+str(side),(side*.65,0,1.11),.025,.25,m['edge'],32)
        for i,z in enumerate([.52,.72,.92,1.08]):cylinder('Orbital secondary orange collar '+str(side)+' '+str(i),(side*.65,0,z),.102 if z<1 else .033,.032,m['amber'],48)
    beam('Orbital lower axial stem',(0,0,-1.20),(0,0,-1.62),.016,m['edge'])
    for i,z in enumerate([-.75,-.88,-1.01]):
        patch('Orbital lower orange vent '+str(i),LOWER,z-.019,z+.019,-math.pi/2,.40,m['amber'],.012,-.020)
    box('Orbital lateral spine',(1.92,0,0),(1.15,.10,.12),m['edge'],.010)
    for i,x in enumerate([2.04,2.42]):
        for j,z in enumerate([-.24,.24]):
            label=str(i)+' '+str(j)
            box('Orbital green bank frame '+label,(x,0,z),(.30,.12,.48),m['hull'],.012)
            box('Orbital green bank insert '+label,(x,-.066,z),(.20,.035,.37),m['green'],.005)
            for k,dz in enumerate([-.12,0,.12]):box('Orbital green bank bar '+label+' '+str(k),(x,-.086,z+dz),(.23,.020,.018),m['edge'],.002)
    cylinder('Orbital bank terminal',(2.70,0,0),.065,.62,m['copper'],48)
    beam('Orbital bank end link',(2.43,0,0),(2.71,0,0),.025,m['edge'])
    for i,z in enumerate([-.24,.24]):cylinder('Orbital bank terminal band '+str(i),(2.70,0,z),.075,.04,m['amber'],48)
    box('Orbital opposite axial root',(-1.75,0,-.02),(.35,.22,.22),m['hull'],.025)
    beam('Orbital opposite axial tip',(-1.80,0,-.02),(-2.12,0,-.02),.023,m['edge'])
    for i,phi in enumerate([-math.pi/2-.20,-math.pi/2,-math.pi/2+.20]):
        # Short fitted green plates on the broad casing, with narrow alloy dividers.
        patch('Orbital central green plate '+str(i),CORE,-.12,.08,phi,.065,m['green'])
        for j,z in enumerate([-.06,.02]):patch('Orbital central plate divider '+str(i)+' '+str(j),CORE,z-.006,z+.006,phi,.067,m['edge'],.016,.003,'Orbital central green plate '+str(i))
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Orbital service cover '+str(i);patch(panel,owner,z0,z1,phi,.13,m['copper' if owner==CAP else 'hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Orbital service slot '+str(i)+' '+str(j),owner,z-.005,z+.005,phi,.09,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.10,.10]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Orbital fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.0035,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
