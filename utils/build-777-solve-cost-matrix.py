#!/usr/bin/env python3
"""
Build the combined heuristic matrix for native-orientation 7x7x7 center solves.

This is the daisy sampler with three changes: it loads the perfect tables built to
the native goal, it passes --native-only so a swapped daisy is not treated as
solved, and it splices solve_axis_costs_777 instead of daisy_axis_costs_777.

Use the same first-pass settings as the daisy matrix: --multiplier 1.8 on 100
scrambles. Re-running after --write, without a multiplier, tightens the matrix
against the matrix itself.
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
    NATIVE_SOLVE_PERFECT_TABLES_777,
    RubiksCube777,
    moves_777,
    solved_777,
)

BINARY = "./ida_search_777_daisy_centers"
SOURCE = Path("rubikscubennnsolver/ida_search_777_daisy_centers.c")
MATRIX_DECL = "static const unsigned char solve_axis_costs_777"
DEFAULT_SAMPLES = Path("utils/777-solve-samples.jsonl")
LEGAL_MOVES = tuple(move for move in moves_777 if move not in DAISY_CENTERS_ILLEGAL_MOVES_777)
COST_MAX = 15


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True), "--native-only"]
    for flag, filename in NATIVE_SOLVE_PERFECT_TABLES_777:
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
