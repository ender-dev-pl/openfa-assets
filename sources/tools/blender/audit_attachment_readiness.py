"""Inspect existing ship/equipment helpers and declared sockets without editing assets."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_catalogue_hierarchy import asset_objects

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/attachment-readiness'
INPUTS = [
    'docs/reconstruction/models/inventory.json',
    'content/standard/catalogues/legacy-gameplay.json',
    'src/OpenFA.Core/Gameplay/Fleet/ShipYardWorkspaceModel.cs',
    'src/OpenFA.Assets/FrontEnd/LegacyManagementWorkspaceRenderer.ShipConstruction.cs',
    'src/OpenFA.Core/Modding/GameplayItemDefinitions.cs',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value):
    if hasattr(value, 'to_dict'):
        return plain(value.to_dict())
    if hasattr(value, 'to_list'):
        return plain(value.to_list())
    if isinstance(value, dict):
        return {key: plain(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(child) for child in value]
    assert value is None or isinstance(value, (str, bool, int, float)), type(value)
    return value


def axis_vector(value):
    axes = {'local '+sign+axis: Vector(tuple((1 if sign == '+' else -1) if i == n else 0
                                           for i in range(3)))
            for n, axis in enumerate('XYZ') for sign in ['+', '-']}
    assert value in axes, 'Uninterpreted axis declaration: '+str(value)
    return axes[value]


def root_frame(matrix, root, axis):
    assert abs(root.determinant()) > 1e-12, 'Singular root transform'
    relative = root.inverted() @ matrix
    forward = relative.to_3x3() @ axis_vector(axis) if axis else None
    assert all(math.isfinite(v) for row in relative for v in row)
    if forward is not None:
        assert forward.length > 1e-12 and all(math.isfinite(v) for v in forward)
        forward.normalize()
    return dict(matrix=[list(row) for row in relative], position=list(relative.translation),
                forward=list(forward) if forward is not None else None)


def capture(native):
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    objects = asset_objects(native)
    root = next((obj for obj in objects if obj.name == 'PlacementRoot'), None)
    helpers = {}
    for obj in objects:
        if obj.type != 'EMPTY':
            continue
        properties = {key: plain(obj[key]) for key in obj.keys() if key != '_RNA_UI'}
        helpers[obj.name] = dict(parent=obj.parent.name if obj.parent else None,
            properties=properties, root_frame=root_frame(obj.matrix_world,
                root.matrix_world if root else Matrix.Identity(4), properties.get('forward_axis')))
    return dict(root_present=root is not None, meshes=sum(obj.type == 'MESH' for obj in objects), helpers=helpers)


def declared_socket_checks(metadata, state):
    rows = []
    for name, declaration in metadata.get('sockets', {}).items():
        helper = state['helpers'].get(name)
        row = dict(name=name, declaration=declaration, present=helper is not None)
        if helper:
            row['position_error'] = max(abs(a-b) for a, b in zip(declaration['position'], helper['root_frame']['position']))
            direction = Vector(declaration['forward']).normalized()
            actual = helper['root_frame']['forward']
            row['forward_error'] = max(abs(a-b) for a, b in zip(direction, actual)) if actual else None
        rows.append(row)
    return rows


def compare(a, b):
    errors = {}
    for name in sorted(a['helpers'].keys() & b['helpers'].keys()):
        native, imported = a['helpers'][name], b['helpers'][name]
        errors[name] = dict(matrix_error=max(abs(x-y) for r, s in zip(native['root_frame']['matrix'], imported['root_frame']['matrix'])
                                            for x, y in zip(r, s)),
                            parent_equal=native['parent'] == imported['parent'],
                            properties_equal=native['properties'] == imported['properties'])
    return dict(missing=sorted(a['helpers'].keys()-b['helpers'].keys()),
                extra=sorted(b['helpers'].keys()-a['helpers'].keys()), common=errors)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((REPO/INPUTS[0]).read_text())
    gameplay = json.loads((REPO/INPUTS[1]).read_text(encoding='utf-8-sig'))
    definitions = {kind: {entry['id']: entry for entry in gameplay[kind]} for kind in ['ships', 'hardpoints']}
    records = [record for record in inventory['records'] if record['category'] in definitions]
    assert len(records) == 57
    rows = []
    for record in records:
        study = [s for s in record['available_studies'] if s['present']][-1]
        source = REPO/study['blend']
        export = source.with_suffix('.glb')
        metadata_path = source.parent/('manifest.json' if record['id'] == 'openfa:transporter' else 'model.json')
        metadata = json.loads(metadata_path.read_text())
        before = {p.name: sha(p) for p in source.parent.iterdir() if p.is_file()}
        assert before[source.name] == study['sha256']
        definition = definitions[record['category']][record['id']]
        bpy.ops.wm.open_mainfile(filepath=str(source))
        native = capture(True)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(export))
        imported = capture(False)
        assert before == {p.name: sha(p) for p in source.parent.iterdir() if p.is_file()}
        name = f'{len(rows):02}.json'
        result = dict(issue=1115, id=record['id'], category=record['category'], culture=record['culture'],
            blend=study['blend'], source_files_sha256=before, metadata=metadata_path.name,
            catalogue={key: definition[key] for key in ['hardpointSlots', 'hardpointMounts', 'defaultHardpointIds', 'role'] if key in definition},
            declared_sockets=metadata.get('sockets', {}),
            unresolved_metadata=metadata.get('unresolved', []),
            native=native, imported=imported, export_comparison=compare(native, imported),
            native_declared_socket_checks=declared_socket_checks(metadata, native),
            imported_declared_socket_checks=declared_socket_checks(metadata, imported),
            source_files_unchanged=True, final_visual_acceptance=False,
            scope='Helper transforms at frame 1 and authored declarations only. Names, counts and 2D UI coordinates do not establish calibrated slot assignments or a mating interface.')
        (OUTPUT/name).write_text(json.dumps(result, indent=2)+'\n')
        rows.append(dict(id=record['id'], category=record['category'], report=name, sha256=sha(OUTPUT/name)))
        print('ATTACHMENT_READINESS_INSPECTED', record['id'], flush=True)
    summary = dict(issue=1115, blender=bpy.app.version_string, records=rows,
        inputs_sha256={name: sha(REPO/name) for name in INPUTS},
        auditor_sha256=sha(Path(__file__)), hierarchy_helper_sha256=sha(Path(__file__).with_name('audit_catalogue_hierarchy.py')),
        final_visual_acceptance=False, source_files_unchanged=True)
    (OUTPUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print('ATTACHMENT_READINESS_AUDIT_OK', len(rows), flush=True)


if __name__ == '__main__':
    main()
