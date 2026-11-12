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

def rigellian(s,role):
    silver=s.mat('silver',(.50,.56,.59),.65,.46);green=s.mat('sage',(.16,.28,.20),.25,.66);gold=s.mat('gold',(.65,.43,.12),.65,.50);copper=s.mat('copper',(.54,.28,.16),.65,.55);dark=s.mat('recess',(.035,.045,.04),.35,.7)
    s.ellipsoid('Rigellian smooth oval hull',(0,0,.35),(2.35,2.85,1.10),silver)
    # Curved green longitudinal fields conform to the actual oval surface.
    for side in [-1,1]:
        verts=[];nx=3;ny=12
        for layer in [-.018,.012]:
            for j in range(ny):
                y=-1.04+j*1.95/(ny-1)
                for i in range(nx):
                    x=side*(.52+i*.12);z=.35+.55*math.sqrt(max(.01,1-(x/1.175)**2-(y/1.425)**2));verts.append((x,y,z+layer))
        n=nx*ny;faces=[]
        for j in range(ny-1):
            for i in range(nx-1):
                q=j*nx+i;faces.extend([(q,q+1,q+1+nx,q+nx),(n+q+nx,n+q+1+nx,n+q+1,n+q)])
        edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(n-2,n-nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
        for i,q in enumerate(edge):t=edge[(i+1)%len(edge)];faces.append((q,t,t+n,q+n))
        s.solid('Rigellian curved green field '+str(side),verts,faces,green)
        x=side*1.13;pod=s.ellipsoid('Rigellian smooth side nacelle '+str(side),(x,.27,.35),(.66,1.72,.65),silver)
        y=-.48 if role=='terraform' else 1.0
        s.ring('Rigellian copper engine mouth '+str(side),(x,y,.35),.26,.18,.18,copper,(0,1,0));hole=s.cyl('Temporary nacelle bore',(x,y,.35),.181,.50,dark,(0,1,0));s.cut(pod,hole);s.cyl('Rigellian blind dark engine '+str(side),(x,-.235 if role=='terraform' else .755,.35),.18,.035,dark,(0,1,0))
    if role=='terraform':s.cyl('Rigellian round gold dorsal cap',(0,.32,.86),.39,.16,gold)
    else:s.box('Rigellian oblong gold dorsal cap',(0,.30,.87),(.53,.92,.16),gold,.15)
    if role=='terraform':
        for side in [-1,1]:
            j=s.joint('PrecisionHornPivot'+str(side),(side*.55,-1.03,.18));s.cyl('Rigellian horn root bearing '+str(side),(side*.55,-1.03,.18),.15,.22,silver,(0,0,1),j)
            pts=[(side*x,y,.10) for x,y in [(.55,-1.00),(.76,-1.22),(.80,-1.52),(.72,-1.80)]]
            curved_bar(s,'Rigellian thick precision horn '+str(side),pts,.32,.30,silver,j);s.box('Rigellian copper working pad '+str(side),(side*.72,-1.82,.10),(.30,.20,.30),copper,.055,j);cycle(s,j,2,side*.12)
    else:
        for side in [-1,1]:repair_tool(s,'Rigellian '+('grip' if side<0 else 'weld'),(side*.66,-1.03,.22),(side*.88,-1.43,.08),(side*.72,-1.80,-.05),silver,copper,gold,side<0)
        s.placement.scale=(.83,.83,.83)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'rigellian',a.role);rigellian(s,a.role)
    s.export(__file__,['Based on the selected supplied rigellian concept;culture-specific hull,working tool and articulation.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
