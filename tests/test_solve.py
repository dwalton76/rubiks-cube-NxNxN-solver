# standard libraries
import json
import os
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube222 import RubiksCube222, solved_222
from rubikscubennnsolver.RubiksCube333 import RubiksCube333, solved_333
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_666
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_777
from rubikscubennnsolver.RubiksCubeNNNEven import RubiksCubeNNNEven, solved_888, solved_101010
from rubikscubennnsolver.RubiksCubeNNNOdd import RubiksCubeNNNOdd, solved_999

ROOT = Path(__file__).resolve().parents[1]
TEST_CUBES = ROOT / "utils" / "test-cubes.json"
ORDER = "URFDLB"

CUBE_CLASSES = {
    "2x2x2": (RubiksCube222, solved_222),
    "3x3x3": (RubiksCube333, solved_333),
    "4x4x4": (RubiksCube444, solved_444),
    "5x5x5": (RubiksCube555, solved_555),
    "6x6x6": (RubiksCube666, solved_666),
    "7x7x7": (RubiksCube777, solved_777),
    "8x8x8": (RubiksCubeNNNEven, solved_888),
    "9x9x9": (RubiksCubeNNNOdd, solved_999),
    "10x10x10": (RubiksCubeNNNEven, solved_101010),
}


class SolveCubeTest(unittest.TestCase):
    """Solve one scramble of each size from utils/test-cubes.json."""

    @classmethod
    def setUpClass(cls):
        cls._orig_cwd = os.getcwd()
        os.chdir(ROOT)
        with open(TEST_CUBES) as fh:
            cls.test_cases = json.load(fh)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._orig_cwd)

    def _solve(self, size: str) -> None:
        cube_class, solved_state = CUBE_CLASSES[size]
        scramble = self.test_cases[size][0]
        cube = cube_class(solved_state, ORDER)
        cube.enable_print_cube = False
        cube.load_state(scramble, ORDER)
        cube.solve()
        self.assertTrue(cube.solved(), f"{size} was not solved: {scramble}")

    def test_solve_2x2x2(self):
        self._solve("2x2x2")

    def test_solve_3x3x3(self):
        self._solve("3x3x3")

    def test_solve_4x4x4(self):
        self._solve("4x4x4")

    def test_solve_5x5x5(self):
        self._solve("5x5x5")

    def test_solve_6x6x6(self):
        self._solve("6x6x6")

    def test_solve_7x7x7(self):
        self._solve("7x7x7")

    def test_solve_8x8x8(self):
        self._solve("8x8x8")

    def test_solve_9x9x9(self):
        self._solve("9x9x9")

    def test_solve_10x10x10(self):
        self._solve("10x10x10")


class RandomizeTest(unittest.TestCase):
    def test_randomize_does_not_emit_half_turn_primes(self):
        cube = RubiksCube444(solved_444, ORDER)
        cube.randomize(count=500)
        illegal = [step for step in cube.solution if step.endswith("2'")]
        self.assertEqual(illegal, [])
        cube.compress_solution()


if __name__ == "__main__":
    unittest.main()
