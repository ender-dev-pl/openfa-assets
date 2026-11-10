"""Select one canonical building only after its actual runtime evidence exists."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'sources/docs/reconstruction/models'
sys.path.insert(0, str(ROOT / 'sources/tools/blender'))
from rigellian_building_runtime_evidence import digest, verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    original = path.read_bytes() if path.exists() else b''
    newline = '\r\n' if b'\r\n' in original else '\n'
    path.write_bytes((json.dumps(data, indent=2) + '\n').replace('\n', newline).encode())


def main(folder):
    folder = folder.resolve()
    assert folder.is_relative_to((ROOT / 'sources/objects/rigellian').resolve())
    meta = json.loads((folder / 'model.json').read_bytes())
    runtime = json.loads((folder / 'runtime-review.json').read_bytes())
    visual = json.loads((folder / 'visual-review.json').read_bytes())
    recipe = json.loads((ROOT / meta['recipe']).read_bytes())
    assert sha(ROOT / meta['recipe']) == meta['recipe_sha256']
    assert visual['runtime_report_sha256'] == sha(folder / 'runtime-review.json')
    assert visual['binaries'] == runtime['binaries'] == meta['binaries']
    assert visual['final_user_artistic_acceptance'] is False
    inventory_path = DOCS / 'inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    record = next(row for row in inventory['records'] if row['id'] == meta['id'])
    relative = (folder / 'model.blend').relative_to(ROOT / 'sources').as_posix()
    if not any(study['blend'] == relative for study in record['available_studies']):
        record.setdefault('historical_studies', []).extend(record['available_studies'])
        record.setdefault('historical_runtime_review', record.get('reviewed_model'))
    media = ROOT / recipe['media']
    concept = visual['concept']
    record['available_studies'] = [dict(stage='canonical-game-remaster', blend=relative,
        present=True, sha256=meta['binaries']['blend'], final_visual_acceptance='not-established',
        views=[dict(label='Legacy-based concept (interpreted details)', image=concept['image']),
               dict(label='Actual independent GLB', image=(media / 'imported-front-quarter.png').relative_to(ROOT).as_posix())])]
    if meta.get('articulation'):
        record['available_studies'][0]['views'].extend(
            dict(label='Articulated head: authored yaw '+str(angle)+' degrees (fixed base)',
                 image=(media/('imported-yaw-'+str(index).zfill(2)+'.png')).relative_to(ROOT).as_posix())
            for index,angle in [(4,90),(8,180),(12,270)])
    paths = {folder / name for name in ['model.blend', 'model.glb', 'model.json',
                                        'runtime-review.json', 'visual-review.json']}
    paths.update(ROOT / name for name in [meta['source'], meta['recipe'], concept['image'], concept['prompt']])
    for attempt in visual.get('concept_attempts',[]):
        for field in ['prompt','image']:
            if attempt.get(field):
                candidate = (ROOT/attempt[field]).resolve()
                assert candidate.is_relative_to(ROOT.resolve()) and candidate.is_file()
                paths.add(candidate)
        if attempt.get('image') and attempt.get('sha256'):
            assert sha(ROOT/attempt['image']) == attempt['sha256']
    paths.update(ROOT / name for name in runtime['helpers'])
    paths.update(media / name for name in runtime['renders'])
    if meta.get('mechanism_evidence'):
        paths.add(ROOT / meta['mechanism_evidence'])
    if recipe.get('state_evidence'):
        paths.add(ROOT / recipe['state_evidence'])
    preview_index = media / 'animation-previews.json'
    if preview_index.exists():
        previews = json.loads(preview_index.read_bytes())
        paths.add(preview_index)
        paths.add(ROOT / previews.get('renderer', 'sources/tools/blender/render_gallery_animations.py'))
        paths.update(ROOT / clip['video'] for clip in previews['clips'])
    proof = dict(format='rigellian-building-remaster-v1', scope='blender-native-and-imported-glb',
                 game_client_integration=False, render_directory=recipe['media'],
                 files={p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)})
    record['reviewed_model'] = dict(blend=relative, sha256=meta['binaries']['blend'], runtime_evidence=proof)
    record['acceptance']['native_and_glb_runtime'] = True
    functional_record = visual['legacy']['functional_record']
    assert functional_record in record['functional_reference']['description_records']
    record['functional_reference']['review_status'] = 'reviewed-original-record-' + str(functional_record)
    record.setdefault('acceptance_evidence', {})['native_and_glb_runtime'] = [
        'Actual saved-native/independent GLB source-bound remaster evidence; client and final artistic acceptance remain separate.',
        (folder / 'runtime-review.json').relative_to(ROOT / 'sources').as_posix(),
        (folder / 'visual-review.json').relative_to(ROOT / 'sources').as_posix()]
    verify(ROOT / 'sources', record)
    write_json(inventory_path, inventory)
    delivery_path = DOCS / 'rigellian-building-remaster-delivery.json'
    delivery = json.loads(delivery_path.read_bytes())
    delivery['models'] = [row for row in delivery['models'] if row['id'] != meta['id']]
    delivery['models'].append(dict(id=meta['id'], key=recipe['key'],
        blend=(folder / 'model.blend').relative_to(ROOT).as_posix(),
        glb=(folder / 'model.glb').relative_to(ROOT).as_posix(), binaries=meta['binaries'],
        triangles=meta['triangles'], meshes=meta['mesh_nodes'], materials=runtime['material_count'],
        embedded_images=runtime['embedded_images'], footprint=meta['footprint'],
        definition_class=meta['definition_class'], construction_updates=meta['construction_updates'],
        root='PlacementRoot', root_matrix=runtime['native_root_matrix'],
        native_world_bounds=runtime['native_world_bounds'], axes='Blender -Y forward; +Z dorsal',
        state_contract=recipe['state_contract'],
        reuse='One current model across gameplay, build menu and SciTek; previous studies are history.',
        limits='Client scale/state/mount integration, Android performance and final user artistic acceptance remain separate.'))
    delivery['models'].sort(key=lambda row: row['key'])
    if meta.get('animation'):
        current = next(row for row in delivery['models'] if row['id'] == meta['id'])
        current['animation'] = meta['animation']
        current['state_mapping'] = meta['states']
    if meta.get('articulation'):
        current = next(row for row in delivery['models'] if row['id'] == meta['id'])
        current['articulation'] = meta['articulation']
    delivery['pending'] = [key for key in delivery['pending'] if key != recipe['key']]
    write_json(delivery_path, delivery)
    print('RIGELLIAN_CANONICAL_REGISTERED', recipe['key'], len(proof['files']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=Path, required=True)
    main(parser.parse_args().model)
