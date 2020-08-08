# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube, wing_str_map
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDAViaC
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.misc import pre_steps_to_try
from rubikscubennnsolver.RubiksCube444Misc import highlow_edge_mapping_combinations
from rubikscubennnsolver.RubiksCubeHighLow import highlow_edge_values_444
from rubikscubennnsolver.swaps import swaps_444

log = logging.getLogger(__name__)

moves_444 = (
    "U",
    "U'",
    "U2",
    "Uw",
    "Uw'",
    "Uw2",
    "L",
    "L'",
    "L2",
    "Lw",
    "Lw'",
    "Lw2",
    "F",
    "F'",
    "F2",
    "Fw",
    "Fw'",
    "Fw2",
    "R",
    "R'",
    "R2",
    "Rw",
    "Rw'",
    "Rw2",
    "B",
    "B'",
    "B2",
    "Bw",
    "Bw'",
    "Bw2",
    "D",
    "D'",
    "D2",
    "Dw",
    "Dw'",
    "Dw2",
    # slices...not used for now
    # "2U", "2U'", "2U2", "2D", "2D'", "2D2",
    # "2L", "2L'", "2L2", "2R", "2R'", "2R2",
    # "2F", "2F'", "2F2", "2B", "2B'", "2B2"
)

solved_444 = "UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB"

centers_444 = (
    6,
    7,
    10,
    11,  # Upper
    22,
    23,
    26,
    27,  # Left
    38,
    39,
    42,
    43,  # Front
    54,
    55,
    58,
    59,  # Right
    70,
    71,
    74,
    75,  # Back
    86,
    87,
    90,
    91,  # Down
)

LFRB_centers_444 = (22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75)  # Left  # Front  # Right  # Back

LR_centers_444 = (22, 23, 26, 27, 54, 55, 58, 59)  # Left  # Right

corners_444 = (1, 4, 13, 16, 17, 20, 29, 32, 33, 36, 45, 48, 49, 52, 61, 64, 65, 68, 77, 80, 81, 84, 93, 96)

edges_444 = (
    2,
    3,
    5,
    8,
    9,
    12,
    14,
    15,  # Upper
    18,
    19,
    21,
    24,
    25,
    28,
    30,
    31,  # Left
    34,
    35,
    37,
    40,
    41,
    44,
    46,
    47,  # Front
    50,
    51,
    53,
    56,
    57,
    60,
    62,
    63,  # Right
    66,
    67,
    69,
    72,
    73,
    76,
    78,
    79,  # Back
    82,
    83,
    85,
    88,
    89,
    92,
    94,
    95,  # Down
)

wings_444 = (
    2,
    3,
    5,
    9,
    8,
    12,
    14,
    15,  # Upper
    21,
    25,
    24,
    28,  # Left
    53,
    57,
    56,
    60,  # Right
    82,
    83,
    85,
    89,
    88,
    92,
    94,
    95,  # Back
)

edges_partner_444 = {
    2: 67,
    3: 66,
    5: 18,
    8: 51,
    9: 19,
    12: 50,
    14: 34,
    15: 35,
    18: 5,
    19: 9,
    21: 72,
    24: 37,
    25: 76,
    28: 41,
    30: 89,
    31: 85,
    34: 14,
    35: 15,
    37: 24,
    40: 53,
    41: 28,
    44: 57,
    46: 82,
    47: 83,
    50: 12,
    51: 8,
    53: 40,
    56: 69,
    57: 44,
    60: 73,
    62: 88,
    63: 92,
    66: 3,
    67: 2,
    69: 56,
    72: 21,
    73: 60,
    76: 25,
    78: 95,
    79: 94,
    82: 46,
    83: 47,
    85: 31,
    88: 62,
    89: 30,
    92: 63,
    94: 79,
    95: 78,
}

wings_for_edges_recolor_pattern_444 = (
    ("0", 2, 67),  # upper
    ("1", 3, 66),
    ("2", 5, 18),
    ("3", 8, 51),
    ("4", 9, 19),
    ("5", 12, 50),
    ("6", 14, 34),
    ("7", 15, 35),
    ("8", 21, 72),  # left
    ("9", 24, 37),
    ("a", 25, 76),
    ("b", 28, 41),
    ("c", 53, 40),  # right
    ("d", 56, 69),
    ("e", 57, 44),
    ("f", 60, 73),
    ("g", 82, 46),  # down
    ("h", 83, 47),
    ("i", 85, 31),
    ("j", 88, 62),
    ("k", 89, 30),
    ("l", 92, 63),
    ("m", 94, 79),
    ("n", 95, 78),
)

symmetry_rotations_tsai_phase3_444 = (
    (),
    ("x",),
    ("x'",),
    ("x", "x"),
    ("y", "y"),
    ("z", "z"),
    ("x", "y", "y"),
    ("x", "z", "z"),
    ("reflect-x",),
    ("reflect-x", "x"),
    ("reflect-x", "x'"),
    ("reflect-x", "x", "x"),
    ("reflect-x", "y", "y"),
    ("reflect-x", "z", "z"),
    ("reflect-x", "x", "y", "y"),
    ("reflect-x", "x", "z", "z"),
)


def edges_recolor_pattern_444(state, only_colors=[]):

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

    state_targets = ("UUUUxxxxxxxxxxxxxxxxUUUU", "xxxxUUUUxxxxUUUUxxxxxxxx", "xxxxxxxxUUUUxxxxUUUUxxxx")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step11-UD-centers-stage.txt",
            self.state_targets,
            linecount=735471,
            max_depth=8,
            filesize=40450905,
            all_moves=moves_444,
            illegal_moves=("Lw", "Lw'", "Lw2", "Bw", "Bw'", "Bw2", "Dw", "Dw'", "Dw2"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join(["U" if parent_state[x] in ("U", "D") else "x" for x in centers_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
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

    state_targets = ("LLLLxxxxxxxxxxxxxxxxLLLL", "xxxxLLLLxxxxLLLLxxxxxxxx", "xxxxxxxxLLLLxxxxLLLLxxxx")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step12-LR-centers-stage.txt",
            self.state_targets,
            linecount=735471,
            max_depth=8,
            filesize=40450905,
            all_moves=moves_444,
            illegal_moves=("Lw", "Lw'", "Lw2", "Bw", "Bw'", "Bw2", "Dw", "Dw'", "Dw2"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join(["L" if parent_state[x] in ("L", "R") else "x" for x in centers_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(centers_444, state):
            cube[pos] = pos_state


class LookupTable444FBCentersStage(LookupTable):
    """
    lookup-table-4x4x4-step13-FB-centers-stage.txt
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

    state_targets = ("FFFFxxxxxxxxxxxxxxxxFFFF", "xxxxFFFFxxxxFFFFxxxxxxxx", "xxxxxxxxFFFFxxxxFFFFxxxx")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-4x4x4-step13-FB-centers-stage.txt",
            self.state_targets,
            linecount=735471,
            max_depth=8,
            filesize=40450905,
            all_moves=moves_444,
            illegal_moves=("Lw", "Lw'", "Lw2", "Bw", "Bw'", "Bw2", "Dw", "Dw'", "Dw2"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join(["F" if parent_state[x] in ("F", "B") else "x" for x in centers_444])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(centers_444, state):
            cube[pos] = pos_state


class LookupTableIDA444ULFRBDCentersStage(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_444,
            illegal_moves=("Lw", "Lw'", "Lw2", "Bw", "Bw'", "Bw2", "Dw", "Dw'", "Dw2"),
            prune_tables=[
                parent.lt_UD_centers_stage,
                parent.lt_LR_centers_stage,
                # parent.lt_FB_centers_stage,
            ],
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
            filesize=227149104,
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
            filesize=1610,
        )


class LookupTable444HighLowEdges(LookupTable):
    """
    lookup-table-4x4x4-step20-highlow-edges.txt
    ===========================================
    1 steps has 36 entries (0 percent, 0.00x previous step)
    2 steps has 348 entries (0 percent, 9.67x previous step)
    3 steps has 3,416 entries (0 percent, 9.82x previous step)
    4 steps has 26,260 entries (1 percent, 7.69x previous step)
    5 steps has 226,852 entries (9 percent, 8.64x previous step)
    6 steps has 2,048,086 entries (88 percent, 9.03x previous step)

    Total: 2,304,998 entries
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
            filesize=182094842,
        )

    def state(self):
        parent_state = self.parent.state
        LR_centers = "".join([parent_state[x] for x in LR_centers_444])
        edges = self.parent.highlow_edges_state(self.parent.edge_mapping)
        return LR_centers + edges

    def ida_heuristic(self):
        parent_state = self.parent.state
        LR_centers = "".join([parent_state[x] for x in LR_centers_444])
        edges_state = self.parent.highlow_edges_state(self.parent.edge_mapping)
        lt_state = LR_centers + edges_state

        cost_to_goal = max(
            self.parent.lt_highlow_edges_edges.heuristic(edges_state),
            self.parent.lt_highlow_edges_centers.heuristic(LR_centers),
        )

        return (lt_state, cost_to_goal)


class LookupTableIDA444Reduce333(LookupTableIDAViaC):
    """
    lookup-table-4x4x4-step31-reduce333-edges.txt
    =============================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 20 entries (0 percent, 5.00x previous step)
    3 steps has 140 entries (0 percent, 7.00x previous step)
    4 steps has 1,141 entries (0 percent, 8.15x previous step)
    5 steps has 8,059 entries (0 percent, 7.06x previous step)
    6 steps has 62,188 entries (0 percent, 7.72x previous step)
    7 steps has 442,293 entries (0 percent, 7.11x previous step)
    8 steps has 2,958,583 entries (1 percent, 6.69x previous step)
    9 steps has 17,286,512 entries (7 percent, 5.84x previous step)
    10 steps has 69,004,356 entries (28 percent, 3.99x previous step)
    11 steps has 122,416,936 entries (51 percent, 1.77x previous step)
    12 steps has 27,298,296 entries (11 percent, 0.22x previous step)
    13 steps has 22,272 entries (0 percent, 0.00x previous step)

    Total: 239,500,800 entries
    Average: 10.635709 moves


    lookup-table-4x4x4-step32-reduce333-centers.txt
    ===============================================
    1 steps has 16 entries (0 percent, 0.00x previous step)
    2 steps has 136 entries (0 percent, 8.50x previous step)
    3 steps has 952 entries (1 percent, 7.00x previous step)
    4 steps has 4,048 entries (6 percent, 4.25x previous step)
    5 steps has 10,588 entries (18 percent, 2.62x previous step)
    6 steps has 16,620 entries (28 percent, 1.57x previous step)
    7 steps has 16,392 entries (27 percent, 0.99x previous step)
    8 steps has 8,768 entries (14 percent, 0.53x previous step)
    9 steps has 1,280 entries (2 percent, 0.15x previous step)

    Total: 58,800 entries
    Average: 6.27 moves


    lookup-table-4x4x4-step30-reduce333.txt
    =======================================
    1 steps has 16 entries (0 percent, 0.00x previous step)
    2 steps has 136 entries (0 percent, 8.50x previous step)
    3 steps has 1,424 entries (0 percent, 10.47x previous step)
    4 steps has 14,032 entries (0 percent, 9.85x previous step)
    5 steps has 134,052 entries (9 percent, 9.55x previous step)
    6 steps has 1,290,292 entries (89 percent, 9.63x previous step)

    Total: 1,439,952 entries
    """

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (
                ("lookup-table-4x4x4-step30-reduce333.txt", 73437552, "82fbc3414d07e53448d0746d96e25ebd"),  # 6-deep
                (
                    "lookup-table-4x4x4-step31-reduce333-edges.hash-cost-only.txt",
                    239500848,
                    "20ac2ed7ca369c3b5183f836f5d99262",
                ),
                (
                    "lookup-table-4x4x4-step32-reduce333-centers.hash-cost-only.txt",
                    None,
                    "3f990fc1fb6bf506d81ba65f03ad74f6",
                ),
            ),
            "4x4x4-reduce-333",  # C_ida_type
        )


class RubiksCube444(RubiksCube):

    instantiated = False

    reduce333_orient_edges_tuples = (
        (2, 67),
        (3, 66),
        (5, 18),
        (8, 51),
        (9, 19),
        (12, 50),
        (14, 34),
        (15, 35),
        (18, 5),
        (19, 9),
        (21, 72),
        (24, 37),
        (25, 76),
        (28, 41),
        (30, 89),
        (31, 85),
        (34, 14),
        (35, 15),
        (37, 24),
        (40, 53),
        (41, 28),
        (44, 57),
        (46, 82),
        (47, 83),
        (50, 12),
        (51, 8),
        (53, 40),
        (56, 69),
        (57, 44),
        (60, 73),
        (62, 88),
        (63, 92),
        (66, 3),
        (67, 2),
        (69, 56),
        (72, 21),
        (73, 60),
        (76, 25),
        (78, 95),
        (79, 94),
        (82, 46),
        (83, 47),
        (85, 31),
        (88, 62),
        (89, 30),
        (92, 63),
        (94, 79),
        (95, 78),
    )

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False):
        RubiksCube.__init__(self, state, order, colormap, debug)
        self.avoid_pll = avoid_pll
        self.edge_mapping = {}

        if RubiksCube444.instantiated:
            # raise Exception("Another 4x4x4 instance is being created")
            log.warning("Another 4x4x4 instance is being created")
        else:
            RubiksCube444.instantiated = True

        if debug:
            log.setLevel(logging.DEBUG)

    def phase(self):
        if self._phase is None:
            self._phase = "Stage UD centers"
            return self._phase

        if self._phase == "Stage UD centers":
            if self.UD_centers_staged():
                self._phase = "Stage LR centers"
            return self._phase

        if self._phase == "Stage LR centers":
            if self.LR_centers_staged():
                self._phase = "Solve Centers"

        if self._phase == "Solve Centers":
            if self.centers_solved():
                self._phase = "Pair Edges"

        if self._phase == "Pair Edges":
            if not self.get_non_paired_edges():
                self._phase = "Solve 3x3x3"

        return self._phase

    def sanity_check(self):
        edge_orbit_0 = (
            2,
            3,
            8,
            12,
            15,
            14,
            9,
            5,
            18,
            19,
            24,
            28,
            31,
            30,
            25,
            21,
            34,
            35,
            40,
            44,
            47,
            46,
            41,
            37,
            50,
            51,
            56,
            60,
            62,
            63,
            57,
            53,
            66,
            67,
            72,
            76,
            79,
            78,
            73,
            69,
            82,
            83,
            88,
            92,
            95,
            94,
            89,
            85,
        )

        self._sanity_check("corners", corners_444, 4)
        self._sanity_check("centers", centers_444, 4)
        self._sanity_check("edge-orbit-0", edge_orbit_0, 8)

    def highlow_edges_state(self, edges_to_flip):
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

    def highlow_edges_print(self):

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
        self.print_cube()

        self.state = original_state[:]
        self.solution = original_solution[:]

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_centers_stage = LookupTable444UDCentersStage(self)
        self.lt_LR_centers_stage = LookupTable444LRCentersStage(self)
        self.lt_FB_centers_stage = LookupTable444FBCentersStage(self)

        self.lt_ULFRBD_centers_stage = LookupTableIDA444ULFRBDCentersStage(self)
        self.lt_ULFRBD_centers_stage.avoid_oll = 0  # avoid OLL on orbit 0

        self.lt_highlow_edges_centers = LookupTable444HighLowEdgesCenters(self)
        self.lt_highlow_edges_edges = LookupTable444HighLowEdgesEdges(self)
        self.lt_highlow_edges = LookupTable444HighLowEdges(self)

        self.lt_reduce333 = LookupTableIDA444Reduce333(self)

    def tsai_phase2(self):
        # Pick the best edge_mapping
        # - an edge_mapping that gives us a hit in the phase2 table is ideal
        #     - pick the best among those
        # - if not pick the one that has the lowest edges_cost
        # - build the phase2 table out to 7-deep to help here
        original_state = self.state[:]
        original_solution = self.solution[:]
        phase1_solution_len = len(self.solution)
        log.info("%s: Start of find best edge_mapping" % self)

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
            count = 0

            for (edges_to_flip_count, edges_to_flip_sets) in highlow_edge_mapping_combinations.items():
                for edge_mapping in edges_to_flip_sets:
                    self.state[:] = tmp_state[:]
                    self.solution[:] = tmp_solution[:]

                    self.edge_mapping = edge_mapping
                    phase2_state = self.lt_highlow_edges.state()
                    edge_mapping_for_phase2_state[phase2_state] = edge_mapping
                    high_low_states_to_find.append(phase2_state)
                    count += 1

                    # If we evaluate all 2048 of them on a pi3 it takes about 1500ms which ends
                    # up being a huge chunk of the total solve time.  Checking the first 25% will
                    # get us a reasonably short solution.
                    if self.cpu_mode == "fast" and count >= 512:
                        break

            log.info(
                "%s: edge_mapping binary_search_multiple %d high_low_states_to_find begin"
                % (self, len(high_low_states_to_find))
            )
            high_low_states = self.lt_highlow_edges.binary_search_multiple(high_low_states_to_find)
            log.info(
                "%s: edge_mapping binary_search_multiple %d high_low_states_to_find end"
                % (self, len(high_low_states_to_find))
            )
            min_edge_mapping = None
            min_phase2_cost = None
            min_phase2_steps = None

            for (phase2_state, phase2_steps) in sorted(high_low_states.items()):
                self.state = tmp_state[:]
                self.solution = tmp_solution[:]
                phase2_steps = phase2_steps.split()
                phase2_cost = len(phase2_steps)

                if min_phase2_cost is None or phase2_cost < min_phase2_cost:
                    min_phase2_cost = phase2_cost
                    min_edge_mapping = edge_mapping_for_phase2_state[phase2_state]
                    min_phase2_steps = list(pre_steps) + phase2_steps[:]
                    log.info("%s: using edge_mapping %s, phase2 cost %s" % (self, min_edge_mapping, phase2_cost))

            if min_edge_mapping:
                if pre_steps:
                    log.info("pre-steps %s required to find a hit" % " ".join(pre_steps))
                break
        else:
            assert False, "write some code to find the best edge_mapping when there is no phase2 hit"

        log.info("%s: End of find best edge_mapping" % self)

        self.state = original_state[:]
        self.solution = original_solution[:]
        self.edge_mapping = min_edge_mapping

        # Test the prune tables
        # self.lt_highlow_edges_centers.solve()
        # self.lt_highlow_edges_edges.solve()
        # self.print_cube()
        # self.highlow_edges_print()
        # sys.exit(0)

        log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        # self.lt_highlow_edges.solve()
        for step in min_phase2_steps:
            self.rotate(step)
        self.solution.append(
            "COMMENT_%d_steps_444_phase2" % self.get_solution_len_minus_rotates(self.solution[phase1_solution_len:])
        )
        self.print_cube()
        self.highlow_edges_print()
        log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def reduce_333(self):

        # save cube state
        self.original_state = self.state[:]
        self.original_solution = self.solution[:]

        log.info("%s: Start of Phase1" % self)

        if not self.centers_staged():
            self.print_cube()
            self.lt_ULFRBD_centers_stage.solve_via_c()
            self.print_cube()

        if self.rotate_for_best_centers_staging():
            self.print_cube()

        phase1_solution_len = len(self.solution)
        self.solution.append("COMMENT_%d_steps_444_phase1" % self.get_solution_len_minus_rotates(self.solution))
        log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # This can happen on the large NNN cubes that are using 444 to pair their inside orbit of edges.
        # We need the edge swaps to be even for our edges lookup table to work.
        if self.edge_swaps_odd(False, 0, False):
            log.warning("%s: edge swaps are odd, running prevent_OLL to correct" % self)
            self.prevent_OLL()
            self.print_cube()
            self.solution.append(
                "COMMENT_%d_steps_prevent_OLL"
                % self.get_solution_len_minus_rotates(self.solution[phase1_solution_len:])
            )
            log.info("%s: End of prevent_OLL, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.tsai_phase2()

        phase2_solution_len = len(self.solution)

        # Pair all 12 edges and solve the centers in one phase
        # Testing the phase3 prune tables
        # self.lt_reduce333_edges_solve.solve()
        # self.lt_reduce333_centers_solve.solve()
        # self.print_cube()
        # log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        # sys.exit(0)

        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_reduce333.avoid_pll = True
        self.lt_reduce333.solve()

        if self.state[6] != "U" or self.state[38] != "F":
            self.rotate_U_to_U()
            self.rotate_F_to_F()

        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_444_phase3" % self.get_solution_len_minus_rotates(self.solution[phase2_solution_len:])
        )
        log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        self.solution.append("CENTERS_SOLVED")
        self.solution.append("EDGES_GROUPED")


def rotate_444(cube, step):
    return [cube[x] for x in swaps_444[step]]
