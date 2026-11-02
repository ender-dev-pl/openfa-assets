"""Publish fresh runtime review evidence without replacing retained models or old reports."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT/'artifacts/issue-185'
DOCS = ROOT/'sources/docs/reconstruction/models'
MEDIA = ROOT/'gallery/media/docs/assets/reconstruction/rigellian-refining-review'
DECISIONS = {
    2: 'Retain six gold ports, actual lower slots, stepped shoulder and tall side channel. Focused highlighted phases and current native/import views do not establish another missing major assembly or a different collar/port arrangement.',
    7: 'Retain the slender stepped spindle, silver open fork crown, real wells and flared bell foot. A gold crown copied from other facilities would contradict this source.',
    9: 'Retain paired open wells, pale uprights, lower rim slots and raised upper well. Current contacts and body divisions reproduce the visible construction; catalogue highlighting does not establish door motion.',
    10: 'Retain the bronze buttresses, surface panels, open shaft and two existing sliding covers. Composed source activity layers and actual closed/half/open GLB renders support this assembly. All 61 authored runtime poses were checked by the unchanged original validator.',
    11: 'Retain the open upper port, internal flat guides, flared collar and front fitting. The left dark sprite patch remains ambiguous shading; adding a second hole is unsupported.',
    12: 'Retain the stepped tip, red middle housing, exposed copper neck and slender coaxial pole/foot. The major visible colour and shape divisions are already present.',
    13: 'Retain the sphere, side braces, real front grille, side fittings and lower spindle/foot. Current renders preserve the visible gaps and main proportions without adding a speculative power mechanism.',
    15: 'Retain the segmented sphere, green service face, equatorial ring, neck and foot. The existing broad divisions and attached face already account for the source-visible equipment.',
    16: 'Retain three globes and feet, open mast supports and curved gold top. Actual gaps and the distinct upper spindle are present; extra antennas or another globe lack evidence.',
    18: 'Retain the stepped green shell, segmented bronze foundation, front rungs, side rod and sideways opening dome halves. Original base/cover layers were composed at descriptor offsets; fresh native/import closed/half/open renders and aperture tests support retaining the previous launch animation.',
    19: 'Retain the tapered pointed barrel, rounded short pivot housing, bronze side fittings and pedestal. All sixteen directional heads were composed over the base; they support the existing major forms. Directional yaw is not evidence for an autonomous firing or idle clip.',
    21: 'Retain five bronze pods, pale rack, central join and green faces. Existing views reproduce the broad pod arrangement and material regions; hidden plumbing and precise pod curvature remain authored.',
    22: 'Retain the thin concave dish, inclined support, central copper feed, four fittings and green pedestal. All sixteen complete directional sprites show the dish changing from a thin diagonal edge to a full circle. The steep oval in the current quarter render is camera/yaw presentation, not proof that physical dish inclination should change. No new idle sweep or pitch clip is established.',
}
FOCUSED_SCITEK = [0, 1, 6, 7, 11, 14, 20, 21, 23, 31]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    newline = '\r\n' if path.as_posix().startswith((ROOT/'sources').as_posix()) else '\n'
    path.write_bytes((json.dumps(data, indent=2)+'\n').replace('\n', newline).encode())


def main():
    published = []
    for key, reason in DECISIONS.items():
        folder = PRIVATE/'retention-runtime'/f'ri{key:02}'
        report = json.loads((folder/'validation.json').read_text())
        assert report['passed'] and report['original_assertions_unchanged'] and report['canonical_inputs_unchanged']
        assert all(sha(ROOT/path) == value for path, value in report['canonical_inputs'].items())
        runner = 'review_rigellian_retained_launcher.py' if key == 18 else 'review_existing_rigellian_refinements.py'
        assert sha(ROOT/'sources/tools/blender'/runner) == report['runner_sha256']
        assert sha(ROOT/'sources/tools/blender'/report['verifier']) == report['verifier_sha256']
        work = ROOT/report['working_copy']
        if key == 18:
            work /= 'gallery/media/docs/assets/reconstruction/launch-facilities/rigellian/ri18'
            original_report = work/'validation.json'
            images = sorted(work.glob('*.png'))
        else:
            original_report = work/'technical-review.json'
            images = sorted(work.glob('imported-glb-*.png'))+[work/'native-current-front-quarter.png']
        assert sha(original_report) == report['actual_runtime_report_sha256']
        target = MEDIA/f'ri{key:02}'
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original_report, target/'actual-runtime-report.json')
        for image in images:
            shutil.copy2(image, target/image.name)
        report.update(visual_decision='retain-existing-study', decision_reason=reason,
                      visual_acceptance='Review decision only; final artistic acceptance and gameplay calibration remain separate',
                      evidence_scope='All 41 correctly paletted catalogue phases; source surface parts and current native/independent GLB views',
                      published_renders={p.name: sha(p) for p in images},
                      actual_runtime_report='actual-runtime-report.json')
        # Keep original runtime and source hashes; this annotation does not rerun or rebind them.
        save(target/'validation.json', report)
        published.append(dict(key=report['key'], id=report['id'], name=report['name'],
                              study=report['study'], blend_sha256=report['blend_sha256'],
                              glb_sha256=report['glb_sha256'], decision='retain-existing-study', reason=reason,
                              validation=(target/'validation.json').relative_to(ROOT).as_posix(),
                              validation_sha256=sha(target/'validation.json')))
    save(DOCS/'rigellian-retained-review.json', dict(issue=185, records=published,
         preserved_model_count=13, newly_refined_model_count=0,
         policy='Fresh source-specific runtime checks and focused visual review; unchanged models are not counted as new refinements'))
    scitek = json.loads((PRIVATE/'scitek-motion-review/manifest-all.json').read_text())
    assert len(scitek['records']) == 36
    assert sha(ROOT/'sources/content/standard/presentation/legacy-domain.json') == scitek['catalogue_sha256']
    for row in scitek['records']:
        assert row['timeline_decoder_sha256'] == sha(Path(__file__).with_name('prepare_rigellian_scitek_review.py'))
        assert not row['direct_rigellian_preview']
        row['visually_reviewed_updates'] = row['sampled_updates'] if row['index'] in FOCUSED_SCITEK else [34, 103, 171]
        row['review_scope'] = '18 spaced motion samples' if row['index'] in FOCUSED_SCITEK else 'Three-image subject overview; not exhaustive motion inspection'
    scitek.update(issue=185, interpretation='All 36 actual research bindings were resolved. Preview subjects are PB/PH/PM/ST, with no direct RI preview binding. Reviewed films show camera changes and highlighted equipment; these other-culture/generic diagrams do not override Rigellian surface evidence or establish a Rigellian operating clip.',
                  private_pixels='Decoded original images and contact sheets remain in ignored artifacts; only reference metadata and hashes are published')
    save(DOCS/'rigellian-scitek-review.json', scitek)
    layout_path = ROOT/'project/layout.json'
    layout = json.loads(layout_path.read_text())
    paths = list(MEDIA.rglob('*'))+[DOCS/'rigellian-retained-review.json', DOCS/'rigellian-scitek-review.json', DOCS/'rigellian-retained-review.md']
    paths += [ROOT/'sources/tools/blender'/p for p in ['review_existing_rigellian_refinements.py', 'review_rigellian_retained_launcher.py']]
    existing = {row['destination'] for row in layout['files']}
    for path in sorted(p for p in paths if p.is_file()):
        destination = path.relative_to(ROOT).as_posix()
        if destination in existing:
            continue
        media = destination.startswith('gallery/media/')
        original = destination.removeprefix('gallery/media/' if media else 'sources/')
        assert not any(row['original'] == original for row in layout['files'])
        layout['files'].append(dict(original=original, destination=destination, role='media' if media else 'source', ownership='authored'))
    save(layout_path, layout)
    print('RIGELLIAN_RETENTION_REVIEW_REGISTERED', len(published))


if __name__ == '__main__':
    main()
