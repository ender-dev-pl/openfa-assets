import bpy,json,hashlib
from pathlib import Path
p=Path(bpy.data.filepath).resolve().parent;s=bpy.context.scene;assert s.frame_end==302 and s.render.fps==24
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();file=p/'render-state.json';state=json.loads(file.read_text()) if file.exists() else {'scene_sha256':sha,'completed':{}}
if state['scene_sha256']!=sha:
 state={'scene_sha256':sha,'completed':{}}
(p/'rendered-frames').mkdir(exist_ok=True)
state['completed']={k:v for k,v in state['completed'].items() if (p/'rendered-frames'/f'frame-{int(k):06d}.png').exists() and hashlib.sha256((p/'rendered-frames'/f'frame-{int(k):06d}.png').read_bytes()).hexdigest()==v}
s.render.resolution_x=640;s.render.resolution_y=560;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.10;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=True
nebula=next(o for o in s.objects if o.name.startswith('Following shot — nebula'));galaxy=next(o for o in s.objects if o.name.startswith('Spiral galaxy —'));cloud=next(o for o in s.objects if o.name.startswith('Next dissolve —'))
for i in range(302):
 path=p/'rendered-frames'/f'frame-{i:06d}.png'
 if path.exists() and state['completed'].get(str(i))==hashlib.sha256(path.read_bytes()).hexdigest():continue
 s.frame_set(i+1);nebula.hide_render=i<132 or i>=236;galaxy.hide_render=i<208;cloud.hide_render=i<288;s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 state['completed'][str(i)]=hashlib.sha256(path.read_bytes()).hexdigest();tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(file)
 print(f'EXTENSION_RENDER {len(state["completed"])}/302',flush=True)
(p/'render-result.json').write_text(json.dumps(dict(frames=302,fps=24,duration_seconds=302/24,reused_frames=192,new_frames=110,scene_sha256=sha),indent=2)+'\n');print('EXTENSION_RENDER_FINISHED',flush=True)
