"""
7x7x7 solver: reduce the cube to a 5x5x5, then finish with the 5x5x5 solver.

A 7x7x7 has 25 centers per face (t-centers, x-centers, and three orbits of
oblique edges) plus three orbits of wings. ``reduce_555`` stages and
daisy-solves the centers. ``group_edges`` (via the 5x5x5 solver) then pairs
the wings and ``solve_333`` finishes the cube. Phase 1 is a fake 5x5x5
center stage. The other phases are IDA searches.

Phase 1 - stage LR inner centers
    Map the inner 3x3 of each face onto a fake 5x5x5 and stage its LR centers.
    ``--solution-count 0`` collects every shortest solution.

Phase 2 - stage UD inner centers and pair LR oblique edges
    One ranked table covers the UFBD inner-t and inner-x centers. The LR
    obliques only have to be paired, not land on LR. Every distinct phase 1
    ending is a root of this search. The orbit-1 table is maxed with the
    sampled unpaired-count matrix, so that exact cost is already a second
    coordinate. Equal matrix costs try the root with fewer unpaired obliques
    first. After the first solution, up to eight roots the matrix priced at
    that same depth are searched one ply shallower, and a shorter one replaces
    it. The matrix cost is scaled by 1.05 for ``PHASE2_SECONDS`` seconds. A
    search still running then is retried at 1.10, which kept the 17-move
    solution on the 66s cube and finished in about 4s. Even and odd orbit-1
    tables are loaded when present, and each root carries its own orbit-1
    requirement. This is the last phase with a 3-wide quarter turn, so it
    owns orbit-1 OLL.

Phase 3 - stage the LR left, middle, and right obliques and the LR outer x-centers
    Those four orbits land on L and R. The search keeps up to 8 distinct shortest
    solutions, and phase 5 drops the ones that reach the same state. This
    phase's moves are applied for the root phase 5 keeps. The search has no
    3-wide quarter turn, so the phase 1 and phase 2 centers and orbit-1 OLL
    stay as phase 2 left them. Larger odd cubes whose outer x are real still
    use the fake 5x5x5 LR center stage for this step.

Phase 5 - stage the UD oblique bars and the UD outer x-centers
    Six pair tables. Try the admissible search for
    ``PHASE56_ADMISSIBLE_CAP`` seconds, then the same search with the
    pair-cost matrix for ``PHASE56_MATRIX_CAP`` seconds. Every distinct
    phase 3 ending is a root, and the shortest staging is kept. This phase
    owns orbit-0 OLL.

Phase 6 - used only when both phase-5 searches time out
    Stage the UD oblique bars with the three oblique tables, then replay
    5x5 phase 2 on the outside centers. Orbit-0 OLL comes from this cube,
    not from the fake cube's edges. ``Lw`` and ``Rw`` move outer x without
    splitting a staged oblique bar.

Phase 7 - solve the LR inner centers and pair the LR oblique bars
    LR inner-t and inner-x must be native. The eight oblique bars on L and R
    must each be one color; their slot does not matter. Cost is the max of the
    LR inner table and ceil(unpaired LR wings * 0.40). 0.25 is admissible;
    0.40 is the measured default and is not a lower bound.
    ``--unpaired-multiplier`` overrides it. Up to 16
    distinct shortest endings are kept, and phase 8 searches those center
    states. Outer x-centers are printed as ``.``.

Phase 8 - solve the UD and FB inners and pair the UD and FB oblique bars
    A bar may sit on either face of its axis. Moves keep the phase 7 LR state:
    outer turns, 2-wide half turns, and the L/R 3-wide half turns. Cost is the
    max of the two paired-bar tables, the two inner-plus-oblique tables, and
    the inner-interaction table, scaled by ``--multiplier 1.2``. The 70^5
    tables have 70 goals. The inner-interaction table is the UD/FB inner-t and
    inner-x quartic. Up to 16 distinct shortest endings are kept for phase 9. Outer
    x-centers are printed as ``.``.

Phase 9 - daisy-solve all six sides
    Every distinct phase 8 ending is a root. The first root that solves at the
    shortest depth is kept, and up to eight roots priced at that depth are
    searched one ply shallower. No 3-wide move remains, so the phase 8 centers
    stay solved. Cost is the max of the eight center tables, with no multiplier.
    Those tables were built with 3Lw2 and 3Rw2 legal, so they are a lower bound
    on this smaller move set. Outer x-centers are printed as ``.``. The
    remaining puzzle is a 5x5x5.
"""

# standard libraries
import logging
import os
import shutil
import subprocess
import tempfile
import time

# rubiks cube libraries
from rubikscubennnsolver.LookupTable import download_file_if_needed
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

# Centers the daisy phases actually rank. Outer x is blanked in those searches.
_DAISY_CENTER_SQUARES = tuple(square for square in centers_777 if square not in set(outer_x_centers_777))

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

# Same left/middle/right triplets as unpaired_oblique_count() in ida_search_777_centers_stage.c
LR_LEFT_OBLIQUES_777 = (
    10, 30, 20, 40, 59, 79, 69, 89, 108, 128, 118, 138,
    157, 177, 167, 187, 206, 226, 216, 236, 255, 275, 265, 285,
)
LR_MIDDLE_OBLIQUES_777 = (
    11, 23, 27, 39, 60, 72, 76, 88, 109, 121, 125, 137,
    158, 170, 174, 186, 207, 219, 223, 235, 256, 268, 272, 284,
)
LR_RIGHT_OBLIQUES_777 = (
    12, 16, 34, 38, 61, 65, 83, 87, 110, 114, 132, 136,
    159, 163, 181, 185, 208, 212, 230, 234, 257, 261, 279, 283,
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
    Phase 2: stage the UD inner t- and x-centers while pairing the LR obliques
    anywhere.

    One ranked table over the UFBD inner-t and inner-x coordinates.

    (16! / (8! * 8!))^2 = 165,636,900 states

                       . . . . . . .
                       . . . . . . .
                       . . U U U . .
                       . . U . U . .
                       . . U U U . .
                       . . . . . . .
                       . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . x x x . .  . . . . . . .  . . x x x . .
    . . . . . . .  . . x . x . .  . . . . . . .  . . x . x . .
    . . . . . . .  . . x x x . .  . . . . . . .  . . x x x . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                       . . . . . . .
                       . . . . . . .
                       . . U U U . .
                       . . U . U . .
                       . . U U U . .
                       . . . . . . .
                       . . . . . . .

    lookup-table-7x7x7-step20-UD-inner-centers-stage.cost-only.bin
    ==============================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 33 entries (0 percent, 16.50x previous step)
    3 steps has 374 entries (0 percent, 11.33x previous step)
    4 steps has 3,838 entries (0 percent, 10.26x previous step)
    5 steps has 39,254 entries (0 percent, 10.23x previous step)
    6 steps has 387,357 entries (0 percent, 9.87x previous step)
    7 steps has 3,374,380 entries (2 percent, 8.71x previous step)
    8 steps has 20,851,334 entries (12 percent, 6.18x previous step)
    9 steps has 65,556,972 entries (39 percent, 3.14x previous step)
    10 steps has 66,986,957 entries (40 percent, 1.02x previous step)
    11 steps has 8,423,610 entries (5 percent, 0.13x previous step)
    12 steps has 12,788 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 9.33 moves

    The LR obliques have no table; ``ida_search_777_centers_stage`` combines this
    table with an unpaired-oblique count over the left/middle/right triplets, and
    the obliques only have to be paired, not land on LR. The solver scales that
    cost by ``--multiplier 1.05`` for ``PHASE2_SECONDS`` seconds, then retries
    the same roots at 1.10. This is the last phase
    with a 3Xw quarter turn available, so it owns orbit-1 OLL.

    ``solution_via_c(roots)`` searches every distinct phase-1 ending in one
    process. Each root carries its own orbit-1 requirement. The first root that
    solves at the shortest depth is the one whose phase-1 moves are kept.
    """

    def __init__(self, parent):
        self.parent = parent
        self.filename = UD_INNER_CENTERS_STAGE_TABLE_777
        self.avoid_oll = None

    def _orbit_requirements(self, orbits_with_oll):
        orbit0_requirement = 0
        orbit1_requirement = 0
        if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
            orbit0_requirement = 1 if 0 in orbits_with_oll else 2
        if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
            orbit1_requirement = 1 if 1 in orbits_with_oll else 2
        return orbit0_requirement, orbit1_requirement

    def _run_centers_stage(self, cmd, timeout):
        logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            try:
                output, _stderr = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                logger.info(
                    "%s: no solution within %.0fs at multiplier %s",
                    self.__class__.__name__,
                    timeout,
                    cmd[cmd.index("--multiplier") + 1],
                )
                return None
            returncode = proc.returncode
        output = output or ""
        for line in output.splitlines():
            logger.info("%s", line)
        return output, returncode

    def solution_via_c(self, roots=None, root_cap=None):
        """
        Return ``(root_index, steps)`` for one cube, or for every phase-1 root.

        ``roots`` is ``(index, kociemba, orbits_with_oll)``. The C search prints
        ``ROOT_INDEX`` for the first root that solves at the shortest depth.
        """
        download_file_if_needed(UD_INNER_CENTERS_STAGE_TABLE_777)
        cmd = [
            "./ida_search_777_centers_stage",
            "--ranked-UD-inner-centers-cost",
            self.filename,
        ]
        even_cost = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage-orbit1-even.cost-only.bin"
        odd_cost = "lookup-tables/lookup-table-7x7x7-step20-UD-inner-centers-stage-orbit1-odd.cost-only.bin"
        if os.path.exists(even_cost) and os.path.exists(odd_cost):
            cmd.extend(("--ud-inner-even-cost", even_cost, "--ud-inner-odd-cost", odd_cost))

        roots_filename = None
        if roots:
            with tempfile.NamedTemporaryFile(mode="w", prefix="777-centers-roots-", suffix=".txt", delete=False) as fh:
                roots_filename = fh.name
                for root_index, kociemba, orbits_with_oll in roots:
                    orbit0_requirement, orbit1_requirement = self._orbit_requirements(orbits_with_oll)
                    fh.write(f"{root_index},{orbit0_requirement},{orbit1_requirement},{kociemba}\n")
            cmd.extend(("--kociemba-file", roots_filename))
        else:
            cmd.extend(("--kociemba", self.parent.get_kociemba_string(True)))
            if self.avoid_oll is not None:
                orbit0_requirement, orbit1_requirement = self._orbit_requirements(
                    self.parent.center_solution_leads_to_oll_parity()
                )
                if orbit0_requirement == 1:
                    cmd.append("--orbit0-need-odd-w")
                elif orbit0_requirement == 2:
                    cmd.append("--orbit0-need-even-w")
                if orbit1_requirement == 1:
                    cmd.append("--orbit1-need-odd-w")
                elif orbit1_requirement == 2:
                    cmd.append("--orbit1-need-even-w")
        if root_cap is not None:
            cmd.extend(("--root-cap", str(root_cap)))

        started = time.perf_counter()
        try:
            result = None
            for multiplier, timeout in (
                (PHASE2_MULTIPLIER, PHASE2_SECONDS),
                (PHASE2_FALLBACK_MULTIPLIER, None),
            ):
                result = self._run_centers_stage(cmd + ["--multiplier", f"{multiplier:.2f}"], timeout)
                if result is not None:
                    break
        finally:
            if roots_filename is not None:
                _keep_slow_phase2_roots(roots_filename, time.perf_counter() - started)
                os.unlink(roots_filename)

        if result is None:
            raise SolveError("ida_search_777_centers_stage timed out")
        output, returncode = result
        self.parent.solve_via_c_output = output
        root_index = 0
        for line in output.splitlines():
            if line.startswith("ROOT_INDEX "):
                root_index = int(line.split()[1])
            if line.startswith("SOLUTION"):
                steps = tuple(line.split(":", 1)[1].strip().split())
                return root_index, steps

        raise SolveError(f"ida_search_777_centers_stage failed with exit {returncode}\n{output}")

    def solve_via_c(self, **_kwargs):
        _root_index, steps = self.solution_via_c()
        for step in steps:
            self.parent.rotate(step)

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

UD_OBLIQUE_ONLY_TABLES_777 = tuple(
    (flag, filename) for flag, filename in UD_PHASE56_TABLES_777 if "outer-x" not in flag
)
PHASE56_PAIR_COST_MATRIX_777 = "rubikscubennnsolver/phase56_pair_cost_matrix_777.bin"
PHASE56_ADMISSIBLE_SECONDS = 0.0
# Measured on random cubes reduced through phase 3. Admissible solutions that
# exist finish by 4.9s; the rest are still running at 12s. Matrix solutions
# cluster under 5.6s, then jump to 13s and beyond. Those tails, including the
# search that ran for 40 minutes, go to the oblique-plus-5x5 fallback.
PHASE56_ADMISSIBLE_CAP = 5.0
PHASE56_MATRIX_CAP = 6.0
# On 30 phase-2 searches at 1.05, 23 finished by 22.8s and the next was 30.7s.
# 1.10 on the 66s/17-move cube finishes in 3.8s at the same length. 1.15 matches
# that length in 3.5s. 1.20 adds a move. Try 1.05 for 25s, then 1.10.
PHASE2_MULTIPLIER = 1.05
PHASE2_FALLBACK_MULTIPLIER = 1.10
PHASE2_SECONDS = 25.0
PHASE1_ROOT_CAP = 16
# A phase-2 search this slow keeps its roots file so the same portfolio can be replayed.
SLOW_PHASE2_SECONDS = 60.0
SLOW_PHASE2_ROOTS_DIR = "/tmp/slow-search-roots"


def _keep_slow_phase2_roots(path, seconds):
    if seconds < SLOW_PHASE2_SECONDS:
        return
    os.makedirs(SLOW_PHASE2_ROOTS_DIR, exist_ok=True)
    dest = os.path.join(SLOW_PHASE2_ROOTS_DIR, f"777-centers-roots-{seconds:.0f}s-{os.path.basename(path)}")
    shutil.copy(path, dest)
    logger.info("kept slow phase-2 roots at %s (%.1fs)", dest, seconds)


PHASE3_SOLUTION_CAP = 8
DAISY_PORTFOLIO_CAP = 16
PHASE8_MULTIPLIER = 1.2


class LookupTableIDA777UDObliquesOuterXStage:
    """
    Combined phases 5/6 IDA. The 7x7 solver stages the UD left, middle, and
    right obliques and the UD outer x-centers. Every distinct phase 3 ending
    is a root. A larger odd cube whose outer x are real uses the same six
    pair tables from its one phase 3 solution.

    Four UFBD coordinates - left oblique, middle oblique, right oblique, and
    outer-x - taken two at a time give the six component tables listed in
    ``UD_PHASE56_TABLES_777``:

    | Flag                          | Coordinate pair        |
    | ----------------------------- | ---------------------- |
    | --left-middle-oblique-cost    | left   x middle        |
    | --left-right-oblique-cost     | left   x right         |
    | --left-oblique-outer-x-cost   | left   x outer-x       |
    | --middle-right-oblique-cost   | middle x right         |
    | --middle-oblique-outer-x-cost | middle x outer-x       |
    | --right-oblique-outer-x-cost  | right  x outer-x       |

    Each is a dense pairwise table of (16! / (8! * 8!))^2 = 165,636,900 entries.
    Their individual diagrams and histograms belong to the builder classes in
    ``rubikscubelookuptables/builder777.py`` and are not repeated here.

    ``solve_via_c(obliques_only=True)`` loads ``UD_OBLIQUE_ONLY_TABLES_777`` and
    passes ``--obliques-only``. ``solution_via_c`` loads all six tables. With
    the default ``PHASE56_ADMISSIBLE_SECONDS`` of 0 it starts on the pair-cost
    matrix. A caller that passes both budgets tries the admissible search
    first, then the matrix, and returns ``None`` when the matrix budget runs
    out. The first root that solves at the shortest depth is kept. The middle
    obliques are the outer t-centers. This phase owns orbit-0 OLL.
                   . . . . . . .
                   . . U . U . .
                   . U . . . U .
                   . . . . . . .
                   . U . . . U .
                   . . U . U . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . x . x . .  . . . . . . .  . . x . x . .
    . . . . . . .  . x . . . x .  . . . . . . .  . x . . . x .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . x . . . x .  . . . . . . .  . x . . . x .
    . . . . . . .  . . x . x . .  . . . . . . .  . . x . x . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . U . U . .
                   . U . . . U .
                   . . . . . . .
                   . U . . . U .
                   . . U . U . .
                   . . . . . . .

    lookup-table-7x7x7-phase5-6-UD-left-right-oblique-centers-stage.cost-only.bin
    =============================================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
    3 steps has 286 entries (0 percent, 9.86x previous step)
    4 steps has 2,052 entries (0 percent, 7.17x previous step)
    5 steps has 16,348 entries (0 percent, 7.97x previous step)
    6 steps has 127,859 entries (0 percent, 7.82x previous step)
    7 steps has 844,248 entries (0 percent, 6.60x previous step)
    8 steps has 4,623,585 entries (2 percent, 5.48x previous step)
    9 steps has 19,019,322 entries (11 percent, 4.11x previous step)
    10 steps has 47,544,426 entries (28 percent, 2.50x previous step)
    11 steps has 61,805,656 entries (37 percent, 1.30x previous step)
    12 steps has 28,890,234 entries (17 percent, 0.47x previous step)
    13 steps has 2,722,462 entries (1 percent, 0.09x previous step)
    14 steps has 40,242 entries (0 percent, 0.01x previous step)
    15 steps has 148 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 10.58 moves

    lookup-table-7x7x7-phase5-6-UD-left-middle-oblique-centers-stage.cost-only.bin
    ==============================================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 33 entries (0 percent, 16.50x previous step)
    3 steps has 358 entries (0 percent, 10.85x previous step)
    4 steps has 2,934 entries (0 percent, 8.20x previous step)
    5 steps has 23,262 entries (0 percent, 7.93x previous step)
    6 steps has 155,679 entries (0 percent, 6.69x previous step)
    7 steps has 893,008 entries (0 percent, 5.74x previous step)
    8 steps has 4,447,409 entries (2 percent, 4.98x previous step)
    9 steps has 17,048,560 entries (10 percent, 3.83x previous step)
    10 steps has 41,869,962 entries (25 percent, 2.46x previous step)
    11 steps has 57,876,856 entries (34 percent, 1.38x previous step)
    12 steps has 35,846,966 entries (21 percent, 0.62x previous step)
    13 steps has 7,122,098 entries (4 percent, 0.20x previous step)
    14 steps has 346,646 entries (0 percent, 0.05x previous step)
    15 steps has 3,126 entries (0 percent, 0.01x previous step)

    Total: 165,636,900 entries
    Average: 10.74 moves

    lookup-table-7x7x7-phase5-6-UD-left-oblique-outer-x-centers-stage.cost-only.bin
    ===============================================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 37 entries (0 percent, 18.50x previous step)
    3 steps has 426 entries (0 percent, 11.51x previous step)
    4 steps has 4,552 entries (0 percent, 10.69x previous step)
    5 steps has 48,826 entries (0 percent, 10.73x previous step)
    6 steps has 497,305 entries (0 percent, 10.19x previous step)
    7 steps has 4,366,446 entries (2 percent, 8.78x previous step)
    8 steps has 25,800,644 entries (15 percent, 5.91x previous step)
    9 steps has 71,891,909 entries (43 percent, 2.79x previous step)
    10 steps has 57,817,231 entries (34 percent, 0.80x previous step)
    11 steps has 5,204,126 entries (3 percent, 0.09x previous step)
    12 steps has 5,395 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 9.19 moves

    lookup-table-7x7x7-phase5-6-UD-middle-right-oblique-centers-stage.cost-only.bin
    ===============================================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 33 entries (0 percent, 16.50x previous step)
    3 steps has 358 entries (0 percent, 10.85x previous step)
    4 steps has 2,934 entries (0 percent, 8.20x previous step)
    5 steps has 23,262 entries (0 percent, 7.93x previous step)
    6 steps has 155,679 entries (0 percent, 6.69x previous step)
    7 steps has 893,008 entries (0 percent, 5.74x previous step)
    8 steps has 4,447,409 entries (2 percent, 4.98x previous step)
    9 steps has 17,048,560 entries (10 percent, 3.83x previous step)
    10 steps has 41,869,962 entries (25 percent, 2.46x previous step)
    11 steps has 57,876,856 entries (34 percent, 1.38x previous step)
    12 steps has 35,846,966 entries (21 percent, 0.62x previous step)
    13 steps has 7,122,098 entries (4 percent, 0.20x previous step)
    14 steps has 346,646 entries (0 percent, 0.05x previous step)
    15 steps has 3,126 entries (0 percent, 0.01x previous step)

    Total: 165,636,900 entries
    Average: 10.74 moves

    lookup-table-7x7x7-phase5-6-UD-right-oblique-outer-x-centers-stage.cost-only.bin
    ================================================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 37 entries (0 percent, 18.50x previous step)
    3 steps has 426 entries (0 percent, 11.51x previous step)
    4 steps has 4,552 entries (0 percent, 10.69x previous step)
    5 steps has 48,826 entries (0 percent, 10.73x previous step)
    6 steps has 497,305 entries (0 percent, 10.19x previous step)
    7 steps has 4,366,446 entries (2 percent, 8.78x previous step)
    8 steps has 25,800,644 entries (15 percent, 5.91x previous step)
    9 steps has 71,891,909 entries (43 percent, 2.79x previous step)
    10 steps has 57,817,231 entries (34 percent, 0.80x previous step)
    11 steps has 5,204,126 entries (3 percent, 0.09x previous step)
    12 steps has 5,395 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 9.19 moves

    lookup-table-7x7x7-phase5-6-UD-middle-oblique-outer-x-centers-stage.cost-only.bin
    =================================================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 33 entries (0 percent, 16.50x previous step)
    3 steps has 374 entries (0 percent, 11.33x previous step)
    4 steps has 3,838 entries (0 percent, 10.26x previous step)
    5 steps has 39,254 entries (0 percent, 10.23x previous step)
    6 steps has 387,357 entries (0 percent, 9.87x previous step)
    7 steps has 3,374,380 entries (2 percent, 8.71x previous step)
    8 steps has 20,851,334 entries (12 percent, 6.18x previous step)
    9 steps has 65,556,972 entries (39 percent, 3.14x previous step)
    10 steps has 66,986,957 entries (40 percent, 1.02x previous step)
    11 steps has 8,423,610 entries (5 percent, 0.13x previous step)
    12 steps has 12,788 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 9.33 moves
    """

    def __init__(self, parent):
        self.parent = parent
        self.avoid_oll = None

    def _orbit_requirements(self, orbits_with_oll):
        orbit0_requirement = 0
        orbit1_requirement = 0
        if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
            orbit0_requirement = 1 if 0 in orbits_with_oll else 2
        if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
            orbit1_requirement = 1 if 1 in orbits_with_oll else 2
        return orbit0_requirement, orbit1_requirement

    def _command(self, obliques_only=False, kociemba=None):
        tables = UD_OBLIQUE_ONLY_TABLES_777 if obliques_only else UD_PHASE56_TABLES_777
        cmd = ["./ida_search_777_UD_centers_stage"]
        if kociemba is not None:
            cmd.extend(("--kociemba", kociemba))
        if obliques_only:
            cmd.append("--obliques-only")
        for flag, filename in tables:
            download_file_if_needed(filename)
            cmd.extend((flag, filename))
        orbit0_pairs = tuple(
            (
                flag.replace("-cost", "-even-cost"),
                flag.replace("-cost", "-odd-cost"),
                filename.replace(".cost-only.bin", "-orbit0-even.cost-only.bin"),
                filename.replace(".cost-only.bin", "-orbit0-odd.cost-only.bin"),
            )
            for flag, filename in tables
        )
        if all(os.path.exists(path) for pair in orbit0_pairs for path in pair[2:]):
            for even_flag, odd_flag, even_path, odd_path in orbit0_pairs:
                cmd.extend((even_flag, even_path, odd_flag, odd_path))

        if kociemba is not None and self.avoid_oll is not None:
            orbits_with_oll = self.parent.center_solution_leads_to_oll_parity()
            if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
                cmd.append("--orbit0-need-odd-w" if 0 in orbits_with_oll else "--orbit0-need-even-w")
            if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
                cmd.append("--orbit1-need-odd-w" if 1 in orbits_with_oll else "--orbit1-need-even-w")
        return cmd

    def _run_search(self, cmd, timeout):
        logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            try:
                output, _stderr = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                logger.info("%s: no solution within %ss", self.__class__.__name__, timeout)
                return None
        output = output or ""
        for line in output.splitlines():
            logger.info("%s", line)
        return output

    def _apply_solution(self, output):
        self.parent.solve_via_c_output = output
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                for step in line.split(":", 1)[1].strip().split():
                    self.parent.rotate(step)
                return True
        return False

    def _solution_from_output(self, output):
        root_index = 0
        steps = None
        for line in output.splitlines():
            if line.startswith("ROOT_INDEX "):
                root_index = int(line.split()[1])
            elif line.startswith("SOLUTION"):
                steps = tuple(line.split(":", 1)[1].strip().split())
        if steps is None:
            return None
        return root_index, steps

    def solution_via_c(
        self,
        roots=None,
        admissible_seconds=PHASE56_ADMISSIBLE_SECONDS,
        matrix_seconds=None,
        fallback_multiplier=None,
    ):
        """
        Return ``(root_index, steps)`` for the current cube, or for every phase-3 root.

        ``roots`` is ``(index, kociemba, orbits_with_oll)``. Returns ``None`` when
        a bounded matrix search times out and there is no multiplier fallback.
        """
        roots_filename = None
        try:
            if roots:
                with tempfile.NamedTemporaryFile(mode="w", prefix="777-ud-roots-", suffix=".txt", delete=False) as fh:
                    roots_filename = fh.name
                    for root_index, kociemba, orbits_with_oll in roots:
                        orbit0_requirement, orbit1_requirement = self._orbit_requirements(orbits_with_oll)
                        fh.write(f"{root_index},{orbit0_requirement},{orbit1_requirement},{kociemba}\n")
                cmd = self._command(obliques_only=False)
                cmd.extend(("--kociemba-file", roots_filename))
            else:
                cmd = self._command(obliques_only=False, kociemba=self.parent.get_kociemba_string(True))

            output = self._run_search(cmd, admissible_seconds) if admissible_seconds else None
            if output is not None:
                found = self._solution_from_output(output)
                if found is None:
                    raise SolveError(f"ida_search_777_UD_centers_stage failed\n{output}")
                self.parent.solve_via_c_output = output
                return found

            matrix_cmd = [*cmd, "--pair-cost-matrix", PHASE56_PAIR_COST_MATRIX_777]
            output = self._run_search(matrix_cmd, matrix_seconds)
            if output is not None:
                found = self._solution_from_output(output)
                if found is None:
                    raise SolveError(f"ida_search_777_UD_centers_stage failed\n{output}")
                self.parent.solve_via_c_output = output
                return found
            if fallback_multiplier is not None:
                fallback_cmd = [*cmd, "--multiplier", str(fallback_multiplier)]
                output = self._run_search(fallback_cmd, None)
                if output is not None:
                    found = self._solution_from_output(output)
                    if found is not None:
                        self.parent.solve_via_c_output = output
                        return found
            if matrix_seconds is not None:
                return None
            raise SolveError(f"ida_search_777_UD_centers_stage failed\n{output}")
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

    def solve_via_c(self, obliques_only=False, **kwargs):
        if obliques_only:
            cmd = self._command(obliques_only=True, kociemba=self.parent.get_kociemba_string(True))
            output = self._run_search(cmd, None)
            if output is not None and self._apply_solution(output):
                return
            raise SolveError(f"ida_search_777_UD_centers_stage failed\n{output}")

        found = self.solution_via_c(**kwargs)
        if found is None:
            raise SolveError("ida_search_777_UD_centers_stage timed out")
        _root_index, steps = found
        for step in steps:
            self.parent.rotate(step)

    def stage_obliques_via_c(self, roots=None):
        """
        Stage UD obliques and leave outer x-centers alone.

        ``roots`` is ``(index, kociemba, orbits_with_oll)``. Returns ``(root_index, steps)``.
        """
        roots_filename = None
        try:
            if roots:
                cmd = self._command(obliques_only=True)
                with tempfile.NamedTemporaryFile(
                    mode="w", prefix="777-ud-obliques-", suffix=".txt", delete=False
                ) as fh:
                    roots_filename = fh.name
                    for root_index, kociemba, orbits_with_oll in roots:
                        orbit0_requirement, orbit1_requirement = self._orbit_requirements(orbits_with_oll)
                        fh.write(f"{root_index},{orbit0_requirement},{orbit1_requirement},{kociemba}\n")
                cmd.extend(("--kociemba-file", roots_filename))
            else:
                cmd = self._command(obliques_only=True, kociemba=self.parent.get_kociemba_string(True))
            output = self._run_search(cmd, None)
            found = None if output is None else self._solution_from_output(output)
            if found is None:
                raise SolveError(f"ida_search_777_UD_centers_stage --obliques-only failed\n{output}")
            self.parent.solve_via_c_output = output
            return found
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

    def recolor(self):
        logger.info(f"{self}: recolor (custom)")
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        tracked = set(UFBD_oblique_edges_777 + UFBD_outer_x_centers_777)
        for x in centers_777:
            if x in tracked:
                self.parent.state[x] = "U" if self.parent.state[x] in ("U", "D") else "x"
            else:
                self.parent.state[x] = "."


# ==================================================
# phases 7 and 8
# daisy-solve UD, LR, and FB centers
# ==================================================
# Phase 7. LR inner-t then LR inner-x, 70^2, one native goal. The two orbits are
# closed under the daisy moves, so the byte is the exact inner distance.
DAISY_LR_INNER_TABLE_777 = (
    "--lr-inner-cost",
    "lookup-tables/lookup-table-7x7x7-daisy-lr-inner-centers.cost-only.bin",
)

# Phase 8 takes the max of the paired-bar tables and the two inner-plus-oblique
# tables. Phase 9 takes the max of PHASE9_TABLES_777. Oblique coordinates in
# those tables have both daisy goals,
# so a swapped orientation costs 0 there; --native-only still rejects that
# orientation and the searcher lifts a 0 cost to 1.
# Each paired-bar file is one axis: left, middle, and right obliques plus the
# two inner orbits. The 70 goals are the C(8, 4) paired-bar placements, with
# the inners native. The slot of a bar does not matter.
PHASE8_PAIRED_TABLES_777 = (
    ("--ud-paired-cost", "lookup-tables/lookup-table-7x7x7-phase8-ud-paired-centers.cost-only.bin"),
    ("--fb-paired-cost", "lookup-tables/lookup-table-7x7x7-phase8-fb-paired-centers.cost-only.bin"),
)
# Native inners on one axis, 70 paired-bar goals on the other axis's obliques.
PHASE8_INNER_OBLIQUE_TABLES_777 = (
    (
        "--ud-inner-fb-obliques-cost",
        "lookup-tables/lookup-table-7x7x7-phase8-ud-inner-fb-obliques-centers.cost-only.bin",
    ),
    (
        "--fb-inner-ud-obliques-cost",
        "lookup-tables/lookup-table-7x7x7-phase8-fb-inner-ud-obliques-centers.cost-only.bin",
    ),
)
PHASE8_INNER_INTERACTION_TABLE_777 = (
    "--inner-interaction-cost",
    "lookup-tables/lookup-table-7x7x7-phase8-inner-interaction-centers.cost-only.bin",
)
PHASE8_TABLES_777 = (
    ("--ud-axis-cost", "lookup-tables/lookup-table-7x7x7-phase8-ud-axis-centers.cost-only.bin"),
    ("--fb-axis-cost", "lookup-tables/lookup-table-7x7x7-phase8-fb-axis-centers.cost-only.bin"),
    ("--lr-oblique-cost", "lookup-tables/lookup-table-7x7x7-phase8-lr-oblique-centers.cost-only.bin"),
    PHASE8_INNER_INTERACTION_TABLE_777,
    (
        "--middle-interaction-cost",
        "lookup-tables/lookup-table-7x7x7-phase8-middle-interaction-centers.cost-only.bin",
    ),
    (
        "--ud-obliques-fb-edges-cost",
        "lookup-tables/lookup-table-7x7x7-phase8-ud-obliques-fb-edges-centers.cost-only.bin",
    ),
    (
        "--fb-obliques-ud-edges-cost",
        "lookup-tables/lookup-table-7x7x7-phase8-fb-obliques-ud-edges-centers.cost-only.bin",
    ),
    (
        "--ud-obliques-fb-inner-t-cost",
        "lookup-tables/lookup-table-7x7x7-phase8-ud-obliques-fb-inner-t-centers.cost-only.bin",
    ),
)
PHASE9_TABLES_777 = tuple((flag, filename.replace("phase8-", "phase9-")) for flag, filename in PHASE8_TABLES_777)

# A wide quarter turn would move centers out of their orbit, so the daisy keeps the
# outer turns and the 2- and 3-wide half turns. This must match move_is_allowed() in
# ida_search_777_daisy_centers.c
DAISY_CENTERS_ILLEGAL_MOVES_777 = tuple(
    f"{prefix}{face}{suffix}" for prefix in ("", "3") for face in "ULFRBD" for suffix in ("w", "w'")
)

# Phase 8 drops the U/D/F/B 3-wide half turns because they split an LR bar and
# move LR inners between L and R. The L/R 3-wide half turns preserve phase 7
# and remain available to solve the UD/FB inners and pair those bars.
PHASE8_PRESERVE_ILLEGAL_MOVES_777 = (
    "3Uw2",
    "3Fw2",
    "3Bw2",
    "3Dw2",
)

# Phase 9 drops the L/R 3-wide half turns as well. No 3-wide move remains, so
# the phase 8 inners and paired bars stay put.
PHASE9_ILLEGAL_MOVES_777 = PHASE8_PRESERVE_ILLEGAL_MOVES_777 + (
    "3Lw2",
    "3Rw2",
)


class LookupTableIDA777DaisyCenters:
    """
    Phase 7, phase 8, then phase 9. Each axis has five C(8,4) center orbits -
    left, middle, and right obliques plus inner-t and inner-x - and outer-x is
    ignored.

    Phase 7 solves LR inner-t and inner-x in the native pattern and pairs the
    left/middle/right oblique bars on L and R. The slot of an LR oblique bar
    does not matter.
    LR centers are already staged, and no move still legal after that carries an
    LR oblique off L or R. Phase 7 uses the daisy move set. Its cost is
    ``DAISY_LR_INNER_TABLE_777``, which is exact for the two LR inner orbits.
    An LR oblique wing on L or R that does not match its bar's middle is unpaired.
    A move pairs at most four of those, so ceil(unpaired * 0.25) is a lower bound.
    The binary defaults to 0.40, which is not admissible. ``--unpaired-multiplier``
    overrides that default.
    Phase 7's cost is the max of that and the inner-table cost. The full
    daisy tables measure distance to a daisy, which can exceed the distance to
    this goal, so phase 7 does not probe them.

    Phase 8 solves the UD and FB inners and pairs the UD and FB oblique bars.
    A bar may sit on either face of its axis. Its moves are the outer turns,
    the 2-wide half turns, and the L/R 3-wide half turns, which keep the phase 7
    state. Cost is the max of ``PHASE8_PAIRED_TABLES_777``,
    ``PHASE8_INNER_OBLIQUE_TABLES_777``, and
    ``PHASE8_INNER_INTERACTION_TABLE_777``. Each paired file is the five orbits
    of one axis. Each inner-oblique file is one axis's inners plus the other
    axis's three oblique orbits. Those four have 70 goals. The inner-interaction
    file is the four UD/FB inner orbits. With the 70^5 files absent, 3Lw2
    repairs eight wings of one axis, so ceil(unpaired * 0.125) is a lower bound.
    The binary defaults to 0.20, which is not admissible. ``--unpaired-multiplier``
    overrides that default.
    The solver passes ``--multiplier 1.2``. ``native_only`` does not apply.
    Up to 16 distinct shortest phase 7 endings become phase 8 roots, and up to
    16 distinct shortest phase 8 endings become phase 9 roots.

    Phase 9 daisy-solves all six sides. It drops every 3-wide move, so the
    phase 8 inners stay solved and the bars stay paired. ``native_only`` applies
    here. ``do_phase9`` skips this search and defaults to true; NNNOdd sets it
    false on every cycle except the last of an orbit. Its cost is the max of
    ``PHASE9_TABLES_777``, with no multiplier.
    Those files are built for phase 9's smaller move set. Tables that include
    an oblique cost 0 at
    either daisy orientation; when ``native_only`` rejects the swapped
    orientation, a table cost of 0 is lifted to 1. Phase 7 does not use a
    multiplier either.

    Component tables

    | Set                                  | Tables | Selected by |
    | ------------------------------------ | ------ | ----------- |
    | DAISY_LR_INNER_TABLE_777             | 1      | phase 7     |
    | PHASE8_PAIRED_TABLES_777             | 2      | phase 8     |
    | PHASE8_INNER_OBLIQUE_TABLES_777      | 2      | phase 8     |
    | PHASE8_INNER_INTERACTION_TABLE_777   | 1      | phase 8     |
    | PHASE9_TABLES_777                    | 8      | phase 9     |
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . . L . L . .  . . . . . . .  . . R . R . .  . . . . . . .
    . . L L L . .  . . . . . . .  . . R R R . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .
    . . . . . . .  . . . . . . .  . . . . . . .  . . . . . . .

                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .
                   . . . . . . .

    lookup-table-7x7x7-daisy-lr-inner-centers.cost-only.bin
    =======================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 22 entries (0 percent, 5.50x previous step)
    3 steps has 82 entries (1 percent, 3.73x previous step)
    4 steps has 292 entries (5 percent, 3.56x previous step)
    5 steps has 986 entries (20 percent, 3.38x previous step)
    6 steps has 2,001 entries (40 percent, 2.03x previous step)
    7 steps has 1,312 entries (26 percent, 0.66x previous step)
    8 steps has 200 entries (4 percent, 0.15x previous step)

    Total: 4,900 entries
    Average: 5.96 moves
    """

    def __init__(self, parent, multiplier=None):
        self.parent = parent
        self.avoid_oll = None
        self.multiplier = multiplier

    def solve_via_c(self, native_only=False, portfolio_cap=None, distinct=True, do_phase9=True, **_kwargs):
        parent = self.parent
        portfolio_cap = DAISY_PORTFOLIO_CAP if portfolio_cap is None else portfolio_cap
        phase7 = self._solutions(
            7,
            [parent.get_kociemba_string(True)],
            solution_count=portfolio_cap,
            distinct=distinct,
        )
        roots8 = self._distinct_centers([steps for _root, steps in phase7])
        logger.info(
            "phase 7: %d shortest solutions, %d distinct phase-8 roots",
            len(phase7),
            len(roots8),
        )
        phase8 = self._solutions(
            8,
            [kociemba for _moves, kociemba in roots8],
            solution_count=portfolio_cap,
            distinct=distinct,
        )
        chains = [(roots8[root_index][0], steps) for root_index, steps in phase8]
        roots9 = self._distinct_phase9(chains)
        logger.info(
            "phase 8: %d shortest solutions, %d distinct phase-9 roots",
            len(phase8),
            len(roots9),
        )
        if do_phase9:
            phase9 = self._solutions(
                9,
                [kociemba for _phase7, _phase8, kociemba in roots9],
                native_only=native_only,
            )
            root_index, phase9_steps = phase9[0]
            phase7_steps, phase8_steps, _kociemba = roots9[root_index]
        else:
            phase7_steps, phase8_steps, _kociemba = roots9[0]
            phase9_steps = ()

        tmp_solution_len = len(parent.solution)
        for step in phase7_steps:
            parent.rotate(step)
        parent.print_cube_add_comment("LR inners solved, LR obliques paired", tmp_solution_len)
        tmp_solution_len = len(parent.solution)
        for step in phase8_steps:
            parent.rotate(step)
        parent.print_cube_add_comment("UD/FB inners solved, UD/FB obliques paired", tmp_solution_len)
        if do_phase9:
            tmp_solution_len = len(parent.solution)
            for step in phase9_steps:
                parent.rotate(step)
            parent.print_cube_add_comment("centers daisy solved", tmp_solution_len)

    def _solutions(self, phase, states, native_only=False, solution_count=None, distinct=True):
        roots_filename = None
        try:
            cmd = self._command(phase, native_only, solution_count=solution_count, distinct=distinct)
            if len(states) == 1:
                cmd.extend(("--kociemba", states[0]))
            else:
                with tempfile.NamedTemporaryFile(
                    mode="w", prefix="777-daisy-roots-", suffix=".txt", delete=False
                ) as fh:
                    roots_filename = fh.name
                    for index, kociemba in enumerate(states):
                        fh.write(f"{index},0,0,{kociemba}\n")
                cmd.extend(("--kociemba-file", roots_filename))
            output = self._run(cmd)
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

        self.parent.solve_via_c_output = output
        found = []
        root_index = 0
        for line in output.splitlines():
            if line.startswith("ROOT_INDEX "):
                root_index = int(line.split()[1])
            elif line.startswith("SOLUTION"):
                found.append((root_index, tuple(line.split(":", 1)[1].strip().split())))
        if not found:
            raise SolveError(f"ida_search_777_daisy_centers failed\n{output}")
        return found

    def _distinct_centers(self, move_lists):
        parent = self.parent
        original_state = parent.state[:]
        original_solution = parent.solution[:]
        seen = set()
        distinct = []
        try:
            for moves in move_lists:
                parent.state = original_state[:]
                parent.solution = original_solution[:]
                for step in moves:
                    parent.rotate(step)
                key = tuple(parent.state[square] for square in _DAISY_CENTER_SQUARES)
                if key in seen:
                    continue
                seen.add(key)
                distinct.append((tuple(moves), parent.get_kociemba_string(True)))
        finally:
            parent.state = original_state[:]
            parent.solution = original_solution[:]
        if not distinct:
            raise SolveError("daisy search produced no center states")
        return distinct

    def _distinct_phase9(self, chains):
        parent = self.parent
        original_state = parent.state[:]
        original_solution = parent.solution[:]
        seen = set()
        distinct = []
        try:
            for phase7_steps, phase8_steps in chains:
                parent.state = original_state[:]
                parent.solution = original_solution[:]
                for step in phase7_steps + phase8_steps:
                    parent.rotate(step)
                key = tuple(parent.state[square] for square in _DAISY_CENTER_SQUARES)
                if key in seen:
                    continue
                seen.add(key)
                distinct.append((phase7_steps, phase8_steps, parent.get_kociemba_string(True)))
        finally:
            parent.state = original_state[:]
            parent.solution = original_solution[:]
        if not distinct:
            raise SolveError("phase 8 produced no phase-9 states")
        return distinct

    def _command(self, phase, native_only, solution_count=None, distinct=True):
        cmd = ["./ida_search_777_daisy_centers", f"--phase{phase}"]
        if phase == 7:
            flag, filename = DAISY_LR_INNER_TABLE_777
            download_file_if_needed(filename)
            cmd.extend((flag, filename))
        elif phase == 8:
            tables = PHASE8_PAIRED_TABLES_777 + PHASE8_INNER_OBLIQUE_TABLES_777 + (PHASE8_INNER_INTERACTION_TABLE_777,)
            for flag, filename in tables:
                download_file_if_needed(filename)
                cmd.extend((flag, filename))
            cmd.extend(("--multiplier", str(PHASE8_MULTIPLIER)))
        elif phase == 9:
            for flag, filename in PHASE9_TABLES_777:
                download_file_if_needed(filename)
                cmd.extend((flag, filename))
            if self.multiplier:
                cmd.extend(("--multiplier", str(self.multiplier)))
            if native_only:
                cmd.append("--native-only")
        if solution_count is not None:
            cmd.extend(("--solution-count", str(solution_count)))
            if not distinct:
                cmd.append("--allow-duplicate-solutions")
        return cmd

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
    # Larger odd cubes set this so a ring with real outer x still stages them.
    stage_outer_x_centers = False
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

    - phase 7 solves LR inner-t and inner-x and pairs the LR oblique bars
    - phase 8 solves the UD and FB inners and pairs the UD and FB oblique bars
    - phase 9 daisy-solves all six sides with no 3-wide move

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

        # phase 2 - stage UD inner centers and pair LR obliques
        self.lt_LR_oblique_edges_UD_inner_centers_stage = LookupTableIDA777LRObliqueEdgesUDInnerCentersStage(self)

        # Phase 3 and everything after it only turns the outer orbit, so no
        # 3Xw quarter turn survives past phase 2 and it is the last chance to
        # fix orbit1 parity. Orbit0 is handled by phase 6, the fake 5x5x5 FB
        # center stage.
        self.lt_LR_oblique_edges_UD_inner_centers_stage.avoid_oll = 1

        # phase 5 pairs UD oblique bars; phase 6 stages the outside centers
        self.lt_UD_obliques_outer_x_stage = LookupTableIDA777UDObliquesOuterXStage(self)
        self.lt_UD_obliques_outer_x_stage.avoid_oll = 0

        # phase 7 pairs LR bars and solves the LR inners; phase 8 does the same
        # for UD and FB; phase 9 daisy-solves with no 3-wide move
        self.lt_daisy_centers = LookupTableIDA777DaisyCenters(self)

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

    def LR_obliques_staged(self) -> bool:
        """True when every L/R-face left, middle, and right oblique is L or R."""
        for square in left_oblique_edges_777 + right_oblique_edges_777 + outer_t_centers_777:
            on_lr = 50 <= square <= 98 or 148 <= square <= 196
            if on_lr and self.state[square] not in ("L", "R"):
                return False
        return True

    def LR_outer_x_staged(self) -> bool:
        """True when every L/R-face outer x-center is L or R."""
        for square in outer_x_centers_777:
            on_lr = 50 <= square <= 98 or 148 <= square <= 196
            if on_lr and self.state[square] not in ("L", "R"):
                return False
        return True

    def UD_obliques_paired(self) -> bool:
        """True when every UD oblique bar has U or D wings, on whichever UFBD face holds it."""
        for left, middle, right in zip(LR_LEFT_OBLIQUES_777, LR_MIDDLE_OBLIQUES_777, LR_RIGHT_OBLIQUES_777):
            if self.state[middle] in ("U", "D"):
                if self.state[left] not in ("U", "D") or self.state[right] not in ("U", "D"):
                    return False
        return True

    def UD_obliques_staged(self) -> bool:
        """True when the UD left, middle, and right obliques sit on U and D."""
        return self._ud_colors_staged(UFBD_oblique_edges_777)

    def UD_outer_x_staged(self) -> bool:
        """True when the UD outer x-centers sit on U and D."""
        return self._ud_colors_staged(UFBD_outer_x_centers_777)

    def _ud_colors_staged(self, squares) -> bool:
        for square in squares:
            on_ud = square <= 49 or square >= 246
            if on_ud != (self.state[square] in ("U", "D")):
                return False
        return True

    def _phase5_root_key(self, orbits_with_oll):
        """Folded UD oblique and outer-x colors, plus the orbit-0 requirement."""

        def fold(color):
            if color == "R":
                return "L"
            if color == "D":
                return "U"
            if color == "B":
                return "F"
            return color

        colors = "".join(fold(self.state[square]) for square in UFBD_oblique_edges_777 + UFBD_outer_x_centers_777)
        return (colors, 0 in orbits_with_oll)

    def _distinct_phase5_roots(self, portfolio):
        """Phase-3 solutions that leave a different phase-5 state, as ``(steps, kociemba, orbits)``."""
        original_state = self.state[:]
        original_solution = self.solution[:]
        distinct = []
        seen = set()
        for steps in portfolio:
            self.state = original_state[:]
            self.solution = original_solution[:]
            for step in steps:
                self.rotate(step)
            orbits = self.center_solution_leads_to_oll_parity()
            key = self._phase5_root_key(orbits)
            if key in seen:
                continue
            seen.add(key)
            distinct.append((steps, self.get_kociemba_string(True), orbits))
        self.state = original_state[:]
        self.solution = original_solution[:]
        return distinct

    def LR_oblique_pair_count(self) -> int:
        """Return how many LR oblique slots are paired, matching the C unpaired count."""
        paired = 0
        for left, middle, right in zip(LR_LEFT_OBLIQUES_777, LR_MIDDLE_OBLIQUES_777, LR_RIGHT_OBLIQUES_777):
            if self.state[middle] in ("L", "R"):
                if self.state[left] in ("L", "R"):
                    paired += 1
                if self.state[right] in ("L", "R"):
                    paired += 1
        return paired

    def _map_555_center_step_to_777(self, step):
        if step.startswith("COMMENT"):
            return None
        if step.startswith("5"):
            return "7" + step[1:]
        if step.startswith("3"):
            raise Exception("5x5x5 solution has 3 wide turn")
        if "w" in step:
            return "3" + step
        return step

    def _phase2_root_key(self, orbits_with_oll):
        """Colors the phase-2 heuristic reads, plus the orbit-1 requirement."""

        def inner_color(color):
            if color == "R":
                return "L"
            if color == "D":
                return "U"
            if color == "B":
                return "F"
            return color

        def oblique_color(color):
            return "L" if color in ("L", "R") else "x"

        inner = "".join(
            inner_color(self.state[square]) for square in UFBD_inner_t_centers_777 + UFBD_inner_x_centers_777
        )
        obliques = "".join(
            oblique_color(self.state[square])
            for square in LR_LEFT_OBLIQUES_777 + LR_MIDDLE_OBLIQUES_777 + LR_RIGHT_OBLIQUES_777
        )
        return (inner, obliques, 1 in orbits_with_oll)

    def _inside_lr_center_solutions(self):
        """Every distinct shortest phase-1 ending, as ``(steps, kociemba, orbits)``."""
        if self.LR_inside_centers_staged():
            orbits = self.center_solution_leads_to_oll_parity()
            return [((), self.get_kociemba_string(True), orbits)]

        self.create_fake_555_from_inside_centers()
        solutions = self.fake_555.lt_LR_centers_stage.solutions_via_c(solution_count=0)
        original_state = self.state[:]
        original_solution = self.solution[:]
        portfolio = []
        seen = set()
        for steps, _centers in solutions:
            self.state = original_state[:]
            self.solution = original_solution[:]
            mapped = []
            for step in steps:
                mapped_step = self._map_555_center_step_to_777(step)
                if mapped_step:
                    self.rotate(mapped_step)
                    mapped.append(mapped_step)
            orbits = self.center_solution_leads_to_oll_parity()
            key = self._phase2_root_key(orbits)
            if key in seen:
                continue
            seen.add(key)
            portfolio.append((tuple(mapped), self.get_kociemba_string(True), orbits))

        self.state = original_state[:]
        self.solution = original_solution[:]
        logger.info(
            "phase 1: %d shortest solutions, %d distinct phase-2 roots",
            len(solutions),
            len(portfolio),
        )
        if not portfolio:
            raise SolveError("phase 1 found no LR inner-center solutions")
        return portfolio

    def group_inside_LR_centers(self):
        if self.LR_inside_centers_staged():
            return

        self.create_fake_555_from_inside_centers()
        solutions = self.fake_555.lt_LR_centers_stage.solutions_via_c(solution_count=0)
        original_state = self.state[:]
        original_solution = self.solution[:]
        best_steps = None
        best_paired = -1
        for steps, _ in solutions:
            self.state = original_state[:]
            self.solution = original_solution[:]
            mapped = []
            for step in steps:
                mapped_step = self._map_555_center_step_to_777(step)
                if mapped_step:
                    self.rotate(mapped_step)
                    mapped.append(mapped_step)
            paired = self.LR_oblique_pair_count()
            if paired > best_paired:
                best_paired = paired
                best_steps = mapped

        self.state = original_state[:]
        self.solution = original_solution[:]
        for step in best_steps:
            self.rotate(step)
        logger.info(
            "group_inside_LR_centers: chose 1 of %d shortest solutions with %d/16 LR oblique pairs",
            len(solutions),
            best_paired,
        )

    def stage_LR_centers(self):
        """
        phase 1 - use 5x5x5 solver to stage the LR inner centers
        phase 2 - stage UD inner centers and pair LR oblique edges, searching
        every distinct phase-1 ending and keeping the first one that solves
        phase 3 - collect every shortest LR oblique and outer-x staging; phase 5
        chooses which one to apply
        """
        if self.stage_outer_x_centers:
            if self.LR_centers_staged() and self.UD_inside_centers_staged():
                return
        elif (
            self.LR_inside_centers_staged()
            and self.UD_inside_centers_staged()
            and self.LR_obliques_staged()
            and self.LR_outer_x_staged()
        ):
            return

        # phase 1 endings are the roots of one phase-2 search. The winning
        # root's phase-1 moves are applied, then the phase-2 solution.
        tmp_solution_len = len(self.solution)
        portfolio = self._inside_lr_center_solutions()
        roots = [(index, kociemba, orbits) for index, (_steps, kociemba, orbits) in enumerate(portfolio)]
        root_index, phase2_steps = self.lt_LR_oblique_edges_UD_inner_centers_stage.solution_via_c(
            roots, root_cap=PHASE1_ROOT_CAP
        )
        for step in portfolio[root_index][0]:
            self.rotate(step)
        self.print_cube_add_comment("LR inner centers staged", tmp_solution_len)

        tmp_solution_len = len(self.solution)
        for step in phase2_steps:
            self.rotate(step)
        self.print_cube_add_comment("UD inner centers staged, LR oblique edges paired", tmp_solution_len)

        # phase 3 - stage LR obliques and outer x, or the full outer LR centers
        # when this ring's outer x are real
        tmp_solution_len = len(self.solution)
        if self.stage_outer_x_centers:
            self.create_fake_555_from_outside_centers()
            fake_555 = self.fake_555
            if not fake_555.LR_centers_staged():
                tmp_555_len = len(fake_555.solution)
                fake_555.lt_LR_centers_stage.solve_via_c()
                fake_555.print_cube_add_comment("LR centers staged", tmp_555_len)

            for step in fake_555.solution:
                if step.startswith("COMMENT"):
                    pass
                else:
                    if step.startswith("5"):
                        step = "7" + step[1:]
                    elif step.startswith("3"):
                        raise Exception("5x5x5 solution has 3 wide turn")
                    self.rotate(step)
            self.print_cube_add_comment("LR centers staged", tmp_solution_len)
        else:
            self._phase3_portfolio = self._phase3_solutions()

    # UD centers
    def UD_inside_centers_staged(self):
        state = self.state

        for x in UD_inside_centers_777:
            if state[x] not in ("U", "D"):
                return False
        return True

    def _stage_outside_centers_via_555(self):
        """Phase 6. Replay 5x5 phase 2 on the outside centers, keeping orbit-0 from this cube."""
        self.create_fake_555_from_outside_centers()
        fake = self.fake_555
        original_parity = fake.center_solution_leads_to_oll_parity
        fake.center_solution_leads_to_oll_parity = self.center_solution_leads_to_oll_parity
        solution_len = len(fake.solution)
        try:
            fake.lt_FB_centers_stage.solve_via_c()
        finally:
            fake.center_solution_leads_to_oll_parity = original_parity
        for step in fake.solution[solution_len:]:
            if step.startswith("COMMENT"):
                continue
            if step.startswith("5"):
                step = "7" + step[1:]
            elif step.startswith("3"):
                raise Exception("5x5x5 solution has 3 wide turn")
            self.rotate(step)

    def _pair_ud_obliques_and_stage(self, roots=None, phase3_steps=None):
        """Phase 5 then phase 6. ``roots`` selects which phase-3 ending to apply first."""
        if roots:
            root_index, pair_steps = self.lt_UD_obliques_outer_x_stage.stage_obliques_via_c(roots)
            tmp_solution_len = len(self.solution)
            for step in phase3_steps[root_index]:
                self.rotate(step)
            self.print_cube_add_comment("LR obliques and outer x staged", tmp_solution_len)
        elif self.UD_obliques_staged():
            pair_steps = ()
        else:
            _root_index, pair_steps = self.lt_UD_obliques_outer_x_stage.stage_obliques_via_c()

        tmp_solution_len = len(self.solution)
        for step in pair_steps:
            self.rotate(step)
        if pair_steps:
            self.print_cube_add_comment("UD obliques staged", tmp_solution_len)
        if not self.UD_obliques_staged():
            raise SolveError("phase 5 did not stage the UD oblique bars")

        tmp_solution_len = len(self.solution)
        self._stage_outside_centers_via_555()
        self.print_cube_add_comment("UD centers staged", tmp_solution_len)
        if not self.UD_centers_staged():
            raise SolveError("phase 6 did not stage the UD centers")
        if not self.UD_obliques_paired():
            raise SolveError("phase 6 split the UD oblique bars")

    def _stage_ud_with_cascade(self, roots=None, phase3_steps=None):
        """Try the six-table phase 5, then oblique staging plus 5x5 phase 2."""
        found = self.lt_UD_obliques_outer_x_stage.solution_via_c(
            roots,
            admissible_seconds=PHASE56_ADMISSIBLE_CAP,
            matrix_seconds=PHASE56_MATRIX_CAP,
        )
        if found is not None:
            root_index, steps = found
            if phase3_steps:
                tmp_solution_len = len(self.solution)
                for step in phase3_steps[root_index]:
                    self.rotate(step)
                self.print_cube_add_comment("LR obliques and outer x staged", tmp_solution_len)
            tmp_solution_len = len(self.solution)
            for step in steps:
                self.rotate(step)
            self.print_cube_add_comment("UD centers staged", tmp_solution_len)
            return

        logger.info(
            "phase 5 timed out after %.0fs admissible and %.0fs with the matrix; staging obliques then 5x5 phase 2",
            PHASE56_ADMISSIBLE_CAP,
            PHASE56_MATRIX_CAP,
        )
        self._pair_ud_obliques_and_stage(roots, phase3_steps)

    def stage_UD_centers(self):
        if self.stage_outer_x_centers:
            if self.UD_centers_staged():
                return
            self._stage_ud_with_cascade()
            return

        portfolio = getattr(self, "_phase3_portfolio", None)
        if portfolio is None:
            if self.UD_centers_staged():
                return
            self._stage_ud_with_cascade()
            return

        self._phase3_portfolio = None
        distinct = self._distinct_phase5_roots(portfolio)
        if not distinct:
            raise SolveError("phase 3 found no LR oblique and outer-x solutions")
        logger.info(
            "phase 3: %d shortest solutions, %d distinct phase-5 roots",
            len(portfolio),
            len(distinct),
        )
        roots = [(index, kociemba, orbits) for index, (_steps, kociemba, orbits) in enumerate(distinct)]
        phase3_steps = [steps for steps, _kociemba, _orbits in distinct]
        self._stage_ud_with_cascade(roots, phase3_steps)

    def _phase3_solutions(self, solution_cap=None):
        """Every shortest phase-3 solution, without applying one."""
        solution_cap = PHASE3_SOLUTION_CAP if solution_cap is None else solution_cap
        cmd = [
            "./ida_search_777_centers_stage",
            "--kociemba",
            self.get_kociemba_string(True),
            "--stage-lr-obliques",
            "--solution-count",
            str(solution_cap),
        ]
        if 0 in self.center_solution_leads_to_oll_parity():
            cmd.append("--initial-orbit0-odd")
        logger.info("phase 3: solving via C\n%s", " ".join(cmd))
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            output, _stderr = proc.communicate()
        output = output or ""
        for line in output.splitlines():
            logger.info("%s", line)
        self.solve_via_c_output = output
        solutions = []
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                solutions.append(tuple(line.split(":", 1)[1].strip().split()))
        if not solutions:
            raise SolveError(f"ida_search_777_centers_stage --stage-lr-obliques failed\n{output}")
        logger.info("phase 3: %d shortest solutions", len(solutions))
        return solutions

    def centers_combined_daisy_solve(self, native_only=False, do_phase9=True):
        self.lt_daisy_centers.solve_via_c(native_only=native_only, do_phase9=do_phase9)

    def reduce_555(self):
        self.lt_init()
        self.stage_LR_centers()
        self.stage_UD_centers()
        self.centers_combined_daisy_solve()


def rotate_777(cube, step):
    return [cube[x] for x in swaps_777[step]]
