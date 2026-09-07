import subprocess
import tempfile
import unittest
from pathlib import Path

from rubikscubennnsolver.RubiksCube666 import DAISY_INNER_X_SPINE_TABLES_666, RubiksCube666, solved_666

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_666_daisy_centers"
TABLE_UNIVERSE = 70**5


SOLVED_SPINE_RANKS = (1_657_032_999, 1_657_028_100, 1_657_032_999)


def make_sparse_solved_table(path, solved_rank):
    with open(path, "wb") as table:
        table.truncate(TABLE_UNIVERSE)
        table.seek(solved_rank)
        table.write(b"\x01")


@unittest.skipUnless(BINARY.is_file(), "ida_search_666_daisy_centers has not been built")
class DaisyCenters666InnerXSpineTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.paths = []
        for (_, filename), solved_rank in zip(DAISY_INNER_X_SPINE_TABLES_666, SOLVED_SPINE_RANKS):
            path = Path(self.tempdir.name) / Path(filename).name
            make_sparse_solved_table(path, solved_rank)
            self.paths.append(path)
        self.cube = RubiksCube666(solved_666, "URFDLB")

    def tearDown(self):
        self.tempdir.cleanup()

    def command(self, table_count=3):
        command = [
            str(BINARY),
            "--kociemba",
            self.cube.get_kociemba_string(True),
        ]
        for (flag, _), path in zip(DAISY_INNER_X_SPINE_TABLES_666[:table_count], self.paths):
            command.extend((flag, str(path)))
        return command

    def test_solved_cube_has_zero_cost_with_three_spine_tables(self):
        result = subprocess.run(self.command() + ["--print-ranks"], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ALL_INNER_X_PLUS_UD_OBLIQUES_RANK 1657032999", result.stdout)
        self.assertIn("ALL_INNER_X_PLUS_LR_OBLIQUES_RANK 1657028100", result.stdout)
        self.assertIn("ALL_INNER_X_PLUS_FB_OBLIQUES_RANK 1657032999", result.stdout)
        self.assertIn("COST 0 DAISY 1", result.stdout)

    def test_partial_spine_table_set_is_rejected(self):
        result = subprocess.run(self.command(table_count=2), capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
