"""Independent RI07 single saucer, tall green mast and silver fork."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import beam,box,cylinder,finish,material
from manufactured_vessels import vessel,profile_radius as radius
from manufactured_roof_wells import roof_well
from terran_missile_parts import band,revolved

BASE=[(0,.46),(.10,.68),(.22,.66),(.55,.48),(1.10,.31),(1.65,.22),(2.12,.22)]
DISC=[(2.00,.38),(2.09,.78),(2.19,1.02),(2.28,1.10),(2.36,1.03),(2.46,.82),(2.56,.46),(2.60,.23)]
MAST=[(2.98,.20),(3.15,.24),(3.70,.24),(3.85,.16),(4.55,.11),(4.65,.08)]
WELL=(-.63,-.30)
DENTS=[(-2.10,.43,.009),(.40,2.28,.009),(.60,3.45,.006)]


def palette():
    return dict(body=material('RI07 | aged jade shell',(.12,.29,.22),.53,.50),
        edge=material('RI07 | abraded pale alloy',(.39,.46,.42),.76,.46),
        dirt=material('RI07 | contaminated gaskets',(.045,.085,.060),.18,.83),
        dark=material('RI07 | deep equipment well',(.015,.025,.024),.38,.64),
        gold=material('RI07 | aged brass fittings',(.46,.29,.085),.73,.49),
        rubbed=material('RI07 | rubbed pale conductor edges',(.55,.63,.61),.80,.39),
        panel=material('RI07 | pale green inspection covers',(.16,.31,.26),.53,.50))


def circular_cover(label,point,normal,r,m):
    normal=Vector(normal).normalized();centre=Vector(point)-normal*.008
    face=cylinder(label+' pressure face',centre,r,.040,m['panel'],vertices=64);face.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    bpy.ops.mesh.primitive_torus_add(major_radius=r*.96,minor_radius=.010,major_segments=48,minor_segments=12,location=centre+normal*.014)
    ring=bpy.context.object;ring.rotation_euler=normal.to_track_quat('Z','Y').to_euler();finish(ring,label+' worn retaining ring',m['edge'],0)
    for face in ring.data.polygons: face.use_smooth=True


def build():
    m=palette();vessel('RI07 flared mounting pedestal',BASE,m['body'],DENTS)
    disc=vessel('RI07 broad laboratory saucer',DISC,m['body'],DENTS);roof_well(disc,'RI07 laboratory',WELL,2.0,m)
    vessel('RI07 segmented green mast',MAST,m['body'],DENTS)
    band('RI07 ground machined rim',.095,.678,.032,m['edge'],.024)
    band('RI07 saucer perimeter seam',2.28,1.104,.026,m['edge'],.020)
    for i,phi in enumerate([-math.pi/2,-.30]):
        normal=Vector((math.cos(phi),math.sin(phi),0));r=radius(DISC,2.28);centre=normal*(r-.010);centre.z=2.28
        bezel=box(f'RI07 rim fitting {i} dark bezel',centre,(.095,.030,.095),m['dark'],.008);bezel.rotation_euler.z=phi-math.pi/2
        centre=normal*(r+.008);centre.z=2.28
        face=box(f'RI07 rim fitting {i} brass face',centre,(.060,.010,.060),m['gold'],.004);face.rotation_euler.z=phi-math.pi/2
    circular_cover('RI07 roof circular inspection cover',(0,-.55,2.535),(0,-1,3.6),.115,m)
    phi=-.85;z=.30;r=radius(BASE,z)
    circular_cover('RI07 pedestal circular inspection cover',(r*math.cos(phi),r*math.sin(phi),z),(math.cos(phi),math.sin(phi),.545),.105,m)
    cylinder('RI07 solid exposed brass neck',(0,0,2.80),.16,.62,m['gold'],vertices=64)
    for i in range(4):
        phi=math.pi/4+i*math.pi/2
        beam('RI07 pale neck retaining strut',(.205*math.cos(phi),.205*math.sin(phi),2.54),(.205*math.cos(phi),.205*math.sin(phi),3.06),.018,m['edge'])
    band('RI07 lower neck retaining collar',2.55,.219,.027,m['edge'],.020)
    band('RI07 upper neck retaining collar',3.03,.219,.030,m['edge'],.018)
    band('RI07 lower mast contaminated joint',3.18,.244,.022,m['dirt'],.015)
    band('RI07 mast shoulder machined joint',3.83,.175,.022,m['edge'],.014)
    cylinder('RI07 silver crown mounting stem',(0,0,4.70),.055,.24,m['edge'],vertices=48)
    revolved('RI07 silver crown fork bowl',[(4.75,.06),(4.82,.12),(4.90,.18),(4.96,.16),(4.99,.10)],m['edge'])
    cylinder('RI07 silver central conductor',(0,0,5.30),.022,1.08,m['edge'],vertices=24)
    for sign in [-1,1]:
        points=[(sign*.05,0,4.82),(sign*.16,0,4.91),(sign*.20,0,5.08),(sign*.20,0,5.59)]
        for a,b in zip(points,points[1:]): beam('RI07 silver outer conductor',a,b,.032,m['edge'])
        cylinder('RI07 silver side terminal',(sign*.20,0,5.59),.034,.035,m['rubbed'],vertices=24)
    cylinder('RI07 silver central terminal',(0,0,5.835),.025,.030,m['rubbed'],vertices=24)
    return m
