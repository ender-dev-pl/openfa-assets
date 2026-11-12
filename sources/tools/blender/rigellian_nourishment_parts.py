"""Independent RI03 stacked process vessels; unseen equipment is authored inference."""
import math
import bmesh
import bpy
from mathutils import Vector
from build_openfa_assets import beam,box,cylinder,finish,material
from terran_missile_parts import band,revolved

BASE=[(0,.57),(.07,.70),(.17,.68),(.32,.48),(.53,.30),(.77,.26),(.94,.27)]
MODULE_STARTS=[1.00,2.10,3.20]
DENTS=[(-2.10,1.41,.008),(.45,2.60,.010),(-.85,3.66,.008)]


def palette():
    return dict(body=material('RI03 | aged jade coating',(.12,.29,.22),.53,.50),
        edge=material('RI03 | abraded pale alloy',(.39,.46,.42),.76,.46),
        dirt=material('RI03 | contaminated neck gaskets',(.045,.085,.060),.18,.83),
        dark=material('RI03 | recessed service equipment',(.015,.025,.024),.38,.64),
        gold=material('RI03 | aged brass necks',(.46,.29,.085),.73,.49),
        rubbed=material('RI03 | rubbed brass retaining edges',(.63,.45,.18),.78,.40))


def module_profile(start):
    return [(start+z,r) for z,r in [(0,.29),(.07,.41),(.19,.48),(.30,.49),(.62,.49),(.77,.44),(.87,.34),(.90,.28)]]


def radius(profile,z):
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(profile,profile[1:]) if za<=z<=zb)


def vessel(name,profile,m):
    heights=[profile[0][0]]
    for (za,_),(zb,_) in zip(profile,profile[1:]):
        steps=max(1,math.ceil((zb-za)/.03));heights += [za+(zb-za)*i/steps for i in range(1,steps+1)]
    count=128;vertices=[]
    for z in heights:
        for i in range(count):
            phi=i*math.tau/count
            dent=sum(depth*math.exp(-2*((math.atan2(math.sin(phi-angle),math.cos(phi-angle))/.11)**2+((z-height)/.09)**2))
                for angle,height,depth in DENTS)
            r=radius(profile,z)-dent;vertices.append((r*math.cos(phi),r*math.sin(phi),z))
    faces=[tuple(reversed(range(count)))]
    for row in range(len(heights)-1):
        for i in range(count):
            j=(i+1)%count;faces.append((row*count+i,row*count+j,(row+1)*count+j,(row+1)*count+i))
    faces.append(tuple((len(heights)-1)*count+i for i in range(count)))
    mesh=bpy.data.meshes.new(name+' editable dented shell');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,m['body'],0)
    for face in mesh.polygons: face.use_smooth=len(face.vertices)==4
    return obj


def carve_service_pocket(obj,start,m,index):
    # Hidden depth/closure construction is inferred; visible vertical fittings are source-backed.
    centre=(.08,-.475,start+.45)
    cutter=box('Temporary service pocket cutter',centre,(.16,.18,.48),m['dark'],.055)
    bpy.context.view_layer.objects.active=cutter
    for modifier in list(cutter.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.context.view_layer.objects.active=obj
    modifier=obj.modifiers.new('Actual rounded service recess','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bm.to_mesh(obj.data);bm.free()
    box(f'RI03 vessel {index} recessed service backing',(.08,-.386,start+.45),(.145,.024,.445),m['dark'],.020)
    rounded_return(start,m['edge'])
    for z in [start+.32,start+.45,start+.58]:
        box('RI03 recessed service cooling louvre',(.08,-.406,z),(.12,.025,.025),m['edge'],.003)


def rounded_return(start,surface):
    path=[]
    for x,z,angle in [(.125,start+.615,0),(.035,start+.615,math.pi/2),
                       (.035,start+.285,math.pi),(.125,start+.285,3*math.pi/2)]:
        for i in range(7):
            phi=angle+i*math.pi/12;path.append(Vector((x+.06*math.cos(phi),-.481,z+.06*math.sin(phi))))
    vertices=[];count=16
    for i,point in enumerate(path):
        tangent=(path[(i+1)%len(path)]-path[(i-1)%len(path)]).normalized();normal=Vector((tangent.z,0,-tangent.x))
        for n in range(count):
            phi=n*math.tau/count;vertices.append(point+.018*(Vector((0,1,0))*math.cos(phi)+normal*math.sin(phi)))
    faces=[]
    for i in range(len(path)):
        for n in range(count):
            following=(i+1)%len(path);j=(n+1)%count
            faces.append((i*count+n,i*count+j,following*count+j,following*count+n))
    mesh=bpy.data.meshes.new('Continuous rounded service return');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('RI03 continuous rounded pocket return',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,surface,0)
    for face in mesh.polygons: face.use_smooth=True


def build():
    m=palette();vessel('RI03 flared mounting pedestal',BASE,m)
    band('RI03 ground mounting rim',.075,.704,.060,m['edge'],.045)
    # Solid necks overlap vessel end caps; rings preserve a visible manufactured seam.
    for i,(bottom,top) in enumerate([(.83,1.07),(1.82,2.17),(2.92,3.27)]):
        cylinder(f'RI03 solid brass interstage neck {i}',(0,0,(bottom+top)/2),.285,top-bottom,m['gold'],vertices=64)
        for z in [bottom+.045,top-.045]: band('RI03 interstage retaining ring',z,.291,.025,m['rubbed'],.020)
        band('RI03 interstage contaminated gasket',top-.025,.287,.018,m['dirt'],.016)
    for i,start in enumerate(MODULE_STARTS):
        body=vessel(f'RI03 rounded vessel {i}',module_profile(start),m);carve_service_pocket(body,start,m,i)
    # Continuous narrow visible service spine: hidden supports are deliberate inference.
    for z1,z2 in [(.20,.65),(.65,1.30),(1.30,2.40),(2.40,3.50),(3.50,3.95)]:
        beam('RI03 continuous pale service spine',(-.14,-.48,z1),(-.14,-.48,z2),.025,m['edge'])
    for start in MODULE_STARTS:
        beam('RI03 spine mounting standoff',(-.14,-.43,start+.45),(-.14,-.48,start+.45),.038,m['edge'])
        for z in [start+.30,start+.60]:
            cylinder('RI03 rear inferred service closure',(0,.485,z),.042,.030,m['gold'],vertices=24,rotation=(math.pi/2,0,0))
    # The source has a low front gold fitting on the foot.
    cylinder('RI03 pedestal brass inspection closure',(.12,-.675,.17),.075,.040,m['gold'],vertices=48,rotation=(math.pi/2,0,0))
    return m
