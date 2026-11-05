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
