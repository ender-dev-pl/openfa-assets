"""Generate native-only colored caps; no original-game pixels are copied.

RGB values are the semantic button colors verified in the original main-menu
reference (artifacts/issue-534-visual-probe/main-menu.png). The delivered row owns
the metal socket/rim; these antialiased discs fill its 24x24 logical-pixel well.
"""
import binascii
import argparse
import math
from pathlib import Path
import struct
import zlib


COLORS = [
    (194, 45, 24),   # 0: saved games, red
    (206, 125, 24),  # 1: intro, orange
    (182, 154, 20),  # 2: quit, yellow
    (4, 89, 8),     # 3: new game / play colony, green
    (16, 24, 162),  # 4: tutorials, dark blue
    (16, 81, 162),  # 5: options, blue
    (113, 36, 158), # 6: multiplayer, purple
]


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack(
        '>I', binascii.crc32(kind + data) & 0xffffffff)


def generate(output):
    output.mkdir(parents=True, exist_ok=True)
    size = 96
    for index, color in enumerate(COLORS):
        rows = bytearray()
        for y in range(size):
            rows.append(0)
            for x in range(size):
                distance = math.hypot(x + 0.5 - size / 2, y + 0.5 - size / 2)
                coverage = max(0, min(1, size / 2 - distance))
                rows.extend((*color, round(255 * coverage)))
        data = b'\x89PNG\r\n\x1a\n'
        data += chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
        data += chunk(b'IDAT', zlib.compress(rows, 9))
        data += chunk(b'IEND', b'')
        (output / f'button-cap-{index}.png').write_bytes(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[3] / 'gallery/media/ui/menu-button-adapters/native')
    generate(parser.parse_args().output)
