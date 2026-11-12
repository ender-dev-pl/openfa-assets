"""Read-only native/imported GLB baseline. No visual or integration acceptance."""
import argparse, hashlib, json, struct, sys
from pathlib import Path
import bpy

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
    deps=bpy.context.evaluated_depsgraph_get(); rows=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH': continue
        evaluated=obj.evaluated_get(deps); mesh=evaluated.to_mesh(); mesh.calc_loop_triangles()
        points=[obj.matrix_world@v.co for v in mesh.vertices]
        rows.append(dict(name=obj.name,triangles=len(mesh.loop_triangles),bounds=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)]))
        evaluated.to_mesh_clear()
    return rows

def main(root, output):
    inventory=root/'sources/docs/reconstruction/models/inventory.json'; data=json.loads(inventory.read_text(encoding='utf-8')); rows=[]
    for record in data['records']:
        if record['culture']!='achaean' or record['category']!='buildings': continue
        for study in record['available_studies']:
            if not study['present']: continue
            source=root/'sources'/study['blend']; export=source.with_suffix('.glb'); before=[sha(source),sha(export)]
            bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False); bpy.context.scene.frame_set(1); native=snapshot()
            bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=str(export)); imported=snapshot()
            raw=export.read_bytes(); length=struct.unpack_from('<I',raw,12)[0]; gltf=json.loads(raw[20:20+length]); counts=[]
            for mesh in gltf.get('meshes',[]):
                for prim in mesh['primitives']:
                    assert prim.get('mode',4)==4
                    counts.append(gltf['accessors'][prim['indices']]['count']//3)
            assert before==[sha(source),sha(export)]
            row=dict(id=record['id'],name=record['name'],stage=study.get('stage'),blend=source.relative_to(root).as_posix(),glb=export.relative_to(root).as_posix(),blend_sha256=before[0],glb_sha256=before[1],native=native,imported=imported,native_triangles=sum(m['triangles'] for m in native),imported_triangles=sum(m['triangles'] for m in imported),glb_index_triangles=sum(counts),clips=[a.get('name','') for a in gltf.get('animations',[])],materials=len(gltf.get('materials',[])),unchanged=True)
            rows.append(row); print('ACHAEAN_BASELINE',record['id'],row['native_triangles'],row['glb_index_triangles'],flush=True)
    assert len({r['id'] for r in rows})==26
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(dict(issue=256,blender=bpy.app.version_string,inventory_sha256=sha(inventory),inspector_sha256=sha(Path(__file__)),scope='Read-only frame-1 mesh/budget/clip inspection. No visual, shader, state, client or artistic acceptance.',records=rows),indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.root.resolve(),a.output.resolve())
