"""Bind existing sampled boundary findings; does not execute containment or accept art."""
import hashlib
import json
from pathlib import Path
from collections import Counter

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/evidence/boundary-coverage'
TOPOLOGY=REPO/'docs/assets/reconstruction/evidence/catalogue-topology'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=ROOT/'summary.json';summary=json.loads(path.read_text());counts=Counter();rows=[]
    assert summary['auditor_sha256']==sha(Path(__file__).with_name('classify_catalogue_boundaries.py'))
    assert summary['topology_summary_sha256']==sha(TOPOLOGY/'summary.json')
    topology=json.loads((TOPOLOGY/'summary.json').read_text());expected={}
    for row in topology['records']:
        report=json.loads((TOPOLOGY/row['report']).read_text())
        names={name for name,issues in report['native_flags'].items() if 'boundary_edges' in issues}
        if names: expected[row['id']]=names
    assert {r['id'] for r in summary['records']}==set(expected)
    for row in summary['records']:
        report_path=ROOT/row['report'];data=json.loads(report_path.read_text())
        assert sha(report_path)==row['sha256'] and data['id']==row['id']
        assert set(data['objects'])==expected[row['id']]
        assert data['blend_sha256']==sha(REPO/data['blend'])
        assert data['topology_report_sha256']==sha(TOPOLOGY/row['report'])
        assert data['source_assets_unchanged'] and data['final_visual_acceptance'] is False
        for name,groups in data['objects'].items():
            counts['boundary_meshes']+=1
            fully_sampled=all(g['covered_samples']==g['sampled_points'] for g in groups)
            counts['meshes_with_every_sample_inside' if fully_sampled else 'meshes_with_partial_or_unestablished_coverage']+=1
            rows.append(dict(id=data['id'],object=name,all_samples_inside=fully_sampled,
                boundary_groups=len(groups),status_counts=dict(Counter(g['status'] for g in groups))))
            for group in groups:
                assert group['sampled_points']==len(group['samples'])<=24
                assert group['covered_samples']==sum(bool(s['inside_closed_objects']) for s in group['samples'])
                counts[group['status']]+=1;counts['sample_points']+=group['sampled_points']
                counts['covered_sample_points']+=group['covered_samples']
                counts['non_loop_boundary_groups']+=not group['closed_wire_loop']
                counts['sample_points_with_ambiguous_candidates']+=sum(bool(s['ambiguous']) for s in group['samples'])
    assert counts['boundary_meshes']==summary['boundary_meshes']==347
    report=dict(issue=1109,summary_sha256=sha(path),checker_sha256=sha(Path(__file__)),
        counts=dict(counts),records=rows,final_visual_acceptance=False,
        scope='Finite sampled evidence only. All-sample containment does not prove complete boundary coverage, manifold assembly, intended function or final quality.')
    (ROOT/'findings.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BOUNDARY_COVERAGE_EVIDENCE_OK',summary['models'],json.dumps(dict(counts)))


if __name__=='__main__': main()
