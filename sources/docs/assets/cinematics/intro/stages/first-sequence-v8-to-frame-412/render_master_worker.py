import bpy,hashlib,json,sys
from pathlib import Path
p=Path(bpy.data.filepath).resolve().parent;args=sys.argv[sys.argv.index('--')+1:];worker,total=map(int,args);sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();file=p/f'master-worker-state-{worker}.json';done={}
for prior in [p/'render-state.json',file]:
 if prior.exists():
  d=json.loads(prior.read_text())
  if d.get('scene_sha256')==sha:done.update(d['completed'])
for s in bpy.data.scenes:
 s.render.threads_mode='FIXED';s.render.threads=1
 if s.render.engine=='CYCLES':s.cycles.samples=24;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.1;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=True
master=bpy.data.scenes['MASTER — First sequence through original frame 412'];bpy.context.window.scene=master;master.render.resolution_x=640;master.render.resolution_y=480;master.render.resolution_percentage=100;state={'scene_sha256':sha,'completed':{}};frames=p/'rendered-frames';frames.mkdir(exist_ok=True)
def save():
 tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(file)
for i in range(worker,826,total):
 path=frames/f'frame-{i:06d}.png'
 if path.exists() and done.get(str(i))==hashlib.sha256(path.read_bytes()).hexdigest():state['completed'][str(i)]=done[str(i)];continue
 for o in bpy.data.scenes['A — Ship and galaxy'].objects:
  if o.name.startswith('Following shot — nebula'):o.hide_render=i<132 or i>=236
  elif o.name.startswith('Next dissolve —'):o.hide_render=True
 master.frame_set(i+1);bpy.context.view_layer.update();master.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=master.name);state['completed'][str(i)]=hashlib.sha256(path.read_bytes()).hexdigest();save();print('MASTER_FRAME',worker,i+1,flush=True)
save();print('MASTER_WORKER_FINISHED',worker,flush=True)
