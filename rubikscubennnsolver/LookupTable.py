
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
fbsmk_count = 0


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

        with open(self.filename) as fh:
            first_line = next(fh)
            self.width = len(first_line)
            (state, steps) = first_line.split(':')
            self.state_width = len(state)

        filesize = os.path.getsize(self.filename)
        self.linecount = filesize/self.width
        self.cache = {}

    def __str__(self):
        return self.desc

    def state(self):

        if self.state_type == 'all':
            state = self.parent.get_state_all()

        elif self.state_type == 'UD-centers-stage':
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_UD for square_index in side.center_pos])

        elif self.state_type == 'UD-centers-solve-on-all':
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x')

        elif self.state_type == 'LR-centers-solve-on-all':
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.center_pos])
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x')

        elif self.state_type == 'FB-centers-solve-on-all':
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.center_pos])
            state = state.replace('U', 'x').replace('L', 'x').replace('R', 'x').replace('D', 'x')

        elif self.state_type == 'UD-centers-oblique-edges-solve':
            state = []

            for side in self.sides_UD:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(self.parent.state[square_index])

            state = ''.join(state)

        elif self.state_type == 'LR-centers-oblique-edges-solve':
            state = []

            for side in self.sides_LR:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(self.parent.state[square_index])

            state = ''.join(state)

        elif self.state_type == 'FB-centers-oblique-edges-solve':
            state = []

            for side in self.sides_FB:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(self.parent.state[square_index])

            state = ''.join(state)

        elif self.state_type == 'LFRB-centers-oblique-edges-solve':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in side.center_corner_pos:
                        state.append('x')
                    else:
                        state.append(self.parent.state[square_index])

            state = ''.join(state)

        elif self.state_type == 'LR-centers-stage':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LFRB for square_index in side.center_pos])
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-stage-on-LFRB':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LFRB for square_index in side.center_pos])
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-stage-on-LFRB-x-center-only':
            state = []
            for side in self.sides_LFRB:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend([self.parent.state[side.center_pos[0]],
                              'x',
                              self.parent.state[side.center_pos[2]],
                              'x',
                              self.parent.state[side.center_pos[4]],
                              'x',
                              self.parent.state[side.center_pos[6]],
                              'x',
                              self.parent.state[side.center_pos[8]]])
            state = ''.join(state)
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-stage-on-LFRB-t-center-only':
            state = []
            for side in self.sides_LFRB:
                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend(['x',
                              self.parent.state[side.center_pos[1]],
                              'x',
                              self.parent.state[side.center_pos[3]],
                              self.parent.state[side.center_pos[4]],
                              self.parent.state[side.center_pos[5]],
                              'x',
                              self.parent.state[side.center_pos[7]],
                              'x'])
            state = ''.join(state)
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LR for square_index in side.center_pos])

        elif self.state_type == 'LFRB-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LFRB for square_index in side.center_pos])

        elif self.state_type == 'FB-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_FB for square_index in side.center_pos])

        elif self.state_type == 'ULFRBD-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.center_pos])

        elif self.state_type == 'UD-centers-on-LR':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LR for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-on-UFDB':
            state = ''.join([self.parent.state[square_index] for side in self.sides_UFDB for square_index in side.center_pos])
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-on-UFDB-x-center-only':
            state = []
            for side in self.sides_UFDB:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.append(self.parent.state[side.center_pos[0]])
                state.append('x')
                state.append(self.parent.state[side.center_pos[2]])
                state.append('x')
                state.append(self.parent.state[side.center_pos[4]])
                state.append('x')
                state.append(self.parent.state[side.center_pos[6]])
                state.append('x')
                state.append(self.parent.state[side.center_pos[8]])
            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-centers-on-UFDB-t-center-only':
            state = []
            for side in self.sides_UFDB:
                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.append('x')
                state.append(self.parent.state[side.center_pos[1]])
                state.append('x')
                state.append(self.parent.state[side.center_pos[3]])
                state.append(self.parent.state[side.center_pos[4]])
                state.append(self.parent.state[side.center_pos[5]])
                state.append('x')
                state.append(self.parent.state[side.center_pos[7]])
                state.append('x')
            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-T-centers-stage':
            # This is currently hard coded for 5x5x5
            state = []

            for side in self.sides_all:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend(['x',
                              self.parent.state[side.center_pos[1]],
                              'x',
                              self.parent.state[side.center_pos[3]],
                              self.parent.state[side.center_pos[4]],
                              self.parent.state[side.center_pos[5]],
                              'x',
                              self.parent.state[side.center_pos[7]],
                              'x'])

            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-X-centers-stage':
            # This is currently hard coded for 5x5x5
            state = []

            for side in self.sides_all:

                # [7, 8, 9, 12, 13, 14, 17, 18, 19]
                #  X  T  X   T  TX   T   X   T   X
                #  0  1  2   3   4   5   6   7   8
                state.extend([self.parent.state[side.center_pos[0]],
                              'x',
                              self.parent.state[side.center_pos[2]],
                              'x',
                              self.parent.state[side.center_pos[4]],
                              'x',
                              self.parent.state[side.center_pos[6]],
                              'x',
                              self.parent.state[side.center_pos[8]]])

            state = ''.join(state)
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UDLR-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.center_pos])
            state = state.replace('F', 'x').replace('B', 'x')

        elif self.state_type == '444-edges-stage-last-four':

            # backup parent state
            original_state = copy(self.parent.state)
            original_solution = copy(self.parent.solution)

            # build lists of paired and unpaired edges
            paired = []
            unpaired = []

            for side in self.sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
                unpaired.extend(side.non_paired_wings(True, True, True, True))

            paired = list(set(paired))
            unpaired = list(set(unpaired))
            #log.info("paired %s" % pformat(paired))
            #log.info("unpaired %s" % pformat(unpaired))

            # x the paired edges
            for (pos1, pos2) in paired:
                self.parent.state[pos1[0]] = 'x'
                self.parent.state[pos1[1]] = 'x'
                self.parent.state[pos2[0]] = 'x'
                self.parent.state[pos2[1]] = 'x'

            # L the unpaired edges
            for (pos1, pos2) in unpaired:
                self.parent.state[pos1[0]] = 'L'
                self.parent.state[pos1[1]] = 'L'
                self.parent.state[pos2[0]] = 'L'
                self.parent.state[pos2[1]] = 'L'

            # 'state' is the state of edges
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.edge_pos])

            # restore parent state to original
            self.parent.state = copy(original_state)
            self.parent.solution = copy(original_solution)

        elif self.state_type == '444-edges-solve-last-four':
            """
            This assumes 444-edges-stage-last-four has been used to stage the last
            four unpaired edges to F-west, F-east, B-west and B-east
            """

            # build a list of paired edges
            paired = []
            for side in self.sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
            paired = list(set(paired))

            if len(paired) == 24:
                state = 'xxxUUxxUUxxxxxxLLxxLLxxxxxxFFxxFFxxxxxxRRxxRRxxxxxxBBxxBBxxxxxxDDxxDDxxx'
            else:
                # backup parent state
                original_state = copy(self.parent.state)
                original_solution = copy(self.parent.solution)

                # x the paired edges
                for (pos1, pos2) in paired:
                    self.parent.state[pos1[0]] = 'x'
                    self.parent.state[pos1[1]] = 'x'
                    self.parent.state[pos2[0]] = 'x'
                    self.parent.state[pos2[1]] = 'x'

                # The unpaired edges must be re-mapped to LL, FF, RR and BB as those were the
                # edges used to build the lookup table. Figure out which pair will be
                # the LL, which will be the RR, etc
                new_LL = None
                new_FF = None
                new_RR = None
                new_BB = None
                for (pos1, pos2) in ((28, 41), (24, 37), (40, 53), (44, 57), (56, 69), (60, 73), (72, 21), (76, 25)):
                    pos1_state = self.parent.state[pos1]
                    pos2_state = self.parent.state[pos2]

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
                    pos1_state = self.parent.state[pos1]
                    pos2_state = self.parent.state[pos2]
                    pos1_pos2_state = (pos1_state, pos2_state)
                    pos2_pos1_state = (pos2_state, pos1_state)

                    if pos1_pos2_state == new_LL or pos2_pos1_state == new_LL:
                        self.parent.state[pos1] = 'L'
                        self.parent.state[pos2] = 'L'

                    elif pos1_pos2_state == new_FF or pos2_pos1_state == new_FF:
                        self.parent.state[pos1] = 'F'
                        self.parent.state[pos2] = 'F'

                    elif pos1_pos2_state == new_RR or pos2_pos1_state == new_RR:
                        self.parent.state[pos1] = 'R'
                        self.parent.state[pos2] = 'R'

                    elif pos1_pos2_state == new_BB or pos2_pos1_state == new_BB:
                        self.parent.state[pos1] = 'B'
                        self.parent.state[pos2] = 'B'

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
                for side in self.sides_all:
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
                            state.append(self.parent.state[square_index])

                state = ''.join(state)

                # restore parent state to original
                self.parent.state = copy(original_state)
                self.parent.solution = copy(original_solution)

        elif self.state_type == '555-edges-stage-last-four':

            # backup parent state
            original_state = copy(self.parent.state)
            original_solution = copy(self.parent.solution)

            # build lists of paired and unpaired edges
            paired = []
            unpaired = []

            for side in self.sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
                unpaired.extend(side.non_paired_wings(True, True, True, True))

            paired = list(set(paired))
            unpaired = list(set(unpaired))
            #log.info("paired %s" % pformat(paired))
            #log.info("unpaired %s" % pformat(unpaired))

            # x the paired edges
            for (pos1, pos2) in paired:
                self.parent.state[pos1[0]] = 'x'
                self.parent.state[pos1[1]] = 'x'
                self.parent.state[pos2[0]] = 'x'
                self.parent.state[pos2[1]] = 'x'

            # L the unpaired edges
            for (pos1, pos2) in unpaired:
                self.parent.state[pos1[0]] = 'L'
                self.parent.state[pos1[1]] = 'L'
                self.parent.state[pos2[0]] = 'L'
                self.parent.state[pos2[1]] = 'L'

            # 'state' is the state of edges
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.edge_pos])

            # restore parent state to original
            self.parent.state = copy(original_state)
            self.parent.solution = copy(original_solution)

        elif self.state_type == '555-edges-solve-last-four':
            """
            This assumes 555-edges-stage-last-four has been used to stage the last
            four unpaired edges to F-west, F-east, B-west and B-east
            """

            # build a list of paired edges
            paired = []
            for side in self.sides_all:
                paired.extend(side.paired_wings(True, True, True, True))
            paired = list(set(paired))

            if len(paired) == 48:
                state = 'xxxxUUUxxxUUUxxxxxxxxLLLxxxLLLxxxxxxxxFFFxxxFFFxxxxxxxxRRRxxxRRRxxxxxxxxBBBxxxBBBxxxxxxxxDDDxxxDDDxxxx'
            else:
                # backup parent state
                original_state = copy(self.parent.state)
                original_solution = copy(self.parent.solution)

                # x the paired edges
                for (pos1, pos2) in paired:
                    self.parent.state[pos1[0]] = 'x'
                    self.parent.state[pos1[1]] = 'x'
                    self.parent.state[pos2[0]] = 'x'
                    self.parent.state[pos2[1]] = 'x'

                # The unpaired edges must be re-mapped to LF, RF, RB and FB as those were the
                # edges used to build the lookup table. Figure out which pair will be
                # the LF, which will be the RF, etc
                new_LF = None
                new_RF = None
                new_LB = None
                new_RB = None
                for (pos1, pos2) in ((35, 56), (40, 61), (45, 66), (60, 81), (65, 86), (70, 91), (85, 106), (90, 111), (95, 116), (110, 31), (115, 36), (120, 41)):
                    pos1_state = self.parent.state[pos1]
                    pos2_state = self.parent.state[pos2]

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
                    pos1_state = self.parent.state[pos1]
                    pos2_state = self.parent.state[pos2]
                    pos1_pos2_state = (pos1_state, pos2_state)
                    pos2_pos1_state = (pos2_state, pos1_state)

                    if pos1_pos2_state == new_LF:
                        self.parent.state[pos1] = 'L'
                        self.parent.state[pos2] = 'F'

                    elif pos2_pos1_state == new_LF:
                        self.parent.state[pos2] = 'L'
                        self.parent.state[pos1] = 'F'

                    elif pos1_pos2_state == new_RF:
                        self.parent.state[pos1] = 'R'
                        self.parent.state[pos2] = 'F'

                    elif pos2_pos1_state == new_RF:
                        self.parent.state[pos2] = 'R'
                        self.parent.state[pos1] = 'F'

                    elif pos1_pos2_state == new_LB:
                        self.parent.state[pos1] = 'L'
                        self.parent.state[pos2] = 'B'

                    elif pos2_pos1_state == new_LB:
                        self.parent.state[pos2] = 'L'
                        self.parent.state[pos1] = 'B'

                    elif pos1_pos2_state == new_RB:
                        self.parent.state[pos1] = 'R'
                        self.parent.state[pos2] = 'B'

                    elif pos2_pos1_state == new_RB:
                        self.parent.state[pos2] = 'R'
                        self.parent.state[pos1] = 'B'

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
                for side in self.sides_all:
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
                            state.append(self.parent.state[square_index])

                state = ''.join(state)

                # restore parent state to original
                self.parent.state = copy(original_state)
                self.parent.solution = copy(original_solution)

        elif self.state_type == '666-UD-inner-X-centers-stage':
            state = 'xxxxx' + self.parent.state[15] + self.parent.state[16] + 'xx' + self.parent.state[21] + self.parent.state[22]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[51] + self.parent.state[52] + 'xx' + self.parent.state[57] + self.parent.state[58]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[87] + self.parent.state[88] + 'xx' + self.parent.state[93] + self.parent.state[94]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[123] + self.parent.state[124] + 'xx' + self.parent.state[129] + self.parent.state[130]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[159] + self.parent.state[160] + 'xx' + self.parent.state[165] + self.parent.state[166]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[195] + self.parent.state[196] + 'xx' + self.parent.state[201] + self.parent.state[202]  + 'xxxxx'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-UD-oblique-edge-pairing':
            state = self.parent.state[9] + self.parent.state[10] +\
                    self.parent.state[14] + self.parent.state[17] +\
                    self.parent.state[20] + self.parent.state[23] +\
                    self.parent.state[27] + self.parent.state[28] +\
                    self.parent.state[45] + self.parent.state[46] +\
                    self.parent.state[50] + self.parent.state[53] +\
                    self.parent.state[56] + self.parent.state[59] +\
                    self.parent.state[63] + self.parent.state[64] +\
                    self.parent.state[81] + self.parent.state[82] +\
                    self.parent.state[86] + self.parent.state[89] +\
                    self.parent.state[92] + self.parent.state[95] +\
                    self.parent.state[99] + self.parent.state[100] +\
                    self.parent.state[117] + self.parent.state[118] +\
                    self.parent.state[122] + self.parent.state[125] +\
                    self.parent.state[128] + self.parent.state[131] +\
                    self.parent.state[135] + self.parent.state[136] +\
                    self.parent.state[153] + self.parent.state[154] +\
                    self.parent.state[158] + self.parent.state[161] +\
                    self.parent.state[164] + self.parent.state[167] +\
                    self.parent.state[171] + self.parent.state[172] +\
                    self.parent.state[189] + self.parent.state[190] +\
                    self.parent.state[194] + self.parent.state[197] +\
                    self.parent.state[200] + self.parent.state[203] +\
                    self.parent.state[207] + self.parent.state[208]
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-UD-oblique-edge-pairing-left-only':
            state = self.parent.state[9] + 'x' +\
                    'x' + self.parent.state[17] +\
                    self.parent.state[20] + 'x' +\
                    'x' + self.parent.state[28] +\
                    self.parent.state[45] + 'x' +\
                    'x' + self.parent.state[53] +\
                    self.parent.state[56] + 'x' +\
                    'x' + self.parent.state[64] +\
                    self.parent.state[81] + 'x' +\
                    'x' + self.parent.state[89] +\
                    self.parent.state[92] + 'x' +\
                    'x' + self.parent.state[100]+\
                    self.parent.state[117] + 'x' +\
                    'x' + self.parent.state[125] +\
                    self.parent.state[128] + 'x' +\
                    'x' + self.parent.state[136] +\
                    self.parent.state[153] + 'x' +\
                    'x' + self.parent.state[161] +\
                    self.parent.state[164] + 'x' +\
                    'x' + self.parent.state[172] +\
                    self.parent.state[189] + 'x' +\
                    'x' + self.parent.state[197] +\
                    self.parent.state[200] + 'x' +\
                    'x' + self.parent.state[208]

            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-UD-oblique-edge-pairing-right-only':
            state = 'x' + self.parent.state[10] +\
                    self.parent.state[14] + 'x' +\
                    'x' + self.parent.state[23] +\
                    self.parent.state[27] + 'x' +\
                    'x' + self.parent.state[46] +\
                    self.parent.state[50] + 'x' +\
                    'x' + self.parent.state[59] +\
                    self.parent.state[63] + 'x' +\
                    'x' + self.parent.state[82] +\
                    self.parent.state[86] + 'x' +\
                    'x' + self.parent.state[95] +\
                    self.parent.state[99] + 'x' +\
                    'x' + self.parent.state[118] +\
                    self.parent.state[122] + 'x' +\
                    'x' + self.parent.state[131] +\
                    self.parent.state[135] + 'x' +\
                    'x' + self.parent.state[154] +\
                    self.parent.state[158] + 'x' +\
                    'x' + self.parent.state[167] +\
                    self.parent.state[171] + 'x' +\
                    'x' + self.parent.state[190] +\
                    self.parent.state[194] + 'x' +\
                    'x' + self.parent.state[203] +\
                    self.parent.state[207] + 'x'

            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '666-LR-inner-X-centers-stage':
            state = 'xxxxx' + self.parent.state[15] + self.parent.state[16] + 'xx' + self.parent.state[21] + self.parent.state[22]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[51] + self.parent.state[52] + 'xx' + self.parent.state[57] + self.parent.state[58]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[87] + self.parent.state[88] + 'xx' + self.parent.state[93] + self.parent.state[94]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[123] + self.parent.state[124] + 'xx' + self.parent.state[129] + self.parent.state[130]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[159] + self.parent.state[160] + 'xx' + self.parent.state[165] + self.parent.state[166]  + 'xxxxx' +\
                    'xxxxx' + self.parent.state[195] + self.parent.state[196] + 'xx' + self.parent.state[201] + self.parent.state[202]  + 'xxxxx'
            state = state.replace('U', 'x').replace('L', 'L').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '666-LR-oblique-edge-pairing':
            state = self.parent.state[45] + self.parent.state[46] +\
                    self.parent.state[50] + self.parent.state[53] +\
                    self.parent.state[56] + self.parent.state[59] +\
                    self.parent.state[63] + self.parent.state[64] +\
                    self.parent.state[81] + self.parent.state[82] +\
                    self.parent.state[86] + self.parent.state[89] +\
                    self.parent.state[92] + self.parent.state[95] +\
                    self.parent.state[99] + self.parent.state[100] +\
                    self.parent.state[117] + self.parent.state[118] +\
                    self.parent.state[122] + self.parent.state[125] +\
                    self.parent.state[128] + self.parent.state[131] +\
                    self.parent.state[135] + self.parent.state[136] +\
                    self.parent.state[153] + self.parent.state[154] +\
                    self.parent.state[158] + self.parent.state[161] +\
                    self.parent.state[164] + self.parent.state[167] +\
                    self.parent.state[171] + self.parent.state[172]
            state = state.replace('U', 'x').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '666-LR-oblique-edge-pairing-left-only':
            state = self.parent.state[45] + 'x' +\
                    'x' + self.parent.state[53] +\
                    self.parent.state[56] + 'x' +\
                    'x' + self.parent.state[64] +\
                    self.parent.state[81] + 'x' +\
                    'x' + self.parent.state[89] +\
                    self.parent.state[92] + 'x' +\
                    'x' + self.parent.state[100] +\
                    self.parent.state[117] + 'x' +\
                    'x' + self.parent.state[125] +\
                    self.parent.state[128] + 'x' +\
                    'x' + self.parent.state[136] +\
                    self.parent.state[153] + 'x' +\
                    'x' + self.parent.state[161] +\
                    self.parent.state[164] + 'x' +\
                    'x' + self.parent.state[172]
            state = state.replace('U', 'x').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '666-LR-oblique-edge-pairing-right-only':
            state = 'x' + self.parent.state[46] +\
                    self.parent.state[50] + 'x' +\
                    'x' + self.parent.state[59] +\
                    self.parent.state[63] + 'x' +\
                    'x' + self.parent.state[82] +\
                    self.parent.state[86] + 'x' +\
                    'x' + self.parent.state[95] +\
                    self.parent.state[99] + 'x' +\
                    'x' + self.parent.state[118] +\
                    self.parent.state[122] + 'x' +\
                    'x' + self.parent.state[131] +\
                    self.parent.state[135] + 'x' +\
                    'x' + self.parent.state[154] +\
                    self.parent.state[158] + 'x' +\
                    'x' + self.parent.state[167] +\
                    self.parent.state[171] + 'x'

            state = state.replace('U', 'x').replace('F', 'x').replace('R', 'L').replace('B', 'x').replace('D', 'x')

        elif self.state_type == '777-UD-oblique-edge-pairing':
            state = 'x' + self.parent.state[10] + self.parent.state[11] + self.parent.state[12] + 'x' +\
                    self.parent.state[16] + 'xxx' + self.parent.state[20] +\
                    self.parent.state[23] + 'xxx' + self.parent.state[27] +\
                    self.parent.state[30] + 'xxx' + self.parent.state[34] +\
                    'x' + self.parent.state[38] + self.parent.state[39] + self.parent.state[40] + 'x' +\
                    'x' + self.parent.state[59] + self.parent.state[60] + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxx' + self.parent.state[69] +\
                    self.parent.state[72] + 'xxx' + self.parent.state[76] +\
                    self.parent.state[79] + 'xxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + self.parent.state[88] + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + self.parent.state[109] + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxx' + self.parent.state[118] +\
                    self.parent.state[121] + 'xxx' + self.parent.state[125] +\
                    self.parent.state[128] + 'xxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + self.parent.state[137] + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + self.parent.state[158] + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxx' + self.parent.state[167] +\
                    self.parent.state[170] + 'xxx' + self.parent.state[174] +\
                    self.parent.state[177] + 'xxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + self.parent.state[186] + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + self.parent.state[207] + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxx' + self.parent.state[216] +\
                    self.parent.state[219] + 'xxx' + self.parent.state[223] +\
                    self.parent.state[226] + 'xxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + self.parent.state[235] + self.parent.state[236] + 'x' +\
                    'x' + self.parent.state[255] + self.parent.state[256] + self.parent.state[257] + 'x' +\
                    self.parent.state[261] + 'xxx' + self.parent.state[265] +\
                    self.parent.state[268] + 'xxx' + self.parent.state[272] +\
                    self.parent.state[275] + 'xxx' + self.parent.state[279] +\
                    'x' + self.parent.state[283] + self.parent.state[284] + self.parent.state[285] + 'x'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-middle-only':
            state = 'xx' + self.parent.state[11] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[23] + 'xxx' + self.parent.state[27] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[39] + 'xx' +\
                    'xx' + self.parent.state[60] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[72] + 'xxx' + self.parent.state[76] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[88] + 'xx' +\
                    'xx' + self.parent.state[109] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[121] + 'xxx' + self.parent.state[125] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[137] + 'xx' +\
                    'xx' + self.parent.state[158] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[170] + 'xxx' + self.parent.state[174] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[186] + 'xx' +\
                    'xx' + self.parent.state[207] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[219] + 'xxx' + self.parent.state[223] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[235] + 'xx' +\
                    'xx' + self.parent.state[256] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[268] + 'xxx' + self.parent.state[272] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[284] + 'xx'

            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-outside-only':
            state = 'x' + self.parent.state[10] + 'x' + self.parent.state[12] + 'x' +\
                    self.parent.state[16] + 'xxx' + self.parent.state[20] +\
                    'xxxxx' +\
                    self.parent.state[30] + 'xxx' + self.parent.state[34] +\
                    'x' + self.parent.state[38] + 'x' + self.parent.state[40] + 'x' +\
                    'x' + self.parent.state[59] + 'x' + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxx' + self.parent.state[69] +\
                    'xxxxx' +\
                    self.parent.state[79] + 'xxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + 'x' + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + 'x' + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxx' + self.parent.state[118] +\
                    'xxxxx' +\
                    self.parent.state[128] + 'xxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + 'x' + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + 'x' + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxx' + self.parent.state[167] +\
                    'xxxxx' +\
                    self.parent.state[177] + 'xxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + 'x' + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + 'x' + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxx' + self.parent.state[216] +\
                    'xxxxx' +\
                    self.parent.state[226] + 'xxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + 'x' + self.parent.state[236] + 'x' +\
                    'x' + self.parent.state[255] + 'x' + self.parent.state[257] + 'x' +\
                    self.parent.state[261] + 'xxx' + self.parent.state[265] +\
                    'xxxxx' +\
                    self.parent.state[275] + 'xxx' + self.parent.state[279] +\
                    'x' + self.parent.state[283] + 'x' + self.parent.state[285] + 'x'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-left-only':
            state = 'x' + self.parent.state[10] + 'xxx' +\
                    'xxxx' + self.parent.state[20] +\
                    'xxxxx' +\
                    self.parent.state[30] + 'xxxx' +\
                    'xxx' + self.parent.state[40] + 'x' +\
                    'x' + self.parent.state[59] + 'xxx' +\
                    'xxxx' + self.parent.state[69] +\
                    'xxxxx' +\
                    self.parent.state[79] + 'xxxx' +\
                    'xxx' + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + 'xxx' +\
                    'xxxx' + self.parent.state[118] +\
                    'xxxxx' +\
                    self.parent.state[128] + 'xxxx' +\
                    'xxx' + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + 'xxx' +\
                    'xxxx' + self.parent.state[167] +\
                    'xxxxx' +\
                    self.parent.state[177] + 'xxxx' +\
                    'xxx' + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + 'xxx' +\
                    'xxxx' + self.parent.state[216] +\
                    'xxxxx' +\
                    self.parent.state[226] + 'xxxx' +\
                    'xxx' + self.parent.state[236] + 'x' +\
                    'x' + self.parent.state[255] + 'xxx' +\
                    'xxxx' + self.parent.state[265] +\
                    'xxxxx' +\
                    self.parent.state[275] + 'xxxx' +\
                    'xxx' + self.parent.state[285] + 'x'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-oblique-edge-pairing-right-only':
            state = 'xxx' + self.parent.state[12] + 'x' +\
                    self.parent.state[16] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[34] +\
                    'x' + self.parent.state[38] + 'xxx' +\
                    'xxx' + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + 'xxx' +\
                    'xxx' + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + 'xxx' +\
                    'xxx' + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + 'xxx' +\
                    'xxx' + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + 'xxx' +\
                    'xxx' + self.parent.state[257] + 'x' +\
                    self.parent.state[261] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[279] +\
                    'x' + self.parent.state[283] + 'xxx'
            state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == '777-UD-centers-reduce-to-555':
            state = 'x' + self.parent.state[10] + self.parent.state[11] + self.parent.state[12] + 'x' +\
                    self.parent.state[16] + 'xxx' + self.parent.state[20] +\
                    self.parent.state[23] + 'xxx' + self.parent.state[27] +\
                    self.parent.state[30] + 'xxx' + self.parent.state[34] +\
                    'x' + self.parent.state[38] + self.parent.state[39] + self.parent.state[40] + 'x' +\
                    'x' + self.parent.state[59] + self.parent.state[60] + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxx' + self.parent.state[69] +\
                    self.parent.state[72] + 'xxx' + self.parent.state[76] +\
                    self.parent.state[79] + 'xxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + self.parent.state[88] + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + self.parent.state[109] + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxx' + self.parent.state[118] +\
                    self.parent.state[121] + 'xxx' + self.parent.state[125] +\
                    self.parent.state[128] + 'xxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + self.parent.state[137] + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + self.parent.state[158] + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxx' + self.parent.state[167] +\
                    self.parent.state[170] + 'xxx' + self.parent.state[174] +\
                    self.parent.state[177] + 'xxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + self.parent.state[186] + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + self.parent.state[207] + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxx' + self.parent.state[216] +\
                    self.parent.state[219] + 'xxx' + self.parent.state[223] +\
                    self.parent.state[226] + 'xxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + self.parent.state[235] + self.parent.state[236] + 'x' +\
                    'x' + self.parent.state[255] + self.parent.state[256] + self.parent.state[257] + 'x' +\
                    self.parent.state[261] + 'xxx' + self.parent.state[265] +\
                    self.parent.state[268] + 'xxx' + self.parent.state[272] +\
                    self.parent.state[275] + 'xxx' + self.parent.state[279] +\
                    'x' + self.parent.state[283] + self.parent.state[284] + self.parent.state[285] + 'x'

        elif self.state_type == '777-UD-centers-reduce-to-555-oblique-only':
            state = 'x' + self.parent.state[10] + self.parent.state[11] + self.parent.state[12] + 'x' +\
                    self.parent.state[16] + 'xxx' + self.parent.state[20] +\
                    self.parent.state[23] + 'xxx' + self.parent.state[27] +\
                    self.parent.state[30] + 'xxx' + self.parent.state[34] +\
                    'x' + self.parent.state[38] + self.parent.state[39] + self.parent.state[40] + 'x' +\
                    'x' + self.parent.state[59] + self.parent.state[60] + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxx' + self.parent.state[69] +\
                    self.parent.state[72] + 'xxx' + self.parent.state[76] +\
                    self.parent.state[79] + 'xxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + self.parent.state[88] + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + self.parent.state[109] + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxx' + self.parent.state[118] +\
                    self.parent.state[121] + 'xxx' + self.parent.state[125] +\
                    self.parent.state[128] + 'xxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + self.parent.state[137] + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + self.parent.state[158] + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxx' + self.parent.state[167] +\
                    self.parent.state[170] + 'xxx' + self.parent.state[174] +\
                    self.parent.state[177] + 'xxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + self.parent.state[186] + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + self.parent.state[207] + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxx' + self.parent.state[216] +\
                    self.parent.state[219] + 'xxx' + self.parent.state[223] +\
                    self.parent.state[226] + 'xxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + self.parent.state[235] + self.parent.state[236] + 'x' +\
                    'x' + self.parent.state[255] + self.parent.state[256] + self.parent.state[257] + 'x' +\
                    self.parent.state[261] + 'xxx' + self.parent.state[265] +\
                    self.parent.state[268] + 'xxx' + self.parent.state[272] +\
                    self.parent.state[275] + 'xxx' + self.parent.state[279] +\
                    'x' + self.parent.state[283] + self.parent.state[284] + self.parent.state[285] + 'x'

        elif self.state_type == '777-UD-centers-reduce-to-555-center-only':
            state = 'xxxxx' +\
                    'x' + self.parent.state[17] + self.parent.state[18] + self.parent.state[19] + 'x' +\
                    'x' + self.parent.state[24] + self.parent.state[25] + self.parent.state[26] + 'x' +\
                    'x' + self.parent.state[31] + self.parent.state[32] + self.parent.state[33] + 'x' +\
                    'xxxxx' +\
                    'xxxxx' +\
                    'x' + self.parent.state[66] + self.parent.state[67] + self.parent.state[68] + 'x' +\
                    'x' + self.parent.state[73] + self.parent.state[74] + self.parent.state[75] + 'x' +\
                    'x' + self.parent.state[80] + self.parent.state[81] + self.parent.state[82] + 'x' +\
                    'xxxxx' +\
                    'xxxxx' +\
                    'x' + self.parent.state[115] + self.parent.state[116] + self.parent.state[117] + 'x' +\
                    'x' + self.parent.state[122] + self.parent.state[123] + self.parent.state[124] + 'x' +\
                    'x' + self.parent.state[129] + self.parent.state[130] + self.parent.state[131] + 'x' +\
                    'xxxxx' +\
                    'xxxxx' +\
                    'x' + self.parent.state[164] + self.parent.state[165] + self.parent.state[166] + 'x' +\
                    'x' + self.parent.state[171] + self.parent.state[172] + self.parent.state[173] + 'x' +\
                    'x' + self.parent.state[178] + self.parent.state[179] + self.parent.state[180] + 'x' +\
                    'xxxxx' +\
                    'xxxxx' +\
                    'x' + self.parent.state[213] + self.parent.state[214] + self.parent.state[215] + 'x' +\
                    'x' + self.parent.state[220] + self.parent.state[221] + self.parent.state[222] + 'x' +\
                    'x' + self.parent.state[227] + self.parent.state[228] + self.parent.state[229] + 'x' +\
                    'xxxxx' +\
                    'xxxxx' +\
                    'x' + self.parent.state[262] + self.parent.state[263] + self.parent.state[264] + 'x' +\
                    'x' + self.parent.state[269] + self.parent.state[270] + self.parent.state[271] + 'x' +\
                    'x' + self.parent.state[276] + self.parent.state[277] + self.parent.state[278] + 'x' +\
                    'xxxxx'

        elif self.state_type == '777-LR-oblique-edge-pairing':
            state = 'x' + self.parent.state[59] + self.parent.state[60] + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxx' + self.parent.state[69] +\
                    self.parent.state[72] + 'xxx' + self.parent.state[76] +\
                    self.parent.state[79] + 'xxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + self.parent.state[88] + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + self.parent.state[109] + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxx' + self.parent.state[118] +\
                    self.parent.state[121] + 'xxx' + self.parent.state[125] +\
                    self.parent.state[128] + 'xxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + self.parent.state[137] + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + self.parent.state[158] + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxx' + self.parent.state[167] +\
                    self.parent.state[170] + 'xxx' + self.parent.state[174] +\
                    self.parent.state[177] + 'xxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + self.parent.state[186] + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + self.parent.state[207] + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxx' + self.parent.state[216] +\
                    self.parent.state[219] + 'xxx' + self.parent.state[223] +\
                    self.parent.state[226] + 'xxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + self.parent.state[235] + self.parent.state[236] + 'x'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-middle-only':
            state = 'xx' + self.parent.state[60] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[72] + 'xxx' + self.parent.state[76] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[88] + 'xx' +\
                    'xx' + self.parent.state[109] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[121] + 'xxx' + self.parent.state[125] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[137] + 'xx' +\
                    'xx' + self.parent.state[158] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[170] + 'xxx' + self.parent.state[174] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[186] + 'xx' +\
                    'xx' + self.parent.state[207] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[219] + 'xxx' + self.parent.state[223] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[235] + 'xx'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-outside-only':
            state = 'x' + self.parent.state[59] + 'x' + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxx' + self.parent.state[69] +\
                    'xxxxx' +\
                    self.parent.state[79] + 'xxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + 'x' + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + 'x' + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxx' + self.parent.state[118] +\
                    'xxxxx' +\
                    self.parent.state[128] + 'xxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + 'x' + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + 'x' + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxx' + self.parent.state[167] +\
                    'xxxxx' +\
                    self.parent.state[177] + 'xxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + 'x' + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + 'x' + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxx' + self.parent.state[216] +\
                    'xxxxx' +\
                    self.parent.state[226] + 'xxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + 'x' + self.parent.state[236] + 'x'

            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-left-only':
            state = 'x' + self.parent.state[59] + 'xxx' +\
                    'xxxx' + self.parent.state[69] +\
                    'xxxxx' +\
                    self.parent.state[79] + 'xxxx' +\
                    'xxx' + self.parent.state[89] + 'x' +\
                    'x' + self.parent.state[108] + 'xxx' +\
                    'xxxx' + self.parent.state[118] +\
                    'xxxxx' +\
                    self.parent.state[128] + 'xxxx' +\
                    'xxx' + self.parent.state[138] + 'x' +\
                    'x' + self.parent.state[157] + 'xxx' +\
                    'xxxx' + self.parent.state[167] +\
                    'xxxxx' +\
                    self.parent.state[177] + 'xxxx' +\
                    'xxx' + self.parent.state[187] + 'x' +\
                    'x' + self.parent.state[206] + 'xxx' +\
                    'xxxx' + self.parent.state[216] +\
                    'xxxxx' +\
                    self.parent.state[226] + 'xxxx' +\
                    'xxx' + self.parent.state[236] + 'x'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-LR-oblique-edge-pairing-right-only':
            state = 'xxx' + self.parent.state[61] + 'x' +\
                    self.parent.state[65] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[83] +\
                    'x' + self.parent.state[87] + 'xxx' +\
                    'xxx' + self.parent.state[110] + 'x' +\
                    self.parent.state[114] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[132] +\
                    'x' + self.parent.state[136] + 'xxx' +\
                    'xxx' + self.parent.state[159] + 'x' +\
                    self.parent.state[163] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[181] +\
                    'x' + self.parent.state[185] + 'xxx' +\
                    'xxx' + self.parent.state[208] + 'x' +\
                    self.parent.state[212] + 'xxxx' +\
                    'xxxxx' +\
                    'xxxx' + self.parent.state[230] +\
                    'x' + self.parent.state[234] + 'xxx'
            state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

        elif self.state_type == '777-UD-centers-oblique-edges-solve-center-only':
            state = []

            for side in self.sides_UD:
                for square_index in side.center_pos:
                    if square_index in (17, 19, 31, 33, 262, 264, 276, 278,
                                        18, 24, 26, 32, 263, 269, 271, 277):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-UD-centers-oblique-edges-solve-edges-only':
            state = []

            for side in self.sides_UD:
                for square_index in side.center_pos:
                    if square_index in (10, 20, 40, 30, 255, 265, 285, 275,
                                        11, 27, 39, 23, 256, 272, 284, 268,
                                        12, 34, 38, 16, 257, 279, 283, 261):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LR-centers-oblique-edges-solve-center-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 67, 68, 73, 74, 75, 80, 81, 82,
                                        164, 165, 166, 171, 172, 173, 178, 179, 180):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LR-centers-oblique-edges-solve-edges-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (59, 60, 61, 65, 72, 79, 69, 76, 83, 87, 88, 89,
                                        157, 158, 159, 163, 170, 177, 167, 174, 181, 185, 186, 187):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-FB-centers-oblique-edges-solve-center-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (115, 116, 117, 122, 123, 124, 129, 130, 131,
                                        213, 214, 215, 220, 221, 222, 227, 228, 229):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-FB-centers-oblique-edges-solve-edges-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (108, 109, 110, 114, 121, 128, 118, 125, 132, 136, 137, 138,
                                        206, 207, 208, 212, 219, 226, 216, 223, 230, 234, 235, 236):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 67, 68, 73, 74, 75, 80, 81, 82,
                                        115, 116, 117, 122, 123, 124, 129, 130, 131,
                                        213, 214, 215, 220, 221, 222, 227, 228, 229,
                                        164, 165, 166, 171, 172, 173, 178, 179, 180):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-left-oblique-edge-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        59, 69, 79, 89, 108, 118, 128, 138, 157, 167, 177, 187, 206, 216, 226, 236):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-middle-oblique-edge-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-right-oblique-edge-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        61, 83, 87, 65, 110, 132, 136, 114, 159, 181, 185, 163, 208, 230, 234, 212):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-t-center-left-oblique-edge-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        59, 69, 79, 89, 108, 118, 128, 138, 157, 167, 177, 187, 206, 216, 226, 236):

                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-t-center-middle-oblique-edge-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235):

                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-middle-oblique-edge-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-left-middle-oblique-edge-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (66, 68, 74, 80, 82, 115, 117, 123, 129, 131, 164, 166, 172, 178, 180, 213, 215, 221, 227, 229,
                                        67, 73, 74, 75, 81, 116, 122, 123, 124, 130, 165, 171, 172, 173, 179, 214, 220, 221, 222, 228,
                                        60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235,
                                        59, 69, 79, 89, 108, 118, 128, 138, 157, 167, 177, 187, 206, 216, 226, 236):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-left-right-oblique-edges-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (59, 61, 65, 79, 69, 83, 87, 89,
                                        157, 159, 163, 177, 167, 181, 185, 187,
                                        108, 110, 114, 128, 118, 132, 136, 138,
                                        206, 208, 212, 226, 216, 230, 234, 236):

                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

        elif self.state_type == '777-LFRB-centers-oblique-edges-solve-middle-right-oblique-edges-only':
            state = []

            for side in self.sides_LFRB:
                for square_index in side.center_pos:
                    if square_index in (60, 72, 76, 88, 109, 121, 125, 137, 158, 170, 174, 186, 207, 219, 223, 235,
                                        61, 83, 87, 65, 110, 132, 136, 114, 159, 181, 185, 163, 208, 230, 234, 212):
                        state.append(self.parent.state[square_index])
                    else:
                        state.append('x')

            state = ''.join(state)

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

        #assert state_to_find, "Was asked to find %s" % state_to_find
        #assert left <= right, "Invalid left %s vs. right %s (left must be <= right)" % (left, right)
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
                log.info("%s left %d, right %d, mid %d, linecount %d, line '%s'" % (self.filename, left, right, mid, self.linecount, line))
                raise e
            '''
            line = fh.readline()
            state = line[0:state_width]

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

    def file_binary_search_multiple_keys(self, fh, states_to_find, debug=False):
        global fbsmk_count
        fbsmk_count += 1
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

        if debug:
            log.info("%s find %d states, %d are not cached" % (self.filename, original_states_to_find_count, states_to_find_count))

        first_index = 0
        last_index = states_to_find_count - 1
        linecount = self.linecount
        cache = self.cache

        while states_to_find_count:
            first_state_to_find = states_to_find[first_index]
            last_state_to_find = states_to_find[last_index]

            if states_to_find_count == 1:
                (_, value) = self.file_binary_search_guts(fh, first_state_to_find, min_left, max_right)
                results[first_state_to_find] = value
                cache[first_state_to_find] = value

                if debug:
                    log.info("%s done" % self.filename)
                return results

            # We sorted states_to_find so find the first state and its linenumber (or the linenumber
            # where it would be if it were there) and remember that linenumber as the furthest
            # left we ever need to look in the file when looking for other states.
            (linenumber, value) = self.file_binary_search_guts(fh, first_state_to_find, min_left, max_right)
            results[first_state_to_find] = value
            cache[first_state_to_find] = value

            if value:
                min_left = linenumber
            else:
                if linenumber:
                    min_left = linenumber - 1
                else:
                    min_left = 0

            # Now do the same with the last state to determine the furthest right we
            # ever need look when looking for other states
            (linenumber, value) = self.file_binary_search_guts(fh, last_state_to_find, min_left, max_right)
            results[last_state_to_find] = value
            cache[last_state_to_find] = value

            if value:
                max_right = linenumber
            else:
                max_right = min(linenumber + 1, linecount)

            if debug:
                log.info("%s first state %s, last state %s, min_left %d, max_right %d" % (self.filename, first_state_to_find, last_state_to_find, min_left, max_right))

            first_index += 1
            last_index -= 1
            states_to_find_count -= 2

        if debug:
            log.info("%s done" % self.filename)
        return results

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
                raise NoSteps("%s: state %s does not have steps" % (self.filename, state))

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

    def ida_search(self, cost_to_here, threshold, prev_step, prev_state, prev_solution):

        # We are above the theshold no matter what the prune table costs are
        if (cost_to_here + 1) > threshold:
            return False

        # Build a list of the steps we need to explore
        step_sequences_to_try = []

        for step in self.moves_all:

            if step in self.moves_illegal:
                continue

            # If this step cancels out the previous step then don't bother with this branch
            if steps_cancel_out(prev_step, step):
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

        # Now try each of those steps and record the (state, step, cost_to_goal) tuple
        # and build a list of states that we need to binary search for
        states_to_check = []
        state_step = []
        pt_states_to_check = {}
        costs_to_goal = {}
        first_step = True
        pt_costs_by_step = {}

        for step_sequence in step_sequences_to_try:
            self.ida_count += 1
            self.parent.state = copy(prev_state)
            self.parent.solution = copy(prev_solution)
            state_original = copy(self.parent.state)

            for step in step_sequence.split():
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

            # get the current state of the cube and the cost_to_goal
            state = self.state()

            pt_costs_by_step[step_sequence] = []

            for pt in self.prune_tables:
                if first_step:
                    pt_states_to_check[pt.filename] = []

                pt_state = pt.state()
                pt_states_to_check[pt.filename].append(pt_state)
                pt_costs_by_step[step_sequence].append((pt.filename, pt_state))

            first_step = False
            state_step.append((state, step_sequence, copy(self.parent.state), copy(self.parent.solution)))
            states_to_check.append(state)

        #states_to_check = sorted(states_to_check)
        #log.info("states_to_check: %s" % pformat(states_to_check))
        #log.info("state_step:\n%s\n" % pformat(state_step))
        #log.info("pt_states_to_check:\n%s\n" % pformat(pt_states_to_check))
        #log.info("pt_costs_by_step:\n%s\n" % pformat(pt_costs_by_step))
        pt_costs = {}

        for pt in self.prune_tables:
            states_to_find = pt_states_to_check[pt.filename]

            with open(pt.filename, 'r') as fh:
                pt_costs[pt.filename] = pt.file_binary_search_multiple_keys(fh, states_to_find)

        #log.info("pt_costs:\n%s\n" % pformat(pt_costs))

        # This will do a multi-key binary search of all states_to_check
        steps_for_states = self.steps(states_to_check)
        #log.info("steps_for_states:\n%s\n" % pformat(steps_for_states))

        for (state, step_sequence, parent_state, parent_solution) in state_step:
            steps = steps_for_states[state]
            self.parent.state = parent_state
            self.parent.solution = parent_solution

            # If there is an entry for 'state' in the lookup table then we have
            # found what we were looking for.  Apply the step needed to put the
            # cube in the state that is in the lookup tables and then apply the
            # 'steps' for this state in the lookup table.
            if steps:
                #log.info("IDA match at %s, cost_to_here %d, cost_to_goal %d, threshold %d, state %s, step sequence %s, steps %s" %
                #        (step, cost_to_here, cost_to_goal, threshold, state, step_sequence, steps))
                for step in steps:
                    self.parent.rotate(step)

                return True

            # extract cost_to_goal from the pt_costs dictionary
            cost_to_goal = 0

            for (pt_filename, pt_state) in pt_costs_by_step[step_sequence]:
                pt_steps = pt_costs[pt_filename][pt_state]

                if pt_steps is None:
                    raise SolveError("%s: prune table %s does not have %s" % (self, pt_filename, pt_state))

                len_pt_steps = len(pt_steps)

                if len_pt_steps > cost_to_goal:
                    cost_to_goal = len_pt_steps

            if (cost_to_here + 1 + cost_to_goal) > threshold:
                #log.info("prune IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                #        (step, cost_to_here, cost_to_goal, threshold))
                self.ida_prune_count += 1
                continue

            # speed experiment...this reduces the time for IDA search by about 20%
            magic_tuple = (cost_to_here + 1, threshold, step_sequence, state)

            if magic_tuple in self.visited_states:
                continue
            self.visited_states.add(magic_tuple)

            state_end_of_this_step = copy(self.parent.state)
            solution_end_of_this_step = copy(self.parent.solution)

            # We need to explore this branch further, make a recursive ida_search() call
            if self.ida_search(cost_to_here + 1, threshold, step_sequence, state_end_of_this_step, solution_end_of_this_step):
                return True

        return False

    def ida_stage(self):
        assert self.state_target is not None, "state_target is None"

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

        if self.threshold_to_shortcut:

            for threshold in range(1, self.threshold_to_shortcut):
                self.visited_states = set()

                if self.ida_search(0, threshold, None, original_state, original_solution):
                    log.info("%s: IDA found match(1), count %d, pruned %d" % (self, self.ida_count, self.ida_prune_count))
                    return
                log.info("%s: IDA threshold %d, count %d, pruned %d" % (self, threshold, self.ida_count, self.ida_prune_count))

            else:
                # restore parent state to original
                self.parent.state = copy(original_state)
                self.parent.solution = copy(original_solution)

                first_pt = self.prune_tables[0]
                log.info("%s: use prune table %s to shortcut IDA search" % (self, first_pt))
                first_pt.solve()
                self.ida_count = 0

                state = self.state()

                if state == self.state_target:
                    log.info("state %s vs state_target %s" % (state, self.state_target))
                    return

                # save cube state
                original_state = copy(self.parent.state)
                original_solution = copy(self.parent.solution)

                for threshold in range(1, 20):
                    self.visited_states = set()

                    if self.ida_search(0, threshold, None, original_state, original_solution):
                        log.info("%s: IDA found match(2), count %d, pruned %d" % (self, self.ida_count, self.ida_prune_count))
                        return
                    log.info("%s: IDA threshold %d, count %d, pruned %d" % (self, threshold, self.ida_count, self.ida_prune_count))
                else:
                    raise SolveError("%s FAILED for state %s" % (self, self.state()))

        else:
            for threshold in range(1, 20):
                self.visited_states = set()

                if self.ida_search(0, threshold, None, original_state, original_solution):
                    log.info("%s: IDA found match(3), count %d, pruned %d" % (self, self.ida_count, self.ida_prune_count))
                    return
                log.info("%s: IDA threshold %d, count %d, pruned %d" % (self, threshold, self.ida_count, self.ida_prune_count))
                self.ida_count = 0
                self.ida_prune_count = 0
            else:
                raise SolveError("%s FAILED for state %s" % (self, self.state()))

    def ida_stage_new(self):
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
            log.info("%s: IDA threshold %d start" % (self, threshold))

            # Build a list of moves we can do 1 move deep
            # Build a list of moves we can do 2 moves deep, this must build on the 1 move deep list
            # Build a list of moves we can do 3 moves deep, this must build on the 2 move deep list
            # etc
            prev_step_sequences = []
            already_checked = set()

            for max_step_count in range(1, threshold+1):
                step_sequences = self.ida_steps_list(prev_step_sequences, threshold, max_step_count)
                # log.info("%s: step_sequences %s" % (self, pformat(step_sequences)))

                states_to_check = []
                pt_states_to_check = {}
                state_step = []
                costs_to_goal = {}
                pt_costs_by_step = {}

                for pt in self.prune_tables:
                    pt_states_to_check[pt.filename] = []

                # Now rotate all of these moves and get the resulting cube for each
                # Do one gigantic binary search
                for step_sequence in step_sequences:

                    if step_sequence in already_checked:
                        continue
                    already_checked.add(step_sequence)

                    self.parent.state = copy(original_state)
                    self.parent.solution = copy(original_solution)
                    self.ida_count += 1

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

                        log.warning("%s: IDA found match(4), count %d" % (self, self.ida_count))
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

                #log.info("%s: IDA threshold %d (max step %d), evaluated %d, pruned %d, keep %d" %\
                #    (self, threshold, max_step_count, self.ida_count, self.ida_prune_count, len(step_sequences_within_cost)))
                self.ida_count = 0
                self.ida_prune_count = 0

        # we should never get to here
        raise SolveError("%s FAILED for state %s" % (self, self.state()))

    def solve(self):
        assert self.state_target is not None, "state_target is None"

        #if self.ida_stage():
        if self.ida_stage_new():
            return

        LookupTable.solve(self)
