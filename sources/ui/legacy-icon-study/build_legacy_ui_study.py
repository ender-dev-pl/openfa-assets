"""Blender-only UI study, referenced to original ICONS.256 and BUTTONS.256.

Usage: blender -b --factory-startup --python-exit-code 1 --python FILE -- OUTPUT
No original textures are used by this scene. PNG assembly is a separate step.
"""
import sys
import math
import json
from pathlib import Path
import bpy
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 40
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.world = bpy.data.worlds.new('Low intensity studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.09,.11,.18,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .35


def material(name, color, metal=.7, rough=.34):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    nt = mat.node_tree
    bs = nt.nodes.get('Principled BSDF')
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Roughness'].default_value = rough
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 38
    tex.inputs['Detail'].default_value = 3
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .29
    ramp.color_ramp.elements[0].color = (*(v*.40 for v in color),1)
    ramp.color_ramp.elements[1].position = .62
    ramp.color_ramp.elements[1].color = (*color,1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
    nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .15
    bump.inputs['Distance'].default_value = .012
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs[0],bs.inputs['Normal'])
    return mat


silver = material('Scratched cold steel',(.63,.67,.72))
white = material('Worn pale hull',(.82,.83,.77),.48,.34)
dark = material('Grime in joints',(.025,.031,.044),.45,.5)
blue = material('Legacy blue enamel',(.15,.16,.75),.24,.31)
gold = material('Handled gold alloy',(.75,.44,.095),.72,.3)
red = material('Dark red Sci-Tek inlay',(.45,.025,.018),.3,.4)
rim = material('Worn rim alloy',(.46,.48,.52),.8,.32)
well = material('Deep navy enamel',(.007,.009,.021),.18,.48)
well.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0
well.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
well.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.06
parts = []


def finish(obj,mat,name):
    obj.name = name
    obj.data.materials.append(mat)
    parts.append(obj)
    return obj


def bevel(obj,width=.04):
    mod = obj.modifiers.new('Rounded worn edges','BEVEL')
    mod.width=width;mod.segments=3
    obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')


def box(name,loc,scale,mat,width=.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel(o,width)
    return finish(o,mat,name)


def poly(name,xy,mat,z=.08,depth=.12):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x,y,z) for x,y in xy],[],[tuple(range(len(xy)))])
    mesh.update()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o)
    sol=o.modifiers.new('Machined thickness','SOLIDIFY');sol.thickness=depth
    bevel(o,.025)
    return finish(o,mat,name)


def uv(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=loc)
    o=bpy.context.object;o.scale=scale
    bpy.ops.object.shade_smooth()
    return finish(o,mat,name)


def tube(name,a,b,r,mat,r2=None):
    vec=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=r,radius2=r if r2 is None else r2,depth=vec.length,location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object;o.rotation_euler=vec.to_track_quat('Z','Y').to_euler()
    bevel(o,.018)
    return finish(o,mat,name)


def arrow():
    poly('Blue right arrow',[(-.17,-.08),(.79,-.08),(.79,-.24),(1.10,0),(.79,.24),(.79,.08),(-.17,.08)],blue,-.1,.09)


def missile():
    # ICONS/017: diagonal pale missile, no flame, blue arrow to its right.
    arrow()
    start=Vector((-.83,-.65,.12));end=Vector((.43,.79,.12));v=end-start
    tube('Missile pale cylindrical body',start+v*.18,start+v*.78,.115,white)
    tube('Steel collar',start+v*.20,start+v*.29,.125,silver)
    tube('Tapered nose',start+v*.78,end,.115,silver,.014)
    tube('Dark engine throat',start+v*.10,start+v*.18,.075,dark)
    poly('Tail fins',[(-.93,-.62),(-.72,-.35),(-.56,-.35),(-.58,-.72),(-.72,-.80),(-.72,-.58)],white,.13,.12)


def craft(cx,cy,s):
    def p(x,y,z=.10):return (cx+x*s,cy+y*s,z)
    poly('Triangular fleet hull',[(cx+x*s,cy+y*s) for x,y in [(-.58,.12),(.46,.58),(.15,-.67),(-.03,-.22)]],white,.08,.10)
    tube('Raised fuselage spine',p(-.09,-.24,.18),p(.34,.44,.18),.085*s,silver,.026*s)
    uv('Dark recessed cockpit',p(.12,.12,.24),(.06*s,.12*s,.035),dark)
    tube('Small engine',p(-.08,-.28,.08),p(-.16,-.42,.08),.065*s,dark)


def fleet():
    # ICONS/016: two white ships, one large and one small, right arrow.
    arrow();craft(-.28,-.18,1.05);craft(-.52,.64,.53)


def funds():
    # ICONS/021: one large round gold coin and four blue horizontal bars.
    for y in [-.65,-.28,.09,.46]:
        box('Blue accounting bar',(.60,y,-.08),(.60,.25,.10),blue,.018)
    tube('Coin milled edge',(-.34,-.10,.02),(-.34,-.10,.22),.65,gold)
    tube('Raised coin face',(-.34,-.10,.22),(-.34,-.10,.26),.55,gold)
    for i in range(36):
        a=i*math.tau/36
        o=box('Worn radial milling',(-.34+.622*math.cos(a),-.10+.622*math.sin(a),.245),(.05,.018,.025),silver,.006)
        o.rotation_euler.z=a
    # Embossed rim catches highlights, but no invented currency symbol.
    bpy.ops.mesh.primitive_torus_add(major_radius=.52,minor_radius=.025,location=(-.34,-.10,.28))
    finish(bpy.context.object,gold,'Embossed coin rim')


def construction():
    # ICONS/010: blue double-ended wrench beside a pale diamond/craft.
    x=-.65
    box('Spanner shaft',(x,0,.09),(.16,.94,.13),blue)
    poly('Upper open spanner',[(x-.36,.61),(x-.23,.89),(x-.20,.48),(x+.12,.48),(x+.21,.88),(x+.34,.62),(x+.23,.27),(x-.22,.27)],blue,.11,.13)
    poly('Lower open spanner',[(x-.22,-.25),(x+.21,-.25),(x+.34,-.60),(x+.20,-.87),(x+.13,-.48),(x-.16,-.48),(x-.23,-.88),(x-.35,-.62)],blue,.11,.13)
    poly('Diamond silhouette',[(.42,.91),(.98,.20),(.43,-.87),(-.05,.20)],white,.06,.13)
    poly('Raised central facet',[(.42,.80),(.45,.20),(.43,-.75),(.10,.20)],silver,.15,.12)
    box('Dark transverse slot',(.45,.19,.29),(.72,.11,.06),dark,.012)
    tube('Central ring',(.45,.14,.29),(.45,.14,.35),.12,dark)
    tube('Central pale insert',(.45,.14,.35),(.45,.14,.37),.055,white)
    box('Left tip',(-.04,.19,.12),(.12,.17,.10),silver,.015)
    box('Right tip',(1.00,.19,.12),(.12,.17,.10),silver,.015)


def scitek():
    # BUTTONS/002: silver oval badge, dark/red SCI-TEK lettering.
    uv('Sci-Tek oval silver badge',(0,0,0),(1.75,.52,.16),rim)
    uv('Sci-Tek brushed inner plate',(0,0,.07),(1.61,.41,.12),silver)
    data=bpy.data.curves.new('SCI-TEK engraved label','FONT')
    data.body='SCI-TEK';data.align_x='CENTER';data.align_y='CENTER'
    data.size=.46;data.extrude=.009;data.bevel_depth=.004
    o=bpy.data.objects.new('SCI-TEK red inlay',data);scene.collection.objects.link(o)
    o.location=(0,0,.205);o.scale.x=1.25;finish(o,red,o.name)


def button():
    uv('Oval button outer metal',(0,0,-.28),(1.90,1.30,.19),rim)
    uv('Polished inner metal lip',(0,0,-.20),(1.76,1.17,.14),silver)
    uv('Navy recessed button well',(0,0,-.12),(1.60,1.04,.12),well)


camera_data=bpy.data.cameras.new('Orthographic icon camera')
camera_data.type='ORTHO';camera_data.ortho_scale=4.5
camera=bpy.data.objects.new('Orthographic icon camera',camera_data)
scene.collection.objects.link(camera);camera.location=(0,0,12)
scene.camera=camera
for name,loc,energy,size in [('Key upper left',(-3,4,6),480,3),('Cool rim',(3,1,4),240,2),('Fill',(-1,-3,5),70,4)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
    light=bpy.data.objects.new(name,data);scene.collection.objects.link(light);light.location=loc
    light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()

groups={}
for name,make in [('missile',missile),('fleet',fleet),('funds',funds),('construction',construction),('scitek',scitek),('button',button)]:
    parts=[];make();groups[name]=list(parts)
    for obj in parts:obj.hide_render=True


def render(name,objects):
    for obj in scene.objects:
        if obj.type in {'MESH','CURVE','FONT'}:obj.hide_render=obj not in objects
    scene.render.resolution_x=384;scene.render.resolution_y=304;scene.render.resolution_percentage=100
    scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)


for name,objects in groups.items():
    render(name,objects)
for obj in scene.objects:
    if obj.type in {'MESH','CURVE','FONT'}:obj.hide_render=False
# Arrange the editable source in separate collections; transforms stay local.
for name,objects in groups.items():
    col=bpy.data.collections.new(name);scene.collection.children.link(col)
    for obj in objects:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        col.objects.link(obj)
        obj.hide_render=name!='missile'
        obj.hide_set(name!='missile')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'legacy-ui-study.blend'))
# Independent import proof is rendered with the same production camera/lights.
for obj in scene.objects:
    obj.hide_set(False)
    obj.select_set(obj.type in {'MESH','CURVE','FONT'})
bpy.ops.export_scene.gltf(filepath=str(OUT/'legacy-ui-study.glb'),use_selection=True,export_format='GLB',export_apply=True)
group_names={name:[o.name for o in objects] for name,objects in groups.items()}
for objects in groups.values():
    for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(OUT/'legacy-ui-study.glb'))
imported=[o for o in scene.objects if o not in before and o.type=='MESH']
proof={}
for name,names in group_names.items():
    objects=[o for o in imported if o.name in names]
    if len(objects)!=len(names):raise RuntimeError(f'Incomplete GLB group {name}: {len(objects)}/{len(names)}')
    render(name+'-imported',objects)
    proof[name]={'source_objects':len(names),'imported_objects':len(objects)}
(OUT/'runtime-proof.json').write_text(json.dumps({'blender':bpy.app.version_string,'groups':proof},indent=2)+'\n')
print('UI_STUDY_RENDERED',OUT)
