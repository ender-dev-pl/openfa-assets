"""Build detailed independent Rigellian Central Unit with a preserved 3x3 placement root."""
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from build_terran_missiles import sha
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_cpu_parts import build
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/central-unit'
VIEWS=[('front-quarter',(8,-12,10)),('rear-quarter',(-8,12,10)),('front',(0,-16,5)),
       ('side',(16,0,5)),('top',(0,0,20)),('underside',(6,-8,-15))]


def main():
    ROOT.mkdir(parents=True,exist_ok=True);scene=setup_scene(900,64)
    collection=bpy.data.collections.new('Rigellian Central Unit editable source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build();meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']='openfa:building/legacy/040';root['footprint_width']=3;root['footprint_height']=3
    root['placement_note']='Nominal footprint-centre origin at ground Z=0; runtime projection calibration pending'
    for obj in meshes: obj.parent=root
    collection.asset_mark();collection.asset_data.description='Independent RI01 study; static CPU, nominal 3x3 ground footprint'
    points=evaluated_points(meshes)
    for view,direction in VIEWS:
        fit_camera(scene,points,direction);render_to(scene,ROOT/(view+'.png'))
    fit_camera(scene,points,VIEWS[0][1])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]: obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    export_glb_to(ROOT/'model.glb');save_blend_to(ROOT/'model.blend')
    reference=json.loads((REPO/'docs/reconstruction/models/rigellian-cpu-reference.json').read_text())
    meta=dict(id=reference['id'],issue=969,revision=3,culture='rigellian',name='Central Unit',global_type=40,footprint=[3,3],
        origin='Footprint centre, ground Z=0; nominal one unit per grid cell, runtime calibration pending',placement_root='PlacementRoot',
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),blender=bpy.app.version_string,
        generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('rigellian_cpu_parts.py')),
        reference_sha256=sha(REPO/'docs/reconstruction/models/rigellian-cpu-reference.json'),mesh_objects=len(meshes),
        views=[view for view,_ in VIEWS],resolution=900,
        observed=['Broad upper saucer and flared waisted base','Exposed barred neck region','Gold three-prong crown','Round dark/pale roof and gold base features'],
        inferred=['Hidden sides/underside','Exact well depth, grille structure, service caps and seam/fastener counts','Materials and dimensions'],
        imported_geometry_or_textures=[],unresolved=['Construction/damage states','Runtime scale/projection/placement','Final artistic acceptance'],
        acceptance='Reference-based detailed study; final visual and integration acceptance open')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('RIGELLIAN_CPU_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
