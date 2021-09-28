# standard libraries
import logging
import sys

# rubiks cube libraries
from rubikscubennnsolver import reverse_steps
from rubikscubennnsolver.LookupTable import LookupTable
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube444Misc import highlow_edge_mapping_combinations
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

corners_666 = (
    1, 6, 31, 36,
    37, 42, 67, 72,
    73, 78, 103, 108,
    109, 114, 139, 144,
    145, 150, 175, 180,
    181, 186, 211, 216,
)

inner_x_centers_666 = (
    15, 16, 21, 22,  # Upper
    51, 52, 57, 58,  # Left
    87, 88, 93, 94,  # Front
    123, 124, 129, 130,  # Right
    159, 160, 165, 166,  # Back
    195, 196, 201, 202,  # Down
)

outer_x_centers_666 = (
    8, 11, 26, 29,
    44, 47, 62, 65,
    80, 83, 98, 101,
    116, 119, 134, 137,
    152, 155, 170, 173,
    188, 191, 206, 209,
)

centers_666 = (
    8, 9, 10, 11, 14, 15, 16, 17, 20, 21, 22, 23, 26, 27, 28, 29,  # Upper
    44, 45, 46, 47, 50, 51, 52, 53, 56, 57, 58, 59, 62, 63, 64, 65,  # Left
    80, 81, 82, 83, 86, 87, 88, 89, 92, 93, 94, 95, 98, 99, 100, 101,  # Front
    116, 117, 118, 119, 122, 123, 124, 125, 128, 129, 130, 131, 134, 135, 136, 137,  # Right
    152, 153, 154, 155, 158, 159, 160, 161, 164, 165, 166, 167, 170, 171, 172, 173,  # Back
    188, 189, 190, 191, 194, 195, 196, 197, 200, 201, 202, 203, 206, 207, 208, 209,  # Down
)

oblique_edges_666 = (
    9, 10, 14, 17, 20, 23, 27, 28,  # Upper
    45, 46, 50, 53, 56, 59, 63, 64,  # Left
    81, 82, 86, 89, 92, 95, 99, 100,  # Front
    117, 118, 122, 125, 128, 131, 135, 136,  # Right
    153, 154, 158, 161, 164, 167, 171, 172,  # Back
    189, 190, 194, 197, 200, 203, 207, 208,  # Down
)

left_oblique_edges_666 = (
    9, 17, 28, 20,
    45, 53, 64, 56,
    81, 89, 100, 92,
    117, 125, 136, 128,
    153, 161, 172, 164,
    189, 197, 208, 200,
)

right_oblique_edges_666 = (
    10, 23, 27, 14,
    46, 59, 63, 50,
    82, 95, 99, 86,
    118, 131, 135, 122,
    154, 167, 171, 158,
    190, 203, 207, 194,
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
    Use an "unpaired oblique edges" heuristic to get the LR oblique edges paired anywhere.
    We do not need these obliques to be placed on sides LR at this point.
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
                "3Lw", "3Lw'",
                "3Rw", "3Rw'",
            ),
            centers_only=True,
            prune_tables=[],
            C_ida_type="6x6x6-LR-oblique-edges-stage",
        )
        # fmt: on

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in oblique_edges_666:
                if self.parent.state[x] == "L" or self.parent.state[x] == "R":
                    self.parent.state[x] = "L"
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


class LookupTable666LRObliquEdgeStageInnerXStage(LookupTableIDAViaGraph):
    """
    Use the inner-x-centers table to pair the LR inner-x-centers while using an "unpaired oblique edges" heuristic
    to get the LR oblique edges paired anywhere.  We do not need these obliques to be placed on sides
    LR at this point.
    """

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
            C_ida_type="6x6x6-LR-oblique-edges-inner-x-centers-stage",
        )
        # fmt: on

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in oblique_edges_666 or x in inner_x_centers_666:
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
            centers_only=True,
            prune_tables=[
                parent.lt_UD_inner_x_centers_stage,
            ],
            C_ida_type="6x6x6-UD-oblique-edges-inner-x-centers-stage",
        )
        # fmt: on

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in oblique_edges_666 or x in inner_x_centers_666:
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
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step11-UD-left-oblique-stage.txt",
            self.state_targets,
            linecount=12870,
            max_depth=9,
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
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

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
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step12-UD-right-oblique-stage.txt",
            self.state_targets,
            linecount=12870,
            max_depth=9,
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
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

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
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step13-UD-outer-x-centers-stage.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=7,
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
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join(["U" if parent_state[x] in ("U", "D") else "x" for x in UFBD_outer_x_centers_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UFBD_outer_x_centers_666, state):
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
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            filename="lookup-table-6x6x6-step14-UD-oblique-stage.txt",
            state_target=self.state_targets,
            linecount=165636900,
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
            ),
            prune_tables=(
                parent.lt_UD_left_oblique_edges_stage,
                parent.lt_UD_right_oblique_edges_stage,
            ),
        )
        # fmt: on
'''


class LookupTableIDA666UDCentersStage(LookupTableIDAViaGraph):
    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
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
            ),
            prune_tables=(
                parent.lt_UD_left_oblique_edges_stage,
                parent.lt_UD_right_oblique_edges_stage,
                parent.lt_UD_outer_x_centers_stage,
            ),
            perfect_hash01_filename="lookup-table-6x6x6-step14-UD-oblique-stage.pt-state-perfect-hash",
            pt1_state_max=12870,
            centers_only=True,
        )
        # fmt: on


# phase 5
class LookupTable666Step50LRCenters(LookupTable):
    """
    lookup-table-6x6x6-step50-LR-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    0 steps has 9 entries (0 percent, 0.00x previous step)
    1 steps has 189 entries (0 percent, 21.00x previous step)
    2 steps has 748 entries (0 percent, 3.96x previous step)
    3 steps has 2,914 entries (0 percent, 3.90x previous step)
    4 steps has 12,388 entries (3 percent, 4.25x previous step)
    5 steps has 44,604 entries (13 percent, 3.60x previous step)
    6 steps has 109,148 entries (31 percent, 2.45x previous step)
    7 steps has 132,424 entries (38 percent, 1.21x previous step)
    8 steps has 37,920 entries (11 percent, 0.29x previous step)
    9 steps has 2,624 entries (0 percent, 0.07x previous step)
    10 steps has 32 entries (0 percent, 0.01x previous step)

    Total: 343,000 entries
    Average: 6.39 moves
    """

    # fmt: off
    state_targets = (
        "LLLLLLLLLLLLxxxxxxxxxxxx",
        "LLLLLLLLLLxxLLxxxxxxxxxx",
        "LLLLLLLLLLxxxxxxxxxxxxLL",
        "LLLLLxLLLxLLxxLxxxLxxxxx",
        "LLLLLxLLLxLLxxxxxLxxxLxx",
        "LLLLLxLLLxxxLLLxxxLxxxxx",
        "LLLLLxLLLxxxLLxxxLxxxLxx",
        "LLLLLxLLLxxxxxLxxxLxxxLL",
        "LLLLLxLLLxxxxxxxxLxxxLLL",
        "LLxLLLxLLLLLxxLxxxLxxxxx",
        "LLxLLLxLLLLLxxxxxLxxxLxx",
        "LLxLLLxLLLxxLLLxxxLxxxxx",
        "LLxLLLxLLLxxLLxxxLxxxLxx",
        "LLxLLLxLLLxxxxLxxxLxxxLL",
        "LLxLLLxLLLxxxxxxxLxxxLLL",
        "LLxLLxxLLxLLxxLxxLLxxLxx",
        "LLxLLxxLLxxxLLLxxLLxxLxx",
        "LLxLLxxLLxxxxxLxxLLxxLLL",
        "xxLLLLLLLLLLLLxxxxxxxxxx",
        "xxLLLLLLLLLLxxxxxxxxxxLL",
        "xxLLLLLLLLxxLLxxxxxxxxLL",
        "xxLLLxLLLxLLLLLxxxLxxxxx",
        "xxLLLxLLLxLLLLxxxLxxxLxx",
        "xxLLLxLLLxLLxxLxxxLxxxLL",
        "xxLLLxLLLxLLxxxxxLxxxLLL",
        "xxLLLxLLLxxxLLLxxxLxxxLL",
        "xxLLLxLLLxxxLLxxxLxxxLLL",
        "xxxLLLxLLLLLLLLxxxLxxxxx",
        "xxxLLLxLLLLLLLxxxLxxxLxx",
        "xxxLLLxLLLLLxxLxxxLxxxLL",
        "xxxLLLxLLLLLxxxxxLxxxLLL",
        "xxxLLLxLLLxxLLLxxxLxxxLL",
        "xxxLLLxLLLxxLLxxxLxxxLLL",
        "xxxLLxxLLxLLLLLxxLLxxLxx",
        "xxxLLxxLLxLLxxLxxLLxxLLL",
        "xxxLLxxLLxxxLLLxxLLxxLLL"
    )

    LR_inner_x_centers_oblique_edges_666 = (
        45, 46, 50, 51, 52, 53, 56, 57, 58, 59, 63, 64,  # Left
        117, 118, 122, 123, 124, 125, 128, 129, 130, 131, 135, 136,  # Right
    )

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step50-LR-solve-inner-x-center-and-oblique-edges.txt",
            self.state_targets,
            linecount=343000,
            max_depth=8,
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
                "Dw", "Dw'"
            ),
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["L" if self.parent.state[x] == "L" else "x" for x in self.LR_inner_x_centers_oblique_edges_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_inner_x_centers_oblique_edges_666, state):
            cube[pos] = pos_state


class LookupTable666Step50HighLowEdges(LookupTable):
    """
    lookup-table-6x6x6-step51-highlow-edges.txt
    ===========================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
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

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step51-highlow-edges.txt",
            "UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
            linecount=2704156,
            max_depth=8,
            all_moves=moves_666,
            # fmt: off
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
                "Dw", "Dw'"
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self) -> str:
        """
        Returns:
            the state of the cube per this lookup table
        """
        self.parent.populate_fake_444_for_inner_x_centers_stage()
        self.parent.fake_444.edge_mapping = self.parent.edge_mapping
        return self.parent.fake_444.lt_phase2_edges.state()

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ["x"]
        self.parent.state.extend(
            list(
                "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
            )
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()

        for step in steps_to_scramble:
            self.parent.rotate(step)


class LookupTableIDA666Step50(LookupTableIDAViaGraph):
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
                "Dw", "Dw'"
            ),
            prune_tables=(
                parent.lt_LR_centers,
                parent.lt_LR_highlow_edges,
            ),
        )
        # fmt: on


class LookupTableIDA666Step50WithoutEdges(LookupTableIDAViaGraph):
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
                "Dw", "Dw'"
            ),
            prune_tables=(
                parent.lt_LR_centers,
            ),
            centers_only=True,
        )
        # fmt: on


# phase 6
class LookupTable666UDInnerXCenterAndObliqueEdges(LookupTable):
    """
    lookup-table-6x6x6-step61-UD-solve-inner-x-center-and-oblique-edges.txt
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
        "DDDUUDDUUDDDUUUDDUUDDUUU",
        "UUUUUUUUUUUUDDDDDDDDDDDD",
    )

    UD_inner_x_centers_oblique_edges = (
        9, 10, 14, 15, 16, 17, 20, 21, 22, 23, 27, 28,  # Upper
        189, 190, 194, 195, 196, 197, 200, 201, 202, 203, 207, 208,  # Down
    )
    # fmt: on

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step61-UD-solve-inner-x-center-and-oblique-edges.txt",
            self.state_targets,
            linecount=343000,
            max_depth=11,
            all_moves=moves_666,
            # fmt: off
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
                "3Uw2",
                "3Dw2",
                "3Fw2",
                "3Bw2",
                "L", "L'",
                "R", "R'"
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        return "".join([self.parent.state[x] for x in self.UD_inner_x_centers_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_inner_x_centers_oblique_edges, state):
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

    # fmt: off
    state_targets = (
        "BBBFFBBFFBBBFFFBBFFBBFFF",
        "FFFFFFFFFFFFBBBBBBBBBBBB",
    )

    FB_inner_x_centers_oblique_edges = (
        81, 82, 86, 87, 88, 89, 92, 93, 94, 95, 99, 100,  # Front
        153, 154, 158, 159, 160, 161, 164, 165, 166, 167, 171, 172,  # Back
    )
    # fmt: on

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt",
            self.state_targets,
            linecount=343000,
            max_depth=11,
            all_moves=moves_666,
            # fmt: off
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
                "3Uw2",
                "3Dw2",
                "3Fw2",
                "3Bw2",
                "L", "L'",
                "R", "R'"
            ),
            # fmt: on
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


class LookupTable666LRObliqueEdges(LookupTable):
    """
    lookup-table-6x6x6-step63-LR-oblique-edges.txt
    ==============================================
    0 steps has 2 entries (0 percent, 0.00x previous step)
    1 steps has 12 entries (0 percent, 6.00x previous step)
    2 steps has 96 entries (0 percent, 8.00x previous step)
    3 steps has 728 entries (0 percent, 7.58x previous step)
    4 steps has 3,446 entries (1 percent, 4.73x previous step)
    5 steps has 10,036 entries (5 percent, 2.91x previous step)
    6 steps has 26,472 entries (15 percent, 2.64x previous step)
    7 steps has 44,832 entries (25 percent, 1.69x previous step)
    8 steps has 41,312 entries (23 percent, 0.92x previous step)
    9 steps has 32,560 entries (18 percent, 0.79x previous step)
    10 steps has 15,176 entries (8 percent, 0.47x previous step)
    11 steps has 1,728 entries (0 percent, 0.11x previous step)

    Total: 176,400 entries
    Average: 7.56 moves
    """

    # fmt: off
    state_targets = (
        "UUUULLLLLLLLFFFFRRRRRRRRBBBBDDDD",
        "UUUURRRRRRRRFFFFLLLLLLLLBBBBDDDD",
    )

    LR_oblique_edges_UFBD_inner_x_centers = (
        15, 16, 21, 22,  # Upper
        45, 46, 50, 53, 56, 59, 63, 64,  # Left
        87, 88, 93, 94,  # Front
        117, 118, 122, 125, 128, 131, 135, 136,  # Right
        159, 160, 165, 166,  # Back
        195, 196, 201, 202,  # Down
    )
    # fmt: on

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step63-LR-oblique-edges.txt",
            self.state_targets,
            linecount=176400,
            max_depth=11,
            all_moves=moves_666,
            # fmt: off
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
                "3Uw2",
                "3Dw2",
                "3Fw2",
                "3Bw2",
                "L", "L'",
                "R", "R'"
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_oblique_edges_UFBD_inner_x_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_oblique_edges_UFBD_inner_x_centers, state):
            cube[pos] = pos_state


class LookupTableIDA666UFBDInnerXCenterAndObliqueEdges(LookupTableIDAViaGraph):
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
                "3Uw2",
                "3Dw2",
                "3Fw2",
                "3Bw2",
                "L", "L'",
                "R", "R'"
            ),
            prune_tables=(
                parent.lt_UD_solve_inner_x_centers_and_oblique_edges,
                parent.lt_FB_solve_inner_x_centers_and_oblique_edges,
                parent.lt_LR_oblique_edges,
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

    def get_fake_444(self):
        if self.fake_444 is None:
            self.fake_444 = RubiksCube444(solved_444, "URFDLB")
            self.fake_444.lt_init()
            self.fake_444.enable_print_cube = False
        else:
            self.fake_444.re_init()
        return self.fake_444

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
        self._sanity_check("edge-orbit-0", edge_orbit_0, 8)
        self._sanity_check("edge-orbit-1", edge_orbit_1, 8)
        self._sanity_check("corners", corners_666, 4)
        self._sanity_check("left-oblique", left_oblique_edges_666, 4)
        self._sanity_check("right-oblique", right_oblique_edges_666, 4)
        self._sanity_check("outside x-center", outer_x_centers_666, 4)
        self._sanity_check("inside x-center", inner_x_centers_666, 4)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # phase 1
        self.lt_LR_inner_x_centers_stage = LookupTable666LRInnerXCentersStage(self)
        self.lt_LR_oblique_edge_stage_inner_x_stage = LookupTable666LRObliquEdgeStageInnerXStage(self)

        # phase 2
        self.lt_LR_oblique_edge_stage = LookupTable666LRObliquEdgeStage(self)
        self.lt_UD_inner_x_centers_stage = LookupTable666UDInnerXCentersStage(self)
        self.lt_UD_outer_x_centers_stage = LookupTable666UDXCentersStage(self)
        self.lt_UD_left_oblique_edges_stage = LookupTable666UDLeftObliqueCentersStage(self)
        self.lt_UD_right_oblique_edges_stage = LookupTable666UDRightObliqueCentersStage(self)

        # phase 3
        self.lt_UD_oblique_edge_stage = LookupTable666UDObliquEdgeStage(self)
        self.lt_UD_oblique_edge_stage.avoid_oll = (0, 1)
        self.lt_UD_oblique_edge_inner_x_center_stage = LookupTable666UDObliquEdgeInnerXCentersStage(self)
        self.lt_UD_oblique_edge_inner_x_center_stage.avoid_oll = (0, 1)

        # phase 4
        self.lt_UD_left_oblique_edges_stage = LookupTable666UDLeftObliqueStage(self)
        self.lt_UD_right_oblique_edges_stage = LookupTable666UDRightObliqueStage(self)
        self.lt_UD_outer_x_centers_stage = LookupTable666UDOuterXCenterStage(self)
        self.lt_UD_centers_stage = LookupTableIDA666UDCentersStage(self)
        self.lt_UD_centers_stage.avoid_oll = (0, 1)

        # phase 5
        self.lt_LR_centers = LookupTable666Step50LRCenters(self)
        self.lt_LR_highlow_edges = LookupTable666Step50HighLowEdges(self)
        self.lt_step50 = LookupTableIDA666Step50(self)
        self.lt_step50_without_edges = LookupTableIDA666Step50WithoutEdges(self)

        # phase 6
        self.lt_UD_solve_inner_x_centers_and_oblique_edges = LookupTable666UDInnerXCenterAndObliqueEdges(self)
        self.lt_FB_solve_inner_x_centers_and_oblique_edges = LookupTable666FBInnerXCenterAndObliqueEdges(self)
        self.lt_LR_oblique_edges = LookupTable666LRObliqueEdges(self)
        self.lt_UFBD_solve_inner_x_centers_and_oblique_edges = LookupTableIDA666UFBDInnerXCenterAndObliqueEdges(self)

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

    def daisy_solve_centers_eo_edges(self):
        """
        The inner x-centers and oblique edges are staged. Daisy solve the centers so that our
        centers are reduced to 555 while also EOing the inside orbit of edges.

        Thoughts on other ways to tackle this problem:
        - There are 70^3 per side so to do this in one phase would be a 70^9 search space which is unrealistic.
        """

        # phase 5
        # - put LR centers such that they can be solved with L L' R R'
        # - EO the inside oribit of edges to prep for the 444 solver to pair those edges
        original_state = self.state[:]
        original_solution = self.solution[:]
        tmp_solution_len = len(self.solution)
        pt_state_indexes_to_edge_mapping = {}

        # try all 2048 edge mappings
        for edges_to_flip_sets in highlow_edge_mapping_combinations.values():
            for edge_mapping in edges_to_flip_sets:
                self.state = original_state[:]
                self.solution = original_solution[:]
                self.edge_mapping = edge_mapping
                pt_state_indexes_to_edge_mapping[
                    tuple([pt.state_index() for pt in self.lt_step50.prune_tables])
                ] = edge_mapping

        self.state = original_state[:]
        self.solution = original_solution[:]
        phase5_solutions = self.lt_step50.solutions_via_c(
            pt_states=pt_state_indexes_to_edge_mapping.keys(), solution_count=1
        )

        phase5_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) = phase5_solutions[0]
        self.edge_mapping = pt_state_indexes_to_edge_mapping[(pt0_state, pt1_state)]

        for step in phase5_solution:
            self.rotate(step)

        self.print_cube_add_comment("LR centers reduced to 555, EOed inside edges", tmp_solution_len)

        # phase 6
        # solve the UD inner x-centers, pair the UD oblique edges and daisy solve UD
        # solve the FB inner x-centers, pair the FB oblique edges and daisy solve FB
        # daisy solve LR
        # this takes ~14 steps
        tmp_solution_len = len(self.solution)
        self.lt_UFBD_solve_inner_x_centers_and_oblique_edges.solve_via_c()
        self.print_cube_add_comment("UD FB centers reduced to 555", tmp_solution_len)

    def daisy_solve_centers(self):
        """
        The inner x-centers and oblique edges are staged. Daisy solve the centers so that our
        centers are reduced to 555.
        """

        # phase 5
        # - put LR centers such that they can be solved with L L' R R'
        tmp_solution_len = len(self.solution)
        self.lt_step50_without_edges.solve_via_c()
        self.print_cube_add_comment("LR centers reduced to 5x5x5", tmp_solution_len)

        # phase 6
        # solve the UD inner x-centers, pair the UD oblique edges and daisy solve UD
        # solve the FB inner x-centers, pair the FB oblique edges and daisy solve FB
        # daisy solve LR
        # this takes ~14 steps
        tmp_solution_len = len(self.solution)
        self.lt_UFBD_solve_inner_x_centers_and_oblique_edges.solve_via_c()
        self.print_cube_add_comment("UD FB centers reduced to 5x5x5", tmp_solution_len)

    def stage_t_centers(self):
        """
        Used by RubiksCubeNNNEven.make_plus_sign

        - pair LR inner x-centers and pair oblique edges (9 moves)
        - stage LR t-centers (6 moves)
        - stage the UD oblique edges and inner x-centers
        """
        # phase 1 - stage the LR inner-x centers and pair the LR oblique edges
        tmp_solution_len = len(self.solution)
        self.lt_LR_oblique_edge_stage_inner_x_stage.solve_via_c(use_kociemba_string=True)
        self.print_cube_add_comment("LR inner x-centers staged, oblique edges paired", tmp_solution_len)

        # phase 2 - Stage LR t-centers via 555
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        tmp_solution_len = len(self.solution)
        fake_555.lt_LR_t_centers_stage_ida.solve_via_c()

        for step in fake_555.solution:
            if not step.startswith("COMMENT"):
                self.rotate(step)

        self.print_cube_add_comment("LR t-centers staged", tmp_solution_len)

        # phase 3 - stage the UD oblique edges and inner x-centers
        tmp_solution_len = len(self.solution)
        self.lt_UD_oblique_edge_inner_x_center_stage.solve_via_c()
        self.print_cube_add_comment("UD t-centers staged", tmp_solution_len)

    def stage_centers(self):
        """
        option A (original strategy)
        - pair all inner x-centers via 444 (9 moves)
        - pair LR oblique edges (9 moves)
        - stage LR (10 moves)
        - stage UD (14 moves)
        - 42 total

        option B (what we use today)
        - pair LR inner x-centers and oblique edges (9 moves)
        - stage LR (10 moves)
        - pair UD inner x-centers and oblique edges (9 moves)
        - stage UD (10 moves)
        - 38 total
        The downside here is the "pair LR inner x-centers and pair oblique edges" phase is pretty slow
        because it is using an unpaired count heuristic.

        Things I have tried here that did not work

        3 phases
        - pair LR inner x-centers and pair oblique edges (9 moves)
        - stage LR (10 moves)
        - stage all of UD in a single phase. This is a 12870^4 search space though and even with
            six (yes six) 12870^2 (165 million entry) perfect-hash tables the IDA ran overnight
            before I killed it.

        Things to try:
        - pair LR inner x-centers and oblique edges (9 moves)
        - stage LR while staging the UDFB inner x-centers? (at least 10 moves)
            - similar to 555 stage LR phase
            - would also stage UDFB inner x-centers which is a 16!/(8! * 8!) or 12870 space
            - would have to avoid any 3w move that would break up an LR obilque edge
            - this would be super slow...735741/(735741*735741*12870) = 0.000 000 000 105
            - not feasible
        - stage UD (14 moves)
        - 33 plus the rest of the moves for the 2nd phase
        """
        use_option_A = False

        if use_option_A:
            # phase 1 - stage the inner-x centers via 444 solver
            fake_444 = self.get_fake_444()
            self.populate_fake_444_for_inner_x_centers_stage()
            tmp_solution_len = len(self.solution)
            fake_444.lt_ULFRBD_centers_stage.solve_via_c()

            for step in fake_444.solution:
                if not step.startswith("COMMENT"):
                    if "w" in step:
                        step = "3" + step
                    self.rotate(step)

            self.print_cube_add_comment("inner x-centers staged", tmp_solution_len)

            # phase 2 - pair LR oblique edges (5 or 6 moves)
            self.lt_LR_oblique_edge_stage.solve_via_c(use_kociemba_string=True)
            self.print_cube_add_comment("LR oblique edges paired", tmp_solution_len)

            # phase 3 - Stage LR centers via 555
            fake_555 = self.get_fake_555()
            self.populate_fake_555_for_ULFRBD_solve()
            tmp_solution_len = len(self.solution)
            fake_555.group_centers_stage_LR()

            for step in fake_555.solution:
                if not step.startswith("COMMENT"):
                    self.rotate(step)

            self.print_cube_add_comment("LR centers staged", tmp_solution_len)

            # phase 4 - pair the UD oblique edges and outer x-centers to finish staging centers
            tmp_solution_len = len(self.solution)
            self.lt_UD_centers_stage.solve_via_c()
            self.print_cube_add_comment("UD centers staged", tmp_solution_len)

        else:

            if not self.LR_centers_staged():
                # phase 1 - stage the LR inner-x centers and pair the LR oblique edges
                tmp_solution_len = len(self.solution)
                self.lt_LR_oblique_edge_stage_inner_x_stage.solve_via_c(use_kociemba_string=True)
                self.print_cube_add_comment("LR inner x-centers staged, oblique edges paired", tmp_solution_len)

                # phase 2 - Stage LR centers via 555
                fake_555 = self.get_fake_555()
                self.populate_fake_555_for_ULFRBD_solve()
                tmp_solution_len = len(self.solution)
                fake_555.group_centers_stage_LR()

                for step in fake_555.solution:
                    if not step.startswith("COMMENT"):
                        self.rotate(step)

                self.print_cube_add_comment("LR centers staged", tmp_solution_len)

            if not self.UD_centers_staged():
                # phase 3 - stage the UD inner-x centers and pair the UD oblique edges
                tmp_solution_len = len(self.solution)
                self.lt_UD_oblique_edge_stage.solve_via_c(use_kociemba_string=True)
                self.print_cube_add_comment("UD inner x-centers staged, oblique edges paired", tmp_solution_len)

                # phase 4 - Stage UD centers via 555
                fake_555 = self.get_fake_555()
                self.populate_fake_555_for_ULFRBD_solve()
                tmp_solution_len = len(self.solution)
                fake_555.group_centers_stage_UD()

                for step in fake_555.solution:
                    if not step.startswith("COMMENT"):
                        self.rotate(step)

                self.print_cube_add_comment("UD centers staged", tmp_solution_len)

    def reduce_555(self):

        if self.reduced_to_555():
            return

        self.lt_init()
        self.stage_centers()
        self.daisy_solve_centers_eo_edges()
        self.pair_inside_edges_via_444()


def rotate_666(cube, step):
    return [cube[x] for x in swaps_666[step]]
