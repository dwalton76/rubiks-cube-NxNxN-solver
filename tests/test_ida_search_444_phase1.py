# standard libraries
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube444 import PHASE1_HIGHLOW_TARGET_444, RubiksCube444, solved_444

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_444_phase1"
ALL_CENTER = ROOT / "lookup-tables" / "lookup-table-4x4x4-step12-all-centers-stage-symmetry.cost-only.bin"
ALL_CENTER_INDEX = Path(f"{ALL_CENTER}.symmetry-index.bin")
LR_UNIVERSE = 51482970
WING_UNIVERSE = math.comb(24, 12)
PLACEHOLDER = "/dev/null"


def write_all_zero_cost(path, universe):
    with open(path, "wb") as table:
        table.write(b"\x01" * universe)


def highlow_string(cube):
    highlow = ["."] * len(cube.state)
    for (square, _), value in zip(cube.reduce333_orient_edges_tuples, cube.highlow_edges_state(None)):
        highlow[square] = value
    return "".join(highlow[1:])


@unittest.skipUnless(BINARY.is_file(), "ida_search_444_phase1 has not been built")
class Phase1Search444Test(unittest.TestCase):
    def setUp(self):
        self.cube = RubiksCube444(solved_444, "URFDLB")
        self.assertEqual(self.cube.highlow_edges_state(None), PHASE1_HIGHLOW_TARGET_444)

    def command(self, *extra, all_center=PLACEHOLDER, all_center_index=PLACEHOLDER, lr=PLACEHOLDER, wing=PLACEHOLDER):
        return [
            str(BINARY),
            "--kociemba",
            self.cube.get_kociemba_string(True),
            "--highlow",
            highlow_string(self.cube),
            "--all-center-cost",
            str(all_center),
            "--all-center-index",
            str(all_center_index),
            "--lr-cost",
            str(lr),
            "--wing-cost",
            str(wing),
            *extra,
        ]

    def test_orbit0_flag_is_required(self):
        result = subprocess.run(self.command("--max-ida-threshold", "0"), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("an orbit0 parity policy is required", result.stderr)

    def test_mapping_count_is_rejected(self):
        result = subprocess.run(
            self.command("--orbit0-need-even-w", "--mapping-count", "8"),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid argument --mapping-count", result.stderr)

    def test_ud_cost_is_rejected(self):
        result = subprocess.run(
            self.command("--orbit0-need-even-w", "--ud-cost", PLACEHOLDER),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid argument --ud-cost", result.stderr)

    @unittest.skipUnless(ALL_CENTER.is_file() and ALL_CENTER_INDEX.is_file(), "all-center tables are not present")
    def test_solved_cube_is_even_parity_goal(self):
        with tempfile.TemporaryDirectory() as tmp:
            lr = Path(tmp) / "lr.bin"
            wing = Path(tmp) / "wing.bin"
            write_all_zero_cost(lr, LR_UNIVERSE)
            write_all_zero_cost(wing, WING_UNIVERSE)
            even = subprocess.run(
                self.command(
                    "--orbit0-need-even-w",
                    "--max-ida-threshold",
                    "0",
                    all_center=ALL_CENTER,
                    all_center_index=ALL_CENTER_INDEX,
                    lr=lr,
                    wing=wing,
                ),
                capture_output=True,
                text=True,
            )
            self.assertEqual(even.returncode, 0, even.stdout + even.stderr)
            self.assertIn("SOLUTION (0 steps)", even.stdout)
            self.assertIn(" INIT    0    0    0    0    0    0", even.stdout)
            self.assertIn("D L L U", even.stdout)
            self.assertIn("D R R U", even.stdout)

            odd = subprocess.run(
                self.command(
                    "--orbit0-need-odd-w",
                    "--max-ida-threshold",
                    "0",
                    all_center=ALL_CENTER,
                    all_center_index=ALL_CENTER_INDEX,
                    lr=lr,
                    wing=wing,
                ),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(odd.returncode, 0)
            self.assertIn("no solution found through threshold 0", odd.stderr)


if __name__ == "__main__":
    unittest.main()
