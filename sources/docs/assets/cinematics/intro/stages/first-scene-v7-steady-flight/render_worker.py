"""Independent one-thread frame partition; each process owns a distinct PNG subset and journal."""
import bpy,hashlib,json,sys
from pathlib import Path
p=Path(bpy.data.filepath).resolve().parent;args=sys.argv[sys.argv.index('--')+1:];worker,total=map(int,args);s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.1;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=True
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();f=p/f'render-worker-{worker}.json';done={}
for prior in [p/'render-state.json',f]:
 if prior.exists():
  data=json.loads(prior.read_text())
  if data.get('scene_sha256')==sha:done.update({k:v for k,v in data['completed'].items() if int(k)%total==worker})
state={'scene_sha256':sha,'completed':done};frames=p/'rendered-frames';frames.mkdir(exist_ok=True)
def save():
 tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(f)
save()
for i in range(worker,302,total):
 path=frames/f'frame-{i:06d}.png'
 if path.exists() and done.get(str(i))==hashlib.sha256(path.read_bytes()).hexdigest():continue
 s.frame_set(i+1)
 for o in s.objects:
  if o.name.startswith('Following shot — nebula'):o.hide_render=i<132 or i>=236
  elif o.name.startswith('Spiral galaxy —'):o.hide_render=i<208
  elif o.name.startswith('Next dissolve —'):o.hide_render=i<288
 s.render.filepath=str(path);bpy.ops.render.render(write_still=True);done[str(i)]=hashlib.sha256(path.read_bytes()).hexdigest();save();print(f'WORKER {worker} FRAME {i+1}',flush=True)
print('WORKER_FINISHED',worker,flush=True)
