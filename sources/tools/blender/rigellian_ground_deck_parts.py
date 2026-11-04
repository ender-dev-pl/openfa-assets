"""Independent RI10 fixed deck and rigid telescopic paired cover study."""
import math
import bmesh
import bpy
from mathutils import Vector
from build_openfa_assets import box,cylinder,beam,finish,material
from rigellian_construction_parts import tidy as original_tidy

RX=.84
RY=.66
HINGE_Z=1.02


def tidy(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
    bm.to_mesh(obj.data);bm.free();original_tidy(obj)


def subtract(obj,cutter):
    for target in [obj,cutter]:
        bpy.context.view_layer.objects.active=target
        for mod in list(target.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Actual manufactured cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)


def palette():
    return dict(body=material('RI10 | worn green casting',(.12,.26,.19),.65,.54),
        edge=material('RI10 | rubbed green edge alloy',(.26,.40,.31),.75,.44),
        gold=material('RI10 | aged brass structure',(.40,.27,.09),.78,.48),
        dark=material('RI10 | recessed graphite',(.018,.028,.032),.55,.62),
        steel=material('RI10 | worn internal steel',(.17,.22,.25),.80,.50),
        red=material('RI10 | red recessed indicators',(.42,.015,.009),.35,.38))


def oval(name,rx,ry,z,depth,surface):
    obj=cylinder(name,(0,0,z),rx,depth,surface,vertices=96)
    obj.scale.y=ry/rx;bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return obj


def cover(sign,surface):
    # Closed D-shaped solid. Local assembly origin stays at the outer edge; no scale animation.
    points=[(0,-RY),(0,RY)]
    for i in range(1,49):
        phi=math.pi/2+i*math.pi/48;points.append((sign*(-RX*math.cos(phi)),RY*math.sin(phi)))
    # Build consistently ordered polygon via angle sort, independently for each half.
    centre=Vector((sign*RX*.40,0))
    points=sorted({(round(x,9),round(y,9)) for x,y in points},key=lambda p:math.atan2(p[1]-centre.y,p[0]-centre.x))
    n=len(points);verts=[(x-sign*RX,y,z) for z in [-.006,.006] for x,y in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new('RI10 independently authored cover solid');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('RI10 left cover shell' if sign<0 else 'RI10 right cover shell',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,surface,.008);return obj


def d_field(name,sign,inner,radius,height,z,depth,surface):
    # Flat centre-facing edge and curved outer edge, observed in catalogue highlight.
    points=[(sign*inner,-height),(sign*inner,height)]
    for i in range(1,49):
        phi=math.pi/2-i*math.pi/48
        points.append((sign*(inner+radius*math.cos(phi)),height*math.sin(phi)))
    centre=Vector((sign*(inner+radius*.4),0))
    points=sorted({(round(x,9),round(y,9)) for x,y in points},key=lambda p:math.atan2(p[1]-centre.y,p[0]-centre.x))
    count=len(points);vertices=[(x,y,level) for level in [z-depth/2,z+depth/2] for x,y in points]
    faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh=bpy.data.meshes.new(name+' closed profile');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    return obj


def parent_preserving(obj,parent):
    world=obj.matrix_world.copy();obj.parent=parent;obj.matrix_world=world


def build():
    m=palette();body=oval('RI10 fixed oval body',1.32,1.02,.62,.74,m['body'])
    bm=bmesh.new();bm.from_mesh(body.data)
    vertical=[edge for edge in bm.edges if abs(edge.verts[0].co.z-edge.verts[1].co.z)>.5]
    bmesh.ops.subdivide_edges(bm,edges=vertical,cuts=17,use_grid_fill=True)
    for vertex in bm.verts:
        phi=math.atan2(vertex.co.y/1.02,vertex.co.x/1.32);z=vertex.co.z+.62
        delta=math.atan2(math.sin(phi+2.2),math.cos(phi+2.2))
        dent=.008*math.exp(-2*((delta/.12)**2+((z-.55)/.12)**2))
        vertex.co.x-=dent*math.cos(phi);vertex.co.y-=dent*math.sin(phi)
    bm.to_mesh(body.data);bm.free()
    cutter=oval('Temporary deck aperture',RX+.035,RY+.035,.72,1.35,m['dark']);subtract(body,cutter);tidy(body)
    # Actual below-ground shaft: no grille or shallow landing floor across its mouth.
    vertices=[];count=128
    for z in [-2.0,.97]:
        for rx,ry in [(.94,.76),(.86,.68)]:
            vertices.extend((rx*math.cos(i*math.tau/count),ry*math.sin(i*math.tau/count),z) for i in range(count))
    faces=[]
    for i in range(count):
        j=(i+1)%count
        faces.extend([(i,j,j+2*count,i+2*count),(i+count,i+3*count,j+3*count,j+count),
                      (i,i+count,j+count,j),(i+2*count,j+2*count,j+3*count,i+3*count)])
    mesh=bpy.data.meshes.new('RI10 deep shaft closed wall');mesh.from_pydata(vertices,[],faces);mesh.update()
    wall=bpy.data.objects.new('RI10 shaft wall below ground',mesh);bpy.context.collection.objects.link(wall)
    finish(wall,wall.name,m['dark'],0);tidy(wall)
    oval('RI10 shaft distant dark bottom',.91,.73,-1.99,.06,m['dark'])
    rim=oval('RI10 green aperture coaming',RX+.09,RY+.09,.97,.12,m['edge'])
    cutter=oval('Temporary coaming opening',RX+.018,RY+.018,.97,.50,m['dark']);subtract(rim,cutter);tidy(rim)
    for i,x in enumerate([-.145,0,.145]):
        y=.68*math.sqrt(1-(x/.86)**2)-.006
        box(f'RI10 shaft wall vertical guide {i}',(x,y,-.35),(.035,.022,2.50),m['steel'],.004)
    for sign in [-1,1]:
        box('RI10 interior indicator retaining case',(sign*.48,.57,.60),(.16,.10,.12),m['steel'],.014)
        box('RI10 interior recessed red indicator',(sign*.48,.515,.60),(.115,.014,.085),m['red'],.004)
        # Broad brass load-bearing front and rear legs are visible in the source.
        # Source front gold regions occupy X=12..17 and 26..33 in the 44px body.
        # Their centred spacing is about 0.34 of total width, not the former 0.73.
        vertices=[]
        for z,cx,width,cy,depth in [(.03,sign*.62,.25,-.98,.30),(.74,sign*.48,.32,-.93,.25)]:
            vertices.extend([(cx-width/2,cy-depth/2,z),(cx+width/2,cy-depth/2,z),
                             (cx+width/2,cy+depth/2,z),(cx-width/2,cy+depth/2,z)])
        faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        mesh=bpy.data.meshes.new('RI10 front splayed buttress solid');mesh.from_pydata(vertices,[],faces);mesh.update()
        front=bpy.data.objects.new('RI10 front splayed brass buttress',mesh);bpy.context.collection.objects.link(front)
        finish(front,front.name,m['gold'],.022)
        box('RI10 front brass foot flange',(sign*.62,-.98,.045),(.33,.35,.09),m['gold'],.012)
        obj=box('RI10 rear brass load-bearing buttress',(sign*.98,.66,.37),(.22,.29,.68),m['gold'],.035)
        obj.rotation_euler.y=sign*.11
        box('RI10 rear brass foot flange',(sign*1.01,.66,.05),(.30,.35,.10),m['gold'],.018)
        cassette=box('RI10 enclosed side cover cassette',(sign*1.10,0,1.04),(.50,1.42,.12),m['body'],.02)
        pocket=box('Temporary cassette internal clearance',(sign*.65,0,1.055),(1.32,1.38,.06),m['dark'],.006)
        subtract(cassette,pocket);tidy(cassette)
        for y in [-.61,.61]:
            box('RI10 fixed cassette guide rail',(sign*1.065,y,1.028),(.43,.025,.012),m['steel'],.003)
    notch=box('Temporary front stair access',(0,-.99,.19),(.80,.44,.40),m['dark'],.025)
    subtract(body,notch);tidy(body)
    for i in range(3):
        box(f'RI10 front access step {i}',(0,-1.01+i*.10,.10+i*.095),(.56,.18,.12),m['body'],.018)
        box(f'RI10 worn step nose {i}',(0,-1.095+i*.10,.155+i*.095),(.53,.025,.020),m['edge'],.004)
    for sign in [-1,1]: box('RI10 rear brass shoulder cap',(sign*.53,.85,.99),(.29,.20,.11),m['gold'],.018)
    box('RI10 right equipment mast foundation',(1.17,.82,.69),(.21,.24,.48),m['gold'],.023)
    beam('RI10 right green mast',(1.17,.82,.80),(1.17,.82,1.23),.045,m['body'])
    beam('RI10 mast bent top',(1.17,.82,1.20),(1.02,.82,1.25),.045,m['body'])
    cylinder('RI10 mast terminal',(1.02,.82,1.25),.060,.080,m['edge'],vertices=24)
    roots=[];segments=[]
    for sign in [-1,1]:
        root=bpy.data.objects.new('CoverLeft' if sign<0 else 'CoverRight',None);bpy.context.collection.objects.link(root)
        root.location=(sign*RX,0,HINGE_Z);root['motion']='Inferred lift and two-stage side retraction; hidden mechanism not observed'
        leaf=cover(sign,m['body']);leaf.parent=root
        cutter=d_field('Temporary shallow D cover inset',sign,.09,.63,.45,HINGE_Z+.025,.050,m['dark'])
        bpy.context.view_layer.update();subtract(leaf,cutter);tidy(leaf)
        panel=d_field('RI10 recessed green cover field',sign,.11,.59,.425,HINGE_Z+.002,.006,m['edge'])
        bpy.context.view_layer.update();parent_preserving(panel,root)
        for inner in [True,False]:
            segment=bpy.data.objects.new(root.name+('Inner' if inner else 'Outer'),None);bpy.context.collection.objects.link(segment);segment.parent=root
            segment['stroke']=sign*(.88 if inner else .46)
            segment.location.z=.008 if inner else -.008
            for original in [leaf,panel]:
                part=original.copy();part.data=original.data.copy();bpy.context.collection.objects.link(part)
                part.name=original.name+(' inner segment' if inner else ' outer segment')
                cutter=box('Temporary segment clipping volume',(sign*(.21 if inner else .63),0,HINGE_Z),(.416,2,1),m['dark'],0)
                bpy.context.view_layer.update();bpy.context.view_layer.objects.active=part
                for mod in list(part.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
                modifier=part.modifiers.new('Solid manufactured telescopic segment','BOOLEAN');modifier.operation='INTERSECT';modifier.solver='EXACT';modifier.object=cutter
                bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True);tidy(part)
                part.parent=segment
            segments.append(segment)
        bpy.data.objects.remove(leaf,do_unlink=True);bpy.data.objects.remove(panel,do_unlink=True)
        roots.append(root)
    return roots,segments
