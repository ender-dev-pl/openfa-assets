"""Culture-specific engineering proposals from the supplied selected concepts."""
import argparse,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from engineering_ship_common import Ship



def cycle(s,j,axis,amount,kind='rotation_euler'):
    start=getattr(j,kind)[axis]
    s.animate(j,axis,[(1,start),(25,start+amount),(49,start),(73,start-amount*.35),(97,start)],kind)

def plate(s,name,polygon,z,depth,mat,parent=None):
    n=len(polygon);v=[(x,y,z+d) for d in [-depth/2,depth/2] for x,y in polygon]
    return s.solid(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,.025,parent)

def curved_bar(s,name,points,width,depth,mat,parent=None):
    # Solid quadrilateral-section continuous curved tool, rather than loose rods.
    verts=[]
    for i,p in enumerate(points):
        prev=Vector(points[max(0,i-1)]);nxt=Vector(points[min(len(points)-1,i+1)]);t=(nxt-prev).normalized();normal=Vector((-t.y,t.x,0)).normalized()
        verts += [tuple(Vector(p)+normal*w+Vector((0,0,z))) for w,z in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]]
    faces=[(3,2,1,0),tuple(range(len(verts)-4,len(verts)))]
    for i in range(len(points)-1):
        for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    return s.solid(name,verts,faces,mat,.025,parent)

def repair_tool(s,prefix,a,b,c,steel,copper,gold,left=True,parent=None):
    j=s.joint(prefix+'Shoulder',a,parent);s.cyl(prefix+' shoulder bearing',a,.14,.22,copper,(1,0,0),j);s.beam(prefix+' upper link',a,b,.19,.20,steel,j)
    k=s.joint(prefix+'Elbow',b,j);s.cyl(prefix+' elbow bearing',b,.14,.22,steel,(1,0,0),k);s.beam(prefix+' lower link',b,c,.19,.20,steel,k)
    if left:
        s.box(prefix+' clamp bridge',(c[0],c[1]-.08,c[2]),(.48,.20,.20),steel,.06,k)
        for sign in [-1,1]:s.box(prefix+' copper gripping jaw '+str(sign),(c[0]+sign*.18,c[1]-.28,c[2]),(.14,.38,.20),copper,.055,k)
    else:
        s.cyl(prefix+' nozzle housing',(c[0],c[1]-.1,c[2]),.14,.27,steel,(0,1,0),k);s.ring(prefix+' gold nozzle',(c[0],c[1]-.29,c[2]),.12,.06,.22,gold,(0,1,0),k)
    cycle(s,j,0,.16 if left else -.12);cycle(s,k,0,-.28 if left else .22)

def ribbon(s,name,stations,thick,mat,parent=None):
    verts=[(x+dx,y,z) for y,x,lo,hi in stations for dx,z in [(-thick/2,lo),(thick/2,lo),(thick/2,hi),(-thick/2,hi)]]
    n=len(stations);faces=[(3,2,1,0),tuple(range(4*n-4,4*n))]+[(4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j) for i in range(n-1) for j in range(4)]
    return s.solid(name,verts,faces,mat,.006,parent)

def achaean(s,role):
    copper=s.mat('copper-hull',(.56,.26,.17),.50,.58);red=s.mat('red-crescent',(.40,.065,.045),.30,.62);silver=s.mat('silver-rim',(.54,.57,.56),.70,.47);dark=s.mat('dark-visor',(.025,.035,.04),.45,.30)
    s.ellipsoid('Achaean long copper spindle',(0,0,.30),(1.13,3.70,.95),copper);s.box('Achaean tiny front visor',(0,-1.58,.57),(.30,.20,.08),dark,.025)
    for y in [-.35,.55]:s.box('Achaean quiet dorsal hatch '+str(y),(0,y,.76),(.31,.28,.045),copper,.035)
    if role=='terraform':
        base=[(-1.58,.24,.32,.34),(-.9,.58,.47,.65),(0,.78,.57,.85),(.9,.74,.75,1.03),(1.6,.48,.98,1.08),(1.82,.32,1.02,1.04)]
        for side in [-1,1]:
            stations=[(y,side*x,lo,hi) for y,x,lo,hi in base];ribbon(s,'Achaean slender silver crescent '+str(side),stations,.10,silver)
            for face in [-1,1]:ribbon(s,'Achaean red blade field '+str(side)+str(face),[(y,side*x+face*.048,lo+.035,hi-.035) for y,x,lo,hi in base[1:5]],.018,red)
            s.beam('Achaean short blade root '+str(side),(side*.34,.18,.45),(side*.72,.18,.72),.17,.18,copper)
        j=s.joint('CrescentGraderPivot',(0,-.94,-.02));s.beam('Achaean grader rooted support',(0,-.94,.08),(0,-1.95,-.32),.22,.23,copper,j)
        pts=[(.91*math.cos(t),-1.50-.45*math.sin(t),-.32+.20*abs(math.cos(t))) for t in [i*math.pi/16 for i in range(17)]]
        curved_bar(s,'Achaean broad copper crescent grader',pts,.18,.26,copper,j);curved_bar(s,'Achaean silver grading edge',[(x,y,z-.13) for x,y,z in pts],.20,.04,silver,j);cycle(s,j,0,.15)
    else:
        top=[(-1.5,0,.56,.58),(-.9,0,.85,1.03),(0,0,1.07,1.27),(.9,0,.96,1.18),(1.5,0,.55,.66)]
        ribbon(s,'Achaean silver overhead arch',top,.12,silver)
        for face in [-1,1]:ribbon(s,'Achaean red overhead arch field '+str(face),[(y,face*.058,lo+.04,hi-.04) for y,x,lo,hi in top[1:4]],.02,red)
        # Broad side crescent closes around the rear boss, with a separate movable lower support.
        yz=[(-1.55,.37),(-.4,.78),(.8,.83),(1.35,.42),(1.38,-.16),(.85,-.58),(.55,-.63),(1.07,-.12),(.98,.24),(.65,.53),(-.4,.57),(-1.55,.35)]
        n=len(yz);v=[(x,y,z) for x in [.46,.58] for y,z in yz];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];s.solid('Achaean silver side crescent',v,faces,silver,.012)
        # A narrow red side inset stays within the silver outline.
        inner=[(-1.20,.41),(-.35,.72),(.75,.75),(1.25,.40),(1.28,-.10),(.86,-.48),(1.15,-.10),(1.06,.25),(.68,.59),(-.35,.62)]
        nn=len(inner);vv=[(x,y,z) for x in [.572,.595] for y,z in inner];ff=[tuple(reversed(range(nn))),tuple(range(nn,2*nn))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)];s.solid('Achaean red side crescent field',vv,ff,red,.006)
        s.cyl('Achaean side circular boss',(.50,.52,.24),.24,.17,silver,(1,0,0));s.cyl('Achaean red boss inset',(.59,.52,.24),.18,.04,red,(1,0,0));s.beam('Achaean boss to fixed blade root',(.50,.52,.24),(.52,.70,.60),.18,.18,copper)
        j=s.joint('CurvedServiceSupport',(.50,.52,.24));pts=[(.50,.52,.24),(.52,.35,-.05),(.45,0,-.28),(.26,-.45,-.45),(.08,-.95,-.49),(0,-1.55,-.48)]
        curved_bar(s,'Achaean silver curved service spine',pts,.19,.25,silver,j);curved_bar(s,'Achaean red service spine inset',[(x,y,z+.11) for x,y,z in pts],.12,.04,red,j)
        s.box('Achaean copper tool housing',(0,-1.60,-.48),(.65,.35,.28),copper,.09,j)
        for x in [-.20,.12]:s.box('Achaean silver lifting claw '+str(x),(x,-1.91,-.48),(.11,.42,.21),silver,.035,j)
        s.cyl('Achaean adjacent silver service nozzle',(.31,-1.75,-.48),.11,.36,silver,(0,1,0),j);s.beam('Achaean nozzle root',(.25,-1.60,-.48),(.31,-1.69,-.48),.17,.18,copper,j);cycle(s,j,0,.14)
        s.placement.scale=(.88,.88,.88)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'achaean',a.role);achaean(s,a.role)
    s.export(__file__,['Based on selected supplied Achaean concepts;slender red/silver arches around a copper spindle.','Working crescent grader or rooted curved service support is animated. Rear/hidden engineering and scale are authored;no game mechanics,unit registration or integration.'])
