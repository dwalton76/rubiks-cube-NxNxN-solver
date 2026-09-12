#!/usr/bin/env python3
"""Sample 5x5x5 one-phase center staging and rebuild its x/t cost matrix."""

# standard libraries
import argparse
import json
import re
import statistics
import subprocess
import time
from collections import defaultdict
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import LookupTableIDA555CentersStageOnePhase, RubiksCube555

BINARY = "./ida_search_555_centers_stage"
X_TABLE = "lookup-tables/lookup-table-5x5x5-step15-x-centers-stage-one-phase.cost-only.bin"
T_TABLE = "lookup-tables/lookup-table-5x5x5-step16-t-centers-stage-one-phase.cost-only.bin"
SOURCE = Path("rubikscubennnsolver/ida_search_555_centers_stage.c")
MATRIX_DECL = "static const unsigned char center_stage_costs_555"
DEFAULT_SAMPLES = Path("utils/555-centers-stage-one-phase-samples.jsonl")
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
X_COST_MAX = 11
T_COST_MAX = 12


def solve_command(state, multiplier):
    cube = RubiksCube555(state, "URFDLB")
    projected = LookupTableIDA555CentersStageOnePhase(cube).center_only_kociemba_string()
    return [
        BINARY,
        "--kociemba",
        projected,
        "--x-cost",
        X_TABLE,
        "--t-cost",
        T_TABLE,
        "--print-ida-summary",
        "--multiplier",
        str(multiplier),
    ]


def parse_path(output):
    """Return (x cost, t cost, true remaining moves) from the IDA summary."""
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
            x_cost, t_cost, _ctg, remaining, _index = (int(value) for value in tokens[1:])
        except ValueError:
            continue
        rows.append((x_cost, t_cost, remaining))
    return rows


def load_records(path):
    if not path.exists():
        return []
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def matrix_from_samples(samples, fallback_multiplier):
    buckets = defaultdict(list)
    for x_cost, t_cost, remaining in samples:
        if 0 <= x_cost <= X_COST_MAX and 0 <= t_cost <= T_COST_MAX:
            buckets[x_cost, t_cost].append(remaining)

    matrix = [[0] * (T_COST_MAX + 1) for _ in range(X_COST_MAX + 1)]
    counts = [[0] * (T_COST_MAX + 1) for _ in range(X_COST_MAX + 1)]
    for x_cost in range(X_COST_MAX + 1):
        for t_cost in range(T_COST_MAX + 1):
            values = buckets.get((x_cost, t_cost), [])
            counts[x_cost][t_cost] = len(values)
            admissible = max(x_cost, t_cost)
            estimate = max(admissible, min(values)) if values else int(fallback_multiplier * admissible + 0.5)
            if x_cost:
                estimate = max(estimate, matrix[x_cost - 1][t_cost])
            if t_cost:
                estimate = max(estimate, matrix[x_cost][t_cost - 1])
            matrix[x_cost][t_cost] = estimate
    return matrix, counts


def format_c_matrix(matrix):
    lines = [f"{MATRIX_DECL}[X_COST_MAX + 1][T_COST_MAX + 1] = {{"]
    for x_cost, row in enumerate(matrix):
        values = ", ".join(f"{value:2d}" for value in row)
        lines.append(f"    {{{values}}},  // x cost {x_cost}")
    lines.append("};\n")
    return "\n".join(lines)


def write_c_matrix(text):
    source = SOURCE.read_text()
    start = source.index(MATRIX_DECL)
    end = source.index("\n};\n", start) + len("\n};\n")
    SOURCE.write_text(source[:start] + text + source[end:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--multiplier", type=float, required=True)
    parser.add_argument("--fallback-multiplier", type=float, default=None)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    records = load_records(args.samples)
    done = {record["cube"] for record in records}
    if not args.report_only:
        states = json.loads(Path("utils/10k-555-cubes.json").read_text())["5x5x5"]
        args.samples.parent.mkdir(parents=True, exist_ok=True)
        with args.samples.open("a") as output_file:
            for index in range(args.count):
                cube_id = args.offset + index
                if cube_id in done:
                    print(f"cube={cube_id:03d} skip", flush=True)
                    continue
                record = {
                    "cube": cube_id,
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
                        solve_command(states[cube_id], args.multiplier),
                        capture_output=True,
                        text=True,
                        timeout=args.timeout,
                    )
                    record["wall"] = round(time.perf_counter() - started, 3)
                    combined_output = proc.stdout + proc.stderr
                    match = SOLUTION_RE.search(combined_output)
                    if proc.returncode == 0 and match:
                        record["ok"] = True
                        record["moves"] = int(match.group(1))
                        record["path"] = parse_path(combined_output)
                except subprocess.TimeoutExpired:
                    record["timeout"] = True
                    record["wall"] = args.timeout

                output_file.write(json.dumps(record) + "\n")
                output_file.flush()
                status = "ok" if record["ok"] else ("TIMEOUT" if record["timeout"] else "FAIL")
                print(
                    f"cube={cube_id:03d} moves={record['moves']} wall={record['wall']} "
                    f"samples={len(record['path'])} {status}",
                    flush=True,
                )
        records = load_records(args.samples)

    selected = [
        record
        for record in records
        if args.offset <= record["cube"] < args.offset + args.count and record.get("multiplier") == args.multiplier
    ]
    path_samples = [tuple(row) for record in selected if record.get("ok") for row in record.get("path", [])]
    fallback = args.fallback_multiplier or args.multiplier
    matrix, counts = matrix_from_samples(path_samples, fallback)
    walls = [record["wall"] for record in selected if record.get("ok")]
    moves = [record["moves"] for record in selected if record.get("ok")]
    timeouts = sum(bool(record.get("timeout")) for record in selected)
    failures = len(selected) - len(walls) - timeouts

    print(
        f"solved={len(walls)}/{len(selected)} timeout={timeouts} failed={failures} "
        f"path_samples={len(path_samples)} "
        f"median_wall={statistics.median(walls) if walls else 0:.3f} "
        f"max_wall={max(walls) if walls else 0:.3f} "
        f"median_moves={statistics.median(moves) if moves else 0}",
        flush=True,
    )
    print("sample counts (rows=x cost 0..11, columns=t cost 0..12):")
    for x_cost, row in enumerate(counts):
        print(f"  x={x_cost:2d} {row}")
    matrix_text = format_c_matrix(matrix)
    print(matrix_text)
    if args.write:
        if len(walls) != args.count:
            raise SystemExit("refusing to write matrix: not all requested cubes solved")
        write_c_matrix(matrix_text)
        print(f"updated {SOURCE}")


if __name__ == "__main__":
    main()
