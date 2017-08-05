
import datetime as dt
from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.rotate_xxx import rotate_222, rotate_444, rotate_555, rotate_666, rotate_777
from pyhashxx import hashxx
import json
import logging
import math
import os
import shutil
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
    if not prev_step.endswith("'") and step.endswith("'") and step[0:-1] == prev_step:
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


def find_prime_in_range(a, b):
    for p in range(a, b):
        for i in range(2, p):
            if p % i == 0:
                break
        else:
            return p
    return None


def find_next_prime(n):
    return find_prime_in_range(n, 2*n)


def get_444_UD_centers_stage(parent_state):
    """
    444-UD-centers-stage
    """
    state = [parent_state[6],
             parent_state[7],
             parent_state[10],
             parent_state[11],
             parent_state[22],
             parent_state[23],
             parent_state[26],
             parent_state[27],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[54],
             parent_state[55],
             parent_state[58],
             parent_state[59],
             parent_state[70],
             parent_state[71],
             parent_state[74],
             parent_state[75],
             parent_state[86],
             parent_state[87],
             parent_state[90],
             parent_state[91]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_444_LR_centers_stage(parent_state):
    """
    444-LR-centers-stage
    """
    '''
    state = [parent_state[22],
             parent_state[23],
             parent_state[26],
             parent_state[27],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[54],
             parent_state[55],
             parent_state[58],
             parent_state[59],
             parent_state[70],
             parent_state[71],
             parent_state[74],
             parent_state[75]]
    '''
    state = [parent_state[6],
             parent_state[7],
             parent_state[10],
             parent_state[11],
             parent_state[22],
             parent_state[23],
             parent_state[26],
             parent_state[27],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[54],
             parent_state[55],
             parent_state[58],
             parent_state[59],
             parent_state[70],
             parent_state[71],
             parent_state[74],
             parent_state[75],
             parent_state[86],
             parent_state[87],
             parent_state[90],
             parent_state[91]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1').replace('U', '0').replace('D', '0')
    return state


def get_444_FB_centers_stage(parent_state):
    """
    444-FB-centers-stage
    """
    state = [parent_state[6],
             parent_state[7],
             parent_state[10],
             parent_state[11],
             parent_state[22],
             parent_state[23],
             parent_state[26],
             parent_state[27],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[54],
             parent_state[55],
             parent_state[58],
             parent_state[59],
             parent_state[70],
             parent_state[71],
             parent_state[74],
             parent_state[75],
             parent_state[86],
             parent_state[87],
             parent_state[90],
             parent_state[91]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('F', '1').replace('R', '0').replace('B', '1').replace('L', '0').replace('U', '0').replace('D', '0')
    return state


def get_444_ULFRBD_centers_stage(parent_state):
    """
    444-ULFRBD-centers-stage
    """
    state = [parent_state[6],
             parent_state[7],
             parent_state[10],
             parent_state[11],
             parent_state[22],
             parent_state[23],
             parent_state[26],
             parent_state[27],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[54],
             parent_state[55],
             parent_state[58],
             parent_state[59],
             parent_state[70],
             parent_state[71],
             parent_state[74],
             parent_state[75],
             parent_state[86],
             parent_state[87],
             parent_state[90],
             parent_state[91]]
    state = ''.join(state)
    state = state.replace('R', 'L').replace('B', 'F').replace('D', 'U')
    return state


def get_444_ULFRBD_centers_solve(parent_state):
    """
    444-ULFRBD-centers-solve
    """
    state = [parent_state[6],
             parent_state[7],
             parent_state[10],
             parent_state[11],
             parent_state[22],
             parent_state[23],
             parent_state[26],
             parent_state[27],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[54],
             parent_state[55],
             parent_state[58],
             parent_state[59],
             parent_state[70],
             parent_state[71],
             parent_state[74],
             parent_state[75],
             parent_state[86],
             parent_state[87],
             parent_state[90],
             parent_state[91]]
    state = ''.join(state)
    return state


def get_444_LR_centers_stage_tsai(parent_state, self):
    """
    444-LR-centers-stage-tsai
    """
    # unroll
    state = ''.join([parent_state[square_index] for side in self.sides_all for square_index in side.center_pos])
    state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1').replace('D', '0').replace('U', '0')
    return state


def get_444_LR_centers_solve_tsai(parent_state, self):
    """
    444-LR-centers-solve-tsai
    """
    # unroll
    state = ''.join([parent_state[square_index] for side in self.sides_all for square_index in side.center_pos])
    state = state.replace('F', 'x').replace('B', 'x').replace('D', 'x').replace('U', 'x')
    return state


def get_444_FB_centers_stage_tsai(parent_state, self):
    """
    444-FB-centers-stage-tsai
    """
    # unroll
    state = ''.join([parent_state[square_index] for side in self.sides_all for square_index in side.center_pos])
    state = state.replace('x', '0').replace('F', '1').replace('R', '0').replace('B', '1').replace('L', '0').replace('D', '0').replace('U', '0')
    return state


def get_444_orient_edges_tsai(parent_state, self):
    """
    444-orient-edges-tsai or 444-phase2-tsai
    """
    parent = self.parent
    original_state = self.parent.state[:]
    original_solution = self.parent.solution[:]

    state = []
    for side in self.sides_all:
        for square_index in xrange(side.min_pos, side.max_pos):

            if square_index in side.corner_pos:
                pass

            elif square_index in side.edge_pos:
                partner_index = side.get_wing_partner(square_index)
                square1 = self.parent.state[square_index]
                square2 = self.parent.state[partner_index]

                try:
                    state.append(self.parent.orient_edges[(square_index, partner_index, square1, square2)])
                except KeyError:
                    raise SolveError("%s is not in self.parent.orient_edges" % str((square_index, partner_index, square1, square2)))

                # If you hit the SolveError above, uncomment this code to build the entry
                # that needs to be added to RubiksCube444.orient_edges
                '''
                if square1 in ('U', 'D'):
                    wing_str = square1 + square2
                elif square2 in ('U', 'D'):
                    wing_str = square2 + square1
                elif square1 in ('L', 'R'):
                    wing_str = square1 + square2
                elif square2 in ('L', 'R'):
                    wing_str = square2 + square1
                else:
                    raise Exception("Could not determine wing_str for (%s, %s)" % (square1, square2))

                # - backup the current state
                # - add an 'x' to the end of the square_index/partner_index
                # - move square_index/partner_index to its final edge location
                # - look for the 'x' to determine if this is the '0' vs '1' wing
                # - restore the original state
                square1_with_x = square1 + 'x'
                square2_with_x = square2 + 'x'

                self.parent.state[square_index] = square1_with_x
                self.parent.state[partner_index] = square2_with_x

                #log.info("PRE: %s at (%d, %d)" % (wing_str, square_index, partner_index))
                #self.parent.print_cube()

                # 'UB0', 'UB1', 'UL0', 'UL1', 'UF0', 'UF1', 'UR0', 'UR1',
                # 'LB0', 'LB1', 'LF0', 'LF1', 'RF0', 'RF1', 'RB0', 'RB1',
                # 'DF0', 'DF1', 'DL0', 'DL1', 'DB0', 'DB1', 'DR0', 'DR1
                if wing_str == 'UB':
                    self.parent.move_wing_to_U_north(square_index)

                    if self.parent.state[2] == 'Ux' or self.parent.state[66] == 'Ux':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'UL':
                    self.parent.move_wing_to_U_west(square_index)

                    if self.parent.state[9] == 'Ux' or self.parent.state[18] == 'Ux':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'UF':
                    self.parent.move_wing_to_U_south(square_index)

                    if self.parent.state[15] == 'Ux' or self.parent.state[34] == 'Ux':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'UR':
                    self.parent.move_wing_to_U_east(square_index)

                    if self.parent.state[8] == 'Ux' or self.parent.state[50] == 'Ux':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'LB':
                    self.parent.move_wing_to_L_west(square_index)

                    if self.parent.state[25] == 'Lx' or self.parent.state[72] == 'Lx':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'LF':
                    self.parent.move_wing_to_L_east(square_index)

                    if self.parent.state[24] == 'Lx' or self.parent.state[41] == 'Lx':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'RF':
                    self.parent.move_wing_to_R_west(square_index)

                    if self.parent.state[57] == 'Rx' or self.parent.state[40] == 'Rx':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'RB':
                    self.parent.move_wing_to_R_east(square_index)

                    if self.parent.state[56] == 'Rx' or self.parent.state[73] == 'Rx':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'DF':
                    self.parent.move_wing_to_D_north(square_index)

                    if self.parent.state[82] == 'Dx' or self.parent.state[47] == 'Dx':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'DL':
                    self.parent.move_wing_to_D_west(square_index)

                    if self.parent.state[89] == 'Dx' or self.parent.state[31] == 'Dx':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'DB':
                    self.parent.move_wing_to_D_south(square_index)

                    if self.parent.state[95] == 'Dx' or self.parent.state[79] == 'Dx':
                        state.append('U')
                    else:
                        state.append('D')

                elif wing_str == 'DR':
                    self.parent.move_wing_to_D_east(square_index)
                    if self.parent.state[88] == 'Dx' or self.parent.state[63] == 'Dx':
                        state.append('U')
                    else:
                        state.append('D')

                else:
                    raise SolveError("invalid wing %s" % wing_str)

                if (square_index, partner_index, square1, square2) not in self.parent.orient_edges:
                    self.parent.orient_edges[(square_index, partner_index, square1, square2)] = state[-1]
                    log.info("orient_edges:\n%s\n" % pformat(self.parent.orient_edges))

                self.parent.state = original_state[:]
                self.parent.solution = original_solution[:]
                '''

            elif square_index in side.center_pos:
                if self.state_type == '444-phase2-tsai':
                    square_state = self.parent.state[square_index]
                    square_state = square_state.replace('B', 'F').replace('U', 'x').replace('D', 'x')
                    state.append(square_state)

    state = ''.join(state)

    if self.state_type == '444-orient-edges-tsai':
        if state.count('U') != 24:
            raise SolveError("state %s has %d Us and %d Ds, should have 24 of each" % (state, state.count('U'), state.count('D')))

        if state.count('D') != 24:
            raise SolveError("state %s has %d Us and %d Ds, should have 24 of each" % (state, state.count('U'), state.count('D')))
    #else:
    #    log.info(state)
    return state


def get_444_phase3_tsai(parent_state, self):
    """
    444-phase3-tsai
    """
    # unroll print
    # print("             parent_state[%d]," % square_index)
    state = [parent_state[2],
             parent_state[3],
             parent_state[5],
             parent_state[6],
             parent_state[7],
             parent_state[8],
             parent_state[9],
             parent_state[10],
             parent_state[11],
             parent_state[12],
             parent_state[14],
             parent_state[15],
             parent_state[18],
             parent_state[19],
             parent_state[21],
             parent_state[22],
             parent_state[23],
             parent_state[24],
             parent_state[25],
             parent_state[26],
             parent_state[27],
             parent_state[28],
             parent_state[30],
             parent_state[31],
             parent_state[34],
             parent_state[35],
             parent_state[37],
             parent_state[38],
             parent_state[39],
             parent_state[40],
             parent_state[41],
             parent_state[42],
             parent_state[43],
             parent_state[44],
             parent_state[46],
             parent_state[47],
             parent_state[50],
             parent_state[51],
             parent_state[53],
             parent_state[54],
             parent_state[55],
             parent_state[56],
             parent_state[57],
             parent_state[58],
             parent_state[59],
             parent_state[60],
             parent_state[62],
             parent_state[63],
             parent_state[66],
             parent_state[67],
             parent_state[69],
             parent_state[70],
             parent_state[71],
             parent_state[72],
             parent_state[73],
             parent_state[74],
             parent_state[75],
             parent_state[76],
             parent_state[78],
             parent_state[79],
             parent_state[82],
             parent_state[83],
             parent_state[85],
             parent_state[86],
             parent_state[87],
             parent_state[88],
             parent_state[89],
             parent_state[90],
             parent_state[91],
             parent_state[92],
             parent_state[94],
             parent_state[95]]
    state = ''.join(state)
    return state


def get_444_UFBR_edges(parent_states, self):
    """
    444-UFBR-edges
    """
    state = []
    for side in self.sides_all:
        for square_index in side.edge_pos:
                partner_index = side.get_wing_partner(square_index)
                square1 = self.parent.state[square_index]
                square2 = self.parent.state[partner_index]
                wing_str = "%s%s" % (square1, square2)

                if wing_str in ('UF', 'UB', 'UR', 'FU', 'BU', 'RU'):
                    state.append(square1)
                else:
                    state.append('x')
    state = ''.join(state)
    return state


def get_444_ULRF_edges(parent_state, self):
    """
    444-ULRF-edges
    """
    state = []
    for side in self.sides_all:
        for square_index in side.edge_pos:
                partner_index = side.get_wing_partner(square_index)
                square1 = self.parent.state[square_index]
                square2 = self.parent.state[partner_index]
                wing_str = "%s%s" % (square1, square2)

                if wing_str in ('UL', 'UR', 'UF', 'LU', 'RU', 'FU'):
                    state.append(square1)
                else:
                    state.append('x')
    state = ''.join(state)
    return state


def get_444_DFBR_edges(parent_state, self):
    """
    444-DFBR-edges
    """
    state = []
    for side in self.sides_all:
        for square_index in side.edge_pos:
                partner_index = side.get_wing_partner(square_index)
                square1 = self.parent.state[square_index]
                square2 = self.parent.state[partner_index]
                wing_str = "%s%s" % (square1, square2)

                if wing_str in ('DF', 'DB', 'DR', 'FD', 'BD', 'RD'):
                    state.append(square1)
                else:
                    state.append('x')
    state = ''.join(state)
    return state


def get_444_DLRF_edges(parent_state, self):
    """
    444-DLRF-edges
    """
    state = []
    for side in self.sides_all:
        for square_index in side.edge_pos:
                partner_index = side.get_wing_partner(square_index)
                square1 = self.parent.state[square_index]
                square2 = self.parent.state[partner_index]
                wing_str = "%s%s" % (square1, square2)

                if wing_str in ('DL', 'DR', 'DF', 'LD', 'RD', 'FD'):
                    state.append(square1)
                else:
                    state.append('x')
    state = ''.join(state)
    return state


def get_555_UD_centers_stage_state(parent_state):
    """
    555-UD-centers-stage
    """
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
    """
    555-UD-T-centers-stage
    """
    state = ''.join(['x', parent_state[8], 'x', parent_state[12], parent_state[13], parent_state[14], 'x', parent_state[18], 'xx', parent_state[33], 'x', parent_state[37], parent_state[38], parent_state[39], 'x', parent_state[43], 'xx', parent_state[58], 'x', parent_state[62], parent_state[63], parent_state[64], 'x', parent_state[68], 'xx', parent_state[83], 'x', parent_state[87], parent_state[88], parent_state[89], 'x', parent_state[93], 'xx', parent_state[108], 'x', parent_state[112], parent_state[113], parent_state[114], 'x', parent_state[118], 'xx', parent_state[133], 'x', parent_state[137], parent_state[138], parent_state[139], 'x', parent_state[143], 'x'])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_555_UD_X_centers_stage_state(parent_state):
    """
    555-UD-X-centers-stage
    """
    state = ''.join([parent_state[7], 'x', parent_state[9], 'x', parent_state[13], 'x', parent_state[17], 'x', parent_state[19], parent_state[32], 'x', parent_state[34], 'x', parent_state[38], 'x', parent_state[42], 'x', parent_state[44], parent_state[57], 'x', parent_state[59], 'x', parent_state[63], 'x', parent_state[67], 'x', parent_state[69], parent_state[82], 'x', parent_state[84], 'x', parent_state[88], 'x', parent_state[92], 'x', parent_state[94], parent_state[107], 'x', parent_state[109], 'x', parent_state[113], 'x', parent_state[117], 'x', parent_state[119], parent_state[132], 'x', parent_state[134], 'x', parent_state[138], 'x', parent_state[142], 'x', parent_state[144]])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_555_UD_centers_stage_LFRB_only_state(parent_state):
    """
    555-UD-centers-stage-LFRB-only
    """
    state = ''.join([parent_state[32], parent_state[33], parent_state[34], # Left
                     parent_state[37], parent_state[38], parent_state[39],
                     parent_state[42], parent_state[43], parent_state[44],
                     parent_state[57], parent_state[58], parent_state[59], # Front
                     parent_state[62], parent_state[63], parent_state[64],
                     parent_state[67], parent_state[68], parent_state[69],
                     parent_state[82], parent_state[83], parent_state[84], # Right
                     parent_state[87], parent_state[88], parent_state[89],
                     parent_state[92], parent_state[93], parent_state[94],
                     parent_state[107], parent_state[108], parent_state[109], # Back
                     parent_state[112], parent_state[113], parent_state[114],
                     parent_state[117], parent_state[118], parent_state[119]])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_555_UD_centers_stage_UFDB_only_state(parent_state):
    """
    555-UD-centers-stage-UFDB-only
    """
    state = ''.join([parent_state[7], parent_state[8], parent_state[9],    # Upper
                     parent_state[12], parent_state[13], parent_state[14],
                     parent_state[17], parent_state[18], parent_state[19],
                     parent_state[57], parent_state[58], parent_state[59], # Front
                     parent_state[62], parent_state[63], parent_state[64],
                     parent_state[67], parent_state[68], parent_state[69],
                     parent_state[132], parent_state[133], parent_state[134], # Down
                     parent_state[137], parent_state[138], parent_state[139],
                     parent_state[142], parent_state[143], parent_state[144],
                     parent_state[107], parent_state[108], parent_state[109], # Back
                     parent_state[112], parent_state[113], parent_state[114],
                     parent_state[117], parent_state[118], parent_state[119]])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_555_UD_centers_stage_ULDR_only_state(parent_state):
    """
    555-UD-centers-stage-ULDR-only
    """
    state = ''.join([parent_state[7], parent_state[8], parent_state[9],    # Upper
                     parent_state[12], parent_state[13], parent_state[14],
                     parent_state[17], parent_state[18], parent_state[19],
                     parent_state[32], parent_state[33], parent_state[34], # Left
                     parent_state[37], parent_state[38], parent_state[39],
                     parent_state[42], parent_state[43], parent_state[44],
                     parent_state[132], parent_state[133], parent_state[134], # Down
                     parent_state[137], parent_state[138], parent_state[139],
                     parent_state[142], parent_state[143], parent_state[144],
                     parent_state[82], parent_state[83], parent_state[84], # Right
                     parent_state[87], parent_state[88], parent_state[89],
                     parent_state[92], parent_state[93], parent_state[94]])
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_555_UD_centers_solve_on_all(parent_state):
    """
    555-UD-centers-solve-on-all
    """
    state = [parent_state[7],
             parent_state[8],
             parent_state[9],
             parent_state[12],
             parent_state[13],
             parent_state[14],
             parent_state[17],
             parent_state[18],
             parent_state[19],
             parent_state[32],
             parent_state[33],
             parent_state[34],
             parent_state[37],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[44],
             parent_state[57],
             parent_state[58],
             parent_state[59],
             parent_state[62],
             parent_state[63],
             parent_state[64],
             parent_state[67],
             parent_state[68],
             parent_state[69],
             parent_state[82],
             parent_state[83],
             parent_state[84],
             parent_state[87],
             parent_state[88],
             parent_state[89],
             parent_state[92],
             parent_state[93],
             parent_state[94],
             parent_state[107],
             parent_state[108],
             parent_state[109],
             parent_state[112],
             parent_state[113],
             parent_state[114],
             parent_state[117],
             parent_state[118],
             parent_state[119],
             parent_state[132],
             parent_state[133],
             parent_state[134],
             parent_state[137],
             parent_state[138],
             parent_state[139],
             parent_state[142],
             parent_state[143],
             parent_state[144]]
    state = ''.join(state)
    state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x')
    return state


def get_555_LR_centers_solve_on_all(parent_state):
    """
    555-LR-centers-solve-on-all
    """
    state = [parent_state[7],
             parent_state[8],
             parent_state[9],
             parent_state[12],
             parent_state[13],
             parent_state[14],
             parent_state[17],
             parent_state[18],
             parent_state[19],
             parent_state[32],
             parent_state[33],
             parent_state[34],
             parent_state[37],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[44],
             parent_state[57],
             parent_state[58],
             parent_state[59],
             parent_state[62],
             parent_state[63],
             parent_state[64],
             parent_state[67],
             parent_state[68],
             parent_state[69],
             parent_state[82],
             parent_state[83],
             parent_state[84],
             parent_state[87],
             parent_state[88],
             parent_state[89],
             parent_state[92],
             parent_state[93],
             parent_state[94],
             parent_state[107],
             parent_state[108],
             parent_state[109],
             parent_state[112],
             parent_state[113],
             parent_state[114],
             parent_state[117],
             parent_state[118],
             parent_state[119],
             parent_state[132],
             parent_state[133],
             parent_state[134],
             parent_state[137],
             parent_state[138],
             parent_state[139],
             parent_state[142],
             parent_state[143],
             parent_state[144]]
    state = ''.join(state)
    state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x')
    return state


def get_555_FB_centers_solve_on_all(parent_state):
    """
    555-FB-centers-solve-on-all
    """
    state = [parent_state[7],
             parent_state[8],
             parent_state[9],
             parent_state[12],
             parent_state[13],
             parent_state[14],
             parent_state[17],
             parent_state[18],
             parent_state[19],
             parent_state[32],
             parent_state[33],
             parent_state[34],
             parent_state[37],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[44],
             parent_state[57],
             parent_state[58],
             parent_state[59],
             parent_state[62],
             parent_state[63],
             parent_state[64],
             parent_state[67],
             parent_state[68],
             parent_state[69],
             parent_state[82],
             parent_state[83],
             parent_state[84],
             parent_state[87],
             parent_state[88],
             parent_state[89],
             parent_state[92],
             parent_state[93],
             parent_state[94],
             parent_state[107],
             parent_state[108],
             parent_state[109],
             parent_state[112],
             parent_state[113],
             parent_state[114],
             parent_state[117],
             parent_state[118],
             parent_state[119],
             parent_state[132],
             parent_state[133],
             parent_state[134],
             parent_state[137],
             parent_state[138],
             parent_state[139],
             parent_state[142],
             parent_state[143],
             parent_state[144]]
    state = ''.join(state)
    state = state.replace('U', 'x').replace('L', 'x').replace('R', 'x').replace('D', 'x')
    return state


def get_555_LR_centers_stage_on_LFRB(parent_state):
    """
    555-LR-centers-stage-on-LFRB
    """
    state = [parent_state[32],
             parent_state[33],
             parent_state[34],
             parent_state[37],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[44],
             parent_state[57],
             parent_state[58],
             parent_state[59],
             parent_state[62],
             parent_state[63],
             parent_state[64],
             parent_state[67],
             parent_state[68],
             parent_state[69],
             parent_state[82],
             parent_state[83],
             parent_state[84],
             parent_state[87],
             parent_state[88],
             parent_state[89],
             parent_state[92],
             parent_state[93],
             parent_state[94],
             parent_state[107],
             parent_state[108],
             parent_state[109],
             parent_state[112],
             parent_state[113],
             parent_state[114],
             parent_state[117],
             parent_state[118],
             parent_state[119]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1')
    return state


def get_555_ULFRBD_centers_solve(parent_state):
    """
    555-ULFRBD-centers-solve
    """
    state = [parent_state[7],
             parent_state[8],
             parent_state[9],
             parent_state[12],
             parent_state[13],
             parent_state[14],
             parent_state[17],
             parent_state[18],
             parent_state[19],
             parent_state[32],
             parent_state[33],
             parent_state[34],
             parent_state[37],
             parent_state[38],
             parent_state[39],
             parent_state[42],
             parent_state[43],
             parent_state[44],
             parent_state[57],
             parent_state[58],
             parent_state[59],
             parent_state[62],
             parent_state[63],
             parent_state[64],
             parent_state[67],
             parent_state[68],
             parent_state[69],
             parent_state[82],
             parent_state[83],
             parent_state[84],
             parent_state[87],
             parent_state[88],
             parent_state[89],
             parent_state[92],
             parent_state[93],
             parent_state[94],
             parent_state[107],
             parent_state[108],
             parent_state[109],
             parent_state[112],
             parent_state[113],
             parent_state[114],
             parent_state[117],
             parent_state[118],
             parent_state[119],
             parent_state[132],
             parent_state[133],
             parent_state[134],
             parent_state[137],
             parent_state[138],
             parent_state[139],
             parent_state[142],
             parent_state[143],
             parent_state[144]]
    state = ''.join(state)
    return state


def get_555_LR_centers_stage_on_LFRB_x_center_only(parent_state):
    """
    555-LR-centers-stage-on-LFRB-x-center-only
    """
    state = [parent_state[32],
             'x',
             parent_state[34],
             'x',
             parent_state[38],
             'x',
             parent_state[42],
             'x',
             parent_state[44],

             parent_state[57],
             'x',
             parent_state[59],
             'x',
             parent_state[63],
             'x',
             parent_state[67],
             'x',
             parent_state[69],

             parent_state[82],
             'x',
             parent_state[84],
             'x',
             parent_state[88],
             'x',
             parent_state[92],
             'x',
             parent_state[94],

             parent_state[107],
             'x',
             parent_state[109],
             'x',
             parent_state[113],
             'x',
             parent_state[117],
             'x',
             parent_state[119]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1')
    return state


def get_555_LR_centers_stage_on_LFRB_t_center_only(parent_state):
    """
    555-LR-centers-stage-on-LFRB-t-center-only
    """
    state = ['x',
             parent_state[33],
             'x',
             parent_state[37],
             parent_state[38],
             parent_state[39],
             'x',
             parent_state[43],
             'x'

             'x',
             parent_state[58],
             'x',
             parent_state[62],
             parent_state[63],
             parent_state[64],
             'x',
             parent_state[68],
             'x'

             'x',
             parent_state[83],
             'x',
             parent_state[87],
             parent_state[88],
             parent_state[89],
             'x',
             parent_state[93],
             'x'

             'x',
             parent_state[108],
             'x',
             parent_state[112],
             parent_state[113],
             parent_state[114],
             'x',
             parent_state[118],
             'x']
    state = ''.join(state)
    state = state.replace('x', '0').replace('F', '0').replace('R', '1').replace('B', '0').replace('L', '1')
    return state


def get_666_UD_centers_oblique_edges_solve(parent_state):
    """
    666-UD-centers-oblique-edges-solve
    """
    state = ['x',
             parent_state[9],
             parent_state[10],
             'x',
             parent_state[14],
             parent_state[15],
             parent_state[16],
             parent_state[17],
             parent_state[20],
             parent_state[21],
             parent_state[22],
             parent_state[23],
             'x',
             parent_state[27],
             parent_state[28],
             'x',
             'x',
             parent_state[189],
             parent_state[190],
             'x',
             parent_state[194],
             parent_state[195],
             parent_state[196],
             parent_state[197],
             parent_state[200],
             parent_state[201],
             parent_state[202],
             parent_state[203],
             'x',
             parent_state[207],
             parent_state[208],
             'x']

    state = ''.join(state)
    return state


def get_666_LR_centers_oblique_edges_solve(parent_state):
    """
    666-LR-centers-oblique-edges-solve
    """
    state = ['x',
             parent_state[45],
             parent_state[46],
             'x',
             parent_state[50],
             parent_state[51],
             parent_state[52],
             parent_state[53],
             parent_state[56],
             parent_state[57],
             parent_state[58],
             parent_state[59],
             'x',
             parent_state[63],
             parent_state[64],
             'x',
             'x',
             parent_state[117],
             parent_state[118],
             'x',
             parent_state[122],
             parent_state[123],
             parent_state[124],
             parent_state[125],
             parent_state[128],
             parent_state[129],
             parent_state[130],
             parent_state[131],
             'x',
             parent_state[135],
             parent_state[136],
             'x']
    state = ''.join(state)
    return state


def get_666_FB_centers_oblique_edges_solve(parent_state):
    """
    666-FB-centers-oblique-edges-solve
    """
    state = ['x',
             parent_state[81],
             parent_state[82],
             'x',
             parent_state[86],
             parent_state[87],
             parent_state[88],
             parent_state[89],
             parent_state[92],
             parent_state[93],
             parent_state[94],
             parent_state[95],
             'x',
             parent_state[99],
             parent_state[100],
             'x',
             'x',
             parent_state[153],
             parent_state[154],
             'x',
             parent_state[158],
             parent_state[159],
             parent_state[160],
             parent_state[161],
             parent_state[164],
             parent_state[165],
             parent_state[166],
             parent_state[167],
             'x',
             parent_state[171],
             parent_state[172],
             'x']
    state = ''.join(state)
    return state


def get_666_LFRB_centers_oblique_edges_solve(parent_state):
    """
    666-LFRB-centers-oblique-edges-solve
    """
    state = ''.join(['x', parent_state[45], parent_state[46], 'x', parent_state[50], parent_state[51], parent_state[52], parent_state[53], parent_state[56], parent_state[57], parent_state[58], parent_state[59], 'x', parent_state[63], parent_state[64], 'xx', parent_state[81], parent_state[82], 'x', parent_state[86], parent_state[87], parent_state[88], parent_state[89], parent_state[92], parent_state[93], parent_state[94], parent_state[95], 'x', parent_state[99], parent_state[100], 'xx', parent_state[117], parent_state[118], 'x', parent_state[122], parent_state[123], parent_state[124], parent_state[125], parent_state[128], parent_state[129], parent_state[130], parent_state[131], 'x', parent_state[135], parent_state[136], 'xx', parent_state[153], parent_state[154], 'x', parent_state[158], parent_state[159], parent_state[160], parent_state[161], parent_state[164], parent_state[165], parent_state[166], parent_state[167], 'x', parent_state[171], parent_state[172], 'x'])
    return state


def get_666_UD_inner_X_centers_stage(parent_state):
    """
    666-UD-inner-X-centers-stage
    """
    state = ['xxxxx', parent_state[15], parent_state[16], 'xx', parent_state[21], parent_state[22], 'xxxxx',
             'xxxxx', parent_state[51], parent_state[52], 'xx', parent_state[57], parent_state[58], 'xxxxx',
             'xxxxx', parent_state[87], parent_state[88], 'xx', parent_state[93], parent_state[94], 'xxxxx',
             'xxxxx', parent_state[123], parent_state[124], 'xx', parent_state[129], parent_state[130], 'xxxxx',
             'xxxxx', parent_state[159], parent_state[160], 'xx', parent_state[165], parent_state[166], 'xxxxx',
             'xxxxx', parent_state[195], parent_state[196], 'xx', parent_state[201], parent_state[202], 'xxxxx']
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_666_UD_oblique_edge_pairing(parent_state):
    """
    666-UD-oblique-edge-pairing
    """
    state = [parent_state[9], parent_state[10],
             parent_state[14], parent_state[17],
             parent_state[20], parent_state[23],
             parent_state[27], parent_state[28],
             parent_state[45], parent_state[46],
             parent_state[50], parent_state[53],
             parent_state[56], parent_state[59],
             parent_state[63], parent_state[64],
             parent_state[81], parent_state[82],
             parent_state[86], parent_state[89],
             parent_state[92], parent_state[95],
             parent_state[99], parent_state[100],
             parent_state[117], parent_state[118],
             parent_state[122], parent_state[125],
             parent_state[128], parent_state[131],
             parent_state[135], parent_state[136],
             parent_state[153], parent_state[154],
             parent_state[158], parent_state[161],
             parent_state[164], parent_state[167],
             parent_state[171], parent_state[172],
             parent_state[189], parent_state[190],
             parent_state[194], parent_state[197],
             parent_state[200], parent_state[203],
             parent_state[207], parent_state[208]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_666_UD_oblique_edge_pairing_left_only(parent_state):
    """
    666-UD-oblique-edge-pairing-left-only
    """
    state = [parent_state[9], 'x',
             'x', parent_state[17],
             parent_state[20], 'x',
             'x', parent_state[28],
             parent_state[45], 'x',
             'x', parent_state[53],
             parent_state[56], 'x',
             'x', parent_state[64],
             parent_state[81], 'x',
             'x', parent_state[89],
             parent_state[92], 'x',
             'x', parent_state[100],
             parent_state[117], 'x',
             'x', parent_state[125],
             parent_state[128], 'x',
             'x', parent_state[136],
             parent_state[153], 'x',
             'x', parent_state[161],
             parent_state[164], 'x',
             'x', parent_state[172],
             parent_state[189], 'x',
             'x', parent_state[197],
             parent_state[200], 'x',
             'x', parent_state[208]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_666_UD_oblique_edge_pairing_right_only(parent_state):
    """
    666-UD-oblique-edge-pairing-right-only
    """
    state = ['x', parent_state[10],
            parent_state[14], 'x',
            'x', parent_state[23],
            parent_state[27], 'x',
            'x', parent_state[46],
            parent_state[50], 'x',
            'x', parent_state[59],
            parent_state[63], 'x',
            'x', parent_state[82],
            parent_state[86], 'x',
            'x', parent_state[95],
            parent_state[99], 'x',
            'x', parent_state[118],
            parent_state[122], 'x',
            'x', parent_state[131],
            parent_state[135], 'x',
            'x', parent_state[154],
            parent_state[158], 'x',
            'x', parent_state[167],
            parent_state[171], 'x',
            'x', parent_state[190],
            parent_state[194], 'x',
            'x', parent_state[203],
            parent_state[207], 'x']
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_666_UD_oblique_edge_pairing_LFRB_only(parent_state):
    """
    666-UD-oblique-edge-pairing-LFRB-only
    """
    state = [parent_state[45], parent_state[46],
             parent_state[50], parent_state[53],
             parent_state[56], parent_state[59],
             parent_state[63], parent_state[64],
             parent_state[81], parent_state[82],
             parent_state[86], parent_state[89],
             parent_state[92], parent_state[95],
             parent_state[99], parent_state[100],
             parent_state[117], parent_state[118],
             parent_state[122], parent_state[125],
             parent_state[128], parent_state[131],
             parent_state[135], parent_state[136],
             parent_state[153], parent_state[154],
             parent_state[158], parent_state[161],
             parent_state[164], parent_state[167],
             parent_state[171], parent_state[172]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_666_LR_inner_X_centers_stage(parent_state):
    """
    666-LR-inner-X-centers-stage
    """
    state = ['xxxxx', parent_state[15], parent_state[16], 'xx', parent_state[21], parent_state[22], 'xxxxx',
             'xxxxx', parent_state[51], parent_state[52], 'xx', parent_state[57], parent_state[58], 'xxxxx',
             'xxxxx', parent_state[87], parent_state[88], 'xx', parent_state[93], parent_state[94], 'xxxxx',
             'xxxxx', parent_state[123], parent_state[124], 'xx', parent_state[129], parent_state[130], 'xxxxx',
             'xxxxx', parent_state[159], parent_state[160], 'xx', parent_state[165], parent_state[166], 'xxxxx',
             'xxxxx', parent_state[195], parent_state[196], 'xx', parent_state[201], parent_state[202], 'xxxxx']
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')
    return state


def get_666_LR_oblique_edge_pairing(parent_state):
    """
    666-LR-oblique-edge-pairing:
    """
    state = [parent_state[45], parent_state[46],
             parent_state[50], parent_state[53],
             parent_state[56], parent_state[59],
             parent_state[63], parent_state[64],
             parent_state[81], parent_state[82],
             parent_state[86], parent_state[89],
             parent_state[92], parent_state[95],
             parent_state[99], parent_state[100],
             parent_state[117], parent_state[118],
             parent_state[122], parent_state[125],
             parent_state[128], parent_state[131],
             parent_state[135], parent_state[136],
             parent_state[153], parent_state[154],
             parent_state[158], parent_state[161],
             parent_state[164], parent_state[167],
             parent_state[171], parent_state[172]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')
    return state


def get_666_LR_oblique_edge_pairing_left_only(parent_state):
    """
    666-LR-oblique-edge-pairing-left-only
    """
    state = [parent_state[45], 'x',
             'x', parent_state[53],
             parent_state[56], 'x',
             'x', parent_state[64],
             parent_state[81], 'x',
             'x', parent_state[89],
             parent_state[92], 'x',
             'x', parent_state[100],
             parent_state[117], 'x',
             'x', parent_state[125],
             parent_state[128], 'x',
             'x', parent_state[136],
             parent_state[153], 'x',
             'x', parent_state[161],
             parent_state[164], 'x',
             'x', parent_state[172]]
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')
    return state


def get_666_LR_oblique_edge_pairing_right_only(parent_state):
    """
    666-LR-oblique-edge-pairing-right-only
    """
    state = ['x', parent_state[46],
             parent_state[50], 'x',
             'x', parent_state[59],
             parent_state[63], 'x',
             'x', parent_state[82],
             parent_state[86], 'x',
             'x', parent_state[95],
             parent_state[99], 'x',
             'x', parent_state[118],
             parent_state[122], 'x',
             'x', parent_state[131],
             parent_state[135], 'x',
             'x', parent_state[154],
             parent_state[158], 'x',
             'x', parent_state[167],
             parent_state[171] + 'x']
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('L', '1').replace('F', '0').replace('R', '1').replace('B', '0').replace('D', '0')
    return state


def get_777_UD_centers_oblique_edges_solve(parent_state):
    """
    777-UD-centers-oblique-edges-solve
    """
    state = ['x',
             parent_state[10],
             parent_state[11],
             parent_state[12],
             'x',
             parent_state[16],
             parent_state[17],
             parent_state[18],
             parent_state[19],
             parent_state[20],
             parent_state[23],
             parent_state[24],
             parent_state[25],
             parent_state[26],
             parent_state[27],
             parent_state[30],
             parent_state[31],
             parent_state[32],
             parent_state[33],
             parent_state[34],
             'x',
             parent_state[38],
             parent_state[39],
             parent_state[40],
             'x',
             'x',
             parent_state[255],
             parent_state[256],
             parent_state[257],
             'x',
             parent_state[261],
             parent_state[262],
             parent_state[263],
             parent_state[264],
             parent_state[265],
             parent_state[268],
             parent_state[269],
             parent_state[270],
             parent_state[271],
             parent_state[272],
             parent_state[275],
             parent_state[276],
             parent_state[277],
             parent_state[278],
             parent_state[279],
             'x',
             parent_state[283],
             parent_state[284],
             parent_state[285],
             'x']
    state = ''.join(state)
    return state


def get_777_LFRB_centers_oblique_edges_solve(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve
    """
    return ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x', parent_state[65], parent_state[66], parent_state[67], parent_state[68], parent_state[69], parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], parent_state[79], parent_state[80], parent_state[81], parent_state[82], parent_state[83], 'x', parent_state[87], parent_state[88], parent_state[89], 'xx', parent_state[108], parent_state[109], parent_state[110], 'x', parent_state[114], parent_state[115], parent_state[116], parent_state[117], parent_state[118], parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], parent_state[128], parent_state[129], parent_state[130], parent_state[131], parent_state[132], 'x', parent_state[136], parent_state[137], parent_state[138], 'xx', parent_state[157], parent_state[158], parent_state[159], 'x', parent_state[163], parent_state[164], parent_state[165], parent_state[166], parent_state[167], parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], parent_state[177], parent_state[178], parent_state[179], parent_state[180], parent_state[181], 'x', parent_state[185], parent_state[186], parent_state[187], 'xx', parent_state[206], parent_state[207], parent_state[208], 'x', parent_state[212], parent_state[213], parent_state[214], parent_state[215], parent_state[216], parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], parent_state[226], parent_state[227], parent_state[228], parent_state[229], parent_state[230], 'x', parent_state[234], parent_state[235], parent_state[236], 'x'])


def get_777_UD_oblique_edge_pairing(parent_state):
    """
    777-UD-oblique-edge-pairing
    """
    state = ['x', parent_state[10], parent_state[11], parent_state[12], 'x',
             parent_state[16], 'xxx', parent_state[20],
             parent_state[23], 'xxx', parent_state[27],
             parent_state[30], 'xxx', parent_state[34],
             'x', parent_state[38], parent_state[39], parent_state[40], 'x',
             'x', parent_state[59], parent_state[60], parent_state[61], 'x',
             parent_state[65], 'xxx', parent_state[69],
             parent_state[72], 'xxx', parent_state[76],
             parent_state[79], 'xxx', parent_state[83],
             'x', parent_state[87], parent_state[88], parent_state[89], 'x',
             'x', parent_state[108], parent_state[109], parent_state[110], 'x',
             parent_state[114], 'xxx', parent_state[118],
             parent_state[121], 'xxx', parent_state[125],
             parent_state[128], 'xxx', parent_state[132],
             'x', parent_state[136], parent_state[137], parent_state[138], 'x',
             'x', parent_state[157], parent_state[158], parent_state[159], 'x',
             parent_state[163], 'xxx', parent_state[167],
             parent_state[170], 'xxx', parent_state[174],
             parent_state[177], 'xxx', parent_state[181],
             'x', parent_state[185], parent_state[186], parent_state[187], 'x',
             'x', parent_state[206], parent_state[207], parent_state[208], 'x',
             parent_state[212], 'xxx', parent_state[216],
             parent_state[219], 'xxx', parent_state[223],
             parent_state[226], 'xxx', parent_state[230],
             'x', parent_state[234], parent_state[235], parent_state[236], 'x',
             'x', parent_state[255], parent_state[256], parent_state[257], 'x',
             parent_state[261], 'xxx', parent_state[265],
             parent_state[268], 'xxx', parent_state[272],
             parent_state[275], 'xxx', parent_state[279],
             'x', parent_state[283], parent_state[284], parent_state[285], 'x']
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_777_UD_oblique_edge_pairing_middle_only(parent_state):
    """
    777-UD-oblique-edge-pairing-middle-only
    """
    state = ['xx', parent_state[11], 'xx',
             'xxxxx',
             parent_state[23], 'xxx', parent_state[27],
             'xxxxx',
             'xx', parent_state[39], 'xx',
             'xx', parent_state[60], 'xx',
             'xxxxx',
             parent_state[72], 'xxx', parent_state[76],
             'xxxxx',
             'xx', parent_state[88], 'xx',
             'xx', parent_state[109], 'xx',
             'xxxxx',
             parent_state[121], 'xxx', parent_state[125],
             'xxxxx',
             'xx', parent_state[137], 'xx',
             'xx', parent_state[158], 'xx',
             'xxxxx',
             parent_state[170], 'xxx', parent_state[174],
             'xxxxx',
             'xx', parent_state[186], 'xx',
             'xx', parent_state[207], 'xx',
             'xxxxx',
             parent_state[219], 'xxx', parent_state[223],
             'xxxxx',
             'xx', parent_state[235], 'xx',
             'xx', parent_state[256], 'xx',
             'xxxxx',
             parent_state[268], 'xxx', parent_state[272],
             'xxxxx',
             'xx', parent_state[284], 'xx']
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_777_UD_oblique_edge_pairing_left_only(parent_state):
    """
    777-UD-oblique-edge-pairing-left-only
    """
    state = ['x', parent_state[10], 'xxx',
             'xxxx', parent_state[20],
             'xxxxx',
             parent_state[30], 'xxxx',
             'xxx', parent_state[40], 'x',
             'x', parent_state[59], 'xxx',
             'xxxx', parent_state[69],
             'xxxxx',
             parent_state[79], 'xxxx',
             'xxx', parent_state[89], 'x',
             'x', parent_state[108], 'xxx',
             'xxxx', parent_state[118],
             'xxxxx',
             parent_state[128], 'xxxx',
             'xxx', parent_state[138], 'x',
             'x', parent_state[157], 'xxx',
             'xxxx', parent_state[167],
             'xxxxx',
             parent_state[177], 'xxxx',
             'xxx', parent_state[187], 'x',
             'x', parent_state[206], 'xxx',
             'xxxx', parent_state[216],
             'xxxxx',
             parent_state[226], 'xxxx',
             'xxx', parent_state[236], 'x',
             'x', parent_state[255], 'xxx',
             'xxxx', parent_state[265],
             'xxxxx',
             parent_state[275], 'xxxx',
             'xxx', parent_state[285], 'x']
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_777_UD_oblique_edge_pairing_right_only(parent_state):
    """
    777-UD-oblique-edge-pairing-right-only
    """
    state = ['xxx', parent_state[12], 'x',
             parent_state[16], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[34],
             'x', parent_state[38], 'xxx',
             'xxx', parent_state[61], 'x',
             parent_state[65], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[83],
             'x', parent_state[87], 'xxx',
             'xxx', parent_state[110], 'x',
             parent_state[114], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[132],
             'x', parent_state[136], 'xxx',
             'xxx', parent_state[159], 'x',
             parent_state[163], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[181],
             'x', parent_state[185], 'xxx',
             'xxx', parent_state[208], 'x',
             parent_state[212], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[230],
             'x', parent_state[234], 'xxx',
             'xxx', parent_state[257], 'x',
             parent_state[261], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[279],
             'x', parent_state[283], 'xxx']
    state = ''.join(state)
    state = state.replace('x', '0').replace('L', '0').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '1').replace('U', '1')
    return state


def get_777_LR_oblique_edge_pairing(parent_state):
    """
    777-LR-oblique-edge-pairing
    """
    state = ['x', parent_state[59], parent_state[60], parent_state[61], 'x',
             parent_state[65], 'xxx', parent_state[69],
             parent_state[72], 'xxx', parent_state[76],
             parent_state[79], 'xxx', parent_state[83],
             'x', parent_state[87], parent_state[88], parent_state[89], 'x',
             'x', parent_state[108], parent_state[109], parent_state[110], 'x',
             parent_state[114], 'xxx', parent_state[118],
             parent_state[121], 'xxx', parent_state[125],
             parent_state[128], 'xxx', parent_state[132],
             'x', parent_state[136], parent_state[137], parent_state[138], 'x',
             'x', parent_state[157], parent_state[158], parent_state[159], 'x',
             parent_state[163], 'xxx', parent_state[167],
             parent_state[170], 'xxx', parent_state[174],
             parent_state[177], 'xxx', parent_state[181],
             'x', parent_state[185], parent_state[186], parent_state[187], 'x',
             'x', parent_state[206], parent_state[207], parent_state[208], 'x',
             parent_state[212], 'xxx', parent_state[216],
             parent_state[219], 'xxx', parent_state[223],
             parent_state[226], 'xxx', parent_state[230],
             'x', parent_state[234], parent_state[235], parent_state[236], 'x']
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')
    return state


def get_777_LR_oblique_edge_pairing_middle_only(parent_state):
    """
    777-LR-oblique-edge-pairing-middle-only
    """
    state = ['xx', parent_state[60], 'xx',
             'xxxxx',
             parent_state[72], 'xxx', parent_state[76],
             'xxxxx',
             'xx', parent_state[88], 'xx',
             'xx', parent_state[109], 'xx',
             'xxxxx',
             parent_state[121], 'xxx', parent_state[125],
             'xxxxx',
             'xx', parent_state[137], 'xx',
             'xx', parent_state[158], 'xx',
             'xxxxx',
             parent_state[170], 'xxx', parent_state[174],
             'xxxxx',
             'xx', parent_state[186], 'xx',
             'xx', parent_state[207], 'xx',
             'xxxxx',
             parent_state[219], 'xxx', parent_state[223],
             'xxxxx',
             'xx', parent_state[235], 'xx']
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')
    return state


def get_777_LR_oblique_edge_pairing_left_only(parent_state):
    """
    777-LR-oblique-edge-pairing-left-only
    """
    state = ['x', parent_state[59], 'xxx',
             'xxxx', parent_state[69],
             'xxxxx',
             parent_state[79], 'xxxx',
             'xxx', parent_state[89], 'x',
             'x', parent_state[108], 'xxx',
             'xxxx', parent_state[118],
             'xxxxx',
             parent_state[128], 'xxxx',
             'xxx', parent_state[138], 'x',
             'x', parent_state[157], 'xxx',
             'xxxx', parent_state[167],
             'xxxxx',
             parent_state[177], 'xxxx',
             'xxx', parent_state[187], 'x',
             'x', parent_state[206], 'xxx',
             'xxxx', parent_state[216],
             'xxxxx',
             parent_state[226], 'xxxx',
             'xxx', parent_state[236], 'x']
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')
    return state


def get_777_LR_oblique_edge_pairing_right_only(parent_state):
    """
    777-LR-oblique-edge-pairing-right-only
    """
    state = ['xxx', parent_state[61], 'x',
             parent_state[65], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[83],
             'x', parent_state[87], 'xxx',
             'xxx', parent_state[110], 'x',
             parent_state[114], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[132],
             'x', parent_state[136], 'xxx',
             'xxx', parent_state[159], 'x',
             parent_state[163], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[181],
             'x', parent_state[185], 'xxx',
             'xxx', parent_state[208], 'x',
             parent_state[212], 'xxxx',
             'xxxxx',
             'xxxx', parent_state[230],
             'x', parent_state[234], 'xxx']
    state = ''.join(state)
    state = state.replace('x', '0').replace('U', '0').replace('F', '0').replace('D', '0').replace('B', '0').replace('R', '1').replace('L', '1')
    return state


def get_777_UD_centers_oblique_edges_solve_center_only(parent_state):
    """
    777-UD-centers-oblique-edges-solve-center-only
    """
    return ''.join(['xxxxxx', parent_state[17], parent_state[18], parent_state[19], 'xx', parent_state[24], 'x', parent_state[26], 'xx', parent_state[31], parent_state[32], parent_state[33], 'xxxxxxxx', 'xxxx', parent_state[262], parent_state[263], parent_state[264], 'xx', parent_state[269], 'x', parent_state[271], 'xx', parent_state[276], parent_state[277], parent_state[278], 'xxxxxx'])


def get_777_UD_centers_oblique_edges_solve_edges_only(parent_state):
    """
    777-UD-centers-oblique-edges-solve-edges-only
    """
    return ''.join(['x', parent_state[10], parent_state[11], parent_state[12], 'x', parent_state[16], 'xxx', parent_state[20], parent_state[23], 'xxx', parent_state[27], parent_state[30], 'xxx', parent_state[34], 'x', parent_state[38], parent_state[39], parent_state[40], 'xx', parent_state[255], parent_state[256], parent_state[257], 'x', parent_state[261], 'xxx', parent_state[265], parent_state[268], 'xxx', parent_state[272], parent_state[275], 'xxx', parent_state[279], 'x', parent_state[283], parent_state[284], parent_state[285], 'x'])


def get_777_LFRB_centers_oblique_edges_solve_inner_x_center_inner_t_center_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-only
    """
    return ''.join(['xxxxxx', parent_state[66], parent_state[67], parent_state[68], 'xx', parent_state[73], parent_state[74], parent_state[75], 'xx', parent_state[80], parent_state[81], parent_state[82], 'xxxxxx', 'xxxxxx', parent_state[115], parent_state[116], parent_state[117], 'xx', parent_state[122], parent_state[123], parent_state[124], 'xx', parent_state[129], parent_state[130], parent_state[131], 'xxxxxx', 'xxxxxx', parent_state[164], parent_state[165], parent_state[166], 'xx', parent_state[171], parent_state[172], parent_state[173], 'xx', parent_state[178], parent_state[179], parent_state[180], 'xxxxxx', 'xxxxxx', parent_state[213], parent_state[214], parent_state[215], 'xx', parent_state[220], parent_state[221], parent_state[222], 'xx', parent_state[227], parent_state[228], parent_state[229], 'xxxxxx'])


def get_777_LFRB_centers_oblique_edges_solve_inner_x_center_left_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-x-center-left-oblique-edge-only
    """
    return ''.join(['x', parent_state[59], 'xxxx', parent_state[66], 'x', parent_state[68], parent_state[69], 'xx', parent_state[74], 'xx', parent_state[79], parent_state[80], 'x', parent_state[82], 'xxxx', parent_state[89], 'xx', parent_state[108], 'xxxx', parent_state[115], 'x', parent_state[117], parent_state[118], 'xx', parent_state[123], 'xx', parent_state[128], parent_state[129], 'x', parent_state[131], 'xxxx', parent_state[138], 'xx', parent_state[157], 'xxxx', parent_state[164], 'x', parent_state[166], parent_state[167], 'xx', parent_state[172], 'xx', parent_state[177], parent_state[178], 'x', parent_state[180], 'xxxx', parent_state[187], 'xx', parent_state[206], 'xxxx', parent_state[213], 'x', parent_state[215], parent_state[216], 'xx', parent_state[221], 'xx', parent_state[226], parent_state[227], 'x', parent_state[229], 'xxxx', parent_state[236], 'x'])


def get_777_LFRB_centers_oblique_edges_solve_inner_x_center_middle_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-x-center-middle-oblique-edge-only
    """
    return ''.join(['xx', parent_state[60], 'xxx', parent_state[66], 'x', parent_state[68], 'x', parent_state[72], 'x', parent_state[74], 'x', parent_state[76], 'x', parent_state[80], 'x', parent_state[82], 'xxx', parent_state[88], 'xxxx', parent_state[109], 'xxx', parent_state[115], 'x', parent_state[117], 'x', parent_state[121], 'x', parent_state[123], 'x', parent_state[125], 'x', parent_state[129], 'x', parent_state[131], 'xxx', parent_state[137], 'xxxx', parent_state[158], 'xxx', parent_state[164], 'x', parent_state[166], 'x', parent_state[170], 'x', parent_state[172], 'x', parent_state[174], 'x', parent_state[178], 'x', parent_state[180], 'xxx', parent_state[186], 'xxxx', parent_state[207], 'xxx', parent_state[213], 'x', parent_state[215], 'x', parent_state[219], 'x', parent_state[221], 'x', parent_state[223], 'x', parent_state[227], 'x', parent_state[229], 'xxx', parent_state[235], 'x', 'x'])


def get_777_LFRB_centers_oblique_edges_solve_inner_x_center_right_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-x-center-right-oblique-edge-only
    """
    return ''.join(['xxx', parent_state[61], 'x', parent_state[65], parent_state[66], 'x', parent_state[68], 'xxx', parent_state[74], 'xxx', parent_state[80], 'x', parent_state[82], parent_state[83], 'x', parent_state[87], 'xxxxxx', parent_state[110], 'x', parent_state[114], parent_state[115], 'x', parent_state[117], 'xxx', parent_state[123], 'xxx', parent_state[129], 'x', parent_state[131], parent_state[132], 'x', parent_state[136], 'xxxxxx', parent_state[159], 'x', parent_state[163], parent_state[164], 'x', parent_state[166], 'xxx', parent_state[172], 'xxx', parent_state[178], 'x', parent_state[180], parent_state[181], 'x', parent_state[185], 'xxxxxx', parent_state[208], 'x', parent_state[212], parent_state[213], 'x', parent_state[215], 'xxx', parent_state[221], 'xxx', parent_state[227], 'x', parent_state[229], parent_state[230], 'x', parent_state[234], 'xxx'])


def get_777_LFRB_centers_oblique_edges_solve_inner_t_center_left_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-t-center-left-oblique-edge-only
    """
    return ''.join(['x', parent_state[59], 'xxxxx', parent_state[67], 'x', parent_state[69], 'x', parent_state[73], parent_state[74], parent_state[75], 'x', parent_state[79], 'x', parent_state[81], 'xxxxx', parent_state[89], 'xx', parent_state[108], 'xxxxx', parent_state[116], 'x', parent_state[118], 'x', parent_state[122], parent_state[123], parent_state[124], 'x', parent_state[128], 'x', parent_state[130], 'xxxxx', parent_state[138], 'xx', parent_state[157], 'xxxxx', parent_state[165], 'x', parent_state[167], 'x', parent_state[171], parent_state[172], parent_state[173], 'x', parent_state[177], 'x', parent_state[179], 'xxxxx', parent_state[187], 'xx', parent_state[206], 'xxxxx', parent_state[214], 'x', parent_state[216], 'x', parent_state[220], parent_state[221], parent_state[222], 'x', parent_state[226], 'x', parent_state[228], 'xxxxx', parent_state[236], 'x'])


def get_777_LFRB_centers_oblique_edges_solve_inner_t_center_middle_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-t-center-middle-oblique-edge-only
    """
    return ''.join(['xx', parent_state[60], 'xxxx', parent_state[67], 'xx', parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], 'xx', parent_state[81], 'xxxx', parent_state[88], 'xxxx', parent_state[109], 'xxxx', parent_state[116], 'xx', parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], 'xx', parent_state[130], 'xxxx', parent_state[137], 'xxxx', parent_state[158], 'xxxx', parent_state[165], 'xx', parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], 'xx', parent_state[179], 'xxxx', parent_state[186], 'xxxx', parent_state[207], 'xxxx', parent_state[214], 'xx', parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], 'xx', parent_state[228], 'xxxx', parent_state[235], 'x', 'x'])


def get_777_LFRB_centers_oblique_edges_solve_inner_x_center_inner_t_center_middle_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-middle-oblique-edge-only
    """
    return ''.join(['xx', parent_state[60], 'xxx', parent_state[66], parent_state[67], parent_state[68], 'x', parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76], 'x', parent_state[80], parent_state[81], parent_state[82], 'xxx', parent_state[88], 'xxxx', parent_state[109], 'xxx', parent_state[115], parent_state[116], parent_state[117], 'x', parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125], 'x', parent_state[129], parent_state[130], parent_state[131], 'xxx', parent_state[137], 'xxxx', parent_state[158], 'xxx', parent_state[164], parent_state[165], parent_state[166], 'x', parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174], 'x', parent_state[178], parent_state[179], parent_state[180], 'xxx', parent_state[186], 'xxxx', parent_state[207], 'xxx', parent_state[213], parent_state[214], parent_state[215], 'x', parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223], 'x', parent_state[227], parent_state[228], parent_state[229], 'xxx', parent_state[235], 'xx'])


def get_777_LFRB_centers_oblique_edges_solve_left_right_oblique_edges_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-left-right-oblique-edges-only
    """
    return ''.join(['x', parent_state[59], 'x', parent_state[61], 'x', parent_state[65], 'xxx', parent_state[69], 'xxxxx', parent_state[79], 'xxx', parent_state[83], 'x', parent_state[87], 'x', parent_state[89], 'xx', parent_state[108], 'x', parent_state[110], 'x', parent_state[114], 'xxx', parent_state[118], 'xxxxx', parent_state[128], 'xxx', parent_state[132], 'x', parent_state[136], 'x', parent_state[138], 'xx', parent_state[157], 'x', parent_state[159], 'x', parent_state[163], 'xxx', parent_state[167], 'xxxxx', parent_state[177], 'xxx', parent_state[181], 'x', parent_state[185], 'x', parent_state[187], 'xx', parent_state[206], 'x', parent_state[208], 'x', parent_state[212], 'xxx', parent_state[216], 'xxxxx', parent_state[226], 'xxx', parent_state[230], 'x', parent_state[234], 'x', parent_state[236], 'x'])


def get_777_LFRB_centers_oblique_edges_solve_middle_right_oblique_edges_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-middle-right-oblique-edges-only
    """
    return ''.join(['xx', parent_state[60], parent_state[61], 'x', parent_state[65], 'xxxx', parent_state[72], 'xxx', parent_state[76], 'xxxx', parent_state[83], 'x', parent_state[87], parent_state[88], 'xxxx', parent_state[109], parent_state[110], 'x', parent_state[114], 'xxxx', parent_state[121], 'xxx', parent_state[125], 'xxxx', parent_state[132], 'x', parent_state[136], parent_state[137], 'xxxx', parent_state[158], parent_state[159], 'x', parent_state[163], 'xxxx', parent_state[170], 'xxx', parent_state[174], 'xxxx', parent_state[181], 'x', parent_state[185], parent_state[186], 'xxxx', parent_state[207], parent_state[208], 'x', parent_state[212], 'xxxx', parent_state[219], 'xxx', parent_state[223], 'xxxx', parent_state[230], 'x', parent_state[234], parent_state[235], 'x', 'x'])


def get_777_LFRB_centers_oblique_edges_solve_inner_t_center_right_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-inner-t-center-right-oblique-edge-only
    """
    return ''.join(['xxx', parent_state[61], 'x', parent_state[65], 'x', parent_state[67], 'xxx', parent_state[73], parent_state[74], parent_state[75], 'xxx', parent_state[81], 'x', parent_state[83], 'x', parent_state[87], 'xxxxxx', parent_state[110], 'x', parent_state[114], 'x', parent_state[116], 'xxx', parent_state[122], parent_state[123], parent_state[124], 'xxx', parent_state[130], 'x', parent_state[132], 'x', parent_state[136], 'xxxxxx', parent_state[159], 'x', parent_state[163], 'x', parent_state[165], 'xxx', parent_state[171], parent_state[172], parent_state[173], 'xxx', parent_state[179], 'x', parent_state[181], 'x', parent_state[185], 'xxxxxx', parent_state[208], 'x', parent_state[212], 'x', parent_state[214], 'xxx', parent_state[220], parent_state[221], parent_state[222], 'xxx', parent_state[228], 'x', parent_state[230], 'x', parent_state[234], 'xxx'])


def get_777_LFRB_centers_oblique_edges_solve_left_middle_oblique_edge_only(parent_state):
    """
    777-LFRB-centers-oblique-edges-solve-left-middle-oblique-edge-only
    """
    return ''.join(['x', parent_state[59], parent_state[60], 'xxxxxx', parent_state[69], parent_state[72], 'xxx', parent_state[76], parent_state[79], 'xxxxxx', parent_state[88], parent_state[89], 'xx', parent_state[108], parent_state[109], 'xxxxxx', parent_state[118], parent_state[121], 'xxx', parent_state[125], parent_state[128], 'xxxxxx', parent_state[137], parent_state[138], 'xx', parent_state[157], parent_state[158], 'xxxxxx', parent_state[167], parent_state[170], 'xxx', parent_state[174], parent_state[177], 'xxxxxx', parent_state[186], parent_state[187], 'xx', parent_state[206], parent_state[207], 'xxxxxx', parent_state[216], parent_state[219], 'xxx', parent_state[223], parent_state[226], 'xxxxxx', parent_state[235], parent_state[236], 'x'])


def get_777_LFRB_inner_x_center_t_center_and_middle_oblique_edges_LR_solve(parent_state):
    """
    777-LFRB-inner-x-center-t-center-and-middle-oblique-edges-LR-solve
    """
    return ''.join(['xx', parent_state[60], 'xx',
                    'x', parent_state[66], parent_state[67], parent_state[68], 'x',
                    parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
                    'x', parent_state[80], parent_state[81], parent_state[82], 'x',
                    'xx', parent_state[88], 'xx',
                    'xx', parent_state[109], 'xx',
                    'x', parent_state[115], parent_state[116], parent_state[117], 'x',
                    parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
                    'x', parent_state[129], parent_state[130], parent_state[131], 'x',
                    'xx', parent_state[137], 'xx',
                    'xx', parent_state[158], 'xx',
                    'x', parent_state[164], parent_state[165], parent_state[166], 'x',
                    parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
                    'x', parent_state[178], parent_state[179], parent_state[180], 'x',
                    'xx', parent_state[186], 'xx',
                    'xx', parent_state[207], 'xx',
                    'x', parent_state[213], parent_state[214], parent_state[215], 'x',
                    parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
                    'x', parent_state[227], parent_state[228], parent_state[229], 'x',
                    'xx', parent_state[235], 'xx'])
    state = state.replace('U', 'x').replace('D', 'x').replace('F', 'x').replace('B', 'x')
    return state


def get_777_LFRB_oblique_edges_LR_solve(parent_state):
    """
    777-LFRB-oblique-edges-LR-solve
    """
    state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x', # Left
                     parent_state[65], 'xxx', parent_state[69],
                     parent_state[72], 'xxx', parent_state[76],
                     parent_state[79], 'xxx', parent_state[83],
                     'x', parent_state[87], parent_state[88], parent_state[89], 'x',
                     'x', parent_state[108], parent_state[109], parent_state[110], 'x', # Front
                     parent_state[114], 'xxx', parent_state[118],
                     parent_state[121], 'xxx', parent_state[125],
                     parent_state[128], 'xxx', parent_state[132],
                     'x', parent_state[136], parent_state[137], parent_state[138], 'x',
                     'x', parent_state[157], parent_state[158], parent_state[159], 'x', # Right
                     parent_state[163], 'xxx', parent_state[167],
                     parent_state[170], 'xxx', parent_state[174],
                     parent_state[177], 'xxx', parent_state[181],
                     'x', parent_state[185], parent_state[186], parent_state[187], 'x',
                     'x', parent_state[206], parent_state[207], parent_state[208], 'x', # Back
                     parent_state[212], 'xxx', parent_state[216],
                     parent_state[219], 'xxx', parent_state[223],
                     parent_state[226], 'xxx', parent_state[230],
                     'x', parent_state[234], parent_state[235], parent_state[236], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('F', 'x').replace('B', 'x')
    return state

def get_777_LR_inner_x_center_t_center_and_middle_oblique_edges_LR_solve(parent_state):
    """
    777-LR-inner-x-center-t-center-and-middle-oblique-edges-LR-solve
    """
    state = ''.join(['xx', parent_state[60], 'xx',
                     'x', parent_state[66], parent_state[67], parent_state[68], 'x',
                     parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
                     'x', parent_state[80], parent_state[81], parent_state[82], 'x',
                     'xx', parent_state[88], 'xx',
                     'xx', parent_state[158], 'xx',
                     'x', parent_state[164], parent_state[165], parent_state[166], 'x',
                     parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
                     'x', parent_state[178], parent_state[179], parent_state[180], 'x',
                     'xx', parent_state[186], 'xx'])
    state = state.replace('U', 'x').replace('D', 'x').replace('F', 'x').replace('B', 'x')
    return state


def get_777_LR_oblique_edges_LR_solve(parent_state):
    """
    777-LR-oblique-edges-LR-solve
    """
    state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x',
                     parent_state[65], 'xxx', parent_state[69],
                     parent_state[72], 'xxx', parent_state[76],
                     parent_state[79], 'xxx', parent_state[83],
                     'x', parent_state[87], parent_state[88], parent_state[89], 'x',
                     'x', parent_state[157], parent_state[158], parent_state[159], 'x',
                     parent_state[163], 'xxx', parent_state[167],
                     parent_state[170], 'xxx', parent_state[174],
                     parent_state[177], 'xxx', parent_state[181],
                     'x', parent_state[185], parent_state[186], parent_state[187], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('F', 'x').replace('B', 'x')
    return state


def get_777_LFRB_centers_oblique_edges_LR_solve(parent_state):
    """
    777-LFRB-centers-oblique-edges-LR-solve
    """
    state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x',
                     parent_state[65], parent_state[66], parent_state[67], parent_state[68], parent_state[69],
                     parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
                     parent_state[79], parent_state[80], parent_state[81], parent_state[82], parent_state[83],
                     'x', parent_state[87], parent_state[88], parent_state[89], 'x',
                     'x', parent_state[108], parent_state[109], parent_state[110], 'x',
                     parent_state[114], parent_state[115], parent_state[116], parent_state[117], parent_state[118],
                     parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
                     parent_state[128], parent_state[129], parent_state[130], parent_state[131], parent_state[132],
                     'x', parent_state[136], parent_state[137], parent_state[138], 'x',
                     'x', parent_state[157], parent_state[158], parent_state[159], 'x',
                     parent_state[163], parent_state[164], parent_state[165], parent_state[166], parent_state[167],
                     parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
                     parent_state[177], parent_state[178], parent_state[179], parent_state[180], parent_state[181],
                     'x', parent_state[185], parent_state[186], parent_state[187], 'x',
                     'x', parent_state[206], parent_state[207], parent_state[208], 'x',
                     parent_state[212], parent_state[213], parent_state[214], parent_state[215], parent_state[216],
                     parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
                     parent_state[226], parent_state[227], parent_state[228], parent_state[229], parent_state[230],
                     'x', parent_state[234], parent_state[235], parent_state[236], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('F', 'x').replace('B', 'x')
    return state


def get_777_LR_centers_oblique_edges_LR_solve(parent_state):
    """
    777-LR-centers-oblique-edges-LR-solve
    """
    state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x',
                     parent_state[65], parent_state[66], parent_state[67], parent_state[68], parent_state[69],
                     parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
                     parent_state[79], parent_state[80], parent_state[81], parent_state[82], parent_state[83],
                     'x', parent_state[87], parent_state[88], parent_state[89], 'x',
                     'x', parent_state[157], parent_state[158], parent_state[159], 'x',
                     parent_state[163], parent_state[164], parent_state[165], parent_state[166], parent_state[167],
                     parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
                     parent_state[177], parent_state[178], parent_state[179], parent_state[180], parent_state[181],
                     'x', parent_state[185], parent_state[186], parent_state[187], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('F', 'x').replace('B', 'x')
    return state


def get_777_LFRB_centers_oblique_edges_FB_solve(parent_state):
    """
    777-LFRB-centers-oblique-edges-FB-solve
    """
    state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x',
                     parent_state[65], parent_state[66], parent_state[67], parent_state[68], parent_state[69],
                     parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
                     parent_state[79], parent_state[80], parent_state[81], parent_state[82], parent_state[83],
                     'x', parent_state[87], parent_state[88], parent_state[89], 'x',
                     'x', parent_state[108], parent_state[109], parent_state[110], 'x',
                     parent_state[114], parent_state[115], parent_state[116], parent_state[117], parent_state[118],
                     parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
                     parent_state[128], parent_state[129], parent_state[130], parent_state[131], parent_state[132],
                     'x', parent_state[136], parent_state[137], parent_state[138], 'x',
                     'x', parent_state[157], parent_state[158], parent_state[159], 'x',
                     parent_state[163], parent_state[164], parent_state[165], parent_state[166], parent_state[167],
                     parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
                     parent_state[177], parent_state[178], parent_state[179], parent_state[180], parent_state[181],
                     'x', parent_state[185], parent_state[186], parent_state[187], 'x',
                     'x', parent_state[206], parent_state[207], parent_state[208], 'x',
                     parent_state[212], parent_state[213], parent_state[214], parent_state[215], parent_state[216],
                     parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
                     parent_state[226], parent_state[227], parent_state[228], parent_state[229], parent_state[230],
                     'x', parent_state[234], parent_state[235], parent_state[236], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('L', 'x').replace('R', 'x')
    return state


def get_777_FB_centers_oblique_edges_FB_solve(parent_state):
    """
    777-FB-centers-oblique-edges-FB-solve
    """
    state = ''.join(['x', parent_state[108], parent_state[109], parent_state[110], 'x',
                     parent_state[114], parent_state[115], parent_state[116], parent_state[117], parent_state[118],
                     parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
                     parent_state[128], parent_state[129], parent_state[130], parent_state[131], parent_state[132],
                     'x', parent_state[136], parent_state[137], parent_state[138], 'x',
                     'x', parent_state[206], parent_state[207], parent_state[208], 'x',
                     parent_state[212], parent_state[213], parent_state[214], parent_state[215], parent_state[216],
                     parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
                     parent_state[226], parent_state[227], parent_state[228], parent_state[229], parent_state[230],
                     'x', parent_state[234], parent_state[235], parent_state[236], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('L', 'x').replace('R', 'x')
    return state


def get_777_LFRB_inner_x_center_t_center_and_middle_oblique_edges_FB_solve(parent_state):
    """
    777-LFRB-inner-x-center-t-center-and-middle-oblique-edges-FB-solve
    """
    state = ''.join(['xx', parent_state[60], 'xx',
                     'x', parent_state[66], parent_state[67], parent_state[68], 'x',
                     parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
                     'x', parent_state[80], parent_state[81], parent_state[82], 'x',
                     'xx', parent_state[88], 'xx',
                     'xx', parent_state[109], 'xx',
                     'x', parent_state[115], parent_state[116], parent_state[117], 'x',
                     parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
                     'x', parent_state[129], parent_state[130], parent_state[131], 'x',
                     'xx', parent_state[137], 'xx',
                     'xx', parent_state[158], 'xx',
                     'x', parent_state[164], parent_state[165], parent_state[166], 'x',
                     parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
                     'x', parent_state[178], parent_state[179], parent_state[180], 'x',
                     'xx', parent_state[186], 'xx',
                     'xx', parent_state[207], 'xx',
                     'x', parent_state[213], parent_state[214], parent_state[215], 'x',
                     parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
                     'x', parent_state[227], parent_state[228], parent_state[229], 'x',
                     'xx', parent_state[235], 'xx'])
    state = state.replace('U', 'x').replace('D', 'x').replace('L', 'x').replace('R', 'x')
    return state


def get_777_FB_inner_x_center_t_center_and_middle_oblique_edges_FB_solve(parent_state):
    """
    777-FB-inner-x-center-t-center-and-middle-oblique-edges-FB-solve
    """
    state = ''.join(['xx', parent_state[109], 'xx',
                     'x', parent_state[115], parent_state[116], parent_state[117], 'x',
                     parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
                     'x', parent_state[129], parent_state[130], parent_state[131], 'x',
                     'xx', parent_state[137], 'xx',
                     'xx', parent_state[207], 'xx',
                     'x', parent_state[213], parent_state[214], parent_state[215], 'x',
                     parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
                     'x', parent_state[227], parent_state[228], parent_state[229], 'x',
                     'xx', parent_state[235], 'xx'])
    state = state.replace('U', 'x').replace('D', 'x').replace('L', 'x').replace('R', 'x')
    return state


def get_777_LFRB_oblique_edges_FB_solve(parent_state):
    """
    777-LFRB-oblique-edges-FB-solve
    """
    state = ''.join(['x', parent_state[59], parent_state[60], parent_state[61], 'x',
                     parent_state[65], 'xxx', parent_state[69],
                     parent_state[72], 'xxx', parent_state[76],
                     parent_state[79], 'xxx', parent_state[83],
                     'x', parent_state[87], parent_state[88], parent_state[89], 'x',
                     'x', parent_state[108], parent_state[109], parent_state[110], 'x',
                     parent_state[114], 'xxx', parent_state[118],
                     parent_state[121], 'xxx', parent_state[125],
                     parent_state[128], 'xxx', parent_state[132],
                     'x', parent_state[136], parent_state[137], parent_state[138], 'x',
                     'x', parent_state[157], parent_state[158], parent_state[159], 'x',
                     parent_state[163], 'xxx', parent_state[167],
                     parent_state[170], 'xxx', parent_state[174],
                     parent_state[177], 'xxx', parent_state[181],
                     'x', parent_state[185], parent_state[186], parent_state[187], 'x',
                     'x', parent_state[206], parent_state[207], parent_state[208], 'x',
                     parent_state[212], 'xxx', parent_state[216],
                     parent_state[219], 'xxx', parent_state[223],
                     parent_state[226], 'xxx', parent_state[230],
                     'x', parent_state[234], parent_state[235], parent_state[236], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('L', 'x').replace('R', 'x')
    return state


def get_777_FB_oblique_edges_FB_solve(parent_state):
    """
    777-FB-oblique-edges-FB-solve
    """
    state = ''.join(['x', parent_state[108], parent_state[109], parent_state[110], 'x',
                     parent_state[114], 'xxx', parent_state[118],
                     parent_state[121], 'xxx', parent_state[125],
                     parent_state[128], 'xxx', parent_state[132],
                     'x', parent_state[136], parent_state[137], parent_state[138], 'x',
                     'x', parent_state[206], parent_state[207], parent_state[208], 'x',
                     parent_state[212], 'xxx', parent_state[216],
                     parent_state[219], 'xxx', parent_state[223],
                     parent_state[226], 'xxx', parent_state[230],
                     'x', parent_state[234], parent_state[235], parent_state[236], 'x'])
    state = state.replace('U', 'x').replace('D', 'x').replace('L', 'x').replace('R', 'x')
    return state


state_functions = {
    '444-UD-centers-stage' : get_444_UD_centers_stage,
    '444-LR-centers-stage' : get_444_LR_centers_stage,
    '444-FB-centers-stage' : get_444_FB_centers_stage,
    '444-ULFRBD-centers-stage' : get_444_ULFRBD_centers_stage,
    '444-ULFRBD-centers-solve' : get_444_ULFRBD_centers_solve,
    '444-LR-centers-stage-tsai' : get_444_LR_centers_stage_tsai,
    '444-LR-centers-solve-tsai' : get_444_LR_centers_solve_tsai,
    '444-FB-centers-stage-tsai' : get_444_FB_centers_stage_tsai,
    '444-orient-edges-tsai' : get_444_orient_edges_tsai,
    '444-phase2-tsai' : get_444_orient_edges_tsai,
    '444-phase3-tsai' : get_444_phase3_tsai,
    '444-UFBR-edges' : get_444_UFBR_edges,
    '444-ULRF-edges' : get_444_ULRF_edges,
    '444-DFBR-edges' : get_444_DFBR_edges,
    '444-DLRF-edges' : get_444_DLRF_edges,
    '555-UD-centers-stage' : get_555_UD_centers_stage_state,
    '555-UD-T-centers-stage' : get_555_UD_T_centers_stage_state,
    '555-UD-X-centers-stage' : get_555_UD_X_centers_stage_state,
    '555-UD-centers-stage-LFRB-only' : get_555_UD_centers_stage_LFRB_only_state,
    '555-UD-centers-stage-UFDB-only' : get_555_UD_centers_stage_UFDB_only_state,
    '555-UD-centers-stage-ULDR-only' : get_555_UD_centers_stage_ULDR_only_state,
    '555-UD-centers-solve-on-all' : get_555_UD_centers_solve_on_all,
    '555-LR-centers-solve-on-all' : get_555_LR_centers_solve_on_all,
    '555-FB-centers-solve-on-all' : get_555_FB_centers_solve_on_all,
    '555-LR-centers-stage-on-LFRB': get_555_LR_centers_stage_on_LFRB,
    '555-ULFRBD-centers-solve' : get_555_ULFRBD_centers_solve,
    '555-LR-centers-stage-on-LFRB-x-center-only' : get_555_LR_centers_stage_on_LFRB_x_center_only,
    '555-LR-centers-stage-on-LFRB-t-center-only' : get_555_LR_centers_stage_on_LFRB_t_center_only,
    '666-UD-centers-oblique-edges-solve' : get_666_UD_centers_oblique_edges_solve,
    '666-LR-centers-oblique-edges-solve' : get_666_LR_centers_oblique_edges_solve,
    '666-FB-centers-oblique-edges-solve' : get_666_FB_centers_oblique_edges_solve,
    '666-LFRB-centers-oblique-edges-solve' : get_666_LFRB_centers_oblique_edges_solve,
    '666-UD-inner-X-centers-stage' : get_666_UD_inner_X_centers_stage,
    '666-UD-oblique-edge-pairing' : get_666_UD_oblique_edge_pairing,
    '666-UD-oblique-edge-pairing-left-only' : get_666_UD_oblique_edge_pairing_left_only,
    '666-UD-oblique-edge-pairing-right-only' : get_666_UD_oblique_edge_pairing_right_only,
    '666-UD-oblique-edge-pairing-LFRB-only' : get_666_UD_oblique_edge_pairing_LFRB_only,
    '666-LR-inner-X-centers-stage' : get_666_LR_inner_X_centers_stage,
    '666-LR-oblique-edge-pairing' : get_666_LR_oblique_edge_pairing,
    '666-LR-oblique-edge-pairing-left-only' : get_666_LR_oblique_edge_pairing_left_only,
    '666-LR-oblique-edge-pairing-right-only' : get_666_LR_oblique_edge_pairing_right_only,
    '777-UD-centers-oblique-edges-solve' : get_777_UD_centers_oblique_edges_solve,
    '777-LFRB-centers-oblique-edges-solve' : get_777_LFRB_centers_oblique_edges_solve,
    '777-UD-oblique-edge-pairing' : get_777_UD_oblique_edge_pairing,
    '777-UD-oblique-edge-pairing-middle-only' : get_777_UD_oblique_edge_pairing_middle_only,
    '777-UD-oblique-edge-pairing-left-only' : get_777_UD_oblique_edge_pairing_left_only,
    '777-UD-oblique-edge-pairing-right-only' : get_777_UD_oblique_edge_pairing_right_only,
    '777-LR-oblique-edge-pairing' : get_777_LR_oblique_edge_pairing,
    '777-LR-oblique-edge-pairing-middle-only' : get_777_LR_oblique_edge_pairing_middle_only,
    '777-LR-oblique-edge-pairing-left-only' : get_777_LR_oblique_edge_pairing_left_only,
    '777-LR-oblique-edge-pairing-right-only' : get_777_LR_oblique_edge_pairing_right_only,
    '777-UD-centers-oblique-edges-solve-center-only' : get_777_UD_centers_oblique_edges_solve_center_only,
    '777-UD-centers-oblique-edges-solve-edges-only' : get_777_UD_centers_oblique_edges_solve_edges_only,
    '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-only' : get_777_LFRB_centers_oblique_edges_solve_inner_x_center_inner_t_center_only,
    '777-LFRB-centers-oblique-edges-solve-inner-x-center-left-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_inner_x_center_left_oblique_edge_only,
    '777-LFRB-centers-oblique-edges-solve-inner-x-center-middle-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_inner_x_center_middle_oblique_edge_only,
    '777-LFRB-centers-oblique-edges-solve-inner-x-center-right-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_inner_x_center_right_oblique_edge_only,
    '777-LFRB-centers-oblique-edges-solve-inner-t-center-left-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_inner_t_center_left_oblique_edge_only,
    '777-LFRB-centers-oblique-edges-solve-inner-t-center-middle-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_inner_t_center_middle_oblique_edge_only,
    '777-LFRB-centers-oblique-edges-solve-inner-x-center-inner-t-center-middle-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_inner_x_center_inner_t_center_middle_oblique_edge_only,
    '777-LFRB-centers-oblique-edges-solve-left-right-oblique-edges-only' : get_777_LFRB_centers_oblique_edges_solve_left_right_oblique_edges_only,
    '777-LFRB-centers-oblique-edges-solve-middle-right-oblique-edges-only' : get_777_LFRB_centers_oblique_edges_solve_middle_right_oblique_edges_only,
    '777-LFRB-centers-oblique-edges-solve-inner-t-center-right-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_inner_t_center_right_oblique_edge_only,
    '777-LFRB-centers-oblique-edges-solve-left-middle-oblique-edge-only' : get_777_LFRB_centers_oblique_edges_solve_left_middle_oblique_edge_only,
    '777-LFRB-inner-x-center-t-center-and-middle-oblique-edges-LR-solve' : get_777_LFRB_inner_x_center_t_center_and_middle_oblique_edges_LR_solve,
    '777-LFRB-oblique-edges-LR-solve' : get_777_LFRB_oblique_edges_LR_solve,
    '777-LR-inner-x-center-t-center-and-middle-oblique-edges-LR-solve' : get_777_LR_inner_x_center_t_center_and_middle_oblique_edges_LR_solve,
    '777-LR-oblique-edges-LR-solve' : get_777_LR_oblique_edges_LR_solve,
    '777-LFRB-centers-oblique-edges-LR-solve' : get_777_LFRB_centers_oblique_edges_LR_solve,
    '777-LR-centers-oblique-edges-LR-solve' : get_777_LR_centers_oblique_edges_LR_solve,
    '777-LFRB-centers-oblique-edges-FB-solve' : get_777_LFRB_centers_oblique_edges_FB_solve,
    '777-FB-centers-oblique-edges-FB-solve' : get_777_FB_centers_oblique_edges_FB_solve,
    '777-LFRB-inner-x-center-t-center-and-middle-oblique-edges-FB-solve' : get_777_LFRB_inner_x_center_t_center_and_middle_oblique_edges_FB_solve,
    '777-FB-inner-x-center-t-center-and-middle-oblique-edges-FB-solve' : get_777_FB_inner_x_center_t_center_and_middle_oblique_edges_FB_solve,
    '777-LFRB-oblique-edges-FB-solve' : get_777_LFRB_oblique_edges_FB_solve,
    '777-FB-oblique-edges-FB-solve' : get_777_FB_oblique_edges_FB_solve,
}


class LookupTable(object):

    def __init__(self, parent, filename, state_type, state_target, state_hex, prune_table, max_depth=None, modulo=None):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.sides_LFRB = (self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB)
        self.sides_UFDB = (self.parent.sideU, self.parent.sideF, self.parent.sideD, self.parent.sideB)
        self.sides_UD = (self.parent.sideU, self.parent.sideD)
        self.sides_LR = (self.parent.sideL, self.parent.sideR)
        self.sides_FB = (self.parent.sideF, self.parent.sideB)
        self.filename = filename
        self.filename_hash = filename + '.hash'
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.filename_exists = False
        self.max_depth = max_depth
        self.modulo = modulo

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"
        assert self.modulo, "%s modulo is %s" % (self, self.modulo)

        # If the user just git cloned the repo all of the lookup tables will still be gzipped
        if not os.path.exists(self.filename):
            if os.path.exists(self.filename + '.gz'):
                log.warning("gunzip --keep %s.gz" % self.filename)
                subprocess.call(['gunzip', '--keep', self.filename + '.gz'])
            else:
                log.warning("%s does not exist" % self.filename)
                return

        # Now create a .hash copy of the lookup table
        if not os.path.exists(self.filename_hash):
            self.convert_file_to_hash()

        # Find the width, state_width and filesize of our .hash file
        with open(self.filename_hash, 'r') as fh:
            first_line = next(fh)
            self.width = len(first_line)

            # Now that the files are hashed the first line may not have an entry
            while ':' not in first_line:
                first_line = next(fh)

            for state_steps in first_line.split(','):
                (state, steps) = state_steps.split(':')
            self.state_width = len(state)

            filesize = os.path.getsize(self.filename_hash)
            self.linecount = int(filesize/self.width)

            if self.linecount * self.width != filesize:
                log.warning("%s is corrupt, self.linecount * self.width != filesize, %d * %d is %d, filesize is %d" %
                    (self.filename_hash, self.linecount, self.width, self.linecount * self.width, filesize))
                sys.exit(0)

        self.filename_exists = True
        self.scratchpad = self.desc + '.scratchpad'
        self.state_type = state_type
        self.state_target = state_target
        self.state_hex = state_hex
        self.prune_table = prune_table
        assert self.state_target is not None, "state_target is None"

        self.cache = {}
        self.guts_call_count = 0
        self.guts_left_right_range = 0
        self.fh_seek_call_count = 0
        self.fh_seek_lines_read = 0
        self.fh = open(self.filename_hash, 'r')

    def __str__(self):
        return self.desc

    def convert_file_to_hash(self):
        log.warning("%s: converting to a .hash file, we only need to do this the first time you run the solver" % self.filename)

        linecount = 0
        with open(self.filename, 'r') as fh:
            for line in fh:
                linecount += 1

        next_prime = find_next_prime(linecount)
        assert next_prime == self.modulo, "linecount %d, next prime %d, modulo %d...next prime and modulo must match" % (linecount, next_prime, self.modulo)

        log.info("%s: has %d lines, hash table will have %d buckets" % (self.filename, linecount, next_prime))
        by_index = {}

        for hash_index in xrange(next_prime):
            by_index[hash_index] = []

        with open(self.filename, 'r') as fh:
            for line in fh:
                line = line.rstrip()
                (state, steps) = line.split(':')
                hash_index = hashxx(state) % next_prime
                #print("state %s, hash %s" % (state, hash_index))
                by_index[hash_index].append(line)

        with open(self.filename_hash, 'w') as fh:
            for x in xrange(next_prime):
                line = ','.join(sorted(by_index[x]))
                fh.write(line + '\n')

        # Now pad the file so that all lines are the same length
        filename_pad = self.filename_hash + '.pad'
        max_length = 0

        with open(self.filename_hash, 'r') as fh:
            for line in fh:
                length = len(line.strip())
                if length > max_length:
                    max_length = length

        with open(filename_pad, 'w') as fh_pad:
            with open(self.filename_hash, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    length = len(line)
                    spaces_to_add = max_length - length

                    if spaces_to_add:
                        line = line + ' ' * spaces_to_add
                    fh_pad.write(line + '\n')

        shutil.move(filename_pad, self.filename_hash)

    def state(self):
        state_function = state_functions.get(self.state_type)

        # TODO stop passing self once you have unrolled all of these
        if state_function in (get_444_LR_centers_stage_tsai,
                              get_444_LR_centers_solve_tsai,
                              get_444_FB_centers_stage_tsai,
                              get_444_orient_edges_tsai,
                              get_444_phase3_tsai,
                              get_444_UFBR_edges,
                              get_444_ULRF_edges,
                              get_444_DFBR_edges,
                              get_444_DLRF_edges):
            state = state_function(self.parent.state, self)
        else:
            state = state_function(self.parent.state)

        if self.state_hex:
            state = convert_state_to_hex(state, self.state_width)

        return state

    def steps(self, state_to_find=None):
        """
        Return a list of the steps found in the lookup table for the current cube state
        """
        if state_to_find is None:
            state_to_find = self.state()

        try:
            return self.cache[state_to_find]
        except KeyError:

            # We use the hash_index as our line number in the file
            hash_index = hashxx(state_to_find) % self.modulo

            # Each line is the same width (they are padded with whitespaces to achieve this)
            # so jump to the hash_index line_number and read the line
            self.fh.seek(hash_index * self.width)
            line = self.fh.readline().rstrip()
            #log.info("%s: state %s, hash_index %s" % (self, state_to_find, hash_index))

            if not line:
                self.cache[state_to_find] = None
                return None

            for state_steps in line.split(','):
                #log.info("%s: %s, state_steps %s" % (self, line, state_steps))
                (state, steps) = state_steps.split(':')

                if state == state_to_find:
                    #log.info("%s: state %s, hash_index %s, steps %s" % (self, state, hash_index, steps))
                    steps_list = steps.split()
                    self.cache[state_to_find] = steps_list
                    return steps_list

                # The states on the line are sorted so stop looking if we know
                # there isn't going to be a match
                # TODO uncomment this once everything is working
                #if state_to_find < state:
                #    return None

            self.cache[state_to_find] = None
            return None

    def steps_length(self, state=None):
        return len(self.steps(state))

    def solve(self):

        if not self.filename_exists:
            raise SolveError("%s does not exist" % self.filename)

        while True:
            state = self.state()
            if self.state_target != 'EDGES':
                log.info("solve() state %s vs state_target %s" % (state, self.state_target))

            if state == self.state_target:
                break

            steps = self.steps(state)

            if not steps:
                raise NoSteps("%s: state %s does not have steps" % (self, state))

            for step in steps:
                self.parent.rotate(step)


class LookupTableIDA(LookupTable):
    """
    """

    def __init__(self, parent, filename, state_type, state_target, state_hex, moves_all, moves_illegal, prune_tables, max_depth, modulo):
        assert modulo, "%s modulo is %s" % (self, self.modulo)
        LookupTable.__init__(self, parent, filename, state_type, state_target, state_hex, False, max_depth, modulo)
        self.moves_all = moves_all
        self.moves_illegal = moves_illegal
        self.prune_tables = prune_tables
        self.visited_states = set()
        self.max_depth = max_depth
        assert self.modulo, "%s modulo is %s" % (self, self.modulo)

        for x in self.moves_illegal:
            if x not in self.moves_all:
                raise Exception("illegal move %s is not in the list of legal moves" % x)

    def ida_cost_estimate(self):
        cost_to_goal = 0

        for pt in self.prune_tables:
            pt_state = pt.state()
            pt_steps = pt.steps(pt_state)

            if pt_state == pt.state_target:
                len_pt_steps = 0

            elif pt_steps:
                len_pt_steps = len(pt_steps)

                # There are few prune tables that I built where instead of listing the steps
                # for a state I just listed how many steps there would be.  I did this to save
                # space.  lookup-table-5x5x5-step13-UD-centers-stage-UFDB-only.txt is one such table.
                if len_pt_steps == 1 and pt_steps[0].isdigit():
                    len_pt_steps = int(pt_steps[0])

            elif pt.max_depth:
                # This is the exception to the rule but some prune tables such
                # as lookup-table-6x6x6-step23-UD-oblique-edge-pairing-LFRB-only.txt
                # are partial tables so use the max_depth of the table +1
                len_pt_steps = pt.max_depth + 1

            else:
                raise SolveError("%s does not have max_depth and does not have steps for %s" % (pt, pt_state))

            if len_pt_steps > cost_to_goal:
                cost_to_goal = len_pt_steps

        return cost_to_goal

    def ida_search(self, steps_to_here, threshold, prev_step, prev_state):
        cost_to_here = len(steps_to_here)

        self.parent.state = prev_state[:]
        current_state = self.state()

        for step in self.moves_all:

            if step in self.moves_illegal:
                continue

            # If this step cancels out the previous step then don't bother with this branch
            if steps_cancel_out(prev_step, step):
                continue

            # If we have already explored the exact same scenario down another branch
            # then we can stop looking down this branch
            if (cost_to_here, current_state, step) in self.explored:
                continue
            self.explored.add((cost_to_here, current_state, step))

            self.parent.state = self.rotate_xxx(prev_state[:], step)
            state = self.state()
            steps = self.steps(state)
            self.ida_count += 1

            # =================================================
            # If there are steps for a state that means our IDA
            # search is done...woohoo!!
            # =================================================
            if steps:
                # rotate_xxx() above is very fast but it does not append the
                # steps to the solution so put the cube back in original state
                # and execute the steps via a normal rotate() call
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]

                for step in steps_to_here + [step,]:
                    self.parent.rotate(step)

                for step in steps:
                    self.parent.rotate(step)

                return True

            # Keep searching
            else:
                cost_to_goal = self.ida_cost_estimate()

                if (cost_to_here + cost_to_goal) <= threshold:
                    state_end_of_this_step = self.parent.state[:]

                    if self.ida_search(steps_to_here + [step,], threshold, step, state_end_of_this_step):
                        return True

        return False

    def ida_stage(self, max_ida_threshold):
        """
        The goal is to find a sequence of moves that will put the cube in a state that is
        in our lookup table self.filename
        """
        start_time0 = dt.datetime.now()
        state = self.state()
        log.info("ida_stage() state %s vs state_target %s" % (state, self.state_target))

        # The cube is already in the desired state, nothing to do
        if state == self.state_target:
            log.info("%s: IDA, cube is already at the target state" % self)
            return

        # The cube is already in a state that is in our lookup table, nothing for IDA to do
        steps = self.steps()

        if steps:
            log.info("%s: IDA, cube is already in a state that is in our lookup table" % self)
            return

        # If we are here (odds are very high we will be) it means that the current
        # cube state was not in the lookup table.  We must now perform an IDA search
        # until we find a sequence of moves that takes us to a state that IS in the
        # lookup table.

        # save cube state
        self.original_state = self.parent.state[:]
        self.original_solution = self.parent.solution[:]

        if self.parent.size == 2:
            self.rotate_xxx = rotate_222
        elif self.parent.size == 4:
            self.rotate_xxx = rotate_444
        elif self.parent.size == 5:
            self.rotate_xxx = rotate_555
        elif self.parent.size == 6:
            self.rotate_xxx = rotate_666
        elif self.parent.size == 7:
            self.rotate_xxx = rotate_777
        else:
            raise ImplementThis("Need rotate_xxx" % (self.parent.size, self.parent.size, self.parent.size))

        #for threshold in xrange(1, max_ida_threshold+1):
        for threshold in xrange(self.max_depth, max_ida_threshold+1):
            steps_to_here = []
            start_time1 = dt.datetime.now()
            self.ida_count = 0
            self.explored = set()

            if self.ida_search(steps_to_here, threshold, None, self.original_state[:]):
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, found match, explored %d branches, took %s (%s total)" %
                    (self, threshold, self.ida_count,
                     pretty_time(end_time1 - start_time1),
                     pretty_time(end_time1 - start_time0)))
                return
            else:
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, no match, explored %d branches, took %s" %
                    (self, threshold, self.ida_count, pretty_time(end_time1 - start_time1)))

        # The only time we will get here is when max_ida_threshold is a low number.  It will be up to the caller to:
        # - 'solve' one of their prune tables to put the cube in a state that we can find a solution for a little more easily
        # - call ida_solve() again but with a near infinite max_ida_threshold...99 is close enough to infinity for IDA purposes
        log.warning("%s: could not find a solution via IDA within %d steps...will 'solve' a prune table and try again" % (self, max_ida_threshold))

        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]
        raise NoIDASolution("%s FAILED for state %s" % (self, self.state()))

    def solve(self, max_ida_stage):

        # This shouldn't happen since the lookup tables are in the repo
        if not self.filename_exists:
            raise SolveError("%s does not exist" % self.filename)

        # Get the cube in a state that is in our lookup table
        self.ida_stage(max_ida_stage)

        # The cube is now in a state where it is in the lookup table, we may need
        # to do several lookups to get to our target state though. Use
        # LookupTabele's solve() to take us the rest of the way to the target state.
        LookupTable.solve(self)

        # Empty out the cache to save some memory
        self.cache = {}
