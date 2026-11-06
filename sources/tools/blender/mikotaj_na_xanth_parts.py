"""First MK4C state-zero interpretation: three metal chambers and copper interfaces."""
import math
import bpy
from mathutils import Vector,Matrix
from build_openfa_assets import material,cylinder,beam,box,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel

CENTRES=[Vector((0,0,0)),Vector((-1.72,0,-.125)),Vector((1.72,0,-.125))]
SCALES=[1,.74,.74]
SLATE=[(-1.0,.08),(-.875,.45),(-.625,.77),(-.25,1.0),(0,1.04),(.25,1.0),(.625,.77),(.875,.45),(1.0,.08)]
GREEN=[(-.0625,1.04),(0,1.06),(.25,1.03),(.625,.80),(.875,.49),(1.0,.08)]
BOSS=[(-.015625,.35),(0,.38),(.125,.34),(.25,.20),(.3125,.16)]
PROFILES={};DENTS={};OWNERS={};PATCHES=[]
for i in range(3):
    for kind,profile,z in [('slate',SLATE,-.55),('green',GREEN,.65)]:
        name='Na-Xanth '+kind+' chamber '+str(i);PROFILES[name]=profile;DENTS[name]=(-math.pi/2,z,.006);OWNERS[name]=i
SOCKETS={'AlignmentAxis':((0,0,1.50),(0,0,1))}


def point(i,p):return CENTRES[i]+Vector(p)*SCALES[i]


def local_surface(name,phi,z,offset=0):
    radius=profile_radius(PROFILES[name],z);angle,height,depth=DENTS[name];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle))
    radius-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));radius+=offset
    return Vector((radius*math.cos(phi),radius*math.sin(phi),z))


def surface(name,phi,z,offset=0):return point(OWNERS[name],local_surface(name,phi,z,offset))


def place_mesh(obj,i,origin=(0,0,0),axis=None):
    rotation=Matrix.Identity(3) if axis is None else Vector(axis).to_track_quat('Z','Y').to_matrix()
    for vertex in obj.data.vertices:vertex.co=point(i,Vector(origin)+rotation @ vertex.co)
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
    m=dict(hull=material('Na-Xanth | worn slate chambers',(.13,.18,.24),.72,.64),green=material('Na-Xanth | worn green upper shells',(.10,.28,.18),.67,.63),copper=material('Na-Xanth | aged copper interfaces',(.30,.13,.075),.78,.64),
        edge=material('Na-Xanth | oxidized service alloy',(.22,.25,.27),.78,.62),dark=material('Na-Xanth | carbon dark recesses',(.012,.016,.018),.40,.80),amber=material('Na-Xanth | dull amber inserts',(.43,.20,.04),.55,.68))
    for name,profile in PROFILES.items():place_mesh(vessel(name,profile,m['hull' if 'slate' in name else 'green'],[DENTS[name]]),OWNERS[name])
    for side in [-1,1]:beam('Na-Xanth structural neck '+str(side),(side*.85,0,-.05),(side*1.45,0,-.05),.16,m['copper'])
    bpy.context.view_layer.update()
    for i in range(3):
        scale=SCALES[i];normal=Vector((0,-1,0));origin=point(i,(0,-1.12,-.10))
        cast_bezel('Na-Xanth body bezel '+str(i),bpy.data.objects['Na-Xanth slate chamber '+str(i)],origin,normal,.40*scale,m['copper'])
        place_mesh(vessel('Na-Xanth forward coupler '+str(i),BOSS,m['copper'],[]),i,(0,-1.15,-.10),normal)
        cylinder('Na-Xanth dark coupler face '+str(i),point(i,(0,-1.15-.313,-.10)),.13*scale,.020*scale,m['dark'],vertices=64,rotation=normal.to_track_quat('Z','Y').to_euler())
        for j,x in enumerate([-.055,0,.055]):box('Na-Xanth face amber tile '+str(i)+' '+str(j),point(i,(x,-1.15-.326,-.10)),(.022*scale,.012*scale,.025*scale),m['amber'],.001*scale)
        for j in range(8):
            phi=j*math.tau/8;axis=Vector((math.cos(phi),math.sin(phi),0));start=axis*.96+Vector((0,0,-.125));end=axis*1.28+Vector((0,0,-.125))
            beam('Na-Xanth perimeter stem '+str(i)+' '+str(j),point(i,start),point(i,end),.024*scale,m['copper'])
            cylinder('Na-Xanth perimeter disc '+str(i)+' '+str(j),point(i,axis*1.27+Vector((0,0,-.125))),.10*scale,.045*scale,m['copper'],vertices=64,rotation=axis.to_track_quat('Z','Y').to_euler())
        for side in [-1,1]:
            beam('Na-Xanth axial stem '+str(i)+' '+str(side),point(i,(0,0,side*.96)),point(i,(0,0,side*1.28)),.025*scale,m['copper'])
            cylinder('Na-Xanth axial disc '+str(i)+' '+str(side),point(i,(0,0,side*1.28)),.20*scale,.045*scale,m['copper'],vertices=64)
        owner='Na-Xanth green chamber '+str(i);panel='Na-Xanth upper dark panel '+str(i);patch(panel,owner,.30,.45,-math.pi/2,.28,m['dark'])
        for j in range(4):patch('Na-Xanth upper amber tile '+str(i)+' '+str(j),owner,.35,.40,-math.pi/2+(j-1.5)*.12,.035,m['amber'],top=.016,back=.003,support=panel)
        for j,z in enumerate([.32,.43]):
            for k,offset in enumerate([-.23,.23]):
                phi=-math.pi/2+offset;n=Vector((math.cos(phi),math.sin(phi),0));p=surface(owner,phi,z)+n*.009*scale
                cylinder('Na-Xanth panel fastener '+str(i)+' '+str(j)+' '+str(k),p,.005*scale,.022*scale,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
