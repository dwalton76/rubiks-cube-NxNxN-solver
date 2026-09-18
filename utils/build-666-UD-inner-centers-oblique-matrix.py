#!/usr/bin/env python3
"""
Build the combined heuristic matrix for 6x6x6 phase 2, which stages the UD
inner x-centers while pairing the LR obliques.

The ranked table only knows about the UD inner x-centers and one move pairs at
most four of the eight LR oblique pairs, so max(table, ceil(unpaired/4)) is
admissible but weak. Samples come from --unpaired-multiplier 0.25, which is
that same admissible pairing bound with a working ceiling.

Every row of the IDA summary gives (unpaired, table cost) -> remaining
moves. The matrix cell is the smallest remaining count seen for that pair,
never below max(ceil(unpaired/4), the table cost).

This builds unpaired_count_UD_inner_centers_666 for ida_search_666_centers_stage.c.
"""

from __future__ import annotations

# standard libraries
import argparse
import math
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
from rubikscubennnsolver.RubiksCube666 import UD_INNER_X_STAGE_TABLE_666, RubiksCube666, moves_666, solved_666

BINARY = "./ida_search_666_centers_stage"
SAMPLES = Path("utils/666-phase2-samples.jsonl")
PHASE2_ILLEGAL_MOVES = {
    "3Uw",
    "3Uw'",
    "3Dw",
    "3Dw'",
    "3Fw",
    "3Fw'",
    "3Bw",
    "3Bw'",
}
LEGAL_MOVES = tuple(move for move in moves_666 if move not in PHASE2_ILLEGAL_MOVES)
UNPAIRED_MAX = 8
# C(24,8) inner-x staging tops out at depth 8 on this move set.
COST_MAX = 8


def solve_command(cube, unpaired_multiplier, threads):
    return [
        BINARY,
        "--kociemba",
        cube.get_kociemba_string(True),
        "--stage-ud-inner-x-pair-lr-obliques",
        "--ud-inner-x-cost",
        UD_INNER_X_STAGE_TABLE_666,
        "--unpaired-multiplier",
        str(unpaired_multiplier),
        "--threads",
        str(threads),
    ]


def parse_path(output):
    # INIT UDIX UNPR CTG TRU IDX -> (UDIX, UNPR, TRU)
    return parse_ida_summary_path(output, token_count=6, value_indexes=(0, 1, 3))


def matrix_from_samples(samples):
    dims = (UNPAIRED_MAX + 1, COST_MAX + 1)

    def admissible(index):
        unpaired, table_cost = index
        return max(table_cost, math.ceil(unpaired / 4) if unpaired else 0)

    remapped = ((unpaired, table_cost, remaining) for table_cost, unpaired, remaining in samples)
    return fill_cost_matrix(remapped, dims, admissible)


def format_matrix(matrix):
    opening = (
        "static const unsigned char unpaired_count_UD_inner_centers_666"
        "[MATRIX_UNPAIRED_MAX + 1][MATRIX_COST_MAX + 1] = {"
    )
    return format_c_matrix_2d(opening, matrix, lambda unpaired: f"unpaired {unpaired}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--unpaired-multiplier", type=float, default=0.25)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--threads", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--samples", type=Path, default=SAMPLES)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    args.samples.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_sample_ids(args.samples)
    if not args.report_only:
        print(
            f"cubes={args.count} unpaired_multiplier={args.unpaired_multiplier} "
            f"threads={args.threads} timeout={args.timeout:.0f}s already_done={len(done)}",
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
                    solve_command(cube, args.unpaired_multiplier, args.threads),
                    args.timeout,
                    parse_path,
                    extra={"unpaired_multiplier": args.unpaired_multiplier, "threads": args.threads},
                )

    solved, timeout, failed, samples, walls, solution_moves = summarize_jsonl(args.samples)
    rows, counts = matrix_from_samples(samples)
    print(
        f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} "
        f"mean_wall={sum(walls) / len(walls) if walls else 0:.1f}s",
        flush=True,
    )
    if solution_moves:
        ordered = sorted(solution_moves)
        print(
            f"median_moves={ordered[len(ordered) // 2]} min_moves={ordered[0]} max_moves={ordered[-1]}",
            flush=True,
        )
    print("sample counts (rows=unpaired 0..8, cols=UD inner-x cost 0..8):", flush=True)
    for unpaired in range(UNPAIRED_MAX + 1):
        print(f"  u={unpaired:2d} {[counts[(unpaired, table_cost)] for table_cost in range(COST_MAX + 1)]}", flush=True)
    print(flush=True)
    print(format_matrix(rows), end="")


if __name__ == "__main__":
    main()
