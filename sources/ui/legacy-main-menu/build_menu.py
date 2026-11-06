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
neon=emit('Inset neon tube',(.03,.12,1.0),1.5)
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
            z=.085+.62*math.sqrt(max(.02,1-(xx*xx+yy*yy)/(1.24**2)))
            vertices.append((xx,yy,z))
    faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    mod=obj.modifiers.new('Inset ornament thickness','SOLIDIFY');mod.thickness=.012
    bevel=obj.modifiers.new('Rounded ornament edges','BEVEL');bevel.width=.009;bevel.segments=3
    return g.finish(obj,mat,name)


def emblem_shape():
    curved_band('Central upright emblem',[(0,-1.00),(0,-.5),(0,0),(0,.5),(0,1.00)],.20,emblem)
    curved_band('Central crossbar emblem',[(-1.02,0),(-.5,0),(0,0),(.5,0),(1.02,0)],.17,emblem)
    for sign in [-1,1]:
        pts=[(sign*(.60+.38*math.cos(t)),.76*math.sin(t)) for t in [math.pi/2+i*math.pi/48 for i in range(49)]]
        curved_band('Paired curved emblem ribbon',pts,.16,emblem)
        for y in [-.76,.76]:
            curved_band('Emblem curled terminal',[(sign*.60,y),(sign*.82,y*.92),(sign*.97,y*.72)],.12,emblem)


def sphere_neon():
    ring('Inset luminous inner rim',1.255,neon,.21,.014)
    for i in range(8):
        ang=i*math.tau/8
        g.uv('Small perimeter status lens',(1.38*math.cos(ang),1.38*math.sin(ang),.17),(.016,.016,.017),neon)


def px(x,y,z=0):return ((x-207.5)/100,(240-y)/100,z)


def panel():
    outline=[(0,0),(415,0),(415,78),(408,102),(392,122),(365,139),(343,148),(359,176),(369,205),(373,236),(368,269),(357,298),(341,324),(365,337),(393,355),(408,378),(415,404),(415,480),(0,480)]
    obj=g.poly('Left console machined shell',[px(x,y)[:2] for x,y in outline],panel_metal,-.10,.12)
    # An actual hole prevents a second, baked sphere behind the independent dome.
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.99,depth=2,location=px(252,236))
    cutter=bpy.context.object
    mod=obj.modifiers.new('Independent sphere socket','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    # Geometric seams, screw recesses and scoring remain readable in the native render.
    for x,y in [(20,22),(20,455),(365,25),(365,455)]:
        xx,yy,_=px(x,y)
        g.uv('Panel fixing recess',(xx,yy,.02),(.055,.055,.016),g.dark)
        path('Worn screw slot',[(xx-.025,yy,.038),(xx+.025,yy,.038)],g.silver,.008)
    for x,y in [(55,62),(125,415),(95,340),(195,50)]:
        xx,yy,_=px(x,y)
        path('Fine surface scoring',[(xx,yy,-.024),(xx+.13,yy+.035,-.024)],g.dark,.004)


PANEL_ROUTE=[(384,0),(384,70),(380,88),(371,104),(354,115),(330,120),(285,120),(252,123),(219,134),(193,152),(174,181),(164,212),(162,239),(165,269),(179,299),(203,322),(231,336),(263,345),(300,347),(339,347),(361,357),(377,375),(384,400),(384,480)]


def rail(mat=neon,width=.012):
    points=[px(x,y,.015) for x,y in PANEL_ROUTE]
    return path('Sweeping recessed perimeter neon',points,mat,width)


def menu_button():
    # Round leading socket and long narrow label area, derived from FE_BUTTO/FE_TAG proportions.
    g.box('Menu row rail',(.30,0,-.09),(3.72,.55,.12),g.rim,.07)
    g.box('Menu row dark field',(.40,0,-.01),(3.43,.41,.08),g.well,.06)
    ring('Leading round option bezel',.34,g.silver,.02,.035,centre=(-1.47,0))
    g.uv('Leading dark option socket',(-1.47,0,-.015),(.30,.30,.06),g.well)


def menu_base():
    outline=[(95,0),(320,0),(320,480),(95,480),(95,395),(88,370),(65,347),(39,334),(39,148),(65,135),(85,113),(95,88)]
    g.poly('Right menu support plate',[((x-160)/100,(240-y)/100) for x,y in outline],panel_metal,-.10,.12)


def row_neon():
    path('Menu row neon underline',[(-1.02,-.18,.06),(1.98,-.18,.06)],neon,.012)
    ring('Menu row luminous option rim',.29,neon,.05,.014,centre=(-1.47,0))


def nameplate():
    data=bpy.data.curves.new('Separate OPENFA lettering','FONT');data.body='OPENFA';data.align_x='CENTER';data.align_y='CENTER';data.size=.67;data.extrude=.035;data.bevel_depth=.008
    obj=bpy.data.objects.new('Optional OPENFA lettering',data);scene.collection.objects.link(obj);obj.rotation_euler.z=math.pi/2
    obj.location=px(63,235,.02);g.finish(obj,g.silver,obj.name)


group('bezel',bezel);group('sphere',sphere);group('emblem',emblem_shape);group('sphere-neon',sphere_neon)
group('panel',panel);group('panel-neon',rail);group('menu-base',menu_base);group('menu-row',menu_button);group('row-neon',row_neon);group('lettering',nameplate)
THEMES={'ruby':(.80,.012,.008),'blue':(.025,.12,.90),'cyan':(.015,.65,.85),'green':(.035,.60,.12),'amber':(.90,.25,.015)}
STATES={'off':0,'dim':.12,'idle':.45,'hover':1.15,'selected':1.8,'pressed':2.8}
records=[]


def illumination(color,strength):
    for mat in [emblem,neon]:
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
    if kind=='panel':g.camera.location=(0,0,12);g.camera_data.ortho_scale=4.80;size=(830,960)
    elif kind=='base':g.camera.location=(0,0,12);g.camera_data.ortho_scale=4.80;size=(640,960)
    elif kind=='row':g.camera.location=(0,0,12);g.camera_data.ortho_scale=4.50;size=(844,192)
    else:g.camera.location=(0,0,12);g.camera_data.ortho_scale=3.20;size=(600,600)
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
g.camera.location=(0,0,12);g.camera_data.ortho_scale=3.2;scene.render.resolution_x=600;scene.render.resolution_y=600
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
(out/'renders.json').write_text(json.dumps({'blender':bpy.app.version_string,'samples':24,'source_hashes':source_hashes,'themes':THEMES,'states':STATES,'groups':names,'renders':records},indent=2)+'\n')
if source_hashes!={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}:raise RuntimeError('Source changed during render')
print('MENU_ASSETS_RENDERED',len(records),'renders')
