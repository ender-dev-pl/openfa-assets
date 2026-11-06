"""Reopen native and GLB cannon models and test actual bores/aperture depth."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import bounds,check_meshes

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/hardpoints'


def ray(obj,origin,direction):
    inverse=obj.matrix_world.inverted()
    hit,point,_,_=obj.ray_cast(inverse @ Vector(origin),(inverse.to_3x3() @ Vector(direction)).normalized())
    return obj.matrix_world @ point if hit else None


def structure(meshes,name):
    lookup={obj.name:obj for obj in meshes}
    if name=='photon-cannon':
        for sign in [-1,1]:
            obj=lookup['Photon paired barrel '+str(sign)]
            assert ray(obj,(sign*.39,-3,.13),(0,1,0)) is None,'Barrel axis must be open'
        assert 'Photon low pressure casing' in lookup and 'Photon rear equipment block' in lookup
    else:
        obj=lookup['Plasma single front assembly']
        assert ray(obj,(0,-3,.16),(0,1,0)) is None,'Plasma barrel axis must be open'
        obj=lookup['Plasma thick ribbed pressure casing']
        point=ray(obj,(-.27,3,.16),(0,-1,0))
        assert point is not None and .40<point.y<.51,'Rear aperture must penetrate the actual casing'
        assert 'Plasma rear aperture sleeve' in lookup
        assert len([obj for obj in meshes if obj.name.startswith('Plasma red casing rib')])==10


def main():
    for name in ['photon-cannon','plasma-cannon']:
        root=ROOT/name
        metadata=json.loads((root/'model.json').read_text())
        for extension in ['blend','glb']:
            assert hashlib.sha256((root/f'model.{extension}').read_bytes()).hexdigest()==metadata[extension+'_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(root/'model.blend'))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        assert len(meshes)==metadata['mesh_objects']
        check_meshes(meshes)
        structure(meshes,name)
        native_bounds=bounds(meshes)
        materials={slot.material.name for obj in meshes for slot in obj.material_slots}
        assert len(materials)==6
        assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
        assert any(collection.asset_data for collection in bpy.data.collections)
        assert not any(obj.animation_data for obj in meshes)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(root/'model.glb'))
        imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(imported)
        structure(imported,name)
        assert len(imported)==len(meshes)
        assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
        assert max(abs(a-b) for a,b in zip(native_bounds,bounds(imported)))<.002
        report=dict(issue=957,blend_sha256=metadata['blend_sha256'],glb_sha256=metadata['glb_sha256'],
                    native_meshes=len(meshes),imported_meshes=len(imported),material_count=6,
                    checks=['native/imported nondegenerate topology','positive closed-shell volumes',
                            'actual axial bores','actual rear aperture depth where applicable',
                            'matching bounds/materials','no external images','no invented aiming animation'],
                    final_visual_acceptance=False)
        (root/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('CANNON_NATIVE_GLB_OK',name,len(meshes),flush=True)


if __name__=='__main__':
    main()
