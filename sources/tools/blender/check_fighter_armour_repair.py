"""Bind the applied armour repair, baseline, actual runtime checks and current pixels."""
import json
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO/'docs/assets/reconstruction/ships/terran/assault-fighter'
OUTPUT = REPO/'docs/assets/reconstruction/evidence/fighter-armour-repair'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proposal = json.loads((OUTPUT/'proposal.json').read_text())
    applied = json.loads((OUTPUT/'applied.json').read_text())
    meta = json.loads((SOURCE/'model.json').read_text())
    technical = json.loads((SOURCE/'technical-review.json').read_text())
    rendered = json.loads((SOURCE/'render-review.json').read_text())
    assert applied['proposal_sha256'] == sha(OUTPUT/'proposal.json')
    assert proposal['probe_sha256'] == sha(REPO/'tools/blender/probe_fighter_armour_tessellation.py')
    assert applied['migration_sha256'] == sha(REPO/'tools/blender/apply_fighter_armour_repair.py')
    assert proposal['helper_sha256'] == applied['helper_sha256'] == meta['helper_sha256']['fighter_plate_topology.py'] == sha(REPO/'tools/blender/fighter_plate_topology.py')
    assert technical['verifier_sha256'] == sha(REPO/'tools/blender/verify_fighter_armour_repair.py')
    assert rendered['reviewer_sha256'] == sha(REPO/'tools/blender/review_fighter_armour_repair.py')
    assert meta['revision'] == applied['revision'] == technical['revision'] == rendered['revision'] == 4
    for ext in ['blend', 'glb']:
        assert proposal['source_hashes'][ext] == applied['previous'][ext+'_sha256']
        assert applied[ext+'_sha256'] == meta[ext+'_sha256'] == technical[ext+'_sha256'] == rendered[ext+'_sha256'] == sha(SOURCE/('model.'+ext))
    assert applied['changes'] == proposal['changes']
    assert applied['saved_native_reopened'] and technical['original_vertices_and_other_meshes_unchanged']
    assert len(proposal['unchanged_mesh_snapshots']) == 138 and len(proposal['original_vertices']) == 12
    for name, digest in proposal['renders'].items():
        assert sha(OUTPUT/name) == digest
    for name, digest in rendered['view_hashes'].items():
        assert sha(SOURCE/(name+'.png')) == digest and rendered['margins'][name] >= 24
    assert all(row['binary_silhouette_different_pixels'] == 0 for row in rendered['before_after'].values())
    assert all(row['binary_silhouette_different_pixels'] == 0 and row['alpha_difference_maximum'] == 0
               and max(row['foreground_mean_rgba_difference'][:3]) < 1.5 for row in rendered['native_imported'].values())
    assert technical['native'].keys() == technical['imported'].keys() == proposal['before'].keys()
    for side in ['native', 'imported']:
        for value in technical[side].values():
            assert value['triangle_signed_volume'] > 0 and value['all_edges_manifold']
            assert not value['nonadjacent_triangle_intersections']
    findings = dict(issue=1108, checker_sha256=sha(Path(__file__)),
        proposal_sha256=sha(OUTPUT/'proposal.json'), applied_sha256=sha(OUTPUT/'applied.json'),
        technical_report_sha256=sha(SOURCE/'technical-review.json'), render_report_sha256=sha(SOURCE/'render-review.json'),
        repaired_panels=12, unchanged_other_meshes=138, all_original_panel_vertices_preserved=True,
        original_intersecting_triangle_pairs=sum(len(row['nonadjacent_triangle_intersections']) for row in proposal['before'].values()),
        original_panels_with_detected_intersections=sum(bool(row['nonadjacent_triangle_intersections']) for row in proposal['before'].values()),
        current_panels_with_detected_intersections=0, native_and_glb_panel_volumes_positive=True,
        before_after_silhouette_views=4, verified_render_files=len(rendered['view_hashes']),
        maximum_native_import_mean_rgb_difference=max(max(row['foreground_mean_rgba_difference'][:3]) for row in rendered['native_imported'].values()),
        final_visual_acceptance=False,
        scope='Technical connectivity correction and current native/import evidence only; not final art, calibrated heading/attachments, full state or game integration acceptance.')
    (OUTPUT/'findings.json').write_text(json.dumps(findings, indent=2)+'\n')
    print('FIGHTER_ARMOUR_REPAIR_EVIDENCE_OK', findings['repaired_panels'], findings['original_intersecting_triangle_pairs'], findings['verified_render_files'])


if __name__ == '__main__':
    main()
