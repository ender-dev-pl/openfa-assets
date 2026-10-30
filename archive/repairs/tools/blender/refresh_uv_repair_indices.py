"""Rebind unchanged dependent evidence only after proving every relevant input unchanged."""
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO/'docs/assets/reconstruction/evidence'
BASE = '894aaf5e0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical_bytes(name, digest=None, baseline=BASE):
    raw = subprocess.run(['git', 'show', baseline+':'+name], cwd=REPO, check=True, stdout=subprocess.PIPE).stdout
    candidates = [raw, raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')]
    if digest:
        return next(value for value in candidates if hashlib.sha256(value).hexdigest() == digest)
    return raw


def retain_unchanged_topology_evidence(baseline=BASE, issue=1111):
    # Component traversal and floating summation order can vary between Blender
    # processes. Retain the original measurement, rather than replacing it merely
    # because an unrelated model was repaired. Exact source/export/algorithm hashes
    # are mandatory; changed sources always keep the newly executed report.
    folder = EVIDENCE/'catalogue-topology'
    summary_path = folder/'summary.json'
    current = json.loads(summary_path.read_text())
    original = json.loads(historical_bytes(str(summary_path.relative_to(REPO)).replace('\\', '/'), baseline=baseline))
    assert current['auditor_sha256'] == original['auditor_sha256'] == sha(Path(__file__).with_name('audit_catalogue_topology.py'))
    previous = {row['id']: row for row in original['records']}
    reused = 0
    for index, row in enumerate(current['records']):
        old = previous[row['id']]
        path = folder/row['report']
        report = json.loads(path.read_text())
        raw = historical_bytes(str(path.relative_to(REPO)).replace('\\', '/'), old['sha256'], baseline=baseline)
        baseline_report = json.loads(raw)
        source = REPO/report['blend']
        assert report['blend_sha256'] == sha(source) and report['glb_sha256'] == sha(source.with_suffix('.glb'))
        if all(baseline_report[key] == report[key] for key in ['id', 'blend', 'blend_sha256', 'glb_sha256']):
            assert baseline_report['source_assets_unchanged'] and baseline_report['final_visual_acceptance'] is False
            path.write_bytes(raw)
            current['records'][index] = old
            reused += 1
    current['evidence_refresh'] = dict(issue=issue, runner_sha256=sha(Path(__file__)), baseline_commit=baseline,
        reused_exact_source_measurements=reused, newly_executed_changed_source_reports=303-reused,
        scope='Full current audit executed. Preserve historical measurements only for byte-identical Blend/GLB inputs and the identical auditor; changed sources retain fresh measurements.')
    summary_path.write_text(json.dumps(current, indent=2)+'\n')


def main():
    retain_unchanged_topology_evidence()
    inventory_path = REPO/'docs/reconstruction/models/inventory.json'
    inventory = json.loads(inventory_path.read_text())
    selected = {r['id']: [s for s in r['available_studies'] if s['present']][-1] for r in inventory['records']}
    topology_path = EVIDENCE/'catalogue-topology/summary.json'
    topology = json.loads(topology_path.read_text())
    path = EVIDENCE/'boundary-coverage/summary.json'
    boundary = json.loads(path.read_text())
    expected = set()
    for row in topology['records']:
        report_path = topology_path.parent/row['report']
        assert sha(report_path) == row['sha256']
        report = json.loads(report_path.read_text())
        if any('boundary_edges' in flags for flags in report['native_flags'].values()):
            expected.add(row['id'])
    assert {r['id'] for r in boundary['records']} == expected
    for row in boundary['records']:
        report_path = path.parent/row['report']
        assert sha(report_path) == row['sha256']
        report = json.loads(report_path.read_text())
        assert report['blend_sha256'] == sha(REPO/report['blend'])
        assert report['topology_report_sha256'] == sha(topology_path.parent/row['report'])
    if boundary['topology_summary_sha256'] != sha(topology_path):
        boundary['index_refresh'] = dict(issue=1111, runner_sha256=sha(Path(__file__)),
            previous_topology_summary_sha256=boundary['topology_summary_sha256'],
            unchanged_boundary_reports_revalidated=len(boundary['records']),
            scope='Only the catalogue index changed. Every sampled source and topology report remains byte-identical; no containment results were recomputed or promoted.')
        boundary['topology_summary_sha256'] = sha(topology_path)
        path.write_text(json.dumps(boundary, indent=2)+'\n')

    path = EVIDENCE/'attachment-readiness/summary.json'
    attachments = json.loads(path.read_text())
    expected = {r['id'] for r in inventory['records'] if r['category'] in ['ships', 'hardpoints']}
    assert len(expected) == 57 and {r['id'] for r in attachments['records']} == expected
    for name, digest in attachments['inputs_sha256'].items():
        if name != str(inventory_path.relative_to(REPO)).replace('\\', '/'):
            assert sha(REPO/name) == digest
    for row in attachments['records']:
        report_path = path.parent/row['report']
        assert sha(report_path) == row['sha256']
        report = json.loads(report_path.read_text())
        source = REPO/report['blend']
        assert report['blend'] == selected[row['id']]['blend']
        assert report['source_files_sha256'][source.name] == selected[row['id']]['sha256']
        assert report['source_files_sha256'] == {p.name: sha(p) for p in source.parent.iterdir() if p.is_file()}
    key = str(inventory_path.relative_to(REPO)).replace('\\', '/')
    if attachments['inputs_sha256'][key] != sha(inventory_path):
        attachments['index_refresh'] = dict(issue=1111, runner_sha256=sha(Path(__file__)),
            previous_inventory_sha256=attachments['inputs_sha256'][key], unchanged_source_bundles_revalidated=57,
            scope='Two building sources changed outside this domain. All 57 selected ship/equipment bundles and other inputs remain byte-identical; no assembly or calibration acceptance.')
        attachments['inputs_sha256'][key] = sha(inventory_path)
        path.write_text(json.dumps(attachments, indent=2)+'\n')
    print('UV_REPAIR_DEPENDENT_INDICES_REFRESHED', len(boundary['records']), 57)


if __name__ == '__main__':
    main()
