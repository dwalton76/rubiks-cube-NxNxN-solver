"""Tests for the optional joint LR t+x table in ida_search_555_centers_stage.

Nibble files are written sparsely, so the tests set only the cells they read.
The walk test uses a depth-3 table from the lookup-tables builder when that
binary is present.
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
T_TABLE = ROOT / "lookup-tables" / "lookup-table-5x5x5-step10-t-centers-stage.cost-only.bin"
X_TABLE = ROOT / "lookup-tables" / "lookup-table-5x5x5-step10-x-centers-stage.cost-only.bin"
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


PARITY_BYTES = (JOINT_CELLS * 6 + 7) // 8 + 1


def write_parity_entries(path, entries):
    """Sparse 6-bit file: cell -> (depth + 1, flags), flags bit 0 even and bit 1 odd. Others read unseen."""
    with open(path, "wb") as table:
        table.truncate(PARITY_BYTES)
    with open(path, "r+b") as table:
        for cell, (value, flags) in entries.items():
            bit = cell * 6
            table.seek(bit // 8)
            word = int.from_bytes(table.read(2).ljust(2, b"\0"), "little")
            word &= ~(0x3F << (bit % 8))
            word |= (value | flags << 4) << (bit % 8)
            table.seek(bit // 8)
            table.write(word.to_bytes(2, "little"))


def fields(stdout):
    """Parse the T_RANK line and the JOINT_<axis> CELL/VALUE lines printed by --print-ranks."""
    rank = re.search(r"T_RANK \d+ T_COST (\d+) X_RANK \d+ X_COST (\d+) COST (\d+)", stdout)
    joint = {
        axis: tuple(int(v) for v in match.groups())
        for axis in AXES
        for match in [re.search(rf"JOINT_{axis} CELL (\d+) VALUE (\d+)", stdout)]
        if match
    }
    return rank, joint


@unittest.skipUnless(
    CENTERS.is_file() and T_TABLE.is_file() and X_TABLE.is_file(), "5x5 center tables or binary missing"
)
class LRJointSearcherTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        self.empty = self.directory / "empty.bin"
        write_nibbles(self.empty, {})

    def tearDown(self):
        self.tempdir.cleanup()

    def run_search(self, cube, *extra):
        return subprocess.run(
            [
                str(CENTERS),
                "--kociemba",
                cube.get_kociemba_string(True),
                "--t-center-cost",
                str(T_TABLE),
                "--x-center-cost",
                str(X_TABLE),
                "--threads",
                "1",
                "--print-ranks",
                *extra,
            ],
            capture_output=True,
            text=True,
        )

    def solution(self, result):
        return next((line for line in result.stdout.splitlines() if line.startswith("SOLUTION")), None)

    def test_empty_joint_table_keeps_the_optimal_solution(self):
        cube = RubiksCube555(solved_555, "URFDLB")
        for move in ("R", "Uw", "F2", "Lw'"):
            cube.rotate(move)
        baseline = self.run_search(cube)
        joint = self.run_search(cube, "--lr-joint-cost", str(self.empty))
        self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
        self.assertEqual(joint.returncode, 0, joint.stdout + joint.stderr)
        self.assertIsNotNone(self.solution(baseline))
        self.assertEqual(self.solution(joint), self.solution(baseline))

    def test_injected_root_value_is_read_and_raises_the_cost(self):
        cube = RubiksCube555(solved_555, "URFDLB")
        for move in ("R", "Uw", "F2", "Lw'"):
            cube.rotate(move)
        probe = self.run_search(cube, "--lr-joint-cost", str(self.empty), "--max-ida-threshold", "0")
        rank, joint = fields(probe.stdout)
        self.assertIsNotNone(rank)
        t_cost, x_cost, _ = (int(v) for v in rank.groups())
        cell = joint["L"][0]

        path = self.directory / "root.bin"
        write_nibbles(path, {cell: 3})
        result = self.run_search(cube, "--lr-joint-cost", str(path), "--max-ida-threshold", "0")
        rank, joint = fields(result.stdout)
        self.assertEqual(joint["L"], (cell, 3))
        self.assertEqual(int(rank.group(3)), max(t_cost, x_cost, 2))

    def test_joint_bound_above_the_threshold_prunes_the_root(self):
        cube = RubiksCube555(solved_555, "URFDLB")
        for move in ("R", "Uw", "F2", "Lw'"):
            cube.rotate(move)
        probe = self.run_search(cube, "--lr-joint-cost", str(self.empty), "--max-ida-threshold", "0")
        _, joint = fields(probe.stdout)
        path = self.directory / "prune.bin"
        write_nibbles(path, {joint["U"][0]: 15})
        result = self.run_search(cube, "--lr-joint-cost", str(path), "--max-ida-threshold", "5")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIsNone(self.solution(result))
        self.assertIn("no solution found", result.stderr)

    def test_wrong_size_file_is_rejected(self):
        short = self.directory / "short.bin"
        short.write_bytes(b"\0" * 100)
        cube = RubiksCube555(solved_555, "URFDLB")
        result = self.run_search(cube, "--lr-joint-cost", str(short))
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected", result.stderr)

    def test_table_choices_without_a_full_source_are_rejected(self):
        state = RubiksCube555(solved_555, "URFDLB").get_kociemba_string(True)
        for tables in (
            [],
            ["--t-center-cost", str(T_TABLE)],
            ["--x-center-cost", str(X_TABLE), "--lr-joint-cost", str(self.empty)],
        ):
            result = subprocess.run([str(CENTERS), "--kociemba", state, *tables], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, tables)


@unittest.skipUnless(
    CENTERS.is_file() and T_TABLE.is_file() and X_TABLE.is_file(), "5x5 center tables or binary missing"
)
class LRJointParitySearcherTest(unittest.TestCase):
    """--lr-joint-parity-cost reads 6-bit cells: depth + 1, plus a flag per parity the shortest path can have."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        self.cube = RubiksCube555(solved_555, "URFDLB")
        for move in ("R", "Uw", "F2", "Lw'"):
            self.cube.rotate(move)

    def tearDown(self):
        self.tempdir.cleanup()

    def run_search(self, table, *extra):
        return subprocess.run(
            [
                str(CENTERS),
                "--kociemba",
                self.cube.get_kociemba_string(True),
                "--t-center-cost",
                str(T_TABLE),
                "--x-center-cost",
                str(X_TABLE),
                "--lr-joint-parity-cost",
                str(table),
                "--threads",
                "1",
                "--print-ranks",
                *extra,
            ],
            capture_output=True,
            text=True,
        )

    def root_cell(self):
        empty = self.directory / "empty.bin"
        write_parity_entries(empty, {})
        probe = self.run_search(empty, "--max-ida-threshold", "0")
        _, joint = fields(probe.stdout)
        return joint["L"][0]

    def root_cost(self, flags, *extra):
        """Root heuristic with the L-axis cell set to depth 9 (bound 8) and the given parity flags."""
        path = self.directory / "root.bin"
        write_parity_entries(path, {self.root_cell(): (9, flags)})
        result = self.run_search(path, "--max-ida-threshold", "0", *extra)
        rank, _ = fields(result.stdout)
        self.assertIsNotNone(rank, result.stdout + result.stderr)
        self.assertIn("FLAGS", result.stdout)
        return int(rank.group(3))

    def test_missing_flag_for_the_needed_parity_adds_one(self):
        # The root needs an odd path under --orbit0-need-odd-w and an even one under --orbit0-need-even-w.
        self.assertEqual(self.root_cost(0b01, "--orbit0-need-odd-w"), 9)
        self.assertEqual(self.root_cost(0b01, "--orbit0-need-even-w"), 8)
        self.assertEqual(self.root_cost(0b10, "--orbit0-need-odd-w"), 8)
        self.assertEqual(self.root_cost(0b10, "--orbit0-need-even-w"), 9)

    def test_both_flags_or_no_parity_requirement_keep_the_plain_bound(self):
        for flags in (0b01, 0b10, 0b11):
            self.assertEqual(self.root_cost(flags), 8, flags)
        for requirement in ("--orbit0-need-odd-w", "--orbit0-need-even-w"):
            self.assertEqual(self.root_cost(0b11, requirement), 8, requirement)

    def test_an_empty_table_keeps_the_optimal_solution(self):
        empty = self.directory / "empty.bin"
        write_parity_entries(empty, {})
        for requirement in ("--orbit0-need-odd-w", "--orbit0-need-even-w"):
            baseline = subprocess.run(
                [
                    str(CENTERS),
                    "--kociemba",
                    self.cube.get_kociemba_string(True),
                    "--t-center-cost",
                    str(T_TABLE),
                    "--x-center-cost",
                    str(X_TABLE),
                    "--threads",
                    "1",
                    requirement,
                ],
                capture_output=True,
                text=True,
            )
            joint = self.run_search(empty, requirement)
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            self.assertEqual(joint.returncode, 0, joint.stdout + joint.stderr)
            solution = next(line for line in baseline.stdout.splitlines() if line.startswith("SOLUTION"))
            self.assertIn(solution, joint.stdout)

    def test_wrong_size_file_is_rejected(self):
        # The plain nibble size is not the parity size.
        wrong = self.directory / "nibble-size.bin"
        write_nibbles(wrong, {})
        result = self.run_search(wrong)
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected", result.stderr)

    def test_two_joint_tables_are_rejected(self):
        empty = self.directory / "empty.bin"
        write_parity_entries(empty, {})
        result = self.run_search(empty, "--lr-joint-cost", str(empty))
        self.assertEqual(result.returncode, 2)


@unittest.skipUnless(
    CENTERS.is_file() and T_TABLE.is_file() and X_TABLE.is_file() and BUILDER.is_file(),
    "5x5 center tables or the joint table builder missing",
)
class LRJointParityWalkTest(unittest.TestCase):
    """A depth-3 parity table must never lengthen a solution, with or without a parity requirement.

    The t/x tables stay loaded: an unseen cell of a partial table reads as no bound, so on its own
    it would accept a far state as solved.
    """

    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.table = Path(cls.tempdir.name) / "parity-depth3.bin"
        built = subprocess.run(
            [str(BUILDER), "--parity", "--output", str(cls.table), "--max-depth", "3", "--threads", "4"],
            capture_output=True,
            text=True,
        )
        assert built.returncode == 0, built.stdout + built.stderr

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def length(self, cube, tables, *extra):
        completed = subprocess.run(
            [str(CENTERS), "--kociemba", cube.get_kociemba_string(True), "--threads", "1", *tables, *extra],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return int(re.search(r"SOLUTION \((\d+) steps\)", completed.stdout).group(1))

    def test_solution_lengths_match_the_t_x_tables(self):
        rng = random.Random(21)
        t_x = ["--t-center-cost", str(T_TABLE), "--x-center-cost", str(X_TABLE)]
        parity = [*t_x, "--lr-joint-parity-cost", str(self.table)]
        for walk in range(6):
            cube = RubiksCube555(solved_555, "URFDLB")
            for _ in range(4):
                cube.rotate(rng.choice(moves_555))
            for requirement in ((), ("--orbit0-need-odd-w",), ("--orbit0-need-even-w",)):
                self.assertEqual(
                    self.length(cube, parity, *requirement), self.length(cube, t_x, *requirement), (walk, requirement)
                )


@unittest.skipUnless(
    CENTERS.is_file() and T_TABLE.is_file() and X_TABLE.is_file() and BUILDER.is_file(),
    "5x5 center tables or the joint table builder missing",
)
class LRJointWalkTest(unittest.TestCase):
    """A depth-3 table from the builder must give 1 <= value <= k + 1 after a k-move walk from solved.

    Every axis starts at distance 0, so the values bound the walk length.
    """

    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.table = Path(cls.tempdir.name) / "joint-depth3.bin"
        built = subprocess.run(
            [str(BUILDER), "--output", str(cls.table), "--max-depth", "3", "--threads", "4"],
            capture_output=True,
            text=True,
        )
        assert built.returncode == 0, built.stdout + built.stderr

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def read_axes(self, cube):
        completed = subprocess.run(
            [
                str(CENTERS),
                "--kociemba",
                cube.get_kociemba_string(True),
                "--t-center-cost",
                str(T_TABLE),
                "--x-center-cost",
                str(X_TABLE),
                "--lr-joint-cost",
                str(self.table),
                "--max-ida-threshold",
                "0",
                "--print-ranks",
            ],
            capture_output=True,
            text=True,
        )
        _, joint = fields(completed.stdout)
        self.assertEqual(set(joint), set(AXES), completed.stdout)
        return {axis: joint[axis][1] for axis in AXES}

    def test_solved_cube_reads_value_one_on_every_axis(self):
        values = self.read_axes(RubiksCube555(solved_555, "URFDLB"))
        self.assertEqual(values, {"L": 1, "U": 1, "F": 1})

    def test_walk_values_bound_the_walk_length(self):
        rng = random.Random(555)
        for walk in range(12):
            cube = RubiksCube555(solved_555, "URFDLB")
            length = 1 + walk % 3
            for _ in range(length):
                cube.rotate(rng.choice(moves_555))
            for axis, value in self.read_axes(cube).items():
                self.assertGreaterEqual(value, 1, (walk, axis))
                self.assertLessEqual(value, length + 1, (walk, axis))

    def solve(self, cube, tables):
        completed = subprocess.run(
            [str(CENTERS), "--kociemba", cube.get_kociemba_string(True), "--threads", "1", "--print-ranks", *tables],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        rank, _ = fields(completed.stdout)
        length = re.search(r"SOLUTION \((\d+) steps\)", completed.stdout)
        self.assertIsNotNone(length, completed.stdout)
        return int(rank.group(3)), int(length.group(1))

    def test_joint_only_matches_the_t_x_solution_length(self):
        joint_only = ["--lr-joint-cost", str(self.table)]
        self.assertEqual(self.solve(RubiksCube555(solved_555, "URFDLB"), joint_only), (0, 0))
        rng = random.Random(13)
        for walk in range(4):
            cube = RubiksCube555(solved_555, "URFDLB")
            for _ in range(3):
                cube.rotate(rng.choice(moves_555))
            _, expected = self.solve(cube, ["--t-center-cost", str(T_TABLE), "--x-center-cost", str(X_TABLE)])
            cost, length = self.solve(cube, joint_only)
            self.assertEqual(length, expected, walk)
            self.assertLessEqual(cost, length, walk)


if __name__ == "__main__":
    unittest.main()
