"""Ordering helpers for the level list.

Levels used to appear in whatever order `os.listdir` returned, which is
filesystem-dependent and arbitrary. The old sort that was meant to fix this
is still commented out in `magicor/states/title.py` — and it could not have
worked anyway: it compared titles as plain strings, so "Forest 10" sorted
before "Forest 2", and it used `cmp`-style logic that Python 3 removed.

Level titles are not written consistently:

    Forest 01, Forest 02, ... forest 14, forest 15   (casing drifts)
    snow 01, snow 02, ... snow-06, snow-07           (separator drifts)
    egypt 15                                          (casing drifts too)

So the sort key has to be case-insensitive and number-aware, and it has to
group by theme so a player finishes one world before starting the next.
"""

import re

# Split a title into text and number chunks so "Forest 10" sorts after
# "Forest 2" instead of before it. Returns a tuple of comparable parts:
# numbers compare as numbers, words compare as lowercase text.
_NUMBER_RUN = re.compile(r"(\d+)")


def title_sort_key(title):
    """Natural sort key for a level title, ignoring case and separator style.

    "Forest 02", "forest 10" and "snow-06" all sort by their word parts in
    lowercase and their number parts as integers, so 10 follows 2 and the
    casing and dash/space differences stop mattering.
    """
    text = (title or "").strip().lower().replace("-", " ")
    parts = []
    for chunk in _NUMBER_RUN.split(text):
        if not chunk:
            continue
        if chunk.isdigit():
            # Numbers sort ahead of words at the same position, and by value.
            parts.append((0, int(chunk), ""))
        else:
            parts.append((1, 0, chunk.strip()))
    return parts


def level_sort_key(level):
    """Sort key for a Level: theme first, then the title naturally.

    Grouping by theme keeps a world's levels together instead of interleaving
    "Egypt 03" between "Forest 03" and "Forest 04". The theme is lowercased
    for the same casing-drift reason as the title.
    """
    theme = (getattr(level, "theme", None) or "").strip().lower()
    return (theme, title_sort_key(getattr(level, "title", None) or ""))
