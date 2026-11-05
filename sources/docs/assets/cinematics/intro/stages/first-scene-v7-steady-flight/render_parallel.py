"""Launch four isolated Blender processes, then merge and verify their frame journals."""
from pathlib import Path
import subprocess,json,hashlib,time,argparse
p=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);args=ap.parse_args();assert 1<=args.workers<=4
scene=p/'opening-steady-flight.blend';sha=hashlib.sha256(scene.read_bytes()).hexdigest();jobs=[]
for i in range(args.workers):
 log=(p/f'worker-{i}.log').open('w');proc=subprocess.Popen(['blender','-t','1','--background',str(scene),'--python-exit-code','1','--python',str(p/'render_worker.py'),'--',str(i),str(args.workers)],stdout=log,stderr=subprocess.STDOUT);jobs.append((proc,log))
while any(proc.poll() is None for proc,_ in jobs):
 count=0
 for i in range(args.workers):
  f=p/f'render-worker-{i}.json'
  if f.exists():
   d=json.loads(f.read_text())
   if d.get('scene_sha256')==sha:count+=len(d['completed'])
 print('PARALLEL_RENDER',count,'/302',flush=True);time.sleep(10)
for proc,log in jobs:log.close();assert proc.returncode==0,proc.returncode
completed={}
for i in range(args.workers):
 d=json.loads((p/f'render-worker-{i}.json').read_text());assert d['scene_sha256']==sha;completed.update(d['completed'])
assert len(completed)==302
for i in range(302):assert hashlib.sha256((p/'rendered-frames'/f'frame-{i:06d}.png').read_bytes()).hexdigest()==completed[str(i)]
f=p/'render-state.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(dict(scene_sha256=sha,completed=completed),indent=2)+'\n');tmp.replace(f);print('PARALLEL_RENDER_VERIFIED 302/302',flush=True)
