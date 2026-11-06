"""Compare native and independently imported solid animation at cardinal poses."""
import bpy,sys,json,hashlib
from pathlib import Path
source=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.render.resolution_x=288;s.render.resolution_y=320;s.cycles.samples=8;s.render.film_transparent=True
for f in [16,31,46]:
    s.frame_set(f);s.render.filepath=str(out/f'native-{f:02}.png');bpy.ops.render.render(write_still=True)
for obj in list(s.objects):
    if obj.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(source.with_suffix('.glb')))
for f in [16,31,46]:
    s.frame_set(f);s.render.filepath=str(out/f'imported-{f:02}.png');bpy.ops.render.render(write_still=True)
(out/'inputs.json').write_text(json.dumps(dict(blend_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(source.with_suffix('.glb').read_bytes()).hexdigest(),frames=[16,31,46]),indent=2)+'\n')
print('SOLID_PREVIEW_POSES_RENDERED')
