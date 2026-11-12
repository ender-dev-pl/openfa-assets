"""Culture-specific engineering proposals from the supplied selected concepts."""
import argparse,math,sys
import bpy,numpy as np
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

def ribbon(s,name,stations,thick,mat,parent=None):
    raw=[Vector(p) for p in stations];dense=[]
    for i in range(len(raw)-1):
        a=raw[max(0,i-1)];b=raw[i];c=raw[i+1];d=raw[min(len(raw)-1,i+2)]
        for step in range(6):
            t=step/6;p=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            p[3]=max(p[3],p[2]+.012);dense.append(tuple(p))
    stations=dense+[tuple(raw[-1])]
    verts=[(x+dx,y,z) for y,x,lo,hi in stations for dx,z in [(-thick/2,lo),(thick/2,lo),(thick/2,hi),(-thick/2,hi)]]
    n=len(stations);faces=[(3,2,1,0),tuple(range(4*n-4,4*n))]+[(4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j) for i in range(n-1) for j in range(4)]
    return s.solid(name,verts,faces,mat,.006,parent)

def achaean(s,role):
    def canonical_mat(name,rgb,metal,rough):
        mat=s.mat(name,tuple(v/255 for v in rgb),metal,rough+.08)
        # The shared helper boosts metals above .4;fit the actual authored ORM median.
        node=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image.name.startswith(name+'-orm'))
        old=node.image;w,h=old.size;pixels=np.empty(w*h*4,dtype=np.float32);old.pixels.foreach_get(pixels);pixels=pixels.reshape(h,w,4)
        pixels[:,:,2]=np.clip(pixels[:,:,2]+metal-np.median(pixels[:,:,2]),0,1)
        pixels[:,:,1]=np.clip(pixels[:,:,1]+rough-np.median(pixels[:,:,1]),0,1)
        node.image=s.texture(name+'-orm',pixels,True)
        assert old.users==0;bpy.data.images.remove(old)
        return mat
    copper=canonical_mat('copper-hull',(141,72,41),115/255,141/255)
    red=canonical_mat('red-crescent',(118,41,37),115/255,141/255)
    silver=canonical_mat('silver-rim',(153,154,146),210/255,102/255)
    dark=canonical_mat('dark-visor',(34,40,42),155/255,159/255)
    # Retain the spindle's envelope but give it the canonical pointed forebody.
    profile=[(-1.85,.018,.02),(-1.5,.11,.10),(-1.0,.35,.28),(-.4,.52,.43),(.25,.565,.475),(.95,.43,.35),(1.5,.19,.19),(1.85,.04,.04)]
    def section(i,t):
        a=profile[max(0,i-1)];b=profile[i];c=profile[i+1];d=profile[min(len(profile)-1,i+2)]
        return [b[0]+(c[0]-b[0])*t]+[max(.008,.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t)) for k in [1,2]]
    rows=[section(i,j/4) for i in range(len(profile)-1) for j in range(4)]+[profile[-1]];n=64
    vertices=[(w*math.cos(i*math.tau/n),y,.30+h*math.sin(i*math.tau/n)) for y,w,h in rows for i in range(n)]
    faces=[tuple(reversed(range(n))),tuple(range((len(rows)-1)*n,len(rows)*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rows)-1) for i in range(n)]
    body=s.solid('Achaean long copper spindle',vertices,faces,copper)
    s.roof(body,'Achaean tiny front visor',0,-1.25,(.22,.16),dark,.025)
    for y in [-.35,.55]:s.roof(body,'Achaean quiet dorsal hatch '+str(y),0,y,(.31,.28),copper,.035)
    if role=='terraform':
        base=[(-1.58,.24,.32,.34),(-.9,.58,.47,.65),(0,.78,.57,.85),(.9,.74,.75,1.03),(1.6,.48,.98,1.08),(1.82,.32,1.02,1.04)]
        for side in [-1,1]:
            stations=[(y,side*x,lo,hi) for y,x,lo,hi in base];ribbon(s,'Achaean slender silver crescent '+str(side),stations,.10,silver)
            for face in [-1,1]:ribbon(s,'Achaean red blade field '+str(side)+str(face),[(y,side*x+face*.048,lo+min(.035,(hi-lo)*.24),hi-min(.035,(hi-lo)*.24)) for y,x,lo,hi in base],.018,red)
            s.beam('Achaean short blade root '+str(side),(side*.34,.18,.45),(side*.72,.18,.72),.17,.18,copper)
        j=s.joint('CrescentGraderPivot',(0,-.94,-.02));s.beam('Achaean grader rooted support',(0,-.94,.08),(0,-1.95,-.32),.22,.23,copper,j)
        pts=[(.91*math.cos(t),-1.50-.45*math.sin(t),-.32+.20*abs(math.cos(t))) for t in [i*math.pi/16 for i in range(17)]]
        curved_bar(s,'Achaean broad copper crescent grader',pts,.18,.26,copper,j);curved_bar(s,'Achaean silver grading edge',[(x,y,z-.13) for x,y,z in pts],.20,.04,silver,j);cycle(s,j,0,.15)
    else:
        # User-reviewed correction: mirrored longitudinal wings,not dissimilar overhead/side hooks.
        base=[(-1.58,.24,.32,.34),(-.9,.58,.47,.65),(0,.78,.57,.85),(.9,.74,.75,1.03),(1.6,.48,.98,1.08),(1.82,.32,1.02,1.04)]
        for side in [-1,1]:
            ribbon(s,'Achaean repair silver wing '+str(side),[(y,side*x,lo,hi) for y,x,lo,hi in base],.10,silver)
            for face in [-1,1]:
                ribbon(s,'Achaean repair red wing field '+str(side)+' '+str(face),[(y,side*x+face*.048,lo+min(.035,(hi-lo)*.24),hi-min(.035,(hi-lo)*.24)) for y,x,lo,hi in base],.018,red)
            s.cyl('Achaean repair wing boss '+str(side),(side*.50,.52,.24),.24,.17,silver,(1,0,0))
            s.cyl('Achaean repair red boss inset '+str(side),(side*.59,.52,.24),.18,.04,red,(1,0,0))
            s.beam('Achaean repair wing root '+str(side),(side*.50,.52,.24),(side*.76,.52,.70),.18,.18,copper)
        j=s.joint('CurvedServiceSupport',(.50,.52,.24));pts=[(.50,.52,.24),(.52,.35,-.05),(.45,0,-.28),(.26,-.45,-.45),(.08,-.95,-.49),(0,-1.55,-.48)]
        curved_bar(s,'Achaean silver curved service spine',pts,.19,.25,silver,j);curved_bar(s,'Achaean red service spine inset',[(x,y,z+.11) for x,y,z in pts],.12,.04,red,j)
        wrist=s.joint('AchaeanServiceWrist',(0,-1.55,-.48),j)
        s.cyl('Achaean service wrist bearing',(0,-1.55,-.48),.13,.46,silver,(1,0,0),wrist)
        s.box('Achaean copper tool housing',(0,-1.60,-.48),(.65,.35,.28),copper,.035,wrist)
        for sign in [-1,1]:
            x=-.04+sign*.16;claw=s.joint('AchaeanClaw'+str(sign),(x,-1.73,-.48),wrist)
            s.cyl('Achaean lifting claw hinge '+str(sign),(x,-1.73,-.48),.063,.25,silver,parent=claw)
            s.box('Achaean silver lifting claw '+str(sign),(x,-1.91,-.48),(.11,.42,.21),silver,.022,claw)
            s.animate(claw,2,[(1,0),(25,0),(49,-sign*.23),(73,0),(97,0)])
        nozzle=s.cyl('Achaean adjacent silver service nozzle',(.31,-1.75,-.48),.11,.36,silver,(0,1,0),wrist);bore=s.cyl('Temporary service nozzle bore',(.31,-1.91,-.48),.055,.24,silver,(0,1,0),wrist);s.cut(nozzle,bore);s.ring('Achaean service nozzle rim',(.31,-1.94,-.48),.105,.055,.045,silver,(0,1,0),wrist);s.beam('Achaean nozzle root',(.25,-1.60,-.48),(.31,-1.69,-.48),.17,.18,copper,wrist)
        s.animate(j,0,[(1,0),(25,.14),(49,.14),(73,.035),(97,0)])
        s.animate(wrist,0,[(1,0),(25,-.11),(49,-.11),(73,-.025),(97,0)])
        s.placement.scale=(.88,.88,.88)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=Ship(a.root.resolve(),'achaean',a.role);achaean(s,a.role)
    s.export(__file__,['Based on selected supplied Achaean concepts;user correction requires mirrored red/silver longitudinal wings on repair ship rather than the asymmetric concept arches.','Canonical atlas colour/effective ORM targets and a tapered copper spindle;unchanged mirrored repair wing geometry. Working crescent grader or rooted curved service support is animated,with independent wrist and closing claws on repair. Rear/hidden engineering and scale are authored;no game mechanics,unit registration or integration.'])
