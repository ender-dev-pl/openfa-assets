"""Building-specific mechanical authoring, informed by PB00–PB39 reference silhouettes."""
import math

import bpy
from mathutils import Vector


def residential(d, floors, security=False):
    d.shell('Segmented habitation base',[(.03,.70),(.24,.70),(.45,.70)],24,'alloy')
    for level in range(floors):
        z = .5+level*.58
        d.shell('Individual curved habitation plates',[(z,.75),(z+.12,.90),(z+.36,.90),(z+.53,.70)],24,'gold')
        d.ring('Dark expansion joint',(0,0,z+.13),.904,.016,'dark')
        d.ring('Lower structural sill',(0,0,z+.08),.86,.022,'bronze')
        d.radial_windows(.916,z+.26,20,height=.07)
    roof = .5+(floors-1)*.58+.53
    d.disc('Roof maintenance deck',(0,0,roof+.01),.55,.025,'alloy')
    d.hatch('Roof access',(0,-.15,roof+.035),.15)
    d.ring('Roof aerial mounting track',(0,0,roof+.035),.50,.014,'dark')
    d.bolts('Roof rim fastener',.62,roof+.025,20)
    d.box('Base personnel airlock',(0,-.73,.24),(.28,.09,.35),'dark')
    d.box('Airlock pressure door',(0,-.786,.24),(.21,.025,.29),'alloy')
    d.vent('Base air exchanger',(.40,-.60,.24),.22,.24,6,rotation=.55)
    if security:
        for i in range(6):
            a = i*math.tau/6
            p = (.99*math.cos(a),.99*math.sin(a),.8)
            d.disc('Security pod sensor',p,.095,.04,'glass',normal=(math.cos(a),math.sin(a),0))
    d.feature('Segmented habitation bands, recessed glazing, expansion joints and pressure airlock')


def storage(d, tiers, protected=False):
    for tier in range(tiers):
        z = tier
        d.shell('Storage vessel structural belt',[(z+.02,.79),(z+.18,.79),(z+.35,.79)],24,'alloy')
        for i in range(4):
            a = i*math.tau/4
            x,y = .47*math.cos(a),.47*math.sin(a)
            d.ring('Vessel equatorial clamp',(x,y,z+.6),.345,.022,'edge')
            d.pipe('Protected vessel feed',[(x*.8,y*.8,z+.95),(x,y,z+.91),(x,y,z+.75)],.027,'bronze')
        for i in range(8):
            a = i*math.tau/8
            d.rod('Storage vertical cage rail',(.78*math.cos(a),.78*math.sin(a),z+.30),
                (.78*math.cos(a),.78*math.sin(a),z+.98),.025,'alloy')
    d.shell('Individual storage hood panels',[(tiers-.02,.80),(tiers+.18,.81),(tiers+.85,.55)],20,'alloy')
    d.ring('Hood service gasket',(0,0,tiers+.18),.815,.023,'dark')
    d.hatch('Storage instrument access',(0,-.62,tiers+.62),.12,(0,-.93,.36))
    d.ladder(.28,-.81,.10,tiers+.10)
    d.feature('Separate vessel clamps, cage rails, protected feed pipes and segmented hood')


def power_store(d):
    for i in range(3):
        a = i*math.tau/3
        x,y = .83*math.cos(a),.83*math.sin(a)
        d.shell('Reservoir foot panels',[(.01,.42),(.13,.40),(.65,.22)],16,'alloy',(x,y))
        d.ring('Reservoir cap gasket',(x,y,.66),.51,.023,'dark')
        d.dome('Reservoir cap plates',.51,.28,.65,'alloy',(x,y),4,16)
        d.ring('Reservoir service flange',(x,y,.26),.35,.025,'edge')
        d.hatch('Reservoir side access',(x,y-.29,.40),.10,(0,-1,0))
        for side in [-1,1]:
            d.pipe('Reservoir cooling riser',[(x+side*.23,y,.16),(x+side*.23,y,.55),
                (x+side*.32,y,.65)],.025,'bronze')
    d.feature('Pressure-reservoir cap plates, cooling risers, flanges and inspection ports')


def turret(d, index, record):
    d.shell('Armoured pedestal sectors',[(.02,.94),(.20,.99),(.45,.90),(.68,.71),(.89,.51)],24,'bronze')
    d.ring('Pedestal foundation joint',(0,0,.12),.98,.026,'dark')
    d.ring('Azimuth race flange',(0,0,.91),.48,.048,'edge')
    d.bolts('Azimuth race fastener',.47,.96,16,size=.018)
    d.hatch('Pedestal systems hatch',(.53,-.80,.43),.15,(.5,-.8,.3),'red')
    d.vent('Turret cooling intake',(-.42,-.70,.38),.23,.19,5,rotation=-.5)
    d.role = 'head'
    d.ring('Rotating joint flexible seal',(0,0,.99),.35,.026,'dark')
    d.disc('Trunnion left',(-.43,0,1.07),.14,.065,'bronze',(-1,0,0))
    d.disc('Trunnion right',(.43,0,1.07),.14,.065,'bronze',(1,0,0))
    length = record['parameters'].get('length',1)
    n = record['parameters'].get('barrels',1)
    bore = record['parameters'].get('bore',.10)
    start,end = Vector((0,-.15,1.08)),Vector((0,-length,1.38))
    axis = (end-start).normalized()
    for barrel in range(n):
        offset = Vector(((barrel-(n-1)/2)*bore*3.2,0,0))
        for ring in range(4):
            p = start.lerp(end,.25+ring*.18)+offset
            d.ring('Barrel heat-sink collar',p,bore*1.15,.018,'dark',axis)
        d.ring('Muzzle locking ring',end+offset,bore*1.05,.022,'bronze',axis)
    for side in [-1,1]:
        d.rod('Elevation actuator body',(side*.29,-.10,1.0),(side*.29,-.47,1.17),.052,'dark')
        d.rod('Elevation actuator piston',(side*.29,-.44,1.16),(side*.29,-.62,1.28),.026)
    d.box('Head rangefinder',(.28,-.23,1.35),(.16,.19,.09),'dark')
    d.disc('Rangefinder lens',(.28,-.335,1.35),.038,.025,'glass',(0,-1,0))
    if index == 17:
        for i in range(10):
            a = i*math.tau/10
            d.disc('Reflector rim rivet',(.64*math.cos(a),-.10+.29*math.sin(a),1.52),.016,.012,'bronze')
        d.rod('Reflector rear brace',(-.38,.12,1.08),(0,.15,1.70),.028)
        d.rod('Reflector rear brace',(.38,.12,1.08),(0,.15,1.70),.028)
    if index == 27:
        d.box('Laser focusing module',(0,-.26,1.30),(.24,.34,.20),'bronze')
    d.role = 'base'
    d.feature('Segmented rounded armour, azimuth race, trunnions, elevation actuators and barrel cooling')


def factory(d):
    for i in range(8):
        x = -1.18+i*.337
        d.box('Factory roof standing seam',(x,.15,1.09),(.025,1.58,.04),'bronze')
    for x in [-.85,0,.85]:
        d.box('Factory ventilation curb',(x,.30,1.14),(.46,.58,.12),'dark')
        for j in range(7):
            d.box('Factory roof louvre',(x,.05+j*.075,1.205),(.40,.025,.025),'edge')
    d.box('Loading bay frame',(0,-.68,.56),(.65,.08,.64),'dark')
    for i in range(8):
        d.box('Loading shutter rib',(0,-.73,.30+i*.067),(.57,.026,.043),'alloy')
    for x in [-1.28,1.28]:
        d.vent('Factory side plant',(x,.18,.55),.68,.36,8,rotation=math.pi/2)
    for x in [-.62,0,.62]:
        d.ring('Factory tank tension band',(x,-1,.35),.28,.025,'bronze')
        d.pipe('Factory tank delivery',[(x,-1,.65),(x,-1.02,1.07),(x,-.65,1.13)],.035)
    d.ladder(-1.16,-.69,.12,1.12)
    d.roof_rail(-1.25,1.25,.94,1.07)
    d.feature('Standing-seam roof, ventilation units, shuttered loading bay and tank delivery manifolds')


def mine(d, deep=False):
    for x in [-.75,.75]:
        for y in [-.65,.65]:
            d.box('Trestle foundation shoe',(x,y,.045),(.31,.31,.09),'dark')
            for z in [.13,.43,.73,1.03]:
                d.box('Trestle horizontal cross tie',(x,y,z),(.25,.25,.035),'edge')
                d.rod('Trestle reverse diagonal',(x-.1,y+.1,z),(x+.1,y-.1,z+.27),.018)
            for z in [.2,.8,1.35]:
                d.disc('Trestle gusset bolt',(x,y-.13,z),.027,.022,'bronze',(0,-1,0))
    for x in [-1,-.5,0,.5,1]:
        d.box('Mine deck plate seam',(x,0,1.762),(.016,1.80,.015),'dark')
    d.roof_rail(-1.02,1.02,.90,1.77)
    d.roof_rail(-1.02,1.02,-.90,1.77)
    d.ring('Drilling hatch clamp',( .35,.39,1.82),.35,.025,'bronze')
    d.bolts('Drilling hatch fastener',.28,1.85,12,(.35,.39),.018)
    d.ladder(.93,-.95,.10,1.92)
    d.pipe('Drilling hydraulic feed',[(-.5,-.73,.15),(-.5,-.73,1.25),(-.4,-.4,1.68)],.035,'bronze')
    if deep:
        for z in [.20,.45,.70,.95,1.2]:
            d.ring('Drill shaft coupler',(0,0,z),.37,.035,'bronze')
    d.feature('Four-sided lattice trestles, gussets, deck plating, guardrails and drill hydraulics')


def silo(d, satellite):
    d.shell('Silo bunker armour sectors',[(.03,1.10),(.20,1.18),(.45,1.02),(.64,.92)],24,'bronze')
    if satellite:
        d.dome('Silo lid armour leaves',.90,.22,.64,'red',rings=4,sectors=24)
    else:
        from refined_silo_iris import build_iris
        build_iris(d)
    d.ring('Lid pressure seal',(0,0,.66),.92,.024,'dark')
    for a in [0,math.pi/2,math.pi,math.pi*1.5]:
        d.box('Silo lid hinge',(math.cos(a)*.91,math.sin(a)*.91,.66),(.17,.13,.09),'alloy',(0,0,a))
    d.bolts('Silo perimeter bolt',1.03,.43,24)
    d.hatch('Silo maintenance hatch',(.74,-.81,.40),.13,(.6,-.7,.3))
    if satellite:
        d.vent('Satellite silo control annex',(0,-1.20,.28),.22,.18,5)
    else:
        for x in [-.36,0,.36]:
            d.box('Launch status lamp',(x,-1.105,.30),(.07,.025,.06),'light')
    d.feature('Segmented bunker and lid armour, hinge blocks, pressure seal and maintenance hatch')


def matrix(d, protected):
    for x in [-.2,.2]:
        for z in [.58,1.05,1.55,2.05,2.43]:
            d.ring('Coil structural clamp',(x,0,z),.15,.025,'bronze')
        d.rod('Coil protected power riser',(x,.16,.50),(x,.16,2.50),.022,'dark')
    for i in range(4):
        a = i*math.tau/4
        for row in range(5):
            for col in range(3):
                r,t = .15+row*.205,(col-1)*.15
                x,y = r*math.cos(a)-t*math.sin(a),r*math.sin(a)+t*math.cos(a)
                d.box('Matrix photovoltaic cell',(x,y,2.89),(.21,.135,.012),'violet',(0,0,a),.002)
        d.rod('Collector hinge actuator',(.20*math.cos(a),.20*math.sin(a),2.53),
            (.77*math.cos(a),.77*math.sin(a),2.81),.024)
    d.hatch('Matrix base electronics',(0,-.44,.28),.14,(0,-1,0))
    if protected:
        d.role = 'head'
        d.ring('Defensive cap azimuth bearing',(0,0,3.0),.24,.028,'dark')
        d.disc('Defensive cap optical sensor',(.16,-.13,3.12),.035,.02,'glass',(0,-1,0))
        d.role = 'base'
    d.feature('Collector cell arrays, hinges, coil clamps and protected power risers')


def refine_building(index, d, record):
    if index in [0,29,39]:
        residential(d,record['parameters']['floors'],index==39)
    elif index == 1:
        power_store(d)
    elif index in [2,30,33]:
        storage(d,record['parameters']['tiers'],index==33)
        if index == 33:
            d.role = 'head'
            d.ring('Protected storage cap bearing',(0,0,3.12),.22,.025,'dark')
            d.role = 'base'
    elif index in [3,17,18,27]:
        turret(d,index,record)
    elif index == 7:
        factory(d)
    elif index in [8,13]:
        mine(d,index==13)
    elif index in [9,14]:
        silo(d,index==9)
    elif index in [28,31]:
        matrix(d,index==31)
    else:
        from refine_terran_special import refine_special
        refine_special(index,d,record)
    assert d.features,record['preview']
