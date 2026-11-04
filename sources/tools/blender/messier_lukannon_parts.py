"""Independent first RI2C hull; hidden sections and mechanisms are not recovered."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,material
from build_assault_fighter import plate
from terran_light_ship_parts import loft
from manufactured_surface_mounts import cast_bezel

SECTIONS=[(-1.60,.10,0,.12),(-1.35,.55,.08,.32),(-.80,.78,.10,.40),(0,.82,.13,.40),(.70,.60,.10,.30),(1.35,.27,.05,.15),(1.60,.04,.02,.05)]
DENTS=[(-.32,-.45,.005),(.36,.52,.004)]
SOCKETS={'AlignmentForward':((0,-1.77,0),(0,-1,0))}


def section(y):
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        if a[0]-1e-8<=y<=b[0]+1e-8:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError(y)


def dent(x,y):return sum(d*math.exp(-2*(((x-cx)/.09)**2+((y-cy)/.12)**2)) for cx,cy,d in DENTS)


def skin(x,y):
    w,z,h=section(y);return z+h*math.sqrt(max(0,1-(x/w)**2))-dent(x,y)


def build():
    m=dict(hull=material('Messier-Lukannon | worn slate hull',(.13,.24,.25),.65,.56),bronze=material('Messier-Lukannon | aged copper details',(.30,.15,.08),.74,.61),
        edge=material('Messier-Lukannon | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Messier-Lukannon | soot graphite',(.012,.013,.017),.45,.76),gold=material('Messier-Lukannon | heat stained bronze',(.40,.30,.10),.78,.66))
    refined=[]
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        n=math.ceil((b[0]-a[0])/.025)
        refined.extend((y,*section(y)) for y in [a[0]+(b[0]-a[0])*i/n for i in range(n)])
    refined.append(SECTIONS[-1]);body=loft('Messier-Lukannon flattened slate hull',refined,m['hull'],rings=96)
    for v in body.data.vertices:
        if v.co.z>.08:v.co.z-=dent(v.co.x,v.co.y)
    body.data.update()
    loft('Messier-Lukannon copper terminal',[(-1.77,.08,0,.10),(-1.65,.22,0,.19),(-1.42,.25,.04,.20)],m['bronze'],rings=64)
    for side in [-1,1]:
        # Opaque swept ventral masses interpret brown lateral pixels; no engine/gun assertion.
        plate('Messier-Lukannon copper ventral wing '+str(side),[(side*.40,-.10,-.10),(side*.52,.75,-.10),(side*1.45,1.05,-.10),(side*1.32,.70,-.10)],.075,m['bronze'],.006)
        for i,y in enumerate([-.56,.43]):
            w,z,h=section(y);x=w*math.sqrt(1-(z/h)**2);normal=Vector((side,0,0));point=Vector((side*x,y,0))+normal*.050
            cast_bezel('Messier-Lukannon side boss bezel '+str(side)+' '+str(i),body,point,normal,.115,m['bronze'])
            cylinder('Messier-Lukannon side boss face '+str(side)+' '+str(i),point+normal*.028,.073,.018,m['bronze'],vertices=64,rotation=normal.to_track_quat('Z','Y').to_euler())
        y=.65;x=side*.16;z=skin(x,y)
        box('Messier-Lukannon slate service cover '+str(side),(x,y,z+.002),(.12,.20,.028),m['hull'],.003)
        for i in range(3):box('Messier-Lukannon service slot '+str(side)+' '+str(i),(x,y-.06+i*.06,z+.020),(.080,.010,.008),m['dark'],.001)
        for i,y in enumerate([-.72,.10]):
            x=side*.30;z=skin(x,y);cylinder('Messier-Lukannon gold dorsal fitting '+str(side)+' '+str(i),(x,y,z+.013),.058,.04,m['gold'],vertices=32)
        # Small edge pads and fasteners remain independently authored maintenance detail.
        box('Messier-Lukannon ventral wing pad '+str(side),(side*.86,.65,-.093),(.20,.15,.028),m['edge'],.003)
    return m
