"""Build and render independent Stasis missile native and standalone sources."""
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from build_terran_missiles import VIEWS,sha
from catalogue_rendering import evaluated_points,fit_camera
from stasis_missile_parts import build
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/missiles/terran/stasis'


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    scene=setup_scene(768,64)
    collection=bpy.data.collections.new('Stasis editable source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build()
    meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    collection.asset_mark();collection.asset_data.description='Independent PM10 study; hidden mechanics and dimensions unresolved'
    points=evaluated_points(meshes)
    for view,direction in VIEWS:
        fit_camera(scene,points,direction);render_to(scene,ROOT/(view+'.png'))
    fit_camera(scene,points,VIEWS[1][1])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes: obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    export_glb_to(ROOT/'model.glb');save_blend_to(ROOT/'model.blend')
    ref=next(r for r in json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())['missiles'] if r['id']=='openfa:stasis')
    meta=dict(id=ref['id'],issue=967,revision=2,blender=bpy.app.version_string,
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),
        generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('stasis_missile_parts.py')),
        dependency_sha256={name:sha(Path(__file__).with_name(name)) for name in ['terran_missile_parts.py','build_terran_missiles.py']},
        mesh_objects=len(meshes),views=[view for view,_ in VIEWS],axis='+Z nose; front -Y; authored units',
        references=dict(management=ref['management_preview']['source_sha256'],surface=ref['surface']['source_sha256'],frames=[0,3,6,9]),
        observed=['Straight green casing and rounded head','Pale upper/joint/lower bands',
                  'Maroon round lower markings','Exposed red tail assembly and short nose pin'],
        inferred=['Fourfold hidden marking count','Tail frame and nozzle mechanism','Exact dimensions and material response'],
        imported_geometry_or_textures=[],unresolved=['Gameplay axes and scale','Mount transforms','Hidden mechanisms','Final artistic acceptance'],
        acceptance='study; final visual and integration acceptance open')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('STASIS_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
