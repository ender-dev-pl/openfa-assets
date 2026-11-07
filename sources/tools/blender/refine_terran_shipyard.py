"""High-detail game-budget Terran Ship Yard: authored rigid assemblies and worn PBR atlas.

PB25 colour/video establish layout and open/closed phases. Internal telescopic shutter
tracks, plate joints and stowage are authored interpretations, not recovered mechanisms.
No legacy pixels are used as textures. Run in Blender 4.5 LTS with -- --draft for previews.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'sources/objects/terran/ship-yard/refined'
MEDIA=ROOT/'gallery/media/objects/terran/ship-yard/refined'
TAU=math.tau
SCALE=.3
GROUPS={}
PARENTS={}
COUNTS={}
RNG=random.Random(225)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def empty(name,parent=None,location=(0,0,0)):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o)
    o.parent=parent;o.location=location;PARENTS[name]=o
    return o


def facegroup(group,vertices,faces,tile=1):
    row=GROUPS.setdefault(group,dict(v=[],f=[],t=[]));off=len(row['v'])
    row['v'].extend(vertices);row['f'].extend([tuple(off+i for i in f) for f in faces]);row['t'].extend([tile]*len(faces))
    COUNTS[group]=COUNTS.get(group,0)+1


def box(group,p,size,tile=1,angle=0,chamfer=.015):
    # An eight-sided solid gives the silhouette real edge catches at modest triangle cost.
    x,y,z=p;a,b,h=[v/2 for v in size];c=min(chamfer,a*.3,b*.3)
    poly=[(-a+c,-b), (a-c,-b),(a,-b+c),(a,b-c),(a-c,b),(-a+c,b),(-a,b-c),(-a,-b+c)]
    co,si=math.cos(angle),math.sin(angle)
    vs=[(x+u*co-v*si,y+u*si+v*co,z+w) for w in [-h,h] for u,v in poly]
    fs=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    facegroup(group,vs,fs,tile)


def lathe(group,p,profile,tile=1,n=20):
    vs=[(p[0]+r*math.cos(TAU*i/n),p[1]+r*math.sin(TAU*i/n),p[2]+z) for z,r in profile for i in range(n)]
    fs=[tuple(range(n-1,-1,-1)),tuple((len(profile)-1)*n+i for i in range(n))]
    for j in range(len(profile)-1):
        for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    facegroup(group,vs,fs,tile)


def rod(group,a,b,r=.025,tile=1,n=8):
    axis=Vector(b)-Vector(a);q=axis.to_track_quat('Z','Y');vs=[]
    for p in [a,b]:
        for i in range(n):vs.append(tuple(Vector(p)+q@Vector((r*math.cos(TAU*i/n),r*math.sin(TAU*i/n),0))))
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    facegroup(group,vs,fs,tile)


def pipe(group,points,r=.05,tile=1):
    for a,b in zip(points,points[1:]):rod(group,a,b,r,tile,10)
    for p in points[1:-1]:lathe(group,(p[0],p[1],p[2]-.06),[(0,r*1.18),(.12,r*1.18)],tile,10)


def ring_sector(group,r0,r1,z0,z1,a0,a1,tile=0,steps=3):
    vs=[]
    for z in [z0,z1]:
        for r in [r0,r1]:
            vs.extend((r*math.cos(a0+(a1-a0)*i/steps),r*math.sin(a0+(a1-a0)*i/steps),z) for i in range(steps+1))
    k=steps+1;fs=[]
    for i in range(steps):fs.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
    fs.extend([(0,k,3*k,2*k),(steps,2*k+steps,3*k+steps,k+steps)])
    facegroup(group,vs,fs,tile)


def rail(group,a,b,height=.32):
    rod(group,(a[0],a[1],a[2]+height),(b[0],b[1],b[2]+height),.018,3)
    rod(group,(a[0],a[1],a[2]+height*.5),(b[0],b[1],b[2]+height*.5),.012,1)
    length=(Vector(b)-Vector(a)).length
    for i in range(max(1,math.ceil(length/.55))+1):
        p=Vector(a).lerp(Vector(b),i/max(1,math.ceil(length/.55)));rod(group,p,p+Vector((0,0,height)),.018,3)


def stairs(group,start,end,width=.52,steps=6):
    a,b=Vector(start),Vector(end);delta=b-a;side=Vector((-delta.y,delta.x,0)).normalized()
    angle=math.atan2(delta.y,delta.x)
    for i in range(steps):
        p=a.lerp(b,(i+.5)/steps);box(group,p,(delta.xy.length/steps+.02,width,.045),8,angle)
        box(group,p+Vector((0,0,.026)),(.025,width,.008),3,angle)
    for s in [-1,1]:
        off=side*width*.55;rod(group,a+off,b+off,.025,1)
        rail(group,a+off,b+off,.35)


def panel_hazard(group,p,size,angle=0):box(group,p,size,10,angle)


def make_static():
    g='StaticBase'
    lathe(g,(0,0,0),[(0,4.42),(.16,4.5),(.23,4.5),(.26,4.36)],1,80)
    # Floor plates, expansion seams and drains, kept inside the circular boundary.
    for i in range(-7,8):
        for j in range(-7,8):
            x=i*.56;y=j*.56
            if math.hypot(abs(x)+.29,abs(y)+.29)<4.27:
                box(g,(x,y,.278),(.545,.545,.035),4 if (i+j)%4 else 12,chamfer=.004)
                if (i*3+j)%13==0:
                    for k in range(7):box(g,(x-.18+k*.06,y,.30),(.025,.32,.008),7,chamfer=.002)
    for k in range(48):
        a0=TAU*k/48+.005;a1=TAU*(k+1)/48-.005
        ring_sector(g,4.22,4.48,.28,1.40,a0,a1,0 if k%4 else 9,2)
        ring_sector(g,4.18,4.51,1.39,1.49,a0,a1,0,2)
        ring_sector(g,4.18,4.28,1.49,1.825,a0,a1,1,2)
        a=(a0+a1)/2
        # Inward ribs, inspection plates and capped upper vents.
        box(g,(4.19*math.cos(a),4.19*math.sin(a),.85),(.08,.09,1.08),1,a)
        for z in [.47,1.18]:
            box(g,(4.17*math.cos(a),4.17*math.sin(a),z),(.026,.33,.17),9,a)
        for t in range(4):
            aa=a0+(a1-a0)*(t+.5)/4
            box(g,(4.34*math.cos(aa),4.34*math.sin(aa),1.50),(.17,.026,.018),7,aa)
        for z in [.39,1.29]:
            rod(g,(4.15*math.cos(a),4.15*math.sin(a),z),(4.10*math.cos(a),4.10*math.sin(a),z),.025,8,6)
    # Service entrances inset against the inner wall, not silhouettes pasted on it.
    for a in [math.pi*.24,math.pi*.75,math.pi*1.15]:
        x,y=4.07*math.cos(a),4.07*math.sin(a)
        box(g,(x,y,.75),(.12,.63,.92),1,a)
        box(g,(x-.075*math.cos(a),y-.075*math.sin(a),.74),(.04,.43,.71),2,a)
        for side in [-1,1]:
            xx=x-side*.27*math.sin(a)-.10*math.cos(a);yy=y+side*.27*math.cos(a)-.10*math.sin(a)
            box(g,(xx,yy,.75),(.06,.065,.85),10,a)
        box(g,(x-.10*math.cos(a),y-.10*math.sin(a),1.20),(.10,.55,.055),6,a)
    # Unequal vessels retain the recognizable legacy equipment distribution.
    for index,(x,y,r,h) in enumerate([(-2.65,-1.70,.65,1.05),(-1.15,-2.80,.73,.96),(.1,2.65,.83,.92),(1.8,2.60,.44,.92),(2.85,1.85,.38,.82),(3.35,.95,.32,.70)]):
        lathe(g,(x,y,.30),[(0,r*.96),(.10,r*1.08),(.16,r*1.08),(.20,r), (h*.76,r),(h*.87,r*.95),(h*.96,r*.65),(h,r*.16)],1,24)
        for z in [.19,.34,h*.76]:lathe(g,(x,y,.3+z),[(0,r*1.015),(.025,r*1.015)],8,24)
        lathe(g,(x,y,.60),[(0,r*1.025),(.12,r*1.025)],10,24)
        lathe(g,(x,y,.30+h),[(0,.095),(.10,.095),(.12,.13)],1,12)
        pipe(g,[(x,y,.42+h),(x-.25,y,.42+h),(x-.5,y,.25+h),(x-.5,y,.44)],.052)
        for k in range(8):
            a=TAU*k/8;rod(g,(x+r*.88*math.cos(a),y+r*.88*math.sin(a),.46),(x+r*.88*math.cos(a),y+r*.88*math.sin(a),.50),.025,8,6)
    # Docking/service deck: separate rigid batch for explicit contact verification.
    g='FabricationDeck'
    for x in [-.78,.78]:
        for y in [-1.4,.7]:box(g,(x,y,.52),(.14,.14,.48),1)
    box(g,(0,-.35,.75),(1.95,2.65,.15),1)
    for i in range(5):
        for j in range(6):box(g,(-.77+i*.385,-1.43+j*.43,.836),(.37,.415,.018),12,chamfer=.004)
    for x in [-.94,.94]:
        box(g,(x,-.35,.85),(.045,2.54,.015),3)
        rail(g,(x,-1.59,.85),(x,-.40,.85))
        rail(g,(x,.40,.85),(x,.88,.85))
    for y in [-1.62,.92]:
        box(g,(0,y,.85),(1.85,.035,.015),3)
    stairs(g,(1.48,-1.85,.31),(.95,-.85,.84),.48,6)
    stairs(g,(-1.48,-1.85,.31),(-.95,-.85,.84),.48,6)
    # Four landing shoes support the lowered beam on the fabrication platform.
    for x in [-.45,.55]:
        for y in [-.20,.20]:box(g,(x,y,.875),(.20,.22,.060),10)
    g='StaticBase'
    # Secondary workbench and catwalk at the rear.
    box(g,(-.8,1.50,.65),(1.8,.48,.10),8)
    for x in [-1.55,-.05]:box(g,(x,1.5,.46),(.10,.4,.38),1)
    rail(g,(-1.65,1.72,.71),(.08,1.72,.71))
    # Crates and service consoles, deliberately few large readable objects.
    for index,(x,y) in enumerate([(-3.1,.7),(-2.8,1.35),(-1.8,2.5),(2.3,-2.3),(2.8,-1.75),(.15,-3.6)]):
        size=.38+index%2*.10
        box(g,(x,y,.30+size/2),(size,size,size),1)
        for dx in [-size*.36,size*.36]:box(g,(x+dx,y,.30+size/2),(.035,size+.02,size+.025),8)
        box(g,(x,y-size*.51,.30+size*.66),(size*.55,.012,.09),3)
    for a in [0,math.pi/2,math.pi,math.pi*1.5]:
        x,y=3.98*math.cos(a),3.98*math.sin(a)
        box(g,(x,y,1.23),(.08,.18,.07),6,a)
    # Work-zone markings; metal strip geometry has no alpha blend/sorting cost.
    for x in [-1.18,1.18]:box(g,(x,-.4,.310),(.035,3.30,.009),3)
    for y in [-2.05,1.25]:box(g,(0,y,.310),(2.40,.035,.009),3)
    # Surface service hardware: horizontal panel joints, louvers, bolts and pipes.
    for k in range(48):
        a=TAU*(k+.5)/48
        for z in [.69,1.02]:
            box(g,(4.495*math.cos(a),4.495*math.sin(a),z),(.018,.48,.018),2,a)
        for z in [.40,1.30]:
            for tangent in [-.16,.16]:
                x=4.505*math.cos(a)-tangent*math.sin(a);y=4.505*math.sin(a)+tangent*math.cos(a)
                rod(g,(x,y,z),(x+.013*math.cos(a),y+.013*math.sin(a),z),.018,8,6)
        if k%3==0:
            for z in [.76,.82,.88,.94]:box(g,(4.14*math.cos(a),4.14*math.sin(a),z),(.04,.22,.022),7,a)
    for x,y,r,h in [(-2.65,-1.70,.65,1.05),(-1.15,-2.80,.73,.96),(.1,2.65,.83,.92)]:
        for k in range(12):
            a=TAU*k/12
            rod(g,(x+r*1.007*math.cos(a),y+r*1.007*math.sin(a),.65),(x+r*1.007*math.cos(a),y+r*1.007*math.sin(a),.3+h*.77),.009,2,6)
        box(g,(x,y-r-.022,.91),(.20,.025,.14),2)
        box(g,(x,y-r-.04,.91),(.12,.012,.055),6)
        for side in [-1,1]:
            pipe(g,[(x+side*r*.75,y,.40),(x+side*r*.75,y-r-.12,.40),(x+side*r*.75,y-r-.12,.75)],.035)
    # Conduits sit against the wall, with bracketed elbows and readable valves.
    for side in [-1,1]:
        pts=[(side*2.75,1.7,.38),(side*3.10,1.2,.38),(side*3.25,.7,.38),(side*3.25,-.3,.38)]
        pipe(g,pts,.055)
        for x,y,z in pts[1:-1]:
            rod(g,(x,y,z),(x,y,z+.20),.03,1)
            lathe(g,(x,y,z+.18),[(0,.09),(.025,.09)],3,10)
    # Tool lockers, hinges, handles and panel instruments.
    for x,y in [(-3.15,.70),(2.80,-1.75)]:
        box(g,(x,y,.91),(.44,.30,.48),1)
        box(g,(x,y-.16,.93),(.36,.015,.31),9)
        box(g,(x+.11,y-.18,.91),(.025,.04,.11),8)
        for dx in [-.10,0,.10]:box(g,(x+dx,y-.18,1.03),(.045,.02,.024),6)
    # Cable trays under the deck and a guarded maintenance walkway.
    for x in [-.80,.80]:
        box(g,(x,-.30,.63),(.075,2.5,.07),2)
        for y in [-1.35,-.85,-.35,.15,.65]:box(g,(x,y,.60),(.22,.035,.025),1)
    for x in [1.85,2.35,2.85]:
        box(g,(x,-.05,.65),(.48,.45,.06),7)
        for y in [-.20,.20]:box(g,(x,y,.46),(.06,.06,.38),1)
    rail(g,(1.60,.20,.69),(3.08,.20,.69))
    stairs(g,(2.75,-.85,.31),(2.75,-.25,.69),.45,4)
    # Crane's fixed foundation and nested lower mast sleeve.
    box(g,(-2.12,0,.39),(.96,.96,.20),10)
    for x in [-2.43,-1.81]:
        for y in [-.31,.31]:
            box(g,(x,y,.62),(.15,.15,.48),1)
            lathe(g,(x,y,.89),[(0,.08),(.04,.08)],8,8)
    box(g,(-2.12,0,.85),(.70,.70,.10),8)


def make_crane():
    g='CraneLift'
    # Telescopic mast lowers only until the boom lands on the deck's four shoes.
    for x in [-.23,.23]:
        for y in [-.23,.23]:box(g,(x,y,1.3),(.10,.10,2.6),1)
    for z in [.22,.77,1.32,1.87,2.42]:
        for y in [-.23,.23]:rod(g,(-.23,y,z),(.23,y,z+.45),.036,8)
        for x in [-.23,.23]:rod(g,(x,-.23,z),(x,.23,z+.45),.036,8)
    for z in [.18,.73,1.28,1.83,2.38]:box(g,(0,0,z),(.55,.55,.075),1)
    box(g,(0,0,2.65),(.90,.95,.16),8)
    for y in [-.44,.44]:rail(g,(-.43,y,2.75),(.43,y,2.75),.25)
    for i in range(12):
        z=.25+i*.19;rod(g,(-.33,-.32,z),(-.33,.04,z),.014,3)
    rod(g,(-.33,-.32,.20),(-.33,-.32,2.5),.02,1)
    rod(g,(-.33,.04,.20),(-.33,.04,2.5),.02,1)
    # Cabin rides with the head; large glazing geometry, mullions and service panels.
    g='CraneSlew'
    box(g,(0,0,.02),(1.05,1.00,.12),1)
    box(g,(-.05,-.20,.36),(.92,.85,.62),0)
    box(g,(-.05,-.635,.44),(.77,.02,.32),5)
    for x in [-.30,.04,.33]:box(g,(x,-.655,.44),(.027,.025,.35),8)
    box(g,(-.525,-.22,.44),(.025,.55,.31),5)
    box(g,(-.05,-.2,.70),(1.02,.96,.10),8)
    box(g,(-.05,-.67,.18),(.68,.025,.12),9)
    for x in [-.33,.26]:box(g,(x,-.69,.13),(.06,.03,.035),6)
    rod('Antenna',(0,0,0),(0,0,.79),.016,8)
    rod('Antenna',(0,0,.54),(.14,0,.54),.01,8)
    lathe('Antenna',(-.46,.01,0),[(0,.07),(.12,.07),(.15,.035)],14,12)
    # Twin I-section rails, cross braces, cap plates and end stops.
    for y in [-.20,.20]:
        box(g,(2.10,y,.17),(4.78,.055,.24),1)
        for z in [.035,.30]:box(g,(2.10,y,z),(4.86,.16,.045),8)
    for x in [i*.35 for i in range(13)]:
        box(g,(x,0,.04),(.055,.48,.05),1)
        rod(g,(x,-.18,.25),(x+.28,.18,.25),.018,1)
    box(g,(4.50,0,.18),(.16,.65,.43),8)
    for y in [-.29,.29]:box(g,(4.51,y,.15),(.12,.07,.28),10)
    # Rigid trolley includes winch drums and independently driven hoist below it.
    g='Trolley';box(g,(0,0,.14),(.60,.70,.21),8)
    for y in [-.30,.30]:
        box(g,(0,y,.20),(.48,.07,.23),0)
        for x in [-.19,.19]:rod(g,(x,y-.06,.03),(x,y+.06,.03),.07,2,12)
    for x in [-.15,.15]:rod(g,(x,-.18,.13),(x,.18,.13),.09,1,12)
    box(g,(0,-.37,.14),(.18,.025,.05),6)
    g='Hoist';box(g,(0,0,0),(.43,.33,.13),3)
    for x in [-.14,.14]:rod(g,(x,-.14,.0),(x,.14,0),.078,1,12)
    for x in [-.14,.14]:rod(g,(x,0,-.05),(x,0,-.26),.025,1,8)
    # Open J hook as polygonal metal segments (a torus would read as the old eye).
    for k in range(8):
        a=-math.pi*.95+k*math.pi*1.45/8;b=-math.pi*.95+(k+1)*math.pi*1.45/8
        rod(g,(.10*math.cos(a),0,-.27+.10*math.sin(a)),(.10*math.cos(b),0,-.27+.10*math.sin(b)),.027,8,8)
    for k in range(4):rod('HoistCables',(-.15+(k//2)*.30,-.10+(k%2)*.20,0),(-.15+(k//2)*.30,-.10+(k%2)*.20,-1),.009,2,6)


def make_shutters():
    # Rigid, overlapping end sections telescope across a central section.
    # Curved ends close the circular opening without oversized rectangular corners.
    for side in [-1,1]:
        for j in range(4):
            y0=j*1.025;y1=min(4.19,(j+1)*1.025+.025);yc=(y0+y1)/2
            span=math.sqrt(4.20**2-yc*yc)
            for piece in [-1,0,1]:
                name=f'Shutter_{side:+d}_{j}_{piece:+d}'
                empty(name,PARENTS['PlacementRoot'])
                o=PARENTS[name];o['assembly']='rigid telescopic cover; hidden travel is authored interpretation'
                o['band']=j;o['side']=side;o['piece']=piece
                o['deployed_y']=side*yc;o['deployed_x']=piece*span*.61
                vertices=[];n=9
                for z in [-.025,.025]:
                    for row in range(n):
                        y=y0+(y1-y0)*row/(n-1);sx=math.sqrt(max(0,4.20**2-y*y))
                        low,high=(-sx,-sx*.22) if piece==-1 else (sx*.22,sx) if piece==1 else (-sx*.34,sx*.34)
                        vertices.extend([(low-o['deployed_x'],side*y-o['deployed_y'],z),(high-o['deployed_x'],side*y-o['deployed_y'],z)])
                k=2*n;faces=[]
                for row in range(n-1):
                    a=row*2;faces.extend([(a,a+2,a+3,a+1),(k+a+1,k+a+3,k+a+2,k+a),(a,k+a,k+a+2,a+2),(a+1,a+3,k+a+3,k+a+1)])
                faces.extend([(0,1,k+1,k),(k-2,2*k-2,2*k-1,k-1)])
                facegroup(name,vertices,faces,0 if j%2 else 9)
                for f in [-.42,.42]:
                    y=yc+(y1-y0)*f;sx=math.sqrt(max(0,4.20**2-y*y))
                    low,high=(-sx,-sx*.22) if piece==-1 else (sx*.22,sx) if piece==1 else (-sx*.34,sx*.34)
                    rod(name,(low-o['deployed_x']+.03,side*y-o['deployed_y'],.034),(high-o['deployed_x']-.03,side*y-o['deployed_y'],.034),.012,1,6)
                    for x in [low+.09,high-.09]:lathe(name,(x-o['deployed_x'],side*y-o['deployed_y'],.03),[(0,.02),(.018,.02)],8,6)


def materials():
    m=bpy.data.materials.new('Ship Yard | worn PBR atlas, opaque game material');m.use_nodes=True;m.use_backface_culling=True
    n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');l.new(bs.outputs['BSDF'],out.inputs['Surface'])
    directory=ROOT/'sources/materials/terran-shipyard-highdetail'
    images={}
    for name in ['albedo','orm','emission']:
        im=bpy.data.images.load(str(directory/(name+'.png')));im.name='Shipyard '+name;im.pack();im.filepath='//../../../../materials/terran-shipyard-highdetail/'+name+'.png';images[name]=im
        tex=n.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear'
        if name=='albedo':l.new(tex.outputs['Color'],bs.inputs['Base Color'])
        elif name=='orm':
            im.colorspace_settings.name='Non-Color';sep=n.new('ShaderNodeSeparateColor');l.new(tex.outputs['Color'],sep.inputs[0]);l.new(sep.outputs['Green'],bs.inputs['Roughness']);l.new(sep.outputs['Blue'],bs.inputs['Metallic'])
        else:l.new(tex.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=2.0
    return m,images


def finalize_geometry(material):
    for group,data in GROUPS.items():
        me=bpy.data.meshes.new(group+' | batched manufactured components');me.from_pydata(data['v'],[],data['f']);me.update()
        o=bpy.data.objects.new(group+'Geometry',me);bpy.context.collection.objects.link(o);o.parent=PARENTS[group];me.materials.append(material)
        o['component_count']=COUNTS[group];o['geometry_role']=group;o['catalogue_id']='terran:ship-yard'
        uv=me.uv_layers.new(name='PBR atlas')
        for poly,tile in zip(me.polygons,data['t']):
            n=poly.normal;axes=sorted(range(3),key=lambda i:abs(n[i]))[:2]
            coords=[me.vertices[me.loops[i].vertex_index].co for i in poly.loop_indices]
            lo=[min(c[a] for c in coords) for a in axes];hi=[max(c[a] for c in coords) for a in axes]
            for li,c in zip(poly.loop_indices,coords):
                u=(c[axes[0]]-lo[0])/max(1e-5,hi[0]-lo[0]);v=(c[axes[1]]-lo[1])/max(1e-5,hi[1]-lo[1])
                uv.data[li].uv=((tile%4+.02+u*.96)/4,1-(tile//4+.02+v*.96)/4)
        # Smooth cylindrical strips while retaining hard manufactured corners.
        for p in me.polygons:
            p.use_smooth=True
        me.set_sharp_from_angle(angle=.65)
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()


def key(o,frame,location=None,rotation=None,scale=None):
    if location is not None:o.location=location;o.keyframe_insert('location',frame=frame)
    if rotation is not None:o.rotation_euler=rotation;o.keyframe_insert('rotation_euler',frame=frame)
    if scale is not None:o.scale=scale;o.keyframe_insert('scale',frame=frame)


def animate():
    # Open working -> crane stowed -> covers closed -> reopen -> working.
    phases=[(1,0),(40,0),(90,0),(125,0),(160,1),(195,1),(225,0),(260,0),(300,0)]
    for name,o in PARENTS.items():
        if not name.startswith('Shutter_'):continue
        j=o['band'];side=o['side'];piece=o['piece']
        for frame,closed in phases:
            y=o['deployed_y'] if closed else side*(3.19+j*.012)
            x=o['deployed_x'] if closed else piece*.12
            z=1.82+piece*.027 if closed else 1.55+(3-j)*.08+piece*.025
            key(o,frame,(x,y,z))
    lift=PARENTS['CraneLift'];slew=PARENTS['CraneSlew'];trolley=PARENTS['Trolley'];hoist=PARENTS['Hoist'];cables=PARENTS['HoistCables']
    # Beam bottom is local +.0125 above Slew; shoes top is .905.
    rest_lift=.905-2.75-.0125
    for frame,z in [(1,.43),(90,.43),(115,rest_lift),(225,rest_lift),(255,.43),(300,.43)]:key(lift,frame,(-2.12,0,z))
    for frame,a in [(1,0),(35,.42),(60,.42),(90,0),(255,0),(275,-.15),(300,0)]:key(slew,frame,rotation=(0,0,a))
    for frame,x in [(1,2.1),(35,3.5),(65,3.5),(85,1.2),(255,1.2),(280,2.1),(300,2.1)]:key(trolley,frame,(x,0,.38))
    for frame,length in [(1,.80),(25,1.40),(55,1.40),(78,.03),(265,.03),(285,.80),(300,.80)]:
        key(hoist,frame,(0,0,-length));key(cables,frame,scale=(1,1,length))
    for frame,a in [(1,0),(78,0),(88,math.pi),(255,math.pi),(265,0),(300,0)]:key(hoist,frame,rotation=(0,a,0))
    for frame,a in [(1,0),(75,0),(90,math.pi/2),(255,math.pi/2),(270,0),(300,0)]:key(PARENTS['Antenna'],frame,rotation=(a,0,0))
    for o in PARENTS.values():
        if o.animation_data and o.animation_data.action:
            o.animation_data.action.name='Ship Yard | working, stow, close, reopen'
            for fc in o.animation_data.action.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'


def camera(scene,position,target=(0,0,.45)):
    c=scene.camera;c.location=position;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=3.9


def setup_scene(draft):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16 if draft else 64;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=800 if draft else 1200;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.render.fps=30;scene.frame_start=1;scene.frame_end=300
    scene.world.color=(.11,.11,.11);scene.view_settings.view_transform='AgX'
    world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.16,.20,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();scene.camera=bpy.context.object;scene.camera.name='Gallery camera'
    for name,p,energy,size,col in [('Key',(-3,-4,6),900,5,(1,.82,.66)),('Fill',(4,-1,4),650,4,(.68,.81,1)),('Rim',(1,4,5),1000,3,(1,.67,.43))]:
        bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    camera(scene,(3.5,-5.5,4.6));return scene


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--draft',action='store_true');parser.add_argument('--no-render',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
    root=empty('PlacementRoot');root.scale=(SCALE,)*3;root['catalogue_id']='terran:ship-yard';root['footprint']='3x3';root['forward_axis']='local -Y'
    empty('StaticBase',root);empty('FabricationDeck',root);lift=empty('CraneLift',root);slew=empty('CraneSlew',lift,(0,0,2.75));trolley=empty('Trolley',slew);empty('Hoist',trolley);empty('HoistCables',trolley);empty('Antenna',slew,(.14,.04,.76))
    make_static();make_crane();make_shutters();mat,images=materials();finalize_geometry(mat);animate();scene=setup_scene(args.draft);scene.frame_set(1)
    collection=bpy.context.collection;collection.asset_mark();collection.asset_data.description='Terran PB25 high-detail industrial yard; shared game atlas, rigid stow/cover assemblies'
    mesh_objects=[o for o in scene.objects if o.type=='MESH'];tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in mesh_objects)
    assert tris<85000,tris
    assert len(mesh_objects)<=32,len(mesh_objects)
    bpy.ops.object.select_all(action='DESELECT')
    for o in list(PARENTS.values())+mesh_objects:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_animation_mode='SCENE',export_anim_scene_split_object=False,export_frame_range=True,export_frame_step=1,export_force_sampling=True,export_extras=True)
    camera(scene,(3.5,-5.5,4.6));scene.frame_set(1);scene.render.filepath='//front-quarter.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True)
    if not args.no_render:
        for view,p,frame in [('front-quarter',(3.5,-5.5,4.6),1),('rear-quarter',(-3.5,5.5,4.6),1),('top',(0,-.001,7),1),('closed',(3.5,-5.5,4.6),165),('mechanism',(3.5,-5.5,4.6),120),('crane-rest',(.7,-2.6,1.8),120)]:
            camera(scene,p);scene.frame_set(frame);scene.render.filepath=str(MEDIA/(view+'.png'));bpy.ops.render.render(write_still=True)
    if not args.no_render:
        # A technical view derived from the same meshes, never a separate nicer model.
        wire=bpy.data.materials.new('Technical shared-geometry edges');wire.use_nodes=True
        n=wire.node_tree.nodes;l=wire.node_tree.links;n.clear()
        w=n.new('ShaderNodeWireframe');w.inputs['Size'].default_value=.0011
        mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(0,0,0,1);mix.inputs[2].default_value=(.02,.65,.08,1)
        emit=n.new('ShaderNodeEmission');output=n.new('ShaderNodeOutputMaterial')
        l.new(w.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],emit.inputs[0]);l.new(emit.outputs[0],output.inputs[0])
        for o in mesh_objects:o.data.materials[0]=wire
        scene.frame_set(1);camera(scene,(3.5,-5.5,4.6));scene.render.filepath=str(MEDIA/'wireframe.png');bpy.ops.render.render(write_still=True)
        for o in mesh_objects:o.data.materials[0]=mat
    # The file is verified again after this metadata-only publication step.
    sys.path.insert(0,str(ROOT/'tools'))
    from publication_support import clean_blend,clean_png
    native_before=(OUT/'model.blend').read_bytes()
    native_after,path_strings,raw_before,raw_after=clean_blend(native_before)
    (OUT/'model.blend').write_bytes(native_after)
    for image in MEDIA.glob('*.png'):image.write_bytes(clean_png(image.read_bytes()))
    report=dict(id='terran:ship-yard',issue=225,stage='high-detail-refinement',source='Independently authored geometry and PBR maps; legacy pixels are reference-only',footprint=[3,3],blend_sha256=sha(OUT/'model.blend'),glb_sha256=sha(OUT/'model.glb'),generator_sha256=sha(Path(__file__)),surface_generator_sha256=sha(Path(__file__).with_name('shipyard_surface_maps.py')),triangles=tris,mesh_nodes=len(mesh_objects),materials=1,texture_resolution=[1024,1024],texture_maps=['albedo','orm','emission'],rigid_animation=True,skeletal_meshes=False,frame_range=[1,300],fps=30,components=COUNTS,crane_rest=dict(frame=120,beam_bottom_local_z=.905,support_top_local_z=.905),source_reference=dict(building='PB25.256',video='PB25.VID',video_frames=264),limitations=['Telescopic shutter internals and mast retraction are authored interpretations; the lowered beam rests on the platform shoes, not below its deck.','No underground hangar volume or calibrated ship attachment sockets.','Client runtime integration and gameplay trigger binding require separate validation.'],replaces_selection='sources/docs/assets/bootstrap-3d/terran-refined/pb25/model.blend',preserved_previous_variants=True,metadata_normalization=dict(path_strings=path_strings,raw_before_sha256=raw_before,raw_after_sha256=raw_after,proof='All decompressed bytes outside fixed-width absolute path strings unchanged; PNG non-image metadata stripped without re-encoding pixels'))
    (OUT/'model.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('HIGH_DETAIL_SHIPYARD_BUILT',tris,'triangles',len(mesh_objects),'mesh nodes',flush=True)

if __name__=='__main__':main()
