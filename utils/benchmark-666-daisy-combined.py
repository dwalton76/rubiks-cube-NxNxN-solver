#!/usr/bin/env python3

"""Compare weighted heuristics for the combined 6x6x6 daisy search."""

# standard libraries
import argparse
import random
import re
import statistics
import subprocess
import time

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube666 import (
    DAISY_PLUS_TABLES_666,
    PHASE5_ILLEGAL_MOVES,
    RubiksCube666,
    moves_666,
    solved_666,
)

BINARY = "./ida_search_666_daisy_centers"
LEGAL_MOVES = tuple(move for move in moves_666 if move not in PHASE5_ILLEGAL_MOVES)
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
SCRAMBLE_LENGTH = 60


def scramble(sample):
    rng = random.Random(f"666-daisy-{sample}")
    cube = RubiksCube666(solved_666, "URFDLB")
    for _ in range(SCRAMBLE_LENGTH):
        cube.rotate(rng.choice(LEGAL_MOVES))
    return cube


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True)]
    for flag, filename in DAISY_PLUS_TABLES_666:
        cmd.extend((flag, filename))
    cmd.extend(("--multiplier", str(multiplier)))
    return cmd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("multipliers", nargs="+", type=float)
    parser.add_argument("--cubes", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    results = {multiplier: [] for multiplier in args.multipliers}
    for sample in range(args.cubes):
        cube = scramble(sample)
        for multiplier in args.multipliers:
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
            print(
                f"DAISY_666 sample={sample:03d} multiplier={multiplier:g} " f"wall={wall:.3f} moves={moves} {status}",
                flush=True,
            )

    for multiplier, measurements in results.items():
        solved = [(wall, moves) for wall, moves in measurements if moves is not None]
        walls = [wall for wall, _ in solved]
        moves = [moves for _, moves in solved]
        print(
            f"DAISY_666_SUMMARY multiplier={multiplier:g} "
            f"solved={len(solved)}/{len(measurements)} "
            f"median_wall={statistics.median(walls) if walls else 0:.3f} "
            f"max_wall={max(walls) if walls else 0:.3f} "
            f"median_moves={statistics.median(moves) if moves else 0} "
            f"max_moves={max(moves) if moves else 0}",
            flush=True,
        )


if __name__ == "__main__":
    main()
