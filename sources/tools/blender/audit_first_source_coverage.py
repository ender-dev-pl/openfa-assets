"""Audit selected first-source files; report availability is not runtime or art acceptance."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'docs/reconstruction/models/first-source-audit.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    inventory_path = ROOT / 'docs/reconstruction/models/inventory.json'
    ledger_path = ROOT / 'docs/reconstruction/models/review-ledger.json'
    inventory = json.loads(inventory_path.read_text())
    ledger = json.loads(ledger_path.read_text())
    rows = []
    for record in inventory['records']:
        studies = [s for s in record['available_studies'] if s['present']]
        assert studies, ('Missing first source', record['id'])
        study = studies[-1]
        blend = (ROOT / study['blend']).resolve()
        assert blend.is_relative_to(ROOT) and blend.is_file()
        assert digest(blend) == study['sha256'], ('Stale source', record['id'])
        folder = blend.parent
        files = {}
        issues = []
        for name in ['model.glb', 'model.json', 'technical-review.json', 'render-review.json']:
            path = folder / name
            if name == 'model.glb' and not path.is_file():
                path = blend.with_suffix('.glb')
            files[name] = dict(present=path.is_file(), path=str(path.relative_to(ROOT)).replace('\\', '/'))
            if path.is_file():
                files[name]['sha256'] = digest(path)
            else:
                issues.append('Missing ' + name)
        metadata = {}
        if files['model.json']['present']:
            metadata = json.loads((folder / 'model.json').read_text())
            for key, actual in [('blend_sha256', study['sha256']),
                                ('glb_sha256', files['model.glb'].get('sha256'))]:
                if metadata.get(key) != actual or actual is None:
                    issues.append('Metadata does not bind current ' + key)
            if metadata.get('id') != record['id']:
                issues.append('Metadata identity absent or different')
        for name in ['technical-review.json', 'render-review.json']:
            if files[name]['present']:
                report = json.loads((folder / name).read_text())
                if report.get('blend_sha256') != study['sha256']:
                    issues.append(name + ' does not bind current Blend')
                if name == 'technical-review.json' and report.get('glb_sha256') != files['model.glb'].get('sha256'):
                    issues.append(name + ' does not bind current GLB')
                if name == 'render-review.json':
                    views = report.get('view_hashes', report.get('hashes', {}))
                    if not views:
                        issues.append('No per-view pixel hashes in render report')
                    for view, expected in views.items():
                        image = folder / (view.replace('\\', '/') if view.endswith('.png') else view + '.png')
                        assert image.resolve().is_relative_to(folder)
                        if not image.is_file() or digest(image) != expected:
                            issues.append('Missing or stale view ' + view)
        reviews = [r for r in ledger['reviews'] if r['category'] == record['category']
                   and r['id'] == record['id'] and r['model']['blend'] == study['blend']
                   and r['model']['sha256'] == study['sha256']]
        gates = sorted({k for r in reviews for k, v in r.get('gates', {}).items() if v is True})
        rows.append(dict(category=record['category'], culture=record['culture'], id=record['id'],
                         stage=study['stage'], blend=study['blend'], blend_sha256=study['sha256'],
                         files=files, evidence_gaps=issues, accepted_ledger_gates=gates,
                         final_artistic_acceptance=False))
    assert len(rows) == 303 and len({(r['category'], r['id']) for r in rows}) == 303
    return dict(schema_version=1, issue=1099, inventory_sha256=digest(inventory_path),
                review_ledger_sha256=digest(ledger_path), definitions=len(rows),
                categories=dict(Counter(r['category'] for r in rows)),
                evidence_gap_counts=dict(Counter(g for r in rows for g in r['evidence_gaps'])),
                selected_sources_with_no_listed_file_gaps=sum(not r['evidence_gaps'] for r in rows),
                selected_sources_with_accepted_runtime_gate=sum('native_and_glb_runtime' in r['accepted_ledger_gates'] for r in rows),
                scope='Exact selected Blend hashes and sibling report/export/pixel bindings only. Does not rerun Blender, validate every report assertion, prove final quality, states, attachments or game integration.',
                selection='Last present registered study per definition, matching existing culture-sheet selection; not an artistic ranking.',
                records=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = build()
    if args.check:
        assert json.loads(OUTPUT.read_text()) == report, 'First-source audit is stale'
    else:
        OUTPUT.write_text(json.dumps(report, indent=2) + '\n')
    print('FIRST_SOURCE_AUDIT_OK', report['definitions'],
          report['selected_sources_with_no_listed_file_gaps'], 'without listed file gaps;',
          report['selected_sources_with_accepted_runtime_gate'], 'selected runtime ledger gates')
    print(json.dumps(report['evidence_gap_counts'], indent=2))


if __name__ == '__main__':
    main()
