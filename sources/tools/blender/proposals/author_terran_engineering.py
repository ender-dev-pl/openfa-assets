"""Author the two selected Terran v3 engineering proposals; no game registration."""
import argparse,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from engineering_ship_refinement import RefinedShip as Ship

def build(root,role):
    s=Ship(root,'terran',role)
    # Canonical glTF material factors are linear;generated colour PNG inputs use sRGB.
    def srgb(values):return tuple(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in values)
    hull=s.mat('slate-blue',srgb((.15,.14,.21)),.48,.46)
    red=s.mat('vermilion',srgb((.55,.025,.018)),.30,.45)
    steel=s.mat('silver-steel',srgb((.31,.33,.38)),.63,.39)
    bronze=s.mat('bronze',srgb((.42,.28,.095)),.58,.46)
    dark=s.mat('working-steel',srgb((.012,.014,.022)),.40,.63)
    glass=s.mat('dark-visor',(.018,.025,.038),.45,.25)
    def plate(name,outline,z,depth,mat,bevel=.014):
        n=len(outline);vertices=[(x,y,z+d) for d in [-depth/2,depth/2] for x,y in outline]
        return s.solid(name,vertices,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,bevel)
    plate('Terran swept layered utility deck',[(-.73,-1.13),(.73,-1.13),(1.10,-.45),(1.48,.65),(1.43,1.05),(.82,1.20),(-.82,1.20),(-1.43,1.05),(-1.48,.65),(-1.10,-.45)],.18,.22,steel)

    outline=[(-.90,.04),(.90,.04),(1.10,.18),(1.10,.38),(.75,.63),(-.75,.63),(-1.10,.38),(-1.10,.18)]
    vertices=[(x*scale,y,z+.07*y) for y,scale in [(-1.10,.62),(-.15,1.0),(.70,1.0),(1.12,.85)] for x,z in outline];faces=[tuple(reversed(range(8))),tuple(range(24,32))]
    for j in range(3):
        for i in range(8):k=(i+1)%8;faces.append((j*8+i,j*8+k,(j+1)*8+k,(j+1)*8+i))
    body=s.solid('Terran solid broad utility hull',vertices,faces,hull,.055)
    for side in [-1,1]:
        # Quiet swept red fields on the sloping roof;no decorative panel grid.
        points=[(side*x,y,.63+.07*y+.014) for x,y in [(.34,-.72),(.53,-.72),(.74,-.18),(.74,.59),(.40,.59)]]
        vertices=[(x,y,z+d) for d in [-.006,.006] for x,y,z in points];n=len(points)
        s.solid('Terran swept red hood field '+str(side),vertices,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],red)
        x=side*1.19
        # Octagonal faceted shroud with circular thermal casing,like the small fleet.
        profile=[(-.325,-.18),(-.19,-.31),(.19,-.31),(.325,-.18),(.325,.18),(.19,.31),(-.19,.31),(-.325,.18)]
        vertices=[(side*(.95+(.30*(y+.73)/1.88))+dx,y,.38+dz) for y in [-.73,1.15] for dx,dz in profile]
        pod=s.solid('Terran integrated engine shroud '+str(side),vertices,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)],hull,.025)
        plate('Terran red deck-edge field '+str(side),[(side*.70,-.96),(side*1.02,-.40),(side*1.40,.75),(side*1.18,.96)],.302,.025,red,.008)
        # One recessed slotted intake behind each shoulder field.
        cutter=s.box('Temporary roof intake '+str(side),(side*.52,.83,.71),(.30,.22,.15),dark,.015);s.cut(body,cutter)
        s.box('Terran inset graphite intake '+str(side),(side*.52,.83,.645),(.28,.20,.025),dark,.01)
        for dy in [-.06,0,.06]:s.box('Terran intake louvre '+str(side)+str(dy),(side*.52,.83+dy,.66),(.27,.025,.018),steel,.004)
        x=side*(.95 if role=='terraform' else 1.25)
        y=-.80 if role=='terraform' else .98
        s.ring('Terran silver engine casing '+str(side),(x,y,.38),.325,.25,.32,steel,(0,1,0))
        s.ring('Terran bronze nozzle rim '+str(side),(x,y+(-.18 if role=='terraform' else .18),.38),.273,.215,.13,bronze,(0,1,0))
        hole=s.cyl('Temporary engine bore',(x,-.92 if role=='terraform' else 1.30,.38),.25,.60,dark,(0,1,0));s.cut(pod,hole)
        s.cyl('Terran sealed dark engine throat '+str(side),(x,-.615 if role=='terraform' else 1.005,.38),.249,.03,dark,(0,1,0))
    if role=='terraform':
        s.cockpit((0,.15,.78),steel,glass)
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
                for sign in [-1,1]:
                    x=sign*.17;jaw=s.joint('GripJawPivot '+str(sign),(c.x+x,c.y-.14,c.z),elbow)
                    s.cyl('Terran lifting jaw hinge '+str(sign),(c.x+x,c.y-.14,c.z),.07,.22,bronze,parent=jaw)
                    s.box('Terran broad lifting jaw '+str(sign),(c.x+x,c.y-.31,c.z),(.14,.36,.19),steel,.022,jaw)
            else:
                s.cyl('Terran welder steel body',(c.x,c.y-.11,c.z),.13,.25,steel,(0,1,0),elbow)
                s.ring('Terran bronze welding tip',(c.x,c.y-.31,c.z),.11,.055,.22,bronze,(0,1,0),elbow)
                s.cyl('Terran blind welding aperture',(c.x,c.y-.23,c.z),.054,.02,dark,(0,1,0),elbow)
    if role=='terraform':s.animate(pivot,0,[(1,0),(97,2*math.pi)])
    else:
        for j in s.joints:
            if 'Jaw' in j.name:
                amount=.24 if j.name.endswith('-1') else -.24
                s.animate(j,2,[(1,0),(25,0),(49,amount),(73,0),(97,0)])
            else:
                amount=.20 if 'Shoulder' in j.name else -.32
                if 'Welder' in j.name:amount*=-.65
                s.animate(j,0,[(1,0),(25,amount),(49,amount),(73,amount*.25),(97,0)])
    if role=='repair':s.placement.scale=(.80,.80,.80)
    s.export(__file__,['Based on selected supplied Terran v3 concept. Canonical-fleet style correction: swept layered deck,tapered faceted hull,circular thermal casings and quiet red fields. Linear canonical material factors converted to sRGB map targets. Role-specific tools retained;repair jaw operation follows arm positioning.','Hidden/rear surfaces,pivot engineering and arbitrary proposal units are authored. No legacy definition,blueprint,production route or game mechanic is supplied.','Repair role supports both repair and new construction in its design intent only.'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);build(a.root.resolve(),a.role)
