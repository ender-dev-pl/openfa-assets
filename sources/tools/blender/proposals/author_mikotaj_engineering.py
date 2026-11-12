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

def mikotaj(s,role):
    green=s.mat('green-structure',(.11,.31,.18),.35,.58);copper=s.mat('copper-frame',(.54,.26,.11),.65,.57);blue=s.mat('blue-faceted-module',(.11,.28,.51),.45,.42);gold=s.mat('gold-connector',(.62,.41,.11),.7,.5);dark=s.mat('dark-working-plate',(.045,.055,.06),.55,.67)
    def module(name,p,size):
        w,l,h=size;outline=[(-.50,-.15),(-.28,-.50),(.28,-.50),(.50,-.15),(.42,.34),(.20,.50),(-.20,.50),(-.42,.34)]
        v=[(p[0]+x*w*scale,p[1]+y*l*scale,p[2]+z*h) for scale,z in [(.78,-.40),(1,0),(.78,.50)] for x,y in outline];n=8
        faces=[tuple(reversed(range(n))),tuple(range(2*n,3*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)]
        return s.solid(name,v,faces,blue,.045)
    if role=='terraform':
        for side in [-1,1]:s.box('Mikotaj long green rail '+str(side),(side*.84,0,0),(.22,3.25,.24),green,.025);s.box('Mikotaj gold core connector '+str(side),(side*.57,0,.12),(.66,.52,.26),gold,.03)
        for y in [-1.5,1.5]:s.box('Mikotaj copper end beam '+str(y),(0,y,0),(1.88,.25,.28),copper,.03)
        module('Mikotaj central faceted blue core',(0,0,.20),(1.42,1.60,.60))
        for side in [-1,1]:
            j=s.joint('FrameWorkingPlate'+str(side),(side*.45,-1.5,0));s.cyl('Mikotaj working plate hinge '+str(side),(side*.45,-1.5,0),.13,.62,copper,(1,0,0),j)
            plate(s,'Mikotaj broad wedge tool '+str(side),[(side*.13,-1.48),(side*.78,-1.48),(side*.80,-2.04),(side*.15,-2.20)],-.05,.22,dark,j);cycle(s,j,0,.18)
    else:
        # Open triangular truss, physically connected rails and diagonal webs.
        for y in [-.25,.25]:s.box('Mikotaj copper truss chord '+str(y),(0,y,.05),(3.65,.13,.16),copper,.02)
        for i in range(8):
            x=-1.70+i*.425;s.beam('Mikotaj triangular web '+str(i),(x,-.25,.05),(x+.425,.25,.05),.10,.16,copper)
        module('Mikotaj central faceted blue core',(0,-.02,.30),(1.16,1.1,.52))
        for side in [-1,1]:
            module('Mikotaj blue end module '+str(side),(side*1.62,0,.12),(.75,.80,.36))
            curved_bar(s,'Mikotaj green core strap '+str(side),[(side*.35,y,z) for y,z in [(-.58,.10),(-.42,.48),(-.30,.59),(.30,.59),(.48,.39),(.58,.10)]],.14,.11,green)
        j=s.joint('IntegratedFrameClamp',(0,-.37,.10));s.beam('Mikotaj clamp rooted shaft',(0,-.25,.10),(0,-.92,-.12),.24,.25,green,j);s.box('Mikotaj green clamp bridge',(0,-.96,-.12),(1.04,.24,.22),green,.03,j)
        for side in [-1,1]:
            finger=s.joint('MikotajClampFinger'+str(side),(side*.43,-.96,-.12),j)
            s.cyl('Mikotaj clamp finger bearing '+str(side),(side*.43,-.96,-.12),.13,.27,gold,parent=finger)
            s.box('Mikotaj green clamp prong '+str(side),(side*.43,-1.20,-.12),(.18,.58,.22),green,.03,finger);s.box('Mikotaj gold clamp pad '+str(side),(side*.43,-1.46,-.12),(.21,.12,.25),gold,.02,finger)
            cycle(s,finger,2,-side*.12)
        cycle(s,j,0,.18)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'mikotaj',a.role);mikotaj(s,a.role)
    s.export(__file__,['Based on the selected supplied mikotaj concept;culture-specific hull,working tool and articulation.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
