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
if len(objects)!=19:raise RuntimeError(f'Unexpected saved visibility: {len(objects)}')
import bmesh
logos=[o for o in objects if o.name.startswith('Continuous welded convex emblem')]
if len(logos)!=1:raise RuntimeError('Saved logo must be one mesh')
bm=bmesh.new();bm.from_mesh(logos[0].data)
bad=sum(not e.is_manifold for e in bm.edges)
if bad:raise RuntimeError(f'Saved logo has {bad} nonmanifold edges')
bm.free()
bpy.context.scene.render.filepath=str(out/'reload.png');bpy.ops.render.render(write_still=True)
(out/'reload.json').write_text(json.dumps({'blender':bpy.app.version_string,'visible_objects':len(objects),'emblem_meshes':1,'emblem_nonmanifold_edges':bad,'source_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256((out/'reload.png').read_bytes()).hexdigest()},indent=2)+'\n')
print('SAVED_MENU_RELOADED',len(objects))
