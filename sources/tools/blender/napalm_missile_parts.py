"""Independent PM02 study with open neck and thick segmented lower shrouds."""
import math

import bpy

from build_openfa_assets import beam,cylinder,material
from build_shield_equipment import shell
from terran_missile_parts import band,palette,revolved


def build():
    m=palette()
    m['copper']=material('Napalm | copper ceramic head',(.38,.115,.065),.55,.40)
    m['amber']=material('Napalm | amber feed jacket',(.53,.20,.025),.5,.34)
    m['body'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.095,.095,.14,1)
    m['body'].diffuse_color=(.095,.095,.14,1)
    m['neck']=material('Napalm | pale actuator alloy',(.31,.38,.46),.65,.35)
    # Low cup has a true open axis, with a distinct hollow bell below it.
    cup=shell('Napalm open lower cup',[(.25,.40),(.42,.57),(.80,.74),(1.05,.79)],
        0,math.tau,dict(shell=m['body'],dark=m['dark']),64,.075)
    cup.rotation_euler.x=math.pi/2
    mount=shell('Napalm annular reservoir support',[(.86,.73),(.94,.73)],0,math.tau,
        dict(shell=m['body'],dark=m['dark']),64,.52)
    mount.rotation_euler.x=math.pi/2
    for angle in [-math.pi/2,math.pi/6,5*math.pi/6]:
        panel=shell('Napalm thick angular shroud',[(.45,.56),(.83,.76),(1.3,.85),
                    (1.9,.85),(2.65,.76),(3.30,.67)],angle-.44,angle+.44,
                    dict(shell=m['body'],dark=m['dark']),12,.085)
        panel.rotation_euler.x=math.pi/2
        # Deliberate industrial facets instead of a smooth replacement cylinder.
        for face in panel.data.polygons: face.use_smooth=False
        for z,r in [(1.0,.79),(1.8,.86),(2.60,.78)]:
            strip=shell('Napalm shroud transverse joint',[(z-.012,r),(z+.012,r)],
                angle-.43,angle+.43,dict(shell=m['dark'],dark=m['dark']),12,.018)
            strip.rotation_euler.x=math.pi/2
        for z,r in [(1.3,.86),(2.55,.79)]:
            # Coordinates match shell orientation: x=r*cos(angle), y=-r*sin(angle).
            x,y=r*math.cos(angle),-r*math.sin(angle)
            start=(x*.99,y*.99,z);end=(x*1.025,y*1.025,z)
            beam('Napalm shroud captive fastener',start,end,.024,m['trim'])
    for angle in [-math.pi/6,math.pi/2,7*math.pi/6]:
        x,y=.44*math.cos(angle),-.44*math.sin(angle)
        tank=revolved('Napalm tapered red reservoir',[(.80,.035),(1.03,.095),(1.6,.20),
            (2.25,.29),(2.95,.33),(3.40,.30),(3.57,.22),(3.64,.06)],m['red'])
        tank.location=(x,y,0)
        for z,r in [(2.28,.30),(3.40,.31)]:
            joint=band('Napalm reservoir seam',z,r,.025,m['red']);joint.location=(x,y,0)
        beam('Napalm reservoir neck feed',(x,y,3.55),(x*.64,y*.64,4.26),.065,m['red'])
        collar=cylinder('Napalm reservoir feed coupling',(x*.72,y*.72,3.98),.09,.11,m['red'],vertices=24)
    cylinder('Napalm central exposed actuator',(0,0,3.96),.115,.66,m['neck'],vertices=32)
    cylinder('Napalm actuator lower collar',(0,0,3.64),.17,.12,m['dark'],vertices=32)
    # Copper head is a broad rounded pear, not the long red jacket of PM00/01.
    revolved('Napalm pear pressure head',[(4.19,.24),(4.23,.48),(4.36,.63),
        (4.58,.70),(4.85,.71),(5.13,.65),(5.45,.53),(5.76,.39),(6.02,.23),(6.18,.08)],m['copper'])
    band('Napalm head lower joint',4.49,.694,.030,m['dark'],.055)
    band('Napalm head joint rim',4.53,.713,.025,m['copper'],.055)
    revolved('Napalm red nose cap',[(5.97,.25),(6.08,.19),(6.20,.075),(6.23,.025)],m['red'])
    # Visible amber bottle/line runs between the red reservoirs and raised head.
    bottle=revolved('Napalm forward amber feed bottle',[(2.95,.075),(3.12,.11),(3.43,.11),(3.58,.055)],m['amber'])
    bottle.location=(0,-.79,0)
    beam('Napalm amber transfer pipe',(0,-.79,3.54),(0,-.28,4.24),.035,m['amber'])
    for z in [3.10,3.38]:
        ring=band('Napalm amber feed clamp',z,.121,.025,m['liner']);ring.location=(0,-.79,0)
    bell=shell('Napalm hollow nozzle',[(.10,.32),(.20,.33),(.40,.25),(.64,.17)],0,math.tau,
        dict(shell=m['liner'],dark=m['dark']),64,.04)
    bell.rotation_euler.x=math.pi/2
    band('Napalm nozzle retaining ring',.18,.37,.075,m['red'],.045)
    cylinder('Napalm recessed throat',(0,0,.69),.13,.025,m['dark'],vertices=48)
