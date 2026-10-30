"""Build independently authored weathered RI02 source, GLB and actual renders."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from build_terran_missiles import sha
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_filtration_parts import build
from terran_light_ship_parts import orient_and_chamfer
from filtration_wear_material import apply as apply_wear

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/filtration-plant'
VIEWS=[('front-quarter',(6,-13,8)),('rear-quarter',(-8,12,8)),('front',(0,-16,4)),
       ('side',(16,0,4)),('top',(0,0,20)),('underside',(6,-8,-15))]


def main():
    ROOT.mkdir(parents=True,exist_ok=True);scene=setup_scene(900,64)
    collection=bpy.data.collections.new('Rigellian Filtration Plant editable source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build();meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    apply_wear(meshes)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']='openfa:building/legacy/041';root['footprint_width']=2;root['footprint_height']=2
    for obj in meshes: obj.parent=root
    collection.asset_mark();collection.asset_data.description='Independent weathered RI02 study; nominal 2x2 placement'
    points=evaluated_points(meshes)
    for view,direction in VIEWS:
        fit_camera(scene,points,direction);render_to(scene,ROOT/(view+'.png'))
    fit_camera(scene,points,VIEWS[0][1]);bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]: obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    export_glb_to(ROOT/'model.glb');save_blend_to(ROOT/'model.blend')
    meta=dict(id='openfa:building/legacy/041',issue=971,revision=4,name='Filtration Plant',culture='rigellian',
        global_type=41,footprint=[2,2],placement_root='PlacementRoot',origin='Nominal footprint centre at ground Z=0; runtime calibration pending',
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),blender=bpy.app.version_string,
        generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('rigellian_filtration_parts.py')),
        reference_sha256=sha(REPO/'docs/reconstruction/models/rigellian-building-references.json'),mesh_objects=len(meshes),
        views=[view for view,_ in VIEWS],resolution=900,
        observed=['Rounded lower body, shoulder and capped upper tower','Six gold front ports and upper gold fitting','Lower vertical slots and side channel'],
        inferred=['Exact hidden surfaces and dimensions','Rear service closures, screws and rail construction','Wear and small dent placement'],
        surface_wear='Packed independently authored colour/roughness maps, abrasion on retaining rims, and shallow geometric dents',
        authored_wear_sha256=sha(ROOT/'authored-wear.json'),wear_material_sha256=sha(Path(__file__).with_name('filtration_wear_material.py')),
        imported_geometry_or_textures=[],unresolved=['Final artistic acceptance','Construction/damage states','Runtime scale/orientation/placement'],
        acceptance='Reference-based detailed study; final acceptance open')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('RIGELLIAN_FILTRATION_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
