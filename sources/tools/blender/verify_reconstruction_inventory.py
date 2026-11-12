"""Validate inventory coverage and reference hashes directly against catalogues and installed archives."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_runtime_evidence import verify_runtime_evidence
from model_state_exports import verify_state_exports
from index_legacy_functional_text import build_index
from prepare_shared_construction_references import build_index as build_construction_index
from index_scaffold_stage_limits import build_index as build_stage_limits
from probe_scaffold_composition import build_evidence as build_body_order_evidence


def main():
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root',type=Path,default=root.parent/'legacy')
    args=parser.parse_args()
    inventory=json.loads((root/'docs/reconstruction/models/inventory.json').read_text(encoding='utf-8'))
    gameplay=json.loads((root/'content/standard/catalogues/legacy-gameplay.json').read_text(encoding='utf-8'))
    buildings=json.loads((root/'content/standard/catalogues/legacy-buildings.json').read_text(encoding='utf-8'))['buildings']
    domain=json.loads((root/'content/standard/presentation/legacy-domain.json').read_text(encoding='utf-8'))
    programme=json.loads((root/'docs/reconstruction/models/programme.json').read_text())
    body_order_path=(root/programme['scaffold_body_order_evidence']).resolve();assert body_order_path.is_relative_to(root)
    body_order_evidence=build_body_order_evidence(root,args.legacy_root)
    assert json.loads(body_order_path.read_text())==body_order_evidence,'Stale original scaffold body ordering evidence'
    construction_path=(root/programme['shared_construction_index']).resolve();assert construction_path.is_relative_to(root)
    construction=build_construction_index(root,args.legacy_root,check=True)
    assert json.loads(construction_path.read_text())==construction,'Stale shared construction reference index'
    limits_path=(root/programme['scaffold_stage_limits']).resolve();assert limits_path.is_relative_to(root)
    expected_limits=build_stage_limits(root,args.legacy_root)
    assert json.loads(limits_path.read_text())==expected_limits,'Stale original scaffold stage limits'
    limits={r['id']:r for r in expected_limits['records']}
    dependencies={item['id']:item for item in construction['building_dependencies']}
    families={item['key']:item for item in construction['families']}
    for study in programme.get('scaffold_studies',[]):
        manifest=(root/study['manifest']).resolve();assert manifest.is_relative_to(root)
        meta=json.loads(manifest.read_text());assert meta['family']==study['family'] and not meta['final_visual_acceptance']
        assert meta['reference_sha256']==hashlib.sha256(construction_path.read_bytes()).hexdigest()
        assert meta['stage_limits_sha256']==hashlib.sha256(limits_path.read_bytes()).hexdigest()
        family_limit=next(f for f in expected_limits['families'] if f['family']==study['family'])
        assert meta['required_max_stage']==family_limit['max_required_stage'] and meta['required_max_tiers']==family_limit['max_required_tiers']
        assert [case['total_stage'] for case in meta['cases']]==list(range(1,family_limit['max_required_stage']+1))
        assert meta['generator_sha256']==hashlib.sha256((root/study['generator']).read_bytes()).hexdigest()
        directory=manifest.parent;digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
        technical=json.loads((directory/'technical-review.json').read_text());renders=json.loads((directory/'render-review.json').read_text())
        for report,script,field in [(technical,study['verifier'],'verifier_sha256'),(renders,study['reviewer'],'reviewer_sha256')]:
            assert report['model_manifest_sha256']==digest and not report['final_visual_acceptance']
            assert report[field]==hashlib.sha256((root/script).read_bytes()).hexdigest()
            assert [case['total_stage'] for case in report['cases']]==[case['total_stage'] for case in meta['cases']]
        if renders.get('body_descriptor_order_verified'):
            assert renders['body_order_evidence_sha256']==hashlib.sha256(body_order_path.read_bytes()).hexdigest()
        for relative,support_digest in technical['support_source_sha256'].items():
            path=(root/relative).resolve();assert path.is_relative_to(root)
            assert hashlib.sha256(path.read_bytes()).hexdigest()==support_digest
        for case,render in zip(meta['cases'],renders['cases']):
            folder=directory/f"stage-{case['total_stage']:02}"
            for extension in ['blend','glb']:
                assert hashlib.sha256((folder/f'model.{extension}').read_bytes()).hexdigest()==case[extension+'_sha256']
            for view,render_digest in render['view_sha256'].items():
                assert hashlib.sha256((folder/(view+'.png')).read_bytes()).hexdigest()==render_digest
    function_path=(root/programme['functional_text_index']).resolve();assert function_path.is_relative_to(root)
    expected_functions,_=build_index(root,args.legacy_root)
    assert json.loads(function_path.read_text())==expected_functions,'Stale original functional source index'
    functional={item['id']:item for item in expected_functions['records']}
    records=inventory['records']
    assert len(records)==inventory['definition_count']==303
    expected={'buildings':buildings,**{category:gameplay[category] for category in ['ships','hardpoints','missiles']}}
    indexed={(record['category'],record['id']):record for record in records}
    assert len(indexed)==len(records)
    for category,definitions in expected.items():
        assert {record['id'] for record in records if record['category']==category}=={item['id'] for item in definitions}
        for item in definitions:
            record=indexed[category,item['id']]
            assert record['legacy_identity']==item.get('legacy',{})
            assert record['functional_reference']==dict(index=programme['functional_text_index'],id=item['id'],review_status=functional[item['id']]['function_review'],description_records=[ref['record'] for ref in functional[item['id']]['descriptions']])
            assert record['culture']==item.get('factionId','shared').rsplit('/',1)[-1]
            if category=='buildings':
                assert record['footprint']==[item['footprintWidth'],item['footprintHeight']]
                dependency=dependencies[item['id']]
                limit=limits[item['id']]
                stage_limits=dict(index=programme['scaffold_stage_limits'],**{field:limit[field] for field in ['stage_ceiling_raw','frames_per_tier','max_stage_while_constructing','max_tiers']})
                assert record['shared_construction_reference']==dict(index=programme['shared_construction_index'],**dependency,stage_limits=stage_limits,studies=[dict(study,sha256=hashlib.sha256((root/study['manifest']).read_bytes()).hexdigest()) for study in programme.get('scaffold_studies',[]) if study['family']==dependency['family']])
                sources=[source for source in record['references'] if source['role']=='runtime.shared-construction']
                assert len(sources)==1 and sources[0]['entry']==families[dependency['family']]['archive_entry'] and sources[0]['present']
            if category=='ships':
                assert record['hardpoint_slots']==item['hardpointSlots']
                assert record['attachment_evidence']['catalogue_mount_coordinates']==item.get('hardpointMounts',[])
    for relative,digest in inventory['source_sha256'].items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest
    archive_cache={}
    checked=0

    def verify_source(source):
        nonlocal checked
        if source['kind']=='non-legacy-source':
            return
        if source['kind']=='rotation-video':
            file=args.legacy_root/source['directory']/source['entry']
            assert file.is_file()==source['present']
            if file.is_file():
                assert hashlib.sha256(file.read_bytes()).hexdigest()==source['sha256']
        else:
            key=(source['directory'],source['archive'])
            if key not in archive_cache:
                file=args.legacy_root/key[0]/key[1]
                entries={}
                if file.is_file():
                    payload=file.read_bytes()
                    table_end=struct.unpack_from('<I',payload,20)[0]
                    for offset in range(24,table_end,24):
                        name=payload[offset:offset+16].split(b'\0',1)[0].decode('ascii').casefold()
                        position,length=struct.unpack_from('<II',payload,offset+16)
                        entries[name]=hashlib.sha256(payload[position:position+length]).hexdigest()
                archive_cache[key]=entries
            found=archive_cache[key].get(source['entry'].casefold())
            assert (found is not None)==source['present'],source
            if found:
                assert found==source['sha256']
            if source.get('decoded_metadata_sha256'):
                file=args.legacy_root/source['directory']/'png'/(Path(source['entry']).stem+'.json')
                assert hashlib.sha256(file.read_bytes()).hexdigest()==source['decoded_metadata_sha256']
                decoded=json.loads(file.read_text(encoding='utf-8'))
                assert len(decoded.get('frames',[]))==source['frame_count']
                embedded=decoded.get('palette',{}).get('embedded')
                assert source['palette_status']==('embedded' if embedded else 'external-palette-binding-required')
        checked+=1

    profiles={'buildings':'buildingId','ships':'shipId','hardpoints':'hardpointId','missiles':'missileId'}
    runtime={item['shipId']:item for item in gameplay['presentation']['ships']}
    missile_runtime={item['missileId']:item for item in gameplay['presentation']['missileSurface']['sprites']}
    for record in records:
        category=record['category']
        matching=[item for item in domain[category] if item[profiles[category]]==record['id']]
        assert record['presentation_profile']==(matching[0]['id'] if matching else None)
        for source in record['references']:
            verify_source(source)
        if category=='ships':
            for role,field in [('surface','surfaceArchiveEntryNames'),('atmospheric','atmosphericArchiveEntryNames')]:
                variant=record['runtime_variants'][role]
                assert [candidate['entry'] for candidate in variant['ordered_candidates']]==runtime[record['id']].get(field,[])
                for candidate in variant['ordered_candidates']:
                    verify_source(candidate)
                selected=next((candidate['entry'] for candidate in variant['ordered_candidates'] if candidate['present']),None)
                assert selected==variant['selected_first_available']
                if role=='surface':
                    assert selected,record['id']
        elif category=='missiles':
            surface=[source for source in record['references'] if source['role']=='runtime.surface-flight']
            assert len(surface)==1 and surface[0]['present']
            assert surface[0]['entry']==missile_runtime[record['id']]['archiveEntryName']
        for study in record['available_studies']:
            file=root/study['blend']
            assert file.is_file()==study['present']
            if file.is_file():
                assert hashlib.sha256(file.read_bytes()).hexdigest()==study['sha256']
            if study.get('state_exports'):
                verify_state_exports(root,record['id'],study)
        for gate,accepted in record['acceptance'].items():
            if accepted:
                assert record.get('acceptance_evidence',{}).get(gate),(record['id'],gate,'acceptance requires explicit evidence')
                model=record['reviewed_model']
                assert model['blend'] in {study['blend'] for study in record['available_studies'] if study['present']}
                file=(root/model['blend']).resolve()
                assert file.is_relative_to(root)
                assert hashlib.sha256(file.read_bytes()).hexdigest()==model['sha256'],(record['id'],'reviewed revision changed')
                if gate=='native_and_glb_runtime': verify_runtime_evidence(root,record)
    print('RECONSTRUCTION_INVENTORY_VERIFIED',len(records),'definitions',checked,'reference occurrences')


if __name__=='__main__':
    main()
