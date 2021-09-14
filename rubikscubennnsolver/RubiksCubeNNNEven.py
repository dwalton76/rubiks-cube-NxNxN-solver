# standard libraries
import gc
import logging
from math import ceil

# rubiks cube libraries
from rubikscubennnsolver.misc import SolveError
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_666
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_777
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges

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


class RubiksCubeNNNEven(RubiksCubeNNNEvenEdges):
    """
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

    def get_fake_777(self):
        if self.fake_777 is None:
            self.fake_777 = RubiksCube777(solved_777, "URFDLB")
            self.fake_777.lt_init()
            self.fake_777.enable_print_cube = False
        else:
            self.fake_777.re_init()

        if self.fake_555:
            self.fake_777.fake_555 = self.fake_555

        return self.fake_777

    def make_plus_sign(self):
        """
        Pair the middle two columns/rows in order to convert this Even cube into
        an Odd cube...this allows us to use the 7x7x7 solver later.  It makes what
        looks like a large "plus" sign on each cube face thus the name of this
        method.
        """
        center_orbit_count = int((self.size - 4) / 2)
        side_name = {0: "U", 1: "L", 2: "F", 3: "R", 4: "B", 5: "D"}

        # Make a big "plus" sign on each side, this will allow us to reduce the
        # centers to a series of 7x7x7 centers
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

            # Group LR centers (in turn groups FB)
            fake_666.group_centers_guts()

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
        gc.collect()
        self.print_cube(
            "%s: Big plus sign formed, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )

    def stage_or_solve_inside_777(self, center_orbit_id, max_center_orbits, width, cycle, max_cycle, action):
        fake_777 = self.get_fake_777()

        for index in range(1, 295):
            fake_777.state[index] = "x"

        start_777 = 0
        start_NNN = 0
        row0_midpoint = ceil(self.size / 2)

        logger.info(
            "%s: Start center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s"
            % (self, center_orbit_id, max_center_orbits, width, cycle, max_cycle)
        )

        side_name = {0: "U", 1: "L", 2: "F", 3: "R", 4: "B", 5: "D"}

        for x in range(6):

            # centers
            mid_NNN_row1 = start_NNN + row0_midpoint + (self.size * (max_center_orbits - center_orbit_id + 1))
            start_NNN_row1 = mid_NNN_row1 - (2 + cycle)
            end_NNN_row1 = mid_NNN_row1 + (2 + cycle) + 1

            start_NNN_row5 = start_NNN_row1 + ((width - 1) * self.size)
            mid_NNN_row5 = mid_NNN_row1 + ((width - 1) * self.size)
            end_NNN_row5 = end_NNN_row1 + ((width - 1) * self.size)

            mid_NNN_row3 = int(mid_NNN_row1 + ((width / 2) * self.size) - self.size)
            start_NNN_row3 = mid_NNN_row3 - (2 + center_orbit_id)
            end_NNN_row3 = mid_NNN_row3 + (2 + center_orbit_id) + 1

            start_NNN_row2 = start_NNN_row3 - (self.size * (cycle + 1))
            start_NNN_row4 = start_NNN_row3 + (self.size * (cycle + 1)) + self.size

            end_NNN_row2 = end_NNN_row3 - (self.size * (cycle + 1))
            end_NNN_row4 = end_NNN_row3 + (self.size * (cycle + 1)) + self.size

            mid_NNN_row2 = int((start_NNN_row2 + end_NNN_row2) / 2)
            mid_NNN_row4 = int((start_NNN_row4 + end_NNN_row4) / 2)

            row1_col1 = start_NNN_row1
            row1_col2 = start_NNN_row1 + 1
            row1_col3 = mid_NNN_row1
            row1_col4 = end_NNN_row1 - 1
            row1_col5 = end_NNN_row1

            row2_col1 = start_NNN_row2
            row2_col2 = start_NNN_row2 + 1
            row2_col3 = mid_NNN_row2
            row2_col4 = end_NNN_row2 - 1
            row2_col5 = end_NNN_row2

            row3_col1 = start_NNN_row3
            row3_col2 = start_NNN_row3 + 1
            row3_col3 = mid_NNN_row3
            row3_col4 = end_NNN_row3 - 1
            row3_col5 = end_NNN_row3

            row4_col1 = start_NNN_row4
            row4_col2 = start_NNN_row4 + 1
            row4_col3 = mid_NNN_row4
            row4_col4 = end_NNN_row4 - 1
            row4_col5 = end_NNN_row4

            row5_col1 = start_NNN_row5
            row5_col2 = start_NNN_row5 + 1
            row5_col3 = mid_NNN_row5
            row5_col4 = end_NNN_row5 - 1
            row5_col5 = end_NNN_row5

            # logger.info("%d: start_NNN_row1 %d, mid_NNN_row1 %d, end_NNN_row1 %d" % (x, start_NNN_row1, mid_NNN_row1, end_NNN_row1))
            # logger.info("%d: start_NNN_row2 %d, mid_NNN_row2 %d, end_NNN_row2 %d" % (x, start_NNN_row2, mid_NNN_row2, end_NNN_row2))
            # logger.info("%d: start_NNN_row3 %d, mid_NNN_row3 %d, end_NNN_row3 %d" % (x, start_NNN_row3, mid_NNN_row3, end_NNN_row3))
            # logger.info("%d: start_NNN_row4 %d, mid_NNN_row4 %d, end_NNN_row4 %d" % (x, start_NNN_row4, mid_NNN_row4, end_NNN_row4))
            # logger.info("%d: start_NNN_row5 %d, mid_NNN_row5 %d, end_NNN_row5 %d" % (x, start_NNN_row5, mid_NNN_row5, end_NNN_row5))

            # logger.info("%d: row1 %d, %d, %d, %d, %d" % (x, row1_col1, row1_col2, row1_col3, row1_col4, row1_col5))
            # logger.info("%d: row2 %d, %d, %d, %d, %d" % (x, row2_col1, row2_col2, row2_col3, row2_col4, row2_col5))
            # logger.info("%d: row3 %d, %d, %d, %d, %d" % (x, row3_col1, row3_col2, row3_col3, row3_col4, row3_col5))
            # logger.info("%d: row4 %d, %d, %d, %d, %d" % (x, row4_col1, row4_col2, row4_col3, row4_col4, row4_col5))
            # logger.info("%d: row5 %d, %d, %d, %d, %d" % (x, row5_col1, row5_col2, row5_col3, row5_col4, row5_col5))

            if (center_orbit_id == 0 and cycle == 0) or (center_orbit_id == max_center_orbits and cycle == max_cycle):
                fake_777.state[start_777 + 9] = self.state[row1_col1]
                fake_777.state[start_777 + 10] = self.state[row1_col2]
                fake_777.state[start_777 + 11] = self.state[row1_col3]
                fake_777.state[start_777 + 12] = self.state[row1_col4]
                fake_777.state[start_777 + 13] = self.state[row1_col5]

                fake_777.state[start_777 + 16] = self.state[row2_col1]
                fake_777.state[start_777 + 17] = self.state[row2_col2]
                fake_777.state[start_777 + 18] = self.state[row2_col3]
                fake_777.state[start_777 + 19] = self.state[row2_col4]
                fake_777.state[start_777 + 20] = self.state[row2_col5]

                fake_777.state[start_777 + 23] = self.state[row3_col1]
                fake_777.state[start_777 + 24] = self.state[row3_col2]
                fake_777.state[start_777 + 25] = self.state[row3_col3]
                fake_777.state[start_777 + 26] = self.state[row3_col4]
                fake_777.state[start_777 + 27] = self.state[row3_col5]

                fake_777.state[start_777 + 30] = self.state[row4_col1]
                fake_777.state[start_777 + 31] = self.state[row4_col2]
                fake_777.state[start_777 + 32] = self.state[row4_col3]
                fake_777.state[start_777 + 33] = self.state[row4_col4]
                fake_777.state[start_777 + 34] = self.state[row4_col5]

                fake_777.state[start_777 + 37] = self.state[row5_col1]
                fake_777.state[start_777 + 38] = self.state[row5_col2]
                fake_777.state[start_777 + 39] = self.state[row5_col3]
                fake_777.state[start_777 + 40] = self.state[row5_col4]
                fake_777.state[start_777 + 41] = self.state[row5_col5]

            else:
                fake_777.state[start_777 + 9] = side_name[x]
                fake_777.state[start_777 + 10] = self.state[row1_col2]
                fake_777.state[start_777 + 11] = self.state[row1_col3]
                fake_777.state[start_777 + 12] = self.state[row1_col4]
                fake_777.state[start_777 + 13] = side_name[x]

                fake_777.state[start_777 + 16] = self.state[row2_col1]
                fake_777.state[start_777 + 17] = self.state[row2_col2]
                fake_777.state[start_777 + 18] = self.state[row2_col3]
                fake_777.state[start_777 + 19] = self.state[row2_col4]
                fake_777.state[start_777 + 20] = self.state[row2_col5]

                fake_777.state[start_777 + 23] = self.state[row3_col1]
                fake_777.state[start_777 + 24] = self.state[row3_col2]
                fake_777.state[start_777 + 25] = self.state[row3_col3]
                fake_777.state[start_777 + 26] = self.state[row3_col4]
                fake_777.state[start_777 + 27] = self.state[row3_col5]

                fake_777.state[start_777 + 30] = self.state[row4_col1]
                fake_777.state[start_777 + 31] = self.state[row4_col2]
                fake_777.state[start_777 + 32] = self.state[row4_col3]
                fake_777.state[start_777 + 33] = self.state[row4_col4]
                fake_777.state[start_777 + 34] = self.state[row4_col5]

                fake_777.state[start_777 + 37] = side_name[x]
                fake_777.state[start_777 + 38] = self.state[row5_col2]
                fake_777.state[start_777 + 39] = self.state[row5_col3]
                fake_777.state[start_777 + 40] = self.state[row5_col4]
                fake_777.state[start_777 + 41] = side_name[x]

            if x == 0:
                side = self.sideU
            elif x == 1:
                side = self.sideL
            elif x == 2:
                side = self.sideF
            elif x == 3:
                side = self.sideR
            elif x == 4:
                side = self.sideB
            elif x == 5:
                side = self.sideD

            # edges
            # top edge
            offset = self.size
            while row1_col1 - offset not in side.edge_north_pos:
                offset += self.size
            edge02 = row1_col1 - offset

            offset = self.size
            while row1_col2 - offset not in side.edge_north_pos:
                offset += self.size
            edge03 = row1_col2 - offset

            offset = self.size
            while row1_col3 - offset not in side.edge_north_pos:
                offset += self.size
            edge04 = row1_col3 - offset

            offset = self.size
            while row1_col4 - offset not in side.edge_north_pos:
                offset += self.size
            edge05 = row1_col4 - offset

            offset = self.size
            while row1_col5 - offset not in side.edge_north_pos:
                offset += self.size
            edge06 = row1_col5 - offset

            fake_777.state[start_777 + 2] = self.state[edge02]
            fake_777.state[start_777 + 3] = self.state[edge03]
            fake_777.state[start_777 + 4] = self.state[edge04]
            fake_777.state[start_777 + 5] = self.state[edge05]
            fake_777.state[start_777 + 6] = self.state[edge06]

            # left edge
            offset = 1
            while row1_col1 - offset not in side.edge_west_pos:
                offset += 1
            edge08 = row1_col1 - offset

            offset = 1
            while row2_col1 - offset not in side.edge_west_pos:
                offset += 1
            edge15 = row2_col1 - offset

            offset = 1
            while row3_col1 - offset not in side.edge_west_pos:
                offset += 1
            edge22 = row3_col1 - offset

            offset = 1
            while row4_col1 - offset not in side.edge_west_pos:
                offset += 1
            edge29 = row4_col1 - offset

            offset = 1
            while row5_col1 - offset not in side.edge_west_pos:
                offset += 1
            edge36 = row5_col1 - offset

            fake_777.state[start_777 + 8] = self.state[edge08]
            fake_777.state[start_777 + 15] = self.state[edge15]
            fake_777.state[start_777 + 22] = self.state[edge22]
            fake_777.state[start_777 + 29] = self.state[edge29]
            fake_777.state[start_777 + 36] = self.state[edge36]

            # right edge
            offset = 1
            while row1_col5 + offset not in side.edge_east_pos:
                offset += 1
            edge14 = row1_col5 + offset

            offset = 1
            while row2_col5 + offset not in side.edge_east_pos:
                offset += 1
            edge21 = row2_col5 + offset

            offset = 1
            while row3_col5 + offset not in side.edge_east_pos:
                offset += 1
            edge28 = row3_col5 + offset

            offset = 1
            while row4_col5 + offset not in side.edge_east_pos:
                offset += 1
            edge35 = row4_col5 + offset

            offset = 1
            while row5_col5 + offset not in side.edge_east_pos:
                offset += 1
            edge42 = row5_col5 + offset

            fake_777.state[start_777 + 14] = self.state[edge14]
            fake_777.state[start_777 + 21] = self.state[edge21]
            fake_777.state[start_777 + 28] = self.state[edge28]
            fake_777.state[start_777 + 35] = self.state[edge35]
            fake_777.state[start_777 + 42] = self.state[edge42]
            # logger.info(f"edge14 {edge14}, edge21 {edge21}, edge28 {edge28}, edge35 {edge35}, edge42 {edge42}, offset {offset}\n\n")

            # bottom edge
            offset = self.size
            while row5_col1 + offset not in side.edge_south_pos:
                offset += self.size
            edge44 = row5_col1 + offset

            offset = self.size
            while row5_col2 + offset not in side.edge_south_pos:
                offset += self.size
            edge45 = row5_col2 + offset

            offset = self.size
            while row5_col3 + offset not in side.edge_south_pos:
                offset += self.size
            edge46 = row5_col3 + offset

            offset = self.size
            while row5_col4 + offset not in side.edge_south_pos:
                offset += self.size
            edge47 = row5_col4 + offset

            offset = self.size
            while row5_col5 + offset not in side.edge_south_pos:
                offset += self.size
            edge48 = row5_col5 + offset

            fake_777.state[start_777 + 44] = self.state[edge44]
            fake_777.state[start_777 + 45] = self.state[edge45]
            fake_777.state[start_777 + 46] = self.state[edge46]
            fake_777.state[start_777 + 47] = self.state[edge47]
            fake_777.state[start_777 + 48] = self.state[edge48]

            # corners
            corner01 = start_NNN + 1
            corner07 = corner01 + self.size - 1
            corner43 = start_NNN + (self.size * self.size)
            corner49 = corner43 - self.size + 1
            fake_777.state[start_777 + 1] = self.state[corner01]
            fake_777.state[start_777 + 7] = self.state[corner07]
            fake_777.state[start_777 + 43] = self.state[corner43]
            fake_777.state[start_777 + 49] = self.state[corner49]

            start_777 += 49
            start_NNN += self.size * self.size

        """
        # fake_777.sanity_check()
        self.print_cube_layout()
        self.print_cube("HERE 00")
        logger.info(f"center_orbit_id {center_orbit_id}, max_center_orbits {max_center_orbits}, width {width}, cycle {cycle}, max_cycle {max_cycle}, action {action}")
        fake_777.enable_print_cube = True
        fake_777.print_cube_layout()
        fake_777.print_cube("HERE 10")
        raise Exception("DONE")
        """

        # Apply the 7x7x7 solution to our cube
        half_size = str(ceil(self.size / 2) - 1 - cycle)
        wide_size = str(ceil(self.size / 2) - 2 - center_orbit_id)

        if action == "stage_UD_centers":
            fake_777.create_fake_555_from_inside_centers()
            fake_777.stage_UD_centers()

        elif action == "stage_LR_centers":
            fake_777.stage_LR_centers()

        elif action == "solve_t_centers":
            fake_777.solve_t_centers()

        elif action == "solve_centers":
            fake_777.solve_centers()

        else:
            raise Exception(f"Invalid action {action}")

        for step in fake_777.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            elif step.startswith("3"):
                self.rotate(half_size + step[1:])
            elif "w" in step:
                self.rotate(wide_size + step)
            else:
                self.rotate(step)

        self.print_cube(
            "%s: End center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s"
            % (self, center_orbit_id, max_center_orbits, width, cycle, max_cycle)
        )

    def group_centers_guts(self):
        self.make_plus_sign()
        self.pair_inside_edges_via_444()

        max_center_orbits = int((self.size - 3) / 2) - 2

        # Stage all LR centers
        for center_orbit_id in range(max_center_orbits + 1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5) / 2)

            for cycle in range(max_cycle + 1):
                self.stage_or_solve_inside_777(
                    center_orbit_id, max_center_orbits, width, cycle, max_cycle, "stage_LR_centers"
                )

        self.print_cube(
            "%s: LR centers are staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )

        # Stage all UD centers
        for center_orbit_id in range(max_center_orbits + 1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5) / 2)

            for cycle in range(max_cycle + 1):
                self.stage_or_solve_inside_777(
                    center_orbit_id, max_center_orbits, width, cycle, max_cycle, "stage_UD_centers"
                )

        self.print_cube(
            "%s: UD centers are staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )

        # Solve all t-centers
        for center_orbit_id in range(max_center_orbits + 1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5) / 2)

            for cycle in range(max_cycle + 1):
                self.stage_or_solve_inside_777(
                    center_orbit_id, max_center_orbits, width, cycle, max_cycle, "solve_t_centers"
                )

        # Solve all centers
        center_orbit_id = max_center_orbits
        width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
        max_cycle = int((width - 5) / 2)

        for cycle in range(max_cycle + 1):
            self.stage_or_solve_inside_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle, "solve_centers")

        self.rotate_U_to_U()
        self.rotate_F_to_F()
        self.print_cube(
            "%s: centers are solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution))
        )

        if not self.centers_solved():
            raise SolveError("centers should be solved")
