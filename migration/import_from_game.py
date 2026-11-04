"""One-time, checksum-preserving migration of versioned canonical asset authoring files."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--destination', type=Path, required=True)
a = p.parse_args()
game = Path.cwd().resolve()
target = a.destination.resolve()
assert target == game.parent / 'openfa-assets'
assert not (target / 'sources').exists(), 'Do not overwrite an existing migration'
tracked = subprocess.check_output(['git', 'ls-files'], text=True).splitlines()
prefixes = ('tools/blender/', 'tools/hq-sprite-authoring/',
            'docs/assets/bootstrap-3d/', 'docs/assets/reconstruction/',
            'docs/assets/bootstrap/', 'docs/assets/interceptor/', 'docs/assets/decoy/',
            'docs/reconstruction/models/', 'tools/assets/legacy-missile-exhaust/')
single = {'tools/Build-BootstrapArtwork.py', 'tools/Prepare-LoadingArtwork.py',
          'tools/Install-OpenFaBlender.ps1', 'tools/create_missile_assets.py',
          'tools/test_create_missile_assets.py', 'tools/create_missile_menu_animation.py',
          'tools/Generate-QuickMenuChrome.py', 'tools/remove_atlas_checkerboard.py',
          'docs/blender-asset-workflow.md'}
owned = {x for x in tracked if x.startswith(prefixes) or x in single}
fixtures = set()
for name in tracked:
    if name.startswith('tools/blender/'):
        text = (game / name).read_text(encoding='utf-8-sig')
        for ref in re.findall(r'(?:src|content|tools)/[A-Za-z0-9_./-]+', text):
            if ref in tracked and (game / ref).is_file() and ref not in owned:
                fixtures.add(ref)
# Shared game tools remain game-owned; these copies are pinned fixtures.
fixtures.update(x for x in tracked if x.startswith('content/standard/catalogues/')
                and x.endswith('.json'))
fixtures.update(x for x in tracked if x.startswith('content/standard/presentation/')
                and x.endswith('.json'))
fixtures.update({'content/standard/images/quick-chrome-metal-tile.png',
                 'content/standard/images/quick-asteroid-icon.png',
                 'content/standard/images/quick-visual-menu-icon-v2.png',
                 'docs/assets/issue-625/test-colony.png'})
external = {x for x in fixtures if x.startswith('src/') or x.endswith('.java')}
fixtures -= external
media = {'.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webp', '.html'}
ui_inputs = {'content/standard/images/' + name for name in [
    'quick-asteroid-icon.png', 'quick-chrome-metal-tile.png', 'quick-visual-menu-icon-v2.png']}
# Apply the publication boundary even when replaying this historical recipe.
policy = Path(__file__).resolve().parents[1] / 'project/excluded-media.json'
excluded = set(json.loads(policy.read_text(encoding='utf-8'))['paths'])
owned = {name for name in owned if 'gallery/media/' + name not in excluded}
fixtures = {name for name in fixtures if 'gallery/media/' + name not in excluded}
rows = []
for name in sorted(owned | fixtures):
    role = 'fixture' if name in fixtures else 'source'
    if Path(name).suffix.lower() in media:
        role = 'media'
    dest = ('gallery/media/' if role == 'media' else 'sources/') + name
    if name in ui_inputs:
        role = 'source-input'
        dest = 'sources/ui/quick-menu/' + Path(name).name
    source = game / name
    output = target / dest
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert hashlib.sha256(output.read_bytes()).hexdigest() == digest
    rows.append(dict(original=name, destination=dest, role=role,
                     ownership='fixture' if name in fixtures else 'moved',
                     bytes=source.stat().st_size, sha256=digest))
manifest = dict(schema_version=1,
    origin='https://github.com/ender-dev-pl/ed-openfa-game',
    origin_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    scope='All tracked canonical asset authoring files; ignored experiments and protected recordings are not moved.',
    counts=dict(collections.Counter(x['role'] for x in rows)), files=rows,
    external_inputs=[dict(original=x, repository='ed-openfa-game',
        sha256=hashlib.sha256((game / x).read_bytes()).hexdigest(),
        role='game-owned evidence, read at runtime; not part of asset sources') for x in sorted(external)])
(target / 'migration').mkdir(exist_ok=True)
(target / 'migration/files.json').write_text(json.dumps(manifest, indent=2)+'\n',encoding='utf-8')
(target / '.gitignore').write_text('/artifacts/\n/.workspace/\n/legacy/\n/.asset-lab/\n**/__pycache__/\n*.py[cod]\n',encoding='utf-8')
(target / '.gitattributes').write_text(
    '# Preserve historical evidence hashes, including Windows checkout bytes.\n'
    '/sources/** -text\n/gallery/media/** -text\n*.blend binary\n*.glb binary\n'
    '/tools/** text eol=lf\n',encoding='utf-8')
print('MIGRATED', len(rows), manifest['counts'], sum(x['bytes'] for x in rows))
