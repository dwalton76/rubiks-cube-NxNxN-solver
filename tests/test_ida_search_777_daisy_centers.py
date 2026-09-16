# standard libraries
import subprocess
import tempfile
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import (
    DAISY_CENTERS_ILLEGAL_MOVES_777,
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
        command = [str(BINARY), "--kociemba", cube.get_kociemba_string(True)]
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

        # The sampled matrix is the default and never reports less than that max.
        result = subprocess.run(
            self.command(self.solved, "--apply-move", "Uw2", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertGreaterEqual(parse_ranks(result.stdout)["COST"], 15)

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
        self.assertEqual(line.split()[1:], [move for move in moves_777 if move not in ILLEGAL_MOVES])

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
        scrambled.rotate("Uw2")
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
            self.command(self.solved, "--apply-move", "Uw2", "--threads", "2", "--max-ida-threshold", "1"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(search.returncode, 0, search.stdout + search.stderr)
        self.assertRegex(search.stdout, r"SOLUTION \(1 steps\): Uw2")
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


if __name__ == "__main__":
    unittest.main()
