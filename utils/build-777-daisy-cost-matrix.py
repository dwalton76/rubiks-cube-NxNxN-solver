#!/usr/bin/env python3
"""
Build the combined heuristic matrix for the 7x7x7 daisy search, which daisies the
UD, LR, and FB centers on all three axes at once.

Each perfect table only knows about one axis and tops out at depth 15, while a
combined daisy is 19 or more moves away, so max(UD, LR, FB) is admissible but can
never guide a search that deep. With a branching factor near 23 the gap is
hopeless, so the samples come from a weighted search instead: --multiplier
inflates the cost to goal, which trades solution length for a search that
finishes in seconds.

Every row of --print-ida-summary gives (UD, LR, FB) -> remaining moves. The matrix
cell is the smallest remaining count seen for that triple, never below
max(UD, LR, FB). A whole cube rotation permutes the three axes without changing the
daisy, so each sample counts for all six orderings of its triple.

Solutions only pass through states where all three axes are scrambled together, so
the cells with one nearly solved axis never get sampled. Falling back to the
admissible max there would leave the search nothing to prune with, so they inherit
the same weighted estimate that produced the samples.

Re-running after dropping a rebuilt matrix into the C file tightens it further,
since the sharper heuristic finds shorter solutions.

This was used to build the daisy_axis_costs_777 matrix in
ida_search_777_daisy_centers.c
"""

from __future__ import annotations

# standard libraries
import argparse
import random
import statistics
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.heuristic_matrix import (
    append_solve_sample,
    fill_cost_matrix,
    format_c_matrix_3d,
    load_done_sample_ids,
    parse_ida_summary_path,
    scramble_cube,
    summarize_jsonl,
    write_c_matrix,
)
from rubikscubennnsolver.RubiksCube777 import (
    DAISY_CENTERS_ILLEGAL_MOVES_777,
    DAISY_PERFECT_TABLES_777,
    RubiksCube777,
    moves_777,
    solved_777,
)

BINARY = "./ida_search_777_daisy_centers"
SOURCE = Path("rubikscubennnsolver/ida_search_777_daisy_centers.c")
MATRIX_DECL = "static const unsigned char daisy_axis_costs_777"
DEFAULT_SAMPLES = Path("utils/777-daisy-samples.jsonl")
LEGAL_MOVES = tuple(move for move in moves_777 if move not in DAISY_CENTERS_ILLEGAL_MOVES_777)
# Every per-axis perfect table tops out at depth 15.
COST_MAX = 15


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True)]
    for flag, filename in DAISY_PERFECT_TABLES_777:
        cmd.extend((flag, filename))
    cmd.append("--print-ida-summary")
    if multiplier:
        cmd.extend(("--multiplier", str(multiplier)))
    return cmd


def parse_path(output):
    return parse_ida_summary_path(output, token_count=8, value_indexes=(0, 1, 2, 4))


def matrix_from_samples(samples, fallback_multiplier):
    size = COST_MAX + 1
    return fill_cost_matrix(
        samples,
        (size, size, size),
        lambda index: max(index),
        permute_coords=True,
        fallback_multiplier=fallback_multiplier,
    )


def format_matrix(matrix):
    opening = f"{MATRIX_DECL}[MATRIX_COST_MAX + 1][MATRIX_COST_MAX + 1][MATRIX_COST_MAX + 1] = {{"
    return format_c_matrix_3d(opening, matrix)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--multiplier", type=float, default=1.8)
    parser.add_argument(
        "--fallback-multiplier",
        type=float,
        default=None,
        help="estimate for unsampled cells, defaults to --multiplier",
    )
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--write", action="store_true", help=f"splice the matrix into {SOURCE}")
    args = parser.parse_args()

    args.samples.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_sample_ids(args.samples)
    if not args.report_only:
        print(
            f"cubes={args.count} multiplier={args.multiplier} timeout={args.timeout:.0f}s already_done={len(done)}",
            flush=True,
        )
        with args.samples.open("a") as out:
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

    solved, timeout, failed, samples, walls, solution_moves = summarize_jsonl(args.samples)
    matrix, counts = matrix_from_samples(samples, args.fallback_multiplier or args.multiplier)
    print(
        f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} "
        f"mean_wall={statistics.mean(walls) if walls else 0:.1f}s "
        f"median_wall={statistics.median(walls) if walls else 0:.1f}s "
        f"max_wall={max(walls) if walls else 0:.1f}s "
        f"median_moves={statistics.median(solution_moves) if solution_moves else 0}",
        flush=True,
    )
    populated = sum(1 for count in counts.values() if count)
    print(f"populated cells {populated} of {(COST_MAX + 1) ** 3}", flush=True)
    print(flush=True)
    text = format_matrix(matrix)
    if args.write:
        write_c_matrix(SOURCE, MATRIX_DECL, text)
        print(f"wrote the matrix to {SOURCE}", flush=True)
    else:
        print(text)


if __name__ == "__main__":
    main()
