
from pprint import pformat
from rubikscubennnsolver import RubiksCube, ImplementThis
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_4x4x4
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_5x5x5
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_6x6x6
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_7x7x7
from math import ceil
import logging
import sys

log = logging.getLogger(__name__)


class RubiksCubeNNNOdd(RubiksCube):

    def phase(self):
        return 'Solve Odd NxNxN'

    def solve_inside_777(self, center_orbit_id, max_center_orbits, width, cycle, max_cycle):
        fake_777 = RubiksCube777(solved_7x7x7, 'URFDLB')

        for index in range(1, 295):
            fake_777.state[index] = 'x'
        fake_777.cpu_mode = self.cpu_mode

        start_777 = 0
        start_NNN = 0
        row0_midpoint = ceil(self.size/2)

        log.warning("Start center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s" %\
            (center_orbit_id, max_center_orbits, width, cycle, max_cycle))

        for x in range(6):
            mid_NNN_row1 = start_NNN + row0_midpoint + (self.size * (max_center_orbits - center_orbit_id + 1))
            start_NNN_row1 = mid_NNN_row1 - (2 + cycle)
            end_NNN_row1 = mid_NNN_row1 + (2 + cycle)

            start_NNN_row5 = start_NNN_row1 + ((width-1) * self.size)
            mid_NNN_row5 = mid_NNN_row1 + ((width-1) * self.size)
            end_NNN_row5 = end_NNN_row1 + ((width-1) * self.size)

            mid_NNN_row3 = int((mid_NNN_row1 + mid_NNN_row5)/2)
            start_NNN_row3 = mid_NNN_row3 - (2 + center_orbit_id)
            end_NNN_row3 = mid_NNN_row3 + (2 + center_orbit_id)

            start_NNN_row2 = start_NNN_row3 - (self.size * (cycle+1))
            start_NNN_row4 = start_NNN_row3 + (self.size * (cycle+1))

            end_NNN_row2 = end_NNN_row3 - (self.size * (cycle+1))
            end_NNN_row4 = end_NNN_row3 + (self.size * (cycle+1))

            mid_NNN_row2 = int((start_NNN_row2 + end_NNN_row2)/2)
            mid_NNN_row4 = int((start_NNN_row4 + end_NNN_row4)/2)

            row1_col1 = start_NNN_row1
            row1_col2 = start_NNN_row1+1
            row1_col3 = mid_NNN_row1
            row1_col4 = end_NNN_row1-1
            row1_col5 = end_NNN_row1

            row2_col1 = start_NNN_row2
            row2_col2 = start_NNN_row2+1
            row2_col3 = mid_NNN_row2
            row2_col4 = end_NNN_row2-1
            row2_col5 = end_NNN_row2

            row3_col1 = start_NNN_row3
            row3_col2 = start_NNN_row3+1
            row3_col3 = mid_NNN_row3
            row3_col4 = end_NNN_row3-1
            row3_col5 = end_NNN_row3

            row4_col1 = start_NNN_row4
            row4_col2 = start_NNN_row4+1
            row4_col3 = mid_NNN_row4
            row4_col4 = end_NNN_row4-1
            row4_col5 = end_NNN_row4

            row5_col1 = start_NNN_row5
            row5_col2 = start_NNN_row5+1
            row5_col3 = mid_NNN_row5
            row5_col4 = end_NNN_row5-1
            row5_col5 = end_NNN_row5

            log.warning("%d: start_NNN_row1 %d, mid_NNN_row1 %d, end_NNN_row1 %d" % (x, start_NNN_row1, mid_NNN_row1, end_NNN_row1))
            log.warning("%d: start_NNN_row2 %d, mid_NNN_row2 %d, end_NNN_row2 %d" % (x, start_NNN_row2, mid_NNN_row2, end_NNN_row2))
            log.warning("%d: start_NNN_row3 %d, mid_NNN_row3 %d, end_NNN_row3 %d" % (x, start_NNN_row3, mid_NNN_row3, end_NNN_row3))
            log.warning("%d: start_NNN_row4 %d, mid_NNN_row4 %d, end_NNN_row4 %d" % (x, start_NNN_row4, mid_NNN_row4, end_NNN_row4))
            log.warning("%d: start_NNN_row5 %d, mid_NNN_row5 %d, end_NNN_row5 %d" % (x, start_NNN_row5, mid_NNN_row5, end_NNN_row5))

            log.warning("%d: row1 %d, %d, %d, %d, %d" % (x, row1_col1, row1_col2, row1_col3, row1_col4, row1_col5))
            log.warning("%d: row2 %d, %d, %d, %d, %d" % (x, row2_col1, row2_col2, row2_col3, row2_col4, row2_col5))
            log.warning("%d: row3 %d, %d, %d, %d, %d" % (x, row3_col1, row3_col2, row3_col3, row3_col4, row3_col5))
            log.warning("%d: row4 %d, %d, %d, %d, %d" % (x, row4_col1, row4_col2, row4_col3, row4_col4, row4_col5))
            log.warning("%d: row5 %d, %d, %d, %d, %d\n\n" % (x, row5_col1, row5_col2, row5_col3, row5_col4, row5_col5))

            # log.warning("End center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s" %\
            #   (center_orbit_id, max_center_orbits, width, cycle, max_cycle))
            if ((center_orbit_id == 0 and cycle == 0) or
                (center_orbit_id == max_center_orbits and cycle == max_cycle)):
                fake_777.state[start_777+9] = self.state[row1_col1]
                fake_777.state[start_777+10] = self.state[row1_col2]
                fake_777.state[start_777+11] = self.state[row1_col3]
                fake_777.state[start_777+12] = self.state[row1_col4]
                fake_777.state[start_777+13] = self.state[row1_col5]

                fake_777.state[start_777+16] = self.state[row2_col1]
                fake_777.state[start_777+17] = self.state[row2_col2]
                fake_777.state[start_777+18] = self.state[row2_col3]
                fake_777.state[start_777+19] = self.state[row2_col4]
                fake_777.state[start_777+20] = self.state[row2_col5]

                fake_777.state[start_777+23] = self.state[row3_col1]
                fake_777.state[start_777+24] = self.state[row3_col2]
                fake_777.state[start_777+25] = self.state[row3_col3]
                fake_777.state[start_777+26] = self.state[row3_col4]
                fake_777.state[start_777+27] = self.state[row3_col5]

                fake_777.state[start_777+30] = self.state[row4_col1]
                fake_777.state[start_777+31] = self.state[row4_col2]
                fake_777.state[start_777+32] = self.state[row4_col3]
                fake_777.state[start_777+33] = self.state[row4_col4]
                fake_777.state[start_777+34] = self.state[row4_col5]

                fake_777.state[start_777+37] = self.state[row5_col1]
                fake_777.state[start_777+38] = self.state[row5_col2]
                fake_777.state[start_777+39] = self.state[row5_col3]
                fake_777.state[start_777+40] = self.state[row5_col4]
                fake_777.state[start_777+41] = self.state[row5_col5]

            else:
                #fake_777.state[start_777+9] = self.state[row1_col1]
                fake_777.state[start_777+10] = self.state[row1_col2]
                fake_777.state[start_777+11] = self.state[row1_col3]
                fake_777.state[start_777+12] = self.state[row1_col4]
                #fake_777.state[start_777+13] = self.state[row1_col5]

                fake_777.state[start_777+16] = self.state[row2_col1]
                fake_777.state[start_777+17] = self.state[row2_col2]
                fake_777.state[start_777+18] = self.state[row2_col3]
                fake_777.state[start_777+19] = self.state[row2_col4]
                fake_777.state[start_777+20] = self.state[row2_col5]

                fake_777.state[start_777+23] = self.state[row3_col1]
                fake_777.state[start_777+24] = self.state[row3_col2]
                fake_777.state[start_777+25] = self.state[row3_col3]
                fake_777.state[start_777+26] = self.state[row3_col4]
                fake_777.state[start_777+27] = self.state[row3_col5]

                fake_777.state[start_777+30] = self.state[row4_col1]
                fake_777.state[start_777+31] = self.state[row4_col2]
                fake_777.state[start_777+32] = self.state[row4_col3]
                fake_777.state[start_777+33] = self.state[row4_col4]
                fake_777.state[start_777+34] = self.state[row4_col5]

                #fake_777.state[start_777+37] = self.state[row5_col1]
                fake_777.state[start_777+38] = self.state[row5_col2]
                fake_777.state[start_777+39] = self.state[row5_col3]
                fake_777.state[start_777+40] = self.state[row5_col4]
                #fake_777.state[start_777+41] = self.state[row5_col5]

            start_777 += 49
            start_NNN += (self.size * self.size)

        # Group LR centers (in turn groups FB)
        fake_777.sanity_check()
        fake_777.print_cube()
        fake_777.lt_init()

        # Apply the 7x7x7 solution to our cube
        half_size = str( ceil(self.size/2) - 1 - cycle )
        wide_size = str( ceil(self.size/2) - 2 - center_orbit_id)
        #log.warning("half_size %s, wide_size %s" % (half_size, wide_size))

        if ((center_orbit_id == 0 and cycle == 0) or
            (center_orbit_id == max_center_orbits and cycle == max_cycle)):
            fake_777.group_centers_guts()
        else:
            fake_777.group_centers_guts(oblique_edges_only=True)

        for step in fake_777.solution:
            if step.startswith("3"):
                self.rotate(half_size + step[1:])
            elif "w" in step:
                self.rotate(wide_size + step)
            else:
                self.rotate(step)

        self.print_cube()
        log.warning("End center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s" %\
            (center_orbit_id, max_center_orbits, width, cycle, max_cycle))

    def group_centers_guts(self):

        max_center_orbits = int((self.size - 3) / 2) - 2
        log.warning("max_center_orbits: %s" % max_center_orbits)

        for center_orbit_id in range(max_center_orbits+1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5)/2)
            log.warning("orbit %s, width %d, max_cycle %s" % (center_orbit_id, width, max_cycle))

            for cycle in range(max_cycle+1):
                self.solve_inside_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle)

        log.info("Centers are solved, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()

    def pair_edge_orbit_via_555(self, orbit):
        log.warning("pair_edge_orbit_via_555 for %d" % orbit)
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.cpu_mode = self.cpu_mode
        fake_555.lt_init()

        # Fill in the corners so we can avoid certain types of parity
        start_555 = 0
        start_777 = 0

        for x in range(6):
            fake_555.state[start_555+1] = self.state[start_777+1]
            fake_555.state[start_555+5] = self.state[start_777 + self.size]
            fake_555.state[start_555+21] = self.state[start_777 + (self.size * self.size) - self.size + 1]
            fake_555.state[start_555+25] = self.state[start_777 + (self.size * self.size)]
            start_777 += self.size * self.size
            start_555 += 25

        # Fill in the edges
        start_555 = 0
        start_777 = 0
        half_size = int(ceil(self.size/2))
        max_orbit = int((self.size - 3)/2)

        for x in range(6):
            row1_col2 = start_777 + half_size
            row1_col1 = row1_col2 - (max_orbit - orbit)
            row1_col3 = row1_col2 + (max_orbit - orbit)

            row2_col1 = start_777 + ((orbit+1) * self.size) + 1
            row2_col3 = row2_col1 + self.size - 1

            row3_col1 = start_777 + (self.size * (half_size - 1)) + 1
            row3_col3 = row3_col1 + self.size - 1

            row4_col1 = start_777 + (self.size * self.size) - ((orbit+2) * self.size) + 1
            row4_col3 = row4_col1 + self.size - 1

            row5_col1 = row1_col1 + ((self.size - 1) * self.size)
            row5_col2 = row1_col2 + ((self.size - 1) * self.size)
            row5_col3 = row1_col3 + ((self.size - 1) * self.size)

            log.warning("%d row1: %s, %s, %s" % (x, row1_col1, row1_col2, row1_col3))
            log.warning("%d row2: %s, %s" % (x, row2_col1, row2_col3))
            log.warning("%d row3: %s, %s" % (x, row3_col1, row3_col3))
            log.warning("%d row4: %s, %s" % (x, row4_col1, row4_col3))
            log.warning("%d row5: %s, %s, %s" % (x, row5_col1, row5_col2, row5_col3))

            # row1
            fake_555.state[start_555+2] = self.state[row1_col1]
            fake_555.state[start_555+3] = self.state[row1_col2]
            fake_555.state[start_555+4] = self.state[row1_col3]

            # row2
            fake_555.state[start_555+6] = self.state[row2_col1]
            fake_555.state[start_555+10] = self.state[row2_col3]

            # row3 - The middle of the edge so orbit doesn't matter
            fake_555.state[start_555+11] = self.state[row3_col1]
            fake_555.state[start_555+15] = self.state[row3_col3]

            # row4
            fake_555.state[start_555+16] = self.state[row4_col1]
            fake_555.state[start_555+20] = self.state[row4_col3]

            # row5
            fake_555.state[start_555+22] = self.state[row5_col1]
            fake_555.state[start_555+23] = self.state[row5_col2]
            fake_555.state[start_555+24] = self.state[row5_col3]

            start_777 += self.size * self.size
            start_555 += 25

        fake_555.sanity_check()
        fake_555.avoid_pll = False
        fake_555.group_edges()
        wide_str = str(orbit + 2)

        for step in fake_555.solution:

            if step == 'EDGES_GROUPED':
                continue

            # Rotate the entire cube
            if step.startswith('5'):
                step = str(self.size) + step[1:]

            elif step in ("Uw", "Uw'", "Uw2",
                          "Lw", "Lw'", "Lw2",
                          "Fw", "Fw'", "Fw2",
                          "Rw", "Rw'", "Rw2",
                          "Bw", "Bw'", "Bw2",
                          "Dw", "Dw'", "Dw2"):
                step = wide_str + step

            self.rotate(step)

    def group_edges(self):

        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        # How many orbits of edges does this cube have?
        max_orbit = int((self.size/2) - 1)

        # Work your way from inside to outside and pair each orbit via the 5x5x5 solver
        for orbit in reversed(list(range(0, max_orbit))):
            self.pair_edge_orbit_via_555(orbit)

        self.solution.append('EDGES_GROUPED')
        log.info("Edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
