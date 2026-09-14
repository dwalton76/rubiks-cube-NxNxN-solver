"""
4x4x4 solver: reduce the cube to a 3x3x3, then finish with the 3x3x3 solver.

A 4x4x4 has 24 centers (four per face), 24 wings (two per 3x3x3 edge), and 8
corners. Reduction pairs each wing with its partner and solves the centers so
the remaining puzzle is a 3x3x3. ``RubiksCube444.reduce_333`` runs two combined
C IDA searches; ``solve_333`` then solves the paired cube.

Phase 1+2 - stage all centers and EO the wings
    ``ida_search_444_phase1_and_2`` over the full 4x4x4 move set. Heuristic is
    the max of the 48-symmetry all-center table, the 51M LR-center table, and
    the high/low wing table (min over all 2048 even edge mappings). Orbit-0 OLL
    is required via ``--orbit0-need-even-w`` / ``--orbit0-need-odd-w``. The
    winning ``edge_mapping`` is recovered from the staged high/low state.

Phase 3+4 - pair all 12 edges and solve the centers
    ``ida_search_444_phase3_and_4`` over the phase-3 move set, using the dense
    all-edge pairing table and the exact LFRB-center graph. Combined solutions
    that would cause PLL parity are skipped. When ``consider_solve_333`` is
    set, PLL-free reductions are scored with the 3x3x3 solver and search stops
    once a 20-move 3x3x3 appears, or after nine reductions.
"""

# standard libraries
import logging
import subprocess
from typing import List, Tuple

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube, wing_str_map
from rubikscubennnsolver.LookupTable import LookupTable, download_file_if_needed
from rubikscubennnsolver.misc import SolveError
from rubikscubennnsolver.RubiksCube444Misc import highlow_edge_mapping_combinations
from rubikscubennnsolver.RubiksCubeHighLow import highlow_edge_values_444
from rubikscubennnsolver.swaps import swaps_444

logger = logging.getLogger(__name__)

# fmt: off
moves_444: Tuple[str] = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2",
    "F", "F'", "F2", "Fw", "Fw'", "Fw2",
    "R", "R'", "R2", "Rw", "Rw'", "Rw2",
    "B", "B'", "B2", "Bw", "Bw'", "Bw2",
    "D", "D'", "D2", "Dw", "Dw'", "Dw2",
    # slices...not used for now
    # "2U", "2U'", "2U2", "2D", "2D'", "2D2",
    # "2L", "2L'", "2L2", "2R", "2R'", "2R2",
    # "2F", "2F'", "2F2", "2B", "2B'", "2B2"
)

solved_444: str = "UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB"
ALL_EDGES_PAIRED_TABLE_444 = "lookup-tables/lookup-table-4x4x4-step33-all-edges-paired.cost-only.bin"
PHASE12_ALL_CENTERS_TABLE_444 = (
    "lookup-tables/lookup-table-4x4x4-step12-all-centers-stage-symmetry.cost-only.bin"
)
PHASE12_ALL_CENTERS_INDEX_444 = f"{PHASE12_ALL_CENTERS_TABLE_444}.symmetry-index.bin"
PHASE12_LR_CENTERS_TABLE_444 = "lookup-tables/lookup-table-4x4x4-step14-LR-centers-stage.cost-only.bin"
PHASE12_HIGHLOW_EDGES_TABLE_444 = "lookup-tables/lookup-table-4x4x4-step23-highlow-edges-edges.cost-only.bin"
PHASE12_HIGHLOW_TARGET_444 = "UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU"
PHASE34_SOLUTIONS_TO_EVALUATE = 9
SOLVE_333_GOOD_ENOUGH = 20

centers_444: Tuple[int] = (
    6, 7, 10, 11,  # Upper
    22, 23, 26, 27,  # Left
    38, 39, 42, 43,  # Front
    54, 55, 58, 59,  # Right
    70, 71, 74, 75,  # Back
    86, 87, 90, 91,  # Down
)

LFRB_centers_444: Tuple[int] = (
    22, 23, 26, 27,  # Left
    38, 39, 42, 43,  # Front
    54, 55, 58, 59,  # Right
    70, 71, 74, 75,  # Back
)

corners_444: Tuple[int] = (
    1, 4, 13, 16,  # Upper
    17, 20, 29, 32,  # Left
    33, 36, 45, 48,  # Front
    49, 52, 61, 64,  # Right
    65, 68, 77, 80,  # Back
    81, 84, 93, 96,  # Down
)

edges_444: Tuple[int] = (
    2, 3, 5, 8, 9, 12, 14, 15,  # Upper
    18, 19, 21, 24, 25, 28, 30, 31,  # Left
    34, 35, 37, 40, 41, 44, 46, 47,  # Front
    50, 51, 53, 56, 57, 60, 62, 63,  # Right
    66, 67, 69, 72, 73, 76, 78, 79,  # Back
    82, 83, 85, 88, 89, 92, 94, 95,  # Down
)

edge_orbit_0_444: Tuple[int] = (
    2, 3, 8, 12, 15, 14, 9, 5,  # Upper
    18, 19, 24, 28, 31, 30, 25, 21,  # Left
    34, 35, 40, 44, 47, 46, 41, 37,  # Front
    50, 51, 56, 60, 62, 63, 57, 53,  # Right
    66, 67, 72, 76, 79, 78, 73, 69,  # Back
    82, 83, 88, 92, 95, 94, 89, 85,  # Down
)

wings_444: Tuple[int] = (
    2, 3, 5, 9, 8, 12, 14, 15,  # Upper
    21, 25, 24, 28,  # Left
    53, 57, 56, 60,  # Right
    82, 83, 85, 89, 88, 92, 94, 95,  # Back
)

wings_for_edges_recolor_pattern_444: Tuple[Tuple[str, int, int]] = (
    ("0", 2, 67),  # Upper
    ("1", 3, 66),
    ("2", 5, 18),
    ("3", 8, 51),
    ("4", 9, 19),
    ("5", 12, 50),
    ("6", 14, 34),
    ("7", 15, 35),
    ("8", 21, 72),  # Left
    ("9", 24, 37),
    ("a", 25, 76),
    ("b", 28, 41),
    ("c", 53, 40),  # Right
    ("d", 56, 69),
    ("e", 57, 44),
    ("f", 60, 73),
    ("g", 82, 46),  # Down
    ("h", 83, 47),
    ("i", 85, 31),
    ("j", 88, 62),
    ("k", 89, 30),
    ("l", 92, 63),
    ("m", 94, 79),
    ("n", 95, 78),
)

reduce333_orient_edges_tuples: Tuple[Tuple[int, int]] = (
    (2, 67), (3, 66), (5, 18), (8, 51), (9, 19), (12, 50), (14, 34), (15, 35),  # Upper
    (18, 5), (19, 9), (21, 72), (24, 37), (25, 76), (28, 41), (30, 89), (31, 85),  # Left
    (34, 14), (35, 15), (37, 24), (40, 53), (41, 28), (44, 57), (46, 82), (47, 83),  # Front
    (50, 12), (51, 8), (53, 40), (56, 69), (57, 44), (60, 73), (62, 88), (63, 92),  # Right
    (66, 3), (67, 2), (69, 56), (72, 21), (73, 60), (76, 25), (78, 95), (79, 94),  # Back
    (82, 46), (83, 47), (85, 31), (88, 62), (89, 30), (92, 63), (94, 79), (95, 78),  # Down
)

paired_edges_444: Tuple[Tuple[int, int]] = (
    (2, 3), (8, 12), (15, 14), (9, 5),  # Upper
    (18, 19), (24, 28), (31, 30), (25, 21),  # Left
    (34, 35), (40, 44), (47, 46), (41, 37),  # Front
    (50, 51), (56, 60), (62, 63), (57, 53),  # Right
    (66, 67), (72, 76), (79, 78), (73, 69),  # Back
    (82, 83), (88, 92), (95, 94), (89, 85),  # Down
)
# fmt: on


def edges_recolor_pattern_444(state: List[int], only_colors: List[str] = None) -> str:
    """
    Args:
        state: the cube state
        only_colors: only re-color this subset of wings

    Returns:
        the re-colored cube
    """

    edge_map = {
        "UB": [],
        "UL": [],
        "UR": [],
        "UF": [],
        "LB": [],
        "LF": [],
        "RB": [],
        "RF": [],
        "DB": [],
        "DL": [],
        "DR": [],
        "DF": [],
        "--": [],
    }

    # Record the two edge_indexes for each of the 12 edges
    for edge_index, square_index, partner_index in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = wing_str_map[square_value + partner_value]
        edge_map[wing_str].append(edge_index)

    # Where is the other wing_str like us?
    for edge_index, square_index, partner_index in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = wing_str_map[square_value + partner_value]

        if only_colors and wing_str not in only_colors:
            state[square_index] = "-"
            state[partner_index] = "-"
        else:
            if wing_str == "--":
                state[square_index] = "-"
                state[partner_index] = "-"
            else:
                for tmp_index in edge_map[wing_str]:
                    if tmp_index != edge_index:
                        state[square_index] = tmp_index
                        state[partner_index] = tmp_index
                        break
                else:
                    raise Exception("could not find tmp_index")

    return "".join(state)


# fmt: off
PHASE34_ILLEGAL_MOVES = (
    "Uw", "Uw'",
    "Lw", "Lw'",
    "Fw", "Fw'",
    "Rw", "Rw'",
    "Bw", "Bw'",
    "Dw", "Dw'",
    "L", "L'",
    "R", "R'",
)

# fmt: on


# ==================================================
# phase 3+4 LFRB-center graph (840 states)
# ==================================================
class LookupTable444Reduce333LFRBCenters(LookupTable):
    """
             . . . .
             . . . .
             . . . .
             . . . .

    . . . .  . . . .  . . . .  . . . .
    . L L .  . F F .  . R R .  . B B .
    . L L .  . F F .  . R R .  . B B .
    . . . .  . . . .  . . . .  . . . .

             . . . .
             . . . .
             . . . .
             . . . .

    lookup-table-4x4x4-step31-centers.txt
    =====================================
    0 steps has 36 entries (4 percent, 0.00x previous step)
    1 steps has 80 entries (9 percent, 2.22x previous step)
    2 steps has 212 entries (25 percent, 2.65x previous step)
    3 steps has 288 entries (34 percent, 1.36x previous step)
    4 steps has 192 entries (22 percent, 0.67x previous step)
    5 steps has 32 entries (3 percent, 0.17x previous step)

    Total: 840 entries
    Average: 2.73 moves
    """

    state_targets = (
        "LLLLBBBBRRRRFFFF",
        "LLLLBFBFRRRRBFBF",
        "LLLLBFBFRRRRFBFB",
        "LLLLFBFBRRRRBFBF",
        "LLLLFBFBRRRRFBFB",
        "LLLLFFFFRRRRBBBB",
        "LRLRBBBBLRLRFFFF",
        "LRLRBBBBRLRLFFFF",
        "LRLRBFBFLRLRBFBF",
        "LRLRBFBFLRLRFBFB",
        "LRLRBFBFRLRLBFBF",
        "LRLRBFBFRLRLFBFB",
        "LRLRFBFBLRLRBFBF",
        "LRLRFBFBLRLRFBFB",
        "LRLRFBFBRLRLBFBF",
        "LRLRFBFBRLRLFBFB",
        "LRLRFFFFLRLRBBBB",
        "LRLRFFFFRLRLBBBB",
        "RLRLBBBBLRLRFFFF",
        "RLRLBBBBRLRLFFFF",
        "RLRLBFBFLRLRBFBF",
        "RLRLBFBFLRLRFBFB",
        "RLRLBFBFRLRLBFBF",
        "RLRLBFBFRLRLFBFB",
        "RLRLFBFBLRLRBFBF",
        "RLRLFBFBLRLRFBFB",
        "RLRLFBFBRLRLBFBF",
        "RLRLFBFBRLRLFBFB",
        "RLRLFFFFLRLRBBBB",
        "RLRLFFFFRLRLBBBB",
        "RRRRBBBBLLLLFFFF",
        "RRRRBFBFLLLLBFBF",
        "RRRRBFBFLLLLFBFB",
        "RRRRFBFBLLLLBFBF",
        "RRRRFBFBLLLLFBFB",
        "RRRRFFFFLLLLBBBB",
    )

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step31-centers.txt",
            self.state_targets,
            linecount=840,
            max_depth=5,
            all_moves=moves_444,
            illegal_moves=PHASE34_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LFRB_centers_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(LFRB_centers_444, state):
            cube[pos] = pos_state


class RubiksCube444(RubiksCube):
    reduce333_orient_edges_tuples = reduce333_orient_edges_tuples

    def sanity_check(self) -> None:
        """
        Verify the cube is valid
        """
        self._sanity_check("corners", corners_444, 4)
        self._sanity_check("centers", centers_444, 4)
        self._sanity_check("edge-orbit-0", edge_orbit_0_444, 8)

    def highlow_edges_state(self, edges_to_flip: List[str]) -> str:
        """
        Args:
            edges_to_flip: a list of wings to flip

        Returns:
            the high/low state of the cube
        """
        state = self.state

        if edges_to_flip:
            result = []
            for x, y in self.reduce333_orient_edges_tuples:
                state_x = state[x]
                state_y = state[y]
                high_low = highlow_edge_values_444[(x, y, state_x, state_y)]
                wing_str = wing_str_map[state_x + state_y]

                if wing_str in edges_to_flip:
                    if high_low == "U":
                        high_low = "D"
                    else:
                        high_low = "U"

                result.append(high_low)
        else:
            result = [
                highlow_edge_values_444[(x, y, state[x], state[y])] for (x, y) in self.reduce333_orient_edges_tuples
            ]

        result = "".join(result)
        return result

    def highlow_edges_print(self) -> None:
        """
        Print the high/low state of the cube
        """

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.highlow_edges_state(self.edge_mapping))
        orient_edge_state_index = 0
        for side in list(self.sides.values()):
            for square_index in side.edge_pos:
                self.state[square_index] = orient_edge_state[orient_edge_state_index]
                orient_edge_state_index += 1
        self.print_cube("high/low edges")

        self.state = original_state[:]
        self.solution = original_solution[:]

    def lt_init(self) -> None:
        """
        Initialize all lookup tables
        """
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_lfrb_centers = LookupTable444Reduce333LFRBCenters(self)

    def phase1_and_2(self, multiplier: float = None) -> None:
        """Stage all centers and EO the wings with ``ida_search_444_phase1_and_2``."""
        tmp_solution_len = len(self.solution)
        for filename in (
            PHASE12_ALL_CENTERS_TABLE_444,
            PHASE12_ALL_CENTERS_INDEX_444,
            PHASE12_LR_CENTERS_TABLE_444,
            PHASE12_HIGHLOW_EDGES_TABLE_444,
        ):
            download_file_if_needed(filename)

        highlow = ["."] * len(self.state)
        for (square, _), value in zip(
            self.reduce333_orient_edges_tuples,
            self.highlow_edges_state(None),
        ):
            highlow[square] = value
        cmd = [
            "./ida_search_444_phase1_and_2",
            "--kociemba",
            self.get_kociemba_string(True),
            "--highlow",
            "".join(highlow[1:]),
            "--all-center-cost",
            PHASE12_ALL_CENTERS_TABLE_444,
            "--all-center-index",
            PHASE12_ALL_CENTERS_INDEX_444,
            "--lr-cost",
            PHASE12_LR_CENTERS_TABLE_444,
            "--wing-cost",
            PHASE12_HIGHLOW_EDGES_TABLE_444,
            "--max-ida-threshold",
            "20",
        ]
        if multiplier:
            cmd.extend(("--multiplier", str(multiplier)))
        if 0 in self.center_solution_leads_to_oll_parity():
            cmd.append("--orbit0-need-odd-w")
        else:
            cmd.append("--orbit0-need-even-w")
        logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        self.solve_via_c_output = output
        solution = None
        for line in output.splitlines():
            logger.info("%s", line)
            if line.startswith("SOLUTION") and solution is None:
                solution = tuple(line.split(":", 1)[1].strip().split())
        if solution is None:
            raise SolveError(f"ida_search_444_phase1_and_2 returned no solution\n{output}")
        for step in solution:
            self.rotate(step)

        self.edge_mapping = None
        mappings = [None]
        for mapping_groups in highlow_edge_mapping_combinations.values():
            mappings.extend(mapping_groups)
        for mapping in mappings:
            if self.highlow_edges_state(mapping) == PHASE12_HIGHLOW_TARGET_444:
                self.edge_mapping = mapping or []
                break
        if self.edge_mapping is None:
            raise SolveError(
                "combined phase 1+2 solution did not produce a valid high/low edge mapping: "
                f"{solution}, {self.highlow_edges_state(None)}\n{output}"
            )
        if 0 in self.center_solution_leads_to_oll_parity():
            raise SolveError("combined phase 1+2 solution left orbit-0 OLL parity")
        self.highlow_edges_print()
        self.print_cube_add_comment("centers staged, edges EOed into high/low groups", tmp_solution_len)

    def phase3_and_4(self, consider_solve_333: bool, max_ida_threshold: int = 20) -> None:
        """Pair all 12 edges and solve the centers with ``ida_search_444_phase3_and_4``."""
        original_state = self.state[:]
        original_solution = self.solution[:]
        want = PHASE34_SOLUTIONS_TO_EVALUATE if consider_solve_333 else 1
        chosen = None
        best_total = None
        scored = 0

        download_file_if_needed(ALL_EDGES_PAIRED_TABLE_444)
        cmd = [
            "./ida_search_444_phase3_and_4",
            "--kociemba",
            self.get_kociemba_string(True),
            "--edge-pairing-cost",
            ALL_EDGES_PAIRED_TABLE_444,
            "--center-graph",
            self.lt_lfrb_centers.filename_bin,
            "--center-state-index",
            str(self.lt_lfrb_centers.state_index()),
            "--solution-count",
            "1000000",
            "--max-ida-threshold",
            str(max_ida_threshold),
        ]
        logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
        lines = []
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        ) as proc:
            for line in proc.stdout:
                lines.append(line)
                logger.info("%s", line.rstrip("\n"))
                if not line.startswith("SOLUTION"):
                    continue
                solution = tuple(line.split(":", 1)[1].strip().split())
                self.state = original_state[:]
                self.solution = original_solution[:]
                for step in solution:
                    self.rotate(step)
                if not self.reduced_to_333():
                    proc.terminate()
                    proc.wait()
                    raise SolveError(f"ida_search_444_phase3_and_4 did not reduce to 3x3x3: {solution}")
                if self.edge_solution_leads_to_pll_parity():
                    continue
                if not consider_solve_333:
                    chosen = solution
                    proc.terminate()
                    proc.wait()
                    break
                tmp_solution_len = len(self.solution)
                self.solve_333(log_cube=False)
                length_333 = len(self.solution[tmp_solution_len:]) - 1
                total = len(solution) + length_333
                desc = f"phase 3+4 is {len(solution)} steps, solve 333 in {length_333} steps, total {total}"
                if best_total is None or total < best_total:
                    logger.info("%s (NEW MIN)", desc)
                    best_total = total
                    chosen = solution
                else:
                    logger.info("%s", desc)
                scored += 1
                if length_333 <= SOLVE_333_GOOD_ENOUGH or scored >= want:
                    proc.terminate()
                    proc.wait()
                    break
            else:
                returncode = proc.wait()
                if chosen is None:
                    raise SolveError(f"ida_search_444_phase3_and_4 failed with exit {returncode}\n{''.join(lines)}")

        self.solve_via_c_output = "".join(lines)
        if chosen is None:
            raise SolveError(f"ida_search_444_phase3_and_4 returned no PLL-free solution\n{''.join(lines)}")

        self.state = original_state[:]
        self.solution = original_solution[:]
        tmp_solution_len = len(self.solution)
        for step in chosen:
            self.rotate(step)
        self.print_cube_add_comment("all edges paired, centers solved", tmp_solution_len)

    def reduced_to_333(self) -> bool:
        if "".join(self.state[x] for x in centers_444) != "UUUULLLLFFFFRRRRBBBBDDDD":
            return False

        # verify the edges are paired
        for x, y in paired_edges_444:
            if self.state[x] != self.state[y]:
                return False

        return True

    def reduce_333(self, consider_solve_333: bool = True) -> None:
        if self.reduced_to_333():
            return

        self.phase1_and_2()
        self.phase3_and_4(consider_solve_333=consider_solve_333)


def rotate_444(cube: List[str], step: str) -> List[str]:
    """
    Args:
        cube: the cube to manipulate
        step: the move to apply to the cube

    Returns:
        the cube state after applying ``step``
    """
    return [cube[x] for x in swaps_444[step]]
