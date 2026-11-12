"""Index original CDB architecture guidance without distributing its prose or changing prior models."""
import argparse,hashlib,json
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
TARGET=REPO/'docs/reconstruction/models/cultural-architecture-index.json'
# Labels, record numbers and offsets were checked directly in the original NUL-delimited CDB.
CULTURES={
 'rigellian':('>Rigellians',18,0x971,['Ergonomic and elegant construction, including practical mining facilities.','Comfortable and carefully composed, with less ostentation than Artemian luxury.','Research facilities are important to ordinary colony life.'],['Use coherent proportions and readable, carefully integrated interfaces.','Do not infer a universal material, colour or mandatory curved form from elegance alone.']),
 'braccatian':('>Braccatians',47,0x2142,['Architecture expresses display, large scale and lavish decoration.','Communal sporting and clan gatherings retain dedicated space even on mining colonies.'],['Use deliberate hierarchy, substantial forms and supported decorative treatment when references allow.','Do not infer exact heraldry or ritual equipment from general cultural display.']),
 'mikotaj':('>The Mikotaj',76,0x39fa,['Design varies with the task and can look unsuitable for its actual function.','Mining-colony structures resemble extracted ores and are heavy and metallic.','Light, airy, acoustically tuned crystal architecture describes home worlds, not the mining-colony default.','Buildings can aid mental focusing; names communicate emotional associations.'],['Prioritize heavy ore-like metallic colony construction when source geometry is ambiguous.','Do not replace mining facilities with generic transparent crystal towers.','Read the individual function before interpreting a seemingly impractical structure.']),
 'artemian':('>Artemians',105,0x5734,['Hard surfaces and metal are culturally preferred; advanced alloys can be functional or decorative.','Designs favour secure exteriors, open interiors, distinct planes, edges and shell-like forms.','Water and hygiene facilities have unusually strong practical and social importance.'],['Use structured metal shells, legible planar breaks and deliberate alloy contrast.','Do not turn a general affinity for shells into a literal animal model without visual evidence.']),
 'mauna':('>The Mauna',137,0x7bea,['Building design rejects aesthetics, decoration and most comfort.','Mining structures are described as angular concrete blocks, with immediate practical purpose taking precedence.'],['Keep architectural masses blunt, straight and strictly functional; detail should serve construction or maintenance.','Do not override an actual curved ship component merely because the building description rejects curves.']),
 'achaean':('>Achaeans',166,0x9d65,['External forms favour curves, onion domes and occasional slender tower elements.','Interiors are highly decorated and crowded, with low barrel vaults and textile furnishings.','Comfort matters even where Terran observers dislike the visual excess.'],['Use curved silhouettes, supported dome profiles and inhabited complexity when relevant to the reference.','Do not add domes, towers or interior furnishings indiscriminately to small vehicles.'])}


def build():
    path=REPO.parent/'legacy/_TEXT/ENGLISH.CDB';raw=path.read_bytes();records=[];offset=0
    for index,payload in enumerate(raw.split(b'\0')):
        records.append((index,offset,payload));offset+=len(payload)+1
    items=[]
    for culture,(label,index,expected_offset,summary,application) in CULTURES.items():
        _,offset,payload=records[index];assert offset==expected_offset,(culture,hex(offset))
        assert records[index-1][2]==b'>Architecture'
        prior=[r[2].decode('cp1252') for r in records[:index] if r[2].startswith(b'>')]
        assert label in prior
        # Ensure no intervening other culture has captured this Architecture section.
        known={v[0] for v in CULTURES.values()};assert next(h for h in reversed(prior) if h in known)==label
        items.append(dict(culture=culture,heading=label[1:],section='Architecture',record=index,offset=offset,offset_hex=hex(offset),byte_length=len(payload),sha256=hashlib.sha256(payload).hexdigest(),source_summary=summary,authoring_interpretation=application,scope='Direct evidence for architecture; vehicle/ship application is contextual extrapolation, never recovered geometry.'))
    return dict(schema_version=1,issue=1004,source=dict(relative_to_legacy='_TEXT/ENGLISH.CDB',encoding='windows-1252',format='NUL-delimited records with explicit culture and Architecture headings',byte_length=len(raw),sha256=hashlib.sha256(raw).hexdigest()),cultures=items,not_located=[dict(culture='terran',reason='No Terran Architecture heading exists in this located CDB; use actual object references rather than inventing a matching cultural article.')],policy=['Read the individual functional description and correctly paletted reference frames first.','Use cultural prose to guide ambiguous new details; keep source statements separate from authoring interpretation.','Architecture prose does not establish vehicle mechanisms, colours, materials of a specific object, sockets or animation timing.','Preserve existing models; no retroactive refining or retrofit without user direction.','Current pass remains first iterations only, with new-object wear and technical export verification.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();data=build()
    if args.check: assert json.loads(TARGET.read_text(encoding='utf-8'))==data,'Cultural architecture index is stale'
    else: TARGET.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('CULTURAL_ARCHITECTURE_INDEX_OK',len(data['cultures']),'source-anchored architecture sections')


if __name__=='__main__':main()
