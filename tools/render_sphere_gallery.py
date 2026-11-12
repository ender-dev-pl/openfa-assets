"""Render the saved sphere animation without changing the authored model."""
import bpy, sys, json, hashlib
from pathlib import Path
source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_x=400;s.render.resolution_y=400
s.render.film_transparent=False
frames=[]
for i,f in enumerate(range(1,74,2)):
    s.frame_set(f);s.render.filepath=str(out/f'frame-{i:03}.png');bpy.ops.render.render(write_still=True)
    frames.append({'file':f'frame-{i:03}.png','source_frame':f,'quaternion':list(bpy.data.objects['SphereRotor'].rotation_quaternion)})
assert len({tuple(round(x,5) for x in f['quaternion']) for f in frames})>30
(out/'render-manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blender':bpy.app.version_string,'fps':30,'frames':frames},indent=2)+'\n')
print('SPHERE_GALLERY_ANIMATION_RENDERED',len(frames))
