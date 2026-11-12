"""Independently authored Hellfire casing and reference-backed visible fittings."""
import math

import bmesh
import bpy

from build_openfa_assets import box,cylinder,finish,material
from build_shield_equipment import shell
from cannon_equipment_parts import oval
from terran_missile_parts import band,revolved


def build():
    m=dict(body=material('Hellfire | blue silver titanium',(.28,.34,.40),.78,.34),
           panel=material('Hellfire | brushed side fairing',(.23,.29,.34),.72,.39),
           trim=material('Hellfire | machined port insert',(.30,.32,.35),.8,.30),
           dark=material('Hellfire | recessed graphite',(.012,.016,.023),.3,.5),
           red=material('Hellfire | oxide identification',(.40,.045,.035),.4,.42),
           liner=material('Hellfire | refractory nozzle',(.22,.18,.14),.65,.46))
    body=revolved('Hellfire fusiform pressure casing',[(.66,.35),(.90,.40),(1.30,.52),
        (1.80,.63),(2.35,.71),(2.90,.735),(3.45,.72),(4.0,.68),(4.43,.625)],m['body'])
    # One actual recessed vertical fitting; its function and hidden counterpart
    # are not established by the single management perspective.
    cutter=oval('Temporary vertical port cutter',[(3.08,.04,.26),(3.14,.10,.30),
        (3.80,.11,.32),(4.00,.17,.32),(4.12,.16,.32),(4.24,.04,.28)],m['dark'],-.65)
    cutter.location.x=-.28
    bpy.context.view_layer.objects.active=body
    boolean=body.modifiers.new('True recessed vertical fitting','BOOLEAN')
    boolean.operation='DIFFERENCE';boolean.solver='EXACT';boolean.object=cutter
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    # Resolve large Boolean boundary faces before export; no tiny sliver patches.
    bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.00001,edges=list(bm.edges))
    bm.to_mesh(body.data);bm.free()
    wall=oval('Hellfire port recessed back wall',[(3.12,.04,.02),(3.20,.09,.025),
        (3.79,.095,.025),(4.00,.15,.025),(4.11,.14,.025),(4.20,.025,.02)],m['dark'],-.35)
    wall.location.x=-.28
    insert=oval('Hellfire vertical port insert',[(3.16,.025,.02),(3.25,.065,.05),
        (3.85,.065,.065),(4.01,.095,.04),(4.08,.02,.02)],m['trim'],-.48)
    insert.location.x=-.28
    # Substantial oval blister follows the narrowing lower casing and intersects
    # it throughout its perimeter, rather than floating at its tapered ends.
    casing_profile=[(.90,.40),(1.30,.52),(1.80,.63),(2.35,.71),(2.90,.735),(3.45,.72)]
    sections=[]
    for i in range(25):
        angle=math.pi*i/24
        z=2.25-1.05*math.cos(angle)
        radius=next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(casing_profile,casing_profile[1:]) if za<=z<=zb)
        sections.append((z,max(.008,.40*math.sin(angle)),-radius+.045,max(.008,.26*math.sin(angle))))
    blister=oval('Hellfire large oval side form',[(z,rx,ry) for z,rx,cy,ry in sections],m['panel'])
    for j,(_,_,cy,_) in enumerate(sections):
        for vertex in list(blister.data.vertices)[j*64:(j+1)*64]: vertex.co.y+=cy
    smooth=blister.modifiers.new('Continuous oval casing relief','SUBSURF')
    smooth.levels=2;smooth.render_levels=2
    revolved('Hellfire long tapered nose',[(4.42,.625),(4.64,.58),(4.94,.49),
        (5.27,.39),(5.60,.29),(5.90,.195),(6.10,.10)],m['body'])
    band('Hellfire nose pressure joint',4.43,.633,.020,m['trim'],.04)
    revolved('Hellfire small red tip',[(5.96,.17),(6.10,.12),(6.22,.05),(6.24,.018)],m['red'])
    # A round red side identification patch is visible on the nose. The angular
    # position, nonverbal mark and exact dimensions are authored.
    vertices=[]
    count=48
    def patch_point(z,arc,lift):
        r=.49+(z-4.94)*(.39-.49)/(5.27-4.94)
        angle=-1.03+arc/r
        return ((r+lift)*math.cos(angle),(r+lift)*math.sin(angle),z)
    for lift in [.003,-.005]:
        vertices.append(patch_point(4.99,0,lift))
        vertices += [patch_point(4.99+.11*math.sin(i*math.tau/count),.11*math.cos(i*math.tau/count),lift) for i in range(count)]
    faces=[]
    for i in range(count):
        a=1+i;b=1+(i+1)%count;offset=count+1
        faces += [(0,a,b),(offset,b+offset,a+offset),(a,a+offset,b+offset,b)]
    mesh=bpy.data.meshes.new('Conformal red nose marking');mesh.from_pydata(vertices,[],faces);mesh.update()
    patch=bpy.data.objects.new('Hellfire nose red identification patch',mesh);bpy.context.collection.objects.link(patch)
    finish(patch,patch.name,m['red'],0)
    skirt=shell('Hellfire hollow tail skirt',[(.12,.23),(.32,.26),(.54,.31),(.72,.37)],
        0,math.tau,dict(shell=m['body'],dark=m['dark']),64,.045)
    skirt.rotation_euler.x=math.pi/2
    bell=shell('Hellfire hollow nozzle',[(.08,.19),(.17,.19),(.36,.15),(.57,.10)],
        0,math.tau,dict(shell=m['liner'],dark=m['dark']),64,.03)
    bell.rotation_euler.x=math.pi/2
    band('Hellfire nozzle retaining rim',.13,.22,.055,m['red'],.025)
    cylinder('Hellfire recessed throat',(0,0,.62),.085,.025,m['dark'],vertices=48)

    # Revised width is based on the management silhouette; units remain authored.
    for obj in list(bpy.context.collection.objects):
        if obj.type=='MESH':
            inverse=obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                point=obj.matrix_world @ vertex.co
                point.x*=1.14;point.y*=1.14
                vertex.co=inverse @ point
