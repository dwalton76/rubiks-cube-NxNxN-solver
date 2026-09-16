#!/usr/bin/env python3
"""
Compare the shared symmetry-compacted 7x7x7 perfect table against the three raw
per-axis tables it replaces.

Both binaries are asked for --print-ranks on the same reachable states. The
per-axis costs and the combined cost must agree exactly; only the rank values
differ, since one indexes raw 70^5 ranks and the other symmetry orbits.

usage: compare-777-perfect-symmetry.py --old BINARY [--new BINARY] [--states N]
                                       [--moves N] [--stage {daisy,solve}]
"""

# standard libraries
import argparse
import random
import subprocess
import sys
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import DAISY_CENTERS_ILLEGAL_MOVES_777, RubiksCube777, moves_777, solved_777

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "lookup-tables"
LEGAL_MOVES = [move for move in moves_777 if move not in set(DAISY_CENTERS_ILLEGAL_MOVES_777)]
AXES = ("UD", "LR", "FB")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--old", required=True, help="binary built before the symmetry change")
parser.add_argument("--new", default=str(ROOT / "ida_search_777_daisy_centers"))
parser.add_argument("--states", type=int, default=40)
parser.add_argument("--moves", type=int, default=12)
parser.add_argument("--stage", choices=("daisy", "solve"), default="daisy")
parser.add_argument("--seed", type=int, default=20260914)
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
        "the three raw per-axis tables this compares against are gone; "
        "they were deleted after the compacted pair was verified. Missing:\n  " + "\n  ".join(missing)
    )
new_tables = [
    "--perfect-cost",
    str(compact),
    "--perfect-index",
    f"{compact}.symmetry-index.bin",
]
native_only = ["--native-only"] if args.stage == "solve" else []


def parse_ranks(stdout):
    line = next(line for line in stdout.splitlines() if "_LEFT_OBLIQUE_RANK " in line)
    tokens = line.split()
    return {tokens[index]: int(tokens[index + 1]) for index in range(0, len(tokens), 2)}


def run(binary, tables, kociemba):
    command = [binary, "--kociemba", kociemba, *tables, *native_only, "--print-ranks"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        sys.exit(f"{binary} failed\n{' '.join(command)}\n{result.stdout}{result.stderr}")
    return parse_ranks(result.stdout)


random.seed(args.seed)
mismatches = 0

for index in range(args.states):
    cube = RubiksCube777(solved_777, "URFDLB")
    for _ in range(args.moves):
        cube.rotate(random.choice(LEGAL_MOVES))
    kociemba = cube.get_kociemba_string(True)

    old = run(args.old, old_tables, kociemba)
    new = run(args.new, new_tables, kociemba)

    for key in ("COST", "DAISY", *(f"{axis}_PERFECT_COST" for axis in AXES)):
        if old[key] != new[key]:
            print(f"MISMATCH state {index} {key}: old {old[key]}, new {new[key]}")
            mismatches += 1

print(
    f"{args.stage}: {args.states} states, {args.moves} random moves each, "
    f"{mismatches} mismatches across the three per-axis costs and the combined cost"
)
sys.exit(1 if mismatches else 0)
