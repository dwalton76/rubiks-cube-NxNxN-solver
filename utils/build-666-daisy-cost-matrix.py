#!/usr/bin/env python3

"""Sample a 6x6 daisy cost matrix from the three inner-x-spine tables.

Solve random cubes with ``ida_search_666_daisy_centers`` and no multiplier so
the search uses the admissible max of the three tables. Every
``--print-ida-summary`` row gives (UD, LR, FB) -> remaining moves. Those
samples fill ``daisy_spine_costs_666`` in ``ida_search_666_daisy_centers.c``.
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
    format_c_matrix_3d,
    load_done_sample_ids,
    parse_ida_summary_path,
    scramble_cube,
    summarize_jsonl,
    write_c_matrix,
)
from rubikscubennnsolver.RubiksCube666 import DAISY_INNER_X_SPINE_TABLES_666, RubiksCube666, moves_666, solved_666

BINARY = "./ida_search_666_daisy_centers"
SOURCE = Path("rubikscubennnsolver/ida_search_666_daisy_centers.c")
MATRIX_DECL = "static const unsigned char daisy_spine_costs_666"
DEFAULT_SAMPLES = Path("utils/666-daisy-spine-samples.jsonl")
DAISY_CENTERS_ILLEGAL_MOVES_666 = {
    "Uw",
    "Uw'",
    "3Uw",
    "3Uw'",
    "Lw",
    "Lw'",
    "3Lw",
    "3Lw'",
    "Fw",
    "Fw'",
    "3Fw",
    "3Fw'",
    "Rw",
    "Rw'",
    "3Rw",
    "3Rw'",
    "Bw",
    "Bw'",
    "3Bw",
    "3Bw'",
    "Dw",
    "Dw'",
    "3Dw",
    "3Dw'",
}
LEGAL_MOVES = tuple(move for move in moves_666 if move not in DAISY_CENTERS_ILLEGAL_MOVES_666)
# The three 70^5 spine tables reach depth 16.
COST_MAX = 16


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True)]
    for flag, filename in DAISY_INNER_X_SPINE_TABLES_666:
        cmd.extend((flag, filename))
    cmd.append("--print-ida-summary")
    if multiplier is not None:
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument(
        "--multiplier",
        type=float,
        default=None,
        help="optional IDA multiplier; omit to search with the admissible max",
    )
    parser.add_argument("--fallback-multiplier", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=120.0)
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
                cube = scramble_cube(random.Random(f"{args.seed}-{sample_id}"), RubiksCube666, solved_666, LEGAL_MOVES)
                append_solve_sample(
                    out,
                    sample_id,
                    solve_command(cube, args.multiplier),
                    args.timeout,
                    parse_path,
                    extra={"multiplier": args.multiplier},
                )

    solved, timeout, failed, samples, walls, solution_moves = summarize_jsonl(args.samples)
    matrix, counts = matrix_from_samples(samples, args.fallback_multiplier)
    filled = sum(1 for count in counts.values() if count)
    total = (COST_MAX + 1) ** 3
    print(f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} " f"cells={filled}/{total}")
    if walls:
        print(
            f"median_wall={sorted(walls)[len(walls) // 2]:.3f} "
            f"median_moves={sorted(solution_moves)[len(solution_moves) // 2]}"
        )
    print(format_matrix(matrix), end="")
    if args.write:
        write_c_matrix(SOURCE, MATRIX_DECL, format_matrix(matrix))
        print(f"wrote {SOURCE}")


if __name__ == "__main__":
    main()
