"""Select one current AC1C model and preserve its completed first editable source."""
from pathlib import Path
import json
from register_achaean_transporter_remaster import write,sha,bind_record

ROOT=Path(__file__).resolve().parents[1]
OBJECT='objects/achaean/dedicated-fighter'


def main():
    out=ROOT/'sources'/OBJECT;report=json.loads((out/'runtime-verification.json').read_text())
    for kind in ['blend','glb']:assert sha(out/f'model.{kind}')==report[kind+'_sha256']
    path=ROOT/'sources/docs/reconstruction/models/inventory.json';inventory=json.loads(path.read_text())
    record=next(r for r in inventory['records'] if r['id']==report['id'])
    preserved=record.setdefault('superseded_studies',[])
    for study in record['available_studies']:
        if study['blend']!=OBJECT+'/model.blend':
            assert sha(ROOT/'sources'/study['blend'])==study['sha256']
            if not any(s['blend']==study['blend'] for s in preserved):preserved.append(dict(study,historical_not_for_packaging=True))
    names=['front-quarter','rear-quarter','front','side','top','underside','technical-wireframe','concept',
           'verified-heading-0','verified-heading-4','verified-heading-8','verified-heading-12','verified-heading-20']
    views=[dict(label=n.replace('-',' ').title(),image='gallery/media/'+OBJECT+'/'+n+'.png') for n in names]
    if (ROOT/'gallery/media'/OBJECT/'concept-model-comparison.jpg').is_file():
        views.append(dict(label='Concept and actual imported GLB',image='gallery/media/'+OBJECT+'/concept-model-comparison.jpg'))
    record['available_studies']=[dict(stage='legacy-hi-def-remaster',blend=OBJECT+'/model.blend',present=True,
        sha256=report['blend_sha256'],final_visual_acceptance='awaiting-user-review',views=views)]
    record['selected_refinement']=dict(issue=236,blend=OBJECT+'/model.blend',glb=OBJECT+'/model.glb',
        source_sha256=report['blend_sha256'],export_sha256=report['glb_sha256'],proposed_world_size=96,
        scale_status='Authored size assumption; current generic fallback96; client acceptance separate')
    record['acceptance'].update(reference_views_reviewed=True,native_and_glb_runtime=True)
    record['functional_reference']['review_status']='reviewed-no-object-specific-narrative-mapped'
    write(out/'model.json',dict(id=report['id'],issue=236,canonical_blend='sources/'+OBJECT+'/model.blend',
        canonical_glb='sources/'+OBJECT+'/model.glb',blend_sha256=report['blend_sha256'],glb_sha256=report['glb_sha256'],
        triangles=report['triangles'],mesh_batches=report['mesh_batches'],materials=1,packed_maps=2,
        shared_cultural_materials='sources/materials/achaean/dedicated-ore-transporter',local_forward='-Y',local_up='+Z',
        native_max_extent=18,proposed_world_size=96,current_client_fallback_size=96,equipment_slots=4,
        calibrated_sockets=0,operational_animations=[],preserved_historical_sources=preserved,
        visual_acceptance='Author review completed; final user/client acceptance separate'))
    bind_record(ROOT,record)
    write(path,inventory)
    layout_path=ROOT/'project/layout.json';layout=json.loads(layout_path.read_text());known={i['destination'] for i in layout['files']}
    paths=list(out.iterdir())+list((ROOT/'gallery/media'/OBJECT).iterdir())
    paths += [ROOT/'sources/tools/blender/remaster_achaean_fighter.py',ROOT/'sources/tools/blender/verify_achaean_fighter_remaster.py']
    for p in sorted(paths):
        rel=p.relative_to(ROOT).as_posix()
        if p.is_file() and rel not in known:layout['files'].append(dict(original=rel,destination=rel,role='media' if rel.startswith('gallery/') else 'source',ownership='authored'))
    write(layout_path,layout);print('FIGHTER_REGISTERED',report['triangles'])


if __name__=='__main__':main()
