# standard libraries
import itertools
import logging
from typing import Dict, List, Tuple

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube, reverse_steps, wing_str_map, wing_strs_all
from rubikscubennnsolver.LookupTable import LookupTable
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.misc import pre_steps_to_try
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

LR_centers_444: Tuple[int] = (
    22, 23, 26, 27,  # Left
    54, 55, 58, 59,  # Right
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
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = wing_str_map[square_value + partner_value]
        edge_map[wing_str].append(edge_index)

    # Where is the other wing_str like us?
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
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


class LookupTable444UDCentersStage(LookupTable):
    """
    lookup-table-4x4x4-step11-UD-centers-stage.txt
    ==============================================
    0 steps has 3 entries (0 percent, 0.00x previous step)
    1 steps has 6 entries (0 percent, 2.00x previous step)
    2 steps has 108 entries (0 percent, 18.00x previous step)
    3 steps has 1,434 entries (0 percent, 13.28x previous step)
    4 steps has 15,210 entries (2 percent, 10.61x previous step)
    5 steps has 126,306 entries (17 percent, 8.30x previous step)
    6 steps has 420,312 entries (57 percent, 3.33x previous step)
    7 steps has 171,204 entries (23 percent, 0.41x previous step)
    8 steps has 888 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    Average: 6.02 moves
    """

    state_targets: Tuple[str] = ("UUUUxxxxxxxxxxxxxxxxUUUU", "xxxxUUUUxxxxUUUUxxxxxxxx", "xxxxxxxxUUUUxxxxUUUUxxxx")

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step11-UD-centers-stage.txt",
            self.state_targets,
            linecount=735471,
            max_depth=8,
            all_moves=moves_444,
            illegal_moves=(),
            use_state_index=True,
            build_state_index=build_state_index,
            md5_bin="2835d311466ad3fada95722fb676ec1a",
            md5_state_index="d0b9bbb685a08bf985782daa78208330",
            md5_txt="a26afb9be23495b3ec19abef686901ae",
        )

    def state(self) -> str:
        """
        Returns:
            the state of the cube per this lookup table
        """
        parent_state = self.parent.state
        return "".join(["U" if parent_state[x] in ("U", "D") else "x" for x in centers_444])

    def populate_cube_from_state(self, state: str, cube: List[str], steps_to_solve: List[str]) -> None:
        """
        Given a state string, populate the cube to match that state string

        Args:
            state: the target state
            cube: the cube to manipulate
            steps_to_solve: N/A for this table
        """
        state = list(state)

        for (pos, pos_state) in zip(centers_444, state):
            cube[pos] = pos_state


class LookupTable444LRCentersStage(LookupTable):
    """
    lookup-table-4x4x4-step12-LR-centers-stage.txt
    ==============================================
    0 steps has 3 entries (0 percent, 0.00x previous step)
    1 steps has 6 entries (0 percent, 2.00x previous step)
    2 steps has 108 entries (0 percent, 18.00x previous step)
    3 steps has 1,434 entries (0 percent, 13.28x previous step)
    4 steps has 15,210 entries (2 percent, 10.61x previous step)
    5 steps has 126,306 entries (17 percent, 8.30x previous step)
    6 steps has 420,312 entries (57 percent, 3.33x previous step)
    7 steps has 171,204 entries (23 percent, 0.41x previous step)
    8 steps has 888 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    Average: 6.02 moves
    """

    state_targets: Tuple[str] = ("LLLLxxxxxxxxxxxxxxxxLLLL", "xxxxLLLLxxxxLLLLxxxxxxxx", "xxxxxxxxLLLLxxxxLLLLxxxx")

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step12-LR-centers-stage.txt",
            self.state_targets,
            linecount=735471,
            max_depth=8,
            all_moves=moves_444,
            illegal_moves=(),
            use_state_index=True,
            build_state_index=build_state_index,
            md5_bin="2835d311466ad3fada95722fb676ec1a",
            md5_state_index="79f362d800935a484dab4de8f655ca07",
            md5_txt="b8609a899722c2c9132d21b09f98c5d9",
        )

    def state(self) -> str:
        """
        Returns:
            the state of the cube per this lookup table
        """
        parent_state = self.parent.state
        return "".join(["L" if parent_state[x] in ("L", "R") else "x" for x in centers_444])

    def populate_cube_from_state(self, state: str, cube: List[str], steps_to_solve: List[str]) -> None:
        """
        Given a state string, populate the cube to match that state string

        Args:
            state: the target state
            cube: the cube to manipulate
            steps_to_solve: N/A for this table
        """
        state = list(state)

        for (pos, pos_state) in zip(centers_444, state):
            cube[pos] = pos_state


class LookupTableIDA444ULFRBDCentersStage(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_444,
            illegal_moves=(),
            prune_tables=[parent.lt_UD_centers_stage, parent.lt_LR_centers_stage],
        )


class LookupTable444HighLowEdgesEdges(LookupTable):
    """
    lookup-table-4x4x4-step21-highlow-edges-edges.txt
    =================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 278 entries (0 percent, 9.59x previous step)
    4 steps has 1,934 entries (0 percent, 6.96x previous step)
    5 steps has 15,640 entries (0 percent, 8.09x previous step)
    6 steps has 124,249 entries (4 percent, 7.94x previous step)
    7 steps has 609,241 entries (22 percent, 4.90x previous step)
    8 steps has 1,224,098 entries (45 percent, 2.01x previous step)
    9 steps has 688,124 entries (25 percent, 0.56x previous step)
    10 steps has 40,560 entries (1 percent, 0.06x previous step)

    Total: 2,704,156 entries
    Average: 7.95 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step21-highlow-edges-edges.txt",
            "UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
            linecount=2704156,
            max_depth=10,
            md5_txt="70496f999f5de71e34164fc8fd17726c",
        )


class LookupTable444HighLowEdgesCenters(LookupTable):
    """
    lookup-table-4x4x4-step22-highlow-edges-centers.txt
    ===================================================
    1 steps has 22 entries (31 percent, 0.00x previous step)
    2 steps has 16 entries (22 percent, 0.73x previous step)
    3 steps has 16 entries (22 percent, 1.00x previous step)
    4 steps has 16 entries (22 percent, 1.00x previous step)

    Total: 70 entries
    Average: 2.37 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step22-highlow-edges-centers.txt",
            (
                "LLLLRRRR",
                "LLRRLLRR",
                "LLRRRRLL",
                "LRLRLRLR",
                "LRLRRLRL",
                "LRRLRLLR",
                "RLLRLRRL",
                "RLRLLRLR",
                "RLRLRLRL",
                "RRLLLLRR",
                "RRLLRRLL",
                "RRRRLLLL",
            ),
            linecount=70,
            max_depth=4,
            md5_txt="8b9c6869ea131aeb20584f5632ae3084",
        )


class LookupTable444HighLowEdges(LookupTable):
    """
    I only kept up to depth-6 but this is the move count for the entire table.
    2,704,156 * 70 = 189,209,920

    lookup-table-4x4x4-step20-highlow-edges.txt
    ===========================================
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 34 entries (0 percent, 17.00x previous step)
    2 steps has 348 entries (0 percent, 10.24x previous step)
    3 steps has 3,416 entries (0 percent, 9.82x previous step)
    4 steps has 26,260 entries (0 percent, 7.69x previous step)
    5 steps has 226,852 entries (0 percent, 8.64x previous step)
    6 steps has 2,048,086 entries (1 percent, 9.03x previous step)
    7 steps has 15,247,140 entries (8 percent, 7.44x previous step)
    8 steps has 62,786,582 entries (33 percent, 4.12x previous step)
    9 steps has 87,604,424 entries (46 percent, 1.40x previous step)
    10 steps has 21,114,568 entries (11 percent, 0.24x previous step)
    11 steps has 233,208 entries (0 percent, 0.01x previous step)

    Total: 189,290,920 entries
    Average: 8.58 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step20-highlow-edges.txt",
            (
                "LLLLRRRRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "LLRRLLRRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "LLRRRRLLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "LRLRLRLRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "LRLRRLRLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "LRRLRLLRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "RLLRLRRLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "RLRLLRLRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "RLRLRLRLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "RRLLLLRRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "RRLLRRLLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
                "RRRRLLLLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
            ),
            all_moves=moves_444,
            legal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            linecount=2304998,
            max_depth=6,
            md5_txt="17d09599ec9d8a6b590628dd3ad60f42",
        )

    def state(self) -> str:
        """
        Returns:
            the state of the cube per this lookup table
        """
        parent_state = self.parent.state
        LR_centers = "".join([parent_state[x] for x in LR_centers_444])
        edges = self.parent.highlow_edges_state(self.parent.edge_mapping)
        return LR_centers + edges

    def ida_heuristic(self) -> Tuple[str, int]:
        """
        Returns:
            the lookup table state
            the cost to goal
        """
        parent_state = self.parent.state
        LR_centers = "".join([parent_state[x] for x in LR_centers_444])
        edges_state = self.parent.highlow_edges_state(self.parent.edge_mapping)
        lt_state = LR_centers + edges_state

        cost_to_goal = max(
            self.parent.lt_highlow_edges_edges.heuristic(edges_state),
            self.parent.lt_highlow_edges_centers.heuristic(LR_centers),
        )

        return (lt_state, cost_to_goal)


# phase 3
class LookupTable444Reduce333FirstTwoCenters(LookupTable):
    """
    lookup-tables/lookup-table-4x4x4-step31-centers.txt
    ===================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 115 entries (13 percent, 115.00x previous step)
    2 steps has 212 entries (25 percent, 1.84x previous step)
    3 steps has 288 entries (34 percent, 1.36x previous step)
    4 steps has 192 entries (22 percent, 0.67x previous step)
    5 steps has 32 entries (3 percent, 0.17x previous step)

    Total: 840 entries
    Average: 2.77 moves
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
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Rw", "Rw'",
                "Bw", "Bw'",
                "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LFRB_centers_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(LFRB_centers_444, state):
            cube[pos] = pos_state


class LookupTable444Reduce333FirstFourEdges(LookupTable):
    """
    lookup-tables/lookup-table-4x4x4-step32-first-four-edges.txt
    ============================================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 27 entries (0 percent, 6.75x previous step)
    3 steps has 216 entries (0 percent, 8.00x previous step)
    4 steps has 1,418 entries (0 percent, 6.56x previous step)
    5 steps has 9,623 entries (0 percent, 6.79x previous step)
    6 steps has 63,448 entries (1 percent, 6.59x previous step)
    7 steps has 365,270 entries (6 percent, 5.76x previous step)
    8 steps has 1,548,382 entries (26 percent, 4.24x previous step)
    9 steps has 3,061,324 entries (52 percent, 1.98x previous step)
    10 steps has 830,336 entries (14 percent, 0.27x previous step)
    11 steps has 552 entries (0 percent, 0.00x previous step)

    Total: 5,880,600 entries
    Average: 8.71 moves
    """

    state_targets = ("--------a8b9ecfd--------",)

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step32-first-four-edges.txt",
            self.state_targets,
            linecount=5880600,
            max_depth=11,
            all_moves=moves_444,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Rw", "Rw'",
                "Bw", "Bw'",
                "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )
        self.only_colors = []

    def state(self):
        if self.only_colors:
            first_four_edges = self.only_colors
        else:
            first_four_edges = ("LB", "LF", "RB", "RF")

        state = edges_recolor_pattern_444(self.parent.state[:], first_four_edges)
        return "".join([state[index] for index in wings_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        # fmt: off
        non_x_plane_edges_444 = (
            2, 3, 5, 8, 9, 12, 14, 15,  # Upper
            18, 19, 30, 31,  # Left
            34, 35, 46, 47,  # Front
            50, 51, 62, 63,  # Right
            66, 67, 78, 79,  # Back
            82, 83, 85, 88, 89, 92, 94, 95,  # Down
        )
        # fmt: on

        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        # start with a solved cube
        self.parent.state = ["x"]
        self.parent.state.extend(
            list("UUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDD")
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()

        for pos in non_x_plane_edges_444:
            self.parent.state[pos] = "-"

        for step in steps_to_scramble:
            self.parent.rotate(step)


class LookupTableIDA444Phase3(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_444,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Rw", "Rw'",
                "Bw", "Bw'",
                "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
            ),
            # fmt: on
            prune_tables=[parent.lt_phase3_centers, parent.lt_phase3_edges],
        )


# phase 4
class LookupTable444Reduce333Centers(LookupTable):
    """
    lookup-tables/lookup-table-4x4x4-step41-centers.txt
    ===================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 42 entries (1 percent, 10.50x previous step)
    3 steps has 244 entries (9 percent, 5.81x previous step)
    4 steps has 774 entries (30 percent, 3.17x previous step)
    5 steps has 878 entries (34 percent, 1.13x previous step)
    6 steps has 569 entries (22 percent, 0.65x previous step)
    7 steps has 8 entries (0 percent, 0.01x previous step)

    Total: 2,520 entries
    Average: 4.67 moves
    """

    state_targets = ("UUUULLLLFFFFRRRRBBBBDDDD",)

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step41-centers.txt",
            self.state_targets,
            linecount=2520,
            max_depth=7,
            all_moves=moves_444,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Rw", "Rw'",
                "Bw", "Bw'",
                "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "Uw2",
                "Dw2",
                "F", "F'",
                "B", "B'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in centers_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(centers_444, state):
            cube[pos] = pos_state


# phase 4
class LookupTable444Reduce333LastEightEdges(LookupTable):
    """
    lookup-tables/lookup-table-4x4x4-step42-last-eight-edges.txt
    ============================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 10 entries (0 percent, 3.33x previous step)
    3 steps has 36 entries (0 percent, 3.60x previous step)
    4 steps has 165 entries (0 percent, 4.58x previous step)
    5 steps has 606 entries (3 percent, 3.67x previous step)
    6 steps has 1,937 entries (9 percent, 3.20x previous step)
    7 steps has 5,172 entries (25 percent, 2.67x previous step)
    8 steps has 7,719 entries (38 percent, 1.49x previous step)
    9 steps has 4,344 entries (21 percent, 0.56x previous step)
    10 steps has 168 entries (0 percent, 0.04x previous step)

    Total: 20,160 entries
    Average: 7.65 moves
    """

    state_targets = ("10425376--------hgkiljnm",)

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step42-last-eight-edges.txt",
            self.state_targets,
            linecount=20160,
            max_depth=10,
            all_moves=moves_444,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Rw", "Rw'",
                "Bw", "Bw'",
                "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "Uw2",
                "Dw2",
                "F", "F'",
                "B", "B'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        if hasattr(self.parent, "lt_phase3_edges") and self.parent.lt_phase3_edges.only_colors:
            last_eight_colors = []

            for wing_str_combo in wing_strs_all:
                if wing_str_combo not in self.parent.lt_phase3_edges.only_colors:
                    last_eight_colors.append(wing_str_combo)
        else:
            last_eight_colors = ("UB", "UL", "UR", "UF", "DB", "DL", "DR", "DF")

        state = edges_recolor_pattern_444(self.parent.state[:], last_eight_colors)
        return "".join([state[index] for index in wings_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        # fmt: off
        x_plane_edges_444 = (
            21, 24, 25, 28,  # Left
            37, 40, 41, 44,  # Front
            53, 56, 57, 60,  # Right
            69, 72, 73, 76,  # Back
        )
        # fmt: on

        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        # start with a solved cube
        self.parent.state = ["x"]
        self.parent.state.extend(
            list("UUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDD")
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()

        for pos in x_plane_edges_444:
            self.parent.state[pos] = "-"

        for step in steps_to_scramble:
            self.parent.rotate(step)


class LookupTableIDA444Phase4(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_444,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Rw", "Rw'",
                "Bw", "Bw'",
                "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "Uw2",
                "Dw2",
                "F", "F'",
                "B", "B'",
            ),
            # fmt: on
            prune_tables=[parent.lt_phase4_centers, parent.lt_phase4_edges],
        )


class RubiksCube444(RubiksCube):

    instantiated = False

    reduce333_orient_edges_tuples: Tuple[Tuple[int, int]] = (
        (2, 67),  # Upper
        (3, 66),
        (5, 18),
        (8, 51),
        (9, 19),
        (12, 50),
        (14, 34),
        (15, 35),
        (18, 5),  # Left
        (19, 9),
        (21, 72),
        (24, 37),
        (25, 76),
        (28, 41),
        (30, 89),
        (31, 85),
        (34, 14),  # Front
        (35, 15),
        (37, 24),
        (40, 53),
        (41, 28),
        (44, 57),
        (46, 82),
        (47, 83),
        (50, 12),  # Right
        (51, 8),
        (53, 40),
        (56, 69),
        (57, 44),
        (60, 73),
        (62, 88),
        (63, 92),
        (66, 3),  # Back
        (67, 2),
        (69, 56),
        (72, 21),
        (73, 60),
        (76, 25),
        (78, 95),
        (79, 94),
        (82, 46),  # Down
        (83, 47),
        (85, 31),
        (88, 62),
        (89, 30),
        (92, 63),
        (94, 79),
        (95, 78),
    )

    def __init__(self, state: str, order: str, colormap: Dict = None, avoid_pll: bool = True, debug: bool = False):
        RubiksCube.__init__(self, state, order, colormap, debug)
        self.avoid_pll = avoid_pll
        self.edge_mapping = {}

        if RubiksCube444.instantiated:
            logger.warning("Another 4x4x4 instance is being created")
        else:
            RubiksCube444.instantiated = True

        if debug:
            logger.setLevel(logging.DEBUG)

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
            for (x, y) in self.reduce333_orient_edges_tuples:
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

        self.lt_UD_centers_stage = LookupTable444UDCentersStage(self)
        self.lt_LR_centers_stage = LookupTable444LRCentersStage(self)
        self.lt_ULFRBD_centers_stage = LookupTableIDA444ULFRBDCentersStage(self)
        self.lt_ULFRBD_centers_stage.avoid_oll = 0  # avoid OLL on orbit 0

        self.lt_highlow_edges_centers = LookupTable444HighLowEdgesCenters(self)
        self.lt_highlow_edges_edges = LookupTable444HighLowEdgesEdges(self)
        self.lt_highlow_edges = LookupTable444HighLowEdges(self)

        self.lt_phase3_centers = LookupTable444Reduce333FirstTwoCenters(self)
        self.lt_phase3_edges = LookupTable444Reduce333FirstFourEdges(self)
        self.lt_phase3 = LookupTableIDA444Phase3(self)

        self.lt_phase4_centers = LookupTable444Reduce333Centers(self)
        self.lt_phase4_edges = LookupTable444Reduce333LastEightEdges(self)
        self.lt_phase4 = LookupTableIDA444Phase4(self)

    def phase1(self) -> None:
        self.original_state = self.state[:]
        self.original_solution = self.solution[:]

        if not self.centers_staged():
            self.lt_ULFRBD_centers_stage.solve_via_c()

        self.rotate_for_best_centers_staging(centers_444)
        phase1_solution_len = len(self.solution)
        self.solution.append(f"COMMENT_{self.get_solution_len_minus_rotates(self.solution)}_steps_444_phase1")
        self.print_cube(f"{self}: end of phase1 ({self.get_solution_len_minus_rotates(self.solution)} steps in)")

        # This can happen on the large NNN cubes that are using 444 to pair their inside orbit of edges.
        # We need the edge swaps to be even for our edges lookup table to work.
        if self.edge_swaps_odd(False, 0, False):
            logger.warning(f"{self}: edge swaps are odd, running prevent_OLL to correct")
            self.prevent_OLL()
            self.print_cube(
                f"{self}: end of prevent_OLL ({self.get_solution_len_minus_rotates(self.solution)} steps in)"
            )
            self.solution.append(
                f"COMMENT_{self.get_solution_len_minus_rotates(self.solution[phase1_solution_len:])}_steps_prevent_OLL"
            )

    def phase2(self) -> None:
        # Pick the best edge_mapping
        # - an edge_mapping that gives us a hit in the phase2 table is ideal
        #     - pick the best among those
        # - if not pick the one that has the lowest edges_cost
        # - build the phase2 table out to 7-deep to help here
        original_state = self.state[:]
        original_solution = self.solution[:]
        phase1_solution_len = len(self.solution)

        for pre_steps in pre_steps_to_try:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in pre_steps:
                self.rotate(step)

            tmp_state = self.state[:]
            tmp_solution = self.solution[:]

            # Build a list of all 2048 states we need to find in the step20-highlow-edges table.
            # We do this so we can leverage binary_search_multiple() which runs about a million
            # times faster than binary searching for all 2048 states one at a time. This allows
            # us to NOT load this file into memory.
            high_low_states_to_find = []
            edge_mapping_for_phase2_state = {}

            # for (edges_to_flip_count, edges_to_flip_sets) in highlow_edge_mapping_combinations.items():
            for edges_to_flip_sets in highlow_edge_mapping_combinations.values():
                for edge_mapping in edges_to_flip_sets:
                    self.state = tmp_state[:]
                    self.solution = tmp_solution[:]

                    self.edge_mapping = edge_mapping
                    phase2_state = self.lt_highlow_edges.state()
                    edge_mapping_for_phase2_state[phase2_state] = edge_mapping
                    high_low_states_to_find.append(phase2_state)

            high_low_states = self.lt_highlow_edges.binary_search_multiple(high_low_states_to_find)
            min_edge_mapping = None
            min_phase2_cost = None
            min_phase2_steps = None

            for (phase2_state, phase2_steps) in sorted(high_low_states.items()):
                self.state = tmp_state[:]
                self.solution = tmp_solution[:]
                phase2_steps = phase2_steps.split()
                phase2_cost = len(phase2_steps)
                desc = f"{self}: edge_mapping {min_edge_mapping}, phase2 cost {phase2_cost}"

                if min_phase2_cost is None or phase2_cost < min_phase2_cost:
                    min_phase2_cost = phase2_cost
                    min_edge_mapping = edge_mapping_for_phase2_state[phase2_state]
                    min_phase2_steps = list(pre_steps) + phase2_steps[:]
                    logger.info(f"{desc} (NEW MIN)")
                elif phase2_cost == min_phase2_cost:
                    logger.info(f"{desc} (TIE)")
                else:
                    logger.debug(desc)

            if min_edge_mapping:
                if pre_steps:
                    logger.info(f"pre-steps {pre_steps} required to find a hit")
                break
        else:
            assert False, "write some code to find the best edge_mapping when there is no phase2 hit"

        self.state = original_state[:]
        self.solution = original_solution[:]
        self.edge_mapping = min_edge_mapping

        # Test the prune tables
        # self.lt_highlow_edges_centers.solve()
        # self.lt_highlow_edges_edges.solve()
        # self.print_cube()
        # self.highlow_edges_print()
        # sys.exit(0)

        for step in min_phase2_steps:
            self.rotate(step)

        self.solution.append(
            f"COMMENT_{self.get_solution_len_minus_rotates(self.solution[phase1_solution_len:])}_steps_444_phase2"
        )
        self.highlow_edges_print()
        self.print_cube(f"{self}: end of phase2 ({self.get_solution_len_minus_rotates(self.solution)} steps in)")

    def phase3(self, wing_str_combo: List[str] = None):
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)

        # phase 3 - search for all wing_strs
        pt_state_indexes = []
        phase3_pt_state_indexes_to_wing_str_combo = {}

        for wing_str_combo in itertools.combinations(wing_strs_all, 4):
            self.state = original_state[:]
            self.solution = original_solution[:]

            self.lt_phase3_edges.only_colors = wing_str_combo
            wing_str_combo_pt_state_indexes = tuple([pt.state_index() for pt in self.lt_phase3.prune_tables])
            phase3_pt_state_indexes_to_wing_str_combo[wing_str_combo_pt_state_indexes] = wing_str_combo
            pt_state_indexes.append(wing_str_combo_pt_state_indexes)

        self.state = original_state[:]
        self.solution = original_solution[:]
        phase3_solutions = self.lt_phase3.solutions_via_c(pt_states=pt_state_indexes)

        phase3_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) = phase3_solutions[0]
        wing_str_combo = phase3_pt_state_indexes_to_wing_str_combo[(pt0_state, pt1_state)]
        self.lt_phase3_edges.only_colors = wing_str_combo

        for step in phase3_solution:
            self.rotate(step)

        self.print_cube(f"{self}: end of phase3 ({self.get_solution_len_minus_rotates(self.solution)} steps in)")
        self.solution.append(
            f"COMMENT_{self.get_solution_len_minus_rotates(self.solution[original_solution_len:])}_steps_444_phase3"
        )

    def phase4(self, max_ida_threshold: int = None):
        tmp_solution_len = len(self.solution)
        phase4_solutions = self.lt_phase4.solutions_via_c(max_ida_threshold=max_ida_threshold, solution_count=500)
        original_state = self.state[:]
        original_solution = self.solution[:]

        for phase4_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) in phase4_solutions:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in phase4_solution:
                self.rotate(step)

            if not self.edge_solution_leads_to_pll_parity():
                logger.info(f"{self}: {phase4_solution} avoids PLL")
                break
        else:
            logger.info(f"{self}: could not find a phase4 solution that avoids PLL")

        self.print_cube(f"{self}: end of phase4 ({self.get_solution_len_minus_rotates(self.solution)} steps in)")
        self.solution.append(
            f"COMMENT_{self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])}_steps_444_phase4"
        )

    def phase3_and_4(self, consider_solve_333: bool):
        original_state = self.state[:]
        original_solution = self.solution[:]

        # phase 3 - search for all wing_strs
        pt_state_indexes = []
        phase3_pt_state_indexes_to_wing_str_combo = {}

        for wing_str_combo in itertools.combinations(wing_strs_all, 4):
            self.state = original_state[:]
            self.solution = original_solution[:]

            self.lt_phase3_edges.only_colors = wing_str_combo
            wing_str_combo_pt_state_indexes = tuple([pt.state_index() for pt in self.lt_phase3.prune_tables])
            phase3_pt_state_indexes_to_wing_str_combo[wing_str_combo_pt_state_indexes] = wing_str_combo
            pt_state_indexes.append(wing_str_combo_pt_state_indexes)

        self.state = original_state[:]
        self.solution = original_solution[:]
        phase3_solutions = self.lt_phase3.solutions_via_c(
            pt_states=pt_state_indexes, solution_count=5000, find_extra=False
        )
        logger.info(f"found {len(phase3_solutions)} phase3 solutions")

        # phase 4 - search for all of the phase3 wing_strs
        pt_state_indexes = []
        phase4_pt_state_indexes_to_phase3_solution = {}
        phase4_pt_state_indexes_to_wing_str_combo = {}

        for phase3_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) in phase3_solutions:
            wing_str_combo = phase3_pt_state_indexes_to_wing_str_combo[(pt0_state, pt1_state)]
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in phase3_solution:
                self.rotate(step)

            self.lt_phase3_edges.only_colors = wing_str_combo
            wing_str_combo_pt_state_indexes = tuple([pt.state_index() for pt in self.lt_phase4.prune_tables])
            phase4_pt_state_indexes_to_wing_str_combo[wing_str_combo_pt_state_indexes] = wing_str_combo
            phase4_pt_state_indexes_to_phase3_solution[wing_str_combo_pt_state_indexes] = phase3_solution
            pt_state_indexes.append(wing_str_combo_pt_state_indexes)

        # find a phase 4 solution that does NOT lead to PLL
        self.state = original_state[:]
        self.solution = original_solution[:]
        solutions_without_pll = []
        solutions_without_pll_states = set()
        solutions_with_pll = set()
        solution_count = 1000

        # disable INFO messages as we try many phase4 solutions
        logging.getLogger().setLevel(logging.WARNING)

        # If we did not find a PLL free solution then increase solution_count by 1000 and try again.
        # We do this until we evaluate enough phase4 solutions that one of them happens to be PLL free.
        while not solutions_without_pll:
            phase4_solutions = self.lt_phase4.solutions_via_c(
                pt_states=pt_state_indexes, solution_count=solution_count, find_extra=True
            )

            for phase4_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) in phase4_solutions:
                wing_str_combo = phase4_pt_state_indexes_to_wing_str_combo[(pt0_state, pt1_state)]
                phase3_solution = phase4_pt_state_indexes_to_phase3_solution[(pt0_state, pt1_state)]

                if (phase3_solution, phase4_solution) in solutions_with_pll:
                    continue

                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in phase3_solution:
                    self.rotate(step)

                for step in phase4_solution:
                    self.rotate(step)

                if self.edge_solution_leads_to_pll_parity():
                    solutions_with_pll.add((phase3_solution, phase4_solution))
                else:
                    if tuple(self.state) in solutions_without_pll_states:
                        continue
                    else:
                        solutions_without_pll.append((phase3_solution, phase4_solution))
                        solutions_without_pll_states.add(tuple(self.state))

            logger.warning(
                f"found {len(phase4_solutions)} phase4 solutions with --solution-count {solution_count}, {len(solutions_without_pll)} solutions without PLL"
            )
            solution_count += 1000

        # sort solutions_without_pll by shortest phase3 + phase4 length
        by_length = []
        for (phase3_solution, phase4_solution) in solutions_without_pll:
            by_length.append((len(phase3_solution) + len(phase4_solution), (phase3_solution, phase4_solution)))
        by_length.sort()
        solutions_without_pll = [x[1] for x in by_length]

        if consider_solve_333:
            min_solution = []
            min_solution_len = None
            PHASE_34_SOLUTIONS_TO_EVALUATE = 5

            for (phase3_solution, phase4_solution) in solutions_without_pll[:PHASE_34_SOLUTIONS_TO_EVALUATE]:
                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in phase3_solution:
                    self.rotate(step)

                for step in phase4_solution:
                    self.rotate(step)

                tmp_solution_len = len(self.solution)
                self.solve_333()
                solve_333_solution_len = len(self.solution[tmp_solution_len:]) - 1  # -1 for the comment
                solution_len = len(phase3_solution) + len(phase4_solution) + solve_333_solution_len
                desc = f"phase 3 is {len(phase3_solution)} steps, phase 4 is {len(phase4_solution)} steps, solve 333 in {solve_333_solution_len} steps, total {solution_len}"

                if min_solution_len is None or solution_len < min_solution_len:
                    logger.warning(f"{desc} (NEW MIN)")
                    min_solution_len = solution_len
                    min_solution = (phase3_solution, phase4_solution)
                else:
                    logger.warning(desc)

            min_phase34_solution = min_solution
        else:
            min_phase34_solution = solutions_without_pll[0]

        logging.getLogger().setLevel(logging.INFO)
        self.state = original_state[:]
        self.solution = original_solution[:]
        (phase3_solution, phase4_solution) = min_phase34_solution

        # apply the phase 3 solution
        tmp_solution_len = len(self.solution)
        for step in phase3_solution:
            self.rotate(step)
        self.print_cube(f"{self}: end of phase3 ({self.get_solution_len_minus_rotates(self.solution)} steps in)")
        self.solution.append(
            f"COMMENT_{self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])}_steps_444_phase3"
        )

        # apply the phase 4 solution
        tmp_solution_len = len(self.solution)
        for step in phase4_solution:
            self.rotate(step)
        self.print_cube(f"{self}: end of phase4 ({self.get_solution_len_minus_rotates(self.solution)} steps in)")
        self.solution.append(
            f"COMMENT_{self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])}_steps_444_phase4"
        )

    def reduce_333(self, consider_solve_333: bool = True) -> None:
        self.phase1()
        self.phase2()
        # self.phase3()
        # self.phase4()
        self.phase3_and_4(consider_solve_333=consider_solve_333)

        self.solution.append("CENTERS_SOLVED")
        self.solution.append("EDGES_GROUPED")


def rotate_444(cube: List[str], step: str) -> List[str]:
    """
    Args:
        cube: the cube to manipulate
        step: the move to apply to the cube

    Returns:
        the cube state after applying ``step``
    """
    return [cube[x] for x in swaps_444[step]]
