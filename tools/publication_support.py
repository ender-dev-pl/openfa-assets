# SPDX-License-Identifier: MIT
"""Compatibility import for the reusable metadata module in tooling/."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tooling'))
from openfa_tools.publication import (  # noqa: E402,F401
    ABSOLUTE, PRIVATE, SECRET, blend_bytes, clean_blend, clean_jpeg,
    clean_png, clean_text, digest, png_chunks, zstd,
)
