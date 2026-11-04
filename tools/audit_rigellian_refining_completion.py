"""Audit all 35 current decisions against actual source-bound runtime evidence."""
import hashlib
import json
from pathlib import Path
import subprocess

from gallery_animation_assets import animation_previews, glb_clips

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'sources/docs/reconstruction/models'
SCRIPTS = ROOT/'sources/tools/blender'
BASE = 'a5c91f9'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().strip()


def main():
    catalogue = read(ROOT/'gallery/catalogue.json')
    rows = [row for row in catalogue if row['culture'] == 'rigellian']
    assert len(rows) == 35 and len({r['id'] for r in rows}) == 35
    inventory = {row['id']: row for row in read(DOCS/'inventory.json')['records']}
    retained = {row['id']: row for row in read(DOCS/'rigellian-retained-review.json')['records']}
    script_hashes = {sha(p) for p in SCRIPTS.glob('*.py')}
    earlier = json.loads(subprocess.check_output(['git', 'show', BASE+':sources/docs/reconstruction/models/inventory.json'], cwd=ROOT))
    earlier = {row['id']: row for row in earlier['records']}
    result, pairs, errors, rgb, old_pairs = [], 0, [], [], 0
    for row in rows:
        study = row['studies'][-1]
        current = [s for s in inventory[row['id']]['available_studies'] if s['present']][-1]
        assert study['blend'] == 'sources/'+current['blend']
        blend, glb = ROOT/study['blend'], ROOT/study['glb']
        assert study['sha256'] == current['sha256'] == sha(blend)
        previous = [s for s in earlier[row['id']]['available_studies'] if s['present']]
        for old in previous:
            old_blend = 'sources/'+old['blend']
            assert sha(ROOT/old_blend) == old['sha256']
            assert old in inventory[row['id']]['available_studies']
            for path in [old_blend, str(Path(old_blend).with_suffix('.glb')).replace('\\', '/')]:
                assert git('hash-object', path) == git('rev-parse', BASE+':'+path), path
            old_pairs += 1
        if row['id'] in retained:
            entry = retained[row['id']]
            assert entry['study'] == study['blend']
            path = ROOT/entry['validation']
            assert sha(path) == entry['validation_sha256']
            report = read(path)
            assert report['passed'] and report['visual_decision'] == 'retain-existing-study'
            assert report['blend_sha256'] == sha(blend) and report['glb_sha256'] == sha(glb)
            assert report['original_assertions_unchanged'] and report['canonical_inputs_unchanged']
            assert all(sha(ROOT/p) == value for p, value in report['canonical_inputs'].items())
            assert sha(path.parent/report['actual_runtime_report']) == report['actual_runtime_report_sha256']
            assert report['verifier_sha256'] == sha(SCRIPTS/report['verifier'])
            assert report['runner_sha256'] in script_hashes
            assert all(sha(path.parent/p) == value for p, value in report['published_renders'].items())
            decision = 'retained-after-focused-review'
        else:
            assert 'rigellian-refined/' in study['blend']
            meta = read(blend.with_suffix('.json'))
            path = (ROOT/study['image']).parent/'validation.json'
            report = read(path)
            for kind in ['blend', 'glb']:
                assert meta[kind+'_sha256'] == report[kind+'_sha256'] == sha(blend.with_suffix('.'+kind))
            assert meta['source_blend_sha256'] == report['source_blend_sha256'] == sha(ROOT/meta['source_study'])
            assert meta['generator_sha256'] == report['generator_sha256'] in script_hashes
            assert report['verifier_sha256'] in script_hashes
            for field in ['dependency_sha256', 'dependencies_sha256']:
                for name, value in meta.get(field, {}).items():
                    assert sha(SCRIPTS/name) == value
            for name, value in meta.get('texture_sha256', {}).items():
                assert sha(ROOT/name) == value
            if 'parts_module' in meta:
                assert sha(SCRIPTS/(meta['parts_module']+'.py')) == meta['parts_sha256']
            if 'lore_sha256' in meta:
                assert meta['lore_sha256'] == sha(DOCS/'rigellian-lore-evidence.json')
            assert report['native_mesh_count'] == report['imported_mesh_count']
            error = report['maximum_native_imported_position_error']
            assert error < .0001
            errors.append(error)
            for name, render in report['renders'].items():
                assert render['native_sha256'] == sha(path.parent/(name+'.png'))
                assert render['imported_sha256'] == sha(path.parent/('imported-'+name+'.png'))
                assert render['silhouette_iou'] == 1
                assert render['foreground_rgb_mean_difference_255'] < 2
                rgb.append(render['foreground_rgb_mean_difference_255'])
                pairs += 1
            assert not glb_clips(glb), 'A new authored clip requires explicit runtime and gallery review'
            decision = 'separate-refinement-study'
        clips = animation_previews(study['blend'], study['glb'], (ROOT/study['image']).parent)
        assert clips == study['animations']
        result.append(dict(id=row['id'], name=row['name'], category=row['category'], decision=decision,
                           blend=study['blend'], blend_sha256=sha(blend), glb=study['glb'], glb_sha256=sha(glb),
                           runtime_validation=path.relative_to(ROOT).as_posix(), runtime_validation_sha256=sha(path),
                           authored_clips=len(clips), earlier_studies_preserved=len(previous)))
    assert sum(r['decision'] == 'separate-refinement-study' for r in result) == 22
    assert len(retained) == 13 and pairs == 61
    assert {c: sum(r['category'] == c for r in result) for c in ['buildings', 'ships', 'missiles']} == dict(buildings=23, ships=5, missiles=7)
    all_clips = sum(len(animation_previews(s['blend'], s['glb'], (ROOT/s['image']).parent)) for r in catalogue for s in r['studies'])
    assert all_clips == 43
    output = dict(issue=185, audit_kind='Current source/report/render/gallery integrity audit; does not replace actual Blender validation or artistic review',
                  auditor_sha256=sha(Path(__file__)), inventory_sha256=sha(DOCS/'inventory.json'),
                  gallery_catalogue_sha256=sha(ROOT/'gallery/catalogue.json'), preservation_base=BASE,
                  earlier_model_pairs_preserved=old_pairs, refined_models=22, retained_models=13,
                  full_scope=35, matched_render_pairs=pairs, maximum_native_imported_position_error=max(errors),
                  maximum_foreground_rgb_mean_difference_255=max(rgb), all_gallery_authored_clips=all_clips,
                  latest_rigellian_authored_clips=sum(r['authored_clips'] for r in result), records=result,
                  evidence_ledgers={name: sha(DOCS/name) for name in ['rigellian-lore-evidence.json', 'rigellian-retained-review.json', 'rigellian-scitek-review.json']},
                  limitations='Final artistic acceptance, hidden construction, scale/direction calibration and gameplay integration remain separate')
    path = DOCS/'rigellian-refining-completion-audit.json'
    path.write_bytes((json.dumps(output, indent=2)+'\n').replace('\n', '\r\n').encode())
    print('RIGELLIAN_FULL_SCOPE_AUDIT_OK', len(result), 'models;', pairs, 'matched render pairs;', all_clips, 'gallery clips;', old_pairs, 'earlier model pairs preserved')


if __name__ == '__main__':
    main()
