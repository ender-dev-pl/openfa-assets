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
    if len(points)>3 and 'core strap' not in name:
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

def rail(s,side,mat,dark,gold):
    # Closed clipped-section tapered beam,related to Ylikt-shan longitudinal rails.
    section=[(-.50,-.50),(.50,-.50),(.50,.18),(.25,.50),(-.25,.50),(-.50,.18)]
    stations=[(-2.12,.08),(-1.10,1),(.95,.94),(1.78,.12)];n=len(section)
    v=[(side*.84+x*.42*scale,y,z*.28) for y,scale in stations for x,z in section]
    f=[tuple(reversed(range(n))),tuple(range(3*n,4*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]
    body=s.solid('Mikotaj tapered blue-grey rail '+str(side),v,f,mat,.012)
    cutter=s.box('Temporary rail service recess',(side*.84,-.15,.17),(.10,1.10,.10),dark,.008);s.cut(body,cutter)
    s.box('Mikotaj rail dark service inset '+str(side),(side*.84,-.15,.119),(.092,1.08,.025),dark,.005)
    s.box('Mikotaj rail gold fitting '+str(side),(side*.84,-.76,.139),(.13,.14,.026),gold,.006)

def mikotaj(s,role):
    green=s.mat('blue-grey-structure',(82/255,105/255,147/255),.54,.51);copper=s.mat('frame-alloy',(72/255,83/255,100/255),.54,.51);blue=s.mat('blue-faceted-module',(82/255,105/255,147/255),.54,.51);gold=s.mat('gold-connector',(175/255,157/255,76/255),.54,.51);dark=s.mat('dark-working-plate',(.045,.055,.06),.55,.67)
    def module(name,p,size):
        w,l,h=size;outline=[(-.50,-.10),(-.12,-.58),(.12,-.58),(.50,-.10),(.42,.34),(.20,.50),(-.20,.50),(-.42,.34)]
        v=[(p[0]+x*w*scale,p[1]+y*l*scale,p[2]+z*h) for scale,z in [(.78,-.40),(1,0),(.78,.50)] for x,y in outline];n=8
        faces=[tuple(reversed(range(n))),tuple(range(2*n,3*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)]
        return s.solid(name,v,faces,blue,.045)
    if role=='terraform':
        for side in [-1,1]:rail(s,side,green,dark,gold);s.box('Mikotaj gold core connector '+str(side),(side*.57,0,.12),(.66,.52,.26),gold,.03)
        for y in [-1.5,1.5]:s.box('Mikotaj alloy end beam '+str(y),(0,y,0),(1.88,.25,.28),copper,.03)
        module('Mikotaj central faceted blue core',(0,0,.20),(1.25,1.85,.48))
        for side in [-1,1]:
            j=s.joint('FrameWorkingPlate'+str(side),(side*.45,-1.5,0));s.cyl('Mikotaj working plate hinge '+str(side),(side*.45,-1.5,0),.13,.62,copper,(1,0,0),j)
            polygon=[(side*.13,-1.48),(side*.78,-1.48),(side*.80,-2.04),(side*.15,-2.20)]
            v=[(x,y,-.16) for x,y in polygon]+[(x,y,.06 if y>-1.6 else -.07) for x,y in polygon]
            f=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
            s.solid('Mikotaj broad wedge tool '+str(side),v,f,dark,.012,j)
            alloy=s.mat('machined-alloy',(.43,.46,.48),.80,.42)
            s.box('Mikotaj worn wedge cutting edge '+str(side),(side*.47,-2.10,-.12),(.56,.10,.055),alloy,.006,j);cycle(s,j,0,.18)
    else:
        # Open triangular truss, physically connected rails and diagonal webs.
        for y in [-.25,.25]:s.box('Mikotaj alloy truss chord '+str(y),(0,y,.05),(3.10,.13,.16),copper,.02)
        for i in range(8):
            x=-1.48+i*.37;s.beam('Mikotaj triangular web '+str(i),(x,-.25,.05),(x+.37,.25,.05),.10,.16,copper)
        module('Mikotaj central faceted blue core',(0,-.02,.30),(1.16,1.35,.40))
        for side in [-1,1]:
            module('Mikotaj blue end module '+str(side),(side*1.34,-.22,.12),(.60,1.75,.30))
            curved_bar(s,'Mikotaj angular core strap '+str(side),[(side*.35,y,z) for y,z in [(-.58,.10),(-.42,.41),(-.30,.50),(.30,.50),(.48,.34),(.58,.10)]],.14,.11,green)
        j=s.joint('IntegratedFrameClamp',(0,-.37,.10));s.beam('Mikotaj clamp rooted shaft',(0,-.25,.10),(0,-.92,-.12),.24,.25,green,j);s.box('Mikotaj alloy clamp bridge',(0,-.96,-.12),(1.04,.24,.22),green,.03,j)
        for side in [-1,1]:
            finger=s.joint('MikotajClampFinger'+str(side),(side*.43,-.96,-.12),j)
            s.cyl('Mikotaj clamp finger bearing '+str(side),(side*.43,-.96,-.12),.13,.27,gold,parent=finger)
            s.box('Mikotaj alloy clamp prong '+str(side),(side*.43,-1.20,-.12),(.18,.58,.22),green,.03,finger);s.box('Mikotaj gold clamp pad '+str(side),(side*.43,-1.46,-.12),(.21,.12,.25),gold,.02,finger)
            s.animate(finger,2,[(1,0),(25,0),(49,-side*.26),(73,0),(97,0)],'rotation_euler')
        s.animate(j,0,[(1,0),(25,.14),(49,.14),(73,0),(97,0)],'rotation_euler')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'mikotaj',a.role);mikotaj(s,a.role)
    s.export(__file__,['Canonical-style cycle 3: user-directed correction toward Ylikt-shan and Hiero;canonical slate-blue/gunmetal and dulled-gold palette supersede green/copper concept colours;geometry from reviewed cycle 2 retained.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
