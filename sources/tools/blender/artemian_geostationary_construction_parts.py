"""First AR5C state-zero interpretation; no second-state/scaffolding mechanism is inferred."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,beam,box,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus

CORE='Geostationary green axial body'
CAP='Geostationary copper aft shell'
BOSS='Geostationary green central boss'
PROFILES={CORE:[(-1.5,.10),(-1.35,.32),(-.95,.50),(-.50,.55),(0,.45),(.3125,.34)],
 CAP:[(-1.4375,.08),(-1.35,.55),(-1.15,.85),(-.95,.76),(-.875,.48)],
 BOSS:[(.3125,.23),(.4375,.38),(.625,.30),(.78125,.08)]}
DENTS={CORE:(-math.pi/2,-.50,.005),CAP:(-math.pi/2,-1.13,.006),BOSS:(-math.pi/2,.60,.004)}
LOCATIONS={name:Vector((0,0,0)) for name in PROFILES}
POD_PROFILE=[(.3125,.16),(.4375,.23),(.5625,.19),(.625,.08)]
for i in range(6):
    name='Geostationary front module '+str(i);phi=i*math.tau/6;PROFILES[name]=POD_PROFILE;LOCATIONS[name]=Vector((.72*math.cos(phi),.72*math.sin(phi),0));DENTS[name]=(-math.pi/2,.53,.003)
PATCHES=[]
PANELS=[(CORE,-.35,-.18,-math.pi/2-.65),(CORE,-.35,-.18,-math.pi/2+.65),(CAP,-1.22,-1.06,-math.pi/2-.65),(CAP,-1.22,-1.06,-math.pi/2+.65)]
DISH_ORIGIN=Vector((-1.40,0,-.60));DISH_NORMAL=Vector((-1,0,0))
SOCKETS={'AlignmentAxis':((0,0,1.42),(0,0,1))}


def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return LOCATIONS[owner]+Vector((r*math.cos(phi),r*math.sin(phi),z))


def place(obj,origin,normal=None):
    rotation=Vector(normal).to_track_quat('Z','Y').to_matrix() if normal is not None else None
    for v in obj.data.vertices:v.co=Vector(origin)+(rotation @ v.co if rotation is not None else v.co)
    obj.data.update();return obj


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=Vector((math.cos(phi),math.sin(phi),0));inv=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
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



def dish(surface_material):
    count=64;rings=8;size=1+count*rings;vertices=[]
    for offset in [0,-.025]:
        vertices.append((0,0,offset))
        for row in range(1,rings+1):
            r=.26*row/rings
            for i in range(count):
                phi=i*math.tau/count;vertices.append((r*math.cos(phi),r*math.sin(phi),.07*(r/.26)**2+offset))
    faces=[]
    for i in range(count):
        a=1+i;b=1+(i+1)%count;faces.extend([(0,a,b),(size,b+size,a+size)])
    for row in range(rings-1):
        for i in range(count):
            a=1+row*count+i;b=1+row*count+(i+1)%count;c=b+count;d=a+count;faces.extend([(a,b,c,d),(a+size,d+size,c+size,b+size)])
    for i in range(count):
        a=1+(rings-1)*count+i;b=1+(rings-1)*count+(i+1)%count;faces.append((a,a+size,b+size,b))
    data=bpy.data.meshes.new('Geostationary side dish');data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new('Geostationary side dish',data);bpy.context.collection.objects.link(obj);finish(obj,obj.name,surface_material,0);return place(obj,DISH_ORIGIN,DISH_NORMAL)


def build():
    PATCHES.clear()
    m=dict(green=material('Geostationary | worn green shells',(.10,.28,.18),.68,.65),copper=material('Geostationary | worn copper shells',(.30,.13,.075),.76,.64),edge=material('Geostationary | oxidized service alloy',(.17,.20,.22),.78,.65),dark=material('Geostationary | carbon dark face',(.012,.016,.018),.40,.80),blue=material('Geostationary | dull blue inserts',(.015,.03,.35),.40,.67),amber=material('Geostationary | dull amber tips',(.45,.15,.025),.45,.69))
    for owner,profile in PROFILES.items():place(vessel(owner,profile,m['copper' if owner==CAP else 'green'],[DENTS[owner]]),LOCATIONS[owner])
    cylinder('Geostationary dark backing face',(0,0,.30),1.25,.12,m['dark'],vertices=128)
    annulus('Geostationary copper face rim',(0,0),[(.25,1.40,1.22),(.3125,1.45,1.22),(.4375,1.38,1.22)],m['copper'],(0,.33,0))
    for i in range(6):
        centre=LOCATIONS['Geostationary front module '+str(i)];heights=[.40,.4375,.45];rows=[(z,profile_radius(POD_PROFILE,z)+.010,profile_radius(POD_PROFILE,z)-.016) for z in heights]
        annulus('Geostationary module copper collar '+str(i),tuple(centre[:2]),rows,m['copper'],(0,.42,0))
    for i in range(12):
        phi=i*math.tau/12;obj=box('Geostationary blue face insert '+str(i),(1.10*math.cos(phi),1.10*math.sin(phi),.364),(.04,.07,.012),m['blue'],.001);obj.rotation_euler.z=phi
    beam('Geostationary aft axial stem',(0,0,-1.43),(0,0,-2.10),.020,m['green']);cylinder('Geostationary aft amber tip',(0,0,-2.10),.030,.04,m['amber'],vertices=32)
    beam('Geostationary fore axial stem',(0,0,.75),(0,0,1.40),.015,m['green']);cylinder('Geostationary fore amber tip',(0,0,1.40),.030,.04,m['amber'],vertices=32)
    dish(m['copper']);beam('Geostationary side dish mast',(-.60,0,-1.05),DISH_ORIGIN-DISH_NORMAL*.015,.020,m['copper'])
    beam('Geostationary side dish feed',DISH_ORIGIN-DISH_NORMAL*.010,DISH_ORIGIN+DISH_NORMAL*.11,.006,m['edge'])
    cylinder('Geostationary side amber feed',DISH_ORIGIN+DISH_NORMAL*.11,.015,.025,m['amber'],vertices=32,rotation=DISH_NORMAL.to_track_quat('Z','Y').to_euler())
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Geostationary service cover '+str(i);patch(panel,owner,z0,z1,phi,.18,m['copper' if owner==CAP else 'green'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Geostationary service slot '+str(i)+' '+str(j),owner,z-.006,z+.006,phi,.12,m['dark'],top=.016,back=.003,support=panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,offset in enumerate([-.14,.14]):
                p,n=hull_frame(owner,phi+offset,z);cylinder('Geostationary fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.0045,.022,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
