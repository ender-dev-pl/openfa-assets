"""Read-only evaluated corner-normal comparison for existing light-ship exports."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / 'docs/assets/reconstruction/evidence/terran-light-ship-normals'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture():
    graph = bpy.context.evaluated_depsgraph_get()
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH': continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        rotation = evaluated.matrix_world.to_3x3().inverted().transposed()
        positions = [tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices]
        normals = [[] for _ in positions]
        for face in mesh.polygons:
            for index in face.loop_indices:
                normals[mesh.loops[index].vertex_index].append(tuple((rotation @ mesh.corner_normals[index].vector).normalized()))
        result[obj.name] = dict(positions=positions, normals=normals,
                               custom_normals=mesh.has_custom_normals,
                               smooth_faces=sum(f.use_smooth for f in mesh.polygons),
                               flat_faces=sum(not f.use_smooth for f in mesh.polygons))
        evaluated.to_mesh_clear()
    return result


def directional(a, b):
    tree = KDTree(len(b['positions']))
    for i, point in enumerate(b['positions']): tree.insert(point, i)
    tree.balance()
    errors = []
    for point, normals in zip(a['positions'], a['normals']):
        candidates = tree.find_range(point, 1e-5)
        assert candidates, 'No matching geometric position'
        other = [Vector(n) for _, i, _ in candidates for n in b['normals'][i]]
        for normal in normals:
            errors.append(min((Vector(normal)-n).length for n in other))
    return dict(corners=len(errors), maximum_vector_error=max(errors),
                mean_vector_error=sum(errors)/len(errors),
                corners_above_001=sum(e > .001 for e in errors),
                corners_above_01=sum(e > .01 for e in errors))


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for slug in ['combat-eagle', 'scoutship']:
        source = REPO / 'docs/assets/reconstruction/ships/terran' / slug
        hashes = {name:sha(source/name) for name in ['model.blend', 'model.glb', 'model.json']}
        bpy.ops.wm.open_mainfile(filepath=str(source/'model.blend'))
        native = capture()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(source/'model.glb'))
        imported = capture()
        assert native.keys() == imported.keys()
        objects = {}
        for name, a in native.items():
            b = imported[name]
            objects[name] = dict(native={k:v for k,v in a.items() if k not in ['positions','normals']},
                imported={k:v for k,v in b.items() if k not in ['positions','normals']},
                native_to_imported=directional(a,b), imported_to_native=directional(b,a))
        assert hashes == {name:sha(source/name) for name in hashes}
        report = dict(issue=1102, id='openfa:'+slug, blender=bpy.app.version_string,
            auditor_sha256=sha(Path(__file__)), sources=hashes, position_tolerance=1e-5,
            objects=objects, final_visual_acceptance=False, source_assets_unchanged=True,
            scope='Bidirectional nearest corner-normal sets at matching world positions; not face-correspondence, render causality or final art acceptance.')
        (OUTPUT/(slug+'.json')).write_text(json.dumps(report,indent=2)+'\n')
        worst = max(max(o[d]['maximum_vector_error'] for d in ['native_to_imported','imported_to_native']) for o in objects.values())
        print('LIGHT_SHIP_NORMAL_AUDIT_OK', slug, len(objects), worst, flush=True)


if __name__ == '__main__':
    main()
