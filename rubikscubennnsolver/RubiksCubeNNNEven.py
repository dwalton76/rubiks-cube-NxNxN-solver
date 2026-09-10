"""
Even NxNxN solver (8x8x8 and up): turn the cube into an odd cube, then reuse
the odd NxNxN solver.

``RubiksCubeNNNEven`` inherits ``RubiksCubeNNNEvenEdges`` and is a sibling of
``RubiksCube666``. Plus-sign staging uses 6x6x6 lookup tables that the 6x6x6
solver itself does not use; those tables live here.

``reduce_555``:
    1. ``make_plus_sign`` maps each inner center orbit onto a fake 6x6x6 and
       stages/daisy-solves it. That pairs the middle two rows and columns of
       every face, leaving a plus sign of already-reduced stickers.
    2. ``pair_inside_edges_via_444`` pairs the innermost wing orbit (and avoids
       PLL) by copying those wings onto a fake 4x4x4.
    3. Drop the middle row and column of each face to build a ``RubiksCubeNNNOdd``
       of size N-1 and ``solve()`` it. That odd cube stages its remaining
       centers via 7x7x7 orbits and pairs the rest of the wings via 5x5x5.

``group_edges`` (on ``RubiksCubeNNNEvenEdges``) then pairs any outer wing
orbits that the odd reduction did not already pair, again via a fake 5x5x5,
inside to outside. ``solve_333`` finishes the cube.
"""

# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver.LookupTable import LookupTable
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.RubiksCube666 import (
    RubiksCube666,
    UFBD_inner_x_centers_666,
    UFBD_left_oblique_edges_666,
    UFBD_right_oblique_edges_666,
    centers_666,
    inner_x_centers_666,
    moves_666,
    oblique_edges_666,
    solved_666,
)
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges
from rubikscubennnsolver.RubiksCubeNNNOdd import RubiksCubeNNNOdd

logger = logging.getLogger(__name__)

solved_888 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
solved_101010 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
solved_121212 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
solved_141414 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

# fmt: off
moves_8x8x8 = (
    "U", "U'", "U2",
    "Uw", "Uw'", "Uw2",
    "3Uw", "3Uw'", "3Uw2",
    "4Uw", "4Uw'", "4Uw2",

    "L", "L'", "L2",
    "Lw", "Lw'", "Lw2",
    "3Lw", "3Lw'", "3Lw2",
    "4Lw", "4Lw'", "4Lw2",

    "F", "F'", "F2",
    "Fw", "Fw'", "Fw2",
    "3Fw", "3Fw'", "3Fw2",
    "4Fw", "4Fw'", "4Fw2",

    "R", "R'", "R2",
    "Rw", "Rw'", "Rw2",
    "3Rw", "3Rw'", "3Rw2",
    "4Rw", "4Rw'", "4Rw2",

    "B", "B'", "B2",
    "Bw", "Bw'", "Bw2",
    "3Bw", "3Bw'", "3Bw2",
    "4Bw", "4Bw'", "4Bw2",

    "D", "D'", "D2",
    "Dw", "Dw'", "Dw2",
    "3Dw", "3Dw'", "3Dw2",
    "4Dw", "4Dw'", "4Dw2",
)

moves_10x10x10 = (
    "U", "U'", "U2",
    "Uw", "Uw'", "Uw2",
    "3Uw", "3Uw'", "3Uw2",
    "4Uw", "4Uw'", "4Uw2",
    "5Uw", "5Uw'", "5Uw2",

    "L", "L'", "L2",
    "Lw", "Lw'", "Lw2",
    "3Lw", "3Lw'", "3Lw2",
    "4Lw", "4Lw'", "4Lw2",
    "5Lw", "5Lw'", "5Lw2",

    "F", "F'", "F2",
    "Fw", "Fw'", "Fw2",
    "3Fw", "3Fw'", "3Fw2",
    "4Fw", "4Fw'", "4Fw2",
    "5Fw", "5Fw'", "5Fw2",

    "R", "R'", "R2",
    "Rw", "Rw'", "Rw2",
    "3Rw", "3Rw'", "3Rw2",
    "4Rw", "4Rw'", "4Rw2",
    "5Rw", "5Rw'", "5Rw2",

    "B", "B'", "B2",
    "Bw", "Bw'", "Bw2",
    "3Bw", "3Bw'", "3Bw2",
    "4Bw", "4Bw'", "4Bw2",
    "5Bw", "5Bw'", "5Bw2",

    "D", "D'", "D2",
    "Dw", "Dw'", "Dw2",
    "3Dw", "3Dw'", "3Dw2",
    "4Dw", "4Dw'", "4Dw2",
    "5Dw", "5Dw'", "5Dw2",
)
# fmt: on


# fmt: off
UD_STAGE_ILLEGAL_MOVES = (
    # keep LR staged; do not turn L or R
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
)
# fmt: on


# ==================================================
# plus-sign staging (even cubes larger than 6x6)
# stage LR inner x-centers and pair the LR obliques
# ==================================================
class LookupTable666LRInnerXCentersStage(LookupTable):
    """
    24! / (8! * 16!) = 735,471 states

                 . . . . . .
                 . . . . . .
                 . . x x . .
                 . . x x . .
                 . . . . . .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . L L . .  . . x x . .  . . L L . .  . . x x . .
    . . L L . .  . . x x . .  . . L L . .  . . x x . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . . . . . .
                 . . x x . .
                 . . x x . .
                 . . . . . .
                 . . . . . .

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

        for pos, pos_state in zip(inner_x_centers_666, state):
            cube[pos] = pos_state


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


# ==================================================
# plus-sign staging (even cubes larger than 6x6)
# stage UD inner x-centers and pair the UD obliques
# ==================================================
class LookupTable666UDInnerXCentersStage(LookupTable):
    """
    16! / (8! * 8!) = 12,870 states

                 . . . . . .
                 . . . . . .
                 . . U U . .
                 . . U U . .
                 . . . . . .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . x x . .  . . . . . .  . . x x . .
    . . . . . .  . . x x . .  . . . . . .  . . x x . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . . . . . .
                 . . U U . .
                 . . U U . .
                 . . . . . .
                 . . . . . .

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
            illegal_moves=UD_STAGE_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_inner_x_centers_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UFBD_inner_x_centers_666, state):
            cube[pos] = pos_state


class LookupTable666UDLeftObliqueCentersStage(LookupTable):
    """
    16! / (8! * 8!) = 12,870 states

                 . . . . . .
                 . . U . . .
                 . . . . U .
                 . U . . . .
                 . . . U . .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . x . . .  . . . . . .  . . x . . .
    . . . . . .  . . . . x .  . . . . . .  . . . . x .
    . . . . . .  . x . . . .  . . . . . .  . x . . . .
    . . . . . .  . . . x . .  . . . . . .  . . . x . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . . U . . .
                 . . . . U .
                 . U . . . .
                 . . . U . .
                 . . . . . .

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
            illegal_moves=UD_STAGE_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_left_oblique_edges_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UFBD_left_oblique_edges_666, state):
            cube[pos] = pos_state


class LookupTable666UDRightObliqueCentersStage(LookupTable):
    """
    16! / (8! * 8!) = 12,870 states

                 . . . . . .
                 . . . U . .
                 . U . . . .
                 . . . . U .
                 . . U . . .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . . x . .  . . . . . .  . . . x . .
    . . . . . .  . x . . . .  . . . . . .  . x . . . .
    . . . . . .  . . . . x .  . . . . . .  . . . . x .
    . . . . . .  . . x . . .  . . . . . .  . . x . . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . . . U . .
                 . U . . . .
                 . . . . U .
                 . . U . . .
                 . . . . . .

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
            illegal_moves=UD_STAGE_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )
    # fmt: on

    def state(self):
        return "".join(["U" if self.parent.state[x] in ("U", "D") else "x" for x in UFBD_right_oblique_edges_666])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(UFBD_right_oblique_edges_666, state):
            cube[pos] = pos_state


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
            illegal_moves=UD_STAGE_ILLEGAL_MOVES,
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


def lt_init_plus_sign(cube: RubiksCube666) -> None:
    """Load plus-sign tables onto a fake 6x6x6 used by even cubes larger than 6x6."""
    if getattr(cube, "lt_LR_oblique_edge_stage_inner_x_stage", None) is not None:
        return

    cube.lt_LR_inner_x_centers_stage = LookupTable666LRInnerXCentersStage(cube)
    cube.lt_LR_oblique_edge_stage_inner_x_stage = LookupTable666LRObliquEdgeStageInnerXStage(cube)
    cube.lt_UD_inner_x_centers_stage = LookupTable666UDInnerXCentersStage(cube)
    cube.lt_UD_left_oblique_edges_stage = LookupTable666UDLeftObliqueCentersStage(cube)
    cube.lt_UD_right_oblique_edges_stage = LookupTable666UDRightObliqueCentersStage(cube)
    cube.lt_UD_oblique_edge_inner_x_center_stage = LookupTable666UDObliquEdgeInnerXCentersStage(cube)
    cube.lt_UD_oblique_edge_inner_x_center_stage.avoid_oll = (0, 1)


def stage_t_centers(cube: RubiksCube666) -> None:
    """
    Used by RubiksCubeNNNEven.make_plus_sign

    - pair LR inner x-centers and pair oblique edges (9 moves)
    - stage LR t-centers (6 moves)
    - stage the UD oblique edges and inner x-centers
    """
    lt_init_plus_sign(cube)

    tmp_solution_len = len(cube.solution)
    cube.lt_LR_oblique_edge_stage_inner_x_stage.solve_via_c(use_kociemba_string=True)
    cube.print_cube_add_comment("LR inner x-centers staged, oblique edges paired", tmp_solution_len)

    fake_555 = cube.get_fake_555()
    cube.populate_fake_555_for_ULFRBD_solve()
    tmp_solution_len = len(cube.solution)
    fake_555.lt_LR_t_centers_stage_ida.solve_via_c()

    for step in fake_555.solution:
        if not step.startswith("COMMENT"):
            cube.rotate(step)

    cube.print_cube_add_comment("LR t-centers staged", tmp_solution_len)

    tmp_solution_len = len(cube.solution)
    cube.lt_UD_oblique_edge_inner_x_center_stage.solve_via_c()
    cube.print_cube_add_comment("UD t-centers staged", tmp_solution_len)


def daisy_solve_centers(cube: RubiksCube666) -> None:
    """Daisy-solve staged 6x6x6 centers without EO'ing the inside wings."""
    tmp_solution_len = len(cube.solution)
    cube.lt_step50_without_edges.solve_via_c()
    cube.print_cube_add_comment("LR centers reduced to 5x5x5", tmp_solution_len)

    tmp_solution_len = len(cube.solution)
    cube.lt_UFBD_solve_inner_x_centers_and_oblique_edges.solve_via_c()
    cube.print_cube_add_comment("UD FB centers reduced to 5x5x5", tmp_solution_len)


class RubiksCubeNNNEven(RubiksCubeNNNEvenEdges):
    """
    Even cubes 8x8x8 and larger. A fake 6x6x6 builds a plus sign so the cube can
    be treated as odd; a fake 4x4x4 pairs the inside wings; then
    ``RubiksCubeNNNOdd`` finishes the reduction. See the module docstring.

    Inheritance model
    -----------------

            RubiksCube
                |
        RubiksCubeNNNEvenEdges
           /            \
    RubiksCubeNNNEven RubiksCube666
    """

    def get_fake_666(self):
        if self.fake_666 is None:
            self.fake_666 = RubiksCube666(solved_666, "URFDLB")
            self.fake_666.lt_init()
            self.fake_666.enable_print_cube = False
        else:
            self.fake_666.re_init()

        if self.fake_555:
            self.fake_666.fake_555 = self.fake_555

        return self.fake_666

    def make_plus_sign(self):
        """
        Pair the middle two columns/rows in order to convert this Even cube into an Odd cube...this
        allows us to use the RubiksCubeNNNOdd solver later.  It makes what looks like a large "plus"
        sign on each cube face thus the name of this method.
        """
        center_orbit_count = int((self.size - 4) / 2)
        side_name = {0: "U", 1: "L", 2: "F", 3: "R", 4: "B", 5: "D"}
        original_solution_len = len(self.solution)
        max_center_orbit_id = center_orbit_count - 1

        # Make a big "plus" sign on each side
        for center_orbit_id in range(center_orbit_count):
            # create a fake 6x6x6 to solve the inside 4x4 block
            fake_666 = self.get_fake_666()

            for index in range(1, 217):
                fake_666.state[index] = "x"

            start_666 = 0
            start_NNN = 0

            for x in range(6):
                start_NNN_row1 = int(start_NNN + (((self.size / 2) - 2) * self.size) + ((self.size / 2) - 1))
                start_NNN_row2 = start_NNN_row1 + self.size
                start_NNN_row3 = start_NNN_row2 + self.size
                start_NNN_row4 = start_NNN_row3 + self.size

                # centers
                fake_666.state[start_666 + 8] = side_name[x]
                fake_666.state[start_666 + 9] = self.state[start_NNN_row1 + 1 - (center_orbit_id * self.size)]
                fake_666.state[start_666 + 10] = self.state[start_NNN_row1 + 2 - (center_orbit_id * self.size)]
                fake_666.state[start_666 + 11] = side_name[x]

                fake_666.state[start_666 + 14] = self.state[start_NNN_row2 - center_orbit_id]
                fake_666.state[start_666 + 15] = self.state[start_NNN_row2 + 1]
                fake_666.state[start_666 + 16] = self.state[start_NNN_row2 + 2]
                fake_666.state[start_666 + 17] = self.state[start_NNN_row2 + 3 + center_orbit_id]

                fake_666.state[start_666 + 20] = self.state[start_NNN_row3 - center_orbit_id]
                fake_666.state[start_666 + 21] = self.state[start_NNN_row3 + 1]
                fake_666.state[start_666 + 22] = self.state[start_NNN_row3 + 2]
                fake_666.state[start_666 + 23] = self.state[start_NNN_row3 + 3 + center_orbit_id]

                fake_666.state[start_666 + 26] = side_name[x]
                fake_666.state[start_666 + 27] = self.state[start_NNN_row4 + 1 + (center_orbit_id * self.size)]
                fake_666.state[start_666 + 28] = self.state[start_NNN_row4 + 2 + (center_orbit_id * self.size)]
                fake_666.state[start_666 + 29] = side_name[x]

                # edges
                # top edge
                edge03 = start_NNN + center_orbit_count + 2
                edge04 = edge03 + 1
                edge05 = edge03 + 2
                edge02 = edge03 - 1
                fake_666.state[start_666 + 2] = self.state[edge02]
                fake_666.state[start_666 + 3] = self.state[edge03]
                fake_666.state[start_666 + 4] = self.state[edge04]
                fake_666.state[start_666 + 5] = self.state[edge05]

                # left_edge
                edge13 = start_NNN + ((center_orbit_count + 1) * self.size) + 1
                edge19 = edge13 + self.size
                edge07 = edge13 - self.size
                edge25 = edge19 + self.size
                fake_666.state[start_666 + 7] = self.state[edge07]
                fake_666.state[start_666 + 13] = self.state[edge13]
                fake_666.state[start_666 + 19] = self.state[edge19]
                fake_666.state[start_666 + 25] = self.state[edge25]

                # right edge
                edge18 = edge13 + self.size - 1
                edge24 = edge18 + self.size
                edge12 = edge18 - self.size
                edge30 = edge24 + self.size
                fake_666.state[start_666 + 12] = self.state[edge12]
                fake_666.state[start_666 + 18] = self.state[edge18]
                fake_666.state[start_666 + 24] = self.state[edge24]
                fake_666.state[start_666 + 30] = self.state[edge30]

                # bottom edge
                edge33 = start_NNN + (self.size * self.size) - center_orbit_count - 2
                edge34 = edge33 + 1
                edge35 = edge33 + 2
                edge32 = edge33 - 1
                fake_666.state[start_666 + 32] = self.state[edge32]
                fake_666.state[start_666 + 33] = self.state[edge33]
                fake_666.state[start_666 + 34] = self.state[edge34]
                fake_666.state[start_666 + 35] = self.state[edge35]

                # corners
                corner01 = start_NNN + 1
                corner06 = corner01 + self.size - 1
                corner36 = start_NNN + (self.size * self.size)
                corner31 = corner36 - self.size + 1
                fake_666.state[start_666 + 1] = self.state[corner01]
                fake_666.state[start_666 + 6] = self.state[corner06]
                fake_666.state[start_666 + 31] = self.state[corner31]
                fake_666.state[start_666 + 36] = self.state[corner36]

                start_666 += 36
                start_NNN += self.size * self.size

            # reduce the centers to 5x5x5 centers
            stage_t_centers(fake_666)

            if center_orbit_id == max_center_orbit_id:
                fake_666.daisy_solve_centers_eo_edges()
            else:
                daisy_solve_centers(fake_666)

            # Apply the 6x6x6 solution to our cube
            half_size = str(int(self.size / 2))
            wide_size = str(int(half_size) - 1 - center_orbit_id)

            for step in fake_666.solution:
                if step.startswith("COMMENT"):
                    self.solution.append(step)
                elif step.startswith("3"):
                    self.rotate(half_size + step[1:])
                elif "w" in step:
                    self.rotate(wide_size + step)
                else:
                    self.rotate(step)

        fake_666 = None

        if len(self.solution) > original_solution_len:
            self.print_cube(
                "%s: Big plus sign formed (%d steps in)" % (self, self.get_solution_len_minus_rotates(self.solution))
            )

    def reduce_555(self):
        # Reduce this even cube to an odd cube
        tmp_solution_len = len(self.solution)
        self.make_plus_sign()
        self.pair_inside_edges_via_444()
        self.print_cube_add_comment("NNN even reduced to NNN odd cube", tmp_solution_len)

        # create a state string we can use to create the reduced NNN odd cube
        kociemba_string = []
        midpoint = int(self.size / 2)

        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for row in range(self.size):
                if row == midpoint:
                    continue

                for col in range(self.size):
                    if col == midpoint:
                        continue
                    pos = side.min_pos + ((row * self.size) + col)
                    kociemba_string.append(self.state[pos])

        fake_odd = RubiksCubeNNNOdd("".join(kociemba_string), "ULFRBD")
        fake_odd.print_cube("NNN odd cube")
        fake_odd.solve()

        for step in fake_odd.solution:
            self.rotate(step)
