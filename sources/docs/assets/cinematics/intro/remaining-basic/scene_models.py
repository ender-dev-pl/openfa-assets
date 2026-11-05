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
