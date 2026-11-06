"""Run existing checks on current selected older alien sources without rebuilding art."""
import hashlib
import json
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
import verify_full_catalogue
import verify_directional_catalogue

REPO=Path(__file__).resolve().parents[2]
OUTPUT=REPO/'docs/assets/reconstruction/evidence/older-alien-building-runtime'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    inventory=json.loads(inventory_path.read_text())
    rows=[]
    for record in inventory['records']:
        if record['category']!='buildings' or record['culture']=='terran': continue
        present=[s for s in record['available_studies'] if s['present']]
        if not present or present[-1]['stage']!='silhouette-study': continue
        study=present[-1];folder=(REPO/study['blend']).parent
        assert sha(folder/'model.blend')==study['sha256']
        meta=json.loads((folder/'model.json').read_text())
        rows.append(dict(id=record['id'],culture=record['culture'],blend=study['blend'],
            global_type=meta['global_type'],directional=bool(meta.get('rotation_rig')),
            mesh_objects=meta['mesh_objects'],
            files={str((folder/name).relative_to(REPO)).replace('\\','/'):sha(folder/name)
                   for name in ['model.blend','model.glb','model.json']}))
    assert len(rows)==114 and len({r['global_type'] for r in rows})==114
    before=list(sys.argv)
    try:
        sys.argv=[__file__,'--','--ids',','.join(str(r['global_type']) for r in rows)]
        verify_full_catalogue.main()
        directional=[r for r in rows if r['directional']]
        if directional:
            sys.argv=[__file__,'--','--ids',','.join(str(r['global_type']) for r in directional)]
            verify_directional_catalogue.main()
    finally:
        sys.argv=before
    for row in rows:
        assert all(sha(REPO/name)==digest for name,digest in row['files'].items()),'Source changed'
    OUTPUT.mkdir(parents=True,exist_ok=True)
    report=dict(issue=1105,blender=bpy.app.version_string,inventory_sha256=sha(inventory_path),
        auditor_sha256=sha(Path(__file__)),
        verifiers={name:sha(Path(__file__).with_name(name)) for name in ['verify_full_catalogue.py','verify_directional_catalogue.py']},
        models=len(rows),directional_models=len(directional),source_assets_unchanged=True,
        records=rows,final_visual_acceptance=False,
        scope='Existing source-specific catalogue checks and applicable sampled native/imported directional rig motion only; no exhaustive topology, UV/material parity, actual render parity, state completeness or final art acceptance.')
    (OUTPUT/'source-specific-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('OLDER_ALIEN_BUILDING_RUNTIME_OK',len(rows),len(directional),flush=True)


if __name__=='__main__': main()
