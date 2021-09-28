# standard libraries
import logging
from math import ceil

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_777
from rubikscubennnsolver.RubiksCubeNNNOddEdges import RubiksCubeNNNOddEdges

logger = logging.getLogger(__name__)

solved_999 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

solved_111111 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

solved_131313 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

solved_151515 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

solved_171717 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"


class RubiksCubeNNNOdd(RubiksCubeNNNOddEdges):
    """
    Inheritance model
    -----------------

            RubiksCube
                |
        RubiksCubeNNNOddEdges
           /            \
    RubiksCubeNNNOdd RubiksCube777
    """

    def get_fake_777(self):
        if self.fake_777 is None:
            self.fake_777 = RubiksCube777(solved_777, "URFDLB")
            self.fake_777.lt_init()
            self.fake_777.enable_print_cube = False
        else:
            self.fake_777.re_init()
        return self.fake_777

    def populate_fake_777(self, center_orbit_id, max_center_orbits, width, cycle, max_cycle):
        fake_777 = self.get_fake_777()

        for index in range(1, 295):
            fake_777.state[index] = "x"

        start_777 = 0
        start_NNN = 0
        row0_midpoint = ceil(self.size / 2)
        row6_midpoint = (self.size * self.size) - row0_midpoint + 1

        logger.info(
            "%s: start orbit, %d/%d, cycle %d/%d, width %d"
            % (self, center_orbit_id, max_center_orbits, cycle, max_cycle, width)
        )
        side_name = {0: "U", 1: "L", 2: "F", 3: "R", 4: "B", 5: "D"}

        for x in range(6):
            # centers
            mid_NNN_row1 = start_NNN + row0_midpoint + (self.size * (max_center_orbits - center_orbit_id + 1))
            start_NNN_row1 = mid_NNN_row1 - (2 + cycle)
            end_NNN_row1 = mid_NNN_row1 + (2 + cycle)

            start_NNN_row5 = start_NNN_row1 + ((width - 1) * self.size)
            mid_NNN_row5 = mid_NNN_row1 + ((width - 1) * self.size)
            end_NNN_row5 = end_NNN_row1 + ((width - 1) * self.size)

            mid_NNN_row3 = int((mid_NNN_row1 + mid_NNN_row5) / 2)
            start_NNN_row3 = mid_NNN_row3 - (2 + center_orbit_id)
            end_NNN_row3 = mid_NNN_row3 + (2 + center_orbit_id)

            start_NNN_row2 = start_NNN_row3 - (self.size * (cycle + 1))
            start_NNN_row4 = start_NNN_row3 + (self.size * (cycle + 1))

            end_NNN_row2 = end_NNN_row3 - (self.size * (cycle + 1))
            end_NNN_row4 = end_NNN_row3 + (self.size * (cycle + 1))

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
            # logger.info("%d: row5 %d, %d, %d, %d, %d\n\n" % (x, row5_col1, row5_col2, row5_col3, row5_col4, row5_col5))

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
                # fake_777.state[start_777+9] = self.state[row1_col1]
                fake_777.state[start_777 + 9] = side_name[x]
                fake_777.state[start_777 + 10] = self.state[row1_col2]
                fake_777.state[start_777 + 11] = self.state[row1_col3]
                fake_777.state[start_777 + 12] = self.state[row1_col4]
                # fake_777.state[start_777+13] = self.state[row1_col5]
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

                # fake_777.state[start_777+37] = self.state[row5_col1]
                fake_777.state[start_777 + 37] = side_name[x]
                fake_777.state[start_777 + 38] = self.state[row5_col2]
                fake_777.state[start_777 + 39] = self.state[row5_col3]
                fake_777.state[start_777 + 40] = self.state[row5_col4]
                # fake_777.state[start_777+41] = self.state[row5_col5]
                fake_777.state[start_777 + 41] = side_name[x]

            # edges
            edge_row0_col1 = start_NNN + (row0_midpoint - (2 + cycle))
            edge_row0_col2 = start_NNN + (row0_midpoint - (1 + cycle))
            edge_row0_col3 = start_NNN + (row0_midpoint)
            edge_row0_col4 = start_NNN + (row0_midpoint + (1 + cycle))
            edge_row0_col5 = start_NNN + (row0_midpoint + (2 + cycle))

            edge_row3_col1 = start_NNN + (((row0_midpoint - 1) * self.size) + 1)
            edge_row1_col1 = edge_row3_col1 - ((2 + cycle) * self.size)
            edge_row2_col1 = edge_row3_col1 - ((1 + cycle) * self.size)
            edge_row4_col1 = edge_row3_col1 + ((1 + cycle) * self.size)
            edge_row5_col1 = edge_row3_col1 + ((2 + cycle) * self.size)

            edge_row1_col2 = edge_row1_col1 + self.size - 1
            edge_row2_col2 = edge_row2_col1 + self.size - 1
            edge_row3_col2 = edge_row3_col1 + self.size - 1
            edge_row4_col2 = edge_row4_col1 + self.size - 1
            edge_row5_col2 = edge_row5_col1 + self.size - 1

            edge_row6_col1 = start_NNN + (row6_midpoint - (2 + cycle))
            edge_row6_col2 = start_NNN + (row6_midpoint - (1 + cycle))
            edge_row6_col3 = start_NNN + (row6_midpoint)
            edge_row6_col4 = start_NNN + (row6_midpoint + (1 + cycle))
            edge_row6_col5 = start_NNN + (row6_midpoint + (2 + cycle))

            # logger.info("%d: edges row0 %d, %d, %d, %d, %d" % (x, edge_row0_col1, edge_row0_col2, edge_row0_col3, edge_row0_col4, edge_row0_col5))
            # logger.info("%d: edges row1 %d, %d" % (x, edge_row1_col1, edge_row1_col2))
            # logger.info("%d: edges row2 %d, %d" % (x, edge_row2_col1, edge_row2_col2))
            # logger.info("%d: edges row3 %d, %d" % (x, edge_row3_col1, edge_row3_col2))
            # logger.info("%d: edges row4 %d, %d" % (x, edge_row4_col1, edge_row4_col2))
            # logger.info("%d: edges row5 %d, %d" % (x, edge_row5_col1, edge_row5_col2))
            # logger.info("%d: edges row6 %d, %d, %d, %d, %d" % (x, edge_row6_col1, edge_row6_col2, edge_row6_col3, edge_row6_col4, edge_row6_col5))
            # logger.info("\n")

            fake_777.state[start_777 + 2] = self.state[edge_row0_col1]
            fake_777.state[start_777 + 3] = self.state[edge_row0_col2]
            fake_777.state[start_777 + 4] = self.state[edge_row0_col3]
            fake_777.state[start_777 + 5] = self.state[edge_row0_col4]
            fake_777.state[start_777 + 6] = self.state[edge_row0_col5]

            fake_777.state[start_777 + 8] = self.state[edge_row1_col1]
            fake_777.state[start_777 + 15] = self.state[edge_row2_col1]
            fake_777.state[start_777 + 22] = self.state[edge_row3_col1]
            fake_777.state[start_777 + 29] = self.state[edge_row4_col1]
            fake_777.state[start_777 + 36] = self.state[edge_row5_col1]

            fake_777.state[start_777 + 14] = self.state[edge_row1_col2]
            fake_777.state[start_777 + 21] = self.state[edge_row2_col2]
            fake_777.state[start_777 + 28] = self.state[edge_row3_col2]
            fake_777.state[start_777 + 35] = self.state[edge_row4_col2]
            fake_777.state[start_777 + 42] = self.state[edge_row5_col2]

            fake_777.state[start_777 + 44] = self.state[edge_row6_col1]
            fake_777.state[start_777 + 45] = self.state[edge_row6_col2]
            fake_777.state[start_777 + 46] = self.state[edge_row6_col3]
            fake_777.state[start_777 + 47] = self.state[edge_row6_col4]
            fake_777.state[start_777 + 48] = self.state[edge_row6_col5]

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

    def stage_or_solve_inside_777(self, center_orbit_id, max_center_orbits, width, cycle, max_cycle, action):
        tmp_solution_len = len(self.solution)
        self.populate_fake_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle)

        if (center_orbit_id == 0 and cycle == 0) or (center_orbit_id == max_center_orbits and cycle == max_cycle):
            outer_x_centers_valid = True
        else:
            outer_x_centers_valid = False

        if action == "stage_UD_centers":
            if outer_x_centers_valid:
                self.fake_777.stage_UD_centers()
            else:
                if cycle == max_cycle:
                    self.fake_777.stage_UD_t_centers()
                else:
                    self.fake_777.lt_UD_oblique_edge_pairing.solve_via_c(use_kociemba_string=True)

        elif action == "stage_LR_centers":
            if outer_x_centers_valid:
                self.fake_777.stage_LR_centers()
            else:
                if cycle == max_cycle:
                    self.fake_777.stage_LR_t_centers()
                else:
                    self.fake_777.lt_LR_oblique_edge_pairing.solve_via_c(use_kociemba_string=True)

        elif action == "solve_t_centers":
            self.fake_777.solve_t_centers()

        else:
            raise Exception(f"Invalid action {action}")

        # Apply the 7x7x7 solution to our cube
        half_size = str(ceil(self.size / 2) - 1 - cycle)
        wide_size = str(ceil(self.size / 2) - 2 - center_orbit_id)

        for step in self.fake_777.solution:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            elif step.startswith("3"):
                self.rotate(half_size + step[1:])
            elif "w" in step:
                self.rotate(wide_size + step)
            else:
                self.rotate(step)

        self.print_cube_add_comment(
            "NNN orbit %d/%d, cycle %d/%d, width %d, x-centers %s"
            % (center_orbit_id, max_center_orbits, cycle, max_cycle, width, outer_x_centers_valid),
            tmp_solution_len,
        )

    def reduce_555(self):
        if self.centers_solved():
            return

        max_center_orbits = int((self.size - 3) / 2) - 2

        # Stage all LR centers
        if not self.LR_centers_staged():
            tmp_solution_len = len(self.solution)

            for center_orbit_id in range(max_center_orbits + 1):
                width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
                max_cycle = int((width - 5) / 2)

                for cycle in range(max_cycle + 1):
                    self.stage_or_solve_inside_777(
                        center_orbit_id, max_center_orbits, width, cycle, max_cycle, "stage_LR_centers"
                    )

            self.print_cube_add_comment("NNN LR centers staged", tmp_solution_len)

        # Stage all UD centers
        if not self.UD_centers_staged():
            tmp_solution_len = len(self.solution)

            for center_orbit_id in range(max_center_orbits + 1):
                width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
                max_cycle = int((width - 5) / 2)

                for cycle in range(max_cycle + 1):
                    self.stage_or_solve_inside_777(
                        center_orbit_id, max_center_orbits, width, cycle, max_cycle, "stage_UD_centers"
                    )

            self.print_cube_add_comment("NNN UD centers staged", tmp_solution_len)

        # Solve all t-centers
        tmp_solution_len = len(self.solution)

        for center_orbit_id in range(max_center_orbits + 1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5) / 2)

            for cycle in range(max_cycle + 1):
                self.stage_or_solve_inside_777(
                    center_orbit_id, max_center_orbits, width, cycle, max_cycle, "solve_t_centers"
                )
        self.print_cube_add_comment("NNN t-centers solved", tmp_solution_len)
