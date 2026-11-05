"""Compare the draft against the existing model and independently imported GLB."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];base,draft=map(Path,args[:2])
def signature(o):
 return dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],uv=[[list(x.uv) for x in uv.data] for uv in o.data.uv_layers],matrix=[list(r) for r in o.matrix_world],materials=[m.name for m in o.data.materials])
bpy.ops.wm.open_mainfile(filepath=str(base.resolve()));original={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(draft.resolve()));s=bpy.context.scene;s.frame_set(1)
for name,sig in original.items():assert signature(bpy.data.objects[name])==sig,name
parts=json.loads((draft.parent/'model.json').read_text())['components'];assert [len(parts[r]) for r in parts]==[7,8,4,8]
native={}
deps=bpy.context.evaluated_depsgraph_get()
for names in parts.values():
 for name in names:
  ob=bpy.data.objects[name];ev=ob.evaluated_get(deps);mesh=ev.to_mesh();vs=[ob.matrix_world@v.co for v in mesh.vertices]
  native[name]=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)];ev.to_mesh_clear()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(draft.with_suffix('.glb').resolve()));bpy.context.scene.frame_set(1)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==27
maximum=0
for ob in meshes:
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
 maximum=max(maximum,max(abs(bounds[i][j]-native[ob.name][i][j]) for i in range(3) for j in range(2)))
assert maximum<2e-5,maximum
proof=dict(base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),blend_sha256=hashlib.sha256(draft.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(draft.with_suffix('.glb').read_bytes()).hexdigest(),preserved_meshes=len(original),imported_meshes=len(meshes),maximum_world_bounds_error=maximum,limitations=['Bounds comparison does not establish topology, animation or material portability acceptance. Further verification required.'])
(draft.parent/'preserved-geometry-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('VIRUS_DRAFT_PRESERVATION_VERIFIED',len(original),len(meshes),maximum)
