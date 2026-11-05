"""Native reopen and independent static-GLB geometry check. No material/animation export acceptance."""
import bpy,json,sys,argparse
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path,required=True);ap.add_argument('--glb',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
def bounds(scene):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
 for o in scene.objects:
  if o.type not in ['MESH','FONT','CURVE']:continue
  e=o.evaluated_get(dg);m=e.to_mesh()
  if m:points.extend(e.matrix_world@v.co for v in m.vertices)
  e.to_mesh_clear()
 return [[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]

bpy.ops.wm.open_mainfile(filepath=str(a.native));s=bpy.context.scene;s.frame_set((s.frame_start+s.frame_end)//2);nb=bounds(s);nmesh=sum(o.type=='MESH' for o in s.objects);name=s.name;frame_range=[s.frame_start,s.frame_end];assert not bpy.data.sounds
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(a.glb));gb=bounds(bpy.context.scene);gmesh=sum(o.type=='MESH' for o in bpy.context.scene.objects);span=max(nb[1][i]-nb[0][i] for i in range(3));error=max(abs(nb[r][i]-gb[r][i]) for r in range(2) for i in range(3));assert error<max(.01,span*.01),(nb,gb,error);assert gmesh>=nmesh,(nmesh,gmesh)
a.report.write_text(json.dumps(dict(scene=name,native_reopened=True,independent_static_glb_import=True,native_meshes=nmesh,imported_meshes=gmesh,native_bounds=nb,imported_bounds=gb,max_bounds_error=error,native_frame_range=frame_range,quality='cinematic_refining_pass_2',animation_source='Editable Blender keyframes; GLB is a static midpoint interchange snapshot.',material_baking='deferred',refining='pass 1; precise matching remains subject to visual review',game_acceptance=False),indent=2)+'\n');print('BASIC_NATIVE_AND_GLB_VERIFIED',name)
