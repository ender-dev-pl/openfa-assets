"""Read-only native/independent-GLB smoke check for existing shared ship choices."""
from pathlib import Path
import hashlib,json,sys,struct
import bpy
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[3]
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SHIPS={'terminator':('TerminatorResearchRotor',71),'fleet-battleship':('BattleshipResearchRoot',45),'command-cruiser':('CommandCruiserRoot',82)}


def snapshot():
    deps=bpy.context.evaluated_depsgraph_get();result={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh()
        points=[obj.matrix_world@v.co for v in mesh.vertices]
        assert points and obj.data.materials,obj.name
        result[obj.name]=dict(matrix=[v for row in obj.matrix_world for v in row],bounds=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)])
        evaluated.to_mesh_clear()
    return result


def main(output):
    rows=[]
    for slug,(root_name,count) in SHIPS.items():
        folder=ROOT/'sources/objects/terran'/slug/'refined';source=folder/'model.blend';glb=folder/'model.glb';before=dict(blend=SHA(source),glb=SHA(glb))
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
        scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects[root_name]
        identity=max(abs(root.matrix_world[i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4));assert identity<1e-6,(slug,'gameplay root',identity)
        native={}
        for frame in [1,31,61]:
            scene.frame_set(frame);bpy.context.view_layer.update();native[frame]=snapshot();assert len(native[frame])==count,(slug,len(native[frame]))
        raw=glb.read_bytes();length=struct.unpack_from('<I',raw,12)[0];document=json.loads(raw[20:20+length]);assert document.get('images') and all('uri' not in r for r in document['images'])
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(glb));scene=bpy.context.scene;matrix_error=0;bounds_error=0
        for frame in native:
            scene.frame_set(frame);bpy.context.view_layer.update();imported=snapshot();assert imported.keys()==native[frame].keys(),slug
            for name,row in native[frame].items():
                matrix_error=max(matrix_error,max(abs(a-b) for a,b in zip(row['matrix'],imported[name]['matrix'])))
                bounds_error=max(bounds_error,max(abs(a-b) for a,b in zip(row['bounds'],imported[name]['bounds'])))
        assert matrix_error<1e-4 and bounds_error<1e-4,(slug,matrix_error,bounds_error)
        assert before==dict(blend=SHA(source),glb=SHA(glb))
        rows.append(dict(id='openfa:'+slug,blend=source.relative_to(ROOT).as_posix(),glb=glb.relative_to(ROOT).as_posix(),binaries=before,mesh_count=count,frames=[1,31,61],maximum_world_matrix_error=matrix_error,maximum_evaluated_bounds_error=bounds_error,gameplay_pose_frame=1,root=root_name,gameplay_root_identity_error=identity,embedded_images=len(document['images']),source_and_export_unchanged=True))
        print('TERRAN_CANONICAL_SELECTION_VERIFIED',slug,matrix_error,bounds_error,flush=True)
    report=dict(issue=248,verifier_sha256=SHA(Path(__file__)),blender=bpy.app.version_string,models=rows,scope='Read-only current saved-native and independent GLB smoke checks for source selection. Three sampled poses are not exhaustive animation/topology/UV/legacy-fidelity or concept review. Existing source-specific SciTek evidence remains separate; client scale/mount/animation handling not accepted.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main(Path(sys.argv[sys.argv.index('--')+1]).resolve())
