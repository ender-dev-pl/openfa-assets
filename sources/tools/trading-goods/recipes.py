"""Per-item reference-guided recipes. Related variants share authored construction functions."""
import modelling as M
import math,random

def beverages(n):
 metal=M.mat('scuffed pewter',(.22,.25,.26),.75,.48);dark=M.mat('recessed bung',(.025,.025,.022),.3,.8);paper=M.mat('cream label',(.68,.58,.34),rough=.9);gold=M.mat('gold foil',(.52,.39,.06),.65,.32)
 if n==1:
  for i,(x,y) in enumerate([(-.65,.4),(.65,.45),(-.65,-.65),(.7,-.6)]):
   p=M.root('individual beer cask '+str(i),(x,y,0));M.lathe('tapered metal pressure cask',[(.40,0),(.45,.1),(.52,.95),(.52,1.05),(.43,1.9),(.34,2)],metal,p)
   for z,r in [(.06,.42),(.97,.53),(1.07,.52),(1.94,.35)]:M.ring('rolled cask seam',(0,0,z),r,.025,metal,p)
   M.cylinder('bung recess',(0,0,2.001),.11,.008,dark,p);M.label('inventory sticker',p,.47,.65,.2,.22,paper)
 elif n in [2,4,5]:
  colors={2:[(.24,.31,.11),(.35,.08,.09),(.10,.27,.12)],4:[(.24,.24,.10)]*3,5:[(.29,.37,.055)]*3}[n]
  for i,c in enumerate(colors):
   mat=M.mat('tinted bottle '+str(i),c,.05,.22,.25);p=M.bottle('separate beverage bottle '+str(i),((i-1)*.9,.15 if i!=1 else -.3,0),mat,gold,paper,height=3.3 if n==5 else 3.0)
   M.text('authored label typography',['VINTAGE','CREAM','CUVEE'][[2,4,5].index(n)],(0,-.397,1.05),.12,dark,p)
 elif n==3:
  c=M.mat('yellow gold carved glass',(.55,.49,.08),.1,.23,.3);p=M.root('panther sweat sculpted decanter');M.lathe('segmented animal-shaped flask',[(.35,0),(.53,.2),(.56,.65),(.43,1.15),(.3,1.3),(.30,1.8),(.4,2.0),(.27,2.25),(.18,2.3),(.25,2.45),(.1,2.55)],c,p)
  for side in [-1,1]:M.ball('ornamental eye',(side*.15,-.19,2.4),(.055,.055,.055),gold,p);M.rod('bent neck wire',(side*.13,0,2.5),(side*.3,0,2.85),.012,gold,p)
 elif n==6:
  c=M.mat('luminous cactus green glass',(.10,.6,.12),.05,.2,.2,emit=.2)
  for i,(x,y) in enumerate([(-.55,-.3),(.65,.4)]):
   p=M.root('sealed crystal urn '+str(i),(x,y,0));p.scale=(1,1,1+i*.15);M.lathe('bulbous urn',[(.45,0),(.56,.12),(.57,1.3),(.50,1.7),(.25,1.9),(.1,2)],c,p);M.ball('urn stopper',(0,0,2.05),(.17,.17,.14),gold,p)
   for side in [-1,1]:r=M.ring('loop handle',(side*.51,0,1.7),.16,.045,c,p);r.rotation_euler.x=math.pi/2
   if i==0:M.label('front urn label',p,.575,.8,.9,.65,dark)

def glassware(n):
 c=M.mat('Bristol violet glass' if n==7 else 'Cantata cyan crystal',(.19,.16,.37) if n==7 else (.025,.45,.49),.15,.18,.35)
 if n==7:
  p=M.root('long-neck Bristol decanter',(0,.25,0));M.lathe('glass decanter',[(.45,0),(.6,.15),(.65,.65),(.5,1.1),(.13,1.5),(.12,2.7),(.22,2.8)],c,p)
  for i,x in enumerate([-1,1]):
   p=M.root('Bristol wine glass '+str(i),(x,-.2,0));M.lathe('foot stem bowl',[(.3,0),(.32,.06),(.055,.14),(.045,.75),(.32,.9),(.38,1.25),(.33,1.4),(.29,1.4),(.33,1.24),(.27,.95),(.04,.85)],c,p)
 else:
  for i,(x,y,typ) in enumerate([(-1,-.3,0),(.1,-.6,0),(1,.2,1),(0,.6,2)]):
   p=M.root('separate cut-crystal vessel '+str(i),(x,y,0));r=.38 if typ!=2 else .75;h=1.8 if typ!=2 else 1.3;M.lathe('faceted cut-glass bowl and stem',[(r*.8,0),(r,.06),(.07,.12),(.06,h*.45),(r*.65,h*.55),(r,h*.9),(r,h),(r*.9,h),(r*.9,h*.9),(r*.55,h*.6)],c,p,segments=24)
   for j in range(16):
    a=j*math.tau/16;M.rod('cut crystal flute',(r*.65*math.cos(a),r*.65*math.sin(a),h*.6),(r*math.cos(a),r*math.sin(a),h*.95),.014,c,p)

BUILDERS={**{i:beverages for i in range(1,7)},7:glassware,8:glassware}

def fabrics(n):
 colors={9:(.015,.025,.24),10:(.50,.008,.016),11:(.46,.54,.22),12:(.48,.57,.30),13:(.075,.16,.55),14:(.61,.64,.35),15:(.45,.085,.012)};c=M.mat('woven '+str(n),colors[n],rough=.85 if n in [9,12,14,15] else .28);bs=c.node_tree.nodes.get('Principled BSDF');bs.inputs['Sheen Weight'].default_value=.45;dark=M.mat('rolled edge shadow',tuple(v*.4 for v in colors[n]),rough=.85);p=M.root('independent fabric roll')
 if n==15:
  wood=M.mat('wooden spool ends',(.20,.12,.055),rough=.8);M.cylinder('spool core',(0,0,-.15),.13,3.1,wood,p);M.lathe('thick combed angora yarn',[(.22,0),(.40,.12),(.43,.4),(.43,2.5),(.35,2.7),(.2,2.8)],c,p)
  for j in range(45):M.ring('wound yarn ridge',(0,0,.15+j*.055),.42,.018,c,p)
  p.rotation_euler=(.1,.30,-.15);return
 verts=[];faces=[];N=40;W=32
 for j in range(N+1):
  y=-1.7+j*2.9/N
  for i in range(W+1):
   x=-1.35+i*2.7/W;z=.14+.10*math.sin(y*3.5)+.045*math.cos(x*3+y*2);verts.append((x,y,z))
 for j in range(N):
  for i in range(W):a=j*(W+1)+i;faces.append((a,a+1,a+W+2,a+W+1))
 sheet=M.mesh('editable draped woven sheet',verts,faces,c,p);s=sheet.modifiers.new('Actual cloth thickness','SOLIDIFY');s.thickness=.018 if n==9 else .008
 for face in sheet.data.polygons:face.use_smooth=True
 o=M.cylinder('rolled cloth body',(-1.35,1.15,.52),.40,2.7,c,p);o.rotation_euler.y=math.pi/2
 for side in [-1,1]:
  points=[]
  for j in range(180):
   angle=j*.105;r=.045+j/179*.355;points.append((side*1.357,1.15+r*math.cos(angle),.52+r*math.sin(angle)))
  M.polyline('visible spiral selvage',points,.009,dark,p)
 if n in [10,12,14]:
  o=M.cylinder('partially rolled lower edge',(-1.35,-1.7,.18),.12,2.7,c,p);o.rotation_euler.y=math.pi/2
 if n==11:
  node=c.node_tree.nodes.new('ShaderNodeTexWave');node.bands_direction='X';node.inputs['Scale'].default_value=8;node.inputs['Distortion'].default_value=6;b=c.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.005;c.node_tree.links.new(node.outputs['Color'],b.inputs['Height']);c.node_tree.links.new(b.outputs[0],bs.inputs['Normal'])
BUILDERS.update({i:fabrics for i in range(9,16)})

def gem(name,loc,r,material,parent=None,sides=10):
 o=M.lathe(name,[(.03,-r*.65),(r,0),(r*.88,r*.40),(r*.48,r*.62)],material,parent,segments=sides);o.location=loc
 for p in o.data.polygons:p.use_smooth=False
 return o

def band(name,r,width,height,material,parent=None,start=.05,end=math.tau-.05):
 verts=[];faces=[];N=80
 for i in range(N+1):
  a=start+(end-start)*i/N
  for rr,z in [(r-width/2,0),(r+width/2,0),(r+width/2,height),(r-width/2,height)]:verts.append((rr*math.cos(a),rr*math.sin(a),z))
 for i in range(N):
  for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
 faces.extend([(0,1,2,3),(4*N+3,4*N+2,4*N+1,4*N)]);return M.mesh(name,verts,faces,material,parent)

def jewellery(n):
 gold=M.mat('worked yellow gold',(.63,.39,.07),.85,.25);silver=M.mat('white gold platinum',(.62,.67,.69),.9,.2);redgold=M.mat('red gold',(.62,.10,.016),.85,.25);blue=M.mat('astramarine jewel',(.025,.38,.55),.18,.15,.15);green=M.mat('emerald jewel',(.01,.52,.045),.1,.16,.15);white=M.mat('diamond jewel',(.75,.85,.91),.1,.10,.3);pearl=M.mat('pearl lustre',(.62,.66,.27),.3,.21);ruby=M.mat('ruby cabochon',(.58,.006,.015),.2,.17)
 if n==16:
  ivory=M.mat('raw opal tiara',(.68,.73,.72),.45,.2);p=M.root('opal and metachrome tiara',(0,.55,0));band('open tiara band',1.5,.12,.15,ivory,p,start=math.pi,end=math.tau)
  for a in [math.pi,math.tau]:M.ball('rounded tiara end',(1.5*math.cos(a),1.5*math.sin(a),.08),(.12,.12,.12),ivory,p)
  M.cube('tiara centre setting',(0,-1.5,.16),(.2,.09,.18),silver,p);gem('tiara central opal',(0,-1.51,.24),.16,white,p,8)
  p=M.root('separate chain bracelet',(0,-2.4,.08))
  for j in range(24):
   a=j*math.tau/24;o=M.ring('individual chain link',(.85*math.cos(a),.55*math.sin(a),0),.08,.016,silver,p);o.scale=(1.4,.75,1);o.rotation_euler.z=a
  gem('bracelet brilliant',(0,-.55,.06),.23,white,p,12)
 elif n==17:
  p=M.root('red gold open choker');band('woven red-gold ribbon',1.5,.12,.4,redgold,p,start=.25,end=math.tau-.25)
  centre=(0,-1.59,.25);v=[centre]
  for j in range(16):
   a=j*math.tau/16;r=.45 if j%2==0 else .25;v.append((r*math.cos(a),-1.59,.25+r*math.sin(a)))
  M.mesh('eight-point gold sunburst',v,[(0,j+1,(j+1)%16+1) for j in range(16)],gold,p);gem('central aquamarine',(0,-1.62,.25),.20,blue,p).rotation_euler.x=math.pi/2
 elif n==18:
  p=M.root('square cut solitaire');g=gem('octagonal square emerald',(0,0,.1),1.15,green,p,8);g.scale=(.83,1.1,.65);r=M.ring('white gold bezel',(0,0,.18),1.13,.055,gold,p);r.scale=(.85,1.1,1)
 elif n==19:
  p=M.root('four-point ruby brooch');cream=M.mat('polished red gold face',(.62,.43,.12),.8,.28)
  for j in range(4):
   a=j*math.pi/2;ca,sa=math.cos(a),math.sin(a);points=[(-.30,.25),(-.25,.7),(0,1.2),(.25,.7),(.30,.25)];v=[(x*ca-y*sa,x*sa+y*ca,.04) for x,y in points];M.mesh('pointed brooch petal',v,[tuple(range(5))],cream,p)
  gem('raised ruby centre',(0,0,.1),.38,ruby,p,8)
 elif n==20:
  p=M.root('23-stone astramarine necklace')
  for i in range(23):
   x=(i-11)*.17;y=.012*(i-11)**2;gem('individual astramarine '+str(i),(x,y,.05),.13,blue,p,8);M.ring('stone gold bezel',(x,y,.02),.14,.018,gold,p)
   if i: M.rod('necklace link',((i-12)*.17,.012*(i-12)**2,0),(x,y,0),.022,gold,p)
 elif n==21:
  p=M.root('eternity ring');band('broad 24ct ring',.85,.22,.30,gold,p,start=0,end=math.tau)
  for j in range(8):a=j*math.tau/8;gem('set ultropaz alexandrite',( .85*math.cos(a),.85*math.sin(a),.30),.10,blue if j%2 else pearl,p,8)
 elif n==22:
  p=M.root('diamond emerald pectoral');band('open metachrome framework',1.6,.20,.08,silver,p,start=.12,end=math.tau-.12)
  for j in range(28):
   a=.15+j*(math.tau-.30)/27;x,y=1.6*math.cos(a),1.6*math.sin(a);M.mesh('wide triangular silver lattice',[(1.35*math.cos(a-.05),1.35*math.sin(a-.05),.04),(1.92*math.cos(a),1.92*math.sin(a),.04),(1.35*math.cos(a+.05),1.35*math.sin(a+.05),.04)],[(0,1,2)],silver,p);gem('pectoral emerald',(x,y,.10),.09,green,p,8)
   for side in [-1,1]:M.rod('triangular lattice rib',(x,y,.05),((1.6+side*.22)*math.cos(a+.08),(1.6+side*.22)*math.sin(a+.08),.05),.025,silver,p)
  gem('pectoral central diamond',(0,-1.65,.14),.22,white,p,12)
 elif n==23:
  p=M.root('seventeen-opal collar');band('pierced gold collar',1.45,.14,.48,gold,p,start=.12,end=math.tau-.12)
  for j in range(17):
   a=.18+j*(math.tau-.36)/16;x,y=1.45*math.cos(a),1.45*math.sin(a);gem('blue opal setting '+str(j),(x,y,.25),.14,blue,p,8);M.ring('white gold opal rim',(x,y,.25),.15,.021,silver,p)
  M.cube('white gold clasp',(1.45,0,.24),(.12,.1,.22),silver,p)
 else:
  p=M.root('three pearl strand bracelet')
  for strand in range(3):
   for j in range(26):
    a=j*math.tau/26;M.ball('individual pearl',(math.cos(a),math.sin(a),strand*.27),(.13,.13,.13),pearl,p)
  M.cube('platinum bracelet clasp',(1.0,0,.28),(.14,.12,.4),silver,p)
BUILDERS.update({i:jewellery for i in range(16,25)})

def gemstones(n):
 colors={25:(.58,.46,.38),26:(.005,.48,.015),27:(.025,.075,.58),28:(.56,.006,.012),29:(.59,.27,.008),30:(.36,.005,.46),31:(.78,.87,.91),32:(.50,.62,.16),33:(.65,.68,.25),34:(.48,.58,.27),35:(.005,.47,.62),36:(.39,.62,.07),37:(.53,.012,.36)};c=M.mat('individual gemstone colour',colors[n],.12,.14,.18 if n!=33 else 0)
 for j,(loc,r) in enumerate([((-.9,-.35,.42),.40),((0,.10,.54),.56),((.9,.45,.42),.40)]):
  if n==33:M.ball('individual lustrous pearl '+str(j),loc,(r,)*3,c,sub=3)
  else:
   p=gem('individually faceted stone '+str(j),loc,r,c,sides=10 if n not in [25,31] else 12);p.rotation_euler=(.25+j*.3,.2*j,.15+j*.6)
 if n in [30,32,34,36]:
  inner=M.mat('internal colour play',tuple(min(1,x*1.2+.08) for x in colors[n]),.25,.16)
  for j,(x,y,z) in enumerate([(-.9,-.35,.45),(0,.1,.56),(.9,.45,.45)]):
   g=gem('inclusion colour facet',(x,y,z+.2),.19,inner,sides=6);g.rotation_euler=(.1,.2,j)
BUILDERS.update({i:gemstones for i in range(25,38)})

def open_case(name,base,lining,angle=1.1):
 p=M.root(name);M.cube('case bottom',(0,0,.08),(1.25,.75,.08),base,p)
 for x in [-1.2,1.2]:M.cube('case side',(x,0,.30),(.05,.75,.25),base,p)
 for y in [-.7,.7]:M.cube('case end',(0,y,.30),(1.2,.05,.25),base,p)
 M.cube('case liner',(0,0,.18),(1.15,.65,.025),lining,p)
 lid=M.root('hinged lid',(0,.72,.55));lid.parent=p;lid.rotation_euler.x=-angle;M.cube('separate lid panel',(0,-.72,0),(1.25,.75,.07),base,lid);M.cube('lid lining',(0,-.72,-.075),(1.12,.62,.006),lining,lid)
 for x in [-.8,.8]:M.rod('hinge barrel',(x-.12,.72,.55),(x+.12,.72,.55),.06,lining,p)
 return p

def horn(name,loc,material,trim,parent=None,size=1):
 p=M.root(name,loc);p.parent=parent;p.scale=(size,)*3;v=[];f=[];N=20;S=32
 for k in range(N+1):
  t=k/N;r=.035+.45*t**1.3;cx=.38*math.sin(t*1.8)
  for j in range(S):a=j*math.tau/S;v.append((cx+r*math.cos(a),r*math.sin(a),2*t))
 for k in range(N):
  for j in range(S):q=k*S+j;b=k*S+(j+1)%S;f.append((q,b,b+S,q+S))
 o=M.mesh('curving hollow horn shell',v,f,material,p);q=o.modifiers.new('Horn wall thickness','SOLIDIFY');q.thickness=.035
 for face in o.data.polygons:face.use_smooth=True
 M.ring('decorative mouth rim',(.38*math.sin(1.8),0,2),.485,.05,trim,p)
 for t in [.45,.65,.83]:
  r=.035+.45*t**1.3;cx=.38*math.sin(t*1.8);M.ring('gold ornamental band',(cx,0,2*t),r,.055,trim,p)
  for j in range(12):a=j*math.tau/12;M.ball('individual band stud',(cx+(r+.045)*math.cos(a),(r+.045)*math.sin(a),2*t),(.035,)*3,trim,p,1)
 return p

def art_food(n):
 gold=M.mat('aged brass',(.5,.28,.055),.75,.4);dark=M.mat('blackened metal',(.022,.025,.028),.6,.55);wood=M.mat('worn warm wood',(.28,.12,.035),rough=.85);cream=M.mat('cream ivory',(.53,.46,.23),rough=.65);blue=M.mat('blue alloy',(.025,.07,.33),.5,.35)
 if n==38:
  M.cube('black plinth',(0,0,.3),(.75,.55,.3),dark);M.cube('cyan pedestal inlay',(0,-.56,.3),(.57,.01,.025),blue);v=[];faces=[];profile=[(.45,.6),(.48,.9),(.26,1.4),(.55,1.8),(.48,2.25),(.23,2.65),(.40,2.9)]
  for k,(w,z) in enumerate(profile):
   for j in range(24):a=j*math.tau/24;v.append((w*math.cos(a)+.13*math.sin(z*3),.28*math.sin(a),z))
  for k in range(len(profile)-1):
   for j in range(24):faces.append((24*k+j,24*k+(j+1)%24,24*(k+1)+(j+1)%24,24*(k+1)+j))
  o=M.mesh('Artemian abstract curved sculpture',v,faces,wood);o.data.materials.append(blue)
  for k,f in enumerate(o.data.polygons):f.material_index=int(k%24>12);f.use_smooth=True
 elif n==39:
  p=M.root('curved pedestal table',(0,0,0));M.lathe('exotic alloy table',[(.9,0),(1,.12),(.45,.35),(.35,.7),(.8,1),(1.1,1.12),(1.1,1.25),(.95,1.3)],blue,p)
  p=M.root('separate tall shelving unit',(-1.7,.6,0))
  for x in [-.35,.35]:
   for y in [-.3,.3]:M.rod('slender shelf leg',(x,y,0),(x,y,2.2),.025,blue,p)
  for z in [.4,1.2,2.2]:M.cube('shelf plane',(0,0,z),(.4,.35,.035),dark,p)
  M.cube('separate storage block',(1.8,0,.3),(.4,.4,.3),blue)
  for z in [.15,.3,.45]:M.cube('drawer seam',(1.8,-.405,z),(.34,.012,.01),dark)
 elif n==40:
  antler=M.mat('polished horn',(.30,.22,.12),rough=.4)
  for i,(x,y) in enumerate([(-.9,.3),(0,-.35),(.9,.4)]):horn('individual drinking horn '+str(i),(x,y,0),antler,gold,size=.85 if i!=1 else 1)
 elif n==41:
  leather=M.mat('Braccatian worked leather',(.16,.045,.008),rough=.65);p=M.root('long decorated leather coat',(0,.4,0));M.cube('coat rear garment',(0,.1,1.6),(.7,.13,1.5),leather,p)
  for side in [-1,1]:
   M.mesh('separate front leather panel',[(side*.10,-.22,.1),(side*.7,-.22,.1),(side*.65,-.22,2.9),(side*.3,-.22,3.1),(side*.1,-.22,2.6)],[(0,1,2,3,4)],leather,p);M.rod('coat sleeve',(side*.65,.1,2.9),(side*1.0,.05,1.8),.24,leather,p);M.ring('decorated cuff',(side*1.0,.05,1.8),.25,.04,gold,p)
   for z in [.4,.7,1,1.3,1.6,1.9,2.2]:M.ball('coat front stud',(side*.25,-.25,z),(.025,.025,.025),gold,p,1)
  for x in [1.5,2.1]:
   p=M.root('separate leather boot',(x,0,0));M.lathe('boot shaft',[(.19,.15),(.16,.4),(.22,1.3)],leather,p);M.cube('boot toe',(0,-.16,.13),(.21,.38,.13),leather,p);M.ring('boot cuff',(0,0,1.3),.23,.035,gold,p)
  r=M.ring('separate worked belt',(-1.6,-.4,.1),.5,.065,leather);r.scale.y=.65;M.cube('belt buckle',(-1.1,-.4,.13),(.10,.12,.025),gold)
 elif n==42:
  steel=M.mat('ornamental blade metal',(.45,.35,.24),.8,.35);p=M.root('ornamental sword',(-1.1,0,0));M.cylinder('sword grip',(0,0,0),.09,.7,wood,p);M.rod('decorative crossguard',(-.35,0,.7),(.35,0,.7),.07,gold,p);M.mesh('leaf shaped blade',[(-.20,0,.7),(-.15,0,2.9),(0,0,3.5),(.15,0,2.9),(.2,0,.7),(0,-.07,1.8)],[(0,1,2,5),(2,3,4,5),(4,0,5)],steel,p)
  p=M.root('ceremonial flail',(0,0,0));M.cylinder('flail grip',(0,0,0),.12,.8,wood,p)
  for j in range(7):o=M.ring('individual flail chain link',(0,0,.9+j*.16),.10,.025,gold,p);o.rotation_euler.y=math.pi/2 if j%2 else 0
  M.ball('flail head',(0,0,2.3),(.3,.3,.3),steel,p,1)
  for j in range(8):a=j*math.tau/8;M.rod('ornamental head spike',(.25*math.cos(a),.25*math.sin(a),2.3),(.46*math.cos(a),.46*math.sin(a),2.3),.04,gold,p)
  p=M.root('triangular archaic string weapon',(1.3,.3,0));M.mesh('triangular decorated frame',[(-.7,0,.5),(.7,0,.5),(0,0,3)],[(0,1,2)],wood,p)
  for z in [.7,.9,1.1,1.3,1.5,1.7,1.9,2.1]:w=.7*(3-z)/2.5;M.rod('individual metallic string',(-w,-.02,z),(w,-.02,z),.008,gold,p)
 elif n==43:
  chocolate=M.mat('chocolate shell',(.16,.06,.012),rough=.5);p=open_case('decorative liqueur chocolate case',gold,dark)
  for x in [-.6,.6]:
   for y in [-.32,.32]:M.ball('individual filled chocolate',(x,y,.4),(.25,.25,.22),chocolate,p)
  for x in [-.6,.6]:M.ring('case lid ornament',(x,-.1,.75),.12,.02,gold,p)
 elif n==44:
  shell=M.mat('ant egg shell',(.30,.23,.17),rough=.45)
  for x,y,r in [(-.65,.3,.6),(.4,.4,.62),(-.5,-.4,.6),(.55,-.4,.65)]:M.ball('individual ant egg',(x,y,.25),(r,r*.65,r*.4),shell,sub=3)
 elif n==45:
  glass=M.mat('brandy glass',(.42,.44,.38),rough=.22,glass=.3);p=M.bottle('pearl brandy flask',(0,0,0),glass,gold,wood,height=2.5,r=.65)
  pearl=M.mat('visible pearl residue',(.68,.68,.48),rough=.2)
  for j in range(18):a=j*2.4;r=.45*(j%3)/2;M.ball('undissolved pearl',(r*math.cos(a),r*math.sin(a),.14+(j%2)*.1),(.07,)*3,pearl,p)
 elif n==46:
  cap=M.mat('goat ear mushroom cap',(.27,.18,.085),rough=.85)
  for i,(x,y,h,r) in enumerate([(-.7,.2,1.6,.65),(.6,.1,1.0,.5),(-.6,-.6,.6,.35),(.7,-.5,.6,.3)]):
   p=M.root('individual mushroom '+str(i),(x,y,0));M.lathe('slightly bowed mushroom stem',[(.14,0),(.12,h*.4),(.18,h)],cream,p);o=M.lathe('broad irregular mushroom cap',[(.12,h),(.65*r,h+.06),(r,h+.12),(r*.95,h+.27),(r*.55,h+.34),(.1,h+.38)],cap,p)
   for v in o.data.vertices:v.co.x+=.04*math.sin(v.co.y*11+i)
   for j in range(20):a=j*math.tau/20;M.rod('underside gill',(.18*math.cos(a),.18*math.sin(a),h+.04),(.85*r*math.cos(a),.85*r*math.sin(a),h+.10),.008,wood,p)
 elif n==47:
  p=M.root('wooden sweetcorn crate');M.cube('crate floor',(0,0,.1),(1.4,.8,.1),wood,p)
  for x in [-1.35,1.35]:M.cube('crate end',(x,0,.5),(.05,.8,.4),wood,p)
  for y in [-.75,.75]:M.cube('crate side',(0,y,.5),(1.4,.05,.4),wood,p)
  yellow=M.mat('sweetcorn kernels',(.65,.47,.025),rough=.5);green=M.mat('green husk',(.10,.20,.02),rough=.85)
  for i,y in enumerate([-.45,0,.45]):
   M.rod('corn core',(-1,y,.7),(1,y,.7),.16,yellow,p)
   for j in range(17):
    x=-1+j*.12
    for k in range(8):a=k*math.tau/8;M.ball('individual corn kernel',(x,y+.20*math.cos(a),.7+.20*math.sin(a)),(.075,.075,.075),yellow,p,1)
   M.mesh('corn husk',[(-1.15,y-.23,.65),(1.1,y-.18,.6),(.4,y+.23,.65)],[(0,1,2)],green,p)
 else:
  wax=M.mat('purple cheese wax',(.25,.035,.17),rough=.6);cheese=M.mat('yellow cheese interior',(.65,.56,.075),rough=.8);v=[(0,0,0),(0,0,.6)];N=48
  for j in range(N+1):a=.45+j*(math.tau-.9)/N;v.extend([(1.3*math.cos(a),1.3*math.sin(a),0),(1.3*math.cos(a),1.3*math.sin(a),.6)])
  f=[]
  for j in range(N):q=2+j*2;f.extend([(q,q+2,q+3,q+1),(0,q+2,q),(1,q+1,q+3)])
  f.extend([(0,1,3,2),(0,2+N*2,3+N*2,1)]);o=M.mesh('whole cheese wheel with removed wedge',v,f,wax);o.data.materials.append(cheese);o.data.polygons[-1].material_index=1;o.data.polygons[-2].material_index=1
  for i in range(8):x=.2+i*.13;M.ball('cheese cut-face hole',(x,.45*x,.15+(i%3)*.14),(.045,.015,.045),wood,sub=1)
BUILDERS.update({i:art_food for i in range(38,49)})

def storage(n):
 sack=M.mat('coarse sack cloth',(.37,.25,.10),rough=.95);metal=M.mat('worn green storage alloy',(.15,.25,.19),.45,.65);dark=M.mat('dark recessed frame',(.045,.07,.06),.3,.85)
 if n==49:
  for i,(x,y,h) in enumerate([(-.8,.3,1.3),(.1,.5,1.5),(.9,.25,1.2),(-.3,-.5,1.1),(.7,-.55,1.2)]):
   p=M.root('individual tied grain sack '+str(i),(x,y,0));M.lathe('bulging woven sack',[(.30,0),(.50,.1),(.52,h*.4),(.4,h*.85),(.18,h),(.07,h+.14)],sack,p);M.ring('tied sack mouth',(0,0,h),.15,.025,dark,p)
  M.ball('flat foreground grain sack',(-.6,-1,.2),(.65,.38,.2),sack)
 elif n==50:
  green=M.mat('packed green seaweed',(.035,.25,.012),rough=.95)
  for i,(x,y,z) in enumerate([(-.6,.25,1.1),(.65,.25,1.1),(0,-.4,0)]):
   p=M.root('stacked open mesh produce crate '+str(i),(x,y,z));M.cube('crate floor',(0,0,.04),(.58,.48,.04),metal,p)
   for side in [-1,1]:
    for j in range(9):
     xx=-.55+j*.137;M.rod('crate lattice upright',(xx,side*.48,0),(xx,side*.48,.9),.018,metal,p)
    for z0 in [.15,.3,.45,.6,.75,.9]:M.rod('crate lattice rail',(-.58,side*.48,z0),(.58,side*.48,z0),.018,metal,p)
    for j in range(8):yy=-.48+j*.137;M.rod('crate end lattice',(side*.58,yy,0),(side*.58,yy,.9),.018,metal,p)
   for j in range(25):a=j*2.4;r=(j%5)*.1;M.ball('coiled seaweed fill',(r*math.cos(a),r*math.sin(a),.83+.07*(j%3)),(.18,.13,.07),green,p,1)
 elif n==51:
  for i,(x,y) in enumerate([(-.7,.3),(.6,.3),(0,-.6)]):
   p=M.root('framed krill canister '+str(i),(x,y,0));M.lathe('bulk food canister',[(.4,0),(.46,.1),(.46,2.1),(.4,2.2)],metal,p)
   for a in [0,math.pi/2,math.pi,math.pi*1.5]:M.rod('canister protective rail',(.52*math.cos(a),.52*math.sin(a),0),(.52*math.cos(a),.52*math.sin(a),2.2),.035,dark,p)
   for z in [0,1.1,2.2]:M.ring('canister end frame',(0,0,z),.52,.04,metal,p)
 else:
  tank=M.mat('water storage tanks',(.42,.49,.53),.4,.48);yellow=M.mat('water cargo markings',(.46,.48,.045),rough=.8);p=M.root('six-tank shipping rack')
  for j in range(2):
   for i in range(3):
    x=(i-1)*.74;z=.5+j*.85;o=M.lathe('individual horizontal water tank',[(.15,0),(.32,.14),(.34,.35),(.34,1.9),(.3,2.12),(.12,2.2)],tank,p);o.rotation_euler.x=math.pi/2;o.location=(x,.8,z);M.cylinder('front valve',(x,-1.42,z),.065,.04,dark,p).rotation_euler.x=math.pi/2
  for x in [-1.2,1.2]:
   for y in [-1.25,.85]:M.rod('rack upright',(x,y,0),(x,y,1.9),.055,metal,p)
  for z in [.05,.9,1.8]:
   for y in [-1.25,.85]:M.rod('rack horizontal brace',(-1.2,y,z),(1.2,y,z),.045,metal,p)
  M.cube('cargo instruction plate',(1.25,0,1.0),(.035,.65,.4),metal,p)
  for y in [-.4,0,.4]:M.cube('yellow cargo pictogram',(1.29,y,1.0),(.015,.1,.13),yellow,p)
BUILDERS.update({i:storage for i in range(49,53)})

def collectibles(n):
 gold=M.mat('antiqued artifact brass',(.48,.29,.055),.8,.4);dark=M.mat('aged black base',(.022,.018,.012),.25,.8);wood=M.mat('antique warm wood',(.22,.085,.025),rough=.8);blue=M.mat('blue enamel',(.025,.30,.38),.2,.35);ivory=M.mat('ivory small pieces',(.65,.55,.36),rough=.7)
 if n==53:
  p=M.root('multi-level Ortok game');M.lathe('oval game table base',[(1.5,0),(1.6,.10),(1.5,.18)],wood,p).scale.y=.65
  for x in [-1.2,1.2]:
   for y in [-.5,.5]:M.rod('turned table leg',(x,y,-.6),(x,y,0),.08,wood,p)
  for j in range(6):
   z=.2+j*.45;o=M.cylinder('separate oval board',(0,0,z),1.5,.045,blue,p);o.scale.y=.65
   for x,y in [(-1.1,-.45),(-.4,-.65),(.4,-.65),(1.1,-.45)]:
    M.cube('miniature mansion',(x,y,z+.12),(.09,.075,.12),ivory,p);M.cube('mansion doorway',(x,y-.078,z+.10),(.025,.008,.06),dark,p)
   for a in [0,math.pi/2,math.pi,math.pi*1.5]:M.rod('board support column',(1.5*math.cos(a),.9*math.sin(a),.2),(1.5*math.cos(a),.9*math.sin(a),2.6),.025,gold,p)
 elif n==54:
  bronze=M.mat('worn goggle bronze',(.30,.18,.07),.5,.5);black=M.mat('black lens',(.003,.004,.005),.1,.15);red=M.mat('small red sensor',(.6,.005,.001),emit=.3);p=M.root('Brutos goggles');band('broad head strap',1.15,.16,.22,bronze,p,start=.15,end=math.tau-.15)
  for x in [-.50,.50]:
   M.ball('rounded goggle housing',(x,-1,.18),(.49,.25,.38),bronze,p);M.ball('black oval lens',(x,-1.23,.18),(.37,.025,.28),black,p);M.ball('red lens glint',(x-.05,-1.26,.22),(.035,.012,.035),red,p)
  M.rod('nose bridge',(-.1,-1,.2),(.1,-1,.2),.09,bronze,p)
 elif n==55:
  red=M.mat('red lacquered cigar box',(.42,.012,.012),.1,.45);brown=M.mat('rolled Huskar leaf',(.20,.11,.025),rough=.9);p=open_case('Huskar cigar box',red,gold,angle=.1)
  for j,y in enumerate([-.4,0,.4]):
   M.rod('individual cigar',(-.9,y,.8),(1.4,y+.3,.8),.09,brown,p);M.rod('gold cigar band',(-.2,y+.09,.8),(-.05,y+.11,.8),.096,gold,p)
  M.ball('box decorative gold seal',(-.4,-.2,.69),(.3,.22,.01),gold,p)
 elif n==56:
  metal=M.mat('oily Maunid puzzle metal',(.22,.21,.18),.75,.6);p=M.root('Maunik puzzle cube');p.rotation_euler=(.12,.1,.2)
  for x in range(3):
   for y in range(3):
    for z in range(3):
     xx,yy,zz=(x-1)*.51,(y-1)*.51,z*.51;M.cube('independent puzzle cubie',(xx,yy,zz),(.245,.245,.245),metal,p)
     if y==0:
      for k in [-1,1]:M.rod('abstract incised cubie motif',(xx-.1,yy-.25,zz+k*.1),(xx+.1,yy-.25,zz-k*.08),.012,dark,p)
 elif n==57:
  p=M.root('Gong of DeathSong and frame');M.cube('gong display footing',(0,0,.05),(1.2,.55,.05),wood,p)
  for x in [-1.1,1.1]:M.cube('ornate frame upright',(x,0,1.25),(.1,.13,1.25),gold,p)
  M.cube('frame top crossbar',(0,0,2.5),(1.2,.13,.12),gold,p);M.cylinder('black gong rim',(0,0,1.25),1.0,.10,dark,p).rotation_euler.x=math.pi/2;M.cylinder('gold sounding disc',(0,-.11,1.25),.74,.035,gold,p).rotation_euler.x=math.pi/2
  for j in range(50):a=j*2.4;r=.10+(j%8)*.075;M.ball('gong patterned dimple',(r*math.cos(a),-.15,1.25+r*math.sin(a)),(.018,.012,.018),dark,p,1)
  M.rod('suspension',(-.3,0,2.5),(-.3,0,2.0),.025,gold,p);M.rod('suspension',(.3,0,2.5),(.3,0,2.0),.025,gold,p)
 elif n==58:
  violet=M.mat('violet holographic globe',(.09,.025,.35),.12,.18,.35);p=M.root('Rigellian star globe stand');M.lathe('gold stand foot',[(.95,0),(1.05,.12),(.95,.22)],gold,p)
  for j in range(4):
   a=j*math.pi/2;x,y=.7*math.cos(a),.7*math.sin(a);M.rod('turned stand pillar',(x,y,.2),(x,y,1.2),.045,gold,p)
   for z in [.3,.45,.6,.75,.9]:M.ring('pillar spiral collar',(x,y,z),.075,.025,gold,p)
  M.ring('equatorial stand',(0,0,1.2),1.0,.05,gold,p);M.ball('separate globe',(0,0,1.4),(.85,.85,.95),violet,p,3)
  for z,r in [(.8,.6),(1.2,.8),(1.6,.83),(2.0,.6)]:M.ring('holographic latitude',(0,0,z),r,.012,blue,p)
  st=M.mat('holographic star nodes',(.25,.42,.9),emit=1)
  for j in range(20):a=j*2.4;z=.65+(j%7)*.22;r=math.sqrt(max(.01,.85**2-(z-1.4)**2));M.ball('star map node',(r*math.cos(a),r*math.sin(a),z),(.025,)*3,st,p,1)
 elif n==59:
  green=M.mat('green apothecary case',(.16,.40,.025),.1,.45);bottle=M.mat('pale remedy glass',(.55,.65,.47),rough=.22,glass=.18);p=open_case('Besthelda apothecary',green,ivory)
  for j in range(2):
   for i in range(11):
    q=M.bottle('individual remedy vial',( -.95+i*.19,-.32+j*.58,.23),bottle,gold,height=.35,r=.065);q.parent=p
 elif n==60:
  glass=M.mat('yellow-green photoplasmic shell',(.48,.57,.12),rough=.18,glass=.45);light=M.mat('photoplasm core',(.65,.4,.05),emit=.5);p=M.root('photoplasmic cocoon');M.lathe('stepped circular cocoon plinth',[(.8,0),(.9,.1),(.8,.2),(.65,.26)],gold,p);M.ball('elliptical clear cocoon',(0,0,1.4),(.62,.48,1.2),glass,p,3)
  for z in [.7,1.4,2.0]:M.ball('internal therapeutic light',(0,0,z),(.16,.13,.16),light,p)
  for side in [-1,1]:M.rod('internal suspension rod',(side*.23,0,.3),(side*.23,0,2.3),.035,gold,p)
BUILDERS.update({i:collectibles for i in range(53,61)})

def rare_goods(n):
 gold=M.mat('ceremonial gold',(.56,.32,.055),.8,.35);wood=M.mat('reddish antique wood',(.23,.08,.025),rough=.8);dark=M.mat('dark artifact metal',(.025,.025,.025),.6,.6);red=M.mat('red enamel',(.5,.015,.008),.25,.45);ivory=M.mat('pale ivory',(.65,.59,.32),rough=.6)
 if n==61:
  p=M.root('Braccatian steam racer');M.mesh('pointed red racing chassis',[(-1.4,-.55,.5),(-1.4,.55,.5),(2,0,.5),(-1.4,-.55,1),(-1.4,.55,1),(2,0,.65)],[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],red,p)
  M.rod('exposed steam boiler',(-.9,0,.95),(.9,0,.95),.35,red,p)
  for x,r in [(-1.1,.55),(1.25,.34)]:
   for side in [-1,1]:
    w=M.cylinder('separate racer wheel',(x,side*.7,r),r,.14,red,p);w.rotation_euler.x=math.pi/2;M.rod('wheel axle',(x,-.85,r),(x,.85,r),.07,dark,p)
    for j in range(8):a=j*math.tau/8;M.rod('wheel spoke',(x,side*.78,r),(x+r*.85*math.cos(a),side*.78,r+r*.85*math.sin(a)),.025,gold,p)
  for x in [-.8,-.4,0,.4]:M.cylinder('steam exhaust stack',(x,0,1.1),.065,.7,gold,p);M.ring('exhaust rim',(x,0,1.8),.07,.015,dark,p)
  M.rod('ornamental rear harpoon assembly',(-.5,0,1.3),(-1.7,0,1.5),.065,dark,p)
  for j in range(5):x=-1+j*.35;M.mesh('painted gold flame motif',[(x,-.56,.55),(x+.18,-.52,.9),(x+.10,-.54,.6),(x+.3,-.50,.8)],[(0,1,2,3)],gold,p)
 elif n==62:
  green=M.mat('green card backs',(.12,.27,.035),rough=.8);p=M.root('KKZ Quad card arrangement');M.cube('wooden game surface',(0,0,.02),(2,1.5,.02),wood,p)
  for i,(x,y) in enumerate([(-.8,.1),(-.3,.4),(.3,.3),(.8,.1),(-.5,-.5),(.2,-.6),(.5,.7)]):
   q=M.root('individual face-up card '+str(i),(x,y,.08+i*.004));q.parent=p;q.rotation_euler.z=(i-3)*.21;M.cube('ivory card',(0,0,0),(.32,.43,.007),ivory,q,bevel=.008);M.cylinder('card emblem',(0,0,.009),.07,.006,gold if i%2 else red,q)
  for x,y in [(-1.35,-.8),(1.35,.85),(-1.3,1)]:
   for j in range(8):M.cube('stacked green-backed card',(x,y,.06+j*.012),(.32,.43,.006),green,p,bevel=.006)
 elif n==63:
  green=M.mat('Kraagil green organic surface',(.15,.27,.012),.15,.55);p=M.root('spined Kraagil oil reference form');M.mesh('flattened pointed head',[(-1.8,0,.2),(-.7,-.5,.1),(-.6,.5,.1),(-.6,0,.65)],[(0,1,2),(0,3,1),(0,2,3),(1,3,2)],green,p)
  for i in range(7):
   x=-.6+i*.35;r=.48*(1-i*.11);M.ball('segmented organic tail',(x,0,.3),(r,.28*(1-i*.09),.3*(1-i*.09)),green,p)
   M.mesh('dorsal organic spine',[(x-.1,0,.4),(x+.1,0,.4),(x-.03,0,.9-i*.06)],[(0,1,2)],gold,p)
   for side in [-1,1]:M.mesh('lateral organic spine',[(x,side*.2,.25),(x+.25,side*.5,.25),(x+.15,side*.15,.25)],[(0,1,2)],green,p)
  for side in [-1,1]:M.ball('organic eye-like nodule',(-.9,side*.25,.43),(.05,.05,.035),gold,p)
 elif n==64:
  p=M.root('Artemian sacrificial double axe');M.lathe('carved wooden haft',[(.12,0),(.09,.2),(.07,2.5),(.13,2.7)],wood,p)
  for side in [-1,1]:
   pts=[(side*.1,0,2.3),(side*.45,0,2.65),(side*.9,0,2.8),(side*1.05,0,2.45),(side*.95,0,2.05),(side*.55,0,1.9),(side*.5,0,2.15)];o=M.mesh('separate crescent axe blade',pts,[tuple(range(7))],gold,p);q=o.modifiers.new('Actual blade thickness','SOLIDIFY');q.thickness=.07
 elif n==65:
  p=horn('ceremonial Horn of Plenty',(0,0,.6),ivory,gold,size=1.4);p.rotation_euler.y=-math.pi/2
  for i in range(26):
   t=i/25;M.ball('hanging ceremonial chain bead',(-2.6+2.4*t,-.08,.35-.32*math.sin(math.pi*t)),(.045,)*3,ivory)
 elif n==66:
  cyan=M.mat('lightwork cyan prism',(.005,.45,.42),.1,.25,.2,emit=.25);purple=M.mat('lightwork violet beam',(.25,.015,.38),emit=.2);body=M.mat('warm bronze figure',(.27,.13,.06),.5,.5);p=M.root('Dionne Lightwork');M.cube('turquoise pedestal',(0,0,.65),(.6,.4,.65),cyan,p)
  for x in [-.18,.18]:M.rod('figure leg',(x,0,1.3),(x,0,2),.11,body,p)
  M.ball('figure torso',(0,0,2.25),(.35,.18,.5),body,p);M.ball('figure head',(0,0,2.95),(.19,.17,.24),body,p)
  for side in [-1,1]:M.rod('figure arm',(side*.28,0,2.55),(side*.4,-.02,1.8),.09,body,p)
  for side in [-1,1]:M.mesh('angular translucent light sheet',[(side*.3,-.1,.1),(side*1.8,.2,3.8),(side*.6,-.1,1.2)],[(0,1,2)],cyan if side<0 else purple,p)
  dot=M.mat('lightwork coloured points',(.12,.28,.62),emit=.4)
  for i in range(14):
   for j in range(14):M.ball('backdrop light node',(-1.6+i*.25,.65,.15+j*.26),(.015,)*3,dot,p,1)
 elif n==67:
  p=M.root('Achaean loving cup');M.lathe('gold foot stem and hollow bowl',[(.6,0),(.7,.1),(.4,.25),(.13,.5),(.12,1.2),(.45,1.35),(.95,1.6),(1,1.95),(.92,1.95),(.85,1.65),(.2,1.4)],gold,p)
  inside=M.mat('red enamel inner bowl',(.45,.005,.003),.15,.28);M.lathe('red inner lining',[(.2,1.42),(.84,1.67),(.91,1.94)],inside,p)
  for side in [-1,1]:o=M.ring('separate cup loop handle',(side*.98,0,1.65),.28,.045,gold,p);o.rotation_euler.x=math.pi/2;o.scale=(1,.7,1)
 else:
  grey=M.mat('Law cube gray metal',(.20,.22,.24),.65,.6);copper=M.mat('Law cube copper base',(.28,.10,.04),.7,.5);p=M.root('Law of the Cube relic and pedestal');M.cube('low wide relic plinth',(0,0,.15),(1.2,.85,.15),copper,p);M.cube('stepped slab',(0,0,.4),(.8,.6,.1),dark,p);M.cube('gray inscribed cube',(0,0,1.05),(.5,.5,.55),grey,p)
  M.polyline('authored angular front motif',[(-.3,-.51,1.3),(-.3,-.51,1.05),(-.1,-.51,1.25),(.12,-.51,1.25),(.25,-.51,1),(.05,-.51,.85)],.025,dark,p);M.cube('red top seal',(0,0,1.61),(.27,.27,.012),red,p);M.rod('side connector',(-.75,0,1.15),(-.5,0,1.15),.075,copper,p)
BUILDERS.update({i:rare_goods for i in range(61,69)})

def medical(n):
 grey=M.mat('medical case alloy',(.42,.47,.49),.45,.5);dark=M.mat('dark inset seams',(.025,.035,.04),.3,.7);cream=M.mat('pale medical casing',(.64,.62,.45),.1,.7);gold=M.mat('yellow fittings',(.60,.47,.04),.3,.45);red=M.mat('red markings',(.6,.005,.003),.1,.5);p=M.root('individual fictional medical package')
 if n in [69,70]:
  col=M.mat('Biofort cream' if n==69 else 'Vir-Attack blue gray',(.60,.56,.37) if n==69 else (.14,.24,.29),.25,.55)
  if n==69:
   M.cube('upright medical case',(0,0,1.1),(.7,.25,1.1),col,p,bevel=.1);lid=M.cube('raised case cover',(0,.30,2.2),(.7,.045,.48),grey,p);lid.rotation_euler.x=-.3
  else:
   v=[(-.8,-.4,0),(.8,-.4,0),(.8,.4,0),(-.8,.4,0),(-.48,-.25,1.8),(.48,-.25,1.8),(.48,.25,1.8),(-.48,.25,1.8)];M.mesh('tapered Vir-Attack housing',v,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0),(4,7,6,5)],col,p);lid=M.cube('hinged top hatch',(0,.15,2.0),(.42,.025,.3),grey,p);lid.rotation_euler.x=-.4;M.cube('side module',(.75,.0,1.3),(.16,.2,.6),col,p)
  for z in [.45,1,1.55]:M.cube('case seam',(0,-.265 if n==69 else -.4,z),(.65,.01,.016),dark,p)
  for x in [-.15,.15]:M.rod('red case handle',(x,-.1,2.05),(x,-.1,2.25),.035,red,p)
  M.cylinder('round medical badge',(0,-.28 if n==69 else -.405,1.15),.24,.025,dark,p).rotation_euler.x=math.pi/2
  M.cube('medical cross upright',(0,-.32 if n==69 else -.44,1.15),(.045,.015,.15),red,p);M.cube('medical cross arm',(0,-.33 if n==69 else -.45,1.15),(.15,.015,.045),red,p)
  for x in [-.75,0,.75]:
   q=M.bottle('separate medicinal vial',(x,-.8,0),grey,cream,height=.5,r=.14);q.parent=p
 elif n==71:
  amber=M.mat('amber preparation bottle',(.42,.18,.005),.1,.25,.15);M.lathe('broad amber bottle',[(.55,0),(.6,.1),(.6,1.7),(.45,1.8),(.16,1.95)],amber,p);M.lathe('yellow conical stopper',[(.18,1.95),(.23,2),(.10,2.4)],gold,p);M.label('orange medicine label',p,.61,1,.7,.55,red);M.text('authored medicine lettering','SUPA',(0,-.63,1.04),.1,gold,p)
 elif n==72:
  green=M.mat('green spray container',(.12,.38,.23),.2,.5);M.lathe('tall preparation cylinder',[(.3,0),(.34,.08),(.34,2),(.39,2.1),(.34,2.3),(.1,2.4)],green,p)
  for z in [.4,1.2,2.05]:M.ring('sprayer body seam',(0,0,z),.345,.018,green,p)
  M.cylinder('yellow neck collar',(0,0,2.05),.40,.14,gold,p);M.rod('spray nozzle',(-.6,0,2.18),(0,0,2.18),.11,green,p);M.polyline('trigger loop',[(-.4,0,2.1),(-.65,0,1.9),(-.4,0,1.3),(-.25,0,1.3),(-.4,0,2.1)],.055,gold,p)
 elif n==73:
  blue=M.mat('Star Balm blue container',(.025,.10,.45),.15,.38);M.lathe('tapered open Star Balm bottle',[(.5,0),(.55,.1),(.4,1.4),(.2,1.9),(.2,2.15),(.15,2.15),(.15,1.95)],blue,p);M.mesh('pale tapered balm label',[(r*math.cos(a),r*math.sin(a),z) for z in [.6,1.4] for a in [-math.pi/2-.8+j*.1 for j in range(17)] for r in [.55+(.4-.55)*(z-.1)/1.3+.01]],[(j,j+1,j+18,j+17) for j in range(16)],cream,p);M.text('authored balm label','BALM',(0,-.46,1.1),.14,blue,p);M.cylinder('detached cap',(.7,0,0),.23,.2,blue,p)
 elif n==74:
  orange=M.mat('orange APV case',(.65,.18,.005),.25,.5);M.cube('portable rectangular payload housing',(0,0,1),(.6,.22,1),orange,p,bevel=.08)
  for x in [-.5,.5]:M.rod('handle upright',(x,0,2),(x,0,2.5),.075,orange,p)
  M.rod('carrying handle',(-.5,0,2.5),(.5,0,2.5),.075,orange,p)
  for z in [.2,.35,1.6,1.8]:M.cube('recessed case seam',(0,-.23,z),(.56,.01,.014),dark,p)
  M.cylinder('fictional hazard medallion',(0,-.24,1),.20,.02,gold,p).rotation_euler.x=math.pi/2;M.cube('hazard upright',(0,-.27,1),(.03,.01,.13),dark,p)
 elif n==75:
  purple=M.mat('Phantom purple container',(.19,.015,.45),.2,.45);M.cube('rounded purple transport shell',(0,0,1.0),(.65,.3,.95),purple,p,bevel=.14)
  for x in [-.48,.48]:M.rod('portable case handle post',(x,0,1.9),(x,0,2.25),.07,purple,p)
  M.rod('metal carrying grip',(-.48,0,2.25),(.48,0,2.25),.07,grey,p)
  for z in [.45,1.45]:
   M.cylinder('large sealed interface',(-.45,-.34,z),.20,.12,purple,p).rotation_euler.x=math.pi/2;M.cylinder('interface centre',(-.45,-.47,z),.12,.02,red,p).rotation_euler.x=math.pi/2
  M.cube('pale central band',(0,-.31,1),(.62,.018,.11),grey,p);M.ball('front identification mark',(.2,-.33,1.5),(.12,.02,.045),red,p)
 elif n==76:
  olive=M.mat('Judgement Day olive shell',(.12,.20,.08),.45,.55);M.lathe('rounded cylindrical payload',[(.3,.2),(.65,.45),(.65,1.6),(.5,1.8),(.1,1.9)],olive,p)
  for z in [.35,1.2]:M.ring('large protective guard ring',(0,0,z),.85,.04,gold,p)
  for a in [0,math.pi/2,math.pi,math.pi*1.5]:x,y=.75*math.cos(a),.75*math.sin(a);M.rod('guard upright',(x,y,.1),(x,y,1.5),.035,red,p);M.ball('support foot',(x,y,.08),(.07,)*3,grey,p)
  for x in [-.35,.35]:M.cylinder('front ribbed service pod',(x,-.5,.65),.14,.7,olive,p)
  M.cylinder('top red seal',(0,0,1.91),.15,.015,red,p)
 else:
  purple=M.mat('Silicon Death violet barrel',(.22,.015,.46),.2,.45);blue=M.mat('bright band',(.015,.24,.48),.4,.35);pink=M.mat('magenta restraint',(.42,.01,.21),.3,.45);o=M.lathe('horizontal sealed barrel',[(.2,0),(.5,.2),(.5,1.6),(.2,1.8)],purple,p);o.rotation_euler.y=math.pi/2;o.location=(-.9,0,.6)
  for i,x in enumerate([-.7,0,.7]):o=M.ring('broad coloured barrel collar',(x,0,.6),.51,.085,blue if i%2 else pink,p);o.rotation_euler.y=math.pi/2
  M.polyline('arched carry handle',[(-.65,0,1.0),(-.65,0,1.4),(.65,0,1.4),(.65,0,1.0)],.07,grey,p)
  for side in [-1,1]:o=M.lathe('sealed pointed end',[(.3,0),(0,.3)],purple,p);o.location=(side*.9,0,.6);o.rotation_euler.y=side*math.pi/2
BUILDERS.update({i:medical for i in range(69,78)})

def ores(n):
 from pathlib import Path
 if n in [78,79,80,81]:
  src=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/trading-goods/TI001/TI001.blend'
  with M.bpy.data.libraries.load(str(src),link=False) as (data,loaded):loaded.objects=data.objects
  for o in loaded.objects:
   if o.type in ['CAMERA','LIGHT']:M.bpy.data.objects.remove(o,do_unlink=True);continue
   M.COL.objects.link(o);o.name=o.name.replace('TI001',M.ID).replace('beer','bulk ore')
  return
 gold=M.mat('ore canister aged gold',(.46,.34,.09),.7,.5);grey=M.mat('canister gray metal',(.27,.31,.31),.6,.6);dark=M.mat('recessed instrument',(.025,.035,.03),.4,.6);red=M.mat('red instrumentation',(.55,.012,.005),emit=.15);col={82:(.45,.33,.06),83:(.27,.12,.035),84:(.20,.23,.20),85:(.22,.14,.26),86:(.20,.47,.035),87:(.45,.006,.008)}[n];mineral=M.mat('actual coloured mineral specimen',col,.1,.8);p=M.root('individual ore packaging')
 if n in [82,83,84]:
  M.lathe('rounded gold ore canister',[(.55,0),(.75,.1),(.75,1.6),(.80,1.65),(.60,1.9),(.25,2.0),(.1,2.05)],gold,p)
  for z in [.1,.6,1.1,1.6]:M.ring('canister cage hoop',(0,0,z),.88,.035,gold,p)
  for j in range(8):a=j*math.tau/8;M.rod('canister protective upright',(.88*math.cos(a),.88*math.sin(a),0),(.88*math.cos(a),.88*math.sin(a),1.65),.035,gold,p)
  M.cube('front terminal',(0,-.9,.35),(.3,.12,.22),grey,p);M.cube('red terminal screen',(0,-1.03,.4),(.20,.01,.07),red,p);M.cube('side cargo block',(-.95,0,.5),(.18,.23,.18),gold,p)
  M.cube('small sample tray',(1.2,-.6,.1),(.35,.3,.1),gold,p)
  for j in range(12):a=j*2.4;r=(j%3)*.07;M.ball('ore granule sample',(1.2+r*math.cos(a),-.6+r*math.sin(a),.25+(j%2)*.05),(.065,)*3,mineral,p,1)
 elif n==85:
  purple=M.mat('Dragonium armored packages',(.32,.25,.36),.3,.6)
  for i,(x,y,z) in enumerate([(-.45,-.3,.35),(.5,.4,.65)]):
   q=M.root('individual armored ore case '+str(i),(x,y,z));q.parent=p;M.cube('armored case body',(0,0,0),(.8,.4,.3),purple,q,bevel=.12)
   for x0 in [-.55,0,.55]:M.cube('case reinforcing strap',(x0,0,0),(.025,.42,.32),grey,q)
   M.cube('recessed case latch',(0,-.42,0),(.18,.02,.06),dark,q)
  M.cube('folded side cargo rail',(1.45,.3,.35),(.35,.15,.12),grey,p)
 else:
  shell=M.mat('green high-grade flask' if n==86 else 'red high-grade flask',col,.35,.4);M.lathe('spherical lower high-grade flask',[(.3,0),(.65,.1),(.85,.45),(.8,.75),(.4,1),(.3,1.15),(.3,1.8),(.15,2),(.12,2.45)],shell,p)
  for z,r in [(.2,.72),(.5,.84),(.9,.54),(1.7,.32)]:M.ring('flask assembly seam',(0,0,z),r,.025,shell,p)
  M.rod('top hand valve',(-.38,0,2.45),(.38,0,2.45),.055,shell,p)
  for side in [-1,1]:M.polyline('flask protective side handle',[(side*.3,0,1.65),(side*.48,0,1.65),(side*.48,0,1.05),(side*.3,0,1.05)],.025,shell,p)
 # The mineral shown in the original inset is authored as a separate 3D specimen, never a projected image.
 x=1.65;z=1.55
 for a,b in [((x-.45,.35,z-.55),(x+.45,.35,z-.55)),((x+.45,.35,z-.55),(x+.45,.35,z+.55)),((x+.45,.35,z+.55),(x-.45,.35,z+.55)),((x-.45,.35,z+.55),(x-.45,.35,z-.55))]:M.rod('specimen display frame',a,b,.012,gold,p)
 M.rod('specimen support',(x,.35,.1),(x,.35,z-.55),.012,gold,p);r=M.ball('separate mineral specimen',(x,.33,z),(.30,.14,.42),mineral,p,2)
 for v in r.data.vertices:v.co*=1+.13*math.sin(v.co.x*19+v.co.z*13)
BUILDERS.update({i:ores for i in range(78,88)})
