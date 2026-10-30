"""Check recorded quantitative export evidence without rerunning Blender or accepting art."""
import argparse
import hashlib
import json
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/evidence/older-alien-building-comparisons'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    selected={}
    for record in json.loads(inventory_path.read_text())['records']:
        studies=[s for s in record['available_studies'] if s['present']]
        if record['category']=='buildings' and record['culture']!='terran' and studies[-1]['stage']=='silhouette-study':
            selected[record['id']]=studies[-1]
    rows=[]
    for path in sorted(ROOT.glob('*/runtime-audit.json')):
        data=json.loads(path.read_text());study=selected[data['id']]
        source=(REPO/study['blend']).parent
        assert data['blend']==study['blend'] and data['sources']['model.blend']==study['sha256']
        assert data['sources']=={name:sha(source/name) for name in data['sources']}
        assert data['auditor_sha256']==sha(Path(__file__).with_name('audit_older_alien_building_exports.py'))
        assert data['snapshot_helper_sha256']==sha(Path(__file__).with_name('audit_transporter_runtime.py'))
        assert data['source_assets_unchanged'] and not data['final_visual_acceptance']
        row=dict(id=data['id'],report_sha256=sha(path),meshes=len(data['native']),
            maximum_position_error=max(o['maximum_bidirectional_position_error'] for o in data['comparisons'].values()),
            maximum_bounds_error=max(o['maximum_bounds_error'] for o in data['comparisons'].values()),
            maximum_material_error=data['maximum_material_value_error'])
        if data['render_sha256']:
            for name,digest in data['render_sha256'].items(): assert sha(path.parent/name)==digest
            pixels_path=path.parent/'pixel-review.json';pixels=json.loads(pixels_path.read_text())
            assert pixels['runtime_audit_sha256']==sha(path)
            assert pixels['reviewer_sha256']==sha(Path(__file__).with_name('review_older_alien_building_exports.py'))
            row['pixel_review_sha256']=sha(pixels_path);row['matched_views']=pixels['comparisons']
        rows.append(row)
    assert len(rows)==len(selected)==114 and {r['id'] for r in rows}==set(selected)
    return dict(issue=1105,inventory_sha256=sha(inventory_path),models=len(rows),
        meshes=sum(r['meshes'] for r in rows),rendered_models=sum('matched_views' in r for r in rows),
        records=rows,final_visual_acceptance=False,
        scope='Current exact-byte source/report binding and measured export comparisons; checker does not run Blender or accept final art/state/game integration.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    report=build();path=ROOT/'summary.json'
    if args.check: assert json.loads(path.read_text())==report,'Stale export summary'
    else: path.write_text(json.dumps(report,indent=2)+'\n')
    print('OLDER_ALIEN_EXPORT_SUMMARY_OK',report['models'],report['meshes'],report['rendered_models'])


if __name__=='__main__': main()
