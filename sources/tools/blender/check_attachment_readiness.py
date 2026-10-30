"""Validate current attachment audit bindings and summarize evidence without promoting gates."""
import hashlib
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/attachment-readiness'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summary = json.loads((OUTPUT/'summary.json').read_text())
    assert summary['auditor_sha256'] == sha(Path(__file__).with_name('audit_attachment_readiness.py'))
    assert summary['hierarchy_helper_sha256'] == sha(Path(__file__).with_name('audit_catalogue_hierarchy.py'))
    for name, digest in summary['inputs_sha256'].items():
        assert sha(REPO/name) == digest
    inventory = json.loads((REPO/'docs/reconstruction/models/inventory.json').read_text())
    selected = {r['id']: [s for s in r['available_studies'] if s['present']][-1]
                for r in inventory['records'] if r['category'] in ['ships', 'hardpoints']}
    assert len(summary['records']) == len(selected) == 57
    assert {row['id'] for row in summary['records']} == selected.keys()
    counts = Counter()
    rows = []
    diagnostics = []
    maximum_matrix_error = 0
    maximum_declared_position_error = 0
    maximum_declared_forward_error = 0
    for row in summary['records']:
        path = OUTPUT/row['report']
        assert sha(path) == row['sha256']
        report = json.loads(path.read_text())
        source = REPO/report['blend']
        assert report['id'] == row['id'] and report['blend'] == selected[row['id']]['blend']
        assert report['source_files_sha256'][source.name] == selected[row['id']]['sha256']
        assert report['source_files_sha256'] == {p.name: sha(p) for p in source.parent.iterdir() if p.is_file()}
        assert report['source_files_unchanged'] and report['final_visual_acceptance'] is False
        counts[report['category']] += 1
        counts['native_meshes'] += report['native']['meshes']
        counts['native_helpers'] += len(report['native']['helpers'])
        counts['imported_helpers'] += len(report['imported']['helpers'])
        declared_equipment = [name for name in report['declared_sockets'] if name.startswith(('Hardpoint ', 'Equipment '))]
        counts['declared_helpers_in_socket_metadata'] += len(report['declared_sockets'])
        counts['declared_equipment_socket_candidates'] += len(declared_equipment)
        counts['models_with_declared_equipment_sockets'] += bool(declared_equipment)
        counts['declared_engine_helpers'] += sum(name.startswith('Engine ') for name in report['declared_sockets'])
        counts['declared_alignment_helpers'] += sum(name.startswith('Alignment') for name in report['declared_sockets'])
        counts['declared_sensor_helpers'] += sum(name.startswith('Sensor') for name in report['declared_sockets'])
        counts['models_without_placement_root'] += not report['native']['root_present']
        checks = report['native_declared_socket_checks']+report['imported_declared_socket_checks']
        for check in checks:
            if not check['present'] or check.get('position_error', 1) > 1e-5 or check.get('forward_error') is None or check['forward_error'] > 1e-5:
                diagnostics.append(dict(id=report['id'], declaration_check=check))
            else:
                counts['matching_declared_socket_checks'] += 1
                maximum_declared_position_error = max(maximum_declared_position_error, check['position_error'])
                maximum_declared_forward_error = max(maximum_declared_forward_error, check['forward_error'])
        comparison = report['export_comparison']
        if comparison['missing'] or comparison['extra']:
            diagnostics.append(dict(id=report['id'], helper_set_difference=comparison))
        for name, check in comparison['common'].items():
            maximum_matrix_error = max(maximum_matrix_error, check['matrix_error'])
            if not check['parent_equal'] or not check['properties_equal'] or check['matrix_error'] > 1e-5:
                diagnostics.append(dict(id=report['id'], helper=name, comparison=check))
        catalogue = report['catalogue']
        if report['category'] == 'ships':
            counts['catalogue_slots'] += catalogue['hardpointSlots']
            counts['ships_with_slots'] += catalogue['hardpointSlots'] > 0
            if catalogue['hardpointSlots'] and not declared_equipment:
                counts['ships_with_slots_without_declared_equipment_helpers'] += 1
                counts['slots_on_ships_without_declared_equipment_helpers'] += catalogue['hardpointSlots']
            counts['catalogue_2d_mounts'] += len(catalogue.get('hardpointMounts', []))
            counts['ships_with_2d_mounts'] += bool(catalogue.get('hardpointMounts'))
        rows.append(dict(id=report['id'], category=report['category'], culture=report['culture'],
            slots=catalogue.get('hardpointSlots'), ui_mounts=len(catalogue.get('hardpointMounts', [])),
            declared_equipment_socket_candidates=declared_equipment,
            other_helpers=[name for name in report['native']['helpers'] if name not in declared_equipment],
            mapping_acceptance='not established by this audit'))
    result = dict(issue=1115, summary_sha256=sha(OUTPUT/'summary.json'), checker_sha256=sha(Path(__file__)),
        counts=dict(counts), records=rows, diagnostics=diagnostics,
        maximum_root_frame_matrix_error=maximum_matrix_error,
        maximum_declared_position_error=maximum_declared_position_error,
        maximum_declared_forward_error=maximum_declared_forward_error,
        final_visual_acceptance=False,
        scope='Names and counts describe authored candidates only. No accepted slot mapping, mating frame, equipment clearance, calibrated scale or gameplay integration is inferred.')
    (OUTPUT/'findings.json').write_text(json.dumps(result, indent=2)+'\n')
    print('ATTACHMENT_READINESS_EVIDENCE_OK', json.dumps(dict(counts)), 'diagnostics', len(diagnostics))


if __name__ == '__main__':
    main()
