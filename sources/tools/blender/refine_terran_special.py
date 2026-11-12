"""Specific functional equipment for the remaining Terran building types."""
import math

import bpy
from mathutils import Vector


def refine_special(index,d,record):
    if index == 4:
        for i in range(4):
            a = i*math.tau/4+math.pi/4
            for side in [-1,1]:
                d.rod('Solar rear spar',(.23*math.cos(a),.23*math.sin(a),2.77),
                    (1.48*math.cos(a)-side*.30*math.sin(a),1.48*math.sin(a)+side*.30*math.cos(a),2.80),.022)
            d.rod('Tracking actuator',(.18*math.cos(a),.18*math.sin(a),2.45),
                (.65*math.cos(a),.65*math.sin(a),2.79),.035,'dark')
        d.shell('Solar mast armoured panels',[(.02,.36),(.18,.37),(1.0,.28),(1.8,.20),(2.3,.15)],8,'violet')
        d.hatch('Solar inverter access',(0,-.31,.58),.12,(0,-1,0))
        d.feature('Mast armour, collector rear spars, tracking actuators and inverter hatch')
    elif index == 5:
        for i in range(3):
            x,y = (i-1)*.55,.3*(i%2)
            z = 2.15-(i%2)*.4
            for zz in [.18,.65,1.18,z-.10]:
                d.ring('Filter pipe bolted sleeve',(x,y,zz),.205,.03,'edge')
            axis = Vector((0,-.45,.17)).normalized()
            end = Vector((x,y-.45,z+.17))
            d.ring('Intake mouth flange',end,.225,.025,'bronze',axis)
            for zz in [-.08,0,.08]:
                d.rod('Intake debris grille',(x-.15,y-.465,z+.17+zz),
                    (x+.15,y-.465,z+.17+zz),.012,'dark')
            d.pipe('Filter monitoring line',[(x+.18,y+.07,.25),(x+.18,y+.07,z-.25),
                (x+.12,y-.10,z)],.012,'bronze')
        d.feature('Bolted pipe couplings, intake flanges, debris screens and monitoring lines')
    elif index == 6:
        d.shell('Generator tapered casing',[(.02,.45),(.18,.45),(.65,.233),(.99,.075)],8,'bronze')
        blades=sorted((obj for obj in d.collection.objects if obj.name.startswith('Upright collector blade')),key=lambda obj:obj.name)
        for i in range(5):
            a = -.9+i*1.8/4
            blades[i].location=(math.sin(a)*.85,i*.035,1+math.cos(a)*.85)
            # The original blade objects are tilted around Y; place cell strips in their local plane.
            for row in range(7):
                offset = -.68+row*.22
                p = (math.sin(a)*(.85+offset),i*.035-.052,1+math.cos(a)*(.85+offset))
                d.box('Generator collector cell strip',p,(.205,.015,.18),'blue',(0,a,0),.002)
        d.disc('Generator fan hinge',(0,.07,1.04),.15,.26,'edge',(0,1,0))
        d.hatch('Generator conversion module',(0,-.35,.43),.12,(0,-1,0))
        d.feature('Tilted collector cell strips and segmented converter casing')
    elif index == 10:
        d.dome('Field generator curved armour',.98,.38,.28,'alloy',rings=4)
        for i in range(3):
            x=(i-1)*.65
            d.disc('Emitter insulated mounting',(x,0,.58),.11,.10,'dark')
            for z in [.83,1.2,1.6]:
                d.disc('Emitter induction collar',(x,0,z),.075,.07,'blue')
            d.pipe('Emitter power feed',[(x,-.12,.44),(x,-.12,.70),(x,0,.83)],.018,'bronze')
        d.hatch('Field generator control',(0,-.9,.43),.15,(0,-.95,.3))
        d.feature('Curved hull plates, insulated emitter mounts, induction collars and power feeds')
    elif index == 11:
        d.shell('Teleporter tower service panels',[(.13,.37),(.70,.37),(1.35,.37),(1.87,.37)],16,'alloy',(0,.15))
        d.ladder(0,-.245,.15,1.83)
        for x in [-.65,.65]:
            for z in [.24,.55,.76]:
                d.ring('Transfer side tank clamp',(x,-.2,z),.18,.022,'bronze')
            d.pipe('Transfer side pressure line',[(x,-.2,.78),(x,-.58,.78),(x*.55,-.60,.60)],.026,'blue')
        d.ring('Transfer aperture pressure bezel',(0,-.78,.60),.23,.04,'bronze',(0,-1,0))
        for i in range(5):
            d.box('Transfer ramp tread',(0,-.76-i*.13,.22-i*.025),(.31,.026,.025),'edge')
        d.feature('Transfer chamber bezel, pressure lines, tower access and ramp treads')
    elif index in [12,22]:
        # Longitude seams follow the ellipsoid rather than floating straight across its face.
        for i in range(12):
            a = i*math.tau/12
            points=[]
            for j in range(25):
                phi=-math.pi/2+j*math.pi/24
                points.append((.833*math.cos(phi)*math.cos(a),.833*math.cos(phi)*math.sin(a),1.35+.923*math.sin(phi)))
            d.pipe('Field orb panel meridian',points,.012,'dark')
        for z in [.78,1.10,1.60,1.92]:
            r=.833*math.sqrt(max(0,1-((z-1.35)/.923)**2))
            d.ring('Field orb latitude joint',(0,0,z),r,.012,'dark')
        d.shell('Orb foundation armour',[(.02,1.26),(.14,1.26),(.25,1.26)],24,'alloy')
        for a in [math.pi/4,math.pi*3/4,math.pi*5/4,math.pi*7/4]:
            d.box('Field regulator cabinet',(.94*math.cos(a),.94*math.sin(a),.32),(.24,.20,.16),'dark',(0,0,a))
        if index==22:
            for i in range(3):
                a=i*math.tau/3
                d.ring('Peripheral orb split joint',(.81*math.cos(a),.81*math.sin(a),.50),.44,.018,'bronze')
        d.feature('Ellipsoid-following panel seams, field regulators and segmented foundation')
    elif index == 15:
        d.shell('Repair drum replaceable skins',[(.05,.83),(.6,.83),(1.2,.83),(1.8,.83),(2.20,.83)],20,'violet')
        for a in [0,math.pi/2,math.pi,math.pi*1.5]:
            p=(.86*math.cos(a),.86*math.sin(a),1.25)
            d.vent('Repair drum heat exchanger',p,.26,.70,12,a+math.pi/2)
        d.hatch('Repair roof hoist hatch',(0,0,2.51),.24)
        d.ladder(.32,-.81,.10,2.30)
        d.feature('Repair drum panel bays, large heat exchangers and roof hoist hatch')
    elif index == 16:
        for z in [.2,.8,1.4,2.0,2.6]:
            for side in [-1,1]:
                d.rod('Sensor lattice diagonal',(side*.18,-.05,z),(-side*.14,-.05,z+.50),.014)
        d.pipe('Sensor waveguide',[(.10,-.12,.12),(.10,-.12,2.95),(0,0,3.14)],.014,'bronze')
        d.disc('Sensor top receiver',(0,0,3.4),.13,.06,'gold')
        d.feature('Open lattice bracing, waveguide and receiver package')
    elif index == 19:
        d.shell('Air main replaceable panels',[(.65,.90),(1.08,.92),(1.65,.79),(2.21,.67)],24,'alloy',(0,.32))
        d.shell('Air auxiliary replaceable panels',[(.35,.52),(.80,.49),(1.24,.47)],20,'alloy',(-.4,-.52))
        d.ring('Air processor inspection flange',(0,.32,1.10),.90,.024,'edge')
        d.dome('Air cap plates',.61,.35,2.26,'bronze',(0,.32),4,20)
        d.vent('Air intake grille',(-.4,-1.02,.75),.30,.34,8)
        d.vent('Air exhaust grille',(.38,-.45,1.45),.23,.29,7)
        d.pipe('Air pressure instrument loop',[(-.79,-.55,.34),(-.79,-.55,1.10),(-.45,-.55,1.25)],.025,'bronze')
        d.feature('Filtration grilles, inspection flanges and pressure instrumentation')
    elif index == 20:
        d.dome('CPU command dome segmented skin',1.45,.9,.52,'gold',rings=7,sectors=32)
        d.radial_windows(1.50,.28,32,height=.08)
        for i in range(5):
            a=math.radians(18)+i*math.tau/5
            x,y=1.82*math.cos(a),1.82*math.sin(a)
            d.bolts('CPU pod roof bolt',.34,.755,10,(x,y),.018)
            d.hatch('CPU pod roof lock',(x,y,.81),.12)
            d.pipe('CPU pod conduit',[(x*.75,y*.75,.36),(x*.90,y*.90,.49),(x,y,.50)],.030,'bronze')
        d.ladder(.34,-1.52,.08,.54)
        d.feature('CPU dome armour tessellation, drum glazing and individually equipped peripheral pods')
    elif index == 21:
        # The large sloping hull receives panels aligned with its actual slope.
        for x in [-.72,-.36,0,.36,.72]:
            d.rod('Seismic roof standing seam',(x,-.96,.52),(x,.94,1.25),.013,'bronze')
        for x in [-.3,.3]:
            d.ring('Seismic service hatch clamp',(x,.30,.977),.17,.02,'edge')
        d.vent('Seismic cooling grille',(0,-1.025,.48),.66,.28,7)
        d.box('Seismic sensor aperture',(0,-1.045,.26),(.45,.06,.11),'dark')
        d.feature('Slope-following roof joints, service clamps, cooling grille and sensor aperture')
    elif index == 23:
        d.shell('Reactor plinth armour',[(.02,1.13),(.15,1.21),(.45,.73)],24,'alloy')
        d.ring('Reactor deck expansion joint',(0,0,.91),.92,.025,'dark')
        for i in range(6):
            a=i*math.tau/6
            x,y=.68*math.cos(a),.68*math.sin(a)
            d.ring('Reactor coolant vessel clamp',(x,y,1.23),.27,.02,'bronze')
            d.pipe('Reactor cooling return',[(x,y,1.05),(x*1.2,y*1.2,.82),(x*1.2,y*1.2,.41)],.024)
        d.hatch('Reactor core service',(0,0,1.45),.10)
        d.feature('Reactor vessel tension bands, closed cooling returns and segmented plinth')
    elif index == 24:
        d.shell('Command cylindrical armour',[(.02,.77),(.65,.77),(1.3,.77),(1.95,.77),(2.3,.77)],24,'alloy')
        d.radial_windows(.79,1.45,24,height=.12)
        d.hatch('Command roof service',(0,0,2.61),.14)
        for i in range(3):
            a=i*math.tau/3
            x,y=.95*math.cos(a),.95*math.sin(a)
            d.box('Command fin edge cap',(x,y,2.34),(.36,.39,.075),'bronze',(0,0,a))
            for z in [.35,.95,1.55]:
                d.box('Command fin equipment inset',(x+.19*math.sin(a),y-.19*math.cos(a),z),(.20,.035,.20),'dark',(0,0,a))
        d.feature('Command armour bays, wraparound glazing and equipped structural fins')
    elif index == 25:
        d.shell('Shipyard retaining wall plates',[(.05,1.36),(.20,1.36),(.40,1.35),(.50,1.30)],32,'bronze')
        for i in range(12):
            a=i*math.tau/12
            d.box('Shipyard deck grating',(.93*math.cos(a),.93*math.sin(a),.215),(.25,.17,.025),'dark',(0,0,a))
        for x in [-.6,.6]:
            for z in [.35,.65,.95]:
                d.rod('Crane tower lattice',(x-.08,0,z),(x+.08,0,z+.28),.016)
                d.rod('Crane tower lattice',(x+.08,0,z),(x-.08,0,z+.28),.016)
        d.rod('Crane hoist cable',(.20,0,1.19),(.20,0,.55),.009,'dark')
        d.ring('Crane lifting eye',(.20,0,.51),.055,.014,'edge',(0,1,0))
        d.box('Shipyard docking cradle',(0,-.30,.3),(.70,.65,.15),'alloy')
        d.feature('Shipyard wall plating, grating, crane lattice, hoist and docking cradle')
    elif index == 26:
        for x in [-.90,-.45,0,.45,.90]:
            d.box('Landing deck joint',(x,0,.204),(.012,1.79,.008),'dark',bevel=0)
        for y in [-.90,-.45,0,.45,.90]:
            d.box('Landing deck cross joint',(0,y,.205),(1.79,.012,.008),'dark',bevel=0)
        for x in [-1.04,1.04]:
            for y in [-.9,-.6,-.3,0,.3,.6,.9]:
                d.box('Pad guide light',(x,y,.1675),(.065,.045,.045),'light')
        for x in [-.8,.8]:
            d.hatch('Pad hydraulic service',(x,.80,.205),.085)
        d.feature('Individually jointed landing deck, guide lights and hydraulic service covers')
    elif index == 32:
        for i in range(3):
            z=.45+i*.80
            d.shell('Refuelling reservoir panels',[(z-.19,.50),(z,.50),(z+.19,.50)],20,'alloy')
            d.ring('Refuelling reservoir tension band',(0,0,z+.20),.515,.022,'bronze')
        for x in [-.29,.29]:
            d.pipe('Refuelling delivery manifold',[(x,-.4,.16),(x,-.4,2.5),(0,-.4,2.58)],.026,'bronze')
        d.hatch('Fuel pressure gauge',(.5,-.43,.80),.12,(0,-1,0),'gold')
        d.feature('Reservoir plate jackets, tension bands, delivery manifolds and pressure gauge')
    elif index == 34:
        d.dome('Medical dome manufactured skin',.95,.60,.4,'alloy',rings=5,sectors=24)
        d.ring('Medical dome structural belt',(0,0,.48),.96,.03,'edge')
        d.box('Medical entry pressure vestibule',(0,-1.0,.36),(.43,.30,.44),'alloy')
        d.box('Medical entry glazing',(0,-1.16,.42),(.28,.025,.23),'glass')
        for x in [-.4,.4]:
            d.ring('Medical side tank clamp',(x,-1.0,.37),.24,.025,'edge')
            d.pipe('Medical side gas supply',[(x,-1,.62),(x,-.8,.68),(x,-.65,.55)],.020,'blue')
            d.ring('Medical gas vessel service flange',(x,-1,.67),.20,.015,'bronze')
            d.bolts('Medical gas vessel flange fastener',.20,.675,6,(x,-1),.014)
        d.feature('Medical dome panelwork, glazed pressure vestibule and side gas supply')
    elif index == 35:
        for level in range(3):
            z=.5+level*.60
            d.shell('Circulation disc skins',[(z,.61),(z+.1,.92),(z+.26,.94),(z+.45,.55)],24,'violet')
            d.ring('Circulation disc pressure seal',(0,0,z+.12),.93,.018,'dark')
            d.radial_windows(.925,z+.20,18,height=.06)
            d.hatch('Circulation disc top access',(.35,0,z+.43),.09)
        d.feature('Segmented circulation discs, pressure seals and wraparound equipment windows')
    elif index == 36:
        for i in range(18):
            a=i*math.tau/18
            points=[]
            for j in range(17):
                phi=j*math.pi/32
                points.append((1.16*math.cos(phi)*math.cos(a),1.16*math.cos(phi)*math.sin(a),.2+.86*math.sin(phi)))
            d.pipe('Leisure canopy glazing mullion',points,.012,'bronze')
        d.ring('Leisure canopy perimeter gasket',(0,0,.22),1.16,.03,'dark')
        d.box('Leisure entry pressure vestibule',(0,-1.10,.40),(.54,.60,.50),'alloy')
        d.box('Leisure entry pressure door',(0,-1.415,.40),(.38,.025,.38),'glass')
        for x in [-.75,.75]:
            d.vent('Leisure annex air conditioning',(x,-1.03,.33),.30,.20,5)
        d.feature('Canopy glazing mullions, pressure door and annex air conditioning')
    elif index == 37:
        # Preserve the existing triangulated dome instead of burying its frame under a generic skin.
        for x in [-.81,.81]:
            d.ring('Hydroponic annex vessel band',(x,-1.52,.30),.25,.022,'edge')
            d.pipe('Hydroponic nutrient feed',[(x,-1.52,.18),(x,-1.28,.18),(x*.65,-1.10,.31)],.025,'blue')
            d.hatch('Hydroponic nutrient valve',(x,-1.77,.30),.075,(0,-1,0),'bronze')
        d.box('Hydroponic annex airlock',(0,-2.075,.27),(.30,.07,.32),'dark')
        d.vent('Hydroponic climate unit',(.35,-2.065,.36),.25,.20,5)
        d.feature('Nutrient feed network, annex airlock and dedicated climate unit')
    elif index == 38:
        d.shell('Hydration segmented bell shell',[(1.69,1.02),(1.90,1.01),(2.16,.87),(2.42,.69),(2.50,.58)],32,'alloy')
        d.ring('Hydration bell pressure flange',(0,0,1.73),1.02,.025,'edge')
        for i in range(8):
            a=i*math.tau/8
            d.disc('Hydration column foot',(.88*math.cos(a),.88*math.sin(a),.07),.12,.08,'dark')
            d.ring('Hydration filter column clamp',(.68*math.cos(a),.68*math.sin(a),1.1),.082,.018,'bronze')
        for z in [.23,.60,1.15,1.45]:
            d.ring('Reservoir external pressure band',(0,0,z),.62,.026,'bronze')
        d.pipe('Hydration return riser',[(-.63,0,.15),(-.63,0,1.45),(-.81,0,1.65)],.025,'blue')
        d.feature('Bell shell plates, pressure flanges, column feet and reservoir return riser')
    else:
        raise ValueError('Missing specific Terran detail recipe '+str(index))
