# standard libraries
import subprocess
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_777
from rubikscubennnsolver.RubiksCubeNNNOdd import RubiksCubeNNNOdd, solved_999

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_777_centers_stage"

# Same left/middle/right triplets as unpaired_oblique_count() in ida_search_777_centers_stage.c
# fmt: off
LEFT_OBLIQUES = (
    10, 30, 20, 40, 59, 79, 69, 89, 108, 128, 118, 138,
    157, 177, 167, 187, 206, 226, 216, 236, 255, 275, 265, 285,
)
MIDDLE_OBLIQUES = (
    11, 23, 27, 39, 60, 72, 76, 88, 109, 121, 125, 137,
    158, 170, 174, 186, 207, 219, 223, 235, 256, 268, 272, 284,
)
RIGHT_OBLIQUES = (
    12, 16, 34, 38, 61, 65, 83, 87, 110, 114, 132, 136,
    159, 163, 181, 185, 208, 212, 230, 234, 257, 261, 279, 283,
)
# fmt: on


def unpaired_lr_obliques(cube):
    unpaired = 16
    for left, middle, right in zip(LEFT_OBLIQUES, MIDDLE_OBLIQUES, RIGHT_OBLIQUES):
        if cube.state[middle] in ("L", "R"):
            if cube.state[left] in ("L", "R"):
                unpaired -= 1
            if cube.state[right] in ("L", "R"):
                unpaired -= 1
    return unpaired


class IdaSearch777CentersStageObliquesOnlyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not BINARY.exists():
            raise unittest.SkipTest(f"{BINARY} is not built")

    def test_usage_requires_ranked_table_or_obliques_only(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        result = subprocess.run(
            [str(BINARY), "--kociemba", cube.get_kociemba_string(True)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("usage:", result.stdout)

    def test_solved_cube_needs_no_moves(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        result = subprocess.run(
            [str(BINARY), "--kociemba", cube.get_kociemba_string(True), "--obliques-only"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
        self.assertEqual(line, "SOLUTION (0 steps):")

    def test_pairs_obliques_without_a_ranked_table(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.rotate("Uw")
        cube.rotate("3Rw")
        self.assertGreater(unpaired_lr_obliques(cube), 0)

        result = subprocess.run(
            [str(BINARY), "--kociemba", cube.get_kociemba_string(True), "--obliques-only"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
        steps = line.split(":", 1)[1].split()
        self.assertTrue(steps)
        for step in steps:
            cube.rotate(step)
        self.assertEqual(unpaired_lr_obliques(cube), 0)

    def test_odd_cube_adapter_uses_obliques_only_searcher(self):
        cube = RubiksCubeNNNOdd(solved_999, "URFDLB")
        fake_777 = cube.get_fake_777()
        fake_777.rotate("Uw")
        fake_777.rotate("3Rw")
        self.assertGreater(unpaired_lr_obliques(fake_777), 0)
        fake_777.lt_LR_oblique_edge_pairing.solve_via_c()
        self.assertEqual(unpaired_lr_obliques(fake_777), 0)
        self.assertIn("searching L/R obliques only, prune pairing regressions", fake_777.solve_via_c_output)
