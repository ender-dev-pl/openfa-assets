"""Independent RI05 flared pedestal, vented head and narrow-root gold fork."""
import math
import bmesh
import bpy
from mathutils import Vector
from build_openfa_assets import beam,box,cylinder,finish,material
from manufactured_frames import rounded_frame
from manufactured_vessels import vessel,profile_radius as radius
from terran_missile_parts import band,revolved

BASE=[(0,.68),(.08,.85),(.18,.81),(.40,.60),(.72,.39),(1.00,.30),(1.15,.29)]
NECK=[(1.08,.28),(1.30,.27),(1.46,.30),(1.58,.36)]
HEAD=[(1.48,.35),(1.60,.50),(1.75,.54),(2.35,.54),(2.52,.42),(2.60,.20)]
VENTS=[(-math.pi/2-.95,.11),(-math.pi/2,.18),(-math.pi/2+.95,.11)]
DENTS=[(-2.10,.48,.010),(.60,2.28,.008)]


def palette():
    return dict(body=material('RI05 | aged jade shell',(.12,.29,.22),.53,.50),
        edge=material('RI05 | abraded pale alloy',(.39,.46,.42),.76,.46),
        dirt=material('RI05 | contaminated gaskets',(.045,.085,.060),.18,.83),
        dark=material('RI05 | recessed equipment',(.015,.025,.024),.38,.64),
        gold=material('RI05 | aged brass conductors',(.46,.29,.085),.73,.49),
        rubbed=material('RI05 | rubbed brass terminals',(.63,.45,.18),.78,.40),
        inset=material('RI05 | blue green inspection inset',(.075,.16,.155),.48,.51))


def cut_vents(head,m):
    for index,(phi,width) in enumerate(VENTS):
        normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-normal.y,normal.x,0))
        centre=normal*.52;centre.z=2.05
        cutter=box('Temporary true head vent cutter',centre,(width,.20,.62),m['dark'],.025)
        cutter.rotation_euler.z=phi-math.pi/2;bpy.context.view_layer.objects.active=cutter
        for modifier in list(cutter.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.context.view_layer.objects.active=head;modifier=head.modifiers.new('Actual head grille opening','BOOLEAN')
        modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
        centre=normal*.423;centre.z=2.05
        backing=box(f'RI05 vent {index} recessed backing',centre,(width*.94,.018,.60),m['dark'],.010)
        backing.rotation_euler.z=phi-math.pi/2
        frame=rounded_frame(f'RI05 vent {index} continuous retaining frame',(0,-.542,2.05),width+.040,.67,.035,.012,m['edge'])
        frame.rotation_euler.z=phi+math.pi/2
        for row,z in enumerate([1.82,1.935,2.05,2.165,2.28]):
            for column in [-1,1] if index==1 else [0]:
                centre=normal*.49+tangent*(column*.045);centre.z=z
                louvre=box(f'RI05 vent {index} paired cooling louvre',centre,(.060 if index==1 else .085,.13,.028),m['edge'],.004)
                louvre.rotation_euler.z=phi-math.pi/2
    bm=bmesh.new();bm.from_mesh(head.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bm.to_mesh(head.data);bm.free()


def build():
    m=palette();base=vessel('RI05 flared mounting pedestal',BASE,m['body'],DENTS)
    vessel('RI05 narrow structural neck',NECK,m['body'],DENTS)
    head=vessel('RI05 rounded vented head',HEAD,m['body'],DENTS);cut_vents(head,m)
    band('RI05 ground contact rim',.065,.825,.035,m['edge'],.030)
    band('RI05 lower neck contaminated seam',1.12,.295,.022,m['dirt'],.015)
    band('RI05 neck machined collar',1.28,.279,.030,m['edge'],.018)
    # Visible low circular fitting: exact internal purpose is not established.
    phi=-.80;z=.36;normal=Vector((math.cos(phi),math.sin(phi),.95)).normalized()
    centre=Vector((radius(BASE,z)*math.cos(phi),radius(BASE,z)*math.sin(phi),z))-normal*.012
    face=cylinder('RI05 pedestal circular inspection face',centre,.145,.060,m['inset'],vertices=64)
    face.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    bpy.context.view_layer.objects.active=face
    for modifier in list(face.modifiers):
        if modifier.type=='BEVEL': modifier.width=.006
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    cutter=cylinder('Temporary actual inspection well cutter',centre+normal*.04,.065,.20,m['dark'],vertices=64)
    cutter.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    for modifier in list(cutter.modifiers): cutter.modifiers.remove(modifier)
    for target in [face,base]:
        bpy.context.view_layer.objects.active=target;modifier=target.modifiers.new('Actual circular inspection well','BOOLEAN')
        modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(target.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bm.to_mesh(target.data);bm.free()
    bpy.data.objects.remove(cutter,do_unlink=True)
    floor=cylinder('RI05 recessed circular inspection floor',centre-normal*.057,.061,.016,m['dark'],vertices=64)
    floor.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    bpy.ops.mesh.primitive_torus_add(major_radius=.142,minor_radius=.014,major_segments=64,minor_segments=12,location=centre+normal*.018)
    ring=bpy.context.object;ring.rotation_euler=normal.to_track_quat('Z','Y').to_euler();finish(ring,'RI05 pedestal worn retaining ring',m['edge'],0)
    for polygon in ring.data.polygons: polygon.use_smooth=True
    # A narrow stem and fork bowl are visible; no broad stepped RI04 crown foot is reused.
    cylinder('RI05 crown solid mounting stem',(0,0,2.665),.090,.21,m['gold'],vertices=48)
    revolved('RI05 crown flared fork bowl',[(2.72,.09),(2.79,.16),(2.87,.205),(2.93,.19),(2.96,.13)],m['gold'])
    cylinder('RI05 crown central conductor',(0,0,3.16),.026,.94,m['gold'],vertices=24)
    for sign in [-1,1]:
        points=[(sign*.06,0,2.79),(sign*.18,0,2.88),(sign*.21,0,3.04),(sign*.21,0,3.39)]
        for a,b in zip(points,points[1:]): beam('RI05 crown outer conductor',a,b,.045,m['gold'])
        cylinder('RI05 crown side terminal',(sign*.21,0,3.39),.047,.045,m['rubbed'],vertices=24)
    cylinder('RI05 crown central terminal',(0,0,3.625),.029,.030,m['rubbed'],vertices=24)
    return m
