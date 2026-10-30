"""Check import integrity, source/media boundaries, catalogue coverage and gallery links."""
import ast
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asset_workspace import ROOT, sha, verify


class LocalLinks(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ['src', 'href'] and value and not urlsplit(value).scheme:
                path = (ROOT / 'gallery' / unquote(urlsplit(value).path)).resolve()
                assert path.is_relative_to(ROOT) and path.is_file(), value


def main():
    verify()
    assert not list((ROOT / 'sources').rglob('*.java')), 'Game decompiler code is external evidence'
    inventory = json.loads((ROOT / 'sources/docs/reconstruction/models/inventory.json').read_text())
    gallery = json.loads((ROOT / 'gallery/catalogue.json').read_text())
    assert len(gallery) == len(inventory['records']) == 303
    assert len({r['id'] for r in gallery}) == len(gallery)
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
            count += 1
    LocalLinks().feed((ROOT / 'gallery/index.html').read_text(encoding='utf-8'))
    scripts = list((ROOT / 'sources').rglob('*.py')) + list((ROOT / 'tools').glob('*.py'))
    for path in scripts:
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    print('PROJECT_VERIFIED', len(gallery), 'definitions', count, 'study entries', len(scripts), 'Python sources')


if __name__ == '__main__':
    main()
