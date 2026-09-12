"""
7x7x7 solver: reduce the cube to a 5x5x5, then finish with the 5x5x5 solver.

A 7x7x7 has 25 centers per face (t-centers, x-centers, and three orbits of
oblique edges) plus three orbits of wings. Reduction stages and daisy-solves
the centers so the remaining puzzle is a 5x5x5. ``RubiksCube777.reduce_555``
does that reduction; ``group_edges`` (via the 5x5x5 solver) then pairs the
wings and ``solve_333`` finishes the cube.

Most of the early work is delegated to a fake 5x5x5 whose inner 3x3 of centers
is filled from this cube. Oblique pairing has no lookup table: a C search uses
an unpaired-count heuristic.

Phase 1 - stage LR inner centers
    Map the inner 3x3 of each face onto a fake 5x5x5 and stage its LR centers.

Phase 2 - stage UD inner centers and pair LR oblique edges
    Stage the U/D inner t- and x-centers with a ranked table while pairing
    every L/R oblique orbit anywhere. The obliques use an unpaired-count
    heuristic and do not need to land on L/R.

Phase 3 - stage the remaining LR centers
    Map the outer 5x5 of each face onto a fake 5x5x5 and stage its LR centers.

Phase 5/6 - stage UD outer x-centers and pair UD obliques
    Ranked pairwise tables over the UFBD outer-x, left, middle, and right
    oblique coordinates. The middle obliques are the outer t-centers, so this
    also stages the remaining UD centers.

Phase 7 - daisy-solve UD, LR, and FB centers
    One ranked IDA over five C(8,4) orbits per axis, ignoring outer-x.
    Perfect 70^5 tables are used; leave-one-out 70^4 tables remain as a fallback.
    The remaining puzzle is a 5x5x5.
"""

# standard libraries
import logging
import subprocess

# rubiks cube libraries
from rubikscubennnsolver.LookupTable import LookupTable, download_file_if_needed
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.misc import SolveError
from rubikscubennnsolver.RubiksCubeNNNOddEdges import RubiksCubeNNNOddEdges
from rubikscubennnsolver.swaps import swaps_777

logger = logging.getLogger(__name__)


# fmt: off
moves_777 = (
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

solved_777 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

centers_777 = (
    9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41,  # Upper
    58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90,  # Left
    107, 108, 109, 110, 111, 114, 115, 116, 117, 118, 121, 122, 123, 124, 125, 128, 129, 130, 131, 132, 135, 136, 137, 138, 139,  # Front
    156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188,  # Right
    205, 206, 207, 208, 209, 212, 213, 214, 215, 216, 219, 220, 221, 222, 223, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237,  # Back
    254, 255, 256, 257, 258, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 282, 283, 284, 285, 286,  # Down
)

outer_x_centers_777 = (
    9, 13, 37, 41,  # Upper
    58, 62, 86, 90,  # Left
    107, 111, 135, 139,  # Front
    156, 160, 184, 188,  # Right
    205, 209, 233, 237,  # Back
    254, 258, 282, 286,  # Down
)

UFBD_outer_x_centers_777 = (
    9, 13, 37, 41,  # Upper
    107, 111, 135, 139,  # Front
    205, 209, 233, 237,  # Back
    254, 258, 282, 286,  # Down
)

inner_x_centers_777 = (
    17, 19, 31, 33,  # Upper
    66, 68, 80, 82,  # Left
    115, 117, 129, 131,  # Front
    164, 166, 178, 180,  # Right
    213, 215, 227, 229,  # Back
    262, 264, 276, 278,  # Down
)

outer_t_centers_777 = (
    11, 23, 27, 39,  # Upper
    60, 72, 76, 88,  # Left
    109, 121, 125, 137,  # Front
    158, 170, 174, 186,  # Right
    207, 219, 223, 235,  # Back
    256, 268, 272, 284,  # Down
)

inner_t_centers_777 = (
    18, 24, 26, 32,  # Upper
    67, 73, 75, 81,  # Left
    116, 122, 124, 130,  # Front
    165, 171, 173, 179,  # Right
    214, 220, 222, 228,  # Back
    263, 269, 271, 277,  # Down
)

middle_centers_777 = (
    25, 74, 123, 172, 221, 270,
)

corners_777 = (
    1, 7, 43, 49,  # Upper
    50, 56, 92, 98,  # Left
    99, 105, 141, 147,  # Front
    148, 154, 190, 196,  # Right
    197, 203, 239, 245,  # Back
    246, 252, 288, 294,  # Down
)

left_oblique_edges_777 = (
    10, 20, 30, 40,  # Upper
    59, 69, 79, 89,  # Left
    108, 118, 128, 138,  # Front
    157, 167, 177, 187,  # Right
    206, 216, 226, 236,  # Back
    255, 265, 275, 285,  # Down
)

right_oblique_edges_777 = (
    12, 16, 34, 38,  # Upper
    61, 65, 83, 87,  # Left
    110, 114, 132, 136,  # Front
    159, 163, 181, 185,  # Right
    208, 212, 230, 234,  # Back
    257, 261, 279, 283,  # Down
)

edge_orbit_0_777 = (
    2, 6, 14, 42, 48, 44, 36, 8,  # Upper
    51, 55, 63, 91, 97, 93, 85, 57,  # Left
    100, 104, 112, 140, 146, 142, 134, 106,  # Front
    149, 153, 161, 189, 195, 191, 183, 155,  # Right
    198, 202, 210, 238, 244, 240, 232, 204,  # Back
    247, 251, 259, 287, 293, 289, 281, 253,  # Down
)

edge_orbit_1_777 = (
    3, 5, 21, 35, 47, 45, 29, 15,  # Upper
    52, 54, 70, 84, 96, 94, 78, 64,  # Left
    101, 103, 119, 133, 145, 143, 127, 113,  # Front
    150, 152, 168, 182, 194, 192, 176, 162,  # Right
    199, 201, 217, 231, 243, 241, 225, 211,  # Back
    248, 250, 266, 280, 292, 290, 274, 260,  # Down
)

edge_orbit_2_777 = (
    4, 28, 46, 22,  # Upper
    53, 77, 95, 71,  # Left
    102, 126, 144, 120,  # Front
    151, 175, 193, 169,  # Right
    200, 224, 242, 218,  # Back
    249, 273, 291, 267,  # Down
)

LR_centers_777 = (
    58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90,  # Left
    156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188,  # Right
)

ULRD_centers_777 = (
    9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41,  # Upper
    58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90,  # Left
    156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188,  # Right
    254, 255, 256, 257, 258, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 282, 283, 284, 285, 286,  # Down
)

UFBD_inner_t_centers_777 = (
    18, 24, 26, 32,  # Upper
    116, 122, 124, 130,  # Front
    214, 220, 222, 228,  # Back
    263, 269, 271, 277,  # Down
)

UFBD_inner_x_centers_777 = (
    17, 19, 31, 33,  # Upper
    115, 117, 129, 131,  # Front
    213, 215, 227, 229,  # Back
    262, 264, 276, 278,  # Down
)

UD_inside_centers_777 = (
    17, 18, 19, 24, 25, 26, 31, 32, 33,  # Upper
    262, 263, 264, 269, 270, 271, 276, 277, 278,  # Down
)

UFBD_left_oblique_777 = (
    10, 20, 30, 40,  # Upper
    108, 118, 128, 138,  # Front
    206, 216, 226, 236,  # Back
    255, 265, 275, 285,  # Down
)

UFBD_right_oblique_777 = (
    12, 16, 34, 38,  # Upper
    110, 114, 132, 136,  # Front
    208, 212, 230, 234,  # Back
    257, 261, 279, 283,  # Down
)

UFBD_middle_oblique_777 = (
    11, 23, 27, 39,  # Upper
    109, 121, 125, 137,  # Front
    207, 219, 223, 235,  # Back
    256, 268, 272, 284,  # Down
)

oblique_edges_777 = (
    10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
    59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89,  # Left
    108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  # Front
    157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187,  # Right
    206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  # Back
    255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
)

UFBD_oblique_edges_777 = (
    10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
    108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  # Front
    206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  # Back
    255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
)

# fmt: on


# ==================================================
# phase 2
# pair LR oblique edges
# ==================================================


# fmt: off
LR_OBLIQUE_PAIRING_ILLEGAL_MOVES = (
    "3Uw", "3Uw'",
    "3Dw", "3Dw'",
    "3Fw", "3Fw'",
    "3Bw", "3Bw'",
)

PHASE5_ILLEGAL_MOVES = (
    # keep LR inside centers staged
    "3Uw", "3Uw'",
    "3Dw", "3Dw'",
    "3Fw", "3Fw'",
    "3Bw", "3Bw'",
    "3Lw", "3Lw'",
    "3Rw", "3Rw'",
    # keep LR centers staged
    "Uw", "Uw'",
    "Dw", "Dw'",
    "Fw", "Fw'",
    "Bw", "Bw'",
    # we are not manipulating anything on L or R
    "L", "L'", "L2",
    "R", "R'", "R2",
)

# fmt: on


UD_INNER_CENTERS_STAGE_TABLE_777 = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage.cost-only.bin"


class LookupTableIDA777LRObliqueEdgesUDInnerCentersStage:
    """
    Stage the U/D inner t- and x-centers while pairing the L/R obliques
    anywhere. The center table has (16! / (8! * 8!))^2 = 165,636,900 states.
    """

    def __init__(self, parent):
        self.parent = parent
        self.filename = UD_INNER_CENTERS_STAGE_TABLE_777
        self.avoid_oll = None

    def solve_via_c(self, **_kwargs):
        download_file_if_needed(UD_INNER_CENTERS_STAGE_TABLE_777)
        cmd = [
            "./ida_search_777_centers_stage",
            "--kociemba",
            self.parent.get_kociemba_string(True),
            "--ranked-UD-inner-centers-cost",
            self.filename,
        ]

        if self.avoid_oll is not None:
            orbits_with_oll = self.parent.center_solution_leads_to_oll_parity()
            if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
                cmd.append("--orbit0-need-odd-w" if 0 in orbits_with_oll else "--orbit0-need-even-w")
            if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
                cmd.append("--orbit1-need-odd-w" if 1 in orbits_with_oll else "--orbit1-need-even-w")

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
            returncode = proc.wait()

        output = "".join(lines)
        self.parent.solve_via_c_output = output
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                for step in line.split(":", 1)[1].strip().split():
                    self.parent.rotate(step)
                return

        raise SolveError(f"ida_search_777_centers_stage failed with exit {returncode}\n{output}")

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        inner_centers = UFBD_inner_t_centers_777 + UFBD_inner_x_centers_777
        for x in centers_777:
            if x in inner_centers:
                self.parent.state[x] = "U" if self.parent.state[x] in ("U", "D") else "x"
            elif x in oblique_edges_777:
                self.parent.state[x] = "L" if self.parent.state[x] in ("L", "R") else "x"
            else:
                self.parent.state[x] = "."


# ==================================================
# phase 5
# pair the UD oblique edges via perfect-hash tables
# ==================================================


class LookupTable777Phase5LeftOblique(LookupTable):
    """
    16! / (8! * 8!) = 12,870 states

                   . . . . . . .
                   . . U . . . .
                   . . . . . U .
                   . . . . . . .
                   . U . . . . .
                   . . . . U . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . x . . . .  . . . . . . .  . . x . . . .
    . . . . . . .  . . . . . x .  . . . . . . .  . . . . . x .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . x . . . . .  . . . . . . .  . x . . . . .
    . . . . . . .  . . . . x . .  . . . . . . .  . . . . x . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . U . . . .
                   . . . . . U .
                   . . . . . . .
                   . U . . . . .
                   . . . . U . .
                   . . . . . . .

    lookup-table-7x7x7-phase5-left-oblique.txt
    ==========================================
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

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-phase5-left-oblique.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=9,
            all_moves=moves_777,
            illegal_moves=PHASE5_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_left_oblique_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UFBD_left_oblique_777, state):
            cube[pos] = pos_state


class LookupTable777Phase5RightOblique(LookupTable):
    """
    16! / (8! * 8!) = 12,870 states

                   . . . . . . .
                   . . . . U . .
                   . U . . . . .
                   . . . . . . .
                   . . . . . U .
                   . . U . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . x . .  . . . . . . .  . . . . x . .
    . . . . . . .  . x . . . . .  . . . . . . .  . x . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . x .  . . . . . . .  . . . . . x .
    . . . . . . .  . . x . . . .  . . . . . . .  . . x . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . U . .
                   . U . . . . .
                   . . . . . . .
                   . . . . . U .
                   . . U . . . .
                   . . . . . . .

    lookup-table-7x7x7-phase5-right-oblique.txt
    ===========================================
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

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-phase5-right-oblique.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=9,
            all_moves=moves_777,
            illegal_moves=PHASE5_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_right_oblique_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UFBD_right_oblique_777, state):
            cube[pos] = pos_state


class LookupTable777Phase5MiddleOblique(LookupTable):
    """
    16! / (8! * 8!) = 12,870 states

                   . . . . . . .
                   . . . U . . .
                   . . . . . . .
                   . U . . . U .
                   . . . . . . .
                   . . . U . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . x . . .  . . . . . . .  . . . x . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . x . . . x .  . . . . . . .  . x . . . x .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . x . . .  . . . . . . .  . . . x . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . U . . .
                   . . . . . . .
                   . U . . . U .
                   . . . . . . .
                   . . . U . . .
                   . . . . . . .

    lookup-table-7x7x7-phase5-middle-oblique.txt
    ============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 25 entries (0 percent, 12.50x previous step)
    3 steps has 210 entries (1 percent, 8.40x previous step)
    4 steps has 722 entries (5 percent, 3.44x previous step)
    5 steps has 1,752 entries (13 percent, 2.43x previous step)
    6 steps has 4,033 entries (31 percent, 2.30x previous step)
    7 steps has 4,014 entries (31 percent, 1.00x previous step)
    8 steps has 1,977 entries (15 percent, 0.49x previous step)
    9 steps has 134 entries (1 percent, 0.07x previous step)

    Total: 12,870 entries
    Average: 6.34 moves
    """

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-phase5-middle-oblique.txt",
            "UUUUxxxxxxxxUUUU",
            linecount=12870,
            max_depth=9,
            all_moves=moves_777,
            illegal_moves=PHASE5_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_middle_oblique_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UFBD_middle_oblique_777, state):
            cube[pos] = pos_state


class LookupTableIDA777UDObliqueEdgePairingNew(LookupTableIDAViaGraph):
    """
    Pair the UD oblique edges
    """

    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=PHASE5_ILLEGAL_MOVES,
            prune_tables=(
                parent.lt_phase5_left_oblique,
                parent.lt_phase5_right_oblique,
                parent.lt_phase5_middle_oblique,
            ),
            centers_only=True,
            perfect_hash01_filename="lookup-table-7x7x7-phase5-left-right-oblique.perfect-hash",
            perfect_hash02_filename="lookup-table-7x7x7-phase5-left-middle-oblique.perfect-hash",
            pt1_state_max=12870,
            pt2_state_max=12870,
            C_ida_type="7x7x7-UD-oblique-edges-stage-new",
        )
        # fmt: on


# ==================================================
# phase 5
# pair the UD oblique edges via an unpaired-count heuristic
# ==================================================
# ==================================================
# combined phases 5/6
# stage UD outer x-centers and pair UD obliques
# ==================================================
UD_PHASE56_TABLES_777 = (
    (
        "--left-middle-oblique-cost",
        "lookup-tables/lookup-table-7x7x7-phase5-6-UD-left-middle-oblique-centers-stage.cost-only.bin",
    ),
    (
        "--left-right-oblique-cost",
        "lookup-tables/lookup-table-7x7x7-phase5-6-UD-left-right-oblique-centers-stage.cost-only.bin",
    ),
    (
        "--left-oblique-outer-x-cost",
        "lookup-tables/lookup-table-7x7x7-phase5-6-UD-left-oblique-outer-x-centers-stage.cost-only.bin",
    ),
    (
        "--middle-right-oblique-cost",
        "lookup-tables/lookup-table-7x7x7-phase5-6-UD-middle-right-oblique-centers-stage.cost-only.bin",
    ),
    (
        "--middle-oblique-outer-x-cost",
        "lookup-tables/lookup-table-7x7x7-phase5-6-UD-middle-oblique-outer-x-centers-stage.cost-only.bin",
    ),
    (
        "--right-oblique-outer-x-cost",
        "lookup-tables/lookup-table-7x7x7-phase5-6-UD-right-oblique-outer-x-centers-stage.cost-only.bin",
    ),
)


class LookupTableIDA777UDObliquesOuterXStage:
    """
    Stage the U/D outer x-centers while pairing the U/D left, middle, and
    right obliques anywhere on U/F/D/B. Six pairwise ranked tables, each
    (16! / (8! * 8!))^2 = 165,636,900 states. The middle obliques are the
    outer t-centers, so this also finishes staging the remaining U/D centers.
    """

    def __init__(self, parent):
        self.parent = parent
        self.avoid_oll = None

    def solve_via_c(self, **_kwargs):
        cmd = ["./ida_search_777_UD_centers_stage", "--kociemba", self.parent.get_kociemba_string(True)]
        for flag, filename in UD_PHASE56_TABLES_777:
            download_file_if_needed(filename)
            cmd.extend((flag, filename))

        if self.avoid_oll is not None:
            orbits_with_oll = self.parent.center_solution_leads_to_oll_parity()
            if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
                cmd.append("--orbit0-need-odd-w" if 0 in orbits_with_oll else "--orbit0-need-even-w")
            if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
                cmd.append("--orbit1-need-odd-w" if 1 in orbits_with_oll else "--orbit1-need-even-w")

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
            returncode = proc.wait()

        output = "".join(lines)
        self.parent.solve_via_c_output = output
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                for step in line.split(":", 1)[1].strip().split():
                    self.parent.rotate(step)
                return

        raise SolveError(f"ida_search_777_UD_centers_stage failed with exit {returncode}\n{output}")

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        tracked = set(UFBD_outer_x_centers_777 + UFBD_oblique_edges_777)
        for x in centers_777:
            if x in tracked:
                self.parent.state[x] = "U" if self.parent.state[x] in ("U", "D") else "x"
            else:
                self.parent.state[x] = "."


# ==================================================
# combined phases 7/8/9
# daisy-solve UD, LR, and FB centers
# ==================================================
DAISY_ORBIT_SLUGS_777 = (
    "without-left-oblique",
    "without-middle-oblique",
    "without-right-oblique",
    "without-inner-t",
    "without-inner-x",
)

DAISY_LEAVE_ONE_OUT_TABLES_777 = tuple(
    (
        f"--{axis.lower()}-{slug}-cost",
        f"lookup-tables/lookup-table-7x7x7-daisy-{axis}-{slug}-centers.cost-only.bin",
    )
    for axis in ("UD", "LR", "FB")
    for slug in DAISY_ORBIT_SLUGS_777
)

DAISY_PERFECT_TABLES_777 = tuple(
    (
        f"--{axis.lower()}-perfect-cost",
        f"lookup-tables/lookup-table-7x7x7-daisy-{axis}-perfect-centers.cost-only.bin",
    )
    for axis in ("UD", "LR", "FB")
)

# The daisy tables cost 0 at either daisy orientation, which leaves --native-only
# blind exactly where the remaining work is. These twins are built to the native
# goal alone, so they measure the distance a larger odd cube actually has to walk.
NATIVE_SOLVE_PERFECT_TABLES_777 = tuple(
    (
        f"--{axis.lower()}-perfect-cost",
        f"lookup-tables/lookup-table-7x7x7-solve-{axis}-perfect-centers.cost-only.bin",
    )
    for axis in ("UD", "LR", "FB")
)

# A wide quarter turn would move centers out of their orbit, so the daisy keeps the
# outer turns and the 2- and 3-wide half turns. This must match move_is_allowed() in
# ida_search_777_daisy_centers.c
DAISY_CENTERS_ILLEGAL_MOVES_777 = tuple(
    f"{prefix}{face}{suffix}" for prefix in ("", "3") for face in "ULFRBD" for suffix in ("w", "w'")
)


class LookupTableIDA777DaisyCenters:
    """
    Daisy-solve the remaining centers on all three axes. Fifteen leave-one-out
    70^4 ranked tables, or three perfect 70^5 tables, each C(8,4) per orbit.

    ``solve_via_c(native_only=True)`` narrows the goal to the native orientation
    and swaps in the perfect tables built to that same goal, which is what cubes
    larger than 7x7x7 need for each center orbit.
    """

    def __init__(self, parent, use_perfect_tables=False, multiplier=None):
        self.parent = parent
        self.avoid_oll = None
        self.use_perfect_tables = use_perfect_tables
        # Without a multiplier the C searcher uses its sampled per-axis cost matrix,
        # which is what utils/build-777-daisy-cost-matrix.py exists to rebuild.
        self.multiplier = multiplier

    def solve_via_c(self, native_only=False, **_kwargs):
        if native_only:
            if not self.use_perfect_tables:
                raise SolveError("--native-only has no leave-one-out tables, it needs the perfect solve tables")
            tables = NATIVE_SOLVE_PERFECT_TABLES_777
        else:
            tables = DAISY_PERFECT_TABLES_777 if self.use_perfect_tables else DAISY_LEAVE_ONE_OUT_TABLES_777
        cmd = ["./ida_search_777_daisy_centers", "--kociemba", self.parent.get_kociemba_string(True)]
        for flag, filename in tables:
            download_file_if_needed(filename)
            cmd.extend((flag, filename))
        if self.multiplier:
            cmd.extend(("--multiplier", str(self.multiplier)))
        if native_only:
            cmd.append("--native-only")

        output = self._run(cmd)
        self.parent.solve_via_c_output = output
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                for step in line.split(":", 1)[1].strip().split():
                    self.parent.rotate(step)
                return

        raise SolveError(f"ida_search_777_daisy_centers failed\n{output}")

    def _run(self, cmd):
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
            proc.wait()

        return "".join(lines)


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

    def sanity_check(self):
        self._sanity_check("edge-orbit-0", edge_orbit_0_777, 8)
        self._sanity_check("edge-orbit-1", edge_orbit_1_777, 8)
        self._sanity_check("edge-orbit-2", edge_orbit_2_777, 4)
        self._sanity_check("corners", corners_777, 4)
        self._sanity_check("left-oblique", left_oblique_edges_777, 4)
        self._sanity_check("right-oblique", right_oblique_edges_777, 4)
        self._sanity_check("outside x-centers", outer_x_centers_777, 4)
        self._sanity_check("inside x-centers", inner_x_centers_777, 4)
        self._sanity_check("outside t-centers", outer_t_centers_777, 4)
        self._sanity_check("inside t-centers", inner_t_centers_777, 4)
        self._sanity_check("centers", middle_centers_777, 1)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # phase 2 - stage U/D inner centers and pair L/R obliques
        self.lt_LR_oblique_edges_UD_inner_centers_stage = LookupTableIDA777LRObliqueEdgesUDInnerCentersStage(self)

        # Phase 3 and everything after it only turns the outer orbit, so no
        # 3Xw quarter turn survives past phase 2 and it is the last chance to
        # fix orbit1 parity. Orbit0 is handled by the combined UD outer-x /
        # oblique phase that replaced fake 5x5x5 FB staging.
        self.lt_LR_oblique_edges_UD_inner_centers_stage.avoid_oll = 1

        # phase 5/6 - stage U/D outer x-centers and pair U/D obliques
        self.lt_UD_obliques_outer_x_stage = LookupTableIDA777UDObliquesOuterXStage(self)
        self.lt_UD_obliques_outer_x_stage.avoid_oll = 0

        # phase 7 - daisy-solve remaining centers on all three axes
        self.lt_daisy_centers = LookupTableIDA777DaisyCenters(self, use_perfect_tables=True)

    def create_fake_555_from_inside_centers(self):
        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_777 = side_index * 49

            # corners
            fake_555.state[1 + offset_555] = self.state[1 + offset_777]
            fake_555.state[5 + offset_555] = self.state[7 + offset_777]
            fake_555.state[21 + offset_555] = self.state[43 + offset_777]
            fake_555.state[25 + offset_555] = self.state[49 + offset_777]

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

            # corners
            fake_555.state[1 + offset_555] = self.state[1 + offset_777]
            fake_555.state[5 + offset_555] = self.state[7 + offset_777]
            fake_555.state[21 + offset_555] = self.state[43 + offset_777]
            fake_555.state[25 + offset_555] = self.state[49 + offset_777]

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

    # LR centers
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
                pass
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                elif "w" in step:
                    step = "3" + step

                self.rotate(step)

    def stage_LR_centers(self):
        """
        phase 1 - use 5x5x5 solver to stage the LR inner centers (10 moves)
        phase 2 - stage UD inner centers and pair LR oblique edges
        phase 3 - use 5x5x5 solver to stage the LR centers (10 moves)
        """
        if self.LR_centers_staged() and self.UD_inside_centers_staged():
            return

        # phase 1 - use 5x5x5 solver to stage the LR inner centers
        tmp_solution_len = len(self.solution)
        self.group_inside_LR_centers()
        self.print_cube_add_comment("LR inner centers staged", tmp_solution_len)

        # phase 2 - stage UD inner centers and pair LR oblique edges
        tmp_solution_len = len(self.solution)
        self.lt_LR_oblique_edges_UD_inner_centers_stage.solve_via_c(use_kociemba_string=True)
        self.print_cube_add_comment("UD inner centers staged, LR oblique edges paired", tmp_solution_len)

        # phase 3 - use 5x5x5 solver to stage the LR centers
        tmp_solution_len = len(self.solution)
        self.create_fake_555_from_outside_centers()
        self.fake_555.group_centers_stage_LR()

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                pass
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

        self.print_cube_add_comment("LR centers staged", tmp_solution_len)

    # UD centers
    def UD_inside_centers_staged(self):
        state = self.state

        for x in UD_inside_centers_777:
            if state[x] not in ("U", "D"):
                return False
        return True

    def stage_UD_centers(self):
        if self.UD_centers_staged():
            return

        # phases 5 and 6 - stage UD outer x-centers and pair UD obliques
        tmp_solution_len = len(self.solution)
        self.lt_UD_obliques_outer_x_stage.solve_via_c()
        self.print_cube_add_comment("UD centers staged", tmp_solution_len)

    def centers_combined_daisy_solve(self, native_only=False):
        tmp_solution_len = len(self.solution)
        self.lt_daisy_centers.solve_via_c(native_only=native_only)
        self.print_cube_add_comment("centers daisy solved", tmp_solution_len)

    def reduce_555(self):
        self.lt_init()
        self.stage_LR_centers()
        self.stage_UD_centers()
        self.centers_combined_daisy_solve()


def rotate_777(cube, step):
    return [cube[x] for x in swaps_777[step]]
