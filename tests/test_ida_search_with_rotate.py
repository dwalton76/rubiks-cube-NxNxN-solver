# standard libraries
import subprocess
import unittest
from unittest.mock import patch

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666 import (
    DAISY_INNER_X_SPINE_TABLES_666,
    RubiksCube666,
    UFBD_outer_x_centers_666,
    solved_666,
)
from rubikscubennnsolver.RubiksCube777 import (
    DAISY_INNER_X_SPINE_TABLE_777,
    DAISY_LR_INNER_TABLE_777,
    PHASE56_PAIR_COST_MATRIX_777,
    PHASE8_INNER_INTERACTION_TABLE_777,
    PHASE8_INNER_OBLIQUE_TABLES_777,
    PHASE8_PAIRED_TABLES_777,
    PHASE8_TABLES_777,
    PHASE9_TABLES_777,
    DAISY_MIXED_TABLES_777,
    DAISY_PERFECT_TABLES_777,
    NATIVE_SOLVE_PERFECT_TABLES_777,
    RubiksCube777,
    UD_OBLIQUE_ONLY_TABLES_777,
    UD_PHASE56_TABLES_777,
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
    def test_555_uses_dedicated_ranked_center_staging(self):
        cube = RubiksCube555(solved_555, "URFDLB")
        with (
            patch("rubikscubennnsolver.LookupTable.download_file_if_needed"),
            patch("rubikscubennnsolver.RubiksCube555.download_file_if_needed"),
        ):
            cube.lt_init()

        self.assertEqual(cube.lt_LR_centers_stage.__class__.__name__, "LookupTableIDA555LRCenterStage")
        self.assertEqual(cube.lt_FB_centers_stage.__class__.__name__, "LookupTableIDA555FBCentersStage")
        self.assertEqual(cube.lt_phase3.__class__.__name__, "LookupTableIDA555LRCenterStageEOBothOrbits")
        self.assertEqual(cube.lt_phase4.__class__.__name__, "LookupTable555Phase4")

    def test_666_uses_lr_then_combined_ud_oblique_and_ranked_ud(self):
        cube = RubiksCube666(solved_666, "URFDLB")
        with patch("rubikscubennnsolver.LookupTable.download_file_if_needed"):
            cube.lt_init()

        self.assertEqual(
            cube.lt_LR_inner_x_centers_stage.__class__.__name__,
            "LookupTableIDA666LRInnerXCentersStage",
        )
        self.assertEqual(
            cube.lt_UD_inner_x_centers_stage_LR_oblique_pairing.__class__.__name__,
            "LookupTableIDA666UDInnerXCentersStageLRObliquePairing",
        )
        self.assertEqual(cube.lt_UD_centers_stage.avoid_oll, 0)
        self.assertEqual(cube.lt_daisy_centers.__class__.__name__, "LookupTableIDA666DaisyCenters")
        self.assertEqual(len(DAISY_INNER_X_SPINE_TABLES_666), 3)
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

    def test_777_phase_one_keeps_the_shortest_solution_with_the_most_lr_pairs(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        self.assertEqual(cube.LR_oblique_pair_count(), 16)

        seen = {}

        def fake_solutions(solution_count):
            seen["solution_count"] = solution_count
            return [(("Uw",), ()), ((), ())]

        cube.lt_init()
        with patch("rubikscubennnsolver.RubiksCube555.download_file_if_needed"):
            cube.get_fake_555()
        with (
            patch.object(cube, "LR_inside_centers_staged", return_value=False),
            patch.object(cube, "create_fake_555_from_inside_centers"),
            patch.object(cube.fake_555.lt_LR_centers_stage, "solutions_via_c", side_effect=fake_solutions),
        ):
            cube.group_inside_LR_centers()

        self.assertEqual(seen["solution_count"], 0)
        self.assertEqual(cube.solution, [])
        self.assertEqual(cube.LR_oblique_pair_count(), 16)

    def test_777_phase1_portfolio_drops_duplicate_phase2_states(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        with patch("rubikscubennnsolver.RubiksCube555.download_file_if_needed"):
            cube.get_fake_555()

        def fake_solutions(solution_count):
            self.assertEqual(solution_count, 0)
            return [((), ()), ((), ())]

        with (
            patch.object(cube, "LR_inside_centers_staged", return_value=False),
            patch.object(cube, "create_fake_555_from_inside_centers"),
            patch.object(cube.fake_555.lt_LR_centers_stage, "solutions_via_c", side_effect=fake_solutions),
        ):
            portfolio = cube._inside_lr_center_solutions()

        self.assertEqual(len(portfolio), 1)
        self.assertEqual(portfolio[0][0], ())
        self.assertEqual(cube.solution, [])

    def test_777_phase2_applies_the_phase1_root_that_solves(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        uw_cube = RubiksCube777(solved_777, "URFDLB")
        uw_cube.rotate("3Uw")
        uw_state = uw_cube.get_kociemba_string(True)
        captured = {}

        class FakeProc:
            def __init__(self, lines):
                self.stdout = lines

            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def wait(self):
                return 0

        def fake_solutions(solution_count):
            self.assertEqual(solution_count, 0)
            return [(("U",), ()), (("Uw",), ())]

        def fake_popen(cmd, **_kwargs):
            captured["cmd"] = cmd
            roots_path = cmd[cmd.index("--kociemba-file") + 1]
            with open(roots_path) as fh:
                captured["roots"] = fh.read().splitlines()
            return FakeProc(["ROOT_INDEX 1\n", "SOLUTION (1 steps): F\n"])

        with patch("rubikscubennnsolver.RubiksCube555.download_file_if_needed"):
            cube.get_fake_555()
        with (
            patch.object(cube, "LR_inside_centers_staged", return_value=False),
            patch.object(cube, "UD_inside_centers_staged", return_value=False),
            patch.object(cube, "LR_obliques_staged", return_value=False),
            patch.object(cube, "create_fake_555_from_inside_centers"),
            patch.object(cube.fake_555.lt_LR_centers_stage, "solutions_via_c", side_effect=fake_solutions),
            patch("rubikscubennnsolver.RubiksCube777.download_file_if_needed"),
            patch("rubikscubennnsolver.RubiksCube777.subprocess.Popen", side_effect=fake_popen),
            patch.object(cube, "_phase3_solutions"),
        ):
            cube.stage_LR_centers()

        self.assertIn("--kociemba-file", captured["cmd"])
        self.assertNotIn("--kociemba", captured["cmd"])
        self.assertEqual(captured["cmd"][captured["cmd"].index("--root-cap") + 1], "16")
        self.assertEqual(len(captured["roots"]), 2)
        self.assertTrue(captured["roots"][1].startswith("1,0,"))
        self.assertIn(uw_state, captured["roots"][1])
        self.assertEqual(cube.solution[0], "3Uw")
        self.assertIn("F", cube.solution)

    def test_larger_odd_cubes_use_combined_phase_two_only_on_full_mapping_slices(self):
        """Partial rings pair obliques only; a real 7x7 of that orbit uses phase 2."""
        cube = RubiksCubeNNNOdd(solved_999, "URFDLB")
        fake_777 = cube.get_fake_777()

        self.assertIsInstance(fake_777, RubiksCube777ForNNNOdd)
        self.assertIs(RubiksCube777ForNNNOdd.stage_LR_centers, RubiksCube777.stage_LR_centers)
        self.assertEqual(fake_777.lt_LR_oblique_edges_UD_inner_centers_stage.avoid_oll, 1)
        self.assertEqual(
            fake_777.lt_LR_oblique_edge_pairing.__class__.__name__,
            "LookupTableIDA777LRObliqueEdgePairing",
        )
        self.assertEqual(fake_777.lt_UD_obliques_outer_x_stage.avoid_oll, 0)
        self.assertEqual(
            fake_777.lt_UD_oblique_edge_pairing.__class__.__name__,
            "LookupTableIDA777UDObliqueEdgePairing",
        )

        calls = []
        with (
            patch.object(cube, "populate_fake_777"),
            patch.object(fake_777, "stage_LR_centers", side_effect=lambda: calls.append("stage")),
            patch.object(fake_777, "stage_LR_t_centers", side_effect=lambda: calls.append("t")),
            patch.object(
                fake_777.lt_LR_oblique_edge_pairing,
                "solve_via_c",
                side_effect=lambda **_kwargs: calls.append("pair"),
            ),
        ):
            cube.stage_or_solve_inside_777(0, 1, 7, 0, 1, "stage_LR_centers")
            cube.stage_or_solve_inside_777(1, 1, 7, 0, 1, "stage_LR_centers")
            cube.stage_or_solve_inside_777(1, 1, 7, 1, 1, "stage_LR_centers")
            cube.stage_or_solve_inside_777(0, 1, 7, 1, 1, "stage_LR_centers")

        self.assertEqual(calls, ["stage", "pair", "stage", "t"])

    def test_larger_odd_cubes_dispatch_ud_staging_like_lr(self):
        cube = RubiksCubeNNNOdd(solved_999, "URFDLB")
        fake_777 = cube.get_fake_777()
        calls = []
        with (
            patch.object(cube, "populate_fake_777"),
            patch.object(fake_777, "stage_UD_centers", side_effect=lambda: calls.append("stage")),
            patch.object(fake_777, "stage_UD_t_centers", side_effect=lambda: calls.append("t")),
            patch.object(
                fake_777.lt_UD_oblique_edge_pairing,
                "solve_via_c",
                side_effect=lambda **_kwargs: calls.append("pair"),
            ),
        ):
            cube.stage_or_solve_inside_777(0, 1, 7, 0, 1, "stage_UD_centers")
            cube.stage_or_solve_inside_777(1, 1, 7, 0, 1, "stage_UD_centers")
            cube.stage_or_solve_inside_777(1, 1, 7, 1, 1, "stage_UD_centers")
            cube.stage_or_solve_inside_777(0, 1, 7, 1, 1, "stage_UD_centers")

        self.assertEqual(calls, ["stage", "pair", "stage", "t"])

    def test_group_inside_ud_centers_skips_when_already_staged(self):
        fake_777 = RubiksCubeNNNOdd(solved_999, "URFDLB").get_fake_777()
        with (
            patch.object(fake_777, "UD_inside_centers_staged", return_value=True),
            patch.object(fake_777, "create_fake_555_from_inside_centers") as create,
        ):
            fake_777.group_inside_UD_centers()
        create.assert_not_called()

    def test_odd_ud_t_centers_do_not_use_fake_555_t_center_ida(self):
        fake_777 = RubiksCubeNNNOdd(solved_999, "URFDLB").get_fake_777()
        calls = []
        with (
            patch.object(fake_777, "UD_centers_staged", return_value=False),
            patch.object(fake_777, "UD_inside_centers_staged", return_value=True),
            patch.object(
                fake_777,
                "create_fake_555_from_outside_centers",
                side_effect=AssertionError("5x5 t-center IDA should not run"),
            ),
            patch.object(
                fake_777.lt_UD_oblique_edge_pairing,
                "solve_via_c",
                side_effect=lambda **_kwargs: calls.append("pair"),
            ),
        ):
            fake_777.stage_UD_t_centers()
        self.assertEqual(calls, ["pair"])

    def test_odd_ud_oblique_pairing_invokes_obliques_only_binary(self):
        fake_777 = RubiksCubeNNNOdd(solved_999, "URFDLB").get_fake_777()
        captured = {}

        class FakeProc:
            def __init__(self):
                self.stdout = iter(["SOLUTION (0 steps):\n"])

            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def wait(self):
                return 0

        def fake_popen(cmd, **_kwargs):
            captured["cmd"] = cmd
            return FakeProc()

        with (
            patch("rubikscubennnsolver.RubiksCubeNNNOdd.download_file_if_needed"),
            patch("rubikscubennnsolver.RubiksCubeNNNOdd.subprocess.Popen", side_effect=fake_popen),
        ):
            fake_777.lt_UD_oblique_edge_pairing.solve_via_c()

        self.assertEqual(captured["cmd"][0], "./ida_search_777_UD_centers_stage")
        self.assertIn("--obliques-only", captured["cmd"])
        self.assertEqual(captured["cmd"][captured["cmd"].index("--multiplier") + 1], "1.3")
        self.assertNotIn("--left-oblique-outer-x-cost", captured["cmd"])
        self.assertEqual(len(UD_OBLIQUE_ONLY_TABLES_777), 3)
        for flag, filename in UD_OBLIQUE_ONLY_TABLES_777:
            self.assertIn(flag, captured["cmd"])
            self.assertIn(filename, captured["cmd"])
            self.assertNotIn("outer-x", flag)

    def test_777_combined_ud_phase_can_try_admissible_search_first(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        captured = {}

        class FakeProc:
            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def communicate(self, timeout=None):
                captured["timeout"] = timeout
                return ("SOLUTION (0 steps):\n", None)

        def fake_popen(cmd, **_kwargs):
            captured["cmd"] = cmd
            return FakeProc()

        with (
            patch("rubikscubennnsolver.RubiksCube777.download_file_if_needed"),
            patch("rubikscubennnsolver.RubiksCube777.subprocess.Popen", side_effect=fake_popen),
        ):
            cube.lt_UD_obliques_outer_x_stage.solve_via_c(admissible_seconds=0.5)

        self.assertEqual(captured["cmd"][0], "./ida_search_777_UD_centers_stage")
        self.assertNotIn("--obliques-only", captured["cmd"])
        self.assertNotIn("--multiplier", captured["cmd"])
        self.assertNotIn("--pair-cost-matrix", captured["cmd"])
        self.assertEqual(captured["timeout"], 0.5)
        for flag, filename in UD_PHASE56_TABLES_777:
            self.assertIn(flag, captured["cmd"])
            self.assertIn(filename, captured["cmd"])

    def test_777_combined_ud_phase_falls_back_to_pair_cost_matrix(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        commands = []

        class TimeoutProc:
            def __init__(self):
                self.killed = False

            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def communicate(self, timeout=None):
                if not self.killed:
                    raise subprocess.TimeoutExpired(cmd="ida", timeout=timeout)
                return ("", None)

            def kill(self):
                self.killed = True

        class SolvedProc:
            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def communicate(self, timeout=None):
                commands.append(("timeout", timeout))
                return ("SOLUTION (2 steps): U U'\n", None)

        procs = [TimeoutProc(), SolvedProc()]

        def fake_popen(cmd, **_kwargs):
            commands.append(cmd)
            return procs.pop(0)

        with (
            patch("rubikscubennnsolver.RubiksCube777.download_file_if_needed"),
            patch("rubikscubennnsolver.RubiksCube777.subprocess.Popen", side_effect=fake_popen),
        ):
            cube.lt_UD_obliques_outer_x_stage.solve_via_c(admissible_seconds=0.5)

        self.assertTrue(procs == [])
        self.assertNotIn("--multiplier", commands[0])
        self.assertNotIn("--pair-cost-matrix", commands[0])
        self.assertEqual(commands[1][commands[1].index("--pair-cost-matrix") + 1], PHASE56_PAIR_COST_MATRIX_777)
        self.assertNotIn("--multiplier", commands[1])
        self.assertEqual(commands[2], ("timeout", None))
        self.assertEqual(cube.solution, ["U", "U'"])

    def test_777_combined_ud_phase_can_start_with_matrix(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        commands = []

        class SolvedProc:
            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def communicate(self, timeout=None):
                return ("SOLUTION (1 steps): U\n", None)

        with (
            patch("rubikscubennnsolver.RubiksCube777.download_file_if_needed"),
            patch(
                "rubikscubennnsolver.RubiksCube777.subprocess.Popen",
                side_effect=lambda cmd, **_kwargs: commands.append(cmd) or SolvedProc(),
            ),
        ):
            _root, steps = cube.lt_UD_obliques_outer_x_stage.solution_via_c(admissible_seconds=0)

        self.assertEqual(steps, ("U",))
        self.assertEqual(len(commands), 1)
        self.assertIn("--pair-cost-matrix", commands[0])

    def test_777_combined_ud_phase_recolors_four_coordinates(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        combined = cube.lt_UD_obliques_outer_x_stage

        self.assertEqual(combined.avoid_oll, 0)
        combined.recolor()

        tracked = UFBD_left_oblique_777 + UFBD_middle_oblique_777 + UFBD_right_oblique_777 + UFBD_outer_x_centers_777
        for square in tracked:
            expected = "U" if square < 50 or square > 245 else "x"
            self.assertEqual(cube.state[square], expected)

    def test_777_ud_phase_stages_obliques_without_outer_x(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        captured = {}

        class FakeProc:
            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def communicate(self, timeout=None):
                captured["timeout"] = timeout
                return ("SOLUTION (0 steps):\n", None)

        def fake_popen(cmd, **_kwargs):
            captured["cmd"] = cmd
            return FakeProc()

        with (
            patch("rubikscubennnsolver.RubiksCube777.download_file_if_needed"),
            patch("rubikscubennnsolver.RubiksCube777.subprocess.Popen", side_effect=fake_popen),
        ):
            cube.lt_UD_obliques_outer_x_stage.solve_via_c(obliques_only=True)

        self.assertIn("--obliques-only", captured["cmd"])
        self.assertNotIn("--multiplier", captured["cmd"])
        self.assertNotIn("--pair-cost-matrix", captured["cmd"])
        self.assertNotIn("--left-oblique-outer-x-cost", captured["cmd"])
        self.assertIsNone(captured["timeout"])
        for flag, filename in UD_OBLIQUE_ONLY_TABLES_777:
            self.assertIn(flag, captured["cmd"])
            self.assertIn(filename, captured["cmd"])

    def test_777_stage_ud_centers_stages_outer_x(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        seen = {}

        def fake_solve(obliques_only=False, **_kwargs):
            seen["obliques_only"] = obliques_only

        with (
            patch.object(cube, "UD_obliques_staged", return_value=False),
            patch.object(cube.lt_UD_obliques_outer_x_stage, "solve_via_c", side_effect=fake_solve),
        ):
            cube.stage_UD_centers()

        self.assertFalse(seen["obliques_only"])

    def test_777_stage_ud_centers_applies_the_phase3_root_phase5_keeps(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        cube._phase3_portfolio = [("U",), ("Uw",)]

        def fake_solution(roots):
            self.assertEqual([index for index, _kociemba, _orbits in roots], [0, 1])
            return (1, ("F",))

        with patch.object(cube.lt_UD_obliques_outer_x_stage, "solution_via_c", side_effect=fake_solution):
            cube.stage_UD_centers()

        self.assertEqual(cube.solution[0], "Uw")
        self.assertIn("F", cube.solution)
        self.assertTrue(any(step.startswith("COMMENT_LR_obliques_and_outer_x_staged") for step in cube.solution))
        self.assertTrue(any(step.startswith("COMMENT_UD_centers_staged") for step in cube.solution))
        self.assertIsNone(cube._phase3_portfolio)

    def test_777_phase3_stages_lr_obliques(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        captured = {}

        class FakeProc:
            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def communicate(self, timeout=None):
                captured["timeout"] = timeout
                return ("SOLUTION (1 steps): U\n", None)

        def fake_popen(cmd, **_kwargs):
            captured["cmd"] = cmd
            return FakeProc()

        with (
            patch.object(cube, "LR_inside_centers_staged", return_value=False),
            patch.object(cube, "UD_inside_centers_staged", return_value=False),
            patch.object(cube, "LR_obliques_staged", return_value=False),
            patch.object(cube, "LR_outer_x_staged", return_value=False),
            patch.object(cube, "_inside_lr_center_solutions", return_value=[((), "STATE", set())]),
            patch.object(
                cube.lt_LR_oblique_edges_UD_inner_centers_stage,
                "solution_via_c",
                return_value=(0, ()),
            ),
            patch.object(cube, "center_solution_leads_to_oll_parity", return_value={0}),
            patch("rubikscubennnsolver.RubiksCube777.subprocess.Popen", side_effect=fake_popen),
        ):
            cube.stage_LR_centers()

        self.assertEqual(captured["cmd"][0], "./ida_search_777_centers_stage")
        self.assertIn("--stage-lr-obliques", captured["cmd"])
        self.assertIn("--initial-orbit0-odd", captured["cmd"])
        self.assertEqual(captured["cmd"][captured["cmd"].index("--solution-count") + 1], "8")
        self.assertIsNone(captured["timeout"])
        self.assertEqual(cube._phase3_portfolio, [("U",)])
        self.assertNotIn("U", cube.solution)

    def test_nnnodd_keeps_outer_x_center_staging(self):
        cube = RubiksCube777ForNNNOdd(solved_777, "URFDLB")
        cube.lt_init()
        seen = {}

        def fake_solve(obliques_only=False, **_kwargs):
            seen["obliques_only"] = obliques_only

        self.assertTrue(cube.stage_outer_x_centers)
        with (
            patch.object(cube, "UD_centers_staged", return_value=False),
            patch.object(cube, "group_inside_UD_centers"),
            patch.object(cube.lt_UD_obliques_outer_x_stage, "solve_via_c", side_effect=fake_solve),
        ):
            cube.stage_UD_centers()

        self.assertFalse(seen["obliques_only"])

    def test_777_combined_daisy_replaces_serial_bar_phases(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        cube.lt_init()
        daisy = cube.lt_daisy_centers

        # One cost table plus its symmetry index, shared by all three axes,
        # plus the inner-x spine and the four mixed-axis 70^5 tables.
        self.assertEqual(len(DAISY_PERFECT_TABLES_777), 2)
        self.assertEqual(DAISY_INNER_X_SPINE_TABLE_777[0], "--inner-x-spine-cost")
        self.assertEqual(len(DAISY_MIXED_TABLES_777), 4)
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

    def test_phase8_starts_without_old_center_tables(self):
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

        self.assertEqual(len(commands), 6)
        self.assertNotIn(
            "--allow-duplicate-solutions",
            daisy._command(8, native_only=False, solution_count=16),
        )
        self.assertIn(
            "--allow-duplicate-solutions",
            daisy._command(8, native_only=False, solution_count=16, distinct=False),
        )
        retired = [filename for _, filename in NATIVE_SOLVE_PERFECT_TABLES_777 + DAISY_PERFECT_TABLES_777]
        retired.append(DAISY_INNER_X_SPINE_TABLE_777[1])
        retired.extend(filename for _, filename in DAISY_MIXED_TABLES_777)
        for index in (0, 3):
            self.assertIn("--phase7", commands[index])
            self.assertNotIn("--phase8", commands[index])
            self.assertNotIn("--phase9", commands[index])
            self.assertNotIn("--native-only", commands[index])
            self.assertIn(DAISY_LR_INNER_TABLE_777[1], commands[index])
            self.assertIn("--lr-inner-cost", commands[index])
            self.assertNotIn("--multiplier", commands[index])
            self.assertEqual(commands[index][commands[index].index("--solution-count") + 1], "16")
        for index in (1, 4):
            self.assertIn("--phase8", commands[index])
            self.assertNotIn("--phase9", commands[index])
            self.assertNotIn("--native-only", commands[index])
            self.assertEqual(commands[index][commands[index].index("--multiplier") + 1], "1.2")
            self.assertEqual(commands[index][commands[index].index("--solution-count") + 1], "16")
            for flag, filename in PHASE8_PAIRED_TABLES_777 + PHASE8_INNER_OBLIQUE_TABLES_777:
                self.assertIn(flag, commands[index])
                self.assertIn(filename, commands[index])
            self.assertIn("--inner-interaction-cost", commands[index])
            self.assertIn(PHASE8_INNER_INTERACTION_TABLE_777[1], commands[index])
            for flag, filename in PHASE8_TABLES_777:
                if flag == "--inner-interaction-cost":
                    continue
                self.assertNotIn(flag, commands[index])
                self.assertNotIn(filename, commands[index])
        self.assertIn("--phase9", commands[2])
        self.assertIn("--phase9", commands[5])
        self.assertNotIn("--multiplier", commands[2])
        self.assertNotIn("--multiplier", commands[5])
        self.assertIn("--native-only", commands[2])
        self.assertNotIn("--native-only", commands[5])
        for flag, filename in PHASE9_TABLES_777:
            self.assertIn(flag, commands[2])
            self.assertIn(filename, commands[2])
            self.assertIn(flag, commands[5])
            self.assertIn(filename, commands[5])
        for _flag, filename in PHASE8_TABLES_777:
            self.assertNotIn(filename, commands[2])
            self.assertNotIn(filename, commands[5])
        for filename in retired:
            for index in (1, 2, 4, 5):
                self.assertNotIn(filename, commands[index])
                self.assertNotIn("--perfect-cost", commands[index])
                self.assertNotIn(DAISY_INNER_X_SPINE_TABLE_777[0], commands[index])


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

        def rank(self):
            return self.state_index()

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


class PhaseOne444Test(unittest.TestCase):
    def test_reduce_333_runs_phase1_then_phase2(self):
        from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444

        cube = RubiksCube444(solved_444, "URFDLB")
        calls = []
        with (
            patch.object(cube, "reduced_to_333", return_value=False),
            patch.object(cube, "phase1", side_effect=lambda: calls.append("1")),
            patch.object(cube, "phase2", side_effect=lambda **_kwargs: calls.append("2")),
        ):
            cube.reduce_333()
        self.assertEqual(calls, ["1", "2"])


class InnerXFake444MappingTest(unittest.TestCase):
    def test_444_wide_turns_map_to_666_three_layer_turns(self):
        from rubikscubennnsolver.RubiksCube444 import centers_444, moves_444, rotate_444, solved_444
        from rubikscubennnsolver.RubiksCube666 import inner_x_centers_666, rotate_666, solved_666

        state_444 = ["x", *solved_444]
        state_666 = ["x", *solved_666]
        for label, (square_444, square_666) in enumerate(zip(centers_444, inner_x_centers_666)):
            marker = chr(65 + label)
            state_444[square_444] = marker
            state_666[square_666] = marker

        for move_444 in moves_444:
            with self.subTest(move=move_444):
                move_666 = f"3{move_444}" if "w" in move_444 else move_444
                moved_444 = rotate_444(state_444, move_444)
                moved_666 = rotate_666(state_666, move_666)
                self.assertEqual(
                    [moved_444[square] for square in centers_444],
                    [moved_666[square] for square in inner_x_centers_666],
                )

    def test_phase_two_goal_helpers_recognize_solved_cube(self):
        cube = RubiksCube666(solved_666, "URFDLB")
        self.assertTrue(cube.LR_inner_x_centers_staged())
        self.assertTrue(cube.inner_x_centers_staged())
        self.assertTrue(cube.LR_obliques_paired())


class PhaseTwo444Test(unittest.TestCase):
    class FakeCube:
        def __init__(self):
            self.state = ["start"]
            self.solution = []
            self.solve_via_c_output = ""

        def get_kociemba_string(self, _all_squares):
            return "U" * 96

        def rotate(self, move):
            self.solution.append(move)
            self.state[0] = " ".join(self.solution)

        def reduced_to_333(self):
            return True

        def edge_solution_leads_to_pll_parity(self):
            return self.state[0] == "A B"

        def print_cube_add_comment(self, comment, start):
            self.solution.append(f"COMMENT_{comment}")

    def test_fake_444_phase2_requests_one_pll_free_solution(self):
        from rubikscubennnsolver.RubiksCube444 import RubiksCube444

        cube = self.FakeCube()

        class FakeProc:
            def __init__(self):
                self.stdout = iter(["SOLUTION (3 steps): C D E\n"])

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def terminate(self):
                pass

            def wait(self):
                return 0

        with (
            patch("rubikscubennnsolver.RubiksCube444.download_file_if_needed"),
            patch("rubikscubennnsolver.RubiksCube444.subprocess.Popen", return_value=FakeProc()) as popen,
        ):
            RubiksCube444.phase2(cube, consider_solve_333=False)

        command = popen.call_args.args[0]
        self.assertIn("--avoid-pll", command)
        self.assertNotIn("--solution-count", command)
        self.assertEqual(cube.solution, ["C", "D", "E", "COMMENT_all edges paired, centers solved"])


class PhaseThreePortfolioTest(unittest.TestCase):
    class FakePhaseThree:
        def solutions_via_c(self, solution_count):
            assert solution_count == 64
            return [(("A",), ()), (("B",), ()), (("C",), ())]

    class Fake555:
        def __init__(self):
            self.lt_LR_centers_stage = PhaseThreePortfolioTest.FakePhaseThree()

    class FakePhaseFour:
        def __init__(self):
            self.roots = None

        def solution_via_c(self, roots):
            self.roots = roots
            return 1, ("P1", "P2")

    class FakeCube:
        def __init__(self):
            self.state = ["x"] * 217
            self.solution = []
            self.fake_555 = PhaseThreePortfolioTest.Fake555()
            self.lt_UD_centers_stage = PhaseThreePortfolioTest.FakePhaseFour()

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

    def test_phase_three_portfolio_deduplicates_roots_and_applies_selected_prefix(self):
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
