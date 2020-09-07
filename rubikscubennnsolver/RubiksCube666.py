# standard libraries
import logging
import sys

# rubiks cube libraries
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDAViaC
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges
from rubikscubennnsolver.swaps import swaps_666

log = logging.getLogger(__name__)


moves_666 = (
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
solved_666 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"


inner_x_centers_666 = (
    15,
    16,
    21,
    22,
    51,
    52,
    57,
    58,
    87,
    88,
    93,
    94,
    123,
    124,
    129,
    130,
    159,
    160,
    165,
    166,
    195,
    196,
    201,
    202,
)

centers_666 = (
    8,
    9,
    10,
    11,
    14,
    15,
    16,
    17,
    20,
    21,
    22,
    23,
    26,
    27,
    28,
    29,  # Upper
    44,
    45,
    46,
    47,
    50,
    51,
    52,
    53,
    56,
    57,
    58,
    59,
    62,
    63,
    64,
    65,  # Left
    80,
    81,
    82,
    83,
    86,
    87,
    88,
    89,
    92,
    93,
    94,
    95,
    98,
    99,
    100,
    101,  # Front
    116,
    117,
    118,
    119,
    122,
    123,
    124,
    125,
    128,
    129,
    130,
    131,
    134,
    135,
    136,
    137,  # Right
    152,
    153,
    154,
    155,
    158,
    159,
    160,
    161,
    164,
    165,
    166,
    167,
    170,
    171,
    172,
    173,  # Back
    188,
    189,
    190,
    191,
    194,
    195,
    196,
    197,
    200,
    201,
    202,
    203,
    206,
    207,
    208,
    209,  # Down
)

UD_centers_666 = (
    8,
    9,
    10,
    11,
    14,
    15,
    16,
    17,
    20,
    21,
    22,
    23,
    26,
    27,
    28,
    29,
    188,
    189,
    190,
    191,
    194,
    195,
    196,
    197,
    200,
    201,
    202,
    203,
    206,
    207,
    208,
    209,
)

FB_centers_666 = (
    80,
    81,
    82,
    83,
    86,
    87,
    88,
    89,
    92,
    93,
    94,
    95,
    98,
    99,
    100,
    101,
    152,
    153,
    154,
    155,
    158,
    159,
    160,
    161,
    164,
    165,
    166,
    167,
    170,
    171,
    172,
    173,
)

UFBD_centers_666 = (
    8,
    9,
    10,
    11,
    14,
    15,
    16,
    17,
    20,
    21,
    22,
    23,
    26,
    27,
    28,
    29,
    80,
    81,
    82,
    83,
    86,
    87,
    88,
    89,
    92,
    93,
    94,
    95,
    98,
    99,
    100,
    101,
    152,
    153,
    154,
    155,
    158,
    159,
    160,
    161,
    164,
    165,
    166,
    167,
    170,
    171,
    172,
    173,
    188,
    189,
    190,
    191,
    194,
    195,
    196,
    197,
    200,
    201,
    202,
    203,
    206,
    207,
    208,
    209,
)

UDFB_left_oblique_edges = (
    9,
    17,
    28,
    20,  # Upper
    189,
    197,
    208,
    200,  # Down
    81,
    89,
    100,
    92,  # Front
    153,
    161,
    172,
    164,  # Back
)

UDFB_right_oblique_edges = (
    10,
    23,
    27,
    14,  # Upper
    190,
    203,
    207,
    194,  # Down
    82,
    95,
    99,
    86,  # Front
    154,
    167,
    171,
    158,  # Back
)

UDFB_outer_x_centers = (
    8,
    11,
    26,
    29,  # Upper
    188,
    191,
    206,
    209,  # Down
    80,
    83,
    98,
    101,  # Front
    152,
    155,
    170,
    173,  # Back
)

UDFB_inner_x_centers = (
    15,
    16,
    21,
    22,  # Upper
    195,
    196,
    201,
    202,  # Down
    87,
    88,
    93,
    94,  # Front
    159,
    160,
    165,
    166,  # Back
)

UFBD_outer_x_centers = (
    8,
    11,
    26,
    29,  # Upper
    80,
    83,
    98,
    101,  # Front
    152,
    155,
    170,
    173,  # Back
    188,
    191,
    206,
    209,  # Down
)

UFBD_inner_x_centers = (
    15,
    16,
    21,
    22,  # Upper
    87,
    88,
    93,
    94,  # Front
    159,
    160,
    165,
    166,  # Back
    195,
    196,
    201,
    202,  # Down
)

LR_left_oblique_edges = (45, 53, 64, 56, 117, 125, 136, 128)
LR_right_oblique_edges = (46, 59, 63, 50, 118, 131, 135, 122)
LR_outer_x_centers = (44, 47, 62, 65, 116, 119, 134, 137)
LR_inner_x_centers = (51, 52, 57, 58, 123, 124, 129, 130)


outer_x_centers_666 = set(
    (8, 11, 26, 29, 44, 47, 62, 65, 80, 83, 98, 101, 116, 119, 134, 137, 152, 155, 170, 173, 188, 191, 206, 209)
)

outer_x_center_inner_x_centers_666 = (
    # outer x-centers
    8,
    11,
    26,
    29,
    44,
    47,
    62,
    65,
    80,
    83,
    98,
    101,
    116,
    119,
    134,
    137,
    152,
    155,
    170,
    173,
    188,
    191,
    206,
    209,
    # inner x-centers
    15,
    16,
    21,
    22,
    51,
    52,
    57,
    58,
    87,
    88,
    93,
    94,
    123,
    124,
    129,
    130,
    159,
    160,
    165,
    166,
    195,
    196,
    201,
    202,
)

UFBD_inner_x_centers_left_oblique_edges_666 = (
    # inner x-centers
    15,
    16,
    21,
    22,
    87,
    88,
    93,
    94,
    159,
    160,
    165,
    166,
    195,
    196,
    201,
    202,
    # left oblique edges
    9,
    17,
    20,
    28,
    81,
    89,
    92,
    100,
    153,
    161,
    164,
    172,
    189,
    197,
    200,
    208,
)

UFBD_inner_x_centers_right_oblique_edges_666 = (
    # inner x-centers
    15,
    16,
    21,
    22,
    87,
    88,
    93,
    94,
    159,
    160,
    165,
    166,
    195,
    196,
    201,
    202,
    # right oblique edges
    10,
    14,
    23,
    27,
    82,
    86,
    95,
    99,
    154,
    158,
    167,
    171,
    190,
    194,
    203,
    207,
)

UFBD_oblique_edges_666 = (
    9,
    10,
    14,
    17,
    20,
    23,
    27,
    28,
    81,
    82,
    86,
    89,
    92,
    95,
    99,
    100,
    153,
    154,
    158,
    161,
    164,
    167,
    171,
    172,
    189,
    190,
    194,
    197,
    200,
    203,
    207,
    208,
)

UFBD_left_oblique_edges_666 = (9, 17, 20, 28, 81, 89, 92, 100, 153, 161, 164, 172, 189, 197, 200, 208)

UFBD_right_oblique_edges_666 = (10, 14, 23, 27, 82, 86, 95, 99, 154, 158, 167, 171, 190, 194, 203, 207)

left_oblique_edges_666 = (
    9,
    17,
    20,
    28,
    45,
    53,
    56,
    64,
    81,
    89,
    92,
    100,
    117,
    125,
    128,
    136,
    153,
    161,
    164,
    172,
    189,
    197,
    200,
    208,
)

right_oblique_edges_666 = (
    10,
    14,
    23,
    27,
    46,
    50,
    59,
    63,
    82,
    86,
    95,
    99,
    118,
    122,
    131,
    135,
    154,
    158,
    167,
    171,
    190,
    194,
    203,
    207,
)

LFRB_left_oblique_edges_666 = (45, 53, 56, 64, 81, 89, 92, 100, 117, 125, 128, 136, 153, 161, 164, 172)

LFRB_right_oblique_edges_666 = (46, 50, 59, 63, 82, 86, 95, 99, 118, 122, 131, 135, 154, 158, 167, 171)

edge_orbit_0 = (
    2,
    5,
    12,
    30,
    35,
    32,
    25,
    7,
    38,
    41,
    48,
    66,
    71,
    68,
    61,
    43,
    74,
    77,
    84,
    102,
    107,
    104,
    97,
    79,
    110,
    113,
    120,
    138,
    143,
    140,
    133,
    115,
    146,
    149,
    156,
    174,
    179,
    176,
    169,
    151,
    182,
    185,
    192,
    210,
    215,
    212,
    205,
    187,
)

edge_orbit_1 = (
    3,
    4,
    18,
    24,
    34,
    33,
    19,
    13,
    39,
    40,
    54,
    60,
    70,
    69,
    55,
    49,
    75,
    76,
    90,
    96,
    106,
    105,
    91,
    85,
    111,
    112,
    126,
    132,
    142,
    141,
    127,
    121,
    147,
    148,
    162,
    168,
    178,
    177,
    163,
    157,
    183,
    184,
    198,
    204,
    214,
    213,
    199,
    193,
)

edges_partner_666 = {
    2: 149,
    3: 148,
    4: 147,
    5: 146,
    7: 38,
    12: 113,
    13: 39,
    18: 112,
    19: 40,
    24: 111,
    25: 41,
    30: 110,
    32: 74,
    33: 75,
    34: 76,
    35: 77,
    38: 7,
    39: 13,
    40: 19,
    41: 25,
    43: 156,
    48: 79,
    49: 162,
    54: 85,
    55: 168,
    60: 91,
    61: 174,
    66: 97,
    68: 205,
    69: 199,
    70: 193,
    71: 187,
    74: 32,
    75: 33,
    76: 34,
    77: 35,
    79: 48,
    84: 115,
    85: 54,
    90: 121,
    91: 60,
    96: 127,
    97: 66,
    102: 133,
    104: 182,
    105: 183,
    106: 184,
    107: 185,
    110: 30,
    111: 24,
    112: 18,
    113: 12,
    115: 84,
    120: 151,
    121: 90,
    126: 157,
    127: 96,
    132: 163,
    133: 102,
    138: 169,
    140: 192,
    141: 198,
    142: 204,
    143: 210,
    146: 5,
    147: 4,
    148: 3,
    149: 2,
    151: 120,
    156: 43,
    157: 126,
    162: 49,
    163: 132,
    168: 55,
    169: 138,
    174: 61,
    176: 215,
    177: 214,
    178: 213,
    179: 212,
    182: 104,
    183: 105,
    184: 106,
    185: 107,
    187: 71,
    192: 140,
    193: 70,
    198: 141,
    199: 69,
    204: 142,
    205: 68,
    210: 143,
    212: 179,
    213: 178,
    214: 177,
    215: 176,
}


# phase 2
class LookupTable666LRObliquEdgeStage(LookupTableIDAViaC):
    """
    All we care about is getting the LR oblique edges paired, we do
    not need them to be placed on sides LR at this point.
    """

    oblique_edges_666 = (
        9,
        10,
        14,
        17,
        20,
        23,
        27,
        28,
        45,
        46,
        50,
        53,
        56,
        59,
        63,
        64,
        81,
        82,
        86,
        89,
        92,
        95,
        99,
        100,
        117,
        118,
        122,
        125,
        128,
        131,
        135,
        136,
        153,
        154,
        158,
        161,
        164,
        167,
        171,
        172,
        189,
        190,
        194,
        197,
        200,
        203,
        207,
        208,
    )

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (),
            "6x6x6-LR-oblique-edges-stage",  # C_ida_type
        )

    def recolor(self):
        log.info("%s: recolor (custom)" % self)
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in self.oblique_edges_666:
                if self.parent.state[x] == "L" or self.parent.state[x] == "R":
                    self.parent.state[x] = "L"
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


# phase 4
class LookupTable666UDLeftObliqueStage(LookupTable):
    """
    lookup-table-6x6x6-step11-UD-left-oblique-stage.txt
    ===================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
    3 steps has 238 entries (1 percent, 8.21x previous step)
    4 steps has 742 entries (5 percent, 3.12x previous step)
    5 steps has 1,836 entries (14 percent, 2.47x previous step)
    6 steps has 4,405 entries (34 percent, 2.40x previous step)
    7 steps has 3,774 entries (29 percent, 0.86x previous step)
    8 steps has 1,721 entries (13 percent, 0.46x previous step)
    9 steps has 122 entries (0 percent, 0.07x previous step)

    Total: 12,870 entries
    Average: 6.27 moves
    """

    state_targets = ("UUUUxxxxxxxxUUUU",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step11-UD-left-oblique-stage.txt",
            self.state_targets,
            linecount=12870,
            max_depth=9,
            filesize=656370,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "3Lw",
                "3Lw'",
                "3Fw",
                "3Fw'",
                "3Rw",
                "3Rw'",
                "3Bw",
                "3Bw'",
                "3Dw",
                "3Dw'",
                "Uw",
                "Uw'",
                "Dw",
                "Dw'",
                "Fw",
                "Fw'",
                "Bw",
                "Bw'",
                # we are not manipulating anything on sides L or R
                "L",
                "L'",
                "L2",
                "R",
                "R'",
                "R2",
                # restricting these has minimal impact on move count
                # but having few moves to explore means a faster IDA
                "U2",
                "D2",
                "F2",
                "B2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join(["U" if parent_state[x] in ("U", "D") else "x" for x in UFBD_left_oblique_edges_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_left_oblique_edges_666, state):
            cube[pos] = pos_state


class LookupTable666UDRightObliqueStage(LookupTable):
    """
    lookup-table-6x6x6-step12-UD-right-oblique-stage.txt
    ====================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
    3 steps has 238 entries (1 percent, 8.21x previous step)
    4 steps has 742 entries (5 percent, 3.12x previous step)
    5 steps has 1,836 entries (14 percent, 2.47x previous step)
    6 steps has 4,405 entries (34 percent, 2.40x previous step)
    7 steps has 3,774 entries (29 percent, 0.86x previous step)
    8 steps has 1,721 entries (13 percent, 0.46x previous step)
    9 steps has 122 entries (0 percent, 0.07x previous step)

    Total: 12,870 entries
    Average: 6.27 moves
    """

    state_targets = ("UUUUxxxxxxxxUUUU",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step12-UD-right-oblique-stage.txt",
            self.state_targets,
            linecount=12870,
            max_depth=9,
            filesize=656370,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "3Lw",
                "3Lw'",
                "3Fw",
                "3Fw'",
                "3Rw",
                "3Rw'",
                "3Bw",
                "3Bw'",
                "3Dw",
                "3Dw'",
                "Uw",
                "Uw'",
                "Dw",
                "Dw'",
                "Fw",
                "Fw'",
                "Bw",
                "Bw'",
                # we are not manipulating anything on sides L or R
                "L",
                "L'",
                "L2",
                "R",
                "R'",
                "R2",
                # restricting these has minimal impact on move count
                # but having few moves to explore means a faster IDA
                "U2",
                "D2",
                "F2",
                "B2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join(["U" if parent_state[x] in ("U", "D") else "x" for x in UFBD_right_oblique_edges_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_right_oblique_edges_666, state):
            cube[pos] = pos_state


class LookupTable666UDOuterXCenterStage(LookupTable):
    """
    lookup-table-6x6x6-step13-UD-outer-x-centers-stage.txt
    ======================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
    3 steps has 234 entries (1 percent, 8.07x previous step)
    4 steps has 1,246 entries (9 percent, 5.32x previous step)
    5 steps has 4,466 entries (34 percent, 3.58x previous step)
    6 steps has 6,236 entries (48 percent, 1.40x previous step)
    7 steps has 656 entries (5 percent, 0.11x previous step)

    Total: 12,870 entries
    Average: 5.45 moves
    """

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step13-UD-outer-x-centers-stage.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=7,
            filesize=553410,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "3Lw",
                "3Lw'",
                "3Fw",
                "3Fw'",
                "3Rw",
                "3Rw'",
                "3Bw",
                "3Bw'",
                "3Dw",
                "3Dw'",
                "Uw",
                "Uw'",
                "Dw",
                "Dw'",
                "Fw",
                "Fw'",
                "Bw",
                "Bw'",
                # we are not manipulating anything on sides L or R
                "L",
                "L'",
                "L2",
                "R",
                "R'",
                "R2",
                # restricting these has minimal impact on move count
                # but having few moves to explore means a faster IDA
                "U2",
                "D2",
                "F2",
                "B2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join(["U" if parent_state[x] in ("U", "D") else "x" for x in UFBD_outer_x_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_outer_x_centers, state):
            cube[pos] = pos_state


'''
class LookupTableIDA666UDObliqueEdgesStage(LookupTableIDAViaGraph):
    """
    This was only used to build the lookup-table-6x6x6-step14-UD-oblique-stage.pt_state
    file which was then converted to lookup-table-6x6x6-step14-UD-oblique-stage.pt-state-perfect-hash

    lookup-table-6x6x6-step14-UD-oblique-stage.txt
    ==============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
    3 steps has 286 entries (0 percent, 9.86x previous step)
    4 steps has 2,020 entries (0 percent, 7.06x previous step)
    5 steps has 15,992 entries (0 percent, 7.92x previous step)
    6 steps has 123,071 entries (0 percent, 7.70x previous step)
    7 steps has 805,821 entries (0 percent, 6.55x previous step)
    8 steps has 4,379,750 entries (2 percent, 5.44x previous step)
    9 steps has 18,300,990 entries (11 percent, 4.18x previous step)
    10 steps has 46,881,308 entries (28 percent, 2.56x previous step)
    11 steps has 62,357,957 entries (37 percent, 1.33x previous step)
    12 steps has 29,875,621 entries (18 percent, 0.48x previous step)
    13 steps has 2,852,222 entries (1 percent, 0.10x previous step)
    14 steps has 41,682 entries (0 percent, 0.01x previous step)
    15 steps has 148 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 10.61 moves
    """

    state_targets = (
        "UUUUUUUUxxxxxxxxxxxxxxxxUUUUUUUU",
    )

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            filename="lookup-table-6x6x6-step14-UD-oblique-stage.txt",
            state_target=self.state_targets,
            linecount=165636900,
            filesize=15238594800,
            max_depth=15,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw", "3Uw'",
                "3Lw", "3Lw'",
                "3Fw", "3Fw'",
                "3Rw", "3Rw'",
                "3Bw", "3Bw'",
                "3Dw", "3Dw'",

                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",

                # we are not manipulating anything on sides L or R
                "L", "L'", "L2",
                "R", "R'", "R2",

                # restricting these has minimal impact on move count
                # but having few moves to explore means a faster IDA
                "U2", "D2", "F2", "B2",
            ),
            prune_tables=(
                parent.lt_UD_left_oblique_edges_stage,
                parent.lt_UD_right_oblique_edges_stage,
            ),
        )
'''


class LookupTableIDA666UDCentersStage(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw",
                "3Uw'",
                "3Lw",
                "3Lw'",
                "3Fw",
                "3Fw'",
                "3Rw",
                "3Rw'",
                "3Bw",
                "3Bw'",
                "3Dw",
                "3Dw'",
                "Uw",
                "Uw'",
                "Dw",
                "Dw'",
                "Fw",
                "Fw'",
                "Bw",
                "Bw'",
                # we are not manipulating anything on sides L or R
                "L",
                "L'",
                "L2",
                "R",
                "R'",
                "R2",
                # restricting these has minimal impact on move count
                # but having few moves to explore means a faster IDA
                "U2",
                "D2",
                "F2",
                "B2",
            ),
            prune_tables=(
                parent.lt_UD_left_oblique_edges_stage,
                parent.lt_UD_right_oblique_edges_stage,
                parent.lt_UD_outer_x_centers_stage,
            ),
            perfect_hash01_filename="lookup-table-6x6x6-step14-UD-oblique-stage.pt-state-perfect-hash",
            pt1_state_max=12870,
        )


# phase 5
class LookupTable666UDInnerXCenterAndObliqueEdges(LookupTable):
    """
    This will solve the UD inner x-centers and pair the UD oblique edges.

    lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    1 steps has 350 entries (0 percent, 0.00x previous step)
    2 steps has 1,358 entries (0 percent, 3.88x previous step)
    3 steps has 5,148 entries (1 percent, 3.79x previous step)
    4 steps has 21,684 entries (6 percent, 4.21x previous step)
    5 steps has 75,104 entries (21 percent, 3.46x previous step)
    6 steps has 134,420 entries (39 percent, 1.79x previous step)
    7 steps has 91,784 entries (26 percent, 0.68x previous step)
    8 steps has 13,152 entries (3 percent, 0.14x previous step)

    Total: 343,000 entries
    Average: 5.93 moves

    We could chop all but the first step on this table but this is one that
    we do not load into memory and it is only 15M so we will keep all of the
    steps.
    """

    UD_inner_x_centers_and_oblique_edges = (
        9,
        10,
        14,
        15,
        16,
        17,
        20,
        21,
        22,
        23,
        27,
        28,  # Upper
        189,
        190,
        194,
        195,
        196,
        197,
        200,
        201,
        202,
        203,
        207,
        208,  # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt",
            (
                "198e67",
                "19b267",
                "19bc47",
                "19be23",
                "19be64",
                "1dc267",
                "1dcc47",
                "1dce23",
                "1dce64",
                "1df047",
                "1df223",
                "1df264",
                "1dfc03",
                "1dfc44",
                "1dfe20",
                "3b8267",
                "3b8c47",
                "3b8e23",
                "3b8e64",
                "3bb047",
                "3bb223",
                "3bb264",
                "3bbc03",
                "3bbc44",
                "3bbe20",
                "3fc047",
                "3fc223",
                "3fc264",
                "3fcc03",
                "3fcc44",
                "3fce20",
                "3ff003",
                "3ff044",
                "3ff220",
                "3ffc00",
                "d98267",
                "d98c47",
                "d98e23",
                "d98e64",
                "d9b047",
                "d9b223",
                "d9b264",
                "d9bc03",
                "d9bc44",
                "d9be20",
                "ddc047",
                "ddc223",
                "ddc264",
                "ddcc03",
                "ddcc44",
                "ddce20",
                "ddf003",
                "ddf044",
                "ddf220",
                "ddfc00",
                "fb8047",
                "fb8223",
                "fb8264",
                "fb8c03",
                "fb8c44",
                "fb8e20",
                "fbb003",
                "fbb044",
                "fbb220",
                "fbbc00",
                "ffc003",
                "ffc044",
                "ffc220",
                "ffcc00",
                "fff000",
            ),
            linecount=343000,
            max_depth=8,
            filesize=15092000,
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        lt_state = 0

        for x in self.UD_inner_x_centers_and_oblique_edges:
            if parent_state[x] == "U":
                lt_state = lt_state | 0x1
            lt_state = lt_state << 1

        lt_state = lt_state >> 1
        lt_state = self.hex_format % lt_state
        return (lt_state, 0)


# phase 6
class LookupTable666LRInnerXCenterAndObliqueEdges(LookupTable):
    """
    lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    0 steps has 4 entries (0 percent, 0.00x previous step)
    1 steps has 28 entries (0 percent, 7.00x previous step)
    2 steps has 332 entries (0 percent, 11.86x previous step)
    3 steps has 2,276 entries (0 percent, 6.86x previous step)
    4 steps has 10,040 entries (0 percent, 4.41x previous step)
    5 steps has 49,532 entries (0 percent, 4.93x previous step)
    6 steps has 265,976 entries (1 percent, 5.37x previous step)
    7 steps has 1,211,572 entries (5 percent, 4.56x previous step)
    8 steps has 3,965,028 entries (16 percent, 3.27x previous step)
    9 steps has 7,762,424 entries (32 percent, 1.96x previous step)
    10 steps has 7,749,136 entries (32 percent, 1.00x previous step)
    11 steps has 2,876,024 entries (11 percent, 0.37x previous step)
    12 steps has 117,084 entries (0 percent, 0.04x previous step)
    13 steps has 544 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    Average: 9.27 moves
    """

    state_targets = (
        "DDDDDDDDLLLLLLLLLLLLRRRRRRRRRRRRUUUUUUUU",
        "DDDDDDDDRRRLLRRLLRRRLLLRRLLRRLLLUUUUUUUU",
        "UUUUUUUULLLLLLLLLLLLRRRRRRRRRRRRDDDDDDDD",
        "UUUUUUUURRRLLRRLLRRRLLLRRLLRRLLLDDDDDDDD",
    )

    ULRD_inner_x_centers_oblique_edges = (
        9,
        10,
        14,
        17,
        20,
        23,
        27,
        28,  # Upper
        45,
        46,
        50,
        51,
        52,
        53,
        56,
        57,
        58,
        59,
        63,
        64,  # Left
        117,
        118,
        122,
        123,
        124,
        125,
        128,
        129,
        130,
        131,
        135,
        136,  # Right
        189,
        190,
        194,
        197,
        200,
        203,
        207,
        208,  # Down
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt",
            self.state_targets,
            linecount=24010000,
            max_depth=13,
            filesize=2232930000,
            all_moves=moves_666,
            illegal_moves=(
                "3Rw",
                "3Rw'",
                "3Lw",
                "3Lw'",
                "3Fw",
                "3Fw'",
                "3Bw",
                "3Bw'",
                "3Uw",
                "3Uw'",
                "3Dw",
                "3Dw'",
                "Rw",
                "Rw'",
                "Lw",
                "Lw'",
                "Fw",
                "Fw'",
                "Bw",
                "Bw'",
                "Uw",
                "Uw'",
                "Dw",
                "Dw'",
                "3Rw2",
                "3Fw2",
                "3Lw",
                "3Lw'",
                "3Lw2",
                "3Dw",
                "3Dw'",
                "3Dw2",
                "3Bw",
                "3Bw'",
                "3Bw2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.ULRD_inner_x_centers_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.ULRD_inner_x_centers_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable666FBInnerXCenterAndObliqueEdges(LookupTable):
    """
    lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 10 entries (0 percent, 5.00x previous step)
    2 steps has 50 entries (0 percent, 5.00x previous step)
    3 steps has 178 entries (0 percent, 3.56x previous step)
    4 steps has 816 entries (0 percent, 4.58x previous step)
    5 steps has 3,894 entries (1 percent, 4.77x previous step)
    6 steps has 15,644 entries (4 percent, 4.02x previous step)
    7 steps has 50,456 entries (14 percent, 3.23x previous step)
    8 steps has 105,874 entries (30 percent, 2.10x previous step)
    9 steps has 119,298 entries (34 percent, 1.13x previous step)
    10 steps has 45,352 entries (13 percent, 0.38x previous step)
    11 steps has 1,410 entries (0 percent, 0.03x previous step)
    12 steps has 16 entries (0 percent, 0.01x previous step)

    Total: 343,000 entries
    Average: 8.34 moves
    """

    state_targets = ("BBBFFBBFFBBBFFFBBFFBBFFF", "FFFFFFFFFFFFBBBBBBBBBBBB")

    FB_inner_x_centers_oblique_edges = (
        81,
        82,
        86,
        87,
        88,
        89,
        92,
        93,
        94,
        95,
        99,
        100,  # Front
        153,
        154,
        158,
        159,
        160,
        161,
        164,
        165,
        166,
        167,
        171,
        172,  # Back
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt",
            self.state_targets,
            linecount=343000,
            max_depth=12,
            filesize=25039000,
            all_moves=moves_666,
            illegal_moves=(
                "3Rw",
                "3Rw'",
                "3Lw",
                "3Lw'",
                "3Fw",
                "3Fw'",
                "3Bw",
                "3Bw'",
                "3Uw",
                "3Uw'",
                "3Dw",
                "3Dw'",
                "Rw",
                "Rw'",
                "Lw",
                "Lw'",
                "Fw",
                "Fw'",
                "Bw",
                "Bw'",
                "Uw",
                "Uw'",
                "Dw",
                "Dw'",
                "3Rw2",
                "3Fw2",
                "3Lw",
                "3Lw'",
                "3Lw2",
                "3Dw",
                "3Dw'",
                "3Dw2",
                "3Bw",
                "3Bw'",
                "3Bw2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.FB_inner_x_centers_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.FB_inner_x_centers_oblique_edges, state):
            cube[pos] = pos_state


class LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_666,
            illegal_moves=(
                "3Rw",
                "3Rw'",
                "3Lw",
                "3Lw'",
                "3Fw",
                "3Fw'",
                "3Bw",
                "3Bw'",
                "3Uw",
                "3Uw'",
                "3Dw",
                "3Dw'",
                "Rw",
                "Rw'",
                "Lw",
                "Lw'",
                "Fw",
                "Fw'",
                "Bw",
                "Bw'",
                "Uw",
                "Uw'",
                "Dw",
                "Dw'",
                "3Rw2",
                "3Fw2",
                "3Lw",
                "3Lw'",
                "3Lw2",
                "3Dw",
                "3Dw'",
                "3Dw2",
                "3Bw",
                "3Bw'",
                "3Bw2",
            ),
            prune_tables=(
                parent.lt_LR_solve_inner_x_centers_and_oblique_edges,
                parent.lt_FB_solve_inner_x_centers_and_oblique_edges,
            ),
            multiplier=1.2,
        )


class RubiksCube666(RubiksCubeNNNEvenEdges):
    """
    6x6x6 strategy
    - stage LR centers to sides L or R (use IDA)
    - stage UD centers to sides U or D...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3

    Inheritance model
    -----------------
            RubiksCube
                |
        RubiksCubeNNNEvenEdges
           /            \
    RubiksCubeNNNEven RubiksCube666
    """

    instantiated = False

    reduce333_orient_edges_tuples = (
        (2, 149),
        (3, 148),
        (4, 147),
        (5, 146),
        (7, 38),
        (12, 113),
        (13, 39),
        (18, 112),
        (19, 40),
        (24, 111),
        (25, 41),
        (30, 110),
        (32, 74),
        (33, 75),
        (34, 76),
        (35, 77),
        (38, 7),
        (39, 13),
        (40, 19),
        (41, 25),
        (43, 156),
        (48, 79),
        (49, 162),
        (54, 85),
        (55, 168),
        (60, 91),
        (61, 174),
        (66, 97),
        (68, 205),
        (69, 199),
        (70, 193),
        (71, 187),
        (74, 32),
        (75, 33),
        (76, 34),
        (77, 35),
        (79, 48),
        (84, 115),
        (85, 54),
        (90, 121),
        (91, 60),
        (96, 127),
        (97, 66),
        (102, 133),
        (104, 182),
        (105, 183),
        (106, 184),
        (107, 185),
        (110, 30),
        (111, 24),
        (112, 18),
        (113, 12),
        (115, 84),
        (120, 151),
        (121, 90),
        (126, 157),
        (127, 96),
        (132, 163),
        (133, 102),
        (138, 169),
        (140, 192),
        (141, 198),
        (142, 204),
        (143, 210),
        (146, 5),
        (147, 4),
        (148, 3),
        (149, 2),
        (151, 120),
        (156, 43),
        (157, 126),
        (162, 49),
        (163, 132),
        (168, 55),
        (169, 138),
        (174, 61),
        (176, 215),
        (177, 214),
        (178, 213),
        (179, 212),
        (182, 104),
        (183, 105),
        (184, 106),
        (185, 107),
        (187, 71),
        (192, 140),
        (193, 70),
        (198, 141),
        (199, 69),
        (204, 142),
        (205, 68),
        (210, 143),
        (212, 179),
        (213, 178),
        (214, 177),
        (215, 176),
    )

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCubeNNNEvenEdges.__init__(self, state, order, colormap, debug)

        if RubiksCube666.instantiated:
            # raise Exception("Another 6x6x6 instance is being created")
            log.warning("Another 6x6x6 instance is being created")
        else:
            RubiksCube666.instantiated = True

    def get_fake_444(self):
        if self.fake_444 is None:
            self.fake_444 = RubiksCube444(solved_444, "URFDLB")
            self.fake_444.cpu_mode = "normal"
            self.fake_444.lt_init()
            self.fake_444.enable_print_cube = False
        else:
            self.fake_444.re_init()
        return self.fake_444

    def get_fake_555(self):
        if self.fake_555 is None:
            self.fake_555 = RubiksCube555(solved_555, "URFDLB")
            self.fake_555.cpu_mode = self.cpu_mode
            self.fake_555.lt_init()
            self.fake_555.enable_print_cube = False

        else:
            self.fake_555.re_init()
        return self.fake_555

    def print_edge_tuples(self):
        edge_indexes = list(edge_orbit_0) + list(edge_orbit_1)
        edge_indexes.sort()

        for (count, square_index) in enumerate(edge_indexes):

            if count % 16 == 0:
                print("")

            # Used to build edges_partner_666
            # side = self.index_to_side[square_index]
            # partner_index = side.get_wing_partner(square_index)
            # print("    %d: %d," % (square_index, partner_index))

            partner_index = edges_partner_666[square_index]
            sys.stdout.write("(%d, %d), " % (square_index, partner_index))

        print("")

    def sanity_check(self):
        corners = (
            1,
            6,
            31,
            36,
            37,
            42,
            67,
            72,
            73,
            78,
            103,
            108,
            109,
            114,
            139,
            144,
            145,
            150,
            175,
            180,
            181,
            186,
            211,
            216,
        )

        left_oblique_edge = (
            9,
            17,
            28,
            20,
            45,
            53,
            64,
            56,
            81,
            89,
            100,
            92,
            117,
            125,
            136,
            128,
            153,
            161,
            172,
            164,
            189,
            197,
            208,
            200,
        )

        right_oblique_edge = (
            10,
            23,
            27,
            14,
            46,
            59,
            63,
            50,
            82,
            95,
            99,
            86,
            118,
            131,
            135,
            122,
            154,
            167,
            171,
            158,
            190,
            203,
            207,
            194,
        )

        outside_x_centers = (
            8,
            11,
            26,
            29,
            44,
            47,
            62,
            65,
            80,
            83,
            98,
            101,
            116,
            119,
            134,
            137,
            152,
            155,
            170,
            173,
            188,
            191,
            206,
            209,
        )

        inside_x_centers = (
            15,
            16,
            21,
            22,
            51,
            52,
            57,
            58,
            87,
            88,
            93,
            94,
            123,
            124,
            129,
            130,
            159,
            160,
            165,
            166,
            195,
            196,
            201,
            202,
        )

        self._sanity_check("edge-orbit-0", edge_orbit_0, 8)
        self._sanity_check("edge-orbit-1", edge_orbit_1, 8)
        self._sanity_check("corners", corners, 4)
        self._sanity_check("left-oblique", left_oblique_edge, 4)
        self._sanity_check("right-oblique", right_oblique_edge, 4)
        self._sanity_check("outside x-center", outside_x_centers, 4)
        self._sanity_check("inside x-center", inside_x_centers, 4)

    def lt_init(self, LR_oblique_edge_only=False):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # phase 2
        self.lt_LR_oblique_edge_stage = LookupTable666LRObliquEdgeStage(self)

        # This is the case if a 777 is using 666 to pair its LR oblique edges
        if LR_oblique_edge_only:
            return

        # phase 4
        self.lt_UD_left_oblique_edges_stage = LookupTable666UDLeftObliqueStage(self)
        self.lt_UD_right_oblique_edges_stage = LookupTable666UDRightObliqueStage(self)
        self.lt_UD_outer_x_centers_stage = LookupTable666UDOuterXCenterStage(self)
        self.lt_UD_centers_stage = LookupTableIDA666UDCentersStage(self)

        # phase 5
        self.lt_UD_solve_inner_x_centers_and_oblique_edges = LookupTable666UDInnerXCenterAndObliqueEdges(self)

        # phase 6
        self.lt_LR_solve_inner_x_centers_and_oblique_edges = LookupTable666LRInnerXCenterAndObliqueEdges(self)
        self.lt_FB_solve_inner_x_centers_and_oblique_edges = LookupTable666FBInnerXCenterAndObliqueEdges(self)
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges = LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(self)

    def populate_fake_444_for_inner_x_centers_stage(self):
        fake_444 = self.get_fake_444()
        fake_444.nuke_corners()
        fake_444.nuke_edges()
        fake_444.nuke_centers()

        for side_index in range(6):
            offset_444 = side_index * 16
            offset_666 = side_index * 36

            # Centers
            fake_444.state[6 + offset_444] = self.state[15 + offset_666]
            fake_444.state[7 + offset_444] = self.state[16 + offset_666]
            fake_444.state[10 + offset_444] = self.state[21 + offset_666]
            fake_444.state[11 + offset_444] = self.state[22 + offset_666]

            # Edges
            fake_444.state[2 + offset_444] = self.state[3 + offset_666]
            fake_444.state[3 + offset_444] = self.state[4 + offset_666]
            fake_444.state[5 + offset_444] = self.state[13 + offset_666]
            fake_444.state[9 + offset_444] = self.state[19 + offset_666]
            fake_444.state[8 + offset_444] = self.state[18 + offset_666]
            fake_444.state[12 + offset_444] = self.state[24 + offset_666]
            fake_444.state[14 + offset_444] = self.state[33 + offset_666]
            fake_444.state[15 + offset_444] = self.state[34 + offset_666]

    def populate_fake_555_for_ULFRBD_solve(self):
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()
        side_names = ("U", "L", "F", "R", "B", "D")

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_666 = side_index * 36
            side_name = side_names[side_index]

            # Corners
            fake_555.state[1 + offset_555] = self.state[1 + offset_666]
            fake_555.state[5 + offset_555] = self.state[6 + offset_666]
            fake_555.state[21 + offset_555] = self.state[31 + offset_666]
            fake_555.state[25 + offset_555] = self.state[36 + offset_666]

            # Centers
            fake_555.state[7 + offset_555] = self.state[8 + offset_666]
            fake_555.state[8 + offset_555] = self.state[9 + offset_666]
            fake_555.state[9 + offset_555] = self.state[11 + offset_666]
            fake_555.state[12 + offset_555] = self.state[14 + offset_666]
            fake_555.state[13 + offset_555] = side_name
            fake_555.state[14 + offset_555] = self.state[17 + offset_666]
            fake_555.state[17 + offset_555] = self.state[26 + offset_666]
            fake_555.state[18 + offset_555] = self.state[27 + offset_666]
            fake_555.state[19 + offset_555] = self.state[29 + offset_666]

            # Edges
            fake_555.state[2 + offset_555] = self.state[2 + offset_666]
            fake_555.state[3 + offset_555] = side_name
            fake_555.state[4 + offset_555] = self.state[5 + offset_666]

            fake_555.state[6 + offset_555] = self.state[7 + offset_666]
            fake_555.state[10 + offset_555] = self.state[12 + offset_666]

            fake_555.state[11 + offset_555] = side_name
            fake_555.state[15 + offset_555] = side_name

            fake_555.state[16 + offset_555] = self.state[25 + offset_666]
            fake_555.state[20 + offset_555] = self.state[30 + offset_666]

            fake_555.state[22 + offset_555] = self.state[32 + offset_666]
            fake_555.state[23 + offset_555] = side_name
            fake_555.state[24 + offset_555] = self.state[35 + offset_666]

    def group_centers_guts(self, oblique_edges_only=False):
        self.lt_init()

        # phase 1
        # stage the inner-x centers via 444 solver
        fake_444 = self.get_fake_444()
        self.populate_fake_444_for_inner_x_centers_stage()
        tmp_solution_len = len(self.solution)

        if oblique_edges_only:
            fake_444.lt_ULFRBD_centers_stage.avoid_oll = None

        fake_444.lt_ULFRBD_centers_stage.solve_via_c()

        for step in fake_444.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                if "w" in step:
                    step = "3" + step
                self.rotate(step)

        self.rotate_for_best_centers_staging(inner_x_centers_666)
        self.print_cube()

        # phase 2
        # pair the LR oblique edges
        tmp_solution_len = len(self.solution)
        self.lt_LR_oblique_edge_stage.solve()
        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_666_LR_oblique_edges_staged"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: LR oblique edges paired (not staged), %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

        # phase 3
        # Stage LR centers via 555
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        tmp_solution_len = len(self.solution)
        fake_555.group_centers_stage_LR()

        for step in fake_555.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                self.rotate(step)

        self.rotate_for_best_centers_staging(inner_x_centers_666)
        self.print_cube()
        log.info("%s: LR centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # phase 4
        # pair the UD oblique edges and outer x-centers to finish staging centers
        self.lt_UD_centers_stage.solve_via_c()

        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_666_centers_staged"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        log.info("%s: centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Reduce the centers to 5x5x5 centers
        # - solve the UD inner x-centers and pair the UD oblique edges
        # - solve the LR inner x-centers and pair the LR oblique edges
        # - solve the FB inner x-centers and pair the FB oblique edges

        # phase 5
        # solve the UD inner x-centers and pair the UD oblique edges
        tmp_solution_len = len(self.solution)
        self.lt_UD_solve_inner_x_centers_and_oblique_edges.solve()
        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_666_UD_reduced_to_555"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: UD inner x-center solved and oblique edges paired, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        # log.info("kociemba: %s" % self.get_kociemba_string(True))

        # phase 6
        # solve the LR inner x-centers and pair the LR oblique edges
        # solve the FB inner x-centers and pair the FB oblique edges
        tmp_solution_len = len(self.solution)
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.solve_via_c()
        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_666_LR_FB_reduced_to_555"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: LFRB inner x-center and oblique edges paired, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

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


def rotate_666(cube, step):
    return [cube[x] for x in swaps_666[step]]
