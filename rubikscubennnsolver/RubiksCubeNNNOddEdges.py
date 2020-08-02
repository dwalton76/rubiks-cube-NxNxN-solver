# standard libraries
import logging
from math import ceil

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555

log = logging.getLogger(__name__)


class RubiksCubeNNNOddEdges(RubiksCube):
    def lt_init(self):
        pass

    def get_fake_555(self):
        if self.fake_555 is None:
            if self.fake_777 and self.fake_777.fake_555:
                self.fake_555 = self.fake_777.fake_555
                self.fake_555.cpu_mode = self.cpu_mode
                self.fake_555.re_init()
                self.fake_555.enable_print_cube = False
            else:
                # Because our centers are already solved we get very little benefit
                # from using the more advanced 555 edge pairing code path...and it
                # takes much longer to run.  For now use the old L4E way it is only
                # about 1 move longer if the centers are solved but runs 3x faster.
                self.fake_555 = RubiksCube555(solved_555, "URFDLB")
                self.fake_555.cpu_mode = self.cpu_mode
                self.fake_555.lt_init()
                self.fake_555.enable_print_cube = False
        else:
            self.fake_555.re_init()
        return self.fake_555

    def pair_edge_orbit_via_555(self, orbit):
        log.info("%s: pair_edge_orbit_via_555 for %d" % (self, orbit))
        fake_555 = self.get_fake_555()

        # Fill in the corners so we can avoid certain types of parity
        start_555 = 0
        start_nnn = 0

        for x in range(6):
            fake_555.state[start_555 + 1] = self.state[start_nnn + 1]
            fake_555.state[start_555 + 5] = self.state[start_nnn + self.size]
            fake_555.state[start_555 + 21] = self.state[start_nnn + (self.size * self.size) - self.size + 1]
            fake_555.state[start_555 + 25] = self.state[start_nnn + (self.size * self.size)]
            start_nnn += self.size * self.size
            start_555 += 25

        # Fill in the edges
        start_555 = 0
        start_nnn = 0
        half_size = int(ceil(self.size / 2))
        max_orbit = int((self.size - 3) / 2)

        for x in range(6):
            row1_col2 = start_nnn + half_size
            row1_col1 = row1_col2 - (max_orbit - orbit)
            row1_col3 = row1_col2 + (max_orbit - orbit)

            row2_col1 = start_nnn + ((orbit + 1) * self.size) + 1
            row2_col3 = row2_col1 + self.size - 1

            row3_col1 = start_nnn + (self.size * (half_size - 1)) + 1
            row3_col3 = row3_col1 + self.size - 1

            row4_col1 = start_nnn + (self.size * self.size) - ((orbit + 2) * self.size) + 1
            row4_col3 = row4_col1 + self.size - 1

            row5_col1 = row1_col1 + ((self.size - 1) * self.size)
            row5_col2 = row1_col2 + ((self.size - 1) * self.size)
            row5_col3 = row1_col3 + ((self.size - 1) * self.size)

            log.debug("%d row1: %s, %s, %s" % (x, row1_col1, row1_col2, row1_col3))
            log.debug("%d row2: %s, %s" % (x, row2_col1, row2_col3))
            log.debug("%d row3: %s, %s" % (x, row3_col1, row3_col3))
            log.debug("%d row4: %s, %s" % (x, row4_col1, row4_col3))
            log.debug("%d row5: %s, %s, %s" % (x, row5_col1, row5_col2, row5_col3))

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

        # Fill in the centers
        if orbit == 0:
            start_555 = 0
            start_nnn = 0
            centers_size = self.size - 2
            half_centers_size = int(centers_size / 2)

            row1_col1 = self.size + 2
            row1_col2 = row1_col1 + half_centers_size
            row1_col3 = row1_col2 + half_centers_size

            row2_col2 = int(ceil((self.size * self.size) / 2))
            row2_col1 = row2_col2 - half_centers_size
            row2_col3 = row2_col2 + half_centers_size

            row3_col3 = (self.size * self.size) - self.size - 1
            row3_col2 = row3_col3 - half_centers_size
            row3_col1 = row3_col2 - half_centers_size

            for x in range(6):
                fake_555.state[start_555 + 7] = self.state[start_nnn + row1_col1]
                fake_555.state[start_555 + 8] = self.state[start_nnn + row1_col2]
                fake_555.state[start_555 + 9] = self.state[start_nnn + row1_col3]

                fake_555.state[start_555 + 12] = self.state[start_nnn + row2_col1]
                fake_555.state[start_555 + 13] = self.state[start_nnn + row2_col2]
                fake_555.state[start_555 + 14] = self.state[start_nnn + row2_col3]

                fake_555.state[start_555 + 17] = self.state[start_nnn + row3_col1]
                fake_555.state[start_555 + 18] = self.state[start_nnn + row3_col2]
                fake_555.state[start_555 + 19] = self.state[start_nnn + row3_col3]

                start_nnn += self.size * self.size
                start_555 += 25

        self.print_cube()
        fake_555.enable_print_cube = True
        fake_555.print_cube()
        fake_555.sanity_check()
        fake_555.avoid_pll = False
        fake_555.reduce_333()

        wide_str = str(orbit + 2)

        for step in fake_555.solution:
            if step in ("CENTERS_SOLVED", "EDGES_GROUPED"):
                continue
            elif step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                # Rotate the entire cube
                if step.startswith("5"):
                    step = str(self.size) + step[1:]

                elif step in (
                    "Uw",
                    "Uw'",
                    "Uw2",
                    "Lw",
                    "Lw'",
                    "Lw2",
                    "Fw",
                    "Fw'",
                    "Fw2",
                    "Rw",
                    "Rw'",
                    "Rw2",
                    "Bw",
                    "Bw'",
                    "Bw2",
                    "Dw",
                    "Dw'",
                    "Dw2",
                ):
                    step = wide_str + step

                elif step in (
                    "2U",
                    "2U'",
                    "2U2",
                    "2L",
                    "2L'",
                    "2L2",
                    "2F",
                    "2F'",
                    "2F2",
                    "2R",
                    "2R'",
                    "2R2",
                    "2B",
                    "2B'",
                    "2B2",
                    "2D",
                    "2D'",
                    "2D2",
                ):
                    step = wide_str + step[1:]

                # log.info("wide_str %s, orig-step %s -> step %s" % (wide_str, orig_step, step))
                self.rotate(step)

    def group_edges(self):

        # How many orbits of edges does this cube have?
        max_orbit = int((self.size / 2) - 1)

        # Work your way from inside to outside and pair each orbit via the 5x5x5 solver
        for orbit in reversed(list(range(0, max_orbit))):
            self.pair_edge_orbit_via_555(orbit)

        self.print_cube()
        log.info("%s: Edges are paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
