"""First RI19 anti-ship lance with fixed base and independently parented yaw assembly."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_surface_mounts import cast_bezel

PROFILES={
 'RI19 fixed green pedestal':[(0,.38),(.05,.46),(.22,.49),(.44,.44),(.65,.35),(.84,.24),(.96,.21),(1.00,.19)],
 'RI19 rotating green head':[(.99,.13),(1.04,.17),(1.12,.19),(1.24,.17),(1.30,.10),(1.33,.04)],
 'RI19 tapered thermal lance':[(0,.09),(.12,.09),(.30,.07),(.68,.04),(.90,.012)]}
PAINT={name:'green' for name in PROFILES}
CENTRES={name:(0,0) for name in PROFILES}
DENTS={'RI19 fixed green pedestal':(-2.2,.50,.003),'RI19 rotating green head':(-1.9,1.18,.002),'RI19 tapered thermal lance':(-1.7,.45,.0015)}
PIVOT=Vector((0,0,1.0));LANCE_START=Vector((.04,.01,1.19));LANCE_AXIS=Vector((.75,.18,.62)).normalized();LANCE_TIP=LANCE_START+LANCE_AXIS*.90
MOVING=['RI19 rotating green head','RI19 tapered thermal lance','RI19 head fitting bezel','RI19 bronze head fitting']


def strip(name,profile,phi,low,high,width,surface):
    vertices=[];count=25
    for row in range(count):
        z=low+(high-low)*row/(count-1);r=profile_radius(profile,z)
        for radial,angle in [(r-.008,phi-width/(2*r)),(r+.006,phi-width/(2*r)),(r+.006,phi+width/(2*r)),(r-.008,phi+width/(2*r))]:
            vertices.append((radial*math.cos(angle),radial*math.sin(angle),z))
    faces=[(3,2,1,0)]
    for row in range(count-1):
        a=row*4;b=a+4
        faces += [(a+j,a+(j+1)%4,b+(j+1)%4,b+j) for j in range(4)]
    faces.append(tuple((count-1)*4+j for j in range(4)))
    mesh=bpy.data.meshes.new(name+' fitted closed casting');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    return obj


def fitting(name,body,point,normal,radius,face_radius,surface,face_surface):
    normal=normal.normalized();point=point+normal*.025
    cast_bezel(name+' bezel',body,point,normal,radius,surface)
    cylinder('RI19 bronze '+('head fitting' if 'head' in name else 'base fitting'),point+normal*.028,face_radius,.016,face_surface,vertices=64,rotation=normal.to_track_quat('Z','Y').to_euler())


def build():
    m=dict(green=material('RI19 | weathered green armour',(.12,.29,.20),.65,.55),
        bronze=material('RI19 | aged bronze fittings',(.31,.20,.065),.74,.54),
        edge=material('RI19 | bearing alloy',(.25,.34,.32),.78,.48),
        dark=material('RI19 | recessed joint steel',(.021,.032,.034),.55,.67))
    parts={name:vessel(name,profile,m['green'],[DENTS[name]]) for name,profile in PROFILES.items()}
    lance=parts['RI19 tapered thermal lance'];lance.location=LANCE_START;lance.rotation_euler=LANCE_AXIS.to_track_quat('Z','Y').to_euler()
    cylinder('RI19 static yaw bearing',(0,0,.995),.145,.090,m['edge'],vertices=64)
    strip('RI19 bronze front strip',PROFILES['RI19 fixed green pedestal'],-math.pi/2,.26,.82,.055,m['bronze'])
    for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6]):
        strip(f'RI19 lower base inset {i}',PROFILES['RI19 fixed green pedestal'],phi,.06,.25,.045,m['dark'])
    z=.36;phi=-math.radians(115);r=profile_radius(PROFILES['RI19 fixed green pedestal'],z)
    fitting('RI19 base fitting',parts['RI19 fixed green pedestal'],Vector((r*math.cos(phi),r*math.sin(phi),z)),Vector((math.cos(phi),math.sin(phi),.227)),.09,.055,m['edge'],m['bronze'])
    z=1.17;r=profile_radius(PROFILES['RI19 rotating green head'],z)
    fitting('RI19 head fitting',parts['RI19 rotating green head'],Vector((0,-r,z)),Vector((0,-1,.1667)),.070,.043,m['edge'],m['bronze'])
    return m
