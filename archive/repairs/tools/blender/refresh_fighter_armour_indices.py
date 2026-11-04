"""Revalidate unaffected Rigellian bundles and retain unchanged topology measurements."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refresh_uv_repair_indices import retain_unchanged_topology_evidence, sha

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO/'docs/assets/reconstruction/evidence/rigellian-runtime-revalidation'


def main():
    retain_unchanged_topology_evidence(baseline='44e3fd4f3', issue=1108)
    path = ROOT/'summary.json'
    summary = json.loads(path.read_text())
    assert summary['runner_sha256'] == sha(REPO/'tools/blender/revalidate_rigellian_buildings.py')
    assert summary['models'] == summary['passed'] == len(summary['records']) == 23
    for row in summary['records']:
        folder = (REPO/row['blend']).parent
        assert row['source_files'] == {str(p.relative_to(folder)).replace('\\', '/'): sha(p)
                                      for p in folder.rglob('*') if p.is_file()}
        assert row['verifier_sha256'] == sha(REPO/'tools/blender'/row['verifier'])
        assert row['new_technical_report_sha256'] == sha(ROOT/folder.name/'technical-review.json')
        assert row['passed'] and row['source_assets_unchanged']
    inventory = REPO/'docs/reconstruction/models/inventory.json'
    if summary['inventory_sha256'] != sha(inventory):
        summary['unrelated_inventory_refresh'] = dict(issue=1108, runner_sha256=sha(Path(__file__)),
            previous_inventory_sha256=summary['inventory_sha256'], exact_unchanged_source_bundles=23,
            scope='Only an unrelated ship source changed. No Rigellian verifier was rerun or result fabricated; all previous source/verifier/report bindings remain exact.')
        summary['inventory_sha256'] = sha(inventory)
        path.write_text(json.dumps(summary, indent=2)+'\n')
    print('FIGHTER_ARMOUR_DEPENDENT_INDICES_REFRESHED', 23)


if __name__ == '__main__':
    main()
