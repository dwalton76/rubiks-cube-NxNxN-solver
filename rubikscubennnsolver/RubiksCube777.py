# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDAViaC
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.misc import SolveError
from rubikscubennnsolver.RubiksCubeNNNOddEdges import RubiksCubeNNNOddEdges
from rubikscubennnsolver.swaps import swaps_777

log = logging.getLogger(__name__)


moves_777 = (
    "U",
    "U'",
    "U2",
    "Uw",
    "Uw'",
    "Uw2",
    "3Uw",
    "3Uw'",
    "3Uw2",
    "L",
    "L'",
    "L2",
    "Lw",
    "Lw'",
    "Lw2",
    "3Lw",
    "3Lw'",
    "3Lw2",
    "F",
    "F'",
    "F2",
    "Fw",
    "Fw'",
    "Fw2",
    "3Fw",
    "3Fw'",
    "3Fw2",
    "R",
    "R'",
    "R2",
    "Rw",
    "Rw'",
    "Rw2",
    "3Rw",
    "3Rw'",
    "3Rw2",
    "B",
    "B'",
    "B2",
    "Bw",
    "Bw'",
    "Bw2",
    "3Bw",
    "3Bw'",
    "3Bw2",
    "D",
    "D'",
    "D2",
    "Dw",
    "Dw'",
    "Dw2",
    "3Dw",
    "3Dw'",
    "3Dw2",
    # slices...not used for now
    # "2U", "2U'", "2U2", "2D", "2D'", "2D2",
    # "2L", "2L'", "2L2", "2R", "2R'", "2R2",
    # "2F", "2F'", "2F2", "2B", "2B'", "2B2",
    # "3U", "3U'", "3U2", "3D", "3D'", "3D2",
    # "3L", "3L'", "3L2", "3R", "3R'", "3R2",
    # "3F", "3F'", "3F2", "3B", "3B'", "3B2"
)

solved_777 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

centers_777 = (
    9,
    10,
    11,
    12,
    13,
    16,
    17,
    18,
    19,
    20,
    23,
    24,
    25,
    26,
    27,
    30,
    31,
    32,
    33,
    34,
    37,
    38,
    39,
    40,
    41,  # Upper
    58,
    59,
    60,
    61,
    62,
    65,
    66,
    67,
    68,
    69,
    72,
    73,
    74,
    75,
    76,
    79,
    80,
    81,
    82,
    83,
    86,
    87,
    88,
    89,
    90,  # Left
    107,
    108,
    109,
    110,
    111,
    114,
    115,
    116,
    117,
    118,
    121,
    122,
    123,
    124,
    125,
    128,
    129,
    130,
    131,
    132,
    135,
    136,
    137,
    138,
    139,  # Front
    156,
    157,
    158,
    159,
    160,
    163,
    164,
    165,
    166,
    167,
    170,
    171,
    172,
    173,
    174,
    177,
    178,
    179,
    180,
    181,
    184,
    185,
    186,
    187,
    188,  # Right
    205,
    206,
    207,
    208,
    209,
    212,
    213,
    214,
    215,
    216,
    219,
    220,
    221,
    222,
    223,
    226,
    227,
    228,
    229,
    230,
    233,
    234,
    235,
    236,
    237,  # Back
    254,
    255,
    256,
    257,
    258,
    261,
    262,
    263,
    264,
    265,
    268,
    269,
    270,
    271,
    272,
    275,
    276,
    277,
    278,
    279,
    282,
    283,
    284,
    285,
    286,  # Down
)

ULRD_centers_777 = (
    9,
    10,
    11,
    12,
    13,
    16,
    17,
    18,
    19,
    20,
    23,
    24,
    25,
    26,
    27,
    30,
    31,
    32,
    33,
    34,
    37,
    38,
    39,
    40,
    41,  # Upper
    58,
    59,
    60,
    61,
    62,
    65,
    66,
    67,
    68,
    69,
    72,
    73,
    74,
    75,
    76,
    79,
    80,
    81,
    82,
    83,
    86,
    87,
    88,
    89,
    90,  # Left
    156,
    157,
    158,
    159,
    160,
    163,
    164,
    165,
    166,
    167,
    170,
    171,
    172,
    173,
    174,
    177,
    178,
    179,
    180,
    181,
    184,
    185,
    186,
    187,
    188,  # Right
    254,
    255,
    256,
    257,
    258,
    261,
    262,
    263,
    264,
    265,
    268,
    269,
    270,
    271,
    272,
    275,
    276,
    277,
    278,
    279,
    282,
    283,
    284,
    285,
    286,  # Down
)


# ===============================
# phase 2 - pair LR oblique edges
# ===============================
class LookupTableIDA777LRObliqueEdgePairing(LookupTableIDAViaC):

    oblique_edges_777 = (
        10,
        11,
        12,
        16,
        20,
        23,
        27,
        30,
        34,
        38,
        39,
        40,  # Upper
        59,
        60,
        61,
        65,
        69,
        72,
        76,
        79,
        83,
        87,
        88,
        89,  # Left
        108,
        109,
        110,
        114,
        118,
        121,
        125,
        128,
        132,
        136,
        137,
        138,  # Front
        157,
        158,
        159,
        163,
        167,
        170,
        174,
        177,
        181,
        185,
        186,
        187,  # Right
        206,
        207,
        208,
        212,
        216,
        219,
        223,
        226,
        230,
        234,
        235,
        236,  # Back
        255,
        256,
        257,
        261,
        265,
        268,
        272,
        275,
        279,
        283,
        284,
        285,  # Down
    )

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (),
            "7x7x7-LR-oblique-edges-stage",  # C_ida_type
        )

    def recolor(self):
        log.info("%s: recolor (custom)" % self)
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_777:
            if x in self.oblique_edges_777:
                if self.parent.state[x] == "L" or self.parent.state[x] == "R":
                    self.parent.state[x] = "L"
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


# ===================================
# phase 5 - pair the oblique UD edges
# ===================================
class LookupTableIDA777UDObliqueEdgePairing(LookupTableIDAViaC):

    UFBD_oblique_edges_777 = (
        10,
        11,
        12,
        16,
        20,
        23,
        27,
        30,
        34,
        38,
        39,
        40,  # Upper
        108,
        109,
        110,
        114,
        118,
        121,
        125,
        128,
        132,
        136,
        137,
        138,  # Front
        206,
        207,
        208,
        212,
        216,
        219,
        223,
        226,
        230,
        234,
        235,
        236,  # Back
        255,
        256,
        257,
        261,
        265,
        268,
        272,
        275,
        279,
        283,
        284,
        285,  # Down
    )

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (),
            "7x7x7-UD-oblique-edges-stage",  # C_ida_type
        )

    def recolor(self):
        log.info("%s: recolor (custom)" % self)
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_777:
            if x in self.UFBD_oblique_edges_777:
                if self.parent.state[x] == "U" or self.parent.state[x] == "D":
                    self.parent.state[x] = "U"
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


# =====================================
# phase 7 - LR centers to vertical bars
# =====================================
class LookupTable777Step41(LookupTable):
    """
    lookup-table-7x7x7-step41.txt
    =============================
    0 steps has 8 entries (0 percent, 0.00x previous step)
    1 steps has 370 entries (0 percent, 46.25x previous step)
    2 steps has 2,000 entries (0 percent, 5.41x previous step)
    3 steps has 10,166 entries (2 percent, 5.08x previous step)
    4 steps has 43,316 entries (12 percent, 4.26x previous step)
    5 steps has 115,392 entries (33 percent, 2.66x previous step)
    6 steps has 135,856 entries (39 percent, 1.18x previous step)
    7 steps has 34,484 entries (10 percent, 0.25x previous step)
    8 steps has 1,408 entries (0 percent, 0.04x previous step)

    Total: 343,000 entries
    Average: 5.40 moves
    """

    state_targets = (
        "LLLLLLLLLLLLRRRRRRRRRRRR",
        "LLLLRLRLRLLLRRRLRLRLRRRR",
        "LLLLRLRLRLLLRRRRLRLRLRRR",
        "LLLRLRLRLLLLRRRLRLRLRRRR",
        "LLLRLRLRLLLLRRRRLRLRLRRR",
        "LLLRRRRRRLLLRRRLLLLLLRRR",
        "LLRLLLLLLLLRLRRRRRRRRLRR",
        "LLRLLLLLLLLRRRLRRRRRRRRL",
        "LLRLRLRLRLLRLRRLRLRLRLRR",
        "LLRLRLRLRLLRLRRRLRLRLLRR",
        "LLRLRLRLRLLRRRLLRLRLRRRL",
        "LLRLRLRLRLLRRRLRLRLRLRRL",
        "LLRRLRLRLLLRLRRLRLRLRLRR",
        "LLRRLRLRLLLRLRRRLRLRLLRR",
        "LLRRLRLRLLLRRRLLRLRLRRRL",
        "LLRRLRLRLLLRRRLRLRLRLRRL",
        "LLRRRRRRRLLRLRRLLLLLLLRR",
        "LLRRRRRRRLLRRRLLLLLLLRRL",
        "LRLLLLLLLLRLRLRRRRRRRRLR",
        "LRLLRLRLRLRLRLRLRLRLRRLR",
        "LRLLRLRLRLRLRLRRLRLRLRLR",
        "LRLRLRLRLLRLRLRLRLRLRRLR",
        "LRLRLRLRLLRLRLRRLRLRLRLR",
        "LRLRRRRRRLRLRLRLLLLLLRLR",
        "LRRLLLLLLLRRLLRRRRRRRLLR",
        "LRRLLLLLLLRRRLLRRRRRRRLL",
        "LRRLRLRLRLRRLLRLRLRLRLLR",
        "LRRLRLRLRLRRLLRRLRLRLLLR",
        "LRRLRLRLRLRRRLLLRLRLRRLL",
        "LRRLRLRLRLRRRLLRLRLRLRLL",
        "LRRRLRLRLLRRLLRLRLRLRLLR",
        "LRRRLRLRLLRRLLRRLRLRLLLR",
        "LRRRLRLRLLRRRLLLRLRLRRLL",
        "LRRRLRLRLLRRRLLRLRLRLRLL",
        "LRRRRRRRRLRRLLRLLLLLLLLR",
        "LRRRRRRRRLRRRLLLLLLLLRLL",
        "RLLLLLLLLRLLLRRRRRRRRLRR",
        "RLLLLLLLLRLLRRLRRRRRRRRL",
        "RLLLRLRLRRLLLRRLRLRLRLRR",
        "RLLLRLRLRRLLLRRRLRLRLLRR",
        "RLLLRLRLRRLLRRLLRLRLRRRL",
        "RLLLRLRLRRLLRRLRLRLRLRRL",
        "RLLRLRLRLRLLLRRLRLRLRLRR",
        "RLLRLRLRLRLLLRRRLRLRLLRR",
        "RLLRLRLRLRLLRRLLRLRLRRRL",
        "RLLRLRLRLRLLRRLRLRLRLRRL",
        "RLLRRRRRRRLLLRRLLLLLLLRR",
        "RLLRRRRRRRLLRRLLLLLLLRRL",
        "RLRLLLLLLRLRLRLRRRRRRLRL",
        "RLRLRLRLRRLRLRLLRLRLRLRL",
        "RLRLRLRLRRLRLRLRLRLRLLRL",
        "RLRRLRLRLRLRLRLLRLRLRLRL",
        "RLRRLRLRLRLRLRLRLRLRLLRL",
        "RLRRRRRRRRLRLRLLLLLLLLRL",
        "RRLLLLLLLRRLLLRRRRRRRLLR",
        "RRLLLLLLLRRLRLLRRRRRRRLL",
        "RRLLRLRLRRRLLLRLRLRLRLLR",
        "RRLLRLRLRRRLLLRRLRLRLLLR",
        "RRLLRLRLRRRLRLLLRLRLRRLL",
        "RRLLRLRLRRRLRLLRLRLRLRLL",
        "RRLRLRLRLRRLLLRLRLRLRLLR",
        "RRLRLRLRLRRLLLRRLRLRLLLR",
        "RRLRLRLRLRRLRLLLRLRLRRLL",
        "RRLRLRLRLRRLRLLRLRLRLRLL",
        "RRLRRRRRRRRLLLRLLLLLLLLR",
        "RRLRRRRRRRRLRLLLLLLLLRLL",
        "RRRLLLLLLRRRLLLRRRRRRLLL",
        "RRRLRLRLRRRRLLLLRLRLRLLL",
        "RRRLRLRLRRRRLLLRLRLRLLLL",
        "RRRRLRLRLRRRLLLLRLRLRLLL",
        "RRRRLRLRLRRRLLLRLRLRLLLL",
        "RRRRRRRRRRRRLLLLLLLLLLLL",
    )

    LR_oblique_edges_and_outer_t_center = (
        # 10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
        59,
        60,
        61,
        65,
        69,
        72,
        76,
        79,
        83,
        87,
        88,
        89,  # Left
        # 108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  # Front
        157,
        158,
        159,
        163,
        167,
        170,
        174,
        177,
        181,
        185,
        186,
        187,  # Right
        # 206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  # Back
        # 255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step41.txt",
            self.state_targets,
            linecount=343000,
            max_depth=8,
            filesize=20237000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "U",
                "U'",
                "U2",
                "D",
                "D'",
                "D2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_oblique_edges_and_outer_t_center])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_oblique_edges_and_outer_t_center, state):
            cube[pos] = pos_state


class LookupTable777Step42(LookupTable):
    """
    lookup-table-7x7x7-step42.txt
    =============================
    0 steps has 10 entries (0 percent, 0.00x previous step)
    1 steps has 216 entries (0 percent, 21.60x previous step)
    2 steps has 1,289 entries (0 percent, 5.97x previous step)
    3 steps has 6,178 entries (1 percent, 4.79x previous step)
    4 steps has 24,456 entries (7 percent, 3.96x previous step)
    5 steps has 73,866 entries (21 percent, 3.02x previous step)
    6 steps has 131,607 entries (38 percent, 1.78x previous step)
    7 steps has 90,214 entries (26 percent, 0.69x previous step)
    8 steps has 14,832 entries (4 percent, 0.16x previous step)
    9 steps has 332 entries (0 percent, 0.02x previous step)

    Total: 343,000 entries
    Average: 5.92 moves
    """

    state_targets = (
        "LLLLLLLLLLLLLRRRRRRRRRRRRR",
        "LLLLLLLLRLLLLRRRRLRRRRRRRR",
        "LLLLLLLLRLLLLRRRRRRRRLRRRR",
        "LLLLRLLLLLLLLRRRRLRRRRRRRR",
        "LLLLRLLLLLLLLRRRRRRRRLRRRR",
        "LLLLRLLLRLLLLRRRRLRRRLRRRR",
        "LLLRLLLRLLLRRLLRRRLRRRLRRR",
        "LLLRLLLRLLLRRRRRLRRRLRRRLL",
        "LLLRLLLRRLLRRLLRRLLRRRLRRR",
        "LLLRLLLRRLLRRLLRRRLRRLLRRR",
        "LLLRLLLRRLLRRRRRLLRRLRRRLL",
        "LLLRLLLRRLLRRRRRLRRRLLRRLL",
        "LLLRRLLRLLLRRLLRRLLRRRLRRR",
        "LLLRRLLRLLLRRLLRRRLRRLLRRR",
        "LLLRRLLRLLLRRRRRLLRRLRRRLL",
        "LLLRRLLRLLLRRRRRLRRRLLRRLL",
        "LLLRRLLRRLLRRLLRRLLRRLLRRR",
        "LLLRRLLRRLLRRRRRLLRRLLRRLL",
        "RRLLLRLLLRLLLLLRRRLRRRLRRR",
        "RRLLLRLLLRLLLRRRLRRRLRRRLL",
        "RRLLLRLLRRLLLLLRRLLRRRLRRR",
        "RRLLLRLLRRLLLLLRRRLRRLLRRR",
        "RRLLLRLLRRLLLRRRLLRRLRRRLL",
        "RRLLLRLLRRLLLRRRLRRRLLRRLL",
        "RRLLRRLLLRLLLLLRRLLRRRLRRR",
        "RRLLRRLLLRLLLLLRRRLRRLLRRR",
        "RRLLRRLLLRLLLRRRLLRRLRRRLL",
        "RRLLRRLLLRLLLRRRLRRRLLRRLL",
        "RRLLRRLLRRLLLLLRRLLRRLLRRR",
        "RRLLRRLLRRLLLRRRLLRRLLRRLL",
        "RRLRLRLRLRLRRLLRLRLRLRLRLL",
        "RRLRLRLRRRLRRLLRLLLRLRLRLL",
        "RRLRLRLRRRLRRLLRLRLRLLLRLL",
        "RRLRRRLRLRLRRLLRLLLRLRLRLL",
        "RRLRRRLRLRLRRLLRLRLRLLLRLL",
        "RRLRRRLRRRLRRLLRLLLRLLLRLL",
    )

    LR_inside_centers_and_left_oblique_edges = (
        # 10, 17, 18, 19, 20, 24, 25, 26, 30, 31, 32, 33, 40,  # Upper
        59,
        66,
        67,
        68,
        69,
        73,
        74,
        75,
        79,
        80,
        81,
        82,
        89,  # Left
        # 108, 115, 116, 117, 118, 122, 123, 124, 128, 129, 130, 131, 138,  # Front
        157,
        164,
        165,
        166,
        167,
        171,
        172,
        173,
        177,
        178,
        179,
        180,
        187,  # Right
        # 206, 213, 214, 215, 216, 220, 221, 222, 226, 227, 228, 229, 236,  # Back
        # 255, 262, 263, 264, 265, 269, 270, 271, 275, 276, 277, 278, 285,  # Down
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step42.txt",
            self.state_targets,
            linecount=343000,
            max_depth=9,
            filesize=22981000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "U",
                "U'",
                "U2",
                "D",
                "D'",
                "D2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_inside_centers_and_left_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_inside_centers_and_left_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable777Step43(LookupTable):
    """
    lookup-table-7x7x7-step43.txt
    =============================
    0 steps has 11 entries (0 percent, 0.00x previous step)
    1 steps has 239 entries (0 percent, 21.73x previous step)
    2 steps has 1,405 entries (0 percent, 5.88x previous step)
    3 steps has 6,372 entries (1 percent, 4.54x previous step)
    4 steps has 25,225 entries (7 percent, 3.96x previous step)
    5 steps has 77,525 entries (22 percent, 3.07x previous step)
    6 steps has 135,173 entries (39 percent, 1.74x previous step)
    7 steps has 85,458 entries (24 percent, 0.63x previous step)
    8 steps has 11,492 entries (3 percent, 0.13x previous step)
    9 steps has 100 entries (0 percent, 0.01x previous step)

    Total: 343,000 entries
    Average: 5.87 moves
    """

    LR_inside_centers_and_outer_t_centers = (
        # 11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39,  # Upper
        60,
        66,
        67,
        68,
        72,
        73,
        74,
        75,
        76,
        80,
        81,
        82,
        88,  # Left
        # 109, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 137,  # Front
        158,
        164,
        165,
        166,
        170,
        171,
        172,
        173,
        174,
        178,
        179,
        180,
        186,  # Right
        # 207, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 235,  # Back
        # 256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284,  # Down
    )

    state_targets = (
        "LLLLLLLLLLLLLRRRRRRRRRRRRR",
        "LLLLLLLLRLLLLRRRRLRRRRRRRR",
        "LLLLLLLLRLLLLRRRRRRRRLRRRR",
        "LLLLRLLLLLLLLRRRRLRRRRRRRR",
        "LLLLRLLLLLLLLRRRRRRRRLRRRR",
        "LLLLRLLLRLLLLRRRRLRRRLRRRR",
        "LLLRLLLRLLLRLRLRRRLRRRLRRR",
        "LLLRLLLRLLLRLRRRLRRRLRRRLR",
        "LLLRLLLRRLLRLRLRRLLRRRLRRR",
        "LLLRLLLRRLLRLRLRRRLRRLLRRR",
        "LLLRLLLRRLLRLRRRLLRRLRRRLR",
        "LLLRLLLRRLLRLRRRLRRRLLRRLR",
        "LLLRRLLRLLLRLRLRRLLRRRLRRR",
        "LLLRRLLRLLLRLRLRRRLRRLLRRR",
        "LLLRRLLRLLLRLRRRLLRRLRRRLR",
        "LLLRRLLRLLLRLRRRLRRRLLRRLR",
        "LLLRRLLRRLLRLRLRRLLRRLLRRR",
        "LLLRRLLRRLLRLRRRLLRRLLRRLR",
        "LRLLLRLLLRLLLRLRRRLRRRLRRR",
        "LRLLLRLLLRLLLRRRLRRRLRRRLR",
        "LRLLLRLLRRLLLRLRRLLRRRLRRR",
        "LRLLLRLLRRLLLRLRRRLRRLLRRR",
        "LRLLLRLLRRLLLRRRLLRRLRRRLR",
        "LRLLLRLLRRLLLRRRLRRRLLRRLR",
        "LRLLRRLLLRLLLRLRRLLRRRLRRR",
        "LRLLRRLLLRLLLRLRRRLRRLLRRR",
        "LRLLRRLLLRLLLRRRLLRRLRRRLR",
        "LRLLRRLLLRLLLRRRLRRRLLRRLR",
        "LRLLRRLLRRLLLRLRRLLRRLLRRR",
        "LRLLRRLLRRLLLRRRLLRRLLRRLR",
        "LRLRLRLRLRLRLRLRLRLRLRLRLR",
        "LRLRLRLRRRLRLRLRLLLRLRLRLR",
        "LRLRLRLRRRLRLRLRLRLRLLLRLR",
        "LRLRRRLRLRLRLRLRLLLRLRLRLR",
        "LRLRRRLRLRLRLRLRLRLRLLLRLR",
        "LRLRRRLRRRLRLRLRLLLRLLLRLR",
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step43.txt",
            self.state_targets,
            linecount=343000,
            max_depth=8,
            filesize=22981000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "U",
                "U'",
                "U2",
                "D",
                "D'",
                "D2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_inside_centers_and_outer_t_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_inside_centers_and_outer_t_centers, state):
            cube[pos] = pos_state


class LookupTable777Step44(LookupTable):
    """
    lookup-table-7x7x7-step44.txt
    =============================
    0 steps has 9 entries (0 percent, 0.00x previous step)
    1 steps has 217 entries (0 percent, 24.11x previous step)
    2 steps has 1,289 entries (0 percent, 5.94x previous step)
    3 steps has 6,178 entries (1 percent, 4.79x previous step)
    4 steps has 24,456 entries (7 percent, 3.96x previous step)
    5 steps has 73,866 entries (21 percent, 3.02x previous step)
    6 steps has 131,607 entries (38 percent, 1.78x previous step)
    7 steps has 90,214 entries (26 percent, 0.69x previous step)
    8 steps has 14,832 entries (4 percent, 0.16x previous step)
    9 steps has 332 entries (0 percent, 0.02x previous step)

    Total: 343,000 entries
    Average: 5.92 moves
    """

    state_targets = (
        "LLLLLLLLLLLLLRRRRRRRRRRRRR",
        "LLLLLLLLLLLRLRLRRRRRRRRRRR",
        "LLLLLLLLLLLRLRRRRRRRRRRRLR",
        "LLRLLRLLRLLLRLRRRLRRLRRLRR",
        "LLRLLRLLRLLLRRRLRRLRRLRRRL",
        "LLRLLRLLRLLRRLLRRLRRLRRLRR",
        "LLRLLRLLRLLRRLRRRLRRLRRLLR",
        "LLRLLRLLRLLRRRLLRRLRRLRRRL",
        "LLRLLRLLRLLRRRRLRRLRRLRRLL",
        "LRLLLLLLLLLLLRLRRRRRRRRRRR",
        "LRLLLLLLLLLLLRRRRRRRRRRRLR",
        "LRLLLLLLLLLRLRLRRRRRRRRRLR",
        "LRRLLRLLRLLLRLLRRLRRLRRLRR",
        "LRRLLRLLRLLLRLRRRLRRLRRLLR",
        "LRRLLRLLRLLLRRLLRRLRRLRRRL",
        "LRRLLRLLRLLLRRRLRRLRRLRRLL",
        "LRRLLRLLRLLRRLLRRLRRLRRLLR",
        "LRRLLRLLRLLRRRLLRRLRRLRRLL",
        "RLLLRLLRLLRLLLRRRLRRLRRLRR",
        "RLLLRLLRLLRLLRRLRRLRRLRRRL",
        "RLLLRLLRLLRRLLLRRLRRLRRLRR",
        "RLLLRLLRLLRRLLRRRLRRLRRLLR",
        "RLLLRLLRLLRRLRLLRRLRRLRRRL",
        "RLLLRLLRLLRRLRRLRRLRRLRRLL",
        "RLRLRRLRRLRLRLRLRLLRLLRLRL",
        "RLRLRRLRRLRRRLLLRLLRLLRLRL",
        "RLRLRRLRRLRRRLRLRLLRLLRLLL",
        "RRLLRLLRLLRLLLLRRLRRLRRLRR",
        "RRLLRLLRLLRLLLRRRLRRLRRLLR",
        "RRLLRLLRLLRLLRLLRRLRRLRRRL",
        "RRLLRLLRLLRLLRRLRRLRRLRRLL",
        "RRLLRLLRLLRRLLLRRLRRLRRLLR",
        "RRLLRLLRLLRRLRLLRRLRRLRRLL",
        "RRRLRRLRRLRLRLLLRLLRLLRLRL",
        "RRRLRRLRRLRLRLRLRLLRLLRLLL",
        "RRRLRRLRRLRRRLLLRLLRLLRLLL",
    )

    LR_inside_centers_and_right_oblique_edges = [
        # 12, 16, 17, 18, 19, 24, 25, 26, 31, 32, 33, 34, 38,  # Upper
        61,
        65,
        66,
        67,
        68,
        73,
        74,
        75,
        80,
        81,
        82,
        83,
        87,  # Left
        # 110, 114, 115, 116, 117, 122, 123, 124, 129, 130, 131, 132, 136,  # Front
        159,
        163,
        164,
        165,
        166,
        171,
        172,
        173,
        178,
        179,
        180,
        181,
        185,  # Right
        # 208, 212, 213, 214, 215, 220, 221, 222, 227, 228, 229, 230, 234,  # Back
        # 257, 261, 262, 263, 264, 269, 270, 271, 276, 277, 278, 279, 283,  # Down
    ]

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step44.txt",
            self.state_targets,
            linecount=343000,
            max_depth=9,
            filesize=22981000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "U",
                "U'",
                "U2",
                "D",
                "D'",
                "D2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_inside_centers_and_right_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_inside_centers_and_right_oblique_edges, state):
            cube[pos] = pos_state


class LookupTableIDA777Step40(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "U",
                "U'",
                "U2",
                "D",
                "D'",
                "D2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            prune_tables=(parent.lt_step41, parent.lt_step42, parent.lt_step43, parent.lt_step44),
        )


# =====================================
# phase 8 - UD centers to vertical bars
# =====================================
class LookupTable777Step51(LookupTable):
    """
    lookup-table-7x7x7-step51.txt
    =============================
    0 steps has 22 entries (0 percent, 0.00x previous step)
    1 steps has 288 entries (0 percent, 13.09x previous step)
    2 steps has 1,328 entries (0 percent, 4.61x previous step)
    3 steps has 6,846 entries (1 percent, 5.16x previous step)
    4 steps has 32,296 entries (9 percent, 4.72x previous step)
    5 steps has 99,008 entries (28 percent, 3.07x previous step)
    6 steps has 148,952 entries (43 percent, 1.50x previous step)
    7 steps has 51,980 entries (15 percent, 0.35x previous step)
    8 steps has 2,272 entries (0 percent, 0.04x previous step)
    9 steps has 8 entries (0 percent, 0.00x previous step)

    Total: 343,000 entries
    Average: 5.61 moves
    """

    state_targets = (
        "DDDDDDDDDDDDUUUUUUUUUUUU",
        "DDDDUDUDUDDDUUUDUDUDUUUU",
        "DDDDUDUDUDDDUUUUDUDUDUUU",
        "DDDUDUDUDDDDUUUDUDUDUUUU",
        "DDDUDUDUDDDDUUUUDUDUDUUU",
        "DDDUUUUUUDDDUUUDDDDDDUUU",
        "DDUDDDDDDDDUDUUUUUUUUDUU",
        "DDUDDDDDDDDUUUDUUUUUUUUD",
        "DDUDUDUDUDDUDUUDUDUDUDUU",
        "DDUDUDUDUDDUDUUUDUDUDDUU",
        "DDUDUDUDUDDUUUDDUDUDUUUD",
        "DDUDUDUDUDDUUUDUDUDUDUUD",
        "DDUUDUDUDDDUDUUDUDUDUDUU",
        "DDUUDUDUDDDUDUUUDUDUDDUU",
        "DDUUDUDUDDDUUUDDUDUDUUUD",
        "DDUUDUDUDDDUUUDUDUDUDUUD",
        "DDUUUUUUUDDUDUUDDDDDDDUU",
        "DDUUUUUUUDDUUUDDDDDDDUUD",
        "DUDDDDDDDDUDUDUUUUUUUUDU",
        "DUDDUDUDUDUDUDUDUDUDUUDU",
        "DUDDUDUDUDUDUDUUDUDUDUDU",
        "DUDUDUDUDDUDUDUDUDUDUUDU",
        "DUDUDUDUDDUDUDUUDUDUDUDU",
        "DUDUUUUUUDUDUDUDDDDDDUDU",
        "DUUDDDDDDDUUDDUUUUUUUDDU",
        "DUUDDDDDDDUUUDDUUUUUUUDD",
        "DUUDUDUDUDUUDDUDUDUDUDDU",
        "DUUDUDUDUDUUDDUUDUDUDDDU",
        "DUUDUDUDUDUUUDDDUDUDUUDD",
        "DUUDUDUDUDUUUDDUDUDUDUDD",
        "DUUUDUDUDDUUDDUDUDUDUDDU",
        "DUUUDUDUDDUUDDUUDUDUDDDU",
        "DUUUDUDUDDUUUDDDUDUDUUDD",
        "DUUUDUDUDDUUUDDUDUDUDUDD",
        "DUUUUUUUUDUUDDUDDDDDDDDU",
        "DUUUUUUUUDUUUDDDDDDDDUDD",
        "UDDDDDDDDUDDDUUUUUUUUDUU",
        "UDDDDDDDDUDDUUDUUUUUUUUD",
        "UDDDUDUDUUDDDUUDUDUDUDUU",
        "UDDDUDUDUUDDDUUUDUDUDDUU",
        "UDDDUDUDUUDDUUDDUDUDUUUD",
        "UDDDUDUDUUDDUUDUDUDUDUUD",
        "UDDUDUDUDUDDDUUDUDUDUDUU",
        "UDDUDUDUDUDDDUUUDUDUDDUU",
        "UDDUDUDUDUDDUUDDUDUDUUUD",
        "UDDUDUDUDUDDUUDUDUDUDUUD",
        "UDDUUUUUUUDDDUUDDDDDDDUU",
        "UDDUUUUUUUDDUUDDDDDDDUUD",
        "UDUDDDDDDUDUDUDUUUUUUDUD",
        "UDUDUDUDUUDUDUDDUDUDUDUD",
        "UDUDUDUDUUDUDUDUDUDUDDUD",
        "UDUUDUDUDUDUDUDDUDUDUDUD",
        "UDUUDUDUDUDUDUDUDUDUDDUD",
        "UDUUUUUUUUDUDUDDDDDDDDUD",
        "UUDDDDDDDUUDDDUUUUUUUDDU",
        "UUDDDDDDDUUDUDDUUUUUUUDD",
        "UUDDUDUDUUUDDDUDUDUDUDDU",
        "UUDDUDUDUUUDDDUUDUDUDDDU",
        "UUDDUDUDUUUDUDDDUDUDUUDD",
        "UUDDUDUDUUUDUDDUDUDUDUDD",
        "UUDUDUDUDUUDDDUDUDUDUDDU",
        "UUDUDUDUDUUDDDUUDUDUDDDU",
        "UUDUDUDUDUUDUDDDUDUDUUDD",
        "UUDUDUDUDUUDUDDUDUDUDUDD",
        "UUDUUUUUUUUDDDUDDDDDDDDU",
        "UUDUUUUUUUUDUDDDDDDDDUDD",
        "UUUDDDDDDUUUDDDUUUUUUDDD",
        "UUUDUDUDUUUUDDDDUDUDUDDD",
        "UUUDUDUDUUUUDDDUDUDUDDDD",
        "UUUUDUDUDUUUDDDDUDUDUDDD",
        "UUUUDUDUDUUUDDDUDUDUDDDD",
        "UUUUUUUUUUUUDDDDDDDDDDDD",
    )

    UD_oblique_edges_and_outer_t_center = (
        10,
        11,
        12,
        16,
        20,
        23,
        27,
        30,
        34,
        38,
        39,
        40,  # Upper
        # 59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89,  # Left
        # 108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  # Front
        # 157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187,  # Right
        # 206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  # Back
        255,
        256,
        257,
        261,
        265,
        268,
        272,
        275,
        279,
        283,
        284,
        285,  # Down
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step51.txt",
            self.state_targets,
            linecount=343000,
            max_depth=9,
            filesize=21266000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Uw2",
                "3Dw2",
                "Uw2",
                "Dw2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_oblique_edges_and_outer_t_center])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_oblique_edges_and_outer_t_center, state):
            cube[pos] = pos_state


class LookupTable777Step52(LookupTable):
    """
    lookup-table-7x7x7-step52.txt
    =============================
    0 steps has 21 entries (0 percent, 0.00x previous step)
    1 steps has 170 entries (0 percent, 8.10x previous step)
    2 steps has 876 entries (0 percent, 5.15x previous step)
    3 steps has 4,080 entries (1 percent, 4.66x previous step)
    4 steps has 16,546 entries (4 percent, 4.06x previous step)
    5 steps has 54,737 entries (15 percent, 3.31x previous step)
    6 steps has 121,824 entries (35 percent, 2.23x previous step)
    7 steps has 115,046 entries (33 percent, 0.94x previous step)
    8 steps has 28,763 entries (8 percent, 0.25x previous step)
    9 steps has 927 entries (0 percent, 0.03x previous step)
    10 steps has 10 entries (0 percent, 0.01x previous step)

    Total: 343,000 entries
    Average: 6.21 moves
    """

    state_targets = (
        "DDUDDDUDDDUDDUUDUUUDUUUDUU",
        "DDUDDDUDUDUDDUUDUDUDUUUDUU",
        "DDUDDDUDUDUDDUUDUUUDUDUDUU",
        "DDUDUDUDDDUDDUUDUDUDUUUDUU",
        "DDUDUDUDDDUDDUUDUUUDUDUDUU",
        "DDUDUDUDUDUDDUUDUDUDUDUDUU",
        "DDUUDDUUDDUUUDDDUUDDUUDDUU",
        "DDUUDDUUDDUUUUUDDUUDDUUDDD",
        "DDUUDDUUUDUUUDDDUDDDUUDDUU",
        "DDUUDDUUUDUUUDDDUUDDUDDDUU",
        "DDUUDDUUUDUUUUUDDDUDDUUDDD",
        "DDUUDDUUUDUUUUUDDUUDDDUDDD",
        "DDUUUDUUDDUUUDDDUDDDUUDDUU",
        "DDUUUDUUDDUUUDDDUUDDUDDDUU",
        "DDUUUDUUDDUUUUUDDDUDDUUDDD",
        "DDUUUDUUDDUUUUUDDUUDDDUDDD",
        "DDUUUDUUUDUUUDDDUDDDUDDDUU",
        "DDUUUDUUUDUUUUUDDDUDDDUDDD",
        "UUUDDUUDDUUDDDDDUUDDUUDDUU",
        "UUUDDUUDDUUDDUUDDUUDDUUDDD",
        "UUUDDUUDUUUDDDDDUDDDUUDDUU",
        "UUUDDUUDUUUDDDDDUUDDUDDDUU",
        "UUUDDUUDUUUDDUUDDDUDDUUDDD",
        "UUUDDUUDUUUDDUUDDUUDDDUDDD",
        "UUUDUUUDDUUDDDDDUDDDUUDDUU",
        "UUUDUUUDDUUDDDDDUUDDUDDDUU",
        "UUUDUUUDDUUDDUUDDDUDDUUDDD",
        "UUUDUUUDDUUDDUUDDUUDDDUDDD",
        "UUUDUUUDUUUDDDDDUDDDUDDDUU",
        "UUUDUUUDUUUDDUUDDDUDDDUDDD",
        "UUUUDUUUDUUUUDDDDUDDDUDDDD",
        "UUUUDUUUUUUUUDDDDDDDDUDDDD",
        "UUUUDUUUUUUUUDDDDUDDDDDDDD",
        "UUUUUUUUDUUUUDDDDDDDDUDDDD",
        "UUUUUUUUDUUUUDDDDUDDDDDDDD",
        "UUUUUUUUUUUUUDDDDDDDDDDDDD",
    )

    UD_inside_centers_and_left_oblique_edges = (
        10,
        17,
        18,
        19,
        20,
        24,
        25,
        26,
        30,
        31,
        32,
        33,
        40,  # Upper
        # 59, 66, 67, 68, 69, 73, 74, 75, 79, 80, 81, 82, 89,  # Left
        # 108, 115, 116, 117, 118, 122, 123, 124, 128, 129, 130, 131, 138,  # Front
        # 157, 164, 165, 166, 167, 171, 172, 173, 177, 178, 179, 180, 187,  # Right
        # 206, 213, 214, 215, 216, 220, 221, 222, 226, 227, 228, 229, 236,  # Back
        255,
        262,
        263,
        264,
        265,
        269,
        270,
        271,
        275,
        276,
        277,
        278,
        285,  # Down
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step52.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=23667000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Uw2",
                "3Dw2",
                "Uw2",
                "Dw2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_inside_centers_and_left_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_inside_centers_and_left_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable777Step53(LookupTable):
    """
    lookup-table-7x7x7-step53.txt
    =============================
    0 steps has 21 entries (0 percent, 0.00x previous step)
    1 steps has 194 entries (0 percent, 9.24x previous step)
    2 steps has 960 entries (0 percent, 4.95x previous step)
    3 steps has 4,061 entries (1 percent, 4.23x previous step)
    4 steps has 16,207 entries (4 percent, 3.99x previous step)
    5 steps has 54,813 entries (15 percent, 3.38x previous step)
    6 steps has 122,554 entries (35 percent, 2.24x previous step)
    7 steps has 116,234 entries (33 percent, 0.95x previous step)
    8 steps has 27,300 entries (7 percent, 0.23x previous step)
    9 steps has 654 entries (0 percent, 0.02x previous step)
    10 steps has 2 entries (0 percent, 0.00x previous step)

    Total: 343,000 entries
    Average: 6.20 moves
    """

    state_targets = (
        "UDUDDDUDDDUDUDUDUUUDUUUDUD",
        "UDUDDDUDUDUDUDUDUDUDUUUDUD",
        "UDUDDDUDUDUDUDUDUUUDUDUDUD",
        "UDUDUDUDDDUDUDUDUDUDUUUDUD",
        "UDUDUDUDDDUDUDUDUUUDUDUDUD",
        "UDUDUDUDUDUDUDUDUDUDUDUDUD",
        "UDUUDDUUDDUUUDDDUUDDUUDDUD",
        "UDUUDDUUDDUUUDUDDUUDDUUDDD",
        "UDUUDDUUUDUUUDDDUDDDUUDDUD",
        "UDUUDDUUUDUUUDDDUUDDUDDDUD",
        "UDUUDDUUUDUUUDUDDDUDDUUDDD",
        "UDUUDDUUUDUUUDUDDUUDDDUDDD",
        "UDUUUDUUDDUUUDDDUDDDUUDDUD",
        "UDUUUDUUDDUUUDDDUUDDUDDDUD",
        "UDUUUDUUDDUUUDUDDDUDDUUDDD",
        "UDUUUDUUDDUUUDUDDUUDDDUDDD",
        "UDUUUDUUUDUUUDDDUDDDUDDDUD",
        "UDUUUDUUUDUUUDUDDDUDDDUDDD",
        "UUUDDUUDDUUDUDDDUUDDUUDDUD",
        "UUUDDUUDDUUDUDUDDUUDDUUDDD",
        "UUUDDUUDUUUDUDDDUDDDUUDDUD",
        "UUUDDUUDUUUDUDDDUUDDUDDDUD",
        "UUUDDUUDUUUDUDUDDDUDDUUDDD",
        "UUUDDUUDUUUDUDUDDUUDDDUDDD",
        "UUUDUUUDDUUDUDDDUDDDUUDDUD",
        "UUUDUUUDDUUDUDDDUUDDUDDDUD",
        "UUUDUUUDDUUDUDUDDDUDDUUDDD",
        "UUUDUUUDDUUDUDUDDUUDDDUDDD",
        "UUUDUUUDUUUDUDDDUDDDUDDDUD",
        "UUUDUUUDUUUDUDUDDDUDDDUDDD",
        "UUUUDUUUDUUUUDDDDUDDDUDDDD",
        "UUUUDUUUUUUUUDDDDDDDDUDDDD",
        "UUUUDUUUUUUUUDDDDUDDDDDDDD",
        "UUUUUUUUDUUUUDDDDDDDDUDDDD",
        "UUUUUUUUDUUUUDDDDUDDDDDDDD",
        "UUUUUUUUUUUUUDDDDDDDDDDDDD",
    )

    UD_inside_centers_and_outer_t_centers = (
        11,
        17,
        18,
        19,
        23,
        24,
        25,
        26,
        27,
        31,
        32,
        33,
        39,  # Upper
        # 60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88,  # Left
        # 109, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 137,  # Front
        # 158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186,  # Right
        # 207, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 235,  # Back
        256,
        262,
        263,
        264,
        268,
        269,
        270,
        271,
        272,
        276,
        277,
        278,
        284,  # Down
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step53.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=23667000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Uw2",
                "3Dw2",
                "Uw2",
                "Dw2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_inside_centers_and_outer_t_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_inside_centers_and_outer_t_centers, state):
            cube[pos] = pos_state


class LookupTable777Step54(LookupTable):
    """
    lookup-table-7x7x7-step54.txt
    =============================
    0 steps has 20 entries (0 percent, 0.00x previous step)
    1 steps has 171 entries (0 percent, 8.55x previous step)
    2 steps has 876 entries (0 percent, 5.12x previous step)
    3 steps has 4,080 entries (1 percent, 4.66x previous step)
    4 steps has 16,546 entries (4 percent, 4.06x previous step)
    5 steps has 54,737 entries (15 percent, 3.31x previous step)
    6 steps has 121,824 entries (35 percent, 2.23x previous step)
    7 steps has 115,046 entries (33 percent, 0.94x previous step)
    8 steps has 28,763 entries (8 percent, 0.25x previous step)
    9 steps has 927 entries (0 percent, 0.03x previous step)
    10 steps has 10 entries (0 percent, 0.01x previous step)

    Total: 343,000 entries
    Average: 6.21 moves
    """

    state_targets = (
        "DDDUDDUDDUDDDUUUDUUDUUDUUU",
        "DDDUDDUDDUDUDUDUDUUDUUDUUU",
        "DDDUDDUDDUDUDUUUDUUDUUDUDU",
        "DDUUDUUDUUDDUDUUDDUDDUDDUU",
        "DDUUDUUDUUDDUUUDDUDDUDDUUD",
        "DDUUDUUDUUDUUDDUDDUDDUDDUU",
        "DDUUDUUDUUDUUDUUDDUDDUDDDU",
        "DDUUDUUDUUDUUUDDDUDDUDDUUD",
        "DDUUDUUDUUDUUUUDDUDDUDDUDD",
        "DUDUDDUDDUDDDUDUDUUDUUDUUU",
        "DUDUDDUDDUDDDUUUDUUDUUDUDU",
        "DUDUDDUDDUDUDUDUDUUDUUDUDU",
        "DUUUDUUDUUDDUDDUDDUDDUDDUU",
        "DUUUDUUDUUDDUDUUDDUDDUDDDU",
        "DUUUDUUDUUDDUUDDDUDDUDDUUD",
        "DUUUDUUDUUDDUUUDDUDDUDDUDD",
        "DUUUDUUDUUDUUDDUDDUDDUDDDU",
        "DUUUDUUDUUDUUUDDDUDDUDDUDD",
        "UDDUUDUUDUUDDDUUDDUDDUDDUU",
        "UDDUUDUUDUUDDUUDDUDDUDDUUD",
        "UDDUUDUUDUUUDDDUDDUDDUDDUU",
        "UDDUUDUUDUUUDDUUDDUDDUDDDU",
        "UDDUUDUUDUUUDUDDDUDDUDDUUD",
        "UDDUUDUUDUUUDUUDDUDDUDDUDD",
        "UDUUUUUUUUUDUDUDDDDDDDDDUD",
        "UDUUUUUUUUUUUDDDDDDDDDDDUD",
        "UDUUUUUUUUUUUDUDDDDDDDDDDD",
        "UUDUUDUUDUUDDDDUDDUDDUDDUU",
        "UUDUUDUUDUUDDDUUDDUDDUDDDU",
        "UUDUUDUUDUUDDUDDDUDDUDDUUD",
        "UUDUUDUUDUUDDUUDDUDDUDDUDD",
        "UUDUUDUUDUUUDDDUDDUDDUDDDU",
        "UUDUUDUUDUUUDUDDDUDDUDDUDD",
        "UUUUUUUUUUUDUDDDDDDDDDDDUD",
        "UUUUUUUUUUUDUDUDDDDDDDDDDD",
        "UUUUUUUUUUUUUDDDDDDDDDDDDD",
    )

    UD_inside_centers_and_right_oblique_edges = [
        12,
        16,
        17,
        18,
        19,
        24,
        25,
        26,
        31,
        32,
        33,
        34,
        38,  # Upper
        # 61, 65, 66, 67, 68, 73, 74, 75, 80, 81, 82, 83, 87,  # Left
        # 110, 114, 115, 116, 117, 122, 123, 124, 129, 130, 131, 132, 136,  # Front
        # 159, 163, 164, 165, 166, 171, 172, 173, 178, 179, 180, 181, 185,  # Right
        # 208, 212, 213, 214, 215, 220, 221, 222, 227, 228, 229, 230, 234,  # Back
        257,
        261,
        262,
        263,
        264,
        269,
        270,
        271,
        276,
        277,
        278,
        279,
        283,  # Down
    ]

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step54.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=24010000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Uw2",
                "3Dw2",
                "Uw2",
                "Dw2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_inside_centers_and_right_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_inside_centers_and_right_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable777Step55(LookupTable):
    """
    lookup-table-7x7x7-step55.txt
    =============================
    0 steps has 2 entries (2 percent, 0.00x previous step)
    1 steps has 8 entries (11 percent, 4.00x previous step)
    2 steps has 20 entries (27 percent, 2.50x previous step)
    3 steps has 24 entries (33 percent, 1.20x previous step)
    4 steps has 18 entries (25 percent, 0.75x previous step)

    Total: 72 entries
    Average: 2.67 moves
    """

    LR_centers_minus_outside_x_centers_777 = (
        59,
        60,
        61,
        65,
        66,
        67,
        68,
        69,
        72,
        73,
        74,
        75,
        76,
        79,
        80,
        81,
        82,
        83,
        87,
        88,
        89,  # Left
        157,
        158,
        159,
        163,
        164,
        165,
        166,
        167,
        170,
        171,
        172,
        173,
        174,
        177,
        178,
        179,
        180,
        181,
        185,
        186,
        187,  # Right
    )

    state_targets = ("LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR", "RRRRLLLRRLLLRRLLLRRRRLLLLRRRLLRRRLLRRRLLLL")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step55.txt",
            self.state_targets,
            linecount=72,
            max_depth=4,
            filesize=4392,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Uw2",
                "3Dw2",
                "Uw2",
                "Dw2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTableIDA777Step50(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Uw2",
                "3Dw2",
                "Uw2",
                "Dw2",
                "F",
                "F'",
                "F2",
                "D",
                "D'",
                "D2",
            ),
            prune_tables=(parent.lt_step51, parent.lt_step52, parent.lt_step53, parent.lt_step54, parent.lt_step55),
        )


# =============================
# phase 9 - centers daisy solve
# =============================
class LookupTable777Step61(LookupTable):
    """
    lookup-table-7x7x7-step61.txt
    =============================
    0 steps has 2 entries (2 percent, 0.00x previous step)
    1 steps has 8 entries (11 percent, 4.00x previous step)
    2 steps has 20 entries (27 percent, 2.50x previous step)
    3 steps has 24 entries (33 percent, 1.20x previous step)
    4 steps has 18 entries (25 percent, 0.75x previous step)

    Total: 72 entries
    Average: 2.67 moves
    """

    UD_centers_minus_outside_x_centers_777 = (
        10,
        11,
        12,
        16,
        17,
        18,
        19,
        20,
        23,
        24,
        25,
        26,
        27,
        30,
        31,
        32,
        33,
        34,
        38,
        39,
        40,  # Upper
        255,
        256,
        257,
        261,
        262,
        263,
        264,
        265,
        268,
        269,
        270,
        271,
        272,
        275,
        276,
        277,
        278,
        279,
        283,
        284,
        285,  # Down
    )

    state_targets = ("UUUUUUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDDDDDD", "DDDDUUUDDUUUDDUUUDDDDUUUUDDDUUDDDUUDDDUUUU")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step61.txt",
            self.state_targets,
            linecount=72,
            max_depth=4,
            filesize=4392,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTable777Step62(LookupTable):
    """
    lookup-table-7x7x7-step62.txt
    =============================
    0 steps has 2 entries (2 percent, 0.00x previous step)
    1 steps has 8 entries (11 percent, 4.00x previous step)
    2 steps has 20 entries (27 percent, 2.50x previous step)
    3 steps has 24 entries (33 percent, 1.20x previous step)
    4 steps has 18 entries (25 percent, 0.75x previous step)

    Total: 72 entries
    Average: 2.67 moves
    """

    LR_centers_minus_outside_x_centers_777 = (
        59,
        60,
        61,
        65,
        66,
        67,
        68,
        69,
        72,
        73,
        74,
        75,
        76,
        79,
        80,
        81,
        82,
        83,
        87,
        88,
        89,  # Left
        157,
        158,
        159,
        163,
        164,
        165,
        166,
        167,
        170,
        171,
        172,
        173,
        174,
        177,
        178,
        179,
        180,
        181,
        185,
        186,
        187,  # Right
    )

    state_targets = ("LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR", "RRRRLLLRRLLLRRLLLRRRRLLLLRRRLLRRRLLRRRLLLL")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step62.txt",
            self.state_targets,
            linecount=72,
            max_depth=4,
            filesize=4392,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTable777Step65(LookupTable):
    """
    lookup-table-7x7x7-step65.txt
    =============================
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 16 entries (0 percent, 8.00x previous step)
    2 steps has 106 entries (0 percent, 6.62x previous step)
    3 steps has 538 entries (0 percent, 5.08x previous step)
    4 steps has 2,308 entries (0 percent, 4.29x previous step)
    5 steps has 9,244 entries (2 percent, 4.01x previous step)
    6 steps has 31,742 entries (9 percent, 3.43x previous step)
    7 steps has 84,464 entries (24 percent, 2.66x previous step)
    8 steps has 128,270 entries (37 percent, 1.52x previous step)
    9 steps has 75,830 entries (22 percent, 0.59x previous step)
    10 steps has 10,480 entries (3 percent, 0.14x previous step)

    Total: 343,000 entries
    Average: 7.73 moves
    """

    FB_inside_centers_and_outer_t_centers = (
        # 11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39,  # Upper
        # 60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88,  # Left
        109,
        115,
        116,
        117,
        121,
        122,
        123,
        124,
        125,
        129,
        130,
        131,
        137,  # Front
        # 158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186,  # Right
        207,
        213,
        214,
        215,
        219,
        220,
        221,
        222,
        223,
        227,
        228,
        229,
        235,  # Back
        # 256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284,  # Down
    )

    state_targets = ("FFFFFFFFFFFFFBBBBBBBBBBBBB", "BFFFBFFFBFFFBFBBBFBBBFBBBF")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step65.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=25039000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.FB_inside_centers_and_outer_t_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.FB_inside_centers_and_outer_t_centers, state):
            cube[pos] = pos_state


class LookupTable777Step66(LookupTable):
    """
    lookup-table-7x7x7-step66.txt
    =============================
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 16 entries (0 percent, 8.00x previous step)
    2 steps has 82 entries (0 percent, 5.12x previous step)
    3 steps has 450 entries (0 percent, 5.49x previous step)
    4 steps has 2,406 entries (0 percent, 5.35x previous step)
    5 steps has 11,960 entries (3 percent, 4.97x previous step)
    6 steps has 43,430 entries (12 percent, 3.63x previous step)
    7 steps has 108,510 entries (31 percent, 2.50x previous step)
    8 steps has 133,124 entries (38 percent, 1.23x previous step)
    9 steps has 40,908 entries (11 percent, 0.31x previous step)
    10 steps has 2,112 entries (0 percent, 0.05x previous step)

    Total: 343,000 entries
    Average: 7.42 moves
    """

    FB_oblique_edges_and_outer_t_center = (
        # 10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
        # 59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89,  # Left
        108,
        109,
        110,
        114,
        118,
        121,
        125,
        128,
        132,
        136,
        137,
        138,  # Front
        # 157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187,  # Right
        206,
        207,
        208,
        212,
        216,
        219,
        223,
        226,
        230,
        234,
        235,
        236,  # Back
        # 255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
    )

    state_targets = ("BBBBBBBBBBBBFFFFFFFFFFFF", "FFFFFFFFFFFFBBBBBBBBBBBB")

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step66.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=23667000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.FB_oblique_edges_and_outer_t_center])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.FB_oblique_edges_and_outer_t_center, state):
            cube[pos] = pos_state


class LookupTableIDA777Step60(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            prune_tables=(parent.lt_step61, parent.lt_step62, parent.lt_step65, parent.lt_step66),
        )


# =================================================
# phase solve t-centers (for cubes larger than 777)
# =================================================
class LookupTable777Step71(LookupTable):
    """
    lookup-table-7x7x7-step71.txt
    =============================
    0 steps has 1 entries (2 percent, 0.00x previous step)
    1 steps has 4 entries (11 percent, 4.00x previous step)
    2 steps has 10 entries (27 percent, 2.50x previous step)
    3 steps has 12 entries (33 percent, 1.20x previous step)
    4 steps has 9 entries (25 percent, 0.75x previous step)

    Total: 36 entries
    Average: 2.67 moves
    """

    UD_centers_minus_outside_x_centers_777 = (
        10,
        11,
        12,
        16,
        17,
        18,
        19,
        20,
        23,
        24,
        25,
        26,
        27,
        30,
        31,
        32,
        33,
        34,
        38,
        39,
        40,  # Upper
        255,
        256,
        257,
        261,
        262,
        263,
        264,
        265,
        268,
        269,
        270,
        271,
        272,
        275,
        276,
        277,
        278,
        279,
        283,
        284,
        285,  # Down
    )

    state_targets = ("UUUUUUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDDDDDD",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step71.txt",
            self.state_targets,
            linecount=36,
            max_depth=4,
            filesize=2196,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTable777Step72(LookupTable):
    """
    lookup-table-7x7x7-step72.txt
    =============================
    0 steps has 1 entries (2 percent, 0.00x previous step)
    1 steps has 4 entries (11 percent, 4.00x previous step)
    2 steps has 10 entries (27 percent, 2.50x previous step)
    3 steps has 12 entries (33 percent, 1.20x previous step)
    4 steps has 9 entries (25 percent, 0.75x previous step)

    Total: 36 entries
    Average: 2.67 moves
    """

    LR_centers_minus_outside_x_centers_777 = (
        59,
        60,
        61,
        65,
        66,
        67,
        68,
        69,
        72,
        73,
        74,
        75,
        76,
        79,
        80,
        81,
        82,
        83,
        87,
        88,
        89,  # Left
        157,
        158,
        159,
        163,
        164,
        165,
        166,
        167,
        170,
        171,
        172,
        173,
        174,
        177,
        178,
        179,
        180,
        181,
        185,
        186,
        187,  # Right
    )

    state_targets = ("LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step72.txt",
            self.state_targets,
            linecount=36,
            max_depth=4,
            filesize=2196,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTable777Step75(LookupTable):
    """
    lookup-table-7x7x7-step75.txt
    =============================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 8 entries (0 percent, 8.00x previous step)
    2 steps has 56 entries (0 percent, 7.00x previous step)
    3 steps has 300 entries (0 percent, 5.36x previous step)
    4 steps has 1,317 entries (0 percent, 4.39x previous step)
    5 steps has 5,382 entries (1 percent, 4.09x previous step)
    6 steps has 19,083 entries (5 percent, 3.55x previous step)
    7 steps has 55,022 entries (16 percent, 2.88x previous step)
    8 steps has 104,894 entries (30 percent, 1.91x previous step)
    9 steps has 106,324 entries (30 percent, 1.01x previous step)
    10 steps has 44,533 entries (12 percent, 0.42x previous step)
    11 steps has 5,880 entries (1 percent, 0.13x previous step)
    12 steps has 200 entries (0 percent, 0.03x previous step)

    Total: 343,000 entries
    Average: 8.28 moves
    """

    FB_inside_centers_and_outer_t_centers = (
        # 11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39,  # Upper
        # 60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88,  # Left
        109,
        115,
        116,
        117,
        121,
        122,
        123,
        124,
        125,
        129,
        130,
        131,
        137,  # Front
        # 158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186,  # Right
        207,
        213,
        214,
        215,
        219,
        220,
        221,
        222,
        223,
        227,
        228,
        229,
        235,  # Back
        # 256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284,  # Down
    )

    state_targets = ("FFFFFFFFFFFFFBBBBBBBBBBBBB",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step75.txt",
            self.state_targets,
            linecount=343000,
            max_depth=12,
            filesize=27097000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.FB_inside_centers_and_outer_t_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.FB_inside_centers_and_outer_t_centers, state):
            cube[pos] = pos_state


class LookupTable777Step76(LookupTable):
    """
    lookup-table-7x7x7-step76.txt
    =============================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 8 entries (0 percent, 8.00x previous step)
    2 steps has 48 entries (0 percent, 6.00x previous step)
    3 steps has 276 entries (0 percent, 5.75x previous step)
    4 steps has 1,572 entries (0 percent, 5.70x previous step)
    5 steps has 8,134 entries (2 percent, 5.17x previous step)
    6 steps has 33,187 entries (9 percent, 4.08x previous step)
    7 steps has 94,826 entries (27 percent, 2.86x previous step)
    8 steps has 141,440 entries (41 percent, 1.49x previous step)
    9 steps has 59,620 entries (17 percent, 0.42x previous step)
    10 steps has 3,808 entries (1 percent, 0.06x previous step)
    11 steps has 80 entries (0 percent, 0.02x previous step)

    Total: 343,000 entries
    Average: 7.63 moves
    """

    FB_oblique_edges_and_outer_t_center = (
        # 10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
        # 59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89,  # Left
        108,
        109,
        110,
        114,
        118,
        121,
        125,
        128,
        132,
        136,
        137,
        138,  # Front
        # 157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187,  # Right
        206,
        207,
        208,
        212,
        216,
        219,
        223,
        226,
        230,
        234,
        235,
        236,  # Back
        # 255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
    )

    state_targets = ("FFFFFFFFFFFFBBBBBBBBBBBB",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step76.txt",
            self.state_targets,
            linecount=343000,
            max_depth=11,
            filesize=24353000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.FB_oblique_edges_and_outer_t_center])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.FB_oblique_edges_and_outer_t_center, state):
            cube[pos] = pos_state


class LookupTableIDA777Step70(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "Uw",
                "Uw'",
                "3Lw",
                "3Lw'",
                "Lw",
                "Lw'",
                "3Fw",
                "3Fw'",
                "Fw",
                "Fw'",
                "3Rw",
                "3Rw'",
                "Rw",
                "Rw'",
                "3Bw",
                "3Bw'",
                "Bw",
                "Bw'",
                "3Dw",
                "3Dw'",
                "Dw",
                "Dw'",
                "L",
                "L'",
                "R",
                "R'",
                "3Fw2",
                "3Bw2",
                "Fw2",
                "Bw2",
                "U",
                "U'",
                "D",
                "D'",
            ),
            prune_tables=(parent.lt_step71, parent.lt_step72, parent.lt_step75, parent.lt_step76),
            multiplier=1.2,
        )


class RubiksCube777(RubiksCubeNNNOddEdges):
    """
    For 7x7x7 centers
    - stage the UD inside 9 centers via 5x5x5
    - UD oblique edges
        - pair the two outside oblique edges via 6x6x6
        - build a lookup table to pair the middle oblique edges with the two
          outside oblique edges. The restriction being that if you do a 3Lw move
          you must also do a 3Rw' in order to keep the two outside oblique edges
          paired up...so it is a slice of the layer in the middle. This table
          should be (24!/(8!*16!))^2 or 540,917,591,800 so use IDA.
    - stage the rest of the UD centers via 5x5x5
    - stage the LR inside 9 centers via 5x5x5
    - LR oblique edges...use the same strategy as UD oblique edges
    - stage the rest of the LR centers via 5x5x5

    - solve the UD centers...this is (8!/(4!*4!))^6 or 117 billion so use IDA
    - solve the LR centers
    - solve the LR and FB centers

    For 7x7x7 edges
    - pair the middle 3 wings for each side via 5x5x5
    - pair the outer 2 wings with the paired middle 3 wings via 5x5x5


    Inheritance model
    -----------------
            RubiksCube
                |
        RubiksCubeNNNOddEdges
           /            \
    RubiksCubeNNNOdd RubiksCube777

    """

    instantiated = False

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCubeNNNOddEdges.__init__(self, state, order, colormap, debug)

        if RubiksCube777.instantiated:
            # raise Exception("Another 7x7x7 instance is being created")
            log.warning("Another 7x7x7 instance is being created")
        else:
            RubiksCube777.instantiated = True

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
            6,
            14,
            42,
            48,
            44,
            36,
            8,
            51,
            55,
            63,
            91,
            97,
            93,
            85,
            57,
            100,
            104,
            112,
            140,
            146,
            142,
            134,
            106,
            149,
            153,
            161,
            189,
            195,
            191,
            183,
            155,
            198,
            202,
            210,
            238,
            244,
            240,
            232,
            204,
            247,
            251,
            259,
            287,
            293,
            289,
            281,
            253,
        )

        edge_orbit_1 = (
            3,
            5,
            21,
            35,
            47,
            45,
            29,
            15,
            52,
            54,
            70,
            84,
            96,
            94,
            78,
            64,
            101,
            103,
            119,
            133,
            145,
            143,
            127,
            113,
            150,
            152,
            168,
            182,
            194,
            192,
            176,
            162,
            199,
            201,
            217,
            231,
            243,
            241,
            225,
            211,
            248,
            250,
            266,
            280,
            292,
            290,
            274,
            260,
        )

        edge_orbit_2 = (
            4,
            28,
            46,
            22,
            53,
            77,
            95,
            71,
            102,
            126,
            144,
            120,
            151,
            175,
            193,
            169,
            200,
            224,
            242,
            218,
            249,
            273,
            291,
            267,
        )

        corners = (
            1,
            7,
            43,
            49,
            50,
            56,
            92,
            98,
            99,
            105,
            141,
            147,
            148,
            154,
            190,
            196,
            197,
            203,
            239,
            245,
            246,
            252,
            288,
            294,
        )

        left_oblique_edge = (
            10,
            20,
            40,
            30,
            59,
            69,
            89,
            79,
            108,
            118,
            138,
            128,
            157,
            167,
            187,
            177,
            206,
            216,
            236,
            226,
            255,
            265,
            285,
            275,
        )

        right_oblique_edge = (
            12,
            34,
            38,
            16,
            61,
            83,
            87,
            65,
            110,
            132,
            136,
            114,
            159,
            181,
            185,
            163,
            208,
            230,
            234,
            212,
            257,
            279,
            283,
            261,
        )

        outside_x_centers = (
            9,
            13,
            37,
            41,
            58,
            62,
            86,
            90,
            107,
            111,
            135,
            139,
            156,
            160,
            184,
            188,
            205,
            209,
            233,
            237,
            254,
            258,
            282,
            286,
        )

        inside_x_centers = (
            17,
            19,
            31,
            33,
            66,
            68,
            80,
            82,
            115,
            117,
            129,
            131,
            164,
            166,
            178,
            180,
            213,
            215,
            227,
            229,
            262,
            264,
            276,
            278,
        )

        outside_t_centers = (
            11,
            23,
            27,
            39,
            60,
            72,
            76,
            88,
            109,
            121,
            125,
            137,
            158,
            170,
            174,
            186,
            207,
            219,
            223,
            235,
            256,
            268,
            272,
            284,
        )

        inside_t_centers = (
            18,
            24,
            26,
            32,
            67,
            73,
            75,
            81,
            116,
            122,
            124,
            130,
            165,
            171,
            173,
            179,
            214,
            220,
            222,
            228,
            263,
            269,
            271,
            277,
        )

        centers = (25, 74, 123, 172, 221, 270)

        self._sanity_check("edge-orbit-0", edge_orbit_0, 8)
        self._sanity_check("edge-orbit-1", edge_orbit_1, 8)
        self._sanity_check("edge-orbit-2", edge_orbit_2, 4)
        self._sanity_check("corners", corners, 4)
        self._sanity_check("left-oblique", left_oblique_edge, 4)
        self._sanity_check("right-oblique", right_oblique_edge, 4)
        self._sanity_check("outside x-centers", outside_x_centers, 4)
        self._sanity_check("inside x-centers", inside_x_centers, 4)
        self._sanity_check("outside t-centers", outside_t_centers, 4)
        self._sanity_check("inside t-centers", inside_t_centers, 4)
        self._sanity_check("centers", centers, 1)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # phase 2 - pair LR oblique edges
        self.lt_LR_oblique_edge_pairing = LookupTableIDA777LRObliqueEdgePairing(self)

        # phase 5 - pair the oblique UD edges
        self.lt_UD_oblique_edge_pairing = LookupTableIDA777UDObliqueEdgePairing(self)

        # phase 7 - LR centers to vertical bars
        self.lt_step41 = LookupTable777Step41(self)
        self.lt_step42 = LookupTable777Step42(self)
        self.lt_step43 = LookupTable777Step43(self)
        self.lt_step44 = LookupTable777Step44(self)
        self.lt_step40 = LookupTableIDA777Step40(self)

        # phase 8 - UD centers to vertical bars
        self.lt_step51 = LookupTable777Step51(self)
        self.lt_step52 = LookupTable777Step52(self)
        self.lt_step53 = LookupTable777Step53(self)
        self.lt_step54 = LookupTable777Step54(self)
        self.lt_step55 = LookupTable777Step55(self)
        self.lt_step50 = LookupTableIDA777Step50(self)

        # phase 9 - centers daisy solve
        self.lt_step61 = LookupTable777Step61(self)
        self.lt_step62 = LookupTable777Step62(self)
        self.lt_step65 = LookupTable777Step65(self)
        self.lt_step66 = LookupTable777Step66(self)
        self.lt_step60 = LookupTableIDA777Step60(self)

        # phase solve t-centers (for cubes larger than 777)
        self.lt_step71 = LookupTable777Step71(self)
        self.lt_step72 = LookupTable777Step72(self)
        self.lt_step75 = LookupTable777Step75(self)
        self.lt_step76 = LookupTable777Step76(self)
        self.lt_step70 = LookupTableIDA777Step70(self)

    def create_fake_555_from_inside_centers(self):

        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_777 = side_index * 49

            # centers
            fake_555.state[7 + offset_555] = self.state[17 + offset_777]
            fake_555.state[8 + offset_555] = self.state[18 + offset_777]
            fake_555.state[9 + offset_555] = self.state[19 + offset_777]
            fake_555.state[12 + offset_555] = self.state[24 + offset_777]
            fake_555.state[13 + offset_555] = self.state[25 + offset_777]
            fake_555.state[14 + offset_555] = self.state[26 + offset_777]
            fake_555.state[17 + offset_555] = self.state[31 + offset_777]
            fake_555.state[18 + offset_555] = self.state[32 + offset_777]
            fake_555.state[19 + offset_555] = self.state[33 + offset_777]

            # edges
            fake_555.state[2 + offset_555] = self.state[3 + offset_777]
            fake_555.state[3 + offset_555] = self.state[4 + offset_777]
            fake_555.state[4 + offset_555] = self.state[5 + offset_777]

            fake_555.state[6 + offset_555] = self.state[15 + offset_777]
            fake_555.state[11 + offset_555] = self.state[22 + offset_777]
            fake_555.state[16 + offset_555] = self.state[29 + offset_777]

            fake_555.state[10 + offset_555] = self.state[21 + offset_777]
            fake_555.state[15 + offset_555] = self.state[28 + offset_777]
            fake_555.state[20 + offset_555] = self.state[35 + offset_777]

            fake_555.state[22 + offset_555] = self.state[45 + offset_777]
            fake_555.state[23 + offset_555] = self.state[46 + offset_777]
            fake_555.state[24 + offset_555] = self.state[47 + offset_777]

    def create_fake_555_from_outside_centers(self):

        # Create a fake 5x5x5 to solve 7x7x7 centers (they have been reduced to a 5x5x5)
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_777 = side_index * 49

            # centers
            fake_555.state[7 + offset_555] = self.state[9 + offset_777]
            fake_555.state[8 + offset_555] = self.state[11 + offset_777]
            fake_555.state[9 + offset_555] = self.state[13 + offset_777]
            fake_555.state[12 + offset_555] = self.state[23 + offset_777]
            fake_555.state[13 + offset_555] = self.state[25 + offset_777]
            fake_555.state[14 + offset_555] = self.state[27 + offset_777]
            fake_555.state[17 + offset_555] = self.state[37 + offset_777]
            fake_555.state[18 + offset_555] = self.state[39 + offset_777]
            fake_555.state[19 + offset_555] = self.state[41 + offset_777]

            # edges
            fake_555.state[2 + offset_555] = self.state[2 + offset_777]
            fake_555.state[3 + offset_555] = self.state[4 + offset_777]
            fake_555.state[4 + offset_555] = self.state[6 + offset_777]

            fake_555.state[6 + offset_555] = self.state[8 + offset_777]
            fake_555.state[11 + offset_555] = self.state[22 + offset_777]
            fake_555.state[16 + offset_555] = self.state[36 + offset_777]

            fake_555.state[10 + offset_555] = self.state[14 + offset_777]
            fake_555.state[15 + offset_555] = self.state[28 + offset_777]
            fake_555.state[20 + offset_555] = self.state[42 + offset_777]

            fake_555.state[22 + offset_555] = self.state[44 + offset_777]
            fake_555.state[23 + offset_555] = self.state[46 + offset_777]
            fake_555.state[24 + offset_555] = self.state[48 + offset_777]

    def UD_inside_centers_staged(self):
        state = self.state

        for x in (17, 18, 19, 24, 25, 26, 31, 32, 33, 262, 263, 264, 269, 270, 271, 276, 277, 278):
            if state[x] not in ("U", "D"):
                return False
        return True

    def group_inside_UD_centers(self):
        self.create_fake_555_from_inside_centers()
        self.fake_555.group_centers_stage_FB()

        for step in self.fake_555.solution:

            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    step = "4" + step[1:]
                elif "w" in step:
                    step = "3" + step

                self.rotate(step)

    def LR_inside_centers_staged(self):
        state = self.state

        for x in (66, 67, 68, 73, 74, 75, 80, 81, 82, 164, 165, 166, 171, 172, 173, 178, 179, 180):
            if state[x] not in ("L", "R"):
                return False
        return True

    def group_inside_LR_centers(self):

        if self.LR_inside_centers_staged():
            return

        self.create_fake_555_from_inside_centers()
        self.fake_555.group_centers_stage_LR()

        for step in self.fake_555.solution:

            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                elif "w" in step:
                    step = "3" + step

                self.rotate(step)

    def stage_UD_centers(self):
        # phase 4 - use 5x5x5 solver to stage the UD inner centers
        self.group_inside_UD_centers()
        self.print_cube()
        log.info(
            "%s: UD inner x-centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # phase 5 - pair the oblique UD edges
        tmp_solution_len = len(self.solution)
        self.lt_UD_oblique_edge_pairing.solve()
        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_777_UD_oblique_edges_staged"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: UD oblique edges paired/staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # phase 6 - use 5x5x5 to stage the UD centers
        self.create_fake_555_from_outside_centers()
        self.fake_555.group_centers_stage_FB()

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

    def stage_LR_centers(self):
        # phase 1 - use 5x5x5 solver to stage the LR inner centers
        self.group_inside_LR_centers()
        self.print_cube()
        log.info(
            "%s: LR inner centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Test the pruning tables
        # self.lt_LR_left_right_oblique_edge_pairing.solve()
        # self.lt_LR_left_middle_oblique_edge_pairing.solve()
        # self.print_cube()
        # log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # phase 2 - pair LR oblique edges
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        tmp_solution_len = len(self.solution)
        self.lt_LR_oblique_edge_pairing.solve()
        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_777_LR_oblique_edges_staged"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: LR oblique edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )

        # phase 3 - use 5x5x5 solver to stage the LR centers
        self.create_fake_555_from_outside_centers()
        self.fake_555.group_centers_stage_LR()

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

        self.print_cube()
        log.info("%s: LR centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

    def LR_centers_vertical_bars(self):

        # Test the pruning tables
        # self.lt_step41.solve()
        # self.lt_step42.solve()
        # self.print_cube()
        # log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # phase 7 - LR centers to vertical bars
        tmp_solution_len = len(self.solution)
        self.lt_step40.solve_via_c()
        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        self.solution.append(
            "COMMENT_%d_steps_777_LR_centers_vertical_bars"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: LR centers vertical bars, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )

    def UD_centers_vertical_bars(self):

        # Test the pruning tables
        # self.lt_step51.solve()
        # self.lt_step52.solve()
        # self.print_cube()
        # log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # phase 8 - UD centers to vertical bars
        tmp_solution_len = len(self.solution)
        self.lt_step50.solve_via_c()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        self.solution.append(
            "COMMENT_%d_steps_777_UD_centers_vertical_bars"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: LR solved, UD centers vertical bars, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

    def centers_daisy_solve(self):
        # phase 9 - centers daisy solve
        tmp_solution_len = len(self.solution)
        self.lt_step60.solve_via_c()
        self.solution.append(
            "COMMENT_%d_steps_777_centers_daisy_solved"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: centers daisy solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_guts(self):
        self.lt_init()

        if not self.LR_centers_staged():
            self.stage_LR_centers()

        if not self.UD_centers_staged():
            self.stage_UD_centers()

        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        self.LR_centers_vertical_bars()
        self.UD_centers_vertical_bars()
        self.centers_daisy_solve()

    def solve_t_centers(self):
        # This is only used when solving a cube larger than 777
        assert self.LR_centers_staged()
        assert self.UD_centers_staged()
        self.LR_centers_vertical_bars()
        self.UD_centers_vertical_bars()

        # phase solve t-centers (for cubes larger than 777)
        tmp_solution_len = len(self.solution)
        self.lt_step70.solve_via_c()
        self.solution.append(
            "COMMENT_%d_steps_777_centers_solved"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def solve_centers(self):
        # This is only used when solving a cube larger than 777
        tmp_solution_len = len(self.solution)
        self.create_fake_555_from_outside_centers()
        self.fake_555.lt_ULFRBD_centers_solve.solve_via_c()

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

        self.solution.append(
            "COMMENT_%d_steps_777_centers_solved"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        if not self.centers_solved():
            raise SolveError("centers should be solved")


def rotate_777(cube, step):
    return [cube[x] for x in swaps_777[step]]
