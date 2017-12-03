
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


def get_first_last_for_binary_search(line_number_to_state, state_to_find, linecount):
    first = 0
    last = linecount - 1
    to_delete = []

    for linenumber in sorted(line_number_to_state.keys()):
        state = line_number_to_state[linenumber]

        if state < state_to_find:
            first = linenumber
            to_delete.append(linenumber)

        elif state == state_to_find:
            first = linenumber
            last = linenumber
            break

        elif state > state_to_find:
            last = linenumber
            break

    for linenumber in to_delete:
        del line_number_to_state[linenumber]

    return (line_number_to_state, first, last)


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


def get_555_ULFRBD_t_centers_solve(parent_state):
    """
    555-ULFRBD-t-centers-solve
    """
    state = ['x',
             parent_state[8],
             'x',
             parent_state[12],
             parent_state[13],
             parent_state[14],
             'x',
             parent_state[18],
             'x',
             'x',
             parent_state[33],
             'x',
             parent_state[37],
             parent_state[38],
             parent_state[39],
             'x',
             parent_state[43],
             'x',
             'x',
             parent_state[58],
             'x',
             parent_state[62],
             parent_state[63],
             parent_state[64],
             'x',
             parent_state[68],
             'x',
             'x',
             parent_state[83],
             'x',
             parent_state[87],
             parent_state[88],
             parent_state[89],
             'x',
             parent_state[93],
             'x',
             'x',
             parent_state[108],
             'x',
             parent_state[112],
             parent_state[113],
             parent_state[114],
             'x',
             parent_state[118],
             'x',
             'x',
             parent_state[133],
             'x',
             parent_state[137],
             parent_state[138],
             parent_state[139],
             'x',
             parent_state[143],
             'x']

    state = ''.join(state)
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

        if 'dummy' not in self.filename:
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

                    # Download part-ac
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ac" %\
                        (self.parent.size, self.parent.size, self.parent.size)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

                    subprocess.call('cat lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-* > lookup-table-4x4x4-step70-tsai-phase3.txt.gz', shell=True)
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-aa')
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ab')
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ac')

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

        self.hex_format = '%' + "0%dx" % self.state_width
        self.filename_exists = True
        self.state_type = state_type

        if isinstance(state_target, tuple):
            self.state_target = set(state_target)
        elif isinstance(state_target, list):
            self.state_target = set(state_target)
        else:
            self.state_target = set((state_target, ))

        self.state_hex = state_hex
        self.cache = {}
        self.fh_txt = open(self.filename, 'r')
        self.preloaded_cache = False

        # This will go away once the transition to move cube specific logic out of LookupTable.py is complete
        if self.state_type is None:
            self.state_function = None
        else:
            try:
                self.state_function = state_functions[self.state_type]
    
            except KeyError:
                self.state_function = None

    def __str__(self):
        return self.desc

    def state(self):
        state = self.state_function(self.parent.state)

        if self.state_hex:
            state = convert_state_to_hex(state, self.state_width)

        return state

    def preload_cache(self):
        log.info("%s: start preload_cache()" % self)
        self.fh_txt.seek(0)

        for line in self.fh_txt.readlines():
            (state, steps) = line.split(':')
            self.cache[state] = steps.split()
        self.fh_txt.seek(0)
        log.info("%s: end preload_cache()" % self)
        self.preloaded_cache = True

    def binary_search(self, state_to_find):
        first = 0
        last = self.linecount - 1

        while first <= last:
            midpoint = int((first + last)/2)
            self.fh_txt.seek(midpoint * self.width)
            line = self.fh_txt.readline().rstrip()

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

    def steps_for_list_of_states(self, list_of_states):
        list_of_states = sorted(list_of_states)
        results = []
        line_number_to_state = {}

        for state_to_find in list_of_states:
            #first = 0
            #last = self.linecount - 1
            (line_number_to_state, first, last) = get_first_last_for_binary_search(line_number_to_state, state_to_find, self.linecount)
            #log.info("%s: first %d, last %d, state_to_find %s" % (self, first, last, state_to_find))

            while first <= last:
                midpoint = int((first + last)/2)
                self.fh_txt.seek(midpoint * self.width)
                line = self.fh_txt.readline().rstrip()

                #log.info("%s: first %d, last %d, midpoint %d, width %d, state_to_find %s, line %s" % (self, first, last, midpoint, self.width, state_to_find, line))

                try:
                    (state, steps) = line.split(':')
                except Exception:
                    log.warning("%s: midpoint %d, width %d, state_to_find %s, line %s" % (self, midpoint, self.width, state_to_find, line))
                    raise

                line_number_to_state[midpoint] = state

                if state == state_to_find:
                    results.append((state_to_find, steps.split()))
                    break
                else:

                    if state_to_find < state:
                        last = midpoint-1
                    else:
                        first = midpoint+1

        return results


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
            #log.info("%s: steps_cost None for %s (stage_target)" % (self, state_to_find))
            return 0
        else:
            #log.info("%s: steps_cost %d for %s (%s)" % (self, len(steps), state_to_find, ' '.join(steps)))
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
        #    log.info("%s: cost_to_goal %d\n" % (self, cost_to_goal))

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

    def ida_search_complete(self, state, steps_to_here):
        steps = self.steps(state)

        if not steps:
            return False

        # =================================================
        # If there are steps for a state that means our IDA
        # search is done...woohoo!!
        # =================================================
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

        if (self.state_type == '444-tsai-phase2' and
            not self.parent.edge_swaps_even(False, None, False)):

            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]
            log.warning("%s: found match but edge swaps are NOT even" % self)
            return False

        if self.avoid_oll and self.parent.center_solution_leads_to_oll_parity():
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]
            log.info("%s: IDA found match but it leads to OLL" % self)
            return False

        if self.avoid_pll and self.parent.edge_solution_leads_to_pll_parity():
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]
            log.info("%s: IDA found match but it leads to PLL" % self)
            return False

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

        return True

    def ida_search(self, steps_to_here, threshold, prev_step, prev_state):
        """
        https://algorithmsinsight.wordpress.com/graph-theory-2/ida-star-algorithm-in-general/
        """
        self.ida_count += 1

        # calculate f_cost which is the cost to where we are plus the estimated cost to reach our goal
        cost_to_here = len(steps_to_here)
        cost_to_goal = self.ida_heuristic()
        f_cost = cost_to_here + cost_to_goal

        state = self.state()

        if self.ida_search_complete(state, steps_to_here):
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

    def solve(self, min_ida_threshold=None, max_ida_threshold=99):
        """
        The goal is to find a sequence of moves that will put the cube in a state that is
        in our lookup table self.filename
        """
        start_time0 = dt.datetime.now()

        # This shouldn't happen since the lookup tables are in the repo
        if not self.filename_exists:
            raise SolveError("%s does not exist" % self.filename)

        state = self.state()
        #log.info("%s: ida_stage() state %s vs state_target %s" % (self, state, self.state_target))

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

        if min_ida_threshold is None:
            min_ida_threshold = self.ida_heuristic()

        # If this is the case the range loop below isn't worth running
        if min_ida_threshold >= max_ida_threshold+1:
            raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))

        log.info("%s: IDA threshold range %d->%d" % (self, min_ida_threshold, max_ida_threshold))

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
        log.info("%s: could not find a solution via IDA with max threshold of %d " % (self, max_ida_threshold))

        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))
