#!/usr/bin/env python3
"""
Build the combined heuristic matrix for the 7x7x7 daisy search, which daisies the
U/D, L/R, and F/B centers on all three axes at once.

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
    DAISY_PERFECT_TABLES_777,
    RubiksCube777,
    moves_777,
    solved_777,
)

BINARY = "./ida_search_777_daisy_centers"
SOURCE = Path("rubikscubennnsolver/ida_search_777_daisy_centers.c")
MATRIX_DECL = "static const unsigned char daisy_axis_costs_777"
DEFAULT_SAMPLES = Path("utils/777-daisy-samples.jsonl")
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
LEGAL_MOVES = tuple(move for move in moves_777 if move not in DAISY_CENTERS_ILLEGAL_MOVES_777)
SCRAMBLE_LENGTH = 60
# Every per-axis perfect table tops out at depth 15.
COST_MAX = 15


def scramble(rng):
    cube = RubiksCube777(solved_777, "URFDLB")
    for _ in range(SCRAMBLE_LENGTH):
        cube.rotate(rng.choice(LEGAL_MOVES))
    return cube


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True)]
    for flag, filename in DAISY_PERFECT_TABLES_777:
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
    along every axis: a more scrambled axis cannot bring the combined daisy closer,
    which keeps the matrix monotonic.
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
