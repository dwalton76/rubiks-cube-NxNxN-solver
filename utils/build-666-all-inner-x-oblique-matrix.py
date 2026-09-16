#!/usr/bin/env python3
"""Sample the 6x6 phase-1 heuristic matrix used by ida_search_666_centers_stage.

Start from the admissible floor max(inner-x, ceil(unpaired/4)), find the
lowest IDA --multiplier that still finishes, then solve cubes from
utils/10k-666-cubes.json. Remaining counts along those solutions fill
unpaired_count_all_inner_x_centers_666. Orbit1 OLL is left off so TRU is
staging/pairing work; the C parity floor still covers OLL at search time.
"""

from __future__ import annotations

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
SOURCE = Path("rubikscubennnsolver/ida_search_666_centers_stage.c")
MATRIX_DECL = "static const unsigned char unpaired_count_all_inner_x_centers_666"
DEFAULT_SAMPLES = Path("utils/666-centers-stage-orbit1-samples.jsonl")
CUBES = Path("utils/10k-666-cubes.json")
SLOW_KOCIEMBA = "LUUUBUFFDBBUDDUDFBRDRBLULFBUURRFLBRLUDBLFRDULBLFLDBRULLBBUFDRRRLRLLDUDLBDRFRDFDRRBDFDLLFLURULFFFBBLRDUUUDUFBRLBRRDBLDUUBLDFDFLRDBLFRDFRBFBFRRDDRBDRBFFRLBUDLFRDRRLUURUUUBBDFBLLBFDRFBUFFLUURBFUUBLFLFDFRDURBFDULLUDLBFBD"
SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
IDA_RE = re.compile(r"IDA found solution, explored ([\d,]+) total nodes, took ([0-9.]+)s")
# The one-phase inner-x table is populated through depth 11.
COST_MAX = 11


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
    """Pull (ix_cost, unpaired, remaining) from the IDA summary."""
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
            ix_cost, unpaired, _ctg, remaining, _index = (int(value) for value in tokens[1:])
        except ValueError:
            continue
        rows.append((ix_cost, unpaired, remaining))
    return rows


def matrix_from_samples(samples, fallback_multiplier):
    """
    Cells hold the smallest remaining count seen for that pair, never below
    max(inner-x, ceil(unpaired/4)). Empty cells use fallback_multiplier times
    that floor. Values also propagate so more unpaired or inner-x work cannot
    lower the estimate.
    """
    buckets = defaultdict(list)
    for ix_cost, unpaired, remaining in samples:
        if 0 <= unpaired <= 8 and 0 <= ix_cost <= COST_MAX:
            buckets[(unpaired, ix_cost)].append(remaining)

    matrix = [[0] * (COST_MAX + 1) for _ in range(9)]
    counts = {}
    for unpaired in range(9):
        floor = math.ceil(unpaired / 4) if unpaired else 0
        for ix_cost in range(COST_MAX + 1):
            values = buckets.get((unpaired, ix_cost), [])
            counts[(unpaired, ix_cost)] = len(values)
            admissible = max(ix_cost, floor)
            if values:
                estimate = max(min(values), admissible)
            else:
                estimate = int(fallback_multiplier * admissible + 0.5)
                estimate = max(estimate, admissible)
            if unpaired:
                estimate = max(estimate, matrix[unpaired - 1][ix_cost])
            if ix_cost:
                estimate = max(estimate, matrix[unpaired][ix_cost - 1])
            matrix[unpaired][ix_cost] = estimate
    return matrix, counts


def format_c_matrix(matrix):
    lines = [f"{MATRIX_DECL}[9][ALL_INNER_X_MATRIX_COST_MAX + 1] = {{"]
    for unpaired, row in enumerate(matrix):
        joined = ", ".join(f"{value:2d}" for value in row)
        lines.append(f"    {{{joined}}},  // {unpaired}")
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
    """Only solved cubes are done; timeouts are retried as the matrix improves."""
    done = set()
    if not path.exists():
        return done
    with path.open() as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("ok"):
                done.add(record["sample"])
    return done


CALIBRATE_MULTIPLIERS = (1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0)


def solve_one(cube, unpaired_multiplier, multiplier, timeout, orbit1):
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            solve_command(cube, unpaired_multiplier, multiplier, orbit1),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, timeout, None
    wall = round(time.perf_counter() - started, 3)
    match = SOLUTION_RE.search(proc.stdout + proc.stderr)
    ok = proc.returncode == 0 and match is not None
    moves = int(match.group(1)) if match else None
    return ok, wall, moves


def lowest_multiplier(cubes, unpaired_multiplier, timeout, orbit1):
    """Return the smallest IDA multiplier that solves every probe cube in time."""
    for multiplier in CALIBRATE_MULTIPLIERS:
        ida_multiplier = None if multiplier == 1.0 else multiplier
        print(f"calibrate multiplier={multiplier} timeout={timeout:.0f}s", flush=True)
        all_ok = True
        for index, cube in enumerate(cubes):
            ok, wall, moves = solve_one(cube, unpaired_multiplier, ida_multiplier, timeout, orbit1)
            status = "ok" if ok else "TIMEOUT"
            print(
                f"  probe={index} moves={moves} wall={wall} {status}",
                flush=True,
            )
            if not ok:
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
    done = load_done(args.samples)
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
                record = {
                    "sample": sample_id,
                    "unpaired_multiplier": args.unpaired_multiplier,
                    "multiplier": args.multiplier,
                    "orbit1": args.orbit1,
                    "ok": False,
                    "timeout": False,
                    "wall": None,
                    "moves": None,
                    "nodes": None,
                    "path": [],
                }
                started = time.perf_counter()
                try:
                    proc = subprocess.run(
                        solve_command(cube, args.unpaired_multiplier, args.multiplier, args.orbit1),
                        capture_output=True,
                        text=True,
                        timeout=args.timeout,
                    )
                    record["wall"] = round(time.perf_counter() - started, 3)
                    output = proc.stdout + proc.stderr
                    match = SOLUTION_RE.search(output)
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
                if record.get("wall") is not None:
                    walls.append(record["wall"])
                if record.get("moves") is not None:
                    solution_moves.append(record["moves"])
                samples.extend(tuple(row) for row in record.get("path", []))
            elif record.get("timeout"):
                timeout += 1
            else:
                failed += 1

    matrix, counts = matrix_from_samples(samples, args.fallback_multiplier)
    filled = sum(1 for count in counts.values() if count)
    total = 9 * (COST_MAX + 1)
    print(f"\nsolved={solved} timeout={timeout} failed={failed} path_samples={len(samples)} " f"cells={filled}/{total}")
    if walls:
        print(
            f"median_wall={sorted(walls)[len(walls) // 2]:.3f} "
            f"median_moves={sorted(solution_moves)[len(solution_moves) // 2]}"
        )
    print("sample counts (rows=unpaired 0..8, cols=inner-x cost):", flush=True)
    for unpaired in range(9):
        print(f"  u={unpaired} {[counts[(unpaired, ix)] for ix in range(COST_MAX + 1)]}", flush=True)
    print(format_c_matrix(matrix), end="")
    if args.write:
        write_c_matrix(SOURCE, format_c_matrix(matrix))
        print(f"wrote {SOURCE}")


if __name__ == "__main__":
    main()
