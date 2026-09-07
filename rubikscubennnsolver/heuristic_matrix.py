"""Shared helpers for the utils/build-*-matrix.py heuristic samplers."""

from __future__ import annotations

# standard libraries
import json
import re
import subprocess
import time
from collections import Counter, defaultdict
from itertools import permutations, product
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

SOLUTION_RE = re.compile(r"SOLUTION \((\d+) steps\)")
IDA_RE = re.compile(r"IDA found solution, explored ([\d,]+) total nodes, took ([0-9.]+)s")

Coord = Tuple[int, ...]
Matrix = List


def parse_ida_summary_path(output: str, token_count: int, value_indexes: Sequence[int]) -> List[Tuple[int, ...]]:
    """Read (cost..., remaining) tuples from an IDA summary that starts at INIT."""
    rows = []
    started = False
    for line in output.splitlines():
        tokens = line.split()
        if not started:
            started = tokens[:1] == ["INIT"]
            if not started:
                continue
        if len(tokens) != token_count:
            continue
        try:
            values = [int(token) for token in tokens[1:]]
        except ValueError:
            continue
        rows.append(tuple(values[index] for index in value_indexes))
    return rows


def scramble_cube(rng, cube_cls, solved, legal_moves, length: int = 60):
    cube = cube_cls(solved, "URFDLB")
    for _ in range(length):
        cube.rotate(rng.choice(legal_moves))
    return cube


def load_done_sample_ids(path: Path, *, ok_only: bool = False) -> set:
    """JSONL sample ids already on disk. ok_only skips timeouts so they can be retried."""
    done = set()
    if not path.exists():
        return done
    with path.open() as handle:
        for line in handle:
            record = json.loads(line)
            if ok_only and not record.get("ok"):
                continue
            done.add(record["sample"])
    return done


def run_timed_solve(cmd, timeout: float) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "timeout": True, "wall": timeout, "output": "", "moves": None, "nodes": None}

    wall = round(time.perf_counter() - started, 3)
    output = proc.stdout + proc.stderr
    match = SOLUTION_RE.search(output)
    ok = proc.returncode == 0 and match is not None
    moves = int(match.group(1)) if match else None
    ida = IDA_RE.search(output)
    nodes = int(ida.group(1).replace(",", "")) if ida else None
    return {"ok": ok, "timeout": False, "wall": wall, "output": output, "moves": moves, "nodes": nodes}


def append_solve_sample(
    out,
    sample_id: int,
    cmd,
    timeout: float,
    parse_path: Callable[[str], list],
    extra: Optional[dict] = None,
) -> dict:
    record = {
        "sample": sample_id,
        "ok": False,
        "timeout": False,
        "wall": None,
        "moves": None,
        "nodes": None,
        "path": [],
    }
    if extra:
        record.update(extra)
    result = run_timed_solve(cmd, timeout)
    record["ok"] = result["ok"]
    record["timeout"] = result["timeout"]
    record["wall"] = result["wall"]
    record["moves"] = result["moves"]
    record["nodes"] = result["nodes"]
    if result["ok"]:
        record["path"] = parse_path(result["output"])
    out.write(json.dumps(record) + "\n")
    out.flush()
    status = "TIMEOUT" if record["timeout"] else ("FAIL" if not record["ok"] else "ok")
    print(
        f"sample={sample_id:04d} moves={record['moves']} wall={record['wall']} " f"path={len(record['path'])} {status}",
        flush=True,
    )
    return record


def summarize_jsonl(path: Path):
    """Return solved/timeout/failed counts, path tuples, walls, and solution lengths."""
    samples = []
    solved = timeout = failed = 0
    walls = []
    solution_moves = []
    with path.open() as handle:
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
    return solved, timeout, failed, samples, walls, solution_moves


def _nested_zeros(dims: Sequence[int]) -> Matrix:
    if len(dims) == 1:
        return [0] * dims[0]
    return [_nested_zeros(dims[1:]) for _ in range(dims[0])]


def _get(matrix: Matrix, index: Coord):
    node = matrix
    for axis in index:
        node = node[axis]
    return node


def _set(matrix: Matrix, index: Coord, value: int) -> None:
    node = matrix
    for axis in index[:-1]:
        node = node[axis]
    node[index[-1]] = value


def cell_remaining_estimate(values: Sequence[int], min_fraction: float = 0.0) -> int:
    """Smallest remaining whose share of the cell is above `min_fraction`.

    Walk from the minimum upward and skip a value while it is `min_fraction`
    or less of the cell (5% drops a lone 8 among twenty samples). If every
    value is that rare, fall back to min.
    """
    if min_fraction <= 0:
        return min(values)
    n = len(values)
    counts = Counter(values)
    for remaining in sorted(counts):
        if counts[remaining] / n > min_fraction:
            return remaining
    return min(values)


def fill_cost_matrix(
    samples: Iterable[Sequence[int]],
    dims: Sequence[int],
    admissible: Callable[[Coord], int],
    *,
    permute_coords: bool = False,
    fallback_multiplier: float = 1.0,
    min_fraction: float = 0.0,
) -> Tuple[Matrix, Dict[Coord, int]]:
    """
    Remaining per cell, never below `admissible`. Occupied cells use the
    smallest remaining whose share of the cell is above `min_fraction` (the
    plain min when that is 0). Empty cells use fallback_multiplier times the
    floor. Values propagate so a more scrambled coordinate cannot look closer
    to solved.
    """
    ndim = len(dims)
    buckets = defaultdict(list)
    for sample in samples:
        coords = tuple(sample[:ndim])
        remaining = sample[ndim]
        if any(not (0 <= coord < dims[axis]) for axis, coord in enumerate(coords)):
            continue
        orderings = permutations(coords) if permute_coords else (coords,)
        for ordering in orderings:
            buckets[ordering].append(remaining)

    matrix = _nested_zeros(dims)
    counts = {}
    for index in product(*(range(size) for size in dims)):
        values = buckets.get(index, [])
        counts[index] = len(values)
        floor = admissible(index)
        if values:
            estimate = max(cell_remaining_estimate(values, min_fraction), floor)
        else:
            estimate = max(int(fallback_multiplier * floor + 0.5), floor)
        for axis, coord in enumerate(index):
            if coord:
                previous = list(index)
                previous[axis] -= 1
                estimate = max(estimate, _get(matrix, tuple(previous)))
        _set(matrix, index, estimate)
    return matrix, counts


def format_c_matrix_2d(opening: str, matrix: Matrix, row_comment: Callable[[int], str]) -> str:
    lines = [opening]
    for unpaired, row in enumerate(matrix):
        joined = ", ".join(f"{value:2d}" for value in row)
        lines.append(f"    {{{joined}}},  // {row_comment(unpaired)}")
    lines.append("};")
    return "\n".join(lines) + "\n"


def format_c_matrix_3d(opening: str, matrix: Matrix, axis0: str = "UD", axis1: str = "LR") -> str:
    lines = [opening]
    for i, plane in enumerate(matrix):
        lines.append(f"    {{  // {axis0} {i}")
        for j, row in enumerate(plane):
            joined = ", ".join(f"{value:2d}" for value in row)
            lines.append(f"        {{{joined}}},  // {axis1} {j}")
        lines.append("    },")
    lines.append("};")
    return "\n".join(lines) + "\n"


def write_c_matrix(path: Path, decl: str, text: str) -> None:
    source = path.read_text()
    start = source.find(decl)
    if start == -1:
        raise SystemExit(f"{decl} not found in {path}")
    end = source.index("\n};\n", start) + len("\n};\n")
    path.write_text(source[:start] + text + source[end:])
