from pathlib import Path
import hashlib,json,subprocess,time,fcntl,argparse
p=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);args=ap.parse_args();assert 1<=args.workers<=4;lock=(p/'.master-render.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);scene=p/'first-sequence-to-412.blend';sha=hashlib.sha256(scene.read_bytes()).hexdigest();jobs=[]
for i in range(args.workers):
 log=(p/f'master-worker-{i}.log').open('w');proc=subprocess.Popen(['blender','-t','1','--background',str(scene),'--python-exit-code','1','--python',str(p/'render_master_worker.py'),'--',str(i),str(args.workers)],stdout=log,stderr=subprocess.STDOUT);jobs.append((proc,log))
while any(proc.poll() is None for proc,_ in jobs):
 count=0
 for i in range(args.workers):
  f=p/f'master-worker-state-{i}.json'
  if f.exists():
   d=json.loads(f.read_text())
   if d.get('scene_sha256')==sha:count+=len(d['completed'])
 print(f'MASTER_RENDER {count}/826',flush=True);time.sleep(10)
for proc,log in jobs:log.close();assert proc.returncode==0,proc.returncode
completed={}
for i in range(args.workers):
 d=json.loads((p/f'master-worker-state-{i}.json').read_text());assert d['scene_sha256']==sha;completed.update(d['completed'])
assert len(completed)==826
for i in range(826):assert hashlib.sha256((p/'rendered-frames'/f'frame-{i:06d}.png').read_bytes()).hexdigest()==completed[str(i)]
(p/'render-state.json').write_text(json.dumps(dict(scene_sha256=sha,completed=completed),indent=2)+'\n');print('MASTER_RENDER_VERIFIED 826/826',flush=True)
