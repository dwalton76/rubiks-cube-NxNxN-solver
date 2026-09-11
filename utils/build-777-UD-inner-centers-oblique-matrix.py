#!/usr/bin/env python3
"""
Build the combined heuristic matrix for 7x7x7 phase 2, which stages the U/D
inner t/x centers while pairing the L/R obliques.

The ranked table only knows about the U/D inner centers and one move pairs at
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

# standard libraries
import argparse
import json
import random
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import LR_OBLIQUE_PAIRING_ILLEGAL_MOVES, RubiksCube777, moves_777, solved_777

TABLE = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage.cost-only.bin"
BINARY = "./ida_search_777_centers_stage"
SAMPLES = Path("utils/777-phase2-samples.jsonl")
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
LEGAL_MOVES = tuple(move for move in moves_777 if move not in LR_OBLIQUE_PAIRING_ILLEGAL_MOVES)
SCRAMBLE_LENGTH = 60
UNPAIRED_MAX = 16
COST_MAX = 12

# ida_heuristic_LR_oblique_edges_stage_777, indexed by unpaired count
LR_OBLIQUE_ONLY_COST = (0, 1, 1, 4, 5, 6, 7, 8, 9, 9, 10, 11, 11, 12, 12, 12, 12)


def scramble(rng):
    cube = RubiksCube777(solved_777, "URFDLB")
    for _ in range(SCRAMBLE_LENGTH):
        cube.rotate(rng.choice(LEGAL_MOVES))
    return cube


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
    """Pull (table cost, unpaired, remaining) from the --print-ida-summary rows."""
    rows = []
    started = False
    for line in output.splitlines():
        tokens = line.split()
        if not started:
            started = tokens[:1] == ["INIT"]
            if not started:
                continue
        if len(tokens) != 6:
            continue
        try:
            table_cost, unpaired, _ctg, remaining, _index = (int(value) for value in tokens[1:])
        except ValueError:
            continue
        rows.append((table_cost, unpaired, remaining))
    return rows


def floor_cost(unpaired, table_cost):
    return max(table_cost, LR_OBLIQUE_ONLY_COST[unpaired])


def matrix_from_samples(samples):
    """
    Cells hold the smallest remaining count seen for that pair. Sampling is
    sparse in the corners, so values also propagate down and to the right:
    neither adding an unpaired oblique nor a more scrambled set of inner
    centers can bring the goal closer, which fills the gaps and keeps the
    matrix monotonic.
    """
    buckets = defaultdict(list)
    for table_cost, unpaired, remaining in samples:
        if 0 <= unpaired <= UNPAIRED_MAX and 0 <= table_cost <= COST_MAX:
            buckets[(unpaired, table_cost)].append(remaining)

    rows = []
    counts = []
    for unpaired in range(UNPAIRED_MAX + 1):
        row = []
        count_row = []
        for table_cost in range(COST_MAX + 1):
            values = buckets.get((unpaired, table_cost), [])
            count_row.append(len(values))
            estimate = min(values) if values else 0
            estimate = max(estimate, floor_cost(unpaired, table_cost))
            if table_cost:
                estimate = max(estimate, row[table_cost - 1])
            if unpaired:
                estimate = max(estimate, rows[unpaired - 1][table_cost])
            row.append(estimate)
        rows.append(row)
        counts.append(count_row)
    return rows, counts


def print_c_matrix(rows):
    print(
        "static const unsigned char unpaired_count_UD_inner_centers_777"
        "[MATRIX_UNPAIRED_MAX + 1][MATRIX_COST_MAX + 1] = {"
    )
    for unpaired, values in enumerate(rows):
        joined = ", ".join(f"{value:2d}" for value in values)
        print(f"    {{{joined}}},  // unpaired {unpaired}")
    print("};")


def load_done(path):
    done = set()
    if not path.exists():
        return done
    with path.open() as fh:
        for line in fh:
            done.add(json.loads(line)["sample"])
    return done


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
    done = load_done(SAMPLES)
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

                cube = scramble(random.Random(f"{args.seed}-{sample_id}"))
                record = {
                    "sample": sample_id,
                    "multiplier": args.multiplier,
                    "ok": False,
                    "timeout": False,
                    "wall": None,
                    "moves": None,
                    "path": [],
                }

                started = time.perf_counter()
                try:
                    proc = subprocess.run(
                        solve_command(cube, args.multiplier),
                        capture_output=True,
                        text=True,
                        timeout=args.timeout,
                    )
                    record["wall"] = round(time.perf_counter() - started, 3)
                    output = proc.stdout + proc.stderr
                    match = SOLUTION_RE.search(output)
                    if proc.returncode == 0 and match:
                        record["ok"] = True
                        record["moves"] = int(match.group(1))
                        record["path"] = parse_path(output)
                except subprocess.TimeoutExpired:
                    record["timeout"] = True
                    record["wall"] = args.timeout

                out.write(json.dumps(record) + "\n")
                out.flush()
                status = "TIMEOUT" if record["timeout"] else ("FAIL" if not record["ok"] else "ok")
                print(
                    f"sample={sample_id:04d} moves={record['moves']} wall={record['wall']} "
                    f"path={len(record['path'])} {status}",
                    flush=True,
                )

    samples = []
    solved = timeout = failed = 0
    walls = []
    with SAMPLES.open() as fh:
        for line in fh:
            record = json.loads(line)
            if record.get("timeout"):
                timeout += 1
            elif record.get("ok"):
                solved += 1
                if record.get("wall") is not None:
                    walls.append(record["wall"])
                samples.extend(tuple(row) for row in record.get("path", []))
            else:
                failed += 1

    rows, counts = matrix_from_samples(samples)
    print(
        f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} "
        f"mean_wall={sum(walls) / len(walls) if walls else 0:.1f}s",
        flush=True,
    )
    print("sample counts (rows=unpaired 0..16, cols=table cost 0..12):", flush=True)
    for unpaired, count_row in enumerate(counts):
        print(f"  u={unpaired:2d} {count_row}", flush=True)
    print(flush=True)
    print_c_matrix(rows)


if __name__ == "__main__":
    main()
