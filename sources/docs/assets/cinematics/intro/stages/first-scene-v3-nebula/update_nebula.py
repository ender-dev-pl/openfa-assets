"""Reference-guided procedural nebula revision of the editable 24fps opening."""
import hashlib
import json
from pathlib import Path
import shutil

import bpy

root = Path(__file__).resolve().parent
root.mkdir(parents=True,exist_ok=True)
source = Path(bpy.data.filepath).resolve()
scene = bpy.context.scene
assert scene.render.fps == 24 and scene.frame_end == 192
objects = [o for o in scene.objects if o.animation_data and o.animation_data.action]
sample_frames = [1,73,121,145,161,177,192]


def poses():
    result=[]
    for frame in sample_frames:
        scene.frame_set(frame)
        result.append([value for obj in objects for row in obj.matrix_world for value in row])
    return result


old_poses = poses()
nebula = next(obj for obj in scene.objects if obj.name.startswith('Following shot — nebula'))
old_nebula = nebula.active_material
old_visibility = next(node for node in old_nebula.node_tree.nodes if node.type=='VALUE')
for frame in range(1,121):
    scene.frame_set(frame)
    assert abs(old_visibility.outputs[0].default_value) < 1e-7
mat = bpy.data.materials.new('Nebula v3 — lavender core, dusty pink arms, blue lower cloud')
mat.use_nodes=True
nodes,links=mat.node_tree.nodes,mat.node_tree.links
nodes.clear()


def math(operation,a,b=None):
    node=nodes.new('ShaderNodeMath');node.operation=operation
    for index,value in enumerate([a] if b is None else [a,b]):
        if hasattr(value,'node'): links.new(value,node.inputs[index])
        else: node.inputs[index].default_value=value
    return node.outputs[0]


def add(items):
    result=items[0]
    for item in items[1:]:result=math('ADD',result,item)
    return result


coord=nodes.new('ShaderNodeTexCoord')
warp=nodes.new('ShaderNodeTexNoise');warp.name='Large turbulent cloud displacement'
warp.inputs['Scale'].default_value=9;warp.inputs['Detail'].default_value=4
links.new(coord.outputs['UV'],warp.inputs['Vector'])
offset=nodes.new('ShaderNodeVectorMath');offset.operation='SUBTRACT'
offset.inputs[1].default_value=(0.5,0.5,0.5);links.new(warp.outputs['Color'],offset.inputs[0])
scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY'
scale.inputs[1].default_value=(0.042,0.035,0);links.new(offset.outputs[0],scale.inputs[0])
warped=nodes.new('ShaderNodeVectorMath');warped.operation='ADD'
links.new(coord.outputs['UV'],warped.inputs[0]);links.new(scale.outputs[0],warped.inputs[1])
fine=nodes.new('ShaderNodeTexNoise');fine.name='Fine wisps and filaments'
fine.inputs['Scale'].default_value=75;fine.inputs['Detail'].default_value=4
fine.inputs['Roughness'].default_value=0.72;links.new(warped.outputs[0],fine.inputs[0])
texture=math('ADD',math('MULTIPLY',fine.outputs['Fac'],0.8),0.45)


def lobe(name,u,v,rx,ry,weight=1):
    subtract=nodes.new('ShaderNodeVectorMath');subtract.operation='SUBTRACT';subtract.label=name
    subtract.inputs[1].default_value=(u,v,0);links.new(warped.outputs[0],subtract.inputs[0])
    stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY'
    stretch.inputs[1].default_value=(1/rx,1/ry,0);links.new(subtract.outputs[0],stretch.inputs[0])
    squared=nodes.new('ShaderNodeVectorMath');squared.operation='DOT_PRODUCT'
    links.new(stretch.outputs[0],squared.inputs[0]);links.new(stretch.outputs[0],squared.inputs[1])
    return math('MULTIPLY',math('EXPONENT',math('MULTIPLY',squared.outputs['Value'],-0.5)),weight)


body=add([lobe('Main vertical body',.27,.57,.083,.205,.8),
          lobe('Lower blue plume',.29,.39,.068,.15,.65),
          lobe('Soft left boundary',.19,.62,.047,.14,.22)])
core=add([lobe('Upper bright spine',.252,.764,.027,.064,.65),
          lobe('Lavender-white core',.278,.694,.034,.073,1.0),
          lobe('Core taper',.303,.607,.029,.063,.5)])
arms=add([lobe('Hook to upper left',.197,.816,.064,.026,.65),
          lobe('Upper hook tip',.135,.839,.035,.025,.3),
          lobe('Right fork',.354,.737,.037,.035,.50),
          lobe('Right fork tip',.386,.781,.019,.035,.25),
          lobe('Dusty lower knot',.267,.346,.047,.083,.22)])
blue=lobe('Cool lower structure',.293,.43,.06,.125,.7)
shadow=math('MAXIMUM',math('SUBTRACT',1,lobe('Dark split above the bright core',.309,.825,.035,.049,.82)),0)
colors=[]
for name,density,color,strength in [
    ('Diffuse violet body',body,(.16,.084,.22),.62),
    ('Warm lavender core',core,(.55,.45,.52),.85),
    ('Dusty rose tendrils',arms,(.27,.105,.24),.65),
    ('Blue cloud base',blue,(.055,.08,.20),.60),
]:
    tint=nodes.new('ShaderNodeRGB');tint.label=name;tint.outputs[0].default_value=(*color,1)
    multiply=nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
    links.new(tint.outputs[0],multiply.inputs[1])
    links.new(math('MULTIPLY',density,strength),multiply.inputs[2]);colors.append(multiply.outputs[0])
combined=colors[0]
for color in colors[1:]:
    node=nodes.new('ShaderNodeMixRGB');node.blend_type='ADD';node.inputs[0].default_value=1
    links.new(combined,node.inputs[1]);links.new(color,node.inputs[2]);combined=node.outputs[0]
detail=nodes.new('ShaderNodeMixRGB');detail.blend_type='MULTIPLY';detail.inputs[0].default_value=1
links.new(combined,detail.inputs[1]);links.new(math('MULTIPLY',texture,shadow),detail.inputs[2])
emission=nodes.new('ShaderNodeEmission');emission.name='Reference palette and nebula brightness'
links.new(detail.outputs[0],emission.inputs['Color'])
visibility=nodes.new('ShaderNodeValue');visibility.name='Nebula reveal / 24 fps'
reveal=[(1,0),(133,0),(145,.25),(153,.65),(161,.9),(177,1),(192,1)]
for frame,value in reveal:
    visibility.outputs[0].default_value=value;visibility.outputs[0].keyframe_insert('default_value',frame=frame)
links.new(visibility.outputs[0],emission.inputs['Strength'])
transparent=nodes.new('ShaderNodeBsdfTransparent')
add_shader=nodes.new('ShaderNodeAddShader')
links.new(transparent.outputs[0],add_shader.inputs[0]);links.new(emission.outputs[0],add_shader.inputs[1])
lightpath=nodes.new('ShaderNodeLightPath')
camera_only=nodes.new('ShaderNodeMixShader')
links.new(lightpath.outputs['Is Camera Ray'],camera_only.inputs[0])
links.new(transparent.outputs[0],camera_only.inputs[1]);links.new(add_shader.outputs[0],camera_only.inputs[2])
output=nodes.new('ShaderNodeOutputMaterial');links.new(camera_only.outputs[0],output.inputs['Surface'])
nebula.data.materials.clear();nebula.data.materials.append(mat)
nebula.location=(0,0,-43);nebula.rotation_euler=(0,0,0);nebula.scale=(17.2,15.05,1)
nebula['method']='Analytic cloud lobes and multi-scale noise; no original image projected into the scene.'

# The preceding solar image must finish fading while the nebula is revealed.
def replace_fade(material_name,kind):
    material=bpy.data.materials[material_name]
    if material.node_tree.animation_data:
        material.node_tree.animation_data_clear()
    tree=material.node_tree
    if kind=='corona':
        target=next(n for n in tree.nodes if n.type=='VALUE').outputs[0]
    else:
        target=next(n for n in tree.nodes if n.type=='MIX_SHADER').inputs[0]
    keys=[(1,1),(121,1),(145,.35),(157,0),(192,0)] if kind!='moon' else [(1,1),(145,1),(157,0),(192,0)]
    for frame,value in keys:
        target.default_value=value;target.keyframe_insert('default_value',frame=frame)
    if kind!='moon':
        strength=next(n for n in tree.nodes if n.type=='EMISSION').inputs['Strength']
        for frame,value in [(1,5),(121,5),(145,1.2),(157,0),(192,0)]:
            strength.default_value=value;strength.keyframe_insert('default_value',frame=frame)


replace_fade('Corona — procedural streamers and warm halo','corona')
replace_fade('Solar photosphere — pale gold','sun')
replace_fade('Occulting body — dark cratered basalt','moon')
new_poses=poses()
error=max(abs(a-b) for old,new in zip(old_poses,new_poses) for a,b in zip(old,new))
assert error<1e-6,'Object trajectory changed'
scene.frame_set(177)
scene['nebula_revision']='v3: lavender-white core, pink arms, blue base and earlier crossfade based on legacy frames 80/88/95.'
destination=root/'opening-reconstruction-nebula.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
scene_hash=hashlib.sha256(destination.read_bytes()).hexdigest()
frames=root/'rendered-frames';frames.mkdir(exist_ok=True)
completed={}
for index in range(120):
    path=frames/f'frame-{index:06d}.png'
    shutil.copyfile(source.parent/'rendered-frames'/path.name,path)
    completed[str(index)]=hashlib.sha256(path.read_bytes()).hexdigest()
(root/'render-state.json').write_text(json.dumps({'scene_sha256':scene_hash,'completed':completed},indent=2)+'\n')
shutil.copyfile(source.parent/'opening-audio.m4a',root/'opening-audio.m4a')
report={'fps':24,'frames':192,'duration_seconds':8,'scene_sha256':scene_hash,
        'reference_frames':[80,88,95],'method':'Procedural gaussian lobes, warped FBM and additive camera-only emission',
        'source_image_projection':False,'nebula_reveal_keys':reveal,'first_frames_reused':120,
        'world_pose_error':error,'trajectory_samples':sample_frames,'animated_objects_checked':len(objects),
        'scope':'Nebula shape/color/brightness plus the preceding eclipse fade. Ship geometry and motion preserved.'}
(root/'nebula-validation.json').write_text(json.dumps(report,indent=2)+'\n')
scene.render.resolution_x=640;scene.render.resolution_y=560;scene.cycles.samples=24
scene.cycles.use_denoising=True
preview=root/'preview';preview.mkdir(exist_ok=True)
for frame in (161,177,191):
    scene.frame_set(frame);scene.render.filepath=str(preview/f'frame-{frame:03d}.png')
    bpy.ops.render.render(write_still=True)
print('NEBULA_REVISION_PREVIEW_READY',json.dumps(report),flush=True)
