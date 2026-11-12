"""Render colour gallery PNGs from preserved natives without changing model sources."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--worker',type=int,default=0);ap.add_argument('--workers',type=int,default=1);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);items=json.loads((a.repo/'docs/trading-goods/coverage.json').read_text())['items'];a.out.mkdir(parents=True,exist_ok=True)
for item in items[a.worker::a.workers]:
 ident=item['legacy_stem'];native=a.repo/item['native'];sha=hashlib.sha256(native.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.04;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=768;s.render.resolution_y=576;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.film_transparent=True
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
 for o in s.objects:
  if o.type not in ['MESH','FONT','CURVE']:continue
  e=o.evaluated_get(dg);mesh=e.to_mesh();points.extend(e.matrix_world@v.co for v in mesh.vertices);e.to_mesh_clear()
 cam=s.camera;inv=cam.matrix_world.inverted();pp=[inv@p for p in points];x0,x1=min(p.x for p in pp),max(p.x for p in pp);y0,y1=min(p.y for p in pp),max(p.y for p in pp);cam.location+=cam.matrix_world.to_quaternion()@Vector(((x0+x1)*.5,(y0+y1)*.5,0));cam.data.ortho_scale=max(x1-x0,(y1-y0)*768/576)*1.16
 out=a.out/(ident+'.png');s.render.filepath=str(out);bpy.ops.render.render(write_still=True);assert hashlib.sha256(native.read_bytes()).hexdigest()==sha
 (a.out/(ident+'.json')).write_text(json.dumps(dict(item_id=item['id'],legacy_stem=ident,native=item['native'],native_sha256=sha,image_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),resolution=[768,576],samples=32,transparent_background=True,model_source_unchanged=True,renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n');print('GALLERY_PNG_RENDERED',ident,flush=True)
