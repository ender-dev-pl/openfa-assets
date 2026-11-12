"""Build an allowlisted, size-limited Pages artifact from the public gallery."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote, unquote, urlsplit
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('index.html', 'ui.html', 'construction-animations.html', 'engineering-proposals.html')
MAX_BYTES = 900 * 1024 * 1024


def build(output, repository='ender-dev-pl/openfa-assets', ref='main'):
    output = output.resolve()
    if output == ROOT or output.is_relative_to(ROOT / 'sources') or (output.exists() and any(output.iterdir())):
        raise ValueError('Choose a new or empty output directory outside sources/')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Expected owner/repository')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'media').mkdir()
    (output / '.nojekyll').write_text('')
    assets = {}
    source_inputs = {}

    def asset(path):
        relative = path.relative_to(ROOT).as_posix()
        if relative in assets:
            return assets[relative]
        data = path.read_bytes()
        source_inputs[relative] = hashlib.sha256(data).hexdigest()
        key = hashlib.sha256(data).hexdigest()[:24]
        if path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            target = 'media/' + key + '.webp'
            with Image.open(path) as image:
                image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                image.thumbnail((960, 960), Image.Resampling.LANCZOS)
                image.save(output / target, 'WEBP', quality=88, method=4)
        elif path.suffix.lower() in {'.webm', '.mp4', '.gif', '.webp'}:
            target = 'media/' + key + path.suffix.lower()
            shutil.copyfile(path, output / target)
        else:
            raise ValueError('Unsupported embedded media: ' + relative)
        assets[relative] = target
        return target

    def rewrite(match):
        attribute, delimiter, value = match.groups()
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group()
        path = (ROOT / 'gallery' / unquote(parsed.path)).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            # Filter option values are intentionally not URLs.
            if attribute == 'value':
                return match.group()
            raise ValueError('Missing or external local link: ' + value)
        relative = path.relative_to(ROOT).as_posix()
        if path.parent == ROOT / 'gallery' and path.name in PAGES:
            target = path.name
        elif attribute in {'src', 'poster', 'value'}:
            target = asset(path)
        else:
            kind = 'blob' if path.suffix.lower() in {'.md', '.json', '.py', '.txt'} else 'raw'
            target = 'https://github.com/' + repository + '/' + kind + '/' + quote(ref, safe='') + '/' + quote(relative)
        if parsed.query:
            target += '?' + parsed.query
        if parsed.fragment:
            target += '#' + parsed.fragment
        return attribute + '=' + delimiter + target + delimiter

    pattern = re.compile(r'\b(src|href|poster|value)=([' + "\"'" + r'])(.*?)\2')
    for name in PAGES:
        source = ROOT / 'gallery' / name
        source_inputs[source.relative_to(ROOT).as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
        page = source.read_text(encoding='utf-8')
        (output / name).write_text(pattern.sub(rewrite, page), encoding='utf-8')
    report = {'pages': list(PAGES), 'embedded_assets': len(assets),
              'bytes': sum(p.stat().st_size for p in output.rglob('*') if p.is_file()),
              'maximum_bytes': MAX_BYTES,
              'policy': 'Only generated HTML, metadata-free previews and explicitly referenced videos are deployed.'}
    report['source_inputs'] = source_inputs
    report['output_sha256'] = {path.relative_to(output).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in output.rglob('*') if path.is_file()}
    if report['bytes'] > MAX_BYTES:
        raise ValueError('Pages artifact exceeds the publication budget')
    (output / 'build-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    verify(output)
    print('PAGES_BUILT',json.dumps({k:v for k,v in report.items() if k not in {'source_inputs','output_sha256'}}),len(report['source_inputs']),'bound sources')


def verify(output):
    allowed = {'.html', '.webp', '.webm', '.mp4', '.gif'}
    for path in output.rglob('*'):
        if path.is_file() and path.name not in {'.nojekyll', 'build-manifest.json'}:
            assert path.suffix in allowed, path.relative_to(output)

    manifest=output/'build-manifest.json'
    if manifest.is_file():
        metadata=json.loads(manifest.read_text(encoding='utf-8'))
        for name,expected in metadata.get('source_inputs',{}).items():
            source=(ROOT/name).resolve()
            if not source.is_relative_to(ROOT.resolve()) or not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=expected:
                raise ValueError('Stale Pages source: '+name)
        for name,expected in metadata.get('output_sha256',{}).items():
            target=(output/name).resolve()
            if not target.is_relative_to(output.resolve()) or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=expected:
                raise ValueError('Changed Pages output: '+name)

    class Links(HTMLParser):
        def handle_starttag(self, tag, attributes):
            for key, value in attributes:
                if key not in {'src', 'href', 'poster'} or not value:
                    continue
                parsed = urlsplit(value)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                path = (output / unquote(parsed.path)).resolve()
                assert path.is_relative_to(output) and path.is_file(), value
    for name in PAGES:
        Links().feed((output / name).read_text(encoding='utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    parser.add_argument('--repository', default='ender-dev-pl/openfa-assets')
    parser.add_argument('--ref', default='main')
    parser.add_argument('--check-existing',action='store_true',help='Verify the committed site against current source and output hashes; do not rebuild')
    args = parser.parse_args()
    if args.check_existing:
        metadata=json.loads((args.output/'build-manifest.json').read_text(encoding='utf-8'))
        assert metadata.get('source_inputs') and metadata.get('output_sha256'),'Pages freshness manifest required'
        verify(args.output.resolve())
        print('COMMITTED_PAGES_VERIFIED',len(metadata['source_inputs']),'source inputs')
    else:
        build(args.output, args.repository, args.ref)
