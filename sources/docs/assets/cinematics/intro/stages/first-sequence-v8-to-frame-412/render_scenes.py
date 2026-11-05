from pathlib import Path
import json,hashlib,subprocess,time,fcntl,argparse
p=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);args=ap.parse_args();assert 1<=args.workers<=4
lock=(p/'.render.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
scene=p/'first-sequence-to-412.blend';sha=hashlib.sha256(scene.read_bytes()).hexdigest();jobs=json.loads((p/'render-jobs.json').read_text())['jobs'];running=[]
for i in range(args.workers):
 log=(p/f'worker-{i}.log').open('w');proc=subprocess.Popen(['blender','-t','1','--background',str(scene),'--python-exit-code','1','--python',str(p/'render_scene_worker.py'),'--',str(i),str(args.workers)],stdout=log,stderr=subprocess.STDOUT);running.append((proc,log))
while any(x.poll() is None for x,_ in running):
 count=0
 for i in range(args.workers):
  f=p/f'worker-state-{i}.json'
  if f.exists():
   d=json.loads(f.read_text())
   if d.get('scene_sha256')==sha:count+=len(d['completed'])
 print(f'SCENE_INPUTS {count}/{len(jobs)}',flush=True);time.sleep(10)
for proc,log in running:log.close();assert proc.returncode==0,proc.returncode
completed={}
for i in range(args.workers):
 d=json.loads((p/f'worker-state-{i}.json').read_text());assert d['scene_sha256']==sha;completed.update(d['completed'])
assert len(completed)==len(jobs)
for job in jobs:assert hashlib.sha256((p/job['path']).read_bytes()).hexdigest()==completed[job['key']]
(p/'scene-render-state.json').write_text(json.dumps(dict(scene_sha256=sha,completed=completed),indent=2)+'\n');print('ALL_SCENE_INPUTS_VERIFIED',len(jobs),flush=True)
