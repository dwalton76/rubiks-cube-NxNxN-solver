import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "utils" / "update-move-count-table.py"


def load_module():
    spec = importlib.util.spec_from_file_location("update_move_count_table", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateMoveCountTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_cli_always_updates_repo_readme(self):
        with patch("sys.argv", ["update-move-count-table.py"]):
            args = self.mod.parse_args()
        self.assertFalse(hasattr(args, "update_readme"))
        self.assertFalse(hasattr(args, "readme"))
        self.assertEqual(self.mod.README, ROOT / "README.md")

    def test_previous_row_matches_readme_top_counts(self):
        previous = self.mod.previous_row_counts(ROOT / "README.md")
        self.assertEqual(previous["4x4x4"], 51.6)
        self.assertEqual(previous["5x5x5"], 78.9)

    def test_sanity_check_rejects_scramble_length_averages(self):
        with self.assertRaisesRegex(RuntimeError, "scramble"):
            self.mod.sanity_check_average("4x4x4", 1000.0, 51.6)
        self.mod.sanity_check_average("4x4x4", 48.0, 51.6)
        self.mod.sanity_check_average("5x5x5", 80.0, 78.9)

    def test_update_readme_inserts_below_separator(self):
        source = (ROOT / "README.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text(source, encoding="utf-8")
            row = "| 01/01/2099 | [deadbeef](https://example.test) | 1 | 2 | 3 | 4 | 5 | 6 | 7 |"
            self.mod.update_readme(readme, row)
            lines = readme.read_text(encoding="utf-8").splitlines()
            header = next(index for index, line in enumerate(lines) if line.startswith("| Date |"))
            self.assertEqual(lines[header + 2], row)

    def test_discard_scramble_drops_randomize_steps(self):
        cube_class, solved = self.mod.CUBE_CLASSES["4x4x4"]
        cube = cube_class(solved, "URFDLB")
        cube.randomize()
        self.assertGreater(len(cube.solution), 100)
        self.mod.discard_scramble(cube)
        self.assertEqual(cube.solution, [])
        self.assertNotEqual("".join(cube.state), solved)

    def test_solve_length_counts_a_solution_that_solves_the_cube(self):
        cube_class, solved = self.mod.CUBE_CLASSES["4x4x4"]
        cube = cube_class(solved, "URFDLB")
        cube.enable_print_cube = False
        cube.randomize()
        self.mod.discard_scramble(cube)
        scrambled = cube.state[:]

        length = self.mod.solve_length(cube)
        solution = cube.solution[:]

        replay = cube_class(solved, "URFDLB")
        replay.state = scrambled[:]
        for step in solution:
            replay.rotate(step)
        self.assertTrue(replay.solved())
        self.assertEqual(length, replay.get_solution_len_minus_rotates(solution))

    def test_4x4_and_5x5_solve_counts_are_near_the_readme(self):
        previous = self.mod.previous_row_counts(ROOT / "README.md")
        for size in ("4x4x4", "5x5x5"):
            lengths = self.mod.measure_size(size, 1)
            self.assertEqual(len(lengths), 1)
            self.mod.sanity_check_average(size, lengths[0], previous[size])
