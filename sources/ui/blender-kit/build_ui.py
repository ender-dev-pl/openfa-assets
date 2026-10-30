"""Blender-authored UI kit. Run Blender --background --python build_ui.py -- --output PATH.

Creates editable geometry, independently imports its GLB, and renders transparent
symbols and physical panel/button states. PNG packaging is a separate explicit step.
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parent)
parser.add_argument('--samples', type=int, default=24)
parser.add_argument('--proof-only', action='store_true', help='Refresh sources and GLB proof without rerendering PNG deliverables')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
args.source.mkdir(parents=True, exist_ok=True)
random.seed(176)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'None'
scene.world = bpy.data.worlds.new('Studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.19, .24, .30, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .45


def material(name, colour, metallic=.6, roughness=.4, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Base Color'].default_value = (*colour, 1)
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*colour, 1)
        bsdf.inputs['Emission Strength'].default_value = emission
    # Restrained grime and small abrasions are authored on all new metal parts.
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 95
    noise.inputs['Detail'].default_value = 2
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[v * .72 for v in colour], 1)
    ramp.color_ramp.elements[1].color = (*colour, 1)
    links.new(noise.outputs['Fac'], ramp.inputs[0])
    links.new(ramp.outputs[0], bsdf.inputs['Base Color'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .10
    bump.inputs['Distance'].default_value = .008
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs[0], bsdf.inputs['Normal'])
    return mat


silver = material('Used satin alloy', (.46, .49, .48))
ivory = material('Worn ceramic markings', (.76, .72, .59), .25, .4)
blue = material('Cobalt glass indicators', (.045, .19, .48), .4, .28, .35)
amber = material('Amber status lens', (.9, .40, .065), .3, .3, .4)
dark = material('Graphite recessed enamel', (.018, .028, .036), .35, .48)
black = material('Dark display glass', (.003, .008, .013), .1, .45)
disabled = material('Inactive oxidized alloy', (.15, .17, .17), .4, .65)
red = material('Warning lens', (.56, .045, .025), .2, .35)
roots = []
active = None


def root(name, x, y):
    global active
    active = bpy.data.objects.new(name, None)
    scene.collection.objects.link(active)
    active.location = (x, y, 0)
    roots.append(active)
    return active


def finish(obj, mat, name):
    obj.name = name
    obj.parent = active
    obj.data.materials.append(mat)
    return obj


def plate(x, y, width, height, z=.04, depth=.10, mat=silver, bevel=.045):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    obj = bpy.context.object
    obj.scale = (width, height, depth)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = obj.modifiers.new('Machined edge radius', 'BEVEL')
    mod.width = min(bevel, depth * .45, width * .12, height * .12)
    mod.segments = 3
    obj.modifiers.new('Weighted machining normals', 'WEIGHTED_NORMAL')
    return finish(obj, mat, 'Bevelled plate')


def line(points, mat=ivory, width=.085, z=.18):
    curve = bpy.data.curves.new('Raised metal trace', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = width
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, xy in zip(spline.points, points):
        p.co = (xy[0], xy[1], z, 1)
    obj = bpy.data.objects.new('Raised trace', curve)
    scene.collection.objects.link(obj)
    return finish(obj, mat, 'Raised trace')


def ring(x=0, y=0, radius=.65, mat=ivory, start=0, end=math.tau, width=.075, z=.18):
    return line([(x + radius * math.cos(start + (end-start)*i/64),
                  y + radius * math.sin(start + (end-start)*i/64)) for i in range(65)], mat, width, z)


def polygon(points, mat=ivory, z=.12):
    mesh = bpy.data.meshes.new('Solid pictogram')
    mesh.from_pydata([(x, y, z) for x, y in points], [], [tuple(range(len(points)))])
    obj = bpy.data.objects.new('Extruded pictogram', mesh)
    scene.collection.objects.link(obj)
    solid = obj.modifiers.new('Cast metal thickness', 'SOLIDIFY')
    solid.thickness = .10
    bevel = obj.modifiers.new('Worn edge radius', 'BEVEL')
    bevel.width = .025
    bevel.segments = 3
    return finish(obj, mat, 'Solid pictogram')


def disc(x=0, y=0, radius=.20, mat=amber, z=.16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(x,y,z))
    obj = bpy.context.object
    obj.scale = (radius, radius, .055)
    bpy.ops.object.shade_smooth()
    return finish(obj, mat, 'Status lens')


def arrow(direction=0, mat=ivory, x=0, y=0, scale=1):
    points = [(-.7,-.16),(.10,-.16),(.10,-.43),(.74,0),(.10,.43),(.10,.16),(-.7,.16)]
    c, s = math.cos(direction), math.sin(direction)
    polygon([(x+scale*(a*c-b*s), y+scale*(a*s+b*c)) for a,b in points], mat)


def ship(x=0, y=0, scale=1, mat=ivory):
    polygon([(x+a*scale,y+b*scale) for a,b in [(0,.85),(-.60,-.55),(-.18,-.36),(0,-.65),(.18,-.36),(.60,-.55)]],mat)
    line([(x,y-.40*scale),(x,y+.45*scale)],blue,.06*scale,.26)


def person(x=0, y=0, scale=1):
    disc(x,y+.32*scale,.22*scale,ivory)
    polygon([(x-.42*scale,y-.55*scale),(x-.35*scale,y-.13*scale),(x,y+.02*scale),
             (x+.35*scale,y-.13*scale),(x+.42*scale,y-.55*scale)],ivory)


def document():
    plate(0,0,1.15,1.5,.08,.13,ivory)
    for y in [-.38,-.08,.22]: line([(-.36,y),(.32,y)],blue,.045,.23)


def gear():
    ring(radius=.53, width=.13)
    for i in range(8):
        angle=i*math.tau/8
        obj=plate(.68*math.cos(angle),.68*math.sin(angle),.25,.25,.15,.16)
        obj.rotation_euler.z=angle
    disc(radius=.2,mat=blue)


def icon(index):
    if index in (0,1,4,42,43,60):
        ring(radius=.7,mat=blue)
        if index in (0,60):
            ring(radius=.38,mat=ivory)
            line([(-.7,0),(.7,0)],ivory,.045)
            line([(0,-.7),(0,.7)],ivory,.045)
            disc(.43,.38,.11,amber)
        elif index==1:
            polygon([(-.63,-.20),(-.45,.48),(.25,.65),(.72,.05),(.31,-.60),(-.30,-.58)],silver)
            disc(-.15,.2,.17,dark,.25)
        else:
            line([(-.95,0),(.95,0)],ivory,.055)
            line([(0,-.95),(0,.95)],ivory,.055)
            disc(.36,.30,.12,amber)
    elif index in (2,3,41,52,53):
        if index==2:
            ship(-.5,-.20,.55);ship(.5,-.20,.55);ship(0,.4,.55)
        else:
            ship(0,.1,.9)
            if index in (52,53):arrow(math.pi/2 if index==52 else -math.pi/2,amber,.70,-.1,.5)
            if index==41:line([(-.85,.6),(-.85,-.7),(.85,-.7),(.85,.6)],blue,.055)
    elif index in (5,38):
        if index==5:
            for y in [-.4,-.08,.24]:
                plate(0,y,1.2,.25,.14,.14,amber)
                line([(-.35,y),(.35,y)],ivory,.025,.25)
        else:polygon([(0,.85),(-.55,.15),(-.33,-.65),(.32,-.65),(.6,.15)],blue)
    elif index in (6,54,55):
        line([(-.6,-.65),(.5,.5)],silver,.16)
        ring(.5,.5,.28,ivory,start=.3,end=5.2,width=.12)
        if index in (6,55):
            line([(-.55,.60),(.6,-.55)],amber,.12)
            plate(-.55,.60,.65,.25,.22,.16,ivory)
    elif index in (7,9,50,51):
        for y in [-.5,0,.5]: line([(-.75,y),(.75,y)],blue,.055)
        for x in [-.75,0,.75]:line([(x,-.5),(x,.5)],ivory,.055)
        if index in (9,51):disc(.36,.25,.14,amber)
        if index==50:line([(-.7,-.75),(0,-.92),(.7,-.75)],amber,.075)
    elif index in (8,16,19,30,31,62,63):
        direction={8:math.pi/2,16:math.pi,19:math.pi/2,30:math.pi,31:0,62:math.pi/2,63:-math.pi/2}[index]
        arrow(direction)
        if index==19:line([(-.7,-.55),(-.7,.1),(.7,.1),(.7,-.55),(-.7,-.55)],blue,.06)
    elif index==10:
        polygon([(-.28,.8),(.28,.8),(.28,.1),(.70,-.65),(-.7,-.65),(-.28,.1)],ivory)
        line([(-.49,-.37),(.47,-.37)],blue,.11,.25)
        disc(.1,-.24,.10,amber,.30)
    elif index==11:
        arrow(0,amber,0,.32,.8);arrow(math.pi,ivory,0,-.32,.8)
    elif index in (12,40):
        plate(0,-.55,.75,.18,.10,.10,silver)
        line([(0,-.55),(0,.5)],ivory,.09)
        ring(0,.5,.25,blue,start=0,end=math.pi)
        ring(0,.5,.6,amber,start=0,end=math.pi,width=.055)
        if index==40:plate(-.6,-.1,.30,.7,.15,.12,blue);plate(.6,-.1,.3,.7,.15,.12,blue)
    elif index in (13,36):
        person(0,0,.85)
        if index==36:person(-.57,-.1,.55);person(.57,-.1,.55)
    elif index in (14,57):
        document()
        if index==57:line([(0,-.6),(0,.6)],amber,.06,.30)
    elif index in (15,22):gear()
    elif index in (17,18):
        if index==17:line([(-.70,0),(-.2,-.5),(.7,.6)],ivory,.13)
        else:line([(-.55,-.55),(.55,.55)],ivory,.13);line([(-.55,.55),(.55,-.55)],amber,.13)
    elif index==20:
        plate(0,0,1.4,1.4,.10,.14,silver)
        plate(0,.35,.8,.45,.23,.10,blue)
        plate(0,-.38,.8,.45,.23,.10,ivory)
    elif index==21:
        plate(0,-.1,1.05,1.2,.10,.15,silver)
        line([(-.7,.6),(.7,.6)],amber,.09)
        for x in [-.28,0,.28]:line([(x,-.55),(x,.35)],dark,.05,.23)
    elif index==23:
        ring(radius=.7,mat=blue)
        disc(0,.43,.10,ivory)
        line([(0,.05),(0,-.4)],ivory,.13)
    elif index in (24,25):
        if index==24:polygon([(-.5,-.7),(.65,0),(-.5,.7)],amber)
        else:plate(-.32,0,.30,1.4,.15,.15,ivory);plate(.32,0,.30,1.4,.15,.15,ivory)
    elif index in (26,27,28,29):
        if index in (28,29):
            ring(-.15,.20,.48,blue)
            line([(.2,-.15),(.70,-.7)],ivory,.12)
            line([(-.42,.20),(.12,.20)],amber,.065)
            if index==28:line([(-.15,-.07),(-.15,.47)],amber,.065)
        else:
            line([(-.65,0),(.65,0)],ivory,.13)
            if index==27:line([(0,-.65),(0,.65)],amber,.13)
    elif index==32:polygon([(.2,.85),(-.6,-.1),(-.04,-.1),(-.2,-.85),(.6,.2),(.06,.2)],amber)
    elif index==33:
        disc(radius=.18,mat=amber)
        for i in range(4):
            a=i*math.pi/2
            polygon([(.2*math.cos(a),.2*math.sin(a)),(.78*math.cos(a+.4),.78*math.sin(a+.4)),
                     (.62*math.cos(a+1),.62*math.sin(a+1))],ivory)
    elif index==34:
        polygon([(-.65,-.5),(-.55,.35),(.1,.8),(.65,.65),(.5,-.1),(-.1,-.5)],ivory)
        line([(-.7,-.65),(.4,.4)],blue,.055,.26)
    elif index==35:polygon([(0,.85),(-.6,-.15),(-.4,-.65),(0,-.8),(.4,-.65),(.6,-.15)],blue)
    elif index==37:
        ring(radius=.72,mat=amber)
        disc(radius=.16,mat=ivory)
        for i in range(3):
            a=i*math.tau/3
            polygon([(.29*math.cos(a),.29*math.sin(a)),(.65*math.cos(a-.4),.65*math.sin(a-.4)),
                     (.65*math.cos(a+.4),.65*math.sin(a+.4))],ivory)
    elif index==39:
        polygon([(-.18,-.6),(-.18,.5),(0,.85),(.18,.5),(.18,-.6),(.45,-.8),(.25,-.8),
                 (0,-.58),(-.25,-.8),(-.45,-.8)],ivory)
        line([(-.17,.12),(.17,.12)],amber,.08,.26)
    elif index in (44,45):
        plate(0,-.25,1.1,.85,.10,.18,amber)
        ring(0,.35,.38,ivory,start=0 if index==44 else .5,end=math.pi)
        line([(-.38,.35),(-.38,-.15)],ivory,.075)
        if index==44:line([(.38,.35),(.38,-.15)],ivory,.075)
        disc(0,-.25,.1,dark,.27)
    elif index in (46,47):
        polygon([(-.65,-.28),(-.25,-.28),(.25,-.7),(.25,.7),(-.25,.28),(-.65,.28)],ivory)
        if index==46:ring(.3,0,.45,blue,start=-.9,end=.9)
        else:line([(.42,-.3),(.85,.3)],amber,.08);line([(.42,.3),(.85,-.3)],amber,.08)
    elif index in (48,49):
        line([(-.75,.25),(-.75,.65),(-.3,.65)],ivory)
        line([(.3,.65),(.75,.65),(.75,.25)],ivory)
        line([(-.75,-.25),(-.75,-.65),(-.3,-.65)],blue)
        line([(.3,-.65),(.75,-.65),(.75,-.25)],blue)
    elif index==56:
        for a in range(4):arrow(a*math.pi/2,amber,0,0,.8)
        disc(radius=.26,mat=ivory,z=.3)
    elif index==58:
        for x,y in [(0,.55),(-.6,-.45),(.6,-.45)]:
            disc(x,y,.2,blue)
            line([(0,0),(x,y)],ivory,.055)
    elif index==59:
        ring(radius=.65,mat=blue,start=2.1,end=7.3,width=.12)
        line([(0,.85),(0,.10)],amber,.13)
    elif index==61:
        plate(0,0,1.8,1.0,.10,.16,silver)
        for y in [-.25,.02,.29]:
            for x in [-.63,-.32,0,.32,.63]:plate(x,y,.18,.12,.25,.08,blue,.015)
    else:raise ValueError(index)


for i in range(64):
    root(f'icon-{i:02}', (i%8-3.5)*2.6, (3.5-i//8)*2.6)
    icon(i)

icons = list(roots)
panel_specs = {}
for area,w,h in [('gameplay',48,40),('frontend',211,48),('control',30,30)]:
    for state in ['normal','selected','pressed','disabled','hover']:
        r=root(f'{area}-{state}', (len(roots)-64)*3, -14)
        width,height=w/20,h/20
        metal=disabled if state=='disabled' else silver
        plate(0,0,width,height,0,.18,metal,.07)
        plate(0,0,width-.20,height-.20,.13,.12,
              blue if state in ('selected','hover') else dark,.045)
        if state=='pressed':plate(0,0,width-.30,height-.30,.20,.12,black,.035)
        for x in [-width/2+.18,width/2-.18]:disc(x,-height/2+.18,.045,amber if state!='disabled' else disabled,.27)
        panel_specs[r.name]=(w,h)

for name,w,h in [('panel',192,144),('gameplay-edge',531,60),('gameplay-menu-edge',109,200),
                 ('gameplay-menu-base',558,480),('gameplay-catalogue-tile',96,96),
                 ('frontend-edge',320,480),('frontend-base',320,480),
                 ('quick-screen',196,218),('quick-header',196,24),('quick-rail',82,64),
                 ('quick-column',56,64),('quick-corner',56,44),('quick-vertical',24,218)]:
    r=root(name,(len(roots)-64)*3,-30)
    wunit,hunit=w/20,h/20
    plate(0,0,wunit,hunit,0,.18,silver,.07)
    plate(0,0,wunit-.28,hunit-.28,.13,.12,black if 'screen' in name else dark,.045)
    for x in [-wunit/2+.18,wunit/2-.18]:
        for y in [-hunit/2+.18,hunit/2-.18]:disc(x,y,.045,silver,.24)
    panel_specs[name]=(w,h)


def lamp(name,location,power,colour,size):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=power;data.color=colour;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj


lights=[lamp('Broad key',(-3,4,8),1000,(1,.91,.78),5),
        lamp('Cool fill',(4,-1,6),500,(.65,.83,1),4),
        lamp('Rim',(-1,-4,5),400,(1,.70,.40),3)]
camera_data=bpy.data.cameras.new('Orthographic UI camera')
camera_data.type='ORTHO'
camera=bpy.data.objects.new('Orthographic UI camera',camera_data)
scene.collection.objects.link(camera)
scene.camera=camera
camera.location=(0,0,30)
camera_data.ortho_scale=24
scene.render.resolution_x=scene.render.resolution_y=1024
scene.render.resolution_percentage=100


def visible(selected):
    for r in roots:
        for obj in r.children_recursive:obj.hide_render=r not in selected


visible(icons)
bpy.ops.wm.save_as_mainfile(filepath=str((args.source/'ui-kit.blend').resolve()))
# Export evaluated meshes/curves so the editable source can be checked separately.
bpy.ops.object.select_all(action='DESELECT')
export_copies=[]
export_materials={}
for r in icons:
    for obj in r.children_recursive:
        mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        copy=bpy.data.objects.new(obj.name+' export mesh',mesh)
        scene.collection.objects.link(copy)
        copy.matrix_world=obj.matrix_world
        for slot in copy.material_slots:
            source=slot.material
            if source.name not in export_materials:
                mat=source.copy()
                bsdf=mat.node_tree.nodes.get('Principled BSDF')
                for link in list(bsdf.inputs['Base Color'].links):mat.node_tree.links.remove(link)
                for link in list(bsdf.inputs['Normal'].links):mat.node_tree.links.remove(link)
                bsdf.inputs['Base Color'].default_value=source.diffuse_color
                export_materials[source.name]=mat
            slot.material=export_materials[source.name]
        copy.select_set(True)
        export_copies.append(copy)
bpy.ops.export_scene.gltf(filepath=str((args.source/'ui-kit.glb').resolve()),use_selection=True,
                          export_format='GLB',export_apply=True)
for copy in export_copies:bpy.data.objects.remove(copy,do_unlink=True)


def render(name, selected, width, height, scale, centre):
    visible(selected)
    camera.location=(centre[0],centre[1],30)
    camera_data.ortho_scale=scale
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    for light,location in zip(lights,[(-3,4,8),(4,-1,6),(-1,-4,5)]):
        light.location=(centre[0]+location[0],centre[1]+location[1],location[2])
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('UI_RENDERED',name,flush=True)


render('source-contact',icons,1024,1024,22,(0,0))
if not args.proof_only:
    for i,r in enumerate(icons):render(f'icon-{i:02}',[r],192,192,2.2,r.location)
    for name,(w,h) in panel_specs.items():
        r=next(r for r in roots if r.name==name)
        render(name,[r],w*4,h*4,max(w,h)/20,r.location)

# Independent GLB scene: only imported exported geometry plus the same studio rig.
visible([])
bpy.ops.import_scene.gltf(filepath=str((args.source/'ui-kit.glb').resolve()))
camera.location=(0,0,30);camera_data.ortho_scale=22
scene.render.resolution_x=scene.render.resolution_y=1024
for light,location in zip(lights,[(-3,4,8),(4,-1,6),(-1,-4,5)]):light.location=location
scene.render.filepath=str(out/'imported-contact.png')
bpy.ops.render.render(write_still=True)
(args.source/'ui-kit.json').write_text(json.dumps({
    'schema_version':1,'generator':'build_ui.py','blender':bpy.app.version_string,
    'view':'AgX / None / sRGB','symbols':64,'panel_states':panel_specs,
    'reference':'ed-openfa-game/docs/assets/issue-627/menu-comparison.png, left Legacy FA panels',
    'materials':'Satin alloy, graphite enamel, cobalt glass, amber lenses; restrained procedural wear',
    'validation':'Actual Cycles CPU renders and independent GLB import; see gallery/media/ui/blender-kit',
},indent=2)+'\n',encoding='utf-8',newline='\n')
print('UI_KIT_COMPLETE',flush=True)
