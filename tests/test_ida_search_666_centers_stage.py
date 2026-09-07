# standard libraries
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube666 import (
    RubiksCube666,
    UFBD_inner_x_centers_666,
    UFBD_left_oblique_edges_666,
    UFBD_outer_x_centers_666,
    UFBD_right_oblique_edges_666,
    moves_666,
    solved_666,
)

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "ida_search_666_centers_stage"
GROUP_UNIVERSE = math.comb(16, 8)
PRODUCT_UNIVERSE = GROUP_UNIVERSE * GROUP_UNIVERSE

ORBIT_SQUARES = {
    "inner": UFBD_inner_x_centers_666,
    "outer": UFBD_outer_x_centers_666,
    "left": UFBD_left_oblique_edges_666,
    "right": UFBD_right_oblique_edges_666,
}

# label, CLI flag, the two orbits the table ranks, whether the search demands it.
# The first two pairings cover all four orbits, so they are the required ones.
TABLES = (
    ("IXOX", "--inner-x-outer-x-cost", ("inner", "outer"), True),
    ("LROB", "--left-right-oblique-cost", ("left", "right"), True),
    ("IXLO", "--inner-x-left-oblique-cost", ("inner", "left"), False),
    ("IXRO", "--inner-x-right-oblique-cost", ("inner", "right"), False),
    ("OXLO", "--outer-x-left-oblique-cost", ("outer", "left"), False),
    ("OXRO", "--outer-x-right-oblique-cost", ("outer", "right"), False),
)
REQUIRED_LABELS = tuple(label for label, _, _, required in TABLES if required)

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


def combination_rank(state):
    """Rank eight U values in the same lexicographic order as .state_index."""
    rank = 0
    u_remaining = 8
    for position, value in enumerate(state):
        positions_after = 15 - position
        if value in ("U", "D"):
            u_remaining -= 1
        elif u_remaining:
            rank += math.comb(positions_after, u_remaining - 1)
    if u_remaining:
        raise ValueError(f"expected eight U/D stickers, found {8 - u_remaining}")
    return rank


def orbit_ranks(cube):
    return {
        orbit: combination_rank([cube.state[index] for index in squares]) for orbit, squares in ORBIT_SQUARES.items()
    }


def table_rank(ranks, orbits):
    first, second = orbits
    return ranks[first] * GROUP_UNIVERSE + ranks[second]


def encoded_cost_for(label, rank):
    """A per-table cost so that max() has a single unambiguous winner to find."""
    return rank % (5 + REQUIRED_LABELS.index(label) if label in REQUIRED_LABELS else 7) + 1


def make_sparse_table(path, entries):
    with open(path, "wb") as table:
        table.truncate(PRODUCT_UNIVERSE)
        for rank, encoded_cost in entries.items():
            table.seek(rank)
            table.write(bytes((encoded_cost,)))


def parse_ranks(stdout):
    """Turn the whitespace-delimited KEY VALUE pairs of --print-ranks into a dict."""
    for line in stdout.splitlines():
        if line.startswith("INNER_RANK "):
            tokens = line.split()
            return {tokens[index]: int(tokens[index + 1]) for index in range(0, len(tokens), 2)}
    raise AssertionError(f"no --print-ranks line in:\n{stdout}")


@unittest.skipUnless(BINARY.is_file(), "ida_search_666_centers_stage has not been built")
class RankedCentersStage666Test(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.paths = {label: Path(self.tempdir.name) / f"{label.lower()}.cost-only.bin" for label, _, _, _ in TABLES}
        self.solved = RubiksCube666(solved_666, "URFDLB")

    def tearDown(self):
        self.tempdir.cleanup()

    def command(self, cube, *extra, labels=REQUIRED_LABELS):
        cmd = [str(BINARY), "--kociemba", cube.get_kociemba_string(True)]
        for label, flag, _, _ in TABLES:
            if label in labels:
                cmd.extend((flag, str(self.paths[label])))
        cmd.extend(extra)
        return tuple(cmd)

    def write_tables(self, cubes, labels=REQUIRED_LABELS):
        """Give every table an entry for each cube state the test will visit."""
        for label, _, orbits, _ in TABLES:
            if label not in labels:
                continue
            entries = {}
            for cube in cubes:
                rank = table_rank(orbit_ranks(cube), orbits)
                entries[rank] = encoded_cost_for(label, rank)
            make_sparse_table(self.paths[label], entries)
            self.assertEqual(self.paths[label].stat().st_size, PRODUCT_UNIVERSE)

    def run_rank(self, cube, *extra, labels=REQUIRED_LABELS):
        result = subprocess.run(
            self.command(cube, *extra, "--print-ranks", labels=labels), capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return parse_ranks(result.stdout)

    def cubes_for_every_legal_move(self):
        legal_moves = [move for move in moves_666 if move not in ILLEGAL_MOVES]
        cubes = [self.solved]
        for move in legal_moves:
            cube = RubiksCube666(solved_666, "URFDLB")
            cube.rotate(move)
            cubes.append(cube)
        return legal_moves, cubes

    def test_product_rank_and_encoded_cost_contract_for_every_legal_move(self):
        all_labels = tuple(label for label, _, _, _ in TABLES)
        legal_moves, cubes = self.cubes_for_every_legal_move()
        self.write_tables(cubes, labels=all_labels)

        for move, cube in zip((None, *legal_moves), cubes):
            with self.subTest(move=move):
                actual = self.run_rank(self.solved, *(("--apply-move", move) if move else ()), labels=all_labels)
                ranks = orbit_ranks(cube)
                expected = {
                    "INNER_RANK": ranks["inner"],
                    "OUTER_RANK": ranks["outer"],
                    "LEFT_RANK": ranks["left"],
                    "RIGHT_RANK": ranks["right"],
                }
                costs = []
                for label, _, orbits, _ in TABLES:
                    rank = table_rank(ranks, orbits)
                    cost = encoded_cost_for(label, rank) - 1
                    costs.append(cost)
                    expected[f"{label}_RANK"] = rank
                    expected[f"{label}_COST"] = cost
                expected["COST"] = max(costs)

                self.assertEqual(actual, expected)

    def test_heuristic_is_the_max_over_the_loaded_tables(self):
        """Adding pairings can only raise the heuristic, never lower it."""
        all_labels = tuple(label for label, _, _, _ in TABLES)
        cube = RubiksCube666(solved_666, "URFDLB")
        cube.rotate("3Rw")
        self.write_tables([cube], labels=all_labels)

        two_tables = self.run_rank(cube, labels=REQUIRED_LABELS)
        six_tables = self.run_rank(cube, labels=all_labels)

        self.assertEqual(two_tables["COST"], max(two_tables[f"{label}_COST"] for label in REQUIRED_LABELS))
        self.assertEqual(six_tables["COST"], max(six_tables[f"{label}_COST"] for label in all_labels))
        self.assertGreaterEqual(six_tables["COST"], two_tables["COST"])

    def test_optional_tables_are_omitted_and_required_tables_are_enforced(self):
        self.write_tables([self.solved], labels=REQUIRED_LABELS)

        printed = self.run_rank(self.solved, labels=REQUIRED_LABELS)
        for label, _, _, required in TABLES:
            self.assertEqual(f"{label}_COST" in printed, required)

        result = subprocess.run(
            self.command(self.solved, "--print-ranks", labels=REQUIRED_LABELS[:1]),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stdout)

    def test_zero_byte_is_absent_and_file_size_is_enforced(self):
        self.write_tables([], labels=REQUIRED_LABELS)
        result = subprocess.run(self.command(self.solved, "--print-ranks"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        printed = parse_ranks(result.stdout)
        self.assertEqual(printed["IXOX_COST"], 255)
        self.assertEqual(printed["LROB_COST"], 255)
        self.assertEqual(printed["COST"], 255)

        self.paths["LROB"].write_bytes(b"\1")
        result = subprocess.run(self.command(self.solved, "--print-ranks"), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(PRODUCT_UNIVERSE), result.stderr)

    def test_legal_moves_match_current_phase_three(self):
        self.write_tables([self.solved])
        result = subprocess.run(
            self.command(self.solved, "--print-legal-moves", "--print-ranks"),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = next(line for line in result.stdout.splitlines() if line.startswith("LEGAL_MOVES"))
        self.assertEqual(line.split()[1:], [move for move in moves_666 if move not in ILLEGAL_MOVES])

    def test_shallow_solution_and_thread_determinism(self):
        scrambled = RubiksCube666(solved_666, "URFDLB")
        scrambled.rotate("Lw")
        for label, _, orbits, required in TABLES:
            if not required:
                continue
            entries = {
                table_rank(orbit_ranks(self.solved), orbits): 1,
                table_rank(orbit_ranks(scrambled), orbits): 2,
            }
            make_sparse_table(self.paths[label], entries)

        solutions = set()
        for threads in ("1", "4"):
            result = subprocess.run(
                self.command(
                    scrambled,
                    "--threads",
                    threads,
                    "--max-ida-threshold",
                    "2",
                    "--orbit0-need-odd-w",
                ),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            solution = next(line for line in result.stdout.splitlines() if line.startswith("SOLUTION"))
            self.assertRegex(solution, r"\bLw'?\b")
            solutions.add(solution)
            # The summary gets one cost column per loaded table.
            self.assertRegex(result.stdout, r"IXOX\s+LROB\s+CTG\s+TRU\s+IDX")
        self.assertEqual(len(solutions), 1)

    def test_orbit_parity_requirements_are_checked_at_goal(self):
        self.write_tables([])
        for label, _, orbits, required in TABLES:
            if required:
                make_sparse_table(self.paths[label], {table_rank(orbit_ranks(self.solved), orbits): 1})

        for orbit in (0, 1):
            with self.subTest(orbit=orbit, parity="even"):
                even = subprocess.run(
                    self.command(
                        self.solved,
                        f"--orbit{orbit}-need-even-w",
                        "--max-ida-threshold",
                        "0",
                    ),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(even.returncode, 0, even.stdout + even.stderr)
                self.assertIn("SOLUTION (0 steps)", even.stdout)

            with self.subTest(orbit=orbit, parity="odd"):
                odd = subprocess.run(
                    self.command(
                        self.solved,
                        f"--orbit{orbit}-need-odd-w",
                        "--max-ida-threshold",
                        "0",
                    ),
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(odd.returncode, 0)
                self.assertIn("IDA failed", odd.stdout)


if __name__ == "__main__":
    unittest.main()
