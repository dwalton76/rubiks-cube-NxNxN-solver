#!/usr/bin/env python3
"""Benchmark the experimental combined 4x4x4 phase 3+4 search."""

import argparse
import json
import logging
import statistics
import subprocess
import time
from pathlib import Path

from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "lookup-tables" / "lookup-table-4x4x4-step33-all-edges-paired.cost-only.bin"
CENTER_GRAPH = ROOT / "lookup-tables" / "lookup-table-4x4x4-step31-centers.bin"
BINARY = ROOT / "ida_search_444_phase3_and_4"


def combined_solution(cube, original_state, original_solution, max_threshold):
    cube.state = original_state[:]
    cube.solution = original_solution[:]
    command = [
        str(BINARY),
        "--kociemba",
        cube.get_kociemba_string(True),
        "--edge-pairing-cost",
        str(TABLE),
        "--center-graph",
        str(CENTER_GRAPH),
        "--center-state-index",
        str(cube.lt_phase3_centers.state_index()),
        "--solution-count",
        "1000000",
        "--max-ida-threshold",
        str(max_threshold),
    ]
    started = time.perf_counter()
    with subprocess.Popen(
        command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    ) as process:
        for line in process.stdout:
            if not line.startswith("SOLUTION"):
                continue
            solution = tuple(line.split(":", 1)[1].strip().split())
            cube.state = original_state[:]
            cube.solution = original_solution[:]
            for move in solution:
                cube.rotate(move)
            if not cube.reduced_to_333():
                process.terminate()
                raise RuntimeError(f"combined solution did not reduce the cube: {solution}")
            if not cube.edge_solution_leads_to_pll_parity():
                process.terminate()
                process.wait()
                return solution, time.perf_counter() - started
        returncode = process.wait()
    raise RuntimeError(f"combined search exited {returncode} without a PLL-free solution")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--max-threshold", type=int, default=20)
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)
    logging.disable(logging.INFO)

    states = json.loads((ROOT / "utils" / "10k-444-cubes.json").read_text())["4x4x4"][
        args.start : args.start + args.count
    ]
    combined_lengths = []
    combined_times = []
    portfolio_lengths = []
    portfolio_times = []

    for offset, state in enumerate(states):
        index = args.start + offset
        cube = RubiksCube444(solved_444, "URFDLB")
        cube.load_state(state, "URFDLB")
        cube.lt_init()
        cube.phase1()
        cube.phase2()
        original_state = cube.state[:]
        original_solution = cube.solution[:]

        solution, elapsed = combined_solution(cube, original_state, original_solution, args.max_threshold)
        combined_lengths.append(len(solution))
        combined_times.append(elapsed)

        cube.state = original_state[:]
        cube.solution = original_solution[:]
        started = time.perf_counter()
        cube.phase3_and_4_portfolio(consider_solve_333=False)
        portfolio_times.append(time.perf_counter() - started)
        portfolio_lengths.append(
            len([step for step in cube.solution[len(original_solution) :] if not str(step).startswith("COMMENT")])
        )
        print(
            f"{index}: combined={combined_lengths[-1]} {combined_times[-1]:.2f}s "
            f"portfolio={portfolio_lengths[-1]} {portfolio_times[-1]:.2f}s"
        )

    print(
        f"combined mean={statistics.mean(combined_lengths):.2f} time={statistics.mean(combined_times):.2f}s; "
        f"portfolio mean={statistics.mean(portfolio_lengths):.2f} time={statistics.mean(portfolio_times):.2f}s"
    )


if __name__ == "__main__":
    main()
