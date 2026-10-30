"""Check exact recorded packaging/UV findings; no Blender execution or final acceptance."""
import hashlib
import json
from pathlib import Path
from collections import Counter

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/evidence/catalogue-texture-uv'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=ROOT/'summary.json';summary=json.loads(path.read_text());counts=Counter();issues=[]
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    assert summary['inventory_sha256']==sha(inventory_path)
    assert summary['auditor_sha256']==sha(Path(__file__).with_name('audit_catalogue_texture_uv.py'))
    selected={r['id']:[s for s in r['available_studies'] if s['present']][-1] for r in json.loads(inventory_path.read_text())['records']}
    assert summary['definitions']==len(summary['records'])==len(selected)==303
    assert {r['id'] for r in summary['records']}==set(selected)
    for row in summary['records']:
        report_path=ROOT/row['report'];report=json.loads(report_path.read_text());study=selected[row['id']]
        assert row['sha256']==sha(report_path) and report['id']==row['id']
        assert report['blend']==study['blend'] and report['blend_sha256']==study['sha256']==sha(REPO/study['blend'])
        assert report['glb_sha256']==sha((REPO/study['blend']).with_suffix('.glb'))
        assert report['source_assets_unchanged'] and report['final_visual_acceptance'] is False
        native=report['native'];glb=report['glb'];counts['native_meshes']+=len(native['objects'])
        counts['native_image_models']+=bool(native['images']);counts['native_images']+=len(native['images'])
        counts['glb_images']+=glb['images'];counts['glb_uv_accessors']+=len(glb['uv_accessors'])
        counts['inspected_glb_uv_coordinates']+=sum(v.get('count',0) for v in glb['uv_accessors'].values() if v['status']=='inspected')
        counts['uninspected_graphs_or_accessors']+=len(native['uninspected'])+len(glb['uninspected'])
        for image in native['images'].values():
            counts['packed_native_images']+=image['packed']
            if 'source_file' in image:
                assert sha(REPO/image['source_file'])==image['source_file_sha256']
                counts['source_bound_native_images']+=1
                counts['matching_packed_source_images']+=image['source_bytes_match_packed']
        if native['issues'] or glb['issues']:
            counts['models_with_dependency_findings']+=1
            counts['native_dependency_diagnostics']+=len(native['issues']);counts['glb_dependency_diagnostics']+=len(glb['issues'])
            issues.append(dict(id=report['id'],native=native['issues'],glb=glb['issues']))
    findings=dict(issue=1110,summary_sha256=sha(path),checker_sha256=sha(Path(__file__)),counts=dict(counts),records=issues,
        final_visual_acceptance=False,scope='Exact current source/report bindings and dependency findings only; not decoded pixel parity, complete shader equivalence, UV distortion/seams or final art acceptance.')
    (ROOT/'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
    print('CATALOGUE_TEXTURE_UV_EVIDENCE_OK',summary['definitions'],json.dumps(dict(counts)))


if __name__=='__main__': main()
