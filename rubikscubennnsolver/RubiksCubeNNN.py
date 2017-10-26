
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


class RubiksCubeNNN(RubiksCube):

    def phase(self):
        return 'Solve NxNxN'


class RubiksCubeNNNOdd(RubiksCubeNNN):

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

    def pair_edge_orbit_via_555(self, orbit):
        log.warning("pair_edge_orbit_via_555 for %d" % orbit)
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.cpu_mode = self.cpu_mode
        fake_555.lt_init()

        # The corners don't matter so x them out
        x_out_corners = True

        if x_out_corners:
            start_555 = 0

            for x in range(6):
                fake_555.state[start_555+1] = 'x'
                fake_555.state[start_555+5] = 'x'
                fake_555.state[start_555+21] = 'x'
                fake_555.state[start_555+25] = 'x'
                start_555 += 25

        else:
            start_index = 0
            fake_555.state[1] = self.state[start_index+1]
            fake_555.state[5] = self.state[start_index + self.size]
            fake_555.state[21] = self.state[start_index + (self.size * self.size) - self.size + 1]
            fake_555.state[25] = self.state[start_index + (self.size * self.size)]
            start_index += self.size * self.size

            fake_555.state[26] = self.state[start_index+1]
            fake_555.state[30] = self.state[start_index + self.size]
            fake_555.state[46] = self.state[start_index + (self.size * self.size) - self.size + 1]
            fake_555.state[50] = self.state[start_index + (self.size * self.size)]
            start_index += self.size * self.size

            fake_555.state[51] = self.state[start_index+1]
            fake_555.state[55] = self.state[start_index + self.size]
            fake_555.state[71] = self.state[start_index + (self.size * self.size) - self.size + 1]
            fake_555.state[75] = self.state[start_index + (self.size * self.size)]
            start_index += self.size * self.size

            fake_555.state[76] = self.state[start_index+1]
            fake_555.state[80] = self.state[start_index + self.size]
            fake_555.state[96] = self.state[start_index + (self.size * self.size) - self.size + 1]
            fake_555.state[100] = self.state[start_index + (self.size * self.size)]
            start_index += self.size * self.size

            fake_555.state[101] = self.state[start_index+1]
            fake_555.state[105] = self.state[start_index + self.size]
            fake_555.state[121] = self.state[start_index + (self.size * self.size) - self.size + 1]
            fake_555.state[125] = self.state[start_index + (self.size * self.size)]
            start_index += self.size * self.size

            fake_555.state[126] = self.state[start_index+1]
            fake_555.state[130] = self.state[start_index + self.size]
            fake_555.state[146] = self.state[start_index + (self.size * self.size) - self.size + 1]
            fake_555.state[150] = self.state[start_index + (self.size * self.size)]
            start_index += self.size * self.size

        start_index = 1
        half_size = int(ceil(self.size/2))
        log.warning("start_index %s, half_size %s, orbit %s" % (start_index, half_size, orbit))
        #sys.exit(0)

        # dwalton here now
        start_555 = 0
        start_777 = 0

        for x in range(6):
            row1_col1 = start_777 + orbit + 2
            row1_col2 = start_777 + half_size
            row1_col3 = start_777 + self.size - orbit - 1

            row2_col1 = start_777 + ((orbit+1) * self.size) + 1
            row2_col3 = row2_col1 + self.size - 1

            row3_col1 = start_777 + (self.size * (half_size - 1)) + 1
            row3_col3 = row3_col1 + self.size - 1

            row4_col1 = start_777 + (self.size * self.size) - ((orbit+2) * self.size) + 1
            row4_col3 = row4_col1 + self.size - 1

            #row5_col1 = start_777 + (self.size * self.size) - self.size + 1 + orbit
            #row5_col2 = start_777 + (self.size * self.size) - half_size
            #row5_col3 = start_777 + (self.size * self.size) - orbit
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
            # dwalton
            #sys.exit(0)

        '''
        # Upper
        fake_555.state[2] = self.state[start_index + orbit + 1]
        fake_555.state[3] = self.state[start_index + half_size - 1]
        fake_555.state[4] = self.state[start_index + self.size - orbit]

        fake_555.state[6] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[10] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[11] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[15] = self.state[start_index + (self.size * half_size)]

        fake_555.state[16] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[20] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[22] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[23] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[24] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size


        # Left
        fake_555.state[27] = self.state[start_index + orbit + 1]
        fake_555.state[28] = self.state[start_index + half_size]
        fake_555.state[29] = self.state[start_index + self.size - orbit]

        fake_555.state[31] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[35] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[36] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[40] = self.state[start_index + (self.size * half_size)]

        fake_555.state[41] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[45] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[47] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[48] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[49] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size

        # Front
        fake_555.state[52] = self.state[start_index + orbit + 1]
        fake_555.state[53] = self.state[start_index + half_size]
        fake_555.state[54] = self.state[start_index + self.size - orbit]

        fake_555.state[56] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[60] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[61] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[65] = self.state[start_index + (self.size * half_size)]

        fake_555.state[66] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[70] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[72] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[73] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[74] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size

        # Right
        fake_555.state[77] = self.state[start_index + orbit + 1]
        fake_555.state[78] = self.state[start_index + half_size]
        fake_555.state[79] = self.state[start_index + self.size - orbit]

        fake_555.state[81] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[85] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[86] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[90] = self.state[start_index + (self.size * half_size)]

        fake_555.state[91] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[95] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[97] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[98] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[99] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size

        # Back
        fake_555.state[102] = self.state[start_index + orbit + 1]
        fake_555.state[103] = self.state[start_index + half_size]
        fake_555.state[104] = self.state[start_index + self.size - orbit]

        fake_555.state[106] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[110] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[111] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[115] = self.state[start_index + (self.size * half_size)]

        fake_555.state[116] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[120] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[122] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[123] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[124] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size


        # Down
        fake_555.state[127] = self.state[start_index + orbit + 1]
        fake_555.state[128] = self.state[start_index + half_size]
        fake_555.state[129] = self.state[start_index + self.size - orbit]

        fake_555.state[131] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[135] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[136] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[140] = self.state[start_index + (self.size * half_size)]

        fake_555.state[141] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[145] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[147] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[148] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[149] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size
        '''

        self.print_cube()
        fake_555.print_cube()
        fake_555.sanity_check()
        fake_555.avoid_pll = False
        fake_555.group_edges()

        wide_str = str(orbit + 1)
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

            #log.warning("fake_555 step %s" % step)
            self.rotate(step)

    def group_edges(self):

        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        # TODO - we need to tell both pair_inside_edges_via_444() and pair_edge_orbit_via_555() to
        # avoid PLL

        # How many orbits of edges does this cube have?
        orbits = int((self.size/2) - 1)

        # Work your way from inside to outside and pair them via the 5x5x5 solver
        for orbit in reversed(list(range(1, orbits))):
            self.pair_edge_orbit_via_555(orbit)

        self.solution.append('EDGES_GROUPED')
        log.info("Edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()


class RubiksCubeNNNEven(RubiksCubeNNN):

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

    def solve_inside_777(self):
        fake_777 = RubiksCube777(solved_7x7x7, 'URFDLB')

        for index in range(1, 295):
            fake_777.state[index] = 'x'
        fake_777.cpu_mode = self.cpu_mode

        start_777 = 0
        start_NNN = 0

        for x in range(6):
            start_NNN_row1 = int(start_NNN + (((self.size/2) - 3) * self.size) + (self.size/2) - 2)
            start_NNN_row2 = start_NNN_row1 + self.size
            start_NNN_row3 = start_NNN_row2 + self.size
            start_NNN_row4 = start_NNN_row3 + self.size + self.size
            start_NNN_row5 = start_NNN_row4 + self.size

            log.warning("%d: start_NNN_row1 %d" % (x, start_NNN_row1))
            log.warning("%d: start_NNN_row2 %d" % (x, start_NNN_row2))
            log.warning("%d: start_NNN_row3 %d" % (x, start_NNN_row3))
            log.warning("%d: start_NNN_row4 %d" % (x, start_NNN_row4))
            log.warning("%d: start_NNN_row5 %d" % (x, start_NNN_row5))

            fake_777.state[start_777+9] = self.state[start_NNN_row1]
            fake_777.state[start_777+10] = self.state[start_NNN_row1+1]
            fake_777.state[start_777+11] = self.state[start_NNN_row1+2]
            fake_777.state[start_777+12] = self.state[start_NNN_row1+4]
            fake_777.state[start_777+13] = self.state[start_NNN_row1+5]

            fake_777.state[start_777+16] = self.state[start_NNN_row2]
            fake_777.state[start_777+17] = self.state[start_NNN_row2+1]
            fake_777.state[start_777+18] = self.state[start_NNN_row2+2]
            fake_777.state[start_777+19] = self.state[start_NNN_row2+4]
            fake_777.state[start_777+20] = self.state[start_NNN_row2+5]

            fake_777.state[start_777+23] = self.state[start_NNN_row3]
            fake_777.state[start_777+24] = self.state[start_NNN_row3+1]
            fake_777.state[start_777+25] = self.state[start_NNN_row3+2]
            fake_777.state[start_777+26] = self.state[start_NNN_row3+4]
            fake_777.state[start_777+27] = self.state[start_NNN_row3+5]

            fake_777.state[start_777+30] = self.state[start_NNN_row4]
            fake_777.state[start_777+31] = self.state[start_NNN_row4+1]
            fake_777.state[start_777+32] = self.state[start_NNN_row4+2]
            fake_777.state[start_777+33] = self.state[start_NNN_row4+4]
            fake_777.state[start_777+34] = self.state[start_NNN_row4+5]

            fake_777.state[start_777+37] = self.state[start_NNN_row5]
            fake_777.state[start_777+38] = self.state[start_NNN_row5+1]
            fake_777.state[start_777+39] = self.state[start_NNN_row5+2]
            fake_777.state[start_777+40] = self.state[start_NNN_row5+4]
            fake_777.state[start_777+41] = self.state[start_NNN_row5+5]

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

    def group_centers_guts(self):
        self.make_plus_sign()
        self.solve_inside_777()

        #self.experiment_777_part1()

        #if not self.centers_solved():
        #    self.experiment_777_part2()

        # TODO: now reduce centers to a 5x5x5 and solve via the 5x5x5 solver
        self.print_cube()
        self.print_solution()
        sys.exit(0)

    def pair_inside_edges_via_444(self):
        fake_444 = RubiksCube444(solved_4x4x4, 'URFDLB')
        fake_444.cpu_mode = self.cpu_mode
        fake_444.lt_init()

        # The corners don't matter but it does make troubleshooting easier if they match
        start_index = 0
        fake_444.state[1] = self.state[start_index+1]
        fake_444.state[4] = self.state[start_index + self.size]
        fake_444.state[13] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_444.state[16] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_444.state[17] = self.state[start_index+1]
        fake_444.state[20] = self.state[start_index + self.size]
        fake_444.state[29] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_444.state[32] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_444.state[33] = self.state[start_index+1]
        fake_444.state[36] = self.state[start_index + self.size]
        fake_444.state[45] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_444.state[48] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_444.state[49] = self.state[start_index+1]
        fake_444.state[52] = self.state[start_index + self.size]
        fake_444.state[61] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_444.state[64] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_444.state[65] = self.state[start_index+1]
        fake_444.state[68] = self.state[start_index + self.size]
        fake_444.state[77] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_444.state[80] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_444.state[81] = self.state[start_index+1]
        fake_444.state[84] = self.state[start_index + self.size]
        fake_444.state[93] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_444.state[96] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        # Upper
        half_size = int(self.size/2)
        start_index = 0
        fake_444.state[2] = self.state[start_index + half_size]
        fake_444.state[3] = self.state[start_index + half_size + 1]
        fake_444.state[5] = self.state[start_index + (self.size * (half_size-1)) + 1]
        fake_444.state[8] = self.state[start_index + (self.size * half_size)]
        fake_444.state[9] = self.state[start_index + (self.size * half_size) + 1]
        fake_444.state[12] = self.state[start_index + (self.size * (half_size+1))]
        fake_444.state[14] = self.state[start_index + (self.size * self.size) - half_size]
        fake_444.state[15] = self.state[start_index + (self.size * self.size) - half_size + 1]
        start_index += self.size * self.size

        # Left
        fake_444.state[18] = self.state[start_index + half_size]
        fake_444.state[19] = self.state[start_index + half_size + 1]
        fake_444.state[21] = self.state[start_index + (self.size * (half_size-1)) + 1]
        fake_444.state[24] = self.state[start_index + (self.size * half_size)]
        fake_444.state[25] = self.state[start_index + (self.size * half_size) + 1]
        fake_444.state[28] = self.state[start_index + (self.size * (half_size+1))]
        fake_444.state[30] = self.state[start_index + (self.size * self.size) - half_size]
        fake_444.state[31] = self.state[start_index + (self.size * self.size) - half_size + 1]
        start_index += self.size * self.size

        # Front
        fake_444.state[34] = self.state[start_index + half_size]
        fake_444.state[35] = self.state[start_index + half_size + 1]
        fake_444.state[37] = self.state[start_index + (self.size * (half_size-1)) + 1]
        fake_444.state[40] = self.state[start_index + (self.size * half_size)]
        fake_444.state[41] = self.state[start_index + (self.size * half_size) + 1]
        fake_444.state[44] = self.state[start_index + (self.size * (half_size+1))]
        fake_444.state[46] = self.state[start_index + (self.size * self.size) - half_size]
        fake_444.state[47] = self.state[start_index + (self.size * self.size) - half_size + 1]
        start_index += self.size * self.size

        # Right
        fake_444.state[50] = self.state[start_index + half_size]
        fake_444.state[51] = self.state[start_index + half_size + 1]
        fake_444.state[53] = self.state[start_index + (self.size * (half_size-1)) + 1]
        fake_444.state[56] = self.state[start_index + (self.size * half_size)]
        fake_444.state[57] = self.state[start_index + (self.size * half_size) + 1]
        fake_444.state[60] = self.state[start_index + (self.size * (half_size+1))]
        fake_444.state[62] = self.state[start_index + (self.size * self.size) - half_size]
        fake_444.state[63] = self.state[start_index + (self.size * self.size) - half_size + 1]
        start_index += self.size * self.size

        # Back
        fake_444.state[66] = self.state[start_index + half_size]
        fake_444.state[67] = self.state[start_index + half_size + 1]
        fake_444.state[69] = self.state[start_index + (self.size * (half_size-1)) + 1]
        fake_444.state[72] = self.state[start_index + (self.size * half_size)]
        fake_444.state[73] = self.state[start_index + (self.size * half_size) + 1]
        fake_444.state[76] = self.state[start_index + (self.size * (half_size+1))]
        fake_444.state[78] = self.state[start_index + (self.size * self.size) - half_size]
        fake_444.state[79] = self.state[start_index + (self.size * self.size) - half_size + 1]
        start_index += self.size * self.size

        # Down
        fake_444.state[82] = self.state[start_index + half_size]
        fake_444.state[83] = self.state[start_index + half_size + 1]
        fake_444.state[85] = self.state[start_index + (self.size * (half_size-1)) + 1]
        fake_444.state[88] = self.state[start_index + (self.size * half_size)]
        fake_444.state[89] = self.state[start_index + (self.size * half_size) + 1]
        fake_444.state[92] = self.state[start_index + (self.size * (half_size+1))]
        fake_444.state[94] = self.state[start_index + (self.size * self.size) - half_size]
        fake_444.state[95] = self.state[start_index + (self.size * self.size) - half_size + 1]
        start_index += self.size * self.size

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

        #log.info("Inside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def pair_edge_orbit_via_555(self, orbit):
        log.warning("pair_edge_orbit_via_555 for %d" % orbit)
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.cpu_mode = self.cpu_mode
        fake_555.lt_init()

        # The corners don't matter but it does make troubleshooting easier if they match
        start_index = 0
        fake_555.state[1] = self.state[start_index+1]
        fake_555.state[5] = self.state[start_index + self.size]
        fake_555.state[21] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_555.state[25] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_555.state[26] = self.state[start_index+1]
        fake_555.state[30] = self.state[start_index + self.size]
        fake_555.state[46] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_555.state[50] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_555.state[51] = self.state[start_index+1]
        fake_555.state[55] = self.state[start_index + self.size]
        fake_555.state[71] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_555.state[75] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_555.state[76] = self.state[start_index+1]
        fake_555.state[80] = self.state[start_index + self.size]
        fake_555.state[96] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_555.state[100] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_555.state[101] = self.state[start_index+1]
        fake_555.state[105] = self.state[start_index + self.size]
        fake_555.state[121] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_555.state[125] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        fake_555.state[126] = self.state[start_index+1]
        fake_555.state[130] = self.state[start_index + self.size]
        fake_555.state[146] = self.state[start_index + (self.size * self.size) - self.size + 1]
        fake_555.state[150] = self.state[start_index + (self.size * self.size)]
        start_index += self.size * self.size

        half_size = int(self.size/2)

        # dwalton this is the even one for comparison
        # Upper
        start_index = 0
        fake_555.state[2] = self.state[start_index + orbit + 1]
        fake_555.state[3] = self.state[start_index + half_size]
        fake_555.state[4] = self.state[start_index + self.size - orbit]

        fake_555.state[6] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[10] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[11] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[15] = self.state[start_index + (self.size * half_size)]

        fake_555.state[16] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[20] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[22] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[23] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[24] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size


        # Left
        fake_555.state[27] = self.state[start_index + orbit + 1]
        fake_555.state[28] = self.state[start_index + half_size]
        fake_555.state[29] = self.state[start_index + self.size - orbit]

        fake_555.state[31] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[35] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[36] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[40] = self.state[start_index + (self.size * half_size)]

        fake_555.state[41] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[45] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[47] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[48] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[49] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size

        # Front
        fake_555.state[52] = self.state[start_index + orbit + 1]
        fake_555.state[53] = self.state[start_index + half_size]
        fake_555.state[54] = self.state[start_index + self.size - orbit]

        fake_555.state[56] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[60] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[61] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[65] = self.state[start_index + (self.size * half_size)]

        fake_555.state[66] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[70] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[72] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[73] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[74] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size

        # Right
        fake_555.state[77] = self.state[start_index + orbit + 1]
        fake_555.state[78] = self.state[start_index + half_size]
        fake_555.state[79] = self.state[start_index + self.size - orbit]

        fake_555.state[81] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[85] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[86] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[90] = self.state[start_index + (self.size * half_size)]

        fake_555.state[91] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[95] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[97] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[98] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[99] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size

        # Back
        fake_555.state[102] = self.state[start_index + orbit + 1]
        fake_555.state[103] = self.state[start_index + half_size]
        fake_555.state[104] = self.state[start_index + self.size - orbit]

        fake_555.state[106] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[110] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[111] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[115] = self.state[start_index + (self.size * half_size)]

        fake_555.state[116] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[120] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[122] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[123] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[124] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size


        # Down
        fake_555.state[127] = self.state[start_index + orbit + 1]
        fake_555.state[128] = self.state[start_index + half_size]
        fake_555.state[129] = self.state[start_index + self.size - orbit]

        fake_555.state[131] = self.state[start_index + (orbit * self.size) + 1]
        fake_555.state[135] = self.state[start_index + (orbit * self.size) + self.size]

        # The middle of the edge so orbit doesn't matter
        fake_555.state[136] = self.state[start_index + (self.size * (half_size - 1)) + 1]
        fake_555.state[140] = self.state[start_index + (self.size * half_size)]

        fake_555.state[141] = self.state[start_index + (self.size * self.size) - (orbit * self.size) - self.size + 1]
        fake_555.state[145] = self.state[start_index + (self.size * self.size) - (orbit * self.size)]

        fake_555.state[147] = self.state[start_index + (self.size * self.size) - self.size + 1 + orbit]
        fake_555.state[148] = self.state[start_index + (self.size * self.size) - half_size]
        fake_555.state[149] = self.state[start_index + (self.size * self.size) - orbit]
        start_index += self.size * self.size

        fake_555.sanity_check()
        self.print_cube()
        fake_555.print_cube()
        fake_555.avoid_pll = False
        fake_555.group_edges()

        wide_str = str(orbit + 1)
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

            #log.warning("fake_555 step %s" % step)
            self.rotate(step)

    def group_edges(self):

        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        # TODO - we need to tell both pair_inside_edges_via_444() and pair_edge_orbit_via_555() to
        # avoid PLL

        # Pair the inside edges via fake 4x4x4
        self.pair_inside_edges_via_444()

        # How many orbits of edges does this cube have?
        orbits = int((self.size/2) - 1)

        # The inside orbit was paired above via pair_inside_edges_via_444()
        # For all of the rest work your way from inside to outside and pair
        # them via the 5x5x5 solver.
        for orbit in reversed(list(range(1, orbits))):
            self.pair_edge_orbit_via_555(orbit)

        self.solution.append('EDGES_GROUPED')
        log.info("Edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
