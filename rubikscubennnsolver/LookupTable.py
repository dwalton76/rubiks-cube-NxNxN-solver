# standard libraries
import os
import sys


class NoIDASolution(Exception):
    pass


_TABLE_TARGETS = (
    ("3x3x3", "333-tables"),
    ("4x4x4", "444-tables"),
    ("5x5x5", "555-tables"),
    ("6x6x6", "666-tables"),
    ("7x7x7", "777-tables"),
)

# Tables that make NNN-tables does not build. Each has its own target in ../rubiks-cube-lookup-tables.
_SEPARATE_TABLE_TARGETS = {
    "lookup-table-5x5x5-step13-LR-t-x-centers-joint.sym-nibble.bin": "555-lr-joint",
}


def _make_target(filename: str) -> str:
    basename = os.path.basename(filename)
    for marker, target in _TABLE_TARGETS:
        if marker in basename:
            return target
    return ""


def download_file_if_needed(filename: str) -> None:
    """Stop the solve when a lookup table has not been built yet.

    ``make 444-tables`` (and the 333, 555, 666, and 777 targets) build every
    table for that cube size into ``lookup-tables/``. An existing file is kept.
    """
    if os.path.exists(filename):
        return
    basename = os.path.basename(filename)
    separate = _SEPARATE_TABLE_TARGETS.get(basename)
    target = _make_target(filename)
    if separate:
        instruction = (
            f"Build it in ../rubiks-cube-lookup-tables with:\n\n    make {separate}\n\n"
            f"then move lookup-tables/{basename} into this repo's lookup-tables/.\n"
        )
    elif target:
        instruction = f"Build them with:\n\n    make {target}\n"
    else:
        instruction = (
            "Build them with make 333-tables, make 444-tables, make 555-tables, "
            "make 666-tables, or make 777-tables.\n"
        )
    print(f"Missing lookup table {filename}\n{instruction}", file=sys.stderr)
    raise SystemExit(1)
