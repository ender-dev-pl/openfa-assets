"""Culture-specific engineering proposals from the supplied selected concepts."""
import argparse,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from engineering_ship_refinement import RefinedShip as Ship



def cycle(s,j,axis,amount,kind='rotation_euler'):
    start=getattr(j,kind)[axis]
    s.animate(j,axis,[(1,start),(25,start+amount),(49,start),(73,start-amount*.35),(97,start)],kind)

def plate(s,name,polygon,z,depth,mat,parent=None):
    n=len(polygon);v=[(x,y,z+d) for d in [-depth/2,depth/2] for x,y in polygon]
    return s.solid(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,.025,parent)

def curved_bar(s,name,points,width,depth,mat,parent=None):
    # Solid quadrilateral-section continuous curved tool, rather than loose rods.
    if len(points)>3:
        raw=[Vector(p) for p in points];dense=[]
        for i in range(len(raw)-1):
            a=raw[max(0,i-1)];b=raw[i];c=raw[i+1];d=raw[min(len(raw)-1,i+2)]
            for step in range(5):
                t=step/5;dense.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
        points=dense+[tuple(raw[-1])]
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

def mauna(s,role):
    grey=s.mat('matte-grey',(.36,.39,.41),.25,.72);blue=s.mat('blue-grey',(.20,.29,.34),.30,.65);orange=s.mat('orange-mark',(.66,.20,.035),.15,.65);dark=s.mat('dark-recess',(.035,.043,.05),.30,.75)
    if role=='terraform':
        s.box('Mauna long monolithic hull',(0,0,.35),(1.60,3.8,.70),grey,.10)
        v=[(-.57,-1.50,.58),(.57,-1.50,.58),(.57,1.25,.58),(-.57,1.25,.58),(-.52,.35,1.08),(.52,.35,1.08),(.52,1.15,1.08),(-.52,1.15,1.08)];s.solid('Mauna sloping central housing',v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],grey,.035)
        for side in [-1,1]:
            s.box('Mauna long side service recess '+str(side),(side*.80,0,.34),(.035,2.75,.20),dark,.025)
            for z in [.78,.88,.98]:s.box('Mauna wedge side vent '+str(side)+str(z),(side*.544,.75,z),(.035,.55,.045),dark,.01)
        s.box('Mauna front dark service slot',(0,-1.90,.39),(1.18,.035,.18),dark,.02);s.box('Mauna orange rear marker',(0,1.50,.72),(.50,.28,.08),orange,.02)
        j=s.joint('GradingBladePivot',(0,-1.26,.05))
        for side in [-1,1]:s.box('Mauna blade mounting block '+str(side),(side*.46,-1.67,-.05),(.26,.80,.42),grey,.025,j)
        s.box('Mauna wide grading blade',(0,-2.00,-.27),(1.55,.45,.21),dark,.02,j)
        for x in [-.57,-.19,.19,.57]:s.box('Mauna broad grading tooth '+str(x),(x,-2.30,-.27),(.24,.27,.21),dark,.018,j)
        cycle(s,j,0,.16)
    else:
        s.box('Mauna squat slab hull',(0,0,.18),(2.05,2.55,.53),grey,.08)
        for side in [-1,1]:
            x=side*.66;s.box('Mauna tall blue stepped tower '+str(side),(x,.25,.87),(.57,1.27,1.10),grey,.035);s.box('Mauna grey tower crown '+str(side),(x,.35,1.42),(.64,1.35,.18),blue,.03);s.box('Mauna vertical dark tower field '+str(side),(x,-.39,.94),(.32,.035,.70),dark,.02)
            for z in [.64,1.04]:s.box('Mauna blue tower side shelf '+str(side)+str(z),(side*.96,.25,z),(.11,1.35,.12),blue,.015)
            for y in [-.55,-.23,.09,.41]:s.box('Mauna low side vent '+str(side)+str(y),(side*1.025,y,.19),(.028,.15,.13),dark,.01)
        for side in [-1,1]:s.box('Mauna front lintel support post '+str(side),(side*.82,-.76,.48),(.21,.29,.30),grey,.025)
        s.box('Mauna overhead crossbeam',(0,.45,1.16),(1.45,.28,.25),grey,.035);s.box('Mauna front tool lintel',(0,-.76,.65),(1.85,.30,.26),grey,.035);s.box('Mauna small orange marker',(0,-.76,.80),(.34,.20,.08),orange,.015)
        for side in [-1,1]:
            x=side*.47;j=s.joint('MaunaServiceSlide'+str(side),(x,-.72,.37));s.box('Mauna rooted tool slider '+str(side),(x,-.96,.37),(.29,.60,.28),grey,.025,j)
            if side<0:
                s.box('Mauna clamp bridge',(x,-1.28,.37),(.48,.17,.24),grey,.02,j)
                for offset in [-.18,.18]:s.box('Mauna squared clamp jaw '+str(offset),(x+offset,-1.48,.37),(.12,.34,.24),grey,.02,j)
            else:s.box('Mauna short square service head',(x,-1.38,.37),(.34,.28,.28),blue,.025,j);s.box('Mauna service dark face',(x,-1.53,.37),(.20,.03,.16),dark,.01,j)
            cycle(s,j,1,.13,'location')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'mauna',a.role);mauna(s,a.role)
    s.export(__file__,['Based on the selected supplied mauna concept;culture-specific hull,working tool and articulation.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
