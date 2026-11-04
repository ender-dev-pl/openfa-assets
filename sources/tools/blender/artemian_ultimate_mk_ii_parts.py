"""First AR3C: elongated silver upper cover, green lower body and perimeter fittings."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

UPPER='Ultimate Mk II silver upper cover'
LOWER='Ultimate Mk II green lower body'
SCALE_Y=2.05
PROFILES={UPPER:[(-.0625,.98),(0,1.05),(.15625,1.02),(.3125,.88),(.4375,.65),(.484375,.32),(.5,.06)],
 LOWER:[(-.3125,.12),(-.28125,.45),(-.1875,.78),(-.09375,.91),(.03125,.93),(.0625,.88)]}
DENTS={UPPER:(-math.pi/2,.36,.006),LOWER:(-math.pi/2,-.24,.005)}
FITTING_PROFILE=[(-.015625,.065),(0,.075),(.0625,.09),(.125,.065),(.15625,.025)]
PATCHES=[]
FITTING_FRAMES=[]
PANELS=[-math.pi/2-.60,-math.pi/2+.60,math.pi/2-.60,math.pi/2+.60]
SOCKETS={'AlignmentForward':((0,-2.20,-.02),(0,-1,0))}


def surface(name,phi,z,offset=0):
    radius=profile_radius(PROFILES[name],z);angle,height,depth=DENTS[name];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle))
    radius-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));radius+=offset
    return Vector((radius*math.cos(phi),radius*math.sin(phi)*SCALE_Y,z))


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=Vector((math.cos(phi),math.sin(phi),0));inverse=obj.matrix_world.inverted()
    hit,where,normal,_=obj.ray_cast(inverse @ (p+n*3),(inverse.to_3x3() @ -n).normalized());assert hit
    where=obj.matrix_world @ where;normal=(inverse.to_3x3().transposed() @ normal).normalized();return where,normal


def stretch(obj):
    for vertex in obj.data.vertices:vertex.co.y*=SCALE_Y
    obj.data.update();return obj


def pose(obj,origin,normal):
    rotation=Vector(normal).to_track_quat('Z','Y').to_matrix()
    for vertex in obj.data.vertices:vertex.co=Vector(origin)+rotation @ vertex.co
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
    PATCHES.clear();FITTING_FRAMES.clear()
    m=dict(hull=material('Ultimate Mk II | worn silver cover',(.27,.29,.30),.78,.63),green=material('Ultimate Mk II | worn green lower shell',(.10,.28,.12),.68,.65),edge=material('Ultimate Mk II | oxidized service alloy',(.17,.20,.22),.78,.65),dark=material('Ultimate Mk II | carbon dark seams',(.012,.016,.018),.40,.80))
    for owner in [UPPER,LOWER]:stretch(vessel(owner,PROFILES[owner],m['hull' if owner==UPPER else 'green'],[DENTS[owner]]))
    heights=[-.015625,0,.015625];rows=[(z,profile_radius(PROFILES[UPPER],z)+.012,profile_radius(PROFILES[UPPER],z)-.018) for z in heights]
    stretch(annulus('Ultimate Mk II lid seam rim',(0,0),rows,m['edge'],(0,0,0)))
    bpy.context.view_layer.update()
    for i in range(12):
        phi=i*math.tau/12;p,n=hull_frame(LOWER,phi,-.15625);origin=p+n*.045
        cast_bezel('Ultimate Mk II fitting bezel '+str(i),bpy.data.objects[LOWER],origin,n,.085,m['hull'])
        pose(vessel('Ultimate Mk II perimeter fitting '+str(i),FITTING_PROFILE,m['hull'],[]),origin+n*.030,n)
        FITTING_FRAMES.append(dict(index=i,origin=list(origin),normal=list(n),status='authored fitting layout; not calibrated equipment mount'))
    for i,phi in enumerate(PANELS):
        panel='Ultimate Mk II service cover '+str(i);patch(panel,UPPER,.18,.30,phi,.18,m['hull'])
        for j,z in enumerate([.215,.265]):patch('Ultimate Mk II service slot '+str(i)+' '+str(j),UPPER,z-.006,z+.006,phi,.12,m['dark'],top=.016,back=.003,support=panel)
        for j,z in enumerate([.195,.285]):
            for k,offset in enumerate([-.14,.14]):
                p,n=hull_frame(UPPER,phi+offset,z);cylinder('Ultimate Mk II fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.0045,.022,m['edge'],vertices=16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
