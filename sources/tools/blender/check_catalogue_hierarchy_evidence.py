"""Check recorded hierarchy/pose comparisons; does not run Blender or accept socket calibration."""
import hashlib
import json
import math
from pathlib import Path
from collections import Counter

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/evidence/catalogue-hierarchy'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=ROOT/'summary.json';summary=json.loads(path.read_text());counts=Counter();differences=[]
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    assert summary['inventory_sha256']==sha(inventory_path)
    assert summary['auditor_sha256']==sha(Path(__file__).with_name('audit_catalogue_hierarchy.py'))
    assert summary['glb_parser_sha256']==sha(Path(__file__).with_name('audit_catalogue_texture_uv.py'))
    selected={r['id']:[s for s in r['available_studies'] if s['present']][-1] for r in json.loads(inventory_path.read_text())['records']}
    assert summary['definitions']==len(summary['records'])==len(selected)==303
    assert {r['id'] for r in summary['records']}==set(selected)
    maximum=0
    for row in summary['records']:
        report_path=ROOT/row['report'];report=json.loads(report_path.read_text());study=selected[row['id']]
        assert row['sha256']==sha(report_path) and report['id']==row['id']
        assert report['blend']==study['blend'] and report['blend_sha256']==study['sha256']==sha(REPO/study['blend'])
        assert report['glb_sha256']==sha((REPO/study['blend']).with_suffix('.glb'))
        assert report['source_assets_unchanged'] and report['final_visual_acceptance'] is False
        for label in ['native','imported']:
            counts[label+'_nodes']+=len(report[label]['nodes'])
            for node in report[label]['nodes'].values(): assert all(math.isfinite(v) for v in node['first_world_matrix'])
        counts['animated_models']+=bool(report['native']['actions']);counts['glb_clips']+=len(report['glb_clips'])
        comparison=report['comparison'];maximum=max(maximum,comparison['maximum_sampled_matrix_error'])
        for key in ['missing_imported','extra_imported','parent_differences','type_differences','property_differences','nodes_above_1e5','issues']:
            counts[key]+=len(comparison[key])
        if comparison['property_differences'] or comparison['issues'] or comparison['nodes_above_1e5']:
            item=dict(id=report['id'],comparison=comparison)
            if comparison['property_differences']:
                metadata_path=(REPO/study['blend']).parent/'model.json'
                metadata=json.loads(metadata_path.read_text())
                item['external_metadata']=dict(path=str(metadata_path.relative_to(REPO)).replace('\\','/'),sha256=sha(metadata_path),id=metadata.get('id'),footprint=metadata.get('footprint'))
                for name in comparison['property_differences']:
                    properties=report['native']['nodes'][name]['properties']
                    if 'catalogue_id' in properties: assert metadata['id']==properties['catalogue_id']
                    if 'footprint_width' in properties: assert metadata['footprint']==[properties['footprint_width'],properties['footprint_height']]
            differences.append(item)
    result=dict(issue=1112,summary_sha256=sha(path),checker_sha256=sha(Path(__file__)),counts=dict(counts),
        maximum_sampled_matrix_error=maximum,records=differences,final_visual_acceptance=False,
        scope='Exact selected source/report bindings and measured sampled hierarchy/pose evidence only; root property omission is separate from external metadata availability and gameplay calibration.')
    (ROOT/'findings.json').write_text(json.dumps(result,indent=2)+'\n')
    print('CATALOGUE_HIERARCHY_EVIDENCE_OK',summary['definitions'],maximum,json.dumps(dict(counts)))


if __name__=='__main__': main()
