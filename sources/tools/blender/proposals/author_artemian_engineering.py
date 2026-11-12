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

def artemian(s,role):
    silver=s.mat('silver-shell',(.53,.58,.57),.65,.50);green=s.mat('deep-green',(.075,.23,.13),.35,.60);dark=s.mat('dark-slots',(.025,.035,.03),.4,.70)
    rim=s.ellipsoid('Artemian green lower rim',(0,0,.18),(2.18,3.22,.55),green);shell=s.ellipsoid('Artemian single silver shell',(0,.05,.39),(2.16,3.12,.84),silver)
    for part in [rim,shell]:
        cutter=s.box('Temporary blunt nose cut',(0,-2.20,.40),(4,2,3),dark,0);s.cut(part,cutter)
        for x in [-.47,.47]:
            cutter=s.box('Temporary actual sliding tool aperture',(x,-1.30,.23),(.56,.65,.32),dark,0);s.cut(part,cutter)
    for cx,y in [(-.60,-.45),(.60,-.45),(0,.95)]:
        for offset in [-.12,0,.12]:
            x=cx+offset;z=.39+.42*math.sqrt(max(.01,1-(x/1.08)**2-((y-.05)/1.56)**2));s.box('Artemian sparse dorsal vent '+str(cx)+str(offset),(x,y,z),(.055,.24,.035),dark,.01)
    for side in [-1,1]:
        x=side*.47;s.box('Artemian front recessed tool slot '+str(side),(x,-.965,.23),(.54,.025,.30),dark,.045);j=s.joint('DirectToolSlide'+str(side),(x,-1.22,.23));s.box('Artemian inner sliding tool rail '+str(side),(x,-1.05,.23),(.28,.55,.18),green,.02,j)
        if role=='terraform':plate(s,'Artemian stout green wedge '+str(side),[(x-.24,-1.19),(x+.24,-1.19),(x+.25,-2.02),(x-.25,-2.18)],.22,.24,green,j)
        elif side<0:
            s.box('Artemian short gripper bridge',(x,-1.46,.23),(.47,.40,.20),silver,.045,j)
            for offset in [-.17,.17]:s.box('Artemian short gripper tine '+str(offset),(x+offset,-1.80,.23),(.13,.45,.20),silver,.035,j)
        else:
            s.box('Artemian broad service blade',(x,-1.63,.23),(.39,.94,.19),silver,.04,j)
            for y in [-1.56,-1.75,-1.94]:s.box('Artemian service blade slot '+str(y),(x,y,.33),(.28,.07,.035),dark,.01,j)
        cycle(s,j,1,.12 if side<0 else .09,'location')
    if role=='repair':s.placement.scale=(.84,.84,.84)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'artemian',a.role);artemian(s,a.role)
    s.export(__file__,['Based on the selected supplied artemian concept;culture-specific hull,working tool and articulation.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
