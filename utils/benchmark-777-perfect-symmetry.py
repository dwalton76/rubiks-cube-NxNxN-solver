#!/usr/bin/env python3
"""
Time the shared symmetry-compacted 7x7x7 perfect table against the three raw
per-axis tables.

Both binaries see identical heuristic values, so they explore the same tree and
the node counts match. The seconds per node is what changes: the compact table
has to normalise each axis onto the UD coordinate, take the smallest of 16
symmetric ranks, and resolve that through a rank-select index.

usage: benchmark-777-perfect-symmetry.py --old BINARY [--new BINARY] [--states N]
                                         [--moves N] [--stage {daisy,solve}]
"""

# standard libraries
import argparse
import random
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import DAISY_CENTERS_ILLEGAL_MOVES_777, RubiksCube777, moves_777, solved_777

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "lookup-tables"
LEGAL_MOVES = [move for move in moves_777 if move not in set(DAISY_CENTERS_ILLEGAL_MOVES_777)]
AXES = ("UD", "LR", "FB")
THRESHOLD = re.compile(r"explored (\d+) nodes, took ([0-9.]+)s")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--old", required=True, help="binary built before the symmetry change")
parser.add_argument("--new", default=str(ROOT / "ida_search_777_daisy_centers"))
parser.add_argument("--states", type=int, default=5)
parser.add_argument("--moves", type=int, default=8)
parser.add_argument("--threads", type=int, default=8)
parser.add_argument("--stage", choices=("daisy", "solve"), default="daisy")
parser.add_argument("--seed", type=int, default=20260914)
parser.add_argument("--new-cost", help="override the compacted cost table, for comparing index splits")
parser.add_argument("--new-index", help="override the symmetry index, for comparing index splits")
args = parser.parse_args()

old_tables = []
for axis in AXES:
    old_tables.extend(
        (
            f"--{axis.lower()}-perfect-cost",
            str(TABLES / f"lookup-table-7x7x7-{args.stage}-{axis}-perfect-centers.cost-only.bin"),
        )
    )
compact = TABLES / f"lookup-table-7x7x7-{args.stage}-perfect-centers.cost-only.bin"
missing = [path for _, path in zip(old_tables[0::2], old_tables[1::2]) if not Path(path).is_file()]
if missing:
    sys.exit(
        "the three raw per-axis tables this times against are gone; "
        "they were deleted after the compacted pair was verified. Missing:\n  " + "\n  ".join(missing)
    )
new_tables = [
    "--perfect-cost",
    args.new_cost or str(compact),
    "--perfect-index",
    args.new_index or f"{compact}.symmetry-index.bin",
]
native_only = ["--native-only"] if args.stage == "solve" else []


def solve(binary, tables, kociemba):
    """
    Returns wall clock, the time the searcher itself reported, and the tree size.

    The two are worth separating: the raw tables pre-fault 4.8 GiB at startup,
    which dominates a short search, while the per-threshold timings the searcher
    logs cover only the search and so isolate the cost of a probe.
    """
    command = [binary, "--kociemba", kociemba, *tables, *native_only, "--threads", str(args.threads)]
    start = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True)
    wall = time.monotonic() - start
    if result.returncode:
        sys.exit(f"{binary} failed\n{' '.join(command)}\n{result.stdout}{result.stderr}")
    thresholds = THRESHOLD.findall(result.stdout)
    nodes = sum(int(count) for count, _ in thresholds)
    searching = sum(float(seconds) for _, seconds in thresholds)
    steps = int(re.search(r"SOLUTION \((\d+) steps\)", result.stdout).group(1))
    return wall, searching, nodes, steps


random.seed(args.seed)
search_ratios = []
wall_ratios = []

for index in range(args.states):
    cube = RubiksCube777(solved_777, "URFDLB")
    for _ in range(args.moves):
        cube.rotate(random.choice(LEGAL_MOVES))
    kociemba = cube.get_kociemba_string(True)

    old_wall, old_search, old_nodes, old_steps = solve(args.old, old_tables, kociemba)
    new_wall, new_search, new_nodes, new_steps = solve(args.new, new_tables, kociemba)

    if (old_nodes, old_steps) != (new_nodes, new_steps):
        print(
            f"state {index}: tree differs, old {old_nodes} nodes / {old_steps} steps, "
            f"new {new_nodes} nodes / {new_steps} steps"
        )
    if old_nodes < 100000:
        print(f"state {index}: {old_nodes} nodes, {old_steps} steps, too small to time", flush=True)
        continue
    search_ratios.append(new_search / old_search if old_search else 0)
    wall_ratios.append(new_wall / old_wall if old_wall else 0)
    print(
        f"state {index}: {old_nodes} nodes, {old_steps} steps, "
        f"search {old_search:.3f}s -> {new_search:.3f}s ({search_ratios[-1]:.2f}x), "
        f"wall {old_wall:.3f}s -> {new_wall:.3f}s ({wall_ratios[-1]:.2f}x), "
        f"{old_nodes / old_search / 1e6:.2f}M -> {new_nodes / new_search / 1e6:.2f}M nodes/s",
        flush=True,
    )

if not search_ratios:
    sys.exit("no state was large enough to time, raise --moves")
print(
    f"{args.stage}: {len(search_ratios)} states, search median {statistics.median(search_ratios):.2f}x, "
    f"wall median {statistics.median(wall_ratios):.2f}x the three raw tables"
)
