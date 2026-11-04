"""Render legacy-referenced frontend sphere/chrome and separate neon layers in Blender."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',required=True,type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
scene=g.scene;scene.cycles.samples=24;scene.view_settings.view_transform='AgX'
scene.render.resolution_percentage=100
groups={}


def group(name,make):
    g.parts=[];make();groups[name]=list(g.parts)
    for o in g.parts:o.hide_render=True


def path(name,points,mat,r=.025):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=r;data.bevel_resolution=4
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,xyz in zip(spline.points,points):p.co=(*xyz,1)
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    return g.finish(obj,mat,name)


def ring(name,r,mat,z=0,width=.025,centre=(0,0),sx=1,sy=1):
    return path(name,[(centre[0]+sx*r*math.cos(i*math.tau/192),centre[1]+sy*r*math.sin(i*math.tau/192),z) for i in range(193)],mat,width)


def emit(name,color,strength):
    mat=g.material(name,color,.15,.3)
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=strength
    return mat


emblem=emit('Emblem luminous ruby',(.75,.012,.008),.8)
neon=emit('Contextual panel neon',(.03,.12,1.0),3.0)
dome_neon=emit('Fixed ruby dome trim',(.60,.008,.006),.35)
for node in emblem.node_tree.nodes:
    if node.type=='BUMP':node.inputs['Strength'].default_value=.025;node.inputs['Distance'].default_value=.001
    if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=180
    if node.type=='VALTORGB':node.color_ramp.elements[0].color=(.48,.006,.004,1)
smoke=g.material('Used smoked blue glass',(.009,.012,.050),.4,.17)
panel_metal=g.material('Used fine-grain console alloy',(.30,.32,.34),.65,.56)
for node in panel_metal.node_tree.nodes:
    if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=360
    if node.type=='BUMP':node.inputs['Distance'].default_value=.002
    if node.type=='VALTORGB':node.color_ramp.elements[0].color=(.20,.22,.24,1)
bs=smoke.node_tree.nodes.get('Principled BSDF');bs.inputs['Coat Weight'].default_value=.55
# Red centre / navy edge is procedural, not a texture from the original.
nt=smoke.node_tree;tex=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tex.outputs['Generated'],sep.inputs[0])
sq=[]
for channel in ['X','Y']:
    sub=nt.nodes.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.5;nt.links.new(sep.outputs[channel],sub.inputs[0])
    mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(sub.outputs[0],mul.inputs[0]);nt.links.new(sub.outputs[0],mul.inputs[1]);sq.append(mul)
add=nt.nodes.new('ShaderNodeMath');add.operation='ADD'
for i,node in enumerate(sq):nt.links.new(node.outputs[0],add.inputs[i])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.008;ramp.color_ramp.elements[0].color=(.13,.003,.006,1)
ramp.color_ramp.elements[1].position=.18;ramp.color_ramp.elements[1].color=(.004,.006,.028,1)
nt.links.new(add.outputs[0],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])


def bezel():
    for radius,width,mat,z in [(1.43,.055,g.silver,.10),(1.35,.035,g.rim,.13),(1.29,.025,g.dark,.19),(1.23,.015,g.silver,.22)]:
        ring('Concentric machined dome bezel',radius,mat,z,width)
    for i in range(4):
        ang=math.pi/4+i*math.pi/2
        g.uv('Recessed bezel fixing',(1.38*math.cos(ang),1.38*math.sin(ang),.15),(.035,.035,.015),g.dark)


def sphere():g.uv('Convex smoked glass dome',(0,0,.04),(1.24,1.24,.62),smoke)


def curved_band(name,points,width,mat):
    # Place the authored ribbon just above the convex lens surface.
    dense=[]
    for a,b in zip(points,points[1:]):
        steps=max(1,math.ceil(math.dist(a,b)/.025))
        dense.extend([(a[0]+(b[0]-a[0])*t/steps,a[1]+(b[1]-a[1])*t/steps) for t in range(steps)])
    points=dense+[points[-1]]
    vertices=[]
    for i,(x,y) in enumerate(points):
        j=min(i+1,len(points)-1);k=max(0,i-1)
        dx=points[j][0]-points[k][0];dy=points[j][1]-points[k][1];length=math.hypot(dx,dy)
        nx=-dy/length*width/2;ny=dx/length*width/2
        for xx,yy in [(x+nx,y+ny),(x-nx,y-ny)]:
            z=.10
            vertices.append((xx,yy,z))
    faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    mod=obj.modifiers.new('Inset ornament thickness','SOLIDIFY');mod.thickness=.032
    bevel=obj.modifiers.new('Rounded ornament edges','BEVEL');bevel.width=.009;bevel.segments=3
    return g.finish(obj,mat,name)


def emblem_shape():
    first=len(g.parts)
    curved_band('Central upright emblem',[(0,-1.00),(0,-.5),(0,0),(0,.5),(0,1.00)],.20,emblem)
    curved_band('Central crossbar emblem',[(-1.02,0),(-.5,0),(0,0),(.5,0),(1.02,0)],.17,emblem)
    for sign in [-1,1]:
        def bezier(a,b,c,d):
            return [tuple((1-t)**3*a[j]+3*(1-t)**2*t*b[j]+3*(1-t)*t*t*c[j]+t**3*d[j] for j in [0,1]) for t in [i/48 for i in range(48)]]
        top=bezier((sign*.98,.55),(sign*.89,.69),(sign*.78,.76),(sign*.60,.76))
        arc=[(sign*(.60+.38*math.cos(t)),.76*math.sin(t)) for t in [math.pi/2+i*math.pi/96 for i in range(96)]]
        bottom=bezier((sign*.60,-.76),(sign*.78,-.76),(sign*.89,-.69),(sign*.98,-.55))+[(sign*.98,-.55)]
        curved_band('Continuous smooth emblem lobe',top+arc+bottom,.16,emblem)
    # Union the complete planar ornament before bending it. No intersecting strips
    # or separate terminal seams remain on the finished convex surface.
    pieces=g.parts[first:]
    bpy.ops.object.select_all(action='DESELECT')
    for obj in pieces:obj.select_set(True)
    bpy.context.view_layer.objects.active=pieces[0]
    for obj in pieces:
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join()
    obj=bpy.context.object;obj.name='Continuous welded convex emblem'
    remesh=obj.modifiers.new('Watertight ornament union','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.006;remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=obj.modifiers.new('Smooth continuous silhouette','SMOOTH');smooth.factor=.55;smooth.iterations=3
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    for vertex in obj.data.vertices:
        x,y,z=vertex.co
        vertex.co.z=.085+.62*math.sqrt(max(.02,1-(x*x+y*y)/(1.24**2)))+(z-.10)
    for face in obj.data.polygons:face.use_smooth=True
    g.parts[first:]=[obj]
    # Assert a single connected component and a closed two-face edge manifold.
    adjacency=[[] for _ in obj.data.vertices];edges={}
    for edge in obj.data.edges:
        a,b=edge.vertices;adjacency[a].append(b);adjacency[b].append(a)
    seen={0};stack=[0]
    while stack:
        for nxt in adjacency[stack.pop()]:
            if nxt not in seen:seen.add(nxt);stack.append(nxt)
    for face in obj.data.polygons:
        ids=list(face.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
    if len(seen)!=len(obj.data.vertices) or any(n!=2 for n in edges.values()):raise RuntimeError('Emblem must be a single watertight surface')
    obj['connected_components']=1;obj['nonmanifold_edges']=0


def sphere_neon():
    ring('Inset luminous inner rim',1.255,dome_neon,.21,.014)
    for i in range(8):
        ang=i*math.tau/8
        g.uv('Small perimeter status lens',(1.38*math.cos(ang),1.38*math.sin(ang),.17),(.016,.016,.017),dome_neon)


def px(x,y,z=0):return ((x-320)/100,(240-y)/100,z)


def panel():
    outline=[(0,0),(640,0),(640,480),(0,480)]
    obj=g.poly('Left console machined shell',[px(x,y)[:2] for x,y in outline],panel_metal,-.10,.12)
    # The two delivered panel slices are cut from this one continuous render.
    # Common geometry, UVs and lighting make every overlap pixel identical.
    for width,mat,z in [(.075,g.silver,.006),(.053,g.dark,.020),(.035,g.rim,.033)]:
        path('Smooth registered recessed neon channel',[px(x,y,z) for x,y in PANEL_ROUTE],mat,width)
    # Geometric seams, screw recesses and scoring remain readable in the native render.
    for x,y in [(20,22),(20,455),(365,25),(365,455)]:
        xx,yy,_=px(x,y)
        g.uv('Panel fixing recess',(xx,yy,.02),(.055,.055,.016),g.dark)
        path('Worn screw slot',[(xx-.025,yy,.038),(xx+.025,yy,.038)],g.silver,.008)
    for x,y in [(55,62),(125,415),(95,340),(195,50)]:
        xx,yy,_=px(x,y)
        path('Fine surface scoring',[(xx,yy,-.024),(xx+.13,yy+.035,-.024)],g.dark,.004)


def sample_line(a,b):
    count=max(2,math.ceil(math.dist(a,b)/.35))
    return [(a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count) for i in range(count)]


def sample_arc(cx,cy,r,start,end):
    count=max(16,math.ceil(abs(end-start)*r/.35))
    return [(cx+r*math.cos(start+(end-start)*i/count),cy+r*math.sin(start+(end-start)*i/count)) for i in range(count)]


PANEL_ROUTE=sample_line((384,0),(384,76))+sample_arc(342,76,42,0,math.pi/2)+sample_line((342,118),(252,118))+sample_arc(252,236,118,-math.pi/2,-3*math.pi/2)+sample_line((252,354),(342,354))+sample_arc(342,396,42,-math.pi/2,0)+sample_line((384,396),(384,480))+[(384,480)]


def rail(mat=neon,width=.025):
    points=[px(x,y,.071) for x,y in PANEL_ROUTE]
    return path('Sweeping recessed perimeter neon',points,mat,width)


def menu_button():
    # Round leading socket and long narrow label area, derived from FE_BUTTO/FE_TAG proportions.
    g.box('Menu row rail',(.30,0,-.09),(3.72,.55,.12),g.rim,.07)
    g.box('Menu row dark field',(.40,0,-.01),(3.43,.41,.08),g.well,.06)
    ring('Leading round option bezel',.34,g.silver,.02,.035,centre=(-1.47,0))
    g.uv('Leading dark option socket',(-1.47,0,-.015),(.30,.30,.06),g.well)


def menu_base():
    g.poly('Common full-canvas support plate',[px(x,y)[:2] for x,y in [(0,0),(640,0),(640,480),(0,480)]],panel_metal,-.10,.12)


def row_neon():
    path('Menu row neon underline',[(-1.02,-.18,.06),(1.98,-.18,.06)],neon,.012)
    ring('Menu row luminous option rim',.29,neon,.05,.014,centre=(-1.47,0))


def nameplate():
    data=bpy.data.curves.new('Separate OPENFA lettering','FONT');data.body='OPENFA';data.align_x='CENTER';data.align_y='CENTER';data.size=.67;data.extrude=.035;data.bevel_depth=.008
    obj=bpy.data.objects.new('Optional OPENFA lettering',data);scene.collection.objects.link(obj);obj.rotation_euler.z=math.pi/2
    obj.location=px(63,235,.02);g.finish(obj,g.silver,obj.name)


group('bezel',bezel);group('sphere',sphere);group('emblem',emblem_shape);group('sphere-neon',sphere_neon)
group('panel',panel);group('panel-neon',rail);group('menu-base',menu_base);group('menu-row',menu_button);group('row-neon',row_neon);group('lettering',nameplate)
from mathutils import Matrix
for name in ['bezel','sphere','emblem','sphere-neon']:
    for obj in groups[name]:obj.matrix_world=Matrix.Translation(px(252,236)) @ Matrix.Diagonal((.66,.66,.66,1)) @ obj.matrix_world
THEMES={'ruby':(.80,.012,.008),'blue':(.025,.12,.90),'cyan':(.015,.65,.85),'green':(.035,.60,.12),'amber':(.90,.25,.015)}
STATES={'off':0,'dim':.12,'idle':.45,'hover':1.15,'selected':1.8,'pressed':2.8}
records=[]


def illumination(color,strength):
    # Context changes the console neon, never the red dome emblem.
    emblem.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.25+strength*.18
    for mat in [neon]:
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(*color,1)
        bs.inputs['Emission Strength'].default_value=strength
        mat.diffuse_color=(*color,1)
        # Base hue is controlled in the procedural material ramp as well.
        for node in mat.node_tree.nodes:
            if node.type=='VALTORGB':
                node.color_ramp.elements[0].color=(*(c*.4 for c in color),1)
                node.color_ramp.elements[1].color=(*color,1)


def render(name,names,kind='sphere'):
    objects={o for n in names for o in groups[n]}
    for obj in scene.objects:
        if obj.type in {'MESH','CURVE','FONT'}:obj.hide_render=obj not in objects
    if kind in ['panel','base']:g.camera.location=(0,0,12);g.camera_data.ortho_scale=6.40;size=(1280,960)
    elif kind=='row':g.camera.location=(0,0,12);g.camera_data.ortho_scale=4.50;size=(844,192)
    else:g.camera.location=(*px(252,236)[:2],12);g.camera_data.ortho_scale=2.00;size=(600,600)
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'file':name+'.png','groups':names,'kind':kind,'size':list(size)})


illumination(THEMES['ruby'],.45)
for name in groups:render('layer-'+name,[name],'base' if name=='menu-base' else 'panel' if name in ['panel','panel-neon','lettering'] else 'row' if name in ['menu-row','row-neon'] else 'sphere')
for theme,color in THEMES.items():
    for state,strength in STATES.items():
        illumination(color,strength)
        render(f'sphere-{theme}-{state}',['bezel','sphere','emblem','sphere-neon'])
        render(f'emission-{theme}-{state}',['emblem','sphere-neon'])
        render(f'rail-{theme}-{state}',['panel-neon'],'panel')
        render(f'row-{theme}-{state}',['menu-row','row-neon'],'row')

# Save the actual authored source, before replacing objects with independent GLB imports.
illumination(THEMES['ruby'],.45)
for name,objects in groups.items():
    col=bpy.data.collections.new(name);scene.collection.children.link(col)
    for obj in objects:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        col.objects.link(obj);obj.hide_render=name not in ['bezel','sphere','emblem','sphere-neon']
        obj.hide_set(obj.hide_render)
g.camera.location=(*px(252,236)[:2],12);g.camera_data.ortho_scale=2.0;scene.render.resolution_x=600;scene.render.resolution_y=600
bpy.ops.wm.save_as_mainfile(filepath=str(out/'main-menu.blend'))
names={n:[o.name for o in objects] for n,objects in groups.items()}
for obj in scene.objects:obj.hide_set(False);obj.select_set(obj.type in {'MESH','CURVE','FONT'})
bpy.ops.export_scene.gltf(filepath=str(out/'main-menu.glb'),use_selection=True,export_format='GLB',export_apply=True)
for objects in groups.values():
    for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(out/'main-menu.glb'))
imported={o.name:o for o in scene.objects if o not in before and o.type=='MESH'}
for name,source_names in names.items():
    if not all(n in imported for n in source_names):raise RuntimeError('GLB lost '+name)
    groups[name]=[imported[n] for n in source_names]
for name in groups:render('imported-'+name,[name],'base' if name=='menu-base' else 'panel' if name in ['panel','panel-neon','lettering'] else 'row' if name in ['menu-row','row-neon'] else 'sphere')
(out/'renders.json').write_text(json.dumps({'blender':bpy.app.version_string,'samples':24,'source_hashes':source_hashes,'themes':THEMES,'states':STATES,'groups':names,'renders':records,'registration':{'canvas':[640,480],'panel_crop':[0,0,415,480],'base_crop':[320,0,640,480],'base_anchor':[320,0],'sphere_anchor':[152,136],'sphere_center':[252,236]},'emblem':{'connected_components':1,'nonmanifold_edges':0,'context_color_invariant':True}},indent=2)+'\n')
if source_hashes!={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}:raise RuntimeError('Source changed during render')
print('MENU_ASSETS_RENDERED',len(records),'renders')
