#!/usr/bin/env python3
"""
Sample and build the heuristic matrix for the combined 6x6x6 daisy search.

The eighteen 70^4 tables form three groups of six according to which complete
axis they contain. The matrix coordinate is the maximum cost in each group:
(UD, LR, FB). Samples record the smallest observed remaining distance for each
coordinate, and cube rotations supply all six axis permutations.
"""

# standard libraries
import argparse
import json
import random
import re
import statistics
import subprocess
import time
from collections import defaultdict
from itertools import permutations
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube666 import (
    DAISY_PLUS_TABLES_666,
    PHASE5_ILLEGAL_MOVES,
    RubiksCube666,
    moves_666,
    solved_666,
)

BINARY = "./ida_search_666_daisy_centers"
SOURCE = Path("rubikscubennnsolver/ida_search_666_daisy_centers.c")
MATRIX_DECL = "static const unsigned char daisy_axis_costs_666"
DEFAULT_SAMPLES = Path("utils/666-daisy-samples.jsonl")
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
LEGAL_MOVES = tuple(move for move in moves_666 if move not in PHASE5_ILLEGAL_MOVES)
SCRAMBLE_LENGTH = 60
TABLES_PER_AXIS = 6
COST_MAX = 13


def scramble(rng):
    cube = RubiksCube666(solved_666, "URFDLB")
    for _ in range(SCRAMBLE_LENGTH):
        cube.rotate(rng.choice(LEGAL_MOVES))
    return cube


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True)]
    for flag, filename in DAISY_PLUS_TABLES_666:
        cmd.extend((flag, filename))
    cmd.extend(("--print-ida-summary", "--multiplier", str(multiplier)))
    return cmd


def parse_path(output):
    """Pull (UD, LR, FB, remaining) from the 18-table IDA summary."""
    rows = []
    started = False
    for line in output.splitlines():
        tokens = line.split()
        if not started:
            started = tokens[:1] == ["INIT"]
            if not started:
                continue
        if len(tokens) != 1 + len(DAISY_PLUS_TABLES_666) + 4:
            continue
        try:
            values = [int(value) for value in tokens[1:]]
        except ValueError:
            continue
        table_costs = values[: len(DAISY_PLUS_TABLES_666)]
        remaining = values[-3]
        axis_costs = tuple(
            max(table_costs[start : start + TABLES_PER_AXIS]) for start in range(0, len(table_costs), TABLES_PER_AXIS)
        )
        rows.append((*axis_costs, remaining))
    return rows


def matrix_from_samples(samples, fallback_multiplier):
    """Build a symmetric, monotonic matrix from minimum observed distances."""
    buckets = defaultdict(list)
    for ud, lr, fb, remaining in samples:
        if all(0 <= cost <= COST_MAX for cost in (ud, lr, fb)):
            for ordering in set(permutations((ud, lr, fb))):
                buckets[ordering].append(remaining)

    matrix = [[[0] * (COST_MAX + 1) for _ in range(COST_MAX + 1)] for _ in range(COST_MAX + 1)]
    counts = {}
    for ud in range(COST_MAX + 1):
        for lr in range(COST_MAX + 1):
            for fb in range(COST_MAX + 1):
                values = buckets.get((ud, lr, fb), [])
                counts[(ud, lr, fb)] = len(values)
                admissible = max(ud, lr, fb)
                estimate = max(min(values), admissible) if values else int(fallback_multiplier * admissible + 0.5)
                if ud:
                    estimate = max(estimate, matrix[ud - 1][lr][fb])
                if lr:
                    estimate = max(estimate, matrix[ud][lr - 1][fb])
                if fb:
                    estimate = max(estimate, matrix[ud][lr][fb - 1])
                matrix[ud][lr][fb] = estimate
    return matrix, counts


def format_c_matrix(matrix):
    lines = [f"{MATRIX_DECL}[MATRIX_COST_MAX + 1][MATRIX_COST_MAX + 1][MATRIX_COST_MAX + 1] = {{"]
    for ud, plane in enumerate(matrix):
        lines.append(f"    {{  // UD {ud}")
        for lr, row in enumerate(plane):
            joined = ", ".join(f"{value:2d}" for value in row)
            lines.append(f"        {{{joined}}},  // LR {lr}")
        lines.append("    },")
    lines.append("};\n")
    return "\n".join(lines)


def write_c_matrix(path, text):
    source = path.read_text()
    start = source.index(MATRIX_DECL)
    end = source.index("\n};\n", start) + len("\n};\n")
    path.write_text(source[:start] + text + source[end:])


def load_done(path):
    done = set()
    if path.exists():
        with path.open() as stream:
            for line in stream:
                done.add(json.loads(line)["sample"])
    return done


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--multiplier", type=float, required=True)
    parser.add_argument("--fallback-multiplier", type=float)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    args.samples.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(args.samples)
    if not args.report_only:
        print(
            f"cubes={args.count} multiplier={args.multiplier:g} "
            f"timeout={args.timeout:.0f}s already_done={len(done)}",
            flush=True,
        )
        with args.samples.open("a") as stream:
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

                stream.write(json.dumps(record) + "\n")
                stream.flush()
                status = "TIMEOUT" if record["timeout"] else ("FAIL" if not record["ok"] else "ok")
                print(
                    f"sample={sample_id:04d} moves={record['moves']} wall={record['wall']} "
                    f"path={len(record['path'])} {status}",
                    flush=True,
                )

    samples = []
    solved = timed_out = failed = 0
    walls = []
    solution_moves = []
    with args.samples.open() as stream:
        for line in stream:
            record = json.loads(line)
            if record.get("timeout"):
                timed_out += 1
            elif record.get("ok"):
                solved += 1
                walls.append(record["wall"])
                solution_moves.append(record["moves"])
                samples.extend(tuple(row) for row in record.get("path", []))
            else:
                failed += 1

    fallback = args.fallback_multiplier or args.multiplier
    matrix, counts = matrix_from_samples(samples, fallback)
    print(
        f"\nsolved={solved} timeout={timed_out} failed={failed} path_samples={len(samples)} "
        f"mean_wall={statistics.mean(walls) if walls else 0:.1f}s "
        f"median_wall={statistics.median(walls) if walls else 0:.1f}s "
        f"max_wall={max(walls) if walls else 0:.1f}s "
        f"median_moves={statistics.median(solution_moves) if solution_moves else 0}",
        flush=True,
    )
    populated = sum(1 for count in counts.values() if count)
    print(f"populated cells {populated} of {(COST_MAX + 1) ** 3}", flush=True)
    text = format_c_matrix(matrix)
    if args.write:
        write_c_matrix(SOURCE, text)
        print(f"wrote the matrix to {SOURCE}", flush=True)
    else:
        print(text)


if __name__ == "__main__":
    main()
