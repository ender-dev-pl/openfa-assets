"""Generate every explicitly authored catalogue model, with resumable review renders."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from catalogue_rendering import assemble, evaluated_points, fit_camera


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', help='Optional comma-separated global types for targeted review')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--resolution',type=int,default=512)
    parser.add_argument('--samples',type=int,default=32)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root = Path(__file__).resolve().parents[2] / 'docs/assets/bootstrap-3d/full-catalogue'
    source = json.loads((root/'recipes.json').read_text(encoding='utf-8'))
    script_root = Path(__file__).resolve().parent
    code_hash = hashlib.sha256(b''.join((script_root/name).read_bytes() for name in
        ['build_full_catalogue.py','catalogue_rendering.py','build_legacy_buildings.py','build_openfa_assets.py'])).hexdigest()
    requested = set(map(int,args.ids.split(','))) if args.ids else set(range(177))
    records = [item for item in source['buildings'] if item['global_type'] in requested]
    assert len(records) == len(requested), 'Unknown catalogue IDs'
    views = [('front-quarter',(8,-12,10.1)),('rear-quarter',(-8,12,10.1)),('top',(0,0,20))]
    for record in records:
        output = root / record['culture'] / record['preview'].lower()
        output.mkdir(parents=True,exist_ok=True)
        recipe_hash = hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()
        if args.resume and (output/'model.json').is_file():
            cached = json.loads((output/'model.json').read_text(encoding='utf-8'))
            complete = all((output/name).is_file() for name in ['model.blend','model.glb']+[view+'.png' for view,_ in views])
            if complete and cached.get('code_sha256')==code_hash and cached.get('recipe_sha256')==recipe_hash and cached['resolution']==args.resolution and cached['samples']==args.samples:
                print('CATALOGUE_CACHED',record['global_type'],record['preview'],flush=True)
                continue
        scene = setup_scene(args.resolution,args.samples)
        scene.name = f"{record['global_type']:03} | {record['name']}"
        collection = bpy.data.collections.new(record['preview']+' | '+record['name'])
        scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        assemble(record)
        collection.asset_mark()
        collection.asset_data.description = record['building_id']+'; '+record['observed_features']
        collection['building_id'] = record['building_id']
        collection['global_type'] = record['global_type']
        collection['footprint'] = record['footprint']
        meshes = [obj for obj in collection.objects if obj.type=='MESH']
        assert len(meshes)>=4,record['building_id']
        points = evaluated_points(meshes)
        low,high = fit_camera(scene,points,views[0][1])
        bpy.ops.object.select_all(action='DESELECT')
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True)
        for name,direction in views:
            fit_camera(scene,points,direction)
            scene.render.filepath = str(output/(name+'.png'))
            bpy.ops.render.render(write_still=True)
        fit_camera(scene,points,views[0][1])
        scene.render.filepath = str(output/'front-quarter.png')
        bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'),compress=True)
        metadata = {key:record[key] for key in ['global_type','building_id','name','culture','footprint','preview','assembly_family','observed_features']}
        metadata.update(mesh_objects=len(meshes),bounds_min=list(low),bounds_max=list(high),
            views=[name for name,_ in views],resolution=args.resolution,samples=args.samples,
            blender=bpy.app.version_string,renderer='Cycles CPU',transparent=True,
            imported_geometry_or_textures=[],recipe_sha256=recipe_hash,code_sha256=code_hash)
        (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
        print('CATALOGUE_MODEL_OK',record['global_type'],record['preview'],len(meshes),flush=True)
    saved = [json.loads(path.read_text(encoding='utf-8')) for path in sorted(root.glob('*/*/model.json'))]
    (root/'manifest.json').write_text(json.dumps({'schema_version':1,'expected_count':177,
        'completed_count':len(saved),'models':sorted(saved,key=lambda item:item['global_type'])},indent=2)+'\n',encoding='utf-8')
    print('CATALOGUE_GENERATION_OK',len(saved),'of 177',flush=True)


if __name__=='__main__':
    main()
