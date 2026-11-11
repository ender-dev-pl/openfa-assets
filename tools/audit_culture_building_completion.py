"""Audit a completed culture against frozen scope and actual bound per-model proofs.

This revalidates saved evidence and galleries. It does not rerun Blender, recreate
legacy references or promote final artistic/client/performance acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'sources/docs/reconstruction/models'
sys.path.insert(0, str(ROOT / 'sources/tools/blender'))
from culture_building_remaster_runtime_evidence import verify
from gallery_animation_assets import animation_previews

COUNTS = {'mikotaj': 21, 'artemian': 23, 'mauna': 21}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def audit(culture):
    expected_count = COUNTS[culture]
    baseline = load(DOCS / 'mam-building-remaster-baseline.json')
    expected = [r for r in baseline['models'] if r['culture'] == culture]
    expected_ids = {r['id'] for r in expected}
    assert len(expected_ids) == len(expected) == expected_count, 'Frozen scope mismatch'
    manifest_path = DOCS / (culture + '-building-remaster-delivery.json')
    manifest = load(manifest_path)
    assert manifest['expected_models'] == expected_count
    assert not manifest['pending'], 'Incomplete culture delivery'
    delivered = manifest['models']
    ids = [r['id'] for r in delivered]
    assert len(ids) == len(set(ids)) == expected_count and set(ids) == expected_ids, 'Missing or duplicate canonical delivery'
    inventory_path = DOCS / 'inventory.json'
    inventory = load(inventory_path)
    records = [r for r in inventory['records'] if r['category'] == 'buildings' and r['culture'] == culture]
    assert len(records) == expected_count and {r['id'] for r in records} == expected_ids
    functional_path = DOCS / 'functional-text-index.json'
    functional_records = load(functional_path)['records']
    catalogue_path = ROOT / 'gallery/catalogue.json'
    catalogue = load(catalogue_path)
    output = []
    preserved = []
    for original in expected:
        record, = [r for r in records if r['id'] == original['id']]
        row, = [r for r in delivered if r['id'] == record['id']]
        verified = verify(ROOT / 'sources', record)
        study, = record['available_studies']
        folder = ROOT / 'sources' / Path(study['blend']).parent
        meta = load(folder / 'model.json')
        concept = load(ROOT / meta['concept_review'])
        runtime = load(folder / 'runtime-review.json')
        visual = load(folder / 'visual-review.json')
        assert meta['key'] == row['key'] == original['key']
        assert meta['footprint'] == row['footprint'] == original['footprint']
        assert meta['definition_class'] == original['legacy_identity']['definitionClass']
        assert meta['construction_updates'] == original['legacy_identity']['constructionUpdates']
        assert row['blend'] == 'sources/' + study['blend']
        assert row['glb'] == (folder / 'model.glb').relative_to(ROOT).as_posix()
        assert row['blend_sha256'] == meta['binaries']['blend'] and row['glb_sha256'] == meta['binaries']['glb']
        assert row['triangles'] == verified['triangles'] and row['clips'] == runtime['clips']
        refs = concept['original_references']
        assert refs['catalogue']['image_updates'] == 41
        assert all(any(s['directory'] == directory and s['frame'] == 1 for s in refs['sprites']) for directory in ['_B', '_ZOOM'])
        functional = concept['functional_source']
        assert functional['id'] == record['id'] and concept['cultural_source']
        cited = [r['record'] for r in functional['descriptions']] if functional.get('descriptions') else functional.get('records', [])
        source, = [r for r in functional_records if r['id'] == record['id']]
        assert cited and set(cited) == {r['record'] for r in source['descriptions']}, 'Functional source record mismatch'
        assert visual['glb_feedback'], 'Missing actual GLB feedback'
        media = ROOT / record['reviewed_model']['runtime_evidence']['render_directory']
        previews = animation_previews(row['blend'], row['glb'], media)
        entry, = [r for r in catalogue if r['id'] == record['id']]
        current, = entry['studies']
        assert current['stage'] == 'canonical-game-remaster' and current['blend'] == row['blend'] and current['glb'] == row['glb'], 'Gallery canonical mismatch'
        assert current.get('animations', []) == previews, 'Gallery animation mismatch'
        assert current['image'] == row['preview'] and (ROOT / row['preview']).is_file()
        for old in original['studies']:
            assert old['blend'] != row['blend'] and old['glb'] != row['glb']
            assert any('sources/' + s['blend'] == old['blend'] and s['sha256'] == old['blend_sha256'] for s in record['historical_studies']), 'Missing historical selection'
            for kind in ['blend', 'glb']:
                assert sha(ROOT / old[kind]) == old[kind + '_sha256'], 'Changed frozen historical pair'
            preserved.append(dict(id=record['id'], **old))
        output.append(dict(id=record['id'], key=meta['key'], blend=row['blend'], glb=row['glb'], binaries=meta['binaries'], triangles=verified['triangles'], meshes=meta['mesh_nodes'], material_maps=len(meta['textures']), concept_attempts=len(concept['iterations']), glb_feedback_passes=len(visual['glb_feedback']), animation_clips=row['clips'], render_pairs=len(visual['pixel_pairs']), game_client_integration=False))
    return dict(schema_version=1, issue=manifest['issue'], culture=culture, model_count=len(output), preserved_original_pairs=len(preserved), total_triangles=sum(r['triangles'] for r in output), animated_models=sum(bool(r['animation_clips']) for r in output), catalogue_image_updates=41 * len(output), render_pairs=sum(r['render_pairs'] for r in output), auditor_sha256=sha(Path(__file__)), inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in [manifest_path, inventory_path, catalogue_path, functional_path, DOCS / 'cultural-architecture-index.json', DOCS / 'mam-building-remaster-baseline.json']}, models=output, preserved=preserved, scope='Current completion integrity backed by bound actual source/concept/native/imported GLB/render/video reviews. No new Blender run or legacy observation is claimed.', limits='Exact hidden engineering,metric scale,client integration/state/shaders/bloom,Android performance and final user artistic acceptance remain separate. No numerical80-percent fidelity measurement is claimed.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--culture', choices=COUNTS, required=True)
    args = parser.parse_args()
    result = audit(args.culture)
    path = DOCS / (args.culture + '-building-completion-audit.json')
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('CULTURE_BUILDING_COMPLETION_OK', args.culture, result['model_count'], 'models;', result['preserved_original_pairs'], 'preserved pairs;', result['render_pairs'], 'render pairs')


if __name__ == '__main__':
    main()
