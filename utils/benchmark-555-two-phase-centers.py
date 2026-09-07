#!/usr/bin/env python3
"""Measure two-phase LR-then-FB 5x5x5 center staging length."""

# standard libraries
import json
import logging
import re
import statistics
import time
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import RubiksCube555

COMMENT_RE = re.compile(r"COMMENT_.*\((\d+)_steps\)")


def main():
    logging.disable(logging.INFO)
    states = json.loads(Path("utils/10k-555-cubes.json").read_text())["5x5x5"][:100]
    rows = []
    for index, state in enumerate(states):
        started = time.perf_counter()
        cube = RubiksCube555(state, "URFDLB")
        cube.lt_init()
        cube.group_centers_phase1_and_2()
        wall = time.perf_counter() - started
        comments = [step for step in cube.solution if step.startswith("COMMENT")]
        staged = [int(COMMENT_RE.search(step).group(1)) for step in comments]
        moves = sum(staged)
        ok = cube.centers_staged()
        print(
            f"TWO_PHASE cube={index:03d} wall={wall:.3f} moves={moves} parts={staged} " f"{'ok' if ok else 'FAIL'}",
            flush=True,
        )
        if not ok:
            raise SystemExit(f"cube {index} did not stage centers")
        rows.append(moves)
    print(
        f"TWO_PHASE_SUMMARY solved={len(rows)}/{len(states)} "
        f"median_moves={statistics.median(rows)} mean_moves={statistics.mean(rows):.2f} "
        f"min_moves={min(rows)} max_moves={max(rows)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
