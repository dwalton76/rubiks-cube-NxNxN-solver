#!/usr/bin/env python3

"""
Measure average moves to reduce 4x4x4 through 10x10x10 cubes to a 3x3x3
and optionally insert a new row in the README Move Counts table.

Example:
    cd ~/rubiks-cube-NxNxN-solver
    ./venv/bin/python3 utils/update-move-count-table.py
    ./venv/bin/python3 utils/update-move-count-table.py --update-readme
"""

# standard libraries
import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_666
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_777
from rubikscubennnsolver.RubiksCubeNNNEven import RubiksCubeNNNEven, solved_888, solved_101010
from rubikscubennnsolver.RubiksCubeNNNOdd import RubiksCubeNNNOdd, solved_999

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ORDER = "URFDLB"
DEFAULT_SIZES = ("4x4x4", "5x5x5", "6x6x6", "7x7x7", "8x8x8", "9x9x9", "10x10x10")
GITHUB_COMMIT_URL = "https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit"

CUBE_CLASSES = {
    "4x4x4": (RubiksCube444, solved_444),
    "5x5x5": (RubiksCube555, solved_555),
    "6x6x6": (RubiksCube666, solved_666),
    "7x7x7": (RubiksCube777, solved_777),
    "8x8x8": (RubiksCubeNNNEven, solved_888),
    "9x9x9": (RubiksCubeNNNOdd, solved_999),
    "10x10x10": (RubiksCubeNNNEven, solved_101010),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Average reduce-to-3x3x3 move counts for the README table")
    parser.add_argument("--count", type=int, default=10, help="scrambles per size (default: 10)")
    parser.add_argument(
        "--sizes",
        nargs="+",
        default=list(DEFAULT_SIZES),
        help="cube sizes to measure (default: 4x4x4 through 10x10x10)",
    )
    parser.add_argument("--update-readme", action="store_true", help="insert a new row at the top of the README table")
    parser.add_argument("--readme", type=Path, default=README, help="README.md to update")
    parser.add_argument("--quiet", action="store_true", help="hide IDA search logs")
    return parser.parse_args()


def git_output(*args) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def format_average(value: float) -> str:
    rounded = round(value, 1)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.1f}"


def table_cells(line: str) -> List[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_counts(cells: List[str]) -> Dict[str, float]:
    if len(cells) != len(DEFAULT_SIZES):
        raise ValueError(f"expected {len(DEFAULT_SIZES)} move-count cells, found {len(cells)}: {cells}")
    values = {}
    for size, text in zip(DEFAULT_SIZES, cells):
        if text.startswith("**") and text.endswith("**"):
            text = text[2:-2]
        values[size] = float(text)
    return values


def previous_row_counts(readme: Path) -> Dict[str, float]:
    lines = readme.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("| Date |"):
            cells = table_cells(lines[index + 2])
            if len(cells) != 2 + len(DEFAULT_SIZES):
                raise ValueError(f"could not parse previous table row: {lines[index + 2]}")
            return parse_counts(cells[2:])
    raise ValueError(f"Move Counts table not found in {readme}")


def reduce_to_333_length(cube) -> int:
    cube.lt_init()
    if cube.is_odd() or cube.centers_solved():
        cube.rotate_U_to_U()
        cube.rotate_F_to_F()
    cube.reduce_333()
    if not cube.reduced_to_333():
        raise RuntimeError(f"{cube} was not reduced to 3x3x3")
    cube.compress_solution()
    return cube.get_solution_len_minus_rotates(cube.solution)


def measure_size(size: str, count: int) -> List[int]:
    cube_class, solved_state = CUBE_CLASSES[size]
    cube = cube_class(solved_state, ORDER)
    cube.enable_print_cube = False
    lengths = []

    for index in range(1, count + 1):
        cube.re_init()
        cube.randomize()
        length = reduce_to_333_length(cube)
        lengths.append(length)
        average = sum(lengths) / len(lengths)
        logger.info("%s cube %d/%d: %d moves (running avg %s)", size, index, count, length, format_average(average))

    return lengths


def format_cell(value: float, previous: Optional[float]) -> str:
    text = format_average(value)
    if previous is not None and value < previous:
        return f"**{text}**"
    return text


def build_row(averages: Dict[str, float], previous: Dict[str, float]) -> str:
    try:
        full = git_output("rev-parse", "HEAD")
        short = git_output("rev-parse", "--short=8", "HEAD")
        commit = f"[{short}]({GITHUB_COMMIT_URL}/{full})"
    except subprocess.CalledProcessError:
        commit = "[TBD](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/TBD)"

    date = datetime.now().strftime("%m/%d/%Y")
    cells = [format_cell(averages[size], previous.get(size)) for size in DEFAULT_SIZES]
    return f"| {date} | {commit} | " + " | ".join(cells) + " |"


def update_readme(readme: Path, row: str) -> None:
    lines = readme.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("| Date |"):
            separator = index + 1
            if not lines[separator].startswith("| ------"):
                raise ValueError(f"unexpected table separator: {lines[separator]}")
            lines.insert(separator + 1, row)
            readme.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            logger.info("inserted row into %s", readme)
            return
    raise ValueError(f"Move Counts table not found in {readme}")


def main() -> int:
    args = parse_args()
    os.chdir(ROOT)

    if args.quiet:
        logging.getLogger("rubikscubennnsolver").setLevel(logging.WARNING)

    if args.count < 1:
        logger.error("--count must be at least 1")
        return 1

    unknown = [size for size in args.sizes if size not in CUBE_CLASSES]
    if unknown:
        logger.error("unknown sizes: %s", ", ".join(unknown))
        return 1

    previous = previous_row_counts(args.readme)
    averages = dict(previous)

    for size in args.sizes:
        lengths = measure_size(size, args.count)
        averages[size] = sum(lengths) / len(lengths)
        logger.info("%s average over %d cubes: %s", size, args.count, format_average(averages[size]))

    row = build_row(averages, previous)
    print(row)

    if args.update_readme:
        update_readme(args.readme, row)

    return 0


if __name__ == "__main__":
    configure_logging()
    sys.exit(main())
