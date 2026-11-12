"""Fresh read-only native/GLB pose and material audit of all research solids."""
import bpy,sys,json,struct,hashlib,traceback
from pathlib import Path
root,out=map(lambda p:Path(p).resolve(),sys.argv[sys.argv.index('--')+1:]);out.parent.mkdir(parents=True,exist_ok=True);integration=json.loads((root/'gallery/media/ui/scitek/integration.json').read_text());records=[]
for rec in integration['records']:
 if '/research/' not in rec.get('binding',''):continue
 row=dict(id=rec['id'],blend=rec['blend'],glb=rec['glb'])
 try:
  blend,glb=root/rec['blend'],root/rec['glb'];row.update(blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(glb.read_bytes()).hexdigest());raw=glb.read_bytes();length=struct.unpack_from('<I',raw,12)[0];document=json.loads(raw[20:20+length]);nodes=[n['name'] for n in document['nodes'] if 'mesh' in n];assert nodes and len(nodes)==len(set(nodes))
  palette=[m.get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1]) for m in document.get('materials',[])];assert palette and any(min(c[:3])<.9 for c in palette),'All materials are default/near white'
  bpy.ops.wm.open_mainfile(filepath=str(blend));s=bpy.context.scene;assert s.render.fps==15;samples=sorted(set([1,(s.frame_end+1)//2,s.frame_end]));expected={}
  for f in samples:
   s.frame_set(f);bpy.context.view_layer.update();expected[f]={n:[list(r) for r in bpy.data.objects[n].matrix_world] for n in nodes}
  bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(glb));assert len([o for o in s.objects if o.type=='MESH'])==len(nodes);maximum=0
  for f in samples:
   s.frame_set(f);bpy.context.view_layer.update()
   for n,m in expected[f].items():maximum=max(maximum,max(abs(bpy.data.objects[n].matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)))
  assert maximum<1e-4,('Native/import pose mismatch',maximum)
  row.update(status='verified',independently_imported_mesh_nodes=len(nodes),frames=samples,max_world_matrix_error=maximum,portable_material_count=len(palette),non_default_portable_colours=True,animation_clips=len(document.get('animations',[])))
 except Exception as error:row.update(status='failed',error=str(error));traceback.print_exc()
 records.append(row);print('SCITEK_FINAL_NATIVE_IMPORT',row['id'],row['status'],flush=True)
report=dict(scope='Fresh source-master/independent GLB pose checks at three timeline samples and portable material presence for all36 research solids; not a replacement for prior subject-specific geometry, choreography, raster or legacy checks.',limitations=['Samples are not an exhaustive animation audit.','Representative portable colours do not bake native procedural wear.','Client/GPU integration remains separately owned.'],records=records,counts=dict(subjects=len(records),verified=sum(r['status']=='verified' for r in records),failed=sum(r['status']=='failed' for r in records)))
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCITEK_FINAL_NATIVE_IMPORT_AUDIT',report['counts']);assert len(records)==36 and report['counts']['failed']==0
