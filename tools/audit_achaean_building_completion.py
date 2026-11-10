"""Cross-check the complete 26-building delivery against current bound evidence."""
import hashlib
import json
from pathlib import Path
import struct
import sys
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'sources/docs/reconstruction/models'
sys.path.insert(0, str(ROOT / 'sources/tools/blender'))
from model_runtime_evidence import verify_runtime_evidence
from gallery_animation_assets import animation_previews, glb_clips


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def selections(delivery, inventory, gallery):
    expected = {f'openfa:building/legacy/{i}' for i in range(151, 177)}
    models = delivery['models']
    assert len(models) == 26 and {x['id'] for x in models} == expected
    assert {x['key'] for x in models} == {f'AC{i:02}' for i in range(1, 27)}
    assert delivery['pending'] == []
    assert len({x['blend'] for x in models}) == len({x['glb'] for x in models}) == 26
    records = [x for x in inventory['records'] if x['culture'] == 'achaean' and x['category'] == 'buildings']
    cards = [x for x in gallery if x['culture'] == 'achaean' and x['category'] == 'buildings']
    assert len(records) == len(cards) == 26
    assert {x['id'] for x in records} == {x['id'] for x in cards} == expected
    records = {x['id']: x for x in records}; cards = {x['id']: x for x in cards}
    result = []
    for model in sorted(models, key=lambda x: x['key']):
        record = records[model['id']]; card = cards[model['id']]
        study, = record['available_studies']; view, = card['studies']
        assert study['present'] and study['stage'] == 'canonical-game-remaster'
        assert model['blend'] == view['blend'] == 'sources/' + study['blend']
        assert model['glb'] == view['glb'] == str(Path(model['blend']).with_suffix('.glb')).replace('\\', '/')
        assert model['binaries']['blend'] == study['sha256'] == view['sha256'] == record['reviewed_model']['sha256']
        assert model['footprint'] == record['footprint']
        assert model['definition_class'] == record['legacy_identity']['definitionClass']
        assert model['construction_updates'] == record['legacy_identity']['constructionUpdates']
        result.append((model, record, view))
    return result


def audit():
    delivery = read(DOCS / 'achaean-building-remaster-delivery.json')
    inventory = read(DOCS / 'inventory.json'); gallery = read(ROOT / 'gallery/catalogue.json')
    references = read(DOCS / 'achaean-building-reference-review.json')
    milestones = read(DOCS / 'achaean-building-milestones.json')
    refs = {x['id']: x for x in references['records']}
    signs = {x['key']: x for x in milestones['records']}
    assert len(refs) == len(signs) == 26
    assert references['presentation_catalogue_sha256'] == sha(ROOT / 'sources/content/standard/presentation/legacy-domain.json')
    research = references['research']; assert research['topics'] == len(research['records']) == 36
    assert research['video_bindings'] == 72 and research['direct_achaean_profile_bindings'] == 0
    assert len(references['achaean_catalogue_bindings']) == 26
    for topic in research['records']:
        assert topic['achaean_building_profile_binding'] is False
        for mode in ['colour', 'technical']:
            assert topic['visually_reviewed_subject_updates'][mode] == topic[mode]['sampled_updates']
            assert len(topic[mode]['sampled_updates']) == len(topic[mode]['sampled_rgb_sha256']) == 3
        assert all(x['culture'] == 'terran' for x in topic['same_named_surface_subjects'])
    output = []; render_pairs = 0; concepts = 0
    for item, record, card in selections(delivery, inventory, gallery):
        folder = (ROOT / item['blend']).parent; meta = read(folder / 'model.json')
        runtime = read(folder / 'runtime-review.json'); visual = read(folder / 'visual-review.json')
        proof = verify_runtime_evidence(ROOT / 'sources', record)
        assert meta['id'] == runtime['id'] == visual['id'] == item['id']
        binaries = {ext: sha(folder / f'model.{ext}') for ext in ['blend', 'glb']}
        assert binaries == item['binaries'] == meta['binaries'] == runtime['binaries'] == visual['binaries']
        ref = refs[item['id']]; sign = signs[item['key']]
        assert ref['reviewed_binaries'] == sign['binaries'] == binaries
        assert ref['reviewed_visual_report_sha256'] == sha(folder / 'visual-review.json')
        assert ref['visually_reviewed_catalogue_updates'] == list(range(41))
        assert visual['legacy']['inspected_catalogue_phases'] == list(range(41))
        assert ref['extra_zoom_layers_reviewed'] == visual['legacy']['additional_zoom_sprite_layers_reviewed'] == [0, 1]
        assert ref['functional_record'] == visual['legacy']['functional_record'] == int(item['key'][2:]) + 1011
        assert ref['culture_record'] == visual['legacy']['culture_record'] == 166
        assert record['functional_reference']['review_status'] == 'reviewed-original-record-' + str(ref['functional_record'])
        assert sign['verified'] is True and sign['signature_state'] == 'VALID' and len(sign['commit']) == 40
        raw = (folder / 'model.glb').read_bytes(); doc = json.loads(raw[20:20 + struct.unpack_from('<I', raw, 12)[0]])
        nodes = [n for n in doc['nodes'] if 'mesh' in n]
        triangles = sum(doc['accessors'][p['indices']]['count'] // 3 for n in nodes for p in doc['meshes'][n['mesh']]['primitives'])
        assert triangles == item['triangles'] == runtime['triangles'] == meta['triangles']
        # AC01 predates the metadata budget field; its bound verifier enforces30k.
        budget = 30000 if item['key'] == 'AC01' else meta['triangle_budget']
        assert triangles < budget <= 120000
        assert len(nodes) == item['meshes'] == runtime['meshes'] == meta['mesh_nodes']
        assert len(doc['materials']) == item['materials'] == runtime['materials']
        assert len(doc['images']) == item['embedded_images'] == runtime['embedded_images']
        assert all('bufferView' in x and 'uri' not in x for x in doc['images'])
        assert runtime['texture_pixels_equal'] and runtime['maximum_bidirectional_surface_error'] < 1e-5
        assert item['root'] == 'PlacementRoot' and item['root_matrix'] == runtime['native_root_matrix']
        assert max(abs(v - (1 if i % 5 == 0 else 0)) for i, v in enumerate(item['root_matrix'])) < 1e-5
        assert item['native_world_bounds'] == runtime['native_world_bounds'] and runtime['native_world_bounds'][2] >= -1e-5
        assert item['state_contract'] == meta['state_contract'] and item['scale_contract'] == meta['scale_contract']
        attempts = visual['concept_attempts']; assert 1 <= len(attempts) <= 3
        assert all(a['tool'] == 'built-in image_gen' and a['feedback'] and (ROOT / a['prompt']).is_file() for a in attempts)
        assert visual['glb_feedback'] and all(x['observation'] and x['action'] for x in visual['glb_feedback'])
        clips = glb_clips(folder / 'model.glb')
        assert [x['name'] for x in clips] == runtime['clips']
        assert animation_previews(item['blend'], item['glb'], (ROOT / card['image']).parent) == card['animations']
        assert bool(clips) == (item['key'] in {'AC12', 'AC20', 'AC25', 'AC26'})
        renders = runtime['renders']; count = len(renders)
        assert count == (10 if item['key'] == 'AC12' else 6)
        assert all('imported-' + n.removeprefix('native-') in renders for n in renders if n.startswith('native-'))
        pixel_means = []
        for name in renders:
            if not name.startswith('native-'):
                continue
            media = (ROOT / card['image']).parent
            native = Image.open(media / name).convert('RGBA')
            imported = Image.open(media / ('imported-' + name.removeprefix('native-'))).convert('RGBA')
            assert native.size == imported.size
            box = ImageChops.lighter(native.getchannel('A'), imported.getchannel('A')).getbbox(); assert box
            assert min(box[0], box[1], native.width - box[2], native.height - box[3]) >= 24
            mean = max(ImageStat.Stat(ImageChops.difference(native, imported).crop(box)).mean)
            assert mean < 1.0, (item['key'], name, mean)
            pixel_means.append(mean)
        assert len(pixel_means) == count // 2
        render_pairs += count // 2; concepts += len(attempts)
        output.append(dict(id=item['id'], key=item['key'], name=item['name'], blend=item['blend'], glb=item['glb'], binaries=binaries,
                           triangles=triangles, triangle_budget=budget, meshes=len(nodes), materials=len(doc['materials']), embedded_images=len(doc['images']),
                           footprint=item['footprint'], definition_class=item['definition_class'], construction_updates=item['construction_updates'],
                           runtime_report=(folder / 'runtime-review.json').relative_to(ROOT).as_posix(), runtime_report_sha256=sha(folder / 'runtime-review.json'),
                           reference_surface_sha256=ref['surface_sha256'], reference_zoom_sha256=ref['extra_zoom_sha256'],
                           bound_runtime_files=proof['files'], render_pairs=count // 2, maximum_render_channel_mean_difference=max(pixel_means), concept_attempts=len(attempts),
                           clips=[x['name'] for x in clips], signed_model_commit=sign['commit'], state_contract=item['state_contract'], scale_contract=item['scale_contract']))
    baseline = read(DOCS / 'achaean-building-remaster-baseline.json'); assert len(baseline['records']) == 29
    selected = {x['blend'] for x in output}; preserved = []
    for old in baseline['records']:
        assert old['blend'] not in selected
        for ext in ['blend', 'glb']: assert sha(ROOT / old[ext]) == old[ext + '_sha256'], old[ext]
        record = next(x for x in inventory['records'] if x['id'] == old['id'])
        assert any('sources/' + s['blend'] == old['blend'] for s in record['historical_studies'])
        preserved.append(dict(id=old['id'], stage=old['stage'], blend=old['blend'], glb=old['glb'], blend_sha256=old['blend_sha256'], glb_sha256=old['glb_sha256']))
    assert len(output) == 26 and render_pairs == 80
    return dict(schema_version=1, issue=256, scope='Current asset-only completion integrity audit backed by actual per-model Blender and reference reviews;not a new Blender run or client/artist acceptance.',
                auditor_sha256=sha(Path(__file__)), model_count=26, preserved_original_pairs=29, render_pairs=render_pairs,
                catalogue_updates_reviewed=26 * 41, extra_zoom_layers_reviewed=26 * 2, research_video_subject_reviews=72,
                concept_attempts=concepts, animated_models=4, total_triangles=sum(x['triangles'] for x in output),
                maximum_model_triangles=max(x['triangles'] for x in output), maximum_model_meshes=max(x['meshes'] for x in output),
                inputs={name: sha(DOCS / name) for name in ['achaean-building-remaster-delivery.json', 'achaean-building-reference-review.json', 'achaean-building-remaster-baseline.json', 'achaean-building-milestones.json']},
                inventory_sha256=sha(DOCS / 'inventory.json'), gallery_catalogue_sha256=sha(ROOT / 'gallery/catalogue.json'), models=output, preserved=preserved,
                limits='One canonical asset pair per definition. Wireframe/diagram rendering should use that geometry. Hidden construction,exact scale/heading/muzzle calibration,game-client/package integration,Android frame time and final user artistic acceptance remain separate;no numerical80-percent fidelity score or continuous collision sweep claimed.')


def main():
    result = audit(); (DOCS / 'achaean-building-completion-audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('ACHAEAN_BUILDING_COMPLETION_AUDIT_OK', result['model_count'], 'models;', result['preserved_original_pairs'], 'preserved pairs;', result['render_pairs'], 'render pairs')


if __name__ == '__main__':
    main()
