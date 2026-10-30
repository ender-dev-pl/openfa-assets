"""Independent first RI1C model; lower masses and mechanical detail are interpretations."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,material
from build_assault_fighter import plate
from terran_light_ship_parts import loft

SECTIONS=[(-1.38,.08,.02,.06),(-1.10,.25,.05,.12),(-.75,.47,.12,.26),(-.20,.65,.16,.34),(.45,.63,.17,.35),(.90,.43,.12,.24),(1.18,.15,.07,.11)]
DENTS=[(-.30,-.35,.005),(.40,.55,.004)]
POD_SECTIONS=[(-.62,.06,-.22,.08),(-.40,.17,-.25,.18),(.18,.21,-.26,.23),(.68,.15,-.23,.17),(.82,.05,-.21,.06)]
SOCKETS={'AlignmentForward':((0,-1.63,.015),(0,-1,0))}


def section(y):
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        if a[0]-1e-8<=y<=b[0]+1e-8:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError(y)


def dent(x,y):return sum(d*math.exp(-2*(((x-cx)/.09)**2+((y-cy)/.12)**2)) for cx,cy,d in DENTS)


def skin(x,y):
    w,z,h=section(y);return z+h*math.sqrt(max(0,1-(x/w)**2))-dent(x,y)


def fitted_patch(side,surface):
    count=13;top=[]
    for row in range(count):
        y=-.06+.28*row/(count-1)
        for column in range(count):
            x=side*(.20+.26*column/(count-1));top.append((x,y,skin(x,y)+.005))
    size=len(top);vertices=top+[(x,y,z-.014) for x,y,z in top];faces=[]
    for row in range(count-1):
        for column in range(count-1):
            a=row*count+column;face=(a,a+1,a+count+1,a+count);faces.append(face);faces.append(tuple(size+v for v in reversed(face)))
    edge=list(range(count))+[row*count+count-1 for row in range(1,count)]+list(reversed(range((count-1)*count,(count-1)*count+count-1)))+[row*count for row in reversed(range(1,count-1))]
    for a,b in zip(edge,edge[1:]+edge[:1]):faces.append((a,a+size,b+size,b))
    name='Delphini Assault gold upper patch '+str(side);mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(surface)
    return obj


def build():
    m=dict(hull=material('Delphini Assault | worn green hull',(.10,.25,.16),.65,.56),bronze=material('Delphini Assault | aged bronze bands',(.31,.20,.08),.74,.61),
        edge=material('Delphini Assault | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Delphini Assault | soot graphite',(.012,.013,.017),.45,.76),gold=material('Delphini Assault | heat stained bronze',(.31,.20,.08),.78,.66))
    refined=[]
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        n=math.ceil((b[0]-a[0])/.025)
        refined.extend((y,*section(y)) for y in [a[0]+(b[0]-a[0])*i/n for i in range(n)])
    refined.append(SECTIONS[-1]);body=loft('Delphini Assault rounded green hull',refined,m['hull'],rings=96)
    for v in body.data.vertices:
        if v.co.z>.08:v.co.z-=dent(v.co.x,v.co.y)
    body.data.update()
    loft('Delphini Assault narrow fore projection',[(-1.63,.035,.015,.035),(-1.50,.11,.02,.08),(-1.27,.12,.035,.085),(-1.12,.09,.045,.06)],m['edge'],rings=48)
    loft('Delphini Assault brown tail detail',[(.85,.12,.08,.10),(1.12,.19,.07,.15),(1.34,.08,.05,.07)],m['bronze'],rings=48)
    for side in [-1,1]:
        obj=loft('Delphini Assault brown ventral body '+str(side),POD_SECTIONS,m['bronze'],rings=48);obj.location.x=side*.50
        # A pair of opaque upper patches is visible; hatch/sensor function is not asserted.
        fitted_patch(side,m['bronze'])
        y=.43;x=side*.17;z=skin(x,y)
        box('Delphini Assault green service cover '+str(side),(x,y,z+.002),(.10,.20,.028),m['hull'],.003)
        for i in range(3):box('Delphini Assault service slot '+str(side)+' '+str(i),(x,y-.06+i*.06,z+.020),(.068,.010,.008),m['dark'],.001)
        for i,y in enumerate([-.28,.10,.46]):
            # Outer pod fittings are service detail, not gun barrels or exhausts.
            for a,b in zip(POD_SECTIONS,POD_SECTIONS[1:]):
                if a[0]<=y<=b[0]:
                    t=(y-a[0])/(b[0]-a[0]);w,z,h=[a[j]+(b[j]-a[j])*t for j in [1,2,3]];break
            cylinder('Delphini Assault ventral fitting '+str(side)+' '+str(i),(side*(.50+w+.004),y,z),.020,.025,m['gold'],vertices=16,rotation=(0,math.pi/2,0))
    loft('Delphini Assault small gold dorsal crest',[(.46,.025,.48,.025),(.57,.10,.48,.04),(.73,.09,.44,.035),(.80,.025,.40,.025)],m['bronze'],rings=32)
    return m
