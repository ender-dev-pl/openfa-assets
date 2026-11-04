"""Bind actual forty-building runtime evidence; does not execute Blender or accept art."""
import argparse
import hashlib
import json
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'docs/assets/reconstruction/evidence/refined-terran-runtime'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    log = ROOT/'source-specific-verifier-output.txt'
    text = log.read_text()
    assert 'Traceback' not in text and 'REFINED_TERRAN_VERIFICATION_OK 40' in text
    assert sorted(map(int,re.findall(r'REFINED_TERRAN_VERIFIED (\d+)',text))) == list(range(40))
    rows = []
    for index in range(40):
        slug = f'pb{index:02}'
        path = ROOT/slug/'runtime-audit.json';report = json.loads(path.read_text())
        source = REPO/'docs/assets/bootstrap-3d/terran-refined'/slug
        assert report['sources'] == {name:sha(source/name) for name in report['sources']}
        assert report['auditor_sha256'] == sha(Path(__file__).with_name('audit_refined_terran_runtime.py'))
        assert report['source_assets_unchanged'] and not report['final_visual_acceptance']
        row = dict(id=report['id'], report_sha256=sha(path), meshes=len(report['native']),
            maximum_position_error=max(o['maximum_bidirectional_position_error'] for o in report['comparisons'].values()),
            maximum_bounds_error=max(o['maximum_bounds_error'] for o in report['comparisons'].values()),
            maximum_material_error=report['maximum_material_value_error'])
        if index in [4,5,10,14]:
            pixels_path = ROOT/slug/'pixel-review.json';pixels = json.loads(pixels_path.read_text())
            assert pixels['runtime_audit_sha256'] == sha(path)
            assert pixels['reviewer_sha256'] == sha(Path(__file__).with_name('review_refined_terran_runtime.py'))
            for name,digest in report['render_sha256'].items(): assert sha(ROOT/slug/name) == digest
            row['pixel_report_sha256'] = sha(pixels_path)
            row['matched_view_comparisons'] = pixels['comparisons']
        rows.append(row)
    return dict(issue=1104, verifier_output_sha256=sha(log),
        source_specific_verifier_sha256=sha(Path(__file__).with_name('verify_refined_terran.py')),
        summary_generator_sha256=sha(Path(__file__)), buildings=40, rendered_buildings=4,
        source_assets_unchanged=True, final_visual_acceptance=False, records=rows,
        scope='Checks existing recorded runtime reports/log and exact source hashes; this summarizer does not run Blender or accept final art, states, sockets or game integration.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    report=build();path=ROOT/'summary.json'
    if args.check: assert json.loads(path.read_text())==report,'Stale summary'
    else: path.write_text(json.dumps(report,indent=2)+'\n')
    print('REFINED_TERRAN_RUNTIME_SUMMARY_OK',report['buildings'],report['rendered_buildings'])


if __name__=='__main__': main()
