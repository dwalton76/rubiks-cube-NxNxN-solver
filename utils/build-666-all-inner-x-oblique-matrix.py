#!/usr/bin/env python3
"""
Solve 6x6x6 phase 1 (all inner x-centers + pair LR obliques) with an
admissible unpaired multiplier of 0.25, then print a heuristic matrix
indexed by (unpaired, inner-x cost) -> remaining moves.

Orbit1 OLL is left off so TRU is remaining work for staging/pairing only.
The existing parity floor still covers OLL at search time.

This was used to build the unpaired_count_all_inner_x_centers_666
matrix in ida_search_666_centers_stage.c
"""

# standard libraries
import argparse
import json
import math
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube666 import RubiksCube666

TABLE = "lookup-tables/lookup-table-6x6x6-step05-inner-x-centers-stage-one-phase.cost-only.bin"
BINARY = "./ida_search_666_centers_stage"
SAMPLES = Path("utils/phase1-025-samples.jsonl")
SUMMARY_RE = re.compile(r"SOLUTION \((\d+) steps\)")
IDA_RE = re.compile(r"IDA found solution, explored ([\d,]+) total nodes, took ([0-9.]+)s")


def solve_command(state):
    cube = RubiksCube666(state, "URFDLB")
    return [
        BINARY,
        "--kociemba",
        cube.get_kociemba_string(True),
        "--all-inner-x-cost",
        TABLE,
        "--unpaired-multiplier",
        "0.25",
    ]


def parse_path(output):
    """Pull (ix_cost, unpaired, remaining) from the IDA summary."""
    rows = []
    found_init = False
    for line in output.splitlines():
        stripped = line.strip()
        if not found_init:
            if stripped.startswith("INIT"):
                found_init = True
            else:
                continue
        if not stripped or stripped.startswith("====") or "CTG" in stripped:
            continue
        tokens = stripped.split()
        if tokens[0] == "INIT":
            numbers = tokens[1:]
        else:
            numbers = tokens[1:]
        if len(numbers) != 5:
            continue
        try:
            ix_cost, unpaired, _ctg, remaining, _idx = (int(value) for value in numbers)
        except ValueError:
            continue
        rows.append((ix_cost, unpaired, remaining))
    return rows


def load_done(path):
    done = set()
    if not path.exists():
        return done
    with path.open() as fh:
        for line in fh:
            record = json.loads(line)
            done.add(record["cube"])
    return done


def matrix_from_samples(samples, ix_max):
    """Minimum remaining moves, never below max(ix, ceil(unpaired/4))."""
    buckets = defaultdict(list)
    for ix_cost, unpaired, remaining in samples:
        if 0 <= unpaired <= 8 and 0 <= ix_cost <= ix_max:
            buckets[(unpaired, ix_cost)].append(remaining)

    rows = []
    counts = []
    for unpaired in range(9):
        row = []
        count_row = []
        floor = math.ceil(unpaired / 4) if unpaired else 0
        for ix_cost in range(ix_max + 1):
            admissible = max(ix_cost, floor)
            values = buckets.get((unpaired, ix_cost), [])
            count_row.append(len(values))
            estimate = min(values) if values else admissible
            row.append(max(admissible, estimate))
        rows.append(row)
        counts.append(count_row)
    return rows, counts


def print_c_matrix(rows, ix_max):
    print(f"unsigned int unpaired_count_all_inner_x_centers_666[9][{ix_max + 1}] = {{")
    for unpaired, values in enumerate(rows):
        joined = ", ".join(f"{value:2d}" for value in values)
        print(f"    {{{joined}}},    // unpaired {unpaired}")
    print("};")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()

    with open("utils/10k-666-cubes.json") as fh:
        states = json.load(fh)["6x6x6"][args.offset : args.offset + args.count]

    SAMPLES.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(SAMPLES)
    print(f"cubes={len(states)} timeout={args.timeout:.0f}s already_done={len(done)}", flush=True)

    with SAMPLES.open("a") as out:
        for index, state in enumerate(states):
            cube_id = args.offset + index
            if cube_id in done:
                print(f"cube={cube_id:03d} skip", flush=True)
                continue

            started = time.perf_counter()
            record = {
                "cube": cube_id,
                "ok": False,
                "timeout": False,
                "wall": None,
                "moves": None,
                "nodes": None,
                "path": [],
            }
            try:
                proc = subprocess.run(
                    solve_command(state),
                    capture_output=True,
                    text=True,
                    timeout=args.timeout,
                )
                record["wall"] = round(time.perf_counter() - started, 3)
                output = proc.stdout + proc.stderr
                match = SUMMARY_RE.search(output)
                ida = IDA_RE.search(output)
                if proc.returncode == 0 and match:
                    record["ok"] = True
                    record["moves"] = int(match.group(1))
                    record["nodes"] = int(ida.group(1).replace(",", "")) if ida else None
                    record["path"] = parse_path(output)
            except subprocess.TimeoutExpired:
                record["timeout"] = True
                record["wall"] = args.timeout

            out.write(json.dumps(record) + "\n")
            out.flush()
            status = "TIMEOUT" if record["timeout"] else ("FAIL" if not record["ok"] else "ok")
            print(
                f"cube={cube_id:03d} moves={record['moves']} wall={record['wall']} "
                f"samples={len(record['path'])} {status}",
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

    ix_max = max((ix for ix, _unpaired, _remaining in samples), default=10)
    ix_max = max(ix_max, 10)
    rows, counts = matrix_from_samples(samples, ix_max)

    print(
        f"\nsolved={solved} timeout={timeout} failed={failed} "
        f"path_samples={len(samples)} mean_wall={sum(walls)/len(walls) if walls else 0:.1f}s",
        flush=True,
    )
    print("sample counts (rows=unpaired 0..8, cols=inner-x cost):", flush=True)
    for unpaired, count_row in enumerate(counts):
        print(f"  u={unpaired} {count_row}", flush=True)
    print(flush=True)
    print_c_matrix(rows, ix_max)


if __name__ == "__main__":
    main()
