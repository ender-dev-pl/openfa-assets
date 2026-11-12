"""Independent editable Terran missile construction; legacy images are reference-only."""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import box,cylinder,finish,material
from cannon_equipment_parts import oval
from build_shield_equipment import shell


def palette():
    return dict(body=material('Missile | graphite titanium',(.18,.18,.22),.65,.42),
                red=material('Missile | oxide red enamel',(.42,.055,.045),.4,.40),
                trim=material('Missile | exposed alloy',(.40,.41,.45),.75,.32),
                dark=material('Missile | recessed graphite',(.012,.014,.02),.3,.55),
                liner=material('Missile | heat stained nozzle',(.25,.15,.08),.7,.40))


def revolved(name,profile,surface):
    return oval(name,[(z,r,r) for z,r in profile],surface)


def band(name,z,r,depth,surface,thickness=.020):
    obj=shell(name,[(z-depth/2,r-.012),(z-depth*.25,r),(z+depth*.25,r),(z+depth/2,r-.012)],
              0,math.tau,dict(shell=surface,dark=surface),64,thickness)
    obj.rotation_euler.x=math.pi/2
    return obj


def build(area=False):
    m=palette()
    revolved('Segmented pressure body',[(.60,.64),(1.05,.64),
             (2.10,.64),(2.28,.63),(2.34,.61),(3.15,.61),(4.18,.61),(4.30,.64)],m['body'])
    aft=shell('Hollow aft pressure skirt',[(.30,.48),(.42,.60),(.60,.64),(.66,.64)],0,math.tau,
              dict(shell=m['body'],dark=m['dark']),64,.08)
    aft.rotation_euler.x=math.pi/2
    for z in [.57,2.28,3.25,4.18]:
        band('Pressure casing circumferential joint',z,.646 if z<2.3 else .618,.030,m['dark'])
        band('Joint machined lip',z+.032,.647 if z<2.3 else .619,.018,m['trim'])
    # Visible long gray middle section is intentionally kept readable.
    for z in [2.62,3.60,3.95]:
        box('Body inspection label',(0,-.618,z),(.17,.012,.018),m['trim'],.003)
    for angle in [math.pi/4+i*math.pi/2 for i in range(4)]:
        # Fourfold hidden-side arrangement is authored, not established by one preview.
        x,y=.64*math.cos(angle),.64*math.sin(angle)
        pod=revolved('Red tail stabilizer pod',[(.47,.035),(.51,.11),(.59,.18),(.72,.21),
            (1.98,.21),(2.10,.18),(2.20,.11),(2.25,.035)],m['red'])
        pod.location=(x,y,0)
        for z in [.73,1.92]:
            collar=band('Tail pod assembly seam',z,.212,.015,m['dark']);collar.location=(x,y,0)
        for z in [.87,1.75]:
            bolt=cylinder('Tail pod captive bolt',(x*1.25,y*1.25,z),.022,.014,m['trim'],vertices=12)
            bolt.rotation_euler=(math.pi/2,0,angle-math.pi/2)
    revolved('Red warhead jacket',[(4.18,.70),(4.24,.735),(5.57,.735),(5.66,.70)],m['red'])
    jacket=bpy.data.objects['Red warhead jacket']
    # A true recessed instrument channel, rather than a black decal.
    cutter=box('Temporary channel cutter',(0,-.715,4.94),(.38,.40,1.13 if not area else .91),m['dark'],.11)
    bpy.context.view_layer.objects.active=cutter
    bpy.ops.object.modifier_apply(modifier=cutter.modifiers[0].name)
    bpy.context.view_layer.objects.active=jacket
    boolean=jacket.modifiers.new('Recessed warhead instrumentation','BOOLEAN')
    boolean.operation='DIFFERENCE';boolean.solver='EXACT';boolean.object=cutter
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    box('Instrument channel back wall',(0,-.527,4.94),(.345,.018,1.07 if not area else .85),m['dark'],.06)
    if area:
        revolved('Area layered rounded nose',[(5.55,.70),(5.70,.70),(5.80,.58),
            (5.91,.57),(6.01,.44),(6.12,.43),(6.22,.24),(6.25,.06)],m['red'])
        for z,r in [(5.71,.75),(5.94,.61),(6.13,.45)]:
            band('Area stepped nose retaining rim',z,r,.055,m['red'],.12)
    else:
        revolved('Explosive rounded shoulder nose',[(5.55,.70),(5.67,.76),(5.76,.70),
            (5.95,.57),(6.12,.40),(6.23,.19),(6.26,.06)],m['red'])
        box('Explosive long instrument insert',(0,-.560,4.83),(.18,.035,.69),m['trim'],.025)
        for x in [-.047,.047]:
            box('Long insert recessed slot',(x,-.582,4.78),(.025,.012,.43),m['dark'],.008)
    disk=cylinder('Warhead instrumentation disk',(0,-.581,5.17),.16,.035,m['trim'],vertices=48,rotation=(math.pi/2,0,0))
    for z in [5.12,5.22]:
        cylinder('Instrument disk fastener',(0,-.605,z),.019,.009,m['dark'],vertices=12,rotation=(math.pi/2,0,0))
    # Nozzle axis is open. Recessed throat ends above the bell; no solid exhaust mesh.
    nozzle=shell('Hollow propulsion bell',[(.10,.39),(.20,.39),(.35,.31),(.57,.22)],0,math.tau,
                 dict(shell=m['liner'],dark=m['dark']),64,.045)
    nozzle.rotation_euler.x=math.pi/2
    collar=shell('Nozzle red retaining collar',[(.145,.43),(.235,.43)],0,math.tau,
                 dict(shell=m['red'],dark=m['dark']),64,.035)
    collar.rotation_euler.x=math.pi/2
    cylinder('Recessed nozzle throat',(0,0,.59),.17,.025,m['dark'],vertices=48)
    for angle in [i*math.tau/12 for i in range(12)]:
        cylinder('Tail casing captive fastener',(.49*math.cos(angle),.49*math.sin(angle),.38),.018,.025,m['trim'],vertices=12)
    return jacket
