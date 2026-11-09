"""Check current source layout, catalogue coverage and gallery links."""
import ast
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asset_workspace import ROOT, sha, verify
from gallery_animation_assets import animation_previews


class LocalLinks(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ['src', 'href', 'poster'] and value and not urlsplit(value).scheme:
                if not urlsplit(value).path:
                    continue  # In-page index links carry catalogue filter state.
                path = (ROOT / 'gallery' / unquote(urlsplit(value).path)).resolve()
                assert path.is_relative_to(ROOT) and path.is_file(), value


def main():
    verify()
    assert not list((ROOT / 'sources').rglob('*.java')), 'Game decompiler code is external evidence'
    inventory = json.loads((ROOT / 'sources/docs/reconstruction/models/inventory.json').read_text())
    sys.path.insert(0,str(ROOT/'sources/tools/blender'))
    from model_runtime_evidence import verify_runtime_evidence
    for record in inventory['records']:
        if record.get('selected_refinement',{}).get('issue')==234:
            verify_runtime_evidence(ROOT/'sources',record)
    gallery = json.loads((ROOT / 'gallery/catalogue.json').read_text())
    from gallery_trading_goods import trading_records
    trades = trading_records(ROOT)
    assert gallery == gallery[:len(inventory['records'])] + trades
    assert len(gallery) == len(inventory['records']) + len(trades)
    assert len(inventory['records']) == inventory['definition_count']
    actual_counts = {}
    for record in inventory['records']:
        cultures = actual_counts.setdefault(record['category'], {})
        cultures[record['culture']] = cultures.get(record['culture'], 0) + 1
    assert actual_counts == inventory['counts_by_category_culture']
    assert len({r['id'] for r in gallery}) == len(gallery)
    from gallery_supplemental import supplemental_records
    assert json.loads((ROOT / 'gallery/supplemental-catalogue.json').read_text()) == supplemental_records()
    count = 0
    for row, definition in zip(gallery, inventory['records']):
        assert (row['id'], row['category'], row['culture']) == (definition['id'], definition['category'], definition['culture'])
        expected = [s for s in definition['available_studies'] if s['present']]
        assert len(row['studies']) == len(expected)
        for study, original in zip(row['studies'], expected):
            assert study['stage'] == original['stage']
            assert study['blend'] == 'sources/' + original['blend']
            assert sha(ROOT / study['blend']) == study['sha256'] == original['sha256']
            assert (ROOT / study['image']).is_file() and study['image'].startswith('gallery/media/')
            assert study.get('views', []) == original.get('views', [])
            for view in study.get('views', []):
                assert view['label'] and view['image'].startswith('gallery/media/')
                assert (ROOT / view['image']).is_file(), view
            assert study['glb'] and (ROOT / study['glb']).is_file(), row['id']
            assert study['animations']==animation_previews(study['blend'],study['glb'],(ROOT/study['image']).parent)
            count += 1
    for page in ['index.html', 'ui.html', 'construction-animations.html']:
        LocalLinks().feed((ROOT / 'gallery' / page).read_text(encoding='utf-8'))
    scripts = (list((ROOT / 'sources').rglob('*.py')) + list((ROOT / 'tools').glob('*.py'))
               + list((ROOT / 'archive').rglob('*.py')) + list((ROOT / 'tooling').rglob('*.py')))
    for path in scripts:
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    print('PROJECT_VERIFIED', len(gallery), 'definitions', count, 'study entries', len(scripts), 'Python sources')


if __name__ == '__main__':
    main()
