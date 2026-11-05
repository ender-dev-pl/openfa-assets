"""Render a 6 fps/320x240 review proxy; canonical native project remains 24 fps/640x480."""
import bpy,json,sys,argparse,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--worker',type=int,default=0);ap.add_argument('--workers',type=int,default=1);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);a.out.mkdir(parents=True,exist_ok=True);sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
m=bpy.data.scenes['MASTER — Full intro basic pass'];bpy.context.window.scene=m
for s in bpy.data.scenes:
 s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_percentage=50
 if s.render.engine=='CYCLES':s.cycles.samples=4;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=not s.get('preserve_signal_noise',False)
m.render.resolution_x=320;m.render.resolution_y=240;m.render.resolution_percentage=100;m.render.image_settings.file_format='PNG';done={}
for i in range(a.worker,937,a.workers):
 m.frame_set(4*i+1);bpy.context.view_layer.update();p=a.out/f'frame-{i:04d}.png';m.render.filepath=str(p);bpy.ops.render.render(write_still=True,scene=m.name);done[str(i)]=hashlib.sha256(p.read_bytes()).hexdigest();print('ANIMATIC_FRAME',i,flush=True)
(a.out/f'worker-{a.worker}.json').write_text(json.dumps(dict(native_sha256=sha,review_fps=6,completed=done),indent=2)+'\n')
