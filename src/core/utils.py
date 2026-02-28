"""Shared utility functions."""

from __future__ import annotations

import json
import pathlib
import re
from collections.abc import Callable


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def write_with_lock_check(path: pathlib.Path, writer_fn: Callable[[pathlib.Path], None]) -> None:
    """Try to write; if the file is locked, prompt the user to close it."""
    while True:
        try:
            writer_fn(path)
            return
        except PermissionError:
            print(f"\n  File is locked: {path}")
            resp = input("  Close the file and press Enter to retry (or type 'q' to skip): ")
            if resp.strip().lower() == "q":
                print(f"  Skipped writing {path}")
                return


def save_json(data: object, path: pathlib.Path) -> None:
    """Write *data* as pretty JSON with UTF-8 encoding."""

    def _writer(p: pathlib.Path) -> None:
        p.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    write_with_lock_check(path, _writer)
    print(f"  Saved {path}")


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------


def sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in Windows / Linux filenames."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = name.strip(". ")
    return name or "_unnamed_"


def parse_range_selection(text: str, max_val: int) -> list[int]:
    """Parse a comma-separated range string like ``"1,3,5-8"`` into a sorted list of ints.

    Values outside ``[1, max_val]`` are silently ignored.
    """
    result: set[int] = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            bounds = part.split("-", 1)
            try:
                lo, hi = int(bounds[0].strip()), int(bounds[1].strip())
            except ValueError:
                continue
            for i in range(lo, hi + 1):
                if 1 <= i <= max_val:
                    result.add(i)
        else:
            try:
                val = int(part)
            except ValueError:
                continue
            if 1 <= val <= max_val:
                result.add(val)
    return sorted(result)
