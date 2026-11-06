"""Check all physical vertices fit the preview; studio background is not black."""
import bpy,sys,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
args=sys.argv[sys.argv.index('--')+1:];source,preview=map(lambda p:Path(p).resolve(),args);proof=json.loads((preview/'proof.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert proof['source_sha256']==sha(source) and proof['frames']==60 and len(list(preview.glob('*.png')))==60
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.render.resolution_x=288;s.render.resolution_y=320;model=json.loads((source.parent/'model.json').read_text());names=[n for group in model['components'].values() for n in group];rows=[]
for f in range(1,61):
 s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();points=[]
 for name in names:
  ob=bpy.data.objects[name];ev=ob.evaluated_get(deps);mesh=ev.to_mesh();points.extend(world_to_camera_view(s,s.camera,ob.matrix_world@v.co) for v in mesh.vertices);ev.to_mesh_clear()
 margin=min(min(p.x*288,(1-p.x)*288,p.y*320,(1-p.y)*320) for p in points);assert margin>=2,(f,margin);assert min(p.z for p in points)>0;rows.append(dict(frame=f-1,minimum_vertex_border_margin=margin))
(preview/'projection-verification.json').write_text(json.dumps(dict(source_sha256=sha(source),all60physical_vertex_projections_unclipped=True,mesh_count=len(names),minimum_margin=min(x['minimum_vertex_border_margin'] for x in rows),frames=rows),indent=2)+'\n',encoding='utf-8');print('PHOTON_PREVIEW_PROJECTION_VERIFIED',min(x['minimum_vertex_border_margin'] for x in rows))
