#!/usr/bin/env python3

# standard libraries
import argparse
import json
import statistics
import time
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import RubiksCube777

parser = argparse.ArgumentParser(description="Time the serial 7x7x7 phase 7/8/9 daisy path")
parser.add_argument("--cubes", type=int, default=3, help="how many cubes to solve")
args = parser.parse_args()

states = json.loads((Path(__file__).parent / "10k-777-cubes.json").read_text())["7x7x7"][: args.cubes]
measurements = []

for index, state in enumerate(states):
    cube = RubiksCube777(state, "URFDLB")
    cube.lt_init()
    cube.stage_LR_centers()
    cube.stage_UD_centers()

    start = time.monotonic()
    solution_start = len(cube.solution)
    cube.LR_centers_vertical_bars()
    cube.UD_centers_vertical_bars()
    cube.centers_daisy_solve()
    elapsed = time.monotonic() - start
    moves = len(cube.solution) - solution_start
    measurements.append((elapsed, moves))

    print(f"DAISY_BASELINE index={index} seconds={elapsed:.6f} moves={moves}", flush=True)

seconds = [elapsed for elapsed, _ in measurements]
moves = [count for _, count in measurements]
print(
    f"DAISY_BASELINE_SUMMARY cubes={len(measurements)} "
    f"median_seconds={statistics.median(seconds):.6f} max_seconds={max(seconds):.6f} "
    f"median_moves={statistics.median(moves)} max_moves={max(moves)}",
    flush=True,
)
