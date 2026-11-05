import bpy,argparse,sys,json,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--frame',type=int,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--percent',type=int,default=100);ap.add_argument('--samples',type=int,default=48);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);m=bpy.data.scenes['MASTER — Cinematic BCD v2'];bpy.context.window.scene=m
for s in bpy.data.scenes:
 if s.render.engine=='CYCLES':s.cycles.samples=a.samples
m.render.resolution_percentage=a.percent;m.frame_set(a.frame*2+1);m.render.filepath=str(a.out);bpy.ops.render.render(write_still=True,scene=m.name);a.out.with_suffix('.json').write_text(json.dumps(dict(native_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),source_frame=a.frame,samples=a.samples,resolution=[1920*a.percent//100,1440*a.percent//100]),indent=2)+'\n')
