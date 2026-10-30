"""First independent PS03 wedge ship; dimensions and hidden parts are interpretations."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,finish,material
from build_assault_fighter import plate
from terran_light_ship_parts import loft
from manufactured_annuli import annulus

SECTIONS=[(-2.10,.075,.035,.070),(-1.70,.26,.055,.13),(-.70,.70,.075,.25),(.35,1.02,.09,.32),(1.10,1.12,.08,.30),(1.48,.91,.035,.22)]
DENTS=[(-.32,-.35,.008),(.38,.45,.006)]
CROSS=[(-1,-.55),(-1,.25),(-.65,.85),(0,1),(.65,.85),(1,.25),(1,-.55),(0,-1)]
SOCKETS={'Hardpoint dorsal':((0,.12,.425),(0,0,1)),'Hardpoint port':((-1.38,.84,.10),(0,-1,0)),'Hardpoint starboard':((1.38,.84,.10),(0,-1,0)),
 'Engine port':((-.72,1.90,.02),(0,1,0)),'Engine starboard':((.72,1.90,.02),(0,1,0))}


def section(y):
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        if a[0]-1e-8<=y<=b[0]+1e-8:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError(y)


def dent(x,y): return sum(d*math.exp(-2*(((x-cx)/.11)**2+((y-cy)/.16)**2)) for cx,cy,d in DENTS)


def mesh_object(name,vertices,faces,surface):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def hull(surface):
    rings=[]
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        n=math.ceil((b[0]-a[0])/.04)
        rings.extend(a[0]+(b[0]-a[0])*i/n for i in range(n))
    rings.append(SECTIONS[-1][0]);vertices=[]
    cross=[]
    for a,b in zip(CROSS,CROSS[1:]+CROSS[:1]):
        cross.extend((a[0]+(b[0]-a[0])*i/6,a[1]+(b[1]-a[1])*i/6) for i in range(6))
    for y in rings:
        w,z,h=section(y)
        for u,v in cross:
            x=w*u;vertices.append((x,y,z+h*v-(dent(x,y) if v>.25 else 0)))
    count=len(cross);first=len(vertices);last=first+1
    vertices.extend([(0,rings[0],section(rings[0])[1]),(0,rings[-1],section(rings[-1])[1])])
    end=(len(rings)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces += [(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(len(rings)-1) for i in range(count)]
    return mesh_object('Destructor continuous faceted hull',vertices,faces,surface)


def flank(side,surface):
    rows=65;vertices=[]
    for i in range(rows):
        y=-1.90+3.23*i/(rows-1);w,z,h=section(y)
        # Embed the back skin into the outer flat flank and lift the paint plate.
        for x,v in [(w-.003,-.18),(w+.008,-.18),(w+.008,.20),(w-.003,.20)]: vertices.append((side*x,y,z+h*v))
    faces=[(3,2,1,0)]
    for i in range(rows-1):
        a=i*4;b=a+4;faces.extend((a+j,a+(j+1)%4,b+(j+1)%4,b+j) for j in range(4))
    faces.append(tuple((rows-1)*4+j for j in range(4)))
    return mesh_object('Destructor red flank '+str(side),vertices,faces,surface)


def build():
    m=dict(hull=material('Destructor | worn violet hull',(.15,.14,.21),.65,.56),red=material('Destructor | worn red markings',(.46,.025,.016),.45,.58),
        edge=material('Destructor | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Destructor | soot graphite',(.012,.013,.017),.45,.76),gold=material('Destructor | heat stained bronze',(.31,.20,.08),.78,.66))
    hull(m['hull'])
    for side in [-1,1]:
        flank(side,m['red'])
        pod=loft('Destructor aft engine housing '+str(side),[(.63,.23,.015,.25),(.90,.34,.015,.31),(1.46,.34,.015,.29),(1.64,.28,.015,.23)],m['hull'],rings=48);pod.location.x=side*.72
        # A closed hollow annulus with no cap over its exhaust axis.
        nozzle=annulus('Destructor exhaust '+str(side),(0,0),[(0,.245,.18),(.10,.265,.185),(.30,.25,.18)],m['gold'],(0,.15,0));nozzle.rotation_euler=(-math.pi/2,0,0);nozzle.location=(side*.72,1.60,.02)
        cylinder('Destructor exhaust throat '+str(side),(side*.72,1.65,.02),.181,.03,m['dark'],vertices=64,rotation=(-math.pi/2,0,0))
        for i in range(12):
            a=i*math.tau/12;beam('Destructor cooling rib '+str(side)+' '+str(i),(side*.72+.25*math.cos(a),1.66,.02+.25*math.sin(a)),(side*.72+.245*math.cos(a),1.91,.02+.245*math.sin(a)),.009,m['edge'])
        points=[(side*.82,.57,.09),(side*1.53,.78,.07),(side*1.62,1.16,.055),(side*.94,1.32,.09)]
        plate('Destructor outboard wing '+str(side),points,.07,m['hull'],.008)
        plate('Destructor red wing tip '+str(side),[(side*1.38,.79,.076),(side*1.53,.79,.076),(side*1.61,1.15,.065),(side*1.44,1.15,.065)],.012,m['red'],.002)
        beam('Destructor outboard prong '+str(side),(side*1.49,.87,.085),(side*1.49,.36,.085),.018,m['edge'])
        box('Destructor aft red panel '+str(side),(side*.72,1.16,.321),(.33,.34,.02),m['red'],.006)
        for y in [-2.10,-2.24]:
            beam('Destructor bow antenna '+str(side)+' '+str(y),(side*.075,-1.98,.04),(side*.095,y-.16,.04),.010,m['edge'])
    # Service vent is attached to the sloped crown; internal fins are authored detail.
    box('Destructor dorsal vent surround',(0,.16,.402),(.43,.43,.035),m['edge'],.008)
    box('Destructor dorsal vent well',(0,.16,.423),(.35,.34,.014),m['dark'],.003)
    for i in range(6):box('Destructor dorsal vent fin '+str(i),(0,.02+i*.055,.436),(.30,.012,.018),m['edge'],.002)
    # Four conformal top service plates, kept within the wedge crown.
    for side in [-1,1]:
        for a,b in [(-.72,-.38),(.50,.79)]:
            points=[]
            for y,u in [(a,.31),(a,.59),(b,.59),(b,.31)]:
                w,z,h=section(y);x=side*w*u;v=1-(u/.65)*.15;points.append((x,y,z+h*v-dent(x,y)+.008))
            plate('Destructor crown service plate '+str(side)+' '+str(a),points,.014,m['edge'],.001)
    return m
