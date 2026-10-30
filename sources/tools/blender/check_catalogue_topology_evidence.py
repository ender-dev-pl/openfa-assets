"""Validate exact recorded topology evidence and produce a gap summary; no Blender execution."""
import hashlib
import json
from pathlib import Path
from collections import Counter

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/evidence/catalogue-topology'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=ROOT/'summary.json';summary=json.loads(path.read_text())
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    inventory=json.loads(inventory_path.read_text())
    assert summary['inventory_sha256']==sha(inventory_path)
    assert summary['auditor_sha256']==sha(Path(__file__).with_name('audit_catalogue_topology.py'))
    selected={r['id']:[s for s in r['available_studies'] if s['present']][-1] for r in inventory['records']}
    assert summary['definitions']==len(summary['records'])==len(selected)==303
    assert {r['id'] for r in summary['records']}==set(selected)
    counts=Counter();flagged=[]
    for row in summary['records']:
        report_path=ROOT/row['report'];report=json.loads(report_path.read_text());study=selected[row['id']]
        assert sha(report_path)==row['sha256']
        assert report['id']==row['id'] and report['blend']==study['blend']
        assert report['blend_sha256']==study['sha256']==sha(REPO/study['blend'])
        assert report['glb_sha256']==sha((REPO/study['blend']).with_suffix('.glb'))
        assert report['source_assets_unchanged'] and report['final_visual_acceptance'] is False
        counts['native_meshes']+=len(report['native']);counts['imported_meshes']+=len(report['imported'])
        if report['native_flags'] or report['imported_flags']: flagged.append(dict(id=row['id'],native=report['native_flags'],imported=report['imported_flags']))
        if report['native_flags']==report['imported_flags']: counts['identical_flag_sets']+=1
        assert report['object_names_equal'] and report['native'].keys()==report['imported'].keys()
        for label in ['native','imported']:
            for obj in report[label].values():
                counts[label+'_raw_boundary_meshes']+=bool(obj['raw']['boundary_edges'])
                counts[label+'_vertices_merged']+=obj['vertices_merged']
                counts[label+'_tiny_faces']+=obj['welded']['tiny_faces']
            for issues in report[label+'_flags'].values():
                counts.update(label+'_meshes_with_'+issue for issue in issues)
    probe=ROOT/'assault-fighter-winding.json';data=json.loads(probe.read_text())
    assert data['probe_sha256']==sha(Path(__file__).with_name('probe_assault_fighter_winding.py'))
    assert data['source_assets_unchanged']
    source=REPO/'docs/assets/reconstruction/ships/terran/assault-fighter'
    assert data['sources']=={name:sha(source/name) for name in data['sources']}
    report=dict(issue=1107,summary_sha256=sha(path),checker_sha256=sha(Path(__file__)),
        winding_probe_sha256=sha(probe),counts=dict(counts),flagged_definitions=len(flagged),records=flagged,
        final_visual_acceptance=False,
        scope='Checks current exact-byte source and measured report hashes; diagnostic flags require geometric/assembly interpretation and do not accept art or all states.')
    (ROOT/'findings.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CATALOGUE_TOPOLOGY_EVIDENCE_OK',summary['definitions'],json.dumps(dict(counts)),len(flagged))


if __name__=='__main__': main()
