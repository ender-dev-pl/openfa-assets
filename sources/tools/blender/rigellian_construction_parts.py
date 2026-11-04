"""Independent RI09 twin open platforms, raised hood and supported green equipment."""
import math
import bmesh
import bpy
from build_openfa_assets import beam,box,cylinder,material
from manufactured_annuli import annulus
from manufactured_vessels import vessel

CENTRES=[(-.85,0),(.85,0)]
ROWS=[(0,.90,.61),(.06,.95,.56),(.28,.95,.56),(.36,.88,.62)]
HOOD=[(1.12,.36),(1.18,.56),(1.28,.70),(1.36,.65),(1.43,.43),(1.47,.20)]
SLOT_ANGLES=[-2.65,-2.20,-1.75,-1.30,-.85]
DENTS=[(-1.45,.20,.006),(-1.10,.20,.006)]
PODS=[(-1.05,-.05),(-.70,.12),(.70,-.05),(1.05,.12)]


def palette():
    return dict(body=material('RI09 | worn blue grey casting',(.24,.32,.35),.72,.50),
        edge=material('RI09 | abraded blue grey rims',(.39,.46,.48),.82,.43),
        dark=material('RI09 | recessed mechanisms',(.015,.024,.027),.40,.65),
        green=material('RI09 | aged green equipment enamel',(.10,.25,.18),.50,.55),
        gold=material('RI09 | aged brass fasteners',(.40,.27,.07),.75,.50),
        red=material('RI09 | oxide red column inset',(.35,.025,.015),.45,.53),
        pale=material('RI09 | rubbed pale structural alloy',(.48,.55,.54),.75,.45))


def tidy(obj):
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    for face in bm.faces:
        zs=[v.co.z for v in face.verts];face.smooth=max(zs)-min(zs)>1e-6
    for edge in bm.edges:
        if edge.is_manifold and edge.calc_face_angle()>.65: edge.smooth=False
    bm.to_mesh(obj.data);bm.free()


def subtract(obj,cutter):
    bpy.context.view_layer.objects.active=cutter
    for modifier in list(cutter.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.context.view_layer.objects.active=obj;modifier=obj.modifiers.new('Actual machined recess','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)


def build():
    m=palette()
    for index,(cx,cy) in enumerate(CENTRES):
        ring=annulus(f'RI09 open annular platform {index}',(cx,cy),ROWS,m['body'],DENTS[index])
        for n,phi in enumerate(SLOT_ANGLES):
            cutter=box('Temporary outer casting channel',(cx+.94*math.cos(phi),cy+.94*math.sin(phi),.18),(.035,.080,.18),m['dark'],.006)
            cutter.rotation_euler.z=phi-math.pi/2;subtract(ring,cutter)
            backing=box(f'RI09 ring {index} channel {n} backing',(cx+.902*math.cos(phi),cy+.902*math.sin(phi),.18),(.030,.012,.16),m['dark'],.002)
            backing.rotation_euler.z=phi-math.pi/2
        tidy(ring)
    box('RI09 front cast joining bridge',(0,-.55,.22),(.54,.32,.26),m['body'],.035)
    box('RI09 longitudinal cast support spine',(0,-.10,.18),(.40,.95,.25),m['body'],.030)
    box('RI09 central raised support column',(0,.12,.65),(.30,.32,1.10),m['body'],.025)
    box('RI09 column red service inset',(0,-.045,.73),(.035,.018,.50),m['red'],.004)
    hood=vessel('RI09 raised circular machinery hood',HOOD,m['body'],[(.50,1.32,.005)]);hood.location.y=.32
    cutter=cylinder('Temporary actual hood inspection recess',(0,.32,1.44),.18,.16,m['dark'],vertices=64)
    subtract(hood,cutter);tidy(hood)
    cylinder('RI09 hood recessed inspection floor',(0,.32,1.365),.17,.018,m['dark'],vertices=64)
    for sign in [-1,1]:
        beam('RI09 rear portal upright',(sign*1.08,.55,.27),(sign*1.08,.55,1.23),.030,m['pale'])
        beam('RI09 rear second portal upright',(sign*1.22,.55,.27),(sign*1.22,.55,1.23),.030,m['pale'])
        beam('RI09 rear portal top tie',(sign*1.08,.55,1.21),(sign*1.22,.55,1.21),.030,m['pale'])
        beam('RI09 rear hood support arm',(sign*.45,.55,1.21),(sign*1.08,.55,1.21),.030,m['pale'])
    for i,(x,y) in enumerate(PODS):
        profile=[(.05,.060),(.12,.075),(.55,.075),(.67,.050),(.72,.045)]
        pod=vessel(f'RI09 internal green equipment post {i}',profile,m['green'],[(-.4,.34,.004)])
        pod.location=(x,y,0)
        beam(f'RI09 equipment post {i} mounting runner',(x,y,.12),(x,.64,.12),.025,m['dark'])
        cylinder(f'RI09 equipment post {i} pale head',(x,y,.68),.080,.035,m['pale'],vertices=32)
        cylinder(f'RI09 equipment post {i} brass side fastener',(x,y-.073,.45),.011,.012,m['gold'],vertices=16,rotation=(math.pi/2,0,0))
    for sign in [-1,1]: cylinder('RI09 hood brass captive fastener',(sign*.43,.27,1.425),.022,.030,m['gold'],vertices=24)
    box('RI09 hood front brass identification fitting',(0,-.358,1.30),(.075,.035,.050),m['gold'],.006)
    cylinder('RI09 front bridge circular inspection cover',(0,-.55,.357),.105,.030,m['edge'],vertices=48)
    return m
