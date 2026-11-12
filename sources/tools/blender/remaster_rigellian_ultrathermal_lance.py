"""RI23 canonical source-preserving remaster with editable yaw and tip socket."""
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
from rigellian_ultrathermal_lance_parts import MOVING,PIVOT,LANCE_TIPS,LANCE_AXIS
import bmesh
from mathutils.bvhtree import BVHTree
FOLDER = ROOT/'sources/objects/rigellian/ultrathermal-lance'
MEDIA = ROOT/'gallery/media/objects/rigellian/ultrathermal-lance'


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
    assert len(meshes)==22
    for obj in meshes:
        assert obj.parent==(yaw if obj.name in MOVING else root)
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        assert closed(obj),obj.name
    original_triangles = 0
    reductions = []
    optimized = []
    for obj in meshes:
        obj.data.calc_loop_triangles()
        original_triangles += len(obj.data.loop_triangles)
        if not(obj.name=='RI23 fixed bronze skirt' or obj.name.startswith('RI23 bronze skirt segment ')):
            continue
        before = len(obj.data.loop_triangles)
        points = [v.co.copy() for v in obj.data.vertices]
        previous = BVHTree.FromPolygons(points,[tuple(p.vertices) for p in obj.data.polygons])
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm,angle_limit=.005,use_dissolve_boundaries=False,
                                verts=list(bm.verts),edges=list(bm.edges),delimit={'MATERIAL','UV'})
        assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.calc_loop_triangles()
        current = BVHTree.FromPolygons([v.co for v in obj.data.vertices],[tuple(p.vertices) for p in obj.data.polygons])
        error = max(max(current.find_nearest(p)[3] for p in points),max(previous.find_nearest(v.co)[3] for v in obj.data.vertices))
        assert error<1e-4,(obj.name,error)
        reductions.append(dict(name=obj.name,original_triangles=before,triangles=len(obj.data.loop_triangles),maximum_vertex_surface_error=error))
        optimized.append(obj.name)
    assert len(optimized)==13
    root['catalogue_id'] = case['id']
    root['forward_axis'] = 'local -Y'
    root['dorsal_axis'] = 'local +Z'
    root['state_contract'] = case['state_contract']
    fit_camera((12,-8,7),meshes)
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
        path = parent/((prefix or 'ri23-')+uuid.uuid4().hex+(suffix or ''))
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
    for view,direction in [('front-quarter',(12,-8,7)),('front',(0,-16,4)),('rear-quarter',(-7,12,7))]:
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
        protected_parts=sorted(o.name for o in meshes if o.name not in optimized),optimized_parts=optimized,
        simplification=reductions,original_triangles=original_triangles,triangles=triangles,mesh_nodes=len(meshes),
        footprint=case['footprint'],definition_class=18,construction_updates=57,
        articulation=dict(kind='ri23-dual-lance-yaw-v1',pivot='YawPivot',axis='local +Z',pivot_position=list(PIVOT),
            moving_meshes=MOVING,tip_sockets=[dict(name='LanceTipSocket '+str(side),lance_mesh='RI23 bronze lance '+str(side),position_zero_yaw=list(tip)) for side,tip in LANCE_TIPS.items()],tip_forward_axis='local +Z',
            lance_axis_zero_yaw=list(LANCE_AXIS),
            descriptor_formula='2+(((heading+8)>>4)&15)',descriptor_domain=list(range(2,18)),
            legacy_static_base_descriptor_empty=False,complete_directional_building_frames=False,
            model_yaw_phase_sign_calibrated=False,firing_or_pitch_cycle_established=False),
        changes='Protected upper assembly unchanged; thirteen lower-foot components lose near-coplanar subdivisions at angle .005rad with UV/material boundaries retained and measured surface error below .0001. Refined taper/segments/relief remain; no invented firing/pitch clip.',
        final_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'model.json').write_bytes((json.dumps(meta,indent=2)+'\n').encode())
    assert sha(source)==case['source_sha256']
    print('RI23_CANONICAL_YAW_SOURCE_PRESERVED',len(meshes),triangles,flush=True)


if __name__=='__main__':
    main()
