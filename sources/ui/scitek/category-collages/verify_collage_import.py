"""Render a saved category source and independently imported static GLB."""
import bpy,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();manifest=Path(sys.argv[sys.argv.index('--')+2]).resolve();spec=json.loads(manifest.read_text());stem=spec['id'].split(':')[-1]
bpy.ops.wm.open_mainfile(filepath=str(out/(stem+'.blend')));s=bpy.context.scene;proof=json.loads((out/'provenance.json').read_text());native={ob.name:ob.matrix_world.copy() for ob in s.objects if ob.type in ['MESH','CURVE']};assert len(native)==proof['mesh_count']
s.render.filepath=str(out/'reload.png');bpy.ops.render.render(write_still=True)
for ob in list(s.objects):
 if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/(stem+'.glb')))
assert len([ob for ob in s.objects if ob.type=='MESH'])==proof['mesh_count']
error=0
for name,pose in native.items():
 ob=bpy.data.objects.get(name);assert ob and ob.type=='MESH';difference=max(abs(pose[i][j]-ob.matrix_world[i][j]) for i in range(4) for j in range(4));assert difference<1e-4,(name,difference);error=max(error,difference)
s.render.filepath=str(out/'imported.png');bpy.ops.render.render(write_still=True)
for subject in proof['subjects']:
 for ob in s.objects:
  if ob.type=='MESH':ob.hide_render=ob.name not in subject['mesh_names']
 s.render.filepath=str(out/('imported-'+subject['subject']+'.png'));bpy.ops.render.render(write_still=True)
(out/'import-verification.json').write_text(json.dumps(dict(mesh_count=proof['mesh_count'],matrix_max_error=error,independent_glb_import=True,saved_source_reload=True,blend_sha256=hashlib.sha256((out/(stem+'.blend')).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/(stem+'.glb')).read_bytes()).hexdigest()),indent=2)+'\n')
print('SCITEK_COLLAGE_IMPORT_VERIFIED',proof['mesh_count'],error)
