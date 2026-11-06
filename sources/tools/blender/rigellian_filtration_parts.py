"""Independent RI02 construction with exportable wear materials and real dents."""
import math

import bmesh
import bpy
from mathutils import Vector
from build_openfa_assets import beam,box,cylinder,finish,material
from terran_missile_parts import band

BODY=[(0,.64),(.08,.73),(.20,.79),(.42,.82),(1.12,.82),(1.32,.77),(1.50,.65),(1.64,.39),(1.70,.32)]
TOWER=[(1.60,.32),(1.80,.35),(2.12,.34),(2.31,.29),(2.43,.22),(2.48,.11)]
DENTS=[(-2.02,.43,.010,.10,.07),(-.50,1.13,.008,.12,.09),(1.14,.72,.012,.16,.10)]


def palette():
    return dict(body=material('RI02 | aged jade shell',(.12,.29,.22),.53,.49),
        faded=material('RI02 | faded jade coating',(.133,.305,.235),.45,.58),
        dirt=material('RI02 | joint contamination',(.075,.13,.10),.18,.86),
        stain=material('RI02 | brown handling stains',(.105,.23,.16),.25,.72),
        edge=material('RI02 | abraded pale alloy',(.39,.46,.42),.76,.49),
        dark=material('RI02 | recessed equipment',(.015,.025,.024),.38,.65),
        gold=material('RI02 | aged brass fittings',(.46,.29,.085),.73,.48),
        gold_wear=material('RI02 | rubbed brass edges',(.63,.45,.18),.78,.39))


def radius(profile,z):
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(profile,profile[1:]) if za<=z<=zb)


def dent_depth(phi,z):
    return sum(depth*math.exp(-((math.atan2(math.sin(phi-angle),math.cos(phi-angle))/width)**2+((z-height)/spread)**2)*2)
        for angle,height,depth,width,spread in DENTS)


def worn_shell(name,profile,m,dented=True):
    heights=[profile[0][0]]
    for (za,_),(zb,_) in zip(profile,profile[1:]):
        count=max(1,math.ceil((zb-za)/.035))
        heights += [za+(zb-za)*i/count for i in range(1,count+1)]
    count=128;vertices=[]
    for z in heights:
        for i in range(count):
            phi=i*math.tau/count;r=radius(profile,z)-(dent_depth(phi,z) if dented else 0)
            vertices.append((r*math.cos(phi),r*math.sin(phi),z))
    faces=[tuple(reversed(range(count)))];indices=[2]
    for row in range(len(heights)-1):
        z=(heights[row]+heights[row+1])/2
        for i in range(count):
            following=(i+1)%count;phi=(i+.5)*math.tau/count
            faces.append((row*count+i,row*count+following,(row+1)*count+following,(row+1)*count+i))
            # Coherent localized stains and seam dirt, not a uniform random speckle.
            delta=lambda angle: math.atan2(math.sin(phi-angle),math.cos(phi-angle))
            streak=math.exp(-(delta(-1.18)/.075)**2)*math.exp(-((z-.53)/.26)**2)
            stain=streak>.22
            seam=min(abs(z-joint) for joint in [profile[0][0]+.05,profile[-1][0]-.05,.21,1.32,1.80,2.31])<.025
            dirt=seam and (abs(delta(-2.1))<.14+.025*math.sin(z*51) or abs(delta(.5))<.09)
            fade=math.exp(-(delta(.8)/.35)**2-((z-.8)/.24)**2)>.4
            index=2 if dirt else 3 if stain else 1 if fade else 0
            indices.append(index)
    faces.append(tuple((len(heights)-1)*count+i for i in range(count)));indices.append(0)
    mesh=bpy.data.meshes.new(name+' editable dented surface');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    for key in ['body','faded','dirt','stain']: mesh.materials.append(m[key])
    for face,index in zip(mesh.polygons,indices): face.material_index=index;face.use_smooth=len(face.vertices)==4
    obj['wear']='Authored shallow geometric dents and localized face materials; no legacy pixels or Blender-only textures'
    return obj


def torus(name,position,normal,major,minor,surface):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=48,minor_segments=12,location=position)
    obj=bpy.context.object;obj.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler()
    finish(obj,name,surface,0)
    for face in obj.data.polygons: face.use_smooth=True
    return obj


def port(name,phi,z,r,m,profile=BODY):
    normal=Vector((math.cos(phi),math.sin(phi),0));distance=radius(profile,z)-dent_depth(phi,z)
    centre=normal*(distance-.012);centre.z=z
    cylinder_obj=cylinder(name+' brass pressure face',centre,r,.050,m['gold'],vertices=48)
    cylinder_obj.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    torus(name+' abraded retaining rim',centre+normal*.012,normal,r*.94,.012,m['gold_wear'])
    # Dull lower ring and asymmetric screw pair are authored mechanical detail.
    for sign in [-1,1]:
        tangent=Vector((-normal.y,normal.x,0));point=centre+normal*.027+tangent*(sign*r*.65)
        fastener=cylinder(name+' captive screw',point,.010,.009,m['dark'],vertices=12)
        fastener.rotation_euler=normal.to_track_quat('Z','Y').to_euler()


def build():
    m=palette();body=worn_shell('RI02 rounded filtration pressure body',BODY,m)
    body.data.materials.append(m['dark'])
    for i in range(8):
        phi=-math.pi/2+(i-3.5)*.13;normal=Vector((math.cos(phi),math.sin(phi),0))
        centre=normal*.79;centre.z=.23
        cutter=box('Temporary true intake cutter',centre,(.050,.14,.18),m['dark'],0)
        cutter.rotation_euler.z=phi-math.pi/2
        bpy.context.view_layer.objects.active=body
        modifier=body.modifiers.new('Actual recessed lower intake','BOOLEAN')
        modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
        centre=normal*.720;centre.z=.23
        backing=box('RI02 recessed intake backing',centre,(.049,.012,.175),m['dark'],.001)
        backing.rotation_euler.z=phi-math.pi/2
    phi=-.55;normal=Vector((math.cos(phi),math.sin(phi),0));centre=normal*.80;centre.z=.78
    cutter=box('Temporary true side channel cutter',centre,(.090,.16,1.03),m['dark'],0)
    cutter.rotation_euler.z=phi-math.pi/2;bpy.context.view_layer.objects.active=body
    modifier=body.modifiers.new('Actual recessed side service channel','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
    centre=normal*.720;centre.z=.78
    backing=box('RI02 recessed side channel backing',centre,(.089,.012,1.025),m['dark'],.001)
    backing.rotation_euler.z=phi-math.pi/2
    bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bm.to_mesh(body.data);bm.free()
    worn_shell('RI02 capped upper tower',TOWER,m,False)
    band('RI02 ground mounting rim',.065,.737,.075,m['edge'],.04)
    band('RI02 shoulder contaminated gasket',1.65,.377,.038,m['dirt'],.028)
    band('RI02 tower lower machined collar',1.79,.355,.032,m['edge'],.025)
    band('RI02 tower cap worn rim',2.315,.294,.025,m['edge'],.022)
    cylinder('RI02 tower terminal cap',(0,0,2.475),.115,.035,m['faded'],vertices=64)
    for row,z in enumerate([.53,.85,1.17]):
        for column,phi in enumerate([-math.pi/2-.30,-math.pi/2+.30]):
            port(f'RI02 front port {row}-{column}',phi,z,.085,m)
    port('RI02 upper tower fitting',-math.pi/2,1.995,.075,m,TOWER)
    # Lower slots are open spaces between load-bearing ribs, with an inset backing.
    for i in range(9):
        phi=-math.pi/2+(i-4)*.13;normal=Vector((math.cos(phi),math.sin(phi),0))
        a=normal*(radius(BODY,.10)+.003);a.z=.10
        b=normal*(radius(BODY,.33)+.003);b.z=.33
        beam('RI02 lower intake structural rib',a,b,.018,m['edge'])
    # Reference-backed tall side channel, with a sunk channel floor and visible rails.
    phi=-.55;normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-normal.y,normal.x,0))
    for sign in [-1,1]:
        points=[]
        for z in [.24,.42,1.12,1.30]:
            p=normal*(radius(BODY,z)+.002)+tangent*(sign*.07);p.z=z;points.append(p)
        for a,b in zip(points,points[1:]): beam('RI02 side channel retaining rail',a,b,.022,m['edge'])
    points=[]
    for i in range(13):
        angle=i*math.pi/12;z=1.30+.07*math.sin(angle)
        p=normal*(radius(BODY,z)+.002)+tangent*(.07*math.cos(angle));p.z=z;points.append(p)
    for a,b in zip(points,points[1:]): beam('RI02 side channel curved crown',a,b,.022,m['edge'])
    # Authored rear service equipment, explicitly inferred from functional construction.
    for z in [.45,.78,1.11]:
        port('RI02 inferred rear service closure',math.pi/2,z,.055,m)
    return m
