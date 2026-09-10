"""
Even NxNxN solver (8x8x8 and up): turn the cube into an odd cube, then reuse
the odd NxNxN solver.

``RubiksCubeNNNEven`` inherits ``RubiksCubeNNNEvenEdges`` and is a sibling of
``RubiksCube666``. Plus-sign staging maps each center orbit onto a fake 6x6x6
and reuses the ranked 6x6x6 center-staging phases.

``reduce_555``:
    1. ``make_plus_sign`` maps each inner center orbit onto a fake 6x6x6 and
       runs its ranked center staging, then daisy-solves it. That pairs the
       middle two rows and columns of every face, leaving a plus sign of
       already-reduced stickers.
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
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_666
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

            # Stage this orbit with the ranked 6x6x6 phases 1-3, then reduce
            # its centers to a 5x5x5.
            fake_666.stage_centers()

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
