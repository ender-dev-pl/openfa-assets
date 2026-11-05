"""12 fps review of original frames 144..412; native animation remains 24 fps."""
import bpy,argparse,sys,json,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--worker',type=int,default=0);ap.add_argument('--workers',type=int,default=1);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();out=a.out/sha[:12];out.mkdir(parents=True,exist_ok=True);m=bpy.data.scenes['MASTER — Full intro basic pass'];bpy.context.window.scene=m
for s in bpy.data.scenes:
 s.render.threads_mode='FIXED';s.render.threads=1
 if s.render.engine=='CYCLES':s.cycles.samples=12;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=not s.get('preserve_signal_noise',False)
done={}
for i in range(a.worker,269,a.workers):
 m.frame_set(2*(144+i)+1);p=out/f'frame-{i:04d}.png';m.render.filepath=str(p);bpy.ops.render.render(write_still=True,scene=m.name);done[str(i)]=hashlib.sha256(p.read_bytes()).hexdigest();print('REVIEW_FRAME',i,flush=True)
(out/f'worker-{a.worker}.json').write_text(json.dumps(dict(native_sha256=sha,completed=done),indent=2)+'\n')
