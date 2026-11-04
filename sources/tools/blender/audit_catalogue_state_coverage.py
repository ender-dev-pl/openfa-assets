"""Map existing state evidence without inferring mechanisms from sprite frame counts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from directional_catalogue_rules import requires_rig
from model_state_exports import verify_state_exports

REPO=Path(__file__).resolve().parents[2]
OUTPUT=REPO/'docs/reconstruction/models/state-coverage-audit.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def animation_config(value,path=''):
    if isinstance(value,dict):
        if 'directionalBodyDefinitionIds' in value: yield path,value
        for key,child in value.items(): yield from animation_config(child,path+'/'+key)
    elif isinstance(value,list):
        for index,child in enumerate(value): yield from animation_config(child,path+'/'+str(index))


def ancestor(nodes,name,parent):
    visited=set()
    while name in nodes and name not in visited:
        if name==parent: return True
        visited.add(name);name=nodes[name]['parent']
    return False


def build():
    folder=REPO/'docs/reconstruction/models'
    inventory_path=folder/'inventory.json';inventory=json.loads(inventory_path.read_text())
    reviewed_path=folder/'reviewed-mechanism-semantics.json';reviewed=json.loads(reviewed_path.read_text())
    assert reviewed['reviewer_sha256']==sha(Path(__file__).with_name('review_ri18_state_semantics.py'))
    for relative,digest in reviewed['source_sha256'].items(): assert sha(REPO/relative)==digest
    for relative,digest in reviewed['legacy_source_sha256'].items(): assert sha(REPO.parent/'legacy'/relative)==digest
    reviews={r['id']:r for r in reviewed['records']}
    gameplay_path=REPO/'content/standard/catalogues/legacy-gameplay.json';gameplay=json.loads(gameplay_path.read_text())
    configs=list(animation_config(gameplay));assert len(configs)==1
    config_path,config=configs[0];directional=set(config['directionalBodyDefinitionIds'])
    recipes_path=REPO/'docs/assets/bootstrap-3d/full-catalogue/recipes.json'
    recipes={r['building_id']:r for r in json.loads(recipes_path.read_text())['buildings']}
    hierarchy_folder=REPO/'docs/assets/reconstruction/evidence/catalogue-hierarchy'
    hierarchy_path=hierarchy_folder/'summary.json';hierarchy=json.loads(hierarchy_path.read_text())
    assert hierarchy['inventory_sha256']==sha(inventory_path)
    hierarchy_rows={r['id']:r for r in hierarchy['records']};rows=[]
    for record in inventory['records']:
        study=[s for s in record['available_studies'] if s['present']][-1]
        blend=REPO/study['blend'];assert sha(blend)==study['sha256']
        metadata_path=blend.parent/'model.json'
        if not metadata_path.exists(): metadata_path=blend.parent/'manifest.json'
        metadata=json.loads(metadata_path.read_text())
        hrow=hierarchy_rows[record['id']];hpath=hierarchy_folder/hrow['report'];assert sha(hpath)==hrow['sha256']
        proof=json.loads(hpath.read_text());assert proof['blend_sha256']==study['sha256']
        assert proof['glb_sha256']==sha(blend.with_suffix('.glb'))
        nodes=proof['native']['nodes'];clip=bool(proof['native']['actions']);rig=metadata.get('rotation_rig');yaw=metadata.get('yaw_pivot')
        if rig:
            assert rig['head'] in nodes and rig['base'] in nodes
            assert all(ancestor(nodes,name,rig['head']) for name in rig['moving_meshes'])
        if yaw:
            assert yaw in nodes and all(ancestor(nodes,name,yaw) for name in metadata['moving_meshes'])
        mechanism=metadata.get('animation')
        if clip and rig: kind='authored-heading-preview'
        elif clip and metadata.get('iris_rig'): kind='authored-iris-cycle'
        elif clip and isinstance(mechanism,dict) and mechanism.get('legacy_state_evidence'): kind='source-evidenced-authored-mechanism-cycle'
        elif clip: kind='unclassified-existing-clip'
        elif yaw: kind='manual-unkeyed-yaw-assembly'
        else: kind='no-keyed-node-clip-established'
        state_exports=None
        if study.get('state_exports'):
            count=verify_state_exports(REPO,record['id'],study)
            index_path=REPO/study['state_exports']['index'];index=json.loads(index_path.read_text())
            state_exports=dict(index=study['state_exports']['index'],index_sha256=sha(index_path),
                descriptor_states=len(index['states']),distinct_pose_exports=count,
                descriptors=[r['descriptor'] for r in index['states']],final_visual_acceptance=False)
        references={}
        for ref in record['references']:
            key=(ref.get('directory'),ref.get('entry'),ref.get('kind'))
            item=references.setdefault(key,dict(directory=key[0],entry=key[1],kind=key[2],present=ref.get('present'),
                frame_count=ref.get('frame_count'),sha256=ref.get('sha256'),roles=[]))
            item['roles'].append(ref['role'])
        rows.append(dict(id=record['id'],category=record['category'],culture=record['culture'],blend=study['blend'],
            blend_sha256=study['sha256'],metadata_sha256=sha(metadata_path),hierarchy_report_sha256=sha(hpath),
            existing_animation_kind=kind,active_node_clip=clip,glb_clips=proof['glb_clips'],
            rotation_rig=rig,manual_yaw_pivot=yaw,declared_moving_meshes=metadata.get('moving_meshes',rig.get('moving_meshes',[]) if rig else []),
            runtime_directional_body=record['id'] in directional,
            authoring_directional_rule=requires_rig(recipes[record['id']]) if record['id'] in recipes else False,
            runtime_activity_selectors=[k for k in ['landingPadDefinitionId','satelliteSiloDefinitionId','missileSiloDefinitionId'] if config.get(k)==record['id']],
            registered_state_exports=state_exports,reference_assets=list(references.values()),
            construction_references_deferred=any(r['role']=='runtime.shared-construction' for r in record['references']),
            reviewed_mechanism=reviews.get(record['id']),
            moving_assembly_acceptance=record['acceptance']['moving_assemblies'],
            state_completeness='not-established',final_visual_acceptance=False))
    assert len(rows)==303
    return dict(issue=1113,auditor_sha256=sha(Path(__file__)),source_sha256={str(p.relative_to(REPO)).replace('\\','/'):sha(p) for p in [inventory_path,gameplay_path,recipes_path,hierarchy_path,reviewed_path,Path(__file__).with_name('directional_catalogue_rules.py'),Path(__file__).with_name('model_state_exports.py')]},
        definitions=len(rows),animation_kinds=dict(Counter(r['existing_animation_kind'] for r in rows)),
        runtime_animation_config_path=config_path,runtime_animation_config=config,
        registered_descriptor_exports=sum(bool(r['registered_state_exports']) for r in rows),records=rows,
        policy=['Reference frame counts and inventory video labels do not prove articulation or required state counts.',
                'Manual unkeyed pivots are not missing merely because there is no clip.',
                'Heading previews and operating mechanisms are separate evidence classes.',
                'Runtime allowlist membership and historical authoring rules are different scopes.',
                'Construction references remain deferred; no scaffold generation or acceptance.',
                'First-source coverage is not complete state/variant or final artistic acceptance.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    report=build()
    if args.check: assert json.loads(OUTPUT.read_text())==report,'State coverage audit is stale'
    else: OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
    print('CATALOGUE_STATE_COVERAGE_OK',report['definitions'],json.dumps(report['animation_kinds']),report['registered_descriptor_exports'])


if __name__=='__main__': main()
