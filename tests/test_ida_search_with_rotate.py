import math
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from rubikscubennnsolver.RubiksCube555 import (
    LookupTableIDA555CentersStageOnePhase,
    RubiksCube555,
    solved_555,
)
from rubikscubennnsolver.RubiksCube666 import (
    ALL_INNER_X_CENTERS_STAGE_MEMORY_MARGIN,
    ALL_INNER_X_CENTERS_STAGE_TABLE_BYTES,
    RubiksCube666,
    solved_666,
)

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_with_rotate"
RANK_UNIVERSE = 9_465_511_770
X_SQUARES = (
    7,
    9,
    17,
    19,
    32,
    34,
    42,
    44,
    57,
    59,
    67,
    69,
    82,
    84,
    92,
    94,
    107,
    109,
    117,
    119,
    132,
    134,
    142,
    144,
)
T_SQUARES = (
    8,
    12,
    14,
    18,
    33,
    37,
    39,
    43,
    58,
    62,
    64,
    68,
    83,
    87,
    89,
    93,
    108,
    112,
    114,
    118,
    133,
    137,
    139,
    143,
)


def staged_color(color):
    if color in ("U", "D"):
        return "U"
    if color in ("L", "R"):
        return "L"
    return "F"


def multiset_perms(counts):
    result = 1
    remaining = sum(counts)
    for count in counts:
        result *= math.comb(remaining, count)
        remaining -= count
    return result


def multiset_rank(state):
    symbols = "FLU"
    counts = [state.count(symbol) for symbol in symbols]
    rank = 0

    for position, char in enumerate(state):
        selected = symbols.index(char)
        for index in range(selected):
            if counts[index]:
                counts[index] -= 1
                rank += multiset_perms(counts)
                counts[index] += 1
        counts[selected] -= 1
    return rank


def projected_rank(cube, squares):
    return multiset_rank("".join(staged_color(cube.state[index]) for index in squares))


def make_sparse_cost_table(path, entries):
    with open(path, "wb") as table:
        table.truncate(RANK_UNIVERSE)
        for rank, encoded_cost in entries.items():
            table.seek(rank)
            table.write(bytes((encoded_cost,)))


class LowMemoryPathTest(unittest.TestCase):
    def test_default_cube_keeps_graph_based_center_staging(self):
        cube = RubiksCube555(solved_555, "URFDLB", high_memory=False)
        cube.lt_init()

        self.assertFalse(hasattr(cube, "lt_centers_stage_one_phase"))
        self.assertEqual(cube.lt_LR_centers_stage.__class__.__name__, "LookupTableIDA555LRCenterStage")

    def test_666_ranked_phase_one_requires_table_plus_margin(self):
        cube = RubiksCube666.__new__(RubiksCube666)
        required = ALL_INNER_X_CENTERS_STAGE_TABLE_BYTES + ALL_INNER_X_CENTERS_STAGE_MEMORY_MARGIN
        original = __import__(
            "rubikscubennnsolver.RubiksCube666",
            fromlist=["available_memory_bytes"],
        ).available_memory_bytes
        module = sys.modules["rubikscubennnsolver.RubiksCube666"]

        try:
            module.available_memory_bytes = lambda: required
            self.assertTrue(cube.can_use_all_inner_x_centers_stage_table())

            module.available_memory_bytes = lambda: required - 1
            self.assertFalse(cube.can_use_all_inner_x_centers_stage_table())

            module.available_memory_bytes = lambda: None
            self.assertFalse(cube.can_use_all_inner_x_centers_stage_table())
        finally:
            module.available_memory_bytes = original

    def test_666_ranked_path_splits_oll_parity_between_phase_one_and_three(self):
        """Phases 2 and 3 have no 3Xw quarter turn, so only phase 1 can flip orbit1."""
        cube = RubiksCube666(solved_666, "URFDLB")
        cube.lt_init()

        if not cube.use_all_inner_x_centers_stage_table:
            self.skipTest("ranked phase 1 is unavailable on this machine")

        self.assertEqual(cube.lt_all_inner_x_centers_stage.avoid_oll, 1)
        self.assertEqual(cube.lt_UD_centers_stage.avoid_oll, 0)


class RankedRotateIDATest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.x_cost = Path(self.tempdir.name) / "x.cost-only.bin"
        self.t_cost = Path(self.tempdir.name) / "t.cost-only.bin"
        self.solved = RubiksCube555(solved_555, "URFDLB")
        self.scrambled = RubiksCube555(solved_555, "URFDLB")
        self.scrambled.rotate("Uw")
        self.solved_x_rank = projected_rank(self.solved, X_SQUARES)
        self.solved_t_rank = projected_rank(self.solved, T_SQUARES)
        self.scrambled_x_rank = projected_rank(self.scrambled, X_SQUARES)
        self.scrambled_t_rank = projected_rank(self.scrambled, T_SQUARES)
        make_sparse_cost_table(self.x_cost, {self.solved_x_rank: 1, self.scrambled_x_rank: 2})
        make_sparse_cost_table(self.t_cost, {self.solved_t_rank: 1, self.scrambled_t_rank: 2})

    def tearDown(self):
        self.tempdir.cleanup()

    def command(self, cube, *extra):
        kociemba = LookupTableIDA555CentersStageOnePhase(cube).center_only_kociemba_string()
        return (
            str(BINARY),
            "--kociemba",
            kociemba,
            "--x-cost",
            str(self.x_cost),
            "--t-cost",
            str(self.t_cost),
            *extra,
        )

    def test_kociemba_state_masks_non_center_squares(self):
        state = LookupTableIDA555CentersStageOnePhase(self.scrambled).center_only_kociemba_string()

        self.assertEqual(len(state), 150)
        self.assertEqual(state.count("."), 96)
        for index, value in enumerate(state):
            self.assertEqual(value == ".", index % 25 not in {6, 7, 8, 11, 12, 13, 16, 17, 18})

    def test_c_rank_and_encoded_cost_match_python(self):
        result = subprocess.run(self.command(self.scrambled, "--print-ranks"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        match = re.search(r"X_RANK (\d+) T_RANK (\d+) COST (\d+)", result.stdout)
        self.assertIsNotNone(match, result.stdout)
        self.assertEqual(
            tuple(map(int, match.groups())),
            (self.scrambled_x_rank, self.scrambled_t_rank, 1),
        )

    def test_missing_and_wrong_size_tables_fail_cleanly(self):
        missing = subprocess.run(
            self.command(self.solved, "--x-cost", str(Path(self.tempdir.name) / "missing")),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("could not open", missing.stderr)

        wrong_size = Path(self.tempdir.name) / "wrong-size.bin"
        wrong_size.write_bytes(b"\x01")
        wrong = subprocess.run(
            self.command(self.solved, "--x-cost", str(wrong_size)),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(wrong.returncode, 0)
        self.assertIn("expected 9465511770", wrong.stderr)

    def test_serial_order_solution_is_thread_count_independent(self):
        solutions = set()

        for threads in ("1", "4"):
            result = subprocess.run(
                self.command(
                    self.scrambled,
                    "--max-ida-threshold",
                    "1",
                    "--threads",
                    threads,
                    "--serial-order",
                ),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("serial move order", result.stdout)
            self.assertIn("PT0  PT1  CTG  TRU  IDX", result.stdout)
            self.assertRegex(result.stdout, r" INIT\s+1\s+1\s+1\s+1\s+0")
            self.assertRegex(result.stdout, r"\s+0\s+0\s+0\s+0\s+1")
            solutions.add(next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION")))

        self.assertEqual(len(solutions), 1, solutions)

    def test_first_solution_wins_by_default_and_still_stages_the_cube(self):
        result = subprocess.run(
            self.command(self.scrambled, "--max-ida-threshold", "1", "--threads", "4"),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("first solution wins", result.stdout)

        solution = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
        cube = RubiksCube555(solved_555, "URFDLB")
        cube.rotate("Uw")
        for move in solution.split(":", 1)[1].split():
            cube.rotate(move)

        self.assertTrue(cube.centers_staged(), solution)

    def test_shallow_rotate_search_and_python_solution_parsing(self):
        self.scrambled.lt_x_centers_stage_one_phase = SimpleNamespace(filename=str(self.x_cost))
        self.scrambled.lt_t_centers_stage_one_phase = SimpleNamespace(filename=str(self.t_cost))
        search = LookupTableIDA555CentersStageOnePhase(self.scrambled)

        old_cwd = os.getcwd()
        try:
            os.chdir(ROOT)
            search.solve_via_c(max_ida_threshold=1, perimeter_depth=0)
        finally:
            os.chdir(old_cwd)

        self.assertTrue(self.scrambled.centers_staged())
        self.assertRegex(self.scrambled.solve_via_c_output, r"SOLUTION \(1 steps\):")

    def test_solved_side_perimeter_intersects_and_reconstructs_tail(self):
        scrambled = RubiksCube555(solved_555, "URFDLB")
        meeting = RubiksCube555(solved_555, "URFDLB")
        scrambled.rotate("Uw")
        meeting.rotate("Uw")
        scrambled.rotate("Fw")

        root_x_rank = projected_rank(scrambled, X_SQUARES)
        root_t_rank = projected_rank(scrambled, T_SQUARES)
        meeting_x_rank = projected_rank(meeting, X_SQUARES)
        meeting_t_rank = projected_rank(meeting, T_SQUARES)
        make_sparse_cost_table(
            self.x_cost,
            {
                self.solved_x_rank: 1,
                meeting_x_rank: 2,
                root_x_rank: 3,
            },
        )
        make_sparse_cost_table(
            self.t_cost,
            {
                self.solved_t_rank: 1,
                meeting_t_rank: 2,
                root_t_rank: 3,
            },
        )

        result = subprocess.run(
            self.command(
                scrambled,
                "--min-ida-threshold",
                "2",
                "--max-ida-threshold",
                "2",
                "--threads",
                "1",
                "--perimeter-depth",
                "1",
                "--perimeter-max-states",
                "100",
            ),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PERIMETER ROOT", result.stdout)
        self.assertIn("PERIMETER HIT", result.stdout)
        self.assertRegex(result.stdout, r"PERIMETER HIT \(forward \d+, perimeter \d+, x_cost \d+, t_cost \d+")
        self.assertIn("built solved-side perimeter depth 1 with 7 states", result.stdout)
        self.assertRegex(result.stdout, r"\d+ perimeter hits")
        solution = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
        moves = solution.split(":", 1)[1].split()
        self.assertEqual(len(moves), 2, solution)
        for move in moves:
            scrambled.rotate(move)
        self.assertTrue(scrambled.centers_staged(), solution)

    def test_perimeter_state_limit_fails_cleanly(self):
        result = subprocess.run(
            self.command(
                self.scrambled,
                "--perimeter-depth",
                "2",
                "--perimeter-max-states",
                "7",
            ),
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("perimeter exceeded 7 states", result.stderr)


class PhaseOnePortfolioTest(unittest.TestCase):
    class FakePruneTable:
        def __init__(self, parent, coordinate):
            self.parent = parent
            self.coordinate = coordinate

        def state_index(self):
            roots = {
                "A": (10, 20),
                "B": (11, 21),
                "C": (11, 21),
            }
            return roots[self.parent.state[0]][self.coordinate]

    class FakePhaseOne:
        def solutions_via_c(self, solution_count):
            assert solution_count == 64
            return [
                (("A",), (0, 0, 0, 0, 0)),
                (("B",), (0, 0, 0, 0, 0)),
                (("C",), (0, 0, 0, 0, 0)),
            ]

    class FakePhaseTwo:
        def __init__(self, parent):
            self.parent = parent
            self.prune_tables = [
                PhaseOnePortfolioTest.FakePruneTable(parent, 0),
                PhaseOnePortfolioTest.FakePruneTable(parent, 1),
            ]
            self.calls = []

        def solutions_via_c(self, pt_states, solution_count):
            assert solution_count == 1
            parity = 0 in self.parent.center_solution_leads_to_oll_parity()
            self.calls.append((parity, tuple(pt_states)))

            if parity:
                return [(("PA1", "PA2", "PA3"), (10, 20, 0, 0, 0))]
            return [(("PB1", "PB2"), (11, 21, 0, 0, 0))]

    class FakeCube:
        def __init__(self):
            self.state = ["root"]
            self.solution = []
            self.lt_LR_centers_stage = PhaseOnePortfolioTest.FakePhaseOne()
            self.lt_FB_centers_stage = PhaseOnePortfolioTest.FakePhaseTwo(self)

        def rotate_U_to_U(self):
            pass

        def rotate_F_to_F(self):
            pass

        def centers_staged(self):
            return self.state[0] == "done"

        def LR_centers_staged(self):
            return self.state[0] in {"A", "B", "C", "done"}

        def FB_centers_staged(self):
            return self.state[0] == "done"

        def center_solution_leads_to_oll_parity(self):
            return [0] if self.state[0] == "A" else []

        def rotate(self, move):
            self.solution.append(move)
            if move in {"A", "B", "C"}:
                self.state[0] = move
            elif move.startswith("P"):
                self.state[0] = "done"

        def print_cube_add_comment(self, comment, start):
            pass

    def test_portfolio_deduplicates_roots_groups_parity_and_picks_shortest_phase_two(self):
        cube = self.FakeCube()

        RubiksCube555.group_centers_phase1_and_2(cube)

        self.assertEqual(cube.solution, ["B", "PB1", "PB2"])
        self.assertEqual(
            set(cube.lt_FB_centers_stage.calls),
            {
                (True, ((10, 20),)),
                (False, ((11, 21),)),
            },
        )


class PhaseOneTwoPortfolio444Test(unittest.TestCase):
    class FakePruneTable:
        def __init__(self, parent, coordinate):
            self.parent = parent
            self.coordinate = coordinate

        def state_index(self):
            roots = {
                "A": (10, 20),
                "B": (11, 21),
                "C": (11, 21),
            }
            return roots[self.parent.state[0]][self.coordinate]

    class FakePhaseOne:
        def solutions_via_c(self, solution_count):
            assert solution_count == 64
            return [
                (("A",), (0, 0, 0, 0, 0)),
                (("B",), (0, 0, 0, 0, 0)),
                (("C",), (0, 0, 0, 0, 0)),
            ]

    class FakePhaseTwo:
        def __init__(self, parent):
            self.parent = parent
            self.prune_tables = [
                PhaseOneTwoPortfolio444Test.FakePruneTable(parent, 0),
                PhaseOneTwoPortfolio444Test.FakePruneTable(parent, 1),
            ]
            self.calls = []

        def solutions_via_c(self, pt_states, solution_count):
            assert solution_count == 1
            parity = 0 in self.parent.center_solution_leads_to_oll_parity()
            self.calls.append((parity, tuple(pt_states)))

            if parity:
                return [(("PA1", "PA2", "PA3"), (10, 20, 0, 0, 0))]
            return [(("PB1", "PB2"), (11, 21, 0, 0, 0))]

    class FakeCube:
        def __init__(self):
            self.state = ["root"]
            self.solution = []
            self.edge_mapping = None
            self.lt_phase1 = PhaseOneTwoPortfolio444Test.FakePhaseOne()
            self.lt_phase2 = PhaseOneTwoPortfolio444Test.FakePhaseTwo(self)

        def LR_centers_staged(self):
            return self.state[0] in {"A", "B", "C", "done"}

        def center_solution_leads_to_oll_parity(self):
            return [0] if self.state[0] == "A" else []

        def phase2_pt_state_indexes(self):
            if self.state[0] == "A":
                return {(10, 20): "map-A"}
            return {(11, 21): "map-B"}

        def rotate(self, move):
            self.solution.append(move)
            if move in {"A", "B", "C"}:
                self.state[0] = move
            elif move.startswith("P"):
                self.state[0] = "done"

        def print_cube_add_comment(self, comment, start):
            pass

        def highlow_edges_print(self):
            pass

    def test_portfolio_deduplicates_roots_groups_parity_and_picks_shortest_phase_two(self):
        from rubikscubennnsolver.RubiksCube444 import RubiksCube444

        cube = self.FakeCube()
        RubiksCube444.phase1_and_2(cube)

        self.assertEqual(cube.solution, ["B", "PB1", "PB2"])
        self.assertEqual(cube.edge_mapping, "map-B")
        self.assertEqual(
            set(cube.lt_phase2.calls),
            {
                (True, ((10, 20),)),
                (False, ((11, 21),)),
            },
        )


class PhaseThreeFourPortfolio666Test(unittest.TestCase):
    class FakePruneTable:
        def __init__(self, parent, coordinate):
            self.parent = parent
            self.coordinate = coordinate

        def state_index(self):
            roots = {
                "A": (10, 20),
                "B": (11, 21),
                "C": (11, 21),
            }
            return roots[self.parent.state[0]][self.coordinate]

    class FakePhaseThree:
        def solutions_via_c(self, solution_count, use_kociemba_string):
            assert solution_count == 64
            assert use_kociemba_string
            return [
                (("A",), (0, 0, 0, 0, 0)),
                (("B",), (0, 0, 0, 0, 0)),
                (("C",), (0, 0, 0, 0, 0)),
            ]

    class FakePhaseFour:
        def __init__(self, parent):
            self.parent = parent
            self.prune_tables = [
                PhaseThreeFourPortfolio666Test.FakePruneTable(parent, 0),
                PhaseThreeFourPortfolio666Test.FakePruneTable(parent, 1),
            ]
            self.calls = []

        def solutions_via_c(self, pt_states, solution_count):
            assert solution_count == 1
            parity = 0 in self.parent.center_solution_leads_to_oll_parity()
            self.calls.append((parity, tuple(pt_states)))

            if parity:
                return [(("PA1", "PA2", "PA3"), (10, 20, 0, 0, 0))]
            return [(("PB1", "PB2"), (11, 21, 0, 0, 0))]

    class Fake555:
        def __init__(self):
            self.state = ["root"]
            self.solution = []
            self.lt_FB_centers_stage = PhaseThreeFourPortfolio666Test.FakePhaseFour(self)

        def center_solution_leads_to_oll_parity(self):
            return [0] if self.state[0] == "A" else []

    class FakeCube:
        def __init__(self):
            self.state = ["root"]
            self.solution = []
            self.fake_555 = PhaseThreeFourPortfolio666Test.Fake555()
            self.lt_UD_oblique_edge_stage = PhaseThreeFourPortfolio666Test.FakePhaseThree()

        def get_fake_555(self):
            return self.fake_555

        def populate_fake_555_for_ULFRBD_solve(self):
            self.fake_555.state = self.state[:]
            self.fake_555.solution = []

        def rotate(self, move):
            self.solution.append(move)
            if move in {"A", "B", "C"}:
                self.state[0] = move

        def print_cube_add_comment(self, comment, start):
            pass

    def test_portfolio_deduplicates_roots_groups_parity_and_picks_shortest_phase_four(self):
        from rubikscubennnsolver.RubiksCube666 import RubiksCube666

        cube = self.FakeCube()
        RubiksCube666.stage_centers_phase3_and_4(cube)

        self.assertEqual(cube.solution, ["B", "PB1", "PB2"])
        self.assertEqual(
            set(cube.fake_555.lt_FB_centers_stage.calls),
            {
                (True, ((10, 20),)),
                (False, ((11, 21),)),
            },
        )


if __name__ == "__main__":
    unittest.main()
