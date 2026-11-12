"""Independent first PS7C orbital dock; unseen faces and arms are interpretations."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,finish,material
from build_assault_fighter import plate
from manufactured_vessels import profile_radius
from manufactured_annuli import annulus

PROFILES={'Space Dock lower tapered hull':[(-2.5,.025),(-2.1,.14),(-1.3,.52),(-.5,.9),(.12,1.15)],
 'Space Dock pyramidal upper hull':[(.08,1.3),(.20,1.25),(.70,.65),(1.05,.22)]}
DENTS={'Space Dock lower tapered hull':(-math.pi/2,-.90,.008),'Space Dock pyramidal upper hull':(-math.pi/2,.40,.006)}
SOCKETS={'Equipment crown':((0,0,1.08),(0,0,1)),'Equipment port':((-1.25,0,.13),(-1,0,0)),
 'Equipment starboard':((1.25,0,.13),(1,0,0)),'Equipment lower':((0,-.5,-1.20),(0,-1,0))}


def shell(name,profile,surface):
    cross=[]
    for i in range(8):
        a=Vector((math.cos(math.pi/8+i*math.tau/8),math.sin(math.pi/8+i*math.tau/8)))
        b=Vector((math.cos(math.pi/8+(i+1)*math.tau/8),math.sin(math.pi/8+(i+1)*math.tau/8)))
        cross.extend(a.lerp(b,j/8) for j in range(8))
    heights=[]
    for a,b in zip(profile,profile[1:]):
        n=math.ceil((b[0]-a[0])/.035);heights.extend(a[0]+(b[0]-a[0])*i/n for i in range(n))
    heights.append(profile[-1][0]);vertices=[];phi0,z0,depth=DENTS[name]
    for z in heights:
        radius=profile_radius(profile,min(profile[-1][0],max(profile[0][0],z)))
        for p in cross:
            phi=math.atan2(p.y,p.x);angle=math.atan2(math.sin(phi-phi0),math.cos(phi-phi0));d=depth*math.exp(-2*((angle/.10)**2+((z-z0)/.12)**2));q=p*radius-p.normalized()*d;vertices.append((q.x,q.y,z))
    count=len(cross);first=len(vertices);last=first+1;vertices.extend([(0,0,heights[0]),(0,0,heights[-1])]);end=(len(heights)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces.extend((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(len(heights)-1) for i in range(count))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def front_y(profile,z):return -profile_radius(profile,z)*math.cos(math.pi/8)


def build():
    m=dict(hull=material('Space Dock | worn violet hull',(.15,.14,.21),.65,.56),red=material('Space Dock | worn red markings',(.46,.025,.016),.45,.58),
        edge=material('Space Dock | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Space Dock | soot graphite',(.012,.013,.017),.45,.76),gold=material('Space Dock | heat stained bronze',(.31,.20,.08),.78,.66))
    for name,profile in PROFILES.items():shell(name,profile,m['hull'])
    annulus('Space Dock equatorial rim',(0,0),[(.075,1.25,.98),(.10,1.34,.98),(.145,1.28,.98)],m['edge'],(0,.1,0))
    # Four radial arms interpret partially visible lateral structures, not proven berth count.
    for i in range(4):
        n=Vector((math.cos(i*math.pi/2),math.sin(i*math.pi/2),0));a=n*.82;a.z=-.23;b=n*1.65;b.z=-.23
        beam('Space Dock radial arm '+str(i),a,b,.065,m['edge']);pod=box('Space Dock berth pod '+str(i),tuple(b),(.38,.25,.23),m['hull'],.018);pod.rotation_euler.z=i*math.pi/2
        c=n*.60;c.z=-.90;d=n*1.48;d.z=-.27;beam('Space Dock diagonal brace '+str(i),c,d,.035,m['edge'])
        p=n*1.66;p.z=-.12;box('Space Dock berth dark inset '+str(i),tuple(p),(.19,.14,.015),m['dark'],.002)
        p=n*1.77;p.z=-.112;cylinder('Space Dock berth marker '+str(i),tuple(p),.014,.012,m['gold'],vertices=16)
    beam('Space Dock main antenna',(0,0,1.01),(0,0,1.90),.025,m['edge'])
    cylinder('Space Dock antenna collar',(0,0,1.08),.09,.12,m['hull'],vertices=32)
    for i,x in enumerate([-.14,.14]):
        beam('Space Dock auxiliary antenna '+str(i),(x,0,.99),(x,0,1.54+i*.13),.011,m['edge'])
    beam('Space Dock lower sensor',(0,0,-2.46),(0,0,-2.83),.009,m['gold'])
    # Front roof markings follow the actual octagonal flat plane.
    profile=PROFILES['Space Dock pyramidal upper hull']
    for side in [-1,1]:
        points=[]
        for x,z in [(side*.12,.26),(side*.28,.26),(side*.20,.64),(side*.08,.64)]:points.append((x,front_y(profile,z)-.004,z))
        obj=plate('Space Dock roof red band '+str(side),points,.012,m['red'],0)
        # Plate extrusion is world -Z; place a tiny closed fitted panel with Y thickness instead.
        for j in range(4,len(obj.data.vertices)):obj.data.vertices[j].co.y+=.012;obj.data.vertices[j].co.z+=.012
    lower=PROFILES['Space Dock lower tapered hull']
    for i,z in enumerate([-.65,-1.05,-1.45]):
        width=profile_radius(lower,z)*.55;y=front_y(lower,z)-.012
        box('Space Dock lower service slot '+str(i),(0,y,z),(width,.035,.065),m['dark'],.003)
        for side in [-1,1]:
            cylinder('Space Dock lower slot fastener '+str(i)+' '+str(side),(side*width*.42,y-.022,z),.012,.012,m['gold'],vertices=16,rotation=(math.pi/2,0,0))
    return m
