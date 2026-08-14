#!/usr/bin/env python3
"""
Split the bitmap font strip (info.png) into one PNG per glyph for visual
debugging and for aligning TEXT_INDEX with the actual art order.

Run from the repository root::

  uv run python scripts/dump_font_glyphs.py
  uv run python scripts/dump_font_glyphs.py -o /tmp/font-glyphs

Output files are named like ``info_23_y.png`` (index + character label from
magicor.Text.TEXT_INDEX). Open the folder and confirm each glyph matches its
label; if not, TEXT_INDEX should be adjusted to match the strip.
"""
from __future__ import annotations

import argparse
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import pygame


_LABEL_SAFE = {
    ".": "dot",
    ",": "comma",
    "!": "bang",
    "?": "qmark",
}


def _safe_label(ch: str) -> str:
    return _LABEL_SAFE.get(ch, ch)


def _glyph_rect(index: int, cell: int | None, fw: int, n: int, height: int) -> pygame.Rect:
    if cell is not None:
        return pygame.Rect(index * cell, 0, cell, height)
    left = int(round(index * fw / n))
    right = int(round((index + 1) * fw / n))
    w = max(1, right - left)
    return pygame.Rect(left, 0, w, height)


def dump_strip(
    font_path: str,
    out_dir: str,
    basename: str,
    text_index: str,
) -> None:
    os.makedirs(out_dir, exist_ok=True)
    surf = pygame.image.load(font_path)
    fw = int(surf.get_width())
    fh = int(surf.get_height())
    n = len(text_index)
    cell = fw // n if fw % n == 0 else None

    print("Font: %s" % os.path.abspath(font_path))
    print("Size: %d x %d, glyphs: %d, cell: %s" % (fw, fh, n, cell if cell else "fractional"))
    print()
    print("idx  char  filename")
    print("---  ----  --------")

    for i, ch in enumerate(text_index):
        src = _glyph_rect(i, cell, fw, n, fh)
        tile = surf.subsurface(src).copy()
        label = _safe_label(ch)
        fn = "%s_%02d_%s.png" % (basename, i, label)
        out_path = os.path.join(out_dir, fn)
        pygame.image.save(tile, out_path)
        print("%3d  %-4r  %s" % (i, ch, fn))


def main() -> int:
    pygame.init()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.join(_REPO_ROOT, "debug", "font-glyphs"),
        help="Output directory (created if missing)",
    )
    parser.add_argument(
        "--data-dir",
        default=os.path.join(_REPO_ROOT, "data", "fonts"),
        help="Directory containing info.png (and optional info-inactive.png)",
    )
    args = parser.parse_args()

    from magicor import Text

    text_index = Text.TEXT_INDEX

    fonts = [
        ("info", os.path.join(args.data_dir, "info.png")),
        ("info-inactive", os.path.join(args.data_dir, "info-inactive.png")),
    ]
    for basename, path in fonts:
        if not os.path.isfile(path):
            print("Skip (not found): %s" % path, file=sys.stderr)
            continue
        print()
        dump_strip(path, args.output, basename, text_index)
        print("Wrote under: %s" % os.path.abspath(args.output))

    print()
    print("Compare each PNG label to the drawn glyph. If labels do not match art,")
    print("edit magicor.Text.TEXT_INDEX so index order matches the strip left-to-right.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
