"""First AR4C transporter: twin gold bodies, silver bridge and lateral modules."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,beam,box,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

MAIN_PROFILE=[(-.375,.08),(-.25,.48),(-.09375,.72),(0,.78),(.15625,.70),(.3125,.52),(.40625,.28),(.4375,.08)]
POD_PROFILE=[(-.125,.04),(-.0625,.17),(0,.22),(.0625,.17),(.09375,.06)]
PROFILES={};LOCATIONS={};DENTS={};PATCHES=[]
for i,y in enumerate([-1.30,1.30]):
    name='Hardcore main pressure body '+str(i);PROFILES[name]=MAIN_PROFILE;LOCATIONS[name]=Vector((0,y,0));DENTS[name]=(-math.pi/2,.20,.006)
    for side in [-1,1]:
        name='Hardcore lateral module '+str(i)+' '+str(side);PROFILES[name]=POD_PROFILE;LOCATIONS[name]=Vector((side*1.16,y,-.03));DENTS[name]=(-math.pi/2,.04,.002)
SOCKETS={'AlignmentForward':((0,-2.20,-.01),(0,-1,0))}
PANELS=[-math.pi/2-.65,-math.pi/2+.65]
TAIL=[(1.60,.45),(2.0,.60),(2.60,.30),(2.75,.03)]


def surface(name,phi,z,offset=0):
    r=profile_radius(PROFILES[name],z);angle,height,depth=DENTS[name];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return LOCATIONS[name]+Vector((r*math.cos(phi),r*math.sin(phi),z))


def place(obj,location):
    for v in obj.data.vertices:v.co+=Vector(location)
    obj.data.update();return obj


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=Vector((math.cos(phi),math.sin(phi),0));inv=obj.matrix_world.inverted()
    hit,where,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
    return obj.matrix_world @ where,(inv.to_3x3().transposed() @ normal).normalized()


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



def tail_width(y):
    return next(wa+(wb-wa)*(y-a)/(b-a) for (a,wa),(b,wb) in zip(TAIL,TAIL[1:]) if a-1e-9<=y<=b+1e-9)


def tail(surface_material):
    ys=[]
    for (a,_),(b,_) in zip(TAIL,TAIL[1:]):
        count=math.ceil((b-a)/.025);ys.extend(a+(b-a)*i/count for i in range(count))
    ys.append(TAIL[-1][0]);columns=33;top=[];back=[]
    for y in ys:
        w=tail_width(y)
        for col in range(columns):
            u=-1+2*col/(columns-1);x=w*u;top.append((x,y,-.07-.02*abs(u)));back.append((x,y,-.14))
    size=len(top);vertices=top+back;faces=[];rows=len(ys)
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,rows-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));data=bpy.data.meshes.new('Hardcore tail plane');data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new('Hardcore tail plane',data);bpy.context.collection.objects.link(obj);finish(obj,obj.name,surface_material,0);return obj


def build():
    PATCHES.clear()
    m=dict(gold=material('Hardcore | worn gold brown shells',(.32,.23,.10),.76,.64),hull=material('Hardcore | worn silver bridge',(.27,.29,.30),.78,.64),edge=material('Hardcore | oxidized blue grey details',(.12,.17,.24),.72,.65),dark=material('Hardcore | carbon dark seams',(.012,.016,.018),.40,.80))
    for name,profile in PROFILES.items():place(vessel(name,profile,m['gold'],[DENTS[name]]),LOCATIONS[name])
    for i,y in enumerate([-1.30,1.30]):
        owner='Hardcore main pressure body '+str(i);heights=[-.06,-.02];rows=[(z,profile_radius(MAIN_PROFILE,z)+.012,profile_radius(MAIN_PROFILE,z)-.018) for z in heights]
        annulus('Hardcore silver body trim '+str(i),(0,y),rows,m['hull'],(0,-.04,0))
        for side in [-1,1]:beam('Hardcore lateral arm '+str(i)+' '+str(side),(side*.62,y,-.03),(side*1.18,y,-.03),.045,m['gold'])
    box('Hardcore silver connecting bridge',(0,0,-.06),(.64,1.72,.14),m['hull'],.012)
    for side in [-1,1]:beam('Hardcore bridge edge rail '+str(side),(side*.25,-.90,.02),(side*.25,.90,.02),.040,m['gold'])
    tail(m['gold']);bpy.context.view_layer.update()
    n=Vector((0,-1,0));origin=Vector((0,-2.12,-.01));cast_bezel('Hardcore fore interface bezel',bpy.data.objects['Hardcore main pressure body 0'],origin,n,.14,m['gold'])
    cylinder('Hardcore blue grey fore interface',origin+n*.030,.11,.020,m['edge'],vertices=64,rotation=n.to_track_quat('Z','Y').to_euler())
    for side in [-1,1]:beam('Hardcore aft blue grey projection '+str(side),(side*.42,1.70,0),(side*.52,2.65,-.02),.012,m['edge'])
    for i in range(2):
        owner='Hardcore main pressure body '+str(i)
        for j,phi in enumerate(PANELS):
            panel='Hardcore service cover '+str(i)+' '+str(j);patch(panel,owner,.15,.28,phi,.18,m['gold'])
            for k,z in enumerate([.185,.245]):patch('Hardcore service slot '+str(i)+' '+str(j)+' '+str(k),owner,z-.006,z+.006,phi,.12,m['dark'],top=.016,back=.003,support=panel)
            for k,z in enumerate([.165,.265]):
                for l,offset in enumerate([-.14,.14]):
                    p,n=hull_frame(owner,phi+offset,z);cylinder('Hardcore fastener '+str(i)+' '+str(j)+' '+str(k)+' '+str(l),p+n*.009,.0045,.022,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
