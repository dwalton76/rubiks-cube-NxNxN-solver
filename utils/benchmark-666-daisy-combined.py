#!/usr/bin/env python3

"""Compare weighted heuristics for the combined 6x6x6 daisy search."""

# standard libraries
import argparse
import json
import re
import statistics
import subprocess
import time
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube666 import DAISY_PLUS_TABLES_666, RubiksCube666

BINARY = "./ida_search_666_daisy_centers"
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True)]
    for flag, filename in DAISY_PLUS_TABLES_666:
        cmd.extend((flag, filename))
    if multiplier is not None:
        cmd.extend(("--multiplier", str(multiplier)))
    return cmd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("multipliers", nargs="+", help="numbers or 'matrix'")
    parser.add_argument("--cubes", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    multipliers = [None if value == "matrix" else float(value) for value in args.multipliers]
    states = json.loads((Path(__file__).parent / "10k-666-cubes.json").read_text())["6x6x6"][: args.cubes]
    results = {multiplier: [] for multiplier in multipliers}
    for sample, state in enumerate(states):
        cube = RubiksCube666(state, "URFDLB")
        cube.lt_init()
        cube.stage_centers()
        for multiplier in multipliers:
            started = time.perf_counter()
            try:
                proc = subprocess.run(
                    solve_command(cube, multiplier),
                    capture_output=True,
                    text=True,
                    timeout=args.timeout,
                )
                wall = time.perf_counter() - started
                match = SOLUTION_RE.search(proc.stdout + proc.stderr)
                moves = int(match.group(1)) if proc.returncode == 0 and match else None
                status = "ok" if moves is not None else "FAIL"
            except subprocess.TimeoutExpired:
                wall = args.timeout
                moves = None
                status = "TIMEOUT"

            results[multiplier].append((wall, moves))
            label = multiplier if multiplier is not None else "matrix"
            print(
                f"DAISY_666 sample={sample:03d} multiplier={label} "
                f"wall={wall:.3f} moves={moves} {status}",
                flush=True,
            )

    for multiplier, measurements in results.items():
        solved = [(wall, moves) for wall, moves in measurements if moves is not None]
        walls = [wall for wall, _ in solved]
        moves = [moves for _, moves in solved]
        label = multiplier if multiplier is not None else "matrix"
        print(
            f"DAISY_666_SUMMARY multiplier={label} "
            f"solved={len(solved)}/{len(measurements)} "
            f"median_wall={statistics.median(walls) if walls else 0:.3f} "
            f"max_wall={max(walls) if walls else 0:.3f} "
            f"median_moves={statistics.median(moves) if moves else 0} "
            f"max_moves={max(moves) if moves else 0}",
            flush=True,
        )


if __name__ == "__main__":
    main()
