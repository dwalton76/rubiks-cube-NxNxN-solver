
import datetime as dt
from copy import copy
from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.rotate_xxx import rotate_222, rotate_444, rotate_555, rotate_666, rotate_777
import logging
import math
import os
import subprocess
import sys


log = logging.getLogger(__name__)


class ImplementThis(Exception):
    pass


class NoSteps(Exception):
    pass


def steps_cancel_out(prev_step, step):

    if prev_step is None:
        return False

    # U2 followed by U2 is a no-op
    if step == prev_step and step.endswith("2"):
        return True

    # U' followed by U is a no-op
    if prev_step.endswith("'") and not step.endswith("'") and step == prev_step[0:-1]:
        return True

    # U followed by U' is a no-op
    if not prev_step.endswith("'") and step.endswith("'") and step[0:1] == prev_step:
        return True

    return False


def pretty_time(delta):
    delta = str(delta)

    if delta.startswith('0:00:00.'):
        delta_us = int(delta.split('.')[1])
        delta_ms = int(delta_us/1000)

        if delta_ms >= 500:
            return "\033[91m%sms\033[0m" % delta_ms
        else:
            return "%sms" % delta_ms

    elif delta.startswith('0:00:01.'):
        delta_us = int(delta.split('.')[1])
        delta_ms = 1000 + int(delta_us/1000)
        return "\033[91m%sms\033[0m" % delta_ms

    else:
        return "\033[91m%s\033[0m" % delta


def convert_state_to_hex(state):
    """
    This assumes that state only has "x"s and Us or Ls or Fs or Rs or Bs or Ds
    """
    state = state.replace('x', '0').replace('U', '1').replace('L', '1').replace('F', '1').replace('R', '1').replace('B', '1').replace('D', '1')
    hex_width = int(math.ceil(len(state)/4.0))
    hex_state = hex(int(state, 2))[2:]

    if hex_state.endswith('L'):
        hex_state = hex_state[:-1]

    return hex_state.zfill(hex_width)


class LookupTable(object):

    def __init__(self, parent, filename, state_type, state_target, state_hex, prune_table):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.sides_LFRB = (self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB)
        self.sides_UFDB = (self.parent.sideU, self.parent.sideF, self.parent.sideD, self.parent.sideB)
        self.sides_UD = (self.parent.sideU, self.parent.sideD)
        self.sides_LR = (self.parent.sideL, self.parent.sideR)
        self.sides_FB = (self.parent.sideF, self.parent.sideB)

        if not os.path.exists(filename):
            if os.path.exists(filename + '.gz'):
                log.warning("gunzip --keep %s.gz" % filename)
                subprocess.call(['gunzip', '--keep', filename + '.gz'])
            else:
                print("ERROR: %s does not exist" % filename)
                sys.exit(1)

        self.filename = filename
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.state_type = state_type
        self.state_target = state_target
        self.state_hex = state_hex
        self.prune_table = prune_table
        self.guts_cache = {}

        with open(self.filename) as fh:
            first_line = next(fh)
            self.width = len(first_line)
            (state, steps) = first_line.split(':')
            self.state_width = len(state)

            filesize = os.path.getsize(self.filename)
            self.linecount = filesize/self.width

            # Populate guts_cache with the first and last line of the file
            self.guts_cache[0] = state
            fh.seek((self.linecount-1) * self.width)

            line = fh.readline()
            (state, steps) = line.split(':')
            self.guts_cache[self.linecount] = state

        self.cache = {}
        self.guts_call_count = 0
        self.guts_left_right_range = 0

    def __str__(self):
        return self.desc

    def state(self):
        parent_state = self.parent.state
        sides_all = self.sides_all
        sides_UD = self.sides_UD
        sides_LFRB = self.sides_LFRB

        if self.state_type == 'all':
            state = self.parent.get_state_all()

        elif self.state_type == 'UD-centers-stage':
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-solve':
            state = ''.join([parent_state[square_index] for side in sides_UD for square_index in side.center_pos])

        elif self.state_type == 'UD-centers-solve-on-all':
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x')

        elif self.state_type == 'LR-centers-solve-on-all':
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x')

        elif self.state_type == 'FB-centers-solve-on-all':
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
            state = state.replace('U', 'x').replace('L', 'x').replace('R', 'x').replace('D', 'x')

        elif self.state_type == 'UD-centers-oblique-edges-solve':
            state = []

            for side in sides_UD:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(parent_state[square_index])

            state = ''.join(state)

        elif self.state_type == 'LR-centers-oblique-edges-solve':
            state = []

            for side in self.sides_LR:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(parent_state[square_index])

            state = ''.join(state)

        elif self.state_type == 'FB-centers-oblique-edges-solve':
            state = []

            for side in self.sides_FB:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(parent_state[square_index])

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve':
            state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x', parent_state[65], parent_state[66], parent_state[67], parent_state[68], parent_state[69], parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], parent_state[79], parent_state[80], parent_state[81], parent_state[82], parent_state[83], 'x', parent_state[87], parent_state[88], parent_state[89], 'xx', parent_state[108], parent_state[109], parent_state[110], 'x', parent_state[114], parent_state[115], parent_state[116], parent_state[117], parent_state[118], parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], parent_state[128], parent_state[129], parent_state[130], parent_state[131], parent_state[132], 'x', parent_state[136], parent_state[137], parent_state[138], 'xx', parent_state[157], parent_state[158], parent_state[159], 'x', parent_state[163], parent_state[164], parent_state[165], parent_state[166], parent_state[167], parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], parent_state[177], parent_state[178], parent_state[179], parent_state[180], parent_state[181], 'x', parent_state[185], parent_state[186], parent_state[187], 'xx', parent_state[206], parent_state[207], parent_state[208], 'x', parent_state[212], parent_state[213], parent_state[214], parent_state[215], parent_state[216], parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], parent_state[226], parent_state[227], parent_state[228], parent_state[229], parent_state[230], 'x', parent_state[234], parent_state[235], parent_state[236], 'x'])

            # old way
            # state = ''.join(['x' if square_index in side.center_corner_pos else parent_state[square_index] for side in sides_LFRB for square_index in side.center_pos])

            # really old way
            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(parent_state[square_index])
            state = ''.join(state)
            '''

        elif self.state_type == '666-LFRB-centers-oblique-edges-solve':
            state = ''.join(['x', parent_state[45], parent_state[46], 'x', parent_state[50], parent_state[51], parent_state[52], parent_state[53], parent_state[56], parent_state[57], parent_state[58], parent_state[59], 'x', parent_state[63], parent_state[64], 'xx', parent_state[81], parent_state[82], 'x', parent_state[86], parent_state[87], parent_state[88], parent_state[89], parent_state[92], parent_state[93], parent_state[94], parent_state[95], 'x', parent_state[99], parent_state[100], 'xx', parent_state[117], parent_state[118], 'x', parent_state[122], parent_state[123], parent_state[124], parent_state[125], parent_state[128], parent_state[129], parent_state[130], parent_state[131], 'x', parent_state[135], parent_state[136], 'xx', parent_state[153], parent_state[154], 'x', parent_state[158], parent_state[159], parent_state[160], parent_state[161], parent_state[164], parent_state[165], parent_state[166], parent_state[167], 'x', parent_state[171], parent_state[172], 'x']) 

            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(parent_state[square_index])
            state = ''.join(state)
            '''

        elif self.state_type == 'LR-centers-stage':
            state = ''.join([parent_state[square_index] for side in sides_LFRB for square_index in side.center_pos])
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-stage-on-LFRB':
            state = ''.join([parent_state[square_index] for side in sides_LFRB for square_index in side.center_pos])
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-stage-on-LFRB-x-center-only':
            state = []
            for side in sides_LFRB:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend([parent_state[side.center_pos[0]],
                              'x',
                              parent_state[side.center_pos[2]],
                              'x',
                              parent_state[side.center_pos[4]],
                              'x',
                              parent_state[side.center_pos[6]],
                              'x',
                              parent_state[side.center_pos[8]]])
            state = ''.join(state)
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-stage-on-LFRB-t-center-only':
            state = []
            for side in sides_LFRB:
                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend(['x',
                              parent_state[side.center_pos[1]],
                              'x',
                              parent_state[side.center_pos[3]],
                              parent_state[side.center_pos[4]],
                              parent_state[side.center_pos[5]],
                              'x',
                              parent_state[side.center_pos[7]],
                              'x'])
            state = ''.join(state)
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-solve':
            state = ''.join([parent_state[square_index] for side in self.sides_LR for square_index in side.center_pos])

        elif self.state_type == 'LFRB-centers-solve':
            state = ''.join([parent_state[square_index] for side in sides_LFRB for square_index in side.center_pos])

        elif self.state_type == 'FB-centers-solve':
            state = ''.join([parent_state[square_index] for side in self.sides_FB for square_index in side.center_pos])

        elif self.state_type == 'ULFRBD-centers-solve':
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])

        elif self.state_type == 'UD-centers-on-LR':
            state = ''.join([parent_state[square_index] for side in self.sides_LR for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-on-UFDB':
            state = ''.join([parent_state[square_index] for side in self.sides_UFDB for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-on-UFDB-x-center-only':
            state = []
            for side in self.sides_UFDB:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.append(parent_state[side.center_pos[0]])
                state.append('x')
                state.append(parent_state[side.center_pos[2]])
                state.append('x')
                state.append(parent_state[side.center_pos[4]])
                state.append('x')
                state.append(parent_state[side.center_pos[6]])
                state.append('x')
                state.append(parent_state[side.center_pos[8]])
            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-on-UFDB-t-center-only':
            state = []
            for side in self.sides_UFDB:
                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.append('x')
                state.append(parent_state[side.center_pos[1]])
                state.append('x')
                state.append(parent_state[side.center_pos[3]])
                state.append(parent_state[side.center_pos[4]])
                state.append(parent_state[side.center_pos[5]])
                state.append('x')
                state.append(parent_state[side.center_pos[7]])
                state.append('x')
            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-T-centers-stage':
            # This is currently hard coded for 5x5x5
            state = []

            for side in sides_all:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend(['x',
                              parent_state[side.center_pos[1]],
                              'x',
                              parent_state[side.center_pos[3]],
                              parent_state[side.center_pos[4]],
                              parent_state[side.center_pos[5]],
                              'x',
                              parent_state[side.center_pos[7]],
                              'x'])

            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-X-centers-stage':
            # This is currently hard coded for 5x5x5
            state = []

            for side in sides_all:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend([parent_state[side.center_pos[0]],
                              'x',
                              parent_state[side.center_pos[2]],
                              'x',
                              parent_state[side.center_pos[4]],
                              'x',
                              parent_state[side.center_pos[6]],
                              'x',
                              parent_state[side.center_pos[8]]])

            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UDLR-centers-solve':
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
            state = state.replace('F', 'x').replace('B', 'x')

        elif self.state_type == '444-edges-stage-last-four':

            # backup parent state
            original_state = copy(parent_state)
            original_solution = copy(self.parent.solution)

            # build lists of paired and unpaired edges
            paired = []
            unpaired = []

            for side in sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
                unpaired.extend(side.non_paired_wings(True, True, True, True))

            paired = list(set(paired))
            unpaired = list(set(unpaired))
            #log.info("paired %s" % pformat(paired))
            #log.info("unpaired %s" % pformat(unpaired))

            # x the paired edges
            for (pos1, pos2) in paired:
                parent_state[pos1[0]] = 'x'
                parent_state[pos1[1]] = 'x'
                parent_state[pos2[0]] = 'x'
                parent_state[pos2[1]] = 'x'

            # L the unpaired edges
            for (pos1, pos2) in unpaired:
                parent_state[pos1[0]] = 'L'
                parent_state[pos1[1]] = 'L'
                parent_state[pos2[0]] = 'L'
                parent_state[pos2[1]] = 'L'

            # 'state' is the state of edges
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.edge_pos])

            # restore parent state to original
            parent_state = copy(original_state)
            self.parent.solution = copy(original_solution)

        elif self.state_type == '444-edges-solve-last-four':
            """
            This assumes 444-edges-stage-last-four has been used to stage the last
            four unpaired edges to F-west, F-east, B-west and B-east
            """

            # build a list of paired edges
            paired = []
            for side in sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
            paired = list(set(paired))

            if len(paired) == 24:
                state = 'xxxUUxxUUxxxxxxLLxxLLxxxxxxFFxxFFxxxxxxRRxxRRxxxxxxBBxxBBxxxxxxDDxxDDxxx'
            else:
                # backup parent state
                original_state = copy(parent_state)
                original_solution = copy(self.parent.solution)

                # x the paired edges
                for (pos1, pos2) in paired:
                    parent_state[pos1[0]] = 'x'
                    parent_state[pos1[1]] = 'x'
                    parent_state[pos2[0]] = 'x'
                    parent_state[pos2[1]] = 'x'

                # The unpaired edges must be re-mapped to LL, FF, RR and BB as those were the
                # edges used to build the lookup table. Figure out which pair will be
                # the LL, which will be the RR, etc
                new_LL = None
                new_FF = None
                new_RR = None
                new_BB = None
                for (pos1, pos2) in ((28, 41), (24, 37), (40, 53), (44, 57), (56, 69), (60, 73), (72, 21), (76, 25)):
                    pos1_state = parent_state[pos1]
                    pos2_state = parent_state[pos2]

                    if new_LL is None:
                        new_LL = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_LL or (pos2_state, pos1_state) == new_LL:
                        continue

                    if new_FF is None:
                        new_FF = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_FF or (pos2_state, pos1_state) == new_FF:
                        continue

                    if new_RR is None:
                        new_RR = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_RR or (pos2_state, pos1_state) == new_RR:
                        continue

                    if new_BB is None:
                        new_BB = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_BB or (pos2_state, pos1_state) == new_BB:
                        continue

                # Now re-map them
                for (pos1, pos2) in ((28, 41), (24, 37), (40, 53), (44, 57), (56, 69), (60, 73), (72, 21), (76, 25)):
                    pos1_state = parent_state[pos1]
                    pos2_state = parent_state[pos2]
                    pos1_pos2_state = (pos1_state, pos2_state)
                    pos2_pos1_state = (pos2_state, pos1_state)

                    if pos1_pos2_state == new_LL or pos2_pos1_state == new_LL:
                        parent_state[pos1] = 'L'
                        parent_state[pos2] = 'L'

                    elif pos1_pos2_state == new_FF or pos2_pos1_state == new_FF:
                        parent_state[pos1] = 'F'
                        parent_state[pos2] = 'F'

                    elif pos1_pos2_state == new_RR or pos2_pos1_state == new_RR:
                        parent_state[pos1] = 'R'
                        parent_state[pos2] = 'R'

                    elif pos1_pos2_state == new_BB or pos2_pos1_state == new_BB:
                        parent_state[pos1] = 'B'
                        parent_state[pos2] = 'B'

                    else:
                        raise SolveError("%s not in new_LL %s, new_FF %s, new_RR %s, new_BB %s" %
                            (pformat(pos1_pos2_state), pformat(new_LL), pformat(new_FF), pformat(new_RR), pformat(new_BB)))

                # 'state' is the state of centers and edges
                #
                # Our cube could be rotated so that U is not on the top and F is not at
                # the front but the lookup table was contructed with U on top and F on
                # the front so when we build the state put U on the top and F on the front.
                # It doesn't matter that our cube is rotated in some other way because all
                # entries in the lookup table preserve the centers.
                state = []
                for side in sides_all:
                    for square_index in range(side.min_pos, side.max_pos+1):

                        if square_index in side.corner_pos:
                            pass

                        elif square_index in side.center_pos:
                            if side == self.parent.sideU:
                                state.append('U')
                            elif side == self.parent.sideL:
                                state.append('L')
                            elif side == self.parent.sideF:
                                state.append('F')
                            elif side == self.parent.sideR:
                                state.append('R')
                            elif side == self.parent.sideB:
                                state.append('B')
                            elif side == self.parent.sideD:
                                state.append('D')

                        else:
                            state.append(parent_state[square_index])

                state = ''.join(state)

                # restore parent state to original
                parent_state = copy(original_state)
                self.parent.solution = copy(original_solution)

        elif self.state_type == '555-edges-stage-last-four':

            # backup parent state
            original_state = copy(parent_state)
            original_solution = copy(self.parent.solution)

            # build lists of paired and unpaired edges
            paired = []
            unpaired = []

            for side in sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
                unpaired.extend(side.non_paired_wings(True, True, True, True))

            paired = list(set(paired))
            unpaired = list(set(unpaired))
            #log.info("paired %s" % pformat(paired))
            #log.info("unpaired %s" % pformat(unpaired))

            # x the paired edges
            for (pos1, pos2) in paired:
                parent_state[pos1[0]] = 'x'
                parent_state[pos1[1]] = 'x'
                parent_state[pos2[0]] = 'x'
                parent_state[pos2[1]] = 'x'

            # L the unpaired edges
            for (pos1, pos2) in unpaired:
                parent_state[pos1[0]] = 'L'
                parent_state[pos1[1]] = 'L'
                parent_state[pos2[0]] = 'L'
                parent_state[pos2[1]] = 'L'

            # 'state' is the state of edges
            state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.edge_pos])

            # restore parent state to original
            parent_state = copy(original_state)
            self.parent.solution = copy(original_solution)

        elif self.state_type == '555-edges-solve-last-four':
            """
            This assumes 555-edges-stage-last-four has been used to stage the last
            four unpaired edges to F-west, F-east, B-west and B-east
            """

            # build a list of paired edges
            paired = []
            for side in sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
            paired = list(set(paired))

            if len(paired) == 48:
                state = 'xxxxUUUxxxUUUxxxxxxxxLLLxxxLLLxxxxxxxxFFFxxxFFFxxxxxxxxRRRxxxRRRxxxxxxxxBBBxxxBBBxxxxxxxxDDDxxxDDDxxxx'
            else:
                # backup parent state
                original_state = copy(parent_state)
                original_solution = copy(self.parent.solution)

                # x the paired edges
                for (pos1, pos2) in paired:
                    parent_state[pos1[0]] = 'x'
                    parent_state[pos1[1]] = 'x'
                    parent_state[pos2[0]] = 'x'
                    parent_state[pos2[1]] = 'x'

                # The unpaired edges must be re-mapped to LF, RF, RB and FB as those were the
                # edges used to build the lookup table. Figure out which pair will be
                # the LF, which will be the RF, etc
                new_LF = None
                new_RF = None
                new_LB = None
                new_RB = None
                for (pos1, pos2) in ((35, 56), (40, 61), (45, 66), (60, 81), (65, 86), (70, 91), (85, 106), (90, 111), (95, 116), (110, 31), (115, 36), (120, 41)):
                    pos1_state = parent_state[pos1]
                    pos2_state = parent_state[pos2]

                    if new_LF is None:
                        new_LF = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_LF or (pos2_state, pos1_state) == new_LF:
                        continue

                    if new_RF is None:
                        new_RF = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_RF or (pos2_state, pos1_state) == new_RF:
                        continue

                    if new_LB is None:
                        new_LB = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_LB or (pos2_state, pos1_state) == new_LB:
                        continue

                    if new_RB is None:
                        new_RB = (pos1_state, pos2_state)
                        continue
                    if (pos1_state, pos2_state) == new_RB or (pos2_state, pos1_state) == new_RB:
                        continue

                # Now re-map them
                for (pos1, pos2) in ((35, 56), (40, 61), (45, 66), (60, 81), (65, 86), (70, 91), (85, 106), (90, 111), (95, 116), (110, 31), (115, 36), (120, 41)):
                    pos1_state = parent_state[pos1]
                    pos2_state = parent_state[pos2]
                    pos1_pos2_state = (pos1_state, pos2_state)
                    pos2_pos1_state = (pos2_state, pos1_state)

                    if pos1_pos2_state == new_LF:
                        parent_state[pos1] = 'L'
                        parent_state[pos2] = 'F'

                    elif pos2_pos1_state == new_LF:
                        parent_state[pos2] = 'L'
                        parent_state[pos1] = 'F'

                    elif pos1_pos2_state == new_RF:
                        parent_state[pos1] = 'R'
                        parent_state[pos2] = 'F'

                    elif pos2_pos1_state == new_RF:
                        parent_state[pos2] = 'R'
                        parent_state[pos1] = 'F'

                    elif pos1_pos2_state == new_LB:
                        parent_state[pos1] = 'L'
                        parent_state[pos2] = 'B'

                    elif pos2_pos1_state == new_LB:
                        parent_state[pos2] = 'L'
                        parent_state[pos1] = 'B'

                    elif pos1_pos2_state == new_RB:
                        parent_state[pos1] = 'R'
                        parent_state[pos2] = 'B'

                    elif pos2_pos1_state == new_RB:
                        parent_state[pos2] = 'R'
                        parent_state[pos1] = 'B'

                    else:
                        raise SolveError("%s not in new_LF %s, new_RF %s, new_LB %s, new_RB %s" %
                            (pformat(pos1_pos2_state), pformat(new_LF), pformat(new_RF), pformat(new_LB), pformat(new_RB)))

                # 'state' is the state of centers and edges
                #
                # Our cube could be rotated so that U is not on the top and F is not at
                # the front but the lookup table was contructed with U on top and F on
                # the front so when we build the state put U on the top and F on the front.
                # It doesn't matter that our cube is rotated in some other way because all
                # entries in the lookup table preserve the centers.
                state = []
                for side in sides_all:
                    for square_index in range(side.min_pos, side.max_pos+1):

                        if square_index in side.corner_pos:
                            pass

                        elif square_index in side.center_pos:
                            if side == self.parent.sideU:
                                state.append('U')
                            elif side == self.parent.sideL:
                                state.append('L')
                            elif side == self.parent.sideF:
                                state.append('F')
                            elif side == self.parent.sideR:
                                state.append('R')
                            elif side == self.parent.sideB:
                                state.append('B')
                            elif side == self.parent.sideD:
                                state.append('D')

                        else:
                            state.append(parent_state[square_index])

                state = ''.join(state)

                # restore parent state to original
                parent_state = copy(original_state)
                self.parent.solution = copy(original_solution)

        elif self.state_type == '666-UD-inner-X-centers-stage':
            state = 'xxxxx' + parent_state[15] + parent_state[16] + 'xx' + parent_state[21] + parent_state[22]  + 'xxxxx' +\
                    'xxxxx' + parent_state[51] + parent_state[52] + 'xx' + parent_state[57] + parent_state[58]  + 'xxxxx' +\
                    'xxxxx' + parent_state[87] + parent_state[88] + 'xx' + parent_state[93] + parent_state[94]  + 'xxxxx' +\
                    'xxxxx' + parent_state[123] + parent_state[124] + 'xx' + parent_state[129] + parent_state[130]  + 'xxxxx' +\
                    'xxxxx' + parent_state[159] + parent_state[160] + 'xx' + parent_state[165] + parent_state[166]  + 'xxxxx' +\
                    'xxxxx' + parent_state[195] + parent_state[196] + 'xx' + parent_state[201] + parent_state[202]  + 'xxxxx'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-UD-oblique-edge-pairing':
            state = parent_state[9] + parent_state[10] +\
                    parent_state[14] + parent_state[17] +\
                    parent_state[20] + parent_state[23] +\
                    parent_state[27] + parent_state[28] +\
                    parent_state[45] + parent_state[46] +\
                    parent_state[50] + parent_state[53] +\
                    parent_state[56] + parent_state[59] +\
                    parent_state[63] + parent_state[64] +\
                    parent_state[81] + parent_state[82] +\
                    parent_state[86] + parent_state[89] +\
                    parent_state[92] + parent_state[95] +\
                    parent_state[99] + parent_state[100] +\
                    parent_state[117] + parent_state[118] +\
                    parent_state[122] + parent_state[125] +\
                    parent_state[128] + parent_state[131] +\
                    parent_state[135] + parent_state[136] +\
                    parent_state[153] + parent_state[154] +\
                    parent_state[158] + parent_state[161] +\
                    parent_state[164] + parent_state[167] +\
                    parent_state[171] + parent_state[172] +\
                    parent_state[189] + parent_state[190] +\
                    parent_state[194] + parent_state[197] +\
                    parent_state[200] + parent_state[203] +\
                    parent_state[207] + parent_state[208]
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-UD-oblique-edge-pairing-left-only':
            state = parent_state[9] + 'x' +\
                    'x' + parent_state[17] +\
                    parent_state[20] + 'x' +\
                    'x' + parent_state[28] +\
                    parent_state[45] + 'x' +\
                    'x' + parent_state[53] +\
                    parent_state[56] + 'x' +\
                    'x' + parent_state[64] +\
                    parent_state[81] + 'x' +\
                    'x' + parent_state[89] +\
                    parent_state[92] + 'x' +\
                    'x' + parent_state[100]+\
                    parent_state[117] + 'x' +\
                    'x' + parent_state[125] +\
                    parent_state[128] + 'x' +\
                    'x' + parent_state[136] +\
                    parent_state[153] + 'x' +\
                    'x' + parent_state[161] +\
                    parent_state[164] + 'x' +\
                    'x' + parent_state[172] +\
                    parent_state[189] + 'x' +\
                    'x' + parent_state[197] +\
                    parent_state[200] + 'x' +\
                    'x' + parent_state[208]

            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-UD-oblique-edge-pairing-right-only':
            state = 'x' + parent_state[10] +\
                    parent_state[14] + 'x' +\
                    'x' + parent_state[23] +\
                    parent_state[27] + 'x' +\
                    'x' + parent_state[46] +\
                    parent_state[50] + 'x' +\
                    'x' + parent_state[59] +\
                    parent_state[63] + 'x' +\
                    'x' + parent_state[82] +\
                    parent_state[86] + 'x' +\
                    'x' + parent_state[95] +\
                    parent_state[99] + 'x' +\
                    'x' + parent_state[118] +\
                    parent_state[122] + 'x' +\
                    'x' + parent_state[131] +\
                    parent_state[135] + 'x' +\
                    'x' + parent_state[154] +\
                    parent_state[158] + 'x' +\
                    'x' + parent_state[167] +\
                    parent_state[171] + 'x' +\
                    'x' + parent_state[190] +\
                    parent_state[194] + 'x' +\
                    'x' + parent_state[203] +\
                    parent_state[207] + 'x'

            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-LR-inner-X-centers-stage':
            state = 'xxxxx' + parent_state[15] + parent_state[16] + 'xx' + parent_state[21] + parent_state[22]  + 'xxxxx' +\
                    'xxxxx' + parent_state[51] + parent_state[52] + 'xx' + parent_state[57] + parent_state[58]  + 'xxxxx' +\
                    'xxxxx' + parent_state[87] + parent_state[88] + 'xx' + parent_state[93] + parent_state[94]  + 'xxxxx' +\
                    'xxxxx' + parent_state[123] + parent_state[124] + 'xx' + parent_state[129] + parent_state[130]  + 'xxxxx' +\
                    'xxxxx' + parent_state[159] + parent_state[160] + 'xx' + parent_state[165] + parent_state[166]  + 'xxxxx' +\
                    'xxxxx' + parent_state[195] + parent_state[196] + 'xx' + parent_state[201] + parent_state[202]  + 'xxxxx'
            state = state.replace('U', 'x').replace('L', 'L').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '666-LR-oblique-edge-pairing':
            state = parent_state[45] + parent_state[46] +\
                    parent_state[50] + parent_state[53] +\
                    parent_state[56] + parent_state[59] +\
                    parent_state[63] + parent_state[64] +\
                    parent_state[81] + parent_state[82] +\
                    parent_state[86] + parent_state[89] +\
                    parent_state[92] + parent_state[95] +\
                    parent_state[99] + parent_state[100] +\
                    parent_state[117] + parent_state[118] +\
                    parent_state[122] + parent_state[125] +\
                    parent_state[128] + parent_state[131] +\
                    parent_state[135] + parent_state[136] +\
                    parent_state[153] + parent_state[154] +\
                    parent_state[158] + parent_state[161] +\
                    parent_state[164] + parent_state[167] +\
                    parent_state[171] + parent_state[172]
            state = state.replace('U', 'x').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '666-LR-oblique-edge-pairing-left-only':
            state = parent_state[45] + 'x' +\
                    'x' + parent_state[53] +\
                    parent_state[56] + 'x' +\
                    'x' + parent_state[64] +\
                    parent_state[81] + 'x' +\
                    'x' + parent_state[89] +\
                    parent_state[92] + 'x' +\
                    'x' + parent_state[100] +\
                    parent_state[117] + 'x' +\
                    'x' + parent_state[125] +\
                    parent_state[128] + 'x' +\
                    'x' + parent_state[136] +\
                    parent_state[153] + 'x' +\
                    'x' + parent_state[161] +\
                    parent_state[164] + 'x' +\
                    'x' + parent_state[172]
            state = state.replace('U', 'x').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '666-LR-oblique-edge-pairing-right-only':
            state = 'x' + parent_state[46] +\
                    parent_state[50] + 'x' +\
                    'x' + parent_state[59] +\
                    parent_state[63] + 'x' +\
                    'x' + parent_state[82] +\
                    parent_state[86] + 'x' +\
                    'x' + parent_state[95] +\
                    parent_state[99] + 'x' +\
                    'x' + parent_state[118] +\
                    parent_state[122] + 'x' +\
                    'x' + parent_state[131] +\
                    parent_state[135] + 'x' +\
                    'x' + parent_state[154] +\
                    parent_state[158] + 'x' +\
                    'x' + parent_state[167] +\
                    parent_state[171] + 'x'

            state = state.replace('U', 'x').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '777-UD-oblique-edge-pairing':
            state = 'x' + parent_state[10] + parent_state[11] + parent_state[12] + 'x' +\
                    parent_state[16] + 'xxx' + parent_state[20] +\
                    parent_state[23] + 'xxx' + parent_state[27] +\
                    parent_state[30] + 'xxx' + parent_state[34] +\
                    'x' + parent_state[38] + parent_state[39] + parent_state[40] + 'x' +\
                    'x' + parent_state[59] + parent_state[60] + parent_state[61] + 'x' +\
                    parent_state[65] + 'xxx' + parent_state[69] +\
                    parent_state[72] + 'xxx' + parent_state[76] +\
                    parent_state[79] + 'xxx' + parent_state[83] +\
                    'x' + parent_state[87] + parent_state[88] + parent_state[89] + 'x' +\
                    'x' + parent_state[108] + parent_state[109] + parent_state[110] + 'x' +\
                    parent_state[114] + 'xxx' + parent_state[118] +\
                    parent_state[121] + 'xxx' + parent_state[125] +\
                    parent_state[128] + 'xxx' + parent_state[132] +\
                    'x' + parent_state[136] + parent_state[137] + parent_state[138] + 'x' +\
                    'x' + parent_state[157] + parent_state[158] + parent_state[159] + 'x' +\
                    parent_state[163] + 'xxx' + parent_state[167] +\
                    parent_state[170] + 'xxx' + parent_state[174] +\
                    parent_state[177] + 'xxx' + parent_state[181] +\
                    'x' + parent_state[185] + parent_state[186] + parent_state[187] + 'x' +\
                    'x' + parent_state[206] + parent_state[207] + parent_state[208] + 'x' +\
                    parent_state[212] + 'xxx' + parent_state[216] +\
                    parent_state[219] + 'xxx' + parent_state[223] +\
                    parent_state[226] + 'xxx' + parent_state[230] +\
                    'x' + parent_state[234] + parent_state[235] + parent_state[236] + 'x' +\
                    'x' + parent_state[255] + parent_state[256] + parent_state[257] + 'x' +\
                    parent_state[261] + 'xxx' + parent_state[265] +\
                    parent_state[268] + 'xxx' + parent_state[272] +\
                    parent_state[275] + 'xxx' + parent_state[279] +\
                    'x' + parent_state[283] + parent_state[284] + parent_state[285] + 'x'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-middle-only':
            state = 'xx' + parent_state[11] + 'xx' +\
                    'xxxxx' +\
                    parent_state[23] + 'xxx' + parent_state[27] +\
                    'xxxxx' +\
                    'xx' + parent_state[39] + 'xx' +\
                    'xx' + parent_state[60] + 'xx' +\
                    'xxxxx' +\
                    parent_state[72] + 'xxx' + parent_state[76] +\
                    'xxxxx' +\
                    'xx' + parent_state[88] + 'xx' +\
                    'xx' + parent_state[109] + 'xx' +\
                    'xxxxx' +\
                    parent_state[121] + 'xxx' + parent_state[125] +\
                    'xxxxx' +\
                    'xx' + parent_state[137] + 'xx' +\
                    'xx' + parent_state[158] + 'xx' +\
                    'xxxxx' +\
                    parent_state[170] + 'xxx' + parent_state[174] +\
                    'xxxxx' +\
                    'xx' + parent_state[186] + 'xx' +\
                    'xx' + parent_state[207] + 'xx' +\
                    'xxxxx' +\
                    parent_state[219] + 'xxx' + parent_state[223] +\
                    'xxxxx' +\
                    'xx' + parent_state[235] + 'xx' +\
                    'xx' + parent_state[256] + 'xx' +\
                    'xxxxx' +\
                    parent_state[268] + 'xxx' + parent_state[272] +\
                    'xxxxx' +\
                    'xx' + parent_state[284] + 'xx'

            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-outside-only':
            state = 'x' + parent_state[10] + 'x' + parent_state[12] + 'x' +\
                    parent_state[16] + 'xxx' + parent_state[20] +\
                    'xxxxx' +\
                    parent_state[30] + 'xxx' + parent_state[34] +\
                    'x' + parent_state[38] + 'x' + parent_state[40] + 'x' +\
                    'x' + parent_state[59] + 'x' + parent_state[61] + 'x' +\
                    parent_state[65] + 'xxx' + parent_state[69] +\
                    'xxxxx' +\
                    parent_state[79] + 'xxx' + parent_state[83] +\
                    'x' + parent_state[87] + 'x' + parent_state[89] + 'x' +\
                    'x' + parent_state[108] + 'x' + parent_state[110] + 'x' +\
                    parent_state[114] + 'xxx' + parent_state[118] +\
                    'xxxxx' +\
                    parent_state[128] + 'xxx' + parent_state[132] +\
                    'x' + parent_state[136] + 'x' + parent_state[138] + 'x' +\
                    'x' + parent_state[157] + 'x' + parent_state[159] + 'x' +\
                    parent_state[163] + 'xxx' + parent_state[167] +\
                    'xxxxx' +\
                    parent_state[177] + 'xxx' + parent_state[181] +\
                    'x' + parent_state[185] + 'x' + parent_state[187] + 'x' +\
                    'x' + parent_state[206] + 'x' + parent_state[208] + 'x' +\
                    parent_state[212] + 'xxx' + parent_state[216] +\
                    'xxxxx' +\
                    parent_state[226] + 'xxx' + parent_state[230] +\
                    'x' + parent_state[234] + 'x' + parent_state[236] + 'x' +\
                    'x' + parent_state[255] + 'x' + parent_state[257] + 'x' +\
                    parent_state[261] + 'xxx' + parent_state[265] +\
                    'xxxxx' +\
                    parent_state[275] + 'xxx' + parent_state[279] +\
                    'x' + parent_state[283] + 'x' + parent_state[285] + 'x'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-left-only':
            state = 'x' + parent_state[10] + 'xxx' +\
                    'xxxx' + parent_state[20] +\
                    'xxxxx' +\
                    parent_state[30] + 'xxxx' +\
                    'xxx' + parent_state[40] + 'x' +\
                    'x' + parent_state[59] + 'xxx' +\
                    'xxxx' + parent_state[69] +\
                    'xxxxx' +\
                    parent_state[79] + 'xxxx' +\
                    'xxx' + parent_state[89] + 'x' +\
                    'x' + parent_state[108] + 'xxx' +\
                    'xxxx' + parent_state[118] +\
                    'xxxxx' +\
                    parent_state[128] + 'xxxx' +\
                    'xxx' + parent_state[138] + 'x' +\
                    'x' + parent_state[157] + 'xxx' +\
                    'xxxx' + parent_state[167] +\
                    'xxxxx' +\
                    parent_state[177] + 'xxxx' +\
                    'xxx' + parent_state[187] + 'x' +\
                    'x' + parent_state[206] + 'xxx' +\
                    'xxxx' + parent_state[216] +\
                    'xxxxx' +\
                    parent_state[226] + 'xxxx' +\
                    'xxx' + parent_state[236] + 'x' +\
                    'x' + parent_state[255] + 'xxx' +\
                    'xxxx' + parent_state[265] +\
                    'xxxxx' +\
                    parent_state[275] + 'xxxx' +\
                    'xxx' + parent_state[285] + 'x'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-right-only':
            state = 'xxx' + parent_state[12] + 'x' +\
                    parent_state[16] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[34] +\
                    'x' + parent_state[38] + 'xxx' +\
                    'xxx' + parent_state[61] + 'x' +\
                    parent_state[65] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[83] +\
                    'x' + parent_state[87] + 'xxx' +\
                    'xxx' + parent_state[110] + 'x' +\
                    parent_state[114] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[132] +\
                    'x' + parent_state[136] + 'xxx' +\
                    'xxx' + parent_state[159] + 'x' +\
                    parent_state[163] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[181] +\
                    'x' + parent_state[185] + 'xxx' +\
                    'xxx' + parent_state[208] + 'x' +\
                    parent_state[212] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[230] +\
                    'x' + parent_state[234] + 'xxx' +\
                    'xxx' + parent_state[257] + 'x' +\
                    parent_state[261] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[279] +\
                    'x' + parent_state[283] + 'xxx'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-LR-oblique-edge-pairing':
            state = 'x' + parent_state[59] + parent_state[60] + parent_state[61] + 'x' +\
                    parent_state[65] + 'xxx' + parent_state[69] +\
                    parent_state[72] + 'xxx' + parent_state[76] +\
                    parent_state[79] + 'xxx' + parent_state[83] +\
                    'x' + parent_state[87] + parent_state[88] + parent_state[89] + 'x' +\
                    'x' + parent_state[108] + parent_state[109] + parent_state[110] + 'x' +\
                    parent_state[114] + 'xxx' + parent_state[118] +\
                    parent_state[121] + 'xxx' + parent_state[125] +\
                    parent_state[128] + 'xxx' + parent_state[132] +\
                    'x' + parent_state[136] + parent_state[137] + parent_state[138] + 'x' +\
                    'x' + parent_state[157] + parent_state[158] + parent_state[159] + 'x' +\
                    parent_state[163] + 'xxx' + parent_state[167] +\
                    parent_state[170] + 'xxx' + parent_state[174] +\
                    parent_state[177] + 'xxx' + parent_state[181] +\
                    'x' + parent_state[185] + parent_state[186] + parent_state[187] + 'x' +\
                    'x' + parent_state[206] + parent_state[207] + parent_state[208] + 'x' +\
                    parent_state[212] + 'xxx' + parent_state[216] +\
                    parent_state[219] + 'xxx' + parent_state[223] +\
                    parent_state[226] + 'xxx' + parent_state[230] +\
                    'x' + parent_state[234] + parent_state[235] + parent_state[236] + 'x'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-middle-only':
            state = 'xx' + parent_state[60] + 'xx' +\
                    'xxxxx' +\
                    parent_state[72] + 'xxx' + parent_state[76] +\
                    'xxxxx' +\
                    'xx' + parent_state[88] + 'xx' +\
                    'xx' + parent_state[109] + 'xx' +\
                    'xxxxx' +\
                    parent_state[121] + 'xxx' + parent_state[125] +\
                    'xxxxx' +\
                    'xx' + parent_state[137] + 'xx' +\
                    'xx' + parent_state[158] + 'xx' +\
                    'xxxxx' +\
                    parent_state[170] + 'xxx' + parent_state[174] +\
                    'xxxxx' +\
                    'xx' + parent_state[186] + 'xx' +\
                    'xx' + parent_state[207] + 'xx' +\
                    'xxxxx' +\
                    parent_state[219] + 'xxx' + parent_state[223] +\
                    'xxxxx' +\
                    'xx' + parent_state[235] + 'xx'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-outside-only':
            state = 'x' + parent_state[59] + 'x' + parent_state[61] + 'x' +\
                    parent_state[65] + 'xxx' + parent_state[69] +\
                    'xxxxx' +\
                    parent_state[79] + 'xxx' + parent_state[83] +\
                    'x' + parent_state[87] + 'x' + parent_state[89] + 'x' +\
                    'x' + parent_state[108] + 'x' + parent_state[110] + 'x' +\
                    parent_state[114] + 'xxx' + parent_state[118] +\
                    'xxxxx' +\
                    parent_state[128] + 'xxx' + parent_state[132] +\
                    'x' + parent_state[136] + 'x' + parent_state[138] + 'x' +\
                    'x' + parent_state[157] + 'x' + parent_state[159] + 'x' +\
                    parent_state[163] + 'xxx' + parent_state[167] +\
                    'xxxxx' +\
                    parent_state[177] + 'xxx' + parent_state[181] +\
                    'x' + parent_state[185] + 'x' + parent_state[187] + 'x' +\
                    'x' + parent_state[206] + 'x' + parent_state[208] + 'x' +\
                    parent_state[212] + 'xxx' + parent_state[216] +\
                    'xxxxx' +\
                    parent_state[226] + 'xxx' + parent_state[230] +\
                    'x' + parent_state[234] + 'x' + parent_state[236] + 'x'

            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-left-only':
            state = 'x' + parent_state[59] + 'xxx' +\
                    'xxxx' + parent_state[69] +\
                    'xxxxx' +\
                    parent_state[79] + 'xxxx' +\
                    'xxx' + parent_state[89] + 'x' +\
                    'x' + parent_state[108] + 'xxx' +\
                    'xxxx' + parent_state[118] +\
                    'xxxxx' +\
                    parent_state[128] + 'xxxx' +\
                    'xxx' + parent_state[138] + 'x' +\
                    'x' + parent_state[157] + 'xxx' +\
                    'xxxx' + parent_state[167] +\
                    'xxxxx' +\
                    parent_state[177] + 'xxxx' +\
                    'xxx' + parent_state[187] + 'x' +\
                    'x' + parent_state[206] + 'xxx' +\
                    'xxxx' + parent_state[216] +\
                    'xxxxx' +\
                    parent_state[226] + 'xxxx' +\
                    'xxx' + parent_state[236] + 'x'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-right-only':
            state = 'xxx' + parent_state[61] + 'x' +\
                    parent_state[65] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[83] +\
                    'x' + parent_state[87] + 'xxx' +\
                    'xxx' + parent_state[110] + 'x' +\
                    parent_state[114] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[132] +\
                    'x' + parent_state[136] + 'xxx' +\
                    'xxx' + parent_state[159] + 'x' +\
                    parent_state[163] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[181] +\
                    'x' + parent_state[185] + 'xxx' +\
                    'xxx' + parent_state[208] + 'x' +\
                    parent_state[212] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + parent_state[230] +\
                    'x' + parent_state[234] + 'xxx'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        # dwalton clean up all of the ones above where we are adding strings together
        elif self.state_type == '777-UD-centers-oblique-edges-solve-center-only':
            state = ''.join(['xxxxxx', parent_state[17], parent_state[18], parent_state[19], 'xx', parent_state[24], 'x', parent_state[26], 'xx', parent_state[31], parent_state[32], parent_state[33], 'xxxxxxxx', 'xxxx', parent_state[262], parent_state[263], parent_state[264], 'xx', parent_state[269], 'x', parent_state[271], 'xx', parent_state[276], parent_state[277], parent_state[278], 'xxxxxx'])

            '''
            state = []
            for side in sides_UD:
                for square_index in side.center_pos:
                    if square_index in (17, 19, 31, 33, 262, 264, 276, 278,
                                        18, 24, 26, 32, 263, 269, 271, 277):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')
            state = ''.join(state)
            '''

        elif self.state_type == '777-UD-centers-oblique-edges-solve-edges-only':
            state = ''.join(['x', parent_state[10], parent_state[11], parent_state[12], 'x', parent_state[16], 'xxx', parent_state[20], parent_state[23], 'xxx', parent_state[27], parent_state[30], 'xxx', parent_state[34], 'x', parent_state[38], parent_state[39], parent_state[40], 'xx', parent_state[255], parent_state[256], parent_state[257], 'x', parent_state[261], 'xxx', parent_state[265], parent_state[268], 'xxx', parent_state[272], parent_state[275], 'xxx', parent_state[279], 'x', parent_state[283], parent_state[284], parent_state[285], 'x'])

            '''
            state = []

            for side in sides_UD:
                for square_index in side.center_pos:
                    if square_index in (10, 20, 40, 30, 255, 265, 285, 275,
                                        11, 27, 39, 23, 256, 272, 284, 268,
                                        12, 34, 38, 16, 257, 279, 283, 261):
                        state.append(parent_state[square_index])
                        # To convert one of these from the old way here to the new way above
                        # - comment out the state.append line above
                        # - uncomment the state.append line below
                        # - pformat(state) at the end of this loop and clean up that output a little and there you go
                        # state.append("parent_state[%d]" % square_index)
                    else:
                        state.append('x')

            log.info("FOO: %s" % pformat(state))
            sys.exit(0)
            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-only':
            state = ''.join(['xxxxxx', parent_state[66], parent_state[67], parent_state[68], 'xx', parent_state[73], parent_state[74], parent_state[75], 'xx', parent_state[80], parent_state[81], parent_state[82], 'xxxxxx', 'xxxxxx', parent_state[115], parent_state[116], parent_state[117], 'xx', parent_state[122], parent_state[123], parent_state[124], 'xx', parent_state[129], parent_state[130], parent_state[131], 'xxxxxx', 'xxxxxx', parent_state[164], parent_state[165], parent_state[166], 'xx', parent_state[171], parent_state[172], parent_state[173], 'xx', parent_state[178], parent_state[179], parent_state[180], 'xxxxxx', 'xxxxxx', parent_state[213], parent_state[214], parent_state[215], 'xx', parent_state[220], parent_state[221], parent_state[222], 'xx', parent_state[227], parent_state[228], parent_state[229], 'xxxxxx'])

            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 67, 68, 73, 74, 75, 80, 81, 82,
                                        115, 116, 117, 122, 123, 124, 129, 130, 131,
                                        213, 214, 215, 220, 221, 222, 227, 228, 229,
                                        164, 165, 166, 171, 172, 173, 178, 179, 180):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')
            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-left-oblique-edge-only':
            state = ''.join(['x', parent_state[59], 'xxxx', parent_state[66], 'x', parent_state[68], parent_state[69], 'xx', parent_state[74], 'xx', parent_state[79], parent_state[80], 'x', parent_state[82], 'xxxx', parent_state[89], 'xx', parent_state[108], 'xxxx', parent_state[115], 'x', parent_state[117], parent_state[118], 'xx', parent_state[123], 'xx', parent_state[128], parent_state[129], 'x', parent_state[131], 'xxxx', parent_state[138], 'xx', parent_state[157], 'xxxx', parent_state[164], 'x', parent_state[166], parent_state[167], 'xx', parent_state[172], 'xx', parent_state[177], parent_state[178], 'x', parent_state[180], 'xxxx', parent_state[187], 'xx', parent_state[206], 'xxxx', parent_state[213], 'x', parent_state[215], parent_state[216], 'xx', parent_state[221], 'xx', parent_state[226], parent_state[227], 'x', parent_state[229], 'xxxx', parent_state[236], 'x'])

            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        59, 69, 79, 89, 108, 118, 128, 138, 157, 167, 177, 187, 206, 216, 226, 236):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')
            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-middle-oblique-edge-only':
            state = ''.join(['xx', parent_state[60], 'xxx', parent_state[66], 'x', parent_state[68], 'x', parent_state[72], 'x', parent_state[74], 'x', parent_state[76], 'x', parent_state[80], 'x', parent_state[82], 'xxx', parent_state[88], 'xxxx', parent_state[109], 'xxx', parent_state[115], 'x', parent_state[117], 'x', parent_state[121], 'x', parent_state[123], 'x', parent_state[125], 'x', parent_state[129], 'x', parent_state[131], 'xxx', parent_state[137], 'xxxx', parent_state[158], 'xxx', parent_state[164], 'x', parent_state[166], 'x', parent_state[170], 'x', parent_state[172], 'x', parent_state[174], 'x', parent_state[178], 'x', parent_state[180], 'xxx', parent_state[186], 'xxxx', parent_state[207], 'xxx', parent_state[213], 'x', parent_state[215], 'x', parent_state[219], 'x', parent_state[221], 'x', parent_state[223], 'x', parent_state[227], 'x', parent_state[229], 'xxx', parent_state[235], 'x', 'x'])

            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')
            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-right-oblique-edge-only':
            state = ''.join(['xxx', parent_state[61], 'x', parent_state[65], parent_state[66], 'x', parent_state[68], 'xxx', parent_state[74], 'xxx', parent_state[80], 'x', parent_state[82], parent_state[83], 'x', parent_state[87], 'xxxxxx', parent_state[110], 'x', parent_state[114], parent_state[115], 'x', parent_state[117], 'xxx', parent_state[123], 'xxx', parent_state[129], 'x', parent_state[131], parent_state[132], 'x', parent_state[136], 'xxxxxx', parent_state[159], 'x', parent_state[163], parent_state[164], 'x', parent_state[166], 'xxx', parent_state[172], 'xxx', parent_state[178], 'x', parent_state[180], parent_state[181], 'x', parent_state[185], 'xxxxxx', parent_state[208], 'x', parent_state[212], parent_state[213], 'x', parent_state[215], 'xxx', parent_state[221], 'xxx', parent_state[227], 'x', parent_state[229], parent_state[230], 'x', parent_state[234], 'xxx'])

            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        61, 83, 87, 65, 110, 132, 136, 114, 159, 181, 185, 163, 208, 230, 234, 212):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')
            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-t-center-left-oblique-edge-only':
            state = ''.join(['x', parent_state[59], 'xxxxx', parent_state[67], 'x', parent_state[69], 'x', parent_state[73], parent_state[74], parent_state[75], 'x', parent_state[79], 'x', parent_state[81], 'xxxxx', parent_state[89], 'xx', parent_state[108], 'xxxxx', parent_state[116], 'x', parent_state[118], 'x', parent_state[122], parent_state[123], parent_state[124], 'x', parent_state[128], 'x', parent_state[130], 'xxxxx', parent_state[138], 'xx', parent_state[157], 'xxxxx', parent_state[165], 'x', parent_state[167], 'x', parent_state[171], parent_state[172], parent_state[173], 'x', parent_state[177], 'x', parent_state[179], 'xxxxx', parent_state[187], 'xx', parent_state[206], 'xxxxx', parent_state[214], 'x', parent_state[216], 'x', parent_state[220], parent_state[221], parent_state[222], 'x', parent_state[226], 'x', parent_state[228], 'xxxxx', parent_state[236], 'x']
)
            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        59, 69, 79, 89, 108, 118, 128, 138, 157, 167, 177, 187, 206, 216, 226, 236):

                        state.append(parent_state[square_index])
                    else:
                        state.append('x')
            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-t-center-middle-oblique-edge-only':
            state = ''.join(['xx', parent_state[60], 'xxxx', parent_state[67], 'xx', parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], 'xx', parent_state[81], 'xxxx', parent_state[88], 'xxxx', parent_state[109], 'xxxx', parent_state[116], 'xx', parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], 'xx', parent_state[130], 'xxxx', parent_state[137], 'xxxx', parent_state[158], 'xxxx', parent_state[165], 'xx', parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], 'xx', parent_state[179], 'xxxx', parent_state[186], 'xxxx', parent_state[207], 'xxxx', parent_state[214], 'xx', parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], 'xx', parent_state[228], 'xxxx', parent_state[235], 'x', 'x'])
            '''
            state = []

            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235):

                        state.append(parent_state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-middle-oblique-edge-only':
            state = ''.join(['xx', parent_state[60], 'xxx', parent_state[66], parent_state[67], parent_state[68], 'x', parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], 'x', parent_state[80], parent_state[81], parent_state[82], 'xxx', parent_state[88], 'xxxx', parent_state[109], 'xxx', parent_state[115], parent_state[116], parent_state[117], 'x', parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], 'x', parent_state[129], parent_state[130], parent_state[131], 'xxx', parent_state[137], 'xxxx', parent_state[158], 'xxx', parent_state[164], parent_state[165], parent_state[166], 'x', parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], 'x', parent_state[178], parent_state[179], parent_state[180], 'xxx', parent_state[186], 'xxxx', parent_state[207], 'xxx', parent_state[213], parent_state[214], parent_state[215], 'x', parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], 'x', parent_state[227], parent_state[228], parent_state[229], 'xxx', parent_state[235], 'xx'])

            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-left-middle-oblique-edge-only':
            # not used...should delete this one
            state = []

            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235,
                                        59, 69, 79, 89, 108, 118, 128, 138, 157, 167, 177, 187, 206, 216, 226, 236):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-left-right-oblique-edges-only':
            state = ''.join(['x', parent_state[59], 'x', parent_state[61], 'x', parent_state[65], 'xxx', parent_state[69], 'xxxxx', parent_state[79], 'xxx', parent_state[83], 'x', parent_state[87], 'x', parent_state[89], 'xx', parent_state[108], 'x', parent_state[110], 'x', parent_state[114], 'xxx', parent_state[118], 'xxxxx', parent_state[128], 'xxx', parent_state[132], 'x', parent_state[136], 'x', parent_state[138], 'xx', parent_state[157], 'x', parent_state[159], 'x', parent_state[163], 'xxx', parent_state[167], 'xxxxx', parent_state[177], 'xxx', parent_state[181], 'x', parent_state[185], 'x', parent_state[187], 'xx', parent_state[206], 'x', parent_state[208], 'x', parent_state[212], 'xxx', parent_state[216], 'xxxxx', parent_state[226], 'xxx', parent_state[230], 'x', parent_state[234], 'x', parent_state[236], 'x'])

            '''
            state = []
            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (59, 61, 65, 79, 69, 83, 87, 89,
                                        157, 159, 163, 177, 167, 181, 185, 187,
                                        108, 110, 114, 128, 118, 132, 136, 138,
                                        206, 208, 212, 226, 216, 230, 234, 236):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)
            '''

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-middle-right-oblique-edges-only':
            state = ''.join(['xx', parent_state[60], parent_state[61], 'x', parent_state[65], 'xxxx', parent_state[72], 'xxx', parent_state[76], 'xxxx', parent_state[83], 'x', parent_state[87], parent_state[88], 'xxxx', parent_state[109], parent_state[110], 'x', parent_state[114], 'xxxx', parent_state[121], 'xxx', parent_state[125], 'xxxx', parent_state[132], 'x', parent_state[136], parent_state[137], 'xxxx', parent_state[158], parent_state[159], 'x', parent_state[163], 'xxxx', parent_state[170], 'xxx', parent_state[174], 'xxxx', parent_state[181], 'x', parent_state[185], parent_state[186], 'xxxx', parent_state[207], parent_state[208], 'x', parent_state[212], 'xxxx', parent_state[219], 'xxx', parent_state[223], 'xxxx', parent_state[230], 'x', parent_state[234], parent_state[235], 'x', 'x'])

            '''
            state = []

            for side in sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235,
                                        61, 83, 87, 65, 110, 132, 136, 114, 159, 181, 185, 163, 208, 230, 234, 212):
                        state.append(parent_state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)
            '''

        else:
            raise ImplementThis("state_type %s" % self.state_type)

        if self.state_hex:
            state = convert_state_to_hex(state)

        return state

    def file_binary_search_guts(self, fh, state_to_find, init_left, init_right):

        if init_left is None:
            left = 0
        else:
            left = init_left

        if init_right is None:
            right = self.linecount - 1
        else:
            right = init_right

        self.guts_call_count += 1
        self.guts_left_right_range += right - left

        state = None
        width = self.width
        state_width = self.state_width

        while left <= right:
            mid = left + ((right - left) /2)
            fh.seek(mid * width)

            '''
            # Use this instead of the 'state, steps = fh.readline...' if you need to debug something
            line = fh.readline()
            try:
                state, steps = line.split(':')
            except Exception as e:
                log.info("%s left %d, right %d, mid %d, linecount %d, line '%s'" % (self, left, right, mid, self.linecount, line))
                raise e
            '''
            line = fh.readline()
            state = line[0:state_width]
            self.guts_cache[mid] = state

            if state_to_find > state:
                left = mid + 1

            elif state_to_find == state:
                (state, steps) = line.split(':')
                return (mid, steps.strip().split())

            else:
                right = mid - 1

        return (mid, None)

    def file_binary_search(self, fh, state_to_find):
        (line_number, value) = self.file_binary_search_guts(fh, state_to_find, None, None)
        return value

    def find_min_left_max_right(self, state_to_find):
        min_left = None
        max_right = None
        line_numbers = sorted(self.guts_cache.keys())
        prev_state = None
        prev_line_number = 0

        for line_number in line_numbers:
            state = self.guts_cache[line_number]

            if prev_state and state_to_find >= prev_state and state_to_find <= state:
                min_left = prev_line_number
                max_right = line_number
                break
            
            prev_state = state
            prev_line_number = line_number

        for line_number in line_numbers:
            if line_number < min_left:
                del self.guts_cache[line_number]

        #log.info("find_min_left_max_right: min_left %s, max_right %s" % (min_left, max_right))
        return (min_left, max_right)

    def file_binary_search_multiple_keys_low_low_python(self, fh, states_to_find, debug=False):
        results = {}
        min_left = None
        max_right = None
        self.guts_cache = {}
        self.guts_call_count = 0
        self.guts_left_right_range = 0

        if not states_to_find:
            return results

        # Look in our cache to see which states we've already found
        original_states_to_find_count = len(states_to_find)
        non_cached_states_to_find = []

        for state in states_to_find:
            steps = self.cache.get(state, -1)

            if steps == -1:
                non_cached_states_to_find.append(state)
            else:
                results[state] = steps

        states_to_find = sorted(non_cached_states_to_find)

        if not states_to_find:
            return results

        states_to_find_count = len(states_to_find)
        # log.info("%s find %d states, %d are not cached" % (self, original_states_to_find_count, states_to_find_count))
        index = 0

        start_time = dt.datetime.now()
        while index < states_to_find_count:
            state_to_find = states_to_find[index]

            (min_left, max_right) = self.find_min_left_max_right(state_to_find)
            #if index % 1000 == 0:
            #    log.info("%s: index %d, state %s, min_left %s, max_right %s" % (self, index, state_to_find, min_left, max_right))

            (line_number, value) = self.file_binary_search_guts(fh, state_to_find, min_left, max_right)
            results[state_to_find] = value
            self.cache[state_to_find] = value
            index += 1

        self.guts_cache = {}
        end_time = dt.datetime.now()
        log.info("%s: found %d states (another %d were cached) in %s" %
            (self, states_to_find_count, original_states_to_find_count - states_to_find_count, pretty_time(end_time - start_time)))
        return results

    def file_binary_search_multiple_keys_low_high_C(self, fh, states_to_find, debug=False):
        results = {}
        min_left = None
        max_right = None

        if not states_to_find:
            return results

        # Look in our cache to see which states we've already found
        original_states_to_find_count = len(states_to_find)
        non_cached_states_to_find = []

        for state in states_to_find:
            steps = self.cache.get(state, -1)

            if steps == -1:
                non_cached_states_to_find.append(state)
            else:
                results[state] = steps

        states_to_find = sorted(non_cached_states_to_find)
        states_to_find_count = len(states_to_find)
        log.info("%s find %d states, %d are not cached" % (self, original_states_to_find_count, states_to_find_count))
        tmp_filename = 'states-to-find-%s'  % self.filename

        # - write states_to_find to a file
        # - call C program to process it
        # - read output into results dictionary
        with open(tmp_filename, 'w') as fh2:
            for state in states_to_find:
                fh2.write(state + '\n')

        cmd = ['./binary-search',
               '--input', tmp_filename,
               '--output',  'foo.txt',
               '--db', self.filename,
               '--line-width', str(self.width),
               '--state-width', str(self.state_width),
               '--line-count', str(self.linecount)]

        if not self.prune_table:
            cmd.append('--exit-on-first-match')

        # log.info(' '.join(cmd))
        subprocess.call(cmd)

        with open('foo.txt', 'r') as fh2:
            for line in fh2:
                (state, steps) = line.strip().split(':')

                if steps == 'None':
                    results[state] = None
                else:
                    results[state] = steps.split()
                self.cache[state] = results[state]
        
        log.info("%s: done" % self)
        return results

    def file_binary_search_multiple_keys(self, fh, states_to_find, debug=False):
        #return self.file_binary_search_multiple_keys_low_high_C(fh, states_to_find, debug)
        return self.file_binary_search_multiple_keys_low_low_python(fh, states_to_find, debug)

    def steps(self, state_to_find=None):
        """
        Return the steps found in the lookup table for the current cube state
        """
        if state_to_find is None:
            state_to_find = self.state()

        if isinstance(state_to_find, list):
            # Return a dictionary where the key is the state and the value is the list of steps
            with open(self.filename, 'r') as fh:
                return self.file_binary_search_multiple_keys(fh, state_to_find)

        else:
            # Return a list of steps that correspond to this state
            with open(self.filename, 'r') as fh:
                return self.file_binary_search(fh, state_to_find)

    def steps_length(self, state=None):
        return len(self.steps(state))

    def solve(self):
        assert self.state_target is not None, "state_target is None"

        while True:
            state = self.state()

            log.info("%s: state %s vs state_target %s" % (self.state_type, state, self.state_target))

            if state == self.state_target:
                break

            steps = self.steps(state)
            # log.info("steps: %s" % ' '.join(steps))

            if not steps:
                raise NoSteps("%s: state %s does not have steps" % (self, state))

            for step in steps:
                self.parent.rotate(step)


class LookupTableIDA(LookupTable):
    """
    """

    def __init__(self, parent, filename, state_type, state_target, state_hex, moves_all, moves_illegal, prune_tables):
        LookupTable.__init__(self, parent, filename, state_type, state_target, state_hex, False)
        self.moves_all = moves_all
        self.moves_illegal = moves_illegal
        self.ida_count = 0
        self.ida_prune_count = 0
        self.prune_tables = prune_tables
        self.visited_states = set()

    def ida_cost(self, max_cost_to_goal):
        costs = []

        for pt in self.prune_tables:
            cost = pt.steps_length()
            if cost >= max_cost_to_goal:
                return cost
            costs.append(cost)

        return max(costs)

    def ida_steps_list(self, prev_step_sequences, threshold, max_step_count):

        # Build a list of the steps we need to explore
        step_sequences_to_try = []

        for step in self.moves_all:

            if step in self.moves_illegal:
                continue

            # Special case, we must preserve the outer UD oblique edges that have already been paired
            if self.filename in ('lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt',
                                 'lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt',
                                 'lookup-table-7x7x7-step12-UD-oblique-edge-pairing-left-only.txt',
                                 'lookup-table-7x7x7-step13-UD-oblique-edge-pairing-right-only.txt',
                                 'lookup-table-7x7x7-step20-LR-oblique-edge-pairing.txt',
                                 'lookup-table-7x7x7-step21-LR-oblique-edge-pairing-middle-only.txt',
                                 'lookup-table-7x7x7-step22-LR-oblique-edge-pairing-left-only.txt',
                                 'lookup-table-7x7x7-step23-LR-oblique-edge-pairing-right-only.txt'):
                if step == "3Rw2":
                    step = "3Rw2 3Lw2"

                elif step == "3Lw2":
                    step = "3Lw2 3Rw2"

                elif step == "3Fw2":
                    step = "3Fw2 3Bw2"

                elif step == "3Bw2":
                    step = "3Bw2 3Fw2"

                elif step == "3Uw2":
                    step = "3Uw2 3Dw2"

                elif step == "3Dw2":
                    step = "3Dw2 3Uw2"

                # "3Uw", "3Uw'", "3Dw", "3Dw'"
                elif step == "3Uw":
                    step = "3Uw 3Dw'"

                elif step == "3Uw'":
                    step = "3Uw' 3Dw"

                elif step == "3Dw":
                    step = "3Dw 3Uw'"

                elif step == "3Dw'":
                    step = "3Dw' 3Uw"

            step_sequences_to_try.append(step)

        if not prev_step_sequences:
            return step_sequences_to_try

        result = []
        for prev_steps in prev_step_sequences:
            for next_step in step_sequences_to_try:

                # If this step cancels out the previous step then don't bother with this branch
                if steps_cancel_out(prev_steps[-1], next_step):
                    continue

                result.append("%s %s" % (prev_steps, next_step))
        return result

    def ida_stage(self):
        state = self.state()
        log.info("state %s vs state_target %s" % (state, self.state_target))

        # The cube is already in the desired state, nothing to do
        if state == self.state_target:
            return

        # The cube is already in a state that is in our lookup table, nothing for IDA to do
        steps = self.steps()

        if steps:
            log.info("%s: IDA count %d, cube is already in a state that is in our lookup table" % (self, self.ida_count))
            return

        # If we are here (odds are very high we will be) it means that the current
        # cube state was not in the lookup table.  We must now perform an IDA search
        # until we find a sequence of moves that takes us to a state that IS in the
        # lookup table.

        # save cube state
        original_state = copy(self.parent.state)
        original_solution = copy(self.parent.solution)

        for threshold in range(1, 20):

            # Build a list of moves we can do 1 move deep
            # Build a list of moves we can do 2 moves deep, this must build on the 1 move deep list
            # Build a list of moves we can do 3 moves deep, this must build on the 2 move deep list
            # etc
            prev_step_sequences = []
            #already_checked = set()

            for max_step_count in range(1, threshold+1):
                step_sequences = self.ida_steps_list(prev_step_sequences, threshold, max_step_count)
                # log.info("%s: step_sequences %s" % (self, pformat(step_sequences)))

                states_to_check = []
                pt_states_to_check = {}
                state_step = []
                costs_to_goal = {}
                pt_costs_by_step = {}

                if step_sequences:
                    log.info("")
                    log.info("%s: IDA threshold %d, %s step_sequences to evaluate (max step %d)" %
                        (self, threshold, len(step_sequences), max_step_count))

                for pt in self.prune_tables:
                    pt_states_to_check[pt.filename] = []

                # Now rotate all of these moves and get the resulting cube for each
                # Do one gigantic binary search
                start_time = dt.datetime.now()
                rotate_count = 0
                for step_sequence in step_sequences:

                    #if step_sequence in already_checked:
                    #    continue
                    #already_checked.add(step_sequence)

                    self.parent.state = copy(original_state)
                    self.parent.solution = copy(original_solution)
                    self.ida_count += 1
                    rotate_count += 1

                    for step in step_sequence.split():
                        state_original = copy(self.parent.state)
                        self.parent.solution.append(step)

                        # We could just call self.parent.rotate(step) here but the explicit
                        # rotate_444, rotate_555, etc are faster.
                        if self.parent.size == 2:
                            rotate_222(self.parent.state, state_original, step)
                        elif self.parent.size == 4:
                            rotate_444(self.parent.state, state_original, step)
                        elif self.parent.size == 5:
                            rotate_555(self.parent.state, state_original, step)
                        elif self.parent.size == 6:
                            rotate_666(self.parent.state, state_original, step)
                        elif self.parent.size == 7:
                            rotate_777(self.parent.state, state_original, step)
                        else:
                            raise ImplementThis("Need rotate_xxx" % (self.parent.size, self.parent.size, self.parent.size))

                    # get the current state of the cube
                    state = self.state()
                    pt_costs_by_step[step_sequence] = []

                    for pt in self.prune_tables:
                        pt_state = pt.state()
                        pt_states_to_check[pt.filename].append(pt_state)
                        pt_costs_by_step[step_sequence].append((pt.filename, pt_state))

                    state_step.append((state, step_sequence))
                    states_to_check.append(state)
                end_time = dt.datetime.now()

                if rotate_count:
                    log.info("%s: IDA threshold %d, rotated %d sequences in %s (max step %d)" %
                        (self, threshold, rotate_count, pretty_time(end_time - start_time), max_step_count))

                self.parent.state = copy(original_state)
                self.parent.solution = copy(original_solution)

                # This will do a multi-key binary search of all states_to_check
                steps_for_states = self.steps(states_to_check)

                # There are steps for a state that means our IDA search is done...woohoo!!
                for (state, step_sequence) in state_step:
                    steps = steps_for_states[state]

                    if steps:
                        for step in step_sequence.split():
                            self.parent.rotate(step)

                        for step in steps:
                            self.parent.rotate(step)

                        log.warning("%s: IDA found match, count %d" % (self, self.ida_count))
                        return

                # Time to prune some branches, do a multi-key binary search for each prune table
                pt_costs = {}
                for pt in self.prune_tables:
                    states_to_find = pt_states_to_check[pt.filename]

                    with open(pt.filename, 'r') as fh:
                        pt_costs[pt.filename] = pt.file_binary_search_multiple_keys(fh, states_to_find)

                step_sequences_within_cost = []
                #log.info("%s: state_step %s" % (self, pformat(state_step)))
                #log.info("%s: pt_costs\n%s\n" % (self, pformat(pt_costs)))

                for (state, step_sequence) in state_step:

                    # extract cost_to_goal from the pt_costs dictionary
                    cost_to_goal = 0
                    cost_to_here = len(step_sequence.split())

                    for (pt_filename, pt_state) in pt_costs_by_step[step_sequence]:
                        pt_steps = pt_costs[pt_filename][pt_state]

                        if pt_steps is None:
                            raise SolveError("%s: prune table %s does not have %s" % (self, pt_filename, pt_state))

                        len_pt_steps = len(pt_steps)

                        if len_pt_steps > cost_to_goal:
                            cost_to_goal = len_pt_steps

                    if (cost_to_here + cost_to_goal) > threshold:
                        #log.info("prune IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                        #        (step, cost_to_here, cost_to_goal, threshold))
                        self.ida_prune_count += 1
                    else:
                        step_sequences_within_cost.append(step_sequence)

                #log.info("%s: IDA threshold %d, max_step_count %d, step_sequences\n%s\n" % (self, threshold, max_step_count, pformat(step_sequences)))
                #log.info("%s: IDA threshold %d, max_step_count %d" % (self, threshold, max_step_count))
                #log.info("%s: step_sequences_within_cost %s" % (self, pformat(step_sequences_within_cost)))
                #foo = len(step_sequences_within_cost)

                #log.info("%s: IDA threshold %d, max_step_count %d, step_sequences_within_cost %d" % (self, threshold, max_step_count, len(step_sequences_within_cost)))
                prev_step_sequences = copy(step_sequences_within_cost)

                log.debug("%s: IDA threshold %d (max step %d), evaluated %d, pruned %d, keep %d" %\
                    (self, threshold, max_step_count, self.ida_count, self.ida_prune_count, len(step_sequences_within_cost)))
                self.ida_count = 0
                self.ida_prune_count = 0

        # we should never get to here
        raise SolveError("%s FAILED for state %s" % (self, self.state()))

    def solve(self):
        assert self.state_target is not None, "state_target is None"

        if self.ida_stage():
            return

        LookupTable.solve(self)
