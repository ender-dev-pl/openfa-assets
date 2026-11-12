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

def braccatian(s,role):
    ochre=s.mat('ochre',(.53,.33,.07),.25,.70);coral=s.mat('coral',(.56,.15,.105),.20,.65);grey=s.mat('dark-structure',(.12,.13,.14),.60,.60);bronze=s.mat('bronze',(.50,.27,.10),.65,.57);dark=s.mat('dark-inset',(.025,.026,.025),.3,.80)
    length=3.35 if role=='terraform' else 2.72
    stations=[(-length*.50,.12),(-length*.46,.65),(-length*.36,1),(length*.36,1),(length*.46,.65),(length*.50,.12)];n=32
    verts=[(.76*r*math.cos(i*2*math.pi/n),y,.40+.575*r*math.sin(i*2*math.pi/n)) for y,r in stations for i in range(n)]
    faces=[tuple(reversed(range(n))),tuple(range(5*n,6*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(5) for i in range(n)]
    body=s.solid('Braccatian ochre barrel hull',verts,faces,ochre)
    for f in body.data.polygons:f.use_smooth=True
    for y in [-length*.40,length*.40]:
        rings=[(y-.36,.90),(y-.28,1),(y+.28,1),(y+.36,.90)]
        vv=[(.60*r*math.cos(i*2*math.pi/n),yy,.40+.465*r*math.sin(i*2*math.pi/n)) for yy,r in rings for i in range(n)]
        ff=[tuple(reversed(range(n))),tuple(range(3*n,4*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]
        s.solid('Braccatian coral end cap '+str(y),vv,ff,coral)
    s.box('Braccatian dorsal broad reinforcement',(0,.05,.96),(.45,length*.73,.12),grey,.045)
    for x in [-.735,.735]:s.box('Braccatian heavy longitudinal reinforcement '+str(x),(x,.05,.40),(.14,length*.74,.34),grey,.04)
    s.box('Braccatian thin sensor slot',(0,-length*.40-.375,.50),(.72,.08,.13),dark,.025)
    for x,z in [(-.33,.63),(.33,.63),(-.33,.18),(.33,.18)]:s.cyl('Braccatian front gold point '+str(x)+str(z),(x,-length*.40-.375,z),.035,.055,bronze,(0,1,0),vertices=16)
    for x in [-.35,0,.35]:s.cyl('Braccatian rear flush outlet '+str(x),(x,length*.40+.375,.40),.13,.12,dark,(0,1,0))
    if role=='terraform':
        for x in [-.58,.58]:s.box('Braccatian fixed jaw hinge support '+str(x),(x,-1.15,-.04),(.20,.40,.85),grey,.055)
        for upper in [False,True]:
            z=.10 if upper else -.40;j=s.joint('CrusherUpper' if upper else 'CrusherLower',(0,-1.15,z));s.cyl('Braccatian crusher hinge '+str(upper),(0,-1.15,z),.13,1.0,bronze,(1,0,0),j)
            s.box('Braccatian coarse jaw '+str(upper),(0,-1.66,z),(.96,1.05,.16),grey,.05,j)
            for x in [-.33,0,.33]:s.box('Braccatian crusher tooth '+str(upper)+str(x),(x,-2.07,z+(-.07 if upper else .07)),(.20,.22,.18),bronze,.02,j)
            cycle(s,j,0,-.16 if upper else .16)
    else:
        collar=s.ring('Braccatian single bronze collar',(0,0,.40),.81,.68,.29,bronze,(0,1,0))
        for v in collar.data.vertices:v.co.z=.40+(v.co.z-.40)*.83
        j=s.joint('VentralServiceYoke',(0,-.05,-.10));s.cyl('Braccatian ventral pivot bearing',(0,-.05,-.10),.18,.40,grey,(1,0,0));s.beam('Braccatian short ventral yoke',(0,-.05,-.10),(0,-1.24,-.42),.22,.25,bronze,j)
        s.box('Braccatian clamp crosspiece',(0,-1.28,-.42),(.85,.22,.24),bronze,.04,j)
        for x in [-.32,.32]:s.box('Braccatian lifting prong '+str(x),(x,-1.60,-.42),(.17,.60,.24),bronze,.04,j)
        s.cyl('Braccatian adjacent steel welding head',(.54,-1.30,-.32),.17,.50,grey,(0,1,0),j);s.beam('Braccatian welded head bracket',(.40,-1.28,-.42),(.54,-1.28,-.32),.18,.20,bronze,j);cycle(s,j,0,.14)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'braccatian',a.role);braccatian(s,a.role)
    s.export(__file__,['Based on the selected supplied braccatian concept;culture-specific hull,working tool and articulation.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
