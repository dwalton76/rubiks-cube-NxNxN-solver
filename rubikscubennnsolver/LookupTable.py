
import datetime as dt
from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.rotate_xxx import rotate_222, rotate_444, rotate_555, rotate_666, rotate_777
from subprocess import check_output
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


def get_444_edges(parent_state):
    return ''.join((parent_state[2],
                    parent_state[3],
                    parent_state[5],
                    parent_state[8],
                    parent_state[9],
                    parent_state[12],
                    parent_state[14],
                    parent_state[15],

                    parent_state[18],
                    parent_state[19],
                    parent_state[21],
                    parent_state[24],
                    parent_state[25],
                    parent_state[28],
                    parent_state[30],
                    parent_state[31],

                    parent_state[34],
                    parent_state[35],
                    parent_state[37],
                    parent_state[40],
                    parent_state[41],
                    parent_state[44],
                    parent_state[46],
                    parent_state[47],

                    parent_state[50],
                    parent_state[51],
                    parent_state[53],
                    parent_state[56],
                    parent_state[57],
                    parent_state[60],
                    parent_state[62],
                    parent_state[63],

                    parent_state[66],
                    parent_state[67],
                    parent_state[69],
                    parent_state[72],
                    parent_state[73],
                    parent_state[76],
                    parent_state[78],
                    parent_state[79],

                    parent_state[82],
                    parent_state[83],
                    parent_state[85],
                    parent_state[88],
                    parent_state[89],
                    parent_state[92],
                    parent_state[94],
                    parent_state[95]))


edges_444 = (('0', 2, 67),  # upper
             ('1', 3, 66),
             ('2', 5, 18),
             ('3', 8, 51),
             ('4', 9, 19),
             ('5', 12, 50),
             ('6', 14, 34),
             ('7', 15, 35),

             ('8', 21, 72), # left
             ('9', 24, 37),
             ('a', 25, 76),
             ('b', 28, 41),

             ('c', 53, 40), # right
             ('d', 56, 69),
             ('e', 57, 44),
             ('f', 60, 73),

             ('g', 82, 46), # down
             ('h', 83, 47),
             ('i', 85, 31),
             ('j', 88, 62),
             ('k', 89, 30),
             ('l', 92, 63),
             ('m', 94, 79),
             ('n', 95, 78))

def edges_high_low_recolor2_444(state):
    edge_map = {
        'BD': [],
        'BL': [],
        'BR': [],
        'BU': [],
        'DF': [],
        'DL': [],
        'DR': [],
        'FL': [],
        'FR': [],
        'FU': [],
        'LU': [],
        'RU': []
    }

    for (edge_index, square_index, partner_index) in edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))
        edge_map[wing_str].append(edge_index)

    #log.info("state: %s" % ''.join(state))
    #log.info("edge_map:\n%s" % pformat(edge_map))

    # Where is the other wing_str like us?
    for (edge_index, square_index, partner_index) in edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))

        for tmp_index in edge_map[wing_str]:
            if tmp_index != edge_index:
                state[square_index] = tmp_index
                state[partner_index] = tmp_index
                break
        else:
            raise Exception("could not find tmp_index")

    return ''.join(state)


def get_444_edges_pattern(parent_state):
    foo = edges_high_low_recolor2_444(parent_state[:])

    return ''.join((foo[2],
                    foo[3],
                    foo[5],
                    foo[8],
                    foo[9],
                    foo[12],
                    foo[14],
                    foo[15],

                    foo[18],
                    foo[19],
                    foo[21],
                    foo[24],
                    foo[25],
                    foo[28],
                    foo[30],
                    foo[31],

                    foo[34],
                    foo[35],
                    foo[37],
                    foo[40],
                    foo[41],
                    foo[44],
                    foo[46],
                    foo[47],

                    foo[50],
                    foo[51],
                    foo[53],
                    foo[56],
                    foo[57],
                    foo[60],
                    foo[62],
                    foo[63],

                    foo[66],
                    foo[67],
                    foo[69],
                    foo[72],
                    foo[73],
                    foo[76],
                    foo[78],
                    foo[79],

                    foo[82],
                    foo[83],
                    foo[85],
                    foo[88],
                    foo[89],
                    foo[92],
                    foo[94],
                    foo[95]))

def get_444_centers_edges_pattern(parent_state):
    foo = edges_high_low_recolor2_444(parent_state[:])

    # record the state of all edges and centers
    return ''.join(foo[2:4] +
                   foo[5:13] +
                   foo[14:16] +
                   foo[18:20] +
                   foo[21:29] +
                   foo[30:32] +
                   foo[34:36] +
                   foo[37:45] +
                   foo[46:48] +
                   foo[50:52] +
                   foo[53:61] +
                   foo[62:64] +
                   foo[66:68] +
                   foo[69:77] +
                   foo[78:80] +
                   foo[82:84] +
                   foo[85:93] +
                   foo[94:96])


def get_444_UD_centers_stage(parent_state):
    """
    444-UD-centers-stage
    """
    babel = {
        'x' : '0',
        'L' : '0',
        'F' : '0',
        'R' : '0',
        'B' : '0',
        'D' : '1',
        'U' : '1',
    }

    state = [babel[parent_state[6]],
             babel[parent_state[7]],
             babel[parent_state[10]],
             babel[parent_state[11]],
             babel[parent_state[22]],
             babel[parent_state[23]],
             babel[parent_state[26]],
             babel[parent_state[27]],
             babel[parent_state[38]],
             babel[parent_state[39]],
             babel[parent_state[42]],
             babel[parent_state[43]],
             babel[parent_state[54]],
             babel[parent_state[55]],
             babel[parent_state[58]],
             babel[parent_state[59]],
             babel[parent_state[70]],
             babel[parent_state[71]],
             babel[parent_state[74]],
             babel[parent_state[75]],
             babel[parent_state[86]],
             babel[parent_state[87]],
             babel[parent_state[90]],
             babel[parent_state[91]]]
    state = ''.join(state)
    return state


def get_444_LR_centers_stage(parent_state):
    """
    444-LR-centers-stage
    """
    babel = {
        'x' : '0',
        'L' : '1',
        'F' : '0',
        'R' : '1',
        'B' : '0',
        'D' : '0',
        'U' : '0',
    }
    state = [babel[parent_state[6]],
             babel[parent_state[7]],
             babel[parent_state[10]],
             babel[parent_state[11]],
             babel[parent_state[22]],
             babel[parent_state[23]],
             babel[parent_state[26]],
             babel[parent_state[27]],
             babel[parent_state[38]],
             babel[parent_state[39]],
             babel[parent_state[42]],
             babel[parent_state[43]],
             babel[parent_state[54]],
             babel[parent_state[55]],
             babel[parent_state[58]],
             babel[parent_state[59]],
             babel[parent_state[70]],
             babel[parent_state[71]],
             babel[parent_state[74]],
             babel[parent_state[75]],
             babel[parent_state[86]],
             babel[parent_state[87]],
             babel[parent_state[90]],
             babel[parent_state[91]]]
    state = ''.join(state)
    return state


def get_444_FB_centers_stage(parent_state):
    """
    444-FB-centers-stage
    """
    babel = {
        'x' : '0',
        'L' : '0',
        'F' : '1',
        'R' : '0',
        'B' : '1',
        'D' : '0',
        'U' : '0',
    }
    state = [babel[parent_state[6]],
             babel[parent_state[7]],
             babel[parent_state[10]],
             babel[parent_state[11]],
             babel[parent_state[22]],
             babel[parent_state[23]],
             babel[parent_state[26]],
             babel[parent_state[27]],
             babel[parent_state[38]],
             babel[parent_state[39]],
             babel[parent_state[42]],
             babel[parent_state[43]],
             babel[parent_state[54]],
             babel[parent_state[55]],
             babel[parent_state[58]],
             babel[parent_state[59]],
             babel[parent_state[70]],
             babel[parent_state[71]],
             babel[parent_state[74]],
             babel[parent_state[75]],
             babel[parent_state[86]],
             babel[parent_state[87]],
             babel[parent_state[90]],
             babel[parent_state[91]]]
    state = ''.join(state)
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


def get_444_UD_centers_solve(parent_state):
    """
    444-UD-centers-solve
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
    state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x')
    return state


def get_444_LR_centers_solve(parent_state):
    """
    444-LR-centers-solve
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
    state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x')
    return state


def get_444_FB_centers_solve(parent_state):
    """
    444-FB-centers-solve
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
    state = state.replace('U', 'x').replace('L', 'x').replace('R', 'x').replace('D', 'x')
    return state

def get_444_LFRB_centers_stage(parent_state):
    """
    444-LFRB-centers-stage
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
    state = state.replace('U', 'x').replace('D', 'x').replace('R', 'L').replace('B', 'F')
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


def get_444_tsai_phase2_orient_edges(parent_state, orient_edges):
    """
    444-tsai-phase2-orient-edges
    """
    return ''.join([
        orient_edges[(2, 67, parent_state[2], parent_state[67])],
        orient_edges[(3, 66, parent_state[3], parent_state[66])],
        orient_edges[(5, 18, parent_state[5], parent_state[18])],
        orient_edges[(8, 51, parent_state[8], parent_state[51])],
        orient_edges[(9, 19, parent_state[9], parent_state[19])],
        orient_edges[(12, 50, parent_state[12], parent_state[50])],
        orient_edges[(14, 34, parent_state[14], parent_state[34])],
        orient_edges[(15, 35, parent_state[15], parent_state[35])],
        orient_edges[(18, 5, parent_state[18], parent_state[5])],
        orient_edges[(19, 9, parent_state[19], parent_state[9])],
        orient_edges[(21, 72, parent_state[21], parent_state[72])],
        orient_edges[(24, 37, parent_state[24], parent_state[37])],
        orient_edges[(25, 76, parent_state[25], parent_state[76])],
        orient_edges[(28, 41, parent_state[28], parent_state[41])],
        orient_edges[(30, 89, parent_state[30], parent_state[89])],
        orient_edges[(31, 85, parent_state[31], parent_state[85])],
        orient_edges[(34, 14, parent_state[34], parent_state[14])],
        orient_edges[(35, 15, parent_state[35], parent_state[15])],
        orient_edges[(37, 24, parent_state[37], parent_state[24])],
        orient_edges[(40, 53, parent_state[40], parent_state[53])],
        orient_edges[(41, 28, parent_state[41], parent_state[28])],
        orient_edges[(44, 57, parent_state[44], parent_state[57])],
        orient_edges[(46, 82, parent_state[46], parent_state[82])],
        orient_edges[(47, 83, parent_state[47], parent_state[83])],
        orient_edges[(50, 12, parent_state[50], parent_state[12])],
        orient_edges[(51, 8, parent_state[51], parent_state[8])],
        orient_edges[(53, 40, parent_state[53], parent_state[40])],
        orient_edges[(56, 69, parent_state[56], parent_state[69])],
        orient_edges[(57, 44, parent_state[57], parent_state[44])],
        orient_edges[(60, 73, parent_state[60], parent_state[73])],
        orient_edges[(62, 88, parent_state[62], parent_state[88])],
        orient_edges[(63, 92, parent_state[63], parent_state[92])],
        orient_edges[(66, 3, parent_state[66], parent_state[3])],
        orient_edges[(67, 2, parent_state[67], parent_state[2])],
        orient_edges[(69, 56, parent_state[69], parent_state[56])],
        orient_edges[(72, 21, parent_state[72], parent_state[21])],
        orient_edges[(73, 60, parent_state[73], parent_state[60])],
        orient_edges[(76, 25, parent_state[76], parent_state[25])],
        orient_edges[(78, 95, parent_state[78], parent_state[95])],
        orient_edges[(79, 94, parent_state[79], parent_state[94])],
        orient_edges[(82, 46, parent_state[82], parent_state[46])],
        orient_edges[(83, 47, parent_state[83], parent_state[47])],
        orient_edges[(85, 31, parent_state[85], parent_state[31])],
        orient_edges[(88, 62, parent_state[88], parent_state[62])],
        orient_edges[(89, 30, parent_state[89], parent_state[30])],
        orient_edges[(92, 63, parent_state[92], parent_state[63])],
        orient_edges[(94, 79, parent_state[94], parent_state[79])],
        orient_edges[(95, 78, parent_state[95], parent_state[78])]
    ])


def get_444_tsai_phase2(parent_state, orient_edges):
    """
    444-tsai-phase2
    """
    babel = {
        'L' : 'L',
        'F' : 'F',
        'R' : 'R',
        'B' : 'F',
        'D' : 'x',
        'U' : 'x',
    }

    return ''.join ([
        orient_edges[(2, 67, parent_state[2], parent_state[67])],
        orient_edges[(3, 66, parent_state[3], parent_state[66])],
        orient_edges[(5, 18, parent_state[5], parent_state[18])],
        babel[parent_state[6]],
        babel[parent_state[7]],
        orient_edges[(8, 51, parent_state[8], parent_state[51])],
        orient_edges[(9, 19, parent_state[9], parent_state[19])],
        babel[parent_state[10]],
        babel[parent_state[11]],
        orient_edges[(12, 50, parent_state[12], parent_state[50])],
        orient_edges[(14, 34, parent_state[14], parent_state[34])],
        orient_edges[(15, 35, parent_state[15], parent_state[35])],
        orient_edges[(18, 5, parent_state[18], parent_state[5])],
        orient_edges[(19, 9, parent_state[19], parent_state[9])],
        orient_edges[(21, 72, parent_state[21], parent_state[72])],
        babel[parent_state[22]],
        babel[parent_state[23]],
        orient_edges[(24, 37, parent_state[24], parent_state[37])],
        orient_edges[(25, 76, parent_state[25], parent_state[76])],
        babel[parent_state[26]],
        babel[parent_state[27]],
        orient_edges[(28, 41, parent_state[28], parent_state[41])],
        orient_edges[(30, 89, parent_state[30], parent_state[89])],
        orient_edges[(31, 85, parent_state[31], parent_state[85])],
        orient_edges[(34, 14, parent_state[34], parent_state[14])],
        orient_edges[(35, 15, parent_state[35], parent_state[15])],
        orient_edges[(37, 24, parent_state[37], parent_state[24])],
        babel[parent_state[38]],
        babel[parent_state[39]],
        orient_edges[(40, 53, parent_state[40], parent_state[53])],
        orient_edges[(41, 28, parent_state[41], parent_state[28])],
        babel[parent_state[42]],
        babel[parent_state[43]],
        orient_edges[(44, 57, parent_state[44], parent_state[57])],
        orient_edges[(46, 82, parent_state[46], parent_state[82])],
        orient_edges[(47, 83, parent_state[47], parent_state[83])],
        orient_edges[(50, 12, parent_state[50], parent_state[12])],
        orient_edges[(51, 8, parent_state[51], parent_state[8])],
        orient_edges[(53, 40, parent_state[53], parent_state[40])],
        babel[parent_state[54]],
        babel[parent_state[55]],
        orient_edges[(56, 69, parent_state[56], parent_state[69])],
        orient_edges[(57, 44, parent_state[57], parent_state[44])],
        babel[parent_state[58]],
        babel[parent_state[59]],
        orient_edges[(60, 73, parent_state[60], parent_state[73])],
        orient_edges[(62, 88, parent_state[62], parent_state[88])],
        orient_edges[(63, 92, parent_state[63], parent_state[92])],
        orient_edges[(66, 3, parent_state[66], parent_state[3])],
        orient_edges[(67, 2, parent_state[67], parent_state[2])],
        orient_edges[(69, 56, parent_state[69], parent_state[56])],
        babel[parent_state[70]],
        babel[parent_state[71]],
        orient_edges[(72, 21, parent_state[72], parent_state[21])],
        orient_edges[(73, 60, parent_state[73], parent_state[60])],
        babel[parent_state[74]],
        babel[parent_state[75]],
        orient_edges[(76, 25, parent_state[76], parent_state[25])],
        orient_edges[(78, 95, parent_state[78], parent_state[95])],
        orient_edges[(79, 94, parent_state[79], parent_state[94])],
        orient_edges[(82, 46, parent_state[82], parent_state[46])],
        orient_edges[(83, 47, parent_state[83], parent_state[47])],
        orient_edges[(85, 31, parent_state[85], parent_state[31])],
        babel[parent_state[86]],
        babel[parent_state[87]],
        orient_edges[(88, 62, parent_state[88], parent_state[62])],
        orient_edges[(89, 30, parent_state[89], parent_state[30])],
        babel[parent_state[90]],
        babel[parent_state[91]],
        orient_edges[(92, 63, parent_state[92], parent_state[63])],
        orient_edges[(94, 79, parent_state[94], parent_state[79])],
        orient_edges[(95, 78, parent_state[95], parent_state[78])]
    ])


def get_444_tsai_phase2_orient_edges_old(parent_state, self):
    """
    444-tsai-phase2-orient-edges or 444-tsai-phase2

    This is what we used originally, I then unrolled it to create the two functions above
    """
    raise Exception("We should not be here")
    state = []
    parent = self.parent
    original_state = self.parent.state[:]
    original_solution = self.parent.solution[:]

    state = []
    for side in self.sides_all:
        for square_index in range(side.min_pos, side.max_pos):

            if square_index in side.corner_pos:
                pass

            elif square_index in side.edge_pos:
                partner_index = side.get_wing_partner(square_index)
                square1 = self.parent.state[square_index]
                square2 = self.parent.state[partner_index]

                try:
                    state.append(self.parent.orient_edges[(square_index, partner_index, square1, square2)])
                    print("        state.append(self.parent.orient_edges[(%d, %d, parent_state[%d], parent_state[%d])])" % (square_index, partner_index, square_index, partner_index))

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
                if self.state_type == '444-tsai-phase2':
                    square_state = self.parent.state[square_index]
                    square_state = square_state.replace('B', 'F').replace('U', 'x').replace('D', 'x')
                    state.append(square_state)
                    print("        state.append(self.parent.state[%d].replace('B', 'F').replace('U', 'x').replace('D', 'x'))" % square_index)

    state = ''.join(state)

    if self.state_type == '444-tsai-phase2-orient-edges':
        if state.count('U') != 24:
            raise SolveError("state %s has %d Us and %d Ds, should have 24 of each" % (state, state.count('U'), state.count('D')))

        if state.count('D') != 24:
            raise SolveError("state %s has %d Us and %d Ds, should have 24 of each" % (state, state.count('U'), state.count('D')))

    return state


def get_444_tsai_phase2_centers_solve(parent_state):
    """
    444-tsai-phase2-centers-solve-tsai
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
    state = state.replace('B', 'F').replace('D', 'x').replace('U', 'x')
    return state


symmetry_rotations_tsai_phase3_444 =\
    ("",
     "y y",
     "x",
     "x y y",
     "x'",
     "x' y y",
     "x x",
     "x x y y",
     "reflect-x",
     "reflect-x y y",
     "reflect-x x",
     "reflect-x x y y",
     "reflect-x x'",
     "reflect-x x' y y",
     "reflect-x x x",
     "reflect-x x x y y")

# 12-23 are high edges, make these U (1)
# 0-11 are low edges, make these D (6)
# https://github.com/cs0x7f/TPR-4x4x4-Solver/blob/master/src/FullCube.java
high_edges_444 = ((14, 2, 67),  # upper
                  (13, 9, 19),
                  (15, 8, 51),
                  (12, 15, 35),
                  (21, 25, 76), # left
                  (20, 24, 37),
                  (23, 57, 44), # right
                  (22, 56, 69),
                  (18, 82, 46), # down
                  (17, 89, 30),
                  (19, 88, 62),
                  (16, 95, 78))

low_edges_444 = ((2, 3, 66),  # upper
                 (1, 5, 18),
                 (3, 12, 50),
                 (0, 14, 34),
                 (9, 21, 72), # left
                 (9, 28, 41),
                 (11, 53, 40), # right
                 (10, 60, 73),
                 (6, 83, 47), # down
                 (5, 85, 31),
                 (7, 92, 63),
                 (4, 94, 79))

def edges_high_low_recolor_444(state):
    """
    Look at all of the high edges and find the low edge for each.
    Return a string that represents where all the low edge siblings live in relation to their high edge counterpart.
    """
    assert len(state) == 97, "Invalid state %s, len is %d" % (state, len(state))
    low_edge_map = {}

    for (low_edge_index, square_index, partner_index) in low_edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        assert square_value != partner_value, "both squares are %s" % square_value
        wing_str = ''.join(sorted([square_value, partner_value]))
        low_edge_index = str(hex(low_edge_index))[2:]
        state[square_index] = low_edge_index
        state[partner_index] = low_edge_index

        assert wing_str not in low_edge_map, "We have two %s wings, one at high_index %s %s and one at high_index %s (%d, %d), state %s" %\
            (wing_str,
             low_edge_map[wing_str],
             pformat(low_edges_444[int(low_edge_map[wing_str])]),
             low_edge_index,
             square_index, partner_index,
             ''.join(state[1:]))

        # save low_edge_index in hex and chop the leading 0x via [2:]
        low_edge_map[wing_str] = low_edge_index

    assert len(low_edge_map.keys()) == 12, "Invalid low_edge_map\n%s\n" % pformat(low_edge_map)

    for (high_edge_index, square_index, partner_index) in high_edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))
        state[square_index] = low_edge_map[wing_str]
        state[partner_index] = low_edge_map[wing_str]
    return state


def reflect_x_444(cube):
    return [cube[0]] +\
           cube[93:97] +\
           cube[89:93] +\
           cube[85:89] +\
           cube[81:85] +\
           cube[29:33] +\
           cube[25:29] +\
           cube[21:25] +\
           cube[17:21] +\
           cube[45:49] +\
           cube[41:45] +\
           cube[37:41] +\
           cube[33:37] +\
           cube[61:65] +\
           cube[57:61] +\
           cube[53:57] +\
           cube[49:53] +\
           cube[77:81] +\
           cube[73:77] +\
           cube[69:73] +\
           cube[65:69] +\
           cube[13:17] +\
           cube[9:13] +\
           cube[5:9] +\
           cube[1:5]


def get_444_phase3_edges(parent_state):
    """
    444-phase3-edges
    """
    original_state = list('x' + ''.join(parent_state[1:]))
    results = []

    for seq in symmetry_rotations_tsai_phase3_444:
        state = original_state[:]

        for step in seq.split():
            if step == 'reflect-x':
                state = reflect_x_444(state[:])
            else:
                state = rotate_444(state[:], step)

        state = edges_high_low_recolor_444(state[:])

        # record the state of all edges
        state = ''.join(state)
        state = ''.join((state[2],   state[9],  state[8],  state[15],
                         state[25], state[24],
                         state[57], state[56],
                         state[82], state[89], state[88], state[95]))
        results.append(state[:])

    results = sorted(results)
    return results[0]


def get_444_tsai_phase3(parent_state):
    """
    444-tsai-phase3
    """
    original_state = edges_high_low_recolor_444(parent_state[:])
    results = []

    for seq in symmetry_rotations_tsai_phase3_444:
        state = original_state[:]

        for step in seq.split():
            if step == 'reflect-x':
                state = reflect_x_444(state[:])
            else:
                state = rotate_444(state[:], step)

        # record the state of all edges and centers
        state = ''.join(state[2:4] +
                        state[5:13] +
                        state[14:16] +
                        state[18:20] +
                        state[21:29] +
                        state[30:32] +
                        state[34:36] +
                        state[37:45] +
                        state[46:48] +
                        state[50:52] +
                        state[53:61] +
                        state[62:64] +
                        state[66:68] +
                        state[69:77] +
                        state[78:80] +
                        state[82:84] +
                        state[85:93] +
                        state[94:96])
        results.append(state[:])

    results = sorted(results)
    return results[0]


def get_555_UD_centers_stage_state(parent_state):
    """
    555-UD-centers-stage
    """
    state = ''.join(parent_state[7:10] +
                    parent_state[12:15] +
                    parent_state[17:20] +
                    parent_state[32:35] +
                    parent_state[37:40] +
                    parent_state[42:45] +
                    parent_state[57:60] +
                    parent_state[62:65] +
                    parent_state[67:70] +
                    parent_state[82:85] +
                    parent_state[87:90] +
                    parent_state[92:95] +
                    parent_state[107:110] +
                    parent_state[112:115] +
                    parent_state[117:120] +
                    parent_state[132:135] +
                    parent_state[137:140] +
                    parent_state[142:145])
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


def get_555_UL_centers_solve_on_all(parent_state):
    """
    555-UL-centers-solve-on-all
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
    state = state.replace('x', '0').replace('U', '1').replace('L', '1').replace('F', '0').replace('R', '0').replace('B', '0').replace('D', '0')
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
    state = [parent_state[32], 'x', parent_state[34],
             'x', parent_state[38], 'x',
             parent_state[42], 'x', parent_state[44],

             parent_state[57], 'x', parent_state[59],
             'x', parent_state[63], 'x',
             parent_state[67], 'x', parent_state[69],

             parent_state[82], 'x', parent_state[84],
             'x', parent_state[88], 'x',
             parent_state[92], 'x', parent_state[94],

             parent_state[107], 'x', parent_state[109],
             'x', parent_state[113], 'x',
             parent_state[117], 'x', parent_state[119]]

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
    state = ['x', parent_state[45], parent_state[46], 'x',
             parent_state[50], parent_state[51], parent_state[52], parent_state[53],
             parent_state[56], parent_state[57], parent_state[58], parent_state[59],
             'x', parent_state[63], parent_state[64], 'x',
             'xxxx',
             'x', parent_state[87], parent_state[88], 'x',
             'x', parent_state[93], parent_state[94], 'x',
             'xxxx',
             'x', parent_state[117], parent_state[118], 'x',
             parent_state[122], parent_state[123], parent_state[124], parent_state[125],
             parent_state[128], parent_state[129], parent_state[130], parent_state[131],
             'x', parent_state[135], parent_state[136], 'x',
             'xxxx',
             'x', parent_state[159], parent_state[160], 'x',
             'x', parent_state[165], parent_state[166], 'x',
             'xxxx']
    state = ''.join(state)
    return state


def get_666_FB_centers_oblique_edges_solve(parent_state):
    """
    666-FB-centers-oblique-edges-solve
    """
    state = ['xxxx',
             'x', parent_state[51], parent_state[52], 'x',
             'x', parent_state[57], parent_state[58], 'x',
             'xxxx',
             'x', parent_state[81], parent_state[82], 'x',
             parent_state[86], parent_state[87], parent_state[88], parent_state[89],
             parent_state[92], parent_state[93], parent_state[94], parent_state[95],
             'x', parent_state[99], parent_state[100], 'x',
             'xxxx',
             'x', parent_state[123], parent_state[124], 'x',
             'x', parent_state[129], parent_state[130], 'x',
             'xxxx',
             'x', parent_state[153], parent_state[154], 'x',
             parent_state[158], parent_state[159], parent_state[160], parent_state[161],
             parent_state[164], parent_state[165], parent_state[166], parent_state[167],
             'x', parent_state[171], parent_state[172], 'x']
    state = ''.join(state)
    return state


def get_666_LFRB_centers_oblique_edges_solve(parent_state):
    """
    666-LFRB-centers-oblique-edges-solve
    """
    state = ''.join(['x', parent_state[45], parent_state[46], 'x', parent_state[50], parent_state[51], parent_state[52], parent_state[53], parent_state[56], parent_state[57], parent_state[58], parent_state[59], 'x', parent_state[63], parent_state[64], 'xx', parent_state[81], parent_state[82], 'x', parent_state[86], parent_state[87], parent_state[88], parent_state[89], parent_state[92], parent_state[93], parent_state[94], parent_state[95], 'x', parent_state[99], parent_state[100], 'xx', parent_state[117], parent_state[118], 'x', parent_state[122], parent_state[123], parent_state[124], parent_state[125], parent_state[128], parent_state[129], parent_state[130], parent_state[131], 'x', parent_state[135], parent_state[136], 'xx', parent_state[153], parent_state[154], 'x', parent_state[158], parent_state[159], parent_state[160], parent_state[161], parent_state[164], parent_state[165], parent_state[166], parent_state[167], 'x', parent_state[171], parent_state[172], 'x'])
    return state


def get_666_LFRB_oblique_edges_solve(parent_state):
    """
    666-LFRB-oblique-edges-solve
    """
    state = ''.join([
    'x', parent_state[45], parent_state[46], 'x',
    parent_state[50], 'xx', parent_state[53],
    parent_state[56], 'xx', parent_state[59],
    'x', parent_state[63], parent_state[64],
    'xx', parent_state[81], parent_state[82], 'x',
    parent_state[86], 'xx', parent_state[89],
    parent_state[92], 'xx', parent_state[95],
    'x', parent_state[99], parent_state[100],
    'xx', parent_state[117], parent_state[118], 'x',
    parent_state[122], 'xx', parent_state[125],
    parent_state[128], 'xx', parent_state[131],
    'x', parent_state[135], parent_state[136],
    'xx', parent_state[153], parent_state[154], 'x',
    parent_state[158], 'xx', parent_state[161],
    parent_state[164], 'xx', parent_state[167],
    'x', parent_state[171], parent_state[172], 'x'])

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
    '444-LFRB-centers-stage' : get_444_LFRB_centers_stage,
    '444-UD-centers-solve' : get_444_UD_centers_solve,
    '444-LR-centers-solve' : get_444_LR_centers_solve,
    '444-FB-centers-solve' : get_444_FB_centers_solve,
    '444-ULFRBD-centers-stage' : get_444_ULFRBD_centers_stage,
    '444-ULFRBD-centers-solve' : get_444_ULFRBD_centers_solve,
    '444-tsai-phase2-orient-edges' : get_444_tsai_phase2_orient_edges,
    '444-tsai-phase2-centers-solve' : get_444_tsai_phase2_centers_solve,
    '444-tsai-phase2' : get_444_tsai_phase2,
    '444-tsai-phase3' : get_444_tsai_phase3,
    '444-phase3-edges' : get_444_phase3_edges,
    '444-edges' : get_444_edges,
    '444-edges-pattern' : get_444_edges_pattern,
    '444-centers-edges-pattern' : get_444_centers_edges_pattern,
    '555-UD-centers-stage' : get_555_UD_centers_stage_state,
    '555-UD-T-centers-stage' : get_555_UD_T_centers_stage_state,
    '555-UD-X-centers-stage' : get_555_UD_X_centers_stage_state,
    '555-UL-centers-solve-on-all' : get_555_UL_centers_solve_on_all,
    '555-LR-centers-stage-on-LFRB': get_555_LR_centers_stage_on_LFRB,
    '555-ULFRBD-centers-solve' : get_555_ULFRBD_centers_solve,
    '555-LR-centers-stage-on-LFRB-x-center-only' : get_555_LR_centers_stage_on_LFRB_x_center_only,
    '555-LR-centers-stage-on-LFRB-t-center-only' : get_555_LR_centers_stage_on_LFRB_t_center_only,
    '666-UD-centers-oblique-edges-solve' : get_666_UD_centers_oblique_edges_solve,
    '666-LR-centers-oblique-edges-solve' : get_666_LR_centers_oblique_edges_solve,
    '666-FB-centers-oblique-edges-solve' : get_666_FB_centers_oblique_edges_solve,
    '666-LFRB-centers-oblique-edges-solve' : get_666_LFRB_centers_oblique_edges_solve,
    '666-LFRB-oblique-edges-solve' : get_666_LFRB_oblique_edges_solve,
    '666-UD-inner-X-centers-stage' : get_666_UD_inner_X_centers_stage,
    '666-UD-oblique-edge-pairing' : get_666_UD_oblique_edge_pairing,
    '666-UD-oblique-edge-pairing-left-only' : get_666_UD_oblique_edge_pairing_left_only,
    '666-UD-oblique-edge-pairing-right-only' : get_666_UD_oblique_edge_pairing_right_only,
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

    def __init__(self, parent, filename, state_type, state_target, state_hex, linecount, max_depth=None):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.filename = filename
        self.filename_gz = filename + '.gz'
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.filename_exists = False
        self.linecount = linecount
        self.max_depth = max_depth
        self.record_stats = False
        self.heuristic_stats = {}
        self.avoid_oll = False
        self.avoid_pll = False

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"
        assert self.linecount, "%s linecount is %s" % (self, self.linecount)

        if not os.path.exists(self.filename):
            if not os.path.exists(self.filename_gz):

                # Special cases where I could not get them one under 100M so I split it via:
                # split -b 40m lookup-table-4x4x4-step70-tsai-phase3.txt.gz "lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-"
                if self.filename_gz == 'lookup-table-4x4x4-step70-tsai-phase3.txt.gz':

                    # Download part-aa
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-aa" %\
                        (self.parent.size, self.parent.size, self.parent.size)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

                    # Download part-ab
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ab" %\
                        (self.parent.size, self.parent.size, self.parent.size)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

                    subprocess.call('cat lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-* > lookup-table-4x4x4-step70-tsai-phase3.txt.gz', shell=True)
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-aa')
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ab')

                elif self.filename_gz == 'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz':

                    # Download all three parts
                    for extension in ('aa', 'ab', 'ac'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    subprocess.call('cat lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-* > lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz', shell=True)
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-aa')
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-ab')
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-ac')

                elif self.filename_gz == 'lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz':

                    # Download all three parts
                    for extension in ('aa', 'ab', 'ac'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    subprocess.call('cat lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-* > lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz', shell=True)
                    os.unlink('lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-aa')
                    os.unlink('lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-ab')
                    os.unlink('lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-ac')

                else:
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/%s" % (self.parent.size, self.parent.size, self.parent.size, self.filename_gz)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

            log.warning("gunzip %s" % self.filename_gz)
            subprocess.call(['gunzip', self.filename_gz])

        # Find the state_width for the entries in our .txt file
        with open(self.filename, 'r') as fh:
            first_line = next(fh)
            self.width = len(first_line)
            (state, steps) = first_line.split(':')
            self.state_width = len(state)

        self.filename_exists = True
        self.state_type = state_type
        assert state_target is not None, "state_target is None"

        if isinstance(state_target, tuple):
            self.state_target = set(state_target)
        elif isinstance(state_target, list):
            self.state_target = set(state_target)
        else:
            self.state_target = set((state_target, ))

        self.state_hex = state_hex
        self.cache = {}
        self.fh_txt = open(self.filename, 'r')
        self.seek_calls = 0
        self.binary_search_calls = 0
        self.total_first_last_delta = 0
        self.state_to_line_number = {}
        self.preloaded_cache = False

        # This will barf for 444-edges-slice-forward and 444-edges-slice-backward
        # but that is ok we never call state() for those
        try:
            self.state_function = state_functions[self.state_type]

            if self.state_function in (get_444_tsai_phase2_orient_edges,
                                       get_444_tsai_phase2):
                self.state_function_pass_orient_edges = True
            else:
                self.state_function_pass_orient_edges = False

        except KeyError:
            self.state_function = None
            self.state_function_pass_orient_edges = False

    def __str__(self):
        return self.desc

    def state(self):
        if self.state_function_pass_orient_edges:
            state = self.state_function(self.parent.state, self.parent.orient_edges)
        else:
            state = self.state_function(self.parent.state)

        if self.state_hex:
            state = convert_state_to_hex(state, self.state_width)

        return state

    def preload_cache(self):
        log.info("%s: start preload_cache()" % self)
        self.fh_txt.seek(0)

        for line in self.fh_txt:
            (state, steps) = line.rstrip().split(':')
            self.cache[state] = steps.split()
        self.fh_txt.seek(0)
        log.info("%s: end preload_cache()" % self)
        self.preloaded_cache = True

    def binary_search(self, state_to_find):
        first = 0
        last = self.linecount - 1
        self.binary_search_calls += 1

        while first <= last:
            midpoint = int((first + last)/2)
            self.fh_txt.seek(midpoint * self.width)
            line = self.fh_txt.readline().rstrip()
            self.total_first_last_delta += (last - first)
            self.seek_calls += 1

            try:
                (state, steps) = line.split(':')
            except Exception:
                log.warning("%s: midpoint %d, width %d, state_to_find %s, line %s" % (self, midpoint, self.width, state_to_find, line))
                raise

            if state == state_to_find:
                return line
            else:
                if state_to_find < state:
                    last = midpoint-1
                else:
                    first = midpoint+1

        return None

    def steps(self, state_to_find=None):
        """
        Return a list of the steps found in the lookup table for the current cube state
        """
        if state_to_find is None:
            state_to_find = self.state()

        # If we are at one of our state_targets we do not need to do anything
        if state_to_find in self.state_target:
            return None

        if self.preloaded_cache:
            return self.cache.get(state_to_find)

        try:
            return self.cache[state_to_find]
        except KeyError:
            line = self.binary_search(state_to_find)

            if line:
                (state, steps) = line.strip().split(':')
                steps_list = steps.split()
                self.cache[state_to_find] = steps_list
                return steps_list

            else:
                self.cache[state_to_find] = None
                return None

    def steps_cost(self, state_to_find=None):

        if state_to_find is None:
            state_to_find = self.state()

        steps = self.steps(state_to_find)

        if steps is None:
            log.info("%s: steps_cost None for %s (stage_target)" % (self, state_to_find))
            return 0
        else:
            log.info("%s: steps_cost %d for %s (%s)" % (self, len(steps), state_to_find, ' '.join(steps)))
            return len(steps)

    def solve(self):

        if not self.filename_exists:
            raise SolveError("%s does not exist" % self.filename)

        if 'TBD' in self.state_target:
            tbd = True
        else:
            tbd = False

        while True:
            state = self.state()

            if tbd:
                log.info("%s: solve() state %s vs state_target %s" % (self, state, pformat(self.state_target)))

            if state in self.state_target:
                break

            steps = self.steps(state)

            if steps:
                #log.info("%s: solve() state %s found %s" % (self, state, ' '.join(steps)))

                for step in steps:
                    self.parent.rotate(step)
            else:
                self.parent.print_cube()
                raise NoSteps("%s: state %s does not have steps" % (self, state))

    def convert_state_to_hex(self, state, hex_width):
        hex_state = hex(int(state, 2))[2:]

        if hex_state.endswith('L'):
            hex_state = hex_state[:-1]

        return hex_state.zfill(hex_width)


class LookupTableIDA(LookupTable):

    def __init__(self, parent, filename, state_type, state_target, state_hex, moves_all, moves_illegal, prune_tables, linecount):
        LookupTable.__init__(self, parent, filename, state_type, state_target, state_hex, linecount)
        self.prune_tables = prune_tables

        for x in moves_illegal:
            if x not in moves_all:
                raise Exception("illegal move %s is not in the list of legal moves" % x)

        self.moves_all = []
        for x in moves_all:
            if x not in moves_illegal:
                self.moves_all.append(x)

    def ida_heuristic_all_costs(self):
        """
        Only used if self.record_stats is True
        """
        results = {}

        for pt in self.prune_tables:
            pt_state = pt.state()
            pt_steps = pt.steps(pt_state)

            if pt_state in pt.state_target:
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
                raise SolveError("%s does not have max_depth and does not have steps for %s, state_width %d" % (pt, pt_state, pt.state_width))

            results[pt.filename] = len_pt_steps

        return results

    def ida_heuristic(self, debug=False):
        cost_to_goal = 0
        pt_costs = []

        for pt in self.prune_tables:
            pt_state = pt.state()
            pt_steps = pt.steps(pt_state)

            if pt_state in pt.state_target:
                len_pt_steps = 0

                #if debug:
                #    log.info("%s: pt_state %s, cost 0, at target" % (pt, pt_state))

            elif pt_steps:
                len_pt_steps = len(pt_steps)

                # There are few prune tables that I built where instead of listing the steps
                # for a state I just listed how many steps there would be.  I did this to save
                # space.  lookup-table-5x5x5-step13-UD-centers-stage-UFDB-only.txt is one such table.
                if len_pt_steps == 1 and pt_steps[0].isdigit():
                    len_pt_steps = int(pt_steps[0])

                #if debug:
                #    log.info("%s: pt_state %s, cost %d" % (pt, pt_state, len_pt_steps))

            elif pt.max_depth:
                # This is the exception to the rule but some prune tables such
                # as lookup-table-6x6x6-step23-UD-oblique-edge-pairing-LFRB-only.txt
                # are partial tables so use the max_depth of the table +1
                len_pt_steps = pt.max_depth + 1

                #if debug:
                #    log.info("%s: pt_state %s, cost %d (max depth)" % (pt, pt_state, len_pt_steps))

            else:
                self.parent.print_cube()
                raise SolveError("%s does not have max_depth and does not have steps for %s, state_width %d" % (pt, pt_state, pt.state_width))

            if self.heuristic_stats:
                pt_costs.append(len_pt_steps)

            if len_pt_steps > cost_to_goal:
                cost_to_goal = len_pt_steps

        if self.heuristic_stats:
            pt_costs = tuple(pt_costs)
            len_pt_steps = self.heuristic_stats.get(pt_costs, 0)

            if len_pt_steps > cost_to_goal:
                #if debug:
                #    log.info("%s: %s increase heuristic from %d to %d" % (self, pformat(pt_costs), cost_to_goal, len_pt_steps))
                cost_to_goal = len_pt_steps

        #if debug:
        #    log.info("%s: cost_to_goal %d" % (self, cost_to_goal))

        return cost_to_goal

    def steps(self, state_to_find):
        """
        Return a list of the steps found in the lookup table for the current cube state
        This is very similar to LookupTable.steps(), the main difference is we do not
        populate self.cache with misses.
        """

        if self.preloaded_cache:
            return self.cache.get(state_to_find)
        else:
            line = self.binary_search(state_to_find)

            if line:
                (state, steps) = line.strip().split(':')
                return steps.split()

            return None

    def ida_search(self, steps_to_here, threshold, prev_step, prev_state):
        """
        https://algorithmsinsight.wordpress.com/graph-theory-2/ida-star-algorithm-in-general/
        """
        cost_to_here = len(steps_to_here)
        cost_to_goal = self.ida_heuristic()
        f_cost = cost_to_here + cost_to_goal
        self.ida_count += 1

        # This looks a little odd because the cube may be in a state where we
        # find a hit in our lookup table and we could execute the steps
        # per the table and be done with our IDA search.
        #
        # That could cause us to return a longer solution but with the benefit
        # of the searching being faster....I am torn on whether to return False
        # here or not.
        if f_cost > threshold:
            return False

        state = self.state()
        steps = self.steps(state)

        # =================================================
        # If there are steps for a state that means our IDA
        # search is done...woohoo!!
        # =================================================
        if steps:

            # rotate_xxx() is very fast but it does not append the
            # steps to the solution so put the cube back in original state
            # and execute the steps via a normal rotate() call
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]

            for step in steps_to_here:
                self.parent.rotate(step)

            for step in steps:
                self.parent.rotate(step)

            # The cube is now in a state where it is in the lookup table, we may need
            # to do several lookups to get to our target state though. Use
            # LookupTabele's solve() to take us the rest of the way to the target state.
            LookupTable.solve(self)

            solution_ok = True

            if (solution_ok and
                self.state_type == '444-tsai-phase2' and
                not self.parent.edge_swaps_even(False, None, False)):

                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                log.warning("%s: found match but edge swaps are NOT even" % self)
                solution_ok = False

            if solution_ok and self.avoid_oll and self.parent.center_solution_leads_to_oll_parity():
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                log.info("%s: IDA found match but it leads to OLL" % self)
                solution_ok = False

            if solution_ok and self.avoid_pll and self.parent.edge_solution_leads_to_pll_parity():
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                log.info("%s: IDA found match but it leads to PLL" % self)
                solution_ok = False

            if solution_ok:
                # record stats here
                if self.record_stats:
                    final_state = self.parent.state[:]
                    final_solution = self.parent.solution[:]

                    self.parent.state = self.original_state[:]
                    self.parent.solution = self.original_solution[:]
                    actual_cost_to_goal = len(final_solution) - len(self.original_solution)
                    stats = []

                    for step in final_solution[len(self.original_solution):]:
                        stats.append(self.ida_heuristic_all_costs())
                        stats[-1]['state'] = self.state()
                        stats[-1]['step'] = step
                        stats[-1]['actual-cost'] = actual_cost_to_goal
                        actual_cost_to_goal -= 1

                        self.parent.rotate(step)

                    #log.info("STATS:\n%s\n" % pformat(stats))
                    #sys.exit(0)
                    with open('%s.stats' % self.filename, 'a') as fh:
                        for entry in stats:

                            if self.filename == 'lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt':
                                fh.write("%s,%d,%d,%d,%d\n" % (
                                    entry['state'],
                                    entry['lookup-table-4x4x4-step11-UD-centers-stage.txt'],
                                    entry['lookup-table-4x4x4-step12-LR-centers-stage.txt'],
                                    entry['lookup-table-4x4x4-step13-FB-centers-stage.txt'],
                                    entry['actual-cost']))

                            elif self.filename == 'lookup-table-4x4x4-step70-tsai-phase3.txt':
                                fh.write("%s,%d,%d,%d\n" % (
                                    entry['state'],
                                    entry['lookup-table-4x4x4-step71-phase3-edges-tsai.txt'],
                                    entry['lookup-table-4x4x4-step72-phase3-centers-tsai.txt'],
                                    entry['actual-cost']))

                    self.parent.state = final_state[:]
                    self.parent.solution = final_solution[:]

                log.info("%s: IDA found match %d steps in, %s, f_cost %d (cost_to_here %d, cost_to_goal %d)" %
                         (self, len(steps_to_here), ' '.join(steps_to_here), f_cost, cost_to_here, cost_to_goal))
                return True

        # ==============
        # Keep Searching
        # ==============
        if f_cost > threshold:
            return False

        # If we have already explored the exact same scenario down another branch
        # then we can stop looking down this branch
        if (cost_to_here, state) in self.explored:
            return False
        self.explored.add((cost_to_here, state))

        for step in self.moves_all:

            # If this step cancels out the previous step then don't bother with this branch
            if prev_step is not None:

                # U2 followed by U2 is a no-op
                if step == prev_step and step.endswith("2"):
                    continue

                # U' followed by U is a no-op
                if step == prev_step[0:-1] and prev_step.endswith("'") and not step.endswith("'"):
                    continue

                # U followed by U' is a no-op
                if step[0:-1] == prev_step and not prev_step.endswith("'") and step.endswith("'"):
                    continue

            self.parent.state = self.rotate_xxx(prev_state[:], step)

            if self.ida_search(steps_to_here + [step,], threshold, step, self.parent.state[:]):
                return True

        self.parent.state = prev_state[:]
        return False

    def solve(self, max_ida_threshold=99):
        """
        The goal is to find a sequence of moves that will put the cube in a state that is
        in our lookup table self.filename
        """
        start_time0 = dt.datetime.now()

        # This shouldn't happen since the lookup tables are in the repo
        if not self.filename_exists:
            raise SolveError("%s does not exist" % self.filename)

        state = self.state()
        log.info("%s: ida_stage() state %s vs state_target %s" % (self, state, self.state_target))

        # The cube is already in the desired state, nothing to do
        if state in self.state_target:
            log.info("%s: IDA, cube is already at the target state %s" % (self, state))
            return

        # The cube is already in a state that is in our lookup table, nothing for IDA to do
        steps = self.steps(state)

        if steps:
            log.info("%s: IDA, cube is already in a state %s that is in our lookup table" % (self, state))

            # The cube is now in a state where it is in the lookup table, we may need
            # to do several lookups to get to our target state though. Use
            # LookupTabele's solve() to take us the rest of the way to the target state.
            LookupTable.solve(self)
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

        min_ida_threshold = self.ida_heuristic()
        log.info("%s: IDA threshold range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))

        for threshold in range(min_ida_threshold, max_ida_threshold+1):
            steps_to_here = []
            start_time1 = dt.datetime.now()
            self.ida_count = 0
            self.explored = set()

            if self.ida_search(steps_to_here, threshold, None, self.original_state[:]):
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d branches, took %s (%s total)" %
                    (self, threshold, self.ida_count,
                     pretty_time(end_time1 - start_time1),
                     pretty_time(end_time1 - start_time0)))
                return
            else:
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d branches, took %s" %
                    (self, threshold, self.ida_count, pretty_time(end_time1 - start_time1)))

        # The only time we will get here is when max_ida_threshold is a low number.  It will be up to the caller to:
        # - 'solve' one of their prune tables to put the cube in a state that we can find a solution for a little more easily
        # - call ida_solve() again but with a near infinite max_ida_threshold...99 is close enough to infinity for IDA purposes
        log.warning("%s: could not find a solution via IDA within %d steps...will 'solve' a prune table and try again" % (self, max_ida_threshold))

        # Uncomment to see output for binary search performance
        '''
        for pt in self.prune_tables:

            # Avoid divide by 0
            if pt.binary_search_calls == 0:
                pt.binary_search_calls = 1

            # Avoid divide by 0
            if pt.seek_calls == 0:
                pt.seek_calls = 1

            log.warning("%s: %d binary search calls, %d seek calls, %d avg seeks per search, %d total first-to-last delta, %d avg first-to-last delta" %
                (pt, pt.binary_search_calls, pt.seek_calls, int(pt.seek_calls/pt.binary_search_calls), pt.total_first_last_delta, int(pt.total_first_last_delta/pt.seek_calls)))

        # Avoid divide by 0
        if self.binary_search_calls == 0:
            self.binary_search_calls = 1

        # Avoid divide by 0
        if self.seek_calls == 0:
            self.seek_calls = 1

        log.warning("%s: %d binary search calls, %d seek calls, %d avg seeks per search, %d total first-to-last delta, %d avg first-to-last delta" %
                (self, self.binary_search_calls, self.seek_calls, int(self.seek_calls/self.binary_search_calls), self.total_first_last_delta, int(self.total_first_last_delta/self.seek_calls)))
        '''

        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        raise NoIDASolution("%s FAILED for state %s" % (self, self.state()))
