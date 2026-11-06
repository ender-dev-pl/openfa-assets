"""Open the saved scene in a fresh Blender process and render its dome."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy

p=argparse.ArgumentParser();p.add_argument('--blend',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.output.resolve();out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(a.blend.resolve()))
objects=[o for o in bpy.context.scene.objects if o.type in ['MESH','CURVE','FONT'] and not o.hide_render]
if len(objects)!=26:raise RuntimeError(f'Unexpected saved visibility: {len(objects)}')
bpy.context.scene.render.filepath=str(out/'reload.png');bpy.ops.render.render(write_still=True)
(out/'reload.json').write_text(json.dumps({'blender':bpy.app.version_string,'visible_objects':len(objects),'source_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256((out/'reload.png').read_bytes()).hexdigest()},indent=2)+'\n')
print('SAVED_MENU_RELOADED',len(objects))
