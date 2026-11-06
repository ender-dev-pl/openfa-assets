"""Validate registered pose-export provenance without inferring artistic acceptance."""
import hashlib
import json
from pathlib import Path


def digest(path):
    data=path.read_bytes()
    if path.suffix in ['.json','.py']: data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


def inside(root,path):
    root=Path(root).resolve();target=(root/path).resolve()
    assert target.is_relative_to(root),'State evidence path leaves repository'
    assert target.is_file(),'Missing state evidence: '+str(path)
    return target


def verify_state_export_data(root,identity,study,index_path,index):
    root=Path(root).resolve();folder=index_path.parent
    blend=inside(root,study['blend']);meta=json.loads(blend.with_name('model.json').read_text())
    assert index['text_hash_policy']=='lf-for-json-and-python'
    assert index['id']==identity==meta['id'],'State catalogue identity differs'
    assert index['revision']==meta['revision'],'State export revision is stale'
    assert index['source_blend_sha256']==meta['blend_sha256']==digest(blend),'State source Blend changed'
    assert index['source_glb_sha256']==meta['glb_sha256']==digest(blend.with_suffix('.glb')),'State source GLB changed'
    evidence=inside(root,meta['animation']['legacy_state_evidence'])
    assert index['mechanism_evidence_sha256']==digest(evidence),'Mechanism evidence changed'
    generator=inside(root,study['state_exports']['generator'])
    assert index['generator_sha256']==digest(generator),'State generator changed'
    assert index['altitude_bands']==json.loads(evidence.read_text())['legacy_mapping']['signed_altitude_bands']
    assert index['no_attached_ship_descriptor']==2
    assert [state['descriptor'] for state in index['states']]==list(range(2,18)),'Incomplete or duplicated descriptor domain'
    covered=[];assets=set()
    for item in index['exports']:
        assert item['glb'] not in assets,'Duplicate exported asset';assets.add(item['glb']);covered.extend(item['descriptors'])
        for key in ['glb','native_render','imported_render']:
            assert Path(item[key]).name==item[key],'State artifact must stay in its own directory'
            target=inside(root,str((folder/item[key]).relative_to(root)))
            assert digest(target)==item[key+'_sha256'],'State artifact changed: '+item[key]
        assert item['maximum_geometry_transform_error']<.00003
        assert item['fixed_moving_intersections']==item['separate_moving_stage_intersections']==0
        if 2 in item['descriptors'] or 15 in item['descriptors']:
            expected=0 if 2 in item['descriptors'] else 9
            assert len(item['indicator_visibility'])==2
            assert all(row['visible_sample_rays']==expected and row['total_sample_rays']==9 for row in item['indicator_visibility'])
    assert sorted(covered)==list(range(2,18)),'Exported descriptor coverage differs'
    for state in index['states']:
        item=next(item for item in index['exports'] if state['descriptor'] in item['descriptors'])
        assert state['asset']==item['glb']
    assert index['final_visual_acceptance'] is False
    report=json.loads(inside(root,str((folder/'render-review.json').relative_to(root))).read_text())
    assert report['state_index_sha256']==digest(index_path),'State render review is stale'
    assert report['id']==identity and report['revision']==meta['revision']
    assert report['exports']==len(index['exports'])==len(report['reviews']) and report['descriptors']==16
    assert {row['key'] for row in report['reviews']}=={row['key'] for row in index['exports']}
    for row in report['reviews']:
        assert min(row['margins'])>=24 and row['binary_silhouette_equal']
        assert max(row['mean_rgba_difference'][:3])<1.5
        assert row['alpha_changed_pixels']<=4 and row['maximum_alpha_difference']<=4
    stowed=next(row for row in report['reviews'] if row['key']=='covers-stowed')
    assert min(stowed['red_pixels_by_image_half'])>=8,'Stowed pose hides red fittings'
    assert report['gallery_sha256']==digest(folder/'gallery.png')
    reviewer=inside(root,study['state_exports']['reviewer'])
    assert report['reviewer_sha256']==digest(reviewer),'State render reviewer changed'
    return len(index['exports'])


def verify_state_exports(root,identity,study):
    registration=study['state_exports'];index_path=inside(root,registration['index'])
    assert digest(index_path)==registration['sha256'],'Registered state index changed'
    return verify_state_export_data(root,identity,study,index_path,json.loads(index_path.read_text()))
