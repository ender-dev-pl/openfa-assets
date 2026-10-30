"""Independent RI06 stacked saucers, actual roof wells and mast construction."""
import math
import bmesh
import bpy
from mathutils import Vector
from build_openfa_assets import beam,box,cylinder,material
from build_shield_equipment import shell
from manufactured_vessels import vessel,profile_radius as radius
from terran_missile_parts import band,revolved

LEVELS=[0,1.00,2.00]
WELL=(-.63,-.30)
MAST_OFFSET=.20
DISC=[(0,.52),(.07,.85),(.16,1.05),(.24,1.10),(.31,1.07),(.43,.86),(.54,.53),(.58,.30)]
MAST=[(2.62,.21),(2.72,.24),(2.85,.22),(3.34,.18),(3.50,.15),(3.65,.11),(3.73,.08)]
DENTS=[(-2.10,.24,.008),(.60,1.24,.008),(-.80,2.24,.009)]


def palette():
    return dict(body=material('RI06 | aged jade shell',(.12,.29,.22),.53,.50),
        edge=material('RI06 | abraded pale alloy',(.39,.46,.42),.76,.46),
        dirt=material('RI06 | contaminated gaskets',(.045,.085,.060),.18,.83),
        dark=material('RI06 | deep equipment wells',(.015,.025,.024),.38,.64),
        gold=material('RI06 | aged brass conductors',(.46,.29,.085),.73,.49),
        rubbed=material('RI06 | rubbed brass terminals',(.63,.45,.18),.78,.40))


def disc_profile(start): return [(z+start,r) for z,r in DISC]


def roof_well(obj,start,index,m):
    cylinder('Temporary actual roof well cutter',(*WELL,start+.47),.17,.60,m['dark'],vertices=64)
    cutter=bpy.context.object
    for modifier in list(cutter.modifiers): cutter.modifiers.remove(modifier)
    bpy.context.view_layer.objects.active=obj;modifier=obj.modifiers.new('Actual recessed roof well','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    for face in bm.faces:
        zs=[v.co.z for v in face.verts];face.smooth=max(zs)-min(zs)>1e-6
    for edge in bm.edges:
        if edge.is_manifold and edge.calc_face_angle()>.65: edge.smooth=False
    bm.to_mesh(obj.data);bm.free()
    liner=shell(f'RI06 level {index} embedded well sleeve',[(start+.15,.177),(start+.41,.177)],0,math.tau,
        dict(shell=m['edge'],dark=m['dark']),64,.022)
    liner.rotation_euler.x=math.pi/2;liner.location=(*WELL,0)
    cylinder(f'RI06 level {index} recessed well floor',(*WELL,start+.17),.160,.040,m['dark'],vertices=64)
    for y in [WELL[1]-.045,WELL[1]+.045]:
        box(f'RI06 level {index} well cooling fin',(WELL[0],y,start+.20),(.18,.018,.030),m['gold'],.003)


def rim_fitting(start,index,phi,m):
    normal=Vector((math.cos(phi),math.sin(phi),0));r=radius(DISC,.23);z=start+.23
    centre=normal*(r-.010);centre.z=z
    bezel=box(f'RI06 level {index} rim fitting bezel',centre,(.095,.030,.095),m['dark'],.008)
    bezel.rotation_euler.z=phi-math.pi/2
    centre=normal*(r+.008);centre.z=z
    face=box(f'RI06 level {index} square brass rim face',centre,(.060,.010,.060),m['gold'],.004)
    face.rotation_euler.z=phi-math.pi/2


def build():
    m=palette()
    vessel('RI06 solid interlevel structural column',[(.02,.30),(2.57,.30)],m['body'],[])
    for index,start in enumerate(LEVELS):
        disc=vessel(f'RI06 broad saucer level {index}',disc_profile(start),m['body'],DENTS)
        roof_well(disc,start,index,m)
        band(f'RI06 level {index} perimeter machined seam',start+.245,1.104,.027,m['edge'],.020)
        for phi in [-math.pi/2,-.30]: rim_fitting(start,index,phi,m)
    vessel('RI06 tapered upper mast',MAST,m['body'],[])
    cylinder('RI06 solid exposed brass mast neck',(0,0,2.50),.18,.42,m['gold'],vertices=64)
    for i in range(4):
        phi=math.pi/4+i*math.pi/2
        beam('RI06 pale neck retaining strut',(.22*math.cos(phi),.22*math.sin(phi),2.30),
            (.22*math.cos(phi),.22*math.sin(phi),2.68),.018,m['edge'])
    band('RI06 lower mast neck retaining collar',2.31,.240,.025,m['edge'],.025)
    band('RI06 upper mast neck retaining collar',2.65,.235,.040,m['body'],.020)
    band('RI06 lower mast contaminated groove',2.80,.231,.032,m['dirt'],.016)
    band('RI06 middle mast machined joint',3.12,.205,.026,m['edge'],.014)
    cylinder('RI06 crown solid mounting stem',(0,0,3.755),.070,.18,m['gold'],vertices=48)
    revolved('RI06 crown compact fork bowl',[(3.78,.07),(3.85,.13),(3.93,.18),(3.99,.16),(4.02,.10)],m['gold'])
    cylinder('RI06 crown central conductor',(0,0,4.25),.023,1.0,m['gold'],vertices=24)
    for sign in [-1,1]:
        points=[(sign*.05,0,3.85),(sign*.15,0,3.94),(sign*.18,0,4.09),(sign*.18,0,4.49)]
        for a,b in zip(points,points[1:]): beam('RI06 crown outer conductor',a,b,.036,m['gold'])
        cylinder('RI06 crown side terminal',(sign*.18,0,4.49),.038,.040,m['rubbed'],vertices=24)
    cylinder('RI06 crown central terminal',(0,0,4.75),.025,.030,m['rubbed'],vertices=24)
    prefixes=('RI06 tapered upper mast','RI06 solid exposed brass mast neck','RI06 pale neck retaining strut',
        'RI06 lower mast neck retaining collar','RI06 upper mast neck retaining collar','RI06 lower mast contaminated groove',
        'RI06 middle mast machined joint','RI06 crown')
    for obj in bpy.context.collection.objects:
        if obj.name.startswith(prefixes): obj.location.z+=MAST_OFFSET
    return m
