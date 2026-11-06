"""Check recorded source-specific evidence; does not run Blender or promote acceptance."""
import hashlib
import json
from pathlib import Path
import re

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/evidence/older-alien-building-runtime'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report=json.loads((ROOT/'source-specific-review.json').read_text())
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    assert report['inventory_sha256']==sha(inventory_path),'Inventory changed'
    assert report['auditor_sha256']==sha(Path(__file__).with_name('verify_older_alien_building_runtime.py'))
    for name,digest in report['verifiers'].items(): assert sha(Path(__file__).with_name(name))==digest
    expected={}
    for record in json.loads(inventory_path.read_text())['records']:
        studies=[s for s in record['available_studies'] if s['present']]
        if record['category']=='buildings' and record['culture']!='terran' and studies[-1]['stage']=='silhouette-study':
            expected[record['id']]=studies[-1]
    assert len(report['records'])==report['models']==len(expected)==114
    assert {r['id'] for r in report['records']}==set(expected)
    for row in report['records']:
        study=expected[row['id']]
        assert row['blend']==study['blend'] and row['files'][row['blend']]==study['sha256']
        for relative,digest in row['files'].items():
            path=(REPO/relative).resolve();assert path.is_relative_to(REPO) and sha(path)==digest
    log=(ROOT/'source-specific-verifier-output.txt').read_text()
    assert 'Traceback' not in log
    assert set(map(int,re.findall(r'CATALOGUE_REOPEN_OK (\d+)',log)))=={r['global_type'] for r in report['records']}
    directional={r['global_type'] for r in report['records'] if r['directional']}
    assert set(map(int,re.findall(r'DIRECTIONAL_RIG_OK (\d+)',log)))==directional
    assert report['directional_models']==len(directional)==15
    for marker in ['CATALOGUE_VERIFICATION_OK 114','DIRECTIONAL_VERIFICATION_OK 15','OLDER_ALIEN_BUILDING_RUNTIME_OK 114 15']:
        assert marker in log
    assert report['source_assets_unchanged'] and report['final_visual_acceptance'] is False
    print('OLDER_ALIEN_BUILDING_EVIDENCE_OK',report['models'],report['directional_models'])


if __name__=='__main__': main()
