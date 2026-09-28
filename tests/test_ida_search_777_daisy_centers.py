# standard libraries
import subprocess
import tempfile
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import (
    DAISY_CENTERS_ILLEGAL_MOVES_777,
    DAISY_LR_INNER_TABLE_777,
    LR_LEFT_OBLIQUES_777,
    LR_MIDDLE_OBLIQUES_777,
    LR_RIGHT_OBLIQUES_777,
    PHASE8_PRESERVE_ILLEGAL_MOVES_777,
    RubiksCube777,
    inner_t_centers_777,
    inner_x_centers_777,
    left_oblique_edges_777,
    moves_777,
    outer_t_centers_777,
    right_oblique_edges_777,
    solved_777,
)

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_777_daisy_centers"
GROUP_UNIVERSE = 70
LEAVE_ONE_OUT_UNIVERSE = GROUP_UNIVERSE**4

# Orbit order must match builder777.DAISY_CENTER_ORBITS_777 and the C searcher.
AXES = (
    (
        "UD",
        "DU",
        {
            "left-oblique": left_oblique_edges_777[0:4] + left_oblique_edges_777[20:24],
            "middle-oblique": outer_t_centers_777[0:4] + outer_t_centers_777[20:24],
            "right-oblique": right_oblique_edges_777[0:4] + right_oblique_edges_777[20:24],
            "inner-t": inner_t_centers_777[0:4] + inner_t_centers_777[20:24],
            "inner-x": inner_x_centers_777[0:4] + inner_x_centers_777[20:24],
        },
    ),
    (
        "LR",
        "LR",
        {
            "left-oblique": left_oblique_edges_777[4:8] + left_oblique_edges_777[12:16],
            "middle-oblique": outer_t_centers_777[4:8] + outer_t_centers_777[12:16],
            "right-oblique": right_oblique_edges_777[4:8] + right_oblique_edges_777[12:16],
            "inner-t": inner_t_centers_777[4:8] + inner_t_centers_777[12:16],
            "inner-x": inner_x_centers_777[4:8] + inner_x_centers_777[12:16],
        },
    ),
    (
        "FB",
        "BF",
        {
            "left-oblique": left_oblique_edges_777[8:12] + left_oblique_edges_777[16:20],
            "middle-oblique": outer_t_centers_777[8:12] + outer_t_centers_777[16:20],
            "right-oblique": right_oblique_edges_777[8:12] + right_oblique_edges_777[16:20],
            "inner-t": inner_t_centers_777[8:12] + inner_t_centers_777[16:20],
            "inner-x": inner_x_centers_777[8:12] + inner_x_centers_777[16:20],
        },
    ),
)
ORBIT_NAMES = ("left-oblique", "middle-oblique", "right-oblique", "inner-t", "inner-x")
OBLIQUE_ORBITS = frozenset(ORBIT_NAMES[:3])
LEAVE_ONE_OUT_TABLES = tuple(
    (
        f"{axis}_WITHOUT_{orbit.replace('-', '_').upper()}",
        f"--{axis.lower()}-without-{orbit}-cost",
        axis,
        orbit,
    )
    for axis, _, _ in AXES
    for orbit in ORBIT_NAMES
)
PERFECT_LABELS = tuple(f"{axis}_PERFECT" for axis, _, _ in AXES)
# One real table and index serve all three axes, and a fake is impractical: the
# index has to name the canonical rank of each of the 105,356,972 symmetry
# orbits, which is the compactor's whole job. tests/test_center_symmetry_777.c
# in rubiks-cube-lookup-tables checks the compaction itself.
PERFECT_COST = Path("lookup-tables/lookup-table-7x7x7-daisy-perfect-centers.cost-only.bin")
PERFECT_INDEX = Path(f"{PERFECT_COST}.symmetry-index.bin")
SPINE_COST = Path("lookup-tables/lookup-table-7x7x7-daisy-inner-x-spine-centers.cost-only.bin")
# Identity-probe group order, then the same groups after every oblique swaps.
# UD and FB solved ranks are 69; LR solved ranks are 0. A color swap sends r to 69-r.
MIXED_COST_FILES = (
    (
        "--inner-x-plus-two-inner-t-cost",
        "IX2IT_OMIT",
        Path("lookup-tables/lookup-table-7x7x7-daisy-inner-x-plus-two-inner-t-centers.cost-only.bin"),
        (69, 0, 69, 69, 0),
        (69, 0, 69, 69, 0),
    ),
    (
        "--inner-t-plus-two-inner-x-cost",
        "IT2IX_OMIT",
        Path("lookup-tables/lookup-table-7x7x7-daisy-inner-t-plus-two-inner-x-centers.cost-only.bin"),
        (69, 0, 69, 69, 0),
        (69, 0, 69, 69, 0),
    ),
    (
        "--middle-plus-two-inner-t-cost",
        "MID2IT_OMIT",
        Path("lookup-tables/lookup-table-7x7x7-daisy-middle-plus-two-inner-t-centers.cost-only.bin"),
        (69, 0, 69, 69, 0),
        (0, 69, 0, 69, 0),
    ),
    (
        "--oblique-weave-cost",
        "WEAVE_MIDDLE",
        Path("lookup-tables/lookup-table-7x7x7-daisy-oblique-weave-centers.cost-only.bin"),
        (69, 69, 0, 0, 69),
        (0, 0, 69, 69, 0),
    ),
)
PERFECT_ORBIT_COUNT = 105_356_972
ILLEGAL_MOVES = frozenset(DAISY_CENTERS_ILLEGAL_MOVES_777)


def combination_rank(values, symbols):
    remaining = [4, 4]
    permutations = GROUP_UNIVERSE
    rank = 0
    slots = 8
    for value in values:
        symbol_index = symbols.index(value)
        if remaining[symbol_index] <= 0:
            raise ValueError(f"too many {value!r} stickers")
        for smaller in range(symbol_index):
            rank += permutations * remaining[smaller] // slots
        permutations = permutations * remaining[symbol_index] // slots
        remaining[symbol_index] -= 1
        slots -= 1
    return rank


def axis_orbits(axis_name):
    for name, symbols, orbits in AXES:
        if name == axis_name:
            return symbols, orbits
    raise KeyError(axis_name)


def orbit_ranks(cube):
    ranks = {}
    for axis, symbols, orbits in AXES:
        for orbit, squares in orbits.items():
            ranks[(axis, orbit)] = combination_rank([cube.state[square] for square in squares], symbols)
    return ranks


def mixed_radix(ranks):
    result = 0
    for rank in ranks:
        result = result * GROUP_UNIVERSE + rank
    return result


def leave_one_out_rank(ranks, axis, omitted):
    return mixed_radix([ranks[(axis, orbit)] for orbit in ORBIT_NAMES if orbit != omitted])


def make_sparse_table(path, size, entries):
    with open(path, "wb") as table:
        table.truncate(size)
        for rank, encoded in entries.items():
            table.seek(rank)
            table.write(bytes((encoded,)))


def parse_ranks(stdout):
    line = next(line for line in stdout.splitlines() if "_LEFT_OBLIQUE_RANK " in line)
    tokens = line.split()
    return {tokens[index]: int(tokens[index + 1]) for index in range(0, len(tokens), 2)}


def phase7_reached(cube):
    state = cube.state
    for left, middle, right in zip(LR_LEFT_OBLIQUES_777, LR_MIDDLE_OBLIQUES_777, LR_RIGHT_OBLIQUES_777):
        if not (50 <= middle <= 98 or 148 <= middle <= 196):
            continue
        if state[left] != state[middle] or state[middle] != state[right]:
            return False
    _, orbits = axis_orbits("LR")
    for orbit in ("inner-t", "inner-x"):
        squares = orbits[orbit]
        if any(state[square] != "L" for square in squares[:4]):
            return False
        if any(state[square] != "R" for square in squares[4:]):
            return False
    return True


def orbit_matches(cube, squares, first, second):
    return all(cube.state[square] == first for square in squares[:4]) and all(
        cube.state[square] == second for square in squares[4:]
    )


def cube_is_daisy(cube, native_only=False):
    faces = {"UD": ("U", "D"), "LR": ("L", "R"), "FB": ("F", "B")}
    for axis_name, (primary, opposite) in faces.items():
        _, orbits = axis_orbits(axis_name)
        native = all(orbit_matches(cube, squares, primary, opposite) for squares in orbits.values())
        swapped = all(
            orbit_matches(
                cube,
                squares,
                opposite if orbit in OBLIQUE_ORBITS else primary,
                primary if orbit in OBLIQUE_ORBITS else opposite,
            )
            for orbit, squares in orbits.items()
        )
        if native_only and not native:
            return False
        if not native and not swapped:
            return False
    return True


def solution_steps(stdout):
    for line in stdout.splitlines():
        if line.startswith("SOLUTION"):
            return line.split(":", 1)[1].strip().split()
    return None


def set_orbit_orientation(cube, axis_name, swapped):
    _, orbits = axis_orbits(axis_name)
    primary, opposite = {"UD": ("U", "D"), "LR": ("L", "R"), "FB": ("F", "B")}[axis_name]
    for orbit, squares in orbits.items():
        first, second = (opposite, primary) if swapped and orbit in OBLIQUE_ORBITS else (primary, opposite)
        for square in squares[:4]:
            cube.state[square] = first
        for square in squares[4:]:
            cube.state[square] = second


@unittest.skipUnless(BINARY.is_file(), "ida_search_777_daisy_centers has not been built")
class DaisyCenters777Test(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.leave_paths = {
            label: Path(self.tempdir.name) / f"{label.lower()}.bin" for label, _, _, _ in LEAVE_ONE_OUT_TABLES
        }
        self.solved = RubiksCube777(solved_777, "URFDLB")

    def tearDown(self):
        self.tempdir.cleanup()

    def command(self, cube, *extra, mode="leave-one-out", labels=None):
        command = [str(BINARY), "--phase8", "--kociemba", cube.get_kociemba_string(True)]
        if mode == "leave-one-out":
            selected = labels or {label for label, _, _, _ in LEAVE_ONE_OUT_TABLES}
            for label, flag, _, _ in LEAVE_ONE_OUT_TABLES:
                if label in selected:
                    command.extend((flag, str(self.leave_paths[label])))
        else:
            command.extend(("--perfect-cost", str(PERFECT_COST), "--perfect-index", str(PERFECT_INDEX)))
        command.extend(extra)
        return command

    def write_leave_one_out(self, cubes, encoded_by_label=None):
        encoded_by_label = encoded_by_label or {
            label: index + 2 for index, (label, _, _, _) in enumerate(LEAVE_ONE_OUT_TABLES)
        }
        for label, _, axis, omitted in LEAVE_ONE_OUT_TABLES:
            entries = {leave_one_out_rank(orbit_ranks(cube), axis, omitted): encoded_by_label[label] for cube in cubes}
            make_sparse_table(self.leave_paths[label], LEAVE_ONE_OUT_UNIVERSE, entries)

    def test_rank_order_max_cost_and_both_daisy_orientations(self):
        native = self.solved
        swapped = RubiksCube777(solved_777, "URFDLB")
        for axis, _, _ in AXES:
            set_orbit_orientation(swapped, axis, True)
        mixed = RubiksCube777(solved_777, "URFDLB")
        set_orbit_orientation(mixed, "UD", True)
        moved = RubiksCube777(solved_777, "URFDLB")
        moved.rotate("Uw2")
        self.write_leave_one_out(
            [native, swapped, mixed, moved],
            {label: 1 for label, _, _, _ in LEAVE_ONE_OUT_TABLES},
        )

        for move, cube, daisy in (
            (None, native, 1),
            (None, swapped, 1),
            (None, mixed, 1),
            ("Uw2", moved, 0),
        ):
            with self.subTest(move=move, daisy=daisy):
                extra = ("--apply-move", move) if move else ()
                source = self.solved if move else cube
                result = subprocess.run(
                    self.command(source, *extra, "--print-ranks"),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                actual = parse_ranks(result.stdout)
                ranks = orbit_ranks(cube)
                for axis, _, orbits in AXES:
                    for orbit in orbits:
                        key = f"{axis}_{orbit.replace('-', '_').upper()}_RANK"
                        self.assertEqual(actual[key], ranks[(axis, orbit)])
                for label, _, axis, omitted in LEAVE_ONE_OUT_TABLES:
                    self.assertEqual(actual[f"{label}_RANK"], leave_one_out_rank(ranks, axis, omitted))
                    self.assertEqual(actual[f"{label}_COST"], 0)
                self.assertEqual(actual["DAISY"], daisy)
                self.assertEqual(actual["COST"], 0 if daisy else 1)

        for cube, daisy in ((native, 1), (swapped, 0), (mixed, 0)):
            with self.subTest(native_only=True, daisy=daisy):
                result = subprocess.run(
                    self.command(cube, "--native-only", "--print-ranks"),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                actual = parse_ranks(result.stdout)
                self.assertEqual(actual["DAISY"], daisy)
                self.assertEqual(actual["COST"], 0 if daisy else 1)

        # Costs 1 through 15 hand each axis a different maximum: UD 5, LR 10, FB 15.
        distinct = {label: index + 2 for index, (label, _, _, _) in enumerate(LEAVE_ONE_OUT_TABLES)}
        self.write_leave_one_out([moved], distinct)
        result = subprocess.run(
            self.command(self.solved, "--apply-move", "Uw2", "--multiplier", "1.0", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = parse_ranks(result.stdout)
        for index, (label, _, _, _) in enumerate(LEAVE_ONE_OUT_TABLES):
            self.assertEqual(actual[f"{label}_COST"], index + 1)
        # A multiplier of 1.0 is the admissible max over the three axes.
        self.assertEqual(actual["COST"], 15)
        self.assertEqual(actual["DAISY"], 0)

        # With no multiplier and no spine file, the heuristic is that same max.
        result = subprocess.run(
            self.command(self.solved, "--apply-move", "Uw2", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(parse_ranks(result.stdout)["COST"], 15)

        # Inflating the max by 2 doubles it, and F below 1.0 is rejected.
        result = subprocess.run(
            self.command(self.solved, "--apply-move", "Uw2", "--multiplier", "2.0", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(parse_ranks(result.stdout)["COST"], 30)

        result = subprocess.run(
            self.command(self.solved, "--multiplier", "0.5", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--multiplier must be at least 1.0", result.stderr)

    def test_legal_moves_required_tables_and_file_size(self):
        self.write_leave_one_out([self.solved], {label: 1 for label, _, _, _ in LEAVE_ONE_OUT_TABLES})
        result = subprocess.run(
            self.command(self.solved, "--print-legal-moves", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = next(line for line in result.stdout.splitlines() if line.startswith("LEGAL_MOVES"))
        phase8_legal = [
            move for move in moves_777 if move not in ILLEGAL_MOVES and move not in PHASE8_PRESERVE_ILLEGAL_MOVES_777
        ]
        self.assertEqual(line.split()[1:], phase8_legal)

        result = subprocess.run(
            self.command(self.solved, "--print-ranks", labels={"UD_WITHOUT_LEFT_OBLIQUE"}),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stdout)

        self.leave_paths["UD_WITHOUT_LEFT_OBLIQUE"].write_bytes(b"\x00")
        result = subprocess.run(
            self.command(self.solved, "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected 24010000", result.stderr)

    def test_zero_cost_goal_and_one_move_search(self):
        scrambled = RubiksCube777(solved_777, "URFDLB")
        scrambled.rotate("Lw2")
        self.write_leave_one_out(
            [self.solved, scrambled],
            {label: 1 for label, _, _, _ in LEAVE_ONE_OUT_TABLES},
        )

        solved = subprocess.run(
            self.command(self.solved, "--max-ida-threshold", "0", "--print-ida-summary"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(solved.returncode, 0, solved.stdout + solved.stderr)
        self.assertIn("SOLUTION (0 steps)", solved.stdout)
        self.assertIn("explored 1 nodes", solved.stdout)

        search = subprocess.run(
            self.command(self.solved, "--apply-move", "Lw2", "--threads", "2", "--max-ida-threshold", "1"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(search.returncode, 0, search.stdout + search.stderr)
        self.assertRegex(search.stdout, r"SOLUTION \(1 steps\): Lw2")
        self.assertRegex(search.stdout, r"explored [1-9][0-9]* nodes")

    @unittest.skipUnless(PERFECT_INDEX.is_file(), "the optional 7x7x7 perfect tables have not been built")
    def test_one_perfect_table_serves_all_three_axes(self):
        # LR obliques swapped is the second daisy goal, so every axis is already
        # at a goal and all three costs are 0 even though each reads the coordinate
        # of a different axis out of the one shared table.
        swapped = RubiksCube777(solved_777, "URFDLB")
        set_orbit_orientation(swapped, "LR", True)

        result = subprocess.run(
            self.command(swapped, "--print-ranks", mode="perfect"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = parse_ranks(result.stdout)
        ranks = orbit_ranks(swapped)

        for axis, _, orbits in AXES:
            for orbit in orbits:
                key = f"{axis}_{orbit.replace('-', '_').upper()}_RANK"
                self.assertEqual(actual[key], ranks[(axis, orbit)])

        for label in PERFECT_LABELS:
            # A canonical rank is mapped into the compacted table, so what the
            # searcher probes is a dense orbit index, not the 70^5 raw rank.
            self.assertLess(actual[f"{label}_RANK"], PERFECT_ORBIT_COUNT)
            self.assertEqual(actual[f"{label}_COST"], 0)
        self.assertEqual(actual["DAISY"], 1)
        self.assertEqual(actual["COST"], 0)

        solved = subprocess.run(
            self.command(swapped, "--max-ida-threshold", "0", mode="perfect"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(solved.returncode, 0, solved.stdout + solved.stderr)
        self.assertIn("SOLUTION (0 steps)", solved.stdout)

    @unittest.skipUnless(PERFECT_INDEX.is_file(), "the optional 7x7x7 perfect tables have not been built")
    def test_perfect_search_scrambled_state_costs_rise_with_distance(self):
        cube = RubiksCube777(solved_777, "URFDLB")
        for move in ("Uw2", "Rw2", "F", "3Fw2", "L"):
            cube.rotate(move)

        result = subprocess.run(
            self.command(cube, "--print-ranks", mode="perfect"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = parse_ranks(result.stdout)

        self.assertEqual(actual["DAISY"], 0)
        self.assertGreater(max(actual[f"{label}_COST"] for label in PERFECT_LABELS), 0)
        self.assertGreater(actual["COST"], 0)

    @unittest.skipUnless(PERFECT_INDEX.is_file() and SPINE_COST.is_file(), "the 7x7x7 spine table has not been built")
    def test_solved_spine_probes_are_depth_zero(self):
        swapped = RubiksCube777(solved_777, "URFDLB")
        set_orbit_orientation(swapped, "LR", True)
        native_rank = 1_657_032_999
        swapped_rank = 1_657_028_100

        for cube, lr_rank in ((self.solved, native_rank), (swapped, swapped_rank)):
            with self.subTest(lr_rank=lr_rank):
                result = subprocess.run(
                    self.command(
                        cube,
                        "--inner-x-spine-cost",
                        str(SPINE_COST),
                        "--print-ranks",
                        mode="perfect",
                    ),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                actual = parse_ranks(result.stdout)
                self.assertEqual(actual["SPINE_UD_RANK"], native_rank)
                self.assertEqual(actual["SPINE_FB_RANK"], native_rank)
                self.assertEqual(actual["SPINE_LR_RANK"], lr_rank)
                for probe in ("UD", "LR", "FB"):
                    self.assertEqual(actual[f"SPINE_{probe}_COST"], 0)
                self.assertEqual(actual["COST"], 0)
                self.assertEqual(actual["DAISY"], 1)

    @unittest.skipUnless(
        PERFECT_INDEX.is_file() and all(path.is_file() for _, _, path, _, _ in MIXED_COST_FILES),
        "the 7x7x7 mixed-axis tables have not been built",
    )
    def test_solved_mixed_probes_are_depth_zero(self):
        swapped = RubiksCube777(solved_777, "URFDLB")
        for axis, _, _ in AXES:
            set_orbit_orientation(swapped, axis, True)
        extra = []
        for flag, _, path, _, _ in MIXED_COST_FILES:
            extra.extend((flag, str(path)))

        for cube in (self.solved, swapped):
            with self.subTest(swapped=cube is swapped):
                result = subprocess.run(
                    self.command(cube, *extra, "--print-ranks", mode="perfect"),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                actual = parse_ranks(result.stdout)
                for _, prefix, _, native_groups, swapped_groups in MIXED_COST_FILES:
                    groups = swapped_groups if cube is swapped else native_groups
                    rank = 0
                    for group in groups:
                        rank = rank * GROUP_UNIVERSE + group
                    self.assertEqual(actual[f"{prefix}_FB_RANK"], rank)
                    for probe in ("FB", "UD", "LR"):
                        self.assertEqual(actual[f"{prefix}_{probe}_RANK"], rank)
                        self.assertEqual(actual[f"{prefix}_{probe}_COST"], 0)
                self.assertEqual(actual["COST"], 0)
                self.assertEqual(actual["DAISY"], 1)

    def phase_command(self, cube, phase, *extra):
        return [str(BINARY), "--kociemba", cube.get_kociemba_string(True), f"--phase{phase}", "--threads", "1", *extra]

    def test_phase7_goal_and_phase8_preserve_moves(self):
        daisy_legal = [move for move in moves_777 if move not in ILLEGAL_MOVES]
        phase7_skip = {
            "U",
            "U'",
            "U2",
            "D",
            "D'",
            "D2",
            "F",
            "F'",
            "F2",
            "B",
            "B'",
            "B2",
            "Lw2",
            "3Lw2",
            "Rw2",
            "3Rw2",
        }
        phase7_legal = [move for move in daisy_legal if move not in phase7_skip]
        phase8_legal = [move for move in daisy_legal if move not in PHASE8_PRESERVE_ILLEGAL_MOVES_777]
        self.assertEqual(len(phase8_legal), 26)

        for phase, expected in ((7, phase7_legal), (8, phase8_legal)):
            result = subprocess.run(
                self.phase_command(self.solved, phase, "--print-legal-moves", "--print-ranks"),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            printed = next(line for line in result.stdout.splitlines() if line.startswith("LEGAL_MOVES"))
            self.assertEqual(printed.split()[1:], expected)
            actual = parse_ranks(result.stdout)
            self.assertEqual(actual["COST"], 0)
            self.assertEqual(actual["GOAL"], 1)
            self.assertEqual(actual["DAISY"], 1)

        split = RubiksCube777(solved_777, "URFDLB")
        split.rotate("3Lw2")
        self.assertTrue(phase7_reached(split))
        result = subprocess.run(
            self.phase_command(split, 7, "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = parse_ranks(result.stdout)
        self.assertEqual(actual["UNPAIRED"], 0)
        self.assertEqual(actual["OBLIQUE_COST"], 0)
        self.assertEqual(actual["COST"], 0)
        self.assertEqual(actual["GOAL"], 1)
        self.assertEqual(actual["DAISY"], 0)

        opposite = RubiksCube777(solved_777, "URFDLB")
        opposite.rotate("3Uw2")
        result = subprocess.run(
            self.phase_command(opposite, 7, "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = parse_ranks(result.stdout)
        self.assertEqual(actual["UNPAIRED"], 4)
        self.assertEqual(actual["OBLIQUE_COST"], 1)
        self.assertEqual(actual["COST"], 1)
        self.assertEqual(actual["GOAL"], 0)

        for move in ("3Uw2",):
            with self.subTest(phase7=move):
                cube = RubiksCube777(solved_777, "URFDLB")
                cube.rotate(move)
                result = subprocess.run(
                    self.phase_command(cube, 7, "--max-ida-threshold", "4"),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                steps = solution_steps(result.stdout)
                self.assertEqual(steps, [move])
                for step in steps:
                    cube.rotate(step)
                self.assertTrue(phase7_reached(cube))
                self.assertTrue(cube_is_daisy(cube))

        preserved = RubiksCube777(solved_777, "URFDLB")
        preserved.rotate("Lw2")
        self.assertTrue(phase7_reached(preserved))
        self.assertFalse(cube_is_daisy(preserved))
        result = subprocess.run(
            self.phase_command(preserved, 8, "--max-ida-threshold", "4"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        steps = solution_steps(result.stdout)
        self.assertEqual(steps, ["Lw2"])
        for step in steps:
            preserved.rotate(step)
        self.assertTrue(phase7_reached(preserved))
        self.assertTrue(cube_is_daisy(preserved))

        result = subprocess.run(
            self.phase_command(split, 8, "--max-ida-threshold", "2"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(solution_steps(result.stdout), ["3Lw2"])

        result = subprocess.run(
            self.phase_command(opposite, 8, "--max-ida-threshold", "2"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("phase 8 start", result.stderr)

    @unittest.skipUnless(Path(DAISY_LR_INNER_TABLE_777[1]).is_file(), "the LR inner table has not been built")
    def test_phase7_lr_inner_table_matches_its_file(self):
        path = Path(DAISY_LR_INNER_TABLE_777[1])
        self.assertEqual(path.stat().st_size, 70 * 70)
        costs = path.read_bytes()

        def expect(cube):
            ranks = orbit_ranks(cube)
            rank = ranks[("LR", "inner-t")] * GROUP_UNIVERSE + ranks[("LR", "inner-x")]
            encoded = costs[rank]
            self.assertGreater(encoded, 0)
            return rank, encoded - 1

        solved_rank, solved_cost = expect(self.solved)
        self.assertEqual(solved_rank, 0)
        self.assertEqual(solved_cost, 0)
        moved = RubiksCube777(solved_777, "URFDLB")
        moved.rotate("3Uw2")
        moved_rank, moved_cost = expect(moved)
        self.assertEqual(moved_cost, 1)

        for cube, rank, cost in ((self.solved, solved_rank, solved_cost), (moved, moved_rank, moved_cost)):
            result = subprocess.run(
                self.phase_command(cube, 7, "--lr-inner-cost", str(path), "--print-ranks"),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actual = parse_ranks(result.stdout)
            self.assertEqual(actual["LR_INNER_RANK"], rank)
            self.assertEqual(actual["LR_INNER_COST"], cost)
            self.assertEqual(actual["OBLIQUE_COST"], 0 if cube is self.solved else 1)
            self.assertEqual(actual["COST"], max(cost, actual["OBLIQUE_COST"]))
            self.assertEqual(actual["GOAL"], 1 if cost == 0 else 0)


if __name__ == "__main__":
    unittest.main()
