"""Authored volumetric recipes based on inspected original ICONS.256 frames.

Names describe visible motifs where command semantics have not been established.
No source image pixels, contours or textures are loaded by this module.
"""
import math
import bpy
from mathutils import Matrix
import legacy_shapes as g

blue=g.blue;white=g.white;silver=g.silver;gold=g.gold;dark=g.dark;red=g.red
green=g.material('Used green enamel',(.12,.46,.18),.22,.4)
orange=g.material('Orange warning enamel',(.85,.19,.025),.28,.4)
yellow=g.material('Worn amber markings',(.96,.60,.12),.28,.4)


def place(make,x=0,y=0,scale=1,angle=0,z=0):
    first=len(g.parts);make()
    matrix=Matrix.Translation((x,y,z)) @ Matrix.Rotation(angle,4,'Z') @ Matrix.Diagonal((scale,scale,scale,1))
    for obj in g.parts[first:]:obj.matrix_world=matrix @ obj.matrix_world


def stroke(points,mat=blue,r=.065,z=.19):
    data=bpy.data.curves.new('Raised round trace','CURVE');data.dimensions='3D'
    data.bevel_depth=r;data.bevel_resolution=3
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,(x,y) in zip(spline.points,points):p.co=(x,y,z,1)
    obj=bpy.data.objects.new('Raised round trace',data);g.scene.collection.objects.link(obj)
    return g.finish(obj,mat,obj.name)


def ellipse(x=0,y=0,rx=.6,ry=None,mat=blue,r=.055,z=.19,start=0,end=math.tau):
    ry=rx if ry is None else ry
    return stroke([(x+rx*math.cos(start+(end-start)*i/64),y+ry*math.sin(start+(end-start)*i/64)) for i in range(65)],mat,r,z)


def arrow(direction=0,mat=blue):
    xy=[(-.86,-.14),(.27,-.14),(.27,-.48),(.88,0),(.27,.48),(.27,.14),(-.86,.14)]
    c=math.cos(direction);s=math.sin(direction)
    return g.poly('Bevelled direction arrow',[(x*c-y*s,x*s+y*c) for x,y in xy],mat,.1,.12)


def bent_arrow(mat=blue):
    g.poly('Bent return arrow',[(-.90,-.12),(-.30,-.58),(-.30,-.28),(.58,-.28),(.58,.75),(.24,.75),(.24,.05),(-.30,.05),(-.30,.38)],mat,.12,.13)


def uturn(mat=blue):
    ellipse(0,-.28,.66,.84,mat,.15,start=.08,end=math.pi-.08)
    for sign in [-1,1]:
        g.poly('Return arrow tip',[(sign*.95,-.20),(sign*.36,-.20),(sign*.65,-.65)],mat,.11,.12)


def plus(mat=blue):
    g.poly('Plus sign',[(-.2,-.8),(.2,-.8),(.2,-.2),(.8,-.2),(.8,.2),(.2,.2),(.2,.8),(-.2,.8),(-.2,.2),(-.8,.2),(-.8,-.2),(-.2,-.2)],mat,.12,.12)


def cross(mat=blue):
    stroke([(-.58,-.64),(.58,.64)],mat,.15)
    stroke([(-.58,.64),(.58,-.64)],mat,.15)


def check(mat=blue):
    g.poly('Check mark',[(-.85,-.12),(-.55,-.12),(-.23,-.40),(.50,.83),(.83,.71),(-.15,-.85)],mat,.12,.12)


def text(body,mat=blue,size=1):
    data=bpy.data.curves.new('Raised label '+body,'FONT')
    data.body=body;data.align_x='CENTER';data.align_y='CENTER';data.size=size
    data.extrude=.055;data.bevel_depth=.015
    obj=bpy.data.objects.new('Raised label '+body,data);g.scene.collection.objects.link(obj)
    obj.location.z=.12;g.finish(obj,mat,obj.name)


def coin():
    g.tube('Coin rim',(0,0,.02),(0,0,.19),.64,gold)
    g.tube('Coin worn face',(0,0,.19),(0,0,.24),.53,gold)
    ellipse(rx=.52,mat=gold,r=.025,z=.25)
    for i in range(24):
        a=math.tau*i/24
        stroke([(.58*math.cos(a),.58*math.sin(a)),(.63*math.cos(a),.63*math.sin(a))],gold,.013,.22)


def head():
    # Profile and nose are retained; not replaced by a generic front-facing user glyph.
    g.uv('Gold cranial shell',(.06,.13,.12),(.46,.59,.22),gold)
    g.poly('Face profile nose',[(-.25,.47),(-.48,.29),(-.43,.09),(-.68,-.01),(-.46,-.13),(-.46,-.36),(-.19,-.50),(.03,-.39),(.11,-.67),(.50,-.67),(.35,-.27)],gold,.13,.12)
    g.uv('Raised ear',(.18,-.02,.32),(.105,.15,.055),yellow)
    stroke([(-.31,.16),(-.22,.18)],dark,.027,.34)
    stroke([(-.48,-.24),(-.25,-.23)],dark,.025,.28)


def skull():
    g.uv('Skull cranium',(0,.24,.1),(.60,.70,.27),white)
    g.uv('Left cheek',(-.43,-.17,.15),(.20,.23,.16),silver)
    g.uv('Right cheek',(.43,-.17,.15),(.20,.23,.16),silver)
    for x in [-.26,.26]:g.uv('Deep eye socket',(x,.19,.33),(.20,.24,.075),dark)
    g.poly('Nasal cavity',[(-.12,-.20),(0,-.04),(.12,-.20),(.08,-.35),(-.07,-.35)],dark,.36,.02)
    g.box('Lower jaw',(0,-.50,.12),(.62,.23,.20),silver)
    for x in [-.24,-.08,.08,.24]:g.box('Individual worn tooth',(x,-.39,.32),(.11,.25,.09),white,.02)


def grid(mat=blue):
    for x in [-.65,-.22,.22,.65]:stroke([(x,-.66),(x,.66)],mat,.045,.1)
    for y in [-.66,-.22,.22,.66]:stroke([(-.88,y),(.88,y)],mat,.045,.1)
    for y in [-.42,.42]:stroke([(-1.0,y),(1.0,y)],mat,.045,.1)


def diamond_target(mat=blue):
    stroke([(0,.88),(.68,0),(0,-.88),(-.68,0),(0,.88)],mat,.075)
    for a,b in [((-1,0),(-.40,0)),((.40,0),(1,0)),((0,-1),(0,-.43)),((0,.43),(0,1))]:stroke([a,b],mat,.065)


def crosshair(mat=orange):
    ellipse(rx=.65,mat=mat,r=.065)
    for a,b in [((-1,0),(1,0)),((0,-1),(0,1))]:stroke([a,b],mat,.055)
    for x in [-.87,-.65,.65,.87]:stroke([(x,-.14),(x,.14)],mat,.035)


def craft():
    # Same triangular hull family as the study, with a slightly larger cockpit.
    g.craft(0,0,1.25)


def fleet():
    g.craft(-.24,-.18,1.05);g.craft(-.50,.63,.53)


def capsule():
    ellipse(rx=.75,ry=.43,mat=white,r=.085)
    ellipse(-.27,0,.20,.20,silver,.045)
    stroke([(.04,.13),(.44,.13)],gold,.045)
    stroke([(.04,-.13),(.44,-.13)],gold,.045)


def eyehand():
    g.poly('Cupped gold hand',[(-.9,-.40),(-.65,-.28),(-.40,-.37),(-.23,-.15),(.10,-.12),(.42,-.33),(.75,-.25),(.95,-.36),(.53,-.57),(.05,-.67),(-.57,-.60)],gold,.10,.13)
    stroke([(-.72,-.20),(-.85,.40),(-.45,.40)],blue,.075)
    stroke([(.72,-.20),(.85,.40),(.45,.40)],blue,.075)
    g.uv('Orbital eye',(0,.44,.13),(.36,.26,.16),blue)
    g.uv('Eye pale lens',(0,.47,.28),(.18,.16,.06),silver)
    stroke([(-.47,-.42),(.35,-.43)],dark,.025,.25)


def orbit_platform(kind='ship',down=False):
    g.uv('Gold orbital platform',(0,-.49,.03),(.92,.23,.10),gold)
    ellipse(0,-.49,.86,.16,gold,.045)
    if kind=='ship':place(craft,0,.29,.65,math.pi/4)
    elif kind=='satellite':
        g.uv('Satellite core',(0,.08,.13),(.28,.35,.18),silver)
        for x in [-.75,.75]:
            ellipse(x,.12,.19,mat=blue,r=.045)
            stroke([(x-.13,-.01),(x+.13,.25)],blue,.04)
        stroke([(-.75,.12),(.75,.12)],silver,.04,.05)
    elif kind=='dish':
        g.uv('Dish antenna',(0,.42,.16),(.19,.17,.10),silver)
        stroke([(0,.34),(0,-.35)],silver,.055)
        stroke([(0,.68),(0,.93)],white,.055)
    elif kind=='tower':
        g.box('Orbital tower',(0,.23,.13),(.20,1.00,.18),silver)
        g.uv('Tower cap',(0,.78,.12),(.30,.13,.13),white)
    if kind!='satellite':place(lambda:arrow(-math.pi/2 if down else math.pi/2),0,-.60,.48,z=.20)


def frame_card():
    stroke([(-.48,-.55),(-.48,.55),(.48,.55),(.48,-.55),(-.48,-.55)],blue,.075)
    for y in [-.19,.19]:g.box('Amber data mark',(0,y,.20),(.31,.12,.08),gold,.015)


def hook():
    ellipse(0,.47,.34,mat=white,r=.12)
    stroke([(0,.08),(-.12,-.19),(-.05,-.52),(.19,-.64),(.40,-.48),(.40,-.24)],white,.11)


def bomb():
    g.uv('Warning device body',(-.25,-.11,.10),(.66,.65,.23),orange)
    place(lambda:cross(yellow),-.25,-.11,.63,z=.16)
    stroke([(.16,.40),(.34,.86),(.63,.82),(.72,.43),(.83,.33)],white,.06)
    for a in [-.8,0,.8,1.6]:stroke([(.87+.12*math.cos(a),.29+.12*math.sin(a)),(.87+.26*math.cos(a),.29+.26*math.sin(a))],yellow,.025)


def tiles():
    corners=[(-.84,-.12),(-.12,.70),(.84,.19),(.08,-.64)]
    mid=[((corners[i][0]+corners[(i+1)%4][0])/2,(corners[i][1]+corners[(i+1)%4][1])/2) for i in range(4)]
    centre=(0,-.01)
    for i in range(4):
        quad=[corners[i],mid[i],centre,mid[(i-1)%4]]
        g.poly('Alternating board tile',quad,red if i%2 else blue,.12,.10)
        stroke(quad+[quad[0]],gold,.028,.20)


def profile_pair():
    place(head,-.56,0,.78)
    first=len(g.parts);place(head,.56,0,.78)
    for obj in g.parts[first:]:obj.matrix_world=Matrix.Scale(-1,4, (1,0,0)) @ obj.matrix_world
    # Reflection above mirrors the complete second profile; restore it to the right.
    for obj in g.parts[first:]:obj.location.x+=1.12


def gift():
    g.box('Gift crate',(0,-.10,.04),(1.18,1.10,.38),gold,.07)
    g.box('Vertical ribbon',(0,-.10,.27),(.13,1.15,.06),red,.02)
    g.box('Horizontal ribbon',(0,-.04,.28),(1.21,.13,.06),red,.02)
    ellipse(-.20,.69,.24,.15,red,.055,start=0,end=math.tau)
    ellipse(.20,.69,.24,.15,red,.055,start=0,end=math.tau)


def two_boxes():
    for x,y in [(-.28,-.25),(.28,.25)]:
        stroke([(x-.43,y-.42),(x-.43,y+.42),(x+.43,y+.42),(x+.43,y-.42),(x-.43,y-.42)],blue,.065)


def bolt():
    obj=g.poly('Lightning bolt',[(.18,.95),(-.58,-.10),(-.10,-.10),(-.28,-.95),(.58,.15),(.12,.15)],blue,.12,.13)
    obj.rotation_euler.z=math.radians(40)


def triangle(direction=0,size=1):
    points=[(-.68,-.60),(.72,0),(-.68,.60)]
    c=math.cos(direction);s=math.sin(direction)
    g.poly('Triangular scroll control',[(size*(x*c-y*s),size*(x*s+y*c)) for x,y in points],blue,.12,.12)


def icon(i):
    if i==0:bent_arrow()
    elif i==1:skull()
    elif i==2:arrow(math.pi)
    elif i==3:arrow()
    elif i==4:plus()
    elif i==5:g.box('Minus',(0,0,.12),(1.65,.35,.13),blue)
    elif i==6:uturn()
    elif i==7:text('i',blue,1.8)
    elif i==8:arrow(math.pi/2)
    elif i==9:arrow(-math.pi/2)
    elif i==10:g.construction()
    elif i==11:place(bolt,-.67,0,.70);place(coin,.33,0,.92)
    elif i==12:bomb()
    elif i==13:hook()
    elif i==14:grid();place(coin,.43,.27,.53,z=.15);place(coin,-.27,-.38,.30,z=.15)
    elif i in (15,16,17):
        if i==17:g.missile()
        else:
            place(craft if i==15 else fleet,-.23,0,.95)
            place(arrow,.66,-.04,.45,z=-.10)
    elif i==18:
        place(lambda:text('CRI',green,1.1),-.22,0,.90)
        stroke([(.53,-.45),(1.02,-.45),(.77,.43),(.53,-.45)],green,.055)
    elif i==19:eyehand()
    elif i==20:tiles()
    elif i==21:g.funds()
    elif i==22:diamond_target()
    elif i==23:capsule();place(arrow,-.88,0,.30);place(lambda:arrow(math.pi),.88,0,.30)
    elif i==24:profile_pair()
    elif i==25:head()
    elif i in (26,27):orbit_platform(down=i==27)
    elif i in (28,31,32):
        place(craft,-.45,0,.88);place(coin,.47,.13,.89,z=-.1)
        if i in (28,31):place(lambda:arrow(mat=green if i==31 else blue),.32,-.03,.46,z=.23)
        else:
            for y in [-.50,-.17,.16,.49]:g.box('Accounting bar',(.87,y,-.07),(.48,.20,.08),blue,.015)
    elif i==29:place(craft,-.51,-.10,.63);place(craft,.53,-.10,.63);place(craft,.33,.75,.30);place(arrow,0,-.05,.43)
    elif i in (30,49):place(craft,-.23,0,1.05);place(lambda:text('?',yellow,1.25),.82,-.02,.65)
    elif i==33:place(craft,.22,.10,1.05);stroke([(-.91,-.65),(-.17,.35)],silver,.085);place(arrow,-.50,-.06,.40)
    elif i in (34,61):place(craft,.32,.08,1.05);place(frame_card,-.71,-.12,.62);place(arrow,-.19,-.05,.36)
    elif i==35:place(craft,-.54,0,.70);place(craft,.42,0,.90);place(arrow,0,-.04,.45)
    elif i==36:place(craft,-.32,0,1.0);place(craft,.72,-.12,.55);place(arrow,.33,-.05,.43)
    elif i==37:place(craft,.44,.05,.90);place(lambda:text('?',yellow,1.25),-.81,-.05,.65);place(arrow,-.24,-.01,.55)
    elif i==38:place(craft,.20,0,1.05);place(bolt,-.72,.06,.74)
    elif i==39:gift()
    elif i==40:
        place(fleet,-.54,0,.68);place(fleet,.54,0,.68)
        stroke([(-.15,.83),(.13,.53),(-.12,.24),(.14,-.06),(-.12,-.35),(.14,-.70)],orange,.07)
    elif i in (41,42):
        place(fleet,-.31,-.03,.90);place(coin,.48,.05,.86,z=-.10)
        place(lambda:arrow(mat=red if i==42 else blue),.40,-.06,.47,z=.2)
    elif i==43:place(fleet,-.48,-.02,.77);place(fleet,.53,-.02,.74);place(lambda:arrow(mat=red),.05,-.05,.53,z=.2)
    elif i==44:place(fleet,-.28,-.04,.88);place(grid,.23,.13,.82,z=-.12);place(frame_card,.46,-.20,.65)
    elif i==45:
        place(fleet,-.42,0,.72)
        ellipse(.26,-.05,.60,.75,red,.065,start=-1.3,end=1.7)
        place(lambda:arrow(math.pi,red),.26,.66,.27)
    elif i==46:place(fleet,.24,-.05,.88);place(bolt,-.65,.05,.68)
    elif i==47:orbit_platform('satellite')
    elif i==48:place(head,-.47,0,.83);place(plus,.59,0,.58)
    elif i==50:orbit_platform('dish')
    elif i==51:
        crosshair();place(lambda:g.missile(False),0,0,.70)
    elif i==52:
        place(craft,-.62,0,.73);place(crosshair,.52,.02,.64)
        place(coin,.52,.02,.90,z=-.10)
        for y in [-.25,.05,.36]:stroke([(-1.12,y),(-.62,y)],silver,.035)
    elif i==53:
        ellipse(rx=.75,mat=gold,r=.075)
        for k,(mat,x,y) in enumerate([(green,-.25,-.23),(red,-.25,.23),(blue,.25,-.23),(white,.25,.23)]):
            g.poly('Four-colour marker sector',[(x-.21,y-.21),(x+.21,y-.21),(x+.21,y+.21),(x-.21,y+.21)],mat,.10,.08)
        stroke([(-.62,-.04),(.62,-.04)],dark,.045);stroke([(0,-.62),(0,.62)],dark,.045)
    elif i==54:place(craft,-.66,0,.62);place(coin,.36,0,.97);place(arrow,-.61,-.01,.45,z=.15)
    elif i==55:place(coin,.25,0,1.00);ellipse(-.55,.04,.22,mat=blue,r=.065)
    elif i==56:grid();g.box('Highlighted grid cell',(.22,-.22,.17),(.39,.39,.08),gold,.02)
    elif i==57:check()
    elif i==58:cross()
    elif i==59:
        ellipse(rx=.85,ry=.50,mat=white,r=.075)
        for x,y,a in [(-.24,.49,0),(.24,-.49,math.pi)]:place(lambda:arrow(a,gold),x,y,.68)
    elif i==60:place(lambda:text('i',blue,1.6),-.74,0,.90);place(coin,.34,0,.97)
    elif i==62:
        first=len(g.parts);place(head,-.37,0,.84)
        for o in g.parts[first:]:
            if o.data.materials:o.data.materials[0]=silver
        place(plus,.67,0,.55)
    elif i==63:orbit_platform('tower')
    elif i==64:
        # The construction wrench is separate from the diamond in frame 010.
        first=len(g.parts);g.construction()
        keep=[]
        for o in g.parts[first:]:
            if o.name.startswith(('Spanner shaft','Upper open spanner','Lower open spanner')):keep.append(o)
            else:bpy.data.objects.remove(o,do_unlink=True)
        g.parts[first:]=keep
        place(craft,.39,0,1.03)
    elif i in (65,66):
        place(coin,.45 if i==65 else -.45,0,.93)
        place(arrow,-.62 if i==65 else .62,0,.64)
    elif i==67:text('ABC',blue,.93)
    elif i==68:crosshair();place(lambda:orbit_platform('tower'),0,0,.68)
    elif i==69:place(head,-.44,0,.84);place(cross,.64,0,.61)
    elif i==70:
        place(head,-.43,0,.84)
        ellipse(.38,0,.14,mat=blue,r=.07)
        stroke([(.51,0),(1.00,0),(1.00,-.17),(.83,-.17),(.83,-.04)],blue,.075)
    elif i==71:place(lambda:craft(),-.46,0,.83,math.pi*.75);place(frame_card,.62,-.11,.67)
    elif i==72:place(coin,0,0,1.02,z=-.10);crosshair()
    elif i==73:craft()
    elif i==74:place(head,-.43,0,.84);place(uturn,.60,-.04,.54)
    else:raise ValueError(i)


NAMES=[
 'return','skull','left','right','plus','minus','return-arch','information','up','down',
 'wrench-diamond','bolt-coin','warning-device','hook','grid-coins','ship-arrow','fleet-arrow','missile-arrow','cria','eye-hand',
 'four-tiles','coin-ledger','diamond-target','capsule-arrows','two-profiles','profile','ship-orbit-up','ship-orbit-down','ship-coin-blue','ships-transfer',
 'ship-question-arrow','ship-coin-green','ship-coin-ledger','ship-bar','ship-card','two-ships-transfer','ship-small-ship','ship-question-left','ship-bolt','gift',
 'split-fleets','fleet-coin-blue','fleet-coin-red','fleets-red-transfer','fleet-grid-card','fleet-return','fleet-bolt','orbital-satellite','profile-plus','ship-question',
 'antenna-orbit','missile-reticle','moving-ship-target','four-colour-marker','ship-to-coin','coin-marker','grid-highlight','confirm','cancel','capsule-cycle',
 'information-coin','ship-card-alternate','silver-profile-plus','tower-orbit','wrench-ship','coin-input','coin-output','alphabet','tower-reticle','profile-cancel',
 'profile-key','ship-card-left','coin-reticle','ship','profile-return']

# Each group of three original CICONS/SCROLL frames is mask/normal/pressed.
CONTROLS=[('up',lambda:arrow(math.pi/2)),('down',lambda:arrow(-math.pi/2)),('lightning',bolt),('return',bent_arrow)]
SCROLL=[('up-large',lambda:triangle(math.pi/2)),('down-large',lambda:triangle(-math.pi/2)),
 ('up-small',lambda:triangle(math.pi/2,.68)),('down-small',lambda:triangle(-math.pi/2,.68)),
 ('left-small',lambda:triangle(math.pi,.68)),('right-small',lambda:triangle(0,.68)),
 ('cancel',cross),('confirm',check),('skull',skull),('overlap-a',two_boxes),('overlap-b',two_boxes),
 ('target',diamond_target),('left-large',lambda:triangle(math.pi)),('right-large',triangle)]
