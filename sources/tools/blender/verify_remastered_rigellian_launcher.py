"""RI18 source preservation, fixed anatomy, rigid poses and matched GLB renders."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import bpy
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).parent))
from remaster_rigellian_launcher import ROOT,FOLDER,MEDIA,CYCLE,STATES,TARGETS,select_clip
from remaster_rigellian_static import fit_camera,strip_png
from verify_rigellian_launcher_candidate import support_checks,descriptors
from audit_rigellian_launcher_source import inspect
from rigellian_launcher_remaster_checks import structure,hardware_sweep


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':
            continue
        assert not obj.modifiers and obj.data.shape_keys is None,obj.name
        obj.data.calc_loop_triangles()
        points = [obj.matrix_world@v.co for v in obj.data.vertices]
        result[obj.name] = dict(points=points,triangles=len(obj.data.loop_triangles),
            materials=sorted({obj.data.materials[p.material_index].name for p in obj.data.polygons}),
            tree=BVHTree.FromPolygons(points,[tuple(p.vertices) for p in obj.data.polygons]))
    return result


def compare(a,b,names):
    error = 0
    for name in names:
        assert a[name]['triangles']==b[name]['triangles'],name
        assert a[name]['materials']==b[name]['materials'],name
        error = max(error,max(b[name]['tree'].find_nearest(p)[3] for p in a[name]['points']),
                    max(a[name]['tree'].find_nearest(p)[3] for p in b[name]['points']))
    assert error<1e-5,error
    return error


VIEWS = [('front-quarter',CYCLE,1,(6,-13,8)),('front',CYCLE,1,(0,-16,7)),
         ('rear-quarter',CYCLE,1,(-7,12,7)),('half-open',CYCLE,16,(6,-13,8)),
         ('open',CYCLE,31,(6,-13,8)),('open-top',CYCLE,31,(0,0,20)),
         ('descriptor09',STATES,9,(6,-13,8)),('descriptor16',STATES,16,(6,-13,8))]


def renders(prefix,offset):
    result = {}
    meshes = [obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    for name,clip,frame,direction in VIEWS:
        select_clip(clip,frame-(int(round(offset)) if clip==STATES else 0))
        fit_camera(direction,meshes)
        bpy.context.scene.camera.data.ortho_scale *= 1.08
        path = MEDIA/(prefix+'-'+name+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        strip_png(path)
        result[path.name] = sha(path)
    return result


def main():
    meta = json.loads((FOLDER/'model.json').read_bytes())
    for kind,expected in meta['binaries'].items():
        assert sha(FOLDER/('model.'+kind))==expected
    source = ROOT/meta['source']
    assert sha(source)==meta['source_sha256']
    assert sha(Path(__file__).with_name('remaster_rigellian_launcher.py'))==meta['author_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    bpy.context.scene.frame_set(1)
    original = geometry()
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'model.blend'),load_ui=False,use_scripts=False)
    select_clip(CYCLE,1)
    native_geometry = geometry()
    preserved_error = compare(original,native_geometry,meta['preserved_components'])
    assert preserved_error<1e-6
    upper_name = 'RI18 stepped green silo casing'
    lower_points = [p for p in original[upper_name]['points'] if p.z<=1.62+1e-7]
    lower_error = max(native_geometry[upper_name]['tree'].find_nearest(p)[3] for p in lower_points)
    assert lower_error<1e-6
    native_form = structure()
    native_report,native_matrices = inspect()
    native_support = support_checks()
    native_hardware = hardware_sweep(select_clip,CYCLE)
    native_offset,native_states = descriptors()
    native_root = [float(v) for row in bpy.data.objects['PlacementRoot'].matrix_world for v in row]
    all_points = [p for item in native_geometry.values() for p in item['points']]
    bounds = [min(p[i] for p in all_points) for i in range(3)]+[max(p[i] for p in all_points) for i in range(3)]
    images = renders('native',native_offset)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:
            bpy.data.objects.remove(obj,do_unlink=True)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(FOLDER/'model.glb'))
    select_clip(CYCLE,1)
    imported_geometry = geometry()
    assert native_geometry.keys()==imported_geometry.keys()
    surface_error = compare(native_geometry,imported_geometry,native_geometry)
    imported_form = structure()
    assert native_form['texture_pixels_and_uvs']==imported_form['texture_pixels_and_uvs']
    imported_report,imported_matrices = inspect()
    imported_support = support_checks()
    imported_hardware = hardware_sweep(select_clip,CYCLE)
    imported_offset,imported_states = descriptors()
    matrix_error = max(abs(a-b) for f in native_matrices for name in native_matrices[f]
        for a,b in zip(native_matrices[f][name],imported_matrices[f][name]))
    descriptor_error = max(abs(a-b) for d in native_states for name in TARGETS
        for a,b in zip(native_states[d][name],imported_states[d][name]))
    assert max(matrix_error,descriptor_error)<1e-5
    for report in [native_report,imported_report]:
        assert all(not row['leaf_fixed_surface_intersections'] for row in report['samples'])
        assert max(report['samples'][30]['open_bore_heights'])<.051
    imported_root = [float(v) for row in bpy.data.objects['PlacementRoot'].matrix_world for v in row]
    assert max(abs(a-b) for a,b in zip(native_root,imported_root))<1e-6
    images.update(renders('imported',imported_offset))
    raw = (FOLDER/'model.glb').read_bytes()
    document = json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    assert {a['name'] for a in document['animations']}=={CYCLE,STATES}
    for animation in document['animations']:
        assert len(animation['channels'])==2
        assert {document['nodes'][c['target']['node']]['name'] for c in animation['channels']}==set(TARGETS)
        assert all(c['target']['path']=='rotation' for c in animation['channels'])
        if animation['name']==STATES:
            assert all(s['interpolation']=='STEP' for s in animation['samplers'])
    helpers = {Path(module.__file__).relative_to(ROOT).as_posix():sha(Path(module.__file__))
        for module in list(sys.modules.values()) if getattr(module,'__file__',None)
        and Path(module.__file__).resolve().is_relative_to(Path(__file__).parent.resolve())}
    report = dict(issue=253,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],
        metadata_sha256=sha(FOLDER/'model.json'),verifier_sha256=sha(Path(__file__)),helpers=helpers,
        native=native_form,imported=imported_form,
        supported_hardware_sweep=dict(native=native_hardware,imported=imported_hardware),
        maximum_bidirectional_surface_error=surface_error,
        protected_surface_error=preserved_error,preserved_lower_casing_surface_error=lower_error,
        native_root_matrix=native_root,imported_root_matrix=imported_root,native_world_bounds=bounds,
        triangles=meta['triangles'],meshes=len(native_geometry),
        material_count=len(document.get('materials',[])),embedded_images=len(document.get('images',[])),
        clips=[a['name'] for a in document['animations']],renders=images,
        sampled_motion=dict(cycle_frames=list(range(1,62)),descriptor_domain=list(range(2,18)),
            leaf_old_body_surface_intersections=False,maximum_axle_leaf_distance=max(native_support,imported_support),
            maximum_cycle_matrix_error=matrix_error,maximum_descriptor_matrix_error=descriptor_error,
            native_descriptor_offset=native_offset,imported_descriptor_offset=imported_offset,
            continuous_sweep_proven=False,descriptor17_composition_verified=False),
        final_artistic_acceptance=False,game_client_integration=False,
        scope='Full bind-geometry/maps and sampled rigid transforms; own-axis hardware seat contacts classified in integer cycle frames; continuous-time sweep and final gallery delivery remain separate.')
    (FOLDER/'runtime-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI18_NATIVE_GLB_GEOMETRY_MAPS_RENDERS_OK',surface_error,matrix_error,descriptor_error,flush=True)


if __name__=='__main__':
    main()
