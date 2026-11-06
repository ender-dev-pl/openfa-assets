"""Fresh-process validation of every saved Blend source and independent GLB import."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from catalogue_rendering import evaluated_points, fit_camera


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids',help='Optional global types for targeted review')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=Path(__file__).resolve().parents[2]/'docs/assets/bootstrap-3d/full-catalogue'
    recipes=json.loads((root/'recipes.json').read_text(encoding='utf-8'))['buildings']
    package=json.loads((root.parents[3]/'content/standard/catalogues/legacy-buildings.json').read_text(encoding='utf-8'))['buildings']
    assert {item['building_id'] for item in recipes}=={item['id'] for item in package}
    ids=set(map(int,args.ids.split(','))) if args.ids else set(range(177))
    script_root=Path(__file__).resolve().parent
    code_hash=hashlib.sha256(b''.join((script_root/name).read_bytes() for name in
        ['build_full_catalogue.py','catalogue_rendering.py','build_legacy_buildings.py','build_openfa_assets.py'])).hexdigest()
    checked=[]
    for recipe in recipes:
        if recipe['global_type'] not in ids:
            continue
        directory=root/recipe['culture']/recipe['preview'].lower()
        metadata=json.loads((directory/'model.json').read_text(encoding='utf-8'))
        assert metadata['code_sha256']==code_hash,recipe['preview']
        assert metadata['recipe_sha256']==hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest()
        assert metadata['building_id']==recipe['building_id'] and metadata['footprint']==recipe['footprint']
        bpy.ops.wm.open_mainfile(filepath=str(directory/'model.blend'))
        scene=bpy.context.scene
        meshes=[obj for obj in scene.objects if obj.type=='MESH']
        assert len(meshes)==metadata['mesh_objects']>=4
        assert scene.render.film_transparent and scene.camera.data.type=='ORTHO'
        assert scene.render.resolution_x==metadata['resolution']==512
        collections=[collection for collection in bpy.data.collections if collection.asset_data]
        assert len(collections)==1 and collections[0]['building_id']==recipe['building_id']
        assert list(collections[0]['footprint'])==recipe['footprint']
        assert not any(image.source=='FILE' for image in bpy.data.images)
        assert all(obj.data.materials and obj.data.polygons for obj in meshes)
        names={obj.name.split('.')[0] for obj in meshes}
        assert {part['name'] for part in recipe['parts']}<=names,recipe['preview']
        points=evaluated_points(meshes)
        low=[min(point[axis] for point in points) for axis in range(3)]
        high=[max(point[axis] for point in points) for axis in range(3)]
        assert all(abs(low[axis]-metadata['bounds_min'][axis])<0.001 for axis in range(3))
        assert all(abs(high[axis]-metadata['bounds_max'][axis])<0.001 for axis in range(3))
        assert all(0.01<high[axis]-low[axis]<20 for axis in range(3)),recipe['preview']
        for direction in [(8,-12,10.1),(-8,12,10.1),(0,0,20)]:
            fit_camera(scene,points,direction)
            inverse=scene.camera.rotation_euler.to_matrix().transposed()
            projected=[inverse @ (point-scene.camera.location) for point in points]
            assert all(abs(point[axis])<scene.camera.data.ortho_scale/2
                       for point in projected for axis in [0,1]),recipe['preview']
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(directory/'model.glb'))
        imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        assert len(imported)==len(meshes),(recipe['preview'],len(imported),len(meshes))
        assert not any(image.source=='FILE' for image in bpy.data.images)
        checked.append(recipe['global_type'])
        print('CATALOGUE_REOPEN_OK',recipe['global_type'],recipe['preview'],len(imported),flush=True)
    assert set(checked)==ids
    print('CATALOGUE_VERIFICATION_OK',len(checked),flush=True)


if __name__=='__main__':
    main()
