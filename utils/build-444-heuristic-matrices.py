#!/usr/bin/env python3
"""Sample 200 random 4x4 reductions and build matrices for both C phases."""

from __future__ import annotations

# standard libraries
import argparse
import json
import random
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.heuristic_matrix import (
    fill_cost_matrix,
    format_c_matrix_2d,
    format_c_matrix_3d,
    parse_ida_summary_path,
    run_timed_solve,
    scramble_cube,
)
from rubikscubennnsolver.RubiksCube444 import (
    ALL_EDGES_PAIRED_TABLE_444,
    PHASE1_ALL_CENTERS_INDEX_444,
    PHASE1_ALL_CENTERS_TABLE_444,
    PHASE1_HIGHLOW_EDGES_TABLE_444,
    PHASE1_HIGHLOW_TARGET_444,
    PHASE1_LR_CENTERS_TABLE_444,
    PHASE2_CENTERS_TABLE_444,
    RubiksCube444,
    highlow_edge_mapping_combinations,
    moves_444,
    solved_444,
)

PHASE1_BINARY = "./ida_search_444_phase1"
PHASE2_BINARY = "./ida_search_444_phase2"
PHASE1_SAMPLES = Path("utils/444-phase1-samples.jsonl")
PHASE2_SAMPLES = Path("utils/444-phase2-samples.jsonl")

# These exceed the completed depths of the component tables. Keeping fixed
# dimensions makes repeated sampling runs produce drop-in-compatible C arrays.
PHASE1_COST_MAX = 12
PHASE2_EDGE_MAX = 12
PHASE2_CENTER_MAX = 9


def highlow_string(cube):
    highlow = ["."] * len(cube.state)
    for (square, _), value in zip(cube.reduce333_orient_edges_tuples, cube.highlow_edges_state(None)):
        highlow[square] = value
    return "".join(highlow[1:])


def cpu_prefix(cores):
    return ["taskset", "--cpu-list", f"0-{cores - 1}"]


def phase1_command(cube, cores):
    cmd = cpu_prefix(cores) + [
        PHASE1_BINARY,
        "--kociemba",
        cube.get_kociemba_string(True),
        "--highlow",
        highlow_string(cube),
        "--all-center-cost",
        PHASE1_ALL_CENTERS_TABLE_444,
        "--all-center-index",
        PHASE1_ALL_CENTERS_INDEX_444,
        "--lr-cost",
        PHASE1_LR_CENTERS_TABLE_444,
        "--wing-cost",
        PHASE1_HIGHLOW_EDGES_TABLE_444,
        "--max-ida-threshold",
        "20",
    ]
    cmd.append("--orbit0-need-odd-w" if 0 in cube.center_solution_leads_to_oll_parity() else "--orbit0-need-even-w")
    return cmd


def phase2_command(cube, cores):
    return cpu_prefix(cores) + [
        PHASE2_BINARY,
        "--kociemba",
        cube.get_kociemba_string(True),
        "--edge-pairing-cost",
        ALL_EDGES_PAIRED_TABLE_444,
        "--center-cost",
        PHASE2_CENTERS_TABLE_444,
        "--max-ida-threshold",
        "20",
        "--avoid-pll",
    ]


def parse_phase1_path(output):
    # INIT CTR LR WING CTG TRU IDX -> (CTR, LR, WING, TRU)
    return parse_ida_summary_path(output, token_count=7, value_indexes=(0, 1, 2, 4))


def parse_phase2_path(output):
    # INIT EDGE CTR CTG TRU IDX -> (EDGE, CTR, TRU)
    return parse_ida_summary_path(output, token_count=6, value_indexes=(0, 1, 3))


def append_record(handle, sample_id, result, path, command, state, solution):
    record = {
        "sample": sample_id,
        "ok": result["ok"],
        "timeout": result["timeout"],
        "wall": result["wall"],
        "moves": result["moves"],
        "nodes": result["nodes"],
        "path": path,
        "solution": solution,
        "command": command,
        "kociemba": state,
    }
    handle.write(json.dumps(record) + "\n")
    handle.flush()
    return record


def load_records(path):
    if not path.exists():
        return {}
    return {record["sample"]: record for record in map(json.loads, path.read_text().splitlines())}


def apply_phase1(cube, solution):
    for step in solution:
        cube.rotate(step)
    mappings = [None]
    for groups in highlow_edge_mapping_combinations.values():
        mappings.extend(groups)
    for mapping in mappings:
        if cube.highlow_edges_state(mapping) == PHASE1_HIGHLOW_TARGET_444:
            cube.edge_mapping = mapping or []
            return
    raise RuntimeError("phase 1 did not produce a high/low mapping")


def solution_from_output(output):
    for line in output.splitlines():
        if line.startswith("SOLUTION"):
            return line.split(":", 1)[1].split()
    return []


def matrix_reports(records12, records34):
    samples12 = [tuple(row) for record in records12.values() if record["ok"] for row in record["path"]]
    matrix12, counts12 = fill_cost_matrix(
        samples12,
        (PHASE1_COST_MAX + 1,) * 3,
        lambda index: max(index),
    )
    print("\nphase 1 sample counts by populated cell:")
    print(f"  observations={len(samples12)} populated={sum(bool(value) for value in counts12.values())}")
    print(
        format_c_matrix_3d(
            "static const unsigned char phase1_cost_matrix_444"
            "[PHASE1_COST_MAX + 1][PHASE1_COST_MAX + 1][PHASE1_COST_MAX + 1] = {",
            matrix12,
            "CTR",
            "LR",
        )
    )

    samples34 = [tuple(row) for record in records34.values() if record["ok"] for row in record["path"]]
    matrix34, counts34 = fill_cost_matrix(
        samples34,
        (PHASE2_EDGE_MAX + 1, PHASE2_CENTER_MAX + 1),
        lambda index: max(index),
    )
    print("phase 2 sample counts by populated cell:")
    print(f"  observations={len(samples34)} populated={sum(bool(value) for value in counts34.values())}")
    print(
        format_c_matrix_2d(
            "static const unsigned char phase2_cost_matrix_444" "[PHASE2_EDGE_MAX + 1][PHASE2_CENTER_MAX + 1] = {",
            matrix34,
            lambda edge: f"edge cost {edge}",
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--cores", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.cores <= 10:
        parser.error("--cores must be between 1 and 10")

    records12 = load_records(PHASE1_SAMPLES)
    records34 = load_records(PHASE2_SAMPLES)
    if not args.report_only:
        print(
            f"cubes={args.count} timeout={args.timeout:.0f}s cores={args.cores} "
            f"phase1_done={len(records12)} phase2_done={len(records34)}",
            flush=True,
        )
        with PHASE1_SAMPLES.open("a") as out12, PHASE2_SAMPLES.open("a") as out34:
            for index in range(args.count):
                sample_id = args.offset + index
                cube = scramble_cube(
                    random.Random(f"{args.seed}-{sample_id}"),
                    RubiksCube444,
                    solved_444,
                    moves_444,
                )
                initial_state = cube.get_kociemba_string(True)

                if sample_id not in records12 or records12[sample_id]["timeout"]:
                    command12 = phase1_command(cube, args.cores)
                    result12 = run_timed_solve(command12, args.timeout)
                    output12 = result12.pop("output")
                    path12 = parse_phase1_path(output12) if result12["ok"] else []
                    solution12 = solution_from_output(output12)
                    records12[sample_id] = append_record(
                        out12, sample_id, result12, path12, command12, initial_state, solution12
                    )
                else:
                    result12 = records12[sample_id]
                    solution12 = result12.get("solution", [])

                if not result12["ok"] or not solution12:
                    print(
                        f"sample={sample_id:04d} phase1 " f"{'TIMEOUT' if result12['timeout'] else 'FAIL'}",
                        flush=True,
                    )
                    continue

                apply_phase1(cube, solution12)
                if sample_id not in records34:
                    command34 = phase2_command(cube, args.cores)
                    result34 = run_timed_solve(command34, args.timeout)
                    output34 = result34.pop("output")
                    path34 = parse_phase2_path(output34) if result34["ok"] else []
                    solution34 = solution_from_output(output34)
                    records34[sample_id] = append_record(
                        out34,
                        sample_id,
                        result34,
                        path34,
                        command34,
                        cube.get_kociemba_string(True),
                        solution34,
                    )
                else:
                    result34 = records34[sample_id]

                print(
                    f"sample={sample_id:04d} "
                    f"p12={records12[sample_id]['wall']}s/{records12[sample_id]['moves']} "
                    f"p34={result34['wall']}s/{result34['moves']} "
                    f"{'TIMEOUT' if result34['timeout'] else ('ok' if result34['ok'] else 'FAIL')}",
                    flush=True,
                )

    matrix_reports(records12, records34)


if __name__ == "__main__":
    main()
