"""Prepare current authoring sources; enable original-game evidence only explicitly."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MEDIA = {'.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webp', '.html'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layout():
    return json.loads((ROOT / 'project/layout.json').read_text(encoding='utf-8'))


def manifest():
    """Historical evidence only; never used to gate ordinary authoring changes."""
    return json.loads((ROOT / 'migration/files.json').read_text(encoding='utf-8'))


def relative_path(value):
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or not path.parts or ':' in value or '\\' in value:
        raise ValueError(f'Expected a project-relative path: {value}')
    return path


def canonical(item):
    path = (ROOT / relative_path(item['destination'])).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
        raise ValueError(f'Missing or external canonical input: {item["destination"]}')
    return path


def verify():
    """Validate the current layout/boundaries, not imported content equality."""
    policy = ROOT / 'project/excluded-media.json'
    if policy.is_file():
        excluded = json.loads(policy.read_text(encoding='utf-8'))['paths']
        for name in excluded:
            if (ROOT / relative_path(name)).exists():
                raise ValueError(f'Original-game media must remain outside the repository: {name}')
    data = layout()
    originals, destinations, inputs = set(), set(), set()
    for item in data['files']:
        original = relative_path(item['original']).as_posix()
        path = canonical(item)
        if original in originals or path in destinations:
            raise ValueError(f'Duplicate layout entry: {original}')
        originals.add(original)
        destinations.add(path)
        role = item['role']
        if role in ['source-input', 'material-texture']:
            directories = ['sources/ui', 'sources/artwork'] if role == 'source-input' else ['sources/materials']
            extensions = {'.png', '.jpg', '.jpeg', '.gif'} if role == 'source-input' else {'.png'}
            if not any(path.is_relative_to((ROOT / d).resolve()) for d in directories) or path.suffix.lower() not in extensions:
                raise ValueError(f'Misplaced source image: {path}')
            inputs.add(path)
        elif role == 'historical-script':
            if not path.is_relative_to((ROOT / 'archive/repairs').resolve()) or path.suffix != '.py':
                raise ValueError(f'Misplaced historical script: {path}')
        elif role not in ['source', 'fixture', 'media']:
            raise ValueError(f'Unknown layout role: {role}')
    for path in (ROOT / 'sources').rglob('*'):
        if path.is_file() and ((path.suffix.lower() in MEDIA and path.resolve() not in inputs)
                              or path.suffix.lower() in ['.cs', '.java']):
            raise ValueError(f'Unregistered source image, finished media or game code: {path}')
    print('CURRENT_LAYOUT_OK', len(originals), flush=True)
    return data


def audit_import():
    """Optional comparison with unchanged original import hashes, with retirements explicit."""
    data = verify()
    current = {item['original']:item for item in data['files']}
    retired = {item['original'] for item in data.get('retired_imports', [])}
    checked = skipped = 0
    for item in manifest()['files']:
        if item['original'] in retired:
            if item['original'] in current:
                raise ValueError(f'Retired input still active: {item["original"]}')
            skipped += 1
            continue
        path = canonical(current[item['original']])
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError(f'Current input differs from original import (may be intentional): {item["original"]}')
        checked += 1
    print('IMPORT_BASELINE_OK', checked, 'unchanged;', skipped, 'explicitly retired', flush=True)


def junction(link, target):
    target = target.resolve()
    if link.exists():
        if link.resolve() != target:
            raise ValueError(f'Existing link has another target: {link}')
        return
    if not target.is_dir():
        raise ValueError(f'Missing external evidence directory: {target}')
    if os.name == 'nt':
        env = dict(os.environ, OPENFA_ASSETS_LINK=str(link), OPENFA_ASSETS_TARGET=str(target))
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
            "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path $env:OPENFA_ASSETS_LINK -Target $env:OPENFA_ASSETS_TARGET | Out-Null"], env=env, check=True)
    else:
        link.symlink_to(target, target_is_directory=True)


def workspace_path(value=None):
    result = Path(value).resolve() if value else ROOT / '.workspace'
    if not result.resolve().is_relative_to(ROOT.resolve()) or result.resolve().is_relative_to((ROOT / 'sources').resolve()):
        raise ValueError('Workspace must be inside this project and outside sources')
    if result.resolve() == ROOT.resolve() or any(result.resolve().is_relative_to((ROOT / p).resolve()) for p in ['gallery', 'archive', 'migration', 'project', 'tools', 'docs']):
        raise ValueError('Workspace must be .workspace or a dedicated directory under artifacts')
    if result != ROOT / '.workspace' and not result.is_relative_to((ROOT / 'artifacts').resolve()):
        raise ValueError('Custom workspaces must live under artifacts')
    return result


def prepare(workspace=None, include_history=False):
    data = verify()
    workspace = workspace_path(workspace)
    state_path = workspace / '.asset-workspace-state.json'
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    updates, hashes = [], dict(previous)
    conflicts = []
    for item in data['files']:
        if item['role'] == 'historical-script' and not include_history and not item.get('verification_support'):
            continue
        name = item['original']
        dest = workspace / relative_path(name)
        if not dest.resolve().is_relative_to(workspace.resolve()):
            raise ValueError(f'Workspace input resolves outside workspace: {name}')
        source = canonical(item)
        current = sha(source)
        if dest.exists():
            actual = sha(dest)
            if actual != current and actual != previous.get(name):
                conflicts.append(name)
                continue
            if actual == current:
                hashes[name] = current
                continue
        updates.append((source, dest))
        hashes[name] = current
    if conflicts:
        raise ValueError('Preserving edited/unmanaged workspace files; resolve conflicts first: '+', '.join(conflicts))
    # Preflight all conflicts before updating any file.
    for source, dest in updates:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    workspace.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(hashes, indent=2)+'\n', encoding='utf-8')
    os.replace(temporary, state_path)
    (workspace / 'artifacts/ship-reference-study').mkdir(parents=True, exist_ok=True)
    print('WORKSPACE_READY', workspace, 'updated', len(updates), flush=True)
    return workspace


def prepare_evidence(legacy, game, workspace=None):
    """Opt-in legacy/game evidence, including immutable historical support scripts."""
    legacy, game = legacy.resolve(), game.resolve()
    if not legacy.is_dir():
        raise ValueError(f'Missing original installation: {legacy}')
    for item in manifest().get('external_inputs', []):
        source = game / relative_path(item['original'])
        if not source.is_file() or sha(source) != item['sha256']:
            raise ValueError(f'Original game evidence changed/missing: {source}')
    workspace = prepare(workspace, include_history=True)
    for item in manifest().get('external_inputs', []):
        if not item['original'].startswith('src/'):
            dest = workspace / relative_path(item['original'])
            source = game / item['original']
            if dest.exists() and sha(dest) != item['sha256']:
                raise ValueError(f'Preserving edited game naming fixture: {dest}')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
    junction(workspace / 'src', game / 'src')
    junction(workspace.parent / 'legacy', legacy)
    decompile = game / 'artifacts/fragile-le-decompilation'
    if decompile.is_dir():
        junction(workspace / 'artifacts/fragile-le-decompilation', decompile)
    print('OPTIONAL_EVIDENCE_READY', flush=True)
    return workspace


def history_environment(game):
    git_dir = subprocess.check_output(['git', '-C', str(game), 'rev-parse', '--absolute-git-dir'], text=True).strip()
    return dict(os.environ, GIT_DIR=git_dir, GIT_WORK_TREE=str(game.resolve()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['verify', 'audit-import', 'prepare', 'evidence', 'references', 'python', 'blender'])
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('--legacy-root', type=Path, default=ROOT.parent / 'legacy')
    parser.add_argument('--game-root', type=Path, default=ROOT.parent / 'openFA-game')
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--include-history', action='store_true')
    parser.add_argument('--allow-history', action='store_true')
    args, rest = parser.parse_known_args()
    rest = rest[1:] if rest[:1] == ['--'] else rest
    workspace = workspace_path(args.workspace)
    if args.command in ['verify', 'audit-import', 'prepare', 'evidence', 'references'] and rest:
        parser.error('Unexpected script arguments')
    if args.command == 'verify':
        verify()
    elif args.command == 'audit-import':
        audit_import()
    elif args.command == 'prepare':
        prepare(workspace, args.include_history)
    elif args.command in ['evidence', 'references']:
        prepare_evidence(args.legacy_root, args.game_root, workspace)
        if args.command == 'references':
            sys.path.insert(0, str(workspace / 'tools/blender'))
            from prepare_shared_construction_references import build_index
            actual = build_index(workspace, args.legacy_root, check=False)
            expected = json.loads((workspace / 'docs/reconstruction/models/shared-construction-references.json').read_text())
            if actual != expected:
                raise ValueError('Decoded reference cache differs from historical evidence')
            index = workspace / 'docs/reconstruction/models/rigellian-building-references.json'
            before = index.read_bytes()
            subprocess.run([sys.executable, str(workspace / 'tools/blender/prepare_rigellian_building_references.py')], cwd=workspace, check=True)
            if index.read_bytes() != before:
                raise ValueError('Rigellian metadata changed during reference decoding')
            print('LOCAL_REFERENCE_CACHE_OK', actual['family_count'], flush=True)
    else:
        if not workspace.is_dir() or not rest:
            parser.error('Prepare a workspace and specify a script first')
        script_name = relative_path(rest[0]).as_posix()
        entry = next((r for r in layout()['files'] if r['original'] == script_name), None)
        script = (workspace / script_name).resolve()
        if not script.is_relative_to(workspace.resolve()) or not script.is_file():
            parser.error('Script must exist inside the workspace')
        env = None
        if entry and entry['role'] == 'historical-script':
            if not args.allow_history:
                parser.error('Archived one-time script: use a matching historical workspace and --allow-history explicitly')
            env = history_environment(args.game_root)
        if args.command == 'python':
            command = [sys.executable, str(script), *rest[1:]]
        else:
            if not args.blender or not args.blender.is_file():
                parser.error('Pass --blender path/to/blender.exe')
            command = [str(args.blender), '--background', '--factory-startup', '--python-exit-code', '1', '--python', str(script)]
            if rest[1:]:
                command += ['--', *rest[1:]]
        subprocess.run(command, cwd=workspace, env=env, check=True)


if __name__ == '__main__':
    main()
