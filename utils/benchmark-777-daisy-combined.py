#!/usr/bin/env python3

# standard libraries
import argparse
import json
import statistics
import time
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import RubiksCube777

parser = argparse.ArgumentParser(description="Time the combined 7x7x7 daisy search")
parser.add_argument(
    "multipliers",
    nargs="*",
    type=float,
    help="--multiplier values to compare, default is the sampled per-axis cost matrix",
)
parser.add_argument("--cubes", type=int, default=3, help="how many cubes to solve")
args = parser.parse_args()

# None runs ida_search_777_daisy_centers with no --multiplier, so it uses the matrix.
multipliers = args.multipliers or [None]

states = json.loads((Path(__file__).parent / "10k-777-cubes.json").read_text())["7x7x7"][: args.cubes]
results = {multiplier: [] for multiplier in multipliers}

for index, state in enumerate(states):
    cube = RubiksCube777(state, "URFDLB")
    cube.lt_init()
    cube.stage_LR_centers()
    cube.stage_UD_centers()
    staged_state = cube.state[:]
    staged_solution = cube.solution[:]

    for multiplier in multipliers:
        cube.state = staged_state[:]
        cube.solution = staged_solution[:]
        cube.lt_daisy_centers.multiplier = multiplier

        start = time.monotonic()
        cube.centers_combined_daisy_solve()
        elapsed = time.monotonic() - start
        moves = len(cube.solution) - len(staged_solution)
        results[multiplier].append((elapsed, moves))

        print(
            f"DAISY_COMBINED index={index} multiplier={multiplier or 'matrix'} " f"seconds={elapsed:.6f} moves={moves}",
            flush=True,
        )

for multiplier, measurements in results.items():
    seconds = [elapsed for elapsed, _ in measurements]
    moves = [count for _, count in measurements]
    print(
        f"DAISY_SUMMARY multiplier={multiplier or 'matrix'} cubes={len(measurements)} "
        f"median_seconds={statistics.median(seconds):.6f} max_seconds={max(seconds):.6f} "
        f"median_moves={statistics.median(moves)} max_moves={max(moves)}",
        flush=True,
    )
