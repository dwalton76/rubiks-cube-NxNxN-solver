
import datetime as dt
from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.rotate_xxx import rotate_222, rotate_444, rotate_555, rotate_666, rotate_777
import gc
import json
import logging
import math
import os
import subprocess
import sys


log = logging.getLogger(__name__)

# NOTE: always use list slicing instead of copy for lists
# See the 3rd post here:
# https://stackoverflow.com/questions/2612802/how-to-clone-or-copy-a-list
# For 100k list copy.copy() took 1.488s where slicing took 0.039s...that is a 38x improvement

class ImplementThis(Exception):
    pass


class NoSteps(Exception):
    pass


class NoIDASolution(Exception):
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


def convert_state_to_hex(state, hex_width):
    hex_state = hex(int(state, 2))[2:]

    if hex_state.endswith('L'):
        hex_state = hex_state[:-1]

    return hex_state.zfill(hex_width)


def get_555_UD_centers_stage_state(parent_state):
    state = ''.join([parent_state[7], parent_state[8], parent_state[9],
                     parent_state[12], parent_state[13], parent_state[14],
                     parent_state[17], parent_state[18], parent_state[19],
                     parent_state[32], parent_state[33], parent_state[34],
                     parent_state[37], parent_state[38], parent_state[39],
                     parent_state[42], parent_state[43], parent_state[44],
                     parent_state[57], parent_state[58], parent_state[59],
                     parent_state[62], parent_state[63], parent_state[64],
                     parent_state[67], parent_state[68], parent_state[69],
                     parent_state[82], parent_state[83], parent_state[84],
                     parent_state[87], parent_state[88], parent_state[89],
                     parent_state[92], parent_state[93], parent_state[94],
                     parent_state[107], parent_state[108], parent_state[109],
                     parent_state[112], parent_state[113], parent_state[114],
                     parent_state[117], parent_state[118], parent_state[119],
                     parent_state[132], parent_state[133], parent_state[134],
                     parent_state[137], parent_state[138], parent_state[139],
                     parent_state[142], parent_state[143], parent_state[144]])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_555_UD_T_centers_stage_state(parent_state):
    state = ''.join(['x', parent_state[8], 'x', parent_state[12], parent_state[13], parent_state[14], 'x', parent_state[18], 'xx', parent_state[33], 'x', parent_state[37], parent_state[38], parent_state[39], 'x', parent_state[43], 'xx', parent_state[58], 'x', parent_state[62], parent_state[63], parent_state[64], 'x', parent_state[68], 'xx', parent_state[83], 'x', parent_state[87], parent_state[88], parent_state[89], 'x', parent_state[93], 'xx', parent_state[108], 'x', parent_state[112], parent_state[113], parent_state[114], 'x', parent_state[118], 'xx', parent_state[133], 'x', parent_state[137], parent_state[138], parent_state[139], 'x', parent_state[143], 'x'])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_555_UD_X_centers_stage_state(parent_state):
    state = ''.join([parent_state[7], 'x', parent_state[9], 'x', parent_state[13], 'x', parent_state[17], 'x', parent_state[19], parent_state[32], 'x', parent_state[34], 'x', parent_state[38], 'x', parent_state[42], 'x', parent_state[44], parent_state[57], 'x', parent_state[59], 'x', parent_state[63], 'x', parent_state[67], 'x', parent_state[69], parent_state[82], 'x', parent_state[84], 'x', parent_state[88], 'x', parent_state[92], 'x', parent_state[94], parent_state[107], 'x', parent_state[109], 'x', parent_state[113], 'x', parent_state[117], 'x', parent_state[119], parent_state[132], 'x', parent_state[134], 'x', parent_state[138], 'x', parent_state[142], 'x', parent_state[144]])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


state_functions = {
    '555-UD-centers-stage' : get_555_UD_centers_stage_state,
    '555-UD-T-centers-stage' : get_555_UD_T_centers_stage_state,
    '555-UD-X-centers-stage' : get_555_UD_X_centers_stage_state
}


class LookupTable(object):

    def __init__(self, parent, filename, state_type, state_target, state_hex, prune_table):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.sides_LFRB = (self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB)
        self.sides_UFDB = (self.parent.sideU, self.parent.sideF, self.parent.sideD, self.parent.sideB)
        self.sides_UD = (self.parent.sideU, self.parent.sideD)
        self.sides_LR = (self.parent.sideL, self.parent.sideR)
        self.sides_FB = (self.parent.sideF, self.parent.sideB)
        self.filename = filename
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.filename_exists = False

        if not os.path.exists(filename):
            if os.path.exists(filename + '.gz'):
                log.warning("gunzip --keep %s.gz" % filename)
                subprocess.call(['gunzip', '--keep', filename + '.gz'])
            else:
                log.warning("ERROR: %s does not exist" % filename)
                return

        self.filename_exists = True
        self.scratchpad = self.desc + '.scratchpad'
        self.state_type = state_type
        self.state_target = state_target
        self.state_hex = state_hex
        self.prune_table = prune_table
        self.guts_cache = {}
        assert self.state_target is not None, "state_target is None"

        with open(self.filename) as fh:
            first_line = next(fh)
            self.width = len(first_line)
            (state, steps) = first_line.split(':')
            self.state_width = len(state)

            filesize = os.path.getsize(self.filename)
            self.linecount = filesize/self.width

            # Populate guts_cache with the first line of the file
            self.guts_cache[0] = first_line.rstrip()

            # Populate guts_cache with the last line of the file
            fh.seek((self.linecount-1) * self.width)
            line = fh.readline()
            (state, steps) = line.split(':')
            self.guts_cache[self.linecount] = line.rstrip()

        #log.info("%s: %d entries in guts_cache" % (self, len(self.guts_cache.keys())))
        self.cache = {}
        self.guts_call_count = 0
        self.guts_left_right_range = 0
        self.fh_seek_call_count = 0
        self.fh_seek_lines_read = 0

    def __str__(self):
        return self.desc

    def state(self):
        #if not self.filename_exists:
        #    print("File %s does not exist" % self.filename)
        #    sys.exit(1)

        state_type = self.state_type
        state_function = state_functions.get(state_type)

        # TODO all of the elif below need to be converted to functions for the state_functions dict
        if state_function:
            state = state_function(self.parent.state)
        else:
            parent_state = self.parent.state
            sides_all = self.sides_all
            sides_UD = self.sides_UD
            sides_LFRB = self.sides_LFRB

            # Used by 222 which doesn't really use a lookup table anymore..should chop all of that code
            if self.state_type == 'all':
                state = self.parent.get_state_all()

            # 4x4x4
            elif self.state_type == '444-UD-centers-stage':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '444-LR-centers-stage':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_LFRB for square_index in side.center_pos])
                state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1')

            elif self.state_type == '444-ULFRBD-centers-solve':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])

            elif self.state_type == '444-centers-and-unpaired-edges':
                state = 'x' + ''.join([parent_state[square_index] for square_index in xrange(1,97)])
                state_list = list(state)

                for (a, b, c, d) in ((2, 3, 67, 66),
                                     (5, 9, 18, 19),
                                     (14, 15, 34, 35),
                                     (8, 12, 51, 50),
                                     (24, 28, 37, 41),
                                     (40, 44, 53, 57),
                                     (56, 60, 69, 73),
                                     (72, 76, 21, 25),
                                     (82, 83, 46, 47),
                                     (85, 89, 31, 30),
                                     (94, 95, 79, 78),
                                     (88, 92, 62, 63)):

                    # If the edge is paired, x it out
                    if state[a] == state[b] and state[c] == state[d]:
                        state_list[a] = "x"
                        state_list[b] = "x"
                        state_list[c] = "x"
                        state_list[d] = "x"

                state = ''.join(state_list)

                state = ''.join((state[2:4],
                                 state[5:13],
                                 state[14:16],
                                 state[18:20],
                                 state[21:29],
                                 state[30:32],
                                 state[34:36],
                                 state[37:45],
                                 state[46:48],
                                 state[50:52],
                                 state[53:61],
                                 state[62:64],
                                 state[66:68],
                                 state[69:77],
                                 state[78:80],
                                 state[82:84],
                                 state[85:93],
                                 state[94:96]))
                '''
                # once ./utils/trim_444_555_edges.py is working use this
                state = ''.join((state[2:4],
                                 state[5],
                                 state[8],
                                 state[9],
                                 state[12],
                                 state[14:16],
                                 state[18:20],
                                 state[21],
                                 state[24],
                                 state[25],
                                 state[28],
                                 state[30:32],
                                 state[34:36],
                                 state[37],
                                 state[40],
                                 state[41],
                                 state[44],
                                 state[46:48],
                                 state[50:52],
                                 state[53],
                                 state[56],
                                 state[57],
                                 state[60],
                                 state[62:64],
                                 state[66:68],
                                 state[69],
                                 state[72],
                                 state[73],
                                 state[76],
                                 state[78:80],
                                 state[82:84],
                                 state[85],
                                 state[88],
                                 state[89],
                                 state[92],
                                 state[94:96]))
                '''

            # 5x5x5
            elif self.state_type == '555-UD-centers-solve-on-all':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
                state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x')

            elif self.state_type == '555-LR-centers-solve-on-all':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
                state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x')

            elif self.state_type == '555-FB-centers-solve-on-all':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])
                state = state.replace('U', 'x').replace('L', 'x').replace('R', 'x').replace('D', 'x')

            elif self.state_type == '555-LR-centers-stage-on-LFRB':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_LFRB for square_index in side.center_pos])
                state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1')

            elif self.state_type == '555-ULFRBD-centers-solve':
                # unroll
                state = ''.join([parent_state[square_index] for side in sides_all for square_index in side.center_pos])

            elif self.state_type == '555-LR-centers-stage-on-LFRB-x-center-only':
                # unroll
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
                state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1')

            elif self.state_type == '555-LR-centers-stage-on-LFRB-t-center-only':
                # unroll
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
                state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1')

            elif self.state_type == '555-centers-and-unpaired-edges':
                state = 'x' + ''.join([parent_state[square_index] for square_index in xrange(1,151)])
                state_list = list(state)

                for (a, b, c, d, e, f) in ((2, 3, 4, 104, 103, 102),
                                           (6, 11, 16, 27, 28, 29),
                                           (10, 15, 20, 79, 78, 77),
                                           (22, 23, 24, 52, 53, 54),
                                           (31, 36, 41, 110, 115, 120),
                                           (35, 40, 45, 56, 61, 66),
                                           (60, 65, 70, 81, 86, 91),
                                           (85, 90, 95, 106, 111, 116),
                                           (72, 73, 74, 127, 128, 129),
                                           (131, 136, 141, 49, 48, 47),
                                           (135, 140, 145, 97, 98, 99),
                                           (147, 148, 149, 124, 123, 122)):

                    # If the edge is paired, x it out
                    if (state[a] == state[b] and state[b] == state[c] and
                        state[d] == state[e] and state[e] == state[f]):
                        state_list[a] = "x"
                        state_list[b] = "x"
                        state_list[c] = "x"
                        state_list[d] = "x"
                        state_list[e] = "x"
                        state_list[f] = "x"

                state = ''.join(state_list)
                state = ''.join((state[2:5],
                                 state[6:21],
                                 state[22:25],
                                 state[27:30],
                                 state[31:46],
                                 state[47:50],
                                 state[52:55],
                                 state[56:71],
                                 state[72:75],
                                 state[77:80],
                                 state[81:96],
                                 state[97:100],
                                 state[102:105],
                                 state[106:121],
                                 state[122:125],
                                 state[127:130],
                                 state[131:146],
                                 state[147:150]))

            # 6x6x6
            elif self.state_type == '666-UD-centers-oblique-edges-solve':
                # unroll
                state = []

                for side in sides_UD:
                    for square_index in side.center_pos:
                        if square_index in side.center_corner_pos:
                            state.append('x')
                        else:
                            state.append(parent_state[square_index])

                state = ''.join(state)

            elif self.state_type == '666-LR-centers-oblique-edges-solve':
                # unroll
                state = []

                for side in self.sides_LR:
                    for square_index in side.center_pos:
                        if square_index in side.center_corner_pos:
                            state.append('x')
                        else:
                            state.append(parent_state[square_index])

                state = ''.join(state)

            elif self.state_type == '666-FB-centers-oblique-edges-solve':
                # unroll
                state = []

                for side in self.sides_FB:
                    for square_index in side.center_pos:
                        if square_index in side.center_corner_pos:
                            state.append('x')
                        else:
                            state.append(parent_state[square_index])

                state = ''.join(state)

            elif self.state_type == '666-LFRB-centers-oblique-edges-solve':
                state = ''.join(['x', parent_state[45], parent_state[46], 'x', parent_state[50], parent_state[51], parent_state[52], parent_state[53], parent_state[56], parent_state[57], parent_state[58], parent_state[59], 'x', parent_state[63], parent_state[64], 'xx', parent_state[81], parent_state[82], 'x', parent_state[86], parent_state[87], parent_state[88], parent_state[89], parent_state[92], parent_state[93], parent_state[94], parent_state[95], 'x', parent_state[99], parent_state[100], 'xx', parent_state[117], parent_state[118], 'x', parent_state[122], parent_state[123], parent_state[124], parent_state[125], parent_state[128], parent_state[129], parent_state[130], parent_state[131], 'x', parent_state[135], parent_state[136], 'xx', parent_state[153], parent_state[154], 'x', parent_state[158], parent_state[159], parent_state[160], parent_state[161], parent_state[164], parent_state[165], parent_state[166], parent_state[167], 'x', parent_state[171], parent_state[172], 'x'])

            elif self.state_type == '666-UD-inner-X-centers-stage':
                # unroll (use join)
                state = 'xxxxx' + parent_state[15] + parent_state[16] + 'xx' + parent_state[21] + parent_state[22]  + 'xxxxx' +\
                        'xxxxx' + parent_state[51] + parent_state[52] + 'xx' + parent_state[57] + parent_state[58]  + 'xxxxx' +\
                        'xxxxx' + parent_state[87] + parent_state[88] + 'xx' + parent_state[93] + parent_state[94]  + 'xxxxx' +\
                        'xxxxx' + parent_state[123] + parent_state[124] + 'xx' + parent_state[129] + parent_state[130]  + 'xxxxx' +\
                        'xxxxx' + parent_state[159] + parent_state[160] + 'xx' + parent_state[165] + parent_state[166]  + 'xxxxx' +\
                        'xxxxx' + parent_state[195] + parent_state[196] + 'xx' + parent_state[201] + parent_state[202]  + 'xxxxx'
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '666-UD-oblique-edge-pairing':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '666-UD-oblique-edge-pairing-left-only':
                # unroll (use join)
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

                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '666-UD-oblique-edge-pairing-right-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '666-LR-inner-X-centers-stage':
                # unroll (use join)
                state = 'xxxxx' + parent_state[15] + parent_state[16] + 'xx' + parent_state[21] + parent_state[22]  + 'xxxxx' +\
                        'xxxxx' + parent_state[51] + parent_state[52] + 'xx' + parent_state[57] + parent_state[58]  + 'xxxxx' +\
                        'xxxxx' + parent_state[87] + parent_state[88] + 'xx' + parent_state[93] + parent_state[94]  + 'xxxxx' +\
                        'xxxxx' + parent_state[123] + parent_state[124] + 'xx' + parent_state[129] + parent_state[130]  + 'xxxxx' +\
                        'xxxxx' + parent_state[159] + parent_state[160] + 'xx' + parent_state[165] + parent_state[166]  + 'xxxxx' +\
                        'xxxxx' + parent_state[195] + parent_state[196] + 'xx' + parent_state[201] + parent_state[202]  + 'xxxxx'
                state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')

            elif self.state_type == '666-LR-oblique-edge-pairing':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')

            elif self.state_type == '666-LR-oblique-edge-pairing-left-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')

            elif self.state_type == '666-LR-oblique-edge-pairing-right-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')


            # 7x7x7
            elif self.state_type == '777-UD-centers-oblique-edges-solve':
                # unroll
                state = []

                for side in sides_UD:
                    for square_index in side.center_pos:
                        if square_index in side.center_corner_pos:
                            state.append('x')
                        else:
                            state.append(parent_state[square_index])

                state = ''.join(state)

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve':
                state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x', parent_state[65], parent_state[66], parent_state[67], parent_state[68], parent_state[69], parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], parent_state[79], parent_state[80], parent_state[81], parent_state[82], parent_state[83], 'x', parent_state[87], parent_state[88], parent_state[89], 'xx', parent_state[108], parent_state[109], parent_state[110], 'x', parent_state[114], parent_state[115], parent_state[116], parent_state[117], parent_state[118], parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], parent_state[128], parent_state[129], parent_state[130], parent_state[131], parent_state[132], 'x', parent_state[136], parent_state[137], parent_state[138], 'xx', parent_state[157], parent_state[158], parent_state[159], 'x', parent_state[163], parent_state[164], parent_state[165], parent_state[166], parent_state[167], parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], parent_state[177], parent_state[178], parent_state[179], parent_state[180], parent_state[181], 'x', parent_state[185], parent_state[186], parent_state[187], 'xx', parent_state[206], parent_state[207], parent_state[208], 'x', parent_state[212], parent_state[213], parent_state[214], parent_state[215], parent_state[216], parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], parent_state[226], parent_state[227], parent_state[228], parent_state[229], parent_state[230], 'x', parent_state[234], parent_state[235], parent_state[236], 'x'])

            elif self.state_type == '777-UD-oblique-edge-pairing':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '777-UD-oblique-edge-pairing-middle-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '777-UD-oblique-edge-pairing-left-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '777-UD-oblique-edge-pairing-right-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')

            elif self.state_type == '777-LR-oblique-edge-pairing':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')

            elif self.state_type == '777-LR-oblique-edge-pairing-middle-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')

            elif self.state_type == '777-LR-oblique-edge-pairing-left-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')

            elif self.state_type == '777-LR-oblique-edge-pairing-right-only':
                # unroll (use join)
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
                state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')

            elif self.state_type == '777-UD-centers-oblique-edges-solve-center-only':
                state = ''.join(['xxxxxx', parent_state[17], parent_state[18], parent_state[19], 'xx', parent_state[24], 'x', parent_state[26], 'xx', parent_state[31], parent_state[32], parent_state[33], 'xxxxxxxx', 'xxxx', parent_state[262], parent_state[263], parent_state[264], 'xx', parent_state[269], 'x', parent_state[271], 'xx', parent_state[276], parent_state[277], parent_state[278], 'xxxxxx'])

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
                            # - pformat(state) at the end of this loop and save that to a file foo
                            # - run utils/fix_foo.py
                            # - yes this is ugly as hell but I only had to do this a few times ever so didn't clean up the process
                            # state.append("parent_state[%d]" % square_index)
                        else:
                            state.append('x')

                log.info("FOO: %s" % pformat(state))
                sys.exit(0)
                state = ''.join(state)
                '''

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-only':
                state = ''.join(['xxxxxx', parent_state[66], parent_state[67], parent_state[68], 'xx', parent_state[73], parent_state[74], parent_state[75], 'xx', parent_state[80], parent_state[81], parent_state[82], 'xxxxxx', 'xxxxxx', parent_state[115], parent_state[116], parent_state[117], 'xx', parent_state[122], parent_state[123], parent_state[124], 'xx', parent_state[129], parent_state[130], parent_state[131], 'xxxxxx', 'xxxxxx', parent_state[164], parent_state[165], parent_state[166], 'xx', parent_state[171], parent_state[172], parent_state[173], 'xx', parent_state[178], parent_state[179], parent_state[180], 'xxxxxx', 'xxxxxx', parent_state[213], parent_state[214], parent_state[215], 'xx', parent_state[220], parent_state[221], parent_state[222], 'xx', parent_state[227], parent_state[228], parent_state[229], 'xxxxxx'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-left-oblique-edge-only':
                state = ''.join(['x', parent_state[59], 'xxxx', parent_state[66], 'x', parent_state[68], parent_state[69], 'xx', parent_state[74], 'xx', parent_state[79], parent_state[80], 'x', parent_state[82], 'xxxx', parent_state[89], 'xx', parent_state[108], 'xxxx', parent_state[115], 'x', parent_state[117], parent_state[118], 'xx', parent_state[123], 'xx', parent_state[128], parent_state[129], 'x', parent_state[131], 'xxxx', parent_state[138], 'xx', parent_state[157], 'xxxx', parent_state[164], 'x', parent_state[166], parent_state[167], 'xx', parent_state[172], 'xx', parent_state[177], parent_state[178], 'x', parent_state[180], 'xxxx', parent_state[187], 'xx', parent_state[206], 'xxxx', parent_state[213], 'x', parent_state[215], parent_state[216], 'xx', parent_state[221], 'xx', parent_state[226], parent_state[227], 'x', parent_state[229], 'xxxx', parent_state[236], 'x'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-middle-oblique-edge-only':
                state = ''.join(['xx', parent_state[60], 'xxx', parent_state[66], 'x', parent_state[68], 'x', parent_state[72], 'x', parent_state[74], 'x', parent_state[76], 'x', parent_state[80], 'x', parent_state[82], 'xxx', parent_state[88], 'xxxx', parent_state[109], 'xxx', parent_state[115], 'x', parent_state[117], 'x', parent_state[121], 'x', parent_state[123], 'x', parent_state[125], 'x', parent_state[129], 'x', parent_state[131], 'xxx', parent_state[137], 'xxxx', parent_state[158], 'xxx', parent_state[164], 'x', parent_state[166], 'x', parent_state[170], 'x', parent_state[172], 'x', parent_state[174], 'x', parent_state[178], 'x', parent_state[180], 'xxx', parent_state[186], 'xxxx', parent_state[207], 'xxx', parent_state[213], 'x', parent_state[215], 'x', parent_state[219], 'x', parent_state[221], 'x', parent_state[223], 'x', parent_state[227], 'x', parent_state[229], 'xxx', parent_state[235], 'x', 'x'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-right-oblique-edge-only':
                state = ''.join(['xxx', parent_state[61], 'x', parent_state[65], parent_state[66], 'x', parent_state[68], 'xxx', parent_state[74], 'xxx', parent_state[80], 'x', parent_state[82], parent_state[83], 'x', parent_state[87], 'xxxxxx', parent_state[110], 'x', parent_state[114], parent_state[115], 'x', parent_state[117], 'xxx', parent_state[123], 'xxx', parent_state[129], 'x', parent_state[131], parent_state[132], 'x', parent_state[136], 'xxxxxx', parent_state[159], 'x', parent_state[163], parent_state[164], 'x', parent_state[166], 'xxx', parent_state[172], 'xxx', parent_state[178], 'x', parent_state[180], parent_state[181], 'x', parent_state[185], 'xxxxxx', parent_state[208], 'x', parent_state[212], parent_state[213], 'x', parent_state[215], 'xxx', parent_state[221], 'xxx', parent_state[227], 'x', parent_state[229], parent_state[230], 'x', parent_state[234], 'xxx'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-t-center-left-oblique-edge-only':
                state = ''.join(['x', parent_state[59], 'xxxxx', parent_state[67], 'x', parent_state[69], 'x', parent_state[73], parent_state[74], parent_state[75], 'x', parent_state[79], 'x', parent_state[81], 'xxxxx', parent_state[89], 'xx', parent_state[108], 'xxxxx', parent_state[116], 'x', parent_state[118], 'x', parent_state[122], parent_state[123], parent_state[124], 'x', parent_state[128], 'x', parent_state[130], 'xxxxx', parent_state[138], 'xx', parent_state[157], 'xxxxx', parent_state[165], 'x', parent_state[167], 'x', parent_state[171], parent_state[172], parent_state[173], 'x', parent_state[177], 'x', parent_state[179], 'xxxxx', parent_state[187], 'xx', parent_state[206], 'xxxxx', parent_state[214], 'x', parent_state[216], 'x', parent_state[220], parent_state[221], parent_state[222], 'x', parent_state[226], 'x', parent_state[228], 'xxxxx', parent_state[236], 'x']
    )
            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-t-center-middle-oblique-edge-only':
                state = ''.join(['xx', parent_state[60], 'xxxx', parent_state[67], 'xx', parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], 'xx', parent_state[81], 'xxxx', parent_state[88], 'xxxx', parent_state[109], 'xxxx', parent_state[116], 'xx', parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], 'xx', parent_state[130], 'xxxx', parent_state[137], 'xxxx', parent_state[158], 'xxxx', parent_state[165], 'xx', parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], 'xx', parent_state[179], 'xxxx', parent_state[186], 'xxxx', parent_state[207], 'xxxx', parent_state[214], 'xx', parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], 'xx', parent_state[228], 'xxxx', parent_state[235], 'x', 'x'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-middle-oblique-edge-only':
                state = ''.join(['xx', parent_state[60], 'xxx', parent_state[66], parent_state[67], parent_state[68], 'x', parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], 'x', parent_state[80], parent_state[81], parent_state[82], 'xxx', parent_state[88], 'xxxx', parent_state[109], 'xxx', parent_state[115], parent_state[116], parent_state[117], 'x', parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], 'x', parent_state[129], parent_state[130], parent_state[131], 'xxx', parent_state[137], 'xxxx', parent_state[158], 'xxx', parent_state[164], parent_state[165], parent_state[166], 'x', parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], 'x', parent_state[178], parent_state[179], parent_state[180], 'xxx', parent_state[186], 'xxxx', parent_state[207], 'xxx', parent_state[213], parent_state[214], parent_state[215], 'x', parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], 'x', parent_state[227], parent_state[228], parent_state[229], 'xxx', parent_state[235], 'xx'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-left-right-oblique-edges-only':
                state = ''.join(['x', parent_state[59], 'x', parent_state[61], 'x', parent_state[65], 'xxx', parent_state[69], 'xxxxx', parent_state[79], 'xxx', parent_state[83], 'x', parent_state[87], 'x', parent_state[89], 'xx', parent_state[108], 'x', parent_state[110], 'x', parent_state[114], 'xxx', parent_state[118], 'xxxxx', parent_state[128], 'xxx', parent_state[132], 'x', parent_state[136], 'x', parent_state[138], 'xx', parent_state[157], 'x', parent_state[159], 'x', parent_state[163], 'xxx', parent_state[167], 'xxxxx', parent_state[177], 'xxx', parent_state[181], 'x', parent_state[185], 'x', parent_state[187], 'xx', parent_state[206], 'x', parent_state[208], 'x', parent_state[212], 'xxx', parent_state[216], 'xxxxx', parent_state[226], 'xxx', parent_state[230], 'x', parent_state[234], 'x', parent_state[236], 'x'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-middle-right-oblique-edges-only':
                state = ''.join(['xx', parent_state[60], parent_state[61], 'x', parent_state[65], 'xxxx', parent_state[72], 'xxx', parent_state[76], 'xxxx', parent_state[83], 'x', parent_state[87], parent_state[88], 'xxxx', parent_state[109], parent_state[110], 'x', parent_state[114], 'xxxx', parent_state[121], 'xxx', parent_state[125], 'xxxx', parent_state[132], 'x', parent_state[136], parent_state[137], 'xxxx', parent_state[158], parent_state[159], 'x', parent_state[163], 'xxxx', parent_state[170], 'xxx', parent_state[174], 'xxxx', parent_state[181], 'x', parent_state[185], parent_state[186], 'xxxx', parent_state[207], parent_state[208], 'x', parent_state[212], 'xxxx', parent_state[219], 'xxx', parent_state[223], 'xxxx', parent_state[230], 'x', parent_state[234], parent_state[235], 'x', 'x'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-inner-t-center-right-oblique-edge-only':
                state = ''.join(['xxx', parent_state[61], 'x', parent_state[65], 'x', parent_state[67], 'xxx', parent_state[73], parent_state[74], parent_state[75], 'xxx', parent_state[81], 'x', parent_state[83], 'x', parent_state[87], 'xxxxxx', parent_state[110], 'x', parent_state[114], 'x', parent_state[116], 'xxx', parent_state[122], parent_state[123], parent_state[124], 'xxx', parent_state[130], 'x', parent_state[132], 'x', parent_state[136], 'xxxxxx', parent_state[159], 'x', parent_state[163], 'x', parent_state[165], 'xxx', parent_state[171], parent_state[172], parent_state[173], 'xxx', parent_state[179], 'x', parent_state[181], 'x', parent_state[185], 'xxxxxx', parent_state[208], 'x', parent_state[212], 'x', parent_state[214], 'xxx', parent_state[220], parent_state[221], parent_state[222], 'xxx', parent_state[228], 'x', parent_state[230], 'x', parent_state[234], 'xxx'])

            elif self.state_type == '777-LFRB-centers-oblique-edges-solve-left-middle-oblique-edge-only':
                state = ''.join(['x', parent_state[59], parent_state[60], 'xxxxxx', parent_state[69], parent_state[72], 'xxx', parent_state[76], parent_state[79], 'xxxxxx', parent_state[88], parent_state[89], 'xx', parent_state[108], parent_state[109], 'xxxxxx', parent_state[118], parent_state[121], 'xxx', parent_state[125], parent_state[128], 'xxxxxx', parent_state[137], parent_state[138], 'xx', parent_state[157], parent_state[158], 'xxxxxx', parent_state[167], parent_state[170], 'xxx', parent_state[174], parent_state[177], 'xxxxxx', parent_state[186], parent_state[187], 'xx', parent_state[206], parent_state[207], 'xxxxxx', parent_state[216], parent_state[219], 'xxx', parent_state[223], parent_state[226], 'xxxxxx', parent_state[235], parent_state[236], 'x'])

            else:
                raise ImplementThis("state_type %s" % self.state_type)

        if self.state_hex:
            state = convert_state_to_hex(state, self.state_width)

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

        width = self.width
        state_width = self.state_width
        state = None
        #left_right_delta = right - left
        # log.warning("file_binary_search_guts %d <-> %d, delta %d, look for %s" % (left, right, left_right_delta, state_to_find))

        #self.guts_call_count += 1
        #self.guts_left_right_range += left_right_delta

        while left <= right:
            #left_right_delta = right - left
            mid = int(left + ((right - left) /2))

            try:
                line = self.guts_cache[mid]
            except KeyError:
                fh.seek(mid * width)
                self.fh_seek_call_count += 1
                self.fh_seek_lines_read += 1
                line = fh.readline().rstrip()
                self.guts_cache[mid] = line
            state = line[0:state_width]

            # dwalton comment this out
            if line[state_width] != ':':
                raise Exception("we are off")

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
        guts_cache = self.guts_cache

        for line_number in line_numbers:
            (state, steps) = guts_cache[line_number].split(':')

            if prev_state and state_to_find >= prev_state and state_to_find <= state:
                min_left = prev_line_number
                max_right = line_number
                break

            prev_state = state
            prev_line_number = line_number

        for line_number in line_numbers:
            if line_number < min_left:
                del self.guts_cache[line_number]
            elif line_number >= min_left:
                break

        #log.info("find_min_left_max_right: min_left(%d) %s, max_right(%d) %s, state_to_find %s" % (min_left_i, min_left, max_right_i, max_right, state_to_find))
        return (min_left, max_right)

    def file_binary_search_multiple_keys_low_low_python(self, fh, states_to_find, debug=False):
        results = {}
        min_left = None
        max_right = None
        self.guts_call_count = 0
        self.guts_left_right_range = 0

        if not states_to_find:
            return results

        # Look in our cache to see which states we've already found
        states_to_find = sorted(list(set(states_to_find)))
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

            (line_number, value) = self.file_binary_search_guts(fh, state_to_find, min_left, max_right)
            results[state_to_find] = value
            self.cache[state_to_find] = value
            index += 1

        end_time = dt.datetime.now()
        #log.info("%s: found %d states (another %d were cached) in %s, %d guts calls, %d avg left->right range, guts_cache has %d entries" %
        #    (self, states_to_find_count, original_states_to_find_count - states_to_find_count, pretty_time(end_time - start_time),
        #     self.guts_call_count, int(self.guts_left_right_range/self.guts_call_count), len(self.guts_cache.keys())))
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

        while True:
            state = self.state()

            if state == self.state_target:
                break

            steps = self.steps(state)

            if not steps:
                raise NoSteps("%s: state %s does not have steps" % (self, state))

            #if self.filename == 'lookup-table-4x4x4-step101-edges.txt':
            #    self.parent.print_cube()
            #    log.warning("%s: steps %s" % (self, ' '.join(steps)))

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

    def ida_stage(self, max_ida_depth):
        start_time0 = dt.datetime.now()
        state = self.state()
        log.debug("state %s vs state_target %s" % (state, self.state_target))

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
        original_state = self.parent.state[:]
        original_solution = self.parent.solution[:]

        if self.parent.size == 2:
            rotate_xxx = rotate_222
        elif self.parent.size == 4:
            rotate_xxx = rotate_444
        elif self.parent.size == 5:
            rotate_xxx = rotate_555
        elif self.parent.size == 6:
            rotate_xxx = rotate_666
        elif self.parent.size == 7:
            rotate_xxx = rotate_777
        else:
            raise ImplementThis("Need rotate_xxx" % (self.parent.size, self.parent.size, self.parent.size))

        states_scratchpad = 'states_scratchpad.txt'
        pt_states_scratchpad = 'pt_states_scratchpad.txt'
        prune_tables = self.prune_tables

        # Because saving a little number to pt_costs_by_step below takes much less memory than
        # saving the pt.filename
        for (index, pt) in enumerate(prune_tables):
            pt.index = index

        for threshold in xrange(1, max_ida_depth+1):

            # Build a list of moves we can do 1 move deep
            # Build a list of moves we can do 2 moves deep, this must build on the 1 move deep list
            # Build a list of moves we can do 3 moves deep, this must build on the 2 move deep list
            # etc
            prev_step_sequences = []

            for max_step_count in xrange(1, threshold+1):
                start_time1 = dt.datetime.now()
                step_sequences = self.ida_steps_list(prev_step_sequences, threshold, max_step_count)

                if step_sequences:
                    log.debug("")
                    log.debug("%s: IDA threshold %d, %s step_sequences to evaluate (max step %d)" %
                        (self, threshold, len(step_sequences), max_step_count))

                # Once we run out of memory and start swapping we are dead in the water.
                # If we are processing more than 500k step_sequences save state to the
                # disk to avoid running out of memory. All of that writing to the disk is
                # slow so that is why we only do this in extreme cases.
                if os.path.exists(states_scratchpad):
                    os.unlink(states_scratchpad)

                if os.path.exists(pt_states_scratchpad):
                    os.unlink(pt_states_scratchpad)
                use_scratchpad = False

                states_to_check = []
                pt_costs_by_step = []

                # Now rotate all of these moves and get the resulting cube for each
                # Do one gigantic binary search
                start_time2 = dt.datetime.now()
                rotate_count = 0

                for (step_sequence_index, step_sequence) in enumerate(step_sequences):
                    self.parent.state = original_state[:]
                    self.parent.solution = original_solution[:]
                    self.ida_count += 1
                    rotate_count += 1

                    steps_in_step_sequence = step_sequence.split()
                    self.parent.solution.extend(steps_in_step_sequence)

                    for step in steps_in_step_sequence:
                        rotate_xxx(self.parent.state, self.parent.state[:], step)

                    # get the current state of the cube
                    state = self.state()
                    states_to_check.append(state)

                    # Save a list of the pt indexes/states for this step_sequence
                    tmp_list = []
                    for pt in prune_tables:
                        tmp_list.append((pt.index, pt.state()))
                    pt_costs_by_step.append(tmp_list)

                    '''
                    # does this help with memory issues?
                    if rotate_count % 500000 == 0:
                        log.debug("%s: rotate count %d" % (self, rotate_count))

                        # Write states to scratchpad to save memory
                        with open(states_scratchpad, 'a') as fh_states_scratchpad:
                            fh_states_scratchpad.write("\n".join(states_to_check) + "\n")
                        log.debug("%s: rotate count %d, wrote entries to %s" % (self, rotate_count, states_scratchpad))
                        states_to_check = []

                        # Write prune table states to scratchpad to save memory
                        with open(pt_states_scratchpad, 'a') as fh_pt_states_scratchpad:
                            to_write = []
                            for list_of_pt_index_pt_state in pt_costs_by_step: # there is one of these per step_sequence
                                to_write.append(json.dumps(list_of_pt_index_pt_state))
                            fh_pt_states_scratchpad.write("\n".join(to_write) + "\n")
                        log.debug("%s: rotate count %d, wrote entries to %s" % (self, rotate_count, pt_states_scratchpad))
                        pt_costs_by_step = []

                        gc.collect()
                        use_scratchpad = True

                if use_scratchpad:
                    if states_to_check:
                        # Write states to scratchpad to save memory
                        with open(states_scratchpad, 'a') as fh_states_scratchpad:
                            fh_states_scratchpad.write("\n".join(states_to_check))
                        log.debug("%s: rotate count %d, wrote entries to %s" % (self, rotate_count, states_scratchpad))
                        states_to_check = []

                    if pt_costs_by_step:
                        # Write prune table states to scratchpad to save memory
                        with open(pt_states_scratchpad, 'a') as fh_pt_states_scratchpad:
                            to_write = []
                            for list_of_pt_index_pt_state in pt_costs_by_step: # there is one of these per step_sequence
                                to_write.append(json.dumps(list_of_pt_index_pt_state))
                            fh_pt_states_scratchpad.write("\n".join(to_write))
                        log.debug("%s: rotate count %d, wrote entries to %s" % (self, rotate_count, pt_states_scratchpad))
                        pt_costs_by_step = []

                    gc.collect()
                    '''
                end_time2 = dt.datetime.now()

                if rotate_count:
                    log.debug("%s: IDA threshold %d (max step %d) rotated %d sequences in %s" %
                        (self, threshold, max_step_count, rotate_count, pretty_time(end_time2 - start_time2)))

                start_time3 = dt.datetime.now()
                self.parent.state = original_state[:]
                self.parent.solution = original_solution[:]

                # with copy
                # IDA threshold 14, rotated 215609 sequences in 0:00:18.440573 (max step 4)

                # with slices
                # IDA threshold 14, rotated 215609 sequences in 0:00:16.131184 (max step 4)

                # with rotate_xxx
                # IDA threshold 14, rotated 215609 sequences in 0:00:15.804288 (max step 4)

                # first time getting the 1.6 million rotates to not run out of memory
                # IDA threshold 14, rotated 1644910 sequences in 0:02:26.224329 (max step 5)

                # IDA threshold 14, rotated 1644910 sequences in 0:02:11.353591 (max step 5)
                # something with using parent_state instead of self.parent.state break...same with self.parent.solution

                # If not using the scratchpad states_to_check is already populated
                if use_scratchpad:
                    states_to_check = []
                    with open(states_scratchpad, 'r') as fh_states_scratchpad:
                        for line in fh_states_scratchpad:
                            states_to_check.append(line.rstrip())

                # This will do a multi-key binary search of all states_to_check
                steps_for_states = self.steps(states_to_check)

                '''
                states_with_steps_count = 0
                for (step_sequence_index, state) in enumerate(states_to_check):
                    if steps_for_states[state]:
                        states_with_steps_count += 1

                if states_with_steps_count:
                    log.info("%s: There are %d states with steps" % (self, states_with_steps_count))
                '''

                # There are steps for a state that means our IDA search is done...woohoo!!
                for (step_sequence_index, state) in enumerate(states_to_check):
                    steps = steps_for_states[state]

                    if steps:
                        step_sequence = step_sequences[step_sequence_index]

                        for step in step_sequence.split():
                            self.parent.rotate(step)

                        for step in steps:
                            self.parent.rotate(step)

                        end_time0 = dt.datetime.now()
                        end_time3 = end_time0
                        log.info("%s: IDA threshold %d (max step %d), took %s (%s to rotate %d, %s to search tables)" %\
                            (self, threshold, max_step_count,
                             pretty_time(end_time3 - start_time1),
                             pretty_time(end_time2 - start_time2), rotate_count,
                             pretty_time(end_time3 - start_time3)))
                        log.warning("%s: IDA threshold %d (max step %d), found match in %s, steps %s" %\
                            (self, threshold, max_step_count,
                             pretty_time(end_time0 - start_time0),
                             step_sequence))
                        return

                # Time to prune some branches, do a multi-key binary search for each prune table
                pt_costs = {}
                for pt in prune_tables:
                    states_to_find = []

                    if use_scratchpad:
                        with open(pt_states_scratchpad, 'r') as fh_pt_states_scratchpad:
                            for line in fh_pt_states_scratchpad:
                                list_of_pt_index_pt_state = json.loads(line.rstrip())

                                for (pt_index, pt_state) in list_of_pt_index_pt_state:
                                    if pt_index == pt.index:
                                        states_to_find.append(pt_state)
                    else:
                        for list_of_pt_index_pt_state in pt_costs_by_step:
                            for (pt_index, pt_state) in list_of_pt_index_pt_state:
                                if pt_index == pt.index:
                                    states_to_find.append(pt_state)

                    with open(pt.filename, 'r') as fh:
                        pt_costs[pt.index] = pt.file_binary_search_multiple_keys(fh, states_to_find)
                    states_to_find = []

                step_sequences_within_cost = []

                # There is one line in fh_pt_states_scratchpad per step_sequence_index so step through these together
                if use_scratchpad:
                    with open(pt_states_scratchpad, 'r') as fh_pt_states_scratchpad:

                        for (step_sequence_index, state) in enumerate(states_to_check):
                            step_sequence = step_sequences[step_sequence_index]

                            # extract cost_to_goal from the pt_costs dictionary
                            cost_to_goal = 0
                            cost_to_here = len(step_sequence.split())

                            line = next(fh_pt_states_scratchpad)
                            list_of_pt_index_pt_state = json.loads(line.rstrip())

                            for (pt_index, pt_state) in list_of_pt_index_pt_state:
                                pt_steps = pt_costs[pt_index][pt_state]
                                len_pt_steps = len(pt_steps)

                                if len_pt_steps > cost_to_goal:
                                    cost_to_goal = len_pt_steps

                            if (cost_to_here + cost_to_goal) > threshold:
                                self.ida_prune_count += 1
                            else:
                                step_sequences_within_cost.append(step_sequence)
                else:
                    for (step_sequence_index, state) in enumerate(states_to_check):
                        step_sequence = step_sequences[step_sequence_index]

                        # extract cost_to_goal from the pt_costs dictionary
                        cost_to_goal = 0
                        cost_to_here = len(step_sequence.split())

                        for (pt_index, pt_state) in pt_costs_by_step[step_sequence_index]:
                            pt_steps = pt_costs[pt_index][pt_state]
                            len_pt_steps = len(pt_steps)

                            if len_pt_steps > cost_to_goal:
                                cost_to_goal = len_pt_steps

                        if (cost_to_here + cost_to_goal) > threshold:
                            self.ida_prune_count += 1
                        else:
                            step_sequences_within_cost.append(step_sequence)

                prev_step_sequences = step_sequences_within_cost[:]
                states_to_check = []
                pt_costs_by_step = []
                self.ida_count = 0
                self.ida_prune_count = 0
                gc.collect()

                if rotate_count:
                    end_time3 = dt.datetime.now()

                    if step_sequences_within_cost:
                        log.info("%s: IDA threshold %d (max step %d), keep %3d, took %s (%s to rotate %d, %s to search tables)" %\
                            (self, threshold, max_step_count, len(step_sequences_within_cost),
                             pretty_time(end_time3 - start_time1),
                             pretty_time(end_time2 - start_time2), rotate_count,
                             pretty_time(end_time3 - start_time3)))

        # The only time we will get here is when max_ida_depth is a low number.  It will be up to the caller to:
        # - 'solve' one of their prune tables to put the cube in a state that we can find a solution for a little more easily
        # - call ida_solve() again but with a near infinite max_ida_depth...99 is close enough to infinity for IDA purposes
        log.warning("%s: could not find a solution via IDA within %d steps...will 'solve' a prune table and try again" % (self, max_ida_depth))
        raise NoIDASolution("%s FAILED for state %s" % (self, self.state()))

    def solve(self, max_ida_stage):
        self.ida_stage(max_ida_stage)
        LookupTable.solve(self)
