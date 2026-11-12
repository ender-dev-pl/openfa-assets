"""First independent RI0A study; most depth and mechanical detail are interpretations."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,material
from build_assault_fighter import plate
from terran_light_ship_parts import loft

SECTIONS=[(-.94,.03,0,.04),(-.78,.33,.01,.13),(-.36,.57,.02,.18),(.25,.62,.02,.19),(.70,.39,.01,.14),(.88,.05,0,.05)]
DENTS=[(.42,-.12,.004),(-.43,.24,.003)]
SOCKETS={'AlignmentForward':((0,-.94,0),(0,-1,0))}


def section(y):
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        if a[0]-1e-8<=y<=b[0]+1e-8:
            t=(y-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in [1,2,3]]
    raise ValueError(y)


def dent(x,y):return sum(d*math.exp(-2*(((x-cx)/.07)**2+((y-cy)/.10)**2)) for cx,cy,d in DENTS)


def build():
    m=dict(hull=material('Lazzaro Research | worn green hull',(.10,.25,.16),.65,.56),bronze=material('Lazzaro Research | aged bronze bands',(.31,.20,.08),.74,.61),
        edge=material('Lazzaro Research | exposed titanium',(.29,.28,.32),.78,.49),dark=material('Lazzaro Research | soot graphite',(.012,.013,.017),.45,.76),gold=material('Lazzaro Research | heat stained bronze',(.31,.20,.08),.78,.66))
    refined=[]
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        n=math.ceil((b[0]-a[0])/.025)
        refined.extend((y,*section(y)) for y in [a[0]+(b[0]-a[0])*i/n for i in range(n)])
    refined.append(SECTIONS[-1]);body=loft('Lazzaro Research compact green hull',refined,m['hull'],rings=96)
    for v in body.data.vertices:
        if v.co.z>.04:v.co.z-=dent(v.co.x,v.co.y)
    body.data.update()
    loft('Lazzaro Research gold central crown',[(-.64,.06,.14,.05),(-.35,.28,.20,.14),(.26,.33,.21,.16),(.57,.15,.18,.10),(.63,.03,.15,.04)],m['bronze'],rings=64)
    for side in [-1,1]:
        for end in [-1,1]:
            # The four-lobe split is an interpretation of tiny grey corner pixels.
            pts=[(side*.35,end*.22,.065),(side*.95,end*.42,.055),(side*.93,end*.72,.055),(side*.38,end*.57,.065)]
            plate('Lazzaro Research grey lobe '+str(side)+' '+str(end),pts,.075,m['edge'],.006)
            plate('Lazzaro Research brown tip '+str(side)+' '+str(end),[(side*.82,end*.45,.062),(side*.95,end*.46,.062),(side*.93,end*.69,.062),(side*.80,end*.65,.062)],.015,m['bronze'],.001)
            # Braces and fasteners are independently authored service detail, not weapons.
            beam('Lazzaro Research lobe brace '+str(side)+' '+str(end),(side*.36,end*.33,-.035),(side*.83,end*.55,.01),.015,m['dark'])
            cylinder('Lazzaro Research lobe fastener '+str(side)+' '+str(end),(side*.66,end*.48,.063),.018,.014,m['gold'],vertices=16)
    # Small opaque service covers on the green shoulder; no sensor/engine claim.
    for side in [-1,1]:
        y=.02;w,z,h=section(y);x=side*.44;skin=z+h*math.sqrt(1-(x/w)**2)-dent(x,y)
        box('Lazzaro Research shoulder cover '+str(side),(x,y,skin+.002),(.09,.16,.025),m['hull'],.003)
        for i in range(3):box('Lazzaro Research shoulder slot '+str(side)+' '+str(i),(x,y-.05+i*.05,skin+.018),(.060,.009,.009),m['dark'],.001)
    return m
