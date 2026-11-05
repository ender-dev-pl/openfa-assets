"""Full authored technical presentation with legacy caption intervals and 423-frame clock.

Camera/pose interpolation is authored from inspected source phases, not recovered
original 3D camera data. The client consumes explicit per-frame camera/material
metadata because glTF cannot portably animate orthographic scale or material hue.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Euler
source=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;root=bpy.data.objects['AntiVirusRotor'];root.animation_data_clear()
model=json.loads((source.parent/'model.json').read_text());components=model['components']
clock_path=source.parent/'material-clock.json';clock=json.loads(clock_path.read_text());assert clock['frame_count']==423
import_samples=clock['independent_import_samples']
wires={name:bpy.data.objects[name+' technical wire'] for name in components}
for name,names in components.items():
    for objname in names:bpy.data.objects[objname].hide_render=True
for o in wires.values():o.hide_render=False
s.render.resolution_x=224;s.render.resolution_y=224;s.cycles.samples=8;s.render.film_transparent=False;s.view_settings.view_transform='Standard'
s.world.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=0
s.frame_start=1;s.frame_end=423;s.render.fps=15
whole=Vector(model['whole_information_local_target']);whole_scale=model['whole_information_ortho_scale'];timeline=[];materials={}
for name,o in wires.items():
    mat=o.data.materials[0].copy();mat.name=name+' animated technical hue';o.data.materials[0]=mat;materials[name]=mat.node_tree.nodes.get('Emission')
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
def envelope(f):
    if f<42:return 0
    if f<66:return smooth((f-42)/24)
    if f<106:return 1
    if f<130:return 1-smooth((f-106)/24)
    return 0
phases=[dict(x) for x in model['phases']]

for f in range(423):
    group_index=min(2,f//141);phase=phases[group_index];local=f%141;zoom=envelope(local)
    # Original films demonstrate oblique orientation, settled component closeups,
    # then return to the whole device. Explicit authored poses retain that order.
    orbit=math.sin(local/140*math.tau)*(1-zoom)
    initial=model['whole_information_rotation_euler'];root.rotation_euler=Euler([initial[i]*(1-zoom)+phase['closeup_rotation_euler'][i]*zoom+math.radians([12,10,-15][i])*orbit for i in range(3)],'XYZ');root.keyframe_insert(data_path='rotation_euler',frame=f+1)
    local=whole.lerp(Vector(phase['local_target']),zoom);target=root.rotation_euler.to_matrix()@Vector((local.x*root.scale.x,local.y*root.scale.y,local.z*root.scale.z));scale=whole_scale+(phase['ortho_scale']-whole_scale)*zoom
    s.camera.location=(target.x,target.y-12,target.z+.15);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
    s.camera.keyframe_insert(data_path='location',frame=f+1);s.camera.keyframe_insert(data_path='rotation_euler',frame=f+1);s.camera.data.keyframe_insert(data_path='ortho_scale',frame=f+1)
    selected=clock['components'][clock['component_phase_by_frame'][f]] if clock['red_active_by_frame'][f] else None
    caption=clock['components'][clock['caption_phase_by_frame'][f]] if clock['caption_phase_by_frame'][f]>=0 else None
    for name,node in materials.items():
        node.inputs['Color'].default_value=(.9,.003,.001,1) if name==selected else (0,.72,.005,1);node.inputs['Color'].keyframe_insert(data_path='default_value',frame=f+1)
    timeline.append(dict(frame=f,rotation_euler=list(root.rotation_euler),camera_position=list(s.camera.location),camera_euler=list(s.camera.rotation_euler),ortho_scale=scale,highlight_component=selected,caption_component=caption,source_decoded_update=clock['decoded_update_by_frame'][f]))
for node in materials.values():
    if node.id_data.animation_data:
        for fc in node.id_data.animation_data.action.fcurves:
            for key in fc.keyframe_points:key.interpolation='CONSTANT'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'anti-virus-missile-information.blend'))
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);s.camera.select_set(True)
for o in wires.values():o.select_set(True)
# The exporter recognizes direct RGBA-to-output as KHR_materials_unlit.
# Export only a static base hue; the explicit timeline supplies material changes.
export_nodes=[]
for ob in wires.values():
    nt=ob.data.materials[0].node_tree;emission=nt.nodes.get('Emission');output=nt.nodes.get('Material Output')
    rgb=nt.nodes.new('ShaderNodeRGB');rgb.outputs['Color'].default_value=emission.inputs['Color'].default_value
    nt.links.new(rgb.outputs['Color'],output.inputs['Surface']);export_nodes.append((nt,emission,output,rgb))
bpy.ops.export_scene.gltf(filepath=str(out/'anti-virus-missile-information.glb'),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_cameras=True,export_format='GLB')
for nt,emission,output,rgb in export_nodes:
    nt.links.new(emission.outputs[0],output.inputs['Surface']);nt.nodes.remove(rgb)

frames=out/'frames';frames.mkdir(exist_ok=True)
reuse='--reuse-native-frames' in sys.argv
if reuse:assert sorted(p.name for p in frames.glob('*.png'))==[f'{i:03}.png' for i in range(423)]
requested=[f+1 for f in import_samples] if '--keyframes-only' in sys.argv else range(1,424)
for f in ([] if reuse else requested):
    s.frame_set(f);s.render.filepath=str(frames/f'{f-1:03}.png');bpy.ops.render.render(write_still=True)
manifest=dict(material_clock_sha256=hashlib.sha256(clock_path.read_bytes()).hexdigest(),material_clock_schema=1,import_material_contract='Pure unlit emission, same shader graph as native technical lines; apply explicit timeline hue.',independent_import_samples=import_samples,highlighted_frames=sum(clock['red_active_by_frame']),caption_visible_frames=sum(x>=0 for x in clock['caption_phase_by_frame']),issue=208,research_id='scitek:anti-virus-missile',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),fps=15,frame_count=423,rendered_frame_count=len(list(frames.glob('*.png'))),native_frame_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(frames.glob('*.png'))},phases=phases,root='AntiVirusRotor',root_scale=list(root.scale),component_nodes={name:o.name for name,o in wires.items()},timing='Legacy 423-frame source red activity and caption visibility are independent. Explicit source-reviewed component phase boundaries; authored camera/pose interpolation.',client_contract='Evaluate timeline camera/root transform and apply red to highlight_component, green to other components. Material hue and orthographic scale animation require timeline metadata; GLB alone does not portably retain them.',timeline=timeline)
(out/'information-timeline.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Prove glTF node geometry/animation can be evaluated independently at caption
# closeups, using the explicit portable camera contract.
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'anti-virus-missile-information.glb'))
for f in import_samples:
    s.frame_set(f+1);entry=timeline[f]
    for name in components:
        o=bpy.data.objects.get(name+' technical wire');assert o
        # Exported material animation is not relied upon. Reapply explicit hue.
        # Runtime hue applies to unlit technical lines. A black Principled BSDF
        # plus emission changes denoising/edge coverage for tiny red fragments.
        mat=o.data.materials[0];nt=mat.node_tree;nt.nodes.clear();node=nt.nodes.new('ShaderNodeEmission')
        node.inputs['Color'].default_value=(.9,.003,.001,1) if name==entry['highlight_component'] else (0,.72,.005,1)
        output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(node.outputs[0],output.inputs[0])
    s.camera.location=entry['camera_position'];s.camera.rotation_euler=entry['camera_euler'];s.camera.data.ortho_scale=entry['ortho_scale'];s.render.filepath=str(out/f'imported-{f:03}.png');bpy.ops.render.render(write_still=True)
print('TRACKER_INFORMATION_RENDERED',len(timeline))
