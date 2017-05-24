
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver.RubiksSide import SolveError
import logging
import math
import os


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

    def __init__(self, parent, filename, state_type, state_target, state_hex=False):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.sides_LFRB = (self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB)
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

        elif self.state_type == 'LR-centers-stage':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LFRB for square_index in side.center_pos])
            state = state.replace('F', 'x').replace('R', 'L').replace('B', 'x')

        elif self.state_type == 'LR-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LR for square_index in side.center_pos])

        elif self.state_type == 'LFRB-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_LFRB for square_index in side.center_pos])

        elif self.state_type == 'FB-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_FB for square_index in side.center_pos])

        elif self.state_type == 'ULFRBD-centers-solve':
            state = ''.join([self.parent.state[square_index] for side in self.sides_all for square_index in side.center_pos])

        elif self.state_type == 'UD-T-centers-stage':
            # This is currently hard coded for 5x5x5
            state = []

            for side in self.sides_all:

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
            state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        elif self.state_type == 'UD-X-centers-stage':
            # This is currently hard coded for 5x5x5
            state = []

            for side in self.sides_all:

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

                # dwalton
                self.parent.print_cube()

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
                    'xx' + self.parent.state[87] + self.parent.state[88] + 'xx' +\
                    'xx' + self.parent.state[109] + 'xx' +\
                    'xxxxx' +\
                    self.parent.state[121] + 'xxx' + self.parent.state[125] +\
                    'xxxxx' +\
                    'xx' + self.parent.state[136] + self.parent.state[137] + 'xx' +\
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

        else:
            raise ImplementThis("state_type %s" % self.state_type)

        if self.state_hex:
            state = convert_state_to_hex(state)

        return state

    def steps(self, state=None):
        """
        Return the steps found in the lookup table for the current cube state
        """
        if state is None:
            state = self.state()
        #log.info("%s state %s" % (self, state))

        with open(self.filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (_, steps) = line.strip().split(':')
                #log.info("%s found state: %d steps in, steps %s" % (self, len(self.parent.solution), steps))
                return steps.split()
        return []

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
        LookupTable.__init__(self, parent, filename, state_type, state_target, state_hex)
        self.moves_all = moves_all
        self.moves_illegal = moves_illegal
        self.ida_count = 0
        self.prune_tables = prune_tables
        self.visited_states = set()

    def ida_cost(self):
        costs = []

        for pt in self.prune_tables:
            costs.append(pt.steps_length())

        return max(costs)

    def ida_search(self, cost_to_here, threshold, prev_step, prev_state, prev_solution):

        for step in self.moves_all:

            if step in self.moves_illegal:
                continue

            # If this step cancels out the previous step then don't bother with this branch
            if steps_cancel_out(prev_step, step):
                continue

            self.parent.state = copy(prev_state)
            self.parent.solution = copy(prev_solution)
            self.parent.rotate(step)
            self.ida_count += 1
            # assert cost_to_here+1 == len(self.parent.solution), "cost_to_here %d, solution %s" % (cost_to_here, ' '.join(self.parent.solution))

            # Do we have the cube in a state where there is a match in the lookup table?
            state = self.state()
            steps = self.steps(state)
            if steps:
                #log.info("match IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                #        (step, cost_to_here, cost_to_goal, threshold))
                for step in steps:
                    self.parent.rotate(step)
                return True

            cost_to_goal = self.ida_cost()

            if (cost_to_here + 1 + cost_to_goal) > threshold:
                #log.info("prune IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                #        (step, cost_to_here, cost_to_goal, threshold))
                continue

            # speed experiment...this should cut out some ida_search calls
            if state in self.visited_states:
                continue
            self.visited_states.add(state)

            state_end_of_this_step = copy(self.parent.state)
            solution_end_of_this_step = copy(self.parent.solution)

            if self.ida_search(cost_to_here + 1, threshold, step, state_end_of_this_step, solution_end_of_this_step):
                return True

        return False

    def solve(self):
        assert self.state_target is not None, "state_target is None"

        while True:
            state = self.state()

            if state == self.state_target:
                break

            steps = self.steps()
            log.info("state %s vs state_target %s" % (state, self.state_target))

            if steps:
                for step in steps:
                    self.parent.rotate(step)
            else:
                # If we are here (odds are very high we will be) it means that the current
                # cube state was not in the lookup table.  We must now perform an IDA search
                # until we find a sequence of moves that takes us to a state that IS in the
                # lookup table.

                # save cube state
                original_state = copy(self.parent.state)
                original_solution = copy(self.parent.solution)

                for threshold in range(1, 20):
                    log.info("%s: IDA threshold %d, count %d" % (self, threshold, self.ida_count))
                    if self.ida_search(0, threshold, None, original_state, original_solution):
                        break
                else:
                    raise SolveError("%s FAILED" % self)
