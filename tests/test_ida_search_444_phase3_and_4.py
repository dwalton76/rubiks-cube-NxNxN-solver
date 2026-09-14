# standard libraries
import subprocess
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_444_phase3_and_4"
EDGE_TABLE = ROOT / "lookup-tables" / "lookup-table-4x4x4-step33-all-edges-paired.cost-only.bin"
CENTER_GRAPH = ROOT / "lookup-tables" / "lookup-table-4x4x4-step31-centers.bin"
CENTER_SOLVED_STATE = 69
PLACEHOLDER = "/dev/null"


@unittest.skipUnless(BINARY.is_file(), "ida_search_444_phase3_and_4 has not been built")
class Phase34Search444Test(unittest.TestCase):
    def setUp(self):
        self.cube = RubiksCube444(solved_444, "URFDLB")

    def command(self, *extra, edge=PLACEHOLDER, graph=PLACEHOLDER, center_state=CENTER_SOLVED_STATE):
        return [
            str(BINARY),
            "--kociemba",
            self.cube.get_kociemba_string(True),
            "--edge-pairing-cost",
            str(edge),
            "--center-graph",
            str(graph),
            "--center-state-index",
            str(center_state),
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

    def test_center_state_index_must_be_in_range(self):
        result = subprocess.run(self.command(center_state=840), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)

    @unittest.skipUnless(EDGE_TABLE.is_file() and CENTER_GRAPH.is_file(), "phase 3+4 tables are not present")
    def test_solved_cube_is_a_zero_move_goal(self):
        result = subprocess.run(
            self.command(
                "--max-ida-threshold",
                "0",
                edge=EDGE_TABLE,
                graph=CENTER_GRAPH,
            ),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION (0 steps)", result.stdout)

    @unittest.skipUnless(EDGE_TABLE.is_file() and CENTER_GRAPH.is_file(), "phase 3+4 tables are not present")
    def test_print_rank_on_solved_cube(self):
        result = subprocess.run(
            self.command("--print-rank", "--max-ida-threshold", "0", edge=EDGE_TABLE, graph=CENTER_GRAPH),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EDGE_PAIRING_RANK 0", result.stdout)
        self.assertIn("CENTER_COST 0", result.stdout)
        self.assertIn("CENTER_EXACT_COST 0", result.stdout)
        self.assertIn("HEURISTIC 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
