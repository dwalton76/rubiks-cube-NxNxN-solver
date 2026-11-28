#!/usr/bin/env python3
"""Compare ida_search_555_centers_stage flag sets on the same scrambled cubes.

Each --config is LABEL:FLAGS (FLAGS may be empty). The first config is the baseline: every other
config must find a solution of the same length, and the summary reports nodes and wall-time ratios.
Every config gets the joint LR t+x table unless its FLAGS pass their own --lr-joint-cost.

    ./venv/bin/python3 utils/benchmark-555-centers-stage.py --count 20 --scramble-length 14 \
        --config base:--orbit0-need-even-w --config threads8:"--orbit0-need-even-w --threads 8"
"""

# standard libraries
import argparse
import math
import random
import re
import shlex
import subprocess
import time

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, moves_555, solved_555

SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
THRESHOLD_RE = re.compile(r"IDA threshold (\d+), explored (\d+) nodes, took ([\d.]+)s")
TABLES = ("--lr-joint-cost", "lookup-tables/lookup-table-5x5x5-step13-LR-t-x-centers-joint.sym-nibble.bin")


def scrambled_states(count, length, seed):
    rng = random.Random(seed)
    states = []
    for _ in range(count):
        cube = RubiksCube555(solved_555, "URFDLB")
        for _ in range(length):
            cube.rotate(rng.choice(moves_555))
        states.append(cube.get_kociemba_string(True))
    return states


def run(state, flags, timeout):
    tables = () if "--lr-joint-cost" in flags else TABLES
    cmd = ["./ida_search_555_centers_stage", "--kociemba", state, *tables, *flags]
    started = time.perf_counter()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"solved": False, "wall": timeout, "nodes": 0, "search": timeout}
    wall = time.perf_counter() - started
    output = result.stdout + result.stderr
    solution = SOLUTION_RE.search(output)
    thresholds = THRESHOLD_RE.findall(output)
    row = {
        "solved": solution is not None,
        "length": int(solution.group(1)) if solution else None,
        "wall": wall,
        "nodes": sum(int(nodes) for _, nodes, _ in thresholds),
        "search": sum(float(seconds) for _, _, seconds in thresholds),
    }
    if solution is None:
        errors = [line for line in result.stderr.splitlines() if line.strip()]
        row["error"] = f"exit {result.returncode}: {errors[-1] if errors else 'no stderr'}"
    return row


def geomean(values):
    return math.exp(sum(math.log(value) for value in values) / len(values))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--scramble-length", type=int, default=14)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--min-search", type=float, default=0.2, help="baseline seconds for a cube to count in ratios")
    parser.add_argument("--config", action="append", default=None, help="LABEL:FLAGS, first is the baseline")
    args = parser.parse_args()

    configs = []
    for text in args.config or ["base:"]:
        label, _, flags = text.partition(":")
        configs.append((label, shlex.split(flags)))
    states = scrambled_states(args.count, args.scramble_length, args.seed)
    results = {label: [] for label, _ in configs}

    for index, state in enumerate(states):
        for label, flags in configs:
            row = run(state, flags, args.timeout)
            results[label].append(row)
            print(
                f"cube={index:03d} {label:>10} solved={row['solved']} length={row.get('length')} "
                f"nodes={row['nodes']} search={row['search']:.2f}s wall={row['wall']:.2f}s"
                + (f" error={row['error']}" if "error" in row else ""),
                flush=True,
            )

    base_label = configs[0][0]
    base = results[base_label]
    print()
    for label, _ in configs:
        rows = results[label]
        both = [i for i in range(len(rows)) if rows[i]["solved"] and base[i]["solved"]]
        mismatched = [i for i in both if rows[i]["length"] != base[i]["length"]]
        line = (
            f"{label:>10}: solved {sum(r['solved'] for r in rows)}/{len(rows)}, "
            f"total nodes {sum(r['nodes'] for r in rows):,}, "
            f"total search {sum(r['search'] for r in rows):.1f}s, wall {sum(r['wall'] for r in rows):.1f}s"
        )
        # Ratios only on cubes that were slow for the baseline; a timeout counts as the timeout.
        deep = [i for i in range(len(rows)) if base[i]["search"] >= args.min_search]
        deep_both = [i for i in deep if i in both]
        if label != base_label and deep:
            time_ratio = geomean([rows[i]["search"] / base[i]["search"] for i in deep])
            line += f", over {len(deep)} deep cubes: search time x{time_ratio:.2f}"
            if deep_both:
                node_ratio = geomean([rows[i]["nodes"] / base[i]["nodes"] for i in deep_both])
                line += f", nodes x{node_ratio:.2f} ({len(deep_both)} solved by both)"
        line += f", LENGTH MISMATCHES {mismatched}" if mismatched else ""
        print(line)


if __name__ == "__main__":
    main()
