"""Index established ENGLISH.TXT function/name blocks for all reconstruction definitions."""
import argparse
import hashlib
import json
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
TARGET=REPO/'docs/reconstruction/models/functional-text-index.json'
BLOCKS={'buildings':(604,177,'globalType'),'ships':(1146,41,'globalTypeIndex'),
        'missiles':(1038,69,'globalTypeIndex'),'hardpoints':(1198,16,'typeIndex')}
REVIEWED={
 'terran:ship-yard':'Ship construction and underground pressurised hangars accessed through landing pads.',
 'terran:landing-pad':'Surface access for small craft entering or leaving underground hangars.',
 'openfa:building/legacy/048':'Rigellian spacecraft construction facility.',
 'openfa:building/legacy/049':'Rigellian equivalent of the Landing Pad; interpreted with the explicit underground-hangar description.',
 'openfa:building/legacy/050':'Builds and launches research and espionage satellites; not a spacecraft hangar or ore extractor.',
 'openfa:building/legacy/051':'Sensors used for research and observation of neighbouring colonies.'}


def sha(data): return hashlib.sha256(data).hexdigest()


def source_digest(path):
    data=path.read_bytes()
    if path.suffix in ['.json','.py','.java','.c']: data=data.replace(b'\r\n',b'\n')
    return sha(data)


def split_records(raw):
    result=[];offset=0
    for index,value in enumerate(raw.split(b'\0')):
        result.append(dict(index=index,offset=offset,payload=value,text=value.decode('cp1252')))
        offset+=len(value)+1
    return result


def reference(record,kind):
    return dict(record=record['index'],offset=record['offset'],offset_hex=hex(record['offset']),
        byte_length=len(record['payload']),sha256=sha(record['payload']),kind=kind)


def validate_name(category,definition,records):
    first,count,key=BLOCKS[category];index=definition['legacy'][key]
    assert 0<=index<count,(category,index)
    record=records[first+index];expected=definition['legacy'].get('name',definition.get('displayName',''))
    assert record['text'].casefold()==expected.casefold(),('Name block mismatch',category,index,record['text'],expected)
    return index,record


def build_index(root=REPO,legacy_root=None):
    root=Path(root);legacy_root=Path(legacy_root or root.parent/'legacy')
    language=legacy_root/'_TEXT/ENGLISH.TXT';raw=language.read_bytes();records=split_records(raw)
    buildings_path=root/'content/standard/catalogues/legacy-buildings.json'
    gameplay_path=root/'content/standard/catalogues/legacy-gameplay.json'
    buildings=json.loads(buildings_path.read_text())['buildings'];gameplay=json.loads(gameplay_path.read_text())
    assert records[861]['text'].startswith('The basic support building')
    assert records[901]['text'].startswith('The Rigellian CPU')
    assert records[910]['text']=='The Ground Deck is the Rigellian Landing Pad.'
    assert records[911]['text'].startswith('The Probe Launch is where the satellites')
    assert records[1037]['text'].startswith('The Power Tower is equivalent')
    assert records[1038]['text']=='Explosive' and records[1146]['text']=='Assault Fighter' and records[1198]['text']=='Ion Cannon'
    ghidra=root/'tools/GhidraFragileFullDecompile.java';decompile=root/'artifacts/fragile-le-decompilation/FRAGILE.LE.decompiled.c'
    source=ghidra.read_text();assert 'BUILDING_NAME_TEXT_RECORD_FIRST = 604' in source
    assert 'BuildingNameTextByGlobalType' in source and 'BuildingShortDescriptionTextByGlobalType' in source
    decompiled=decompile.read_text();assert 'BuildingNameTextByGlobalType + iVar5 * 4' in decompiled
    items=[];readings=[]
    for category,definitions in [('buildings',buildings),('ships',gameplay['ships']),('missiles',gameplay['missiles']),('hardpoints',gameplay['hardpoints'])]:
        _,count,key=BLOCKS[category];assert len(definitions)==count
        assert sorted(item['legacy'][key] for item in definitions)==list(range(count))
        for definition in definitions:
            index,name=validate_name(category,definition,records);descriptions=[]
            if category=='buildings':
                descriptions.append(reference(records[861+index],'building-long'))
                if index<40: descriptions.append(reference(records[821+index],'building-short'))
            elif category=='missiles' and index<13:
                descriptions.append(reference(records[1133+index],'missile-short-placeholder' if index>=11 else 'missile-short'))
            elif category=='ships' and index==9:
                descriptions.append(reference(records[1197],'spy-satellite-function'))
            item=dict(category=category,id=definition['id'],name=name['text'],global_type=index,
                culture=definition.get('factionId','shared').rsplit('/',1)[-1],name_reference=reference(name,'catalogue-name'),
                descriptions=descriptions,function_review='source-function-reviewed' if definition['id'] in REVIEWED else 'not-reviewed',
                geometry_review=False,narrative_coverage='established-records' if descriptions else 'not-established-in-mapped-blocks')
            if category=='buildings':
                item['footprint']=[definition['footprintWidth'],definition['footprintHeight']]
                item['definition_class']=definition['legacy']['definitionClass']
                item['runtime_role_evidence']=definition['runtime'].get('effects',[])
            elif category=='ships':
                item['runtime_role_evidence']=dict(role_class=definition['legacy'].get('roleClass'),tags=definition.get('tags',[]),
                    production_capabilities=definition.get('production',{}).get('requiredCapabilityIds',[]))
            elif category=='missiles':
                item['runtime_role_evidence']=dict(effect_behavior_id=definition.get('effectBehaviorId'),effect_index=definition['legacy'].get('effectIndex'))
            else: item['runtime_role_evidence']=dict(role=definition['role'])
            if definition['id'] in REVIEWED: item['reviewed_function_summary']=REVIEWED[definition['id']]
            if definition['id']=='openfa:building/legacy/049': item['explicit_functional_cross_reference']='terran:landing-pad'
            items.append(item)
            readings.append((item,[(ref,records[ref['record']]['text']) for ref in descriptions]))
    assert len(items)==303 and len({item['id'] for item in items})==303
    assert set(REVIEWED)<={item['id'] for item in items},'Reviewed functions must reference real catalogue IDs'
    assert all(item.get('explicit_functional_cross_reference',item['id']) in {row['id'] for row in items} for item in items)
    result=dict(schema_version=1,issue=981,language='English',source_encoding='windows-1252',
        text_hash_policy='LF-normalized JSON/Python/Java/C; original ENGLISH.TXT payloads and offsets use exact bytes',
        sources=dict(language_file=dict(relative_to_legacy='_TEXT/ENGLISH.TXT',sha256=sha(raw),byte_length=len(raw)),
            building_catalogue_sha256=source_digest(buildings_path),gameplay_catalogue_sha256=source_digest(gameplay_path),
            ghidra_naming_source_sha256=source_digest(ghidra),decompile_sha256=source_digest(decompile)),
        mapping=dict(name_blocks={key:dict(first=value[0],count=value[1]) for key,value in BLOCKS.items()},
            building_long_description_first=861,terran_building_short_description_first=821,
            terran_missile_short_description_first=1133,spy_satellite_description_record=1197,
            basis='177 building names match Ghidra record 604+globalType; all 303 names match catalogue global indices. Ordered description blocks have checked boundary/identity anchors.',
            limitation='This verifies text-block correspondence, not every runtime long-description lookup or text in other banks such as ENGLISH.CDB.'),
        coverage=dict(definitions=303,name_records=303,building_long_descriptions=177,terran_building_short_descriptions=40,
            terran_missile_short_descriptions=13,missile_placeholder_descriptions=2,ship_narrative_records=1,
            narrative_mapping_not_established=sum(not item['descriptions'] for item in items),function_sources_reviewed=len(REVIEWED)),
        policy='Located text is not a completed function/geometry review. Runtime roles supplement but do not replace original descriptions. Read the description before interpreting shapes.',
        records=items,final_visual_acceptance=False)
    return result,readings


def reading_aid(readings,folder):
    folder.mkdir(parents=True,exist_ok=True);lines=['# Original functional text: reference-only reading aid','',
        'Generated from the installed ENGLISH.TXT. No model or game asset embeds this source text.','']
    for item,descriptions in readings:
        lines.extend([f"## {item['category']}: {item['name']} ({item['id']})",''])
        for ref,text in descriptions: lines.extend([f"Record {ref['record']}, offset {ref['offset_hex']}, {ref['kind']}",'',text,''])
        if not descriptions: lines.extend(['No narrative mapping established in the indexed blocks; other sources remain unreviewed.',''])
    (folder/'functional-reading-aid.md').write_text('\n'.join(lines),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    parser.add_argument('--show',help='Catalogue ID whose original mapped descriptions should be printed')
    parser.add_argument('--legacy-root',type=Path,default=REPO.parent/'legacy');args=parser.parse_args()
    result,readings=build_index(legacy_root=args.legacy_root)
    if args.check: assert json.loads(TARGET.read_text())==result,'Stale functional text index'
    else:
        TARGET.write_text(json.dumps(result,indent=2)+'\n')
        reading_aid(readings,REPO/'artifacts/issue-981-functional-text')
    if args.show:
        item,descriptions=next((item,texts) for item,texts in readings if item['id']==args.show)
        print(item['name'],item['id'])
        for ref,text in descriptions: print(ref['kind'],ref['offset_hex'],text)
    print('FUNCTIONAL_TEXT_INDEX_OK',len(result['records']),'definitions',result['coverage'])


if __name__=='__main__': main()
