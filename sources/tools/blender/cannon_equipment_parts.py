"""Independent PH06/PH07 solid equipment construction, without imported art."""
import math

import bpy

from build_openfa_assets import beam,box,cylinder,finish,material
from build_assault_fighter import plate
from build_shield_equipment import ring,shell


def palette():
    return dict(body=material('Cannon | olive titanium',(.23,.22,.15),.6,.43),
                trim=material('Cannon | machined edges',(.43,.42,.34),.72,.33),
                red=material('Cannon | oxide heat shield',(.34,.065,.045),.45,.42),
                dark=material('Cannon | deep aperture',(.014,.012,.030),.25,.55),
                ceramic=material('Cannon | pale insulators',(.47,.46,.39),.12,.52),
                copper=material('Cannon | copper feeds',(.45,.20,.08),.75,.35))


def oval(name,sections,surface,cy=0):
    # Height, X radius and Y radius define an editable layered pressure casing.
    count=64
    vertices=[(x*math.cos(i*math.tau/count),cy+y*math.sin(i*math.tau/count),z)
              for z,x,y in sections for i in range(count)]
    faces=[tuple(reversed(range(count))),tuple(range((len(sections)-1)*count,len(sections)*count))]
    faces += [(row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i)
              for row in range(len(sections)-1) for i in range(count)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj,name,surface,.008)
    for face in mesh.polygons:
        face.use_smooth=len(face.vertices)==4
    return obj


def oval_ring(name,z,cy,rx,ry,surface):
    obj=ring(name,0,1,.035,surface)
    obj.rotation_euler.x=math.pi/2
    obj.scale=(rx,1,ry)
    obj.location=(0,cy,z)
    return obj


def wedge_casing(name,sections,surface):
    outline=[(0,-1),(.49,-.91),(.82,-.59),(1,-.06),(1,.55),(.74,1),
             (-.74,1),(-1,.55),(-1,-.06),(-.82,-.59),(-.49,-.91)]
    count=len(outline)
    vertices=[(x*rx,y*ry,z) for z,rx,ry in sections for x,y in outline]
    faces=[tuple(reversed(range(count))),tuple(range((len(sections)-1)*count,len(sections)*count))]
    faces += [(row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i)
              for row in range(len(sections)-1) for i in range(count)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj,name,surface,.035)
    return obj


def barrel(name,x,z,profile,m):
    obj=shell(name,profile,0,math.tau,dict(shell=m['trim'],dark=m['dark']),48,.018)
    obj.location=(x,0,z)
    tip=profile[0][0]
    tip_radius=profile[0][1]
    heat=shell(name+' red muzzle sleeve',[(tip-.02,tip_radius+.012),(tip+.19,tip_radius+.022)],
               0,math.tau,dict(shell=m['red'],dark=m['dark']),48,.020)
    heat.location=(x,0,z)
    end=profile[-1][0]
    cylinder(name+' recessed breech',(x,end+.015,z),profile[-1][1]-.02,.025,m['dark'],rotation=(math.pi/2,0,0))
    for y in [end-.06,end-.19]:
        collar=ring(name+' breech collar',y,profile[-1][1]+.018,.045,m['ceramic'])
        collar.location.x=x
        collar.location.z=z
    return obj


def photon(m):
    oval('Photon low pressure casing',[(.02,.77,.62),(.08,.90,.73),(.27,.91,.75),(.38,.81,.66)],m['body'],-.22)
    oval_ring('Photon perimeter lip',.34,-.22,.88,.73,m['trim'])
    # Rear unit is visibly rectangular, unlike the broad circular forward cover.
    box('Photon rear equipment block',(0,.69,.13),(1.03,1.03,.33),m['body'],.08)
    box('Photon rear equipment top cover',(0,.83,.315),(.78,.64,.027),m['trim'],.025)
    for i in range(6):
        box('Photon rear heat exchanger',(0,.62+i*.066,.338),(.54,.025,.018),m['dark'],.003)
    for sign in [-1,1]:
        barrel('Photon paired barrel '+str(sign),sign*.39,.13,
               [(-2.30,.040),(-2.08,.055),(-1.08,.050),(-.82,.10)],m)
        # Two rear connector throats, not assumed to be thrusters.
        conn=shell('Photon rear connector',[(1.14,.12),(1.36,.12)],0,math.tau,
                   dict(shell=m['red'],dark=m['dark']),40,.025)
        conn.location=(sign*.32,0,.11)
        cylinder('Photon connector inner stop',(sign*.32,1.16,.11),.075,.02,m['dark'],rotation=(math.pi/2,0,0))
        for y in [.43,.70,.98]:
            cylinder('Photon equipment captive screw',(sign*.43,y,.31),.018,.018,m['dark'],vertices=8)
        beam('Photon copper feed',(sign*.55,.80,-.02),(sign*.55,-.52,-.02),.021,m['copper'])
    cylinder('Photon circular dorsal access cap',(0,-.20,.403),.23,.025,m['trim'],vertices=48)
    cylinder('Photon cap inset',(0,-.20,.421),.175,.018,m['body'],vertices=48)
    for i in range(8):
        angle=i*math.tau/8
        cylinder('Photon lid fastener',(.21*math.cos(angle),-.20+.21*math.sin(angle),.422),.015,.012,m['dark'],vertices=8)
    for i in range(4):
        angle=math.pi/4+i*math.pi/2
        beam('Photon cover radial seam',(.30*math.cos(angle),-.22+.26*math.sin(angle),.385),
             (.76*math.cos(angle),-.22+.60*math.sin(angle),.385),.004,m['dark'])
    oval('Photon underside inspection plate',[(-.045,.51,.40),(-.015,.55,.44)],m['dark'],-.22)


def plasma(m):
    body=wedge_casing('Plasma thick ribbed pressure casing',[(-.10,.68,.62),(-.03,.82,.75),(.29,.89,.80),(.41,.83,.74)],m['red'])
    rear_face=box('Plasma rear service face',(0,.803,.16),(1.12,.05,.47),m['trim'],.018)
    # Large, off-centre rear aperture is cut into the actual pressure casing.
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.225,depth=.64,location=(-.27,.77,.16),rotation=(math.pi/2,0,0))
    cutter=bpy.context.object
    for target in [body,rear_face]:
        bpy.context.view_layer.objects.active=target
        modifier=target.modifiers.new('True rear equipment port','BOOLEAN')
        modifier.operation='DIFFERENCE'
        modifier.solver='EXACT'
        modifier.object=cutter
        bpy.ops.object.modifier_move_to_index(modifier=modifier.name,index=0)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    cylinder('Plasma deep rear port stop',(-.27,.65,.16),.218,.025,m['dark'],rotation=(math.pi/2,0,0))
    sleeve=shell('Plasma rear aperture sleeve',[(.55,.245),(.82,.255)],0,math.tau,
                 dict(shell=m['trim'],dark=m['dark']),64,.030)
    sleeve.location=(-.27,0,.16)
    collar=ring('Plasma rear aperture lip',.815,.255,.055,m['trim'])
    collar.location.x=-.27
    collar.location.z=.16
    wedge_casing('Plasma cover machined perimeter',[(.385,.87,.78),(.43,.89,.80)],m['trim'])
    wedge_casing('Plasma heavy olive dorsal cover',[(.425,.87,.77),(.47,.86,.76),(.56,.75,.65)],m['body'])
    wedge_casing('Plasma lower casing seam',[(-.08,.80,.74),(-.05,.82,.75)],m['trim'])
    barrel('Plasma single front assembly',0,.16,[(-1.43,.070),(-1.22,.13),(-.99,.17),(-.75,.145)],m)
    for sign in [-1,1]:
        for y in [-.43,-.23,-.03,.17,.37]:
            x=sign*.89*math.sqrt(1-(y/.80)**2)
            rib=box('Plasma red casing rib',(x,y,.17),(.065,.065,.30),m['red'],.014)
            rib.rotation_euler.z=-sign*y*.5
        beam('Plasma side conductor',(sign*.68,-.40,.06),(sign*.68,.39,.06),.021,m['copper'])
        for x,y in [(sign*.75,-.40),(sign*.79,.50)]:
            box('Plasma silver corner guard',(x,y,.15),(.10,.12,.48),m['trim'],.022)
        cylinder('Plasma flank inspection bolt',(sign*.77,.10,.47),.027,.025,m['dark'],vertices=8)
    cylinder('Plasma raised top fitting',(0,.20,.585),.13,.055,m['trim'],vertices=32)
    cylinder('Plasma fitting centre stud',(0,.20,.65),.036,.10,m['ceramic'],vertices=16)
    for i in range(3):
        box('Plasma rear panel vent',(.37,.836,.09+i*.075),(.22,.025,.025),m['dark'],.004)
    for angle in [math.pi/6,math.pi*5/6]:
        beam('Plasma dorsal panel seam',(.19*math.cos(angle),.19*math.sin(angle),.566),
             (.62*math.cos(angle),.55*math.sin(angle),.566),.004,m['dark'])
    # Fine service construction is authored detail, not asserted legacy panel topology.
    plate('Plasma front hatch gasket',[(-.31,-.46,.563),(.31,-.46,.563),(.48,-.15,.563),(-.48,-.15,.563)],.009,m['dark'],.002)
    plate('Plasma front service hatch',[(-.29,-.44,.570),(.29,-.44,.570),(.45,-.17,.570),(-.45,-.17,.570)],.010,m['body'],.003)
    for x,y in [(-.25,-.40),(.25,-.40),(-.38,-.21),(.38,-.21)]:
        cylinder('Plasma captive hatch screw',(x,y,.578),.015,.012,m['trim'],vertices=8)
