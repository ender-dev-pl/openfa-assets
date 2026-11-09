"""Read-only current candidate/native/GLB smoke inspection; no acceptance promotion."""
from pathlib import Path
import argparse,hashlib,json,struct,sys
import bpy
ROOT=Path(__file__).resolve().parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def snapshot():
    deps=bpy.context.evaluated_depsgraph_get();objects={};roots=[]
    for obj in bpy.context.scene.objects:
        if obj.type in ['MESH','EMPTY'] and obj.parent is None:
            roots.append(dict(name=obj.name,type=obj.type,matrix=[float(v) for row in obj.matrix_world for v in row]))
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();points=[obj.matrix_world@v.co for v in mesh.vertices]
        objects[obj.name]=dict(triangles=len(mesh.loop_triangles),vertices=len(mesh.vertices),bounds=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)],materials=[m.name for m in obj.data.materials if m])
        evaluated.to_mesh_clear()
    images=[dict(name=i.name,size=list(i.size),packed=bool(i.packed_file)) for i in bpy.data.images if i.users and i.source!='VIEWER']
    actions=[dict(object=o.name,action=o.animation_data.action.name,frames=list(o.animation_data.action.frame_range)) for o in bpy.context.scene.objects if o.animation_data and o.animation_data.action]
    return dict(meshes=objects,roots=roots,images=images,actions=actions)


def main(output):
    inventory=ROOT/'sources/docs/reconstruction/models/inventory.json';data=json.loads(inventory.read_bytes());refs=json.loads((ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json').read_bytes());records=[];models=[]
    for key in ['040','041','042']:
        record=next(r for r in data['records'] if r['id']=='openfa:building/legacy/'+key);candidate=[s for s in record['available_studies'] if s['present']][-1]
        models.append((record,candidate['blend'],'latest present inventory study'))
        reviewed=record.get('reviewed_model',{}).get('blend')
        if reviewed and reviewed!=candidate['blend']:models.append((record,reviewed,'earlier inventory-ledger binding'))
    for record,relative,role in models:
        source=(ROOT/'sources'/relative).resolve();assert source.is_relative_to((ROOT/'sources').resolve()) and source.suffix=='.blend'
        export=source.with_suffix('.glb');before=dict(blend=sha(source),glb=sha(export))
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);bpy.context.scene.frame_set(1);bpy.context.view_layer.update();native=snapshot()
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(export));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();imported=snapshot()
        names_match=native['meshes'].keys()==imported['meshes'].keys();error=max((abs(a-b) for name,row in native['meshes'].items() if name in imported['meshes'] for a,b in zip(row['bounds'],imported['meshes'][name]['bounds'])),default=0)
        raw=export.read_bytes();assert raw[:4]==b'glTF';length=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+length]);after=dict(blend=sha(source),glb=sha(export));assert before==after,'Inspection changed a model'
        reference=next(r for r in refs['buildings'] if r['id']==record['id'])
        records.append(dict(id=record['id'],key=reference['key'],name=record['name'],footprint=reference['footprint'],definition_class=reference['definition_class'],role=role,blend=source.relative_to(ROOT).as_posix(),glb=export.relative_to(ROOT).as_posix(),binaries=before,source_unchanged=True,native=native,imported=imported,names_match=names_match,maximum_same_name_world_bounds_error=error,glb_material_count=len(gltf.get('materials',[])),glb_embedded_images=sum('bufferView' in i for i in gltf.get('images',[])),glb_image_count=len(gltf.get('images',[])),glb_clips=[a.get('name','') for a in gltf.get('animations',[])]))
        print('RIGELLIAN_BASELINE_INSPECTED',reference['key'],role,len(native['meshes']),names_match,error,flush=True)
    report=dict(issue=253,blender=bpy.app.version_string,inspector_sha256=sha(Path(__file__)),inventory_snapshot_sha256=sha(inventory),records=records,scope='Fresh saved-native and independent GLB geometry/root/material-count smoke only. No render/pixel parity, exact shader/UV/topology or exhaustive state validation, client calibration or artistic acceptance inferred. Previous models remain byte-identical.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(Path(args.output).resolve())
