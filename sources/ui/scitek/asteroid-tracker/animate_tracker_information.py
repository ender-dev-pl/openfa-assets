"""Full authored technical presentation with legacy caption intervals and 564-frame clock.

Camera/pose interpolation is authored from inspected source phases, not recovered
original 3D camera data. The client consumes explicit per-frame camera/material
metadata because glTF cannot portably animate orthographic scale or material hue.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Euler
source=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;root=bpy.data.objects['TrackerRotor'];root.animation_data_clear()
model=json.loads((source.parent/'model.json').read_text());components=model['components']
wires={name:bpy.data.objects[name+' technical wire'] for name in components}
for name,names in components.items():
    for objname in names:bpy.data.objects[objname].hide_render=True
for o in wires.values():o.hide_render=False
s.render.resolution_x=224;s.render.resolution_y=224;s.cycles.samples=4;s.render.film_transparent=False;s.view_settings.view_transform='Standard'
s.world.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=0
s.frame_start=1;s.frame_end=564;s.render.fps=15
whole=Vector((.25,0,1.45));whole_scale=4.0;timeline=[];materials={}
for name,o in wires.items():
    mat=o.data.materials[0].copy();mat.name=name+' animated technical hue';o.data.materials[0]=mat;materials[name]=mat.node_tree.nodes.get('Emission')
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
def envelope(f):
    if f<42:return 0
    if f<66:return smooth((f-42)/24)
    if f<106:return 1
    if f<130:return 1-smooth((f-106)/24)
    return 0
phases=model['phases']
for f in range(564):
    group_index=min(3,f//141);phase=phases[group_index];local=f%141;zoom=envelope(local)
    # Original films demonstrate oblique orientation, settled frontal closeups,
    # then return to the whole device. Explicit authored poses retain that order.
    orbit=math.sin(local/140*math.tau)*(1-zoom)
    root.rotation_euler=Euler((math.radians(17)*orbit,math.radians(12)*orbit,math.radians(-22)*orbit),'XYZ');root.keyframe_insert(data_path='rotation_euler',frame=f+1)
    target=whole.lerp(Vector(phase['target']),zoom);scale=whole_scale+(phase['ortho_scale']-whole_scale)*zoom
    s.camera.location=(target.x,-12,target.z+.15);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
    s.camera.keyframe_insert(data_path='location',frame=f+1);s.camera.keyframe_insert(data_path='rotation_euler',frame=f+1);s.camera.data.keyframe_insert(data_path='ortho_scale',frame=f+1)
    selected=phase['component'] if phase['first_legacy_frame']<=f<=phase['last_legacy_frame'] else None
    for name,node in materials.items():
        node.inputs['Color'].default_value=(.9,.003,.001,1) if name==selected else (0,.72,.005,1);node.inputs['Color'].keyframe_insert(data_path='default_value',frame=f+1)
    timeline.append(dict(frame=f,rotation_euler=list(root.rotation_euler),camera_position=list(s.camera.location),camera_euler=list(s.camera.rotation_euler),ortho_scale=scale,highlight_component=selected))
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'asteroid-tracker-information.blend'))
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);s.camera.select_set(True)
for o in wires.values():o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'asteroid-tracker-information.glb'),use_selection=True,export_apply=True,export_animations=True,export_cameras=True,export_format='GLB')
frames=out/'frames';frames.mkdir(exist_ok=True)
for f in range(1,565):
    s.frame_set(f);s.render.filepath=str(frames/f'{f-1:03}.png');bpy.ops.render.render(write_still=True)
manifest=dict(issue=208,research_id='scitek:asteroid-tracker',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),fps=15,frame_count=564,phases=phases,root='TrackerRotor',component_nodes={name:o.name for name,o in wires.items()},timing='Legacy 564-frame information clock and caption intervals; pose and camera interpolation are authored approximations of the inspected film.',client_contract='Evaluate timeline camera/root transform and apply red to highlight_component, green to other components. Material hue and orthographic scale animation require timeline metadata; GLB alone does not portably retain them.',timeline=timeline)
(out/'information-timeline.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Prove glTF node geometry/animation can be evaluated independently at caption
# closeups, using the explicit portable camera contract.
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'asteroid-tracker-information.glb'))
for f in [0,87,228,369,510,563]:
    s.frame_set(f+1);entry=timeline[f]
    for name in components:
        o=bpy.data.objects.get(name+' technical wire');assert o
        # Exported material animation is not relied upon. Reapply explicit hue.
        mat=o.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Base Color'].default_value=(0,0,0,1);bs.inputs['Emission Color'].default_value=(.9,.003,.001,1) if name==entry['highlight_component'] else (0,.72,.005,1);bs.inputs['Emission Strength'].default_value=1
    s.camera.location=entry['camera_position'];s.camera.rotation_euler=entry['camera_euler'];s.camera.data.ortho_scale=entry['ortho_scale'];s.render.filepath=str(out/f'imported-{f:03}.png');bpy.ops.render.render(write_still=True)
print('TRACKER_INFORMATION_RENDERED',len(timeline))
