"""Bake explicit split normals so smooth native ribs use glTF's shading representation."""
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_culture_scaffolds import ROOT,REPO,sha
from build_refined_terran import render_to,save_blend_to
from build_refined_rigellian_scaffold import export_glb_to
from catalogue_rendering import evaluated_points,fit_camera


def main():
    index=json.loads((ROOT/'index.json').read_text())
    for family in index['families']:
        if family['family'] not in ['MKS2','MKS3','ACS2','ACS3']:continue
        folder=ROOT/Path(family['manifest']).parent
        manifest=json.loads((folder/'model.json').read_text())
        for case in manifest['cases']:
            print('CULTURE_NORMALS',family['family'],case['stage'],flush=True)
            stage=folder/f"stage-{case['stage']:02}"
            assert sha(stage/'model.blend')==case['blend_sha256']
            bpy.ops.wm.open_mainfile(filepath=str(stage/'model.blend'))
            scene=bpy.context.scene
            meshes=[o for o in scene.objects if o.type=='MESH']
            for obj in {o.data.as_pointer():o for o in meshes}.values():
                normals=[tuple(n.vector) for n in obj.data.corner_normals]
                # glTF expresses flat caps and curved sides through split
                # normals on smooth faces. Mirror that representation natively;
                # retain each original corner normal and the intended contour.
                for face in obj.data.polygons:face.use_smooth=True
                obj.data.normals_split_custom_set(normals)
            bpy.context.view_layer.update()
            camera=scene.camera;pose=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
            render_to(scene,stage/'front-quarter.png')
            if case['rear_view']:
                fit_camera(scene,evaluated_points(meshes),(-10,10,10));render_to(scene,stage/'rear-quarter.png')
            scene.camera.location=pose[0];scene.camera.rotation_euler=pose[1];scene.camera.data.ortho_scale=pose[2]
            bpy.ops.object.select_all(action='DESELECT')
            for obj in scene.objects:
                if obj.type in ['MESH','EMPTY']:obj.select_set(True)
            bpy.context.view_layer.objects.active=bpy.data.objects['PlacementRoot']
            export_glb_to(stage/'model.glb');save_blend_to(stage/'model.blend')
            case['blend_sha256']=sha(stage/'model.blend');case['glb_sha256']=sha(stage/'model.glb')
        manifest['normal_finalization']='Explicit original split normals on smooth faces, matching glTF representation; geometry, UVs and material design unchanged'
        manifest['inputs'][str(Path(__file__).relative_to(REPO)).replace('\\','/')]=sha(Path(__file__))
        (folder/'model.json').write_text(json.dumps(manifest,indent=2)+'\n')
        family['sha256']=sha(folder/'model.json')
    (ROOT/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    print('CULTURE_NORMALS_FINALIZED',65,flush=True)


if __name__=='__main__':main()
