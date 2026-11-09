"""Apply reviewed rougher alloy finish to existing canonical geometry, no copies."""
from pathlib import Path
import argparse,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).parent))
import remaster_braccatian_mobile_ships as author


def main(key):
    out,media=author.folders(key);meta=json.loads((out/'model.json').read_text());before={k:author.sha(out/('model.'+k)) for k in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False);bpy.context.preferences.filepaths.save_version=0
    material=author.material()
    for o in author.meshes():
        o.data.materials.clear();o.data.materials.append(material)
        for f in o.data.polygons:f.material_index=0
    for m in list(bpy.data.materials):
        if m.users==0:bpy.data.materials.remove(m)
    for image in list(bpy.data.images):
        if image.users==0:bpy.data.images.remove(image)
    scene=bpy.context.scene
    for label,direction in author.VIEWS.items():
        author.fit_camera(scene,author.evaluated_points(author.meshes()),direction);scene.render.filepath=str(media/(label+'.png'));bpy.ops.render.render(write_still=True)
    author.fit_camera(scene,author.evaluated_points(author.meshes()),author.VIEWS['front-quarter'])
    bpy.ops.object.select_all(action='DESELECT')
    for o in scene.objects:
        if o.type in ['MESH','EMPTY']:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True,relative_remap=True)
    meta.update(blend_sha256=author.sha(out/'model.blend'),glb_sha256=author.sha(out/'model.glb'),maps_generator_sha256=author.sha(author.ROOT/'tools/author_braccatian_ship_maps.py'),map_sha256={p.name:author.sha(p) for p in author.MAPS.glob('*.png')})
    meta['surface_refinement']=dict(generator=Path(__file__).relative_to(author.ROOT).as_posix(),generator_sha256=author.sha(Path(__file__)),input_binary_hashes=before,reason='Retrospective concept/GLB feedback: increase roughness from .43 to .57 and metalness from .66 to .80 for used alloy; retain geometry, palette regions and isolated wear without dense panels.')
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('BRACCATIAN_FINISH_REFINED',key,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ship',choices=author.CASES,required=True);main(p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
