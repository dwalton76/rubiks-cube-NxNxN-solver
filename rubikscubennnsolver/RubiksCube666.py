
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis, steps_cancel_out
from rubikscubennnsolver.RubiksCube555 import RubiksCube555
from rubikscubennnsolver.RubiksSide import Side, SolveError
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)

# "Uw2": ["U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2", "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2", "F", "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2", "R", "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2", "B", "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2", "D", "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2"],

moves_6x6x6 = ("U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2",
               "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",
               "F" , "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",
               "R" , "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",
               "B" , "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",
               "D" , "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2")



class RubiksCube666(RubiksCube):

    def lookup_table_666_UD_inner_x_centers_stage(self):
        state = 'xxxxx' + self.state[15] + self.state[16] + 'xx' + self.state[21] + self.state[22]  + 'xxxxx' +\
                'xxxxx' + self.state[51] + self.state[52] + 'xx' + self.state[57] + self.state[58]  + 'xxxxx' +\
                'xxxxx' + self.state[87] + self.state[88] + 'xx' + self.state[93] + self.state[94]  + 'xxxxx' +\
                'xxxxx' + self.state[123] + self.state[124] + 'xx' + self.state[129] + self.state[130]  + 'xxxxx' +\
                'xxxxx' + self.state[159] + self.state[160] + 'xx' + self.state[165] + self.state[166]  + 'xxxxx' +\
                'xxxxx' + self.state[195] + self.state[196] + 'xx' + self.state[201] + self.state[202]  + 'xxxxx'
        state = state.replace('U', 'U').replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')
        filename = 'lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.warning("UD inner x-centers-stage %s: FOUND entry %d steps in (%s), %s" %\
                    (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                for step in steps:
                    self.rotate(step)
            else:
                raise SolveError("UD inner x-centers-stage could not find %s" % state)

    def lookup_table_666_LR_inner_x_centers_stage(self):
        state = 'xxxxx' + self.state[15] + self.state[16] + 'xx' + self.state[21] + self.state[22]  + 'xxxxx' +\
                'xxxxx' + self.state[51] + self.state[52] + 'xx' + self.state[57] + self.state[58]  + 'xxxxx' +\
                'xxxxx' + self.state[87] + self.state[88] + 'xx' + self.state[93] + self.state[94]  + 'xxxxx' +\
                'xxxxx' + self.state[123] + self.state[124] + 'xx' + self.state[129] + self.state[130]  + 'xxxxx' +\
                'xxxxx' + self.state[159] + self.state[160] + 'xx' + self.state[165] + self.state[166]  + 'xxxxx' +\
                'xxxxx' + self.state[195] + self.state[196] + 'xx' + self.state[201] + self.state[202]  + 'xxxxx'
        state = state.replace('U', 'x').replace('L', 'L').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')
        filename = 'lookup-table-6x6x6-step30-LR-inner-x-centers-stage.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.warning("LR inner x-centers-stage %s: FOUND entry %d steps in (%s), %s" %\
                    (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                for step in steps:
                    self.rotate(step)
            else:
                raise SolveError("LR inner x-centers-stage could not find %s" % state)

    def lookup_table_666_UD_oblique_edge_pairing(self):
        state = 'x' + self.state[9] + self.state[10] + 'x' +\
                self.state[14] + 'xx' + self.state[17] +\
                self.state[20] + 'xx' + self.state[23] +\
                'x' + self.state[27] + self.state[28] + 'x' +\
               'x' + self.state[45] + self.state[46] + 'x' +\
                self.state[50] + 'xx' + self.state[53] +\
                self.state[56] + 'xx' + self.state[59] +\
                'x' + self.state[63] + self.state[64] + 'x' +\
               'x' + self.state[81] + self.state[82] + 'x' +\
                self.state[86] + 'xx' + self.state[89] +\
                self.state[92] + 'xx' + self.state[95] +\
                'x' + self.state[99] + self.state[100] + 'x' +\
               'x' + self.state[117] + self.state[118] + 'x' +\
                self.state[122] + 'xx' + self.state[125] +\
                self.state[128] + 'xx' + self.state[131] +\
                'x' + self.state[135] + self.state[136] + 'x' +\
               'x' + self.state[153] + self.state[154] + 'x' +\
                self.state[158] + 'xx' + self.state[161] +\
                self.state[164] + 'xx' + self.state[167] +\
                'x' + self.state[171] + self.state[172] + 'x' +\
               'x' + self.state[189] + self.state[190] + 'x' +\
                self.state[194] + 'xx' + self.state[197] +\
                self.state[200] + 'xx' + self.state[203] +\
                'x' + self.state[207] + self.state[208] + 'x'

        state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')
        filename = 'lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.warning("UD oblique-edge-pairing-stage %s: FOUND entry %d steps in (%s), %s" %\
                    (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))

                # TODO we only need to do the steps needed to get the UD oblique edges paired, if we follow the
                # steps all the way through we will also stage them to sides UD.  Having them staged does tend
                # to make the IDA for fake_555.lookup_table_555_UD_centers_stage go very quickly though so it
                # may be better to follow these through the whole way after all...investigate.
                for step in steps:
                    self.rotate(step)
                return True

        return False

    def get_lookup_table_666_UD_oblique_edge_pairing_left_only(self):
        state = 'x' + self.state[9] + 'xx' +\
                'xxx' + self.state[17] +\
                self.state[20] + 'xxx' +\
                'xx' + self.state[28] + 'x' +\
                'x' + self.state[45] + 'xx' +\
                'xxx' + self.state[53] +\
                self.state[56] + 'xxx' +\
                'xx' + self.state[64] + 'x' +\
                'x' + self.state[81] + 'xx' +\
                'xxx' + self.state[89] +\
                self.state[92] + 'xxx' +\
                'xx' + self.state[100] + 'x' +\
                'x' + self.state[117] + 'xx' +\
                'xxx' + self.state[125] +\
                self.state[128] + 'xxx' +\
                'xx' + self.state[136] + 'x' +\
                'x' + self.state[153] + 'xx' +\
                'xxx' + self.state[161] +\
                self.state[164] + 'xxx' +\
                'xx' + self.state[172] + 'x' +\
                'x' + self.state[189] + 'xx' +\
                'xxx' + self.state[197] +\
                self.state[200] + 'xxx' +\
                'xx' + self.state[208] + 'x'

        state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')
        filename = 'lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                #log.warning("UD oblique-edge-pairing-left-only-stage %s: FOUND entry %d steps in (%s), %s" %\
                #    (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                return len(steps)
            else:
                raise SolveError("get_lookup_table_666_UD_oblique_edge_pairing_left_only could not find %s" % state)

    def get_lookup_table_666_UD_oblique_edge_pairing_right_only(self):
        state = 'xx' + self.state[10] + 'x' +\
                self.state[14] + 'xxx' +\
                'xxx' + self.state[23] +\
                'x' + self.state[27] + 'xx' +\
                'xx' + self.state[46] + 'x' +\
                self.state[50] + 'xxx' +\
                'xxx' + self.state[59] +\
                'x' + self.state[63] + 'xx' +\
                'xx' + self.state[82] + 'x' +\
                self.state[86] + 'xxx' +\
                'xxx' + self.state[95] +\
                'x' + self.state[99] + 'xx' +\
                'xx' + self.state[118] + 'x' +\
                self.state[122] + 'xxx' +\
                'xxx' + self.state[131] +\
                'x' + self.state[135] + 'xx' +\
                'xx' + self.state[154] + 'x' +\
                self.state[158] + 'xxx' +\
                'xxx' + self.state[167] +\
                'x' + self.state[171] + 'xx' +\
                'xx' + self.state[190] + 'x' +\
                self.state[194] + 'xxx' +\
                'xxx' + self.state[203] +\
                'x' + self.state[207] + 'xx'

        state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')
        filename = 'lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                #log.warning("UD oblique-edge-pairing-left-only-stage %s: FOUND entry %d steps in (%s), %s" %\
                #    (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                return len(steps)
            else:
                raise SolveError("get_lookup_table_666_UD_oblique_edge_pairing_right_only could not find %s" % state)

    def ida_search_UD_oblique_edge_pairing(self, cost_to_here, threshold, prev_step, prev_state, prev_solution):

        for step in moves_6x6x6:

            # If this step cancels out the previous step then don't bother with this branch
            if steps_cancel_out(prev_step, step):
                continue

            # These would break up the staged UD inner x-centers
            if step in ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'"):
                continue

            self.state = copy(prev_state)
            self.solution = copy(prev_solution)
            self.rotate(step)

            # Do we have the cube in a state where there is a match in the lookup table?
            if self.lookup_table_666_UD_oblique_edge_pairing():
                return True

            cost_to_goal = max(self.get_lookup_table_666_UD_oblique_edge_pairing_left_only(),
                               self.get_lookup_table_666_UD_oblique_edge_pairing_right_only())

            if (cost_to_here + 1 + cost_to_goal) > threshold:
                #log.info("prune IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                #    (step1, cost_to_here, cost_to_goal, threshold))
                continue

            state_end_of_this_step = copy(self.state)
            solution_end_of_this_step = copy(self.solution)

            if self.ida_search_UD_oblique_edge_pairing(cost_to_here + 1, threshold, step, state_end_of_this_step, solution_end_of_this_step):
                return True

        return False

    def populate_fake_555_for_UD(self, fake_555):
        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # The UD t-centers are staged
        fake_555.state[8] = "U"
        fake_555.state[12] = "U"
        fake_555.state[13] = "U"
        fake_555.state[14] = "U"
        fake_555.state[18] = "U"

        fake_555.state[133] = "U"
        fake_555.state[137] = "U"
        fake_555.state[138] = "U"
        fake_555.state[139] = "U"
        fake_555.state[143] = "U"

        # Upper
        if self.state[8] in ("U", "D"):
            fake_555.state[7] = "U"
        if self.state[11] in ("U", "D"):
            fake_555.state[9] = "U"
        if self.state[26] in ("U", "D"):
            fake_555.state[17] = "U"
        if self.state[29] in ("U", "D"):
            fake_555.state[19] = "U"

        # Left
        if self.state[44] in ("U", "D"):
            fake_555.state[32] = "U"
        if self.state[47] in ("U", "D"):
            fake_555.state[34] = "U"
        if self.state[62] in ("U", "D"):
            fake_555.state[42] = "U"
        if self.state[65] in ("U", "D"):
            fake_555.state[44] = "U"

        # Front
        if self.state[80] in ("U", "D"):
            fake_555.state[57] = "U"
        if self.state[83] in ("U", "D"):
            fake_555.state[59] = "U"
        if self.state[98] in ("U", "D"):
            fake_555.state[67] = "U"
        if self.state[101] in ("U", "D"):
            fake_555.state[69] = "U"

        # Right
        if self.state[116] in ("U", "D"):
            fake_555.state[82] = "U"
        if self.state[119] in ("U", "D"):
            fake_555.state[84] = "U"
        if self.state[134] in ("U", "D"):
            fake_555.state[92] = "U"
        if self.state[137] in ("U", "D"):
            fake_555.state[94] = "U"

        # Back
        if self.state[152] in ("U", "D"):
            fake_555.state[107] = "U"
        if self.state[155] in ("U", "D"):
            fake_555.state[109] = "U"
        if self.state[170] in ("U", "D"):
            fake_555.state[117] = "U"
        if self.state[173] in ("U", "D"):
            fake_555.state[119] = "U"

        # Down
        if self.state[188] in ("U", "D"):
            fake_555.state[132] = "U"
        if self.state[191] in ("U", "D"):
            fake_555.state[134] = "U"
        if self.state[206] in ("U", "D"):
            fake_555.state[142] = "U"
        if self.state[209] in ("U", "D"):
            fake_555.state[144] = "U"

    def populate_fake_555_for_LR(self, fake_555):
        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # The LR t-centers are staged
        fake_555.state[33] = "L"
        fake_555.state[37] = "L"
        fake_555.state[38] = "L"
        fake_555.state[39] = "L"
        fake_555.state[43] = "L"

        fake_555.state[83] = "L"
        fake_555.state[87] = "L"
        fake_555.state[88] = "L"
        fake_555.state[89] = "L"
        fake_555.state[93] = "L"

        # Upper
        if self.state[8] in ("L", "R"):
            fake_555.state[7] = "L"
        if self.state[11] in ("L", "R"):
            fake_555.state[9] = "L"
        if self.state[26] in ("L", "R"):
            fake_555.state[17] = "L"
        if self.state[29] in ("L", "R"):
            fake_555.state[19] = "L"

        # Left
        if self.state[44] in ("L", "R"):
            fake_555.state[32] = "L"
        if self.state[47] in ("L", "R"):
            fake_555.state[34] = "L"
        if self.state[62] in ("L", "R"):
            fake_555.state[42] = "L"
        if self.state[65] in ("L", "R"):
            fake_555.state[44] = "L"

        # Front
        if self.state[80] in ("L", "R"):
            fake_555.state[57] = "L"
        if self.state[83] in ("L", "R"):
            fake_555.state[59] = "L"
        if self.state[98] in ("L", "R"):
            fake_555.state[67] = "L"
        if self.state[101] in ("L", "R"):
            fake_555.state[69] = "L"

        # Right
        if self.state[116] in ("L", "R"):
            fake_555.state[82] = "L"
        if self.state[119] in ("L", "R"):
            fake_555.state[84] = "L"
        if self.state[134] in ("L", "R"):
            fake_555.state[92] = "L"
        if self.state[137] in ("L", "R"):
            fake_555.state[94] = "L"

        # Back
        if self.state[152] in ("L", "R"):
            fake_555.state[107] = "L"
        if self.state[155] in ("L", "R"):
            fake_555.state[109] = "L"
        if self.state[170] in ("L", "R"):
            fake_555.state[117] = "L"
        if self.state[173] in ("L", "R"):
            fake_555.state[119] = "L"

        # Down
        if self.state[188] in ("L", "R"):
            fake_555.state[132] = "L"
        if self.state[191] in ("L", "R"):
            fake_555.state[134] = "L"
        if self.state[206] in ("L", "R"):
            fake_555.state[142] = "L"
        if self.state[209] in ("L", "R"):
            fake_555.state[144] = "L"

    def lookup_table_666_LR_inner_x_centers_oblique_pairing_stage(self):
        tmp_state = ''.join([self.state[square_index] for side in (self.sideL, self.sideF, self.sideR, self.sideB) for square_index in side.center_pos])
        tmp_state = tmp_state.replace('L', 'L').replace('F', 'x').replace('R', 'L').replace('B', 'x')

        # We need to x out the outer x-centers for each side
        state = ''
        for y in range(4):
            state += 'x' + tmp_state[1:3] + 'x' +\
                     tmp_state[4:12] +\
                     'x' + tmp_state[13:15] + 'x'
            tmp_state = tmp_state[16:]

        filename = 'lookup-table-6x6x6-step30-LR-inner-x-centers-and-oblique-pairing-stage.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.warning("LR inner-x-centers-oblique-pairing-stage %s: FOUND entry %d steps in (%s), %s" %\
                    (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                for step in steps:
                    self.rotate(step)
                return True

        return False

    def lookup_table_666_LR_oblique_pairing_stage(self):
        tmp_state = ''.join([self.state[square_index] for side in (self.sideL, self.sideF, self.sideR, self.sideB) for square_index in side.center_pos])
        tmp_state = tmp_state.replace('U', 'x').replace('L', 'L').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        # We need to x out the inner and outer x-centers for each side
        state = ''
        for y in range(4):
            state += 'x' + tmp_state[1:3] + 'x' +\
                     tmp_state[4] + 'xx' + tmp_state[7] +\
                     tmp_state[8] + 'xx' + tmp_state[11] +\
                     'x' + tmp_state[13:15] + 'x'
            tmp_state = tmp_state[16:]

        filename = 'lookup-table-6x6x6-step31-LR-oblique-pairing-stage.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                #log.warning("LR oblique-pairing-stage %s: FOUND entry %d steps in (%s), %s" %\
                #    (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                return steps
            else:
                raise SolveError("lookup_table_666_LR_oblique_pairing_stage failed to find state %s" % state)

        return None

    def ida_search_LR_inner_x_centers_oblique_pairing_stage(self, cost_to_here, threshold, prev_step, prev_state, prev_solution):

        for step in moves_6x6x6:

            # These moves would destroy the staged UD centers
            if step in ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'"):
                continue

            # If this step cancels out the previous step then don't bother with this branch
            if steps_cancel_out(prev_step, step):
                continue

            self.state = copy(prev_state)
            self.solution = copy(prev_solution)
            self.rotate(step)
            self.ida_count += 1

            # Do we have the cube in a state where there is a match in the lookup table?
            if self.lookup_table_666_LR_inner_x_centers_oblique_pairing_stage():
                return True

            cost_to_goal = len(self.lookup_table_666_LR_oblique_pairing_stage())

            if (cost_to_here + 1 + cost_to_goal) > threshold:
                continue

            state_end_of_this_step = copy(self.state)
            solution_end_of_this_step = copy(self.solution)

            if self.ida_search_LR_inner_x_centers_oblique_pairing_stage(cost_to_here + 1, threshold, step, state_end_of_this_step, solution_end_of_this_step):
                return True

        return False

    def group_centers_guts(self):
        self.lookup_table_666_UD_inner_x_centers_stage()
        # self.print_cube()

        if not self.lookup_table_666_UD_oblique_edge_pairing():

            # save cube state
            original_state = copy(self.state)
            original_solution = copy(self.solution)

            # If we are here (odds are very high we will be) it means that the current
            # cube state was not in the lookup table.  We must now perform an IDA search
            # until we find a sequence of moves that takes us to a state that IS in the
            # lookup table.
            for threshold in range(1, 10):
                log.info("ida_search_UD_oblique_edge_pairing: threshold %d" % threshold)
                if self.ida_search_UD_oblique_edge_pairing(0, threshold, None, original_state, original_solution):
                    break
            else:
                raise SolveError("UD oblique-edge-pairing-stage FAILED")

        self.print_cube()

        # At this point we can treat UD centers like 5x5x5 centers
        # Create a dummy 5x5x5 cube object that we can use to figure out what steps to
        fake_555 = RubiksCube555('UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB')
        self.populate_fake_555_for_UD(fake_555)

        if not fake_555.lookup_table_555_UD_centers_stage():

            # If we are here (odds are very high we will be) it means that the current
            # cube state was not in the lookup table.  We must now perform an IDA search
            # until we find a sequence of moves that takes us to a state that IS in the
            # lookup table.

            # save cube state
            original_state = copy(fake_555.state)
            original_solution = copy(fake_555.solution)

            for threshold in range(1, 10):
                log.info("ida_UD_centers_stage: threshold %d" % threshold)
                if fake_555.ida_UD_centers_stage(0, threshold, None, original_state, original_solution):
                    break
            else:
                raise SolveError("5x5x5 UD centers-stage FAILED")

        for step in fake_555.solution:
            self.rotate(step)
        log.info("UD staged, %d steps in" % len(self.solution))
        self.print_cube()

        if not self.lookup_table_666_LR_inner_x_centers_oblique_pairing_stage():

            # save cube state
            original_state = copy(self.state)
            original_solution = copy(self.solution)

            # If we are here (odds are very high we will be) it means that the current
            # cube state was not in the lookup table.  We must now perform an IDA search
            # until we find a sequence of moves that takes us to a state that IS in the
            # lookup table.
            self.ida_count = 0

            for threshold in range(1, 25):
                log.info("ida_search_LR_inner_x_centers_oblique_pairing_stage: threshold %d, ida_count %d" % (threshold, self.ida_count))
                if self.ida_search_LR_inner_x_centers_oblique_pairing_stage(0, threshold, None, original_state, original_solution):
                    break
            else:
                raise SolveError("ida_search_LR_inner_x_centers_oblique_pairing_stage FAILED")

        log.info("Took %d steps to stage UD centers and LR inner-x-centers and oblique pairs" % len(self.solution))
        self.print_cube()

        # At this point we can treat UD centers like 5x5x5 centers
        # Create a dummy 5x5x5 cube object that we can use to figure out what steps to
        fake_555 = RubiksCube555('UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB')
        self.populate_fake_555_for_LR(fake_555)
        fake_555.print_cube()

        fake_555.lookup_table_555_LR_centers_stage()
        for step in fake_555.solution:
            self.rotate(step)

        log.info("Took %d steps to stage ULFRBD centers" % len(self.solution))
        self.print_cube()
        sys.exit(0)
