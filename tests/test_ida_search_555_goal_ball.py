"""Tests for the optional goal ball (--goal-ball) in ida_search_555_centers_stage.

A ball file is a hash of canonical states, so the tests build shallow ones
with the lookup-tables builder and skip when that binary is absent. At
threshold T the search must never go past depth T - ball depth, which the
"max depth" field of each threshold log line shows.
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
JOINT_TABLE = ROOT / "lookup-tables" / "lookup-table-5x5x5-step13-LR-t-x-centers-joint.sym-nibble.bin"
BALL_8 = ROOT / "lookup-tables" / "lookup-table-5x5x5-phase1-centers-goal-ball.sym-depth8.hash.bin"
BUILDER = ROOT.parent / "rubiks-cube-lookup-tables" / "rubikscubelookuptables" / "build-555-goal-ball"
BALL_DEPTH = 4
# Phase 1 takes 16 moves for this cube.
SIXTEEN_MOVE_CUBE = (
    "LLFBRBFUDULBULBBDDUBBBBLDFDULDLURFBDFRLDUFDBRLDUFBLURFRFRDRBULFBLLLBURUFRFURDDLBULLLRLRDFRDRBBRUDFDUFRBUDULF"
    "DUFULDFRBRBULLUFFBLRDDDDFRRBUBRLBUUFFRRDFF"
)
REQUIREMENTS = ((), ("--orbit0-need-odd-w",), ("--orbit0-need-even-w",))


def search(kociemba, *arguments):
    return subprocess.run([str(CENTERS), "--kociemba", kociemba, *arguments], capture_output=True, text=True)


def solution_length(completed):
    match = re.search(r"SOLUTION \((\d+) steps\)", completed.stdout)
    return int(match.group(1)) if match else None


def threshold_depths(completed):
    """(threshold, max depth) for each IDA threshold log line."""
    return [
        (int(threshold), int(depth))
        for threshold, depth in re.findall(
            r"IDA threshold (\d+), .* max depth (\d+)", completed.stdout + completed.stderr
        )
    ]


@unittest.skipUnless(
    CENTERS.is_file() and T_TABLE.is_file() and X_TABLE.is_file() and BUILDER.is_file(),
    "5x5 center tables, the binary, or the goal ball builder missing",
)
class GoalBallSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.ball = Path(cls.tempdir.name) / "ball.bin"
        built = subprocess.run(
            [str(BUILDER), "--output", str(cls.ball), "--max-depth", str(BALL_DEPTH), "--slots-log2", "17"],
            capture_output=True,
            text=True,
        )
        assert built.returncode == 0, built.stdout + built.stderr

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def t_x(self):
        return ["--t-center-cost", str(T_TABLE), "--x-center-cost", str(X_TABLE)]

    def test_solved_cube_is_in_the_ball_at_zero(self):
        cube = RubiksCube555(solved_555, "URFDLB")
        completed = search(cube.get_kociemba_string(True), *self.t_x(), "--goal-ball", str(self.ball), "--print-ranks")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("BALL EVEN 0 ODD ", completed.stdout)
        self.assertEqual(solution_length(completed), 0)

    def test_lengths_match_the_t_x_tables_and_stay_inside_the_horizon(self):
        rng = random.Random(8)
        for walk in range(6):
            cube = RubiksCube555(solved_555, "URFDLB")
            for _ in range(6 + walk % 3):
                cube.rotate(rng.choice(moves_555))
            kociemba = cube.get_kociemba_string(True)
            for requirement in REQUIREMENTS:
                expected = search(kociemba, *self.t_x(), "--threads", "2", *requirement)
                ball = search(kociemba, *self.t_x(), "--threads", "2", "--goal-ball", str(self.ball), *requirement)
                self.assertEqual(ball.returncode, 0, ball.stdout + ball.stderr)
                self.assertEqual(solution_length(ball), solution_length(expected), (walk, requirement))
                depths = threshold_depths(ball)
                self.assertTrue(depths, ball.stderr)
                for threshold, depth in depths:
                    self.assertLessEqual(depth, max(threshold - BALL_DEPTH, 0), (walk, requirement, threshold))


@unittest.skipUnless(
    CENTERS.is_file() and JOINT_TABLE.is_file() and BALL_8.is_file(), "joint LR table or depth-8 goal ball missing"
)
class GoalBallSixteenMoveTest(unittest.TestCase):
    def test_sixteen_move_cube_never_goes_past_depth_eight(self):
        completed = search(
            SIXTEEN_MOVE_CUBE,
            "--lr-joint-cost",
            str(JOINT_TABLE),
            "--goal-ball",
            str(BALL_8),
            "--orbit0-need-even-w",
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(solution_length(completed), 16)
        self.assertEqual(max(depth for _, depth in threshold_depths(completed)), 8)


if __name__ == "__main__":
    unittest.main()
