# standard libraries
import unittest
from unittest.mock import patch

# rubiks cube libraries
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666 import (
    DAISY_PLUS_TABLES_666,
    RubiksCube666,
    UFBD_outer_x_centers_666,
    solved_666,
)
from rubikscubennnsolver.RubiksCube777 import (
    DAISY_LEAVE_ONE_OUT_TABLES_777,
    DAISY_PERFECT_TABLES_777,
    NATIVE_SOLVE_PERFECT_TABLES_777,
    RubiksCube777,
    UFBD_inner_t_centers_777,
    UFBD_inner_x_centers_777,
    UFBD_left_oblique_777,
    UFBD_middle_oblique_777,
    UFBD_outer_x_centers_777,
    UFBD_right_oblique_777,
    oblique_edges_777,
    solved_777,
)
from rubikscubennnsolver.RubiksCubeNNNEven import RubiksCubeNNNEven, solved_888
from rubikscubennnsolver.RubiksCubeNNNOdd import RubiksCube777ForNNNOdd, RubiksCubeNNNOdd, solved_999


class CenterStagingTablesTest(unittest.TestCase):
    def test_two_phase_option_keeps_graph_based_center_staging(self):
        cube = RubiksCube555(solved_555, "URFDLB", use_one_phase_centers_stage=False)
        cube.lt_init()

        self.assertFalse(hasattr(cube, "lt_centers_stage_one_phase"))
        self.assertEqual(cube.lt_LR_centers_stage.__class__.__name__, "LookupTableIDA555LRCenterStage")

    def test_666_ranked_path_splits_oll_parity_between_phase_one_and_three(self):
        """Phases 2 and 3 have no 3Xw quarter turn, so only phase 1 can flip orbit1."""
        cube = RubiksCube666(solved_666, "URFDLB")
        with patch("rubikscubennnsolver.LookupTable.download_file_if_needed"):
            cube.lt_init()

        self.assertEqual(cube.lt_all_inner_x_centers_stage.avoid_oll, 1)
        self.assertEqual(cube.lt_UD_centers_stage.avoid_oll, 0)
        self.assertFalse(hasattr(cube, "lt_LR_oblique_edge_stage_inner_x_stage"))
        self.assertFalse(hasattr(cube, "lt_centers_reduce_555"))
        self.assertEqual(cube.lt_daisy_centers.__class__.__name__, "LookupTableIDA666DaisyCenters")
        self.assertEqual(len(DAISY_PLUS_TABLES_666), 18)
        self.assertIsNone(cube.lt_daisy_centers.multiplier)

    def test_666_has_no_eo_phase_of_its_own(self):
        """The fake 4x4x4 that pairs the inside wings EOes them along the way."""
        cube = RubiksCube666(solved_666, "URFDLB")
        with patch("rubikscubennnsolver.LookupTable.download_file_if_needed"):
            cube.lt_init()

        self.assertFalse(hasattr(cube, "lt_EO_inside_wings"))
        self.assertFalse(hasattr(cube, "lt_LR_highlow_edges"))
        self.assertFalse(hasattr(cube, "lt_UD_solve_inner_x_centers_and_oblique_edges"))

    def test_even_plus_sign_daisy_solves_every_center_orbit(self):
        events = []

        class Fake666:
            def __init__(self):
                self.state = ["x"] * 217
                self.solution = []

            def stage_centers(self):
                events.append("stage")

            def daisy_solve_centers(self):
                events.append("daisy")

        cube = RubiksCubeNNNEven(solved_888, "URFDLB")
        fake_666 = Fake666()
        cube.get_fake_666 = lambda: fake_666

        cube.make_plus_sign()

        self.assertEqual(events, ["stage", "daisy", "stage", "daisy"])

    def test_777_combined_phase_recolors_both_coordinates(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        combined = cube.lt_LR_oblique_edges_UD_inner_centers_stage

        self.assertFalse(hasattr(cube, "stage_UD_inner_centers_in_phase2"))
        self.assertFalse(hasattr(cube, "lt_LR_oblique_edge_pairing"))
        self.assertFalse(hasattr(cube, "lt_UD_oblique_edge_pairing"))
        self.assertEqual(combined.avoid_oll, 1)
        self.assertNotIsInstance(combined, LookupTableIDAViaGraph)
        self.assertEqual(
            combined.filename,
            "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage.cost-only.bin",
        )

        combined.recolor()

        inner_centers = UFBD_inner_t_centers_777 + UFBD_inner_x_centers_777
        for square in inner_centers:
            expected = "U" if square < 50 or square > 245 else "x"
            self.assertEqual(cube.state[square], expected)

        for square in oblique_edges_777:
            expected = "L" if 49 < square < 99 or 147 < square < 197 else "x"
            self.assertEqual(cube.state[square], expected)

    def test_larger_odd_cubes_pair_obliques_without_the_combined_phase(self):
        """One orbit at a time means the U/D inner centers cannot be staged here."""
        cube = RubiksCubeNNNOdd(solved_999, "URFDLB")
        fake_777 = cube.get_fake_777()

        self.assertIsInstance(fake_777, RubiksCube777ForNNNOdd)
        self.assertIsInstance(fake_777.lt_LR_oblique_edge_pairing, LookupTableIDAViaGraph)
        self.assertEqual(fake_777.lt_UD_obliques_outer_x_stage.avoid_oll, 0)
        self.assertIsInstance(fake_777.lt_UD_oblique_edge_pairing, LookupTableIDAViaGraph)

    def test_777_combined_ud_phase_recolors_four_coordinates(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        combined = cube.lt_UD_obliques_outer_x_stage

        self.assertEqual(combined.avoid_oll, 0)
        self.assertNotIsInstance(combined, LookupTableIDAViaGraph)
        combined.recolor()

        tracked = UFBD_outer_x_centers_777 + UFBD_left_oblique_777 + UFBD_middle_oblique_777 + UFBD_right_oblique_777
        for square in tracked:
            expected = "U" if square < 50 or square > 245 else "x"
            self.assertEqual(cube.state[square], expected)

    def test_777_combined_daisy_replaces_serial_bar_phases(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        daisy = cube.lt_daisy_centers

        self.assertNotIsInstance(daisy, LookupTableIDAViaGraph)
        self.assertTrue(daisy.use_perfect_tables)
        self.assertEqual(len(DAISY_LEAVE_ONE_OUT_TABLES_777), 15)
        self.assertEqual(len(DAISY_PERFECT_TABLES_777), 3)

        # A per-axis table tops out at depth 15 while the combined daisy is 19+ moves
        # away, so the C searcher leans on its sampled cost matrix rather than a
        # multiplier over the admissible max.
        self.assertIsNone(daisy.multiplier)

    def test_larger_odd_cubes_use_native_only_daisy_without_step_tables(self):
        cube = RubiksCubeNNNOdd(solved_999, "URFDLB")
        fake_777 = cube.get_fake_777()
        calls = []

        with (
            patch.object(cube, "populate_fake_777"),
            patch.object(
                fake_777,
                "centers_combined_daisy_solve",
                side_effect=lambda **kwargs: calls.append(kwargs),
            ),
        ):
            cube.stage_or_solve_inside_777(0, 0, 7, 0, 0, "solve_centers")

        self.assertEqual(calls, [{"native_only": True}])
        for step in (70, 71, 72, 75, 76):
            self.assertFalse(hasattr(fake_777, f"lt_step{step}"))
        self.assertIsNotNone(fake_777.lt_daisy_centers)

    def test_native_only_daisy_uses_its_own_perfect_tables(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        daisy = cube.lt_daisy_centers
        commands = []

        def fake_run(cmd):
            commands.append(cmd)
            return "SOLUTION (0 steps):"

        with (
            patch("rubikscubennnsolver.RubiksCube777.download_file_if_needed"),
            patch.object(daisy, "_run", side_effect=fake_run),
        ):
            daisy.solve_via_c(native_only=True)
            daisy.solve_via_c()

        self.assertEqual(len(NATIVE_SOLVE_PERFECT_TABLES_777), 3)
        self.assertIn("--native-only", commands[0])
        self.assertNotIn("--native-only", commands[1])
        for _, filename in NATIVE_SOLVE_PERFECT_TABLES_777:
            self.assertIn(filename, commands[0])
            self.assertNotIn(filename, commands[1])
        for _, filename in DAISY_PERFECT_TABLES_777:
            self.assertIn(filename, commands[1])
            self.assertNotIn(filename, commands[0])


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

        def solutions_via_c(self, pt_states):
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

        def solutions_via_c(self, pt_states):
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
        # rubiks cube libraries
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


class PhaseTwoPortfolioTest(unittest.TestCase):
    class FakePhaseTwo:
        def solutions_via_c(self, solution_count):
            assert solution_count == 64
            return [(("A",), ()), (("B",), ()), (("C",), ())]

    class Fake555:
        def __init__(self):
            self.lt_LR_centers_stage = PhaseTwoPortfolioTest.FakePhaseTwo()

    class FakePhaseThree:
        def __init__(self):
            self.roots = None

        def solution_via_c(self, roots):
            self.roots = roots
            return 1, ("P1", "P2")

    class FakeCube:
        def __init__(self):
            self.state = ["x"] * 217
            self.solution = []
            self.fake_555 = PhaseTwoPortfolioTest.Fake555()
            self.lt_UD_centers_stage = PhaseTwoPortfolioTest.FakePhaseThree()

        def get_fake_555(self):
            return self.fake_555

        def populate_fake_555_for_ULFRBD_solve(self):
            pass

        def rotate(self, move):
            self.solution.append(move)
            if move == "A":
                self.state[UFBD_outer_x_centers_666[0]] = "A"
            elif move in ("B", "C"):
                self.state[UFBD_outer_x_centers_666[0]] = "B"

        def center_solution_leads_to_oll_parity(self):
            return {0} if self.state[UFBD_outer_x_centers_666[0]] == "A" else set()

        def get_kociemba_string(self, _all_squares):
            return self.state[UFBD_outer_x_centers_666[0]] * 216

        def print_cube_add_comment(self, _comment, _start):
            pass

    def test_phase_two_portfolio_deduplicates_roots_and_applies_selected_prefix(self):
        cube = self.FakeCube()

        RubiksCube666.stage_LR_and_UD_centers(cube)

        self.assertEqual(cube.solution, ["B", "P1", "P2"])
        self.assertEqual(
            cube.lt_UD_centers_stage.roots,
            [
                (0, "A" * 216, frozenset({0})),
                (1, "B" * 216, frozenset()),
            ],
        )


class Reduce555Test(unittest.TestCase):
    def test_reduce_555_daisies_the_centers_then_hands_the_wings_to_the_444(self):
        events = []

        class FakeDaisy:
            def solve_via_c(self):
                events.append("daisy")

        class FakeCube:
            solution = []
            lt_daisy_centers = FakeDaisy()
            daisy_solve_centers = RubiksCube666.daisy_solve_centers

            def reduced_to_555(self):
                return False

            def lt_init(self):
                events.append("lt_init")

            def stage_centers(self):
                events.append("stage")

            def pair_inside_edges_via_444(self):
                events.append("pair-444")

            def print_cube_add_comment(self, _comment, _start):
                pass

        RubiksCube666.reduce_555(FakeCube())

        self.assertEqual(events, ["lt_init", "stage", "daisy", "pair-444"])


if __name__ == "__main__":
    unittest.main()
