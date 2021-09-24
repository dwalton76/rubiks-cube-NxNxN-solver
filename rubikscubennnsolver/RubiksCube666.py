# standard libraries
import logging
import sys

# rubiks cube libraries
from rubikscubennnsolver.LookupTable import LookupTable
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges
from rubikscubennnsolver.swaps import swaps_666

logger = logging.getLogger(__name__)


# fmt: off
moves_666 = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",
    "F", "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",
    "R", "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",
    "B", "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",
    "D", "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2",
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
    15, 16, 21, 22,  # Upper
    51, 52, 57, 58,  # Left
    87, 88, 93, 94,  # Front
    123, 124, 129, 130,  # Right
    159, 160, 165, 166,  # Back
    195, 196, 201, 202,  # Down
)

centers_666 = (
    8, 9, 10, 11, 14, 15, 16, 17, 20, 21, 22, 23, 26, 27, 28, 29,  # Upper
    44, 45, 46, 47, 50, 51, 52, 53, 56, 57, 58, 59, 62, 63, 64, 65,  # Left
    80, 81, 82, 83, 86, 87, 88, 89, 92, 93, 94, 95, 98, 99, 100, 101,  # Front
    116, 117, 118, 119, 122, 123, 124, 125, 128, 129, 130, 131, 134, 135, 136, 137,  # Right
    152, 153, 154, 155, 158, 159, 160, 161, 164, 165, 166, 167, 170, 171, 172, 173,  # Back
    188, 189, 190, 191, 194, 195, 196, 197, 200, 201, 202, 203, 206, 207, 208, 209,  # Down
)

UFBD_left_oblique_edges_666 = (
    9, 17, 20, 28,  # Upper
    81, 89, 92, 100,  # Front
    153, 161, 164, 172,  # Back
    189, 197, 200, 208,  # Down
)

UFBD_right_oblique_edges_666 = (
    10, 14, 23, 27,  # Upper
    82, 86, 95, 99,  # Front
    154, 158, 167, 171,  # Back
    190, 194, 203, 207,  # Down
)

UFBD_outer_x_centers_666 = (
    8, 11, 26, 29,  # Upper
    80, 83, 98, 101,  # Front
    152, 155, 170, 173,  # Back
    188, 191, 206, 209,  # Down
)

UFBD_inner_x_centers_666 = (
    15, 16, 21, 22,  # Upper
    87, 88, 93, 94,  # Front
    159, 160, 165, 166,  # Back
    195, 196, 201, 202,  # Down
)

edge_orbit_0 = (
    2, 5, 12, 30, 35, 32, 25, 7,
    38, 41, 48, 66, 71, 68, 61, 43,
    74, 77, 84, 102, 107, 104, 97, 79,
    110, 113, 120, 138, 143, 140, 133, 115,
    146, 149, 156, 174, 179, 176, 169, 151,
    182, 185, 192, 210, 215, 212, 205, 187,
)

edge_orbit_1 = (
    3, 4, 18, 24, 34, 33, 19, 13,
    39, 40, 54, 60, 70, 69, 55, 49,
    75, 76, 90, 96, 106, 105, 91, 85,
    111, 112, 126, 132, 142, 141, 127, 121,
    147, 148, 162, 168, 178, 177, 163, 157,
    183, 184, 198, 204, 214, 213, 199, 193,
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
# fmt: on


# phase 1
class LookupTable666LRInnerXCentersStage(LookupTable):
    """
    lookup-table-6x6x6-step00-inner-x-centers-stage.txt
    ===================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 82 entries (0 percent, 20.50x previous step)
    3 steps has 1,206 entries (0 percent, 14.71x previous step)
    4 steps has 14,116 entries (1 percent, 11.70x previous step)
    5 steps has 123,404 entries (16 percent, 8.74x previous step)
    6 steps has 422,508 entries (57 percent, 3.42x previous step)
    7 steps has 173,254 entries (23 percent, 0.41x previous step)
    8 steps has 896 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    Average: 6.03 moves
    """

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step00-inner-x-centers-stage.txt",
            "xxxxLLLLxxxxLLLLxxxxxxxx",
            linecount=735471,
            max_depth=8,
            all_moves=moves_666,
            illegal_moves=(),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        return "".join(["L" if self.parent.state[x] in ("L", "R") else "x" for x in inner_x_centers_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(inner_x_centers_666, state):
            cube[pos] = pos_state


class LookupTable666LRObliquEdgeStage(LookupTableIDAViaGraph):
    """
    Use the inner-x-centers table to pair the LR inner-x-centers while using an "unpaired oblique edges" heuristic
    to get the LR oblique edges paired anywhere.  We do not need these obliques to be placed on sides
    LR at this point.
    """

    # fmt: off
    oblique_edges_666 = (
        9, 10, 14, 17, 20, 23, 27, 28,
        45, 46, 50, 53, 56, 59, 63, 64,
        81, 82, 86, 89, 92, 95, 99, 100,
        117, 118, 122, 125, 128, 131, 135, 136,
        153, 154, 158, 161, 164, 167, 171, 172,
        189, 190, 194, 197, 200, 203, 207, 208,
    )
    # fmt: on

    def __init__(self, parent):

        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_666,
            illegal_moves=(),
            centers_only=True,
            prune_tables=[
                parent.lt_LR_inner_x_centers_stage,
            ],
            C_ida_type="6x6x6-LR-oblique-edges-stage",  # C_ida_type
        )
        # fmt: on

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in self.oblique_edges_666 or x in inner_x_centers_666:
                if self.parent.state[x] == "L" or self.parent.state[x] == "R":
                    self.parent.state[x] = "L"
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


# phase 3
class LookupTable666UDInnerXCentersStage(LookupTable):
    """
    lookup-table-6x6x6-step11-UD-inner-x-centers-stage.txt
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

    # fmt: off
    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step11-UD-inner-x-centers-stage.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=7,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "L", "L'", "L2",
                "R", "R'", "R2"
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_inner_x_centers_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_inner_x_centers_666, state):
            cube[pos] = pos_state


class LookupTable666UDXCentersStage(LookupTable):
    """
    lookup-table-6x6x6-step12-UD-x-centers.txt
    ==========================================
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

    # fmt: off
    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step12-UD-x-centers.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=7,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "L", "L'", "L2",
                "R", "R'", "R2"
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_outer_x_centers_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_outer_x_centers_666, state):
            cube[pos] = pos_state


class LookupTable666UDLeftObliqueCentersStage(LookupTable):
    """
    lookup-table-6x6x6-step13-UD-left-oblique-centers.txt
    =====================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 70 entries (0 percent, 17.50x previous step)
    3 steps has 804 entries (6 percent, 11.49x previous step)
    4 steps has 4,615 entries (35 percent, 5.74x previous step)
    5 steps has 7,048 entries (54 percent, 1.53x previous step)
    6 steps has 328 entries (2 percent, 0.05x previous step)

    Total: 12,870 entries
    Average: 4.52 moves
    """

    # fmt: off
    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step13-UD-left-oblique-centers.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=6,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "L", "L'", "L2",
                "R", "R'", "R2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_left_oblique_edges_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_left_oblique_edges_666, state):
            cube[pos] = pos_state


class LookupTable666UDRightObliqueCentersStage(LookupTable):
    """
    lookup-table-6x6x6-step14-UD-right-oblique-centers.txt
    ======================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 70 entries (0 percent, 17.50x previous step)
    3 steps has 804 entries (6 percent, 11.49x previous step)
    4 steps has 4,615 entries (35 percent, 5.74x previous step)
    5 steps has 7,048 entries (54 percent, 1.53x previous step)
    6 steps has 328 entries (2 percent, 0.05x previous step)

    Total: 12,870 entries
    Average: 4.52 moves
    """

    # fmt: off
    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step14-UD-right-oblique-centers.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=6,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "L", "L'", "L2",
                "R", "R'", "R2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_right_oblique_edges_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_right_oblique_edges_666, state):
            cube[pos] = pos_state


class LookupTable666UDObliquEdgeStage(LookupTableIDAViaGraph):
    """
    Use the inner-x-centers table to pair the UFBD inner-x-centers while using an "unpaired oblique edges" heuristic
    to get the UD oblique edges paired anywhere on sides UFDB.  We do not need these obliques to be placed on sides
    UD at this point.
    """

    # fmt: off
    oblique_edges_666 = (
        9, 10, 14, 17, 20, 23, 27, 28,
        45, 46, 50, 53, 56, 59, 63, 64,
        81, 82, 86, 89, 92, 95, 99, 100,
        117, 118, 122, 125, 128, 131, 135, 136,
        153, 154, 158, 161, 164, 167, 171, 172,
        189, 190, 194, 197, 200, 203, 207, 208,
    )

    def __init__(self, parent):

        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "L", "L'", "L2",
                "R", "R'", "R2",
            ),
            centers_only=True,
            prune_tables=[
                parent.lt_UD_inner_x_centers_stage,
            ],
            C_ida_type="6x6x6-UD-oblique-edges-stage",  # C_ida_type
        )
    # fmt: on

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        # self.parent.nuke_edges()

        for x in centers_666:
            if x in self.oblique_edges_666 or x in inner_x_centers_666:
                if self.parent.state[x] == "U" or self.parent.state[x] == "D":
                    self.parent.state[x] = "U"
                elif self.parent.state[x] == "L" or self.parent.state[x] == "R":
                    self.parent.state[x] = "."
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


class LookupTable666UDObliquEdgeInnerXCentersStage(LookupTableIDAViaGraph):
    """
    Stage the UD inner x-centers and oblique edges
    """

    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_666,
            illegal_moves=(
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "L", "L'", "L2",
                "R", "R'", "R2",
            ),
            prune_tables=(
                parent.lt_UD_inner_x_centers_stage,
                parent.lt_UD_left_oblique_edges_stage,
                parent.lt_UD_right_oblique_edges_stage,
            ),
            centers_only=True,
            perfect_hash01_filename="lookup-table-6x6x6-step16-UD-left-oblique-inner-x-centers.perfect-hash",
            perfect_hash02_filename="lookup-table-6x6x6-step17-UD-right-oblique-inner-x-centers.perfect-hash",
            perfect_hash12_filename="lookup-table-6x6x6-step15-UD-oblique-centers.perfect-hash",
            pt1_state_max=12870,
            pt2_state_max=12870,
        )
        # fmt: on


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

    # fmt: off
    UD_inner_x_centers_and_oblique_edges = (
        9, 10, 14, 15, 16, 17, 20, 21, 22, 23, 27, 28,  # Upper
        189, 190, 194, 195, 196, 197, 200, 201, 202, 203, 207, 208,  # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt",
            (
                "198e67", "19b267", "19bc47", "19be23", "19be64", "1dc267", "1dcc47", "1dce23",
                "1dce64", "1df047", "1df223", "1df264", "1dfc03", "1dfc44", "1dfe20", "3b8267",
                "3b8c47", "3b8e23", "3b8e64", "3bb047", "3bb223", "3bb264", "3bbc03", "3bbc44",
                "3bbe20", "3fc047", "3fc223", "3fc264", "3fcc03", "3fcc44", "3fce20", "3ff003",
                "3ff044", "3ff220", "3ffc00", "d98267", "d98c47", "d98e23", "d98e64", "d9b047",
                "d9b223", "d9b264", "d9bc03", "d9bc44", "d9be20", "ddc047", "ddc223", "ddc264",
                "ddcc03", "ddcc44", "ddce20", "ddf003", "ddf044", "ddf220", "ddfc00", "fb8047",
                "fb8223", "fb8264", "fb8c03", "fb8c44", "fb8e20", "fbb003", "fbb044", "fbb220",
                "fbbc00", "ffc003", "ffc044", "ffc220", "ffcc00", "fff000",
            ),
            linecount=343000,
            max_depth=8,
            md5_txt="e1b1991511ed4bba6ee5cbc118b19ea3",
        )
    # fmt: on

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
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 12 entries (0 percent, 6.00x previous step)
    2 steps has 68 entries (0 percent, 5.67x previous step)
    3 steps has 282 entries (0 percent, 4.15x previous step)
    4 steps has 1,218 entries (0 percent, 4.32x previous step)
    5 steps has 5,382 entries (1 percent, 4.42x previous step)
    6 steps has 20,484 entries (5 percent, 3.81x previous step)
    7 steps has 62,640 entries (18 percent, 3.06x previous step)
    8 steps has 118,196 entries (34 percent, 1.89x previous step)
    9 steps has 104,328 entries (30 percent, 0.88x previous step)
    10 steps has 29,872 entries (8 percent, 0.29x previous step)
    11 steps has 516 entries (0 percent, 0.02x previous step)

    Total: 343,000 entries
    Average: 8.11 moves
    """

    # fmt: off
    state_targets = (
        "LLLLLLLLLLLLRRRRRRRRRRRR",
        "RRRLLRRLLRRRLLLRRLLRRLLL",
    )

    LR_inner_x_centers_oblique_edges = (
        45, 46, 50, 51, 52, 53, 56, 57, 58, 59, 63, 64,  # Left
        117, 118, 122, 123, 124, 125, 128, 129, 130, 131, 135, 136,  # Right
    )
    # fmt: on

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt",
            self.state_targets,
            linecount=343000,
            max_depth=12,
            all_moves=moves_666,
            illegal_moves=(
                "3Rw", "3Rw'",
                "3Lw", "3Lw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "Rw", "Rw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "3Rw2",
                "3Lw2",
                "3Fw2",
                "3Bw2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
            md5_bin="ab6a16a1f73c7a77570d89818d1e4821",
            md5_state_index="9cb94f2836125f89c439cd354c3252c1",
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_inner_x_centers_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_inner_x_centers_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable666FBInnerXCenterAndObliqueEdges(LookupTable):
    """
    lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 12 entries (0 percent, 6.00x previous step)
    2 steps has 68 entries (0 percent, 5.67x previous step)
    3 steps has 282 entries (0 percent, 4.15x previous step)
    4 steps has 1,218 entries (0 percent, 4.32x previous step)
    5 steps has 5,382 entries (1 percent, 4.42x previous step)
    6 steps has 20,484 entries (5 percent, 3.81x previous step)
    7 steps has 62,640 entries (18 percent, 3.06x previous step)
    8 steps has 118,196 entries (34 percent, 1.89x previous step)
    9 steps has 104,328 entries (30 percent, 0.88x previous step)
    10 steps has 29,872 entries (8 percent, 0.29x previous step)
    11 steps has 516 entries (0 percent, 0.02x previous step)

    Total: 343,000 entries
    Average: 8.11 moves
    """

    state_targets = ("BBBFFBBFFBBBFFFBBFFBBFFF", "FFFFFFFFFFFFBBBBBBBBBBBB")

    # fmt: off
    FB_inner_x_centers_oblique_edges = (
        81, 82, 86, 87, 88, 89, 92, 93, 94, 95, 99, 100,  # Front
        153, 154, 158, 159, 160, 161, 164, 165, 166, 167, 171, 172,  # Back
    )
    # fmt: on

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt",
            self.state_targets,
            linecount=343000,
            max_depth=12,
            all_moves=moves_666,
            illegal_moves=(
                "3Rw", "3Rw'",
                "3Lw", "3Lw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "Rw", "Rw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "3Rw2",
                "3Lw2",
                "3Fw2",
                "3Bw2",
            ),
            use_state_index=True,
            build_state_index=build_state_index,
            md5_bin="e3ffa78934aea743884dcd0c4121420f",
            md5_state_index="83059d579e597f51e8322c684bb7fb08",
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.FB_inner_x_centers_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.FB_inner_x_centers_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable666UDObliqueEdges(LookupTable):
    """
    lookup-tables/lookup-table-6x6x6-step63-UD-oblique-edges.txt
    ============================================================
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 12 entries (0 percent, 6.00x previous step)
    2 steps has 112 entries (0 percent, 9.33x previous step)
    3 steps has 842 entries (0 percent, 7.52x previous step)
    4 steps has 4,494 entries (1 percent, 5.34x previous step)
    5 steps has 14,522 entries (4 percent, 3.23x previous step)
    6 steps has 39,056 entries (11 percent, 2.69x previous step)
    7 steps has 76,368 entries (22 percent, 1.96x previous step)
    8 steps has 83,760 entries (24 percent, 1.10x previous step)
    9 steps has 69,560 entries (20 percent, 0.83x previous step)
    10 steps has 39,736 entries (11 percent, 0.57x previous step)
    11 steps has 12,808 entries (3 percent, 0.32x previous step)
    12 steps has 1,728 entries (0 percent, 0.13x previous step)

    Total: 343,000 entries
    Average: 7.92 moves
    """

    # fmt: off
    state_targets = (
        "UUUUUUUULLLLFFFFRRRRBBBBDDDDDDDD",
        "DDDDDDDDLLLLFFFFRRRRBBBBUUUUUUUU",
    )

    UD_oblique_edges_LFRB_inner_x_centers = (
        9, 10, 14, 17, 20, 23, 27, 28,  # Upper
        51, 52, 57, 58,  # Left
        87, 88, 93, 94,  # Front
        123, 124, 129, 130,  # Right
        159, 160, 165, 166,  # Back
        189, 190, 194, 197, 200, 203, 207, 208,  # Down
    )
    # fmt: on

    def __init__(self, parent, build_state_index: bool = False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step63-UD-oblique-edges.txt',
            self.state_targets,
            linecount=343000,
            max_depth=12,
            all_moves=moves_666,
            illegal_moves=(
                "3Rw", "3Rw'",
                "3Lw", "3Lw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "Rw", "Rw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "3Rw2",
                "3Lw2",
                "3Fw2",
                "3Bw2"
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_oblique_edges_LFRB_inner_x_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_oblique_edges_LFRB_inner_x_centers, state):
            cube[pos] = pos_state


class LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(LookupTableIDAViaGraph):
    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_666,
            illegal_moves=(
                "3Rw", "3Rw'",
                "3Lw", "3Lw'",
                "3Fw", "3Fw'",
                "3Bw", "3Bw'",
                "3Uw", "3Uw'",
                "3Dw", "3Dw'",
                "Rw", "Rw'",
                "Lw", "Lw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Uw", "Uw'",
                "Dw", "Dw'",
                "3Rw2",
                "3Lw2",
                "3Fw2",
                "3Bw2",
            ),
            prune_tables=(
                parent.lt_LR_solve_inner_x_centers_and_oblique_edges,
                parent.lt_FB_solve_inner_x_centers_and_oblique_edges,
                parent.lt_UD_oblique_edges,
            ),
            centers_only=True,
        )
        # fmt: on


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
            # logger.warning("Another 6x6x6 instance is being created")
            pass
        else:
            RubiksCube666.instantiated = True

    def get_fake_555(self):
        if self.fake_555 is None:
            self.fake_555 = RubiksCube555(solved_555, "URFDLB")
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
        # fmt: off
        corners = (
            1, 6, 31, 36,
            37, 42, 67, 72,
            73, 78, 103, 108,
            109, 114, 139, 144,
            145, 150, 175, 180,
            181, 186, 211, 216,
        )

        left_oblique_edge = (
            9, 17, 28, 20,
            45, 53, 64, 56,
            81, 89, 100, 92,
            117, 125, 136, 128,
            153, 161, 172, 164,
            189, 197, 208, 200,
        )

        right_oblique_edge = (
            10, 23, 27, 14,
            46, 59, 63, 50,
            82, 95, 99, 86,
            118, 131, 135, 122,
            154, 167, 171, 158,
            190, 203, 207, 194,
        )

        outside_x_centers = (
            8, 11, 26, 29,
            44, 47, 62, 65,
            80, 83, 98, 101,
            116, 119, 134, 137,
            152, 155, 170, 173,
            188, 191, 206, 209,
        )

        inside_x_centers = (
            15, 16, 21, 22,
            51, 52, 57, 58,
            87, 88, 93, 94,
            123, 124, 129, 130,
            159, 160, 165, 166,
            195, 196, 201, 202,
        )
        # fmt: on

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

        # phase 1
        self.lt_LR_inner_x_centers_stage = LookupTable666LRInnerXCentersStage(self)
        self.lt_LR_oblique_edge_stage = LookupTable666LRObliquEdgeStage(self)

        # phase 2
        self.lt_UD_inner_x_centers_stage = LookupTable666UDInnerXCentersStage(self)
        self.lt_UD_outer_x_centers_stage = LookupTable666UDXCentersStage(self)
        self.lt_UD_left_oblique_edges_stage = LookupTable666UDLeftObliqueCentersStage(self)
        self.lt_UD_right_oblique_edges_stage = LookupTable666UDRightObliqueCentersStage(self)

        # phase 3
        self.lt_UD_oblique_edge_stage = LookupTable666UDObliquEdgeStage(self)
        self.lt_UD_oblique_edge_stage.avoid_oll = (0, 1)

        self.lt_UD_oblique_edge_inner_x_center_stage = LookupTable666UDObliquEdgeInnerXCentersStage(self)
        self.lt_UD_oblique_edge_inner_x_center_stage.avoid_oll = (0, 1)

        # This is the case if a 777 is using 666 to pair its LR oblique edges
        # TODO is this still needed?
        if LR_oblique_edge_only:
            return

        # phase 5
        self.lt_UD_solve_inner_x_centers_and_oblique_edges = LookupTable666UDInnerXCenterAndObliqueEdges(self)

        # phase 6
        self.lt_LR_solve_inner_x_centers_and_oblique_edges = LookupTable666LRInnerXCenterAndObliqueEdges(self)
        self.lt_FB_solve_inner_x_centers_and_oblique_edges = LookupTable666FBInnerXCenterAndObliqueEdges(self)
        self.lt_UD_oblique_edges = LookupTable666UDObliqueEdges(self)
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges = LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(self)

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

            # corners
            fake_555.state[1 + offset_555] = self.state[1 + offset_666]
            fake_555.state[5 + offset_555] = self.state[6 + offset_666]
            fake_555.state[21 + offset_555] = self.state[31 + offset_666]
            fake_555.state[25 + offset_555] = self.state[36 + offset_666]

            # centers
            fake_555.state[7 + offset_555] = self.state[8 + offset_666]
            fake_555.state[8 + offset_555] = self.state[9 + offset_666]
            fake_555.state[9 + offset_555] = self.state[11 + offset_666]
            fake_555.state[12 + offset_555] = self.state[14 + offset_666]
            fake_555.state[13 + offset_555] = side_name
            fake_555.state[14 + offset_555] = self.state[17 + offset_666]
            fake_555.state[17 + offset_555] = self.state[26 + offset_666]
            fake_555.state[18 + offset_555] = self.state[27 + offset_666]
            fake_555.state[19 + offset_555] = self.state[29 + offset_666]

            # edges
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

    def reduced_to_555(self) -> bool:

        if not all([self.state[x] == "U" for x in (15, 16, 21, 22)]):  # Upper
            return False

        if not all([self.state[x] == "L" for x in (51, 52, 57, 58)]):  # Left
            return False

        if not all([self.state[x] == "F" for x in (87, 88, 93, 94)]):  # Front
            return False

        if not all([self.state[x] == "R" for x in (123, 124, 129, 130)]):  # Right
            return False

        if not all([self.state[x] == "B" for x in (159, 160, 165, 166)]):  # Back
            return False

        if not all([self.state[x] == "D" for x in (195, 196, 201, 202)]):  # Down
            return False

        # verify all oblique edges are paired
        # fmt: off
        for (x, y) in (
            (9, 10), (20, 14), (17, 23), (28, 27),  # Upper
            (45, 46), (56, 50), (53, 59), (64, 63),  # Left
            (81, 82), (92, 86), (89, 95), (100, 99),  # Front
            (117, 118), (128, 122), (125, 131), (136, 135),  # Right
            (153, 154), (164, 158), (161, 167), (172, 171),  # Back
            (189, 190), (200, 194), (197, 203), (208, 207),  # Down
        ):
            if self.state[x] != self.state[y]:
                return False

        # verify the inside orbit of edges are paired
        for (x, y) in (
            (3, 4), (18, 24), (34, 33), (19, 13),  # Upper
            (39, 40), (54, 60), (70, 69), (55, 49),  # Left
            (75, 76), (90, 96), (106, 105), (91, 85),  # Front
            (111, 112), (126, 132), (142, 141), (127, 121),  # Right
            (147, 148), (162, 168), (178, 177), (163, 157),  # Back
            (183, 184), (198, 204), (214, 213), (199, 193),  # Down
        ):
            if self.state[x] != self.state[y]:
                return False
        # fmt: on

        return True

    def daisy_solve_centers(self):
        """
        The inner x-centers and oblique edges are staged. Daisy solve the centers by
        - pair the inner x-centers
        - pair the oblique edges
        - put the oblique edges in a "daisy" pattern around the inner x-centers

        This reduces our centers to 5x5x5 centers
        """

        # HMMM - thoughts on other ways to tackle this problem:
        #
        #   There are 70^3 per side so to do this in one phase would be a 70^9 search space!
        #   You could potentially do multiple 70^5 perfect-hash tables with 1,680,700,000 entries
        #   or 70^4 perfect-hash with 24,010,000 entries
        #
        #       70^5/70^9 is 0.000 000 041
        #       70^4/70^9 is 0.000 000 000 594
        #
        #   Realistically it would take multiple 70^5 perfect-hash tables to make this fast enough. It
        #   might be doable but that means the solver could no longer run on a raspberry pi.
        #
        #
        #   Another two phase approach could be
        #   - solve the inner x-centers and pair all of the edges (via unpaired count heuristic). The inner x-centers
        #     part would average 7.51 moves. I've never tried the unpaired count heuristic for multiple sides at the
        #     same time. Maybe try that first (without worrying about inner x-centers) and see how slow it is?
        #   - use 555 to daisy solve the t-centers. This will average 5.19 move (see Build555ULFRBDTCenterDaisySolve)
        #   I have no idea if this would be any better than the two-phase approach we have today.

        # phase 5
        # solve the UD inner x-centers and pair the UD oblique edges
        # this takes ~6 steps
        tmp_solution_len = len(self.solution)
        self.lt_UD_solve_inner_x_centers_and_oblique_edges.solve()
        self.print_cube(
            "%s: UD inner x-center solved and oblique edges paired (%d steps in)"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        self.solution.append(
            "COMMENT_%d_steps_666_UD_reduced_to_555"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        # phase 6
        # solve the LR inner x-centers, pair the LR oblique edges and daisy solve LR
        # solve the FB inner x-centers, pair the FB oblique edges and daisy solve FB
        # daisy solve UD
        # this takes ~14 steps
        tmp_solution_len = len(self.solution)
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.solve_via_c()
        self.print_cube(
            "%s: LFRB inner x-center and oblique edges paired (%d steps in)"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        self.solution.append(
            "COMMENT_%d_steps_666_reduced_to_555"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

    def stage_t_centers(self):
        """
        Used by RubiksCubeNNNEven.make_plus_sign
        """
        # phase 1
        # stage the LR inner-x centers and pair the LR oblique edges
        tmp_solution_len = len(self.solution)
        self.lt_LR_oblique_edge_stage.solve_via_c(use_kociemba_string=True)
        self.print_cube(
            "%s: LR oblique edges paired but not staged (%d steps in)"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        self.solution.append(
            "COMMENT_%d_steps_666_LR_oblique_edges_paired"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        # phase 2
        # Stage LR t-centers via 555
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        tmp_solution_len = len(self.solution)
        fake_555.lt_LR_t_centers_stage_ida.solve_via_c()

        for step in fake_555.solution:
            self.rotate(step)

        self.print_cube(
            "%s: LR t-centers staged (%d steps in)" % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        self.solution.append(
            "COMMENT_%d_steps_666_LR_t_centers_staged"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        # phase 3
        # stage the UD oblique edges and inner x-centers
        tmp_solution_len = len(self.solution)
        self.lt_UD_oblique_edge_inner_x_center_stage.solve_via_c()
        self.print_cube(
            "%s: UD oblique edges and inner x-centers staged (%d steps in)"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        self.solution.append(
            "COMMENT_%d_steps_666_UD_oblique_edges_inner_x_centers_staged"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

    def stage_centers(self):
        """
        Things I have tried here that did not work
        - pair LR inner x-centers and pair oblique edges
        - stage LR
        - stage all of UD in a single phase. This is a 12870^4 search space though and even with six (yes six) 12870^2
            (165 million entry) perfect-hash tables the IDA ran overnight before I killed it.
        """
        if not self.LR_centers_staged():
            # phase 1
            # stage the LR inner-x centers and pair the LR oblique edges
            tmp_solution_len = len(self.solution)
            self.lt_LR_oblique_edge_stage.solve_via_c(use_kociemba_string=True)
            self.print_cube(
                "%s: LR oblique edges paired but not staged (%d steps in)"
                % (self, self.get_solution_len_minus_rotates(self.solution))
            )
            self.solution.append(
                "COMMENT_%d_steps_666_LR_oblique_edges_paired"
                % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
            )

            # phase 2
            # Stage LR centers via 555
            fake_555 = self.get_fake_555()
            self.populate_fake_555_for_ULFRBD_solve()
            tmp_solution_len = len(self.solution)
            fake_555.group_centers_stage_LR()

            for step in fake_555.solution:
                self.rotate(step)

            self.print_cube(
                "%s: LR centers staged (%d steps in)" % (self, self.get_solution_len_minus_rotates(self.solution))
            )

        if not self.UD_centers_staged():
            # phase 3
            # pair the UD oblique edges and outer x-centers
            tmp_solution_len = len(self.solution)
            self.lt_UD_oblique_edge_inner_x_center_stage.solve_via_c()
            self.print_cube(
                "%s: UD oblique edges and inner x-centers staged (%d steps in)"
                % (self, self.get_solution_len_minus_rotates(self.solution))
            )
            self.solution.append(
                "COMMENT_%d_steps_666_UD_oblique_edges_inner_x_centers_staged"
                % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
            )

            # phase 4
            # Stage UD centers via 555
            fake_555 = self.get_fake_555()
            self.populate_fake_555_for_ULFRBD_solve()
            tmp_solution_len = len(self.solution)
            fake_555.group_centers_stage_UD()

            for step in fake_555.solution:
                self.rotate(step)

            self.print_cube(
                "%s: UD centers staged (%d steps in)" % (self, self.get_solution_len_minus_rotates(self.solution))
            )

    def reduce_555(self):

        if self.reduced_to_555():
            return

        self.lt_init()
        self.stage_centers()
        self.daisy_solve_centers()
        self.pair_inside_edges_via_444()


def rotate_666(cube, step):
    return [cube[x] for x in swaps_666[step]]
