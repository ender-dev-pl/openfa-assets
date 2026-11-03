"""Register source-bound three-ship refinements and two fresh retention decisions for #190."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CASES={'rattlesnake':('BR0A','Rattlesnake',False),'widowmaker':('BR1C','WidowMaker',True),'heartsblood':('BR2C','HeartsBlood',True),
       'morning-glory':('BR3A','Morning Glory',False),'skymech':('BR4C','SkyMech',True)}
REASONS={
 'rattlesnake':'All 32 populated tiny headings reviewed. The current curved rose body, pale-gold prow and broadened raised aft end already reproduce the visible form and major colour divisions. Existing fitted service fields are sufficient; no additional visible legacy component is established by these 5-19 pixel-wide views. Retain rather than invent machinery; fresh construction/material/UV/helper/GLB/render checks required.',
 'morning-glory':'All 32 populated tiny headings reviewed. The current narrow gold spindle, broad rose terminal, short axial projection and grey opposite tip correspond to the visible shape/colour regions. Exact transverse shape and hidden surface details remain uncertain. Additional machinery is not established at 9-18 pixels across; retain with fresh construction/material/UV/helper/GLB/render checks.',
 'widowmaker':'All 32 headings reviewed. Preserve tapered gold body, rose nose, four genuine aft openings and grey armour/strakes; replace eight hairline neck accents with broad source-visible rose fields. Exact field cross-sections remain authored.',
 'heartsblood':'All sixteen populated even descriptors and empty odd descriptors reviewed. Preserve gold body, four rose radial pods with three bands each, nose and four aft openings; replace eight hairline forward accents with broad rose fields. Empty descriptors do not establish a second geometric state.',
 'skymech':'Both fixed states reviewed. User identifies an orbital station with a much broader central body reaching near the peripheral hemispheres. Replace the thin core/ribs/arm housings with a broad two-chamber core, large axial equipment and radial service casings; add dome fittings/window and concentric module faces. Preserve caps, peripheral modules and alignment axis. User subsequently identifies frame two as scaffolded construction: this finished variant is only phase zero; the separate animated construction variant is required by issue #192.'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,data):
    newline='\r\n' if b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(data,indent=2)+'\n').replace('\n',newline).encode())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True);key=parser.parse_args().model
    code,name,modified=CASES[key];relative=Path('docs/assets/reconstruction/braccatian-refined/ships')/key
    source=ROOT/'sources'/relative if modified else ROOT/'sources/docs/assets/reconstruction/ships/braccatian'/key
    media=ROOT/'gallery/media'/relative if modified else ROOT/'gallery/media/docs/assets/reconstruction/braccatian-refined/ship-retention'/key
    meta=json.loads((source/'model.json').read_text());report=json.loads((media/'validation.json').read_text());model_id='openfa:ship/braccatian/'+key
    assert meta['id']==model_id and report['model']==key and report['decision']==('refined' if modified else 'retained-after-focused-review')
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==report[kind+'_sha256']==sha(source/('model.'+kind))
    baseline=ROOT/'sources/docs/assets/reconstruction/ships/braccatian'/key/'model.blend';assert report['source_blend_sha256']==sha(baseline)
    verifier=ROOT/'sources/tools/blender/verify_refined_braccatian_ships.py';assert report['verifier_sha256']==sha(verifier)
    for name,value in report['verifier_dependencies_sha256'].items():assert sha(verifier.with_name(name))==value
    if modified:
        assert report['generator_sha256']==meta['generator_sha256']==sha(verifier.with_name('refine_braccatian_ships.py'))
        for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    assert report['maximum_native_imported_position_error']<.0001 and report['retained_geometry_uv_normal_equality'] and report['alignment_helpers_preserved']
    for side in ['native','imported']:assert report[side+'_structure']['positive_closed_meshes']==report[side+'_mesh_count']
    for view,r in report['renders'].items():
        assert r['native_sha256']==sha(media/(view+'.png')) and r['imported_sha256']==sha(media/('imported-'+view+'.png'))
    inventory_path=ROOT/'sources/docs/reconstruction/models/inventory.json';inventory=json.loads(inventory_path.read_text())
    row=next(r for r in inventory['records'] if r['id']==model_id)
    if modified:
        study=dict(stage=meta['stage'],blend=(relative/'model.blend').as_posix(),present=True,sha256=meta['blend_sha256'],final_visual_acceptance='not-established')
        previous=[s for s in row['available_studies'] if s['blend']==study['blend']];assert not previous or previous==[study],'Preserve accepted prior studies'
        if not previous:row['available_studies'].append(study)
    ledger_path=ROOT/'sources/docs/reconstruction/models/braccatian-ship-decisions.json'
    evidence={name:sha(ROOT/'sources/docs/reconstruction/models'/name) for name in ['braccatian-refining-baseline.json','braccatian-lore-evidence.json','functional-text-index.json','braccatian-scitek-evidence.json']}
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else dict(issue=190,culture='braccatian',scope='All five ships, including unchanged models',evidence_sha256=evidence,records=[])
    assert ledger['evidence_sha256']==evidence,'Review evidence changed'
    entry=dict(id=model_id,key=code,name=name,decision=report['decision'],reason=REASONS[key],model=(source/'model.blend').relative_to(ROOT).as_posix(),
      blend_sha256=report['blend_sha256'],glb_sha256=report['glb_sha256'],validation=(media/'validation.json').relative_to(ROOT).as_posix(),validation_sha256=sha(media/'validation.json'))
    existing=[r for r in ledger['records'] if r['id']==model_id];assert not existing or existing==[entry],'Accepted decision changed; publish a separate reviewed revision'
    if not existing:ledger['records'].append(entry)
    ledger['records'].sort(key=lambda r:r['key']);ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
    layout_path=ROOT/'project/layout.json';layout=json.loads(layout_path.read_text());destinations={r['destination'] for r in layout['files']}
    paths=[p for p in media.rglob('*') if p.is_file()]
    if modified:paths+=list(source.iterdir())+list((ROOT/'sources/materials/reconstruction/braccatian-refined/ships'/key).glob('*.png'))
    paths += [verifier,verifier.with_name('refine_braccatian_ships.py'),ledger_path,ROOT/'sources/docs/reconstruction/models/braccatian-ship-refinement.md']
    for p in sorted(paths):
        assert p.is_file() and p.suffix!='.blend1';destination=p.relative_to(ROOT).as_posix()
        if destination in destinations:continue
        media_file=destination.startswith('gallery/media/');original=destination.removeprefix('gallery/media/' if media_file else 'sources/')
        assert not any(r['original']==original for r in layout['files'])
        role='media' if media_file else 'material-texture' if original.startswith('materials/') else 'source'
        layout['files'].append(dict(original=original,destination=destination,role=role,ownership='authored'));destinations.add(destination)
    save(inventory_path,inventory);save(layout_path,layout);print('BRACCATIAN_SHIP_DECISION_REGISTERED',key,report['decision'])


if __name__=='__main__':main()
