"""Independent RI08 drum, flared data housing, twin supports and silver fork."""
import math
import bmesh
import bpy
from mathutils import Vector
from build_openfa_assets import beam,box,cylinder,finish,material
from manufactured_vessels import vessel,profile_radius as radius
from manufactured_surface_mounts import cast_bezel
from terran_missile_parts import band,revolved

DRUM=[(0,.35),(.10,.50),(.25,.58),(.80,.58),(.96,.49),(1.06,.36)]
NECK=[(.96,.29),(1.30,.29)]
MIDDLE=[(1.23,.35),(1.34,.56),(1.48,.77),(1.62,.90),(1.74,.87),(1.89,.65),(2.10,.39),(2.22,.34)]
HEAD=[(2.10,.34),(2.20,.38),(2.30,.44),(2.65,.44),(2.82,.35),(2.90,.22)]
SLOTS=[-.78,-.60,-.42]
DENTS=[(-2.40,.55,.008),(.60,1.62,.009),(.80,2.50,.006)]


def palette():
    return dict(body=material('RI08 | aged jade shell',(.12,.29,.22),.53,.50),
        edge=material('RI08 | abraded pale alloy',(.39,.46,.42),.76,.46),
        dark=material('RI08 | recessed equipment',(.015,.025,.024),.38,.64),
        dirt=material('RI08 | contaminated gaskets',(.045,.085,.060),.18,.83),
        gold=material('RI08 | aged brass fittings',(.46,.29,.085),.73,.49),
        rubbed=material('RI08 | rubbed brass edges',(.63,.45,.18),.78,.40),
        panel=material('RI08 | faded jade side-module casing',(.15,.30,.24),.46,.57))


def square_fitting(label,profile,phi,z,m):
    normal=Vector((math.cos(phi),math.sin(phi),0));r=radius(profile,z);centre=normal*(r-.012);centre.z=z
    bezel=box(label+' retaining bezel',centre,(.102,.040,.102),m['dark'],.009);bezel.rotation_euler.z=phi-math.pi/2
    centre=normal*(r+.012);centre.z=z
    face=box(label+' inset brass face',centre,(.065,.014,.065),m['gold'],.005);face.rotation_euler.z=phi-math.pi/2


def lower_slots(drum,m):
    for i,phi in enumerate(SLOTS):
        normal=Vector((math.cos(phi),math.sin(phi),0));centre=normal*.575;centre.z=.49
        cutter=box('Temporary actual drum intake cutter',centre,(.055,.16,.50),m['dark'],.012)
        cutter.rotation_euler.z=phi-math.pi/2;bpy.context.view_layer.objects.active=cutter
        for modifier in list(cutter.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.context.view_layer.objects.active=drum;modifier=drum.modifiers.new('Actual lower intake channel','BOOLEAN')
        modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
        centre=normal*.497;centre.z=.49
        backing=box(f'RI08 lower slot {i} recessed backing',centre,(.052,.012,.475),m['dark'],.004)
        backing.rotation_euler.z=phi-math.pi/2
    bm=bmesh.new();bm.from_mesh(drum.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    for face in bm.faces:
        zs=[v.co.z for v in face.verts];face.smooth=max(zs)-min(zs)>1e-6
    for edge in bm.edges:
        if edge.is_manifold and edge.calc_face_angle()>.65: edge.smooth=False
    bm.to_mesh(drum.data);bm.free()


def build():
    m=palette();drum=vessel('RI08 lower intake drum',DRUM,m['body'],DENTS);lower_slots(drum,m)
    vessel('RI08 solid connecting neck',NECK,m['body'],[])
    middle=vessel('RI08 flared middle housing',MIDDLE,m['body'],DENTS)
    vessel('RI08 rounded upper head',HEAD,m['body'],DENTS)
    band('RI08 ground machined rim',.12,.515,.026,m['edge'],.020)
    band('RI08 neck contaminated gasket',1.17,.297,.022,m['dirt'],.015)
    band('RI08 middle perimeter seam',1.62,.904,.026,m['edge'],.018)
    band('RI08 head lower machined joint',2.16,.376,.040,m['edge'],.020)
    for i,(phi,z) in enumerate([(-math.pi/2-.45,.62),(-math.pi/2+.05,.62),(-math.pi/2+.05,.35)]):
        square_fitting(f'RI08 lower fitting {i}',DRUM,phi,z,m)
    for i,phi in enumerate([-math.pi/2-.55,-math.pi/2,-math.pi/2+.55]):
        square_fitting(f'RI08 upper collar fitting {i}',MIDDLE,phi,2.08,m)
    phi=-.90;z=1.82;normal=Vector((math.cos(phi),math.sin(phi),1.4666667)).normalized()
    point=Vector((radius(MIDDLE,z)*math.cos(phi),radius(MIDDLE,z)*math.sin(phi),z))
    cast_bezel('RI08 large circular pressure bezel',middle,point,normal,.195,m['dark'])
    face=cylinder('RI08 large circular brass pressure face',point+normal*.024,.155,.015,m['gold'],vertices=64)
    face.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    bpy.ops.mesh.primitive_torus_add(major_radius=.172,minor_radius=.014,major_segments=64,minor_segments=12,location=point+normal*.024)
    ring=bpy.context.object;ring.rotation_euler=normal.to_track_quat('Z','Y').to_euler();finish(ring,'RI08 large circular rubbed retaining ring',m['rubbed'],0)
    for polygon in ring.data.polygons: polygon.use_smooth=True
    for phi in [-math.pi/2-.30,-math.pi/2+.30]:
        for z in [2.43,2.64]:
            normal=Vector((math.cos(phi),math.sin(phi),0));point=normal*(radius(HEAD,z)-.005);point.z=z
            screw=cylinder('RI08 head captive dark fastener',point,.016,.018,m['dark'],vertices=16)
            screw.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    for sign in [-1,1]:
        beam('RI08 twin upper support',(sign*.10,0,2.84),(sign*.10,0,4.12),.025,m['edge'])
    box('RI08 support-mounted side equipment casing',(.22,0,3.35),(.24,.16,.28),m['panel'],.025)
    box('RI08 side-module dark front inset',(.22,-.084,3.35),(.10,.012,.16),m['dark'],.008)
    revolved('RI08 silver crown fork bowl',[(4.00,.08),(4.07,.15),(4.16,.19),(4.22,.15),(4.25,.09)],m['edge'])
    cylinder('RI08 silver central conductor',(0,0,4.69),.020,.90,m['edge'],vertices=24)
    for sign in [-1,1]:
        points=[(sign*.05,0,4.12),(sign*.17,0,4.23),(sign*.21,0,4.39),(sign*.21,0,4.83)]
        for a,b in zip(points,points[1:]): beam('RI08 silver outer conductor',a,b,.028,m['edge'])
        cylinder('RI08 silver side terminal',(sign*.21,0,4.83),.030,.035,m['edge'],vertices=24)
    cylinder('RI08 silver central terminal',(0,0,5.14),.023,.030,m['edge'],vertices=24)
    return m
