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
import json
import random
import re
import subprocess
import time
from collections import defaultdict
from itertools import permutations
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube666 import DAISY_INNER_X_SPINE_TABLES_666, RubiksCube666, moves_666, solved_666

BINARY = "./ida_search_666_daisy_centers"
SOURCE = Path("rubikscubennnsolver/ida_search_666_daisy_centers.c")
MATRIX_DECL = "static const unsigned char daisy_spine_costs_666"
DEFAULT_SAMPLES = Path("utils/666-daisy-spine-samples.jsonl")
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
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
SCRAMBLE_LENGTH = 60
# The three 70^5 spine tables reach depth 16.
COST_MAX = 16


def scramble(rng):
    cube = RubiksCube666(solved_666, "URFDLB")
    for _ in range(SCRAMBLE_LENGTH):
        cube.rotate(rng.choice(LEGAL_MOVES))
    return cube


def solve_command(cube, multiplier):
    cmd = [BINARY, "--kociemba", cube.get_kociemba_string(True)]
    for flag, filename in DAISY_INNER_X_SPINE_TABLES_666:
        cmd.extend((flag, filename))
    cmd.append("--print-ida-summary")
    if multiplier is not None:
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
    lines.append("};")
    return "\n".join(lines) + "\n"


def write_c_matrix(path, text):
    source = path.read_text()
    start = source.find(MATRIX_DECL)
    if start == -1:
        raise SystemExit(f"{MATRIX_DECL} not found in {path}")
    end = source.index("\n};\n", start) + len("\n};\n")
    path.write_text(source[:start] + text + source[end:])


def load_done(path):
    done = set()
    if not path.exists():
        return done
    with path.open() as handle:
        for line in handle:
            done.add(json.loads(line)["sample"])
    return done


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
    with args.samples.open() as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("ok"):
                solved += 1
                walls.append(record["wall"])
                solution_moves.append(record["moves"])
                samples.extend(record["path"])
            elif record.get("timeout"):
                timeout += 1
            else:
                failed += 1

    matrix, counts = matrix_from_samples(samples, args.fallback_multiplier)
    filled = sum(1 for count in counts.values() if count)
    total = (COST_MAX + 1) ** 3
    print(f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} " f"cells={filled}/{total}")
    if walls:
        print(
            f"median_wall={sorted(walls)[len(walls) // 2]:.3f} "
            f"median_moves={sorted(solution_moves)[len(solution_moves) // 2]}"
        )
    print(format_c_matrix(matrix), end="")
    if args.write:
        write_c_matrix(SOURCE, format_c_matrix(matrix))
        print(f"wrote {SOURCE}")


if __name__ == "__main__":
    main()
