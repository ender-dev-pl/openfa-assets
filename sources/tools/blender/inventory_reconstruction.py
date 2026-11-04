"""Inventory real catalogue definitions, archive references and unfinished model studies."""
import argparse
import collections
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path


REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'docs/reconstruction/models'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish_text(path,text):
    # Windows viewers can briefly lock an existing generated file. Publish a
    # complete fresh file rather than truncating the authoritative inventory.
    stage=REPO/'artifacts/reconstruction-inventory-stage'
    stage.mkdir(parents=True,exist_ok=True)
    temporary=stage/(uuid.uuid4().hex+path.suffix)
    temporary.write_text(text,encoding='utf-8')
    for attempt in range(10):
        try:
            os.replace(temporary,path)
            return
        except OSError:
            if attempt==9:
                raise
            time.sleep(.2)


def references(value,path='profile'):
    if isinstance(value,dict):
        for key,child in value.items():
            if key=='assetId' or key.endswith('AnimationId'):
                yield path+'.'+key,child
            elif key not in ['id']:
                yield from references(child,path+'.'+key)
    elif isinstance(value,list):
        for index,child in enumerate(value):
            yield from references(child,f'{path}[{index}]')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root',type=Path,default=REPO.parent/'legacy')
    args=parser.parse_args()
    sys.path.insert(0,str(args.legacy_root/'tools'))
    from fragile256 import read_archive
    gameplay_path=REPO/'content/standard/catalogues/legacy-gameplay.json'
    buildings_path=REPO/'content/standard/catalogues/legacy-buildings.json'
    domain_path=REPO/'content/standard/presentation/legacy-domain.json'
    gameplay,buildings,domain=read(gameplay_path),read(buildings_path)['buildings'],read(domain_path)
    programme=read(OUT/'programme.json')
    body_order_path=REPO/programme['scaffold_body_order_evidence']
    construction_path=REPO/programme['shared_construction_index']
    construction=read(construction_path)
    limits_path=REPO/programme['scaffold_stage_limits']
    limits={r['id']:r for r in read(limits_path)['records']}
    construction_dependencies={item['id']:item for item in construction['building_dependencies']}
    construction_families={item['key']:item for item in construction['families']}
    functional_path=REPO/programme['functional_text_index']
    functional={item['id']:item for item in read(functional_path)['records']}
    reviews={(item['category'],item['id']):item for item in read(OUT/'review-ledger.json')['reviews']}
    assets={item['id']:item for item in domain['assets']}
    animations={item['id']:item for item in domain['animations']}
    archives={}

    def archive(directory,name):
        key=(directory,name)
        if key not in archives:
            file=args.legacy_root/directory/name
            if file.is_file():
                _,payload,entries=read_archive(file)
                archives[key]=(payload,{entry.name.casefold():entry for entry in entries})
            else:
                archives[key]=(b'',{})
        return archives[key]

    def source(directory,entry,archive_name=None,video=False):
        result={'directory':directory,'entry':entry,'kind':'rotation-video' if video else 'sprite-sheet'}
        if video:
            file=args.legacy_root/directory/entry
            result.update(present=file.is_file(),sha256=digest(file) if file.is_file() else None)
            result['palette_status']='requires-video-palette-decoding'
        else:
            name=archive_name or directory
            payload,entries=archive(directory,name)
            found=entries.get(entry.casefold())
            result.update(archive=name,present=found is not None)
            if found:
                result.update(sha256=hashlib.sha256(payload[found.offset:found.offset+found.length]).hexdigest(),payload_bytes=found.length)
            meta=args.legacy_root/directory/'png'/(Path(entry).stem+'.json')
            if meta.is_file():
                decoded=read(meta)
                result['decoded_metadata_sha256']=digest(meta)
                result['frame_count']=len(decoded.get('frames',[]))
                result['palette_status']='embedded' if decoded.get('palette',{}).get('embedded') else 'external-palette-binding-required'
            else:
                result['palette_status']='not-yet-decoded'
        return result

    def profile_sources(profile):
        found=[]
        for role,reference in references(profile):
            animation=animations.get(reference)
            asset_id=animation['assetId'] if animation else reference
            assert asset_id in assets,(role,reference)
            asset=assets[asset_id]
            definition=asset['source']
            directory=definition.get('directoryName')
            entry=definition.get('entryName') or definition.get('fileName')
            if not directory or not entry:
                found.append({'role':role,'asset_id':asset_id,'kind':'non-legacy-source','source':definition})
                continue
            item=source(directory,entry,definition.get('archiveName'),definition['type']=='legacy-video')
            item.update(role=role,asset_id=asset_id)
            if animation:
                item['animation_id']=reference
            found.append(item)
        return found

    def studies(category,definition):
        paths=[]
        index=definition.get('legacy',{}).get('globalType',definition.get('legacy',{}).get('globalTypeIndex'))
        if category=='buildings':
            recipe=building_recipes[definition['id']]
            paths.append(('silhouette-study',REPO/'docs/assets/bootstrap-3d/full-catalogue'/recipe['culture']/recipe['preview'].lower()/'model.blend'))
            if definition['factionId'].endswith('/terran'):
                paths.append(('refined-study',REPO/f'docs/assets/bootstrap-3d/terran-refined/pb{index:02}/model.blend'))
        elif definition['id']=='openfa:transporter':
            paths.append(('transporter-study',REPO/'docs/assets/bootstrap-3d/transporter-inspired/transporter.blend'))
        for study in programme['additional_studies']:
            if study['category']==category and study['id']==definition['id']:
                paths.append((study['stage'],REPO/study['blend']))
        result=[{'stage':stage,'blend':str(path.relative_to(REPO)).replace('\\','/'),
                 'present':path.is_file(),'sha256':digest(path) if path.is_file() else None,
                 'final_visual_acceptance':'not-established'} for stage,path in paths]
        for item in result:
            registered=next((study for study in programme['additional_studies'] if study['category']==category and study['id']==definition['id'] and study['blend']==item['blend']),None)
            if registered and registered.get('state_exports'):
                item['state_exports']=registered['state_exports']
        return result

    building_recipes={item['building_id']:item for item in read(REPO/'docs/assets/bootstrap-3d/full-catalogue/recipes.json')['buildings']}
    profile_keys={'buildings':'buildingId','ships':'shipId','hardpoints':'hardpointId','missiles':'missileId'}
    profiles={category:{profile[profile_keys[category]]:profile for profile in domain[category]} for category in profile_keys}
    ship_runtime={item['shipId']:item for item in gameplay['presentation']['ships']}
    missile_runtime={item['missileId']:item for item in gameplay['presentation']['missileSurface']['sprites']}
    records=[]
    for category,definitions in [('buildings',buildings),('ships',gameplay['ships']),('hardpoints',gameplay['hardpoints']),('missiles',gameplay['missiles'])]:
        for definition in definitions:
            key=definition['id']
            faction=definition.get('factionId')
            culture=faction.rsplit('/',1)[-1] if faction else 'shared'
            profile=profiles[category].get(key)
            record={'category':category,'id':key,'name':definition.get('displayName') or definition.get('runtime',{}).get('displayName'),
                'workstream_issue':programme['workstreams'][category]['issue'],
                'culture':culture,'legacy_identity':definition.get('legacy',{}),
                'functional_reference':dict(index=programme['functional_text_index'],id=key,review_status=functional[key]['function_review'],description_records=[ref['record'] for ref in functional[key]['descriptions']]),
                'presentation_profile':profile['id'] if profile else None,
                'references':profile_sources(profile) if profile else [],
                'available_studies':studies(category,definition),
                'acceptance':{'reference_views_reviewed':False,'silhouette_and_proportions':False,
                    'high_detail_structure':False,'materials':False,'moving_assemblies':False,
                    'attachment_transforms':False,'native_and_glb_runtime':False,
                    'final_visual_acceptance':False},'open_evidence_questions':[]}
            review=reviews.get((category,key))
            if review:
                assert set(review.get('gates',{}))<=record['acceptance'].keys()
                assert all(isinstance(value,bool) for value in review.get('gates',{}).values())
                record['acceptance'].update(review.get('gates',{}))
                record['acceptance_evidence']=review.get('evidence',{})
                record['reviewed_model']=review.get('model')
            if category=='buildings':
                record['footprint']=[definition['footprintWidth'],definition['footprintHeight']]
                recipe=building_recipes[key]
                dependency=construction_dependencies[key];family=construction_families[dependency['family']]
                limit=limits[key]
                stage_limits=dict(index=programme['scaffold_stage_limits'],**{field:limit[field] for field in ['stage_ceiling_raw','frames_per_tier','max_stage_while_constructing','max_tiers']})
                record['shared_construction_reference']=dict(index=programme['shared_construction_index'],**dependency,stage_limits=stage_limits,studies=[dict(study,sha256=digest(REPO/study['manifest'])) for study in programme.get('scaffold_studies',[]) if study['family']==dependency['family']])
                record['references'].append(dict(source('_B',family['archive_entry']),role='runtime.shared-construction'))
                record['reference_recipe']={'path':'docs/assets/bootstrap-3d/full-catalogue/recipes.json','global_type':recipe['global_type']}
            elif category=='ships':
                runtime=ship_runtime[key]
                record['hardpoint_slots']=definition['hardpointSlots']
                record['attachment_evidence']={'catalogue_mount_coordinates':definition.get('hardpointMounts',[]),
                    'coordinate_space':'legacy ship-designer 2D preview; not recovered 3D sockets',
                    'three_dimensional_sockets':'not-established',
                    'source':'docs/legacy/ship-hardpoints.md and legacy-gameplay.json'}
                for role,field in [('surface','surfaceArchiveEntryNames'),('atmospheric','atmosphericArchiveEntryNames')]:
                    candidates=[source('_S',entry) for entry in runtime.get(field,[])]
                    record.setdefault('runtime_variants',{})[role]={'ordered_candidates':candidates,
                        'selected_first_available':next((candidate['entry'] for candidate in candidates if candidate['present']),None)}
                preview=runtime.get('previewArchiveEntryName')
                if preview:
                    record['references'].append(dict(source('_MA',preview),role='runtime.catalogue-preview'))
                if len(definition.get('hardpointMounts',[]))<definition['hardpointSlots']:
                    record['open_evidence_questions'].append('Catalogue provides fewer 2D mount coordinates than equipment slots; recover attachment geometry.')
            elif category=='missiles':
                record['references'].append(dict(source('_M',missile_runtime[key]['archiveEntryName']),role='runtime.surface-flight'))
                record['flight_frame_count']=gameplay['presentation']['missileSurface']['frameCount']
            elif category=='hardpoints':
                record['shared_definition_scope']='Global equipment definition; race-specific mesh variants not established.'
                record['open_evidence_questions'].append('Determine whether visible mounts differ by culture; do not multiply shared definitions or assume shared geometry without evidence.')
            if not profile:
                record['open_evidence_questions'].append('No legacy-domain UI presentation profile; use runtime sprite evidence and recover additional views.')
            if any(ref.get('palette_status')=='external-palette-binding-required' for ref in record['references']):
                record['open_evidence_questions'].append('Resolve external palette from renderer/legacy evidence before treating decoded grayscale previews as colour references.')
            if not any(study['present'] for study in record['available_studies']):
                record['open_evidence_questions'].append('No authored source model is registered in this inventory.')
            records.append(record)
    assert len(records)==303 and len({(record['category'],record['id']) for record in records})==303
    counts={category:dict(collections.Counter(record['culture'] for record in records if record['category']==category)) for category in profile_keys}
    required_files=[body_order_path,limits_path,*(REPO/study['manifest'] for study in programme.get('scaffold_studies',[])),construction_path,functional_path,REPO/programme['cultural_style_index'],gameplay_path,buildings_path,domain_path,REPO/'src/OpenFA.Assets/FrontEnd/GameplayAssets.cs',OUT/'programme.json',OUT/'review-ledger.json']
    data={'schema_version':1,'programme_issue':946,'inventory_issue':947,
        'definition_count':len(records),'counts_by_category_culture':counts,
        'unique_mesh_count':'not-established; shared bodies, variants and effects require visual evidence',
        'source_sha256':{str(path.relative_to(REPO)).replace('\\','/'):digest(path) for path in required_files},
        'acceptance_policy':'Prior art is an available study, not final acceptance. Each gate needs new explicit evidence under programme #946.',
        'records':records}
    OUT.mkdir(parents=True,exist_ok=True)
    publish_text(OUT/'inventory.json',json.dumps(data,indent=2)+'\n')
    lines=['# Complete model reconstruction inventory','',
        'Programme #946; inventory #947. Workstreams: buildings #948, ships/vehicles #949, hardpoints #950, missiles #951.',
        'Rebuild with `python tools/blender/inventory_reconstruction.py --legacy-root ../legacy`; validate with `python tools/blender/verify_reconstruction_inventory.py`.','',
        'This is an evidence and work ledger, not a claim of finished art. All final acceptance gates remain open.','',
        '| Category | Definitions | Available authored studies | UI profiles |','| --- | ---: | ---: | ---: |']
    for category in profile_keys:
        subset=[record for record in records if record['category']==category]
        lines.append(f'| {category} | {len(subset)} | {sum(any(study["present"] for study in record["available_studies"]) for record in subset)} | {sum(record["presentation_profile"] is not None for record in subset)} |')
    lines += ['', '## Culture coverage','', '| Culture | Buildings | Ships/vehicles | Missiles |','| --- | ---: | ---: | ---: |']
    for culture in counts['buildings']:
        lines.append(f'| {culture} | '+ ' | '.join(str(counts[category].get(culture,0)) for category in ['buildings','ships','missiles'])+' |')
    lines += ['', 'The 16 hardpoint definitions are global. Culture-specific geometry is unresolved; 16 is not a proven number of final hardpoint meshes.','',
        '## Confirmed gaps and constraints','',
        '- Every ship and missile has a runtime mapping, even when the separate UI presentation domain lacks a profile.',
        '- Ship candidates preserve runtime fallback order. Archive presence and payload hashes come from the actual installed archives, not filename guesses.',
        '- External-palette sprite references are flagged. A grayscale export is not an accepted colour reference.',
        f'- {sum(item["hardpointSlots"] for item in gameplay["ships"])} ship equipment slots are declared, with only {sum(len(item.get("hardpointMounts",[])) for item in gameplay["ships"])} explicit catalogue mount coordinates. Those coordinates are 2D designer positions, not 3D socket transforms.',
        '- Existing building/transporter files are registered as studies. Final silhouette, construction detail, materials, mechanisms and attachment acceptance are not inferred from their existence.',
        '- Catalogue definitions do not establish the number of unique meshes. Shared bodies, cultural variants, launch states, construction stages and visual effects need explicit investigation.',
        '', '## Evidence required for acceptance','',
        'For each record, first read the original functional description and establish what the object does; use that evidence to distinguish shafts, walls, platforms and mechanisms before interpreting pixel features. Retain multiple correctly paletted reference views and an observed/inferred feature sheet; review actual renders; record refinement decisions; verify editable/native and imported GLB geometry, materials, pivots, attachments and animation; link technical checks and final visual acceptance to a commit.',
        'Only then may the corresponding gates change. Technical exports and polygon counts alone do not establish visual acceptance.',
        '', '## Functional source evidence','',
        '[shared-construction-references.json](shared-construction-references.json) indexes 28 culture/footprint families and maps all 177 buildings to shared construction sprites; decoded references do not accept replacement state models.',
        '', '[functional-text-index.json](functional-text-index.json) links original ENGLISH.TXT records to all 303 definitions. Read mapped descriptions before modelling; source-function review and located text do not accept geometry. See [functional-source-review.md](functional-source-review.md) for coverage, unresolved text banks and the reference-only reading aid.',
        '', '[cultural-architecture.md](cultural-architecture.md) and [cultural-architecture-index.json](cultural-architecture-index.json) summarize six original ENGLISH.CDB Architecture sections with source offsets and hashes. Consult them for new ambiguous details, distinguishing direct building evidence from contextual ship interpretation; do not retrofit older models or resume refining.',
        '', '## Persistent review state','',
        '`programme.json` routes categories to linked issues and registers additional authored studies. Add a category/id/stage/blend entry to `additional_studies` when introducing a new model.',
        '`review-ledger.json` is authored review evidence, separate from the generated inventory. A review contains category/id, a model {blend, sha256}, gates {gate: boolean}, and evidence {gate: [commit/reference/render/check citations]}. Regeneration preserves this ledger. Accepted gates require the exact registered model hash and nonempty evidence; modifying a reviewed model invalidates verification until it is re-reviewed.',
        'The native_and_glb_runtime gate is a scoped Blender native/imported-GLB check. Its model.runtime_evidence binds the export, metadata, reports, scripts and rendered pixels; JSON/Python text uses LF-normalized hashes, while binary files use exact byte hashes. verify_reconstruction_inventory.py rejects missing, changed or mismatched evidence. This gate does not accept artistic quality, animation/state completeness, calibrated attachments or game-client integration.',
        'No existing model has been marked finally accepted by this inventory milestone.','']
    publish_text(OUT/'README.md','\n'.join(lines))
    print('RECONSTRUCTION_INVENTORY_OK',len(records),counts)


if __name__=='__main__':
    main()
