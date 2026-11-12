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

def fairing(s,name,p,size,mat,port=False):
    outline=([(-.44,-.50),(.44,-.50),(.50,-.18),(.44,.30),(.20,.50),(-.20,.50),(-.44,.30),(-.50,-.18)] if port else [(-.10,-.58),(.10,-.58),(.50,-.15),(.44,.34),(.20,.50),(-.20,.50),(-.44,.34),(-.50,-.15)])
    w,l,h=size;n=len(outline)
    v=[(p[0]+x*w*scale,p[1]+y*l*scale,p[2]+z*h) for scale,z in [(.90,-.50),(1,-.10),(.62,.50)] for x,y in outline]
    f=[tuple(reversed(range(n))),tuple(range(2*n,3*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)]
    return s.solid(name,v,f,mat,.014)


def artemian(s,role):
    # Current canonical atlas medians,not colours guessed from the lit concept.
    silver=s.mat('silver-shell',(136/255,144/255,147/255),198/255-.12,139/255+.08)
    green=s.mat('deep-green',(61/255,128/255,71/255),198/255-.12,140/255+.08)
    dark=s.mat('dark-slots',(16/255,21/255,25/255),30/255,140/255+.08)
    edge=s.mat('canonical-silver-edge',(170/255,180/255,184/255),198/255-.12,140/255+.08)
    plate(s,'Artemian green wedge hull',[(-.12,-2.05),(.12,-2.05),(1.42,.87),(1.15,1.42),(-1.15,1.42),(-1.42,.87)],.11,.24,green)
    fairing(s,'Artemian single silver shell main fairing',(0,.12,.42),(.76,2.30,.56),silver)
    for side in [-1,1]:
        x=side*.96;pod=fairing(s,'Artemian silver tool fairing '+str(side),(x,-.12,.35),(.58,1.72,.44),silver,True)
        cutter=s.box('Temporary actual sliding tool aperture',(x,-1.14,.24),(.44,.52,.29),dark,.008);s.cut(pod,cutter)
    for y in [.30,.66]:
        for x in [-.12,0,.12]:s.box('Artemian sparse dorsal vent '+str(y)+str(x),(x,y,.705),(.055,.24,.035),dark,.008)
    for side in [-1,1]:
        x=side*.66;s.box('Artemian green service hatch '+str(side),(x,.94,.242),(.34,.38,.025),green,.012)
        for y in [.87,1.00]:s.box('Artemian green hatch inset '+str(side)+str(y),(x,y,.255),(.20,.045,.018),dark,.004)
    for side in [-1,1]:
        x=side*.96;s.box('Artemian front recessed tool slot '+str(side),(x,-.88,.24),(.40,.025,.27),dark,.018)
        j=s.joint('DirectToolSlide'+str(side),(x,-1.22,.23));s.box('Artemian inner sliding tool rail '+str(side),(x,-1.05,.23),(.28,.55,.18),green,.02,j)
        if role=='terraform':
            polygon=[(x-.23,-1.19),(x+.23,-1.19),(x+.24,-2.02),(x-.24,-2.18)]
            v=[(px,py,.10) for px,py in polygon]+[(px,py,.34 if py>-1.5 else .19) for px,py in polygon]
            f=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
            s.solid('Artemian stout green wedge '+str(side),v,f,green,.014,j)
            s.box('Artemian replaceable wedge edge '+str(side),(x,-2.09,.16),(.43,.10,.055),edge,.006,j)
        elif side<0:
            wrist=s.joint('ArtemianGripperWrist',(x,-1.46,.23),j)
            s.box('Artemian short gripper bridge',(x,-1.46,.23),(.47,.40,.20),silver,.025,wrist)
            for sign in [-1,1]:
                finger=s.joint('ArtemianGripperFinger'+str(sign),(x+sign*.17,-1.60,.23),wrist)
                s.cyl('Artemian gripper finger bearing '+str(sign),(x+sign*.17,-1.60,.23),.065,.23,edge,parent=finger)
                s.box('Artemian short gripper tine '+str(sign),(x+sign*.17,-1.82,.23),(.13,.45,.20),silver,.018,finger)
                s.animate(finger,2,[(1,0),(25,0),(49,-sign*.20),(73,0),(97,0)],'rotation_euler')
            s.animate(wrist,0,[(1,0),(25,.12),(49,.12),(73,0),(97,0)],'rotation_euler')
        else:
            blade=s.box('Artemian broad service blade',(x,-1.63,.23),(.39,.94,.19),silver,.025,j)
            for y in [-1.56,-1.75,-1.94]:
                cutter=s.box('Temporary service blade recess',(x,y,.335),(.28,.07,.08),dark,.006,j);s.cut(blade,cutter)
                s.box('Artemian service blade slot '+str(y),(x,y,.302),(.27,.06,.025),dark,.004,j)
        start=j.location.y;s.animate(j,1,[(1,start),(25,start-.11),(49,start-.11),(73,start),(97,start)],'location')
    if role=='repair':s.placement.scale=(.84,.84,.84)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'artemian',a.role);artemian(s,a.role)
    s.export(__file__,['Canonical-style cycle 2:user-directed green wedge deck and separate silver fairings based on current All-Purpose Assault and Gerla-Kans Explorer;supersedes the oval concept silhouette.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
