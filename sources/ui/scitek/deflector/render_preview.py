"""Render the actual authored Long Range Transmitter turntable, preserving source identity."""
import bpy,sys,json,hashlib
from pathlib import Path
source=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8;s.render.resolution_x=480;s.render.resolution_y=320;s.camera.data.ortho_scale=1.6;s.render.film_transparent=False
for frame in range(1,61):
    s.frame_set(frame);s.render.filepath=str(out/f'{frame-1:03}.png');bpy.ops.render.render(write_still=True)
(out/'proof.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),frames=60,fps=15),indent=2)+'\n')
print('TRACKER_PREVIEW_RENDERED')
