"""Author the two selected Terran v3 engineering proposals; no game registration."""
import argparse,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from engineering_ship_common import Ship

def build(root,role):
    s=Ship(root,'terran',role)
    hull=s.mat('slate-blue',(.25,.29,.38),.35,.55);red=s.mat('vermilion',(.60,.055,.035),.12,.65);steel=s.mat('silver-steel',(.46,.49,.55),.65,.43);bronze=s.mat('bronze',(.52,.29,.11),.65,.46);dark=s.mat('working-steel',(.065,.075,.09),.55,.65);glass=s.mat('dark-visor',(.018,.025,.038),.45,.25)
    outline=[(-.90,.04),(.90,.04),(1.10,.18),(1.10,.38),(.75,.63),(-.75,.63),(-1.10,.38),(-1.10,.18)]
    vertices=[(x*scale,y,z+.07*y) for y,scale in [(-1.10,1.0),(.70,1.0),(1.12,.85)] for x,z in outline];faces=[tuple(reversed(range(8))),tuple(range(16,24))]
    for j in range(2):
        for i in range(8):k=(i+1)%8;faces.append((j*8+i,j*8+k,(j+1)*8+k,(j+1)*8+i))
    body=s.solid('Terran solid broad utility hull',vertices,faces,hull,.055)
    for side in [-1,1]:
        # Red fields follow the broad hood and its sloping shoulder.
        points=[(side*x,y,.63+.07*y-max(0,x-.75)*.25/.35+.014) for x,y in [(.40,-.90),(.75,-.90),(.96,-.90),(.96,.45),(.75,.45),(.40,.45)]]
        vertices=[(x,y,z+d) for d in [-.006,.006] for x,y,z in points];n=len(points)
        s.solid('Terran broad red hood field '+str(side),vertices,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],red)
        x=side*1.21;pod=s.box('Terran integrated engine shroud '+str(side),(x,.22,.38),(.65,1.90,.72),hull,.23)
        y=-.80 if role=='terraform' else .98
        s.ring('Terran silver engine casing '+str(side),(x,y,.38),.325,.25,.32,steel,(0,1,0))
        s.ring('Terran bronze nozzle rim '+str(side),(x,y+(-.18 if role=='terraform' else .18),.38),.273,.215,.13,bronze,(0,1,0))
        hole=s.cyl('Temporary engine bore',(x,-.92 if role=='terraform' else 1.30,.38),.25,.60,dark,(0,1,0));s.cut(pod,hole)
        s.cyl('Terran sealed dark engine throat '+str(side),(x,-.615 if role=='terraform' else 1.005,.38),.249,.03,dark,(0,1,0))
    if role=='terraform':
        s.box('Terran low control blister',(0,.15,.78),(.80,.70,.37),steel,.15)
        s.box('Terran single front visor',(0,-.19,.78),(.65,.055,.20),glass,.055)
        pivot=s.joint('MillingDrumPivot',(0,-1.43,-.14))
        s.cyl('Terran one horizontal milling drum',(0,-1.43,-.14),.27,1.72,dark,(1,0,0),pivot)
        for side in [-1,1]:
            s.beam('Terran stout drum bracket '+str(side),(side*.91,-.85,.23),(side*.91,-1.43,-.14),.18,.22,hull)
            s.cyl('Terran drum end bearing '+str(side),(side*.91,-1.43,-.14),.16,.17,steel,(1,0,0))
        for i in range(4):
            angle=i*math.pi/2
            for j,x in enumerate([-.53,0,.53]):
                o=s.box('Terran coarse cutter tooth '+str(i)+' '+str(j),(x,-1.43+.28*math.sin(angle),-.14+.28*math.cos(angle)),(.22,.20,.10),bronze,.015,pivot);o.rotation_euler.x=-angle
    else:
        s.box('Terran low central visor',(0,-1.105,.36),(.76,.09,.19),glass,.055)
        for side in [-1,1]:
            a=Vector((side*.75,-1.04,.14));b=Vector((side*.95,-1.40,-.04));c=Vector((side*.86,-1.82,-.16));parent=s.joint('GripShoulderPivot' if side<0 else 'WelderShoulderPivot',a)
            s.cyl('Terran shoulder bearing '+str(side),a,.13,.19,steel,(1,0,0),parent)
            s.beam('Terran upper tool arm '+str(side),a,b,.16,.18,steel,parent)
            elbow=s.joint('GripElbowPivot' if side<0 else 'WelderElbowPivot',b,parent)
            s.cyl('Terran elbow bearing '+str(side),b,.13,.20,steel,(1,0,0),elbow)
            s.beam('Terran lower tool arm '+str(side),b,c,.16,.18,steel,elbow)
            if side<0:
                s.box('Terran clamp crosspiece',(c.x,c.y-.10,c.z),(.47,.19,.19),steel,.04,elbow)
                for x in [-.17,.17]:s.box('Terran broad lifting jaw '+str(x),(c.x+x,c.y-.29,c.z),(.14,.35,.19),steel,.035,elbow)
            else:
                s.cyl('Terran welder steel body',(c.x,c.y-.11,c.z),.13,.25,steel,(0,1,0),elbow)
                s.ring('Terran bronze welding tip',(c.x,c.y-.31,c.z),.11,.055,.22,bronze,(0,1,0),elbow)
                s.cyl('Terran blind welding aperture',(c.x,c.y-.23,c.z),.054,.02,dark,(0,1,0),elbow)
    if role=='terraform':s.animate(pivot,0,[(1,0),(97,2*math.pi)])
    else:
        for j in s.joints:
            amount=.20 if 'Shoulder' in j.name else -.32
            if 'Welder' in j.name:amount*=-.65
            s.animate(j,0,[(1,0),(25,amount),(49,0),(73,-amount*.45),(97,0)])
    if role=='repair':s.placement.scale=(.80,.80,.80)
    s.export(__file__,['Based on selected supplied Terran v3 concept. Broad hull,two shrouds,quiet red fields and one role-specific tool set.','Hidden/rear surfaces,pivot engineering and arbitrary proposal units are authored. No legacy definition,blueprint,production route or game mechanic is supplied.','Repair role supports both repair and new construction in its design intent only.'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);build(a.root.resolve(),a.role)
