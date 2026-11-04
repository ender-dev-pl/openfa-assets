"""Normalize all used family assets and original global-type keys for runtime integration."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from culture_scaffold_contract import definitions_for,phases

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/scaffolds/culture-kits'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def build_index():
    limits_path=REPO/'docs/reconstruction/models/scaffold-stage-limits.json'
    limits=json.loads(limits_path.read_text())
    families=[]
    for family in limits['families']:
        if not family['max_required_stage']:continue
        key=family['family']
        folder=ROOT/'families'/key if key!='RIS2' else ROOT.parent/'rigellian/size-2-refined'
        manifest=json.loads((folder/'model.json').read_text())
        masks={}
        if key=='RIS2':
            sequence=json.loads((folder/'construction-sequence.json').read_text())
            masks={case['stage']:case['hide_during_reveal_and_removal'] for case in sequence['stages']}
        cases=[]
        for case in manifest['cases']:
            stage=case.get('stage',case.get('total_stage'))
            asset=folder/f'stage-{stage:02}/model.glb'
            assert sha(asset)==case['glb_sha256']
            relative=str(asset.relative_to(REPO)).replace('\\','/')
            cases.append(dict(stage=stage,frames=case['frames'],glb='sources/'+relative,workspace_glb=relative,
                              glb_sha256=case['glb_sha256'],hide_on_reveal=masks[stage] if key=='RIS2' else case['hide_on_reveal']))
        assert [c['stage'] for c in cases]==list(range(1,family['max_required_stage']+1))
        relative=str((folder/'model.json').relative_to(REPO)).replace('\\','/')
        families.append(dict(family=key,manifest='sources/'+relative,workspace_manifest=relative,
                             manifest_sha256=sha(folder/'model.json'),pitch=manifest['pitch'],stages=cases))
    definitions=[]
    for record in limits['records']:
        sequence=next(d for d in definitions_for(record['family'],limits) if d['id']==record['id'])
        definitions.append(dict(global_type=record['global_type'],**sequence,family=record['family'],
                                construction_updates=record['construction_updates'],frames_per_tier=record['frames_per_tier']))
    assert len(definitions)==177 and sorted(d['global_type'] for d in definitions)==list(range(177))
    assert len(families)==19 and sum(len(f['stages']) for f in families)==281
    return dict(schema_version=1,issue=188,phases=phases(),definitions=definitions,families=families,
                path_base='glb/manifest paths are relative to canonical repository root; workspace_glb/workspace_manifest are relative to assembled workspace root',
                timing='Simulation/presenter-owned; source ceiling is not construction duration; no duration split is prescribed',
                coordinate_system='Blender sources are Z-up; GLB uses standard glTF axis conversion',
                calibration='All pitches remain provisional; fit footprint, height and overhang clearance around the real target building',
                family_selection='Current definition-culture mapping; original ownership-based selection remains unverified',
                source_limits_sha256=sha(limits_path),generator_sha256=sha(Path(__file__)))


if __name__=='__main__':
    data=build_index()
    (ROOT/'integration.json').write_text(json.dumps(data,indent=2)+'\n')
    print('CULTURE_INTEGRATION_INDEX_OK',len(data['definitions']),len(data['families']))
