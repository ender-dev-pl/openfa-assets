"""Focused retained-missile decisions: fresh native/independent GLB construction and render proof."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_refined_braccatian_ships import mesh_geometry,materials,compare_materials,helpers
from verify_rigellian_crowns import snapshot,drift,compare_render
from verify_skymech_construction import component_volumes
from verify_assault_fighter import check_meshes
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips
EVIDENCE=ROOT/'sources/docs/reconstruction/models/braccatian-missile-evidence.json'
VIEWS={'front-quarter':(7,-12,9),'rear-quarter':(-7,12,8),'plan':(0,0,18),'equipment-detail':(4,-6,8)}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def frame_view(view):
    scene=bpy.context.scene;camera=scene.camera;direction=Vector(VIEWS[view]).normalized();points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    centre=Vector([(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)])
    camera.location=centre+direction*16;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';bpy.context.view_layer.update();local=[camera.matrix_world.inverted()@p for p in points]
    camera.data.ortho_scale=.90 if view=='equipment-detail' else max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.18


def contract(checker,imported=False):
    objects=meshes();check_meshes(objects,allow_packed_images=True);construction=checker.structure(objects,imported=imported);textures=checker.texture_evidence(objects);volumes={o.name:component_volumes(o) for o in objects}
    assert all(len(v)==1 for v in volumes.values());assert not any(o.animation_data for o in bpy.context.scene.objects)
    collection=next(c for c in bpy.data.collections if c.asset_data);assert all(o.name in collection.objects for o in bpy.context.scene.objects if o.type in ['MESH','EMPTY'])
    return dict(construction=construction,textures=textures,closed_positive_meshes=len(objects),component_volumes=volumes)


def run(row):
    slug=row['slug'];source=ROOT/row['model'];meta=json.loads(source.with_suffix('.json').read_text());output=ROOT/'gallery/media/docs/assets/reconstruction/braccatian-refined/missile-retention'/slug;output.mkdir(parents=True,exist_ok=True)
    for ext in ['blend','glb']:assert sha(source.with_suffix('.'+ext))==meta[ext+'_sha256']==row[ext+'_sha256']
    checker=importlib.import_module('verify_braccatian_'+slug.replace('-','_'));checker.ROOT=source.parent
    for key,name in [('generator_sha256','build_braccatian_'+slug.replace('-','_')+'.py'),('parts_sha256','braccatian_'+slug.replace('-','_')+'_parts.py')]:assert meta[key]==sha(Path(__file__).with_name(name))
    for n,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(n))==digest
    for frame in row['decoded_frames']:assert sha(ROOT/frame['png'])==frame['png_sha256']
    wear=json.loads((source.parent/'authored-wear.json').read_text());assert sha(source.parent/'authored-wear.json')==meta['authored_wear_sha256'];assert wear['generator_sha256']==sha(Path(__file__).with_name('author_braccatian_'+slug.replace('-','_')+'_wear.py'))
    layout={r['original']:r['destination'] for r in json.loads((ROOT/'project/layout.json').read_text())['files']}
    for n,digest in wear['images'].items():
        original=(source.parent/n).relative_to(ROOT/'sources').as_posix();assert sha(ROOT/layout[original])==digest
    bpy.ops.wm.open_mainfile(filepath=str(source));geometry={o.name:mesh_geometry(o) for o in meshes()};native=snapshot();native_helpers=helpers();native_materials=materials();native_normals=checker.normal_evidence(meshes(),authored=True);native_contract=contract(checker)
    assert all(mesh_geometry(o)==geometry[o.name] for o in meshes()),'Read-only review altered native geometry/UVs/normals'
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    for view in VIEWS:frame_view(view);scene.render.filepath=str(output/(view+'.png'));bpy.ops.render.render(write_still=True)
    collection=next(c for c in bpy.data.collections if c.asset_data)
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name];bpy.ops.import_scene.gltf(filepath=str(source.with_suffix('.glb')))
    imported=snapshot();imported_helpers=helpers();compare_materials(native_materials,materials());imported_contract=contract(checker,imported=True);assert native_contract['textures']==imported_contract['textures'];assert native_contract['construction']['geometric_vertices']==imported_contract['construction']['geometric_vertices'];assert native.keys()==imported.keys() and native_helpers.keys()==imported_helpers.keys();position_error=helper_error=normal_error=0
    for name,a in native.items():
        b=imported[name];assert a['parent']==b['parent'] and a['materials']==b['materials'];position_error=max(position_error,drift(a['points'],b['points']),drift(b['points'],a['points']))
    for name,a in native_helpers.items():
        b=imported_helpers[name];assert a['parent']==b['parent'];helper_error=max(helper_error,max(abs(x-y) for ra,rb in zip(a['matrix'],b['matrix']) for x,y in zip(ra,rb)))
    normals=checker.normal_evidence(meshes())
    for name,points in native_normals.items():
        assert points.keys()==normals[name].keys()
        for p,values in points.items():
            for n in values:normal_error=max(normal_error,min((Vector(n)-Vector(v)).length for v in normals[name][p]))
    assert position_error<1e-5 and helper_error<1e-5 and normal_error<1e-3
    assert glb_clips(source.with_suffix('.glb'))==[] and not any(o.animation_data for o in scene.objects)
    renders={}
    for view in VIEWS:
        frame_view(view);p=output/('imported-'+view+'.png');scene.render.filepath=str(p);bpy.ops.render.render(write_still=True);renders[view]=compare_render(output/(view+'.png'),p,view!='equipment-detail')
    for ext in ['blend','glb']:assert sha(source.with_suffix('.'+ext))==row[ext+'_sha256'],'Accepted missile source was modified'
    names=['verify_refined_braccatian_ships.py','verify_rigellian_crowns.py','verify_skymech_construction.py','verify_assault_fighter.py','verify_rigellian_filtration.py','verify_braccatian_'+slug.replace('-','_')+'.py']
    report=dict(issue=190,id=row['id'],key=row['key'],name=row['name'],decision='retained-after-focused-review',model=row['model'],blend_sha256=row['blend_sha256'],glb_sha256=row['glb_sha256'],generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in names},evidence_sha256=sha(EVIDENCE),blender=bpy.app.version_string,native_mesh_count=len(native),imported_mesh_count=len(imported),native_contract=native_contract,imported_contract=imported_contract,maximum_native_imported_position_error=position_error,maximum_imported_helper_matrix_error=helper_error,maximum_corner_normal_error=normal_error,retained_native_geometry_uv_normals_preserved=True,alignment_helpers_preserved=True,effective_pbr_channels_preserved=True,legacy_descriptors_reviewed=len(row['decoded_frames']),authored_clips=[],renders=renders,acceptance='Fresh actual runtime review; source silhouette comparison and reasoned final retention decision remain separate; hidden sections/alloys and game calibration remain authored/open')
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('BRACCATIAN_MISSILE_RETENTION_VERIFIED',slug,len(native),position_error,normal_error,flush=True)


def main():
    rows=json.loads(EVIDENCE.read_text())['records'];parser=argparse.ArgumentParser();parser.add_argument('--models',nargs='+',choices=[r['slug'] for r in rows],required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    for slug in args.models:run(next(r for r in rows if r['slug']==slug))


if __name__=='__main__':main()
