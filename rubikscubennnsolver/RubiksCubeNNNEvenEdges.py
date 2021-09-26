# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555

logger = logging.getLogger(__name__)


class RubiksCubeNNNEvenEdges(RubiksCube):
    def lt_init(self):
        pass

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

    def pair_inside_edges_via_444(self):
        original_solution_len = len(self.solution)
        fake_444 = self.get_fake_444()

        # Fill in the corners so that we can avoid PLL parity when pairing the edges
        start_444 = 0
        start_nnn = 0

        for x in range(6):
            fake_444.state[start_444 + 1] = self.state[start_nnn + 1]
            fake_444.state[start_444 + 4] = self.state[start_nnn + self.size]
            fake_444.state[start_444 + 13] = self.state[start_nnn + (self.size * self.size) - self.size + 1]
            fake_444.state[start_444 + 16] = self.state[start_nnn + (self.size * self.size)]
            start_nnn += self.size * self.size
            start_444 += 16

        # Fill in the edges
        start_444 = 0
        start_nnn = 0
        half_size = int(self.size / 2)

        for x in range(6):

            fake_444.state[start_444 + 2] = self.state[start_nnn + half_size]
            fake_444.state[start_444 + 3] = self.state[start_nnn + half_size + 1]
            fake_444.state[start_444 + 5] = self.state[start_nnn + (self.size * (half_size - 1)) + 1]
            fake_444.state[start_444 + 8] = self.state[start_nnn + (self.size * half_size)]
            fake_444.state[start_444 + 9] = self.state[start_nnn + (self.size * half_size) + 1]
            fake_444.state[start_444 + 12] = self.state[start_nnn + (self.size * (half_size + 1))]
            fake_444.state[start_444 + 14] = self.state[start_nnn + (self.size * self.size) - half_size]
            fake_444.state[start_444 + 15] = self.state[start_nnn + (self.size * self.size) - half_size + 1]
            start_nnn += self.size * self.size
            start_444 += 16

        fake_444.sanity_check()
        fake_444.reduce_333(consider_solve_333=False)
        half_size_str = str(half_size)

        for step in fake_444.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                # Rotate the entire cube
                # fmt: off
                if step.startswith("4"):
                    step = str(self.size) + step[1:]

                elif step in (
                    "Uw", "Uw'", "Uw2",
                    "Lw", "Lw'", "Lw2",
                    "Fw", "Fw'", "Fw2",
                    "Rw", "Rw'", "Rw2",
                    "Bw", "Bw'", "Bw2",
                    "Dw", "Dw'", "Dw2",
                ):
                    step = half_size_str + step
                # fmt: on

                self.rotate(step)

        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if len(self.solution) > original_solution_len:
            self.print_cube(
                "%s: inside edges are paired (%d steps in)" % (self, self.get_solution_len_minus_rotates(self.solution))
            )

    def pair_edge_orbit_via_555(self, orbit):
        logger.info("%s: pair_edge_orbit_via_555 for %d" % (self, orbit))
        fake_555 = self.get_fake_555()
        half_size = int(self.size / 2)
        max_orbit = int((self.size - 2) / 2) - 1

        start_555 = 0
        start_nnn = 0

        for x in range(6):
            # corners
            fake_555.state[start_555 + 1] = self.state[start_nnn + 1]
            fake_555.state[start_555 + 5] = self.state[start_nnn + self.size]
            fake_555.state[start_555 + 21] = self.state[start_nnn + (self.size * self.size) - self.size + 1]
            fake_555.state[start_555 + 25] = self.state[start_nnn + (self.size * self.size)]

            # centers
            row1_col2 = start_nnn + half_size + self.size
            row1_col1 = row1_col2 - (max_orbit - orbit)
            row1_col3 = row1_col2 + (max_orbit - orbit) + 1

            row2_col1 = start_nnn + int((self.size * self.size) / 2) + 2
            row2_col2 = row2_col1 + half_size - 1
            row2_col3 = row2_col1 + self.size - 3

            row3_col2 = start_nnn + (self.size * self.size) - half_size - self.size
            row3_col1 = row3_col2 - (max_orbit - orbit)
            row3_col3 = row3_col2 + (max_orbit - orbit) + 1

            # logger.info("row1_col1 %d, row1_col2 %d, row1_col3 %d" % (row1_col1, row1_col2, row1_col3))
            # logger.info("row2_col1 %d, row2_col2 %d, row2_col3 %d" % (row2_col1, row2_col2, row2_col3))
            # logger.info("row3_col1 %d, row3_col2 %d, row3_col3 %d" % (row3_col1, row3_col2, row3_col3))

            fake_555.state[start_555 + 7] = self.state[row1_col1]
            fake_555.state[start_555 + 8] = self.state[row1_col2]
            fake_555.state[start_555 + 9] = self.state[row1_col3]

            fake_555.state[start_555 + 12] = self.state[row2_col1]
            fake_555.state[start_555 + 13] = self.state[row2_col2]
            fake_555.state[start_555 + 14] = self.state[row2_col3]

            fake_555.state[start_555 + 17] = self.state[row3_col1]
            fake_555.state[start_555 + 18] = self.state[row3_col2]
            fake_555.state[start_555 + 19] = self.state[row3_col3]

            # edges
            row1_col2 = start_nnn + half_size
            row1_col1 = row1_col2 - (max_orbit - orbit)
            row1_col3 = row1_col2 + (max_orbit - orbit) + 1

            row2_col1 = start_nnn + ((orbit + 1) * self.size) + 1
            row2_col3 = row2_col1 + self.size - 1

            row3_col1 = start_nnn + (self.size * (half_size - 1)) + 1
            row3_col3 = row3_col1 + self.size - 1

            row4_col1 = start_nnn + (self.size * self.size) - ((orbit + 2) * self.size) + 1
            row4_col3 = row4_col1 + self.size - 1

            row5_col1 = row1_col1 + ((self.size - 1) * self.size)
            row5_col2 = row1_col2 + ((self.size - 1) * self.size)
            row5_col3 = row1_col3 + ((self.size - 1) * self.size)

            # logger.info("%d row1: %s, %s, %s" % (x, row1_col1, row1_col2, row1_col3))
            # logger.info("%d row2: %s, %s" % (x, row2_col1, row2_col3))
            # logger.info("%d row3: %s, %s" % (x, row3_col1, row3_col3))
            # logger.info("%d row4: %s, %s" % (x, row4_col1, row4_col3))
            # logger.info("%d row5: %s, %s, %s" % (x, row5_col1, row5_col2, row5_col3))

            # row1
            fake_555.state[start_555 + 2] = self.state[row1_col1]
            fake_555.state[start_555 + 3] = self.state[row1_col2]
            fake_555.state[start_555 + 4] = self.state[row1_col3]

            # row2
            fake_555.state[start_555 + 6] = self.state[row2_col1]
            fake_555.state[start_555 + 10] = self.state[row2_col3]

            # row3 - The middle of the edge so orbit doesn't matter
            fake_555.state[start_555 + 11] = self.state[row3_col1]
            fake_555.state[start_555 + 15] = self.state[row3_col3]

            # row4
            fake_555.state[start_555 + 16] = self.state[row4_col1]
            fake_555.state[start_555 + 20] = self.state[row4_col3]

            # row5
            fake_555.state[start_555 + 22] = self.state[row5_col1]
            fake_555.state[start_555 + 23] = self.state[row5_col2]
            fake_555.state[start_555 + 24] = self.state[row5_col3]

            start_nnn += self.size * self.size
            start_555 += 25

        fake_555.sanity_check()
        fake_555.enable_print_cube = True
        fake_555.reduce_333()

        wide_str = str(orbit + 2)
        for step in fake_555.solution:

            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                # Rotate the entire cube
                # fmt: off
                if step.startswith("5"):
                    step = str(self.size) + step[1:]

                elif step in (
                    "Uw", "Uw'", "Uw2",
                    "Lw", "Lw'", "Lw2",
                    "Fw", "Fw'", "Fw2",
                    "Rw", "Rw'", "Rw2",
                    "Bw", "Bw'", "Bw2",
                    "Dw", "Dw'", "Dw2",
                ):
                    step = wide_str + step

                elif step in (
                    "2U", "2U'", "2U2",
                    "2L", "2L'", "2L2",
                    "2F", "2F'", "2F2",
                    "2R", "2R'", "2R2",
                    "2B", "2B'", "2B2",
                    "2D", "2D'", "2D2",
                ):
                    step = wide_str + step[1:]
                # fmt: on

                self.rotate(step)

    def group_edges(self):
        # For 6x6x6 the inside edges are already paired at the end of reduce_555
        # For 8x8x8 and larger the inside edges were paired right after make_plus_sign

        # How many orbits of edges does this cube have?
        max_orbit = int((self.size / 2) - 1)

        # The inside orbit was paired above via pair_inside_edges_via_444()
        # For all of the rest work your way from inside to outside and pair
        # them via the 5x5x5 solver.
        for orbit in reversed(list(range(0, max_orbit - 1))):
            self.pair_edge_orbit_via_555(orbit)

        self.print_cube(
            "%s: edges are paired (%d steps in)" % (self, self.get_solution_len_minus_rotates(self.solution))
        )
