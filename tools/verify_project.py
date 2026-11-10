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
    sys.path.insert(0, str(ROOT / 'sources/tools/blender'))
    from model_runtime_evidence import verify_runtime_evidence
    for record in inventory['records']:
        reviewed = record.get('reviewed_model')
        proof = reviewed.get('runtime_evidence') if isinstance(reviewed, dict) else None
        if isinstance(proof, dict) and proof.get('format') in {'rigellian-building-remaster-v1', 'achaean-building-remaster-v1', 'achaean-static-building-remaster-v2', 'achaean-animated-building-remaster-v1'}:
            verify_runtime_evidence(ROOT / 'sources', record)
    gallery = json.loads((ROOT / 'gallery/catalogue.json').read_text())
    migration=json.loads((ROOT/'sources/docs/reconstruction/models/shipyard-canonical-assets.json').read_text())
    for asset in migration['models']:
        record=next(row for row in inventory['records'] if row['id']==asset['id'])
        assert len(record['available_studies'])==1, (asset['id'],'duplicate model study')
        study=record['available_studies'][0]
        assert 'sources/'+study['blend']==asset['blend']
        published=next(row for row in gallery if row['id']==asset['id'])
        assert len(published['studies'])==1
        assert published['studies'][0]['glb']==asset['glb']
        for kind in ['blend','glb']:
            assert sha(ROOT/asset[kind])==asset[kind+'_sha256']
            assert list((ROOT/asset[kind]).parent.rglob('*.'+kind))==[ROOT/asset[kind]], (asset['id'],'duplicate canonical payload')
        for old in asset['removed_models']:
            assert not (ROOT/old['path']).exists(),('superseded model restored',old['path'])
    for old,new in migration['redirects'].items():
        assert (ROOT/new).is_file()
        if old!=new:assert not (ROOT/old).exists(),('obsolete payload path restored',old)
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
            assert study['glb'] and (ROOT / study['glb']).is_file(), row['id']
            assert study['animations']==animation_previews(study['blend'],study['glb'],(ROOT/study['image']).parent)
            from gallery_showcase_assets import showcase_previews
            assert study.get('showcases',[])==showcase_previews(original)
            assert study.get('views',[])==original.get('views',[])
            for view in study.get('views',[]):
                assert view['label'] and view['image'].startswith('gallery/media/')
                path=(ROOT/view['image']).resolve()
                assert path.is_relative_to((ROOT/'gallery/media').resolve()) and path.is_file(),view
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
