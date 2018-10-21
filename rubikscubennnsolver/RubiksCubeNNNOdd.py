
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_777
from rubikscubennnsolver.RubiksCubeNNNOddEdges import RubiksCubeNNNOddEdges
from math import ceil
import logging
import sys

log = logging.getLogger(__name__)

solved_999 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

solved_111111 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

solved_131313 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

solved_151515 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

solved_171717 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'


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

    def phase(self):
        return 'Solve Odd NxNxN'

    def get_fake_777(self):
        if self.fake_777 is None:
            self.fake_777 = RubiksCube777(solved_777, 'URFDLB')
            self.fake_777.cpu_mode = self.cpu_mode
            self.fake_777.lt_init()
            self.fake_777.enable_print_cube = False
        else:
            self.fake_777.re_init()
        return self.fake_777

    def stage_or_solve_inside_777(self, center_orbit_id, max_center_orbits, width, cycle, max_cycle, action):
        fake_777 = self.get_fake_777()

        for index in range(1, 295):
            fake_777.state[index] = 'x'

        start_777 = 0
        start_NNN = 0
        row0_midpoint = ceil(self.size/2)

        log.info("%s: Start center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s" %\
            (self, center_orbit_id, max_center_orbits, width, cycle, max_cycle))

        side_name = {
            0 : 'U',
            1 : 'L',
            2 : 'F',
            3 : 'R',
            4 : 'B',
            5 : 'D',
        }

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

            #log.info("%d: start_NNN_row1 %d, mid_NNN_row1 %d, end_NNN_row1 %d" % (x, start_NNN_row1, mid_NNN_row1, end_NNN_row1))
            #log.info("%d: start_NNN_row2 %d, mid_NNN_row2 %d, end_NNN_row2 %d" % (x, start_NNN_row2, mid_NNN_row2, end_NNN_row2))
            #log.info("%d: start_NNN_row3 %d, mid_NNN_row3 %d, end_NNN_row3 %d" % (x, start_NNN_row3, mid_NNN_row3, end_NNN_row3))
            #log.info("%d: start_NNN_row4 %d, mid_NNN_row4 %d, end_NNN_row4 %d" % (x, start_NNN_row4, mid_NNN_row4, end_NNN_row4))
            #log.info("%d: start_NNN_row5 %d, mid_NNN_row5 %d, end_NNN_row5 %d" % (x, start_NNN_row5, mid_NNN_row5, end_NNN_row5))

            #log.info("%d: row1 %d, %d, %d, %d, %d" % (x, row1_col1, row1_col2, row1_col3, row1_col4, row1_col5))
            #log.info("%d: row2 %d, %d, %d, %d, %d" % (x, row2_col1, row2_col2, row2_col3, row2_col4, row2_col5))
            #log.info("%d: row3 %d, %d, %d, %d, %d" % (x, row3_col1, row3_col2, row3_col3, row3_col4, row3_col5))
            #log.info("%d: row4 %d, %d, %d, %d, %d" % (x, row4_col1, row4_col2, row4_col3, row4_col4, row4_col5))
            #log.info("%d: row5 %d, %d, %d, %d, %d\n\n" % (x, row5_col1, row5_col2, row5_col3, row5_col4, row5_col5))

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
                fake_777.state[start_777+9] = side_name[x]
                fake_777.state[start_777+10] = self.state[row1_col2]
                fake_777.state[start_777+11] = self.state[row1_col3]
                fake_777.state[start_777+12] = self.state[row1_col4]
                #fake_777.state[start_777+13] = self.state[row1_col5]
                fake_777.state[start_777+13] = side_name[x]

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
                fake_777.state[start_777+37] = side_name[x]
                fake_777.state[start_777+38] = self.state[row5_col2]
                fake_777.state[start_777+39] = self.state[row5_col3]
                fake_777.state[start_777+40] = self.state[row5_col4]
                #fake_777.state[start_777+41] = self.state[row5_col5]
                fake_777.state[start_777+41] = side_name[x]

            start_777 += 49
            start_NNN += (self.size * self.size)

        #fake_777.sanity_check()
        fake_777.print_cube()

        # Apply the 7x7x7 solution to our cube
        half_size = str(ceil(self.size/2) - 1 - cycle)
        wide_size = str(ceil(self.size/2) - 2 - center_orbit_id)

        if action == "stage_UD_centers":
            fake_777.stage_UD_centers()
        elif action == "stage_LR_centers":
            fake_777.stage_LR_centers()
        elif action == "LR_centers_vertical_bars":
            fake_777.LR_centers_vertical_bars()
        elif action == "UD_centers_vertical_bars":
            fake_777.UD_centers_vertical_bars()
        elif action == "solve_centers":
            fake_777.group_centers_guts()
        else:
            raise Exception("Invalid action %s" % action)

        for step in fake_777.solution:
            if step.startswith('COMMENT'):
                self.solution.append(step)
            elif step.startswith("3"):
                self.rotate(half_size + step[1:])
            elif "w" in step:
                self.rotate(wide_size + step)
            else:
                self.rotate(step)

        self.print_cube()
        log.info("%s: End center_orbit_id, %d, max_center_orbits %s, width %s, cycle %s, max_cycle %s" %\
            (self, center_orbit_id, max_center_orbits, width, cycle, max_cycle))

    def group_centers_guts(self):

        max_center_orbits = int((self.size - 3) / 2) - 2

        # Stage all UD centers
        for center_orbit_id in range(max_center_orbits+1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5)/2)

            for cycle in range(max_cycle+1):
                self.stage_or_solve_inside_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle, "stage_UD_centers")

        self.print_cube()
        log.warning("%s: UD centers are staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Stage all LR centers
        for center_orbit_id in range(max_center_orbits+1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5)/2)

            for cycle in range(max_cycle+1):
                self.stage_or_solve_inside_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle, "stage_LR_centers")

        self.print_cube()
        log.warning("%s: LR centers are staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # I tried this once it didn't work...if it had next step would have
        # been to do the same for UD (make them vertical bars)
        '''
        # LR centers to vertical bars
        for center_orbit_id in range(max_center_orbits+1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5)/2)

            for cycle in range(max_cycle+1):
                self.stage_or_solve_inside_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle, "LR_centers_vertical_bars")

        self.print_cube()
        log.warning("%s: LR centers are vertical bars, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        '''

        # Solve all centers
        for center_orbit_id in range(max_center_orbits+1):
            width = self.size - 2 - ((max_center_orbits - center_orbit_id) * 2)
            max_cycle = int((width - 5)/2)

            for cycle in range(max_cycle+1):
                self.stage_or_solve_inside_777(center_orbit_id, max_center_orbits, width, cycle, max_cycle, "solve_centers")

        self.print_cube()
        log.info("%s: centers are solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
