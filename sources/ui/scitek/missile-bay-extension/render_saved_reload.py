"""Render independent GLB and a saved native reload in the same studio."""
import bpy,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
source=out/'missile-bay-extension.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);s.cycles.samples=16
for ob in list(s.objects):
    if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'missile-bay-extension.glb'))
assert len([o for o in s.objects if o.type=='MESH'])==97
s.frame_set(1);s.render.filepath=str(out/'imported-solid.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);s.cycles.samples=16;s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True)
(out/'native-review-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),native_runtime=True,saved_source_reload=True,independent_import_meshes=97,limitation='Raster comparison is separate; geometry/pose checks are in shared-geometry-verification.json.'),indent=2)+'\n',encoding='utf-8')
print('BAY_SHARED_REVIEW_RENDERED')
