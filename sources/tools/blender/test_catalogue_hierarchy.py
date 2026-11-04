"""Controlled animated hierarchy round-trip; never writes game model sources."""
import math
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_catalogue_hierarchy import asset_objects,capture,compare


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    root=bpy.data.objects.new('TestRoot',None);bpy.context.scene.collection.objects.link(root)
    root['catalogue_id']='controlled-fixture';root.rotation_euler.z=0;root.keyframe_insert('rotation_euler',frame=1)
    root.rotation_euler.z=math.pi/2;root.keyframe_insert('rotation_euler',frame=17)
    socket=bpy.data.objects.new('TestSocket',None);bpy.context.scene.collection.objects.link(socket)
    socket.parent=root;socket.location=(0,2,0);socket['forward_axis']='local +Z';socket['calibration']='authored-uncalibrated'
    bpy.ops.mesh.primitive_cube_add(size=.4);hull=bpy.context.object;hull.name='TestHull';hull.parent=socket
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=17;scene.render.fps=24
    native,poses=capture(asset_objects(True))
    action=root.animation_data.action
    track=root.animation_data.nla_tracks.new();track.name='Active fixture track'
    track.strips.new('Active fixture cycle',1,action);root.animation_data.action=None
    muted=root.animation_data.nla_tracks.new();muted.name='Muted distant fixture track';muted.mute=True
    muted.strips.new('Ignored distant cycle',100,action)
    nla,nla_poses=capture(asset_objects(True))
    assert nla['action_range']==[1,17],nla
    assert max(abs(a-b) for phase in poses for name in poses[phase] for a,b in zip(poses[phase][name],nla_poses[phase][name]))<1e-6
    track.mute=True;root.animation_data.action=action
    root.animation_data.nla_tracks.remove(track);root.animation_data.nla_tracks.remove(muted)
    path=Path(__file__).resolve().parents[2]/'artifacts/issue-1112-controlled-hierarchy.glb'
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_apply=True,export_animations=True,
        export_extras=True,export_frame_range=True,export_force_sampling=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
    imported,other=capture(asset_objects(False));result=compare(native,imported,poses,other)
    assert not result['missing_imported'] and not result['extra_imported']
    assert not result['parent_differences'] and not result['type_differences'] and not result['property_differences']
    assert result['maximum_sampled_matrix_error']<1e-5,result
    imported['nodes']['TestSocket']['parent']=None
    imported['nodes']['TestSocket']['properties']['calibration']='different'
    changed=compare(native,imported,poses,other)
    assert 'TestSocket' in changed['parent_differences'] and 'TestSocket' in changed['property_differences']
    print('CATALOGUE_HIERARCHY_TEST_OK',result['maximum_sampled_matrix_error'],flush=True)


if __name__=='__main__': main()
