"""Show all four open panels in the authoritative saved pose, then reload."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();source=out/'solar-matrix.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
hinges=[bpy.data.objects[f'Collector hinge {i+1}'] for i in range(4)]
assert all(abs(o.rotation_euler.y)<1e-6 for o in hinges)
panels=[bpy.data.objects[f'Splayed collector panel {i+1}'] for i in range(4)]
assert all(not o.hide_render for o in panels)
centres=[sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices) for o in panels]
assert all(min((a-b).length for b in centres if b!=a)>.7 for a in centres)
for name,position in [('canopy-four-panels',(4,-6,10)),('canopy-top',(0,0,10))]:
 target=Vector((0,0,3.28));s.camera.location=position;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=2.2;s.render.resolution_x=480;s.render.resolution_y=480;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
(out/'open-panel-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),open_panels=4,all_hinges_open=True,all_panels_visible_to_renderer=True,distinct_panel_centres=[list(v) for v in centres]),indent=2)+'\n')
print('FOUR_OPEN_PANELS_VERIFIED')
