
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


class RubiksCubeNNNEven(RubiksCube):

    def phase(self):
        return 'Solve Even NxNxN'

    def make_plus_sign(self):
        """
        Pair the middle two columns/rows in order to convert this Even cube into
        an Odd cube...this allows us to use the 7x7x7 solver later.  It makes what
        looks like a large "plus" sign on each cube face thus the name of this
        method.
        """
        center_orbit_count = int((self.size - 4)/2)

        # Make a big "plus" sign on each side, this will allow us to reduce the
        # centers to a series of 7x7x7 centers
        for center_orbit_id in range(center_orbit_count):

            # Group UD centers
            # - create a fake 6x6x6 to solve the inside 4x4 block
            fake_666 = RubiksCube666(solved_6x6x6, 'URFDLB')

            for index in range(1, 217):
                fake_666.state[index] = 'x'
            fake_666.cpu_mode = self.cpu_mode

            start_666 = 0
            start_NNN = 0

            for x in range(6):
                start_NNN_row1 = int(start_NNN + (((self.size/2) - 2) * self.size) + ((self.size/2) - 1))
                start_NNN_row2 = start_NNN_row1 + self.size
                start_NNN_row3 = start_NNN_row2 + self.size
                start_NNN_row4 = start_NNN_row3 + self.size

                #fake_666.state[start_666+8] = self.state[start_NNN_row1 - (center_orbit_id * self.size)]
                fake_666.state[start_666+9] = self.state[start_NNN_row1+1 - (center_orbit_id * self.size)]
                fake_666.state[start_666+10] = self.state[start_NNN_row1+2 - (center_orbit_id * self.size)]
                #fake_666.state[start_666+11] = self.state[start_NNN_row1+3 - (center_orbit_id * self.size)]

                fake_666.state[start_666+14] = self.state[start_NNN_row2 - center_orbit_id]
                fake_666.state[start_666+15] = self.state[start_NNN_row2+1]
                fake_666.state[start_666+16] = self.state[start_NNN_row2+2]
                fake_666.state[start_666+17] = self.state[start_NNN_row2+3 + center_orbit_id]

                fake_666.state[start_666+20] = self.state[start_NNN_row3 - center_orbit_id]
                fake_666.state[start_666+21] = self.state[start_NNN_row3+1]
                fake_666.state[start_666+22] = self.state[start_NNN_row3+2]
                fake_666.state[start_666+23] = self.state[start_NNN_row3+3 + center_orbit_id]

                #fake_666.state[start_666+26] = self.state[start_NNN_row4 + (center_orbit_id * self.size)]
                fake_666.state[start_666+27] = self.state[start_NNN_row4+1 + (center_orbit_id * self.size)]
                fake_666.state[start_666+28] = self.state[start_NNN_row4+2 + (center_orbit_id * self.size)]
                #fake_666.state[start_666+29] = self.state[start_NNN_row4+3 + (center_orbit_id * self.size)]
                start_666 += 36
                start_NNN += (self.size * self.size)

            fake_666.sanity_check()

            # Group LR centers (in turn groups FB)
            fake_666.lt_init()
            fake_666.print_cube()
            fake_666.group_centers_guts(oblique_edges_only=True)
            #fake_666.print_solution()
            fake_666.print_cube()

            # Apply the 6x6x6 solution to our cube
            half_size = str(int(self.size/2))
            wide_size = str(int(half_size) - 1 - center_orbit_id)

            for step in fake_666.solution:
                if step.startswith("3"):
                    self.rotate(half_size + step[1:])
                elif "w" in step:
                    self.rotate(wide_size + step)
                else:
                    self.rotate(step)
            fake_666 = None

        log.info("Big plus sign formed, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()

    def solve_inside_777(self, center_orbit_id, max_center_orbits, width, cycle, max_cycle):
        fake_777 = RubiksCube777(solved_7x7x7, 'URFDLB')

        for index in range(1, 295):
            fake_777.state[index] = 'x'
        fake_777.cpu_mode = self.cpu_mode

        start_777 = 0
        start_NNN = 0
        row0_midpoint = ceil(self.size/2)

        log.info("Start center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s" %\
            (center_orbit_id, max_center_orbits, width, cycle, max_cycle))

        for x in range(6):
            mid_NNN_row1 = start_NNN + row0_midpoint + (self.size * (max_center_orbits - center_orbit_id + 1))
            start_NNN_row1 = mid_NNN_row1 - (2 + cycle)
            end_NNN_row1 = mid_NNN_row1 + (2 + cycle) + 1

            start_NNN_row5 = start_NNN_row1 + ((width-1) * self.size)
            mid_NNN_row5 = mid_NNN_row1 + ((width-1) * self.size)
            end_NNN_row5 = end_NNN_row1 + ((width-1) * self.size)

            mid_NNN_row3 = int(mid_NNN_row1 + ((width/2) * self.size) - self.size)
            start_NNN_row3 = mid_NNN_row3 - (2 + center_orbit_id)
            end_NNN_row3 = mid_NNN_row3 + (2 + center_orbit_id) + 1

            start_NNN_row2 = start_NNN_row3 - (self.size * (cycle+1))
            start_NNN_row4 = start_NNN_row3 + (self.size * (cycle+1)) + self.size

            end_NNN_row2 = end_NNN_row3 - (self.size * (cycle+1))
            end_NNN_row4 = end_NNN_row3 + (self.size * (cycle+1)) + self.size

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

            log.info("%d: start_NNN_row1 %d, mid_NNN_row1 %d, end_NNN_row1 %d" % (x, start_NNN_row1, mid_NNN_row1, end_NNN_row1))
            log.info("%d: start_NNN_row2 %d, mid_NNN_row2 %d, end_NNN_row2 %d" % (x, start_NNN_row2, mid_NNN_row2, end_NNN_row2))
            log.info("%d: start_NNN_row3 %d, mid_NNN_row3 %d, end_NNN_row3 %d" % (x, start_NNN_row3, mid_NNN_row3, end_NNN_row3))
            log.info("%d: start_NNN_row4 %d, mid_NNN_row4 %d, end_NNN_row4 %d" % (x, start_NNN_row4, mid_NNN_row4, end_NNN_row4))
            log.info("%d: start_NNN_row5 %d, mid_NNN_row5 %d, end_NNN_row5 %d" % (x, start_NNN_row5, mid_NNN_row5, end_NNN_row5))

            log.info("%d: row1 %d, %d, %d, %d, %d" % (x, row1_col1, row1_col2, row1_col3, row1_col4, row1_col5))
            log.info("%d: row2 %d, %d, %d, %d, %d" % (x, row2_col1, row2_col2, row2_col3, row2_col4, row2_col5))
            log.info("%d: row3 %d, %d, %d, %d, %d" % (x, row3_col1, row3_col2, row3_col3, row3_col4, row3_col5))
            log.info("%d: row4 %d, %d, %d, %d, %d" % (x, row4_col1, row4_col2, row4_col3, row4_col4, row4_col5))
            log.info("%d: row5 %d, %d, %d, %d, %d\n\n" % (x, row5_col1, row5_col2, row5_col3, row5_col4, row5_col5))

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
        log.info("End center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s" %\
            (center_orbit_id, max_center_orbits, width, cycle, max_cycle))

    def group_centers_guts(self):
        self.make_plus_sign()

        max_center_orbits = int((self.size - 3) / 2) - 2

        for center_orbit_id in range(max_center_orbits+1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5)/2)

            for cycle in range(max_cycle+1):
                self.solve_inside_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle)

        log.info("Centers are solved, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()

    def pair_inside_edges_via_444(self):
        fake_444 = RubiksCube444(solved_4x4x4, 'URFDLB')
        fake_444.cpu_mode = self.cpu_mode
        fake_444.lt_init()

        # Fill in the corners so that we can avoid PLL parity when pairing the edges
        start_444 = 0
        start_777 = 0

        for x in range(6):
            fake_444.state[start_444+1] = self.state[start_777+1]
            fake_444.state[start_444+4] = self.state[start_777 + self.size]
            fake_444.state[start_444+13] = self.state[start_777 + (self.size * self.size) - self.size + 1]
            fake_444.state[start_444+16] = self.state[start_777 + (self.size * self.size)]
            start_777 += self.size * self.size
            start_444 += 16

        # Fill in the edges
        start_444 = 0
        start_777 = 0
        half_size = int(self.size/2)

        for x in range(6):

            fake_444.state[start_444+2] = self.state[start_777 + half_size]
            fake_444.state[start_444+3] = self.state[start_777 + half_size + 1]
            fake_444.state[start_444+5] = self.state[start_777 + (self.size * (half_size-1)) + 1]
            fake_444.state[start_444+8] = self.state[start_777 + (self.size * half_size)]
            fake_444.state[start_444+9] = self.state[start_777 + (self.size * half_size) + 1]
            fake_444.state[start_444+12] = self.state[start_777 + (self.size * (half_size+1))]
            fake_444.state[start_444+14] = self.state[start_777 + (self.size * self.size) - half_size]
            fake_444.state[start_444+15] = self.state[start_777 + (self.size * self.size) - half_size + 1]
            start_777 += self.size * self.size
            start_444 += 16

        fake_444.sanity_check()
        fake_444.group_edges()
        half_size_str = str(half_size)

        for step in fake_444.solution:

            if step == 'EDGES_GROUPED':
                continue

            # Rotate the entire cube
            if step.startswith('4'):
                step = str(self.size) + step[1:]

            elif step in ("Uw", "Uw'", "Uw2",
                          "Lw", "Lw'", "Lw2",
                          "Fw", "Fw'", "Fw2",
                          "Rw", "Rw'", "Rw2",
                          "Bw", "Bw'", "Bw2",
                          "Dw", "Dw'", "Dw2"):
                step = half_size_str + step

            self.rotate(step)

        log.info("Inside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def pair_edge_orbit_via_555(self, orbit):
        log.info("pair_edge_orbit_via_555 for %d" % orbit)
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
        half_size = int(self.size/2)
        max_orbit = int((self.size - 2)/2) - 1

        for x in range(6):
            row1_col2 = start_777 + half_size
            row1_col1 = row1_col2 - (max_orbit - orbit)
            row1_col3 = row1_col2 + (max_orbit - orbit) + 1

            row2_col1 = start_777 + ((orbit+1) * self.size) + 1
            row2_col3 = row2_col1 + self.size - 1

            row3_col1 = start_777 + (self.size * (half_size - 1)) + 1
            row3_col3 = row3_col1 + self.size - 1

            row4_col1 = start_777 + (self.size * self.size) - ((orbit+2) * self.size) + 1
            row4_col3 = row4_col1 + self.size - 1

            row5_col1 = row1_col1 + ((self.size - 1) * self.size)
            row5_col2 = row1_col2 + ((self.size - 1) * self.size)
            row5_col3 = row1_col3 + ((self.size - 1) * self.size)

            log.info("%d row1: %s, %s, %s" % (x, row1_col1, row1_col2, row1_col3))
            log.info("%d row2: %s, %s" % (x, row2_col1, row2_col3))
            log.info("%d row3: %s, %s" % (x, row3_col1, row3_col3))
            log.info("%d row4: %s, %s" % (x, row4_col1, row4_col3))
            log.info("%d row5: %s, %s, %s" % (x, row5_col1, row5_col2, row5_col3))

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
        self.print_cube()
        fake_555.print_cube()
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

        # Pair the inside edges via fake 4x4x4
        self.pair_inside_edges_via_444()

        # How many orbits of edges does this cube have?
        max_orbit = int((self.size/2) - 1)

        # The inside orbit was paired above via pair_inside_edges_via_444()
        # For all of the rest work your way from inside to outside and pair
        # them via the 5x5x5 solver.
        for orbit in reversed(list(range(0, max_orbit-1))):
            self.pair_edge_orbit_via_555(orbit)

        self.solution.append('EDGES_GROUPED')
        log.info("Edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
