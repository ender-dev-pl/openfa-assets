"""Reopen native sources and GLB exports; check geometry and declared structure."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import bounds,check_meshes

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/ships/terran'


def check_y_notch(meshes):
    for x in [-.25,0,.25]:
        for y in [.80,1.20,1.70,2.20]:
            for obj in meshes:
                inverse=obj.matrix_world.inverted()
                hit,_,_,_=obj.ray_cast(inverse @ Vector((x,y,3)),
                    (inverse.to_3x3() @ Vector((0,0,-1))).normalized())
                assert not hit,'Combat Eagle Y notch is filled by '+obj.name
    # User correction: the rear arms need broad solid bodies extending to the
    # trailing edge, not thin diagonal strips around the central negative space.
    wings=[obj for obj in meshes if obj.name.startswith('Swept structural wing')]
    for wing in wings:
        zs=[v.co.z for v in wing.data.vertices]
        assert max(zs)-min(zs)>.50,'Combat Eagle rear arms must have structural depth'
    for x in [-2,-1.2,1.2,2]:
        for y in [2.1,2.4]:
            hits=[]
            for obj in wings:
                inverse=obj.matrix_world.inverted()
                hit,_,_,_=obj.ray_cast(inverse @ Vector((x,y,3)),
                    (inverse.to_3x3() @ Vector((0,0,-1))).normalized())
                hits.append(hit)
            assert any(hits),'Combat Eagle rear body area is missing'


def main():
    for name in ['combat-eagle','scoutship']:
        root=ROOT/name
        metadata=json.loads((root/'model.json').read_text())
        for extension in ['blend','glb']:
            assert hashlib.sha256((root/f'model.{extension}').read_bytes()).hexdigest()==metadata[extension+'_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(root/'model.blend'))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        assert len(meshes)==metadata['mesh_objects']
        check_meshes(meshes)
        native_bounds=bounds(meshes)
        assert bpy.context.scene.camera.data.type=='ORTHO'
        assert bpy.context.scene.render.film_transparent
        assert any(collection.asset_data for collection in bpy.data.collections)
        if name=='combat-eagle':
            assert len([obj for obj in meshes if obj.name.startswith('Swept structural wing')])==2
            assert any(obj.name=='Eagle dorsal service spine' for obj in meshes)
            # The source silhouette is a Y, with a deep open bay between the
            # rear arms. Check actual geometry, not a decorative dark patch.
            check_y_notch(meshes)
        else:
            assert any(obj.name=='Scout separate forward sensor pod' for obj in meshes)
            assert len([obj for obj in meshes if obj.name.startswith('Scout conformal crown rim cover')])==6
            assert len([obj for obj in meshes if obj.name.startswith('Scout conformal red shoulder belt')])==10
            assert not any(obj.name.startswith('Scout crown service plate') for obj in meshes)
            shell=bpy.data.objects['Scout raised oval crown']
            hit,point,_,_=shell.ray_cast(Vector((0,.26,2)),Vector((0,0,-1)))
            assert hit and point.z<.43,'Oval crown must have a real recessed centre'
            hit,rim,_,_=shell.ray_cast(Vector((0,1.20,2)),Vector((0,0,-1)))
            assert hit and rim.z>.45,'The rear rim must remain closed above the inset floor'
            assert len([obj for obj in meshes if obj.name.startswith('Scout inner rim silver element')])==14
        materials={slot.material.name for obj in meshes for slot in obj.material_slots}
        assert len(materials)==7
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(root/'model.glb'))
        imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(imported)
        assert len(imported)==len(meshes)
        assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
        assert max(abs(a-b) for a,b in zip(native_bounds,bounds(imported)))<.002
        if name=='combat-eagle':
            check_y_notch(imported)
        report=dict(issue=954,blend_sha256=metadata['blend_sha256'],glb_sha256=metadata['glb_sha256'],
                    native_meshes=len(meshes),imported_meshes=len(imported),material_count=7,bounds=native_bounds,
                    checks=['nonempty materialled geometry','no degenerate source/imported faces','no loose edges',
                            'no non-manifold edge fans','positive closed-shell signed volumes','matching imported bounds',
                            'no external image dependencies','declared per-ship structural features'],
                    negative_space_check='12 clear notch rays and 8 solid rear-body rays, native and imported' if name=='combat-eagle' else 'not applicable',
                    final_visual_acceptance=False)
        (root/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('LIGHT_SHIP_NATIVE_GLB_OK',name,len(meshes),flush=True)


if __name__=='__main__':
    main()
