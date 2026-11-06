import bpy,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();base=Path(sys.argv[sys.argv.index('--')+2]).resolve()
def signatures():
 result={}
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or not ob.name.startswith('Fleet Battleship '):continue
  data=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers},matrix=[list(row) for row in ob.matrix_basis],materials=[mat.name for mat in ob.data.materials]);result[ob.name]=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
 return result
bpy.ops.wm.open_mainfile(filepath=str(base));expected=signatures();assert len(expected)==35
bpy.ops.wm.open_mainfile(filepath=str(out/'fleet-battleship.blend'));assert signatures()==expected;s=bpy.context.scene;s.cycles.samples=16;s.frame_set(1)
for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'fleet-battleship.glb'));assert len([o for o in s.objects if o.type=='MESH'])==45
root=bpy.data.objects['BattleshipResearchRoot'];s.frame_set(1);a=root.matrix_world.copy();s.frame_set(16);b=root.matrix_world.copy();assert sum(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))>1;s.frame_set(1)
s.render.filepath=str(out/'imported-solid.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'fleet-battleship.blend'));s=bpy.context.scene;s.frame_set(1);s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True)
(out/'verification.json').write_text(json.dumps(dict(native_runtime=True,saved_source_reload=True,independent_solid_import=True,imported_root_rotation_verified=True,source_mesh_count=35,all_mesh_geometry_uv_material_slots_and_local_transforms_preserved=True,source_mesh_signatures=expected,base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((out/'fleet-battleship.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'fleet-battleship.glb').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8');print('DEFLECTOR_NATIVE_IMPORT_VERIFIED')
