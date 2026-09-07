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

Every row of --print-ida-summary gives
(unpaired, table cost, orbit-1 cost) -> remaining moves. The matrix cell is
the smallest remaining count seen for that tuple, never below the existing
two-coordinate matrix or the orbit-1 cost.

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
    format_c_matrix_3d,
    load_done_sample_ids,
    parse_ida_summary_path,
    scramble_cube,
    summarize_jsonl,
    write_c_matrix,
)
from rubikscubennnsolver.RubiksCube777 import LR_OBLIQUE_PAIRING_ILLEGAL_MOVES, RubiksCube777, moves_777, solved_777

TABLE = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage.cost-only.bin"
ORBIT1_EVEN_TABLE = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage-orbit1-even.cost-only.bin"
ORBIT1_ODD_TABLE = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage-orbit1-odd.cost-only.bin"
BINARY = "./ida_search_777_centers_stage"
SAMPLES = Path("utils/777-phase2-orbit1-samples.jsonl")
LEGAL_MOVES = tuple(move for move in moves_777 if move not in LR_OBLIQUE_PAIRING_ILLEGAL_MOVES)
UNPAIRED_MAX = 16
COST_MAX = 12
ORBIT1_COST_MAX = 13
SOURCE = Path("rubikscubennnsolver/ida_search_777_centers_stage.c")
DECL = "static const unsigned char unpaired_count_UD_inner_centers_777"

# unpaired-count costs the old oblique-only phase 2 used, indexed by unpaired count
LR_OBLIQUE_ONLY_COST = (0, 1, 1, 4, 5, 6, 7, 8, 9, 9, 10, 11, 11, 12, 12, 12, 12)

# Current production matrix. It is the floor for every orbit-1 plane, so an
# empty sampled cell cannot weaken the existing heuristic.
CURRENT_MATRIX = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
    (1, 1, 2, 3, 6, 7, 7, 7, 8, 9, 10, 11, 12),
    (1, 1, 2, 3, 6, 7, 8, 9, 9, 9, 10, 11, 12),
    (6, 6, 6, 6, 6, 7, 8, 9, 11, 13, 13, 13, 13),
    (6, 6, 6, 7, 7, 7, 8, 9, 11, 13, 14, 15, 15),
    (8, 8, 8, 8, 8, 8, 8, 9, 11, 13, 15, 15, 15),
    (8, 10, 10, 11, 11, 11, 11, 11, 11, 13, 15, 15, 15),
    (8, 10, 10, 12, 12, 12, 12, 12, 12, 13, 15, 16, 16),
    (9, 10, 11, 12, 12, 12, 12, 12, 12, 13, 15, 16, 16),
    (9, 11, 12, 14, 14, 14, 14, 14, 14, 14, 15, 16, 16),
    (10, 11, 12, 14, 14, 14, 14, 14, 14, 14, 15, 18, 18),
    (11, 11, 12, 14, 14, 14, 14, 17, 17, 17, 17, 18, 18),
    (11, 11, 12, 14, 14, 14, 15, 17, 17, 17, 17, 18, 18),
    (12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 18, 18, 18),
    (12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 19, 19, 19),
    (12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 19, 19, 19),
    (12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 19, 19, 19),
)


def solve_command(cube, multiplier):
    orbit1_odd = 1 in cube.center_solution_leads_to_oll_parity()
    cmd = [
        BINARY,
        "--kociemba",
        cube.get_kociemba_string(True),
        "--ranked-UD-inner-centers-cost",
        TABLE,
        "--ud-inner-even-cost",
        ORBIT1_EVEN_TABLE,
        "--ud-inner-odd-cost",
        ORBIT1_ODD_TABLE,
        "--orbit1-need-odd-w" if orbit1_odd else "--orbit1-need-even-w",
        "--print-ida-summary",
    ]
    if multiplier:
        cmd.extend(["--multiplier", str(multiplier)])
    return cmd


def parse_path(output):
    return parse_ida_summary_path(output, token_count=7, value_indexes=(0, 1, 2, 4))


def matrix_from_samples(samples):
    dims = (UNPAIRED_MAX + 1, COST_MAX + 1, ORBIT1_COST_MAX + 1)

    def admissible(index):
        unpaired, table_cost, orbit1_cost = index
        return max(CURRENT_MATRIX[unpaired][table_cost], orbit1_cost)

    # Samples are (table, orbit1, unpaired, remaining); matrix order is
    # [unpaired][table][orbit1].
    remapped = tuple(
        (unpaired, table_cost, orbit1_cost, remaining) for table_cost, orbit1_cost, unpaired, remaining in samples
    )
    matrix, counts = fill_cost_matrix(remapped, dims, admissible)

    # The third dimension is much more sparsely sampled than the old matrix.
    # Require repeated evidence and limit one refresh to a two-move increase.
    # This avoids spreading a single high weighted-search path into untouched
    # cells through monotonic propagation.
    for unpaired in range(UNPAIRED_MAX + 1):
        for table_cost in range(COST_MAX + 1):
            for orbit1_cost in range(ORBIT1_COST_MAX + 1):
                index = (unpaired, table_cost, orbit1_cost)
                floor = admissible(index)
                if counts[index] < 3:
                    matrix[unpaired][table_cost][orbit1_cost] = floor
                else:
                    matrix[unpaired][table_cost][orbit1_cost] = min(
                        matrix[unpaired][table_cost][orbit1_cost],
                        floor + 2,
                    )
    return matrix, counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--multiplier", type=float, default=1.4)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--write-source", action="store_true")
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
    print("sample counts by unpaired count:", flush=True)
    for unpaired in range(UNPAIRED_MAX + 1):
        count = sum(
            counts[(unpaired, table_cost, orbit1_cost)]
            for table_cost in range(COST_MAX + 1)
            for orbit1_cost in range(ORBIT1_COST_MAX + 1)
        )
        print(f"  u={unpaired:2d} {count}", flush=True)
    print(flush=True)
    opening = DECL + ("[MATRIX_UNPAIRED_MAX + 1][MATRIX_COST_MAX + 1][MATRIX_ORBIT1_COST_MAX + 1] = {")
    text = format_c_matrix_3d(opening, rows, axis0="unpaired", axis1="centers")
    print(text, end="")
    if args.write_source:
        write_c_matrix(SOURCE, DECL, text)
        print(f"wrote {SOURCE}", flush=True)


if __name__ == "__main__":
    main()
