"""Independent RI14 power-generation installation; hidden machinery is not established."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,material,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel

PROFILES={
 'RI14 twin chamber lower body':[(0,.34),(.04,.40),(.10,.43),(.67,.43),(.72,.40),(.76,.33),(.87,.33),(.92,.40),(.96,.43),(1.50,.43),(1.56,.40),(1.59,.31)],
 'RI14 tapered grey connector':[(1.53,.29),(1.60,.30),(1.66,.25),(1.72,.24),(1.74,.20),(1.79,.20),(1.84,.14),(1.92,.09),(2.06,.09)],
 'RI14 bronze upper vessel':[(1.99,.075),(2.04,.11),(2.12,.18),(2.25,.25),(2.65,.27),(2.78,.28),(2.83,.25)],
 'RI14 central crown probe':[(2.78,.055),(2.91,.055),(3.00,.07),(3.05,.065),(3.26,.05),(3.36,.035),(3.40,.02)]}
PAINT={name:('bronze' if 'lower body' in name or 'bronze' in name else 'grey') for name in PROFILES}
PAINT['RI14 open upturned crown']='grey'
CENTRES={name:(0,0) for name in PAINT}
DENTS={'RI14 twin chamber lower body':(-1.7,1.20,.004),'RI14 tapered grey connector':(-1.8,1.65,.002),
 'RI14 bronze upper vessel':(-1.4,2.50,.003),'RI14 central crown probe':(-1.6,3.13,.001)}
CROWN=[(2.76,.23,.10),(2.80,.39,.32),(2.90,.52,.46),(3.00,.57,.52),(3.03,.57,.52)]


def build():
    m=dict(bronze=material('RI14 | aged bronze housing',(.29,.19,.065),.73,.54),
        grey=material('RI14 | weathered grey alloy',(.26,.32,.38),.75,.50),
        edge=material('RI14 | machined crown fittings',(.36,.43,.49),.80,.48),
        detail=material('RI14 | bronze service panels',(.27,.175,.055),.72,.56),
        dark=material('RI14 | recessed bronze joints',(.065,.044,.019),.58,.65))
    parts={name:vessel(name,profile,m[PAINT[name]],[DENTS[name]]) for name,profile in PROFILES.items()}
    annulus('RI14 open upturned crown',(0,0),CROWN,m['grey'],(0,.3,0))
    cylinder('RI14 crown floor',(0,0,2.815),.31,.070,m['edge'],vertices=96)
    for i,phi in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
        # Flared rectangular rim prongs, not separate round antennae.
        vertices=[]
        for z,inner,outer,half_width in [(2.975,.515,.58,.030),(3.23,.57,.60,.014)]:
            for radial,tangent in [(inner,-half_width),(outer,-half_width),(outer,half_width),(inner,half_width)]:
                vertices.append((radial*math.cos(phi)-tangent*math.sin(phi),radial*math.sin(phi)+tangent*math.cos(phi),z))
        mesh=bpy.data.meshes.new(f'RI14 crown prong {i} editable casting')
        mesh.from_pydata(vertices,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update()
        obj=bpy.data.objects.new(f'RI14 crown upright {i}',mesh);bpy.context.collection.objects.link(obj)
        finish(obj,obj.name,m['edge'],.003)
    cylinder('RI14 silver front conduit',(.20,-.40,.845),.027,1.65,m['edge'],vertices=32)
    body=parts['RI14 twin chamber lower body']
    for i,z in enumerate([.20,.59,1.09,1.43]):
        r=profile_radius(PROFILES['RI14 twin chamber lower body'],z);point=Vector((.20,-math.sqrt(r*r-.20**2),z))
        normal=Vector((point.x,point.y,0)).normalized();point+=normal*.010
        cast_bezel(f'RI14 conduit retaining shoe {i}',body,point,normal,.055,m['dark'])
    for i,z in enumerate([.38,1.25]):
        box(f'RI14 service panel frame {i}',(-.08,-.415,z),(.26,.045,.37),m['dark'],.005)
        box(f'RI14 service panel {i}',(-.08,-.438,z),(.22,.020,.33),m['detail'],.004)
        for j in range(3):
            box(f'RI14 service inset {i} {j}',(-.08,-.449,z+(j-1)*.085),(.15,.008,.018),m['dark'],.002)
        for j,(x,dz) in enumerate([(-.17,-.12),(.01,-.12),(-.17,.12),(.01,.12)]):
            cylinder(f'RI14 panel captive fastener {i} {j}',(x,-.451,z+dz),.006,.009,m['edge'],vertices=6,rotation=(math.pi/2,0,0))
    for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6]):
        r=profile_radius(PROFILES['RI14 bronze upper vessel'],2.45)
        normal=Vector((math.cos(phi),math.sin(phi),0));centre=normal*(r+.003)+Vector((0,0,2.45))
        panel=box(f'RI14 upper vessel alloy inset {i}',centre,(.095,.045,.23),m['edge'],.004)
        panel.rotation_euler.z=phi+math.pi/2
    return m
