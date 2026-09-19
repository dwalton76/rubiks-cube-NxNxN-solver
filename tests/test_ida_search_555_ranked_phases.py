# standard libraries
import math
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# rubiks cube libraries
import rubikscubennnsolver.RubiksCube555 as cube555_module
from rubikscubennnsolver.RubiksCube555 import (
    LookupTable555EdgeOrientInnerOrbit,
    LookupTable555EdgeOrientOuterOrbit,
    LookupTable555Phase3LRCenterStage,
    LookupTable555Phase4,
    RubiksCube555,
    UFBD_t_centers_555,
    UFBD_x_centers_555,
    solved_555,
    t_centers_without_middles_555,
    x_centers_without_middles_555,
)
from rubikscubennnsolver.swaps import swaps_555

ROOT = Path(__file__).resolve().parents[1]
PHASE1 = ROOT / "ida_search_555_phase1"
PHASE2 = ROOT / "ida_search_555_phase2"
PHASE3 = ROOT / "ida_search_555_phase3"
PHASE4 = ROOT / "ida_search_555_phase4"
PHASE5 = ROOT / "ida_search_555_phase5"
PHASE6 = ROOT / "ida_search_555_phase6"
PHASE1_UNIVERSE = math.comb(24, 8)
PHASE2_UNIVERSE = math.comb(16, 8)
PHASE5_CENTERS_UNIVERSE = 70**4
PHASE5_COMBO_UNIVERSE = 70 * 70 * 1680 * 70
PHASE6_EDGE_UNIVERSE = 812_851_200
PHASE6_CENTER_UNIVERSE = 176_400
PHASE2_ILLEGAL = {"Uw", "Uw'", "Fw", "Fw'", "Bw", "Bw'", "Dw", "Dw'"}
PHASE5_LEGAL = {
    "U2",
    "Uw2",
    "L2",
    "Lw2",
    "F",
    "F'",
    "F2",
    "Fw2",
    "R2",
    "Rw2",
    "B",
    "B'",
    "B2",
    "Bw2",
    "D2",
    "Dw2",
}
PHASE6_LEGAL = {
    "U",
    "U'",
    "U2",
    "L2",
    "Lw2",
    "F2",
    "Fw2",
    "R2",
    "Rw2",
    "B2",
    "Bw2",
    "D",
    "D'",
    "D2",
}


def rank_selected(values, selected):
    rank = 0
    remaining = 8
    for position, value in enumerate(values):
        if value in selected:
            remaining -= 1
        elif remaining:
            rank += math.comb(len(values) - position - 1, remaining - 1)
    if remaining:
        raise ValueError("coordinate must contain eight selected stickers")
    return rank


def sparse_cost_file(path, universe, ranks, encoded=1):
    exists = path.exists()
    with open(path, "r+b" if exists else "wb") as table:
        if not exists:
            table.truncate(universe)
        for rank in ranks:
            table.seek(rank)
            table.write(bytes((encoded,)))


def multiset_rank(values, symbols, counts):
    remaining = list(counts)
    permutations = math.factorial(sum(counts))
    for count in counts:
        permutations //= math.factorial(count)
    rank = 0

    for position, value in enumerate(values):
        slots = len(values) - position
        symbol_index = symbols.index(value)
        for smaller in range(symbol_index):
            rank += permutations * remaining[smaller] // slots
        permutations = permutations * remaining[symbol_index] // slots
        remaining[symbol_index] -= 1
    return rank


def phase5_permuted_rank(move, squares, values, partners=None):
    cube = ["x"] * 151
    for position, square in enumerate(squares):
        cube[square] = values[position]
        if partners:
            cube[partners[position]] = values[position]
    moved = [cube[index] for index in swaps_555[move]]
    return [moved[square] for square in squares]


def combo_unrank(rank):
    occupancy = rank % 70
    rank //= 70
    wing = rank % 1680
    rank //= 1680
    fb_x = rank % 70
    fb_t = rank // 70
    return fb_t, fb_x, wing, occupancy


def occupancy_unrank(rank, n=8, k=4):
    mask = 0
    remaining = k
    for position in range(n):
        if not remaining:
            break
        after = n - position - 1
        selected_prefix = math.comb(after, remaining - 1)
        if rank < selected_prefix:
            mask |= 1 << position
            remaining -= 1
        else:
            rank -= selected_prefix
    return mask


def occupancy_to_labeled(rank):
    mask = occupancy_unrank(rank)
    labels = iter("ABCD")
    return "".join(next(labels) if mask & (1 << index) else "x" for index in range(8))


def fields(stdout, prefix):
    line = next(line for line in stdout.splitlines() if line.startswith(prefix))
    tokens = line.split()
    return {tokens[index]: tokens[index + 1] for index in range(0, len(tokens), 2)}
    line = next(line for line in stdout.splitlines() if line.startswith(prefix))
    tokens = line.split()
    return {tokens[index]: tokens[index + 1] for index in range(0, len(tokens), 2)}


class Ranked555PythonWiringTest(unittest.TestCase):
    def setUp(self):
        self.cube = RubiksCube555(solved_555, "URFDLB")
        with patch("rubikscubennnsolver.RubiksCube555.download_file_if_needed"):
            self.cube.lt_init()

    def test_t_center_only_wrapper_uses_phase1_binary(self):
        with (
            patch.object(cube555_module, "download_file_if_needed"),
            patch.object(
                cube555_module.subprocess,
                "check_output",
                return_value=b"SOLUTION (0 steps):\n",
            ) as check_output,
        ):
            solutions = self.cube.lt_LR_t_centers_stage_ida.solutions_via_c()

        command = check_output.call_args.args[0]
        self.assertEqual(command[0], "./ida_search_555_phase1")
        self.assertIn("--t-centers-only", command)
        self.assertNotIn("--x-center-cost", command)
        self.assertEqual(solutions, [((), (None,) * 5)])

    def test_phase2_wrapper_maps_solution_back_to_ranked_root(self):
        with (
            patch.object(cube555_module, "download_file_if_needed"),
            patch.object(
                cube555_module.subprocess,
                "check_output",
                return_value=b"SOLUTION ROOT 1 (2 steps): U2 F2\n",
            ),
        ):
            solutions = self.cube.lt_FB_centers_stage.solutions_via_c(
                pt_states=[(5, 6), (3, 4)],
            )

        self.assertEqual(solutions, [(("U2", "F2"), (5, 6, None, None, None))])

    def test_phase3_wrapper_uses_phase3_binary(self):
        expected_root = (
            self.cube.lt_phase3_lr_center_stage.rank(),
            self.cube.lt_phase3_eo_outer_orbit.rank(),
            self.cube.lt_phase3_eo_inner_orbit.rank(),
        )
        with (
            patch.object(cube555_module, "download_file_if_needed"),
            patch.object(
                cube555_module.subprocess,
                "check_output",
                return_value=b"SOLUTION ROOT 0 (0 steps):\n",
            ) as check_output,
        ):
            solutions = self.cube.lt_phase3.solutions_via_c()

        command = check_output.call_args.args[0]
        self.assertEqual(command[0], "./ida_search_555_phase3")
        self.assertIn("--roots-file", command)
        self.assertEqual(solutions, [((), expected_root + (None, None))])

    def test_phase4_wrapper_batches_combinations(self):
        combos = (("UB", "UL", "UR", "UF"), ("DB", "DL", "DR", "DF"))
        with (
            patch.object(cube555_module, "download_file_if_needed"),
            patch.object(
                cube555_module.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    args=(), returncode=0, stdout="SOLUTION ROOT 1 (0 steps):\n", stderr=""
                ),
            ) as run,
        ):
            results = self.cube.lt_phase4.solutions_via_c(combos)

        command = run.call_args.args[0]
        self.assertEqual(command[0], "./ida_search_555_phase4")
        self.assertIn("--roots-file", command)
        self.assertEqual(results, [(0, ["DB", "DF", "DL", "DR"], ())])

    def test_phase5_rank_and_wrapper_use_three_ranked_tables(self):
        self.assertEqual(
            self.cube.lt_phase5.ranks(("LB", "LF", "RB", "RF")),
            (4899, 576219265, 576214855, 1320),
        )
        completed = subprocess.CompletedProcess(
            [],
            0,
            stdout="SOLUTION ROOT 1 (2 steps): U2 F2\n",
            stderr="",
        )
        with (
            patch.object(cube555_module, "download_file_if_needed"),
            patch.object(cube555_module.subprocess, "run", return_value=completed) as run,
        ):
            solutions = self.cube.lt_phase5.solutions_via_c(
                [(5, 6, 7, 8), (3, 4, 5, 6)],
                solution_count=500,
                find_extra=True,
            )

        command = run.call_args.args[0]
        self.assertEqual(command[0], "./ida_search_555_phase5")
        self.assertIn("--centers-cost", command)
        self.assertIn("--high-combo-cost", command)
        self.assertIn("--low-combo-cost", command)
        self.assertIn("--find-extra", command)
        self.assertEqual(solutions, [(("U2", "F2"), (5, 6, 7, 8))])

    def test_phase6_rank_and_wrapper_use_two_ranked_tables(self):
        expected_root = self.cube.lt_phase6.ranks()
        self.assertEqual(expected_root, (0, 29399))
        completed = subprocess.CompletedProcess(
            [],
            0,
            stdout="SOLUTION ROOT 0 (2 steps): U2 F2\n",
            stderr="",
        )
        with (
            patch.object(cube555_module, "download_file_if_needed"),
            patch.object(cube555_module.subprocess, "run", return_value=completed) as run,
        ):
            solutions = self.cube.lt_phase6.solutions_via_c([expected_root])

        command = run.call_args.args[0]
        self.assertEqual(command[0], "./ida_search_555_phase6")
        self.assertIn("--edge-cost", command)
        self.assertIn("--center-cost", command)
        self.assertNotIn("--prune-table-perfect-hash01", command)
        self.assertEqual(solutions, [(("U2", "F2"), expected_root)])


@unittest.skipUnless(PHASE1.is_file() and PHASE2.is_file(), "5x5 ranked solvers have not been built")
class Ranked555PhasesTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        self.cube = RubiksCube555(solved_555, "URFDLB")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_phase1_rank_and_zero_solution(self):
        t_rank = rank_selected(
            [self.cube.state[square] for square in t_centers_without_middles_555],
            {"L", "R"},
        )
        x_rank = rank_selected(
            [self.cube.state[square] for square in x_centers_without_middles_555],
            {"L", "R"},
        )
        t_path = self.directory / "phase1-t.bin"
        x_path = self.directory / "phase1-x.bin"
        sparse_cost_file(t_path, PHASE1_UNIVERSE, [t_rank])
        sparse_cost_file(x_path, PHASE1_UNIVERSE, [x_rank])

        result = subprocess.run(
            [
                str(PHASE1),
                "--kociemba",
                self.cube.get_kociemba_string(True),
                "--t-center-cost",
                str(t_path),
                "--x-center-cost",
                str(x_path),
                "--max-ida-threshold",
                "0",
                "--print-ranks",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = fields(result.stdout, "T_RANK ")
        self.assertEqual(int(actual["T_RANK"]), t_rank)
        self.assertEqual(int(actual["X_RANK"]), x_rank)
        self.assertIn("SOLUTION (0 steps):", result.stdout)

    def test_phase1_t_centers_only_does_not_require_x_table(self):
        t_rank = rank_selected(
            [self.cube.state[square] for square in t_centers_without_middles_555],
            {"L", "R"},
        )
        t_path = self.directory / "phase1-t-only.bin"
        sparse_cost_file(t_path, PHASE1_UNIVERSE, [t_rank])

        result = subprocess.run(
            [
                str(PHASE1),
                "--kociemba",
                self.cube.get_kociemba_string(True),
                "--t-center-cost",
                str(t_path),
                "--t-centers-only",
                "--max-ida-threshold",
                "0",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION (0 steps):", result.stdout)

    def test_phase2_multiple_roots_and_legal_moves(self):
        t_rank = rank_selected(
            [self.cube.state[square] for square in UFBD_t_centers_555],
            {"F", "B"},
        )
        x_rank = rank_selected(
            [self.cube.state[square] for square in UFBD_x_centers_555],
            {"F", "B"},
        )
        t_path = self.directory / "phase2-t.bin"
        x_path = self.directory / "phase2-x.bin"
        roots_path = self.directory / "roots.txt"
        sparse_cost_file(t_path, PHASE2_UNIVERSE, [t_rank])
        sparse_cost_file(x_path, PHASE2_UNIVERSE, [x_rank])
        roots_path.write_text(f"alpha,{t_rank},{x_rank}\nbeta,{t_rank},{x_rank}\n")

        result = subprocess.run(
            [
                str(PHASE2),
                "--roots-file",
                str(roots_path),
                "--t-center-cost",
                str(t_path),
                "--x-center-cost",
                str(x_path),
                "--orbit0-need-even-w",
                "--max-ida-threshold",
                "0",
                "--print-ranks",
                "--print-legal-moves",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ROOT alpha T_RANK", result.stdout)
        self.assertIn("SOLUTION ROOT alpha (0 steps):", result.stdout)
        legal_line = next(line for line in result.stdout.splitlines() if line.startswith("LEGAL_MOVES"))
        self.assertFalse(PHASE2_ILLEGAL.intersection(legal_line.split()[1:]))

    def test_one_move_search_and_orbit0_parity(self):
        for binary, squares, selected, universe, parity_flag, move in (
            (PHASE1, t_centers_without_middles_555, {"L", "R"}, PHASE1_UNIVERSE, None, "Uw"),
            (
                PHASE2,
                UFBD_t_centers_555,
                {"F", "B"},
                PHASE2_UNIVERSE,
                "--orbit0-need-odd-w",
                "Lw",
            ),
        ):
            moved = RubiksCube555(solved_555, "URFDLB")
            moved.rotate(move)
            other_squares = x_centers_without_middles_555 if binary == PHASE1 else UFBD_x_centers_555
            solved_ranks = (
                rank_selected([self.cube.state[square] for square in squares], selected),
                rank_selected([self.cube.state[square] for square in other_squares], selected),
            )
            moved_ranks = (
                rank_selected([moved.state[square] for square in squares], selected),
                rank_selected([moved.state[square] for square in other_squares], selected),
            )
            t_path = self.directory / f"{binary.name}-move-t.bin"
            x_path = self.directory / f"{binary.name}-move-x.bin"
            sparse_cost_file(t_path, universe, solved_ranks[:1])
            sparse_cost_file(x_path, universe, solved_ranks[1:])
            if moved_ranks[0] != solved_ranks[0]:
                sparse_cost_file(t_path, universe, moved_ranks[:1], encoded=2)
            if moved_ranks[1] != solved_ranks[1]:
                sparse_cost_file(x_path, universe, moved_ranks[1:], encoded=2)
            command = [
                str(binary),
                "--kociemba",
                moved.get_kociemba_string(True),
                "--t-center-cost",
                str(t_path),
                "--x-center-cost",
                str(x_path),
                "--max-ida-threshold",
                "1",
            ]
            if parity_flag:
                command.append(parity_flag)
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"{binary.name}\n{result.stdout}{result.stderr}")
            self.assertRegex(result.stdout, rf"SOLUTION(?: ROOT 0)? \(1 steps\): {move}'?")

    @unittest.skipUnless(PHASE3.is_file(), "5x5 phase-3 solver has not been built")
    def test_phase3_zero_solution_from_roots_file(self):
        lr_rank = LookupTable555Phase3LRCenterStage(self.cube).rank()
        outer_rank = LookupTable555EdgeOrientOuterOrbit(self.cube).rank()
        inner_rank = LookupTable555EdgeOrientInnerOrbit(self.cube).rank()
        lr_path = self.directory / "phase3-lr.bin"
        outer_path = self.directory / "phase3-outer.bin"
        inner_path = self.directory / "phase3-inner.bin"
        sparse_cost_file(lr_path, 4900, [lr_rank])
        sparse_cost_file(outer_path, 2704156, [outer_rank])
        sparse_cost_file(inner_path, 4096, [inner_rank])
        roots_path = self.directory / "phase3-roots.txt"
        roots_path.write_text(f"0,{lr_rank},{outer_rank},{inner_rank}\n")
        result = subprocess.run(
            [
                str(PHASE3),
                "--roots-file",
                str(roots_path),
                "--lr-center-cost",
                str(lr_path),
                "--eo-outer-cost",
                str(outer_path),
                "--eo-inner-cost",
                str(inner_path),
                "--max-ida-threshold",
                "0",
                "--print-ranks",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION ROOT 0 (0 steps):", result.stdout)

    @unittest.skipUnless(PHASE3.is_file(), "5x5 phase-3 solver has not been built")
    def test_phase3_uses_cheapest_root_not_the_max_heuristic(self):
        lr_rank = LookupTable555Phase3LRCenterStage(self.cube).rank()
        outer_rank = LookupTable555EdgeOrientOuterOrbit(self.cube).rank()
        inner_rank = LookupTable555EdgeOrientInnerOrbit(self.cube).rank()
        expensive_lr = 1 if lr_rank != 1 else 2
        lr_path = self.directory / "phase3-lr-cheapest.bin"
        outer_path = self.directory / "phase3-outer-cheapest.bin"
        inner_path = self.directory / "phase3-inner-cheapest.bin"
        sparse_cost_file(lr_path, 4900, [lr_rank])
        sparse_cost_file(lr_path, 4900, [expensive_lr], encoded=6)
        sparse_cost_file(outer_path, 2704156, [outer_rank])
        sparse_cost_file(inner_path, 4096, [inner_rank])
        roots_path = self.directory / "phase3-mixed-roots.txt"
        roots_path.write_text(
            f"expensive,{expensive_lr},{outer_rank},{inner_rank}\n" f"cheap,{lr_rank},{outer_rank},{inner_rank}\n"
        )
        result = subprocess.run(
            [
                str(PHASE3),
                "--roots-file",
                str(roots_path),
                "--lr-center-cost",
                str(lr_path),
                "--eo-outer-cost",
                str(outer_path),
                "--eo-inner-cost",
                str(inner_path),
                "--max-ida-threshold",
                "20",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION ROOT cheap (0 steps):", result.stdout)
        self.assertNotIn("SOLUTION ROOT expensive", result.stdout)

    @unittest.skipUnless(PHASE4.is_file(), "5x5 phase-4 solver has not been built")
    def test_phase4_zero_solution_from_ranked_root(self):
        phase4 = LookupTable555Phase4(self.cube)
        combo = ("UB", "UL", "UR", "UF")
        rank = phase4.rank(combo)
        cost_path = self.directory / "phase4.bin"
        roots_path = self.directory / "phase4-roots.txt"
        sparse_cost_file(cost_path, 495**3, [rank])
        roots_path.write_text(f"four,{rank}\n")
        result = subprocess.run(
            [
                str(PHASE4),
                "--roots-file",
                str(roots_path),
                "--cost-table",
                str(cost_path),
                "--max-ida-threshold",
                "0",
                "--print-ranks",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"ROOT four RANK {rank} COST 0", result.stdout)
        self.assertIn("SOLUTION ROOT four (0 steps):", result.stdout)


@unittest.skipUnless(PHASE5.is_file(), "5x5 phase-5 solver has not been built")
class Ranked555Phase5Test(unittest.TestCase):
    center_groups = (
        (33, 37, 39, 43, 83, 87, 89, 93),
        (32, 34, 42, 44, 82, 84, 92, 94),
        (58, 62, 64, 68, 108, 112, 114, 118),
        (57, 59, 67, 69, 107, 109, 117, 119),
    )
    high_squares = (2, 24, 35, 41, 85, 91, 127, 149)
    high_partners = (104, 54, 56, 120, 106, 70, 72, 122)
    low_squares = (4, 22, 31, 45, 81, 95, 129, 147)
    low_partners = (102, 52, 110, 66, 60, 116, 74, 124)
    midge_squares = (3, 23, 36, 40, 86, 90, 128, 148)
    midge_partners = (103, 53, 115, 61, 65, 111, 73, 123)

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        self.centers_path = self.directory / "phase5-centers.bin"
        self.high_path = self.directory / "phase5-high.bin"
        self.low_path = self.directory / "phase5-low.bin"

    def tearDown(self):
        self.tempdir.cleanup()

    def command(self, roots_path):
        return [
            str(PHASE5),
            "--roots-file",
            str(roots_path),
            "--centers-cost",
            str(self.centers_path),
            "--high-combo-cost",
            str(self.high_path),
            "--low-combo-cost",
            str(self.low_path),
        ]

    def write_zero_costs(self, centers_ranks, high_ranks, low_ranks):
        sparse_cost_file(self.centers_path, PHASE5_CENTERS_UNIVERSE, centers_ranks)
        sparse_cost_file(self.high_path, PHASE5_COMBO_UNIVERSE, high_ranks)
        sparse_cost_file(self.low_path, PHASE5_COMBO_UNIVERSE, low_ranks)

    @staticmethod
    def exact_goal_ranks():
        midge_binary = multiset_rank("xxLLLLxx", "Lx", (4, 4))
        high_wing = multiset_rank("xxBADCxx", "ABCDx", (1, 1, 1, 1, 4))
        low_wing = multiset_rank("xxABCDxx", "ABCDx", (1, 1, 1, 1, 4))
        return high_wing * 70 + midge_binary, low_wing * 70 + midge_binary, low_wing

    @staticmethod
    def relative_combo(fb_t, fb_x, wing_state, midge_state):
        label_map = {}
        occupancy = []
        for char in midge_state:
            if char == "x":
                occupancy.append("x")
                continue
            if char not in label_map:
                label_map[char] = "ABCD"[len(label_map)]
            occupancy.append("L")
        canon = "".join("x" if char == "x" else label_map[char] for char in wing_state)
        wing_rank = multiset_rank(canon, "ABCDx", (1, 1, 1, 1, 4))
        midge_rank = multiset_rank("".join(occupancy), "Lx", (4, 4))
        return (((fb_t * 70) + fb_x) * 1680 + wing_rank) * 70 + midge_rank

    def test_phase5_rank_boundaries_and_legal_moves(self):
        centers_rank = PHASE5_CENTERS_UNIVERSE - 1
        combo_rank = PHASE5_COMBO_UNIVERSE - 1
        _, _, _, occupancy = combo_unrank(combo_rank)
        midge_rank = multiset_rank(occupancy_to_labeled(occupancy), "ABCDx", (1, 1, 1, 1, 4))
        self.write_zero_costs([centers_rank], [combo_rank], [combo_rank])
        roots_path = self.directory / "boundary-roots.txt"
        roots_path.write_text(f"boundary,{centers_rank},{combo_rank},{combo_rank},{midge_rank}\n")

        result = subprocess.run(
            self.command(roots_path)
            + [
                "--max-ida-threshold",
                "0",
                "--print-ranks",
                "--print-legal-moves",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            f"ROOT boundary CENTERS_RANK {centers_rank} HIGH_RANK {combo_rank} " f"LOW_RANK {combo_rank} COST 0",
            result.stdout,
        )
        legal_line = next(line for line in result.stdout.splitlines() if line.startswith("LEGAL_MOVES"))
        self.assertEqual(set(legal_line.split()[1:]), PHASE5_LEGAL)
        self.assertNotIn("SOLUTION ROOT boundary", result.stdout)

    def test_phase5_find_extra_collects_roots_at_minimum_threshold(self):
        high_rank, low_rank, midge_rank = self.exact_goal_ranks()
        self.write_zero_costs([0], [high_rank], [low_rank])
        roots_path = self.directory / "portfolio-roots.txt"
        roots_path.write_text(
            f"first,0,{high_rank},{low_rank},{midge_rank}\n" f"second,0,{high_rank},{low_rank},{midge_rank}\n"
        )

        result = subprocess.run(
            self.command(roots_path)
            + [
                "--max-ida-threshold",
                "0",
                "--solution-count",
                "2",
                "--find-extra",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            [line for line in result.stdout.splitlines() if line.startswith("SOLUTION ROOT")],
            [
                "SOLUTION ROOT first (0 steps):",
                "SOLUTION ROOT second (0 steps):",
            ],
        )

    def test_phase5_without_find_extra_stops_at_first_root(self):
        high_rank, low_rank, midge_rank = self.exact_goal_ranks()
        self.write_zero_costs([0], [high_rank], [low_rank])
        roots_path = self.directory / "first-root.txt"
        roots_path.write_text(
            f"first,0,{high_rank},{low_rank},{midge_rank}\n" f"second,0,{high_rank},{low_rank},{midge_rank}\n"
        )

        result = subprocess.run(
            self.command(roots_path) + ["--max-ida-threshold", "0", "--solution-count", "2"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION ROOT first (0 steps):", result.stdout)
        self.assertNotIn("SOLUTION ROOT second", result.stdout)

    def test_phase5_one_move_rank_transitions(self):
        binary_values = "LLLLxxxx"
        high_goal = "xxBADCxx"
        low_goal = "xxABCDxx"
        midge_goal = "xxABCDxx"
        center_parts = [
            multiset_rank(
                phase5_permuted_rank("F", squares, binary_values),
                "Lx",
                (4, 4),
            )
            for squares in self.center_groups
        ]
        centers_rank = 0
        for part in center_parts:
            centers_rank = centers_rank * 70 + part

        fb_parts = center_parts[2:]
        moved_midge_state = phase5_permuted_rank(
            "F",
            self.midge_squares,
            midge_goal,
            self.midge_partners,
        )
        moved_midge_rank = multiset_rank(moved_midge_state, "ABCDx", (1, 1, 1, 1, 4))

        def absolute_combo_rank(squares, partners, values):
            wing_state = phase5_permuted_rank("F", squares, values, partners)
            occupancy = "".join("x" if char == "x" else "L" for char in moved_midge_state)
            wing_rank = multiset_rank(wing_state, "ABCDx", (1, 1, 1, 1, 4))
            midge_rank = multiset_rank(occupancy, "Lx", (4, 4))
            return (((fb_parts[0] * 70) + fb_parts[1]) * 1680 + wing_rank) * 70 + midge_rank

        def relative_combo_rank(squares, partners, values):
            wing_state = phase5_permuted_rank("F", squares, values, partners)
            return self.relative_combo(fb_parts[0], fb_parts[1], wing_state, moved_midge_state)

        root_high = absolute_combo_rank(self.high_squares, self.high_partners, high_goal)
        root_low = absolute_combo_rank(self.low_squares, self.low_partners, low_goal)
        high_rank = relative_combo_rank(self.high_squares, self.high_partners, high_goal)
        low_rank = relative_combo_rank(self.low_squares, self.low_partners, low_goal)
        goal_high_rank, goal_low_rank, _ = self.exact_goal_ranks()
        self.write_zero_costs([0], [goal_high_rank], [goal_low_rank])
        if centers_rank:
            sparse_cost_file(self.centers_path, PHASE5_CENTERS_UNIVERSE, [centers_rank], encoded=2)
        if high_rank:
            sparse_cost_file(self.high_path, PHASE5_COMBO_UNIVERSE, [high_rank], encoded=2)
        if low_rank:
            sparse_cost_file(self.low_path, PHASE5_COMBO_UNIVERSE, [low_rank], encoded=2)
        roots_path = self.directory / "one-move-root.txt"
        roots_path.write_text(f"moved,{centers_rank},{root_high},{root_low},{moved_midge_rank}\n")

        result = subprocess.run(
            self.command(roots_path) + ["--max-ida-threshold", "1", "--print-ranks"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION ROOT moved (1 steps): F", result.stdout)


@unittest.skipUnless(PHASE6.is_file(), "5x5 phase-6 solver has not been built")
class Ranked555Phase6Test(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        self.edge_path = self.directory / "phase6-edges.bin"
        self.center_path = self.directory / "phase6-centers.bin"
        self.cube = RubiksCube555(solved_555, "URFDLB")
        with patch("rubikscubennnsolver.RubiksCube555.download_file_if_needed"):
            self.cube.lt_init()

    def tearDown(self):
        self.tempdir.cleanup()

    def command(self, roots_path):
        return [
            str(PHASE6),
            "--roots-file",
            str(roots_path),
            "--edge-cost",
            str(self.edge_path),
            "--center-cost",
            str(self.center_path),
        ]

    def write_costs(self, edge_ranks, center_ranks, encoded=1):
        sparse_cost_file(self.edge_path, PHASE6_EDGE_UNIVERSE, edge_ranks, encoded)
        sparse_cost_file(self.center_path, PHASE6_CENTER_UNIVERSE, center_ranks, encoded)

    def test_phase6_rank_boundaries_and_legal_moves(self):
        edge_rank = PHASE6_EDGE_UNIVERSE - 1
        center_rank = PHASE6_CENTER_UNIVERSE - 1
        self.write_costs([edge_rank], [center_rank])
        roots_path = self.directory / "boundary-roots.txt"
        roots_path.write_text(f"boundary root,{edge_rank},{center_rank}\n")

        result = subprocess.run(
            self.command(roots_path) + ["--max-ida-threshold", "0", "--print-ranks", "--print-legal-moves"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            f"ROOT boundary root EDGE_RANK {edge_rank} CENTER_RANK {center_rank} COST 0",
            result.stdout,
        )
        legal_line = next(line for line in result.stdout.splitlines() if line.startswith("LEGAL_MOVES"))
        self.assertEqual(set(legal_line.split()[1:]), PHASE6_LEGAL)
        self.assertIn("SOLUTION ROOT boundary root (0 steps):", result.stdout)

    def test_phase6_rejects_out_of_range_root(self):
        self.write_costs([0], [0])
        roots_path = self.directory / "invalid-root.txt"
        roots_path.write_text(f"bad,{PHASE6_EDGE_UNIVERSE},0\n")

        result = subprocess.run(self.command(roots_path), capture_output=True, text=True)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ID,EDGE_RANK,CENTER_RANK", result.stderr)

    def test_phase6_portfolio_preserves_root_identity(self):
        edge_rank, center_rank = self.cube.lt_phase6.ranks()
        self.write_costs([edge_rank], [center_rank])
        roots_path = self.directory / "portfolio-roots.txt"
        roots_path.write_text(
            f"first root,{edge_rank},{center_rank}\n" f"second-root,{edge_rank},{center_rank} # duplicate coordinate\n"
        )

        result = subprocess.run(
            self.command(roots_path) + ["--max-ida-threshold", "0", "--solution-count", "2", "--find-extra"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            [line for line in result.stdout.splitlines() if line.startswith("SOLUTION ROOT")],
            [
                "SOLUTION ROOT first root (0 steps):",
                "SOLUTION ROOT second-root (0 steps):",
            ],
        )

    def test_phase6_one_move_rank_transitions(self):
        high, _, low = self.cube.lt_phase6.edge_square_groups

        def perturb(cube):
            for first, second in ((high[0], high[1]), (low[0], low[1])):
                first_partner = cube555_module.edges_partner_555[first]
                second_partner = cube555_module.edges_partner_555[second]
                cube.state[first], cube.state[second] = cube.state[second], cube.state[first]
                cube.state[first_partner], cube.state[second_partner] = (
                    cube.state[second_partner],
                    cube.state[first_partner],
                )
            cube.state[32], cube.state[82] = cube.state[82], cube.state[32]

        perturb(self.cube)
        root_ranks = self.cube.lt_phase6.ranks()

        target = RubiksCube555(solved_555, "URFDLB")
        with patch("rubikscubennnsolver.RubiksCube555.download_file_if_needed"):
            target.lt_init()
        perturb(target)
        target.rotate("F2")
        target_ranks = target.lt_phase6.ranks()
        self.assertNotEqual(root_ranks, target_ranks)
        self.write_costs(target_ranks[:1], target_ranks[1:])
        if root_ranks[0] != target_ranks[0]:
            sparse_cost_file(self.edge_path, PHASE6_EDGE_UNIVERSE, root_ranks[:1], encoded=2)
        if root_ranks[1] != target_ranks[1]:
            sparse_cost_file(self.center_path, PHASE6_CENTER_UNIVERSE, root_ranks[1:], encoded=2)
        roots_path = self.directory / "one-move-root.txt"
        roots_path.write_text(f"moved,{root_ranks[0]},{root_ranks[1]}\n")

        result = subprocess.run(
            self.command(roots_path) + ["--max-ida-threshold", "1", "--print-ranks", "--print-transitions"],
            capture_output=True,
            text=True,
        )

        self.assertIn(
            f"TRANSITION ROOT moved MOVE F2 EDGE_RANK {target_ranks[0]} CENTER_RANK {target_ranks[1]}",
            result.stdout,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOLUTION ROOT moved (1 steps): F2", result.stdout)


if __name__ == "__main__":
    unittest.main()
