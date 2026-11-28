"""Tests for the joint LR t+x table in ida_search_555_centers_stage.

Nibble files are written sparsely, so the tests set only the cells they read. An unseen cell gives
no bound, so an empty table is a blind but still optimal search. The walk tests use a depth-3 table
from the lookup-tables builder when that binary is present.
"""

# standard libraries
import os
import random
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, moves_555, solved_555

ROOT = Path(__file__).resolve().parents[1]
CENTERS = Path(os.environ.get("CENTERS_STAGE_BINARY", ROOT / "ida_search_555_centers_stage"))
BUILDER = ROOT.parent / "rubiks-cube-lookup-tables" / "rubikscubelookuptables" / "build-555-lr-joint"
JOINT_CELLS = 46935 * 735471
JOINT_BYTES = (JOINT_CELLS + 1) // 2
AXES = ("L", "U", "F")


def write_nibbles(path, values):
    """Sparse nibble file: depth + 1 per cell, unset cells read as unseen (0)."""
    with open(path, "wb") as table:
        table.truncate(JOINT_BYTES)
    with open(path, "r+b") as table:
        for cell, value in values.items():
            table.seek(cell // 2)
            current = table.read(1)
            byte = current[0] if current else 0
            if cell & 1:
                byte = (byte & 0x0F) | (value << 4)
            else:
                byte = (byte & 0xF0) | value
            table.seek(cell // 2)
            table.write(bytes((byte,)))


def fields(stdout):
    """Parse the COST line and the JOINT_<axis> CELL/VALUE lines printed by --print-ranks."""
    cost = re.search(r"^COST (\d+)$", stdout, re.MULTILINE)
    joint = {
        axis: tuple(int(v) for v in match.groups())
        for axis in AXES
        for match in [re.search(rf"JOINT_{axis} CELL (\d+) VALUE (\d+)", stdout)]
        if match
    }
    return (int(cost.group(1)) if cost else None), joint


def solution_length(stdout):
    match = re.search(r"SOLUTION \((\d+) steps\)", stdout)
    return int(match.group(1)) if match else None


def scrambled(*moves):
    cube = RubiksCube555(solved_555, "URFDLB")
    for move in moves:
        cube.rotate(move)
    return cube


@unittest.skipUnless(CENTERS.is_file(), "ida_search_555_centers_stage was not built")
class LRJointSearcherTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        self.empty = self.directory / "empty.bin"
        write_nibbles(self.empty, {})

    def tearDown(self):
        self.tempdir.cleanup()

    def run_search(self, cube, table, *extra):
        return subprocess.run(
            [
                str(CENTERS),
                "--kociemba",
                cube.get_kociemba_string(True),
                "--lr-joint-cost",
                str(table),
                "--threads",
                "1",
                "--print-ranks",
                *extra,
            ],
            capture_output=True,
            text=True,
        )

    def test_empty_table_stages_a_short_scramble(self):
        cube = scrambled("Uw", "R")
        result = self.run_search(cube, self.empty)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(fields(result.stdout)[0], 1)
        solution = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
        for move in solution.split(":", 1)[1].split():
            cube.rotate(move)
        self.assertTrue(cube.centers_staged())

    def test_injected_root_value_is_read_and_raises_the_cost(self):
        cube = scrambled("R", "Uw", "F2", "Lw'")
        _, joint = fields(self.run_search(cube, self.empty, "--max-ida-threshold", "0").stdout)
        cell = joint["L"][0]

        path = self.directory / "root.bin"
        write_nibbles(path, {cell: 3})
        cost, joint = fields(self.run_search(cube, path, "--max-ida-threshold", "0").stdout)
        self.assertEqual(joint["L"], (cell, 3))
        self.assertEqual(cost, 2)

    def test_joint_bound_above_the_threshold_prunes_the_root(self):
        cube = scrambled("R", "Uw", "F2", "Lw'")
        _, joint = fields(self.run_search(cube, self.empty, "--max-ida-threshold", "0").stdout)
        path = self.directory / "prune.bin"
        write_nibbles(path, {joint["U"][0]: 15})
        result = self.run_search(cube, path, "--max-ida-threshold", "5")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIsNone(solution_length(result.stdout))
        self.assertIn("no solution found", result.stderr)

    def test_wrong_size_file_is_rejected(self):
        short = self.directory / "short.bin"
        short.write_bytes(b"\0" * 100)
        result = self.run_search(scrambled(), short)
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected", result.stderr)

    def test_missing_joint_table_is_rejected(self):
        state = scrambled().get_kociemba_string(True)
        result = subprocess.run([str(CENTERS), "--kociemba", state], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


@unittest.skipUnless(CENTERS.is_file() and BUILDER.is_file(), "ida_search_555_centers_stage or the builder missing")
class LRJointWalkTest(unittest.TestCase):
    """A depth-3 table from the builder must give 1 <= value <= k + 1 after a k-move walk from solved.

    Every axis starts at distance 0, so the values bound the walk length.
    """

    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.table = Path(cls.tempdir.name) / "joint-depth3.bin"
        cls.empty = Path(cls.tempdir.name) / "empty.bin"
        write_nibbles(cls.empty, {})
        built = subprocess.run(
            [str(BUILDER), "--output", str(cls.table), "--max-depth", "3", "--threads", "4"],
            capture_output=True,
            text=True,
        )
        assert built.returncode == 0, built.stdout + built.stderr

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def run_search(self, cube, table, *extra):
        completed = subprocess.run(
            [
                str(CENTERS),
                "--kociemba",
                cube.get_kociemba_string(True),
                "--lr-joint-cost",
                str(table),
                "--threads",
                "1",
                "--print-ranks",
                *extra,
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return completed.stdout

    def read_axes(self, cube):
        _, joint = fields(self.run_search(cube, self.table))
        self.assertEqual(set(joint), set(AXES))
        return {axis: joint[axis][1] for axis in AXES}

    def test_solved_cube_reads_value_one_on_every_axis(self):
        self.assertEqual(self.read_axes(scrambled()), {"L": 1, "U": 1, "F": 1})

    def test_walk_values_bound_the_walk_length(self):
        rng = random.Random(555)
        for walk in range(12):
            length = 1 + walk % 3
            cube = scrambled(*(rng.choice(moves_555) for _ in range(length)))
            for axis, value in self.read_axes(cube).items():
                self.assertGreaterEqual(value, 1, (walk, axis))
                self.assertLessEqual(value, length + 1, (walk, axis))

    def test_solution_lengths_match_the_blind_search(self):
        self.assertEqual(solution_length(self.run_search(scrambled(), self.table)), 0)
        rng = random.Random(13)
        for walk in range(6):
            moves = [rng.choice(moves_555) for _ in range(3)]
            cube = scrambled(*moves)
            # Ask for the walk's own parity: the other one can need a much longer blind search.
            odd = sum("w" in move and not move.endswith("2") for move in moves) % 2
            for requirement in ((), (f"--orbit0-need-{'odd' if odd else 'even'}-w",)):
                stdout = self.run_search(cube, self.table, *requirement)
                cost, _ = fields(stdout)
                length = solution_length(stdout)
                self.assertEqual(length, solution_length(self.run_search(cube, self.empty, *requirement)), walk)
                self.assertLessEqual(cost, length, walk)


if __name__ == "__main__":
    unittest.main()
