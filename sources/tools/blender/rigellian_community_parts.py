"""Independently authored RI04 twin community pods and compact three-prong crown."""
import math
import bmesh
import bpy
from mathutils import Vector
from build_openfa_assets import beam,box,cylinder,material
from manufactured_frames import rounded_frame
from manufactured_vessels import vessel,profile_radius as radius
from terran_missile_parts import band,revolved

LOWER=[(0,.40),(.09,.52),(.23,.59),(.40,.61),(.78,.61),(.98,.52),(1.08,.37)]
UPPER=[(1.15,.36),(1.27,.52),(1.43,.61),(1.65,.62),(2.09,.62),(2.27,.51),(2.39,.33)]
DENTS=[(-2.10,.53,.009),(.45,1.92,.010)]


def palette():
    return dict(body=material('RI04 | aged jade shell',(.12,.29,.22),.53,.50),
        edge=material('RI04 | abraded pale alloy',(.39,.46,.42),.76,.46),
        dirt=material('RI04 | contaminated gaskets',(.045,.085,.060),.18,.83),
        dark=material('RI04 | recessed equipment',(.015,.025,.024),.38,.64),
        gold=material('RI04 | aged brass fittings',(.46,.29,.085),.73,.49),
        rubbed=material('RI04 | rubbed brass edges',(.63,.45,.18),.78,.40),
        red=material('RI04 | oxide red equipment core',(.38,.025,.015),.46,.49))


def square_fitting(label,profile,phi,z,m):
    normal=Vector((math.cos(phi),math.sin(phi),0));r=radius(profile,z);centre=normal*(r-.015);centre.z=z
    bezel=box(label+' dark retaining bezel',centre,(.133,.060,.133),m['dark'],.012);bezel.rotation_euler.z=phi-math.pi/2
    centre=normal*(r+.017);centre.z=z
    face=box(label+' square brass face',centre,(.080,.012,.080),m['gold'],.006);face.rotation_euler.z=phi-math.pi/2
    tangent=Vector((-normal.y,normal.x,0))
    for sign in [-1,1]:
        point=normal*(r+.019)+tangent*(sign*.046);point.z=z+sign*.046
        screw=cylinder(label+' captive corner screw',point,.007,.010,m['rubbed'],vertices=12)
        screw.rotation_euler=normal.to_track_quat('Z','Y').to_euler()


def build():
    m=palette();lower=vessel('RI04 lower rounded pod',LOWER,m['body'],DENTS);vessel('RI04 upper rounded pod',UPPER,m['body'],DENTS)
    cylinder('RI04 solid structural waist',(0,0,1.115),.37,.23,m['body'],vertices=64)
    band('RI04 ground contact rim',.045,.466,.040,m['edge'],.040)
    band('RI04 waist contaminated seam',1.12,.375,.025,m['dirt'],.020)
    cutter=box('Temporary lower equipment cutter',(.10,-.555,.55),(.42,.22,.78),m['dark'],.075)
    bpy.context.view_layer.objects.active=cutter
    for modifier in list(cutter.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.context.view_layer.objects.active=lower;modifier=lower.modifiers.new('Actual lower service recess','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(lower.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bm.to_mesh(lower.data);bm.free()
    box('RI04 recessed service backing',(.10,-.452,.55),(.39,.030,.73),m['dark'],.035)
    rounded_frame('RI04 curved service retaining frame',(.10,-.602,.55),.48,.81,.095,.021,m['edge'])
    cylinder('RI04 vertical red equipment core',(.10,-.482,.55),.024,.72,m['red'],vertices=32)
    for z in [.25,.43,.61,.79]:
        for x in [-.075,.275]:
            box('RI04 pale paired equipment louvre',(x,-.535,z),(.15,.15,.045),m['edge'],.006)
    for row,z in enumerate([1.68,2.02]):
        for column,offset in enumerate([-.63,0,.63]):
            square_fitting(f'RI04 upper fitting {row}-{column}',UPPER,-math.pi/2+offset,z-(.10 if column==1 else 0),m)
    for i,z in enumerate([.43,.72]): square_fitting(f'RI04 lower fitting {i}',LOWER,-math.pi/2-.68,z,m)
    # Compact stepped gold foot and stout fork differ from the taller RI01 conductor.
    revolved('RI04 crown stepped brass foundation',[(2.34,.30),(2.43,.32),(2.54,.23),(2.62,.18),(2.70,.19),(2.78,.13)],m['gold'])
    band('RI04 crown rubbed mounting lip',2.43,.325,.040,m['rubbed'],.030)
    cylinder('RI04 crown solid fork socket',(0,0,2.79),.14,.12,m['gold'],vertices=48)
    revolved('RI04 crown flared fork cradle',[(2.76,.11),(2.82,.15),(2.90,.22),(2.96,.20),(2.99,.14)],m['gold'])
    cylinder('RI04 crown central conductor',(0,0,3.17),.030,.86,m['gold'],vertices=24)
    for sign in [-1,1]:
        points=[(sign*.06,0,2.83),(sign*.20,0,2.94),(sign*.24,0,3.09),(sign*.24,0,3.35)]
        for a,b in zip(points,points[1:]): beam('RI04 crown outer conductor',a,b,.055,m['gold'])
        cylinder('RI04 crown side terminal',(sign*.24,0,3.35),.057,.050,m['rubbed'],vertices=24)
    cylinder('RI04 crown central terminal',(0,0,3.59),.033,.035,m['rubbed'],vertices=24)
    return m
