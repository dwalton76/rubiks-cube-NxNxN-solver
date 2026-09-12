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
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
LEGAL_MOVES = tuple(move for move in moves_777 if move not in DAISY_CENTERS_ILLEGAL_MOVES_777)
SCRAMBLE_LENGTH = 60
COST_MAX = 15


def scramble(rng):
    cube = RubiksCube777(solved_777, "URFDLB")
    for _ in range(SCRAMBLE_LENGTH):
        cube.rotate(rng.choice(LEGAL_MOVES))
    return cube


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True), "--native-only"]
    for flag, filename in NATIVE_SOLVE_PERFECT_TABLES_777:
        cmd.extend((flag, filename))
    cmd.append("--print-ida-summary")
    if multiplier:
        cmd.extend(("--multiplier", str(multiplier)))
    return cmd


def parse_path(output):
    """Pull (UD, LR, FB, remaining) from the --print-ida-summary rows."""
    rows = []
    started = False
    for line in output.splitlines():
        tokens = line.split()
        if not started:
            started = tokens[:1] == ["INIT"]
            if not started:
                continue
        if len(tokens) != 8:
            continue
        try:
            ud, lr, fb, _ctg, remaining, _index, _daisy = (int(value) for value in tokens[1:])
        except ValueError:
            continue
        rows.append((ud, lr, fb, remaining))
    return rows


def matrix_from_samples(samples, fallback_multiplier):
    """
    Cells hold the smallest remaining count seen for that triple, and unsampled
    cells hold fallback_multiplier times the admissible max. Values also propagate
    along every axis so a more scrambled axis cannot look closer to native.
    """
    buckets = defaultdict(list)
    for ud, lr, fb, remaining in samples:
        if all(0 <= cost <= COST_MAX for cost in (ud, lr, fb)):
            for ordering in permutations((ud, lr, fb)):
                buckets[ordering].append(remaining)

    matrix = [[[0] * (COST_MAX + 1) for _ in range(COST_MAX + 1)] for _ in range(COST_MAX + 1)]
    counts = {}
    for ud in range(COST_MAX + 1):
        for lr in range(COST_MAX + 1):
            for fb in range(COST_MAX + 1):
                values = buckets.get((ud, lr, fb), [])
                counts[(ud, lr, fb)] = len(values)
                admissible = max(ud, lr, fb)
                if values:
                    estimate = max(min(values), admissible)
                else:
                    estimate = int(fallback_multiplier * admissible + 0.5)
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
    """Swap the matrix in the C source for a freshly sampled one."""
    source = path.read_text()
    start = source.index(MATRIX_DECL)
    end = source.index("\n};\n", start) + len("\n};\n")
    path.write_text(source[:start] + text + source[end:])


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
    done = load_done(args.samples)
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
    solution_moves = []
    with args.samples.open() as fh:
        for line in fh:
            record = json.loads(line)
            if record.get("timeout"):
                timeout += 1
            elif record.get("ok"):
                solved += 1
                if record.get("wall") is not None:
                    walls.append(record["wall"])
                if record.get("moves") is not None:
                    solution_moves.append(record["moves"])
                samples.extend(tuple(row) for row in record.get("path", []))
            else:
                failed += 1

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
    text = format_c_matrix(matrix)
    if args.write:
        write_c_matrix(SOURCE, text)
        print(f"wrote the matrix to {SOURCE}", flush=True)
    else:
        print(text)


if __name__ == "__main__":
    main()
