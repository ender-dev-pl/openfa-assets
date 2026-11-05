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
