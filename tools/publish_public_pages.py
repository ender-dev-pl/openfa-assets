"""Push only reviewed static content to gh-pages, without Actions artifact storage."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from build_public_pages import ROOT, verify
from verify_publication import problems


def command(arguments, cwd=None):
    return subprocess.check_output(arguments, cwd=cwd, text=True).strip()


def validate(site):
    site = site.resolve()
    if site == ROOT or (site / '.git').exists():
        raise ValueError('Choose a fresh generated site directory, not the source checkout')
    verify(site)
    for path in site.rglob('*'):
        if path.is_symlink():
            raise ValueError('Symlinks are not public content')
        if path.is_file() and problems(path):
            raise ValueError('Private or unreviewed metadata: ' + path.relative_to(site).as_posix())
    return site


def prepare(site):
    site = validate(site)
    subprocess.run(['git', 'init', '-b', 'gh-pages', str(site)], check=True, capture_output=True)
    for name, value in [('user.name', 'OpenFA Pages'), ('user.email', 'publication@openfa.invalid'),
                        ('commit.gpgsign', 'false'), ('core.autocrlf', 'false'), ('gc.auto', '0')]:
        subprocess.run(['git', '-C', str(site), 'config', name, value], check=True)
    subprocess.run(['git', '-C', str(site), 'add', '--all'], check=True)
    subprocess.run(['git', '-C', str(site), 'commit', '-m', 'docs: publish generated asset gallery'], check=True, capture_output=True)
    return command(['git', '-C', str(site), 'rev-parse', 'HEAD'])


def publish(site, repository, request_build=False):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Expected owner/repository')
    if request_build:
        settings = json.loads(command(['gh', 'api', 'repos/' + repository + '/pages']))
        if settings.get('build_type') != 'legacy' or settings.get('source') != {'branch': 'gh-pages', 'path': '/'}:
            raise ValueError('Configure Pages: Deploy from a branch > gh-pages > /(root) first')
    url = 'https://github.com/' + repository + '.git'
    remote = command(['git', 'ls-remote', '--heads', url, 'refs/heads/gh-pages'])
    expected = remote.split()[0] if remote else ''
    commit = prepare(site)
    subprocess.run(['git', '-C', str(site), 'push',
                    '--force-with-lease=refs/heads/gh-pages:' + expected,
                    url, 'HEAD:refs/heads/gh-pages'], check=True)
    result = {'branch': 'gh-pages', 'commit': commit, 'repository': repository,
              'pages_build_requested': request_build}
    if request_build:
        # GITHUB_TOKEN pushes do not trigger native Pages builds automatically.
        build = json.loads(command(['gh', 'api', '--method', 'POST', 'repos/' + repository + '/pages/builds']))
        result['build_status'] = build.get('status')
        result['build_url'] = build.get('url')
    print('PAGES_CONTENT_PUSHED', json.dumps(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=ROOT / '_site')
    parser.add_argument('--repository', default='ender-dev-pl/openfa-assets')
    parser.add_argument('--request-build', action='store_true', help='Require configured Pages and explicitly request its native build')
    args = parser.parse_args()
    publish(args.site, args.repository, args.request_build)
