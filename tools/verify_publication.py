"""Fail closed on private paths, credential patterns and hidden image metadata."""
import argparse
import json
from pathlib import Path
import re
import struct
import sys
from PIL import Image
from publication_support import ABSOLUTE, PRIVATE, SECRET, blend_bytes, png_chunks

ROOT = Path(__file__).resolve().parents[1]
TEXT = {'.json', '.py', '.md', '.log', '.txt', '.html', '.yml', '.yaml', '.ps1', '.cjs', '.cs', '.csproj'}
SKIP = {'.git', '.workspace', 'artifacts', '_site', '__pycache__', '.pytest_cache'}


def problems(path):
    data = path.read_bytes()
    findings = []
    if path.suffix == '.blend':
        data = blend_bytes(data)
        # Broad drive syntax is noisy in arbitrary geometry bytes; inspect only
        # printable strings and require a directory component for generic roots.
        directories = re.compile(rb'(?<![A-Za-z0-9])[A-Za-z]:[\\/]+[A-Za-z][A-Za-z0-9_. -]{2,}[\\/]')
        if ABSOLUTE.search(data) or any(directories.search(s) for s in re.findall(rb'[\x20-\x7e]{6,}', data)):
            findings.append('absolute path in native model')
    elif path.suffix == '.glb':
        if data[:4] != b'glTF':
            findings.append('invalid GLB')
        else:
            size = struct.unpack_from('<I', data, 12)[0]
            data = data[20:20 + size]
            if PRIVATE.search(data):
                findings.append('absolute path in GLB JSON')
    elif path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.gif'}:
        with Image.open(path) as image:
            metadata = repr((image.info, dict(image.getexif()))).encode()
            if PRIVATE.search(metadata) or SECRET.search(metadata):
                findings.append('private image metadata')
            if path.suffix.lower() == '.png' and any(kind in {b'tEXt', b'zTXt', b'iTXt', b'eXIf', b'tIME'} for kind, _ in png_chunks(data)):
                findings.append('unreviewed image text/EXIF/timestamp metadata')
        # Image payloads are binary, not text paths.
    elif path.suffix in TEXT or path.name in {'.gitignore', '.gitattributes', 'AGENTS.md'}:
        if data.startswith((b'\xff\xfe', b'\xfe\xff')):
            data = data.decode('utf-16').encode('utf-8')
        if PRIVATE.search(data):
            findings.append('absolute local path in text')
    elif ABSOLUTE.search(data):
        findings.append('absolute path in binary metadata')
    if SECRET.search(data):
        findings.append('credential/private-key signature (value suppressed)')
    if path.name in {'.env', 'id_rsa', 'id_ed25519', '.netrc'} or path.suffix.lower() in {'.pem', '.pfx', '.p12', '.key'}:
        findings.append('credential-like filename')
    return findings


def verify(root):
    failures = []
    count = 0
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part in SKIP for part in relative.parts):
            continue
        if path.is_symlink():
            failures.append((relative.as_posix(), ['symlink is not a publication input']))
        elif path.is_file():
            count += 1
            try:
                errors = problems(path)
            except Exception as error:
                errors = ['cannot inspect file: ' + type(error).__name__]
            if errors:
                failures.append((relative.as_posix(), errors))
        if count and count % 1000 == 0 and path.is_file():
            print('PUBLICATION_SCAN', count, flush=True)
    for name, errors in failures:
        print(name + ': ' + '; '.join(errors))
    print('PUBLICATION_SCAN_RESULT', count, 'files', len(failures), 'failures')
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    verify(parser.parse_args().root.resolve())
