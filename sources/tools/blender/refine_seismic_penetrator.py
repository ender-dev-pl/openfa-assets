"""PB21 third study from paletted catalogue rotation and ST24 technical wireframe."""
import hashlib
import json
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.noise import noise

ROOT = Path(__file__).resolve().parents[3]
REL = Path('docs/assets/reconstruction/seismic-penetrator/pb21')
SOURCE = ROOT/'sources/docs/assets/bootstrap-3d/terran-refined/pb21/model.blend'
OUTPUT = ROOT/'sources'/REL
MEDIA = ROOT/'gallery/media'/REL
TEXTURES = ROOT/'sources/materials/reconstruction/seismic-penetrator/pb21'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def material(name, colour, metal=.45, rough=.7, texture=False):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*colour,1);mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*colour,1)
    shader.inputs['Metallic'].default_value=metal;shader.inputs['Roughness'].default_value=rough
    if texture:
        size=384;image=bpy.data.images.new(name+' baked wear',width=size,height=size)
        pixels=[];rng=random.Random(181)
        for y in range(size):
            for x in range(size):
                u=x/size;v=y/size
                broad=noise(Vector((u*8,v*8,2.1)))
                fine=noise(Vector((u*145,v*145,1.3)))
                stain=max(0,noise(Vector((u*19,v*19,8.7)))-.12)
                value=.90+broad*.21+fine*.11-stain*.28+rng.uniform(-.025,.025)
                pixels.extend([max(0,min(1,c*value)) for c in colour]+[1])
        image.pixels.foreach_set(pixels);image.filepath_raw=str(TEXTURES/(name.split('|')[-1].strip().replace(' ','-')+'.png'))
        image.file_format='PNG';image.save();image.pack()
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
        mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    return mat


def mesh(name,vertices,faces,mat):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj);obj.data.materials.append(mat)
    uv=data.uv_layers.new(name='Wear UV')
    for polygon in data.polygons:
        axis=max(range(3),key=lambda i:abs(polygon.normal[i]));axes=[i for i in range(3) if i!=axis]
        for loop in polygon.loop_indices:
            p=data.vertices[data.loops[loop].vertex_index].co
            uv.data[loop].uv=(p[axes[0]]*.32+.5,p[axes[1]]*.32+.5)
    return obj


def bevel(obj,width=.012):
    mod=obj.modifiers.new('Small used edge radius','BEVEL');mod.width=width;mod.segments=2
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def box(name,centre,size,mat):
    x,y,z=centre;a,b,c=[v/2 for v in size]
    return bevel(mesh(name,[(x+sx*a,y+sy*b,z+sz*c) for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]],
        [(0,2,3,1),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)],mat),min(size)/7)


def rod(name,a,b,r,mat,vertices=10):
    direction=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=direction.length,location=(Vector(a)+Vector(b))/2)
    obj=bpy.context.object;obj.name=name;obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
    for p in obj.data.polygons:p.use_smooth=len(p.vertices)==4
    return obj


def lathe(name,profile,mat,centre=(0,0),start=0,span=math.tau,count=96):
    closed=abs(span-math.tau)<.001;steps=count if closed else count+1
    points=[(centre[0]+r*math.cos(start+i*span/count),centre[1]+r*math.sin(start+i*span/count),z) for z,r in profile for i in range(steps)]
    faces=[]
    for j in range(len(profile)-1):
        for i in range(count):
            nxt=(i+1)%steps
            faces.append((j*steps+i,j*steps+nxt,(j+1)*steps+nxt,(j+1)*steps+i))
    if not closed:
        faces.extend([tuple(j*steps for j in reversed(range(len(profile)))),tuple(j*steps+steps-1 for j in range(len(profile)))])
    obj=mesh(name,points,faces,mat)
    for p in obj.data.polygons:p.use_smooth=len(p.vertices)==4
    return obj


def roof_z(x,y):
    return 1.09+min(0,y+.22)*.31+.018*(1-(x/1.1)**2)


def roof_width(y):
    return 1.10 if y>=-.45 else math.sqrt(max(.0001,1.10**2-(y+.45)**2))


def roof_surface(name,x0,x1,y0,y1,mat,lift=.004):
    vertices=[(x,y,roof_z(x,y)+lift) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
    return mesh(name,vertices,[(0,1,2,3)],mat)


def lattice(name,a,b,mat):
    a=Vector(a);b=Vector(b);length=(b-a).length;axis=(b-a).normalized();bottom=.09;top=.58
    for z in [bottom,top]:rod(name+' frame',a+Vector((0,0,z)),b+Vector((0,0,z)),.017,mat)
    for sign in [-1,1]:
        slope=sign*.80
        for k in range(-8,18):
            offset=k*.24
            hits=[]
            for t,z in [(0,offset),(length,slope*length+offset),((bottom-offset)/slope,bottom),((top-offset)/slope,top)]:
                if -.0001<=t<=length+.0001 and bottom-.0001<=z<=top+.0001:
                    point=a+axis*t+Vector((0,0,z))
                    if not any((point-h).length<.001 for h in hits):hits.append(point)
            if len(hits)==2:rod(name+' diamond brace',hits[0],hits[1],.0085,mat,6)
    for t in [0,length/2,length]:rod(name+' upright',a+axis*t+Vector((0,0,bottom)),a+axis*t+Vector((0,0,top)),.016,mat)


def construct(m):
    # Wireframe shows a rounded machine bell within the shell, and a slotted
    # lower ring. Red in ST24 is an annotation colour, not red material.
    centre=(0,-.40)
    profile=[(.025,.76),(.055,.91),(.13,1.00),(.31,1.00),(.41,.96),(.46,.86)]
    lathe('Exposed grey violet drilling drum',profile,m['drum'],centre,start=-math.pi/2+.09,span=math.tau-.18,count=128)
    lathe('Lower drum dark belt',[(.16,1.002),(.225,1.002)],m['dark'],centre,start=-math.pi/2+.09,span=math.tau-.18,count=128)
    bell=lathe('Rounded internal survey machine bell',[(.34,.89),(.50,.89),(.69,.82),(.86,.68),(.98,.50),(1.01,.16)],m['drum'],centre)
    for vertex in bell.data.vertices:
        vertex.co.z=min(vertex.co.z,roof_z(vertex.co.x,vertex.co.y)-.16)
    # An actual inset sector, following the drum profile, forms the service gap.
    lathe('Front lower drum recessed radial slot',[(z,r-.085) for z,r in profile],m['dark'],centre,start=-math.pi/2-.09,span=.18,count=8)
    for x in [-.54,.54]:
        y=-1.30;rod('Nose shell standoff',(x,y,.38),(x,y,roof_z(x,y)-.085),.026,m['steel'])
    for x in [-1.02,1.02]:
        lathe('Rear cylindrical foundation pier',[(.015,.145),(.055,.16),(.83,.16),(.90,.14)],m['hull'],(x,.84),count=48)
        lathe('Pier foot wear band',[(.02,.161),(.10,.161)],m['dark'],(x,.84),count=48)
    lattice('Rear open bracing',(-1.02,.94,0),(1.02,.94,0),m['lattice'])
    for sign in [-1,1]:
        lattice('Side open bracing '+str(sign),(sign*1.055,-.18,0),(sign*1.055,.84,0),m['lattice'])
    # Main roof is a compound sloped shell with a semicircular nose, not a box.
    rows=[-1.549+i*(2.499/44) for i in range(45)]+[-.45,-.22]
    rows=sorted(set(rows));n=48;verts=[]
    for y in rows:
        w=roof_width(y)
        for j in range(n+1):
            x=-w+2*w*j/n;z=roof_z(x,y)
            # Small local dents, below silhouette scale.
            z-=.006*math.exp(-((x-.78)**2+(y+.68)**2)/.014)
            verts.append((x,y,z))
    faces=[(i*(n+1)+j,i*(n+1)+j+1,(i+1)*(n+1)+j+1,(i+1)*(n+1)+j) for i in range(len(rows)-1) for j in range(n)]
    shell=mesh('Rounded compound roof and nose',verts,faces,m['hull'])
    solid=shell.modifiers.new('Shell plate thickness','SOLIDIFY');solid.thickness=.065
    bpy.context.view_layer.objects.active=shell;bpy.ops.object.modifier_apply(modifier=solid.name)
    bevel(shell,.009)
    # Retain a shallow upper skirt; the lower rear remains visibly open.
    edges=[(-1.1,.95),(1.1,.95),(1.1,-.45)]
    edges += [(1.1*math.cos(a),-.45+1.1*math.sin(a)) for a in [-i*math.pi/40 for i in range(1,41)]]
    edges += [(-1.1,.95)]
    for i,(p,q) in enumerate(zip(edges,edges[1:])):
        low=lambda v:.58 if v[1]>=-.22 else roof_z(*v)-.15
        v=[(*p,low(p)),(*q,low(q)),(*q,roof_z(*q)-.055),(*p,roof_z(*p)-.055)]
        mesh('Upper shell edge skirt '+str(i),v,[(0,1,2,3)],m['hull'])
    # Rear deck hatches are visibly unequal, silver-violet and shallow.
    for index,(x,y,r) in enumerate([(-.40,.47,.175),(.39,.47,.235)]):
        z=roof_z(x,y)
        lathe('Hatch '+str(index)+' recessed flange',[(z+.003,r*1.11),(z+.026,r*1.11),(z+.033,r)],m['dark'],(x,y),count=64)
        lathe('Hatch '+str(index)+' shallow domed lid',[(z+.027,r),(z+.055,r*.95),(z+.095,r*.70),(z+.116,r*.32),(z+.12,0)],m['drum'],(x,y),count=64)
        for a in [0,math.pi]:
            box('Hatch rim catch',(x+r*math.cos(a),y+r*math.sin(a),z+.04),(.028,.055,.018),m['steel'])
    for x,y in [(-1.02,.84),(1.02,.84)]:
        for dx,h in [(-.035,.25),(.035,.32)]:
            rod('Short rear survey aerial',(x+dx,y,.90),(x+dx,y,1.09+h),.006,m['dark'],6)
    # ST24 cutaway identifies this nose fork as the head of a long probe shaft.
    px,py=-.46,-1.21;z=roof_z(px,py)
    rod('Front geophysical probe shaft',(px,py,.065),(px,py,z+.12),.022,m['steel'],16)
    lathe('Probe guide collar',[(z-.025,.065),(z+.025,.065)],m['steel'],(px,py),count=24)
    for dx in [-.045,.045]:rod('Pale probe fork tine',(px+dx,py,z+.07),(px+dx,py,z+.19),.013,m['pale'],10)
    rod('Probe fork bridge',(px-.045,py,z+.07),(px+.045,py,z+.07),.013,m['pale'],10)
    lathe('Internal precision drill head',[(.04,0),(.11,.075),(.20,.033),(.30,.033)],m['steel'],(px,py),count=24)
    # Confirmed roof paint follows the sloped plate rather than floating above it.
    for row in range(3):
        for col in range(2):
            x=.08+col*.24;y=-1.04+row*.20
            roof_surface('Faded red roof marking',x,x+.215,y,y+.105,m['red'])
    for x in [.64,.73]:roof_surface('Pale nose roof stripe',x,x+.036,-1.23,-.42,m['stripe'])
    # Thin joints and use marks, without inventing the previous five heavy ribs.
    for sign in [-1,1]:
        for i in range(12):
            y=-.40+i*.108;x=sign*1.06
            roof_surface('Edge abrasion',x-.002,x+.002,y,y+.018,m['scuff'],.005)
    rng=random.Random(21)
    for i in range(65):
        y=rng.uniform(-1.42,.90);w=roof_width(y);x=rng.uniform(-w*.93,w*.93)
        length=rng.uniform(.012,.06);width=rng.uniform(.001,.003)
        roof_surface('Roof fine service scratch',x,x+width,y,min(.94,y+length),m['scuff'],.005)
    # Small internal drive connections are visible through the rear frame.
    rod('Internal survey drive cross shaft',(-.70,.35,.30),(.70,.35,.30),.045,m['dark'],16)
    for x in [-.60,.60]:
        lathe('Internal drive coupling',[(.22,.12),(.28,.12),(.34,.08)],m['steel'],(x,.35),count=32)


def configure_camera(direction):
    scene=bpy.context.scene;camera=scene.camera;points=[]
    for obj in scene.objects:
        if obj.type=='MESH':points.extend(obj.matrix_world@v.co for v in obj.data.vertices)
    centre=(Vector([min(p[i] for p in points) for i in range(3)])+Vector([max(p[i] for p in points) for i in range(3)]))/2
    direction=Vector(direction).normalized();camera.location=centre+direction*12
    camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO'
    bpy.context.view_layer.update();local=[camera.matrix_world.inverted()@p for p in points]
    camera.data.ortho_scale=max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.17


VIEWS={'front-quarter':(6,-10,7),'rear-quarter':(-6,10,6),'front':(0,-10,4),'side':(10,0,3),'top':(0,-.001,12)}


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True);TEXTURES.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    m=dict(hull=material('PB21 | ochre shell',(.34,.255,.12),texture=True),
        drum=material('PB21 | grey violet machinery',(.205,.205,.255),.5,.53,True),
        lattice=material('PB21 | pale lattice',(.49,.44,.33),.55,.75),
        steel=material('PB21 | used steel',(.35,.37,.38),.70,.58),
        dark=material('PB21 | recessed machinery',(.035,.040,.045),.5,.8),
        pale=material('PB21 | probe ceramic',(.65,.64,.55),.20,.65),
        red=material('PB21 | faded red paint',(.35,.075,.035),.15,.85,True),
        stripe=material('PB21 | pale roof stripe',(.62,.48,.24),.2,.8),
        scuff=material('PB21 | exposed worn edge',(.40,.36,.28),.65,.65))
    construct(m)
    root=bpy.data.objects.new('PlacementRoot',None);scene.collection.objects.link(root)
    root['catalogue_id']='terran:seismic-penetrator';root['footprint_width']=root['footprint_height']=3
    for obj in scene.objects:
        if obj.type=='MESH':obj.parent=root
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100
    if scene.render.engine=='CYCLES':scene.cycles.samples=48
    scene.frame_start=scene.frame_end=1;scene.frame_set(1)
    configure_camera(VIEWS['front-quarter'])
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'),export_format='GLB',use_selection=True,export_extras=True,export_apply=True,export_animations=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    for name,direction in VIEWS.items():
        configure_camera(direction);scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    meta=dict(issue=181,id='terran:seismic-penetrator',culture='terran',footprint=[3,3],
        source_study=str(SOURCE.relative_to(ROOT)),source_blend_sha256=sha(SOURCE),
        blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),generator_sha256=sha(Path(__file__)),
        reference='sources/docs/reconstruction/models/seismic-penetrator-reference.json',
        features=['Compound curved nose shell','Exposed slotted grey-violet drum and internal machine bell','Open diamond rear/side bracing and cylindrical corner piers','Unequal shallow roof hatches','Short aerials and fork-topped geophysical probe continuing to an internal drill head','Sloped roof paint, worn edges, mottled casing, scratches and small dents'],
        animation='Static building study. ST24 technical camera/highlighting sequence is reference evidence, not an invented gameplay loop.',
        material_policy='Packed original authored wear textures embedded in GLB; legacy images used only as shape/colour references, never mapped onto the model',
        inferred=['Absolute dimensions and unseen internal connections','Use-related wear positions and intensity'],
        views=list(VIEWS),blender=bpy.app.version_string)
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('PB21_REFINED_SOURCE_EXPORTED',len([o for o in scene.objects if o.type=='MESH']),flush=True)


if __name__=='__main__':main()
