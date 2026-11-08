"""Select issue 234's current model without deleting the completed first source."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ID = 'openfa:ship/achaean/dedicated-ore-transporter'
OBJECT = 'objects/achaean/dedicated-ore-transporter'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    old = path.read_bytes() if path.exists() else b''
    text = json.dumps(value, indent=2, ensure_ascii=True)+'\n'
    path.write_bytes(text.replace('\n', '\r\n' if b'\r\n' in old else '\n').encode())


def main():
    out = ROOT/'sources'/OBJECT
    report = json.loads((out/'runtime-verification.json').read_text())
    for name in ['blend', 'glb']:
        assert sha(out/('model.'+name)) == report[name+'_sha256']
    path = ROOT/'sources/docs/reconstruction/models/inventory.json'
    inventory = json.loads(path.read_text(encoding='utf-8'))
    record = next(r for r in inventory['records'] if r['id'] == ID)
    preserved = record.setdefault('superseded_studies', [])
    for study in record['available_studies']:
        if study['blend'] != OBJECT+'/model.blend':
            assert sha(ROOT/'sources'/study['blend']) == study['sha256']
            if not any(s['blend'] == study['blend'] for s in preserved):
                preserved.append(dict(study, historical_not_for_packaging=True))
    views = [{'label': name.replace('-', ' ').title(), 'image': 'gallery/media/'+OBJECT+'/'+name+'.png'}
             for name in ['front-quarter', 'rear-quarter', 'top', 'front', 'side', 'underside',
                          'crescent-detail', 'hull-detail', 'technical-wireframe', 'concept',
                          'verified-side', 'verified-front', 'verified-legacy-side', 'verified-legacy-quarter']]
    for name,label in [('verified-bridge-detail','Four glazed crew domes'),
                       ('verified-hull-profile','Hull profile diagnostic - wing assemblies hidden')]:
        if (ROOT/'gallery/media'/OBJECT/(name+'.png')).is_file():
            views.append(dict(label=label,image='gallery/media/'+OBJECT+'/'+name+'.png'))
    if (ROOT/'gallery/media'/OBJECT/'feedback-comparison.jpg').is_file():
        views.append(dict(label='Concept and GLB feedback comparison', image='gallery/media/'+OBJECT+'/feedback-comparison.jpg'))
    if (ROOT/'gallery/media'/OBJECT/'wing-root-comparison.jpg').is_file():
        views.append(dict(label='Leading shield correction', image='gallery/media/'+OBJECT+'/wing-root-comparison.jpg'))
    if (ROOT/'gallery/media'/OBJECT/'round-shape-comparison.jpg').is_file():
        views.append(dict(label='Asymmetric hull, lobes and glazing - before and after',image='gallery/media/'+OBJECT+'/round-shape-comparison.jpg'))
    record['available_studies'] = [dict(stage='legacy-hi-def-remaster', blend=OBJECT+'/model.blend',
        present=True, sha256=report['blend_sha256'], final_visual_acceptance='awaiting-user-review', views=views)]
    record['selected_refinement'] = dict(issue=234, blend=OBJECT+'/model.blend', glb=OBJECT+'/model.glb',
        source_sha256=report['blend_sha256'], export_sha256=report['glb_sha256'], proposed_world_size=180,
        scale_status='Authored recommendation; current client fallback is 96; integration not applied')
    record['functional_reference']['review_status'] = 'reviewed-no-object-specific-narrative-mapped'
    record['acceptance'].update(reference_views_reviewed=True, native_and_glb_runtime=True)
    write(path, inventory)
    metadata = dict(id=ID, issue=234, canonical_blend='sources/'+OBJECT+'/model.blend',
        canonical_glb='sources/'+OBJECT+'/model.glb', source_sha256=report['blend_sha256'],
        export_sha256=report['glb_sha256'], triangles=report['triangles'], mesh_batches=report['mesh_batches'],
        materials=report['materials'], crew_domes=4, packed_maps=2, map_dimensions=[2048, 2048], local_forward='-Y', local_up='+Z',
        native_max_extent=18, proposed_world_size=180, current_client_fallback_size=96,
        scale_status='Unapplied authored recommendation, not physical metres',
        equipment_slots=4, calibrated_sockets=0, operational_animations=[],
        technical_verification='runtime-verification.json', visual_acceptance='awaiting-user-review',
        game_integration='separate acceptance required', preserved_historical_sources=preserved)
    write(out/'model.json', metadata)
    layout_path = ROOT/'project/layout.json'
    layout = json.loads(layout_path.read_text(encoding='utf-8'))
    known = {item['destination'] for item in layout['files']}
    paths = list(out.iterdir())+list((ROOT/'sources/materials/achaean/dedicated-ore-transporter').iterdir())
    paths += list((ROOT/'gallery/media'/OBJECT).iterdir())
    paths += [ROOT/'sources/tools/achaean_transporter_maps.py',
              ROOT/'sources/tools/blender/remaster_achaean_transporter.py',
              ROOT/'sources/tools/blender/render_achaean_transporter_round_review.py',
              ROOT/'sources/tools/blender/verify_achaean_transporter_remaster.py']
    for item in sorted(paths):
        rel = item.relative_to(ROOT).as_posix()
        if item.is_file() and rel not in known:
            role = 'material-texture' if rel.startswith('sources/materials/') else 'media' if rel.startswith('gallery/') else 'source'
            layout['files'].append(dict(original=rel, destination=rel, role=role, ownership='authored'))
    write(layout_path, layout)
    print('ACHAEAN_CANONICAL_REGISTERED', report['triangles'], 'triangles; historical source preserved')


if __name__ == '__main__':
    main()
