
from pprint import pformat
from rubikscubennnsolver import RubiksCube, ImplementThis
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_4x4x4
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_5x5x5
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_6x6x6
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_7x7x7
import logging
import sys

log = logging.getLogger(__name__)


class RubiksCubeNNNOdd(RubiksCube):

    def __init__(self, state, order,  colormap, debug=False):
        RubiksCube.__init__(self, state, order, colormap)

        if debug:
            log.setLevel(logging.DEBUG)

    def phase(self):
        return 'Solve NxNxN'


class RubiksCubeNNNEven(RubiksCube):

    def __init__(self, state, order, colormap, debug=False):
        RubiksCube.__init__(self, state, order, colormap)

        if debug:
            log.setLevel(logging.DEBUG)

    def phase(self):
        return 'Solve NxNxN'

    def group_centers_guts(self):
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

                log.info("%d: start_NNN_row1 %d, row2 %d, row3 %d row4 %d" %
                    (x, start_NNN_row1, start_NNN_row2, start_NNN_row3, start_NNN_row4))

                fake_666.state[start_666+9] = self.state[start_NNN_row1+1 - (center_orbit_id * self.size)]
                fake_666.state[start_666+10] = self.state[start_NNN_row1+2 - (center_orbit_id * self.size)]

                fake_666.state[start_666+14] = self.state[start_NNN_row2 - center_orbit_id]
                fake_666.state[start_666+15] = self.state[start_NNN_row2+1]
                fake_666.state[start_666+16] = self.state[start_NNN_row2+2]
                fake_666.state[start_666+17] = self.state[start_NNN_row2+3 + center_orbit_id]

                fake_666.state[start_666+20] = self.state[start_NNN_row3 - center_orbit_id]
                fake_666.state[start_666+21] = self.state[start_NNN_row3+1]
                fake_666.state[start_666+22] = self.state[start_NNN_row3+2]
                fake_666.state[start_666+23] = self.state[start_NNN_row3+3 + center_orbit_id]

                fake_666.state[start_666+27] = self.state[start_NNN_row4+1 + (center_orbit_id * self.size)]
                fake_666.state[start_666+28] = self.state[start_NNN_row4+2 + (center_orbit_id * self.size)]
                start_666 += 36
                start_NNN += (self.size * self.size)

            # Group LR centers (in turn groups FB)
            fake_666.print_cube()
            fake_666.lt_init()
            fake_666.group_centers_guts(oblique_edges_only=True)
            fake_666.print_solution()
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

        self.print_cube()
        log.info("Big plus sign formed, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

        center_orbit_count = ((self.size/2) - 3)/2
        log.info("center_orbit_count %d" % center_orbit_count)

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
                start_NNN_row2 = start_NNN_row1 + self.size
                start_NNN_row3 = start_NNN_row2 + self.size
                start_NNN_row4 = start_NNN_row3 + self.size + self.size
                start_NNN_row5 = start_NNN_row4 + self.size
                offset_from_edge = start_NNN_row1 % self.size

                end_NNN_row1 = (start_NNN_row1 - offset_from_edge) + self.size - offset_from_edge + 1
                end_NNN_row2 = end_NNN_row1 + self.size
                end_NNN_row3 = end_NNN_row2 + self.size
                end_NNN_row4 = end_NNN_row3 + self.size + self.size
                end_NNN_row5 = end_NNN_row4 + self.size

                log.info("%d: offset_from_edge %s" % (x, offset_from_edge))
                log.info("%d: start_NNN_row1 %d, end_NNN_row1 %d" % (x, start_NNN_row1, end_NNN_row1))
                log.info("%d: start_NNN_row2 %d, end_NNN_row2 %d" % (x, start_NNN_row2, end_NNN_row2))
                log.info("%d: start_NNN_row3 %d, end_NNN_row3 %d" % (x, start_NNN_row3, end_NNN_row3))
                log.info("%d: start_NNN_row4 %d, end_NNN_row4 %d" % (x, start_NNN_row4, end_NNN_row4))
                log.info("%d: start_NNN_row5 %d, end_NNN_row5 %d" % (x, start_NNN_row5, end_NNN_row5))

                fake_777.state[start_777+9] = self.state[start_NNN_row1+0]
                fake_777.state[start_777+10] = self.state[start_NNN_row1+1] 
                fake_777.state[start_777+11] = self.state[start_NNN_row1+2]
                fake_777.state[start_777+12] = self.state[end_NNN_row1-1]
                fake_777.state[start_777+13] = self.state[end_NNN_row1]

                fake_777.state[start_777+16] = self.state[start_NNN_row2+0]
                fake_777.state[start_777+17] = self.state[start_NNN_row2+1]
                fake_777.state[start_777+18] = self.state[start_NNN_row2+2]
                fake_777.state[start_777+19] = self.state[end_NNN_row2-1]
                fake_777.state[start_777+20] = self.state[end_NNN_row2]

                fake_777.state[start_777+23] = self.state[start_NNN_row3+0]
                fake_777.state[start_777+24] = self.state[start_NNN_row3+1]
                fake_777.state[start_777+25] = self.state[start_NNN_row3+2]
                fake_777.state[start_777+26] = self.state[end_NNN_row3-1]
                fake_777.state[start_777+27] = self.state[end_NNN_row3]

                fake_777.state[start_777+30] = self.state[start_NNN_row4+0]
                fake_777.state[start_777+31] = self.state[start_NNN_row4+1]
                fake_777.state[start_777+32] = self.state[start_NNN_row4+2]
                fake_777.state[start_777+33] = self.state[end_NNN_row4-1]
                fake_777.state[start_777+34] = self.state[end_NNN_row4]

                fake_777.state[start_777+37] = self.state[start_NNN_row5+0]
                fake_777.state[start_777+38] = self.state[start_NNN_row5+1]
                fake_777.state[start_777+39] = self.state[start_NNN_row5+2]
                fake_777.state[start_777+40] = self.state[end_NNN_row5-1]
                fake_777.state[start_777+41] = self.state[end_NNN_row5]

                start_777 += 49
                start_NNN += (self.size * self.size)

                #fake_777.print_cube()
                #sys.exit(0)

            # dwalton here now
            # Group LR centers (in turn groups FB)
            fake_777.print_cube()
            fake_777.lt_init()
            #fake_777.group_centers_guts(oblique_edges_only=True)
            fake_777.group_centers_guts()
            #fake_777.print_solution()
            fake_777.print_cube()

            # Apply the 7x7x7 solution to our cube
            half_size = str(int(self.size/2) - 1)
            wide_size = str(int(half_size) - 1 - center_orbit_id)
            #half_size = '3'
            #wide_size = '2'
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

            self.print_cube()
            #self.print_cube_layout()
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

        log.info("Edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
