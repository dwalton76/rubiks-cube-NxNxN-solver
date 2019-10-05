from rubikscubennnsolver.misc import SolveError
from rubikscubennnsolver.RubiksCubeNNNOddEdges import RubiksCubeNNNOddEdges
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableIDAViaC,
)
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
import logging
import sys

log = logging.getLogger(__name__)


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

ULRD_centers_777 = (
    9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41,  # Upper
    58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90,  # Left
    156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188,  # Right
    254, 255, 256, 257, 258, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 282, 283, 284, 285, 286,  # Down
)


class LookupTableIDA777LRObliqueEdgePairing(LookupTableIDAViaC):

    oblique_edges_777 = (
        10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
        59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89,  # Left
        108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  # Front
        157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187,  # Right
        206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  # Back
        255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
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


class LookupTableIDA777UDObliqueEdgePairing(LookupTableIDAViaC):

    UFBD_oblique_edges_777 = (
        10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40,  # Upper
        108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  # Front
        206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  # Back
        255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  # Down
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
        'LLLLLLLLLLLLRRRRRRRRRRRR',
        'LLLLRLRLRLLLRRRLRLRLRRRR',
        'LLLLRLRLRLLLRRRRLRLRLRRR',
        'LLLRLRLRLLLLRRRLRLRLRRRR',
        'LLLRLRLRLLLLRRRRLRLRLRRR',
        'LLLRRRRRRLLLRRRLLLLLLRRR',
        'LLRLLLLLLLLRLRRRRRRRRLRR',
        'LLRLLLLLLLLRRRLRRRRRRRRL',
        'LLRLRLRLRLLRLRRLRLRLRLRR',
        'LLRLRLRLRLLRLRRRLRLRLLRR',
        'LLRLRLRLRLLRRRLLRLRLRRRL',
        'LLRLRLRLRLLRRRLRLRLRLRRL',
        'LLRRLRLRLLLRLRRLRLRLRLRR',
        'LLRRLRLRLLLRLRRRLRLRLLRR',
        'LLRRLRLRLLLRRRLLRLRLRRRL',
        'LLRRLRLRLLLRRRLRLRLRLRRL',
        'LLRRRRRRRLLRLRRLLLLLLLRR',
        'LLRRRRRRRLLRRRLLLLLLLRRL',
        'LRLLLLLLLLRLRLRRRRRRRRLR',
        'LRLLRLRLRLRLRLRLRLRLRRLR',
        'LRLLRLRLRLRLRLRRLRLRLRLR',
        'LRLRLRLRLLRLRLRLRLRLRRLR',
        'LRLRLRLRLLRLRLRRLRLRLRLR',
        'LRLRRRRRRLRLRLRLLLLLLRLR',
        'LRRLLLLLLLRRLLRRRRRRRLLR',
        'LRRLLLLLLLRRRLLRRRRRRRLL',
        'LRRLRLRLRLRRLLRLRLRLRLLR',
        'LRRLRLRLRLRRLLRRLRLRLLLR',
        'LRRLRLRLRLRRRLLLRLRLRRLL',
        'LRRLRLRLRLRRRLLRLRLRLRLL',
        'LRRRLRLRLLRRLLRLRLRLRLLR',
        'LRRRLRLRLLRRLLRRLRLRLLLR',
        'LRRRLRLRLLRRRLLLRLRLRRLL',
        'LRRRLRLRLLRRRLLRLRLRLRLL',
        'LRRRRRRRRLRRLLRLLLLLLLLR',
        'LRRRRRRRRLRRRLLLLLLLLRLL',
        'RLLLLLLLLRLLLRRRRRRRRLRR',
        'RLLLLLLLLRLLRRLRRRRRRRRL',
        'RLLLRLRLRRLLLRRLRLRLRLRR',
        'RLLLRLRLRRLLLRRRLRLRLLRR',
        'RLLLRLRLRRLLRRLLRLRLRRRL',
        'RLLLRLRLRRLLRRLRLRLRLRRL',
        'RLLRLRLRLRLLLRRLRLRLRLRR',
        'RLLRLRLRLRLLLRRRLRLRLLRR',
        'RLLRLRLRLRLLRRLLRLRLRRRL',
        'RLLRLRLRLRLLRRLRLRLRLRRL',
        'RLLRRRRRRRLLLRRLLLLLLLRR',
        'RLLRRRRRRRLLRRLLLLLLLRRL',
        'RLRLLLLLLRLRLRLRRRRRRLRL',
        'RLRLRLRLRRLRLRLLRLRLRLRL',
        'RLRLRLRLRRLRLRLRLRLRLLRL',
        'RLRRLRLRLRLRLRLLRLRLRLRL',
        'RLRRLRLRLRLRLRLRLRLRLLRL',
        'RLRRRRRRRRLRLRLLLLLLLLRL',
        'RRLLLLLLLRRLLLRRRRRRRLLR',
        'RRLLLLLLLRRLRLLRRRRRRRLL',
        'RRLLRLRLRRRLLLRLRLRLRLLR',
        'RRLLRLRLRRRLLLRRLRLRLLLR',
        'RRLLRLRLRRRLRLLLRLRLRRLL',
        'RRLLRLRLRRRLRLLRLRLRLRLL',
        'RRLRLRLRLRRLLLRLRLRLRLLR',
        'RRLRLRLRLRRLLLRRLRLRLLLR',
        'RRLRLRLRLRRLRLLLRLRLRRLL',
        'RRLRLRLRLRRLRLLRLRLRLRLL',
        'RRLRRRRRRRRLLLRLLLLLLLLR',
        'RRLRRRRRRRRLRLLLLLLLLRLL',
        'RRRLLLLLLRRRLLLRRRRRRLLL',
        'RRRLRLRLRRRRLLLLRLRLRLLL',
        'RRRLRLRLRRRRLLLRLRLRLLLL',
        'RRRRLRLRLRRRLLLLRLRLRLLL',
        'RRRRLRLRLRRRLLLRLRLRLLLL',
        'RRRRRRRRRRRRLLLLLLLLLLLL'
    )

    LR_oblique_edges_and_outer_t_center = (
        # 10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40, # Upper
        59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89, # Left
        # 108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138, # Front
        157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187, # Right
        # 206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236, # Back
        # 255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285, # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step41.txt',
            self.state_targets,
            linecount=343000,
            max_depth=8,
            filesize=20237000,
            all_moves=moves_777,
            illegal_moves=(
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
            ),
            use_state_index=True,
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
        'LLLLLLLLLLLLLRRRRRRRRRRRRR',
        'LLLLLLLLRLLLLRRRRLRRRRRRRR',
        'LLLLLLLLRLLLLRRRRRRRRLRRRR',
        'LLLLRLLLLLLLLRRRRLRRRRRRRR',
        'LLLLRLLLLLLLLRRRRRRRRLRRRR',
        'LLLLRLLLRLLLLRRRRLRRRLRRRR',
        'LLLRLLLRLLLRRLLRRRLRRRLRRR',
        'LLLRLLLRLLLRRRRRLRRRLRRRLL',
        'LLLRLLLRRLLRRLLRRLLRRRLRRR',
        'LLLRLLLRRLLRRLLRRRLRRLLRRR',
        'LLLRLLLRRLLRRRRRLLRRLRRRLL',
        'LLLRLLLRRLLRRRRRLRRRLLRRLL',
        'LLLRRLLRLLLRRLLRRLLRRRLRRR',
        'LLLRRLLRLLLRRLLRRRLRRLLRRR',
        'LLLRRLLRLLLRRRRRLLRRLRRRLL',
        'LLLRRLLRLLLRRRRRLRRRLLRRLL',
        'LLLRRLLRRLLRRLLRRLLRRLLRRR',
        'LLLRRLLRRLLRRRRRLLRRLLRRLL',
        'RRLLLRLLLRLLLLLRRRLRRRLRRR',
        'RRLLLRLLLRLLLRRRLRRRLRRRLL',
        'RRLLLRLLRRLLLLLRRLLRRRLRRR',
        'RRLLLRLLRRLLLLLRRRLRRLLRRR',
        'RRLLLRLLRRLLLRRRLLRRLRRRLL',
        'RRLLLRLLRRLLLRRRLRRRLLRRLL',
        'RRLLRRLLLRLLLLLRRLLRRRLRRR',
        'RRLLRRLLLRLLLLLRRRLRRLLRRR',
        'RRLLRRLLLRLLLRRRLLRRLRRRLL',
        'RRLLRRLLLRLLLRRRLRRRLLRRLL',
        'RRLLRRLLRRLLLLLRRLLRRLLRRR',
        'RRLLRRLLRRLLLRRRLLRRLLRRLL',
        'RRLRLRLRLRLRRLLRLRLRLRLRLL',
        'RRLRLRLRRRLRRLLRLLLRLRLRLL',
        'RRLRLRLRRRLRRLLRLRLRLLLRLL',
        'RRLRRRLRLRLRRLLRLLLRLRLRLL',
        'RRLRRRLRLRLRRLLRLRLRLLLRLL',
        'RRLRRRLRRRLRRLLRLLLRLLLRLL'
    )

    LR_inside_centers_and_left_oblique_edges = (
        # 10, 17, 18, 19, 20, 24, 25, 26, 30, 31, 32, 33, 40, # Upper
        59, 66, 67, 68, 69, 73, 74, 75, 79, 80, 81, 82, 89, # Left
        # 108, 115, 116, 117, 118, 122, 123, 124, 128, 129, 130, 131, 138, # Front
        157, 164, 165, 166, 167, 171, 172, 173, 177, 178, 179, 180, 187, # Right
        # 206, 213, 214, 215, 216, 220, 221, 222, 226, 227, 228, 229, 236, # Back
        # 255, 262, 263, 264, 265, 269, 270, 271, 275, 276, 277, 278, 285, # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step42.txt',
            self.state_targets,
            linecount=343000,
            max_depth=9,
            filesize=22981000,
            all_moves=moves_777,
            illegal_moves=(
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
            ),
            use_state_index=True,
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
        # 11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39, # Upper
        60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88, # Left
        # 109, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 137, # Front
        158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186, # Right
        # 207, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 235, # Back
        # 256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284, # Down
    )

    state_targets = (
        'LLLLLLLLLLLLLRRRRRRRRRRRRR',
        'LLLLLLLLRLLLLRRRRLRRRRRRRR',
        'LLLLLLLLRLLLLRRRRRRRRLRRRR',
        'LLLLRLLLLLLLLRRRRLRRRRRRRR',
        'LLLLRLLLLLLLLRRRRRRRRLRRRR',
        'LLLLRLLLRLLLLRRRRLRRRLRRRR',
        'LLLRLLLRLLLRLRLRRRLRRRLRRR',
        'LLLRLLLRLLLRLRRRLRRRLRRRLR',
        'LLLRLLLRRLLRLRLRRLLRRRLRRR',
        'LLLRLLLRRLLRLRLRRRLRRLLRRR',
        'LLLRLLLRRLLRLRRRLLRRLRRRLR',
        'LLLRLLLRRLLRLRRRLRRRLLRRLR',
        'LLLRRLLRLLLRLRLRRLLRRRLRRR',
        'LLLRRLLRLLLRLRLRRRLRRLLRRR',
        'LLLRRLLRLLLRLRRRLLRRLRRRLR',
        'LLLRRLLRLLLRLRRRLRRRLLRRLR',
        'LLLRRLLRRLLRLRLRRLLRRLLRRR',
        'LLLRRLLRRLLRLRRRLLRRLLRRLR',
        'LRLLLRLLLRLLLRLRRRLRRRLRRR',
        'LRLLLRLLLRLLLRRRLRRRLRRRLR',
        'LRLLLRLLRRLLLRLRRLLRRRLRRR',
        'LRLLLRLLRRLLLRLRRRLRRLLRRR',
        'LRLLLRLLRRLLLRRRLLRRLRRRLR',
        'LRLLLRLLRRLLLRRRLRRRLLRRLR',
        'LRLLRRLLLRLLLRLRRLLRRRLRRR',
        'LRLLRRLLLRLLLRLRRRLRRLLRRR',
        'LRLLRRLLLRLLLRRRLLRRLRRRLR',
        'LRLLRRLLLRLLLRRRLRRRLLRRLR',
        'LRLLRRLLRRLLLRLRRLLRRLLRRR',
        'LRLLRRLLRRLLLRRRLLRRLLRRLR',
        'LRLRLRLRLRLRLRLRLRLRLRLRLR',
        'LRLRLRLRRRLRLRLRLLLRLRLRLR',
        'LRLRLRLRRRLRLRLRLRLRLLLRLR',
        'LRLRRRLRLRLRLRLRLLLRLRLRLR',
        'LRLRRRLRLRLRLRLRLRLRLLLRLR',
        'LRLRRRLRRRLRLRLRLLLRLLLRLR'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step43.txt',
            self.state_targets,
            linecount=343000,
            max_depth=8,
            filesize=22981000,
            all_moves=moves_777,
            illegal_moves=(
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
            ),
            use_state_index=True,
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
        'LLLLLLLLLLLLLRRRRRRRRRRRRR',
        'LLLLLLLLLLLRLRLRRRRRRRRRRR',
        'LLLLLLLLLLLRLRRRRRRRRRRRLR',
        'LLRLLRLLRLLLRLRRRLRRLRRLRR',
        'LLRLLRLLRLLLRRRLRRLRRLRRRL',
        'LLRLLRLLRLLRRLLRRLRRLRRLRR',
        'LLRLLRLLRLLRRLRRRLRRLRRLLR',
        'LLRLLRLLRLLRRRLLRRLRRLRRRL',
        'LLRLLRLLRLLRRRRLRRLRRLRRLL',
        'LRLLLLLLLLLLLRLRRRRRRRRRRR',
        'LRLLLLLLLLLLLRRRRRRRRRRRLR',
        'LRLLLLLLLLLRLRLRRRRRRRRRLR',
        'LRRLLRLLRLLLRLLRRLRRLRRLRR',
        'LRRLLRLLRLLLRLRRRLRRLRRLLR',
        'LRRLLRLLRLLLRRLLRRLRRLRRRL',
        'LRRLLRLLRLLLRRRLRRLRRLRRLL',
        'LRRLLRLLRLLRRLLRRLRRLRRLLR',
        'LRRLLRLLRLLRRRLLRRLRRLRRLL',
        'RLLLRLLRLLRLLLRRRLRRLRRLRR',
        'RLLLRLLRLLRLLRRLRRLRRLRRRL',
        'RLLLRLLRLLRRLLLRRLRRLRRLRR',
        'RLLLRLLRLLRRLLRRRLRRLRRLLR',
        'RLLLRLLRLLRRLRLLRRLRRLRRRL',
        'RLLLRLLRLLRRLRRLRRLRRLRRLL',
        'RLRLRRLRRLRLRLRLRLLRLLRLRL',
        'RLRLRRLRRLRRRLLLRLLRLLRLRL',
        'RLRLRRLRRLRRRLRLRLLRLLRLLL',
        'RRLLRLLRLLRLLLLRRLRRLRRLRR',
        'RRLLRLLRLLRLLLRRRLRRLRRLLR',
        'RRLLRLLRLLRLLRLLRRLRRLRRRL',
        'RRLLRLLRLLRLLRRLRRLRRLRRLL',
        'RRLLRLLRLLRRLLLRRLRRLRRLLR',
        'RRLLRLLRLLRRLRLLRRLRRLRRLL',
        'RRRLRRLRRLRLRLLLRLLRLLRLRL',
        'RRRLRRLRRLRLRLRLRLLRLLRLLL',
        'RRRLRRLRRLRRRLLLRLLRLLRLLL'
    )

    LR_inside_centers_and_right_oblique_edges = [
        # 12, 16, 17, 18, 19, 24, 25, 26, 31, 32, 33, 34, 38, # Upper
        61, 65, 66, 67, 68, 73, 74, 75, 80, 81, 82, 83, 87, # Left
        # 110, 114, 115, 116, 117, 122, 123, 124, 129, 130, 131, 132, 136, # Front
        159, 163, 164, 165, 166, 171, 172, 173, 178, 179, 180, 181, 185, # Right
        # 208, 212, 213, 214, 215, 220, 221, 222, 227, 228, 229, 230, 234, # Back
        # 257, 261, 262, 263, 264, 269, 270, 271, 276, 277, 278, 279, 283, # Down
    ]

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step44.txt',
            self.state_targets,
            linecount=343000,
            max_depth=9,
            filesize=22981000,
            all_moves=moves_777,
            illegal_moves=(
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
            ),
            use_state_index=True,
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
            ),
            prune_tables=(
                parent.lt_step41,
                parent.lt_step42,
                parent.lt_step43,
                parent.lt_step44,
            ),
        )


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
        'DDDDDDDDDDDDUUUUUUUUUUUU',
        'DDDDUDUDUDDDUUUDUDUDUUUU',
        'DDDDUDUDUDDDUUUUDUDUDUUU',
        'DDDUDUDUDDDDUUUDUDUDUUUU',
        'DDDUDUDUDDDDUUUUDUDUDUUU',
        'DDDUUUUUUDDDUUUDDDDDDUUU',
        'DDUDDDDDDDDUDUUUUUUUUDUU',
        'DDUDDDDDDDDUUUDUUUUUUUUD',
        'DDUDUDUDUDDUDUUDUDUDUDUU',
        'DDUDUDUDUDDUDUUUDUDUDDUU',
        'DDUDUDUDUDDUUUDDUDUDUUUD',
        'DDUDUDUDUDDUUUDUDUDUDUUD',
        'DDUUDUDUDDDUDUUDUDUDUDUU',
        'DDUUDUDUDDDUDUUUDUDUDDUU',
        'DDUUDUDUDDDUUUDDUDUDUUUD',
        'DDUUDUDUDDDUUUDUDUDUDUUD',
        'DDUUUUUUUDDUDUUDDDDDDDUU',
        'DDUUUUUUUDDUUUDDDDDDDUUD',
        'DUDDDDDDDDUDUDUUUUUUUUDU',
        'DUDDUDUDUDUDUDUDUDUDUUDU',
        'DUDDUDUDUDUDUDUUDUDUDUDU',
        'DUDUDUDUDDUDUDUDUDUDUUDU',
        'DUDUDUDUDDUDUDUUDUDUDUDU',
        'DUDUUUUUUDUDUDUDDDDDDUDU',
        'DUUDDDDDDDUUDDUUUUUUUDDU',
        'DUUDDDDDDDUUUDDUUUUUUUDD',
        'DUUDUDUDUDUUDDUDUDUDUDDU',
        'DUUDUDUDUDUUDDUUDUDUDDDU',
        'DUUDUDUDUDUUUDDDUDUDUUDD',
        'DUUDUDUDUDUUUDDUDUDUDUDD',
        'DUUUDUDUDDUUDDUDUDUDUDDU',
        'DUUUDUDUDDUUDDUUDUDUDDDU',
        'DUUUDUDUDDUUUDDDUDUDUUDD',
        'DUUUDUDUDDUUUDDUDUDUDUDD',
        'DUUUUUUUUDUUDDUDDDDDDDDU',
        'DUUUUUUUUDUUUDDDDDDDDUDD',
        'UDDDDDDDDUDDDUUUUUUUUDUU',
        'UDDDDDDDDUDDUUDUUUUUUUUD',
        'UDDDUDUDUUDDDUUDUDUDUDUU',
        'UDDDUDUDUUDDDUUUDUDUDDUU',
        'UDDDUDUDUUDDUUDDUDUDUUUD',
        'UDDDUDUDUUDDUUDUDUDUDUUD',
        'UDDUDUDUDUDDDUUDUDUDUDUU',
        'UDDUDUDUDUDDDUUUDUDUDDUU',
        'UDDUDUDUDUDDUUDDUDUDUUUD',
        'UDDUDUDUDUDDUUDUDUDUDUUD',
        'UDDUUUUUUUDDDUUDDDDDDDUU',
        'UDDUUUUUUUDDUUDDDDDDDUUD',
        'UDUDDDDDDUDUDUDUUUUUUDUD',
        'UDUDUDUDUUDUDUDDUDUDUDUD',
        'UDUDUDUDUUDUDUDUDUDUDDUD',
        'UDUUDUDUDUDUDUDDUDUDUDUD',
        'UDUUDUDUDUDUDUDUDUDUDDUD',
        'UDUUUUUUUUDUDUDDDDDDDDUD',
        'UUDDDDDDDUUDDDUUUUUUUDDU',
        'UUDDDDDDDUUDUDDUUUUUUUDD',
        'UUDDUDUDUUUDDDUDUDUDUDDU',
        'UUDDUDUDUUUDDDUUDUDUDDDU',
        'UUDDUDUDUUUDUDDDUDUDUUDD',
        'UUDDUDUDUUUDUDDUDUDUDUDD',
        'UUDUDUDUDUUDDDUDUDUDUDDU',
        'UUDUDUDUDUUDDDUUDUDUDDDU',
        'UUDUDUDUDUUDUDDDUDUDUUDD',
        'UUDUDUDUDUUDUDDUDUDUDUDD',
        'UUDUUUUUUUUDDDUDDDDDDDDU',
        'UUDUUUUUUUUDUDDDDDDDDUDD',
        'UUUDDDDDDUUUDDDUUUUUUDDD',
        'UUUDUDUDUUUUDDDDUDUDUDDD',
        'UUUDUDUDUUUUDDDUDUDUDDDD',
        'UUUUDUDUDUUUDDDDUDUDUDDD',
        'UUUUDUDUDUUUDDDUDUDUDDDD',
        'UUUUUUUUUUUUDDDDDDDDDDDD'
    )

    UD_oblique_edges_and_outer_t_center = (
        10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40, # Upper
        # 59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89, # Left
        # 108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138, # Front
        # 157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187, # Right
        # 206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236, # Back
        255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285, # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step51.txt',
            self.state_targets,
            linecount=343000,
            max_depth=9,
            filesize=21266000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Uw2", "3Dw2", "Uw2", "Dw2",

                "F", "F'", "F2",
                "D", "D'", "D2",
            ),
            use_state_index=True,
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
        'DDUDDDUDDDUDDUUDUUUDUUUDUU',
        'DDUDDDUDUDUDDUUDUDUDUUUDUU',
        'DDUDDDUDUDUDDUUDUUUDUDUDUU',
        'DDUDUDUDDDUDDUUDUDUDUUUDUU',
        'DDUDUDUDDDUDDUUDUUUDUDUDUU',
        'DDUDUDUDUDUDDUUDUDUDUDUDUU',
        'DDUUDDUUDDUUUDDDUUDDUUDDUU',
        'DDUUDDUUDDUUUUUDDUUDDUUDDD',
        'DDUUDDUUUDUUUDDDUDDDUUDDUU',
        'DDUUDDUUUDUUUDDDUUDDUDDDUU',
        'DDUUDDUUUDUUUUUDDDUDDUUDDD',
        'DDUUDDUUUDUUUUUDDUUDDDUDDD',
        'DDUUUDUUDDUUUDDDUDDDUUDDUU',
        'DDUUUDUUDDUUUDDDUUDDUDDDUU',
        'DDUUUDUUDDUUUUUDDDUDDUUDDD',
        'DDUUUDUUDDUUUUUDDUUDDDUDDD',
        'DDUUUDUUUDUUUDDDUDDDUDDDUU',
        'DDUUUDUUUDUUUUUDDDUDDDUDDD',
        'UUUDDUUDDUUDDDDDUUDDUUDDUU',
        'UUUDDUUDDUUDDUUDDUUDDUUDDD',
        'UUUDDUUDUUUDDDDDUDDDUUDDUU',
        'UUUDDUUDUUUDDDDDUUDDUDDDUU',
        'UUUDDUUDUUUDDUUDDDUDDUUDDD',
        'UUUDDUUDUUUDDUUDDUUDDDUDDD',
        'UUUDUUUDDUUDDDDDUDDDUUDDUU',
        'UUUDUUUDDUUDDDDDUUDDUDDDUU',
        'UUUDUUUDDUUDDUUDDDUDDUUDDD',
        'UUUDUUUDDUUDDUUDDUUDDDUDDD',
        'UUUDUUUDUUUDDDDDUDDDUDDDUU',
        'UUUDUUUDUUUDDUUDDDUDDDUDDD',
        'UUUUDUUUDUUUUDDDDUDDDUDDDD',
        'UUUUDUUUUUUUUDDDDDDDDUDDDD',
        'UUUUDUUUUUUUUDDDDUDDDDDDDD',
        'UUUUUUUUDUUUUDDDDDDDDUDDDD',
        'UUUUUUUUDUUUUDDDDUDDDDDDDD',
        'UUUUUUUUUUUUUDDDDDDDDDDDDD'
    )

    UD_inside_centers_and_left_oblique_edges = (
        10, 17, 18, 19, 20, 24, 25, 26, 30, 31, 32, 33, 40, # Upper
        # 59, 66, 67, 68, 69, 73, 74, 75, 79, 80, 81, 82, 89, # Left
        # 108, 115, 116, 117, 118, 122, 123, 124, 128, 129, 130, 131, 138, # Front
        # 157, 164, 165, 166, 167, 171, 172, 173, 177, 178, 179, 180, 187, # Right
        # 206, 213, 214, 215, 216, 220, 221, 222, 226, 227, 228, 229, 236, # Back
        255, 262, 263, 264, 265, 269, 270, 271, 275, 276, 277, 278, 285, # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step52.txt',
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=23667000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Uw2", "3Dw2", "Uw2", "Dw2",

                "F", "F'", "F2",
                "D", "D'", "D2",
            ),
            use_state_index=True,
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
        'UDUDDDUDDDUDUDUDUUUDUUUDUD',
        'UDUDDDUDUDUDUDUDUDUDUUUDUD',
        'UDUDDDUDUDUDUDUDUUUDUDUDUD',
        'UDUDUDUDDDUDUDUDUDUDUUUDUD',
        'UDUDUDUDDDUDUDUDUUUDUDUDUD',
        'UDUDUDUDUDUDUDUDUDUDUDUDUD',
        'UDUUDDUUDDUUUDDDUUDDUUDDUD',
        'UDUUDDUUDDUUUDUDDUUDDUUDDD',
        'UDUUDDUUUDUUUDDDUDDDUUDDUD',
        'UDUUDDUUUDUUUDDDUUDDUDDDUD',
        'UDUUDDUUUDUUUDUDDDUDDUUDDD',
        'UDUUDDUUUDUUUDUDDUUDDDUDDD',
        'UDUUUDUUDDUUUDDDUDDDUUDDUD',
        'UDUUUDUUDDUUUDDDUUDDUDDDUD',
        'UDUUUDUUDDUUUDUDDDUDDUUDDD',
        'UDUUUDUUDDUUUDUDDUUDDDUDDD',
        'UDUUUDUUUDUUUDDDUDDDUDDDUD',
        'UDUUUDUUUDUUUDUDDDUDDDUDDD',
        'UUUDDUUDDUUDUDDDUUDDUUDDUD',
        'UUUDDUUDDUUDUDUDDUUDDUUDDD',
        'UUUDDUUDUUUDUDDDUDDDUUDDUD',
        'UUUDDUUDUUUDUDDDUUDDUDDDUD',
        'UUUDDUUDUUUDUDUDDDUDDUUDDD',
        'UUUDDUUDUUUDUDUDDUUDDDUDDD',
        'UUUDUUUDDUUDUDDDUDDDUUDDUD',
        'UUUDUUUDDUUDUDDDUUDDUDDDUD',
        'UUUDUUUDDUUDUDUDDDUDDUUDDD',
        'UUUDUUUDDUUDUDUDDUUDDDUDDD',
        'UUUDUUUDUUUDUDDDUDDDUDDDUD',
        'UUUDUUUDUUUDUDUDDDUDDDUDDD',
        'UUUUDUUUDUUUUDDDDUDDDUDDDD',
        'UUUUDUUUUUUUUDDDDDDDDUDDDD',
        'UUUUDUUUUUUUUDDDDUDDDDDDDD',
        'UUUUUUUUDUUUUDDDDDDDDUDDDD',
        'UUUUUUUUDUUUUDDDDUDDDDDDDD',
        'UUUUUUUUUUUUUDDDDDDDDDDDDD'
    )

    UD_inside_centers_and_outer_t_centers = (
        11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39, # Upper
        # 60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88, # Left
        # 109, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 137, # Front
        # 158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186, # Right
        # 207, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 235, # Back
        256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284, # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step53.txt',
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=23667000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Uw2", "3Dw2", "Uw2", "Dw2",

                "F", "F'", "F2",
                "D", "D'", "D2",
            ),
            use_state_index=True,
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
        'DDDUDDUDDUDDDUUUDUUDUUDUUU',
        'DDDUDDUDDUDUDUDUDUUDUUDUUU',
        'DDDUDDUDDUDUDUUUDUUDUUDUDU',
        'DDUUDUUDUUDDUDUUDDUDDUDDUU',
        'DDUUDUUDUUDDUUUDDUDDUDDUUD',
        'DDUUDUUDUUDUUDDUDDUDDUDDUU',
        'DDUUDUUDUUDUUDUUDDUDDUDDDU',
        'DDUUDUUDUUDUUUDDDUDDUDDUUD',
        'DDUUDUUDUUDUUUUDDUDDUDDUDD',
        'DUDUDDUDDUDDDUDUDUUDUUDUUU',
        'DUDUDDUDDUDDDUUUDUUDUUDUDU',
        'DUDUDDUDDUDUDUDUDUUDUUDUDU',
        'DUUUDUUDUUDDUDDUDDUDDUDDUU',
        'DUUUDUUDUUDDUDUUDDUDDUDDDU',
        'DUUUDUUDUUDDUUDDDUDDUDDUUD',
        'DUUUDUUDUUDDUUUDDUDDUDDUDD',
        'DUUUDUUDUUDUUDDUDDUDDUDDDU',
        'DUUUDUUDUUDUUUDDDUDDUDDUDD',
        'UDDUUDUUDUUDDDUUDDUDDUDDUU',
        'UDDUUDUUDUUDDUUDDUDDUDDUUD',
        'UDDUUDUUDUUUDDDUDDUDDUDDUU',
        'UDDUUDUUDUUUDDUUDDUDDUDDDU',
        'UDDUUDUUDUUUDUDDDUDDUDDUUD',
        'UDDUUDUUDUUUDUUDDUDDUDDUDD',
        'UDUUUUUUUUUDUDUDDDDDDDDDUD',
        'UDUUUUUUUUUUUDDDDDDDDDDDUD',
        'UDUUUUUUUUUUUDUDDDDDDDDDDD',
        'UUDUUDUUDUUDDDDUDDUDDUDDUU',
        'UUDUUDUUDUUDDDUUDDUDDUDDDU',
        'UUDUUDUUDUUDDUDDDUDDUDDUUD',
        'UUDUUDUUDUUDDUUDDUDDUDDUDD',
        'UUDUUDUUDUUUDDDUDDUDDUDDDU',
        'UUDUUDUUDUUUDUDDDUDDUDDUDD',
        'UUUUUUUUUUUDUDDDDDDDDDDDUD',
        'UUUUUUUUUUUDUDUDDDDDDDDDDD',
        'UUUUUUUUUUUUUDDDDDDDDDDDDD'
    )

    UD_inside_centers_and_right_oblique_edges = [
        12, 16, 17, 18, 19, 24, 25, 26, 31, 32, 33, 34, 38, # Upper
        # 61, 65, 66, 67, 68, 73, 74, 75, 80, 81, 82, 83, 87, # Left
        # 110, 114, 115, 116, 117, 122, 123, 124, 129, 130, 131, 132, 136, # Front
        # 159, 163, 164, 165, 166, 171, 172, 173, 178, 179, 180, 181, 185, # Right
        # 208, 212, 213, 214, 215, 220, 221, 222, 227, 228, 229, 230, 234, # Back
        257, 261, 262, 263, 264, 269, 270, 271, 276, 277, 278, 279, 283, # Down
    ]

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step54.txt',
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=24010000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Uw2", "3Dw2", "Uw2", "Dw2",

                "F", "F'", "F2",
                "D", "D'", "D2",
            ),
            use_state_index=True,
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
        59, 60, 61, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 87, 88, 89, # Left
        157, 158, 159, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 185, 186, 187, # Right
    )

    state_targets = (
        "LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR",
        "RRRRLLLRRLLLRRLLLRRRRLLLLRRRLLRRRLLRRRLLLL",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step55.txt',
            self.state_targets,
            linecount=72,
            max_depth=4,
            filesize=4392,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Uw2", "3Dw2", "Uw2", "Dw2",

                "F", "F'", "F2",
                "D", "D'", "D2",
            ),
            use_state_index=True,
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
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Uw2", "3Dw2", "Uw2", "Dw2",

                "F", "F'", "F2",
                "D", "D'", "D2",
            ),
            prune_tables=(
                parent.lt_step51,
                parent.lt_step52,
                parent.lt_step53,
                parent.lt_step54,
                parent.lt_step55,
            ),
        )



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
        10, 11, 12, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 38, 39, 40, # Upper
        255, 256, 257, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 283, 284, 285,  # Down
    )

    state_targets = (
        "UUUUUUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDDDDDD",
        "DDDDUUUDDUUUDDUUUDDDDUUUUDDDUUDDDUUDDDUUUU",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step61.txt',
            self.state_targets,
            linecount=72,
            max_depth=4,
            filesize=4392,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
        59, 60, 61, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 87, 88, 89, # Left
        157, 158, 159, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 185, 186, 187, # Right
    )

    state_targets = (
        "LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR",
        "RRRRLLLRRLLLRRLLLRRRRLLLLRRRLLRRRLLRRRLLLL",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step62.txt',
            self.state_targets,
            linecount=72,
            max_depth=4,
            filesize=4392,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
        # 11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39, # Upper
        # 60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88, # Left
        109, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 137, # Front
        # 158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186, # Right
        207, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 235, # Back
        # 256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284, # Down
    )

    state_targets = (
        "FFFFFFFFFFFFFBBBBBBBBBBBBB",
        "BFFFBFFFBFFFBFBBBFBBBFBBBF",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step65.txt',
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=25039000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
        # 10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40, # Upper
        # 59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89, # Left
        108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138, # Front
        # 157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187, # Right
        206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236, # Back
        # 255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285, # Down
    )

    state_targets = (
        "BBBBBBBBBBBBFFFFFFFFFFFF",
        "FFFFFFFFFFFFBBBBBBBBBBBB",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step66.txt',
            self.state_targets,
            linecount=343000,
            max_depth=10,
            filesize=23667000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            prune_tables=(
                parent.lt_step61,
                parent.lt_step62,
                parent.lt_step65,
                parent.lt_step66,
            ),
        )


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
        10, 11, 12, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 38, 39, 40, # Upper
        255, 256, 257, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 283, 284, 285,  # Down
    )

    state_targets = (
        "UUUUUUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDDDDDD",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step71.txt',
            self.state_targets,
            linecount=36,
            max_depth=4,
            filesize=2196,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
        59, 60, 61, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 87, 88, 89, # Left
        157, 158, 159, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 185, 186, 187, # Right
    )

    state_targets = (
        "LLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRR",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step72.txt',
            self.state_targets,
            linecount=36,
            max_depth=4,
            filesize=2196,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
        # 11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39, # Upper
        # 60, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 88, # Left
        109, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 137, # Front
        # 158, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 186, # Right
        207, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 235, # Back
        # 256, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 284, # Down
    )

    state_targets = (
        "FFFFFFFFFFFFFBBBBBBBBBBBBB",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step75.txt',
            self.state_targets,
            linecount=343000,
            max_depth=12,
            filesize=27097000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
        # 10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40, # Upper
        # 59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89, # Left
        108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138, # Front
        # 157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187, # Right
        206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236, # Back
        # 255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285, # Down
    )

    state_targets = (
        "FFFFFFFFFFFFBBBBBBBBBBBB",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step76.txt',
            self.state_targets,
            linecount=343000,
            max_depth=11,
            filesize=24353000,
            all_moves=moves_777,
            illegal_moves=(
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            use_state_index=True,
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
                "3Uw", "3Uw'", "Uw", "Uw'",
                "3Lw", "3Lw'", "Lw", "Lw'",
                "3Fw", "3Fw'", "Fw", "Fw'",
                "3Rw", "3Rw'", "Rw", "Rw'",
                "3Bw", "3Bw'", "Bw", "Bw'",
                "3Dw", "3Dw'", "Dw", "Dw'",
                "L", "L'",
                "R", "R'",
                "3Fw2", "3Bw2", "Fw2", "Bw2",
                "U", "U'",
                "D", "D'"
            ),
            prune_tables=(
                parent.lt_step71,
                parent.lt_step72,
                parent.lt_step75,
                parent.lt_step76,
            ),
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
            2, 6, 14, 42, 48, 44, 36, 8,
            51, 55, 63, 91, 97, 93, 85, 57,
            100, 104, 112, 140, 146, 142, 134, 106,
            149, 153, 161, 189, 195, 191, 183, 155,
            198, 202, 210, 238, 244, 240, 232, 204,
            247, 251, 259, 287, 293, 289, 281, 253,
        )

        edge_orbit_1 = (
            3, 5, 21, 35, 47, 45, 29, 15,
            52, 54, 70, 84, 96, 94, 78, 64,
            101, 103, 119, 133, 145, 143, 127, 113,
            150, 152, 168, 182, 194, 192, 176, 162,
            199, 201, 217, 231, 243, 241, 225, 211,
            248, 250, 266, 280, 292, 290, 274, 260,
        )

        edge_orbit_2 = (
            4, 28, 46, 22,
            53, 77, 95, 71,
            102, 126, 144, 120,
            151, 175, 193, 169,
            200, 224, 242, 218,
            249, 273, 291, 267,
        )

        corners = (
            1, 7, 43, 49,
            50, 56, 92, 98,
            99, 105, 141, 147,
            148, 154, 190, 196,
            197, 203, 239, 245,
            246, 252, 288, 294,
        )

        left_oblique_edge = (
            10, 20, 40, 30,
            59, 69, 89, 79,
            108, 118, 138, 128,
            157, 167, 187, 177,
            206, 216, 236, 226,
            255, 265, 285, 275,
        )

        right_oblique_edge = (
            12, 34, 38, 16,
            61, 83, 87, 65,
            110, 132, 136, 114,
            159, 181, 185, 163,
            208, 230, 234, 212,
            257, 279, 283, 261,
        )

        outside_x_centers = (
            9, 13, 37, 41,
            58, 62, 86, 90,
            107, 111, 135, 139,
            156, 160, 184, 188,
            205, 209, 233, 237,
            254, 258, 282, 286,
        )

        inside_x_centers = (
            17, 19, 31, 33,
            66, 68, 80, 82,
            115, 117, 129, 131,
            164, 166, 178, 180,
            213, 215, 227, 229,
            262, 264, 276, 278,
        )

        outside_t_centers = (
            11, 23, 27, 39,
            60, 72, 76, 88,
            109, 121, 125, 137,
            158, 170, 174, 186,
            207, 219, 223, 235,
            256, 268, 272, 284,
        )

        inside_t_centers = (
            18, 24, 26, 32,
            67, 73, 75, 81,
            116, 122, 124, 130,
            165, 171, 173, 179,
            214, 220, 222, 228,
            263, 269, 271, 277,
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

        self.lt_LR_oblique_edge_pairing = LookupTableIDA777LRObliqueEdgePairing(self)
        self.lt_UD_oblique_edge_pairing = LookupTableIDA777UDObliqueEdgePairing(self)

        self.lt_step41 = LookupTable777Step41(self)
        self.lt_step42 = LookupTable777Step42(self)
        self.lt_step43 = LookupTable777Step43(self)
        self.lt_step44 = LookupTable777Step44(self)
        self.lt_step40 = LookupTableIDA777Step40(self)

        self.lt_step51 = LookupTable777Step51(self)
        self.lt_step52 = LookupTable777Step52(self)
        self.lt_step53 = LookupTable777Step53(self)
        self.lt_step54 = LookupTable777Step54(self)
        self.lt_step55 = LookupTable777Step55(self)
        self.lt_step50 = LookupTableIDA777Step50(self)

        self.lt_step61 = LookupTable777Step61(self)
        self.lt_step62 = LookupTable777Step62(self)
        self.lt_step65 = LookupTable777Step65(self)
        self.lt_step66 = LookupTable777Step66(self)
        self.lt_step60 = LookupTableIDA777Step60(self)

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
        self.group_inside_UD_centers()
        self.print_cube()
        log.info(
            "%s: UD inner x-centers staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Pair the oblique UD edges
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

        # Stage the UD centers
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
        log.info(
            "%s: UD centers staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
        log.info("")
        log.info("")
        log.info("")
        log.info("")

    def stage_LR_centers(self):
        # Uses 5x5x5 solver to stage the inner x-centers
        self.group_inside_LR_centers()
        self.print_cube()
        log.info(
            "%s: LR inner x-centers staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
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

        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        tmp_solution_len = len(self.solution)
        self.lt_LR_oblique_edge_pairing.solve()
        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_777_LR_oblique_edges_staged"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: LR oblique edges staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

        # Stage the LR centers
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
        log.info(
            "%s: LR centers staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )
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

        tmp_solution_len = len(self.solution)
        self.lt_step40.solve_via_c()
        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        self.solution.append(
            "COMMENT_%d_steps_777_LR_centers_vertical_bars"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )
        log.info(
            "%s: LR centers vertical bars, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

    def UD_centers_vertical_bars(self):

        # Test the pruning tables
        # self.lt_step51.solve()
        # self.lt_step52.solve()
        # self.print_cube()
        # log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

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
        tmp_solution_len = len(self.solution)
        self.lt_step60.solve_via_c()
        self.solution.append(
            "COMMENT_%d_steps_777_centers_daisy_solved"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info(
            "%s: centers daisy solved, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

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

        tmp_solution_len = len(self.solution)
        self.lt_step70.solve_via_c()
        self.solution.append(
            "COMMENT_%d_steps_777_centers_solved"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        self.print_cube()
        # log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info(
            "%s: centers solved, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

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
        log.info(
            "%s: centers solved, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

        if not self.centers_solved():
            raise SolveError("centers should be solved")

swaps_777 = { "2B": ( 0, 1, 2, 3, 4, 5, 6, 7, 153, 160, 167, 174, 181, 188, 195, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 14, 52, 53, 54, 55, 56, 57, 13, 59, 60, 61, 62, 63, 64, 12, 66, 67, 68, 69, 70, 71, 11, 73, 74, 75, 76, 77, 78, 10, 80, 81, 82, 83, 84, 85, 9, 87, 88, 89, 90, 91, 92, 8, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 287, 154, 155, 156, 157, 158, 159, 286, 161, 162, 163, 164, 165, 166, 285, 168, 169, 170, 171, 172, 173, 284, 175, 176, 177, 178, 179, 180, 283, 182, 183, 184, 185, 186, 187, 282, 189, 190, 191, 192, 193, 194, 281, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 51, 58, 65, 72, 79, 86, 93, 288, 289, 290, 291, 292, 293, 294,), "2B'": ( 0, 1, 2, 3, 4, 5, 6, 7, 93, 86, 79, 72, 65, 58, 51, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 281, 52, 53, 54, 55, 56, 57, 282, 59, 60, 61, 62, 63, 64, 283, 66, 67, 68, 69, 70, 71, 284, 73, 74, 75, 76, 77, 78, 285, 80, 81, 82, 83, 84, 85, 286, 87, 88, 89, 90, 91, 92, 287, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 8, 154, 155, 156, 157, 158, 159, 9, 161, 162, 163, 164, 165, 166, 10, 168, 169, 170, 171, 172, 173, 11, 175, 176, 177, 178, 179, 180, 12, 182, 183, 184, 185, 186, 187, 13, 189, 190, 191, 192, 193, 194, 14, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 195, 188, 181, 174, 167, 160, 153, 288, 289, 290, 291, 292, 293, 294,), "2B2": ( 0, 1, 2, 3, 4, 5, 6, 7, 287, 286, 285, 284, 283, 282, 281, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 195, 52, 53, 54, 55, 56, 57, 188, 59, 60, 61, 62, 63, 64, 181, 66, 67, 68, 69, 70, 71, 174, 73, 74, 75, 76, 77, 78, 167, 80, 81, 82, 83, 84, 85, 160, 87, 88, 89, 90, 91, 92, 153, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 93, 154, 155, 156, 157, 158, 159, 86, 161, 162, 163, 164, 165, 166, 79, 168, 169, 170, 171, 172, 173, 72, 175, 176, 177, 178, 179, 180, 65, 182, 183, 184, 185, 186, 187, 58, 189, 190, 191, 192, 193, 194, 51, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 14, 13, 12, 11, 10, 9, 8, 288, 289, 290, 291, 292, 293, 294,), "2D": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 232, 233, 234, 235, 236, 237, 238, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 85, 86, 87, 88, 89, 90, 91, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 134, 135, 136, 137, 138, 139, 140, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 183, 184, 185, 186, 187, 188, 189, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2D'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 134, 135, 136, 137, 138, 139, 140, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 183, 184, 185, 186, 187, 188, 189, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 232, 233, 234, 235, 236, 237, 238, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 85, 86, 87, 88, 89, 90, 91, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2D2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 183, 184, 185, 186, 187, 188, 189, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 232, 233, 234, 235, 236, 237, 238, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 85, 86, 87, 88, 89, 90, 91, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 134, 135, 136, 137, 138, 139, 140, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2F": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 97, 90, 83, 76, 69, 62, 55, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 253, 56, 57, 58, 59, 60, 61, 254, 63, 64, 65, 66, 67, 68, 255, 70, 71, 72, 73, 74, 75, 256, 77, 78, 79, 80, 81, 82, 257, 84, 85, 86, 87, 88, 89, 258, 91, 92, 93, 94, 95, 96, 259, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 36, 150, 151, 152, 153, 154, 155, 37, 157, 158, 159, 160, 161, 162, 38, 164, 165, 166, 167, 168, 169, 39, 171, 172, 173, 174, 175, 176, 40, 178, 179, 180, 181, 182, 183, 41, 185, 186, 187, 188, 189, 190, 42, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 191, 184, 177, 170, 163, 156, 149, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2F'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 149, 156, 163, 170, 177, 184, 191, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 42, 56, 57, 58, 59, 60, 61, 41, 63, 64, 65, 66, 67, 68, 40, 70, 71, 72, 73, 74, 75, 39, 77, 78, 79, 80, 81, 82, 38, 84, 85, 86, 87, 88, 89, 37, 91, 92, 93, 94, 95, 96, 36, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 259, 150, 151, 152, 153, 154, 155, 258, 157, 158, 159, 160, 161, 162, 257, 164, 165, 166, 167, 168, 169, 256, 171, 172, 173, 174, 175, 176, 255, 178, 179, 180, 181, 182, 183, 254, 185, 186, 187, 188, 189, 190, 253, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 55, 62, 69, 76, 83, 90, 97, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2F2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 259, 258, 257, 256, 255, 254, 253, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 191, 56, 57, 58, 59, 60, 61, 184, 63, 64, 65, 66, 67, 68, 177, 70, 71, 72, 73, 74, 75, 170, 77, 78, 79, 80, 81, 82, 163, 84, 85, 86, 87, 88, 89, 156, 91, 92, 93, 94, 95, 96, 149, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 97, 150, 151, 152, 153, 154, 155, 90, 157, 158, 159, 160, 161, 162, 83, 164, 165, 166, 167, 168, 169, 76, 171, 172, 173, 174, 175, 176, 69, 178, 179, 180, 181, 182, 183, 62, 185, 186, 187, 188, 189, 190, 55, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 42, 41, 40, 39, 38, 37, 36, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2L": ( 0, 1, 244, 3, 4, 5, 6, 7, 8, 237, 10, 11, 12, 13, 14, 15, 230, 17, 18, 19, 20, 21, 22, 223, 24, 25, 26, 27, 28, 29, 216, 31, 32, 33, 34, 35, 36, 209, 38, 39, 40, 41, 42, 43, 202, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 2, 101, 102, 103, 104, 105, 106, 9, 108, 109, 110, 111, 112, 113, 16, 115, 116, 117, 118, 119, 120, 23, 122, 123, 124, 125, 126, 127, 30, 129, 130, 131, 132, 133, 134, 37, 136, 137, 138, 139, 140, 141, 44, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 289, 203, 204, 205, 206, 207, 208, 282, 210, 211, 212, 213, 214, 215, 275, 217, 218, 219, 220, 221, 222, 268, 224, 225, 226, 227, 228, 229, 261, 231, 232, 233, 234, 235, 236, 254, 238, 239, 240, 241, 242, 243, 247, 245, 246, 100, 248, 249, 250, 251, 252, 253, 107, 255, 256, 257, 258, 259, 260, 114, 262, 263, 264, 265, 266, 267, 121, 269, 270, 271, 272, 273, 274, 128, 276, 277, 278, 279, 280, 281, 135, 283, 284, 285, 286, 287, 288, 142, 290, 291, 292, 293, 294,), "2L'": ( 0, 1, 100, 3, 4, 5, 6, 7, 8, 107, 10, 11, 12, 13, 14, 15, 114, 17, 18, 19, 20, 21, 22, 121, 24, 25, 26, 27, 28, 29, 128, 31, 32, 33, 34, 35, 36, 135, 38, 39, 40, 41, 42, 43, 142, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 247, 101, 102, 103, 104, 105, 106, 254, 108, 109, 110, 111, 112, 113, 261, 115, 116, 117, 118, 119, 120, 268, 122, 123, 124, 125, 126, 127, 275, 129, 130, 131, 132, 133, 134, 282, 136, 137, 138, 139, 140, 141, 289, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 44, 203, 204, 205, 206, 207, 208, 37, 210, 211, 212, 213, 214, 215, 30, 217, 218, 219, 220, 221, 222, 23, 224, 225, 226, 227, 228, 229, 16, 231, 232, 233, 234, 235, 236, 9, 238, 239, 240, 241, 242, 243, 2, 245, 246, 244, 248, 249, 250, 251, 252, 253, 237, 255, 256, 257, 258, 259, 260, 230, 262, 263, 264, 265, 266, 267, 223, 269, 270, 271, 272, 273, 274, 216, 276, 277, 278, 279, 280, 281, 209, 283, 284, 285, 286, 287, 288, 202, 290, 291, 292, 293, 294,), "2L2": ( 0, 1, 247, 3, 4, 5, 6, 7, 8, 254, 10, 11, 12, 13, 14, 15, 261, 17, 18, 19, 20, 21, 22, 268, 24, 25, 26, 27, 28, 29, 275, 31, 32, 33, 34, 35, 36, 282, 38, 39, 40, 41, 42, 43, 289, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 244, 101, 102, 103, 104, 105, 106, 237, 108, 109, 110, 111, 112, 113, 230, 115, 116, 117, 118, 119, 120, 223, 122, 123, 124, 125, 126, 127, 216, 129, 130, 131, 132, 133, 134, 209, 136, 137, 138, 139, 140, 141, 202, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 142, 203, 204, 205, 206, 207, 208, 135, 210, 211, 212, 213, 214, 215, 128, 217, 218, 219, 220, 221, 222, 121, 224, 225, 226, 227, 228, 229, 114, 231, 232, 233, 234, 235, 236, 107, 238, 239, 240, 241, 242, 243, 100, 245, 246, 2, 248, 249, 250, 251, 252, 253, 9, 255, 256, 257, 258, 259, 260, 16, 262, 263, 264, 265, 266, 267, 23, 269, 270, 271, 272, 273, 274, 30, 276, 277, 278, 279, 280, 281, 37, 283, 284, 285, 286, 287, 288, 44, 290, 291, 292, 293, 294,), "2R": ( 0, 1, 2, 3, 4, 5, 104, 7, 8, 9, 10, 11, 12, 111, 14, 15, 16, 17, 18, 19, 118, 21, 22, 23, 24, 25, 26, 125, 28, 29, 30, 31, 32, 33, 132, 35, 36, 37, 38, 39, 40, 139, 42, 43, 44, 45, 46, 47, 146, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 251, 105, 106, 107, 108, 109, 110, 258, 112, 113, 114, 115, 116, 117, 265, 119, 120, 121, 122, 123, 124, 272, 126, 127, 128, 129, 130, 131, 279, 133, 134, 135, 136, 137, 138, 286, 140, 141, 142, 143, 144, 145, 293, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 48, 199, 200, 201, 202, 203, 204, 41, 206, 207, 208, 209, 210, 211, 34, 213, 214, 215, 216, 217, 218, 27, 220, 221, 222, 223, 224, 225, 20, 227, 228, 229, 230, 231, 232, 13, 234, 235, 236, 237, 238, 239, 6, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 240, 252, 253, 254, 255, 256, 257, 233, 259, 260, 261, 262, 263, 264, 226, 266, 267, 268, 269, 270, 271, 219, 273, 274, 275, 276, 277, 278, 212, 280, 281, 282, 283, 284, 285, 205, 287, 288, 289, 290, 291, 292, 198, 294,), "2R'": ( 0, 1, 2, 3, 4, 5, 240, 7, 8, 9, 10, 11, 12, 233, 14, 15, 16, 17, 18, 19, 226, 21, 22, 23, 24, 25, 26, 219, 28, 29, 30, 31, 32, 33, 212, 35, 36, 37, 38, 39, 40, 205, 42, 43, 44, 45, 46, 47, 198, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 6, 105, 106, 107, 108, 109, 110, 13, 112, 113, 114, 115, 116, 117, 20, 119, 120, 121, 122, 123, 124, 27, 126, 127, 128, 129, 130, 131, 34, 133, 134, 135, 136, 137, 138, 41, 140, 141, 142, 143, 144, 145, 48, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 293, 199, 200, 201, 202, 203, 204, 286, 206, 207, 208, 209, 210, 211, 279, 213, 214, 215, 216, 217, 218, 272, 220, 221, 222, 223, 224, 225, 265, 227, 228, 229, 230, 231, 232, 258, 234, 235, 236, 237, 238, 239, 251, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 104, 252, 253, 254, 255, 256, 257, 111, 259, 260, 261, 262, 263, 264, 118, 266, 267, 268, 269, 270, 271, 125, 273, 274, 275, 276, 277, 278, 132, 280, 281, 282, 283, 284, 285, 139, 287, 288, 289, 290, 291, 292, 146, 294,), "2R2": ( 0, 1, 2, 3, 4, 5, 251, 7, 8, 9, 10, 11, 12, 258, 14, 15, 16, 17, 18, 19, 265, 21, 22, 23, 24, 25, 26, 272, 28, 29, 30, 31, 32, 33, 279, 35, 36, 37, 38, 39, 40, 286, 42, 43, 44, 45, 46, 47, 293, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 240, 105, 106, 107, 108, 109, 110, 233, 112, 113, 114, 115, 116, 117, 226, 119, 120, 121, 122, 123, 124, 219, 126, 127, 128, 129, 130, 131, 212, 133, 134, 135, 136, 137, 138, 205, 140, 141, 142, 143, 144, 145, 198, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 146, 199, 200, 201, 202, 203, 204, 139, 206, 207, 208, 209, 210, 211, 132, 213, 214, 215, 216, 217, 218, 125, 220, 221, 222, 223, 224, 225, 118, 227, 228, 229, 230, 231, 232, 111, 234, 235, 236, 237, 238, 239, 104, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 6, 252, 253, 254, 255, 256, 257, 13, 259, 260, 261, 262, 263, 264, 20, 266, 267, 268, 269, 270, 271, 27, 273, 274, 275, 276, 277, 278, 34, 280, 281, 282, 283, 284, 285, 41, 287, 288, 289, 290, 291, 292, 48, 294,), "2U": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 106, 107, 108, 109, 110, 111, 112, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 155, 156, 157, 158, 159, 160, 161, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 204, 205, 206, 207, 208, 209, 210, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 57, 58, 59, 60, 61, 62, 63, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2U'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 204, 205, 206, 207, 208, 209, 210, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 57, 58, 59, 60, 61, 62, 63, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 106, 107, 108, 109, 110, 111, 112, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 155, 156, 157, 158, 159, 160, 161, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "2U2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 155, 156, 157, 158, 159, 160, 161, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 204, 205, 206, 207, 208, 209, 210, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 57, 58, 59, 60, 61, 62, 63, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 106, 107, 108, 109, 110, 111, 112, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3B": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 152, 159, 166, 173, 180, 187, 194, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 21, 53, 54, 55, 56, 57, 58, 20, 60, 61, 62, 63, 64, 65, 19, 67, 68, 69, 70, 71, 72, 18, 74, 75, 76, 77, 78, 79, 17, 81, 82, 83, 84, 85, 86, 16, 88, 89, 90, 91, 92, 93, 15, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 280, 153, 154, 155, 156, 157, 158, 279, 160, 161, 162, 163, 164, 165, 278, 167, 168, 169, 170, 171, 172, 277, 174, 175, 176, 177, 178, 179, 276, 181, 182, 183, 184, 185, 186, 275, 188, 189, 190, 191, 192, 193, 274, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 52, 59, 66, 73, 80, 87, 94, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3B'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 94, 87, 80, 73, 66, 59, 52, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 274, 53, 54, 55, 56, 57, 58, 275, 60, 61, 62, 63, 64, 65, 276, 67, 68, 69, 70, 71, 72, 277, 74, 75, 76, 77, 78, 79, 278, 81, 82, 83, 84, 85, 86, 279, 88, 89, 90, 91, 92, 93, 280, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 15, 153, 154, 155, 156, 157, 158, 16, 160, 161, 162, 163, 164, 165, 17, 167, 168, 169, 170, 171, 172, 18, 174, 175, 176, 177, 178, 179, 19, 181, 182, 183, 184, 185, 186, 20, 188, 189, 190, 191, 192, 193, 21, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 194, 187, 180, 173, 166, 159, 152, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3B2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 280, 279, 278, 277, 276, 275, 274, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 194, 53, 54, 55, 56, 57, 58, 187, 60, 61, 62, 63, 64, 65, 180, 67, 68, 69, 70, 71, 72, 173, 74, 75, 76, 77, 78, 79, 166, 81, 82, 83, 84, 85, 86, 159, 88, 89, 90, 91, 92, 93, 152, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 94, 153, 154, 155, 156, 157, 158, 87, 160, 161, 162, 163, 164, 165, 80, 167, 168, 169, 170, 171, 172, 73, 174, 175, 176, 177, 178, 179, 66, 181, 182, 183, 184, 185, 186, 59, 188, 189, 190, 191, 192, 193, 52, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 21, 20, 19, 18, 17, 16, 15, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Bw": ( 0, 154, 161, 168, 175, 182, 189, 196, 153, 160, 167, 174, 181, 188, 195, 152, 159, 166, 173, 180, 187, 194, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 7, 14, 21, 53, 54, 55, 56, 6, 13, 20, 60, 61, 62, 63, 5, 12, 19, 67, 68, 69, 70, 4, 11, 18, 74, 75, 76, 77, 3, 10, 17, 81, 82, 83, 84, 2, 9, 16, 88, 89, 90, 91, 1, 8, 15, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 280, 287, 294, 155, 156, 157, 158, 279, 286, 293, 162, 163, 164, 165, 278, 285, 292, 169, 170, 171, 172, 277, 284, 291, 176, 177, 178, 179, 276, 283, 290, 183, 184, 185, 186, 275, 282, 289, 190, 191, 192, 193, 274, 281, 288, 239, 232, 225, 218, 211, 204, 197, 240, 233, 226, 219, 212, 205, 198, 241, 234, 227, 220, 213, 206, 199, 242, 235, 228, 221, 214, 207, 200, 243, 236, 229, 222, 215, 208, 201, 244, 237, 230, 223, 216, 209, 202, 245, 238, 231, 224, 217, 210, 203, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 52, 59, 66, 73, 80, 87, 94, 51, 58, 65, 72, 79, 86, 93, 50, 57, 64, 71, 78, 85, 92,), "3Bw'": ( 0, 92, 85, 78, 71, 64, 57, 50, 93, 86, 79, 72, 65, 58, 51, 94, 87, 80, 73, 66, 59, 52, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 288, 281, 274, 53, 54, 55, 56, 289, 282, 275, 60, 61, 62, 63, 290, 283, 276, 67, 68, 69, 70, 291, 284, 277, 74, 75, 76, 77, 292, 285, 278, 81, 82, 83, 84, 293, 286, 279, 88, 89, 90, 91, 294, 287, 280, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 15, 8, 1, 155, 156, 157, 158, 16, 9, 2, 162, 163, 164, 165, 17, 10, 3, 169, 170, 171, 172, 18, 11, 4, 176, 177, 178, 179, 19, 12, 5, 183, 184, 185, 186, 20, 13, 6, 190, 191, 192, 193, 21, 14, 7, 203, 210, 217, 224, 231, 238, 245, 202, 209, 216, 223, 230, 237, 244, 201, 208, 215, 222, 229, 236, 243, 200, 207, 214, 221, 228, 235, 242, 199, 206, 213, 220, 227, 234, 241, 198, 205, 212, 219, 226, 233, 240, 197, 204, 211, 218, 225, 232, 239, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 194, 187, 180, 173, 166, 159, 152, 195, 188, 181, 174, 167, 160, 153, 196, 189, 182, 175, 168, 161, 154,), "3Bw2": ( 0, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 196, 195, 194, 53, 54, 55, 56, 189, 188, 187, 60, 61, 62, 63, 182, 181, 180, 67, 68, 69, 70, 175, 174, 173, 74, 75, 76, 77, 168, 167, 166, 81, 82, 83, 84, 161, 160, 159, 88, 89, 90, 91, 154, 153, 152, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 94, 93, 92, 155, 156, 157, 158, 87, 86, 85, 162, 163, 164, 165, 80, 79, 78, 169, 170, 171, 172, 73, 72, 71, 176, 177, 178, 179, 66, 65, 64, 183, 184, 185, 186, 59, 58, 57, 190, 191, 192, 193, 52, 51, 50, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,), "3D": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 225, 226, 227, 228, 229, 230, 231, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 78, 79, 80, 81, 82, 83, 84, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 127, 128, 129, 130, 131, 132, 133, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 176, 177, 178, 179, 180, 181, 182, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3D'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 127, 128, 129, 130, 131, 132, 133, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 176, 177, 178, 179, 180, 181, 182, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 225, 226, 227, 228, 229, 230, 231, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 78, 79, 80, 81, 82, 83, 84, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3D2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 176, 177, 178, 179, 180, 181, 182, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 225, 226, 227, 228, 229, 230, 231, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 78, 79, 80, 81, 82, 83, 84, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 127, 128, 129, 130, 131, 132, 133, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Dw": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 288, 281, 274, 267, 260, 253, 246, 289, 282, 275, 268, 261, 254, 247, 290, 283, 276, 269, 262, 255, 248, 291, 284, 277, 270, 263, 256, 249, 292, 285, 278, 271, 264, 257, 250, 293, 286, 279, 272, 265, 258, 251, 294, 287, 280, 273, 266, 259, 252,), "3Dw'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 252, 259, 266, 273, 280, 287, 294, 251, 258, 265, 272, 279, 286, 293, 250, 257, 264, 271, 278, 285, 292, 249, 256, 263, 270, 277, 284, 291, 248, 255, 262, 269, 276, 283, 290, 247, 254, 261, 268, 275, 282, 289, 246, 253, 260, 267, 274, 281, 288,), "3Dw2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246,), "3F": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 96, 89, 82, 75, 68, 61, 54, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 260, 55, 56, 57, 58, 59, 60, 261, 62, 63, 64, 65, 66, 67, 262, 69, 70, 71, 72, 73, 74, 263, 76, 77, 78, 79, 80, 81, 264, 83, 84, 85, 86, 87, 88, 265, 90, 91, 92, 93, 94, 95, 266, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 29, 151, 152, 153, 154, 155, 156, 30, 158, 159, 160, 161, 162, 163, 31, 165, 166, 167, 168, 169, 170, 32, 172, 173, 174, 175, 176, 177, 33, 179, 180, 181, 182, 183, 184, 34, 186, 187, 188, 189, 190, 191, 35, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 192, 185, 178, 171, 164, 157, 150, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3F'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 150, 157, 164, 171, 178, 185, 192, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 35, 55, 56, 57, 58, 59, 60, 34, 62, 63, 64, 65, 66, 67, 33, 69, 70, 71, 72, 73, 74, 32, 76, 77, 78, 79, 80, 81, 31, 83, 84, 85, 86, 87, 88, 30, 90, 91, 92, 93, 94, 95, 29, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 266, 151, 152, 153, 154, 155, 156, 265, 158, 159, 160, 161, 162, 163, 264, 165, 166, 167, 168, 169, 170, 263, 172, 173, 174, 175, 176, 177, 262, 179, 180, 181, 182, 183, 184, 261, 186, 187, 188, 189, 190, 191, 260, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 54, 61, 68, 75, 82, 89, 96, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3F2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 266, 265, 264, 263, 262, 261, 260, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 192, 55, 56, 57, 58, 59, 60, 185, 62, 63, 64, 65, 66, 67, 178, 69, 70, 71, 72, 73, 74, 171, 76, 77, 78, 79, 80, 81, 164, 83, 84, 85, 86, 87, 88, 157, 90, 91, 92, 93, 94, 95, 150, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 96, 151, 152, 153, 154, 155, 156, 89, 158, 159, 160, 161, 162, 163, 82, 165, 166, 167, 168, 169, 170, 75, 172, 173, 174, 175, 176, 177, 68, 179, 180, 181, 182, 183, 184, 61, 186, 187, 188, 189, 190, 191, 54, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 35, 34, 33, 32, 31, 30, 29, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Fw": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 96, 89, 82, 75, 68, 61, 54, 97, 90, 83, 76, 69, 62, 55, 98, 91, 84, 77, 70, 63, 56, 50, 51, 52, 53, 260, 253, 246, 57, 58, 59, 60, 261, 254, 247, 64, 65, 66, 67, 262, 255, 248, 71, 72, 73, 74, 263, 256, 249, 78, 79, 80, 81, 264, 257, 250, 85, 86, 87, 88, 265, 258, 251, 92, 93, 94, 95, 266, 259, 252, 141, 134, 127, 120, 113, 106, 99, 142, 135, 128, 121, 114, 107, 100, 143, 136, 129, 122, 115, 108, 101, 144, 137, 130, 123, 116, 109, 102, 145, 138, 131, 124, 117, 110, 103, 146, 139, 132, 125, 118, 111, 104, 147, 140, 133, 126, 119, 112, 105, 43, 36, 29, 151, 152, 153, 154, 44, 37, 30, 158, 159, 160, 161, 45, 38, 31, 165, 166, 167, 168, 46, 39, 32, 172, 173, 174, 175, 47, 40, 33, 179, 180, 181, 182, 48, 41, 34, 186, 187, 188, 189, 49, 42, 35, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 190, 183, 176, 169, 162, 155, 148, 191, 184, 177, 170, 163, 156, 149, 192, 185, 178, 171, 164, 157, 150, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Fw'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 150, 157, 164, 171, 178, 185, 192, 149, 156, 163, 170, 177, 184, 191, 148, 155, 162, 169, 176, 183, 190, 50, 51, 52, 53, 35, 42, 49, 57, 58, 59, 60, 34, 41, 48, 64, 65, 66, 67, 33, 40, 47, 71, 72, 73, 74, 32, 39, 46, 78, 79, 80, 81, 31, 38, 45, 85, 86, 87, 88, 30, 37, 44, 92, 93, 94, 95, 29, 36, 43, 105, 112, 119, 126, 133, 140, 147, 104, 111, 118, 125, 132, 139, 146, 103, 110, 117, 124, 131, 138, 145, 102, 109, 116, 123, 130, 137, 144, 101, 108, 115, 122, 129, 136, 143, 100, 107, 114, 121, 128, 135, 142, 99, 106, 113, 120, 127, 134, 141, 252, 259, 266, 151, 152, 153, 154, 251, 258, 265, 158, 159, 160, 161, 250, 257, 264, 165, 166, 167, 168, 249, 256, 263, 172, 173, 174, 175, 248, 255, 262, 179, 180, 181, 182, 247, 254, 261, 186, 187, 188, 189, 246, 253, 260, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 56, 63, 70, 77, 84, 91, 98, 55, 62, 69, 76, 83, 90, 97, 54, 61, 68, 75, 82, 89, 96, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Fw2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 50, 51, 52, 53, 192, 191, 190, 57, 58, 59, 60, 185, 184, 183, 64, 65, 66, 67, 178, 177, 176, 71, 72, 73, 74, 171, 170, 169, 78, 79, 80, 81, 164, 163, 162, 85, 86, 87, 88, 157, 156, 155, 92, 93, 94, 95, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 151, 152, 153, 154, 91, 90, 89, 158, 159, 160, 161, 84, 83, 82, 165, 166, 167, 168, 77, 76, 75, 172, 173, 174, 175, 70, 69, 68, 179, 180, 181, 182, 63, 62, 61, 186, 187, 188, 189, 56, 55, 54, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3L": ( 0, 1, 2, 243, 4, 5, 6, 7, 8, 9, 236, 11, 12, 13, 14, 15, 16, 229, 18, 19, 20, 21, 22, 23, 222, 25, 26, 27, 28, 29, 30, 215, 32, 33, 34, 35, 36, 37, 208, 39, 40, 41, 42, 43, 44, 201, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 3, 102, 103, 104, 105, 106, 107, 10, 109, 110, 111, 112, 113, 114, 17, 116, 117, 118, 119, 120, 121, 24, 123, 124, 125, 126, 127, 128, 31, 130, 131, 132, 133, 134, 135, 38, 137, 138, 139, 140, 141, 142, 45, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 290, 202, 203, 204, 205, 206, 207, 283, 209, 210, 211, 212, 213, 214, 276, 216, 217, 218, 219, 220, 221, 269, 223, 224, 225, 226, 227, 228, 262, 230, 231, 232, 233, 234, 235, 255, 237, 238, 239, 240, 241, 242, 248, 244, 245, 246, 247, 101, 249, 250, 251, 252, 253, 254, 108, 256, 257, 258, 259, 260, 261, 115, 263, 264, 265, 266, 267, 268, 122, 270, 271, 272, 273, 274, 275, 129, 277, 278, 279, 280, 281, 282, 136, 284, 285, 286, 287, 288, 289, 143, 291, 292, 293, 294,), "3L'": ( 0, 1, 2, 101, 4, 5, 6, 7, 8, 9, 108, 11, 12, 13, 14, 15, 16, 115, 18, 19, 20, 21, 22, 23, 122, 25, 26, 27, 28, 29, 30, 129, 32, 33, 34, 35, 36, 37, 136, 39, 40, 41, 42, 43, 44, 143, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 248, 102, 103, 104, 105, 106, 107, 255, 109, 110, 111, 112, 113, 114, 262, 116, 117, 118, 119, 120, 121, 269, 123, 124, 125, 126, 127, 128, 276, 130, 131, 132, 133, 134, 135, 283, 137, 138, 139, 140, 141, 142, 290, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 45, 202, 203, 204, 205, 206, 207, 38, 209, 210, 211, 212, 213, 214, 31, 216, 217, 218, 219, 220, 221, 24, 223, 224, 225, 226, 227, 228, 17, 230, 231, 232, 233, 234, 235, 10, 237, 238, 239, 240, 241, 242, 3, 244, 245, 246, 247, 243, 249, 250, 251, 252, 253, 254, 236, 256, 257, 258, 259, 260, 261, 229, 263, 264, 265, 266, 267, 268, 222, 270, 271, 272, 273, 274, 275, 215, 277, 278, 279, 280, 281, 282, 208, 284, 285, 286, 287, 288, 289, 201, 291, 292, 293, 294,), "3L2": ( 0, 1, 2, 248, 4, 5, 6, 7, 8, 9, 255, 11, 12, 13, 14, 15, 16, 262, 18, 19, 20, 21, 22, 23, 269, 25, 26, 27, 28, 29, 30, 276, 32, 33, 34, 35, 36, 37, 283, 39, 40, 41, 42, 43, 44, 290, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 243, 102, 103, 104, 105, 106, 107, 236, 109, 110, 111, 112, 113, 114, 229, 116, 117, 118, 119, 120, 121, 222, 123, 124, 125, 126, 127, 128, 215, 130, 131, 132, 133, 134, 135, 208, 137, 138, 139, 140, 141, 142, 201, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 143, 202, 203, 204, 205, 206, 207, 136, 209, 210, 211, 212, 213, 214, 129, 216, 217, 218, 219, 220, 221, 122, 223, 224, 225, 226, 227, 228, 115, 230, 231, 232, 233, 234, 235, 108, 237, 238, 239, 240, 241, 242, 101, 244, 245, 246, 247, 3, 249, 250, 251, 252, 253, 254, 10, 256, 257, 258, 259, 260, 261, 17, 263, 264, 265, 266, 267, 268, 24, 270, 271, 272, 273, 274, 275, 31, 277, 278, 279, 280, 281, 282, 38, 284, 285, 286, 287, 288, 289, 45, 291, 292, 293, 294,), "3Lw": ( 0, 245, 244, 243, 4, 5, 6, 7, 238, 237, 236, 11, 12, 13, 14, 231, 230, 229, 18, 19, 20, 21, 224, 223, 222, 25, 26, 27, 28, 217, 216, 215, 32, 33, 34, 35, 210, 209, 208, 39, 40, 41, 42, 203, 202, 201, 46, 47, 48, 49, 92, 85, 78, 71, 64, 57, 50, 93, 86, 79, 72, 65, 58, 51, 94, 87, 80, 73, 66, 59, 52, 95, 88, 81, 74, 67, 60, 53, 96, 89, 82, 75, 68, 61, 54, 97, 90, 83, 76, 69, 62, 55, 98, 91, 84, 77, 70, 63, 56, 1, 2, 3, 102, 103, 104, 105, 8, 9, 10, 109, 110, 111, 112, 15, 16, 17, 116, 117, 118, 119, 22, 23, 24, 123, 124, 125, 126, 29, 30, 31, 130, 131, 132, 133, 36, 37, 38, 137, 138, 139, 140, 43, 44, 45, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 290, 289, 288, 204, 205, 206, 207, 283, 282, 281, 211, 212, 213, 214, 276, 275, 274, 218, 219, 220, 221, 269, 268, 267, 225, 226, 227, 228, 262, 261, 260, 232, 233, 234, 235, 255, 254, 253, 239, 240, 241, 242, 248, 247, 246, 99, 100, 101, 249, 250, 251, 252, 106, 107, 108, 256, 257, 258, 259, 113, 114, 115, 263, 264, 265, 266, 120, 121, 122, 270, 271, 272, 273, 127, 128, 129, 277, 278, 279, 280, 134, 135, 136, 284, 285, 286, 287, 141, 142, 143, 291, 292, 293, 294,), "3Lw'": ( 0, 99, 100, 101, 4, 5, 6, 7, 106, 107, 108, 11, 12, 13, 14, 113, 114, 115, 18, 19, 20, 21, 120, 121, 122, 25, 26, 27, 28, 127, 128, 129, 32, 33, 34, 35, 134, 135, 136, 39, 40, 41, 42, 141, 142, 143, 46, 47, 48, 49, 56, 63, 70, 77, 84, 91, 98, 55, 62, 69, 76, 83, 90, 97, 54, 61, 68, 75, 82, 89, 96, 53, 60, 67, 74, 81, 88, 95, 52, 59, 66, 73, 80, 87, 94, 51, 58, 65, 72, 79, 86, 93, 50, 57, 64, 71, 78, 85, 92, 246, 247, 248, 102, 103, 104, 105, 253, 254, 255, 109, 110, 111, 112, 260, 261, 262, 116, 117, 118, 119, 267, 268, 269, 123, 124, 125, 126, 274, 275, 276, 130, 131, 132, 133, 281, 282, 283, 137, 138, 139, 140, 288, 289, 290, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 45, 44, 43, 204, 205, 206, 207, 38, 37, 36, 211, 212, 213, 214, 31, 30, 29, 218, 219, 220, 221, 24, 23, 22, 225, 226, 227, 228, 17, 16, 15, 232, 233, 234, 235, 10, 9, 8, 239, 240, 241, 242, 3, 2, 1, 245, 244, 243, 249, 250, 251, 252, 238, 237, 236, 256, 257, 258, 259, 231, 230, 229, 263, 264, 265, 266, 224, 223, 222, 270, 271, 272, 273, 217, 216, 215, 277, 278, 279, 280, 210, 209, 208, 284, 285, 286, 287, 203, 202, 201, 291, 292, 293, 294,), "3Lw2": ( 0, 246, 247, 248, 4, 5, 6, 7, 253, 254, 255, 11, 12, 13, 14, 260, 261, 262, 18, 19, 20, 21, 267, 268, 269, 25, 26, 27, 28, 274, 275, 276, 32, 33, 34, 35, 281, 282, 283, 39, 40, 41, 42, 288, 289, 290, 46, 47, 48, 49, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 245, 244, 243, 102, 103, 104, 105, 238, 237, 236, 109, 110, 111, 112, 231, 230, 229, 116, 117, 118, 119, 224, 223, 222, 123, 124, 125, 126, 217, 216, 215, 130, 131, 132, 133, 210, 209, 208, 137, 138, 139, 140, 203, 202, 201, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 143, 142, 141, 204, 205, 206, 207, 136, 135, 134, 211, 212, 213, 214, 129, 128, 127, 218, 219, 220, 221, 122, 121, 120, 225, 226, 227, 228, 115, 114, 113, 232, 233, 234, 235, 108, 107, 106, 239, 240, 241, 242, 101, 100, 99, 1, 2, 3, 249, 250, 251, 252, 8, 9, 10, 256, 257, 258, 259, 15, 16, 17, 263, 264, 265, 266, 22, 23, 24, 270, 271, 272, 273, 29, 30, 31, 277, 278, 279, 280, 36, 37, 38, 284, 285, 286, 287, 43, 44, 45, 291, 292, 293, 294,), "3R": ( 0, 1, 2, 3, 4, 103, 6, 7, 8, 9, 10, 11, 110, 13, 14, 15, 16, 17, 18, 117, 20, 21, 22, 23, 24, 25, 124, 27, 28, 29, 30, 31, 32, 131, 34, 35, 36, 37, 38, 39, 138, 41, 42, 43, 44, 45, 46, 145, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 250, 104, 105, 106, 107, 108, 109, 257, 111, 112, 113, 114, 115, 116, 264, 118, 119, 120, 121, 122, 123, 271, 125, 126, 127, 128, 129, 130, 278, 132, 133, 134, 135, 136, 137, 285, 139, 140, 141, 142, 143, 144, 292, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 47, 200, 201, 202, 203, 204, 205, 40, 207, 208, 209, 210, 211, 212, 33, 214, 215, 216, 217, 218, 219, 26, 221, 222, 223, 224, 225, 226, 19, 228, 229, 230, 231, 232, 233, 12, 235, 236, 237, 238, 239, 240, 5, 242, 243, 244, 245, 246, 247, 248, 249, 241, 251, 252, 253, 254, 255, 256, 234, 258, 259, 260, 261, 262, 263, 227, 265, 266, 267, 268, 269, 270, 220, 272, 273, 274, 275, 276, 277, 213, 279, 280, 281, 282, 283, 284, 206, 286, 287, 288, 289, 290, 291, 199, 293, 294,), "3R'": ( 0, 1, 2, 3, 4, 241, 6, 7, 8, 9, 10, 11, 234, 13, 14, 15, 16, 17, 18, 227, 20, 21, 22, 23, 24, 25, 220, 27, 28, 29, 30, 31, 32, 213, 34, 35, 36, 37, 38, 39, 206, 41, 42, 43, 44, 45, 46, 199, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 5, 104, 105, 106, 107, 108, 109, 12, 111, 112, 113, 114, 115, 116, 19, 118, 119, 120, 121, 122, 123, 26, 125, 126, 127, 128, 129, 130, 33, 132, 133, 134, 135, 136, 137, 40, 139, 140, 141, 142, 143, 144, 47, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 292, 200, 201, 202, 203, 204, 205, 285, 207, 208, 209, 210, 211, 212, 278, 214, 215, 216, 217, 218, 219, 271, 221, 222, 223, 224, 225, 226, 264, 228, 229, 230, 231, 232, 233, 257, 235, 236, 237, 238, 239, 240, 250, 242, 243, 244, 245, 246, 247, 248, 249, 103, 251, 252, 253, 254, 255, 256, 110, 258, 259, 260, 261, 262, 263, 117, 265, 266, 267, 268, 269, 270, 124, 272, 273, 274, 275, 276, 277, 131, 279, 280, 281, 282, 283, 284, 138, 286, 287, 288, 289, 290, 291, 145, 293, 294,), "3R2": ( 0, 1, 2, 3, 4, 250, 6, 7, 8, 9, 10, 11, 257, 13, 14, 15, 16, 17, 18, 264, 20, 21, 22, 23, 24, 25, 271, 27, 28, 29, 30, 31, 32, 278, 34, 35, 36, 37, 38, 39, 285, 41, 42, 43, 44, 45, 46, 292, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 241, 104, 105, 106, 107, 108, 109, 234, 111, 112, 113, 114, 115, 116, 227, 118, 119, 120, 121, 122, 123, 220, 125, 126, 127, 128, 129, 130, 213, 132, 133, 134, 135, 136, 137, 206, 139, 140, 141, 142, 143, 144, 199, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 145, 200, 201, 202, 203, 204, 205, 138, 207, 208, 209, 210, 211, 212, 131, 214, 215, 216, 217, 218, 219, 124, 221, 222, 223, 224, 225, 226, 117, 228, 229, 230, 231, 232, 233, 110, 235, 236, 237, 238, 239, 240, 103, 242, 243, 244, 245, 246, 247, 248, 249, 5, 251, 252, 253, 254, 255, 256, 12, 258, 259, 260, 261, 262, 263, 19, 265, 266, 267, 268, 269, 270, 26, 272, 273, 274, 275, 276, 277, 33, 279, 280, 281, 282, 283, 284, 40, 286, 287, 288, 289, 290, 291, 47, 293, 294,), "3Rw": ( 0, 1, 2, 3, 4, 103, 104, 105, 8, 9, 10, 11, 110, 111, 112, 15, 16, 17, 18, 117, 118, 119, 22, 23, 24, 25, 124, 125, 126, 29, 30, 31, 32, 131, 132, 133, 36, 37, 38, 39, 138, 139, 140, 43, 44, 45, 46, 145, 146, 147, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 250, 251, 252, 106, 107, 108, 109, 257, 258, 259, 113, 114, 115, 116, 264, 265, 266, 120, 121, 122, 123, 271, 272, 273, 127, 128, 129, 130, 278, 279, 280, 134, 135, 136, 137, 285, 286, 287, 141, 142, 143, 144, 292, 293, 294, 190, 183, 176, 169, 162, 155, 148, 191, 184, 177, 170, 163, 156, 149, 192, 185, 178, 171, 164, 157, 150, 193, 186, 179, 172, 165, 158, 151, 194, 187, 180, 173, 166, 159, 152, 195, 188, 181, 174, 167, 160, 153, 196, 189, 182, 175, 168, 161, 154, 49, 48, 47, 200, 201, 202, 203, 42, 41, 40, 207, 208, 209, 210, 35, 34, 33, 214, 215, 216, 217, 28, 27, 26, 221, 222, 223, 224, 21, 20, 19, 228, 229, 230, 231, 14, 13, 12, 235, 236, 237, 238, 7, 6, 5, 242, 243, 244, 245, 246, 247, 248, 249, 241, 240, 239, 253, 254, 255, 256, 234, 233, 232, 260, 261, 262, 263, 227, 226, 225, 267, 268, 269, 270, 220, 219, 218, 274, 275, 276, 277, 213, 212, 211, 281, 282, 283, 284, 206, 205, 204, 288, 289, 290, 291, 199, 198, 197,), "3Rw'": ( 0, 1, 2, 3, 4, 241, 240, 239, 8, 9, 10, 11, 234, 233, 232, 15, 16, 17, 18, 227, 226, 225, 22, 23, 24, 25, 220, 219, 218, 29, 30, 31, 32, 213, 212, 211, 36, 37, 38, 39, 206, 205, 204, 43, 44, 45, 46, 199, 198, 197, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 5, 6, 7, 106, 107, 108, 109, 12, 13, 14, 113, 114, 115, 116, 19, 20, 21, 120, 121, 122, 123, 26, 27, 28, 127, 128, 129, 130, 33, 34, 35, 134, 135, 136, 137, 40, 41, 42, 141, 142, 143, 144, 47, 48, 49, 154, 161, 168, 175, 182, 189, 196, 153, 160, 167, 174, 181, 188, 195, 152, 159, 166, 173, 180, 187, 194, 151, 158, 165, 172, 179, 186, 193, 150, 157, 164, 171, 178, 185, 192, 149, 156, 163, 170, 177, 184, 191, 148, 155, 162, 169, 176, 183, 190, 294, 293, 292, 200, 201, 202, 203, 287, 286, 285, 207, 208, 209, 210, 280, 279, 278, 214, 215, 216, 217, 273, 272, 271, 221, 222, 223, 224, 266, 265, 264, 228, 229, 230, 231, 259, 258, 257, 235, 236, 237, 238, 252, 251, 250, 242, 243, 244, 245, 246, 247, 248, 249, 103, 104, 105, 253, 254, 255, 256, 110, 111, 112, 260, 261, 262, 263, 117, 118, 119, 267, 268, 269, 270, 124, 125, 126, 274, 275, 276, 277, 131, 132, 133, 281, 282, 283, 284, 138, 139, 140, 288, 289, 290, 291, 145, 146, 147,), "3Rw2": ( 0, 1, 2, 3, 4, 250, 251, 252, 8, 9, 10, 11, 257, 258, 259, 15, 16, 17, 18, 264, 265, 266, 22, 23, 24, 25, 271, 272, 273, 29, 30, 31, 32, 278, 279, 280, 36, 37, 38, 39, 285, 286, 287, 43, 44, 45, 46, 292, 293, 294, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 241, 240, 239, 106, 107, 108, 109, 234, 233, 232, 113, 114, 115, 116, 227, 226, 225, 120, 121, 122, 123, 220, 219, 218, 127, 128, 129, 130, 213, 212, 211, 134, 135, 136, 137, 206, 205, 204, 141, 142, 143, 144, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 200, 201, 202, 203, 140, 139, 138, 207, 208, 209, 210, 133, 132, 131, 214, 215, 216, 217, 126, 125, 124, 221, 222, 223, 224, 119, 118, 117, 228, 229, 230, 231, 112, 111, 110, 235, 236, 237, 238, 105, 104, 103, 242, 243, 244, 245, 246, 247, 248, 249, 5, 6, 7, 253, 254, 255, 256, 12, 13, 14, 260, 261, 262, 263, 19, 20, 21, 267, 268, 269, 270, 26, 27, 28, 274, 275, 276, 277, 33, 34, 35, 281, 282, 283, 284, 40, 41, 42, 288, 289, 290, 291, 47, 48, 49,), "3U": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 113, 114, 115, 116, 117, 118, 119, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 162, 163, 164, 165, 166, 167, 168, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 211, 212, 213, 214, 215, 216, 217, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 64, 65, 66, 67, 68, 69, 70, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3U'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 211, 212, 213, 214, 215, 216, 217, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 64, 65, 66, 67, 68, 69, 70, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 113, 114, 115, 116, 117, 118, 119, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 162, 163, 164, 165, 166, 167, 168, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3U2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 162, 163, 164, 165, 166, 167, 168, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 211, 212, 213, 214, 215, 216, 217, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 64, 65, 66, 67, 68, 69, 70, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 113, 114, 115, 116, 117, 118, 119, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Uw": ( 0, 43, 36, 29, 22, 15, 8, 1, 44, 37, 30, 23, 16, 9, 2, 45, 38, 31, 24, 17, 10, 3, 46, 39, 32, 25, 18, 11, 4, 47, 40, 33, 26, 19, 12, 5, 48, 41, 34, 27, 20, 13, 6, 49, 42, 35, 28, 21, 14, 7, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Uw'": ( 0, 7, 14, 21, 28, 35, 42, 49, 6, 13, 20, 27, 34, 41, 48, 5, 12, 19, 26, 33, 40, 47, 4, 11, 18, 25, 32, 39, 46, 3, 10, 17, 24, 31, 38, 45, 2, 9, 16, 23, 30, 37, 44, 1, 8, 15, 22, 29, 36, 43, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "3Uw2": ( 0, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "B": ( 0, 154, 161, 168, 175, 182, 189, 196, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 7, 51, 52, 53, 54, 55, 56, 6, 58, 59, 60, 61, 62, 63, 5, 65, 66, 67, 68, 69, 70, 4, 72, 73, 74, 75, 76, 77, 3, 79, 80, 81, 82, 83, 84, 2, 86, 87, 88, 89, 90, 91, 1, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 294, 155, 156, 157, 158, 159, 160, 293, 162, 163, 164, 165, 166, 167, 292, 169, 170, 171, 172, 173, 174, 291, 176, 177, 178, 179, 180, 181, 290, 183, 184, 185, 186, 187, 188, 289, 190, 191, 192, 193, 194, 195, 288, 239, 232, 225, 218, 211, 204, 197, 240, 233, 226, 219, 212, 205, 198, 241, 234, 227, 220, 213, 206, 199, 242, 235, 228, 221, 214, 207, 200, 243, 236, 229, 222, 215, 208, 201, 244, 237, 230, 223, 216, 209, 202, 245, 238, 231, 224, 217, 210, 203, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 50, 57, 64, 71, 78, 85, 92,), "B'": ( 0, 92, 85, 78, 71, 64, 57, 50, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 288, 51, 52, 53, 54, 55, 56, 289, 58, 59, 60, 61, 62, 63, 290, 65, 66, 67, 68, 69, 70, 291, 72, 73, 74, 75, 76, 77, 292, 79, 80, 81, 82, 83, 84, 293, 86, 87, 88, 89, 90, 91, 294, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 1, 155, 156, 157, 158, 159, 160, 2, 162, 163, 164, 165, 166, 167, 3, 169, 170, 171, 172, 173, 174, 4, 176, 177, 178, 179, 180, 181, 5, 183, 184, 185, 186, 187, 188, 6, 190, 191, 192, 193, 194, 195, 7, 203, 210, 217, 224, 231, 238, 245, 202, 209, 216, 223, 230, 237, 244, 201, 208, 215, 222, 229, 236, 243, 200, 207, 214, 221, 228, 235, 242, 199, 206, 213, 220, 227, 234, 241, 198, 205, 212, 219, 226, 233, 240, 197, 204, 211, 218, 225, 232, 239, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 196, 189, 182, 175, 168, 161, 154,), "B2": ( 0, 294, 293, 292, 291, 290, 289, 288, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 196, 51, 52, 53, 54, 55, 56, 189, 58, 59, 60, 61, 62, 63, 182, 65, 66, 67, 68, 69, 70, 175, 72, 73, 74, 75, 76, 77, 168, 79, 80, 81, 82, 83, 84, 161, 86, 87, 88, 89, 90, 91, 154, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 92, 155, 156, 157, 158, 159, 160, 85, 162, 163, 164, 165, 166, 167, 78, 169, 170, 171, 172, 173, 174, 71, 176, 177, 178, 179, 180, 181, 64, 183, 184, 185, 186, 187, 188, 57, 190, 191, 192, 193, 194, 195, 50, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 7, 6, 5, 4, 3, 2, 1,), "Bw": ( 0, 154, 161, 168, 175, 182, 189, 196, 153, 160, 167, 174, 181, 188, 195, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 7, 14, 52, 53, 54, 55, 56, 6, 13, 59, 60, 61, 62, 63, 5, 12, 66, 67, 68, 69, 70, 4, 11, 73, 74, 75, 76, 77, 3, 10, 80, 81, 82, 83, 84, 2, 9, 87, 88, 89, 90, 91, 1, 8, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 287, 294, 155, 156, 157, 158, 159, 286, 293, 162, 163, 164, 165, 166, 285, 292, 169, 170, 171, 172, 173, 284, 291, 176, 177, 178, 179, 180, 283, 290, 183, 184, 185, 186, 187, 282, 289, 190, 191, 192, 193, 194, 281, 288, 239, 232, 225, 218, 211, 204, 197, 240, 233, 226, 219, 212, 205, 198, 241, 234, 227, 220, 213, 206, 199, 242, 235, 228, 221, 214, 207, 200, 243, 236, 229, 222, 215, 208, 201, 244, 237, 230, 223, 216, 209, 202, 245, 238, 231, 224, 217, 210, 203, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 51, 58, 65, 72, 79, 86, 93, 50, 57, 64, 71, 78, 85, 92,), "Bw'": ( 0, 92, 85, 78, 71, 64, 57, 50, 93, 86, 79, 72, 65, 58, 51, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 288, 281, 52, 53, 54, 55, 56, 289, 282, 59, 60, 61, 62, 63, 290, 283, 66, 67, 68, 69, 70, 291, 284, 73, 74, 75, 76, 77, 292, 285, 80, 81, 82, 83, 84, 293, 286, 87, 88, 89, 90, 91, 294, 287, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 8, 1, 155, 156, 157, 158, 159, 9, 2, 162, 163, 164, 165, 166, 10, 3, 169, 170, 171, 172, 173, 11, 4, 176, 177, 178, 179, 180, 12, 5, 183, 184, 185, 186, 187, 13, 6, 190, 191, 192, 193, 194, 14, 7, 203, 210, 217, 224, 231, 238, 245, 202, 209, 216, 223, 230, 237, 244, 201, 208, 215, 222, 229, 236, 243, 200, 207, 214, 221, 228, 235, 242, 199, 206, 213, 220, 227, 234, 241, 198, 205, 212, 219, 226, 233, 240, 197, 204, 211, 218, 225, 232, 239, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 195, 188, 181, 174, 167, 160, 153, 196, 189, 182, 175, 168, 161, 154,), "Bw2": ( 0, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 196, 195, 52, 53, 54, 55, 56, 189, 188, 59, 60, 61, 62, 63, 182, 181, 66, 67, 68, 69, 70, 175, 174, 73, 74, 75, 76, 77, 168, 167, 80, 81, 82, 83, 84, 161, 160, 87, 88, 89, 90, 91, 154, 153, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 93, 92, 155, 156, 157, 158, 159, 86, 85, 162, 163, 164, 165, 166, 79, 78, 169, 170, 171, 172, 173, 72, 71, 176, 177, 178, 179, 180, 65, 64, 183, 184, 185, 186, 187, 58, 57, 190, 191, 192, 193, 194, 51, 50, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,), "D": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 239, 240, 241, 242, 243, 244, 245, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 92, 93, 94, 95, 96, 97, 98, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 141, 142, 143, 144, 145, 146, 147, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 190, 191, 192, 193, 194, 195, 196, 288, 281, 274, 267, 260, 253, 246, 289, 282, 275, 268, 261, 254, 247, 290, 283, 276, 269, 262, 255, 248, 291, 284, 277, 270, 263, 256, 249, 292, 285, 278, 271, 264, 257, 250, 293, 286, 279, 272, 265, 258, 251, 294, 287, 280, 273, 266, 259, 252,), "D'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 141, 142, 143, 144, 145, 146, 147, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 190, 191, 192, 193, 194, 195, 196, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 239, 240, 241, 242, 243, 244, 245, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 92, 93, 94, 95, 96, 97, 98, 252, 259, 266, 273, 280, 287, 294, 251, 258, 265, 272, 279, 286, 293, 250, 257, 264, 271, 278, 285, 292, 249, 256, 263, 270, 277, 284, 291, 248, 255, 262, 269, 276, 283, 290, 247, 254, 261, 268, 275, 282, 289, 246, 253, 260, 267, 274, 281, 288,), "D2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 190, 191, 192, 193, 194, 195, 196, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 239, 240, 241, 242, 243, 244, 245, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 92, 93, 94, 95, 96, 97, 98, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 141, 142, 143, 144, 145, 146, 147, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246,), "Dw": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 288, 281, 274, 267, 260, 253, 246, 289, 282, 275, 268, 261, 254, 247, 290, 283, 276, 269, 262, 255, 248, 291, 284, 277, 270, 263, 256, 249, 292, 285, 278, 271, 264, 257, 250, 293, 286, 279, 272, 265, 258, 251, 294, 287, 280, 273, 266, 259, 252,), "Dw'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 252, 259, 266, 273, 280, 287, 294, 251, 258, 265, 272, 279, 286, 293, 250, 257, 264, 271, 278, 285, 292, 249, 256, 263, 270, 277, 284, 291, 248, 255, 262, 269, 276, 283, 290, 247, 254, 261, 268, 275, 282, 289, 246, 253, 260, 267, 274, 281, 288,), "Dw2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246,), "F": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 98, 91, 84, 77, 70, 63, 56, 50, 51, 52, 53, 54, 55, 246, 57, 58, 59, 60, 61, 62, 247, 64, 65, 66, 67, 68, 69, 248, 71, 72, 73, 74, 75, 76, 249, 78, 79, 80, 81, 82, 83, 250, 85, 86, 87, 88, 89, 90, 251, 92, 93, 94, 95, 96, 97, 252, 141, 134, 127, 120, 113, 106, 99, 142, 135, 128, 121, 114, 107, 100, 143, 136, 129, 122, 115, 108, 101, 144, 137, 130, 123, 116, 109, 102, 145, 138, 131, 124, 117, 110, 103, 146, 139, 132, 125, 118, 111, 104, 147, 140, 133, 126, 119, 112, 105, 43, 149, 150, 151, 152, 153, 154, 44, 156, 157, 158, 159, 160, 161, 45, 163, 164, 165, 166, 167, 168, 46, 170, 171, 172, 173, 174, 175, 47, 177, 178, 179, 180, 181, 182, 48, 184, 185, 186, 187, 188, 189, 49, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 190, 183, 176, 169, 162, 155, 148, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "F'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 148, 155, 162, 169, 176, 183, 190, 50, 51, 52, 53, 54, 55, 49, 57, 58, 59, 60, 61, 62, 48, 64, 65, 66, 67, 68, 69, 47, 71, 72, 73, 74, 75, 76, 46, 78, 79, 80, 81, 82, 83, 45, 85, 86, 87, 88, 89, 90, 44, 92, 93, 94, 95, 96, 97, 43, 105, 112, 119, 126, 133, 140, 147, 104, 111, 118, 125, 132, 139, 146, 103, 110, 117, 124, 131, 138, 145, 102, 109, 116, 123, 130, 137, 144, 101, 108, 115, 122, 129, 136, 143, 100, 107, 114, 121, 128, 135, 142, 99, 106, 113, 120, 127, 134, 141, 252, 149, 150, 151, 152, 153, 154, 251, 156, 157, 158, 159, 160, 161, 250, 163, 164, 165, 166, 167, 168, 249, 170, 171, 172, 173, 174, 175, 248, 177, 178, 179, 180, 181, 182, 247, 184, 185, 186, 187, 188, 189, 246, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 56, 63, 70, 77, 84, 91, 98, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "F2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 252, 251, 250, 249, 248, 247, 246, 50, 51, 52, 53, 54, 55, 190, 57, 58, 59, 60, 61, 62, 183, 64, 65, 66, 67, 68, 69, 176, 71, 72, 73, 74, 75, 76, 169, 78, 79, 80, 81, 82, 83, 162, 85, 86, 87, 88, 89, 90, 155, 92, 93, 94, 95, 96, 97, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 149, 150, 151, 152, 153, 154, 91, 156, 157, 158, 159, 160, 161, 84, 163, 164, 165, 166, 167, 168, 77, 170, 171, 172, 173, 174, 175, 70, 177, 178, 179, 180, 181, 182, 63, 184, 185, 186, 187, 188, 189, 56, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 49, 48, 47, 46, 45, 44, 43, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "Fw": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 97, 90, 83, 76, 69, 62, 55, 98, 91, 84, 77, 70, 63, 56, 50, 51, 52, 53, 54, 253, 246, 57, 58, 59, 60, 61, 254, 247, 64, 65, 66, 67, 68, 255, 248, 71, 72, 73, 74, 75, 256, 249, 78, 79, 80, 81, 82, 257, 250, 85, 86, 87, 88, 89, 258, 251, 92, 93, 94, 95, 96, 259, 252, 141, 134, 127, 120, 113, 106, 99, 142, 135, 128, 121, 114, 107, 100, 143, 136, 129, 122, 115, 108, 101, 144, 137, 130, 123, 116, 109, 102, 145, 138, 131, 124, 117, 110, 103, 146, 139, 132, 125, 118, 111, 104, 147, 140, 133, 126, 119, 112, 105, 43, 36, 150, 151, 152, 153, 154, 44, 37, 157, 158, 159, 160, 161, 45, 38, 164, 165, 166, 167, 168, 46, 39, 171, 172, 173, 174, 175, 47, 40, 178, 179, 180, 181, 182, 48, 41, 185, 186, 187, 188, 189, 49, 42, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 190, 183, 176, 169, 162, 155, 148, 191, 184, 177, 170, 163, 156, 149, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "Fw'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 149, 156, 163, 170, 177, 184, 191, 148, 155, 162, 169, 176, 183, 190, 50, 51, 52, 53, 54, 42, 49, 57, 58, 59, 60, 61, 41, 48, 64, 65, 66, 67, 68, 40, 47, 71, 72, 73, 74, 75, 39, 46, 78, 79, 80, 81, 82, 38, 45, 85, 86, 87, 88, 89, 37, 44, 92, 93, 94, 95, 96, 36, 43, 105, 112, 119, 126, 133, 140, 147, 104, 111, 118, 125, 132, 139, 146, 103, 110, 117, 124, 131, 138, 145, 102, 109, 116, 123, 130, 137, 144, 101, 108, 115, 122, 129, 136, 143, 100, 107, 114, 121, 128, 135, 142, 99, 106, 113, 120, 127, 134, 141, 252, 259, 150, 151, 152, 153, 154, 251, 258, 157, 158, 159, 160, 161, 250, 257, 164, 165, 166, 167, 168, 249, 256, 171, 172, 173, 174, 175, 248, 255, 178, 179, 180, 181, 182, 247, 254, 185, 186, 187, 188, 189, 246, 253, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 56, 63, 70, 77, 84, 91, 98, 55, 62, 69, 76, 83, 90, 97, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "Fw2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 50, 51, 52, 53, 54, 191, 190, 57, 58, 59, 60, 61, 184, 183, 64, 65, 66, 67, 68, 177, 176, 71, 72, 73, 74, 75, 170, 169, 78, 79, 80, 81, 82, 163, 162, 85, 86, 87, 88, 89, 156, 155, 92, 93, 94, 95, 96, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 150, 151, 152, 153, 154, 91, 90, 157, 158, 159, 160, 161, 84, 83, 164, 165, 166, 167, 168, 77, 76, 171, 172, 173, 174, 175, 70, 69, 178, 179, 180, 181, 182, 63, 62, 185, 186, 187, 188, 189, 56, 55, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "L": ( 0, 245, 2, 3, 4, 5, 6, 7, 238, 9, 10, 11, 12, 13, 14, 231, 16, 17, 18, 19, 20, 21, 224, 23, 24, 25, 26, 27, 28, 217, 30, 31, 32, 33, 34, 35, 210, 37, 38, 39, 40, 41, 42, 203, 44, 45, 46, 47, 48, 49, 92, 85, 78, 71, 64, 57, 50, 93, 86, 79, 72, 65, 58, 51, 94, 87, 80, 73, 66, 59, 52, 95, 88, 81, 74, 67, 60, 53, 96, 89, 82, 75, 68, 61, 54, 97, 90, 83, 76, 69, 62, 55, 98, 91, 84, 77, 70, 63, 56, 1, 100, 101, 102, 103, 104, 105, 8, 107, 108, 109, 110, 111, 112, 15, 114, 115, 116, 117, 118, 119, 22, 121, 122, 123, 124, 125, 126, 29, 128, 129, 130, 131, 132, 133, 36, 135, 136, 137, 138, 139, 140, 43, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 288, 204, 205, 206, 207, 208, 209, 281, 211, 212, 213, 214, 215, 216, 274, 218, 219, 220, 221, 222, 223, 267, 225, 226, 227, 228, 229, 230, 260, 232, 233, 234, 235, 236, 237, 253, 239, 240, 241, 242, 243, 244, 246, 99, 247, 248, 249, 250, 251, 252, 106, 254, 255, 256, 257, 258, 259, 113, 261, 262, 263, 264, 265, 266, 120, 268, 269, 270, 271, 272, 273, 127, 275, 276, 277, 278, 279, 280, 134, 282, 283, 284, 285, 286, 287, 141, 289, 290, 291, 292, 293, 294,), "L'": ( 0, 99, 2, 3, 4, 5, 6, 7, 106, 9, 10, 11, 12, 13, 14, 113, 16, 17, 18, 19, 20, 21, 120, 23, 24, 25, 26, 27, 28, 127, 30, 31, 32, 33, 34, 35, 134, 37, 38, 39, 40, 41, 42, 141, 44, 45, 46, 47, 48, 49, 56, 63, 70, 77, 84, 91, 98, 55, 62, 69, 76, 83, 90, 97, 54, 61, 68, 75, 82, 89, 96, 53, 60, 67, 74, 81, 88, 95, 52, 59, 66, 73, 80, 87, 94, 51, 58, 65, 72, 79, 86, 93, 50, 57, 64, 71, 78, 85, 92, 246, 100, 101, 102, 103, 104, 105, 253, 107, 108, 109, 110, 111, 112, 260, 114, 115, 116, 117, 118, 119, 267, 121, 122, 123, 124, 125, 126, 274, 128, 129, 130, 131, 132, 133, 281, 135, 136, 137, 138, 139, 140, 288, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 43, 204, 205, 206, 207, 208, 209, 36, 211, 212, 213, 214, 215, 216, 29, 218, 219, 220, 221, 222, 223, 22, 225, 226, 227, 228, 229, 230, 15, 232, 233, 234, 235, 236, 237, 8, 239, 240, 241, 242, 243, 244, 1, 245, 247, 248, 249, 250, 251, 252, 238, 254, 255, 256, 257, 258, 259, 231, 261, 262, 263, 264, 265, 266, 224, 268, 269, 270, 271, 272, 273, 217, 275, 276, 277, 278, 279, 280, 210, 282, 283, 284, 285, 286, 287, 203, 289, 290, 291, 292, 293, 294,), "L2": ( 0, 246, 2, 3, 4, 5, 6, 7, 253, 9, 10, 11, 12, 13, 14, 260, 16, 17, 18, 19, 20, 21, 267, 23, 24, 25, 26, 27, 28, 274, 30, 31, 32, 33, 34, 35, 281, 37, 38, 39, 40, 41, 42, 288, 44, 45, 46, 47, 48, 49, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 245, 100, 101, 102, 103, 104, 105, 238, 107, 108, 109, 110, 111, 112, 231, 114, 115, 116, 117, 118, 119, 224, 121, 122, 123, 124, 125, 126, 217, 128, 129, 130, 131, 132, 133, 210, 135, 136, 137, 138, 139, 140, 203, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 141, 204, 205, 206, 207, 208, 209, 134, 211, 212, 213, 214, 215, 216, 127, 218, 219, 220, 221, 222, 223, 120, 225, 226, 227, 228, 229, 230, 113, 232, 233, 234, 235, 236, 237, 106, 239, 240, 241, 242, 243, 244, 99, 1, 247, 248, 249, 250, 251, 252, 8, 254, 255, 256, 257, 258, 259, 15, 261, 262, 263, 264, 265, 266, 22, 268, 269, 270, 271, 272, 273, 29, 275, 276, 277, 278, 279, 280, 36, 282, 283, 284, 285, 286, 287, 43, 289, 290, 291, 292, 293, 294,), "Lw": ( 0, 245, 244, 3, 4, 5, 6, 7, 238, 237, 10, 11, 12, 13, 14, 231, 230, 17, 18, 19, 20, 21, 224, 223, 24, 25, 26, 27, 28, 217, 216, 31, 32, 33, 34, 35, 210, 209, 38, 39, 40, 41, 42, 203, 202, 45, 46, 47, 48, 49, 92, 85, 78, 71, 64, 57, 50, 93, 86, 79, 72, 65, 58, 51, 94, 87, 80, 73, 66, 59, 52, 95, 88, 81, 74, 67, 60, 53, 96, 89, 82, 75, 68, 61, 54, 97, 90, 83, 76, 69, 62, 55, 98, 91, 84, 77, 70, 63, 56, 1, 2, 101, 102, 103, 104, 105, 8, 9, 108, 109, 110, 111, 112, 15, 16, 115, 116, 117, 118, 119, 22, 23, 122, 123, 124, 125, 126, 29, 30, 129, 130, 131, 132, 133, 36, 37, 136, 137, 138, 139, 140, 43, 44, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 289, 288, 204, 205, 206, 207, 208, 282, 281, 211, 212, 213, 214, 215, 275, 274, 218, 219, 220, 221, 222, 268, 267, 225, 226, 227, 228, 229, 261, 260, 232, 233, 234, 235, 236, 254, 253, 239, 240, 241, 242, 243, 247, 246, 99, 100, 248, 249, 250, 251, 252, 106, 107, 255, 256, 257, 258, 259, 113, 114, 262, 263, 264, 265, 266, 120, 121, 269, 270, 271, 272, 273, 127, 128, 276, 277, 278, 279, 280, 134, 135, 283, 284, 285, 286, 287, 141, 142, 290, 291, 292, 293, 294,), "Lw'": ( 0, 99, 100, 3, 4, 5, 6, 7, 106, 107, 10, 11, 12, 13, 14, 113, 114, 17, 18, 19, 20, 21, 120, 121, 24, 25, 26, 27, 28, 127, 128, 31, 32, 33, 34, 35, 134, 135, 38, 39, 40, 41, 42, 141, 142, 45, 46, 47, 48, 49, 56, 63, 70, 77, 84, 91, 98, 55, 62, 69, 76, 83, 90, 97, 54, 61, 68, 75, 82, 89, 96, 53, 60, 67, 74, 81, 88, 95, 52, 59, 66, 73, 80, 87, 94, 51, 58, 65, 72, 79, 86, 93, 50, 57, 64, 71, 78, 85, 92, 246, 247, 101, 102, 103, 104, 105, 253, 254, 108, 109, 110, 111, 112, 260, 261, 115, 116, 117, 118, 119, 267, 268, 122, 123, 124, 125, 126, 274, 275, 129, 130, 131, 132, 133, 281, 282, 136, 137, 138, 139, 140, 288, 289, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 44, 43, 204, 205, 206, 207, 208, 37, 36, 211, 212, 213, 214, 215, 30, 29, 218, 219, 220, 221, 222, 23, 22, 225, 226, 227, 228, 229, 16, 15, 232, 233, 234, 235, 236, 9, 8, 239, 240, 241, 242, 243, 2, 1, 245, 244, 248, 249, 250, 251, 252, 238, 237, 255, 256, 257, 258, 259, 231, 230, 262, 263, 264, 265, 266, 224, 223, 269, 270, 271, 272, 273, 217, 216, 276, 277, 278, 279, 280, 210, 209, 283, 284, 285, 286, 287, 203, 202, 290, 291, 292, 293, 294,), "Lw2": ( 0, 246, 247, 3, 4, 5, 6, 7, 253, 254, 10, 11, 12, 13, 14, 260, 261, 17, 18, 19, 20, 21, 267, 268, 24, 25, 26, 27, 28, 274, 275, 31, 32, 33, 34, 35, 281, 282, 38, 39, 40, 41, 42, 288, 289, 45, 46, 47, 48, 49, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 245, 244, 101, 102, 103, 104, 105, 238, 237, 108, 109, 110, 111, 112, 231, 230, 115, 116, 117, 118, 119, 224, 223, 122, 123, 124, 125, 126, 217, 216, 129, 130, 131, 132, 133, 210, 209, 136, 137, 138, 139, 140, 203, 202, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 142, 141, 204, 205, 206, 207, 208, 135, 134, 211, 212, 213, 214, 215, 128, 127, 218, 219, 220, 221, 222, 121, 120, 225, 226, 227, 228, 229, 114, 113, 232, 233, 234, 235, 236, 107, 106, 239, 240, 241, 242, 243, 100, 99, 1, 2, 248, 249, 250, 251, 252, 8, 9, 255, 256, 257, 258, 259, 15, 16, 262, 263, 264, 265, 266, 22, 23, 269, 270, 271, 272, 273, 29, 30, 276, 277, 278, 279, 280, 36, 37, 283, 284, 285, 286, 287, 43, 44, 290, 291, 292, 293, 294,), "R": ( 0, 1, 2, 3, 4, 5, 6, 105, 8, 9, 10, 11, 12, 13, 112, 15, 16, 17, 18, 19, 20, 119, 22, 23, 24, 25, 26, 27, 126, 29, 30, 31, 32, 33, 34, 133, 36, 37, 38, 39, 40, 41, 140, 43, 44, 45, 46, 47, 48, 147, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 252, 106, 107, 108, 109, 110, 111, 259, 113, 114, 115, 116, 117, 118, 266, 120, 121, 122, 123, 124, 125, 273, 127, 128, 129, 130, 131, 132, 280, 134, 135, 136, 137, 138, 139, 287, 141, 142, 143, 144, 145, 146, 294, 190, 183, 176, 169, 162, 155, 148, 191, 184, 177, 170, 163, 156, 149, 192, 185, 178, 171, 164, 157, 150, 193, 186, 179, 172, 165, 158, 151, 194, 187, 180, 173, 166, 159, 152, 195, 188, 181, 174, 167, 160, 153, 196, 189, 182, 175, 168, 161, 154, 49, 198, 199, 200, 201, 202, 203, 42, 205, 206, 207, 208, 209, 210, 35, 212, 213, 214, 215, 216, 217, 28, 219, 220, 221, 222, 223, 224, 21, 226, 227, 228, 229, 230, 231, 14, 233, 234, 235, 236, 237, 238, 7, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 239, 253, 254, 255, 256, 257, 258, 232, 260, 261, 262, 263, 264, 265, 225, 267, 268, 269, 270, 271, 272, 218, 274, 275, 276, 277, 278, 279, 211, 281, 282, 283, 284, 285, 286, 204, 288, 289, 290, 291, 292, 293, 197,), "R'": ( 0, 1, 2, 3, 4, 5, 6, 239, 8, 9, 10, 11, 12, 13, 232, 15, 16, 17, 18, 19, 20, 225, 22, 23, 24, 25, 26, 27, 218, 29, 30, 31, 32, 33, 34, 211, 36, 37, 38, 39, 40, 41, 204, 43, 44, 45, 46, 47, 48, 197, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 7, 106, 107, 108, 109, 110, 111, 14, 113, 114, 115, 116, 117, 118, 21, 120, 121, 122, 123, 124, 125, 28, 127, 128, 129, 130, 131, 132, 35, 134, 135, 136, 137, 138, 139, 42, 141, 142, 143, 144, 145, 146, 49, 154, 161, 168, 175, 182, 189, 196, 153, 160, 167, 174, 181, 188, 195, 152, 159, 166, 173, 180, 187, 194, 151, 158, 165, 172, 179, 186, 193, 150, 157, 164, 171, 178, 185, 192, 149, 156, 163, 170, 177, 184, 191, 148, 155, 162, 169, 176, 183, 190, 294, 198, 199, 200, 201, 202, 203, 287, 205, 206, 207, 208, 209, 210, 280, 212, 213, 214, 215, 216, 217, 273, 219, 220, 221, 222, 223, 224, 266, 226, 227, 228, 229, 230, 231, 259, 233, 234, 235, 236, 237, 238, 252, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 105, 253, 254, 255, 256, 257, 258, 112, 260, 261, 262, 263, 264, 265, 119, 267, 268, 269, 270, 271, 272, 126, 274, 275, 276, 277, 278, 279, 133, 281, 282, 283, 284, 285, 286, 140, 288, 289, 290, 291, 292, 293, 147,), "R2": ( 0, 1, 2, 3, 4, 5, 6, 252, 8, 9, 10, 11, 12, 13, 259, 15, 16, 17, 18, 19, 20, 266, 22, 23, 24, 25, 26, 27, 273, 29, 30, 31, 32, 33, 34, 280, 36, 37, 38, 39, 40, 41, 287, 43, 44, 45, 46, 47, 48, 294, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 239, 106, 107, 108, 109, 110, 111, 232, 113, 114, 115, 116, 117, 118, 225, 120, 121, 122, 123, 124, 125, 218, 127, 128, 129, 130, 131, 132, 211, 134, 135, 136, 137, 138, 139, 204, 141, 142, 143, 144, 145, 146, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 198, 199, 200, 201, 202, 203, 140, 205, 206, 207, 208, 209, 210, 133, 212, 213, 214, 215, 216, 217, 126, 219, 220, 221, 222, 223, 224, 119, 226, 227, 228, 229, 230, 231, 112, 233, 234, 235, 236, 237, 238, 105, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 7, 253, 254, 255, 256, 257, 258, 14, 260, 261, 262, 263, 264, 265, 21, 267, 268, 269, 270, 271, 272, 28, 274, 275, 276, 277, 278, 279, 35, 281, 282, 283, 284, 285, 286, 42, 288, 289, 290, 291, 292, 293, 49,), "Rw": ( 0, 1, 2, 3, 4, 5, 104, 105, 8, 9, 10, 11, 12, 111, 112, 15, 16, 17, 18, 19, 118, 119, 22, 23, 24, 25, 26, 125, 126, 29, 30, 31, 32, 33, 132, 133, 36, 37, 38, 39, 40, 139, 140, 43, 44, 45, 46, 47, 146, 147, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 251, 252, 106, 107, 108, 109, 110, 258, 259, 113, 114, 115, 116, 117, 265, 266, 120, 121, 122, 123, 124, 272, 273, 127, 128, 129, 130, 131, 279, 280, 134, 135, 136, 137, 138, 286, 287, 141, 142, 143, 144, 145, 293, 294, 190, 183, 176, 169, 162, 155, 148, 191, 184, 177, 170, 163, 156, 149, 192, 185, 178, 171, 164, 157, 150, 193, 186, 179, 172, 165, 158, 151, 194, 187, 180, 173, 166, 159, 152, 195, 188, 181, 174, 167, 160, 153, 196, 189, 182, 175, 168, 161, 154, 49, 48, 199, 200, 201, 202, 203, 42, 41, 206, 207, 208, 209, 210, 35, 34, 213, 214, 215, 216, 217, 28, 27, 220, 221, 222, 223, 224, 21, 20, 227, 228, 229, 230, 231, 14, 13, 234, 235, 236, 237, 238, 7, 6, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 240, 239, 253, 254, 255, 256, 257, 233, 232, 260, 261, 262, 263, 264, 226, 225, 267, 268, 269, 270, 271, 219, 218, 274, 275, 276, 277, 278, 212, 211, 281, 282, 283, 284, 285, 205, 204, 288, 289, 290, 291, 292, 198, 197,), "Rw'": ( 0, 1, 2, 3, 4, 5, 240, 239, 8, 9, 10, 11, 12, 233, 232, 15, 16, 17, 18, 19, 226, 225, 22, 23, 24, 25, 26, 219, 218, 29, 30, 31, 32, 33, 212, 211, 36, 37, 38, 39, 40, 205, 204, 43, 44, 45, 46, 47, 198, 197, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 6, 7, 106, 107, 108, 109, 110, 13, 14, 113, 114, 115, 116, 117, 20, 21, 120, 121, 122, 123, 124, 27, 28, 127, 128, 129, 130, 131, 34, 35, 134, 135, 136, 137, 138, 41, 42, 141, 142, 143, 144, 145, 48, 49, 154, 161, 168, 175, 182, 189, 196, 153, 160, 167, 174, 181, 188, 195, 152, 159, 166, 173, 180, 187, 194, 151, 158, 165, 172, 179, 186, 193, 150, 157, 164, 171, 178, 185, 192, 149, 156, 163, 170, 177, 184, 191, 148, 155, 162, 169, 176, 183, 190, 294, 293, 199, 200, 201, 202, 203, 287, 286, 206, 207, 208, 209, 210, 280, 279, 213, 214, 215, 216, 217, 273, 272, 220, 221, 222, 223, 224, 266, 265, 227, 228, 229, 230, 231, 259, 258, 234, 235, 236, 237, 238, 252, 251, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 104, 105, 253, 254, 255, 256, 257, 111, 112, 260, 261, 262, 263, 264, 118, 119, 267, 268, 269, 270, 271, 125, 126, 274, 275, 276, 277, 278, 132, 133, 281, 282, 283, 284, 285, 139, 140, 288, 289, 290, 291, 292, 146, 147,), "Rw2": ( 0, 1, 2, 3, 4, 5, 251, 252, 8, 9, 10, 11, 12, 258, 259, 15, 16, 17, 18, 19, 265, 266, 22, 23, 24, 25, 26, 272, 273, 29, 30, 31, 32, 33, 279, 280, 36, 37, 38, 39, 40, 286, 287, 43, 44, 45, 46, 47, 293, 294, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 240, 239, 106, 107, 108, 109, 110, 233, 232, 113, 114, 115, 116, 117, 226, 225, 120, 121, 122, 123, 124, 219, 218, 127, 128, 129, 130, 131, 212, 211, 134, 135, 136, 137, 138, 205, 204, 141, 142, 143, 144, 145, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 199, 200, 201, 202, 203, 140, 139, 206, 207, 208, 209, 210, 133, 132, 213, 214, 215, 216, 217, 126, 125, 220, 221, 222, 223, 224, 119, 118, 227, 228, 229, 230, 231, 112, 111, 234, 235, 236, 237, 238, 105, 104, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 6, 7, 253, 254, 255, 256, 257, 13, 14, 260, 261, 262, 263, 264, 20, 21, 267, 268, 269, 270, 271, 27, 28, 274, 275, 276, 277, 278, 34, 35, 281, 282, 283, 284, 285, 41, 42, 288, 289, 290, 291, 292, 48, 49,), "U": ( 0, 43, 36, 29, 22, 15, 8, 1, 44, 37, 30, 23, 16, 9, 2, 45, 38, 31, 24, 17, 10, 3, 46, 39, 32, 25, 18, 11, 4, 47, 40, 33, 26, 19, 12, 5, 48, 41, 34, 27, 20, 13, 6, 49, 42, 35, 28, 21, 14, 7, 99, 100, 101, 102, 103, 104, 105, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 148, 149, 150, 151, 152, 153, 154, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 197, 198, 199, 200, 201, 202, 203, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 50, 51, 52, 53, 54, 55, 56, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "U'": ( 0, 7, 14, 21, 28, 35, 42, 49, 6, 13, 20, 27, 34, 41, 48, 5, 12, 19, 26, 33, 40, 47, 4, 11, 18, 25, 32, 39, 46, 3, 10, 17, 24, 31, 38, 45, 2, 9, 16, 23, 30, 37, 44, 1, 8, 15, 22, 29, 36, 43, 197, 198, 199, 200, 201, 202, 203, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 50, 51, 52, 53, 54, 55, 56, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 99, 100, 101, 102, 103, 104, 105, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 148, 149, 150, 151, 152, 153, 154, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "U2": ( 0, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 148, 149, 150, 151, 152, 153, 154, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 197, 198, 199, 200, 201, 202, 203, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 50, 51, 52, 53, 54, 55, 56, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 99, 100, 101, 102, 103, 104, 105, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "Uw": ( 0, 43, 36, 29, 22, 15, 8, 1, 44, 37, 30, 23, 16, 9, 2, 45, 38, 31, 24, 17, 10, 3, 46, 39, 32, 25, 18, 11, 4, 47, 40, 33, 26, 19, 12, 5, 48, 41, 34, 27, 20, 13, 6, 49, 42, 35, 28, 21, 14, 7, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "Uw'": ( 0, 7, 14, 21, 28, 35, 42, 49, 6, 13, 20, 27, 34, 41, 48, 5, 12, 19, 26, 33, 40, 47, 4, 11, 18, 25, 32, 39, 46, 3, 10, 17, 24, 31, 38, 45, 2, 9, 16, 23, 30, 37, 44, 1, 8, 15, 22, 29, 36, 43, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "Uw2": ( 0, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,), "x": ( 0, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 56, 63, 70, 77, 84, 91, 98, 55, 62, 69, 76, 83, 90, 97, 54, 61, 68, 75, 82, 89, 96, 53, 60, 67, 74, 81, 88, 95, 52, 59, 66, 73, 80, 87, 94, 51, 58, 65, 72, 79, 86, 93, 50, 57, 64, 71, 78, 85, 92, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 190, 183, 176, 169, 162, 155, 148, 191, 184, 177, 170, 163, 156, 149, 192, 185, 178, 171, 164, 157, 150, 193, 186, 179, 172, 165, 158, 151, 194, 187, 180, 173, 166, 159, 152, 195, 188, 181, 174, 167, 160, 153, 196, 189, 182, 175, 168, 161, 154, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197,), "x'": ( 0, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 92, 85, 78, 71, 64, 57, 50, 93, 86, 79, 72, 65, 58, 51, 94, 87, 80, 73, 66, 59, 52, 95, 88, 81, 74, 67, 60, 53, 96, 89, 82, 75, 68, 61, 54, 97, 90, 83, 76, 69, 62, 55, 98, 91, 84, 77, 70, 63, 56, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 154, 161, 168, 175, 182, 189, 196, 153, 160, 167, 174, 181, 188, 195, 152, 159, 166, 173, 180, 187, 194, 151, 158, 165, 172, 179, 186, 193, 150, 157, 164, 171, 178, 185, 192, 149, 156, 163, 170, 177, 184, 191, 148, 155, 162, 169, 176, 183, 190, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147,), "x2": ( 0, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,), "y": ( 0, 43, 36, 29, 22, 15, 8, 1, 44, 37, 30, 23, 16, 9, 2, 45, 38, 31, 24, 17, 10, 3, 46, 39, 32, 25, 18, 11, 4, 47, 40, 33, 26, 19, 12, 5, 48, 41, 34, 27, 20, 13, 6, 49, 42, 35, 28, 21, 14, 7, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 252, 259, 266, 273, 280, 287, 294, 251, 258, 265, 272, 279, 286, 293, 250, 257, 264, 271, 278, 285, 292, 249, 256, 263, 270, 277, 284, 291, 248, 255, 262, 269, 276, 283, 290, 247, 254, 261, 268, 275, 282, 289, 246, 253, 260, 267, 274, 281, 288,), "y'": ( 0, 7, 14, 21, 28, 35, 42, 49, 6, 13, 20, 27, 34, 41, 48, 5, 12, 19, 26, 33, 40, 47, 4, 11, 18, 25, 32, 39, 46, 3, 10, 17, 24, 31, 38, 45, 2, 9, 16, 23, 30, 37, 44, 1, 8, 15, 22, 29, 36, 43, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 288, 281, 274, 267, 260, 253, 246, 289, 282, 275, 268, 261, 254, 247, 290, 283, 276, 269, 262, 255, 248, 291, 284, 277, 270, 263, 256, 249, 292, 285, 278, 271, 264, 257, 250, 293, 286, 279, 272, 265, 258, 251, 294, 287, 280, 273, 266, 259, 252,), "y2": ( 0, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246,), "z": ( 0, 92, 85, 78, 71, 64, 57, 50, 93, 86, 79, 72, 65, 58, 51, 94, 87, 80, 73, 66, 59, 52, 95, 88, 81, 74, 67, 60, 53, 96, 89, 82, 75, 68, 61, 54, 97, 90, 83, 76, 69, 62, 55, 98, 91, 84, 77, 70, 63, 56, 288, 281, 274, 267, 260, 253, 246, 289, 282, 275, 268, 261, 254, 247, 290, 283, 276, 269, 262, 255, 248, 291, 284, 277, 270, 263, 256, 249, 292, 285, 278, 271, 264, 257, 250, 293, 286, 279, 272, 265, 258, 251, 294, 287, 280, 273, 266, 259, 252, 141, 134, 127, 120, 113, 106, 99, 142, 135, 128, 121, 114, 107, 100, 143, 136, 129, 122, 115, 108, 101, 144, 137, 130, 123, 116, 109, 102, 145, 138, 131, 124, 117, 110, 103, 146, 139, 132, 125, 118, 111, 104, 147, 140, 133, 126, 119, 112, 105, 43, 36, 29, 22, 15, 8, 1, 44, 37, 30, 23, 16, 9, 2, 45, 38, 31, 24, 17, 10, 3, 46, 39, 32, 25, 18, 11, 4, 47, 40, 33, 26, 19, 12, 5, 48, 41, 34, 27, 20, 13, 6, 49, 42, 35, 28, 21, 14, 7, 203, 210, 217, 224, 231, 238, 245, 202, 209, 216, 223, 230, 237, 244, 201, 208, 215, 222, 229, 236, 243, 200, 207, 214, 221, 228, 235, 242, 199, 206, 213, 220, 227, 234, 241, 198, 205, 212, 219, 226, 233, 240, 197, 204, 211, 218, 225, 232, 239, 190, 183, 176, 169, 162, 155, 148, 191, 184, 177, 170, 163, 156, 149, 192, 185, 178, 171, 164, 157, 150, 193, 186, 179, 172, 165, 158, 151, 194, 187, 180, 173, 166, 159, 152, 195, 188, 181, 174, 167, 160, 153, 196, 189, 182, 175, 168, 161, 154,), "z'": ( 0, 154, 161, 168, 175, 182, 189, 196, 153, 160, 167, 174, 181, 188, 195, 152, 159, 166, 173, 180, 187, 194, 151, 158, 165, 172, 179, 186, 193, 150, 157, 164, 171, 178, 185, 192, 149, 156, 163, 170, 177, 184, 191, 148, 155, 162, 169, 176, 183, 190, 7, 14, 21, 28, 35, 42, 49, 6, 13, 20, 27, 34, 41, 48, 5, 12, 19, 26, 33, 40, 47, 4, 11, 18, 25, 32, 39, 46, 3, 10, 17, 24, 31, 38, 45, 2, 9, 16, 23, 30, 37, 44, 1, 8, 15, 22, 29, 36, 43, 105, 112, 119, 126, 133, 140, 147, 104, 111, 118, 125, 132, 139, 146, 103, 110, 117, 124, 131, 138, 145, 102, 109, 116, 123, 130, 137, 144, 101, 108, 115, 122, 129, 136, 143, 100, 107, 114, 121, 128, 135, 142, 99, 106, 113, 120, 127, 134, 141, 252, 259, 266, 273, 280, 287, 294, 251, 258, 265, 272, 279, 286, 293, 250, 257, 264, 271, 278, 285, 292, 249, 256, 263, 270, 277, 284, 291, 248, 255, 262, 269, 276, 283, 290, 247, 254, 261, 268, 275, 282, 289, 246, 253, 260, 267, 274, 281, 288, 239, 232, 225, 218, 211, 204, 197, 240, 233, 226, 219, 212, 205, 198, 241, 234, 227, 220, 213, 206, 199, 242, 235, 228, 221, 214, 207, 200, 243, 236, 229, 222, 215, 208, 201, 244, 237, 230, 223, 216, 209, 202, 245, 238, 231, 224, 217, 210, 203, 56, 63, 70, 77, 84, 91, 98, 55, 62, 69, 76, 83, 90, 97, 54, 61, 68, 75, 82, 89, 96, 53, 60, 67, 74, 81, 88, 95, 52, 59, 66, 73, 80, 87, 94, 51, 58, 65, 72, 79, 86, 93, 50, 57, 64, 71, 78, 85, 92,), "z2": ( 0, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 218, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,), }


def rotate_777(cube, step):
    return [cube[x] for x in swaps_777[step]]
