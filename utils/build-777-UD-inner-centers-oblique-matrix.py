#!/usr/bin/env python3
"""
Build the combined heuristic matrix for 7x7x7 phase 2, which stages the UD
inner t/x centers while pairing the LR obliques.

The ranked table only knows about the UD inner centers and one move pairs at
most four obliques, so max(table, ceil(unpaired/4)) is admissible but tops out
near 12 while real phase-2 solutions run 15 to 17 moves. With a branching
factor near 40 that gap is hopeless to search, so the samples come from a
weighted search instead: --multiplier inflates the cost to goal, which trades
a move or two of solution length for a search that finishes in seconds.

Every row of --print-ida-summary gives (unpaired, table cost) -> remaining
moves. The matrix cell is the smallest remaining count seen for that pair,
never below max(the empirical oblique-only cost, the table cost).

Re-running after dropping a rebuilt matrix into the C file tightens it
further, since the sharper heuristic finds shorter solutions.

This was used to build the unpaired_count_UD_inner_centers_777 matrix in
ida_search_777_centers_stage.c
"""

from __future__ import annotations

# standard libraries
import argparse
import random
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.heuristic_matrix import (
    append_solve_sample,
    fill_cost_matrix,
    format_c_matrix_2d,
    load_done_sample_ids,
    parse_ida_summary_path,
    scramble_cube,
    summarize_jsonl,
)
from rubikscubennnsolver.RubiksCube777 import LR_OBLIQUE_PAIRING_ILLEGAL_MOVES, RubiksCube777, moves_777, solved_777

TABLE = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage.cost-only.bin"
BINARY = "./ida_search_777_centers_stage"
SAMPLES = Path("utils/777-phase2-samples.jsonl")
LEGAL_MOVES = tuple(move for move in moves_777 if move not in LR_OBLIQUE_PAIRING_ILLEGAL_MOVES)
UNPAIRED_MAX = 16
COST_MAX = 12

# unpaired-count costs the old oblique-only phase 2 used, indexed by unpaired count
LR_OBLIQUE_ONLY_COST = (0, 1, 1, 4, 5, 6, 7, 8, 9, 9, 10, 11, 11, 12, 12, 12, 12)


def solve_command(cube, multiplier):
    cmd = [
        BINARY,
        "--kociemba",
        cube.get_kociemba_string(True),
        "--ranked-UD-inner-centers-cost",
        TABLE,
        "--print-ida-summary",
    ]
    if multiplier:
        cmd.extend(["--multiplier", str(multiplier)])
    return cmd


def parse_path(output):
    return parse_ida_summary_path(output, token_count=6, value_indexes=(0, 1, 3))


def matrix_from_samples(samples):
    dims = (UNPAIRED_MAX + 1, COST_MAX + 1)

    def admissible(index):
        unpaired, table_cost = index
        return max(table_cost, LR_OBLIQUE_ONLY_COST[unpaired])

    # Samples are (table_cost, unpaired, remaining); the matrix is [unpaired][table_cost].
    remapped = ((unpaired, table_cost, remaining) for table_cost, unpaired, remaining in samples)
    return fill_cost_matrix(remapped, dims, admissible)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--multiplier", type=float, default=1.4)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    SAMPLES.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_sample_ids(SAMPLES)
    if not args.report_only:
        print(
            f"cubes={args.count} multiplier={args.multiplier} timeout={args.timeout:.0f}s " f"already_done={len(done)}",
            flush=True,
        )
        with SAMPLES.open("a") as out:
            for index in range(args.count):
                sample_id = args.offset + index
                if sample_id in done:
                    print(f"sample={sample_id:04d} skip", flush=True)
                    continue
                cube = scramble_cube(random.Random(f"{args.seed}-{sample_id}"), RubiksCube777, solved_777, LEGAL_MOVES)
                append_solve_sample(
                    out,
                    sample_id,
                    solve_command(cube, args.multiplier),
                    args.timeout,
                    parse_path,
                    extra={"multiplier": args.multiplier},
                )

    solved, timeout, failed, samples, walls, _solution_moves = summarize_jsonl(SAMPLES)
    rows, counts = matrix_from_samples(samples)
    print(
        f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} "
        f"mean_wall={sum(walls) / len(walls) if walls else 0:.1f}s",
        flush=True,
    )
    print("sample counts (rows=unpaired 0..16, cols=table cost 0..12):", flush=True)
    for unpaired in range(UNPAIRED_MAX + 1):
        print(f"  u={unpaired:2d} {[counts[(unpaired, table_cost)] for table_cost in range(COST_MAX + 1)]}", flush=True)
    print(flush=True)
    opening = (
        "static const unsigned char unpaired_count_UD_inner_centers_777"
        "[MATRIX_UNPAIRED_MAX + 1][MATRIX_COST_MAX + 1] = {"
    )
    print(format_c_matrix_2d(opening, rows, lambda unpaired: f"unpaired {unpaired}"), end="")


if __name__ == "__main__":
    main()
