
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

    def solve_inside_777(self):
        fake_777 = RubiksCube777(solved_7x7x7, 'URFDLB')

        for index in range(1, 295):
            fake_777.state[index] = 'x'
        fake_777.cpu_mode = self.cpu_mode

        start_777 = 0
        start_NNN = 0
        row1_column = int((self.size/2) - 1)
        log.warning("row1_column %s, size %s" % (row1_column, self.size))

        for x in range(6):
            start_NNN_row1 = int(start_NNN + row1_column + ((row1_column-1) * self.size))
            start_NNN_row2 = start_NNN_row1 + self.size
            start_NNN_row3 = start_NNN_row2 + self.size
            start_NNN_row4 = start_NNN_row3 + self.size
            start_NNN_row5 = start_NNN_row4 + self.size

            log.warning("%d: start_NNN_row1 %d" % (x, start_NNN_row1))
            log.warning("%d: start_NNN_row2 %d" % (x, start_NNN_row2))
            log.warning("%d: start_NNN_row3 %d" % (x, start_NNN_row3))
            log.warning("%d: start_NNN_row4 %d" % (x, start_NNN_row4))
            log.warning("%d: start_NNN_row5 %d" % (x, start_NNN_row5))

            fake_777.state[start_777+9] = self.state[start_NNN_row1]
            fake_777.state[start_777+10] = self.state[start_NNN_row1+1]
            fake_777.state[start_777+11] = self.state[start_NNN_row1+2]
            fake_777.state[start_777+12] = self.state[start_NNN_row1+3]
            fake_777.state[start_777+13] = self.state[start_NNN_row1+4]

            fake_777.state[start_777+16] = self.state[start_NNN_row2]
            fake_777.state[start_777+17] = self.state[start_NNN_row2+1]
            fake_777.state[start_777+18] = self.state[start_NNN_row2+2]
            fake_777.state[start_777+19] = self.state[start_NNN_row2+3]
            fake_777.state[start_777+20] = self.state[start_NNN_row2+4]

            fake_777.state[start_777+23] = self.state[start_NNN_row3]
            fake_777.state[start_777+24] = self.state[start_NNN_row3+1]
            fake_777.state[start_777+25] = self.state[start_NNN_row3+2]
            fake_777.state[start_777+26] = self.state[start_NNN_row3+3]
            fake_777.state[start_777+27] = self.state[start_NNN_row3+4]

            fake_777.state[start_777+30] = self.state[start_NNN_row4]
            fake_777.state[start_777+31] = self.state[start_NNN_row4+1]
            fake_777.state[start_777+32] = self.state[start_NNN_row4+2]
            fake_777.state[start_777+33] = self.state[start_NNN_row4+3]
            fake_777.state[start_777+34] = self.state[start_NNN_row4+4]

            fake_777.state[start_777+37] = self.state[start_NNN_row5]
            fake_777.state[start_777+38] = self.state[start_NNN_row5+1]
            fake_777.state[start_777+39] = self.state[start_NNN_row5+2]
            fake_777.state[start_777+40] = self.state[start_NNN_row5+3]
            fake_777.state[start_777+41] = self.state[start_NNN_row5+4]

            start_777 += 49
            start_NNN += (self.size * self.size)

        # Group LR centers (in turn groups FB)
        fake_777.sanity_check()
        fake_777.print_cube()
        fake_777.lt_init()
        fake_777.group_centers_guts()
        fake_777.print_cube()

        # Apply the 7x7x7 solution to our cube
        half_size = str(int(self.size/2) - 1)
        wide_size = str(int(half_size) - 1)

        for step in fake_777.solution:
            if step.startswith("3"):
                self.rotate(half_size + step[1:])
            elif "w" in step:
                self.rotate(wide_size + step)
            else:
                self.rotate(step)


    def experiment_777_part1(self):
        center_orbit_count = int((self.size - 4)/2)
        log.warning("center_orbit_count %d" % center_orbit_count)

        #for center_orbit_id in range(center_orbit_count):
        for center_orbit_id in range(1):
            fake_777 = RubiksCube777(solved_7x7x7, 'URFDLB')

            for index in range(1, 295):
                fake_777.state[index] = 'x'
            fake_777.cpu_mode = self.cpu_mode

            start_777 = 0
            start_NNN = 0

            for x in range(6):
                start_NNN_row1 = int(start_NNN + (((self.size/2) - 3) * self.size) + (self.size/2) - 2)
                start_NNN_row1 -= self.size * center_orbit_id
                start_NNN_row2 = start_NNN_row1 + self.size - center_orbit_id
                start_NNN_row3 = start_NNN_row2 + self.size
                start_NNN_row4 = start_NNN_row3 + self.size + self.size + (self.size * center_orbit_id * 2)
                start_NNN_row5 = start_NNN_row4 + self.size + center_orbit_id
                offset_from_edge = start_NNN_row1 % self.size

                end_NNN_row1 = (start_NNN_row1 - offset_from_edge) + self.size - offset_from_edge + 1
                start_to_end_delta = end_NNN_row1 - start_NNN_row1
                start_to_end_inner_delta = start_to_end_delta + (2 * center_orbit_id)

                end_NNN_row2 = start_NNN_row2 + start_to_end_inner_delta
                end_NNN_row3 = start_NNN_row3 + start_to_end_inner_delta
                end_NNN_row4 = start_NNN_row4 + start_to_end_inner_delta
                end_NNN_row5 = start_NNN_row5 + start_to_end_delta

                log.warning("%d/%d: offset_from_edge %s" % (center_orbit_id, x, offset_from_edge))
                log.warning("%d/%d: start_NNN_row1 %d, end_NNN_row1 %d" % (center_orbit_id, x, start_NNN_row1, end_NNN_row1))
                log.warning("%d/%d: start_NNN_row2 %d, end_NNN_row2 %d" % (center_orbit_id, x, start_NNN_row2, end_NNN_row2))
                log.warning("%d/%d: start_NNN_row3 %d, end_NNN_row3 %d" % (center_orbit_id, x, start_NNN_row3, end_NNN_row3))
                log.warning("%d/%d: start_NNN_row4 %d, end_NNN_row4 %d" % (center_orbit_id, x, start_NNN_row4, end_NNN_row4))
                log.warning("%d/%d: start_NNN_row5 %d, end_NNN_row5 %d" % (center_orbit_id, x, start_NNN_row5, end_NNN_row5))

                assert end_NNN_row1 > start_NNN_row1, "row1 start %d -> end %d" % (start_NNN_row1, end_NNN_row1)
                assert end_NNN_row2 > start_NNN_row2, "row2 start %d -> end %d" % (start_NNN_row2, end_NNN_row2)
                assert end_NNN_row3 > start_NNN_row3, "row3 start %d -> end %d" % (start_NNN_row3, end_NNN_row3)
                assert end_NNN_row4 > start_NNN_row4, "row4 start %d -> end %d" % (start_NNN_row4, end_NNN_row4)
                assert end_NNN_row5 > start_NNN_row5, "row5 start %d -> end %d" % (start_NNN_row5, end_NNN_row5)

                fake_777.state[start_777+9] = self.state[start_NNN_row1]
                fake_777.state[start_777+10] = self.state[start_NNN_row1+1]
                fake_777.state[start_777+11] = self.state[start_NNN_row1+2]
                fake_777.state[start_777+12] = self.state[end_NNN_row1-1]
                fake_777.state[start_777+13] = self.state[end_NNN_row1]

                fake_777.state[start_777+16] = self.state[start_NNN_row2]
                fake_777.state[start_777+17] = self.state[start_NNN_row2+1]
                fake_777.state[start_777+18] = self.state[start_NNN_row2+2]
                fake_777.state[start_777+19] = self.state[end_NNN_row2-1]
                fake_777.state[start_777+20] = self.state[end_NNN_row2]

                fake_777.state[start_777+23] = self.state[start_NNN_row3]
                fake_777.state[start_777+24] = self.state[start_NNN_row3+1]
                fake_777.state[start_777+25] = self.state[start_NNN_row3+2]
                fake_777.state[start_777+26] = self.state[end_NNN_row3-1]
                fake_777.state[start_777+27] = self.state[end_NNN_row3]

                fake_777.state[start_777+30] = self.state[start_NNN_row4]
                fake_777.state[start_777+31] = self.state[start_NNN_row4+1]
                fake_777.state[start_777+32] = self.state[start_NNN_row4+2]
                fake_777.state[start_777+33] = self.state[end_NNN_row4-1]
                fake_777.state[start_777+34] = self.state[end_NNN_row4]

                fake_777.state[start_777+37] = self.state[start_NNN_row5]
                fake_777.state[start_777+38] = self.state[start_NNN_row5+1]
                fake_777.state[start_777+39] = self.state[start_NNN_row5+2]
                fake_777.state[start_777+40] = self.state[end_NNN_row5-1]
                fake_777.state[start_777+41] = self.state[end_NNN_row5]

                start_777 += 49
                start_NNN += (self.size * self.size)

            fake_777.sanity_check()

            # Group LR centers (in turn groups FB)
            fake_777.print_cube()
            log.warning("fake_777 kociemba: %s" % fake_777.get_kociemba_string(True))
            fake_777.lt_init()
            #fake_777.group_centers_guts(oblique_edges_only=True)
            fake_777.group_centers_guts()
            fake_777.print_cube()

            # Apply the 7x7x7 solution to our cube
            half_size = str(int(self.size/2) - 1)
            wide_size = str(int(half_size) - 1 - center_orbit_id)
            self.print_cube()
            log.warning("half_size %s, wide_size %s" % (half_size, wide_size))

            for step in fake_777.solution:
                if step.startswith("3"):
                    self.rotate(half_size + step[1:])
                elif "w" in step:
                    self.rotate(wide_size + step)
                else:
                    self.rotate(step)
            fake_777 = None
            log.warning("%d/%d: end of orbit" % (center_orbit_id, x))
            self.print_cube()

    def experiment_777_part2(self):
        center_orbit_count = int((self.size - 4)/2)
        log.warning("center_orbit_count %d" % center_orbit_count)

        #for center_orbit_id in range(center_orbit_count):
        for center_orbit_id in range(1):
            fake_777 = RubiksCube777(solved_7x7x7, 'URFDLB')

            for index in range(1, 295):
                fake_777.state[index] = 'x'
            fake_777.cpu_mode = self.cpu_mode

            start_777 = 0
            start_NNN = 0

            for x in range(6):
                start_NNN_row1 = int(start_NNN + ((self.size/2) - 2) + self.size)
                start_NNN_row2 = start_NNN_row1 + (self.size * 2) - 1
                start_NNN_row3 = start_NNN_row2 + self.size
                start_NNN_row4 = start_NNN_row3 + (self.size * 2)
                start_NNN_row5 = start_NNN_row4 + (self.size * 2) + 1
                offset_from_edge = start_NNN_row1 % self.size

                end_NNN_row1 = (start_NNN_row1 - offset_from_edge) + self.size - offset_from_edge + 1
                start_to_end_narrow_delta = end_NNN_row1 - start_NNN_row1
                start_to_end_wide_delta = start_to_end_narrow_delta + (2 * (center_orbit_id + 1))

                end_NNN_row2 = start_NNN_row2 + start_to_end_wide_delta
                end_NNN_row3 = start_NNN_row3 + start_to_end_wide_delta
                end_NNN_row4 = start_NNN_row4 + start_to_end_wide_delta
                end_NNN_row5 = start_NNN_row5 + start_to_end_narrow_delta

                log.warning("%d/%d: offset_from_edge %s" % (center_orbit_id, x, offset_from_edge))
                log.warning("%d/%d: start_NNN_row1 %d, end_NNN_row1 %d" % (center_orbit_id, x, start_NNN_row1, end_NNN_row1))
                log.warning("%d/%d: start_NNN_row2 %d, end_NNN_row2 %d" % (center_orbit_id, x, start_NNN_row2, end_NNN_row2))
                log.warning("%d/%d: start_NNN_row3 %d, end_NNN_row3 %d" % (center_orbit_id, x, start_NNN_row3, end_NNN_row3))
                log.warning("%d/%d: start_NNN_row4 %d, end_NNN_row4 %d" % (center_orbit_id, x, start_NNN_row4, end_NNN_row4))
                log.warning("%d/%d: start_NNN_row5 %d, end_NNN_row5 %d" % (center_orbit_id, x, start_NNN_row5, end_NNN_row5))

                assert end_NNN_row1 > start_NNN_row1, "row1 start %d -> end %d" % (start_NNN_row1, end_NNN_row1)
                assert end_NNN_row2 > start_NNN_row2, "row2 start %d -> end %d" % (start_NNN_row2, end_NNN_row2)
                assert end_NNN_row3 > start_NNN_row3, "row3 start %d -> end %d" % (start_NNN_row3, end_NNN_row3)
                assert end_NNN_row4 > start_NNN_row4, "row4 start %d -> end %d" % (start_NNN_row4, end_NNN_row4)
                assert end_NNN_row5 > start_NNN_row5, "row5 start %d -> end %d" % (start_NNN_row5, end_NNN_row5)

                #fake_777.state[start_777+9] = self.state[start_NNN_row1]
                fake_777.state[start_777+10] = self.state[start_NNN_row1+1]
                fake_777.state[start_777+11] = self.state[start_NNN_row1+2]
                fake_777.state[start_777+12] = self.state[end_NNN_row1-1]
                #fake_777.state[start_777+13] = self.state[end_NNN_row1]

                fake_777.state[start_777+16] = self.state[start_NNN_row2]
                fake_777.state[start_777+17] = self.state[start_NNN_row2+1]
                fake_777.state[start_777+18] = self.state[start_NNN_row2+2]
                fake_777.state[start_777+19] = self.state[end_NNN_row2-1]
                fake_777.state[start_777+20] = self.state[end_NNN_row2]

                fake_777.state[start_777+23] = self.state[start_NNN_row3]
                fake_777.state[start_777+24] = self.state[start_NNN_row3+1]
                fake_777.state[start_777+25] = self.state[start_NNN_row3+2]
                fake_777.state[start_777+26] = self.state[end_NNN_row3-1]
                fake_777.state[start_777+27] = self.state[end_NNN_row3]

                fake_777.state[start_777+30] = self.state[start_NNN_row4]
                fake_777.state[start_777+31] = self.state[start_NNN_row4+1]
                fake_777.state[start_777+32] = self.state[start_NNN_row4+2]
                fake_777.state[start_777+33] = self.state[end_NNN_row4-1]
                fake_777.state[start_777+34] = self.state[end_NNN_row4]

                #fake_777.state[start_777+37] = self.state[start_NNN_row5]
                fake_777.state[start_777+38] = self.state[start_NNN_row5+1]
                fake_777.state[start_777+39] = self.state[start_NNN_row5+2]
                fake_777.state[start_777+40] = self.state[end_NNN_row5-1]
                #fake_777.state[start_777+41] = self.state[end_NNN_row5]

                start_777 += 49
                start_NNN += (self.size * self.size)

            fake_777.sanity_check()

            # Group LR centers (in turn groups FB)
            fake_777.print_cube()
            log.warning("fake_777 kociemba: %s" % fake_777.get_kociemba_string(True))
            fake_777.lt_init()
            fake_777.group_centers_guts(oblique_edges_only=True)
            #fake_777.group_centers_guts()
            fake_777.print_cube()

            # Apply the 7x7x7 solution to our cube
            half_size = str(int(self.size/2) - 1)
            wide_size = str(int(half_size) - 1 - center_orbit_id)
            #self.print_cube()
            wide_size = '2'
            log.warning("half_size %s, wide_size %s" % (half_size, wide_size))

            for step in fake_777.solution:
                if step.startswith("3"):
                    self.rotate(half_size + step[1:])
                elif "w" in step:
                    self.rotate(wide_size + step)
                else:
                    self.rotate(step)
            fake_777 = None
            log.warning("%d/%d: end of orbit" % (center_orbit_id, x))
            self.print_cube()

    def group_centers_guts(self):
        self.solve_inside_777()

        # TODO: now reduce centers to a 5x5x5 and solve via the 5x5x5 solver

        # dwalton here now
        self.print_cube()
        sys.exit(0)

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
