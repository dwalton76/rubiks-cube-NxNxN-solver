#!/usr/bin/env python3
"""Compare weighted heuristics for 5x5x5 one-phase center staging."""

# standard libraries
import argparse
import json
import re
import statistics
import subprocess
import time
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import LookupTableIDA555CentersStageOnePhase, RubiksCube555

BINARY = "./ida_search_555_centers_stage"
X_TABLE = "lookup-tables/lookup-table-5x5x5-step15-x-centers-stage-one-phase.cost-only.bin"
T_TABLE = "lookup-tables/lookup-table-5x5x5-step16-t-centers-stage-one-phase.cost-only.bin"
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")


def solve_command(state, multiplier):
    cube = RubiksCube555(state, "URFDLB")
    projected = LookupTableIDA555CentersStageOnePhase(cube).center_only_kociemba_string()
    command = [
        BINARY,
        "--kociemba",
        projected,
        "--x-cost",
        X_TABLE,
        "--t-cost",
        T_TABLE,
    ]
    if multiplier is not None:
        command.extend(("--multiplier", str(multiplier)))
    return command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("multipliers", nargs="+", help="numbers or 'matrix'")
    parser.add_argument("--cubes", type=int, default=10)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    multipliers = [None if value == "matrix" else float(value) for value in args.multipliers]
    all_states = json.loads(Path("utils/10k-555-cubes.json").read_text())["5x5x5"]
    states = all_states[args.offset : args.offset + args.cubes]
    results = {multiplier: [] for multiplier in multipliers}
    for cube_index, state in enumerate(states, start=args.offset):
        for multiplier in multipliers:
            started = time.perf_counter()
            try:
                proc = subprocess.run(
                    solve_command(state, multiplier),
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
                f"CENTERS_555 cube={cube_index:03d} multiplier={label} " f"wall={wall:.3f} moves={moves} {status}",
                flush=True,
            )

    for multiplier, measurements in results.items():
        solved = [(wall, moves) for wall, moves in measurements if moves is not None]
        walls = [wall for wall, _moves in solved]
        moves = [moves for _wall, moves in solved]
        label = multiplier if multiplier is not None else "matrix"
        print(
            f"CENTERS_555_SUMMARY multiplier={label} solved={len(solved)}/{len(measurements)} "
            f"median_wall={statistics.median(walls) if walls else 0:.3f} "
            f"max_wall={max(walls) if walls else 0:.3f} "
            f"median_moves={statistics.median(moves) if moves else 0} "
            f"max_moves={max(moves) if moves else 0}",
            flush=True,
        )


if __name__ == "__main__":
    main()
