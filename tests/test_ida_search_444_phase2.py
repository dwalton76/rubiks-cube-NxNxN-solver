# standard libraries
import subprocess
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube444 import PHASE2_CENTERS_TABLE_444, RubiksCube444, solved_444

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_444_phase2"
EDGE_TABLE = ROOT / "lookup-tables" / "lookup-table-4x4x4-step33-all-edges-paired.cost-only.bin"
CENTER_TABLE = ROOT / PHASE2_CENTERS_TABLE_444
PLACEHOLDER = "/dev/null"


@unittest.skipUnless(BINARY.is_file(), "ida_search_444_phase2 has not been built")
class Phase2Search444Test(unittest.TestCase):
    def setUp(self):
        self.cube = RubiksCube444(solved_444, "URFDLB")

    def command(self, *extra, edge=PLACEHOLDER, centers=PLACEHOLDER):
        return [
            str(BINARY),
            "--kociemba",
            self.cube.get_kociemba_string(True),
            "--edge-pairing-cost",
            str(edge),
            "--center-cost",
            str(centers),
            *extra,
        ]

    def test_missing_tables_print_usage(self):
        result = subprocess.run(
            [str(BINARY), "--kociemba", self.cube.get_kociemba_string(True)], capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)

    def test_invalid_argument_is_rejected(self):
        result = subprocess.run(self.command("--ud-cost", PLACEHOLDER), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid argument --ud-cost", result.stderr)

    @unittest.skipUnless(EDGE_TABLE.is_file() and CENTER_TABLE.is_file(), "phase 2 tables are not present")
    def test_solved_cube_is_a_zero_move_goal(self):
        result = subprocess.run(
            self.command(
                "--max-ida-threshold",
                "0",
                edge=EDGE_TABLE,
                centers=CENTER_TABLE,
            ),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION (0 steps)", result.stdout)

    @unittest.skipUnless(EDGE_TABLE.is_file() and CENTER_TABLE.is_file(), "phase 2 tables are not present")
    def test_print_rank_on_solved_cube(self):
        result = subprocess.run(
            self.command("--print-rank", "--max-ida-threshold", "0", edge=EDGE_TABLE, centers=CENTER_TABLE),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EDGE_PAIRING_RANK 0", result.stdout)
        self.assertIn("CENTER_EXACT_COST 0", result.stdout)
        self.assertIn("HEURISTIC 0", result.stdout)

    @unittest.skipUnless(EDGE_TABLE.is_file() and CENTER_TABLE.is_file(), "phase 2 tables are not present")
    def test_avoid_pll_returns_first_pll_free_reduction(self):
        cube = RubiksCube444(
            "DLLUUUUULUURUDDBDFFRLLLDURRBLLBLFBRRFBBDFFFRLUFBFLDDFDDFDDDUFDUU" "FRBLLRRRBLLURBLDBBDRFFFURBBRBBRU",
            "URFDLB",
        )
        result = subprocess.run(
            [
                str(BINARY),
                "--kociemba",
                cube.get_kociemba_string(True),
                "--edge-pairing-cost",
                str(EDGE_TABLE),
                "--center-cost",
                str(CENTER_TABLE),
                "--avoid-pll",
                "--max-ida-threshold",
                "20",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        solution_line = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
        for step in solution_line.split(":", 1)[1].split():
            cube.rotate(step)
        self.assertTrue(cube.reduced_to_333())
        self.assertFalse(cube.edge_solution_leads_to_pll_parity())


if __name__ == "__main__":
    unittest.main()
