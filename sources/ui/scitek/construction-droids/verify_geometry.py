import bpy,sys,json,bmesh,hashlib,struct
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'construction-droids.blend'));s=bpy.context.scene
model=json.loads((out/'model.json').read_text());root=bpy.data.objects['ConstructionDroidRig'];roles=['chassis','heavy-manipulator','optical-sensor','spot-welder','light-manipulator','laser-solder-tool'];assert list(model['components'])==roles
names=sum(model['components'].values(),[]);hardware=[bpy.data.objects[n] for n in names];closed=0
for ob in hardware:
 parent=ob.parent
 while parent and parent!=root:parent=parent.parent
 assert parent==root,ob.name
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;bm.free();closed+=1
assert len(model['phases'])==5 and model['information_timeline_frames']==705
assert len([n for n in names if n.startswith('Heavy curved gripping jaw')])==3
assert len([n for n in names if n.startswith('Pale precision gripper finger')])==2
assert len([n for n in names if n.startswith('Precision laser solder needle')])==2
assert len(model['solid_only_effect_nodes'])==33 and len([n for n in model['solid_only_effect_nodes'] if n.startswith('Welding spark ')])==32
assert model['solid_animation']['frame_count']==120 and not model['solid_animation']['body_turntable']
rig=json.loads((out/'solid-animation-timeline.json').read_text());assert rig['frame_count']==120 and len(rig['timeline'])==120 and rig['source_blend_sha256']==hashlib.sha256((out/'construction-droids.blend').read_bytes()).hexdigest();assert rig['source_glb_sha256']==hashlib.sha256((out/'construction-droids.glb').read_bytes()).hexdigest()
assert not rig['timeline'][0]['visible_effects'] and rig['timeline'][60]['visible_effects'] and not rig['timeline'][119]['visible_effects']
assert root.animation_data is None and all(abs(x-1)<1e-5 for x in root.scale)
def glb_nodes(path):
 raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+length]);return d,[n.get('name','') for n in d['nodes']]
doc,solid=glb_nodes(out/'construction-droids.glb');assert len(doc['animations'])==1 and all(n in solid for n in model['solid_only_effect_nodes'])
for path in out.glob('construction-droids-*.glb'):
 _,nodes=glb_nodes(path);assert not any(n.startswith('Welding spark ') or n=='Spot welding arc' for n in nodes),path
(out/'geometry-verification.json').write_text(json.dumps(dict(closed_hardware_meshes=closed,hardware_curves=len(hardware)-closed,heavy_jaws=3,light_fingers=2,laser_solder_needles=2,spark_nodes=32,welding_arc_nodes=1,preview_frames=120,body_turntable=False,rigid_node_animation=True,information_frames=705,information_phases=5,solid_camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y]),source_blend_sha256=rig['source_blend_sha256']),indent=2)+'\n',newline='\n');print('DROID_GEOMETRY_VERIFIED',closed)
