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

def braccatian(s,role):
    # Medians of the current canonical 4x2 Braccatian colour/ORM atlas tiles.
    def colour(rgb):return tuple(v/255 for v in rgb)
    ochre=s.mat('ochre',colour((192,154,85)),.68,.649)
    coral=s.mat('coral',colour((157,83,72)),.68,.645)
    grey=s.mat('dark-structure',colour((92,105,115)),.68,.645)
    bronze=s.mat('bronze',colour((115,85,48)),.68,.645)
    dark=s.mat('dark-inset',colour((13,17,20)),38/255,.649)
    length=3.35 if role=='terraform' else 2.72
    # A low forward lobe,waist and higher aft lobe,related to Rattlesnake.
    stations=[(-.50,.12,.35,.80),(-.46,.62,.35,.80),(-.32,.86,.32,.86),(-.06,.80,.32,.80),(.16,.94,.41,.95),(.36,1,.52,1.04),(.46,.88,.50,1.0),(.50,.65,.50,.90)]
    stations=[(y*length,r,z,h) for y,r,z,h in stations];n=64
    def section(y,rows=stations):
        for i,(a,b) in enumerate(zip(rows,rows[1:])):
            if a[0]-1e-8<=y<=b[0]+1e-8:
                t=(y-a[0])/(b[0]-a[0]);before=rows[max(0,i-1)];after=rows[min(len(rows)-1,i+2)]
                return tuple(.5*((2*a[k])+(-before[k]+b[k])*t+(2*before[k]-5*a[k]+4*b[k]-after[k])*t*t+(-before[k]+3*a[k]-3*b[k]+after[k])*t*t*t) for k in [1,2,3])
        raise ValueError(y)
    def smooth_rows(rows):
        return [(a[0]+(b[0]-a[0])*j/4,*section(a[0]+(b[0]-a[0])*j/4,rows)) for a,b in zip(rows,rows[1:]) for j in range(4)]+[rows[-1]]
    def loft(name,rows,mat):
        verts=[(.76*r*math.cos(i*math.tau/n),y,z+.575*r*h*math.sin(i*math.tau/n)) for y,r,z,h in rows for i in range(n)]
        count=len(rows);faces=[tuple(reversed(range(n))),tuple(range((count-1)*n,count*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(count-1) for i in range(n)]
        return s.solid(name,verts,faces,mat)
    # Stable helper lookup name retained;the material is now rose-copper.
    body=loft('Braccatian ochre barrel hull',smooth_rows(stations),coral)
    loft('Braccatian pale ochre prow',smooth_rows([(-length*.53,.12,.35,.80),(-length*.49,.64,.35,.80),(-length*.40,.84,.34,.84),(-length*.33,.87,.32,.86)]),ochre)
    def skin_patch(name,y0,y1,u0,u1,mat,lift=.012):
        ys=sorted(set([y0,y1]+[y for y,_,_,_ in stations if y0<y<y1]+[y0+(y1-y0)*i/14 for i in range(1,14)]));width=7;count=len(ys)*width;verts=[]
        for d in [lift,lift-(.050 if lift>.02 else .025)]:
            for y in ys:
                r,z,h=section(y)
                for i in range(width):
                    u=u0+(u1-u0)*i/(width-1);verts.append((.76*r*u,y,z+.575*r*h*math.sqrt(max(0,1-u*u))+d))
        faces=[]
        for j in range(len(ys)-1):
            for i in range(width-1):
                q=j*width+i;f=(q,q+1,q+width+1,q+width);faces.extend([f,tuple(count+k for k in reversed(f))])
        edge=list(range(width))+[j*width+width-1 for j in range(1,len(ys))]+list(reversed(range((len(ys)-1)*width,(len(ys)-1)*width+width-1)))+[j*width for j in reversed(range(1,len(ys)-1))]
        faces.extend((a,a+count,b+count,b) for a,b in zip(edge,edge[1:]+edge[:1]));return s.solid(name,verts,faces,mat)
    skin_patch('Braccatian dorsal broad reinforcement',-length*.25,length*.43,-.34,.34,coral)
    for side in [-1,1]:
        skin_patch('Braccatian slender ochre inlay '+str(side),-length*.28,length*.44,side*.58,side*.65,ochre)
    for y in [-length*.17,length*.08,length*.31]:skin_patch('Braccatian narrow transverse ochre band '+str(y),y-.023,y+.023,-.63,.63,ochre,lift=.032)
    s.cyl('Braccatian circular recessed prow sensor',(0,-length*.53-.006,.35),.056,.025,dark,(0,1,0))
    for x in [-.35,0,.35]:s.cyl('Braccatian rear flush outlet '+str(x),(x,length*.50+.04,.43),.13,.12,dark,(0,1,0))
    if role=='terraform':
        for x in [-.58,.58]:s.box('Braccatian fixed jaw hinge support '+str(x),(x,-1.15,-.04),(.20,.40,.85),grey,.055)
        for upper in [False,True]:
            z=.10 if upper else -.40;j=s.joint('CrusherUpper' if upper else 'CrusherLower',(0,-1.15,z));s.cyl('Braccatian crusher hinge '+str(upper),(0,-1.15,z),.13,1.0,bronze,(1,0,0),j)
            s.box('Braccatian coarse jaw '+str(upper),(0,-1.66,z),(.96,1.05,.16),grey,.05,j)
            for x in [-.33,0,.33]:s.box('Braccatian crusher tooth '+str(upper)+str(x),(x,-2.07,z+(-.07 if upper else .07)),(.20,.22,.18),bronze,.02,j)
            cycle(s,j,0,-.16 if upper else .16)
    else:
        # Fit the strap to the actual waist instead of bridging over its roof.
        verts=[]
        for y in [-.09,.09]:
            r,z,h=section(y)
            for d in [.035,-.012]:
                for i in range(n):
                    angle=i*math.tau/n;verts.append(((.76*r+d)*math.cos(angle),y,z+(.575*r*h+d)*math.sin(angle)))
        faces=[]
        for i in range(n):
            k=(i+1)%n;faces.extend([(i,k,2*n+k,2*n+i),(n+k,n+i,3*n+i,3*n+k),(k,i,n+i,n+k),(2*n+i,2*n+k,3*n+k,3*n+i)])
        s.solid('Braccatian single bronze collar',verts,faces,ochre)
        j=s.joint('VentralServiceYoke',(0,-.05,-.10));s.cyl('Braccatian ventral pivot bearing',(0,-.05,-.10),.18,.40,grey,(1,0,0));s.beam('Braccatian short ventral yoke',(0,-.05,-.10),(0,-1.24,-.42),.22,.25,bronze,j)
        s.box('Braccatian clamp crosspiece',(0,-1.28,-.42),(.85,.22,.24),bronze,.04,j)
        for sign in [-1,1]:
            x=sign*.32;finger=s.joint('Braccatian service finger '+str(sign),(x,-1.35,-.42),j)
            s.cyl('Braccatian service finger hinge '+str(sign),(x,-1.35,-.42),.08,.28,grey,parent=finger)
            s.box('Braccatian lifting prong '+str(sign),(x,-1.60,-.42),(.17,.60,.24),bronze,.04,finger)
            s.animate(finger,2,[(1,0),(25,0),(49,-sign*.24),(73,0),(97,0)])
        head=s.cyl('Braccatian adjacent steel welding head',(.54,-1.30,-.32),.17,.50,grey,(0,1,0),j);bore=s.cyl('Temporary welding bore',(.54,-1.50,-.32),.075,.40,grey,(0,1,0),j);s.cut(head,bore);s.ring('Braccatian welding nozzle rim',(.54,-1.57,-.32),.16,.075,.06,grey,(0,1,0),j);s.cyl('Braccatian recessed nozzle back',(.54,-1.285,-.32),.073,.03,grey,(0,1,0),j);s.beam('Braccatian welded head bracket',(.40,-1.28,-.42),(.54,-1.28,-.32),.18,.20,bronze,j)
        s.animate(j,0,[(1,0),(25,.14),(49,.14),(73,.035),(97,0)])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'braccatian',a.role);braccatian(s,a.role)
    s.export(__file__,['Based on the selected supplied braccatian concept;canonical-style correction with rose-copper fore/aft lobes,waist,pale ochre prow and narrow inlays. Tool articulation preserved;repair positioning precedes independent finger closure.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
