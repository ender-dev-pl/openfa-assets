# SPDX-License-Identifier: MIT
"""Resolve explicit ordered path scopes; unknown paths receive no license grant."""
from collections import Counter
import json
from pathlib import PurePosixPath


def validate_policy(policy):
    if policy.get('schema_version') != 1:
        raise ValueError('Unsupported licensing policy')
    seen_ids, seen_paths = set(), set()
    for rule in policy['rules']:
        if rule['id'] in seen_ids:
            raise ValueError('Duplicate licensing rule: '+rule['id'])
        seen_ids.add(rule['id'])
        if rule.get('reviewed_general_source'):
            if (rule.get('prefixes') or not rule.get('paths')
                    or rule.get('license_expression') != 'MIT'
                    or rule.get('kind') != 'general-tool'
                    or any(not path.startswith('sources/tools/') or PurePosixPath(path).suffix != '.py'
                           for path in rule['paths'])):
                raise ValueError('Reviewed general sources require exact Python tool paths and MIT')
        if not rule.get('paths') and not rule.get('prefixes'):
            raise ValueError('Rule must have an explicit path scope')
        for path in rule.get('paths', []) + rule.get('prefixes', []):
            clean = path.rstrip('/')
            if not clean or PurePosixPath(clean).is_absolute() or '..' in PurePosixPath(clean).parts or ':' in path or '\\' in path:
                raise ValueError('Expected safe repository-relative licensing path')
        for path in rule.get('paths', []):
            if path in seen_paths:
                raise ValueError('Conflicting exact licensing path: '+path)
            seen_paths.add(path)


def classify(path, policy):
    path = str(path)
    if PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts or ':' in path or '\\' in path:
        raise ValueError('Expected repository-relative POSIX path')
    for rule in policy['rules']:
        scoped = path in rule.get('paths', []) or any(path.startswith(prefix) for prefix in rule.get('prefixes', []))
        if scoped and (not rule.get('suffixes') or PurePosixPath(path).suffix in rule['suffixes']):
            return {key: rule[key] for key in ['id', 'license_expression', 'kind', 'notice']}
    raise ValueError('Unclassified publication file: '+path)


def load_policy(root):
    policy = json.loads((root/'project/licensing.json').read_text(encoding='utf-8'))
    validate_policy(policy)
    return policy


def audit(root, paths):
    policy = load_policy(root)
    reviewed_sources = {path for rule in policy['rules'] if rule.get('reviewed_general_source')
                        for path in rule.get('paths', [])}
    counts = Counter()
    sources, exceptions = [], []
    path_set = set(paths)
    for rule in policy['rules']:
        for path in rule.get('paths', []):
            if path not in path_set:
                raise ValueError('Stale explicit licensing path: '+path)
    for path in sorted(path_set):
        if not (root/path).is_file() or (root/path).is_symlink():
            raise ValueError('Expected regular publication file: '+path)
        row = dict(path=path, **classify(path, policy))
        if 'MIT' in row['license_expression'] and ((path.startswith(('sources/', 'archive/')) and path not in reviewed_sources) or PurePosixPath(path).suffix in {'.blend','.glb','.png','.jpg','.webm','.ttf'}):
            raise ValueError('Creative source or payload must not receive a tooling MIT grant: '+path)
        counts[row['kind']] += 1
        if row['kind'] in ['asset-specific-source','general-tool']:
            sources.append(row)
        if row['kind'] in ['excluded','third-party']:
            exceptions.append(row)
    return dict(scope='Path licensing declarations, not proof of copyright ownership or a Git-history audit.',
                files=len(path_set), counts=dict(sorted(counts.items())), sources=sources, exceptions=exceptions)
