"""Original detailed RI01 geometry, authored from paletted surface/hologram evidence."""
import math

import bmesh
import bpy
from mathutils import Vector

from build_openfa_assets import beam,box,cylinder,finish,material
from build_shield_equipment import shell
from terran_missile_parts import band,revolved

ROOF=[(1.95,.40),(2.08,.70),(2.25,1.06),(2.35,1.17),(2.45,1.13),(2.58,.94),(2.70,.66),(2.80,.32),(2.84,.20)]
BASE=[(.04,1.04),(.12,1.13),(.30,1.08),(.58,.84),(.95,.55),(1.27,.39),(1.38,.38)]


def palette():
    return dict(body=material('Rigellian CPU | teal titanium',(.075,.23,.18),.57,.43),
        panel=material('Rigellian CPU | pale green shell',(.18,.32,.28),.53,.41),
        edge=material('Rigellian CPU | machined pale alloy',(.33,.43,.40),.76,.34),
        dark=material('Rigellian CPU | deep equipment well',(.012,.025,.024),.3,.55),
        gold=material('Rigellian CPU | brass conductor alloy',(.47,.29,.07),.72,.37),
        glass=material('Rigellian CPU | blue green service inset',(.025,.09,.105),.45,.31))


def base_radius(z):
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(BASE,BASE[1:]) if za<=z<=zb)


def service_cap(name,phi,z,radius,surface):
    normal=Vector((math.cos(phi),math.sin(phi),.82)).normalized()
    position=Vector((base_radius(z)*math.cos(phi),base_radius(z)*math.sin(phi),z))-normal*.005
    obj=cylinder(name,position,radius,.040,surface,vertices=48)
    obj.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    return obj


def roof_plate(surface):
    count=48;rings=9;size=1+rings*count;vertices=[]
    def surface_height(x,y):
        radius=math.hypot(x,y)
        upper=ROOF[4:]
        return next(za+(zb-za)*(radius-ra)/(rb-ra) for (za,ra),(zb,rb) in zip(upper,upper[1:]) if rb<=radius<=ra)
    for lift in [.005,-.012]:
        vertices.append((.48,-.25,surface_height(.48,-.25)+lift))
        for j in range(1,rings+1):
            radius=.16*j/rings
            for i in range(count):
                angle=i*math.tau/count;x=.48+radius*math.cos(angle);y=-.25+radius*math.sin(angle)
                vertices.append((x,y,surface_height(x,y)+lift))
    faces=[]
    for i in range(count):
        a=1+i;b=1+(i+1)%count;faces += [(0,a,b),(size,b+size,a+size)]
    for row in range(rings-1):
        for i in range(count):
            a=1+row*count+i;b=1+row*count+(i+1)%count;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for i in range(count):
        a=1+(rings-1)*count+i;b=1+(rings-1)*count+(i+1)%count
        faces.append((a,a+size,b+size,b))
    mesh=bpy.data.meshes.new('Conformal roof service plate');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('CPU pale conformal roof service cap',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,surface,0)


def crown(m):
    band('CPU crown brass seating ring',2.86,.225,.10,m['gold'],.07)
    cylinder('CPU crown solid mounting socket',(0,0,2.85),.17,.08,m['gold'],vertices=48)
    cylinder('CPU crown central conductor',(0,0,3.42),.038,1.22,m['gold'],vertices=24)
    for sign in [-1,1]:
        points=[(sign*.07,0,2.88),(sign*.12,0,3.06),(sign*.27,0,3.24),
                (sign*.30,0,3.40),(sign*.30,0,3.82)]
        for a,b in zip(points,points[1:]): beam('CPU crown outer conductor',a,b,.031,m['gold'])
        cylinder('CPU crown side terminal',(sign*.30,0,3.83),.036,.065,m['gold'],vertices=24)
    cylinder('CPU crown central terminal',(0,0,4.04),.041,.065,m['gold'],vertices=24)


def build():
    m=palette()
    revolved('CPU flared waisted foundation',BASE,m['body'])
    revolved('CPU foundation ground lip',[(0,1.03),(.035,1.10),(.10,1.10),(.14,1.05)],m['edge'])
    band('CPU foundation upper seam',1.27,.397,.035,m['panel'],.035)
    neck=shell('CPU neck with actual grille opening',[(1.32,.39),(2.10,.40)],
        math.pi/2+.65,math.pi/2-.65+math.tau,dict(shell=m['body'],dark=m['dark']),64,.08)
    neck.rotation_euler.x=math.pi/2
    cylinder('CPU exposed brass neck core',(0,0,1.70),.155,.72,m['gold'],vertices=48)
    for z in [1.44,1.58,1.72,1.86,2.00]:
        box('CPU grille horizontal structural fin',(0,-.30,z),(.55,.11,.045),m['edge'],.006)
    for x in [-.27,.27]:
        beam('CPU grille side retaining rail',(x,-.29,1.38),(x,-.29,2.03),.024,m['panel'])
    band('CPU lower neck collar',1.37,.405,.09,m['edge'],.08)
    band('CPU upper neck collar',2.04,.42,.10,m['panel'],.10)
    roof=revolved('CPU broad upper saucer',ROOF,m['panel'])
    band('CPU saucer perimeter machined rim',2.35,1.183,.065,m['edge'],.05)
    # True well in the roof, rather than an opaque dark decal.
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.205,depth=.70,location=(-.55,-.12,2.80))
    cutter=bpy.context.object
    bpy.context.view_layer.objects.active=roof
    modifier=roof.modifiers.new('Actual recessed roof well','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(roof.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bm.to_mesh(roof.data);bm.free()
    liner=shell('CPU roof well inner sleeve',[(2.44,.21),(2.62,.21)],0,math.tau,
        dict(shell=m['edge'],dark=m['dark']),64,.028)
    liner.rotation_euler.x=math.pi/2;liner.location=(-.55,-.12,0)
    cylinder('CPU roof well recessed floor',(-.55,-.12,2.46),.19,.040,m['dark'],vertices=64)
    for i in range(3):
        box('CPU well interior cooling fin',(-.55,-.20+i*.075,2.485),(.22,.018,.022),m['gold'],.003)
    # Roof segmentation and fastener repetition are authored manufactured detail.
    for i in range(12):
        phi=i*math.tau/12
        cylinder('CPU perimeter captive fastener',(1.095*math.cos(phi),1.095*math.sin(phi),2.46),.019,.020,m['dark'],vertices=12)
    roof_plate(m['edge'])
    for phi,z,radius,surface in [(-.85,.40,.13,m['gold']),(-2.08,.25,.060,m['gold']),(-1.68,1.00,.055,m['glass'])]:
        service_cap('CPU foundation circular service cap',phi,z,radius,surface)
    # Shallow foundation seams follow real conical surfaces; no legacy textures.
    for phi in [i*math.tau/8 for i in range(8)]:
        for za,zb in [(.20,.48),(.52,.86)]:
            splits=[za]+[z for z,_ in BASE if za<z<zb]+[zb]
            for a_z,b_z in zip(splits,splits[1:]):
                a=(base_radius(a_z)*math.cos(phi),base_radius(a_z)*math.sin(phi),a_z)
                b=(base_radius(b_z)*math.cos(phi),base_radius(b_z)*math.sin(phi),b_z)
                beam('CPU foundation panel joint',a,b,.005,m['dark'])
    crown(m)
