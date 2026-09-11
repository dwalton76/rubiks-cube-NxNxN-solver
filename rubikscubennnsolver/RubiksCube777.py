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

Phase 4 - stage UD inner centers
    Same as phase 1, but for U/D via the 5x5x5 FB stager. Only larger odd
    cubes run this; on a 7x7x7 phase 2 has already staged them.

Phase 5/6 - stage UD outer x-centers and pair UD obliques
    Ranked pairwise tables over the UFBD outer-x, left, middle, and right
    oblique coordinates. The middle obliques are the outer t-centers, so this
    also stages the remaining UD centers. Larger odd cubes keep the older
    split path when a fake-7x7 outer-x coordinate is only a placeholder.

Phase 7/8/9 - daisy-solve UD, LR, and FB centers
    One ranked IDA over five C(8,4) orbits per axis, ignoring outer-x. The
    first attempt uses fifteen leave-one-out 70^4 tables; three 70^5 tables
    are the fallback if that search is slower than the old serial bars path.
    The remaining puzzle is a 5x5x5.

Odd cubes larger than 7x7x7 reuse this solver on concentric orbits. After
the combined daisy search they still run the t-center IDA (step70) in
``RubiksCubeNNNOdd``.
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

LR_oblique_edges_and_outer_t_center = (
    59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89,  # Left
    157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187,  # Right
)

LR_inside_centers_and_left_oblique_edges = (
    59, 66, 67, 68, 69, 73, 74, 75, 79, 80, 81, 82, 89,  # Left
    157, 164, 165, 166, 167, 171, 172, 173, 177, 178, 179, 180, 187,  # Right
)

LR_inside_centers_and_outer_t_centers = (
    60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88,  # Left
    158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186,  # Right
)

LR_inside_centers_and_right_oblique_edges = (
    61, 65, 66, 67, 68, 73, 74, 75, 80, 81, 82, 83, 87,  # Left
    159, 163, 164, 165, 166, 171, 172, 173, 178, 179, 180, 181, 185,  # Right
)

UD_oblique_edges_and_outer_t_center = (
    10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
    255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
)

UD_inside_centers_and_left_oblique_edges = (
    10, 17, 18, 19, 20, 24, 25, 26, 30, 31, 32, 33, 40,  # Upper
    255, 262, 263, 264, 265, 269, 270, 271, 275, 276, 277, 278, 285,  # Down
)

UD_inside_centers_and_outer_t_centers = (
    11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39,  # Upper
    256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284,  # Down
)

UD_inside_centers_and_right_oblique_edges = (
    12, 16, 17, 18, 19, 24, 25, 26, 31, 32, 33, 34, 38,  # Upper
    257, 261, 262, 263, 264, 269, 270, 271, 276, 277, 278, 279, 283,  # Down
)

LR_centers_minus_outside_x_centers_777 = (
    59, 60, 61, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 87, 88, 89,  # Left
    157, 158, 159, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 185, 186, 187,  # Right
)

UD_centers_minus_outside_x_centers_777 = (
    10, 11, 12, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 38, 39, 40,  # Upper
    255, 256, 257, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 283, 284, 285,  # Down
)

FB_inside_centers_and_outer_t_centers = (
    109, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 137,  # Front
    207, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 235,  # Back
)

FB_oblique_edges_and_outer_t_center = (
    108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  # Front
    206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  # Back
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

PHASE7_ILLEGAL_MOVES = (
    # keep all centers staged
    "3Uw", "3Uw'", "Uw", "Uw'",
    "3Lw", "3Lw'", "Lw", "Lw'",
    "3Fw", "3Fw'", "Fw", "Fw'",
    "3Rw", "3Rw'", "Rw", "Rw'",
    "3Bw", "3Bw'", "Bw", "Bw'",
    "3Dw", "3Dw'", "Dw", "Dw'",
    "U", "U'", "U2",
    "D", "D'", "D2",
    "F", "F'", "F2",
    "D", "D'", "D2",
)

PHASE8_ILLEGAL_MOVES = (
    "3Uw", "3Uw'", "Uw", "Uw'",
    "3Lw", "3Lw'", "Lw", "Lw'",
    "3Fw", "3Fw'", "Fw", "Fw'",
    "3Rw", "3Rw'", "Rw", "Rw'",
    "3Bw", "3Bw'", "Bw", "Bw'",
    "3Dw", "3Dw'", "Dw", "Dw'",
    "L", "L'",
    "R", "R'",
    "3Uw2", "Uw2",
    "3Dw2", "Dw2",
    "F", "F'", "F2",
    "D", "D'", "D2",
)

PHASE9_ILLEGAL_MOVES = (
    "3Uw", "3Uw'", "Uw", "Uw'",
    "3Lw", "3Lw'", "Lw", "Lw'",
    "3Fw", "3Fw'", "Fw", "Fw'",
    "3Rw", "3Rw'", "Rw", "Rw'",
    "3Bw", "3Bw'", "Bw", "Bw'",
    "3Dw", "3Dw'", "Dw", "Dw'",
    "L", "L'",
    "R", "R'",
    "3Fw2", "Fw2",
    "3Bw2", "Bw2",
    "U", "U'",
    "D", "D'",
)

# fmt: on


class LookupTableIDA777LRObliqueEdgePairing(LookupTableIDAViaGraph):
    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=LR_OBLIQUE_PAIRING_ILLEGAL_MOVES,
            centers_only=True,
            C_ida_type="7x7x7-LR-oblique-edges-stage",
        )
        # fmt: on

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_777:
            if x in oblique_edges_777:
                if self.parent.state[x] == "L" or self.parent.state[x] == "R":
                    self.parent.state[x] = "L"
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


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
class LookupTableIDA777UDObliqueEdgePairing(LookupTableIDAViaGraph):

    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=PHASE5_ILLEGAL_MOVES,
            centers_only=True,
            C_ida_type="7x7x7-UD-oblique-edges-stage",
        )
        # fmt: on

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_777:
            if x in UFBD_oblique_edges_777:
                if self.parent.state[x] == "U" or self.parent.state[x] == "D":
                    self.parent.state[x] = "U"
                else:
                    self.parent.state[x] = "x"
            else:
                self.parent.state[x] = "."


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
    """

    def __init__(self, parent, use_perfect_tables=False, multiplier=None):
        self.parent = parent
        self.avoid_oll = None
        self.use_perfect_tables = use_perfect_tables
        # Without a multiplier the C searcher uses its sampled per-axis cost matrix,
        # which is what utils/build-777-daisy-cost-matrix.py exists to rebuild.
        self.multiplier = multiplier

    def solve_via_c(self, **_kwargs):
        tables = DAISY_PERFECT_TABLES_777 if self.use_perfect_tables else DAISY_LEAVE_ONE_OUT_TABLES_777
        cmd = ["./ida_search_777_daisy_centers", "--kociemba", self.parent.get_kociemba_string(True)]
        for flag, filename in tables:
            download_file_if_needed(filename)
            cmd.extend((flag, filename))
        if self.multiplier:
            cmd.extend(("--multiplier", str(self.multiplier)))

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

        raise SolveError(f"ida_search_777_daisy_centers failed with exit {returncode}\n{output}")


# ==================================================
# phase 7
# LR centers to vertical bars
# ==================================================
class LookupTable777Step41(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . L . . . L .  . . . . . . .  . R . . . R .  . . . . . . .
    . L . . . L .  . . . . . . .  . R . . . R .  . . . . . . .
    . L . . . L .  . . . . . . .  . R . . . R .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step41.txt",
            self.state_targets,
            linecount=343000,
            max_depth=8,
            all_moves=moves_777,
            illegal_moves=PHASE7_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LR_oblique_edges_and_outer_t_center])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(LR_oblique_edges_and_outer_t_center, state):
            cube[pos] = pos_state


class LookupTable777Step42(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . L . . . .  . . . . . . .  . . R . . . .  . . . . . . .
    . . L L L L .  . . . . . . .  . . R R R R .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . L L L L . .  . . . . . . .  . R R R R . .  . . . . . . .
    . . . . L . .  . . . . . . .  . . . . R . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step42.txt",
            self.state_targets,
            linecount=343000,
            max_depth=9,
            all_moves=moves_777,
            illegal_moves=PHASE7_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LR_inside_centers_and_left_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(LR_inside_centers_and_left_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable777Step43(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . L . . .  . . . . . . .  . . . R . . .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . L L L L L .  . . . . . . .  . R R R R R .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . . . L . . .  . . . . . . .  . . . R . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step43.txt",
            self.state_targets,
            linecount=343000,
            max_depth=8,
            all_moves=moves_777,
            illegal_moves=PHASE7_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LR_inside_centers_and_outer_t_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(LR_inside_centers_and_outer_t_centers, state):
            cube[pos] = pos_state


class LookupTable777Step44(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . L . .  . . . . . . .  . . . . R . .  . . . . . . .
    . L L L L . .  . . . . . . .  . R R R R . .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . . L L L L .  . . . . . . .  . . R R R R .  . . . . . . .
    . . L . . . .  . . . . . . .  . . R . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step44.txt",
            self.state_targets,
            linecount=343000,
            max_depth=9,
            all_moves=moves_777,
            illegal_moves=PHASE7_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LR_inside_centers_and_right_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(LR_inside_centers_and_right_oblique_edges, state):
            cube[pos] = pos_state


class LookupTableIDA777Step40(LookupTableIDAViaGraph):
    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=PHASE7_ILLEGAL_MOVES,
            prune_tables=(parent.lt_step41, parent.lt_step42, parent.lt_step43, parent.lt_step44),
            centers_only=True,
        )
        # fmt: on


# ==================================================
# phase 8
# UD centers to vertical bars
# ==================================================
class LookupTable777Step51(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . U U U . .
                   . U . . . U .
                   . U . . . U .
                   . U . . . U .
                   . . U U U . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . D D D . .
                   . D . . . D .
                   . D . . . D .
                   . D . . . D .
                   . . D D D . .
                   . . . . . . .

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

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step51.txt",
            self.state_targets,
            linecount=343000,
            max_depth=9,
            all_moves=moves_777,
            illegal_moves=PHASE8_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in UD_oblique_edges_and_outer_t_center])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UD_oblique_edges_and_outer_t_center, state):
            cube[pos] = pos_state


class LookupTable777Step52(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . U . . . .
                   . . U U U U .
                   . . U U U . .
                   . U U U U . .
                   . . . . U . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . D . . . .
                   . . D D D D .
                   . . D D D . .
                   . D D D D . .
                   . . . . D . .
                   . . . . . . .

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

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step52.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_777,
            illegal_moves=PHASE8_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in UD_inside_centers_and_left_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UD_inside_centers_and_left_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable777Step53(LookupTable):
    """
                   . . . . . . .
                   . . . U . . .
                   . . U U U . .
                   . U U U U U .
                   . . U U U . .
                   . . . U . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . D . . .
                   . . D D D . .
                   . D D D D D .
                   . . D D D . .
                   . . . D . . .
                   . . . . . . .

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

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step53.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_777,
            illegal_moves=PHASE8_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in UD_inside_centers_and_outer_t_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UD_inside_centers_and_outer_t_centers, state):
            cube[pos] = pos_state


class LookupTable777Step54(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . . . U . .
                   . U U U U . .
                   . . U U U . .
                   . . U U U U .
                   . . U . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . D . .
                   . D D D D . .
                   . . D D D . .
                   . . D D D D .
                   . . D . . . .
                   . . . . . . .

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

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step54.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_777,
            illegal_moves=PHASE8_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in UD_inside_centers_and_right_oblique_edges])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UD_inside_centers_and_right_oblique_edges, state):
            cube[pos] = pos_state


class LookupTable777Step55(LookupTable):
    """
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . L L L L L .  . . . . . . .  . R R R R R .  . . . . . . .
    . L L L L L .  . . . . . . .  . R R R R R .  . . . . . . .
    . L L L L L .  . . . . . . .  . R R R R R .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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

    state_targets = ("LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR", "RRRRLLLRRLLLRRLLLRRRRLLLLRRRLLRRRLLRRRLLLL")

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step55.txt",
            self.state_targets,
            linecount=72,
            max_depth=4,
            all_moves=moves_777,
            illegal_moves=PHASE8_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LR_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(LR_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTableIDA777Step50(LookupTableIDAViaGraph):
    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=PHASE8_ILLEGAL_MOVES,
            prune_tables=(parent.lt_step51, parent.lt_step52, parent.lt_step53, parent.lt_step54, parent.lt_step55),
            centers_only=True,
        )
        # fmt: on


# ==================================================
# phase 9
# daisy-solve the centers
# ==================================================
class LookupTable777Step61(LookupTable):
    """
                   . . . . . . .
                   . . U U U . .
                   . U U U U U .
                   . U U U U U .
                   . U U U U U .
                   . . U U U . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . D D D . .
                   . D D D D D .
                   . D D D D D .
                   . D D D D D .
                   . . D D D . .
                   . . . . . . .

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

    state_targets = ("UUUUUUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDDDDDD", "DDDDUUUDDUUUDDUUUDDDDUUUUDDDUUDDDUUDDDUUUU")

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step61.txt",
            self.state_targets,
            linecount=72,
            max_depth=4,
            all_moves=moves_777,
            illegal_moves=PHASE9_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in UD_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UD_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTable777Step62(LookupTable):
    """
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . L L L L L .  . . . . . . .  . R R R R R .  . . . . . . .
    . L L L L L .  . . . . . . .  . R R R R R .  . . . . . . .
    . L L L L L .  . . . . . . .  . R R R R R .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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

    state_targets = ("LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR", "RRRRLLLRRLLLRRLLLRRRRLLLLRRRLLRRRLLRRRLLLL")

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step62.txt",
            self.state_targets,
            linecount=72,
            max_depth=4,
            all_moves=moves_777,
            illegal_moves=PHASE9_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LR_centers_minus_outside_x_centers_777])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(LR_centers_minus_outside_x_centers_777, state):
            cube[pos] = pos_state


class LookupTable777Step65(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . F . . .  . . . . . . .  . . . B . . .
    . . . . . . .  . . F F F . .  . . . . . . .  . . B B B . .
    . . . . . . .  . F F F F F .  . . . . . . .  . B B B B B .
    . . . . . . .  . . F F F . .  . . . . . . .  . . B B B . .
    . . . . . . .  . . . F . . .  . . . . . . .  . . . B . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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

    state_targets = ("FFFFFFFFFFFFFBBBBBBBBBBBBB", "BFFFBFFFBFFFBFBBBFBBBFBBBF")

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step65.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_777,
            illegal_moves=PHASE9_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in FB_inside_centers_and_outer_t_centers])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(FB_inside_centers_and_outer_t_centers, state):
            cube[pos] = pos_state


class LookupTable777Step66(LookupTable):
    """
    (8! / (4! * 4!))^3 = 343,000 states

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . F F F . .  . . . . . . .  . . B B B . .
    . . . . . . .  . F . . . F .  . . . . . . .  . B . . . B .
    . . . . . . .  . F . . . F .  . . . . . . .  . B . . . B .
    . . . . . . .  . F . . . F .  . . . . . . .  . B . . . B .
    . . . . . . .  . . F F F . .  . . . . . . .  . . B B B . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

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

    state_targets = ("BBBBBBBBBBBBFFFFFFFFFFFF", "FFFFFFFFFFFFBBBBBBBBBBBB")

    def __init__(self, parent, build_state_index=False):
        # fmt: off
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-7x7x7-step66.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_777,
            illegal_moves=PHASE9_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
        # fmt: on

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in FB_oblique_edges_and_outer_t_center])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(FB_oblique_edges_and_outer_t_center, state):
            cube[pos] = pos_state


class LookupTableIDA777Step60(LookupTableIDAViaGraph):
    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_777,
            illegal_moves=PHASE9_ILLEGAL_MOVES,
            prune_tables=(parent.lt_step61, parent.lt_step62, parent.lt_step65, parent.lt_step66),
            centers_only=True,
        )
        # fmt: on


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

    # Odd cubes larger than 7x7x7 reduce one center orbit at a time on a fake
    # 7x7x7, so staging that orbit's U/D inner centers here would be undone by
    # the next orbit. They clear this and pair the L/R obliques on their own.
    stage_UD_inner_centers_in_phase2 = True

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

        # Odd cubes larger than 7x7x7 pair the L/R obliques of an inner center
        # orbit on their own, where the U/D inner centers of the fake 7x7x7 are
        # not a meaningful coordinate.
        self.lt_LR_oblique_edge_pairing = LookupTableIDA777LRObliqueEdgePairing(self)

        # Phase 3 and everything after it only turns the outer orbit, so no
        # 3Xw quarter turn survives past phase 2 and it is the last chance to
        # fix orbit1 parity. Orbit0 is handled by the combined UD outer-x /
        # oblique phase that replaced fake 5x5x5 FB staging.
        self.lt_LR_oblique_edges_UD_inner_centers_stage.avoid_oll = 1

        # phase 5/6 - stage U/D outer x-centers and pair U/D obliques
        self.lt_UD_obliques_outer_x_stage = LookupTableIDA777UDObliquesOuterXStage(self)
        self.lt_UD_obliques_outer_x_stage.avoid_oll = 0

        # Larger odd cubes pair U/D obliques of an inner orbit on their own
        # when the fake-7x7 outer-x coordinate is only a placeholder.
        self.lt_UD_oblique_edge_pairing = LookupTableIDA777UDObliqueEdgePairing(self)

        # phases 7/8/9 - daisy-solve remaining centers on all three axes
        self.lt_daisy_centers = LookupTableIDA777DaisyCenters(self, use_perfect_tables=True)

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

        # phase 9 - daisy-solve the centers
        self.lt_step61 = LookupTable777Step61(self)
        self.lt_step62 = LookupTable777Step62(self)
        self.lt_step65 = LookupTable777Step65(self)
        self.lt_step66 = LookupTable777Step66(self)
        self.lt_step60 = LookupTableIDA777Step60(self)

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

    def _stage_LR_centers_common(self, all_centers: bool) -> None:
        """
        phase 1 - use 5x5x5 solver to stage the LR inner centers (10 moves)
        phase 2 - stage UD inner centers and pair LR oblique edges
        phase 3 - one of
        - use 5x5x5 solver to stage the LR centers (10 moves)
        - use 5x5x5 solver to stage the LR t-centers (5 moves)
        """
        if self.LR_centers_staged():
            # Phase 2 also stages the U/D inner centers, so L/R being staged
            # is not on its own enough to skip this.
            if not self.stage_UD_inner_centers_in_phase2 or self.UD_inside_centers_staged():
                return

        # phase 1 - use 5x5x5 solver to stage the LR inner centers
        tmp_solution_len = len(self.solution)
        self.group_inside_LR_centers()
        self.print_cube_add_comment("LR inner centers staged", tmp_solution_len)

        # phase 2 - stage UD inner centers and pair LR oblique edges
        tmp_solution_len = len(self.solution)

        if self.stage_UD_inner_centers_in_phase2:
            self.lt_LR_oblique_edges_UD_inner_centers_stage.solve_via_c(use_kociemba_string=True)
            desc = "UD inner centers staged, LR oblique edges paired"
        else:
            self.lt_LR_oblique_edge_pairing.solve_via_c(use_kociemba_string=True)
            desc = "LR oblique edges paired"

        self.print_cube_add_comment(desc, tmp_solution_len)

        # phase 3 - use 5x5x5 solver to stage the LR centers
        tmp_solution_len = len(self.solution)
        self.create_fake_555_from_outside_centers()

        if all_centers:
            self.fake_555.group_centers_stage_LR()
            desc = "LR centers staged"
        else:
            self.fake_555.lt_LR_t_centers_stage_ida.solve_via_c()
            desc = "LR t-centers staged"

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                pass
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

        self.print_cube_add_comment(desc, tmp_solution_len)

    def stage_LR_centers(self):
        self._stage_LR_centers_common(True)

    def stage_LR_t_centers(self):
        self._stage_LR_centers_common(False)

    def LR_centers_vertical_bars(self):
        # phase 7 - LR centers to vertical bars
        tmp_solution_len = len(self.solution)
        self.lt_step40.solve_via_c()
        self.print_cube_add_comment("LR centers vertical bars", tmp_solution_len)

    # UD centers
    def UD_inside_centers_staged(self):
        state = self.state

        for x in UD_inside_centers_777:
            if state[x] not in ("U", "D"):
                return False
        return True

    def group_inside_UD_centers(self):
        self.create_fake_555_from_inside_centers()
        self.fake_555.group_centers_stage_FB()

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                pass
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    step = "4" + step[1:]
                elif "w" in step:
                    step = "3" + step

                self.rotate(step)

    def _stage_UD_centers(self, all_centers: bool):
        if self.UD_centers_staged():
            return

        # phase 4 - use 5x5x5 solver to stage the UD inner centers
        if not self.stage_UD_inner_centers_in_phase2:
            tmp_solution_len = len(self.solution)
            self.group_inside_UD_centers()
            self.print_cube_add_comment("UD inner x-centers staged", tmp_solution_len)

        if all_centers:
            # phases 5 and 6 - stage UD outer x-centers and pair UD obliques
            tmp_solution_len = len(self.solution)
            self.lt_UD_obliques_outer_x_stage.solve_via_c()
            self.print_cube_add_comment("UD centers staged", tmp_solution_len)
            return

        # t-centers-only fallback used by larger odd cubes when the fake-7x7
        # outer-x coordinate is not a real sticker from the active orbit.
        tmp_solution_len = len(self.solution)
        self.lt_UD_oblique_edge_pairing.solve_via_c(use_kociemba_string=True)
        self.print_cube_add_comment("UD oblique edges paired", tmp_solution_len)

        tmp_solution_len = len(self.solution)
        self.create_fake_555_from_outside_centers()
        self.fake_555.lt_UD_t_centers_stage_ida.solve_via_c()
        desc = "UD t-centers staged"

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                pass
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

        self.print_cube_add_comment(desc, tmp_solution_len)

    def stage_UD_centers(self):
        self._stage_UD_centers(True)

    def stage_UD_t_centers(self):
        self._stage_UD_centers(False)

    def UD_centers_vertical_bars(self):
        # phase 8 - UD centers to vertical bars
        tmp_solution_len = len(self.solution)
        self.lt_step50.solve_via_c()
        self.print_cube_add_comment("LR solved, UD vertical bars", tmp_solution_len)

    def centers_daisy_solve(self):
        # phase 9 - centers daisy solve (serial graph path, kept for A/B)
        tmp_solution_len = len(self.solution)
        self.lt_step60.solve_via_c()
        self.print_cube_add_comment("centers daisy solved", tmp_solution_len)

    def centers_combined_daisy_solve(self):
        tmp_solution_len = len(self.solution)
        self.lt_daisy_centers.solve_via_c()
        self.print_cube_add_comment("centers daisy solved", tmp_solution_len)

    def solve_centers(self):
        # This is only used when solving a cube larger than 777
        tmp_solution_len = len(self.solution)
        self.create_fake_555_from_outside_centers()
        self.fake_555.lt_ULFRBD_centers_solve.solve_via_c()

        for step in self.fake_555.solution:
            if step.startswith("COMMENT"):
                pass
            else:
                if step.startswith("5"):
                    step = "7" + step[1:]
                elif step.startswith("3"):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

        self.print_cube_add_comment("centers solved", tmp_solution_len)

        if not self.centers_solved():
            raise SolveError("centers should be solved")

    def reduce_555(self):
        self.lt_init()
        self.stage_LR_centers()
        self.stage_UD_centers()
        self.centers_combined_daisy_solve()


def rotate_777(cube, step):
    return [cube[x] for x in swaps_777[step]]
