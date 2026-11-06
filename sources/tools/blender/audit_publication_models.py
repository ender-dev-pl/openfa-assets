"""Fresh reopen and dependency checks after certified path-only normalization."""
import bpy,json,sys,hashlib
from pathlib import Path
root,out=map(lambda s:Path(s).resolve(),sys.argv[sys.argv.index('--')+1:])
cert=json.loads((root/'docs/merge-review-2026-11-06/publication-normalization.json').read_text());rows=[]
for entry in cert['files']:
 p=root/entry['path']
 if p.suffix!='.blend':continue
 assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['after_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 assert any(o.type in ['MESH','CURVE','FONT'] for o in bpy.context.scene.objects),p.name
 missing=[]
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file():missing.append('image:'+im.name)
 for font in bpy.data.fonts:
  if font.filepath not in ['', '<builtin>'] and not font.packed_file and not Path(bpy.path.abspath(font.filepath)).is_file():missing.append('font:'+font.name)
 for lib in bpy.data.libraries:
  if not Path(bpy.path.abspath(lib.filepath)).is_file():missing.append('library:'+lib.name)
 assert not missing,(entry['path'],missing)
 rows.append(dict(path=entry['path'],sha256=entry['after_sha256'],native_reopened=True,missing_dependencies=missing))
 print('NORMALIZED_NATIVE_REOPENED',entry['path'],flush=True)
out.write_text(json.dumps(dict(scope='Fresh runtime reopen and external dependency verification after path-only normalization; complements binary geometry/animation preservation certificate and independent GLB audit.',count=len(rows),records=rows),indent=2)+'\n')
print('NORMALIZED_NATIVE_RUNTIME_OK',len(rows))
