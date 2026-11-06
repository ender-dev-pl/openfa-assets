"""Reconstruct the linear memory image described by a DOS/4G LE executable."""

from __future__ import annotations

import argparse
import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path


PAGE_SIZE_OFFSET = 0x28
BYTES_ON_LAST_PAGE_OFFSET = 0x2C
PAGE_COUNT_OFFSET = 0x14
OBJECT_TABLE_OFFSET = 0x40
OBJECT_COUNT_OFFSET = 0x44
OBJECT_PAGE_MAP_OFFSET = 0x48
DATA_PAGES_OFFSET = 0x80
OBJECT_SIZE = 24
PAGE_MAP_ENTRY_SIZE = 4


class LeFormatError(ValueError):
    """Raised when an input is not a supported Linear Executable."""


@dataclass(frozen=True)
class ObjectInfo:
    number: int
    virtual_size: int
    base_address: int
    flags: int
    page_map_index: int
    page_count: int


def u32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise LeFormatError(f"truncated 32-bit field at 0x{offset:X}")
    return struct.unpack_from("<I", data, offset)[0]


def parse_le(data: bytes) -> tuple[int, int, int, int, list[ObjectInfo]]:
    if data[:2] != b"LE":
        raise LeFormatError("missing LE signature")
    if len(data) < DATA_PAGES_OFFSET + 4:
        raise LeFormatError("truncated LE header")

    page_size = u32(data, PAGE_SIZE_OFFSET)
    page_count = u32(data, PAGE_COUNT_OFFSET)
    bytes_on_last_page = u32(data, BYTES_ON_LAST_PAGE_OFFSET)
    data_pages_offset = u32(data, DATA_PAGES_OFFSET)
    object_table_offset = u32(data, OBJECT_TABLE_OFFSET)
    object_count = u32(data, OBJECT_COUNT_OFFSET)
    if page_size == 0 or page_size & (page_size - 1):
        raise LeFormatError(f"unsupported page size 0x{page_size:X}")
    if data_pages_offset > len(data):
        raise LeFormatError("data pages begin beyond end of file")
    if object_count == 0:
        raise LeFormatError("LE contains no objects")

    objects: list[ObjectInfo] = []
    for index in range(object_count):
        offset = object_table_offset + index * OBJECT_SIZE
        if offset + OBJECT_SIZE > len(data):
            raise LeFormatError("truncated object table")
        objects.append(
            ObjectInfo(
                number=index + 1,
                virtual_size=u32(data, offset),
                base_address=u32(data, offset + 4),
                flags=u32(data, offset + 8),
                page_map_index=u32(data, offset + 12),
                page_count=u32(data, offset + 16),
            )
        )
    if page_count == 0 or bytes_on_last_page > page_size:
        raise LeFormatError("invalid physical page count or final page length")
    return page_size, page_count, bytes_on_last_page, data_pages_offset, objects


def page_number(data: bytes, page_map_offset: int, index: int) -> tuple[int, int]:
    """Return LE's big-endian 24-bit page number and its page flags."""

    offset = page_map_offset + (index - 1) * PAGE_MAP_ENTRY_SIZE
    if offset + PAGE_MAP_ENTRY_SIZE > len(data):
        raise LeFormatError(f"truncated page map entry {index}")
    return (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2], data[offset + 3]


def reconstruct(source: Path, destination: Path) -> dict[str, object]:
    data = source.read_bytes()
    page_size, page_count, bytes_on_last_page, data_pages_offset, objects = parse_le(data)
    page_map_offset = u32(data, OBJECT_PAGE_MAP_OFFSET)
    image_size = max(item.base_address + item.virtual_size for item in objects)
    image = bytearray(image_size)
    copied_pages = 0
    zero_pages = 0

    for item in objects:
        for relative_page in range(item.page_count):
            page_index = item.page_map_index + relative_page
            page_number_value, flags = page_number(data, page_map_offset, page_index)
            if flags != 0:
                raise LeFormatError(
                    f"unsupported page flags 0x{flags:X} at object {item.number}, page {relative_page}"
                )
            target = item.base_address + relative_page * page_size
            copy_size = min(page_size, item.virtual_size - relative_page * page_size)
            if copy_size <= 0:
                continue
            if page_number_value == 0:
                zero_pages += 1
                continue
            source_offset = data_pages_offset + (page_number_value - 1) * page_size
            source_size = page_size
            if page_number_value == page_count and bytes_on_last_page:
                source_size = bytes_on_last_page
            source_size = min(source_size, copy_size)
            if source_offset + source_size > len(data):
                raise LeFormatError(
                    f"page {page_number_value} for object {item.number} lies outside the file"
                )
            image[target : target + source_size] = data[source_offset : source_offset + source_size]
            copied_pages += 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(image)
    return {
        "format": "linear-executable-memory-image",
        "source": source.name,
        "source_size": len(data),
        "memory_image": destination.name,
        "memory_image_size": len(image),
        "page_size": page_size,
        "page_count": page_count,
        "bytes_on_last_page": bytes_on_last_page,
        "data_pages_offset": data_pages_offset,
        "copied_pages": copied_pages,
        "zero_pages": zero_pages,
        "objects": [asdict(item) for item in objects],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="input LE executable")
    parser.add_argument("destination", type=Path, help="output flat memory image")
    parser.add_argument("--metadata", type=Path, help="optional JSON description of the mapped objects")
    arguments = parser.parse_args()
    try:
        metadata = reconstruct(arguments.source, arguments.destination)
        if arguments.metadata:
            arguments.metadata.parent.mkdir(parents=True, exist_ok=True)
            arguments.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    except (LeFormatError, OSError) as error:
        print(f"error: {error}")
        return 1
    print(f"Wrote {arguments.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
