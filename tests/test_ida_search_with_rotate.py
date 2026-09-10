# standard libraries
import unittest
from unittest.mock import patch

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, UFBD_outer_x_centers_666, solved_666
from rubikscubennnsolver.RubiksCubeNNNEven import RubiksCubeNNNEven, solved_888


class CenterStagingTablesTest(unittest.TestCase):
    def test_default_cube_keeps_graph_based_center_staging(self):
        cube = RubiksCube555(solved_555, "URFDLB")
        cube.lt_init()

        self.assertFalse(hasattr(cube, "lt_centers_stage_one_phase"))
        self.assertEqual(cube.lt_LR_centers_stage.__class__.__name__, "LookupTableIDA555LRCenterStage")

    def test_666_ranked_path_splits_oll_parity_between_phase_one_and_three(self):
        """Phases 2 and 3 have no 3Xw quarter turn, so only phase 1 can flip orbit1."""
        cube = RubiksCube666(solved_666, "URFDLB")
        cube.lt_init()

        self.assertEqual(cube.lt_all_inner_x_centers_stage.avoid_oll, 1)
        self.assertEqual(cube.lt_UD_centers_stage.avoid_oll, 0)
        self.assertFalse(hasattr(cube, "lt_LR_oblique_edge_stage_inner_x_stage"))

    def test_even_plus_sign_uses_ranked_staging_and_keeps_outer_eo(self):
        events = []

        class Fake666:
            def __init__(self):
                self.state = ["x"] * 217
                self.solution = []

            def stage_centers(self):
                events.append("stage")

            def daisy_solve_centers_eo_edges(self):
                events.append("outer-eo")

        cube = RubiksCubeNNNEven(solved_888, "URFDLB")
        fake_666 = Fake666()
        cube.get_fake_666 = lambda: fake_666

        with patch(
            "rubikscubennnsolver.RubiksCubeNNNEven.daisy_solve_centers",
            side_effect=lambda unused: events.append("inner-no-eo"),
        ):
            cube.make_plus_sign()

        self.assertEqual(events, ["stage", "inner-no-eo", "stage", "outer-eo"])


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


class PhaseFiveSixPortfolioTest(unittest.TestCase):
    class FakeStep50PruneTable:
        def state_index(self):
            return 0

    class FakePhaseFive:
        def __init__(self):
            self.prune_tables = [
                PhaseFiveSixPortfolioTest.FakeStep50PruneTable(),
                PhaseFiveSixPortfolioTest.FakeStep50PruneTable(),
            ]

        def solutions_via_c(self, pt_states, solution_count, find_extra):
            assert solution_count == 64
            assert find_extra
            assert list(pt_states) == [(0, 0)]
            return [
                (("A",), (0, 0, 0, 0, 0)),
                (("B", "C", "D"), (0, 0, 0, 0, 0)),
            ]

    class FakePhaseSixPruneTable:
        def __init__(self, parent, coordinate):
            self.parent = parent
            self.coordinate = coordinate

        def state_index(self):
            roots = {
                "A": (10, 20, 30),
                "B": (11, 21, 31),
                "D": (11, 21, 31),
            }
            return roots[self.parent.state[0]][self.coordinate]

    class FakePhaseSix:
        def __init__(self, parent):
            self.parent = parent
            self.calls = []
            self.prune_tables = [
                PhaseFiveSixPortfolioTest.FakePhaseSixPruneTable(parent, 0),
                PhaseFiveSixPortfolioTest.FakePhaseSixPruneTable(parent, 1),
                PhaseFiveSixPortfolioTest.FakePhaseSixPruneTable(parent, 2),
            ]

        def solutions_via_c(self, pt_states, solution_count):
            assert solution_count == 1
            self.calls.append(tuple(pt_states))
            roots = set(pt_states)
            if roots == {(10, 20, 30)}:
                return [(("PA1", "PA2", "PA3"), (10, 20, 30, 0, 0))]
            if roots == {(11, 21, 31)}:
                return [(("PB1", "PB2"), (11, 21, 31, 0, 0))]
            raise AssertionError(f"phase 6 searched mixed length groups: {pt_states}")

    class FakeCube:
        def __init__(self):
            self.state = ["root"]
            self.solution = []
            self.edge_mapping = None
            self.lt_step50 = PhaseFiveSixPortfolioTest.FakePhaseFive()
            self.lt_UFBD_solve_inner_x_centers_and_oblique_edges = PhaseFiveSixPortfolioTest.FakePhaseSix(self)

        def rotate(self, move):
            self.solution.append(move)
            if move in {"A", "B", "C", "D"}:
                self.state[0] = move

        def print_cube_add_comment(self, _comment, _start):
            pass

    def test_phase_five_portfolio_deduplicates_phase_six_roots_and_picks_shortest_total(self):
        cube = self.FakeCube()

        RubiksCube666.daisy_solve_centers_eo_edges(cube)

        self.assertEqual(cube.solution, ["A", "PA1", "PA2", "PA3"])
        self.assertEqual(
            cube.lt_UFBD_solve_inner_x_centers_and_oblique_edges.calls,
            [((10, 20, 30),), ((11, 21, 31),)],
        )


if __name__ == "__main__":
    unittest.main()
