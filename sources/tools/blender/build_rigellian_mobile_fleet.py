"""Issue 232: source-bound Rigellian mobile fleet, shared worn portable PBR.

Hi-def references define visible assemblies, not texture pixels. -Y forward/Z up.
Hidden construction and proposed world sizes are authored, not recovered data.
Run Blender --background --python this-file -- [--ship SLUG] [--no-render].
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
import refine_terran_shipyard as g

ROOT = Path(__file__).resolve().parents[3]
STYLE = json.loads((ROOT/'sources/objects/rigellian/fleet-style.json').read_text())
TAU = math.tau
_emit=g.facegroup


def emit(group, vertices, faces, tile=1):
    _emit(group,vertices,faces,tile)
    low=tuple(min(p[a] for p in vertices) for a in range(3))
    high=tuple(max(p[a] for p in vertices) for a in range(3))
    g.GROUPS[group].setdefault('charts',[]).extend([(low,high)]*len(faces))


g.facegroup=emit


def ellipsoid(group, centre, radii, tile=0, rings=12, sides=32):
    vs = []
    for j in range(rings+1):
        a = math.pi*j/rings
        for i in range(sides):
            b = TAU*i/sides
            vs.append((centre[0]+radii[0]*math.sin(a)*math.cos(b),
                       centre[1]+radii[1]*math.sin(a)*math.sin(b),
                       centre[2]+radii[2]*math.cos(a)))
    fs = [(j*sides+i, j*sides+(i+1)%sides, (j+1)*sides+(i+1)%sides, (j+1)*sides+i)
          for j in range(rings) for i in range(sides)]
    g.facegroup(group, vs, fs, tile)


def capsule(centre, radii, rows, sectors=24, tile=0):
    """Recessed continuous hull + individually separated conformal plates."""
    # A few broad formed skins, NOT a dense tiled armour grid. Fine detail belongs
    # to service machinery and joins; the user explicitly rejected the grid.
    rows=7 if radii[1]<5 else 8
    sectors=12
    def point(a,b,offset=1):
        a=.28+(math.pi-.50)*a/math.pi
        s=max(0,math.sin(a))
        return (centre[0]+radii[0]*s**.72*math.cos(b)*offset,
                centre[1]-radii[1]*math.cos(a)*offset,
                centre[2]+radii[2]*s**.82*math.sin(b)*offset)
    core=[point(math.pi*j/(rows*2),TAU*i/(sectors*2)) for j in range(rows*2+1) for i in range(sectors*2)]
    n=sectors*2
    core_faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(rows*2) for i in range(n)]
    core_faces.extend([tuple(range(n-1,-1,-1)),tuple(range(rows*2*n,(rows*2+1)*n))])
    g.facegroup('PressureHull',core,core_faces,4)
    for j in range(rows):
        a0 = math.pi*(.005+.99*j/rows)+.0013
        a1 = math.pi*(.005+.99*(j+1)/rows)-.0013
        for i in range(sectors):
            shift=TAU/sectors*(.24 if j%2 else 0)
            b0, b1 = TAU*i/sectors+.002+shift, TAU*(i+1)/sectors-.002+shift
            vs = []
            resolution=5;count=(resolution+1)**2
            for layer in [0,1]:
                for aj in range(resolution+1):
                    a = a0+(a1-a0)*aj/resolution
                    for bi in range(resolution+1):
                        b = b0+(b1-b0)*bi/resolution
                        edge=min(aj,bi,resolution-aj,resolution-bi)
                        offset=(1.008 if edge else 1.004) if layer==0 else .998
                        if layer==0 and (i*7+j*11)%29==0 and aj==2 and bi==2:offset-=.002
                        vs.append(point(a,b,offset))
            n=resolution+1;fs=[]
            for k in range(resolution):
                for l in range(resolution):
                    q=(k*n+l,k*n+l+1,(k+1)*n+l+1,(k+1)*n+l)
                    fs.extend([q,tuple(v+count for v in reversed(q))])
            boundary=list(range(n))+[k*n+resolution for k in range(1,n)]
            boundary += [resolution*n+l for l in range(resolution-1,-1,-1)]
            boundary += [k*n for k in range(resolution-1,0,-1)]
            fs += [(a,a+count,b+count,b) for a,b in zip(boundary,boundary[1:]+boundary[:1])]
            t = tile if (i+3*j)%11 else (8 if tile == 0 else tile)
            g.facegroup('HullPlates', vs, fs, t)
            # Raised fasteners and inset service sockets sit on the actual plate.
            if (i+j)%5==0 and 1<j<rows-2:
                a=(a0+a1)/2;b=(b0+b1)/2
                p=Vector(point(a,b,1.012))
                normal=Vector(((p.x-centre[0])/radii[0]**2,(p.y-centre[1])/radii[1]**2,(p.z-centre[2])/radii[2]**2)).normalized()
                size=min(.019,radii[1]*.004)
                g.rod('PlateFasteners',p,p+normal*size*.65,size,4,6)
                g.rod('PlateFasteners',p+normal*size*.65,p+normal*size*.9,size*.45,1,6)


def nozzle(x, y, z, r, length=.24):
    # Local circular section about Y; copper rim encloses a dark recess.
    for tile, radius, yy in [(4,r,y),(2,r*.97,y+.02),(4,r*.77,y+.04),(6,r*.46,y+.045)]:
        profile = [(yy-length,radius*.8),(yy,radius)]
        vs = [(x+rr*math.cos(TAU*i/32), t, z+rr*math.sin(TAU*i/32)) for t,rr in profile for i in range(32)]
        faces = [(i,(i+1)%32,(i+1)%32+32,i+32) for i in range(32)]
        if tile in (4,6):faces.append(tuple(range(32,64)))
        g.facegroup('DriveAssemblies',vs,faces,tile)


def nose_collar(y,r):
    profile=[(y+.25,r*.91),(y+.16,r),(y-.09,r),(y-.15,r*.81),
             (y-.15,r*.59),(y+.04,r*.59),(y+.08,r*.82)]
    vs=[(rr*math.cos(TAU*i/48),yy,rr*math.sin(TAU*i/48)) for yy,rr in profile for i in range(48)]
    fs=[(j*48+i,j*48+(i+1)%48,((j+1)%len(profile))*48+(i+1)%48,((j+1)%len(profile))*48+i) for j in range(len(profile)) for i in range(48)]
    g.facegroup('NoseShield',vs,fs,2)
    g.rod('Systems',(0,y-.02,0),(0,y+.02,0),r*.56,4,40)
    g.rod('Windows',(0,y-.035,0),(0,y-.045,0),r*.28,5,32)
    for i in range(12):
        a=TAU*i/12
        g.rod('PlateFasteners',(r*.87*math.cos(a),y-.12,r*.87*math.sin(a)),
              (r*.87*math.cos(a),y-.14,r*.87*math.sin(a)),.012,4,6)


def fin(points, thickness=.045, tile=2):
    vs = [(x,y,z+offset) for offset in [-thickness/2,thickness/2] for x,y,z in points]
    n = len(points)
    fs = [tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    g.facegroup('StructuralFins',vs,fs,tile)
    for a,b in zip(points,points[1:]+points[:1]):g.rod('StructuralFins',a,b,.013,1,6)


def cap(x,y,z,r):
    g.lathe('Systems',(x,y,z-.02),[(0,r*.99),(.03,r*1.04),(.075,r*1.04)],4,40)
    g.lathe('Systems',(x,y,z+.05),[(0,r),(.035,r),(.075,r*.94),(.11,r*.65),(.12,.025)],3,40)
    for i in range(12):
        a=TAU*i/12
        g.box('Windows',(x+r*1.045*math.cos(a),y+r*1.045*math.sin(a),z+.025),
              (r*.27,.016,.029),5,a+math.pi/2,chamfer=.003)
    for i in range(12):
        a = TAU*i/12
        g.rod('Systems',(x+r*.85*math.cos(a),y+r*.85*math.sin(a),z+.07),
              (x+r*.85*math.cos(a),y+r*.85*math.sin(a),z+.087),.012,4,6)


def antenna(x,y,z,height):
    g.lathe('Systems',(x,y,z),[(0,.055),(.06,.055),(.11,.028)],1,12)
    g.rod('Systems',(x,y,z+.08),(x,y,z+height),.012,1,8)
    g.box('NavigationLights',(x,y,z+height),(.027,.027,.055),5,chamfer=.004)


def canopy(y,z,length,width,height):
    # Paned opaque glass: physical ribs, no transparency sorting in the game.
    ellipsoid('Glazing',(0,y,z),(width,length,height),7,10,24)
    for j in range(7):
        a = math.pi*(.15+.7*j/6)
        yy = y-length*math.cos(a)
        pts = [(width*math.sin(a)*math.cos(math.pi*i/16),yy,
                z+height*math.sin(a)*math.sin(math.pi*i/16)+.012) for i in range(17)]
        for a,b in zip(pts,pts[1:]):g.rod('CanopyFrames',a,b,.014,1,6)
    for side in [-1,1]:
        pts = [(side*width*.58*math.sin(a),y-length*math.cos(a),z+height*.82*math.sin(a)+.015)
               for a in [math.pi*(.06+.88*j/20) for j in range(21)]]
        for a,b in zip(pts,pts[1:]):g.rod('CanopyFrames',a,b,.012,1,6)


def service_deck(x,y,z,width,length):
    g.box('Systems',(x,y,z),(width,length,.07),4)
    for j in range(8):
        g.box('Systems',(x,y-length*.42+j*length*.12,z+.05),(width*.87,length*.035,.035),1,chamfer=.004)


def side_bay(side,x,y,z,length,height):
    """Readable layered vent/coolant equipment rather than a painted rectangle."""
    g.box('RecessedEquipment',(side*x,y,z),(.07,length,height),4)
    for j in range(max(4,round(length/.09))):
        yy=y-length*.43+j*length*.86/max(3,round(length/.09)-1)
        g.box('RecessedEquipment',(side*(x+.045),yy,z),(.045,.022,height*.78),14,chamfer=.003)
    for zz in [-height*.50,height*.50]:
        g.rod('RecessedEquipment',(side*(x+.07),y-length*.5,z+zz),
              (side*(x+.07),y+length*.5,z+zz),.018,1,8)
    g.rod('RecessedEquipment',(side*(x+.075),y-length*.4,z),
          (side*(x+.075),y+length*.4,z),.018,2,10)


def dorsal_hatch(x,y,z,w,l,tile=0):
    g.box('Systems',(x,y,z),(w,l,.065),4)
    g.box('Systems',(x,y,z+.04),(w*.91,l*.94,.035),tile)
    for xx in [-.35,.35]:
        for yy in [-.38,.38]:
            g.rod('PlateFasteners',(x+xx*w,y+yy*l,z+.06),(x+xx*w,y+yy*l,z+.077),.009,4,6)
    g.box('Systems',(x,y-l*.25,z+.068),(w*.35,.035,.012),1,chamfer=.003)


def windows(length, width, z, count):
    for side in [-1,1]:
        for i in range(count):
            y = -length*.30+length*.62*i/max(1,count-1)
            x = side*width*max(.1,1-(y/(length*.51))**2)**.30
            g.box('WindowFrames',(x,y,z),(.045,.125,.065),4)
            g.box('Windows',(x+side*.025,y,z),(.008,.095,.029),5,chamfer=.002)


def saucer():
    # Rounded saucer with four copper research pods, gold dome and equipment aft.
    ellipsoid('PressureHull',(0,0,0),(1.1,1.07,.245),4,14,64)
    for j in range(2):
        r0,r1=.69+j*.20,.69+(j+1)*.20-.003
        for k in range(16):
            a0,a1=TAU*k/16+.003,TAU*(k+1)/16-.003
            vs=[]
            for layer in [0,1]:
                for ri in range(4):
                    r=r0+(r1-r0)*ri/3
                    for ai in range(5):
                        a=a0+(a1-a0)*ai/4
                        z=.245*math.sqrt(max(0,1-(r/1.1)**2))+.009-layer*.012
                        vs.append((r*math.cos(a),r*math.sin(a),z))
            fs=[]
            for ri in range(3):
                for ai in range(4):
                    q=(ri*5+ai,ri*5+ai+1,(ri+1)*5+ai+1,(ri+1)*5+ai)
                    fs.extend([q,tuple(v+20 for v in reversed(q))])
            boundary=list(range(5))+[9,14,19]+list(range(18,14,-1))+[10,5]
            fs.extend((a,a+20,b+20,b) for a,b in zip(boundary,boundary[1:]+boundary[:1]))
            g.facegroup('HullPlates',vs,fs,0)
    g.lathe('Systems',(0,0,.17),[(0,.70),(.08,.67),(.13,.57),(.16,.45),(.18,.12)],3,64)
    # Radial cap seams, bolt ring, inset hatch and perimeter belt details.
    g.lathe('Systems',(0,0,.347),[(0,.14),(.018,.15),(.035,.13)],3,32)
    for i in range(8):
        a=TAU*i/8
        g.rod('Systems',(.64*math.cos(a),.64*math.sin(a),.28),(.64*math.cos(a),.64*math.sin(a),.296),.013,4,6)
        pts=[(r*math.cos(a),r*math.sin(a),z) for r,z in [(.16,.350),(.45,.333),(.57,.303),(.66,.253)]]
        for p,q in zip(pts,pts[1:]):g.rod('Systems',p,q,.003,13,5)
        g.box('WindowFrames',(1.10*math.cos(a),1.10*math.sin(a),-.015),(.12,.025,.11),4,a+math.pi/2)
        if i%3!=0:g.box('Windows',(1.118*math.cos(a),1.118*math.sin(a),-.015),(.073,.012,.032),5,a+math.pi/2)
    for j in range(2):
        for i in range(12):
            a=TAU*(i+.5)/12;r=.48+j*.42
            g.rod('PlateFasteners',(r*math.cos(a),r*math.sin(a),.239-.10*(r/1.1)**2),
                  (r*math.cos(a),r*math.sin(a),.248-.10*(r/1.1)**2),.008,4,6)
    g.lathe('WindowFrames',(0,0,.19),[(0,.70),(.07,.69)],4,64)
    for i in range(32):
        a = TAU*i/32
        g.box('WindowFrames',(.703*math.cos(a),.703*math.sin(a),.23),(.111,.032,.072),4,a+math.pi/2,chamfer=.004)
        g.box('Windows',(.724*math.cos(a),.724*math.sin(a),.23),(.075,.009,.035),5,a+math.pi/2,chamfer=.002)
    for x in [-.86,.86]:
        for y in [-.70,.70]:
            ellipsoid('Pods',(x,y,0),(.255,.36,.20),2,10,24)
            g.box('WindowFrames',(x,y-.369,0),(.21,.04,.085),4)
            g.box('Windows',(x,y-.394,0),(.14,.015,.04),5)
            for t in [-.10,.10]:
                g.rod('Systems',(x+t,y-.24,.115),(x+t,y+.24,.115),.009,4,6)
            for yy in [-.12,.12]:
                for xx in [-.17,.17]:
                    g.rod('PlateFasteners',(x+xx,y+yy,.13),(x+xx,y+yy,.145),.009,4,6)
    for x in [-.52,.42]:
        g.box('Systems',(x,.59,.28),(.28,.27,.20),0)
        g.box('Windows',(x,.44,.32),(.20,.018,.045),5)
        # Keep the low service housing;omit unsupported tall aerials.
    # No parabolic dish:the original RI0A heading bank does not support it.
    for x in [-.42,.42]:nozzle(x,.95,-.15,.12,.12)
    service_deck(0,-.78,.16,.30,.20)
    for x in [-.68,.68]:g.rod('Systems',(x,-.3,-.15),(x,.45,-.15),.025,1,10)
    # Seat louvres on the aft service-box roofs,away from the gold dome rim.
    for x in [-.52,.42]:service_deck(x,.59,.397,.20,.20)
    for x in [-.34,.34]:
        g.pipe('Systems',[(x,.58,.32),(x,.80,.32),(x,.89,.12)],.018,4)
    # Authored hidden-side service housing, not a claim of recovered internals.
    g.lathe('Systems',(0,0,-.20),[(0,.55),(-.065,.48),(-.12,.32),(-.14,.14)],0,48)
    g.lathe('Systems',(0,0,-.34),[(0,.14),(-.025,.14),(-.04,.10)],4,24)
    for x in [-.48,.48]:
        for y in [-.36,.36]:
            g.box('Systems',(x,y,-.235),(.18,.27,.10),4)
            for j in range(5):g.box('Systems',(x,y-.10+j*.05,-.29),(.15,.021,.018),1,chamfer=.003)
            g.box('Windows',(x,y,-.304),(.055,.025,.008),6,chamfer=.002)


def assault():
    capsule((0,0,0),(.95,2.85,.62),18,28)
    ellipsoid('NoseShield',(0,-2.57,0),(.39,.38,.30),2,10,28)
    canopy(-1.30,.49,.56,.34,.095)
    # Low armoured bridge collar distinguishes the assault hull from civilian bubbles.
    for side in [-1,1]:
        fin([(side*.30,-1.95,.48),(side*.40,-1.67,.47),(side*.41,-.75,.50),
             (side*.28,-.62,.57)],.065,0)
    dorsal_hatch(0,-.51,.60,.46,.34,0)
    for side in [-1,1]:
        ellipsoid('Pods',(side*.87,.77,0),(.27,.54,.38),2,12,32)
        for y in [-.55,.40]:
            fin([(side*.68,y-.55,-.23),(side*1.38,y-.27,-.60),
                 (side*1.30,y+.62,-.57),(side*.74,y+.43,-.19)],.06)
        # Broad gold paint/armour fields lie on the curved hull, not upright fins.
        vertices=[];nx,ny=5,9
        for depth in [-.012,.012]:
            for j in range(ny):
                y=-1.05+j*1.95/(ny-1)
                half=.95*max(.01,1-(y/2.85)**2)**.36
                for i in range(nx):
                    x=side*half*(.37+i*.47/(nx-1))
                    z=.62*max(.01,1-(y/2.85)**2)**.41*math.sqrt(max(.01,1-(x/half)**2))
                    vertices.append((x,y,z+depth+.025))
        n=nx*ny;faces=[]
        for j in range(ny-1):
            for i in range(nx-1):
                q=j*nx+i;faces.extend([(q,q+1,q+1+nx,q+nx),(n+q+nx,n+q+1+nx,n+q+1,n+q)])
        edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(n-2,n-nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
        faces.extend((q,t,t+n,q+n) for q,t in zip(edge,edge[1:]+edge[:1]))
        g.facegroup('GoldHullFields',vertices,faces,3)
        service_deck(side*.47,.95,.52,.36,.64)
        # Layered shoulder armour, wide ochre identity fields and inset machinery.
        fin([(side*.39,-.7,.52),(side*.76,-.48,.47),(side*.86,1.35,.36),(side*.46,1.45,.55)],.075,0)
        fin([(side*.72,-1.15,.27),(side*.90,-.90,.19),(side*.94,.45,.17),(side*.82,.57,.30)],.035,3)
        side_bay(side,.98,-.15,-.12,1.30,.25)
        side_bay(side,.72,1.65,-.12,.62,.30)
        g.pipe('Systems',[(side*.81,-1.70,-.11),(side*.98,-1.2,-.11),(side*.98,-.2,-.11)],.026,1)
        dorsal_hatch(side*.35,1.85,.43,.30,.40)
        for j in range(3):g.box('Systems',(side*.86,-.65+j*.18,.20),(.05,.11,.12),3)
        nozzle(side*.42,2.90,0,.31,.45)
        ellipsoid('DriveAssemblies',(side*.42,2.06,0),(.36,.76,.35),0,12,28)
    # Closed hardpoint covers, not an assumed fixed modular weapon loadout.
    for x,y,z in [(0,-.2,.67),(-.70,-1.22,-.28),(.70,-1.22,-.28)]:
        g.box('HardpointCovers',(x,y,z),(.28,.43,.12),4)
        g.box('HardpointCovers',(x,y,z+.07),(.24,.35,.055),1)
    antenna(0,1.15,.64,.45)
    windows(5.6,.98,.05,11)


def heavy():
    capsule((0,0,0),(1.17,4.2,.86),26,32,1)
    nose_collar(-4.02,.55)
    canopy(-2.70,.57,1.14,.53,.36)
    for y,r in [(-1.35,.44),(.4,.56),(2.0,.36)]:cap(0,y,.78,r)
    for side in [-1,1]:
        for y in [-1.35,1.15]:
            ellipsoid('CopperHousings',(side*1.12,y,0),(.15,.48,.44),2,14,32)
            g.box('Windows',(side*1.275,y,0),(.012,.20,.04),5)
        for y in [-1.0,1.40]:
            fin([(side*.71,y-.8,-.55),(side*1.55,y-.35,-.57),
                 (side*1.48,y+.85,-.53),(side*.74,y+.65,-.51)],.06,2)
        service_deck(side*.56,.10,.73,.30,.65)
        for y in [-2.0,.05,2.10]:side_bay(side,1.21,y,-.36,.72,.29)
        for y in [-.75,1.10,2.65]:dorsal_hatch(side*.53,y,.75,.33,.42,1)
        g.pipe('Systems',[(side*.74,-2.6,-.54),(side*1.02,-2.1,-.55),(side*1.02,2.5,-.55)],.024,2)
        for y in [-2.0,-.2,1.60]:
            g.box('Systems',(side*.55,y,-.70),(.28,.70,.12),4)
            for j in range(6):g.box('Systems',(side*.55,y-.27+j*.10,-.77),(.24,.045,.03),1)
    nozzle(0,4.12,0,.58,.45)
    antenna(.25,1.22,.84,.37)
    windows(8.2,1.20,-.1,23)


def transport():
    capsule((0,-3.8,0),(1.83,4.8,1.25),28,32,1)
    capsule((0,4.7,.10),(1.62,3.9,1.06),26,32,1)
    g.box('CargoBridge',(0,.80,.10),(1.90,1.60,1.15),4,chamfer=.15)
    for x in [-.75,.75]:
        for z in [-.35,.48]:
            g.rod('CargoBridge',(x,-.1,z),(x,1.75,z),.075,1,12)
    for side in [-1,1]:
        for z in [-.25,.42]:
            g.rod('CargoBridge',(side*1.13,-1.20,z),(side*1.13,2.45,z),.055,1,12)
        for y in [-.85,.35,1.60,2.12]:
            g.box('CargoBridge',(side*1.13,y,.085),(.17,.12,.77),0)
            g.rod('PlateFasteners',(side*1.22,y,.09),(side*1.25,y,.09),.028,4,8)
    # The reference's blunt optical prow is distinct from the pressure envelope.
    for x in [-.32,.32]:
        g.rod('Systems',(x,-7.45,.72),(x,-7.67,.38),.035,1,10)
    # Local centre of the front module puts its nose at -8.20.
    nose_collar(-8.40,.70)
    canopy(-6.0,.79,1.48,.65,.48)
    cap(0,-3.4,1.20,.78);cap(0,4.0,1.16,.62)
    for x in [-.45,.45]:
        g.box('CargoBridge',(x,.55,.61),(.70,1.80,.32),4)
        for y in [.0,.55,1.10]:
            g.box('CargoBridge',(x,y,.80),(.64,.48,.07),1)
            g.box('CargoBridge',(x,y-.25,.67),(.50,.018,.065),3)
    for side in [-1,1]:
        for y in [-2.2,3.80]:
            ellipsoid('DriveAssemblies',(side*2.10,y,.04),(.48,1.23,.48),0,16,32)
            nozzle(side*2.10,y+1.30,.04,.36,.22)
            fin([(side*1.23,y-1.1,-.1),(side*2.35,y-.6,-.15),
                 (side*2.25,y+1.0,-.1),(side*1.25,y+1.2,-.05)],.09,3)
        for y in [-4.4,4.6]:service_deck(side*.78,y,.98,.44,1.0)
        for y in [-4.8,-2.5,3.5,5.6]:
            side_bay(side,1.80 if y<0 else 1.64,y,-.50,1.10,.38)
            dorsal_hatch(side*.72,y,1.01,.48,.58,1)
        for y in [-1.45,.1,1.65]:
            g.box('CargoBridge',(side*.95,y,.59),(.39,.36,.68),4)
            for z in [.42,.72]:g.box('CargoBridge',(side*1.16,y,z),(.025,.26,.055),3)
        g.pipe('Systems',[(side*1.12,-3.8,-.89),(side*1.38,-2.8,-.88),(side*1.38,1.5,-.70),(side*1.12,2.5,-.70)],.035,2)
        # Small repeated freight/service lights establish the larger scale.
        for j in range(35):
            y=-6.5+j*.38
            x=side*(1.73 if y<0 else 1.53)*math.sqrt(max(.22,1-((y+3.3)/5.4 if y<0 else (y-4.05)/4.7)**2))
            g.box('WindowFrames',(x,y,-.35),(.045,.105,.085),4)
            g.box('Windows',(x+side*.027,y,-.35),(.008,.065,.025),5,chamfer=.001)
        for y in [-3.6,-1.0,2.6,5.4]:
            g.box('Systems',(side*.60,y,-1.05),(.40,.70,.14),4)
            for j in range(6):g.box('Systems',(side*.60,y-.27+j*.10,-1.13),(.34,.045,.025),1)
    nozzle(0,8.65,.1,.60,.45)
    for x in [-.38,.38]:antenna(x,1.35,.77,.28)


def material():
    mat=bpy.data.materials.new('Rigellian | shared worn PBR');mat.use_nodes=True
    tree=mat.node_tree;bs=tree.nodes.get('Principled BSDF')
    textures={}
    for name in ['base-colour','occlusion-roughness-metallic','emission']:
        path=ROOT/'sources/materials/rigellian-mobile-fleet'/f'{name}.png'
        im=bpy.data.images.load(str(path),check_existing=True)
        if name=='occlusion-roughness-metallic':im.colorspace_settings.name='Non-Color'
        im.pack();node=tree.nodes.new('ShaderNodeTexImage');node.image=im;textures[name]=node
    tree.links.new(textures['base-colour'].outputs['Color'],bs.inputs['Base Color'])
    sep=tree.nodes.new('ShaderNodeSeparateColor');tree.links.new(textures['occlusion-roughness-metallic'].outputs['Color'],sep.inputs['Color'])
    tree.links.new(sep.outputs['Green'],bs.inputs['Roughness']);tree.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    tree.links.new(textures['emission'].outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=2.0
    return mat


def finalize(mat, root):
    objects=[]
    for name,data in g.GROUPS.items():
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(data['v'],[],data['f']);mesh.update()
        uv=mesh.uv_layers.new(name='Rigellian PBR atlas')
        for face,tile,(low,high) in zip(mesh.polygons,data['t'],data['charts']):
            normal=face.normal;axis=max(range(3),key=lambda a:abs(normal[a]));axes=[a for a in range(3) if a!=axis]
            coords=[mesh.vertices[mesh.loops[i].vertex_index].co for i in face.loop_indices]
            for li,v in zip(face.loop_indices,coords):
                u,w=[(v[a]-low[a])/max(high[a]-low[a],.000001) for a in axes]
                uv.data[li].uv=((tile%4+.025+u*.95)/4,1-(tile//4+.025+w*.95)/4)
            face.use_smooth=name in ('PressureHull','HullPlates','Pods','NoseShield','CopperHousings','ScienceDish','Glazing')
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
        mesh.set_sharp_from_angle(angle=.65)
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.parent=root;mesh.materials.append(mat);objects.append(obj)
    return objects


def studio(length, width=1000):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.resolution_x=width;scene.render.resolution_y=round(width*.75);scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    if scene.world is None:scene.world=bpy.data.worlds.new('Neutral orbital studio')
    scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.14,.18,.22,1);bg.inputs[1].default_value=.5
    scene.view_settings.view_transform='AgX'
    scene.view_settings.exposure=-.65
    bpy.ops.object.camera_add();scene.camera=bpy.context.object;scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=length*1.5
    for name,pos,power,colour in [('Key',(-.6,-.7,1.1),1100,(1,.87,.74)),('Fill',(1,-.2,.6),850,(.74,.87,1)),('Rim',(.1,1,.8),1500,(1,.87,.66))]:
        bpy.ops.object.light_add(type='AREA',location=Vector(pos)*length)
        light=bpy.context.object;light.name=name;light.data.energy=power*length*length/16;light.data.shape='DISK';light.data.size=length*.8;light.data.color=colour
        light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
    return scene


def aim(scene,p,length):
    camera=scene.camera;camera.location=Vector(p)*length
    camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    inv=camera.matrix_world.inverted()
    pts=[inv@(o.matrix_world@Vector(v)) for o in scene.objects if o.type=='MESH' for v in o.bound_box]
    width=max(v.x for v in pts)-min(v.x for v in pts);height=max(v.y for v in pts)-min(v.y for v in pts)
    camera.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.14
    # Centre projected geometry, including dish/masts, without changing physical scale.
    delta=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,0))
    camera.location+=camera.rotation_euler.to_quaternion()@delta


def build(ship,no_render):
    bpy.ops.wm.read_factory_settings(use_empty=False);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.context.preferences.filepaths.save_version=0;g.GROUPS.clear();g.PARENTS.clear();g.COUNTS.clear()
    root=g.empty('PlacementRoot');root['catalogue_id']=ship['id'];root['forward_axis']='-Y';root['up_axis']='Z'
    root['proposed_world_size']=ship['proposed_world_size'];root['world_size_is_authored_recommendation']=True
    root['source_reference']=ship['legacy_entry'];root['hi_def_reference_sha256']=ship['hi_def_reference']['sha256']
    root['attachment_status']='No calibrated weapon sockets; use catalogue hardpoints after integration acceptance'
    {'lazzaro-research':saucer,'delphini-assault':assault,'messier-lukannon':heavy,'transportation':transport}[ship['slug']]()
    meshes=finalize(material(),root)
    bounds=[Vector(v) for o in meshes for v in o.bound_box]
    lo=Vector(tuple(min(p[a] for p in bounds) for a in range(3)));hi=Vector(tuple(max(p[a] for p in bounds) for a in range(3)))
    factor=ship['authoring_length_units']/max(hi-lo);centre=(lo+hi)/2
    for obj in meshes:
        for vert in obj.data.vertices:vert.co=(vert.co-centre)*factor
    length=ship['authoring_length_units'];scene=studio(length);aim(scene,(.8,-1.15,.72),length)
    out=ROOT/ship['canonical_directory'];out.mkdir(parents=True,exist_ok=True)
    media=ROOT/'gallery/media/objects/rigellian'/ship['slug'];media.mkdir(parents=True,exist_ok=True)
    triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    assert triangles<=110000,(ship['slug'],triangles)
    assert len(meshes)<=24,(ship['slug'],len(meshes))
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for obj in meshes:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True,export_cameras=False,export_lights=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True,relative_remap=True)
    if not no_render:
        for view,pos in [('front-quarter',(.8,-1.15,.72)),('rear-quarter',(-.8,1.15,.72)),('top',(0,-.001,1.5)),('underside',(.8,-1.15,-.72))]:
            aim(scene,pos,length)
            if view=='underside':
                for light in [o for o in scene.objects if o.type=='LIGHT']:
                    light.location.z=-light.location.z;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    report={'id':ship['id'],'triangles':triangles,'mesh_batches':len(meshes),'materials':1,
            'measured_dimensions':[round(v*factor,6) for v in hi-lo],
            'normalization_factor':factor,'proposed_world_size':ship['proposed_world_size'],
            'world_size_status':'authored recommendation; requires game catalogue override',
            'blend_sha256':hashlib.sha256((out/'model.blend').read_bytes()).hexdigest(),
            'glb_sha256':hashlib.sha256((out/'model.glb').read_bytes()).hexdigest()}
    (out/'generation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RIGELLIAN_GENERATED '+json.dumps(report),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ship');parser.add_argument('--no-render',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for ship in STYLE['ships']:
        if not args.ship or ship['slug']==args.ship:build(ship,args.no_render)
