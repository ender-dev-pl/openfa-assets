import bpy,hashlib,json,sys
from pathlib import Path
p=Path(bpy.data.filepath).resolve().parent;args=sys.argv[sys.argv.index('--')+1:];worker,total=map(int,args);manifest=json.loads((p/'render-jobs.json').read_text());sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();file=p/f'worker-state-{worker}.json';done={}
for prior in [p/'scene-render-state.json',file]:
 if prior.exists():
  d=json.loads(prior.read_text())
  if d.get('scene_sha256')==sha:done.update(d['completed'])
state={'scene_sha256':sha,'completed':{}}
def save():
 tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(file)
for index,job in enumerate(manifest['jobs']):
 if index%total!=worker:continue
 key=job['key'];path=p/job['path']
 if path.exists() and done.get(key)==hashlib.sha256(path.read_bytes()).hexdigest():state['completed'][key]=done[key];continue
 s=bpy.data.scenes[job['scene']];bpy.context.window.scene=s;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_percentage=100;s.render.resolution_x=640;s.render.resolution_y=480 if job['code']=='A' else 262;s.cycles.samples=24;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.10;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=True;s.frame_set(job['frame']);bpy.context.view_layer.update()
 if job['code']=='A':
  for o in s.objects:
   if o.name.startswith('Following shot — nebula'):o.hide_render=job['frame']<133 or job['frame']>=237
   elif o.name.startswith('Next dissolve —'):o.hide_render=True
 path.parent.mkdir(parents=True,exist_ok=True);s.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=s.name);state['completed'][key]=hashlib.sha256(path.read_bytes()).hexdigest();save();print('SCENE_FRAME',worker,key,flush=True)
save();print('WORKER_FINISHED',worker,flush=True)
