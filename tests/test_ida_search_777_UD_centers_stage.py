# standard libraries
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import (
    RubiksCube777,
    UFBD_left_oblique_777,
    UFBD_middle_oblique_777,
    UFBD_right_oblique_777,
    moves_777,
    solved_777,
)

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_777_UD_centers_stage"
GROUP_UNIVERSE = math.comb(16, 8)
PRODUCT_UNIVERSE = GROUP_UNIVERSE**2
OUTER_X = (9, 13, 37, 41, 107, 111, 135, 139, 205, 209, 233, 237, 254, 258, 282, 286)
ORBITS = {
    "outer": OUTER_X,
    "left": UFBD_left_oblique_777,
    "middle": UFBD_middle_oblique_777,
    "right": UFBD_right_oblique_777,
}
# Flag and rank order must match ida_search_777_UD_centers_stage.c and the builders.
TABLES = (
    ("LOMO", "--left-middle-oblique-cost", ("left", "middle")),
    ("LORO", "--left-right-oblique-cost", ("left", "right")),
    ("LOOX", "--left-oblique-outer-x-cost", ("left", "outer")),
    ("MORO", "--middle-right-oblique-cost", ("middle", "right")),
    ("MOOX", "--middle-oblique-outer-x-cost", ("middle", "outer")),
    ("ROOX", "--right-oblique-outer-x-cost", ("right", "outer")),
)
ILLEGAL_MOVES = frozenset(
    (
        "3Uw",
        "3Uw'",
        "3Dw",
        "3Dw'",
        "3Fw",
        "3Fw'",
        "3Bw",
        "3Bw'",
        "3Lw",
        "3Lw'",
        "3Rw",
        "3Rw'",
        "Uw",
        "Uw'",
        "Dw",
        "Dw'",
        "Fw",
        "Fw'",
        "Bw",
        "Bw'",
        "L",
        "L'",
        "L2",
        "R",
        "R'",
        "R2",
    )
)


def combination_rank(values):
    rank = 0
    remaining = 8
    for position, value in enumerate(values):
        if value in ("U", "D"):
            remaining -= 1
        elif remaining:
            rank += math.comb(15 - position, remaining - 1)
    if remaining:
        raise ValueError("coordinate does not contain eight U/D stickers")
    return rank


def orbit_ranks(cube):
    return {name: combination_rank([cube.state[square] for square in squares]) for name, squares in ORBITS.items()}


def table_rank(ranks, pair):
    return ranks[pair[0]] * GROUP_UNIVERSE + ranks[pair[1]]


def make_sparse_table(path, entries):
    with open(path, "wb") as table:
        table.truncate(PRODUCT_UNIVERSE)
        for rank, encoded in entries.items():
            table.seek(rank)
            table.write(bytes((encoded,)))


def parse_ranks(stdout):
    line = next(line for line in stdout.splitlines() if line.startswith("OUTER_RANK "))
    tokens = line.split()
    return {tokens[index]: int(tokens[index + 1]) for index in range(0, len(tokens), 2)}


@unittest.skipUnless(BINARY.is_file(), "ida_search_777_UD_centers_stage has not been built")
class RankedUDCentersStage777Test(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.paths = {label: Path(self.tempdir.name) / f"{label.lower()}.cost-only.bin" for label, _, _ in TABLES}
        self.solved = RubiksCube777(solved_777, "URFDLB")

    def tearDown(self):
        self.tempdir.cleanup()

    def command(self, cube, *extra, labels=None):
        labels = labels or {label for label, _, _ in TABLES}
        command = [str(BINARY), "--kociemba", cube.get_kociemba_string(True)]
        for label, flag, _ in TABLES:
            if label in labels:
                command.extend((flag, str(self.paths[label])))
        command.extend(extra)
        return command

    def write_tables(self, cubes, encoded_by_label=None):
        encoded_by_label = encoded_by_label or {label: index + 2 for index, (label, _, _) in enumerate(TABLES)}
        for label, _, pair in TABLES:
            entries = {table_rank(orbit_ranks(cube), pair): encoded_by_label[label] for cube in cubes}
            make_sparse_table(self.paths[label], entries)

    def test_rank_and_max_cost_contract_after_representative_moves(self):
        cubes = [self.solved]
        for move in ("U", "Lw", "3Lw2"):
            cube = RubiksCube777(solved_777, "URFDLB")
            cube.rotate(move)
            cubes.append(cube)
        self.write_tables(cubes)

        for move, expected_cube in zip((None, "U", "Lw", "3Lw2"), cubes):
            with self.subTest(move=move):
                extra = ("--apply-move", move) if move else ()
                result = subprocess.run(
                    self.command(self.solved, *extra, "--print-ranks"),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                actual = parse_ranks(result.stdout)
                ranks = orbit_ranks(expected_cube)
                self.assertEqual(actual["OUTER_RANK"], ranks["outer"])
                self.assertEqual(actual["LEFT_RANK"], ranks["left"])
                self.assertEqual(actual["MIDDLE_RANK"], ranks["middle"])
                self.assertEqual(actual["RIGHT_RANK"], ranks["right"])
                for index, (label, _, pair) in enumerate(TABLES):
                    self.assertEqual(actual[f"{label}_RANK"], table_rank(ranks, pair))
                    self.assertEqual(actual[f"{label}_COST"], index + 1)
                self.assertEqual(actual["COST"], 6)

    def test_phase5_legal_moves_and_required_tables(self):
        self.write_tables([self.solved])
        result = subprocess.run(
            self.command(self.solved, "--print-legal-moves", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = next(line for line in result.stdout.splitlines() if line.startswith("LEGAL_MOVES"))
        self.assertEqual(line.split()[1:], [move for move in moves_777 if move not in ILLEGAL_MOVES])

        result = subprocess.run(
            self.command(self.solved, "--print-ranks", labels={"LOMO"}),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stdout)

    def test_zero_cost_goal_and_orbit0_parity(self):
        parity_goal = RubiksCube777(solved_777, "URFDLB")
        parity_goal.rotate("Lw")
        self.write_tables([self.solved, parity_goal], {label: 1 for label, _, _ in TABLES})

        even = subprocess.run(
            self.command(self.solved, "--orbit0-need-even-w", "--max-ida-threshold", "0"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(even.returncode, 0, even.stdout + even.stderr)
        self.assertIn("SOLUTION (0 steps)", even.stdout)

        odd = subprocess.run(
            self.command(
                self.solved,
                "--orbit0-need-odd-w",
                "--threads",
                "2",
                "--max-ida-threshold",
                "1",
            ),
            capture_output=True,
            text=True,
        )
        self.assertEqual(odd.returncode, 0, odd.stdout + odd.stderr)
        self.assertRegex(odd.stdout, r"SOLUTION \(1 steps\): Lw'?")


if __name__ == "__main__":
    unittest.main()
