#!/usr/bin/env python3
"""Sample the 6x6 phase-1 heuristic matrix used by ida_search_666_centers_stage.

Start from the admissible floor max(inner-x, ceil(unpaired/4)), find the
lowest IDA --multiplier that still finishes, then solve cubes from
utils/10k-666-cubes.json. Remaining counts along those solutions fill
unpaired_count_all_inner_x_centers_666; each cell uses the smallest remaining
that appears in more than 5% of that cell (override with --min-fraction). Orbit1 OLL is
left off so TRU is staging/pairing work; the C parity floor still covers OLL
at search time.
"""

from __future__ import annotations

# standard libraries
import argparse
import json
import math
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.heuristic_matrix import (
    append_solve_sample,
    fill_cost_matrix,
    format_c_matrix_2d,
    load_done_sample_ids,
    parse_ida_summary_path,
    run_timed_solve,
    summarize_jsonl,
    write_c_matrix,
)
from rubikscubennnsolver.RubiksCube666 import RubiksCube666

TABLE = "lookup-tables/lookup-table-6x6x6-step05-inner-x-centers-stage-one-phase.cost-only.bin"
BINARY = "./ida_search_666_centers_stage"
SOURCE = Path("rubikscubennnsolver/ida_search_666_centers_stage.c")
MATRIX_DECL = "static const unsigned char unpaired_count_all_inner_x_centers_666"
DEFAULT_SAMPLES = Path("utils/666-centers-stage-orbit1-samples.jsonl")
CUBES = Path("utils/10k-666-cubes.json")
SLOW_KOCIEMBA = "LUUUBUFFDBBUDDUDFBRDRBLULFBUURRFLBRLUDBLFRDULBLFLDBRULLBBUFDRRRLRLLDUDLBDRFRDFDRRBDFDLLFLURULFFFBBLRDUUUDUFBRLBRRDBLDUUBLDFDFLRDBLFRDFRBFBFRRDDRBDRBFFRLBUDLFRDRRLUURUUUBBDFBLLBFDRFBUFFLUURBFUUBLFLFDFRDURBFDULLUDLBFBD"
# The one-phase inner-x table is populated through depth 11.
COST_MAX = 11
UNPAIRED_MAX = 8
CALIBRATE_MULTIPLIERS = (1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0)


def solve_command(cube, unpaired_multiplier, multiplier, orbit1):
    cmd = [
        BINARY,
        "--kociemba",
        cube.get_kociemba_string(True),
        "--all-inner-x-cost",
        TABLE,
        "--all-inner-x-index",
        f"{TABLE}.symmetry-index.bin",
        "--max-ida-threshold",
        "30",
    ]
    if unpaired_multiplier is not None:
        cmd.extend(("--unpaired-multiplier", str(unpaired_multiplier)))
    if multiplier is not None:
        cmd.extend(("--multiplier", str(multiplier)))
    if orbit1:
        if 1 in cube.center_solution_leads_to_oll_parity():
            cmd.append("--orbit1-need-odd-w")
        else:
            cmd.append("--orbit1-need-even-w")
    return cmd


def parse_path(output):
    return parse_ida_summary_path(output, token_count=6, value_indexes=(0, 1, 3))


def matrix_from_samples(samples, fallback_multiplier, min_fraction=0.05):
    dims = (UNPAIRED_MAX + 1, COST_MAX + 1)

    def admissible(index):
        unpaired, ix_cost = index
        floor = math.ceil(unpaired / 4) if unpaired else 0
        return max(ix_cost, floor)

    # Samples are (ix_cost, unpaired, remaining); the matrix is [unpaired][ix_cost].
    remapped = ((unpaired, ix_cost, remaining) for ix_cost, unpaired, remaining in samples)
    return fill_cost_matrix(
        remapped,
        dims,
        admissible,
        fallback_multiplier=fallback_multiplier,
        min_fraction=min_fraction,
    )


def format_matrix(matrix):
    opening = f"{MATRIX_DECL}[9][ALL_INNER_X_MATRIX_COST_MAX + 1] = {{"
    return format_c_matrix_2d(opening, matrix, str)


def lowest_multiplier(cubes, unpaired_multiplier, timeout, orbit1):
    """Return the smallest IDA multiplier that solves every probe cube in time."""
    for multiplier in CALIBRATE_MULTIPLIERS:
        ida_multiplier = None if multiplier == 1.0 else multiplier
        print(f"calibrate multiplier={multiplier} timeout={timeout:.0f}s", flush=True)
        all_ok = True
        for index, cube in enumerate(cubes):
            result = run_timed_solve(
                solve_command(cube, unpaired_multiplier, ida_multiplier, orbit1),
                timeout,
            )
            status = "ok" if result["ok"] else "TIMEOUT"
            print(f"  probe={index} moves={result['moves']} wall={result['wall']} {status}", flush=True)
            if not result["ok"]:
                all_ok = False
                break
        if all_ok:
            return ida_multiplier, multiplier
    raise SystemExit(f"no multiplier in {CALIBRATE_MULTIPLIERS} solved the probe cubes within {timeout:.0f}s")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument(
        "--unpaired-multiplier",
        type=float,
        default=None,
        help="optional unpaired formula; omit to search with the current matrix",
    )
    parser.add_argument(
        "--multiplier",
        type=float,
        default=None,
        help="IDA cost multiplier; omit to search with heuristic 1.0",
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="find the lowest --multiplier that solves --calibrate-count cubes before sampling",
    )
    parser.add_argument("--calibrate-count", type=int, default=4)
    parser.add_argument("--calibrate-timeout", type=float, default=30.0)
    parser.add_argument(
        "--orbit1",
        action="store_true",
        help="set --orbit1-need-odd/even-w from OLL parity (production phase-1 flags)",
    )
    parser.add_argument("--fallback-multiplier", type=float, default=1.0)
    parser.add_argument(
        "--min-fraction",
        type=float,
        default=0.05,
        help="ignore a cell's minimum remaining while it is this fraction or less of the cell",
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--write", action="store_true", help=f"splice the matrix into {SOURCE}")
    args = parser.parse_args()

    all_states = json.loads(CUBES.read_text())["6x6x6"]
    if args.calibrate and not args.report_only:
        probes = [RubiksCube666(state, "URFDLB") for state in all_states[: args.calibrate_count]]
        if args.orbit1:
            probes.append(RubiksCube666(SLOW_KOCIEMBA, "URFDLB"))
        chosen, displayed = lowest_multiplier(probes, args.unpaired_multiplier, args.calibrate_timeout, args.orbit1)
        args.multiplier = chosen
        print(f"using multiplier={displayed}", flush=True)

    states = all_states[args.offset : args.offset + args.count]
    args.samples.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_sample_ids(args.samples, ok_only=True)
    if not args.report_only:
        print(
            f"cubes={len(states)} unpaired_multiplier={args.unpaired_multiplier} "
            f"multiplier={args.multiplier} orbit1={args.orbit1} timeout={args.timeout:.0f}s "
            f"already_done={len(done)}",
            flush=True,
        )
        with args.samples.open("a") as out:
            for index, state in enumerate(states):
                sample_id = args.offset + index
                if sample_id in done:
                    print(f"sample={sample_id:04d} skip", flush=True)
                    continue
                cube = RubiksCube666(state, "URFDLB")
                append_solve_sample(
                    out,
                    sample_id,
                    solve_command(cube, args.unpaired_multiplier, args.multiplier, args.orbit1),
                    args.timeout,
                    parse_path,
                    extra={
                        "unpaired_multiplier": args.unpaired_multiplier,
                        "multiplier": args.multiplier,
                        "orbit1": args.orbit1,
                    },
                )

    solved, timeout, failed, samples, walls, solution_moves = summarize_jsonl(args.samples)
    matrix, counts = matrix_from_samples(samples, args.fallback_multiplier, args.min_fraction)
    filled = sum(1 for count in counts.values() if count)
    total = (UNPAIRED_MAX + 1) * (COST_MAX + 1)
    print(f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} " f"cells={filled}/{total}")
    if walls:
        print(
            f"median_wall={sorted(walls)[len(walls) // 2]:.3f} "
            f"median_moves={sorted(solution_moves)[len(solution_moves) // 2]}"
        )
    print("sample counts (rows=unpaired 0..8, cols=inner-x cost):", flush=True)
    for unpaired in range(UNPAIRED_MAX + 1):
        print(f"  u={unpaired} {[counts[(unpaired, ix)] for ix in range(COST_MAX + 1)]}", flush=True)
    print(format_matrix(matrix), end="")
    if args.write:
        write_c_matrix(SOURCE, MATRIX_DECL, format_matrix(matrix))
        print(f"wrote {SOURCE}")


if __name__ == "__main__":
    main()
