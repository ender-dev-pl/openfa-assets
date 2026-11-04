"""Expand authored label wells, preserving circular sockets and row dimensions.

Usage: python expand_native_menu_labels.py [--source original-native-row-directory] [--output directory]
Source: openfa-assets/gallery/media/ui/legacy-main-menu-refined/native
at 78cf3723. Always read original source images, never the expanded outputs.
"""
from pathlib import Path
import argparse
from PIL import Image


def generate(source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for theme in ('amber', 'green', 'blue', 'cyan'):
        for state in ('idle', 'hover', 'selected', 'pressed', 'off'):
            name = f'row-{theme}-{state}.png'
            with Image.open(source / name) as original:
                image = original.convert('RGBA')
            if image.size != (211, 48):
                raise ValueError(f'{name}: expected 211x48 authored row')
            # The left 56 columns contain the circular socket. Expand only the
            # rectangular field; its 28px interior becomes a 42px label well.
            label = image.crop((56, 0, 211, 48)).resize((155, 72), Image.Resampling.LANCZOS)
            image.paste(label.crop((0, 12, 155, 60)), (56, 0))
            image.save(destination / name)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=root / 'gallery/media/ui/legacy-main-menu-refined/native')
    parser.add_argument('--output', type=Path, default=root / 'gallery/media/ui/menu-button-adapters/native')
    options = parser.parse_args()
    generate(options.source, options.output)
