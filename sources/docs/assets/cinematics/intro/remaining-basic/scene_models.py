"""Scene definitions are added in chronological, committed milestones. Basic pass only."""
import blockout_tools as T
from mathutils import Vector
import math

def transmissions(info):
 if info['id'].startswith('E'):T.signal(info);return
 s=T.SCENE;c=T.camera((3,-11,2.9),(0,0,4.5),42);T.background('red');T.light('cool face key',(-4,-4,8),700,(.38,.45,.64));T.light('red rim',(4,2,7),950,(.6,.12,.16));a=T.human('broadcast officer',uniform=(.045,.065,.063),skin=(.23,.22,.28));T.talk(a,448,604)
 for n,z in [(448,-.20),(510,.10),(555,-.09),(604,.08)]:T.key(a['head'],'rotation_euler',n,(0,.03,z))
 for n,loc,target in [(448,(3,-11,2.9),(0,0,4.5)),(554,(3,-11,2.9),(0,0,4.5)),(555,(2,-7.3,4.0),(0,0,5.15)),(604,(2,-7.3,4.0),(0,0,5.15))]:
  T.key(c,'location',n,loc);T.key(c,'rotation_euler',n,(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler())
 for fc in c.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'

BUILDERS={'transmissions':transmissions}

def head_only(actor,z=2):
 keep={actor['root'],actor['head'],*actor['head'].children_recursive}
 for obj in list(T.SCENE.objects):
  if obj.name.startswith(T.PREFIX+' / '+actor['root'].name.split(' / ')[-1]) and obj not in keep:T.bpy.data.objects.remove(obj,do_unlink=True)
 actor['head'].location.z=z

def portraits(info):
 ident=info['id'];T.light('portrait key',(-4,-5,8),900,(1,.78,.55));T.light('portrait fill',(4,-2,5),350,(.50,.55,1))
 gold=T.material('aged frame gold',(.38,.23,.06),.75,.4)
 if ident=='H1':
  T.camera((3,-10,2.2),(0,0,1.5),45);T.curtains();a=T.human('bronze bust',skin=(.38,.24,.09),bronze=True);head_only(a,2);T.tube('bust neck',(0,0,.4),(0,0,1.4),.28,gold);T.cube('bust plinth',(0,0,.28),(1.4,.8,.10),gold);T.torus('plinth rim',(0,0,.42),1.15,.09,gold)
  T.key(a['head'],'rotation_euler',642,(0,0,-.9));T.key(a['head'],'rotation_euler',677,(0,0,.35));portrait_caption('Parrilo Salaria')
 elif ident=='H2':
  T.camera((0,-12,2.2),(0,0,2.2),ortho=12.2);wall=T.material('damask wall',(.10,.022,.06));T.panel('portrait wall',(0,2,2.2),18,8,wall);velvet=T.material('portrait painted ground',(.065,.018,.025));T.panel('portrait canvas proxy',(0,.9,2.2),3.3,4.7,velvet)
  a=T.human('Marcissus portrait',scale=.67,uniform=(.28,.26,.24),skin=(.37,.25,.17),hair=(.10,.055,.035),cape=(.22,.025,.025))
  for x in [-1.75,1.75]:T.cube('portrait frame upright',(x,-.6,2.2),(.095,.09,2.4),gold)
  for z in [-.2,4.6]:T.cube('portrait frame crossbar',(0,-.6,z),(1.84,.09,.09),gold)
  for x in [-1.75,1.75]:
   for z in [-.2,4.6]:T.torus('frame corner flourish',(x,-.61,z),.16,.045,gold,vertical=True)
  portrait_caption('Marcissus Salaria')
 elif ident=='H3':
  T.camera((0,-12,2.7),(0,0,2.7),ortho=10);a=T.human('Lynn cameo',skin=(.42,.31,.25),hair=(.38,.37,.34));head_only(a,2.8);dress=T.material('cameo pale collar',(.32,.36,.32));T.ball('cameo shoulders',(0,.1,1.35),(.85,.35,.56),dress);T.tube('cameo neck',(0,0,1.4),(0,0,2.2),.23,a['skin']);rim=T.material('cameo dark blue rim',(.006,.015,.05),.3,.4);T.torus('cameo ring',(0,.1,2.7),1.65,.12,rim,vertical=True)
  for i in range(12):
   angle=i*2*math.pi/12;flower=T.material('cameo petal '+str(i),(.12,.015,.24) if i%2 else (.01,.045,.23),emit=.5);T.ball('cameo flower '+str(i),(1.75*math.cos(angle),-.05,2.7+1.75*math.sin(angle)),(.24,.10,.15),flower)
  portrait_caption('Lynn Salaria')
 else:
  T.camera((5,-11,4.8),(0,0,4.9),45);T.background('sky');a=T.human('Dramon admiral',uniform=(.065,.018,.12),skin=(.36,.23,.12),hair=(.04,.025,.02),cape=(.045,.16,.055),hat=True);green=T.material('admiral green sash',(.07,.19,.08));T.polygon('admiral sash',[(-1.1,-.52,4.1),(-.25,-.55,4.1),(.95,-.55,2.1),(.1,-.56,2.1)],[(0,1,2,3)],green);portrait_caption('Dramon Salaria')

BUILDERS['portraits']=portraits

def portrait_caption(text):
 o=T.caption(text);cam=T.SCENE.camera
 if cam.data.type=='ORTHO':o.data.size*=cam.data.ortho_scale/6.4;o.location.y=-cam.data.ortho_scale*(262/640)*.45
 return o

def blast(name,loc,start,parent=None,size=1):
 root=T.empty(name,loc,parent);orange=T.material(name+' orange',(1,.12,.006),worn=False,emit=3);hot=T.material(name+' hot',(1,.65,.12),worn=False,emit=4)
 for i in range(7):
  angle=i*2.4;T.ball(name+' lobe '+str(i),(.5*math.cos(angle),.4*math.sin(angle),.23*(i%3)),(.55,.48,.5),hot if i%3==0 else orange,root,1)
 for n,s in [(start-1,.001),(start+1,size),(start+5,size*.75),(start+11,.001)]:T.key(root,'scale',n,(s,)*3)
 return root

def battle(info):
 if info['id']=='I':
  c=T.camera((16,-24,9),(0,0,3),45);T.stars(91);T.light('warship key',(-8,-10,12),3000,(.5,.6,.65),8);T.light('warship rim',(6,6,10),900,(.3,.4,.3),7);hull=T.material('worn warship green',(.035,.065,.045),.35,.65);dark=T.material('hull vents',(.003,.006,.005));steel=T.material('turret steel',(.09,.12,.13),.7,.4);ship=T.empty('capital ship',(0,0,3));verts=[]
  for y,w,z in [(-5,.3,.1),(-4,1.3,.55),(-1,1.8,.8),(3,1.5,.65),(5,.85,.25)]:verts.extend([(-w,y,-.45),(w,y,-.45),(w,y,z),(-w,y,z)])
  faces=[(0,3,2,1),(16,17,18,19)]
  for j in range(4):
   for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
  T.polygon('capital ship hull',verts,faces,hull,ship)
  for y in [-2.8,-1.8,-.8,.2,1.2,2.2]:
   for side in [-1,1]:
    w=1.3+(y+4)*.5/3 if y<=-1 else 1.8-(y+1)*.3/4
    vent=T.cube('diagonal hull vent',(side*(w+.025),y,-.1),(.025,.28,.19),dark,ship,.01);vent.rotation_euler.x=-.55
  for x in [-.65,.65]:
   for y in [.4,1.4,2.4]:T.ball('dorsal turret',(x,y,.78),(.35,.36,.25),steel,ship);T.tube('turret barrel',(x,y,.9),(x,y-.75,1),.055,steel,ship)
  for n,pos in [(792,(0,1,3)),(910,(0,0,3)),(957,(1,-2,3))]:T.key(ship,'location',n,pos)
  for n in [868,890,939]:blast('hull impact '+str(n),(-1.5,-2,.25),n,ship,1.3)
  fighter=T.empty('passing small attacker');T.cube('attacker fuselage',(0,0,0),(.3,2.5,.20),steel,fighter);T.polygon('attacker wings',[(-3,1,0),(0,-1,0),(3,1,0),(0,2,0)],[(0,1,2,3)],steel,fighter)
  for n,pos in [(906,(-10,8,7)),(916,(0,-9,6)),(924,(18,-35,3))]:T.key(fighter,'location',n,pos)
  for n,loc in [(792,(16,-24,9)),(916,(16,-24,9)),(917,(9,-14,6)),(957,(9,-14,6))]:T.key(c,'location',n,loc);T.key(c,'rotation_euler',n,(Vector((0,0,3))-Vector(loc)).to_track_quat('-Z','Y').to_euler())
  for fc in c.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='CONSTANT'
 else:
  T.camera((0,-15,2.2),(0,0,2.6),45);T.light('escape warm key',(-3,-3,9),1000,(1,.7,.4));ground=T.material('escape ground',(.09,.10,.025));T.cube('escape ground',(0,2,-.3),(18,18,.3),ground);rock=T.material('escape rock',(.10,.055,.10));T.ball('large broken rock',(5,8,4),(9,3,6),rock,sub=1);a=T.human('escaping figure',uniform=(.045,.09,.045),skin=(.31,.22,.15));cloud=blast('escape explosion',(3,6,2),960,size=5)
  for n in range(959,978,2):
   phase=(n-959)*.9;T.key(a['root'],'location',n,(0,(n-959)*.18,.25+.22*abs(math.sin(phase))))
   for i,leg in enumerate(a['legs']):T.key(leg,'rotation_euler',n,(.7*math.sin(phase+i*math.pi),0,0))
   for i,arm in enumerate(a['arms']):T.key(arm,'rotation_euler',n,(-.65*math.sin(phase+i*math.pi),0,0))

BUILDERS['battle']=battle

def council(info):
 T.light('council warm key',(-4,-5,9),1300,(1,.63,.35),6);T.light('council fill',(5,-2,7),600,(.55,.50,.75));T.curtains((.18,.055,.012));gold=T.material('council old gold',(.35,.18,.035),.7,.42);stone=T.material('council table green marble',(.12,.16,.09),.15,.55);T.ball('oval council table',(0,-.6,2.3),(4,2.5,.18),stone);T.tube('table pedestal',(0,-.6,.1),(0,-.6,2.3),.75,stone);T.cube('throne back',(0,2.4,2.9),(1.1,.2,2.1),gold)
 hero=T.human('seated admiral',loc=(0,1.4,0),scale=.8,uniform=(.07,.018,.12),skin=(.35,.23,.13),hair=(.04,.025,.02),cape=(.055,.16,.055),hat=True)
 for leg in hero['legs']:leg.rotation_euler.x=-1.1
 for arm in hero['arms']:arm.rotation_euler.x=-1.0
 for x in [-2.5,2.5]:T.human('standing guard '+str(x),loc=(x,2,0),scale=.86,uniform=(.025,.07,.04),skin=(.30,.23,.17),hair=(.025,.02,.02))
 for a in [-1,1]:
  tube=T.tube('throne crest ray',(0,3,4.6),(a*2.3,3,6),.065,gold)
 T.torus('throne crest ring',(0,3,5.4),1.05,.06,gold,vertical=True)
 paper=T.material('document yellow paper',(.56,.35,.055),rough=.95,worn=False);ink=T.material('placeholder document strokes',(.012,.008,.002),worn=False);T.cube('document',(0.8,-.7,2.51),(.67,.85,.008),paper,bevel=.01)
 for row in range(8):
  for col in range(5):T.cube('unreadable document mark',(.31+col*.21,-.12-row*.17,2.525),(.065,.013,.003),ink,bevel=0)
 pen=T.tube('signing stylus',(.36,-.1,-1.15),(.36,-.25,-1.78),.027,ink,hero['arms'][1]);T.talk(hero,info['source_start'],info['source_end'])
 if info['id']=='K':
  T.camera((-6,-13,5.4),(0,1,3),45);fore=T.human('foreground witness',loc=(-6.0,-3.7,0),scale=.95,uniform=(.04,.065,.075),skin=(.20,.25,.28));fore['root'].rotation_euler.z=math.pi;white=T.material('witness white collar',(.40,.46,.48));T.cube('witness collar',(0,0,4.37),(1.0,.5,.15),white,fore['root'])
 else:
  T.camera((-4,-9,8.5),(0,.3,4.0),36);T.key(hero['head'],'rotation_euler',1073,(.14,0,-.1));T.key(hero['head'],'rotation_euler',1147,(.2,0,.1))
  for n in range(1073,1148,4):T.key(hero['arms'][1],'rotation_euler',n,(-1.0,.06,.08*math.sin(n*.55)))

BUILDERS['council']=council

def alien_body(info):
 root=T.empty('alien speaker');armor=T.material('alien banded armor',(.10,.055,.11),.35,.5);skin=T.material('alien dark green',(.025,.085,.055),.15,.65);band=T.material('alien copper purple bands',(.26,.13,.18),.5,.45);eye=T.material('alien eyes',(.28,.5,.07),worn=False,emit=.4)
 T.ball('alien torso',(0,.1,2.5),(1.35,.7,1.3),armor,root)
 for side in [-1,1]:
  T.ball('alien shoulder',(side*1.4,.1,3.2),(.85,.65,.75),armor,root)
  for i in range(4):T.torus('shoulder armor band',(side*1.4,.1,2.8+i*.22),.61,.065,band,root)
  for j in range(3):T.tube('back spine',(side*(.9+j*.22),.5,3.8),(side*(1.35+j*.33),.7,4.8-j*.15),.08,skin,root)
 head=T.empty('alien head',(0,0,4.6),root);T.ball('alien face',(0,-.18,-.15),(.76,.59,.8),skin,head)
 rings=[(-.2,.78,.54),(.45,1.35,.72),(.85,1.06,.63),(1.25,.25,.23)];verts=[]
 for z,rx,ry in rings:
  for i in range(12):a=i*math.tau/12;verts.append((rx*math.cos(a),ry*math.sin(a),z))
 faces=[]
 for j in range(3):
  for i in range(12):faces.append((j*12+i,j*12+(i+1)%12,(j+1)*12+(i+1)%12,(j+1)*12+i))
 faces.extend([tuple(range(11,-1,-1)),tuple(range(36,48))]);T.polygon('flared alien helmet',verts,faces,skin,head)
 for side in [-1,1]:
  T.tube('helmet horn',(side*.9,.1,.7),(side*1.5,.15,1.45),.1,skin,head);T.ball('glowing alien eye',(side*.30,-.73,-.18),(.18,.04,.10),eye,head)
 jaw=T.empty('alien jaw',(0,-.25,-.65),head);T.ball('alien chin',(0,-.13,0),(.55,.4,.22),skin,jaw)
 for i in range(5):T.cube('chest band',(0,-.66,2.15+i*.25),(1.05,.045,.055),band,root,.02)
 T.talk(dict(jaw=jaw),info['source_start'],info['source_end'])
 for n,v in [(info['source_start'],(0,0,-.10)),(info['source_end'],(.04,0,.10))]:T.key(head,'rotation_euler',n,v)
 return root

def alien(info):
 if info['id'] in ['E3','E4']:
  # Standalone generated interference bridges, keeping original cut timing.
  T.signal(info);return
 T.background('space').scale.x=3;T.light('alien green rim',(-4,2,8),1000,(.25,.75,.40));T.light('alien face key',(1,-6,7),1000,(.65,.70,.52));alien_body(info)
 loc,target,lens={'M':((3,-12,5.4),(0,0,4),38),'N':((8,-9,5),(0,0,4.2),42),'O':((1.5,-8,5),(0,0,4.75),42)}[info['id']];T.camera(loc,target,lens)

BUILDERS['alien']=alien

def laboratory(info):
 blue=T.material('lab blue enamel',(.045,.16,.25),.35,.4);white=T.material('lab pale metal',(.43,.55,.57),.5,.4);pipe=T.material('lab green conduits',(.035,.21,.17),.3,.5);dark=T.material('lab wall',(.035,.04,.045),.2,.7);T.light('lab ceiling',(0,-2,10),2200,(.65,.8,1),12);T.light('lab side',(10,-5,7),1000,(.8,.85,.65),7)
 if info['id']=='P':
  T.panel('lab rear wall',(0,4,4),72,13,dark);T.light('scientist fill',(13,-5,8),900,(.8,.85,.7),6)
  for z in range(0,10):T.tube('wall seam',(-18,3.94,z),(18,3.94,z),.016,white)
  T.cube('long laboratory bench',(0,1,1.3),(14,1,.25),blue);T.cube('bench pale worktop',(0,1,1.59),(14,1.1,.07),white)
  for x in [-9,-4,1,6,11]:T.cube('lab bench support',(x,1,.5),(.20,.65,.75),blue)
  for x in [-8,0,8]:
   for side in [-1,1]:
    prev=None
    for i in range(49):
     z=1.7+i*.12;a=i*.24+(0 if side==1 else math.pi);point=(x+.58*math.cos(a),1+.58*math.sin(a),z)
     if prev:T.tube('double helix strand',prev,point,.12,white)
     prev=point
     if side==1 and i%3==0:T.tube('double helix rung',(x-.58*math.cos(a),1-.58*math.sin(a),z),point,.055,pipe)
  for z in [6.2,6.5]:
   T.tube('overhead conduit',(-18,3,z),(15,3,z),.10,pipe);T.tube('conduit elbow',(15,3,z),(16,2,z-1),.10,pipe)
  for x in [-11,-3,5]:
   T.tube('apparatus foot',(x,.5,1.7),(x,.5,2.2),.65,blue);T.tube('apparatus chamber',(x,.5,2.2),(x,.5,4.5),.35,blue)
   for z in [2.3,3,3.7,4.4]:T.torus('apparatus chamber ring',(x,.5,z),.38,.07,white)
  a=T.human('laboratory scientist',loc=(13,0,0),scale=.85,uniform=(.085,.14,.075),skin=(.34,.25,.18),hair=(.025,.02,.02))
  for arm in a['arms']:arm.rotation_euler.x=-1.15
  T.cube('scientist handheld pad',(13,-1.05,2.8),(.60,.10,.36),blue)
  c=T.camera((-8,-11,4.6),(-7,1,3.8),40)
  for n,x in [(1493,-8),(1663,12)]:
   loc=Vector((x,-11,4.6));target=Vector((x+1,1,3.8));T.key(c,'location',n,loc);T.key(c,'rotation_euler',n,(target-loc).to_track_quat('-Z','Y').to_euler())
 else:
  T.panel('handheld view floor',(0,4,3),25,14,dark)
  for x in range(-12,13,2):T.tube('floor panel seam',(x,3.9,-3),(x,3.9,10),.02,white)
  c=T.camera((0,-10,4),(0,0,3),42);pad=T.empty('handheld display');screen=T.material('screen green',(.10,.18,.12),worn=False,emit=.5);T.cube('pad housing',(0,.1,3),(1.7,.18,.95),blue,pad);T.panel('pad screen',(0,-.10,3),2.4,1.5,screen,pad)
  for side in [-1,1]:
   grip=T.torus('green oval grip',(side*1.65,-.1,3),.65,.13,pipe,pad,True);grip.scale.x=.40
   for j in range(7):T.ball('pad key',(side*1.4,-.15,2.45+j*.17),(.045,.025,.045),white,pad)
   T.tube('green sleeve',(side*3,-2,1),(side*2,-.5,2.5),.32,pipe);T.tube('bare forearm',(side*2,-.5,2.5),(side*1.7,-.2,3.2),.16,T.material('operator skin',(.34,.24,.17)));T.ball('gripping hand',(side*1.64,-.23,3.2),(.18,.15,.24),T.material('hand skin',(.34,.24,.17)))
  a=T.human('display portrait',loc=(0,-.3,1.4),scale=.6,uniform=(.13,.12,.08),skin=(.42,.30,.18),hair=(.27,.22,.14));head_only(a,2)
  # The screen portrait is authored 3D proxy geometry, not a legacy bitmap.
  a['root'].parent=pad;a['root'].location=(0,-.31,1.8)
  T.key(pad,'rotation_euler',1665,(0,-.025,-.05));T.key(pad,'rotation_euler',1730,(0,.025,.04))

BUILDERS['laboratory']=laboratory
