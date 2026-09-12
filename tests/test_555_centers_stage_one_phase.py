import math
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from rubikscubennnsolver.RubiksCube555 import (
    LookupTableIDA555CentersStageOnePhase,
    RubiksCube555,
    solved_555,
)

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_555_centers_stage"
RANK_UNIVERSE = 9_465_511_770
X_SQUARES = (
    7,
    9,
    17,
    19,
    32,
    34,
    42,
    44,
    57,
    59,
    67,
    69,
    82,
    84,
    92,
    94,
    107,
    109,
    117,
    119,
    132,
    134,
    142,
    144,
)
T_SQUARES = (
    8,
    12,
    14,
    18,
    33,
    37,
    39,
    43,
    58,
    62,
    64,
    68,
    83,
    87,
    89,
    93,
    108,
    112,
    114,
    118,
    133,
    137,
    139,
    143,
)


def staged_color(color):
    if color in ("U", "D"):
        return "U"
    if color in ("L", "R"):
        return "L"
    return "F"


def multiset_perms(counts):
    result = 1
    remaining = sum(counts)
    for count in counts:
        result *= math.comb(remaining, count)
        remaining -= count
    return result


def multiset_rank(state):
    symbols = "FLU"
    counts = [state.count(symbol) for symbol in symbols]
    rank = 0
    for char in state:
        selected = symbols.index(char)
        for index in range(selected):
            if counts[index]:
                counts[index] -= 1
                rank += multiset_perms(counts)
                counts[index] += 1
        counts[selected] -= 1
    return rank


def projected_rank(cube, squares):
    return multiset_rank("".join(staged_color(cube.state[index]) for index in squares))


def make_sparse_cost_table(path, entries):
    with path.open("wb") as table:
        table.truncate(RANK_UNIVERSE)
        for rank, encoded_cost in entries.items():
            table.seek(rank)
            table.write(bytes((encoded_cost,)))


class OnePhaseCenterStageTest(unittest.TestCase):
    def test_option_is_on_by_default(self):
        self.assertTrue(RubiksCube555(solved_555, "URFDLB").use_one_phase_centers_stage)
        self.assertFalse(
            RubiksCube555(
                solved_555,
                "URFDLB",
                use_one_phase_centers_stage=False,
            ).use_one_phase_centers_stage
        )

    def test_kociemba_state_masks_non_centers(self):
        cube = RubiksCube555(solved_555, "URFDLB")
        cube.rotate("Uw")
        state = LookupTableIDA555CentersStageOnePhase(cube).center_only_kociemba_string()
        center_indexes = {6, 7, 8, 11, 12, 13, 16, 17, 18}

        self.assertEqual(len(state), 150)
        self.assertEqual(state.count("."), 96)
        for index, value in enumerate(state):
            self.assertEqual(value == ".", index % 25 not in center_indexes)

    def test_c_ranked_costs_and_one_move_solution(self):
        if not BINARY.exists():
            self.skipTest("ida_search_555_centers_stage has not been compiled")

        solved = RubiksCube555(solved_555, "URFDLB")
        scrambled = RubiksCube555(solved_555, "URFDLB")
        scrambled.rotate("Uw")
        solved_x = projected_rank(solved, X_SQUARES)
        solved_t = projected_rank(solved, T_SQUARES)
        scrambled_x = projected_rank(scrambled, X_SQUARES)
        scrambled_t = projected_rank(scrambled, T_SQUARES)

        with tempfile.TemporaryDirectory() as directory:
            x_cost = Path(directory) / "x.bin"
            t_cost = Path(directory) / "t.bin"
            make_sparse_cost_table(x_cost, {solved_x: 1, scrambled_x: 2})
            make_sparse_cost_table(t_cost, {solved_t: 1, scrambled_t: 2})
            projected = LookupTableIDA555CentersStageOnePhase(scrambled).center_only_kociemba_string()
            command = [
                str(BINARY),
                "--kociemba",
                projected,
                "--x-cost",
                str(x_cost),
                "--t-cost",
                str(t_cost),
                "--multiplier",
                "1.0",
                "--max-ida-threshold",
                "1",
                "--threads",
                "1",
                "--print-ranks",
            ]
            ranks = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(ranks.returncode, 0, ranks.stdout + ranks.stderr)
            match = re.search(r"X_RANK (\d+) T_RANK (\d+) COST (\d+)", ranks.stdout)
            self.assertEqual(
                tuple(map(int, match.groups())),
                (scrambled_x, scrambled_t, 1),
            )

            command.remove("--print-ranks")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            solution = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
            for move in solution.split(":", 1)[1].split():
                scrambled.rotate(move)
            self.assertTrue(scrambled.centers_staged())

            wrapped = RubiksCube555(solved_555, "URFDLB")
            wrapped.rotate("Uw")
            wrapped.lt_x_centers_stage_one_phase = SimpleNamespace(filename=str(x_cost))
            wrapped.lt_t_centers_stage_one_phase = SimpleNamespace(filename=str(t_cost))
            search = LookupTableIDA555CentersStageOnePhase(wrapped, multiplier=1.0)
            old_cwd = os.getcwd()
            try:
                os.chdir(ROOT)
                search.solve_via_c(max_ida_threshold=1)
            finally:
                os.chdir(old_cwd)
            self.assertTrue(wrapped.centers_staged())


if __name__ == "__main__":
    unittest.main()
