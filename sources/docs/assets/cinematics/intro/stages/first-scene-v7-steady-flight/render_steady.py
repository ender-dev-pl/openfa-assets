import bpy,hashlib,json
from pathlib import Path
p=Path(bpy.data.filepath).resolve().parent;s=bpy.context.scene;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.1;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=True
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();f=p/'render-state.json';state=json.loads(f.read_text()) if f.exists() else {}
if state.get('scene_sha256')!=sha:state={'scene_sha256':sha,'completed':{}}
frames=p/'rendered-frames';frames.mkdir(exist_ok=True)
for i in range(302):
 path=frames/f'frame-{i:06d}.png'
 if path.exists() and state['completed'].get(str(i))==hashlib.sha256(path.read_bytes()).hexdigest():continue
 s.frame_set(i+1)
 for o in s.objects:
  if o.name.startswith('Following shot — nebula'):o.hide_render=i<132 or i>=236
  elif o.name.startswith('Spiral galaxy —'):o.hide_render=i<208
  elif o.name.startswith('Next dissolve —'):o.hide_render=i<288
 s.render.filepath=str(path);bpy.ops.render.render(write_still=True);state['completed'][str(i)]=hashlib.sha256(path.read_bytes()).hexdigest();f.write_text(json.dumps(state,indent=2)+'\n');print(f'STEADY_RENDER {i+1}/302',flush=True)
