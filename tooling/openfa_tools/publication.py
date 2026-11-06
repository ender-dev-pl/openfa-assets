# SPDX-License-Identifier: MIT
"""Metadata-only publication transformations; no user-specific paths in output."""
import ctypes
import hashlib
import os
from pathlib import Path
import re
import struct
import zlib

ABSOLUTE = re.compile(rb'(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]+(?:Users|tools|Program Files|work|tmp|git)[\\/][\x20-\x7e]*|/(?:home|Users)/[\x20-\x7e]*)')
PRIVATE = re.compile(rb'(?<![A-Za-z0-9])[A-Za-z]:[\\/]+|/(?:home|Users)/|file:' + rb'///', re.I)
SECRET = re.compile(rb'gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|sk-[A-Za-z0-9_-]{25,}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def zstd(data, compress=False):
    try:
        import zstandard
        if compress:
            return zstandard.ZstdCompressor(level=3).compress(data)
        import io
        with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data)) as stream:
            return stream.read()
    except ImportError:
        # Local fallback uses the library bundled with Git for Windows.
        import shutil
        git = Path(shutil.which('git')).resolve()
        choices = [git.parent / 'libzstd.dll', git.parent.parent / 'mingw64/bin/libzstd.dll']
        library = next((p for p in choices if p.is_file()), None)
        if library is None:
            raise RuntimeError('Install requirements-publication.txt to inspect compressed Blend files')
        lib = ctypes.CDLL(str(library))
        if compress:
            lib.ZSTD_compressBound.argtypes = [ctypes.c_size_t]
            lib.ZSTD_compressBound.restype = ctypes.c_size_t
            capacity = lib.ZSTD_compressBound(len(data))
            lib.ZSTD_compress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
            lib.ZSTD_compress.restype = ctypes.c_size_t
            output = ctypes.create_string_buffer(capacity)
            size = lib.ZSTD_compress(output, capacity, data, len(data), 3)
        else:
            lib.ZSTD_decompressBound.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            lib.ZSTD_decompressBound.restype = ctypes.c_ulonglong
            capacity = lib.ZSTD_decompressBound(data, len(data))
            if capacity > 1024 * 1024 * 1024:
                raise ValueError('Invalid or oversized Zstandard input')
            lib.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
            lib.ZSTD_decompress.restype = ctypes.c_size_t
            output = ctypes.create_string_buffer(capacity)
            size = lib.ZSTD_decompress(output, capacity, data, len(data))
        lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
        if lib.ZSTD_isError(size):
            raise ValueError('Zstandard operation failed')
        return output.raw[:size]


def blend_bytes(data):
    if data.startswith(b'\x28\xb5\x2f\xfd'):
        data = zstd(data)
    elif data.startswith(b'\x1f\x8b'):
        import gzip
        data = gzip.decompress(data)
    if not data.startswith(b'BLENDER'):
        raise ValueError('Unsupported Blend encoding')
    return data


def clean_blend(data, resolver=None):
    raw = blend_bytes(data)
    edits = []
    # Blender serializes these values as fixed-width, NUL-terminated char arrays.
    # Replace only the existing string bytes and zero-fill, preserving all block
    # sizes, pointer addresses, DNA, geometry, animation and packed image payloads.
    def replace(match):
        old = match.group()
        name = re.split(rb'[\\/]', old.rstrip(b'\\/'))[-1]
        new = resolver(old) if resolver else None
        if new is None:
            new = b'//' + name if b'.' in name else b'//'
        if len(new) > len(old):
            new = b'//'
        edits.append((match.start(), match.end()))
        return new + b'\0' * (len(old) - len(new))
    cleaned = ABSOLUTE.sub(replace, raw)
    assert len(cleaned) == len(raw)
    # Every byte outside the disclosed path strings must remain identical.
    cursor = 0
    for start, end in edits:
        assert raw[cursor:start] == cleaned[cursor:start]
        cursor = end
    assert raw[cursor:] == cleaned[cursor:]
    assert not ABSOLUTE.search(cleaned)
    return zstd(cleaned, compress=True), len(edits), digest(raw), digest(cleaned)


def png_chunks(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Invalid PNG')
    offset = 8
    while offset < len(data):
        size = struct.unpack_from('>I', data, offset)[0]
        end = offset + size + 12
        chunk = data[offset:end]
        if len(chunk) != size + 12:
            raise ValueError('Truncated PNG')
        yield chunk[4:8], chunk
        offset = end


def clean_png(data):
    # Strip text, EXIF and timestamps; retain all colour/alpha/image chunks
    # byte-for-byte. No re-encoding or changes to rendered pixels.
    return data[:8] + b''.join(chunk for kind, chunk in png_chunks(data)
                              if kind not in {b'tEXt', b'zTXt', b'iTXt', b'eXIf', b'tIME'})


def clean_jpeg(data):
    if not data.startswith(b'\xff\xd8'):
        raise ValueError('Invalid JPEG')
    output = data[:2]
    offset = 2
    while offset < len(data):
        if data[offset] != 255:
            raise ValueError('Invalid JPEG marker')
        marker = data[offset + 1]
        if marker in {0xda, 0xd9}:
            return output + data[offset:]
        size = int.from_bytes(data[offset + 2:offset + 4], 'big')
        end = offset + 2 + size
        # EXIF/XMP (APP1), Photoshop/IPTC (APP13), comments.
        if marker not in {0xe1, 0xed, 0xfe}:
            output += data[offset:end]
        offset = end
    return output


def clean_text(data):
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        data = data.decode('utf-16').encode('utf-8')
    # Keep only a generic filename in retained diagnostic reports/examples.
    paths = re.compile(rb'(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]+[^\s\x00"\x27`<>|]+|/(?:home|Users)/[^\s\x00"\x27`<>|]+)')
    return paths.sub(lambda m: b'[local]/' + re.split(rb'[\\/]', m.group().rstrip(b'\\/'))[-1],
                        data)
