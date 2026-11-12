"""RI22 canonical source-preserving remaster with editable yaw and tip socket."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import uuid
import bpy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
from remaster_rigellian_static import closed,fit_camera,strip_png
from rigellian_ex_fang_parts import MOVING,PIVOT,FEED_TIP as LANCE_TIP,DISH_AXIS as LANCE_AXIS
FOLDER = ROOT/'sources/objects/rigellian/ex-fang'
MEDIA = ROOT/'gallery/media/objects/rigellian/ex-fang'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    recipe = FOLDER/'recipe.json'
    case = json.loads(recipe.read_bytes())
    source = ROOT/case['source']
    assert sha(source)==case['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.frame_set(1)
    root,yaw = bpy.data.objects['PlacementRoot'],bpy.data.objects['YawPivot']
    assert yaw.parent==root and (yaw.location-PIVOT).length<1e-6
    meshes = [o for o in scene.objects if o.type=='MESH']
    assert len(meshes)==16
    for obj in meshes:
        assert obj.parent==(yaw if obj.name in MOVING else root)
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        assert closed(obj),obj.name
    root['catalogue_id'] = case['id']
    root['forward_axis'] = 'local -Y'
    root['dorsal_axis'] = 'local +Z'
    root['state_contract'] = case['state_contract']
    fit_camera((6,-13,8),meshes)
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.cycles.samples = 32
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    temporary_root = ROOT/'artifacts/rigellian-remaster-temp'
    temporary_root.mkdir(parents=True,exist_ok=True)
    previous = tempfile.mkdtemp

    def workspace_temp(suffix=None,prefix=None,dir=None):
        parent = Path(dir).resolve() if dir else temporary_root
        assert parent.is_relative_to(ROOT.resolve())
        path = parent/((prefix or 'ri22-')+uuid.uuid4().hex+(suffix or ''))
        path.mkdir()
        return str(path)

    tempfile.mkdtemp = workspace_temp
    try:
        bpy.ops.export_scene.gltf(filepath=str(FOLDER/'model.glb'),export_format='GLB',use_selection=True,
                                 export_apply=True,export_extras=True,export_animations=False)
    finally:
        tempfile.mkdtemp = previous
    bpy.ops.wm.save_as_mainfile(filepath=str(FOLDER/'model.blend'),compress=True)
    sys.path.insert(0,str(ROOT/'tools'))
    from publication_support import clean_blend
    target = FOLDER/'model.blend'
    target.write_bytes(clean_blend(target.read_bytes())[0])
    MEDIA.mkdir(parents=True,exist_ok=True)
    for view,direction in [('front-quarter',(6,-13,8)),('front',(0,-16,4)),('rear-quarter',(-7,12,7))]:
        fit_camera(direction,meshes)
        scene.render.filepath = str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
        strip_png(MEDIA/(view+'.png'))
    triangles = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    meta = dict(issue=253,id=case['id'],name=case['name'],source=case['source'],source_sha256=sha(source),
        author_sha256=sha(Path(__file__)),recipe=recipe.relative_to(ROOT).as_posix(),recipe_sha256=sha(recipe),
        binaries={kind:sha(FOLDER/('model.'+kind)) for kind in ['blend','glb']},
        protected_parts=sorted(o.name for o in meshes),triangles=triangles,mesh_nodes=len(meshes),
        footprint=case['footprint'],definition_class=40,construction_updates=48,
        articulation=dict(kind='ri22-manual-yaw-v1',pivot='YawPivot',axis='local +Z',pivot_position=list(PIVOT),
            moving_meshes=MOVING,tip_socket='CollectorAxisSocket',tip_forward_axis='local +Z',
            tip_position_zero_yaw=list(LANCE_TIP),lance_axis_zero_yaw=list(LANCE_AXIS),
            descriptor_formula='2+(((heading+8)>>4)&15)',descriptor_domain=list(range(2,18)),
            legacy_static_base_descriptor_empty=True,complete_directional_building_frames=True,
            model_yaw_phase_sign_calibrated=False,firing_or_pitch_cycle_established=False),
        changes='Evaluated source geometry/materials and articulated hierarchy retained; canonical source/export/evidence/gallery consolidation. No tessellation reduction or invented firing/pitch clip.',
        final_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'model.json').write_bytes((json.dumps(meta,indent=2)+'\n').encode())
    assert sha(source)==case['source_sha256']
    print('RI22_CANONICAL_YAW_SOURCE_PRESERVED',len(meshes),triangles,flush=True)


if __name__=='__main__':
    main()
