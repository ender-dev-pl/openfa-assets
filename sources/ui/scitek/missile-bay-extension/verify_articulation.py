"""Independent GLB local carriage motion, stationary housing, loop and rasters."""
import bpy,sys,json,hashlib
from pathlib import Path
source=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.render.resolution_x=288;s.render.resolution_y=320;s.cycles.samples=8;s.render.film_transparent=True
samples=[1,31,61,91,121,151,166,180];native={};fixed=['Tall missile launcher mast','Annular revolving magazine','Open upper blast guard']
def values(m):return [v for row in m for v in row]
rig=json.loads((source.parent/'solid-animation-timeline.json').read_text());nodes=rig['animated_mesh_nodes'];s.frame_set(1);bpy.context.view_layer.update();baseline={n:values(bpy.data.objects[n].matrix_world) for n in fixed}
for f in samples:
 s.frame_set(f);bpy.context.view_layer.update()
 for n in fixed:assert max(abs(a-b) for a,b in zip(baseline[n],values(bpy.data.objects[n].matrix_world)))<1e-5
 native[f]={n:values(bpy.data.objects[n].matrix_world) for n in nodes};s.render.filepath=str(out/f'native-{f:03}.png');bpy.ops.render.render(write_still=True)
s.frame_set(181);bpy.context.view_layer.update()
for n in nodes:assert max(abs(a-b) for a,b in zip(native[1][n],values(bpy.data.objects[n].matrix_world)))<1e-5
assert max(abs(a-b) for n in nodes for a,b in zip(native[1][n],native[151][n]))>.5
for ob in list(s.objects):
 if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(source.with_suffix('.glb')));errors={};s.frame_set(1);bpy.context.view_layer.update();baseline={n:values(bpy.data.objects[n].matrix_world) for n in fixed}
for f in samples:
 s.frame_set(f);bpy.context.view_layer.update();errors[str(f)]={n:max(abs(a-b) for a,b in zip(native[f][n],values(bpy.data.objects[n].matrix_world))) for n in nodes};assert max(errors[str(f)].values())<1e-4,(f,errors[str(f)])
 for n in fixed:assert max(abs(a-b) for a,b in zip(baseline[n],values(bpy.data.objects[n].matrix_world)))<1e-5
 s.render.filepath=str(out/f'imported-{f:03}.png');bpy.ops.render.render(write_still=True)
(out/'inputs.json').write_text(json.dumps(dict(blend_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(source.with_suffix('.glb').read_bytes()).hexdigest(),frames=samples,body_turntable=False,fixed_housing=True,pivot_matrix_max_errors=errors,loop_closes=True),indent=2)+'\n');print('MISSILE_BAY_ARTICULATION_VERIFIED')
