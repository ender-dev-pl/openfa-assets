"""Reopen the saved Blend and render its selected missile group in Blender."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--blend',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=a.blend.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
visible=[o.name for o in bpy.context.scene.objects if o.type in {'MESH','CURVE','FONT'} and not o.hide_render]
if len(visible)!=6:raise RuntimeError(f'Saved scene visibility differs: {visible}')
bpy.context.scene.render.filepath=str(out/'reopened-source.png')
bpy.ops.render.render(write_still=True)
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'visible_objects':visible,'expected_group':'gameplay-017','render_sha256':hashlib.sha256((out/'reopened-source.png').read_bytes()).hexdigest()}
(out/'reopened-source.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED_SOURCE_RUNTIME_VERIFIED',len(visible),'objects')
