"""Verify or assemble the historical layout without writing renders into sources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def manifest():
    return json.loads((ROOT / 'migration/files.json').read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    data = manifest()
    seen = set()
    for item in data['files']:
        dest = (ROOT / item['destination']).resolve()
        assert dest.is_relative_to(ROOT), item['destination']
        assert dest.is_file(), item['destination']
        assert dest not in seen, item['destination']
        seen.add(dest)
        assert dest.stat().st_size == item['bytes'], item['destination']
        assert sha(dest) == item['sha256'], item['destination']
    forbidden = {'.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webp', '.html'}
    assert not [p for p in (ROOT / 'sources').rglob('*') if p.suffix.lower() in forbidden]
    assert not list((ROOT / 'sources').rglob('*.cs')), 'Game C# files must not be copied into asset sources'
    print('MIGRATION_HASHES_OK', len(seen), flush=True)


def junction(link, target):
    target = target.resolve()
    if link.exists():
        assert link.resolve() == target, f'Existing link has another target: {link}'
        return
    assert target.is_dir(), target
    if os.name == 'nt':
        # Paths are passed as environment values, never interpolated as shell code.
        env = dict(os.environ, OPENFA_ASSETS_LINK=str(link), OPENFA_ASSETS_TARGET=str(target))
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
            'New-Item -ItemType Junction -Path $env:OPENFA_ASSETS_LINK -Target $env:OPENFA_ASSETS_TARGET | Out-Null'],
            env=env, check=True)
    else:
        link.symlink_to(target, target_is_directory=True)


def prepare(legacy, game):
    verify()
    workspace = ROOT / '.workspace'
    workspace.mkdir(exist_ok=True)
    for item in manifest()['files']:
        dest = workspace / item['original']
        assert dest.resolve().is_relative_to(workspace.resolve())
        if dest.exists():
            assert sha(dest) == item['sha256'], f'Preserving edited workspace file: {dest}'
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item['destination'], dest)
    game = game.resolve()
    for item in manifest().get('external_inputs', []):
        source = game / item['original']
        assert source.is_file() and sha(source) == item['sha256'], f'Game evidence changed: {source}'
        if not item['original'].startswith('src/'):
            # Non-C# naming evidence is a disposable runtime fixture only.
            dest = workspace / item['original']
            if dest.exists():
                assert sha(dest) == item['sha256'], dest
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
    junction(workspace / 'src', game / 'src')
    (workspace / 'artifacts/ship-reference-study').mkdir(parents=True, exist_ok=True)
    junction(ROOT / 'legacy', legacy)
    decompile = game / 'artifacts/fragile-le-decompilation'
    if decompile.is_dir():
        junction(workspace / 'artifacts/fragile-le-decompilation', decompile)
    print('WORKSPACE_READY', workspace, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['verify', 'prepare', 'references', 'python', 'blender'])
    parser.add_argument('--legacy-root', type=Path, default=ROOT.parent / 'legacy')
    parser.add_argument('--game-root', type=Path, default=ROOT.parent / 'openFA-game')
    parser.add_argument('--blender', type=Path)
    args, rest = parser.parse_known_args()
    rest = rest[1:] if rest[:1] == ['--'] else rest
    if args.command == 'verify':
        assert not rest
        verify()
    elif args.command == 'prepare':
        assert not rest
        prepare(args.legacy_root, args.game_root)
    elif args.command == 'references':
        assert not rest
        workspace = ROOT / '.workspace'
        assert workspace.is_dir(), 'Run prepare first'
        sys.path.insert(0, str(workspace / 'tools/blender'))
        from prepare_shared_construction_references import build_index
        actual = build_index(workspace, args.legacy_root, check=False)
        expected = json.loads((workspace / 'docs/reconstruction/models/shared-construction-references.json').read_text())
        assert actual == expected, 'Regenerated local reference cache differs from historical evidence'
        reference_index = workspace / 'docs/reconstruction/models/rigellian-building-references.json'
        before = reference_index.read_bytes()
        subprocess.run([sys.executable, str(workspace / 'tools/blender/prepare_rigellian_building_references.py')],
                       cwd=workspace, check=True)
        assert reference_index.read_bytes() == before, 'Rigellian reference metadata changed during cache decoding'
        print('LOCAL_REFERENCE_CACHE_OK', actual['family_count'], flush=True)
    else:
        workspace = ROOT / '.workspace'
        assert workspace.is_dir(), 'Run prepare first'
        assert rest, 'Specify a script relative to the assembled workspace'
        script = (workspace / rest[0]).resolve()
        assert script.is_relative_to(workspace.resolve()) and script.is_file()
        if args.command == 'python':
            command = [sys.executable, str(script), *rest[1:]]
        else:
            assert args.blender and args.blender.is_file(), 'Pass --blender path/to/blender.exe'
            command = [str(args.blender), '--background', '--factory-startup',
                       '--python-exit-code', '1', '--python', str(script)]
            if rest[1:]:
                command += ['--', *rest[1:]]
        subprocess.run(command, cwd=workspace, check=True)


if __name__ == '__main__':
    main()
